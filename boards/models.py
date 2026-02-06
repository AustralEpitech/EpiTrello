from django.db import models
from django.contrib.auth.models import User


class Board(models.Model):
    title = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_boards")
    members = models.ManyToManyField(User, related_name="joined_boards", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class List(models.Model):
    title = models.CharField(max_length=100)
    board = models.ForeignKey(
        Board, on_delete=models.CASCADE, related_name="lists"
    )
    position = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["position"]

    def __str__(self):
        return f"{self.board.title} - {self.title}"


class Label(models.Model):
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7, default="#3b82f6")  # Code hex
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Card(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    list = models.ForeignKey(
        List, on_delete=models.CASCADE, related_name="cards"
    )
    position = models.IntegerField(default=0)
    due_date = models.DateTimeField(blank=True, null=True)
    assigned_to = models.ManyToManyField(
        User, blank=True, related_name="assigned_cards"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    labels = models.ManyToManyField(Label, blank=True, related_name="cards")

    class Meta:
        ordering = ["position"]

    def __str__(self):
        return f"{self.title} ({self.list.title})"


class Checklist(models.Model):
    title = models.CharField(max_length=100, default="Checklist")
    card = models.ForeignKey(
        "Card", on_delete=models.CASCADE, related_name="checklists"
    )
    position = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["position"]

    def __str__(self):
        return f"{self.title} (Card: {self.card.title})"


class Subtask(models.Model):
    title = models.CharField(max_length=100)
    card = models.ForeignKey(
        Card, on_delete=models.CASCADE, related_name="subtasks"
    )
    checklist = models.ForeignKey(
        Checklist, on_delete=models.CASCADE, related_name="items", null=True, blank=True
    )
    is_completed = models.BooleanField(default=False)
    position = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["position", "created_at"]

    def __str__(self):
        return f"{self.title} (Card: {self.card.title})"


class Comment(models.Model):
    content = models.TextField()
    card = models.ForeignKey(
        Card, on_delete=models.CASCADE, related_name="comments"
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Comment by {self.author} on {self.card.title}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.CharField(max_length=255)
    link = models.CharField(max_length=255, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"
