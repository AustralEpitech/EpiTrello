from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from boards.models import Board, List, Card, Label, Comment, Notification
import json


class ReorderTests(TestCase):
    """Tests pour les endpoints de réordonnancement"""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client = Client()
        self.client.login(username="testuser", password="password")
        self.board = Board.objects.create(title="Test Board", owner=self.user)
        self.list1 = List.objects.create(title="List 1", board=self.board, position=1)
        self.list2 = List.objects.create(title="List 2", board=self.board, position=2)
        self.card1 = Card.objects.create(title="Card 1", list=self.list1, position=1)
        self.card2 = Card.objects.create(title="Card 2", list=self.list1, position=2)

    def test_reorder_lists_success(self):
        """Test de réordonnancement des listes avec succès"""
        url = reverse("boards:reorder_lists", kwargs={"board_id": self.board.id})
        payload = {"order": [self.list2.id, self.list1.id]}
        response = self.client.post(url, data=json.dumps(payload), content_type="application/json")
        
        self.assertEqual(response.status_code, 200)
        self.list1.refresh_from_db()
        self.list2.refresh_from_db()
        self.assertEqual(self.list2.position, 1)
        self.assertEqual(self.list1.position, 2)

    def test_reorder_lists_invalid_json(self):
        """Test de réordonnancement avec JSON invalide"""
        url = reverse("boards:reorder_lists", kwargs={"board_id": self.board.id})
        response = self.client.post(url, data="invalid json", content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_reorder_lists_invalid_order_format(self):
        """Test de réordonnancement avec format d'ordre invalide"""
        url = reverse("boards:reorder_lists", kwargs={"board_id": self.board.id})
        payload = {"order": "not a list"}
        response = self.client.post(url, data=json.dumps(payload), content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_reorder_cards_success(self):
        """Test de réordonnancement des cartes avec succès"""
        url = reverse("boards:reorder_cards", kwargs={"board_id": self.board.id})
        payload = {
            "lists": [
                {"id": self.list1.id, "card_ids": [self.card2.id, self.card1.id]}
            ]
        }
        response = self.client.post(url, data=json.dumps(payload), content_type="application/json")
        
        self.assertEqual(response.status_code, 200)
        self.card1.refresh_from_db()
        self.card2.refresh_from_db()
        self.assertEqual(self.card2.position, 1)
        self.assertEqual(self.card1.position, 2)

    def test_reorder_cards_move_to_different_list(self):
        """Test de déplacement de carte vers une autre liste"""
        url = reverse("boards:reorder_cards", kwargs={"board_id": self.board.id})
        payload = {
            "lists": [
                {"id": self.list1.id, "card_ids": [self.card2.id]},
                {"id": self.list2.id, "card_ids": [self.card1.id]}
            ]
        }
        response = self.client.post(url, data=json.dumps(payload), content_type="application/json")
        
        self.assertEqual(response.status_code, 200)
        self.card1.refresh_from_db()
        self.assertEqual(self.card1.list_id, self.list2.id)

    def test_reorder_cards_invalid_json(self):
        """Test de réordonnancement de cartes avec JSON invalide"""
        url = reverse("boards:reorder_cards", kwargs={"board_id": self.board.id})
        response = self.client.post(url, data="invalid", content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_reorder_cards_invalid_lists_format(self):
        """Test de réordonnancement avec format invalide"""
        url = reverse("boards:reorder_cards", kwargs={"board_id": self.board.id})
        payload = {"lists": "not a list"}
        response = self.client.post(url, data=json.dumps(payload), content_type="application/json")
        self.assertEqual(response.status_code, 400)


class LabelTests(TestCase):
    """Tests pour les endpoints de labels"""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client = Client()
        self.client.login(username="testuser", password="password")
        self.board = Board.objects.create(title="Test Board", owner=self.user)
        self.list = List.objects.create(title="Test List", board=self.board)
        self.card = Card.objects.create(title="Test Card", list=self.list)

    def test_create_label_success(self):
        """Test de création d'un label avec succès"""
        url = reverse("boards:create_label", kwargs={"board_id": self.board.id, "card_id": self.card.id})
        payload = {"name": "Bug", "color": "#ff0000"}
        response = self.client.post(url, data=json.dumps(payload), content_type="application/json")
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Label.objects.filter(name="Bug").exists())
        label = Label.objects.get(name="Bug")
        self.assertEqual(label.color, "#ff0000")
        self.assertTrue(self.card.labels.filter(id=label.id).exists())

    def test_create_label_invalid_color(self):
        """Test de création de label avec couleur invalide (fallback à défaut)"""
        url = reverse("boards:create_label", kwargs={"board_id": self.board.id, "card_id": self.card.id})
        payload = {"name": "Test", "color": "invalid"}
        response = self.client.post(url, data=json.dumps(payload), content_type="application/json")
        
        self.assertEqual(response.status_code, 200)
        label = Label.objects.get(name="Test")
        self.assertEqual(label.color, "#3b82f6")  # Couleur par défaut

    def test_create_label_missing_name(self):
        """Test de création de label sans nom"""
        url = reverse("boards:create_label", kwargs={"board_id": self.board.id, "card_id": self.card.id})
        payload = {"color": "#ff0000"}
        response = self.client.post(url, data=json.dumps(payload), content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_toggle_card_label_add(self):
        """Test d'ajout d'un label à une carte"""
        label = Label.objects.create(name="Feature", color="#00ff00")
        url = reverse("boards:toggle_card_label", kwargs={"board_id": self.board.id, "card_id": self.card.id})
        payload = {"label_id": label.id}
        response = self.client.post(url, data=json.dumps(payload), content_type="application/json")
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.card.labels.filter(id=label.id).exists())

    def test_toggle_card_label_remove(self):
        """Test de retrait d'un label d'une carte"""
        label = Label.objects.create(name="Feature", color="#00ff00")
        self.card.labels.add(label)
        
        url = reverse("boards:toggle_card_label", kwargs={"board_id": self.board.id, "card_id": self.card.id})
        payload = {"label_id": label.id}
        response = self.client.post(url, data=json.dumps(payload), content_type="application/json")
        
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.card.labels.filter(id=label.id).exists())

    def test_toggle_card_label_missing_label_id(self):
        """Test de toggle sans label_id"""
        url = reverse("boards:toggle_card_label", kwargs={"board_id": self.board.id, "card_id": self.card.id})
        payload = {}
        response = self.client.post(url, data=json.dumps(payload), content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_delete_label_success(self):
        """Test de suppression d'un label d'une carte"""
        label = Label.objects.create(name="Obsolete", color="#888888")
        self.card.labels.add(label)
        
        url = reverse("boards:delete_label", kwargs={"board_id": self.board.id, "card_id": self.card.id, "label_id": label.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.card.labels.filter(id=label.id).exists())

    def test_delete_label_orphan_cleanup(self):
        """Test que le label orphelin est supprimé automatiquement"""
        label = Label.objects.create(name="ToDelete", color="#999999")
        self.card.labels.add(label)
        
        url = reverse("boards:delete_label", kwargs={"board_id": self.board.id, "card_id": self.card.id, "label_id": label.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 200)
        # Le label doit être supprimé car il n'est plus utilisé
        self.assertFalse(Label.objects.filter(id=label.id).exists())


class CommentTests(TestCase):
    """Tests pour les endpoints de commentaires"""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client = Client()
        self.client.login(username="testuser", password="password")
        self.board = Board.objects.create(title="Test Board", owner=self.user)
        self.list = List.objects.create(title="Test List", board=self.board)
        self.card = Card.objects.create(title="Test Card", list=self.list)

    def test_create_comment_success(self):
        """Test de création de commentaire avec succès"""
        url = reverse("boards:create_comment", kwargs={"board_id": self.board.id, "card_id": self.card.id})
        payload = {"content": "This is a test comment"}
        response = self.client.post(url, data=json.dumps(payload), content_type="application/json")
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Comment.objects.filter(content="This is a test comment").exists())
        comment = Comment.objects.get(content="This is a test comment")
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.card, self.card)

    def test_create_comment_empty_content(self):
        """Test de création de commentaire vide"""
        url = reverse("boards:create_comment", kwargs={"board_id": self.board.id, "card_id": self.card.id})
        payload = {"content": ""}
        response = self.client.post(url, data=json.dumps(payload), content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_create_comment_whitespace_only(self):
        """Test de création de commentaire avec espaces seulement"""
        url = reverse("boards:create_comment", kwargs={"board_id": self.board.id, "card_id": self.card.id})
        payload = {"content": "   "}
        response = self.client.post(url, data=json.dumps(payload), content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_comments_in_card_detail(self):
        """Test que les commentaires sont retournés dans le détail de la carte"""
        Comment.objects.create(card=self.card, author=self.user, content="Comment 1")
        Comment.objects.create(card=self.card, author=self.user, content="Comment 2")
        
        url = reverse("boards:card_detail", kwargs={"board_id": self.board.id, "card_id": self.card.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["comments"]), 2)
        self.assertEqual(data["comment_count"], 2)


class NotificationTests(TestCase):
    """Tests pour les endpoints de notifications"""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client = Client()
        self.client.login(username="testuser", password="password")

    def test_notifications_list_page(self):
        """Test de la page liste des notifications"""
        Notification.objects.create(user=self.user, message="Test notification 1")
        Notification.objects.create(user=self.user, message="Test notification 2")
        
        url = reverse("boards:notifications_list")
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test notification 1")
        self.assertContains(response, "Test notification 2")

    def test_mark_notification_read(self):
        """Test de marquage d'une notification comme lue"""
        notif = Notification.objects.create(user=self.user, message="Unread notification")
        self.assertFalse(notif.is_read)
        
        url = reverse("boards:mark_notification_read", kwargs={"notification_id": notif.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 200)
        notif.refresh_from_db()
        self.assertTrue(notif.is_read)

    def test_mark_notification_read_wrong_user(self):
        """Test qu'un utilisateur ne peut pas marquer la notification d'un autre"""
        other_user = User.objects.create_user(username="other", password="password")
        notif = Notification.objects.create(user=other_user, message="Someone else's notification")
        
        url = reverse("boards:mark_notification_read", kwargs={"notification_id": notif.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 404)

    def test_mark_all_notifications_read(self):
        """Test de marquage de toutes les notifications comme lues"""
        Notification.objects.create(user=self.user, message="Notif 1", is_read=False)
        Notification.objects.create(user=self.user, message="Notif 2", is_read=False)
        Notification.objects.create(user=self.user, message="Notif 3", is_read=True)
        
        url = reverse("boards:mark_all_notifications_read")
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 200)
        unread_count = Notification.objects.filter(user=self.user, is_read=False).count()
        self.assertEqual(unread_count, 0)


class ExportTests(TestCase):
    """Tests pour les endpoints d'export"""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client = Client()
        self.client.login(username="testuser", password="password")
        self.board = Board.objects.create(title="Export Test Board", owner=self.user)
        self.list = List.objects.create(title="Test List", board=self.board, position=1)
        self.card = Card.objects.create(
            title="Test Card",
            description="Test description",
            list=self.list,
            position=1
        )

    def test_export_board_json(self):
        """Test d'export en JSON"""
        url = reverse("boards:export_board", kwargs={"board_id": self.board.id, "export_format": "json"})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertIn('attachment', response['Content-Disposition'])
        
        data = response.json()
        self.assertEqual(data['title'], "Export Test Board")
        self.assertEqual(data['owner'], "testuser")
        self.assertEqual(len(data['lists']), 1)
        self.assertEqual(data['lists'][0]['title'], "Test List")
        self.assertEqual(len(data['lists'][0]['cards']), 1)
        self.assertEqual(data['lists'][0]['cards'][0]['title'], "Test Card")

    def test_export_board_csv(self):
        """Test d'export en CSV"""
        url = reverse("boards:export_board", kwargs={"board_id": self.board.id, "export_format": "csv"})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment', response['Content-Disposition'])
        
        content = response.content.decode('utf-8')
        self.assertIn('Card ID', content)
        self.assertIn('Test Card', content)
        self.assertIn('Test List', content)

    def test_export_board_invalid_format(self):
        """Test d'export avec format invalide"""
        url = reverse("boards:export_board", kwargs={"board_id": self.board.id, "export_format": "xml"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)

    def test_export_board_no_access(self):
        """Test qu'un utilisateur sans accès ne peut pas exporter"""
        other_user = User.objects.create_user(username="other", password="password")
        self.client.logout()
        self.client.login(username="other", password="password")
        
        url = reverse("boards:export_board", kwargs={"board_id": self.board.id, "export_format": "json"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class ErrorHandlingTests(TestCase):
    """Tests pour la gestion d'erreurs et validations"""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client = Client()
        self.client.login(username="testuser", password="password")
        self.board = Board.objects.create(title="Test Board", owner=self.user)
        self.list = List.objects.create(title="Test List", board=self.board)
        self.card = Card.objects.create(title="Test Card", list=self.list)

    def test_update_card_missing_title(self):
        """Test de mise à jour de carte sans titre"""
        url = reverse("boards:update_card", kwargs={"board_id": self.board.id, "card_id": self.card.id})
        payload = {"title": "", "description": "Test"}
        response = self.client.post(url, data=json.dumps(payload), content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_update_card_invalid_due_date(self):
        """Test de mise à jour avec date d'échéance invalide"""
        url = reverse("boards:update_card", kwargs={"board_id": self.board.id, "card_id": self.card.id})
        payload = {"title": "Test", "due_date": "invalid-date"}
        response = self.client.post(url, data=json.dumps(payload), content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_create_subtask_missing_title(self):
        """Test de création de subtask sans titre"""
        url = reverse("boards:create_subtask", kwargs={"board_id": self.board.id, "card_id": self.card.id})
        payload = {"title": ""}
        response = self.client.post(url, data=json.dumps(payload), content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_toggle_card_assignment_missing_user_id(self):
        """Test d'assignation sans user_id"""
        url = reverse("boards:toggle_card_assignment", kwargs={"board_id": self.board.id, "card_id": self.card.id})
        payload = {}
        response = self.client.post(url, data=json.dumps(payload), content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_access_nonexistent_board(self):
        """Test d'accès à un board inexistant"""
        url = reverse("boards:board_detail", kwargs={"board_id": 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_access_nonexistent_card(self):
        """Test d'accès à une carte inexistante"""
        url = reverse("boards:card_detail", kwargs={"board_id": self.board.id, "card_id": 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_delete_list_updates_board(self):
        """Test que la suppression d'une liste fonctionne"""
        url = reverse("boards:delete_list", kwargs={"board_id": self.board.id, "list_id": self.list.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertFalse(List.objects.filter(id=self.list.id).exists())

    def test_rename_board_empty_title(self):
        """Test de renommage de board avec titre vide"""
        url = reverse("boards:rename_board", kwargs={"board_id": self.board.id})
        response = self.client.post(url, {"title": ""})
        self.assertEqual(response.status_code, 302)
        self.board.refresh_from_db()
        self.assertEqual(self.board.title, "Test Board")  # Unchanged
