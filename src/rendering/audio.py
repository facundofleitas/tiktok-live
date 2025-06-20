"""
Manejador de audio del juego.
"""

import os
from typing import Optional
import pygame

from ..core.config import app_config


class AudioManager:
    """Manejador centralizado de audio."""

    def __init__(self):
        self.peg_hit_sound: Optional[pygame.mixer.Sound] = None
        self.slot_hit_sound: Optional[pygame.mixer.Sound] = None
        self.donation_sound: Optional[pygame.mixer.Sound] = None
        self._initialized = False
        self._is_muted = False
        self._volume = 1.0  # Volumen actual (0.0 a 1.0)

    def initialize(self) -> None:
        """Inicializa el sistema de audio."""
        if self._initialized:
            return

        try:
            pygame.mixer.init(
                frequency=app_config.AUDIO_FREQUENCY,
                size=app_config.AUDIO_SIZE,
                channels=app_config.AUDIO_CHANNELS,
                buffer=app_config.AUDIO_BUFFER
            )
            self._load_sounds()
            self._initialized = True
            print("🔊 Sistema de audio inicializado correctamente")
        except Exception as e:
            print(f"⚠️  Error al inicializar audio: {e}")

    def _load_sounds(self) -> None:
        """Carga todos los archivos de sonido."""
        # Sonido de colisión con pegs
        try:
            peg_sound_path = app_config.SOUNDS_DIR / "happy-pop-sonido.wav"
            if peg_sound_path.exists():
                self.peg_hit_sound = pygame.mixer.Sound(str(peg_sound_path))
                self.peg_hit_sound.set_volume(0.3)
                print(f"✅ Sonido cargado: {peg_sound_path.name}")
            else:
                print(f"⚠️  Archivo no encontrado: {peg_sound_path}")
        except Exception as e:
            print(f"❌ Error cargando sonido de peg: {e}")

        # Sonido de slot/ganador
        try:
            slot_sound_path = app_config.SOUNDS_DIR / "sonido-ganador.wav"
            if slot_sound_path.exists():
                self.slot_hit_sound = pygame.mixer.Sound(str(slot_sound_path))
                self.slot_hit_sound.set_volume(0.5)
                print(f"✅ Sonido cargado: {slot_sound_path.name}")
            else:
                print(f"⚠️  Archivo no encontrado: {slot_sound_path}")
        except Exception as e:
            print(f"❌ Error cargando sonido de slot: {e}")

    def play_peg_hit(self) -> None:
        """Reproduce el sonido de colisión con peg."""
        if self.peg_hit_sound and not self._is_muted:
            self.peg_hit_sound.play()

    def play_slot_hit(self) -> None:
        """Reproduce el sonido de llegada a slot."""
        if self.slot_hit_sound and not self._is_muted:
            self.slot_hit_sound.play()

    def play_donation(self) -> None:
        """Reproduce el sonido de donación (puede ser el mismo que slot por ahora)."""
        if self.slot_hit_sound and not self._is_muted:
            self.slot_hit_sound.play()

    def set_volume(self, volume: float) -> None:
        """Establece el volumen general (0.0 a 1.0)."""
        self._volume = max(0.0, min(1.0, volume))
        self._update_volumes()

    def _update_volumes(self) -> None:
        """Actualiza los volúmenes de todos los sonidos."""
        effective_volume = 0.0 if self._is_muted else self._volume
        
        if self.peg_hit_sound:
            self.peg_hit_sound.set_volume(effective_volume * 0.3)
        if self.slot_hit_sound:
            self.slot_hit_sound.set_volume(effective_volume * 0.5)

    def toggle_mute(self) -> bool:
        """Alterna el estado de mute. Retorna True si está muteado."""
        self._is_muted = not self._is_muted
        self._update_volumes()
        status = "🔇 Audio muteado" if self._is_muted else "🔊 Audio activado"
        print(status)
        return self._is_muted

    def set_mute(self, muted: bool) -> None:
        """Establece el estado de mute."""
        if self._is_muted != muted:
            self._is_muted = muted
            self._update_volumes()
            status = "🔇 Audio muteado" if self._is_muted else "🔊 Audio activado"
            print(status)

    def is_muted(self) -> bool:
        """Retorna True si el audio está muteado."""
        return self._is_muted

    def get_volume(self) -> float:
        """Retorna el volumen actual (0.0 a 1.0)."""
        return self._volume

    def cleanup(self) -> None:
        """Limpia los recursos de audio."""
        if self._initialized:
            pygame.mixer.quit()
            self._initialized = False 