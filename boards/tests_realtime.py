from unittest.mock import patch
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Board, List, Card
import json


class DummyLayer:
    def __init__(self):
        self.calls = []

    async def group_send(self, group, event):
        self.calls.append((group, event))


class ChannelsBroadcastTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="owner", password="pass123!A")
        self.board = Board.objects.create(title="B", owner=self.user)
        self.list = List.objects.create(title="L", board=self.board, position=1)
        self.card = Card.objects.create(title="C1", list=self.list)
        self.client.login(username="owner", password="pass123!A")

    def test_update_card_triggers_broadcast(self):
        dummy = DummyLayer()
        with patch("boards.views.get_channel_layer", return_value=dummy):
            url = reverse("boards:update_card", kwargs={"board_id": self.board.id, "card_id": self.card.id})
            payload = {"title": "C1 updated", "description": "d"}
            res = self.client.post(url, data=json.dumps(payload), content_type="application/json")
            self.assertEqual(res.status_code, 200)
            # au moins un envoi broadcast
            self.assertTrue(dummy.calls)
            group, event = dummy.calls[-1]
            self.assertEqual(group, f"board_{self.board.id}")
            self.assertEqual(event.get("type"), "broadcast")
            self.assertEqual(event.get("payload", {}).get("action"), "card.updated")

    def test_delete_card_triggers_broadcast(self):
        dummy = DummyLayer()
        with patch("boards.views.get_channel_layer", return_value=dummy):
            url = reverse("boards:delete_card", kwargs={"board_id": self.board.id, "card_id": self.card.id})
            res = self.client.post(url)
            self.assertEqual(res.status_code, 200)
            self.assertTrue(dummy.calls)
            group, event = dummy.calls[-1]
            self.assertEqual(group, f"board_{self.board.id}")
            self.assertEqual(event.get("payload", {}).get("action"), "card.deleted")
