from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
import json
from .models import Board, List, Card

class EpiTrelloUserTests(TestCase):
    """
    Cette classe de test vérifie les fonctionnalités principales du point de vue de l'utilisateur.
    Elle simule un navigateur web pour tester si les pages s'affichent et si les actions fonctionnent.
    """

    def setUp(self):
        """
        Configuration initiale avant chaque test :
        On crée un utilisateur de test et quelques données de base.
        """
        self.username = "testuser"
        self.password = "password123"
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.client = Client()
        # Un second utilisateur pour les tests d'invitation
        self.user2 = User.objects.create_user(username="collab", password="password456")

        # Création d'un tableau initial pour les tests de lecture/détails
        self.board = Board.objects.create(title="Tableau de Test", owner=self.user)
        self.list = List.objects.create(title="A faire", board=self.board)
        self.card = Card.objects.create(title="Tâche 1", list=self.list)

    def test_page_accueil_accessible(self):
        """Vérifie que n'importe qui peut voir la page d'accueil."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "EpiTrello")

    def test_liste_tableaux_requiert_connexion(self):
        """Vérifie que la page des tableaux n'est pas accessible sans être connecté."""
        response = self.client.get(reverse('boards:board_list'))
        # 302 est le code de redirection vers la page de login
        self.assertEqual(response.status_code, 302)

    def test_acces_tableaux_apres_connexion(self):
        """Vérifie que l'utilisateur peut voir ses tableaux une fois connecté."""
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('boards:board_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tableau de Test")

    def test_creation_nouveau_tableau(self):
        """Vérifie qu'un utilisateur peut créer un tableau via le formulaire."""
        self.client.login(username=self.username, password=self.password)
        # On simule l'envoi du formulaire de création
        response = self.client.post(reverse('boards:create_board'), {'title': 'Projet Secret'})
        
        # On vérifie qu'on est redirigé vers la liste
        self.assertEqual(response.status_code, 302)
        # On vérifie que le tableau existe bien en base de données
        self.assertTrue(Board.objects.filter(title='Projet Secret').exists())

    def test_creation_carte(self):
        """Vérifie l'ajout d'une carte dans une liste existante."""
        self.client.login(username=self.username, password=self.password)
        url = reverse('boards:create_card', kwargs={'board_id': self.board.id})
        response = self.client.post(url, {
            'list_id': self.list.id,
            'title': 'Nouvelle Tâche',
            'description': 'Détails de la tâche'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Card.objects.filter(title='Nouvelle Tâche').exists())

    def test_api_details_carte_json(self):
        """
        Vérifie la partie 'AJAX' : on demande les détails d'une carte.
        L'application doit répondre en format JSON, pas en HTML.
        """
        self.client.login(username=self.username, password=self.password)
        url = reverse('boards:card_detail', kwargs={'board_id': self.board.id, 'card_id': self.card.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        # On vérifie que le contenu JSON contient bien le titre de notre carte
        data = response.json()
        self.assertEqual(data['title'], "Tâche 1")

    def test_suppression_carte_ajax(self):
        """Vérifie qu'on peut archiver/supprimer une carte via une requête AJAX."""
        self.client.login(username=self.username, password=self.password)
        url = reverse('boards:delete_card', kwargs={'board_id': self.board.id, 'card_id': self.card.id})
        # Les actions de suppression sont souvent en POST pour la sécurité
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 200)
        # On vérifie que la carte n'est plus en base
        self.assertFalse(Card.objects.filter(id=self.card.id).exists())

    def test_recherche_tableaux_ajax(self):
        """Vérifie que la recherche dynamique (partielle) fonctionne."""
        self.client.login(username=self.username, password=self.password)
        # On cherche un terme qui n'existe pas
        url = reverse('boards:board_list') + "?q=introuvable"
        # On simule une requête AJAX (XMLHttpRequest)
        response = self.client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        self.assertEqual(response.status_code, 200)
        # Le template partiel board_grid.html doit être utilisé
        self.assertContains(response, "Aucun tableau ne correspond")

    def test_page_404_personnalisee(self):
        """Vérifie que la page 404 personnalisée s'affiche quand une URL est inconnue."""
        # On force DEBUG=False temporairement pour simuler la production
        with self.settings(DEBUG=False, ALLOWED_HOSTS=['*']):
            response = self.client.get('/cette-page-n-existe-pas-du-tout/')
            self.assertEqual(response.status_code, 404)
            self.assertTemplateUsed(response, '404.html')
            self.assertContains(response, "Oups ! Page égarée", status_code=404)

    def test_inscription_utilisateur(self):
        """Vérifie qu'un nouvel utilisateur peut s'inscrire."""
        url = reverse('boards:signup')
        # On tente de créer un nouvel utilisateur avec un mot de passe robuste
        response = self.client.post(url, {
            'username': 'unique_user_signup',
            'password1': 'EpiTrello2026!',
            'password2': 'EpiTrello2026!'
        })
        
        # Si le test échoue, on affiche les erreurs pour débugger
        if response.status_code != 302:
            print(response.context['form'].errors)

        self.assertEqual(response.status_code, 302) # Redirect to home
        self.assertTrue(User.objects.filter(username='unique_user_signup').exists())
        # Check if logged in
        self.assertIn('_auth_user_id', self.client.session)

    def test_tri_cartes(self):
        """Vérifie que les différents modes de tri des cartes fonctionnent."""
        # On vide la liste initiale pour avoir un test propre
        self.list.cards.all().delete()
        
        # Création de cartes avec des titres et dates d'échéance spécifiques
        c1 = Card.objects.create(title="Zebra", list=self.list, due_date=timezone.now() + timezone.timedelta(days=10))
        c2 = Card.objects.create(title="Alpha", list=self.list, due_date=timezone.now() + timezone.timedelta(days=1))
        
        # 1. Test Tri par Titre (A-Z)
        self.client.login(username=self.username, password=self.password)
        url = reverse('boards:board_detail', kwargs={'board_id': self.board.id}) + "?sort=title"
        response = self.client.get(url)
        cards = response.context['board'].lists.all()[0].cached_cards
        self.assertEqual(cards[0].title, "Alpha")
        self.assertEqual(cards[1].title, "Zebra")
        
        # 2. Test Tri par Date d'échéance (Ascendant)
        url = reverse('boards:board_detail', kwargs={'board_id': self.board.id}) + "?sort=due_date"
        response = self.client.get(url)
        cards = response.context['board'].lists.all()[0].cached_cards
        # Alpha (1 jour) doit être avant Zebra (10 jours)
        self.assertEqual(cards[0].title, "Alpha")
        self.assertEqual(cards[1].title, "Zebra")

    def test_deconnexion_utilisateur(self):
        """Vérifie que l'utilisateur peut se déconnecter via GET et POST."""
        self.client.login(username=self.username, password=self.password)
        # Test POST (recommandé)
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertFalse('_auth_user_id' in self.client.session)

        # Test GET (supporté par notre vue personnalisée)
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_page_profil_accessible(self):
        """Vérifie que la page de profil est accessible une fois connecté."""
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('boards:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.username)
        self.assertContains(response, "Tableaux")
        self.assertContains(response, "Dernière connexion")

    def test_login_redirects_to_board_list(self):
        """Après connexion sans 'next', l'utilisateur est redirigé vers sa home (boards:board_list)."""
        response = self.client.post(reverse('login'), {
            'username': self.username,
            'password': self.password,
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].endswith(reverse('boards:board_list')))

    def test_invite_member_success(self):
        """L'owner peut inviter un membre par son nom d'utilisateur."""
        self.client.login(username=self.username, password=self.password)
        url = reverse('boards:invite_member', kwargs={'board_id': self.board.id})
        response = self.client.post(url, {'username': 'collab'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.board.members.filter(id=self.user2.id).exists())

    def test_member_can_access_board(self):
        """Un membre invité peut accéder au détail du board et le voir dans sa liste."""
        # inviter d'abord collab
        self.client.login(username=self.username, password=self.password)
        invite_url = reverse('boards:invite_member', kwargs={'board_id': self.board.id})
        self.client.post(invite_url, {'username': 'collab'})
        # accès en tant que membre
        self.client.logout()
        self.client.login(username='collab', password='password456')
        detail_url = reverse('boards:board_detail', kwargs={'board_id': self.board.id})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        # présent dans la liste des boards
        list_url = reverse('boards:board_list')
        response = self.client.get(list_url)
        self.assertContains(response, 'Tableau de Test')

    def test_notification_created_on_invite(self):
        """Une notification est créée quand un utilisateur est invité."""
        self.client.login(username=self.username, password=self.password)
        url = reverse('boards:invite_member', kwargs={'board_id': self.board.id})
        self.client.post(url, {'username': 'collab'})
        
        self.assertTrue(self.user2.notifications.filter(message__contains="invité").exists())

    def test_notification_created_on_assignment(self):
        """Une notification est créée quand un utilisateur est assigné à une carte."""
        self.client.login(username=self.username, password=self.password)
        # Inviter d'abord pour qu'il ait accès
        self.board.members.add(self.user2)
        
        url = reverse('boards:toggle_card_assignment', kwargs={'board_id': self.board.id, 'card_id': self.card.id})
        # Note: toggle_card_assignment attend user_id dans le payload JSON
        self.client.post(url, data=json.dumps({'user_id': self.user2.id}), content_type="application/json")
        
        self.assertTrue(self.user2.notifications.filter(message__contains="assigné").exists())

    def test_non_member_cannot_access_board(self):
        """Un utilisateur non invité ni propriétaire ne peut pas accéder au board."""
        stranger = User.objects.create_user(username='stranger', password='pass789')
        self.client.login(username='stranger', password='pass789')
        url = reverse('boards:board_detail', kwargs={'board_id': self.board.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_member_cannot_access_manage_members(self):
        """Un simple membre ne peut pas accéder à la gestion des membres."""
        self.board.members.add(self.user2)
        self.client.login(username='collab', password='password456')
        url = reverse('boards:manage_members', kwargs={'board_id': self.board.id})
        response = self.client.get(url)
        # On s'attend à une redirection vers le board_detail avec un message d'erreur
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].endswith(reverse('boards:board_detail', kwargs={'board_id': self.board.id})))

    def test_manage_members_page_access(self):
        """Seul l'owner peut accéder à la page de gestion des membres."""
        # Owner
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('boards:manage_members', kwargs={'board_id': self.board.id}))
        self.assertEqual(response.status_code, 200)

        # Membre
        self.board.members.add(self.user2)
        self.client.login(username='collab', password='password456')
        response = self.client.get(reverse('boards:manage_members', kwargs={'board_id': self.board.id}))
        self.assertEqual(response.status_code, 302) # Redirect due to messages.error

    def test_remove_member_success(self):
        """L'owner peut retirer un membre."""
        self.board.members.add(self.user2)
        self.client.login(username=self.username, password=self.password)
        url = reverse('boards:remove_member', kwargs={'board_id': self.board.id, 'user_id': self.user2.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.board.members.filter(id=self.user2.id).exists())

    def test_notification_count_in_context(self):
        """Vérifie que le compteur de notifications est disponible dans le contexte de différentes pages."""
        # Créer une notification
        from .models import Notification
        Notification.objects.create(user=self.user, message="Test")
        
        self.client.login(username=self.username, password=self.password)
        
        # Tester sur l'accueil
        response = self.client.get(reverse('home'))
        self.assertEqual(response.context['unread_notifications_count'], 1)
        
        # Tester sur le détail d'un board
        response = self.client.get(reverse('boards:board_detail', kwargs={'board_id': self.board.id}))
        self.assertEqual(response.context['unread_notifications_count'], 1)
        
        # Tester sur la liste des boards
        response = self.client.get(reverse('boards:board_list'))
        self.assertEqual(response.context['unread_notifications_count'], 1)

    def test_message_appears_after_action(self):
        """Vérifie qu'un message de succès (Toast) est rendu dans le HTML après une action."""
        self.client.login(username=self.username, password=self.password)
        
        # Action 1: Renommer (redirige vers board_list)
        url = reverse('boards:rename_board', kwargs={'board_id': self.board.id})
        response = self.client.post(url, {'title': 'Nouveau Nom'}, follow=True)
        self.assertContains(response, 'window.pushToast')
        self.assertContains(response, 'Tableau renommé')
        
        # Action 2: Créer une liste (redirige vers board_detail)
        url = reverse('boards:create_list', kwargs={'board_id': self.board.id})
        response = self.client.post(url, {'title': 'Nouvelle Liste'}, follow=True)
        self.assertContains(response, 'window.pushToast')
        self.assertContains(response, 'Liste ajoutée avec succès.')

    def test_password_change_flow(self):
        """Un utilisateur connecté peut changer son mot de passe via les vues Django et se reconnecter."""
        self.client.login(username=self.username, password=self.password)
        # Afficher le formulaire
        response = self.client.get(reverse('password_change'))
        self.assertEqual(response.status_code, 200)
        # Soumettre un nouveau mot de passe
        new_pass = 'NewPassw0rd!2026'
        response = self.client.post(reverse('password_change'), {
            'old_password': self.password,
            'new_password1': new_pass,
            'new_password2': new_pass,
        })
        # Redirection vers done
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].endswith(reverse('password_change_done')))
        # Déconnexion puis reconnexion avec le nouveau MDP
        self.client.logout()
        self.assertTrue(self.client.login(username=self.username, password=new_pass))



class EpiTrelloIsolationTests(TestCase):
    def setUp(self):
        self.user_a = User.objects.create_user(username="alice", password="passA123!")
        self.user_b = User.objects.create_user(username="bob", password="passB123!")
        self.board_a = Board.objects.create(title="Board A", owner=self.user_a)
        self.list_a = List.objects.create(title="Liste A", board=self.board_a)
        self.card_a1 = Card.objects.create(title="Secret A1", list=self.list_a)
        self.client = Client()

    def test_user_b_cannot_see_user_a_board_detail(self):
        self.client.login(username="bob", password="passB123!")
        url = reverse('boards:board_detail', kwargs={'board_id': self.board_a.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_user_b_cannot_fetch_user_a_card_json(self):
        self.client.login(username="bob", password="passB123!")
        url = reverse('boards:card_detail', kwargs={'board_id': self.board_a.id, 'card_id': self.card_a1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_user_b_cannot_delete_user_a_card(self):
        self.client.login(username="bob", password="passB123!")
        url = reverse('boards:delete_card', kwargs={'board_id': self.board_a.id, 'card_id': self.card_a1.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Card.objects.filter(id=self.card_a1.id).exists())

    def test_board_list_shows_only_own_boards(self):
        # user_b creates own board
        board_b = Board.objects.create(title="Board B", owner=self.user_b)
        self.client.login(username="bob", password="passB123!")
        url = reverse('boards:board_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Board B")
        self.assertNotContains(response, "Board A")
