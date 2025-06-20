"""
Clase base abstracta para fuentes de eventos.
"""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from typing import Callable, Optional


class EventSource(ABC):
    """Interfaz abstracta para recibir eventos de live streams."""

    def __init__(self) -> None:
        # Callbacks principales
        self._on_comment_cb: Optional[Callable[[str, Optional[str]], None]] = None
        self._on_like_cb: Optional[Callable[[str, Optional[str]], None]] = None
        self._on_follow_cb: Optional[Callable[[str, Optional[str]], None]] = None
        self._on_donation_cb: Optional[Callable[[str, float, Optional[str]], None]] = None
        self._on_share_cb: Optional[Callable[[str, Optional[str]], None]] = None
        
        # Lista de callbacks para compatibilidad
        self._follow_callbacks: list[Callable[[str, Optional[str]], None]] = []

    # ------------------------------------------------------------------
    # API pública para clientes
    # ------------------------------------------------------------------
    
    def on_comment(self, cb: Callable[[str, Optional[str]], None]) -> None:
        """Registra callback para comentarios."""
        self._on_comment_cb = cb

    def on_like(self, cb: Callable[[str, Optional[str]], None]) -> None:
        """Registra callback para likes."""
        self._on_like_cb = cb

    def on_follow(self, cb: Callable[[str, Optional[str]], None]) -> None:
        """Registra callback para follows."""
        self._on_follow_cb = cb
        self._follow_callbacks.append(cb)

    def on_donation(self, cb: Callable[[str, float, Optional[str]], None]) -> None:
        """Registra callback para donaciones."""
        self._on_donation_cb = cb

    def on_share(self, cb: Callable[[str, Optional[str]], None]) -> None:
        """Registra callback para shares."""
        self._on_share_cb = cb

    # ------------------------------------------------------------------
    # Métodos protegidos para implementaciones
    # ------------------------------------------------------------------
    
    def _emit_comment(self, username: str, avatar_url: Optional[str] = None) -> None:
        """Emite un evento de comentario."""
        if self._on_comment_cb:
            self._on_comment_cb(username, avatar_url)

    def _emit_like(self, username: str, avatar_url: Optional[str] = None) -> None:
        """Emite un evento de like."""
        if self._on_like_cb:
            self._on_like_cb(username, avatar_url)

    def _emit_follow(self, username: str, avatar_url: Optional[str] = None) -> None:
        """Emite un evento de follow."""
        if self._on_follow_cb:
            self._on_follow_cb(username, avatar_url)
        
        # Compatibilidad con callbacks múltiples
        for callback in self._follow_callbacks:
            callback(username, avatar_url)

    def _emit_donation(self, username: str, amount: float, avatar_url: Optional[str] = None) -> None:
        """Emite un evento de donación."""
        if self._on_donation_cb:
            self._on_donation_cb(username, amount, avatar_url)

    def _emit_share(self, username: str, avatar_url: Optional[str] = None) -> None:
        """Emite un evento de share."""
        if self._on_share_cb:
            self._on_share_cb(username, avatar_url)

    # ------------------------------------------------------------------
    # Métodos abstractos que deben implementar las subclases
    # ------------------------------------------------------------------
    
    @abstractmethod
    async def run(self) -> None:
        """Inicia la fuente de eventos."""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Detiene la fuente de eventos."""
        pass 