"""
Aplicación principal del juego TikTok Plinko Battle.
"""

import argparse
import logging
import sys
from typing import Optional

import pygame

from ..core import GameConfig, GameState
from ..events import DummyEventSource, TikTokEventSource, EventSource
from ..rendering import PygameRenderer
from ..core.config import app_config
from .event_coordinator import EventCoordinator


class GameApp:
    """Aplicación principal del juego."""

    def __init__(self):
        self.game_state: Optional[GameState] = None
        self.renderer: Optional[PygameRenderer] = None
        self.event_coordinator: Optional[EventCoordinator] = None
        self._running = False

    def run(self, tiktok_username: Optional[str] = None) -> None:
        """Ejecuta la aplicación principal."""
        try:
            self._initialize(tiktok_username)
            self._game_loop()
        except KeyboardInterrupt:
            print("\n⏹️  Juego detenido por el usuario")
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            logging.exception("Error en la aplicación principal")
        finally:
            self._cleanup()

    def _initialize(self, tiktok_username: Optional[str]) -> None:
        """Inicializa todos los componentes del juego."""
        print("🎮 Inicializando TikTok Plinko Battle...")
        
        # Configurar logging
        logging.basicConfig(level=logging.INFO)
        
        # Crear configuración y estado del juego
        config = GameConfig()
        self.game_state = GameState(config)
        
        # Crear fuente de eventos
        event_source = self._create_event_source(tiktok_username)
        
        # Crear coordinador de eventos
        self.event_coordinator = EventCoordinator(event_source, self.game_state)
        
        # Crear renderizador
        self.renderer = PygameRenderer(self.game_state)
        
        # Iniciar coordinador de eventos
        self.event_coordinator.start()
        
        print("✅ Inicialización completada")
        print("🎯 ¡Que comience la batalla!")
        print("-" * 50)
        print("🎮 CONTROLES:")
        print("   ESC - Salir del juego")
        print("   R   - Reiniciar puntuaciones")
        print("   M   - Mutear/Desmutear audio")
        print("-" * 50)

    def _create_event_source(self, tiktok_username: Optional[str]) -> EventSource:
        """Crea la fuente de eventos apropiada."""
        if tiktok_username:
            try:
                return TikTokEventSource(tiktok_username)
            except ImportError:
                print("❌ TikTokLive no está disponible.")
                print("💡 Instala con: pip install TikTokLive")
                print("🔄 Usando generador de eventos dummy...")
                return DummyEventSource()
        else:
            print("🤖 Usando generador de eventos dummy para pruebas")
            return DummyEventSource()

    def _game_loop(self) -> None:
        """Loop principal del juego."""
        if not self.renderer or not self.game_state:
            raise RuntimeError("El juego no está inicializado correctamente")

        self._running = True
        clock = self.renderer.get_clock()

        while self._running:
            # Calcular delta time
            dt_ms = clock.tick(app_config.TARGET_FPS)
            dt = dt_ms / 1000.0

            # Procesar eventos de pygame
            self._handle_pygame_events()

            # Actualizar lógica del juego
            self.game_state.update(dt)

            # Renderizar frame
            self.renderer.draw()

    def _handle_pygame_events(self) -> None:
        """Maneja los eventos de pygame."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False
            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event)

    def _handle_keydown(self, event: pygame.event.Event) -> None:
        """Maneja eventos de teclado."""
        if event.key == pygame.K_ESCAPE:
            self._running = False
        elif event.key == pygame.K_r:
            # Reset del juego
            if self.game_state:
                self.game_state.reset()
                print("🔄 Juego reiniciado")
        elif event.key == pygame.K_m:
            # Toggle mute del audio
            if self.renderer and self.renderer.audio_manager:
                self.renderer.audio_manager.toggle_mute()
        elif event.key == pygame.K_SPACE:
            # Pausa/resume (futuro)
            pass

    def _cleanup(self) -> None:
        """Limpia todos los recursos."""
        print("\n🧹 Limpiando recursos...")
        
        if self.event_coordinator:
            self.event_coordinator.stop()
        
        if self.renderer:
            self.renderer.cleanup()
        
        print("✅ Limpieza completada")


def main() -> None:
    """Punto de entrada principal de la aplicación."""
    parser = argparse.ArgumentParser(description="TikTok Plinko Battle")
    parser.add_argument(
        "--tiktok",
        metavar="USERNAME",
        help="Nombre de usuario de TikTok para conectarse al live (si se omite, se usa DummyEventSource)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Habilitar logging detallado"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    
    app = GameApp()
    app.run(args.tiktok)


if __name__ == "__main__":
    main() 