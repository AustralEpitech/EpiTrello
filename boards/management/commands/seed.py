from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from boards.models import Board, List, Card, Label, Subtask, Comment
from django.utils import timezone
import random

class Command(BaseCommand):
    help = "Peuple la base de données avec des données de test"

    def handle(self, *args, **kwargs):
        self.stdout.write("Nettoyage de la base de données...")
        # On évite de supprimer les utilisateurs pour ne pas casser les sessions en cours
        Board.objects.all().delete()
        Label.objects.all().delete()

        self.stdout.write("Création des utilisateurs...")
        admin, _ = User.objects.get_or_create(username="admin", is_staff=True, is_superuser=True)
        admin.set_password("admin123")
        admin.save()

        alice, _ = User.objects.get_or_create(username="alice")
        alice.set_password("alice123")
        alice.save()

        bob, _ = User.objects.get_or_create(username="bob")
        bob.set_password("bob123")
        bob.save()

        self.stdout.write("Création des labels...")
        labels_data = [
            ("Urgent", "#ef4444"),
            ("En attente", "#f59e0b"),
            ("Design", "#ec4899"),
            ("Backend", "#3b82f6"),
            ("Frontend", "#10b981"),
        ]
        labels = [Label.objects.create(name=name, color=color) for name, color in labels_data]

        self.stdout.write("Création du tableau d'Alice...")
        board_alice = Board.objects.create(title="Projet Site Web", owner=alice)
        
        list_names = ["À faire", "En cours", "Terminé"]
        lists = []
        for i, name in enumerate(list_names):
            lists.append(List.objects.create(title=name, board=board_alice, position=i))

        # Cartes pour Alice
        cards_data = [
            ("Maquette Figma", "Finir les maquettes de la page d'accueil", lists[0], [labels[2]]),
            ("Installation Django", "Setup initial du projet et des modèles", lists[2], [labels[3]]),
            ("Authentification", "Mettre en place le login/signup", lists[1], [labels[3], labels[0]]),
            ("Header Responsive", "Le menu burger ne marche pas sur iPhone", lists[0], [labels[4]]),
        ]

        for title, desc, lst, card_labels in cards_data:
            card = Card.objects.create(title=title, description=desc, list=lst)
            card.labels.set(card_labels)
            
            # Ajouter des sous-tâches
            if title == "Authentification":
                Subtask.objects.create(card=card, title="Créer les templates", is_completed=True)
                Subtask.objects.create(card=card, title="Configurern URLS", is_completed=False)
            
            # Ajouter un commentaire
            if title == "Maquette Figma":
                Comment.objects.create(card=card, author=alice, content="J'ai partagé le lien sur Slack.")

        self.stdout.write("Création du tableau partagé (Alice & Bob)...")
        board_shared = Board.objects.create(title="Roadmap Produit", owner=alice)
        board_shared.members.add(bob)

        list_todo = List.objects.create(title="Sprint 1", board=board_shared, position=0)
        
        c1 = Card.objects.create(
            title="Refactor API", 
            description="Nettoyer les vues et utiliser des QuerySets optimisés", 
            list=list_todo,
            due_date=timezone.now() + timezone.timedelta(days=5)
        )
        c1.assigned_to.add(bob)
        c1.labels.add(labels[3])
        
        Comment.objects.create(card=c1, author=bob, content="Je m'en occupe dès lundi.")

        self.stdout.write(self.style.SUCCESS("Base de données peuplée avec succès !"))
        self.stdout.write(f"Identifiants : admin/admin123, alice/alice123, bob/bob123")
