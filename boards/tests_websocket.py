from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async
from django.test import TestCase
from django.contrib.auth.models import User
from boards.models import Board
from boards.consumers import BoardConsumer
from channels.layers import get_channel_layer


class BoardConsumerTests(TestCase):
    """Tests pour le WebSocket consumer BoardConsumer"""

    async def test_anonymous_user_rejected(self):
        """Test qu'un utilisateur non authentifié est rejeté"""
        communicator = WebsocketCommunicator(BoardConsumer.as_asgi(), "/ws/boards/1/")
        communicator.scope['user'] = None
        connected, _ = await communicator.connect()
        self.assertFalse(connected)
        await communicator.disconnect()

    async def test_user_without_access_rejected(self):
        """Test qu'un utilisateur sans accès au board est rejeté"""
        # Créer un utilisateur et un board
        user = await database_sync_to_async(User.objects.create_user)(
            username="testuser", password="password"
        )
        owner = await database_sync_to_async(User.objects.create_user)(
            username="owner", password="password"
        )
        board = await database_sync_to_async(Board.objects.create)(
            title="Private Board", owner=owner
        )

        # Tenter de se connecter avec un utilisateur sans accès
        communicator = WebsocketCommunicator(
            BoardConsumer.as_asgi(), f"/ws/boards/{board.id}/"
        )
        communicator.scope['user'] = user
        communicator.scope['url_route'] = {'kwargs': {'board_id': board.id}}
        
        connected, _ = await communicator.connect()
        self.assertFalse(connected)
        await communicator.disconnect()

    async def test_owner_can_connect(self):
        """Test qu'un owner peut se connecter au WebSocket"""
        # Créer un utilisateur et un board
        owner = await database_sync_to_async(User.objects.create_user)(
            username="owner", password="password"
        )
        board = await database_sync_to_async(Board.objects.create)(
            title="Test Board", owner=owner
        )

        # Se connecter en tant qu'owner
        communicator = WebsocketCommunicator(
            BoardConsumer.as_asgi(), f"/ws/boards/{board.id}/"
        )
        communicator.scope['user'] = owner
        communicator.scope['url_route'] = {'kwargs': {'board_id': board.id}}
        
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        await communicator.disconnect()

    async def test_member_can_connect(self):
        """Test qu'un membre peut se connecter au WebSocket"""
        # Créer un owner et un membre
        owner = await database_sync_to_async(User.objects.create_user)(
            username="owner", password="password"
        )
        member = await database_sync_to_async(User.objects.create_user)(
            username="member", password="password"
        )
        board = await database_sync_to_async(Board.objects.create)(
            title="Test Board", owner=owner
        )
        # Ajouter le membre
        await database_sync_to_async(board.members.add)(member)

        # Se connecter en tant que membre
        communicator = WebsocketCommunicator(
            BoardConsumer.as_asgi(), f"/ws/boards/{board.id}/"
        )
        communicator.scope['user'] = member
        communicator.scope['url_route'] = {'kwargs': {'board_id': board.id}}
        
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        await communicator.disconnect()

    async def test_ping_pong(self):
        """Test du mécanisme ping-pong"""
        owner = await database_sync_to_async(User.objects.create_user)(
            username="owner", password="password"
        )
        board = await database_sync_to_async(Board.objects.create)(
            title="Test Board", owner=owner
        )

        communicator = WebsocketCommunicator(
            BoardConsumer.as_asgi(), f"/ws/boards/{board.id}/"
        )
        communicator.scope['user'] = owner
        communicator.scope['url_route'] = {'kwargs': {'board_id': board.id}}
        
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        
        # Envoyer un ping
        await communicator.send_json_to({"type": "ping"})
        
        # Recevoir le pong
        response = await communicator.receive_json_from()
        self.assertEqual(response["type"], "pong")
        
        await communicator.disconnect()

    async def test_broadcast_message(self):
        """Test de diffusion d'un message au groupe"""
        owner = await database_sync_to_async(User.objects.create_user)(
            username="owner", password="password"
        )
        board = await database_sync_to_async(Board.objects.create)(
            title="Test Board", owner=owner
        )

        communicator = WebsocketCommunicator(
            BoardConsumer.as_asgi(), f"/ws/boards/{board.id}/"
        )
        communicator.scope['user'] = owner
        communicator.scope['url_route'] = {'kwargs': {'board_id': board.id}}
        
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Envoyer un broadcast au groupe via le channel layer
        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            f"board_{board.id}",
            {
                "type": "broadcast",
                "payload": {"action": "test.event", "data": "test_data"}
            }
        )

        # Recevoir le message diffusé
        response = await communicator.receive_json_from()
        self.assertEqual(response["action"], "test.event")
        self.assertEqual(response["data"], "test_data")

        await communicator.disconnect()
