"""
Manejador de eventos de TikTok Live.
"""

from __future__ import annotations

import logging
from typing import Optional

from .base import EventSource

try:
    from TikTokLive import TikTokLiveClient
    from TikTokLive.events import (
        ConnectEvent, 
        CommentEvent, 
        DiggEvent, 
        SocialEvent,
        DisconnectEvent,
        GiftEvent,
        LikeEvent
    )
    TIKTOK_AVAILABLE = True
except ImportError:
    TIKTOK_AVAILABLE = False


class TikTokEventSource(EventSource):
    """EventSource que consume eventos de un stream de TikTok Live."""

    def __init__(self, username: str):
        if not TIKTOK_AVAILABLE:
            raise ImportError("TikTokLive no está disponible. Instala con: pip install TikTokLive")
        
        super().__init__()
        self.username = username
        self._client: Optional[TikTokLiveClient] = None
        self._running = False

    async def run(self) -> None:
        """Conecta al stream de TikTok y procesa eventos."""
        try:
            self._client = TikTokLiveClient(unique_id=self.username)
            self._setup_event_handlers()
            
            print(f"🔴 Conectando a TikTok Live: @{self.username}")
            await self._client.start()
            
        except Exception as e:
            logging.error(f"Error conectando a TikTok Live: {e}")
            raise

    async def stop(self) -> None:
        """Desconecta del stream de TikTok."""
        self._running = False
        if self._client:
            await self._client.disconnect()

    def _extract_avatar_url(self, user) -> Optional[str]:
        """Extrae la URL del avatar desde el objeto user de TikTok."""
        try:
            if hasattr(user, 'avatar_thumb') and hasattr(user.avatar_thumb, 'm_urls'):
                urls = user.avatar_thumb.m_urls
                if urls and len(urls) > 0:
                    return urls[0]
        except (AttributeError, IndexError):
            pass
        return None

    def _setup_event_handlers(self) -> None:
        """Configura los manejadores de eventos de TikTok."""
        if not self._client:
            return

        @self._client.on(ConnectEvent)
        async def on_connect(event: ConnectEvent) -> None:
            self._running = True
            print(f"✅ Conectado a @{self.username}")

        @self._client.on(DisconnectEvent)
        async def on_disconnect(event: DisconnectEvent) -> None:
            self._running = False
            print("❌ Desconectado del stream")

        @self._client.on(CommentEvent)
        async def on_comment(event: CommentEvent) -> None:
            username = event.user.unique_id
            # Para CommentEvent, el avatar está en user_info
            avatar_url = self._extract_avatar_url(event.user_info)

            logging.info(f"Comentario de {username}: {event.comment}")
            self._emit_comment(username, avatar_url)

        @self._client.on(DiggEvent)
        async def on_like(event: DiggEvent) -> None:
            username = event.user.unique_id
            avatar_url = self._extract_avatar_url(event.user)
            
            logging.info(f"Like de {username}")
            self._emit_like(username, avatar_url)

        @self._client.on(SocialEvent)
        async def on_follow(event: SocialEvent) -> None:
            username = event.user.unique_id
            avatar_url = self._extract_avatar_url(event.user)
            
            logging.info(f"Follow de {username}")
            self._emit_follow(username, avatar_url)

        @self._client.on(GiftEvent)
        async def on_gift(event: GiftEvent) -> None:
            username = event.user.unique_id
            avatar_url = self._extract_avatar_url(event.user)
            gift_name = event.gift.name
            amount = getattr(event.gift, 'diamond_count', 1.0)
            
            logging.info(f"Regalo de {username}: {gift_name} (${amount:.2f})")
            self._emit_donation(username, amount, avatar_url)

        @self._client.on(LikeEvent)
        async def on_mass_like(event: LikeEvent) -> None:
            username = event.user.unique_id
            avatar_url = self._extract_avatar_url(event.user)
            
            logging.info(f"Likes masivos de {username}")
            self._emit_like(username, avatar_url) 