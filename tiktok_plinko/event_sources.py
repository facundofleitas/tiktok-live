from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from typing import Callable, Coroutine, Optional

from .game_logic import Team


class EventSource(ABC):
    """Interfaz abstracta para recibir eventos de live streams."""

    def __init__(self) -> None:
        # Callbacks a registrar por el cliente
        self._on_comment_cb: Optional[Callable[[str, Team, Optional[str]], None]] = None
        self._on_like_cb: Optional[Callable[[str], None]] = None
        self._on_follow_cb: Optional[Callable[[str], None]] = None

    # ------------------------------------------------------------------
    # API pública para clientes
    # ------------------------------------------------------------------
    def on_comment(self, cb: Callable[[str, Team, Optional[str]], None]) -> None:
        self._on_comment_cb = cb

    def on_like(self, cb: Callable[[str], None]) -> None:
        self._on_like_cb = cb

    def on_follow(self, cb: Callable[[str], None]) -> None:
        self._on_follow_cb = cb

    # ------------------------------------------------------------------
    # Métodos a implementar por subclases
    # ------------------------------------------------------------------
    @abstractmethod
    async def run(self) -> None:
        """Inicia la escucha de eventos (loop asíncrono)."""

    # ------------------------------------------------------------------
    # Helpers para subclases
    # ------------------------------------------------------------------
    def _emit_comment(self, username: str, team: Team, avatar_url: Optional[str] = None) -> None:
        if self._on_comment_cb:
            self._on_comment_cb(username, team, avatar_url)

    def _emit_like(self, username: str) -> None:
        if self._on_like_cb:
            self._on_like_cb(username)

    def _emit_follow(self, username: str) -> None:
        if self._on_follow_cb:
            self._on_follow_cb(username)


class DummyEventSource(EventSource):
    """Generador de eventos aleatorios para pruebas locales."""

    def __init__(self, interval: float = 1.0):
        super().__init__()
        self.interval = interval
        self._running = True

    async def run(self) -> None:
        import random

        # Datos mock de usuarios con avatar
        avatars = [
            ("alice", "https://i.pravatar.cc/150?img=5"),
            ("bob", "https://i.pravatar.cc/150?img=6"),
            ("carol", "https://i.pravatar.cc/150?img=7"),
            ("dave", "https://i.pravatar.cc/150?img=8"),
            ("eve", "https://i.pravatar.cc/150?img=9"),
        ]

        while self._running:
            await asyncio.sleep(self.interval)
            username, avatar_url = random.choice(avatars)
            team = random.choice([Team.WOMEN, Team.MEN])
            self._emit_comment(username, team, avatar_url)

    def stop(self) -> None:
        self._running = False 