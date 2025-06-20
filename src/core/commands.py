"""
Sistema de comandos con costo de puntos para usuarios.
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
from enum import Enum

from .config import app_config


class CommandType(Enum):
    """Tipos de comandos disponibles."""
    MSG = "msg"


@dataclass
class ScreenMessage:
    """Mensaje que aparece en pantalla."""
    username: str
    message: str
    avatar_surface: Any = field(default=None, repr=False)
    timestamp: float = field(default_factory=time.time)
    duration: float = 5.0  # Duración en segundos
    x: float = 0.0
    y: float = 0.0
    alpha: int = 255


@dataclass
class SpecialEffect:
    """Efecto especial activado por comando."""
    effect_type: str
    username: str
    timestamp: float = field(default_factory=time.time)
    duration: float = 3.0
    active: bool = True
    params: Dict[str, Any] = field(default_factory=dict)


class CommandProcessor:
    """Procesador de comandos de usuarios."""
    
    def __init__(self):
        self.screen_messages: List[ScreenMessage] = []
        self.special_effects: List[SpecialEffect] = []
        self.user_effects: Dict[str, List[str]] = {}  # Efectos activos por usuario
        
    def parse_command(self, comment: str) -> Optional[tuple[CommandType, str]]:
        """
        Parsea un comentario para detectar comandos.
        
        Formatos soportados:
        - msg {message}
        """
        comment = comment.strip().lower()
        
        # Comando con parámetro (msg)
        msg_match = re.match(r'^msg\s+(.+)$', comment)
        if msg_match:
            message = msg_match.group(1).strip()
            if len(message) > 0 and len(message) <= 50:  # Límite de caracteres
                return (CommandType.MSG, message)
        
        # Comandos simples
        for cmd_type in CommandType:
            if cmd_type != CommandType.MSG and comment == cmd_type.value:
                return (cmd_type, "")
        
        return None
    
    def can_afford_command(self, username: str, command_type: CommandType, user_scores: Dict[str, Any]) -> bool:
        """Verifica si el usuario puede pagar el comando."""
        if username not in user_scores:
            return False
        
        cost = app_config.COMMAND_COSTS.get(command_type.value, 0)
        return user_scores[username].score >= cost
    
    def execute_command(
        self, 
        username: str, 
        command_type: CommandType, 
        parameter: str,
        user_scores: Dict[str, Any],
        game_state: Any
    ) -> bool:
        """
        Ejecuta un comando si el usuario puede pagarlo.
        Retorna True si se ejecutó exitosamente.
        """
        if not self.can_afford_command(username, command_type, user_scores):
            return False
        
        cost = app_config.COMMAND_COSTS.get(command_type.value, 0)
        
        # Cobrar el comando
        user_scores[username].score -= cost
        
        # Ejecutar el comando específico
        if command_type == CommandType.MSG:
            self._execute_msg_command(username, parameter, user_scores[username])
        
        return True
    
    def _execute_msg_command(self, username: str, message: str, user_score: Any) -> None:
        """Ejecuta comando de mensaje en pantalla."""
        screen_msg = ScreenMessage(
            username=username,
            message=message,
            avatar_surface=user_score.avatar_surface,
            duration=6.0,  # Duración más larga para mejor visibilidad
            x=0,  # Se calculará en el renderizador
            y=0   # Se calculará en el renderizador
        )
        self.screen_messages.append(screen_msg)
        print(f"💬 {username}: {message}")
    

    def update(self, dt: float) -> None:
        """Actualiza mensajes en pantalla y efectos especiales."""
        current_time = time.time()
        
        # Actualizar mensajes en pantalla
        self.screen_messages = [
            msg for msg in self.screen_messages
            if current_time - msg.timestamp < msg.duration
        ]
