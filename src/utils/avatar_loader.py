"""
Cargador de avatares desde URLs.
"""

import urllib.request
from io import BytesIO
from typing import Optional, Any
import pygame


class AvatarLoader:
    """Cargador de avatares con cache y manejo de errores."""

    def __init__(self):
        self._cache: dict[str, Any] = {}

    def load_avatar(self, avatar_url: str, username: Optional[str] = None) -> Optional[Any]:
        """Carga un avatar desde una URL con cache."""
        # Verificar cache
        if avatar_url in self._cache:
            return self._cache[avatar_url]

        try:
            if not pygame.get_init():
                return None
            
            # Crear request con headers
            request = urllib.request.Request(
                avatar_url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
            
            with urllib.request.urlopen(request, timeout=10) as response:
                if response.status != 200:
                    return None
                    
                data = response.read()
                if len(data) == 0:
                    return None
                
                # Cargar imagen
                avatar_surface = pygame.image.load(BytesIO(data))
                
                # Convertir para mejor rendimiento
                if avatar_surface.get_alpha() is not None:
                    avatar_surface = avatar_surface.convert_alpha()
                else:
                    avatar_surface = avatar_surface.convert()
                
                # Guardar en cache
                self._cache[avatar_url] = avatar_surface
                
                return avatar_surface
                
        except Exception:
            # En caso de error, guardar None en cache para evitar reintentos
            self._cache[avatar_url] = None
            return None

    def clear_cache(self) -> None:
        """Limpia el cache de avatares."""
        self._cache.clear()

    def get_cache_size(self) -> int:
        """Retorna el número de avatares en cache."""
        return len(self._cache) 