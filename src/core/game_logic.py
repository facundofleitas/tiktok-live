"""
Lógica central del juego Plinko.
"""

from __future__ import annotations

import math
import random
import urllib.request
from dataclasses import dataclass, field
from io import BytesIO
from typing import List, Tuple, Any, Optional, Dict

from src.core.commands import CommandProcessor


@dataclass
class UserScore:
    """Representa la puntuación de un usuario."""
    username: str
    score: int
    avatar_surface: Any = field(default=None, repr=False)
    avatar_url: Optional[str] = None


@dataclass
class GameConfig:
    """Parámetros de configuración que definen el tablero."""

    width: int = 600
    height: int = 800
    peg_radius: int = 6
    ball_radius: int = 20
    gravity: float = 2000  # px / s^2
    damping: float = 0.55  # rebote
    rows: int = 8  # número de niveles (fila superior incluida)
    top_pegs: int = 3  # pegs en la primera fila
    bottom_margin: int = 10  # espacio para las ranuras inferiores
    top_margin: int = 200  # espacio superior antes de la primera fila
    cols: int = 9
    slot_count: int = 9  # número de ranuras en la parte inferior
    slot_scores: List[int] = field(
        default_factory=lambda: [100, 50, 25, 10, 5, 10, 25, 50, 100]
    )


    def __post_init__(self) -> None:
        if len(self.slot_scores) != self.slot_count:
            raise ValueError("slot_scores length must match slot_count")


@dataclass
class Ball:
    """Representa una pelota en el juego."""
    
    x: float
    y: float
    vx: float
    vy: float
    radius: int
    username: str
    active: bool = True
    avatar_surface: Any = field(default=None, repr=False)
    rotation: float = 0.0  # Ángulo de rotación en grados

    def update(self, dt: float, gravity: float) -> None:
        """Actualiza la física de la pelota."""
        if not self.active:
            return
        
        self.vy += gravity * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Actualizar rotación basada en la velocidad horizontal (física real)
        # La pelota rota en la dirección del movimiento
        # Si se mueve hacia la derecha (+vx), rota hacia la derecha (sentido horario, +rotación)
        # Si se mueve hacia la izquierda (-vx), rota hacia la izquierda (sentido antihorario, -rotación)
        rotation_speed = self.vx * 1.5  # Factor de rotación (sin abs para mantener dirección)
        self.rotation += rotation_speed * dt
        self.rotation = self.rotation % 360  # Mantener entre 0-360 grados

    def deactivate(self) -> None:
        """Desactiva la pelota."""
        self.active = False


@dataclass
class Peg:
    """Representa un peg en el tablero."""
    
    x: float
    y: float
    radius: int
    hit_timer: float = 0.0  # Tiempo restante de brillo después de ser golpeado


class GameState:
    """Estado completo del juego."""

    def __init__(self, config: GameConfig):
        self.config = config
        self.balls: List[Ball] = []
        self.pegs: List[Peg] = self._create_pegs()
        self.user_scores: Dict[str, UserScore] = {}
        self.sound_events: List[str] = []
        self.command_processor = CommandProcessor()

    def _create_pegs(self) -> List[Peg]:
        """Crea la distribución triangular de pegs."""
        pegs: List[Peg] = []
        max_pegs = self.config.top_pegs + (self.config.rows - 1)
        row_height = (
            self.config.height - self.config.bottom_margin - self.config.top_margin
        ) / self.config.rows
        peg_spacing = self.config.width / (max_pegs + 1)

        for row in range(self.config.rows):
            pegs_in_row = self.config.top_pegs + row
            start_offset_pegs = (max_pegs - pegs_in_row) / 2
            y = self.config.top_margin + row * row_height
            
            for i in range(pegs_in_row):
                x = (start_offset_pegs + i + 1) * peg_spacing
                pegs.append(Peg(x, y, self.config.peg_radius))
        
        return pegs

    def spawn_ball(
        self,
        username: str,
        avatar_url: Optional[str] = None,
    ) -> None:
        """Crea una bola en la parte superior."""
        x = self.config.width / 2
        y = self.config.top_margin - 40
        vx = random.uniform(-40, 40)
        vy = 0

        # Registrar usuario si no existe
        if username not in self.user_scores:
            avatar_surface = None
            if avatar_url:
                avatar_surface = self._load_avatar(avatar_url, username)
            
            self.user_scores[username] = UserScore(
                username=username,
                score=0,
                avatar_surface=avatar_surface,
                avatar_url=avatar_url
            )

        # Usar avatar cacheado
        avatar_surface = self.user_scores[username].avatar_surface

        self.balls.append(
            Ball(
                x=x,
                y=y,
                vx=vx,
                vy=vy,
                radius=self.config.ball_radius,
                username=username,
                avatar_surface=avatar_surface,
            )
        )

    def _load_avatar(self, avatar_url: str, username: Optional[str] = None) -> Any:
        """Carga el avatar desde una URL de forma segura."""
        try:
            import pygame

            if not pygame.get_init():
                return None
            
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
                
                avatar_surface = pygame.image.load(BytesIO(data))
                
                if avatar_surface.get_alpha() is not None:
                    avatar_surface = avatar_surface.convert_alpha()
                else:
                    avatar_surface = avatar_surface.convert()
                
                return avatar_surface
                
        except Exception:
            pass
        
        return None

    def get_top_users(self, limit: int = 10) -> List[UserScore]:
        """Obtiene el top de usuarios ordenado por puntuación."""
        return sorted(
            self.user_scores.values(),
            key=lambda user: user.score,
            reverse=True
        )[:limit]

    def update(self, dt: float) -> None:
        """Actualiza la lógica del juego."""
        active_balls: List[Ball] = []
        self.command_processor.update(dt)
        
        for ball in self.balls:
            if not ball.active:
                continue
                
            ball.update(dt, self.config.gravity)
            self._handle_collisions(ball)
            
            # Verifica si llegó al fondo
            if ball.y >= self.config.height - self.config.ball_radius - self.config.bottom_margin:
                self._handle_ball_scored(ball)
                ball.deactivate()
            else:
                active_balls.append(ball)
        
        self.balls = active_balls

        # Actualiza temporizador de brillo en pegs
        for peg in self.pegs:
            if peg.hit_timer > 0:
                peg.hit_timer = max(0.0, peg.hit_timer - dt)

    def _handle_collisions(self, ball: Ball) -> None:
        """Maneja las colisiones entre pelotas y pegs."""
        for peg in self.pegs:
            dx = ball.x - peg.x
            dy = ball.y - peg.y
            dist = math.hypot(dx, dy)
            overlap = ball.radius + peg.radius - dist
            
            if overlap > 0:  # colisión
                # Calcula normal
                nx = dx / dist if dist else 0
                ny = dy / dist if dist else 0
                
                # Empuja la bola fuera del peg
                ball.x += nx * overlap
                ball.y += ny * overlap
                
                # Refleja la velocidad
                dot = ball.vx * nx + ball.vy * ny
                ball.vx -= 2 * dot * nx
                ball.vy -= 2 * dot * ny
                
                # Aplica amortiguación
                ball.vx *= self.config.damping
                ball.vy *= self.config.damping

                # Activa glow
                peg.hit_timer = 0.5

    def process_comment(self, username: str, comment: str, avatar_url: Optional[str] = None) -> bool:
        """
        Procesa un comentario para detectar comandos.
        Retorna True si se procesó un comando, False si es un comentario normal.
        """
        command_result = self.command_processor.parse_command(comment)
        
        if command_result:
            command_type, parameter = command_result
            success = self.command_processor.execute_command(
                username, command_type, parameter, self.user_scores, self
            )
            return success
        
        return False
    
    def _handle_ball_scored(self, ball: Ball) -> None:
        """Maneja cuando una pelota llega al fondo."""
        max_pegs = self.config.top_pegs + self.config.rows - 1
        slot_width = self.config.width / (max_pegs + 1)
        slot_count = max_pegs - 1

        slot_index = int((ball.x - slot_width) // slot_width)
        slot_index = max(0, min(slot_index, slot_count - 1))

        if slot_index >= len(self.config.slot_scores):
            points = self.config.slot_scores[-1]
        else:
            points = self.config.slot_scores[slot_index]

        # Agregar puntos al usuario
        if ball.username in self.user_scores:
            self.user_scores[ball.username].score += points

        self.sound_events.append(("slot_hit", ball.x, ball.y))

    def reset(self) -> None:
        """Reinicia el estado del juego."""
        self.balls.clear()
        # Resetear puntuaciones pero mantener usuarios registrados
        for user_score in self.user_scores.values():
            user_score.score = 0
        self.sound_events.clear() 