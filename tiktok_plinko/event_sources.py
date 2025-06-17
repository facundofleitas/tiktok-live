from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from typing import Callable, Coroutine, Optional

from .game_logic import Team


class EventSource(ABC):
    """Interfaz abstracta para recibir eventos de live streams."""

    def __init__(self) -> None:
        # Callbacks a registrar por el cliente
        self._on_comment_cb: Optional[Callable[[str, Team], None]] = None
        self._on_like_cb: Optional[Callable[[str], None]] = None
        self._on_follow_cb: Optional[Callable[[str], None]] = None

    # ------------------------------------------------------------------
    # API pública para clientes
    # ------------------------------------------------------------------
    def on_comment(self, cb: Callable[[str, Team], None]) -> None:
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
    def _emit_comment(self, username: str, team: Team) -> None:
        if self._on_comment_cb:
            self._on_comment_cb(username, team)

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

        while self._running:
            await asyncio.sleep(self.interval)
            username = f"user{random.randint(1, 1000)}"
            team = random.choice([Team.WOMEN, Team.MEN])
            self._emit_comment(username, team)

    def stop(self) -> None:
        self._running = False 