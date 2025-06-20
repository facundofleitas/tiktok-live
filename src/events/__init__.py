"""
Módulo de eventos - Manejo de eventos de diferentes fuentes de streaming.
"""

from .base import EventSource
from .dummy import DummyEventSource
from .tiktok import TikTokEventSource

__all__ = [
    "EventSource",
    "DummyEventSource", 
    "TikTokEventSource"
] 