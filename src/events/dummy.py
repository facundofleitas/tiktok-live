"""
Generador de eventos aleatorios para pruebas locales.
"""

import asyncio
import random
from typing import Optional

from .base import EventSource
from ..core.config import app_config


class DummyEventSource(EventSource):
    """Generador de eventos aleatorios para pruebas locales."""

    def __init__(self, interval: Optional[float] = None):
        super().__init__()
        self.interval = interval or app_config.DUMMY_EVENT_INTERVAL
        self._running = False

    async def run(self) -> None:
        """Inicia la generación de eventos aleatorios."""
        self._running = True
        
        # Datos mock de usuarios con avatar
        avatars = [
            ("alice", "https://i.pravatar.cc/150?img=5"),
            ("bob", "https://i.pravatar.cc/150?img=6"),
            ("carol", "https://i.pravatar.cc/150?img=7"),
            ("dave", "https://i.pravatar.cc/150?img=8"),
            ("eve", "https://i.pravatar.cc/150?img=9"),
            ("frank", "https://i.pravatar.cc/150?img=10"),
            ("grace", "https://i.pravatar.cc/150?img=11"),
            ("henry", "https://i.pravatar.cc/150?img=12"),
        ]

        print("🎮 Iniciando generador de eventos dummy...")
        print(f"⏱️  Intervalo: {self.interval}s")
        print("-" * 50)

        while self._running:
            await asyncio.sleep(self.interval)
            
            if not self._running:
                break
                
            username, avatar_url = random.choice(avatars)
            
            # Distribución de eventos más realista
            event_weights = {
                "command": 0.5
            }
            
            event_type = random.choices(
                list(event_weights.keys()),
                weights=list(event_weights.values())
            )[0]
            
            if event_type == "comment":
                print(f"💬 COMENTARIO: {username}")
                self._emit_comment(username, avatar_url)
                
            elif event_type == "follow":
                print(f"👥 FOLLOW: {username}")
                self._emit_follow(username, avatar_url)
                
            elif event_type == "like":
                print(f"❤️ LIKE: {username}")
                self._emit_like(username, avatar_url)
                
            elif event_type == "share":
                print(f"📤 SHARE: {username}")
                self._emit_share(username, avatar_url)
                
            elif event_type == "donation":
                amount = random.uniform(1.0, 100.0)
                print(f"💰 DONACIÓN: {username} -> ${amount:.2f}")
                self._emit_donation(username, amount, avatar_url)

            elif event_type == "command":
                print(f"💬 COMANDO: {username}")
                self._emit_comment(username, avatar_url, "msg Hello World")

    async def stop(self) -> None:
        """Detiene la generación de eventos."""
        self._running = False
        print("⏹️  Generador de eventos dummy detenido") 