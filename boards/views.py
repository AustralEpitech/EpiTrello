from django.shortcuts import render
from .models import Board


def board_list(request):
    boards = Board.objects.all()
    return render(request, "boards/board_list.html", {"boards": boards})


def board_detail(request, board_id):
    board = Board.objects.get(id=board_id)
    return render(request, "boards/board_detail.html", {"board": board})
