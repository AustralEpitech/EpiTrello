from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import AnonymousUser

from .models import Board


import logging

logger = logging.getLogger(__name__)


class BoardConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.board_id = self.scope.get("url_route", {}).get("kwargs", {}).get("board_id")
        self.group_name = f"board_{self.board_id}"
        logger.debug(f"Tentative de connexion WebSocket pour le tableau {self.board_id}")

        user = self.scope.get("user")
        if not user or isinstance(user, AnonymousUser) or not user.is_authenticated:
            logger.warning(f"Connexion WebSocket refusée : utilisateur non authentifié")
            await self.close(code=4401)  # unauthorized
            return

        # Check access rights
        has_access = await self._user_has_access(user.id, self.board_id)
        if not has_access:
            logger.warning(f"Connexion WebSocket refusée : utilisateur {user.username} n'a pas accès au tableau {self.board_id}")
            await self.close(code=4403)  # forbidden
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        logger.info(f"WebSocket connecté : utilisateur {user.username} sur le tableau {self.board_id}")

    async def disconnect(self, code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            logger.info(f"WebSocket déconnecté (code: {code}) pour le tableau {self.board_id}")

    async def receive_json(self, content, **kwargs):
        # Optional: handle pings or client messages
        cmd = content.get("type")
        if cmd == "ping":
            await self.send_json({"type": "pong"})

    async def broadcast(self, event):
        # Event shape: {"type": "broadcast", "payload": {...}}
        logger.debug(f"Diffusion d'un événement au WebSocket du tableau {self.board_id}")
        await self.send_json(event.get("payload", {}))

    @database_sync_to_async
    def _user_has_access(self, user_id, board_id):
        try:
            get_object_or_404(Board, Q(owner_id=user_id) | Q(members__id=user_id), pk=board_id)
            return True
        except Exception:
            return False
