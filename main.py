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

        # --- Supersampling para mejor calidad ---
        self.scale = 3  # Renderizar internamente al doble de resolución
        self.lores_width = game_state.config.width
        self.lores_height = game_state.config.height
        self.hires_width = self.lores_width * self.scale
        self.hires_height = self.lores_height * self.scale

        # La pantalla que ve el usuario (baja resolución)
        self.screen = pygame.display.set_mode((self.lores_width, self.lores_height))
        # La superficie interna para dibujar (alta resolución)
        self.hires_surface = pygame.Surface((self.hires_width, self.hires_height))

        pygame.display.set_caption("TikTok Plinko Battle")
        self.clock = pygame.time.Clock()
        # Colores
        self.bg_color = (30, 30, 30)
        self.peg_color = (200, 200, 200)
        self.women_color = (255, 100, 180)
        self.men_color = (100, 150, 255)
        # La fuente también se escala para el renderizado en alta resolución
        self.font = pygame.font.SysFont("Arial", 24 * self.scale)

    def draw(self) -> None:
        # 1. Dibujar todo en la superficie de alta resolución
        self.hires_surface.fill(self.bg_color)
        self._draw_pegs()
        self._draw_slots()
        self._draw_balls()
        self._draw_scores()

        # 2. Reducir la superficie de alta resolución a la pantalla con un filtro suave
        pygame.transform.smoothscale(
            self.hires_surface, (self.lores_width, self.lores_height), self.screen
        )

        # 3. Actualizar la pantalla
        pygame.display.flip()

    def _draw_pegs(self) -> None:
        glow_duration = 0.5  # Debe coincidir con timer en lógica
        for peg in self.game_state.pegs:
            # Si está activo el glow, dibuja un efecto neón con desenfoque.
            if peg.hit_timer > 0:
                t = peg.hit_timer / glow_duration  # 1 -> recién golpeado, 0 -> sin glow

                # Todos los cálculos se hacen en coordenadas de alta resolución
                base_peg_radius_hires = peg.radius * self.scale
                glow_radius = int(base_peg_radius_hires * (3 + 2 * t))
                core_radius = base_peg_radius_hires + int(base_peg_radius_hires * 0.5 * t)

                glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(
                    glow_surf, (0, 255, 255), (glow_radius, glow_radius), core_radius
                )

                # Técnica de "Gaussian Blur" simulado
                temp_size = (glow_radius * 2 // 4, glow_radius * 2 // 4)
                small_surf = pygame.transform.smoothscale(glow_surf, temp_size)
                blurred_surf = pygame.transform.smoothscale(
                    small_surf, (glow_radius * 2, glow_radius * 2)
                )

                alpha = int(255 * t**1.5)
                blurred_surf.set_alpha(alpha)

                # Dibujar en la superficie hires, con coordenadas escaladas
                self.hires_surface.blit(
                    blurred_surf,
                    (int(peg.x * self.scale - glow_radius), int(peg.y * self.scale - glow_radius)),
                    special_flags=pygame.BLEND_RGBA_ADD,
                )

            # Dibuja el peg base en alta resolución
            pygame.draw.circle(
                self.hires_surface,
                self.peg_color,
                (int(peg.x * self.scale), int(peg.y * self.scale)),
                int(peg.radius * self.scale),
            )

    def _draw_slots(self) -> None:
        max_pegs = self.game_state.config.top_pegs + self.game_state.config.rows - 1
        slot_count = max_pegs - 1
        # Ancho de ranura calculado en alta resolución
        slot_width = self.hires_width / (max_pegs + 1)
        slot_height = self.game_state.config.bottom_margin * self.scale

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
            idx = min(distance, len(base_colors) - 1)
            return base_colors[idx]

        for i in range(slot_count):
            if i < len(self.game_state.config.slot_scores):
                points = self.game_state.config.slot_scores[i]
            else:
                points = self.game_state.config.slot_scores[-1]

            color = color_for_index(i)
            # Coordenadas y tamaño en alta resolución
            x = (i + 1) * slot_width
            y = self.hires_height - slot_height
            rect = pygame.Rect(x, y, slot_width, slot_height)
            pygame.draw.rect(self.hires_surface, color, rect)
            # Borde escalado
            pygame.draw.rect(self.hires_surface, (0, 0, 0), rect, 2 * self.scale)

            # Texto de puntos (la fuente ya está escalada)
            label = f"{points}"
            text = self.font.render(label, True, (255, 255, 255))
            txt_rect = text.get_rect(center=(x + slot_width / 2, y + slot_height / 2))
            self.hires_surface.blit(text, txt_rect)

    def _draw_balls(self) -> None:
        for ball in self.game_state.balls:
            color = self.women_color if ball.team == Team.WOMEN else self.men_color
            # Dibujar bola en alta resolución
            pygame.draw.circle(
                self.hires_surface,
                color,
                (int(ball.x * self.scale), int(ball.y * self.scale)),
                ball.radius * self.scale,
            )

    def _draw_scores(self) -> None:
        women_score = self.game_state.scores[Team.WOMEN]
        men_score = self.game_state.scores[Team.MEN]
        text_women = self.font.render(f"Mujeres: {women_score}", True, self.women_color)
        text_men = self.font.render(f"Hombres: {men_score}", True, self.men_color)
        # Posicionar texto en coordenadas de alta resolución
        self.hires_surface.blit(text_women, (10 * self.scale, 10 * self.scale))
        self.hires_surface.blit(
            text_men, (self.hires_width - text_men.get_width() - 10 * self.scale, 10 * self.scale)
        )


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