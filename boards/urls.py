from django.urls import path
from . import views

app_name = "boards"

urlpatterns = [
    path("", views.board_list, name="board_list"),
    path("search/", views.global_search, name="global_search"),
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
    path("board/<int:board_id>/export/<str:export_format>/", views.export_board, name="export_board"),
    path("board/<int:board_id>/invite", views.invite_member, name="invite_member"),
    path("board/<int:board_id>/members", views.manage_members, name="manage_members"),
    path("board/<int:board_id>/members/<int:user_id>/remove", views.remove_member, name="remove_member"),
    path("board/<int:board_id>/cards/<int:card_id>/", views.card_detail, name="card_detail"),
    path("board/<int:board_id>/cards/<int:card_id>/update", views.update_card, name="update_card"),
    path("board/<int:board_id>/cards/<int:card_id>/labels/toggle", views.toggle_card_label, name="toggle_card_label"),
    path("board/<int:board_id>/cards/<int:card_id>/subtasks/create", views.create_subtask, name="create_subtask"),
    path("board/<int:board_id>/cards/<int:card_id>/checklists/create", views.create_checklist, name="create_checklist"),
    path("board/<int:board_id>/cards/<int:card_id>/checklists/<int:checklist_id>/delete", views.delete_checklist, name="delete_checklist"),
    path("board/<int:board_id>/cards/<int:card_id>/subtasks/<int:subtask_id>/toggle", views.toggle_subtask, name="toggle_subtask"),
    path("board/<int:board_id>/cards/<int:card_id>/subtasks/<int:subtask_id>/delete", views.delete_subtask, name="delete_subtask"),
    path("board/<int:board_id>/cards/<int:card_id>/comments/create", views.create_comment, name="create_comment"),
    path("board/<int:board_id>/cards/<int:card_id>/labels/create", views.create_label, name="create_label"),
    path("board/<int:board_id>/cards/<int:card_id>/labels/<int:label_id>/delete", views.delete_label, name="delete_label"),
    path("board/<int:board_id>/cards/<int:card_id>/delete", views.delete_card, name="delete_card"),
    path("board/<int:board_id>/cards/<int:card_id>/assign", views.toggle_card_assignment, name="toggle_card_assignment"),
    path("boards/create", views.create_board, name="create_board"),
    # Routes de test pour les pages d'erreur
    path("test-404/", views.test_404, name="test_404"),
    path("test-500/", views.test_500, name="test_500"),
    path("signup/", views.signup, name="signup"),
    path("profile/", views.profile, name="profile"),
    path("notifications/", views.notifications_list, name="notifications_list"),
    path("notifications/<int:notification_id>/read", views.mark_notification_read, name="mark_notification_read"),
    path("notifications/read-all", views.mark_all_notifications_read, name="mark_all_notifications_read"),
]
