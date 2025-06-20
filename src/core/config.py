"""
Configuración centralizada de la aplicación.
"""

import os
from typing import Dict
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AppConfig:
    """Configuración general de la aplicación."""
    
    # Rutas de assets
    CONTENT_DIR: Path = Path("content")
    SOUNDS_DIR: Path = CONTENT_DIR / "sounds"
    IMAGES_DIR: Path = CONTENT_DIR / "images"
    FONTS_DIR: Path = CONTENT_DIR / "fonts"
    
    # Configuración de audio
    AUDIO_FREQUENCY: int = 22050
    AUDIO_SIZE: int = -16
    AUDIO_CHANNELS: int = 2
    AUDIO_BUFFER: int = 512
    
    # Configuración de renderizado
    DEFAULT_SCALE: int = 3  # Supersampling
    TARGET_FPS: int = 60
    
    # Configuración de eventos
    DUMMY_EVENT_INTERVAL: float = 1.0
    
    # Configuración de pelotas por evento
    BALLS_PER_COMMENT: int = 1
    BALLS_PER_LIKE: int = 1
    BALLS_PER_FOLLOW: int = 2
    BALLS_PER_SHARE: int = 3
    BALLS_PER_DONATION: int = 5  # Base, se multiplica por el monto
    
    # Configuración de comandos
    COMMAND_COSTS: Dict[str, int] = None
    
    def __post_init__(self):
        """Valida que los directorios de assets existan."""
        for directory in [self.CONTENT_DIR, self.SOUNDS_DIR, self.IMAGES_DIR]:
            if not directory.exists():
                print(f"⚠️  Directorio no encontrado: {directory}")

                # Configuración de costos de comandos
        if self.COMMAND_COSTS is None:
            self.COMMAND_COSTS = {
                'msg': 50,      # Mostrar mensaje en pantalla
            }


# Instancia global de configuración
app_config = AppConfig() 