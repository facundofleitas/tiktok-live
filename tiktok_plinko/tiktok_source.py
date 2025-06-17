from __future__ import annotations

import asyncio
import logging
from typing import Optional

from tiktok_live import TikTokLiveClient
from tiktok_live.types.events import CommentEvent, LikeEvent, FollowEvent

from .event_sources import EventSource
from .game_logic import Team


class TikTokEventSource(EventSource):
    """EventSource que consume eventos de un stream de TikTok Live."""

    def __init__(self, username: str):
        super().__init__()
        self.username = username
        self._client: Optional[TikTokLiveClient] = None

    async def run(self) -> None:
        logging.info("Conectando a TikTok Live de %s", self.username)
        self._client = TikTokLiveClient(unique_id=self.username)

        @self._client.on("comment")
        async def on_comment(event: CommentEvent):  # type: ignore
            team = self._infer_team(event.comment)
            self._emit_comment(event.user.nickname, team)

        @self._client.on("like")
        async def on_like(event: LikeEvent):  # type: ignore
            self._emit_like(event.user.nickname)

        @self._client.on("follow")
        async def on_follow(event: FollowEvent):  # type: ignore
            self._emit_follow(event.user.nickname)

        await self._client.start()

    # ------------------------------------------------------------------
    # Inferencia de género (muy simplificada)
    # ------------------------------------------------------------------
    def _infer_team(self, comment_text: str) -> Team:
        """Devuelve Team.MEN si el comentario contiene "boy", etc. Placeholder."""
        text = comment_text.lower()
        if any(word in text for word in ["girl", "woman", "chica", "mujer"]):
            return Team.WOMEN
        return Team.MEN 