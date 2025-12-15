import json
import re
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Max, Prefetch
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST, require_http_methods
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.urls import reverse
from .models import Board, List, Card, Label, Subtask, Comment


def _annotate_boards(boards_qs):
    boards = []
    for board in boards_qs:
        lists = list(board.lists.all())
        card_count = sum(len(board_list.cards.all()) for board_list in lists)
        board.list_count = len(lists)
        board.card_count = card_count
        boards.append(board)
    return boards


@login_required
def board_list(request):
    boards_qs = (
        Board.objects.select_related("owner")
        .prefetch_related(
            Prefetch("lists", queryset=List.objects.prefetch_related("cards"))
        )
    )
    query = (request.GET.get("q") or "").strip()
    if query:
        boards_qs = boards_qs.filter(title__icontains=query)
    owner_filter = request.GET.get("owner")
    if owner_filter == "me":
        boards_qs = boards_qs.filter(owner=request.user)
    sort = request.GET.get("sort") or "recent"
    sort_map = {
        "recent": "-created_at",
        "alphabetic": "title",
        "activity": "-created_at",
    }
    boards_qs = boards_qs.order_by(sort_map.get(sort, "-created_at"))
    boards = _annotate_boards(boards_qs)
    context = {
        "boards": boards,
        "query": query,
        "owner_filter": owner_filter or "all",
        "sort": sort,
    }
    template_name = "boards/board_list.html"
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        template_name = "boards/partials/board_grid.html"
    return render(request, template_name, context)


def board_detail(request, board_id):
    cards_prefetch = Prefetch(
        "cards",
        queryset=Card.objects.select_related("list")
        .prefetch_related("labels", "subtasks", "comments")
        .order_by("position"),
    )
    lists_prefetch = Prefetch(
        "lists",
        queryset=List.objects.prefetch_related(cards_prefetch).order_by("position"),
    )
    board = get_object_or_404(
        Board.objects.select_related("owner").prefetch_related(lists_prefetch),
        pk=board_id,
    )

    raw_query = (request.GET.get("q") or "").strip()
    query = raw_query.lower()
    for board_list in board.lists.all():
        cards_queryset = board_list.cards.all()
        if query:
            cards_queryset = cards_queryset.filter(title__icontains=query)
        cards = list(cards_queryset)
        for card in cards:
            subtasks = list(card.subtasks.all())
            comments = list(card.comments.all())
            card.total_subtasks = len(subtasks)
            card.completed_subtasks = sum(1 for subtask in subtasks if subtask.is_completed)
            card.comment_count = len(comments)
        board_list.cached_cards = cards

    context = {
        "board": board,
        "query": raw_query,
    }
    return render(request, "boards/board_detail.html", context)


@require_POST
def create_list(request, board_id):
    board = get_object_or_404(Board, pk=board_id)
    title = (request.POST.get("title") or "").strip()
    if not title:
        return redirect("boards:board_detail", board_id=board.id)

    max_position = board.lists.aggregate(max_pos=Max("position"))["max_pos"] or 0
    List.objects.create(title=title, board=board, position=max_position + 1)
    messages.success(request, "Liste ajoutée avec succès.")

    return redirect("boards:board_detail", board_id=board.id)


@require_POST
def create_card(request, board_id):
    board = get_object_or_404(Board, pk=board_id)
    list_id = request.POST.get("list_id")
    title = (request.POST.get("title") or "").strip()
    description = (request.POST.get("description") or "").strip()

    if not title or not list_id:
        return redirect("boards:board_detail", board_id=board.id)

    board_list = get_object_or_404(List, pk=list_id, board=board)
    max_position = board_list.cards.aggregate(max_pos=Max("position"))["max_pos"] or 0
    Card.objects.create(
        title=title,
        description=description,
        list=board_list,
        position=max_position + 1,
    )
    messages.success(request, "Carte créée avec succès.")
    return redirect("boards:board_detail", board_id=board.id)


@require_POST
def reorder_lists(request, board_id):
    board = get_object_or_404(Board, pk=board_id)
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return HttpResponseBadRequest("Invalid JSON payload.")
    order = payload.get("order")
    if not isinstance(order, list):
        return HttpResponseBadRequest("Invalid order format.")
    with transaction.atomic():
        for position, list_id in enumerate(order, start=1):
            List.objects.filter(pk=list_id, board=board).update(position=position)
    return JsonResponse({"status": "ok"})


@require_POST
def reorder_cards(request, board_id):
    board = get_object_or_404(Board, pk=board_id)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return HttpResponseBadRequest("Invalid JSON payload.")

    lists_payload = payload.get("lists")
    if not isinstance(lists_payload, list):
        return HttpResponseBadRequest("Invalid lists format.")

    with transaction.atomic():
        for list_item in lists_payload:
            list_id = list_item.get("id")
            card_ids = list_item.get("card_ids") or []
            if not list_id or not isinstance(card_ids, list):
                continue

            board_list = List.objects.filter(pk=list_id, board=board).first()
            if not board_list:
                continue

            for position, card_id in enumerate(card_ids, start=1):
                Card.objects.filter(pk=card_id, list__board=board).update(
                    list=board_list,
                    position=position,
                )

    return JsonResponse({"status": "ok"})


@require_POST
def rename_board(request, board_id):
    board = get_object_or_404(Board, pk=board_id)
    title = (request.POST.get("title") or "").strip()
    if title:
        board.title = title
        board.save(update_fields=["title"])
        messages.success(request, "Tableau renommé.")
    return redirect("boards:board_list")


@require_POST
def delete_board(request, board_id):
    board = get_object_or_404(Board, pk=board_id)
    board.delete()
    messages.success(request, "Tableau supprimé.")
    return redirect("boards:board_list")


@require_POST
def delete_list(request, board_id, list_id):
    board = get_object_or_404(Board, pk=board_id)
    board_list = get_object_or_404(List, pk=list_id, board=board)
    board_list.delete()
    messages.success(request, "Liste supprimée.")
    return redirect("boards:board_detail", board_id=board.id)


def _get_payload(request):
    if request.content_type == "application/json":
        try:
            return json.loads(request.body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return {}
    return request.POST


def _card_queryset():
    return Card.objects.select_related("list__board").prefetch_related(
        "labels",
        "subtasks",
        Prefetch(
            "comments",
            queryset=Comment.objects.select_related("author").order_by("-created_at"),
        ),
    )


def _card_response(card):
    labels = [
        {"id": label.id, "name": label.name, "color": label.color}
        for label in card.labels.all()
    ]
    label_ids = {label["id"] for label in labels}
    available_labels = [
        {
            "id": label.id,
            "name": label.name,
            "color": label.color,
            "assigned": label.id in label_ids,
        }
        for label in Label.objects.order_by("name")
    ]
    subtasks = [
        {"id": subtask.id, "title": subtask.title, "is_completed": subtask.is_completed}
        for subtask in card.subtasks.all()
    ]
    comments = [
        {
            "id": comment.id,
            "author": comment.author.get_full_name() or comment.author.username,
            "content": comment.content,
            "created_at": comment.created_at.strftime("%d/%m/%Y %H:%M"),
        }
        for comment in card.comments.all()
    ]
    return {
        "id": card.id,
        "board_id": card.list.board_id,
        "list_id": card.list_id,
        "title": card.title,
        "description": card.description or "",
        "due_date": card.due_date.isoformat() if card.due_date else None,
        "due_date_display": timezone.localtime(card.due_date).strftime("%d/%m/%Y %H:%M") if card.due_date else "",
        "due_date_local": timezone.localtime(card.due_date).strftime("%Y-%m-%dT%H:%M") if card.due_date else "",
        "labels": labels,
        "available_labels": available_labels,
        "subtasks": subtasks,
        "completed_subtasks": sum(1 for subtask in subtasks if subtask["is_completed"]),
        "total_subtasks": len(subtasks),
        "comments": comments,
        "comment_count": len(comments),
    }


def _get_card(board_id, card_id):
    return get_object_or_404(_card_queryset(), pk=card_id, list__board_id=board_id)


@require_http_methods(["GET"])
def card_detail(request, board_id, card_id):
    card = _get_card(board_id, card_id)
    return JsonResponse(_card_response(card))


@require_POST
def update_card(request, board_id, card_id):
    card = _get_card(board_id, card_id)
    payload = _get_payload(request)
    title = (payload.get("title") or "").strip()
    if not title:
        return HttpResponseBadRequest("Le titre est requis.")
    description = (payload.get("description") or "").strip()
    due_date_raw = payload.get("due_date")
    if due_date_raw:
        parsed = parse_datetime(due_date_raw)
        if parsed is None:
            return HttpResponseBadRequest("Date limite invalide.")
        if timezone.is_naive(parsed):
            parsed = timezone.make_aware(parsed, timezone.get_current_timezone())
        card.due_date = parsed
    else:
        card.due_date = None
    card.title = title
    card.description = description
    card.save(update_fields=["title", "description", "due_date"])
    return JsonResponse(_card_response(_get_card(board_id, card_id)))


@require_POST
def toggle_card_label(request, board_id, card_id):
    card = _get_card(board_id, card_id)
    payload = _get_payload(request)
    label_id = payload.get("label_id")
    if not label_id:
        return HttpResponseBadRequest("label_id requis.")
    label = get_object_or_404(Label, pk=label_id)
    if card.labels.filter(pk=label.id).exists():
        card.labels.remove(label)
    else:
        card.labels.add(label)
    return JsonResponse(_card_response(_get_card(board_id, card_id)))


@require_POST
def create_subtask(request, board_id, card_id):
    card = _get_card(board_id, card_id)
    payload = _get_payload(request)
    title = (payload.get("title") or "").strip()
    if not title:
        return HttpResponseBadRequest("Le titre de la sous-tâche est requis.")
    Subtask.objects.create(card=card, title=title)
    return JsonResponse(_card_response(_get_card(board_id, card_id)))


@require_POST
def toggle_subtask(request, board_id, card_id, subtask_id):
    card = _get_card(board_id, card_id)
    subtask = get_object_or_404(Subtask, pk=subtask_id, card=card)
    subtask.is_completed = not subtask.is_completed
    subtask.save(update_fields=["is_completed"])
    return JsonResponse(_card_response(_get_card(board_id, card_id)))


@require_POST
def delete_subtask(request, board_id, card_id, subtask_id):
    card = _get_card(board_id, card_id)
    subtask = get_object_or_404(Subtask, pk=subtask_id, card=card)
    subtask.delete()
    return JsonResponse(_card_response(_get_card(board_id, card_id)))


@require_POST
def create_comment(request, board_id, card_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentification requise."}, status=403)
    card = _get_card(board_id, card_id)
    payload = _get_payload(request)
    content = (payload.get("content") or "").strip()
    if not content:
        return HttpResponseBadRequest("Le commentaire est requis.")
    Comment.objects.create(card=card, author=request.user, content=content)
    return JsonResponse(_card_response(_get_card(board_id, card_id)))


@require_POST
def create_label(request, board_id, card_id):
    card = _get_card(board_id, card_id)
    payload = _get_payload(request)
    name = (payload.get("name") or "").strip()
    color = (payload.get("color") or "#3b82f6").strip()
    if not name:
        return HttpResponseBadRequest("Le nom de l'étiquette est requis.")
    if not re.match(r"^#(?:[0-9a-fA-F]{3}){1,2}$", color):
        color = "#3b82f6"
    label = Label.objects.create(name=name, color=color)
    card.labels.add(label)
    return JsonResponse(_card_response(_get_card(board_id, card_id)))


@require_POST
def delete_label(request, board_id, card_id, label_id):
    card = _get_card(board_id, card_id)
    label = get_object_or_404(Label, pk=label_id)
    card.labels.remove(label)
    if not label.cards.exists():
        label.delete()
    return JsonResponse(_card_response(_get_card(board_id, card_id)))


@require_POST
def delete_card(request, board_id, card_id):
    card = _get_card(board_id, card_id)
    card_id_value = card.id
    card.delete()
    return JsonResponse({"status": "deleted", "card_id": card_id_value})


@login_required
@require_POST
def create_board(request):
    title = (request.POST.get("title") or "").strip()
    if not title:
        messages.error(request, "Le titre est obligatoire.")
        return redirect("boards:board_list")
    Board.objects.create(title=title, owner=request.user)
    messages.success(request, "Nouveau tableau créé.")
    return redirect("boards:board_list")


def home(request):
    primary_href = "#create-board" if request.user.is_authenticated else reverse("boards:board_list")
    secondary_href = reverse("boards:board_list")
    context = {
        "hero": {
            "title": "Organise tout ton travail avec EpiTrello",
            "subtitle": "Tableaux, listes et cartes pour garder ton équipe alignée.",
            "cta_primary": {"label": "Créer un tableau", "href": primary_href},
            "cta_secondary": {"label": "Découvrir", "href": secondary_href},
        },
        "preview_columns": ["TODO", "En cours", "Terminé"],
        "preview_cards": [1, 2],
    }
    if request.user.is_authenticated:
        boards_qs = (
            Board.objects.filter(owner=request.user)
            .select_related("owner")
            .prefetch_related(
                Prefetch("lists", queryset=List.objects.prefetch_related("cards"))
            )
            .order_by("-created_at")
        )
        context["boards"] = _annotate_boards(boards_qs)
    return render(request, "boards/home.html", context)


def admin_logout(request):
    logout(request)
    messages.success(request, "Déconnexion effectuée.")
    return redirect("home")

