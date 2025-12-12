from django.contrib import admin
from .models import Board, List, Card, Label, Subtask, Comment


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "created_at")
    list_filter = ("created_at",)
    search_fields = ("title",)


@admin.register(List)
class ListAdmin(admin.ModelAdmin):
    list_display = ("title", "board", "position")
    list_filter = ("board",)
    search_fields = ("title",)


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ("title", "list", "due_date", "position")
    list_filter = ("list", "due_date")
    search_fields = ("title", "description")
    filter_horizontal = ("assigned_to", "labels")


@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = ("name", "color")


@admin.register(Subtask)
class SubtaskAdmin(admin.ModelAdmin):
    list_display = ("title", "card", "is_completed")
    list_filter = ("is_completed",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("author", "card", "created_at")
    list_filter = ("created_at",)
