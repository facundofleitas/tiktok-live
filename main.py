from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from threading import Thread
from typing import Optional

import pygame

from tiktok_plinko.event_sources import DummyEventSource, EventSource
from tiktok_plinko.game_logic import GameConfig, GameState, Team

try:
    from tiktok_plinko.tiktok_source import TikTokEventSource
except ImportError:
    TikTokEventSource = None  # type: ignore


# -----------------------------------------------------------------------------
# Renderizado con pygame
# -----------------------------------------------------------------------------
class PygameRenderer:
    def __init__(self, game_state: GameState):
        pygame.init()
        self.game_state = game_state
        self.screen = pygame.display.set_mode((game_state.config.width, game_state.config.height))
        pygame.display.set_caption("TikTok Plinko Battle")
        self.clock = pygame.time.Clock()
        # Colores
        self.bg_color = (30, 30, 30)
        self.peg_color = (200, 200, 200)
        self.women_color = (255, 100, 180)
        self.men_color = (100, 150, 255)
        self.font = pygame.font.SysFont("Arial", 24)

    def draw(self) -> None:
        self.screen.fill(self.bg_color)
        self._draw_pegs()
        self._draw_slots()
        self._draw_balls()
        self._draw_scores()
        pygame.display.flip()

    def _draw_pegs(self) -> None:
        glow_duration = 1.0  # Debe coincidir con timer en lógica
        for peg in self.game_state.pegs:
            # Si está activo el glow, dibuja un halo con varias capas para un fade moderno
            if peg.hit_timer > 0:
                # t va de 1 a 0 conforme el brillo se desvanece
                t = peg.hit_timer / glow_duration
                max_radius = int(peg.radius * (3.0 - 1.5 * t))  # se reduce con el tiempo
                num_layers = 10
                # Recorremos desde capas externas (más grandes) a internas para que el centro resalte
                for i in reversed(range(num_layers)):
                    layer_ratio = (i + 1) / num_layers  # 0..1
                    radius = int(max_radius * layer_ratio)
                    # Fade radial (capas externas más transparentes)
                    radial_alpha = (layer_ratio ** 2)
                    # Fade temporal (luz se apaga con t)
                    temporal_alpha = t ** 1.3  # curva más suave
                    alpha = int(255 * temporal_alpha * radial_alpha)
                    if alpha <= 3:
                        continue
                    glow_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                    glow_color = (50, 240, 255, alpha)  # cian eléctrico
                    pygame.draw.circle(glow_surf, glow_color, (radius, radius), radius)
                    self.screen.blit(
                        glow_surf, (int(peg.x - radius), int(peg.y - radius)), special_flags=pygame.BLEND_RGBA_ADD
                    )

            # Dibuja el peg base por encima
            pygame.draw.circle(self.screen, self.peg_color, (int(peg.x), int(peg.y)), peg.radius)

    def _draw_slots(self) -> None:
        max_pegs = self.game_state.config.top_pegs + self.game_state.config.rows - 1
        slot_count = max_pegs - 1
        slot_width = self.game_state.config.width / (max_pegs + 1)
        slot_height = self.game_state.config.bottom_margin

        # Colores gradientes del centro (amarillo) a extremos (rojo)
        base_colors = [
            (220, 0, 0),
            (220, 70, 0),
            (220, 120, 0),
            (220, 180, 0),
            (220, 220, 0),
        ]

        def color_for_index(i: int) -> tuple[int, int, int]:
            mid = slot_count // 2
            distance = abs(i - mid)
            # Normaliza distancia a rango de base_colors
            idx = min(distance, len(base_colors) - 1)
            return base_colors[idx]

        for i in range(slot_count):
            # Seleccionar puntos (si falta, usar último)
            if i < len(self.game_state.config.slot_scores):
                points = self.game_state.config.slot_scores[i]
            else:
                points = self.game_state.config.slot_scores[-1]

            color = color_for_index(i)
            x = (i + 1) * slot_width
            y = self.game_state.config.height - slot_height
            rect = pygame.Rect(x, y, slot_width, slot_height)
            pygame.draw.rect(self.screen, color, rect)
            # Borde
            pygame.draw.rect(self.screen, (0, 0, 0), rect, 2)

            # Texto de puntos
            label = f"{points}"
            text = self.font.render(label, True, (255, 255, 255))
            txt_rect = text.get_rect(center=(x + slot_width / 2, y + slot_height / 2))
            self.screen.blit(text, txt_rect)

    def _draw_balls(self) -> None:
        for ball in self.game_state.balls:
            color = self.women_color if ball.team == Team.WOMEN else self.men_color
            pygame.draw.circle(self.screen, color, (int(ball.x), int(ball.y)), ball.radius)

    def _draw_scores(self) -> None:
        women_score = self.game_state.scores[Team.WOMEN]
        men_score = self.game_state.scores[Team.MEN]
        text_women = self.font.render(f"Mujeres: {women_score}", True, self.women_color)
        text_men = self.font.render(f"Hombres: {men_score}", True, self.men_color)
        self.screen.blit(text_women, (10, 10))
        self.screen.blit(text_men, (self.game_state.config.width - text_men.get_width() - 10, 10))


# -----------------------------------------------------------------------------
# Bucles de ejecución
# -----------------------------------------------------------------------------
async def run_event_source(event_source: EventSource, game_state: GameState) -> None:
    # Registra callbacks
    event_source.on_comment(lambda username, team: game_state.spawn_ball(team))

    # Por ahora ignoramos likes/follows
    await event_source.run()


def start_event_loop(loop: asyncio.AbstractEventLoop) -> None:
    asyncio.set_event_loop(loop)
    loop.run_forever()


# -----------------------------------------------------------------------------
# Entrypoint
# -----------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="TikTok Plinko Battle")
    parser.add_argument(
        "--tiktok",
        metavar="USERNAME",
        help="Nombre de usuario de TikTok para conectarse al live (si se omite, se usa DummyEventSource)",
    )
    args = parser.parse_args()

    config = GameConfig()
    game_state = GameState(config)

    # Selecciona fuente de eventos
    if args.tiktok:
        if TikTokEventSource is None:
            print("El paquete tiktok-live no está disponible.")
            sys.exit(1)
        event_source: EventSource = TikTokEventSource(args.tiktok)
    else:
        event_source = DummyEventSource(interval=1.0)

    # Inicia loop asíncrono en hilo separado
    loop = asyncio.new_event_loop()
    t = Thread(target=start_event_loop, args=(loop,), daemon=True)
    t.start()

    asyncio.run_coroutine_threadsafe(run_event_source(event_source, game_state), loop)

    renderer = PygameRenderer(game_state)

    running = True
    while running:
        dt_ms = renderer.clock.tick(60)
        dt = dt_ms / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        game_state.update(dt)
        renderer.draw()

    pygame.quit()
    loop.call_soon_threadsafe(loop.stop)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main() 