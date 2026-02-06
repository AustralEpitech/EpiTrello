from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Board, List, Card

class GlobalSearchTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.other_user = User.objects.create_user(username="otheruser", password="password")
        
        self.board1 = Board.objects.create(title="Board One", owner=self.user)
        self.board2 = Board.objects.create(title="Board Two", owner=self.other_user)
        self.board2.members.add(self.user)
        self.board3 = Board.objects.create(title="Private Board", owner=self.other_user)
        
        self.list1 = List.objects.create(title="List 1", board=self.board1)
        self.card1 = Card.objects.create(title="Find me in Board One", list=self.list1)
        self.card2 = Card.objects.create(title="Another card", description="Searchable description", list=self.list1)
        
        self.list2 = List.objects.create(title="List 2", board=self.board2)
        self.card3 = Card.objects.create(title="Find me in Board Two", list=self.list2)
        
        self.list3 = List.objects.create(title="List 3", board=self.board3)
        self.card4 = Card.objects.create(title="Find me in Private Board", list=self.list3)
        
        self.client = Client()
        self.client.login(username="testuser", password="password")

    def test_search_boards(self):
        response = self.client.get(reverse('boards:global_search'), {'q': 'Board'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Board One")
        self.assertContains(response, "Board Two")
        self.assertNotContains(response, "Private Board")

    def test_search_cards(self):
        # Search by title
        response = self.client.get(reverse('boards:global_search'), {'q': 'Find me'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Find me in Board One")
        self.assertContains(response, "Find me in Board Two")
        self.assertNotContains(response, "Find me in Private Board")
        
        # Search by description
        response = self.client.get(reverse('boards:global_search'), {'q': 'Searchable'})
        self.assertContains(response, "Another card")
