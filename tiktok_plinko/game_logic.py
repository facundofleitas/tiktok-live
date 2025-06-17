from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Tuple, Any


class Team(Enum):
    WOMEN = auto()
    MEN = auto()


@dataclass
class GameConfig:
    """Parámetros de configuración que definen el tablero."""

    width: int = 600
    height: int = 800
    peg_radius: int = 6
    ball_radius: int = 20
    gravity: float = 2000 # px / s^2
    damping: float = 0.55  # rebote
    rows: int = 8  # número de niveles (fila superior incluida)
    top_pegs: int = 3  # pegs en la primera fila
    bottom_margin: int = 60  # espacio para las ranuras inferiores
    top_margin: int = 100  # espacio superior antes de la primera fila
    cols: int = 9
    slot_count: int = 9  # número de ranuras en la parte inferior
    slot_scores: List[int] = field(
        default_factory=lambda: [100, 50, 25, 10, 5, 10, 25, 50, 100]
    )
    # Cada slot tiene un multiplicador diferente, los extremos dan más puntos

    def __post_init__(self) -> None:
        if len(self.slot_scores) != self.slot_count:
            raise ValueError("slot_scores length must match slot_count")


@dataclass
class Ball:
    x: float
    y: float
    vx: float
    vy: float
    team: Team
    radius: int
    active: bool = True
    avatar_surface: Any = field(default=None, repr=False)  # superficie con el avatar del usuario

    def update(self, dt: float, gravity: float) -> None:
        if not self.active:
            return
        # Física básica
        self.vy += gravity * dt
        self.x += self.vx * dt
        self.y += self.vy * dt

    def deactivate(self) -> None:
        self.active = False


@dataclass
class Peg:
    x: float
    y: float
    radius: int
    # Tiempo restante de brillo (segundos) después de ser golpeado
    hit_timer: float = 0.0


class GameState:
    """Estado completo del juego, útil para pruebas unitarias y renderizado."""

    def __init__(self, config: GameConfig):
        self.config = config
        self.balls: List[Ball] = []
        self.pegs: List[Peg] = self._create_pegs()
        self.scores = {Team.WOMEN: 0, Team.MEN: 0}

    # ---------------------------------------------------------------------
    # Creación de tablero
    # ---------------------------------------------------------------------
    def _create_pegs(self) -> List[Peg]:
        pegs: List[Peg] = []
        # Distribución triangular
        max_pegs = self.config.top_pegs + (self.config.rows - 1)  # pegs en la última fila
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

    # ---------------------------------------------------------------------
    # API externa
    # ---------------------------------------------------------------------
    def spawn_ball(
        self,
        team: Team,
        username: str | None = None,
        avatar_url: str | None = None,
    ) -> None:
        """Crea una bola en la parte superior con velocidad inicial aleatoria.

        Si se proporciona `avatar_url`, se intentará descargar la imagen y
        almacenarla en la superficie `avatar_surface` de la bola para que el
        renderizador pueda dibujarla en lugar del círculo de color.
        """

        x = self.config.width / 2
        y = self.config.top_margin - 40  # justo encima de la primera fila
        vx = random.uniform(-40, 40)
        vy = 0

        avatar_surface = None
        if avatar_url:
            try:
                # Cargamos la imagen desde la URL. Todo se hace bajo demanda y
                # sin bloqueo de la UI principal (puede tardar un par de ms).
                import urllib.request
                from io import BytesIO

                import pygame  # type: ignore

                with urllib.request.urlopen(avatar_url, timeout=5) as response:
                    data = response.read()
                    avatar_surface = pygame.image.load(BytesIO(data)).convert_alpha()
            except Exception as exc:  # pylint: disable=broad-except
                # Si algo falla, seguimos sin avatar y usamos el círculo por defecto
                print(f"No se pudo cargar avatar {avatar_url}: {exc}")

        self.balls.append(
            Ball(
                x=x,
                y=y,
                vx=vx,
                vy=vy,
                team=team,
                radius=self.config.ball_radius,
                avatar_surface=avatar_surface,
            )
        )

    def update(self, dt: float) -> None:
        """Actualiza la lógica del juego.

        1. Actualiza física de bolas.
        2. Maneja colisiones peg-bola.
        3. Detecta si la bola llega al fondo y asigna puntuación.
        """
        active_balls: List[Ball] = []
        for ball in self.balls:
            if not ball.active:
                continue
            ball.update(dt, self.config.gravity)
            self._handle_collisions(ball)
            # Comprueba si llegó al fondo
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

    # ------------------------------------------------------------------
    # Lógica interna
    # ------------------------------------------------------------------
    def _handle_collisions(self, ball: Ball) -> None:
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
                peg.hit_timer = 0.5  # durará medio segundo

    def _handle_ball_scored(self, ball: Ball) -> None:
        # Huecos entre los pegs inferiores
        max_pegs = self.config.top_pegs + self.config.rows - 1
        slot_width = self.config.width / (max_pegs + 1)
        slot_count = max_pegs - 1

        # Los huecos comienzan a partir de x = slot_width hasta x = max_pegs*slot_width
        slot_index = int((ball.x - slot_width) // slot_width)
        slot_index = max(0, min(slot_index, slot_count - 1))

        # Asegura lista de puntuaciones suficientemente larga
        if slot_index >= len(self.config.slot_scores):
            points = self.config.slot_scores[-1]
        else:
            points = self.config.slot_scores[slot_index]

        self.scores[ball.team] += points

    # ------------------------------------------------------------------
    # Utilidades para pruebas y depuración
    # ------------------------------------------------------------------
    def reset(self) -> None:
        self.balls.clear()
        self.scores = {Team.WOMEN: 0, Team.MEN: 0} 