"""
Módulo de aplicación principal - Coordinación de todos los componentes.
"""

from .game_app import GameApp
from .event_coordinator import EventCoordinator

__all__ = [
    "GameApp",
    "EventCoordinator"
] 