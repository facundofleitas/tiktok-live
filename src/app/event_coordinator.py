"""
Coordinador de eventos - Conecta las fuentes de eventos con el estado del juego.
"""

from __future__ import annotations

import asyncio
import logging
from threading import Thread
from typing import TYPE_CHECKING

from ..core.config import app_config

if TYPE_CHECKING:
    from ..events.base import EventSource
    from ..core.game_logic import GameState


class EventCoordinator:
    """Coordina los eventos entre las fuentes y el estado del juego."""

    def __init__(self, event_source: EventSource, game_state: GameState):
        self.event_source = event_source
        self.game_state = game_state
        self.loop: asyncio.AbstractEventLoop | None = None
        self.thread: Thread | None = None
        self._running = False

    def start(self) -> None:
        """Inicia el coordinador de eventos en un hilo separado."""
        if self._running:
            return

        self._running = True
        self._register_callbacks()
        
        # Crear loop asíncrono en hilo separado
        self.loop = asyncio.new_event_loop()
        self.thread = Thread(target=self._start_event_loop, daemon=True)
        self.thread.start()

        # Ejecutar la fuente de eventos
        asyncio.run_coroutine_threadsafe(self.event_source.run(), self.loop)

    def stop(self) -> None:
        """Detiene el coordinador de eventos."""
        if not self._running:
            return

        self._running = False
        
        if self.loop:
            # Detener la fuente de eventos
            asyncio.run_coroutine_threadsafe(self.event_source.stop(), self.loop)
            # Detener el loop
            self.loop.call_soon_threadsafe(self.loop.stop)

        if self.thread:
            self.thread.join(timeout=5.0)

    def _start_event_loop(self) -> None:
        """Inicia el loop asíncrono en el hilo separado."""
        asyncio.set_event_loop(self.loop)
        if self.loop:
            self.loop.run_forever()

    def _register_callbacks(self) -> None:
        """Registra todos los callbacks de eventos."""
        # Comentarios -> Spawn balls
        self.event_source.on_comment(self._handle_comment)
        
        # Follows -> Spawn balls
        self.event_source.on_follow(self._handle_follow)
        
        # Likes -> Spawn balls
        self.event_source.on_like(self._handle_like)
        
        # Shares -> Spawn balls
        self.event_source.on_share(self._handle_share)
        
        # Donaciones -> Spawn balls múltiples
        self.event_source.on_donation(self._handle_donation)

    def _handle_comment(self, username: str, avatar_url: str | None = None, comment: str = "") -> None:
        """Maneja eventos de comentarios."""
        logging.info(f"Comentario de {username}")
        
        if comment:
            self.game_state.process_comment(username, comment, avatar_url)
            logging.info(f"Comentario procesado: {comment}")

        # Generar múltiples pelotas según configuración
        for _ in range(app_config.BALLS_PER_COMMENT):
            self.game_state.spawn_ball(username=username, avatar_url=avatar_url)

    def _handle_follow(self, username: str, avatar_url: str | None = None) -> None:
        """Maneja eventos de follows."""
        logging.info(f"Follow de {username}")
        
        # Generar múltiples pelotas según configuración
        for _ in range(app_config.BALLS_PER_FOLLOW):
            self.game_state.spawn_ball(username=username, avatar_url=avatar_url)

    def _handle_like(self, username: str, avatar_url: str | None = None) -> None:
        """Maneja eventos de likes."""
        logging.info(f"Like de {username}")
        
        # Generar múltiples pelotas según configuración
        for _ in range(app_config.BALLS_PER_LIKE):
            self.game_state.spawn_ball(username=username, avatar_url=avatar_url)

    def _handle_share(self, username: str, avatar_url: str | None = None) -> None:
        """Maneja eventos de shares."""
        logging.info(f"Share de {username}")
        
        # Generar múltiples pelotas según configuración
        for _ in range(app_config.BALLS_PER_SHARE):
            self.game_state.spawn_ball(username=username, avatar_url=avatar_url)

    def _handle_donation(self, username: str, amount: float, avatar_url: str | None = None) -> None:
        """Maneja eventos de donaciones."""
        logging.info(f"Donación de {username}: ${amount:.2f}")
        
        # Las donaciones generan múltiples bolas según el monto
        base_balls = app_config.BALLS_PER_DONATION
        bonus_balls = min(int(amount / 10), 10)  # Máximo 10 pelotas bonus
        total_balls = base_balls + bonus_balls
        
        for _ in range(total_balls):
            self.game_state.spawn_ball(username=username, avatar_url=avatar_url)
        
        # Agregar evento de sonido especial para donaciones
        self.game_state.sound_events.append(("donation", amount)) 