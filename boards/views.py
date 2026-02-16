import json
import logging
import re
import csv
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import logout, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.db.models import Max, Min, Prefetch, Q
from django.http import Http404, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST, require_http_methods
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.urls import reverse
from .models import Board, List, Card, Label, Subtask, Comment, Notification, Checklist
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from django.contrib.auth.views import PasswordChangeView
from django.core.mail import send_mail

logger = logging.getLogger(__name__)

def _send_board_event(board_id: int, payload: dict):
    try:
        layer = get_channel_layer()
        if not layer:
            logger.warning(f"Impossible de diffuser l'événement : CHANNEL_LAYER non configuré.")
            return
        logger.debug(f"Diffusion d'un événement au groupe board_{board_id} : {payload.get('action')}")
        async_to_sync(layer.group_send)(
            f"board_{board_id}",
            {"type": "broadcast", "payload": payload},
        )
    except Exception as e:
        logger.error(f"Erreur lors de la diffusion de l'événement au tableau {board_id} : {e}")
        pass


class CustomPasswordChangeView(PasswordChangeView):
    def form_valid(self, form):
        response = super().form_valid(form)
        # Notification par email (affichée en console en local)
        if self.request.user.email:
            send_mail(
                "Votre mot de passe a été modifié - EpiTrello",
                f"Bonjour {self.request.user.username},\n\nLe mot de passe de votre compte EpiTrello vient d'être modifié.\nSi vous n'êtes pas à l'origine de cette action, merci de contacter le support.",
                "security@epitrello.local",
                [self.request.user.email],
                fail_silently=True,
            )
        # On peut aussi ajouter une notification interne
        Notification.objects.create(
            user=self.request.user,
            message="Votre mot de passe a été modifié avec succès.",
            link=reverse("boards:profile")
        )
        return response

def _annotate_boards(boards_qs):
    boards = []
    for board in boards_qs:
        lists = list(board.lists.all())
        card_count = sum(len(board_list.cards.all()) for board_list in lists)
        board.list_count = len(lists)
        board.card_count = card_count
        boards.append(board)
    return boards


def _ensure_board_access(request, board_id):
    return get_object_or_404(Board, Q(owner=request.user) | Q(members=request.user), pk=board_id)


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
    owner_filter = (request.GET.get("owner") or "me")
    if not (owner_filter == "all" and request.user.is_staff):
        boards_qs = boards_qs.filter(Q(owner=request.user) | Q(members=request.user)).distinct()
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


@login_required
def board_detail(request, board_id):
    _ensure_board_access(request, board_id)
    sort = request.GET.get("sort", "position")
    sort_map = {
        "title": "title",
        "due_date": "due_date",
        "created_at": "-created_at",
        "position": "position",
        "label": "labels__name",
    }
    order_by = sort_map.get(sort, "position")

    cards_queryset = Card.objects.select_related("list").prefetch_related(
        "labels", "subtasks", "comments"
    )
    if sort == "label":
        cards_queryset = cards_queryset.annotate(
            first_label=Min("labels__name")
        ).order_by("first_label", "position")
    else:
        cards_queryset = cards_queryset.order_by(order_by)

    cards_prefetch = Prefetch("cards", queryset=cards_queryset)
    lists_prefetch = Prefetch(
        "lists",
        queryset=List.objects.prefetch_related(cards_prefetch).order_by("position"),
    )
    # On remplace l'appel direct à get_object_or_404 par board_obj déjà récupéré
    board = get_object_or_404(
        Board.objects.select_related("owner").prefetch_related(lists_prefetch).filter(Q(owner=request.user) | Q(members=request.user)).distinct(),
        pk=board_id,
    )

    raw_query = (request.GET.get("q") or "").strip()
    query = raw_query.lower()
    for board_list in board.lists.all():
        cards_queryset = board_list.cards.all()
        # Le filtrage IC contains sur le titre se fait en base de données si possible
        # mais ici cards_queryset est déjà un QuerySet ordonné grâce au Prefetch
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

    # Get all labels used in this board
    board_labels = Label.objects.filter(cards__list__board_id=board_id).distinct()

    context = {
        "board": board,
        "query": raw_query,
        "current_sort": sort,
        "board_labels": board_labels,
        "now": timezone.now(),
    }
    return render(request, "boards/board_detail.html", context)


@login_required
def global_search(request):
    query = (request.GET.get("q") or "").strip()
    boards = []
    cards = []

    if query:
        # Boards accessibles par l'utilisateur dont le titre contient la requête
        boards = Board.objects.filter(
            Q(title__icontains=query),
            Q(owner=request.user) | Q(members=request.user)
        ).distinct().select_related("owner")

        # Cards accessibles par l'utilisateur dont le titre ou la description contient la requête
        cards = Card.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query),
            Q(list__board__owner=request.user) | Q(list__board__members=request.user)
        ).distinct().select_related("list__board")

    context = {
        "query": query,
        "boards": boards,
        "cards": cards,
    }
    return render(request, "boards/global_search.html", context)


@login_required
@require_POST
def create_list(request, board_id):
    _ensure_board_access(request, board_id)
    board = get_object_or_404(Board, pk=board_id)
    title = (request.POST.get("title") or "").strip()
    if not title:
        return redirect("boards:board_detail", board_id=board.id)

    max_position = board.lists.aggregate(max_pos=Max("position"))["max_pos"] or 0
    List.objects.create(title=title, board=board, position=max_position + 1)
    messages.success(request, "Liste ajoutée avec succès.")

    return redirect("boards:board_detail", board_id=board.id)


@login_required
@require_POST
def create_card(request, board_id):
    _ensure_board_access(request, board_id)
    board = get_object_or_404(Board, pk=board_id)
    list_id = request.POST.get("list_id")
    title = (request.POST.get("title") or "").strip()
    description = (request.POST.get("description") or "").strip()

    if not title or not list_id:
        return redirect("boards:board_detail", board_id=board.id)

    board_list = get_object_or_404(List, pk=list_id, board=board)
    max_position = board_list.cards.aggregate(max_pos=Max("position"))["max_pos"] or 0
    new_card = Card.objects.create(
        title=title,
        description=description,
        list=board_list,
        position=max_position + 1,
    )
    _send_board_event(board.id, {"action": "card.created", "card": _card_response(new_card)})
    messages.success(request, "Carte créée avec succès.")
    return redirect("boards:board_detail", board_id=board.id)


@login_required
@require_POST
def reorder_lists(request, board_id):
    _ensure_board_access(request, board_id)
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
    _send_board_event(board.id, {"action": "lists.reordered", "order": order})
    return JsonResponse({"status": "ok"})


@login_required
@require_POST
def reorder_cards(request, board_id):
    _ensure_board_access(request, board_id)
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

    _send_board_event(board.id, {"action": "cards.reordered", "lists": lists_payload})
    return JsonResponse({"status": "ok"})


@login_required
@require_POST
def rename_board(request, board_id):
    _ensure_board_access(request, board_id)
    board = get_object_or_404(Board, pk=board_id)
    title = (request.POST.get("title") or "").strip()
    if title:
        board.title = title
        board.save(update_fields=["title"])
        messages.success(request, "Tableau renommé.")
    return redirect("boards:board_list")


@login_required
@require_POST
def delete_board(request, board_id):
    _ensure_board_access(request, board_id)
    board = get_object_or_404(Board, pk=board_id)
    board.delete()
    messages.success(request, "Tableau supprimé.")
    return redirect("boards:board_list")


@login_required
@require_POST
def delete_list(request, board_id, list_id):
    _ensure_board_access(request, board_id)
    board = get_object_or_404(Board, pk=board_id)
    board_list = get_object_or_404(List, pk=list_id, board=board)
    list_id_val = board_list.id
    board_list.delete()
    _send_board_event(board.id, {"action": "list.deleted", "list_id": list_id_val})
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
        "checklists",
        "checklists__items",
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
    
    # New checklists structure
    checklists = []
    for cl in card.checklists.all():
        items = [
            {"id": item.id, "title": item.title, "is_completed": item.is_completed}
            for item in cl.items.all()
        ]
        total = len(items)
        completed = sum(1 for item in items if item["is_completed"])
        percent = int((completed / total * 100)) if total > 0 else 0
        checklists.append({
            "id": cl.id,
            "title": cl.title,
            "items": items,
            "total_items": total,
            "completed_items": completed,
            "percent": percent
        })

    # Legacy subtasks (without checklist)
    standalone_subtasks = [
        {"id": subtask.id, "title": subtask.title, "is_completed": subtask.is_completed}
        for subtask in card.subtasks.all() if subtask.checklist_id is None
    ]
    
    all_subtasks = [
        {"id": s.id, "is_completed": s.is_completed}
        for s in card.subtasks.all()
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

    assigned_users = [
        {"id": u.id, "username": u.username, "initial": u.username[0].upper()}
        for u in card.assigned_to.all()
    ]
    assigned_ids = {u["id"] for u in assigned_users}
    board = card.list.board
    members = [
        {
            "id": u.id,
            "username": u.username,
            "initial": u.username[0].upper(),
            "is_assigned": u.id in assigned_ids
        }
        for u in User.objects.filter(Q(owned_boards=board) | Q(joined_boards=board)).distinct().order_by("username")
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
        "checklists": checklists,
        "subtasks": standalone_subtasks, # compatibility
        "completed_subtasks": sum(1 for s in all_subtasks if s["is_completed"]),
        "total_subtasks": len(all_subtasks),
        "comments": comments,
        "comment_count": len(comments),
        "assigned_users": assigned_users,
        "members": members,
    }


def _get_card(board_id, card_id):
    return get_object_or_404(_card_queryset(), pk=card_id, list__board_id=board_id)


@login_required
@require_http_methods(["GET"])
def card_detail(request, board_id, card_id):
    _ensure_board_access(request, board_id)
    card = _get_card(board_id, card_id)
    return JsonResponse(_card_response(card))


@login_required
@require_POST
def update_card(request, board_id, card_id):
    _ensure_board_access(request, board_id)
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
    updated = _get_card(board_id, card_id)
    _send_board_event(board_id, {"action": "card.updated", "card": _card_response(updated)})
    return JsonResponse(_card_response(updated))


@login_required
@require_POST
def toggle_card_label(request, board_id, card_id):
    _ensure_board_access(request, board_id)
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
    updated = _get_card(board_id, card_id)
    _send_board_event(board_id, {"action": "card.updated", "card": _card_response(updated)})
    return JsonResponse(_card_response(updated))


@login_required
@require_POST
def create_subtask(request, board_id, card_id):
    _ensure_board_access(request, board_id)
    card = _get_card(board_id, card_id)
    payload = _get_payload(request)
    title = (payload.get("title") or "").strip()
    checklist_id = payload.get("checklist_id")
    if not title:
        return HttpResponseBadRequest("Le titre de l'élément est requis.")
    
    checklist = None
    if checklist_id:
        checklist = get_object_or_404(Checklist, pk=checklist_id, card=card)
    
    Subtask.objects.create(card=card, checklist=checklist, title=title)
    updated = _get_card(board_id, card_id)
    _send_board_event(board_id, {"action": "card.updated", "card": _card_response(updated)})
    return JsonResponse(_card_response(updated))


@login_required
@require_POST
def create_checklist(request, board_id, card_id):
    _ensure_board_access(request, board_id)
    card = _get_card(board_id, card_id)
    payload = _get_payload(request)
    title = (payload.get("title") or "Checklist").strip()
    Checklist.objects.create(card=card, title=title)
    updated = _get_card(board_id, card_id)
    _send_board_event(board_id, {"action": "card.updated", "card": _card_response(updated)})
    return JsonResponse(_card_response(updated))


@login_required
@require_POST
def delete_checklist(request, board_id, card_id, checklist_id):
    _ensure_board_access(request, board_id)
    card = _get_card(board_id, card_id)
    checklist = get_object_or_404(Checklist, pk=checklist_id, card=card)
    checklist.delete()
    updated = _get_card(board_id, card_id)
    _send_board_event(board_id, {"action": "card.updated", "card": _card_response(updated)})
    return JsonResponse(_card_response(updated))


@login_required
@require_POST
def toggle_subtask(request, board_id, card_id, subtask_id):
    _ensure_board_access(request, board_id)
    card = _get_card(board_id, card_id)
    subtask = get_object_or_404(Subtask, pk=subtask_id, card=card)
    subtask.is_completed = not subtask.is_completed
    subtask.save(update_fields=["is_completed"])
    updated = _get_card(board_id, card_id)
    _send_board_event(board_id, {"action": "card.updated", "card": _card_response(updated)})
    return JsonResponse(_card_response(updated))


@login_required
@require_POST
def delete_subtask(request, board_id, card_id, subtask_id):
    _ensure_board_access(request, board_id)
    card = _get_card(board_id, card_id)
    subtask = get_object_or_404(Subtask, pk=subtask_id, card=card)
    subtask.delete()
    updated = _get_card(board_id, card_id)
    _send_board_event(board_id, {"action": "card.updated", "card": _card_response(updated)})
    return JsonResponse(_card_response(updated))


@login_required
@require_POST
def create_comment(request, board_id, card_id):
    _ensure_board_access(request, board_id)
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentification requise."}, status=403)
    card = _get_card(board_id, card_id)
    payload = _get_payload(request)
    content = (payload.get("content") or "").strip()
    if not content:
        return HttpResponseBadRequest("Le commentaire est requis.")
    Comment.objects.create(card=card, author=request.user, content=content)
    updated = _get_card(board_id, card_id)
    _send_board_event(board_id, {"action": "card.updated", "card": _card_response(updated)})
    return JsonResponse(_card_response(updated))


@login_required
@require_POST
def create_label(request, board_id, card_id):
    _ensure_board_access(request, board_id)
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
    updated = _get_card(board_id, card_id)
    _send_board_event(board_id, {"action": "card.updated", "card": _card_response(updated)})
    return JsonResponse(_card_response(updated))


@login_required
@require_POST
def delete_label(request, board_id, card_id, label_id):
    _ensure_board_access(request, board_id)
    card = _get_card(board_id, card_id)
    label = get_object_or_404(Label, pk=label_id)
    card.labels.remove(label)
    if not label.cards.exists():
        label.delete()
    updated = _get_card(board_id, card_id)
    _send_board_event(board_id, {"action": "card.updated", "card": _card_response(updated)})
    return JsonResponse(_card_response(updated))


@login_required
@require_POST
def delete_card(request, board_id, card_id):
    _ensure_board_access(request, board_id)
    card = _get_card(board_id, card_id)
    card_id_value = card.id
    card.delete()
    _send_board_event(board_id, {"action": "card.deleted", "card_id": card_id_value})
    return JsonResponse({"status": "deleted", "card_id": card_id_value})


@login_required
@require_POST
def toggle_card_assignment(request, board_id, card_id):
    _ensure_board_access(request, board_id)
    card = _get_card(board_id, card_id)
    payload = _get_payload(request)
    user_id = payload.get("user_id")
    if not user_id:
        return HttpResponseBadRequest("user_id requis.")
    user_to_assign = get_object_or_404(User, Q(owned_boards__id=board_id) | Q(joined_boards__id=board_id), pk=user_id)
    if card.assigned_to.filter(pk=user_to_assign.id).exists():
        card.assigned_to.remove(user_to_assign)
    else:
        card.assigned_to.add(user_to_assign)
        if user_to_assign != request.user:
            Notification.objects.create(
                user=user_to_assign,
                message=f"Vous avez été assigné à la carte '{card.title}'",
                link=reverse("boards:board_detail", kwargs={"board_id": board_id})
            )
    updated = _get_card(board_id, card_id)
    _send_board_event(board_id, {"action": "card.updated", "card": _card_response(updated)})
    return JsonResponse(_card_response(updated))


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


@login_required
@require_POST
def invite_member(request, board_id):
    board = _ensure_board_access(request, board_id)
    if request.user != board.owner:
        messages.error(request, "Seul le propriétaire peut inviter des membres.")
        return redirect("boards:board_detail", board_id=board.id)
    username = (request.POST.get("username") or "").strip()
    if not username:
        messages.error(request, "Nom d'utilisateur requis.")
        return redirect("boards:board_detail", board_id=board.id)

    try:
        user_to_invite = User.objects.get(username=username)
    except User.DoesNotExist:
        messages.error(request, f"L'utilisateur '{username}' n'existe pas.")
        return redirect("boards:board_detail", board_id=board.id)

    if user_to_invite == board.owner or board.members.filter(pk=user_to_invite.pk).exists():
        messages.info(request, f"{username} est déjà membre de ce tableau.")
    else:
        board.members.add(user_to_invite)
        Notification.objects.create(
            user=user_to_invite,
            message=f"Vous avez été invité au tableau '{board.title}' par {request.user.username}",
            link=reverse("boards:board_detail", kwargs={"board_id": board.id})
        )
        messages.success(request, f"{username} a été invité au tableau.")

    return redirect("boards:board_detail", board_id=board.id)


@login_required
def manage_members(request, board_id):
    board = _ensure_board_access(request, board_id)
    if request.user != board.owner:
        messages.error(request, "Seul le propriétaire peut gérer les membres.")
        return redirect("boards:board_detail", board_id=board.id)
    
    context = {
        "board": board,
        "members": board.members.all(),
    }
    return render(request, "boards/manage_members.html", context)


@login_required
@require_POST
def remove_member(request, board_id, user_id):
    board = _ensure_board_access(request, board_id)
    if request.user != board.owner:
        return JsonResponse({"error": "Action non autorisée."}, status=403)
    
    user_to_remove = get_object_or_404(User, pk=user_id)
    board.members.remove(user_to_remove)
    
    return JsonResponse({"status": "ok", "message": f"{user_to_remove.username} retiré du tableau."})


def home(request):
    primary_href = (reverse("boards:board_list") + "?new=1") if request.user.is_authenticated else reverse("boards:board_list")
    secondary_href = "#features"
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


def logout_view(request):
    logout(request)
    messages.success(request, "Déconnexion effectuée.")
    return redirect("home")


def test_404(request):
    return render(request, "404.html", status=404)


def test_500(request):
    return render(request, "500.html", status=500)


def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            messages.success(request, "Inscription réussie !")
            return redirect("home")
    else:
        form = UserCreationForm()
    return render(request, "registration/signup.html", {"form": form})


@login_required
def profile(request):
    boards_count = Board.objects.filter(owner=request.user).count()
    notifications = request.user.notifications.all()[:10]
    context = {
        "user": request.user,
        "boards_count": boards_count,
        "notifications": notifications,
    }
    return render(request, "boards/profile.html", context)


@login_required
def notifications_list(request):
    notifications = request.user.notifications.all()
    context = {
        "notifications": notifications,
    }
    return render(request, "boards/notifications.html", context)


@login_required
@require_POST
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, pk=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({"status": "ok"})


@login_required
@require_POST
def mark_all_notifications_read(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return JsonResponse({"status": "ok"})


@login_required
def export_board(request, board_id, export_format):
    board = _ensure_board_access(request, board_id)
    
    # Eager load all related data
    board = Board.objects.prefetch_related(
        Prefetch('lists', queryset=List.objects.prefetch_related(
            Prefetch('cards', queryset=Card.objects.prefetch_related(
                'assigned_to', 'labels', 'subtasks', 
                Prefetch('comments', queryset=Comment.objects.select_related('author'))
            ).order_by('position'))
        ).order_by('position')),
        'owner',
        'members'
    ).get(pk=board_id)

    if export_format == "json":
        board_data = {
            "id": board.id,
            "title": board.title,
            "owner": board.owner.username,
            "members": [member.username for member in board.members.all()],
            "lists": []
        }
        for lst in board.lists.all():
            list_data = {
                "id": lst.id,
                "title": lst.title,
                "position": lst.position,
                "cards": []
            }
            for card in lst.cards.all():
                card_data = {
                    "id": card.id,
                    "title": card.title,
                    "description": card.description,
                    "position": card.position,
                    "due_date": card.due_date.isoformat() if card.due_date else None,
                    "assigned_to": [user.username for user in card.assigned_to.all()],
                    "labels": [label.name for label in card.labels.all()],
                    "subtasks": [{"title": s.title, "is_completed": s.is_completed} for s in card.subtasks.all()],
                    "comments": [{
                        "author": c.author.username,
                        "content": c.content,
                        "created_at": c.created_at.isoformat()
                    } for c in card.comments.all()]
                }
                list_data["cards"].append(card_data)
            board_data["lists"].append(list_data)
        
        response = JsonResponse(board_data, json_dumps_params={'indent': 2})
        response['Content-Disposition'] = f'attachment; filename="{board.title}.json"'
        return response

    elif export_format == "csv":
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{board.title}.csv"'
        
        writer = csv.writer(response)
        # CSV Header
        writer.writerow([
            'Card ID', 'Card Title', 'Card Description', 'List Name', 'Position', 
            'Due Date', 'Assigned Members', 'Labels', 'Subtasks Count', 'Completed Subtasks', 'Comments Count'
        ])
        
        for lst in board.lists.all():
            for card in lst.cards.all():
                assigned_members = ", ".join([user.username for user in card.assigned_to.all()])
                labels = ", ".join([label.name for label in card.labels.all()])
                subtasks = card.subtasks.all()
                completed_subtasks = sum(1 for s in subtasks if s.is_completed)
                
                writer.writerow([
                    card.id,
                    card.title,
                    card.description,
                    lst.title,
                    card.position,
                    card.due_date.strftime('%Y-%m-%d %H:%M') if card.due_date else '',
                    assigned_members,
                    labels,
                    len(subtasks),
                    completed_subtasks,
                    card.comments.count()
                ])
        return response

    return HttpResponseBadRequest("Invalid format specified.")

