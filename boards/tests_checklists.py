from django.test import TestCase, Client
from django.contrib.auth.models import User
from boards.models import Board, List, Card, Checklist, Subtask
from django.urls import reverse
import json

class ChecklistTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client = Client()
        self.client.login(username="testuser", password="password")
        self.board = Board.objects.create(title="Test Board", owner=self.user)
        self.list = List.objects.create(title="Test List", board=self.board)
        self.card = Card.objects.create(title="Test Card", list=self.list)

    def test_create_checklist(self):
        url = reverse("boards:create_checklist", kwargs={"board_id": self.board.id, "card_id": self.card.id})
        response = self.client.post(url, data=json.dumps({"title": "My Checklist"}), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Checklist.objects.count(), 1)
        self.assertEqual(Checklist.objects.first().title, "My Checklist")

    def test_create_subtask_in_checklist(self):
        checklist = Checklist.objects.create(title="My Checklist", card=self.card)
        url = reverse("boards:create_subtask", kwargs={"board_id": self.board.id, "card_id": self.card.id})
        response = self.client.post(url, data=json.dumps({"title": "Item 1", "checklist_id": checklist.id}), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Subtask.objects.count(), 1)
        subtask = Subtask.objects.first()
        self.assertEqual(subtask.title, "Item 1")
        self.assertEqual(subtask.checklist, checklist)

    def test_delete_checklist(self):
        checklist = Checklist.objects.create(title="My Checklist", card=self.card)
        Subtask.objects.create(title="Item 1", card=self.card, checklist=checklist)
        url = reverse("boards:delete_checklist", kwargs={"board_id": self.board.id, "card_id": self.card.id, "checklist_id": checklist.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Checklist.objects.count(), 0)
        self.assertEqual(Subtask.objects.count(), 0) # Cascade delete

    def test_card_detail_returns_checklists(self):
        checklist = Checklist.objects.create(title="My Checklist", card=self.card)
        Subtask.objects.create(title="Item 1", card=self.card, checklist=checklist, is_completed=True)
        Subtask.objects.create(title="Item 2", card=self.card, checklist=checklist, is_completed=False)
        
        url = reverse("boards:card_detail", kwargs={"board_id": self.board.id, "card_id": self.card.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["checklists"]), 1)
        self.assertEqual(data["checklists"][0]["title"], "My Checklist")
        self.assertEqual(len(data["checklists"][0]["items"]), 2)
        self.assertEqual(data["checklists"][0]["percent"], 50)
