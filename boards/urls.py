from django.urls import path
from . import views

app_name = "boards"

urlpatterns = [
    path("", views.board_list, name="board_list"),
    path("board/<int:board_id>/", views.board_detail, name="board_detail"),
    path(
        "board/<int:board_id>/lists/create",
        views.create_list,
        name="create_list",
    ),
    path(
        "board/<int:board_id>/cards/create",
        views.create_card,
        name="create_card",
    ),
    path(
        "board/<int:board_id>/lists/reorder",
        views.reorder_lists,
        name="reorder_lists",
    ),
    path(
        "board/<int:board_id>/lists/<int:list_id>/delete",
        views.delete_list,
        name="delete_list",
    ),
    path(
        "board/<int:board_id>/reorder",
        views.reorder_cards,
        name="reorder_cards",
    ),
    path("board/<int:board_id>/rename", views.rename_board, name="rename_board"),
    path("board/<int:board_id>/delete", views.delete_board, name="delete_board"),
    path("board/<int:board_id>/cards/<int:card_id>/", views.card_detail, name="card_detail"),
    path("board/<int:board_id>/cards/<int:card_id>/update", views.update_card, name="update_card"),
    path("board/<int:board_id>/cards/<int:card_id>/labels/toggle", views.toggle_card_label, name="toggle_card_label"),
    path("board/<int:board_id>/cards/<int:card_id>/subtasks/create", views.create_subtask, name="create_subtask"),
    path("board/<int:board_id>/cards/<int:card_id>/subtasks/<int:subtask_id>/toggle", views.toggle_subtask, name="toggle_subtask"),
    path("board/<int:board_id>/cards/<int:card_id>/subtasks/<int:subtask_id>/delete", views.delete_subtask, name="delete_subtask"),
    path("board/<int:board_id>/cards/<int:card_id>/comments/create", views.create_comment, name="create_comment"),
    path("board/<int:board_id>/cards/<int:card_id>/labels/create", views.create_label, name="create_label"),
    path("board/<int:board_id>/cards/<int:card_id>/labels/<int:label_id>/delete", views.delete_label, name="delete_label"),
    path("board/<int:board_id>/cards/<int:card_id>/delete", views.delete_card, name="delete_card"),
    path("boards/create", views.create_board, name="create_board"),
]
