"""
Renderizador principal usando Pygame.
"""

from __future__ import annotations

import time
import pygame
import random
from typing import TYPE_CHECKING

from .audio import AudioManager
from .particles import SimpleParticleSystem
from ..core.config import app_config

if TYPE_CHECKING:
    from ..core.game_logic import GameState


class PygameRenderer:
    """Renderizador principal del juego usando Pygame."""

    def __init__(self, game_state: GameState):
        pygame.init()
        
        self.game_state = game_state
        self.audio_manager = AudioManager()
        self.particle_system = SimpleParticleSystem()
        
        # Configuración de supersampling
        self.scale = app_config.DEFAULT_SCALE
        self.lores_width = game_state.config.width
        self.lores_height = game_state.config.height
        self.hires_width = self.lores_width * self.scale
        self.hires_height = self.lores_height * self.scale

        # Superficies de renderizado
        self.screen = pygame.display.set_mode((self.lores_width, self.lores_height))
        self.hires_surface = pygame.Surface((self.hires_width, self.hires_height))

        pygame.display.set_caption("TikTok Plinko Top Users")
        self.clock = pygame.time.Clock()
        
        # Configuración de colores
        self._setup_colors()
        
        # Inicializar audio
        self.audio_manager.initialize()
        
        # Cargar assets
        self._load_assets()

    def _setup_colors(self) -> None:
        """Configura la paleta de colores."""
        self.bg_color = (27, 64, 114)
        self.peg_color = (200, 200, 200)
        self.ball_color = (100, 200, 255)  # Color único para todas las pelotas
        self.text_color = (255, 255, 255)
        self.top_bg_color = (40, 40, 60, 180)  # Fondo semi-transparente para el top

    def _load_assets(self) -> None:
        """Carga imágenes y fuentes."""
        # Cargar imagen de fondo
        try:
            bg_path = app_config.IMAGES_DIR / "backgroundS.png"
            if bg_path.exists():
                self.bg_image = pygame.image.load(str(bg_path))
                self.bg_image = pygame.transform.scale(self.bg_image, (self.hires_width, self.hires_height))
                print(f"✅ Imagen de fondo cargada: {bg_path.name}")
            else:
                self.bg_image = None
                print(f"⚠️  Imagen de fondo no encontrada: {bg_path}")
        except Exception as e:
            print(f"❌ Error cargando imagen de fondo: {e}")
            self.bg_image = None

        # Configurar fuentes
        self.font = pygame.font.SysFont("Arial", 24 * self.scale)
        self.small_font = pygame.font.SysFont("Arial", 18 * self.scale)
        self.large_font = pygame.font.SysFont("Arial", 32 * self.scale)
        
        # Fuente especial para emojis
        try:
            # Intentar cargar una fuente que soporte mejor los emojis
            self.emoji_font = pygame.font.SysFont("Segoe UI Emoji", 24 * self.scale)
            if not self.emoji_font:
                self.emoji_font = pygame.font.SysFont("Apple Color Emoji", 24 * self.scale)
            if not self.emoji_font:
                self.emoji_font = pygame.font.SysFont("Noto Color Emoji", 24 * self.scale)
        except:
            pass
        
        # Si no se pudo cargar fuente de emoji, usar la fuente normal
        if not hasattr(self, 'emoji_font') or not self.emoji_font:
            self.emoji_font = self.font

    def draw(self) -> None:
        """Renderiza un frame completo."""
        dt = self.clock.get_time() / 1000.0
        
        # Actualizar sistemas
        self.particle_system.update(dt)
        self._generate_trail_particles()
        self._handle_sound_events()
        
        # Renderizar en superficie de alta resolución
        self._draw_background()
        self._draw_pegs()
        self._draw_slots()
        self._draw_particles()
        self._draw_balls()
        self._draw_top_users()
        self._render_screen_messages(self.hires_surface)

        # Escalar a pantalla final
        pygame.transform.smoothscale(
            self.hires_surface, (self.lores_width, self.lores_height), self.screen
        )

        pygame.display.flip()

    def _draw_background(self) -> None:
        """Dibuja el fondo."""
        if self.bg_image:
            self.hires_surface.blit(self.bg_image, (0, 0))
        else:
            self.hires_surface.fill(self.bg_color)

    def _draw_pegs(self) -> None:
        """Dibuja todos los pegs con efectos."""
        glow_duration = 0.5
        
        for peg in self.game_state.pegs:
            peg_center = (int(peg.x * self.scale), int(peg.y * self.scale))
            peg_radius = int(peg.radius * self.scale)
            
            # Sombra del peg
            self._draw_peg_shadow(peg_center, peg_radius)
            
            # Efecto de brillo si fue golpeado
            if peg.hit_timer > 0:
                self._draw_peg_glow(peg, peg_center, peg_radius, glow_duration)
            
            # Peg principal
            pygame.draw.circle(self.hires_surface, self.peg_color, peg_center, peg_radius)
            
            # Efecto de luna (highlight)
            self._draw_peg_highlight(peg_center, peg_radius)

    def _draw_peg_shadow(self, center: tuple[int, int], radius: int) -> None:
        """Dibuja la sombra de un peg."""
        shadow_offset = 3 * self.scale
        shadow_blur = 8 * self.scale
        shadow_center = (center[0] + shadow_offset, center[1] + shadow_offset)
        
        shadow_size = int((radius + shadow_blur) * 2)
        shadow_surface = pygame.Surface((shadow_size, shadow_size), pygame.SRCALPHA)
        shadow_surf_center = (shadow_size // 2, shadow_size // 2)
        
        pygame.draw.circle(shadow_surface, (0, 0, 0, 40), shadow_surf_center, radius)
        
        # Simular blur
        blur_size = (shadow_size // 6, shadow_size // 6)
        small_shadow = pygame.transform.smoothscale(shadow_surface, blur_size)
        blurred_shadow = pygame.transform.smoothscale(small_shadow, (shadow_size, shadow_size))
        
        shadow_pos = (shadow_center[0] - shadow_size // 2, shadow_center[1] - shadow_size // 2)
        self.hires_surface.blit(blurred_shadow, shadow_pos, special_flags=pygame.BLEND_ALPHA_SDL2)

    def _draw_peg_glow(self, peg, center: tuple[int, int], radius: int, glow_duration: float) -> None:
        """Dibuja el efecto de brillo del peg."""
        t = peg.hit_timer / glow_duration
        
        base_radius = radius
        glow_radius = int(base_radius * (3 + 2 * t))
        core_radius = base_radius + int(base_radius * 0.7 * t)

        glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (255, 255, 255), (glow_radius, glow_radius), core_radius)

        # Simular blur gaussiano
        temp_size = (glow_radius * 2 // 4, glow_radius * 2 // 4)
        small_surf = pygame.transform.smoothscale(glow_surf, temp_size)
        blurred_surf = pygame.transform.smoothscale(small_surf, (glow_radius * 2, glow_radius * 2))

        alpha = int(255 * t**1.5)
        blurred_surf.set_alpha(alpha)

        self.hires_surface.blit(
            blurred_surf,
            (center[0] - glow_radius, center[1] - glow_radius),
            special_flags=pygame.BLEND_RGBA_ADD,
        )

    def _draw_peg_highlight(self, center: tuple[int, int], radius: int) -> None:
        """Dibuja el efecto de highlight del peg."""
        moon_shadow_color = (255, 255, 255)
        moon_offset = radius * -0.3
        moon_center = (center[0] + moon_offset, center[1] + moon_offset)
        moon_radius = int(radius * 0.9)
        
        mask_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(mask_surface, (255, 255, 255, 255), (radius, radius), radius)
        
        shadow_internal_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        internal_shadow_pos = (moon_center[0] - center[0] + radius, moon_center[1] - center[1] + radius)
        pygame.draw.circle(shadow_internal_surface, moon_shadow_color, internal_shadow_pos, moon_radius)
        
        shadow_internal_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        self.hires_surface.blit(shadow_internal_surface, (center[0] - radius, center[1] - radius), special_flags=pygame.BLEND_ALPHA_SDL2)

    def _draw_slots(self) -> None:
        """Dibuja las ranuras de puntuación."""
        max_pegs = self.game_state.config.top_pegs + self.game_state.config.rows - 1
        slot_count = max_pegs - 1
        
        slot_margin = 8 * self.scale
        total_margin_space = slot_margin * (slot_count - 1)
        available_width = self.hires_width - total_margin_space
        slot_width = available_width / (max_pegs + 1)
        slot_height = 40 * self.scale
        bottom_margin = 5 * self.scale

        base_colors = [
            (25, 244, 26),
            (113, 247, 32),
            (203, 251, 31),
            (250, 152, 2),
            (244, 54, 6),
        ]

        def color_for_index(i: int) -> tuple[int, int, int]:
            mid = slot_count // 2
            distance = abs(i - mid)
            idx = min(distance, len(base_colors) - 1)
            return base_colors[idx]

        for i in range(slot_count):
            points = (self.game_state.config.slot_scores[i] 
                     if i < len(self.game_state.config.slot_scores) 
                     else self.game_state.config.slot_scores[-1])

            color = color_for_index(i)
            x = (i + 1) * slot_width + i * slot_margin
            y = self.hires_height - slot_height - bottom_margin
            rect = pygame.Rect(x, y, slot_width, slot_height)
            
            # Sombra del slot
            self._draw_slot_shadow(x, y, slot_width, slot_height)
            
            # Slot principal
            border_radius = int(5 * self.scale)
            pygame.draw.rect(self.hires_surface, color, rect, border_radius=border_radius)
            
            # Texto de puntos
            label = f"{points}"
            text_color = (0, 0, 0)
            text = self.font.render(label, True, text_color)
            txt_rect = text.get_rect(center=(x + slot_width / 2, y + slot_height / 2))
            self.hires_surface.blit(text, txt_rect)

    def _draw_slot_shadow(self, x: float, y: float, width: float, height: float) -> None:
        """Dibuja la sombra de un slot."""
        shadow_offset = 4 * self.scale
        shadow_blur = 16 * self.scale
        
        shadow_surface = pygame.Surface((width + shadow_blur * 2, height + shadow_blur * 2), pygame.SRCALPHA)
        shadow_color = (0, 0, 0, 60)
        
        shadow_base_rect = pygame.Rect(shadow_blur, shadow_blur, width, height)
        pygame.draw.rect(shadow_surface, shadow_color, shadow_base_rect, border_radius=int(5 * self.scale))
        
        # Simular blur
        blur_size_1 = (int((width + shadow_blur * 2) // 8), int((height + shadow_blur * 2) // 8))
        small_surface_1 = pygame.transform.smoothscale(shadow_surface, blur_size_1)
        medium_surface = pygame.transform.smoothscale(small_surface_1, (int((width + shadow_blur * 2) // 2), int((height + shadow_blur * 2) // 2)))
        blurred_shadow = pygame.transform.smoothscale(medium_surface, (width + shadow_blur * 2, height + shadow_blur * 2))
        
        shadow_pos = (x + shadow_offset - shadow_blur, y + shadow_offset - shadow_blur)
        self.hires_surface.blit(blurred_shadow, shadow_pos, special_flags=pygame.BLEND_ALPHA_SDL2)

    def _draw_balls(self) -> None:
        """Dibuja todas las pelotas."""
        for ball in self.game_state.balls:
            center = (int(ball.x * self.scale), int(ball.y * self.scale))
            radius_px = int(ball.radius * self.scale)
            
            if ball.avatar_surface is not None:
                self._draw_ball_with_avatar(ball, center, radius_px)
            else:
                self._draw_ball_simple(ball, center, radius_px)

    def _draw_ball_with_avatar(self, ball, center: tuple[int, int], radius_px: int) -> None:
        """Dibuja una pelota con avatar."""
        diameter = radius_px * 2
        
        # Escalar avatar al tamaño original
        avatar_img = pygame.transform.smoothscale(ball.avatar_surface, (diameter, diameter))
        
        # Rotar el avatar manteniendo el tamaño original
        rotated_avatar = pygame.transform.rotate(avatar_img, ball.rotation)
        
        # Crear superficie del tamaño original para mantener consistencia
        final_avatar = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
        
        # Centrar la imagen rotada en la superficie original
        rotated_rect = rotated_avatar.get_rect(center=(diameter // 2, diameter // 2))
        final_avatar.blit(rotated_avatar, rotated_rect)
        
        # Aplicar máscara circular al tamaño original
        mask = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
        pygame.draw.circle(mask, (255, 255, 255, 255), (radius_px, radius_px), radius_px)
        final_avatar.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        # Borde de la pelota
        pygame.draw.circle(self.hires_surface, self.ball_color, center, radius_px + 3)

        # Avatar con tamaño consistente
        rect = final_avatar.get_rect(center=center)
        self.hires_surface.blit(final_avatar, rect)

    def _draw_ball_simple(self, ball, center: tuple[int, int], radius_px: int) -> None:
        """Dibuja una pelota simple sin avatar."""
        pygame.draw.circle(self.hires_surface, self.ball_color, center, radius_px)

    def _draw_particles(self) -> None:
        """Dibuja todas las partículas activas."""
        for particle in self.particle_system.get_particles():
            life_ratio = particle.life / particle.max_life
            alpha = int(255 * life_ratio * life_ratio)
            alpha = max(0, min(255, alpha))
            
            if alpha > 5:
                x = int(particle.x * self.scale)
                y = int(particle.y * self.scale)
                size = max(1, int(particle.size * self.scale * life_ratio))
                
                color = (*particle.color, alpha)
                
                temp_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surface, color, (size, size), size)
                
                self.hires_surface.blit(temp_surface, (x - size, y - size))

    def _draw_top_users(self) -> None:
        """Dibuja el top de usuarios."""
        top_users = self.game_state.get_top_users(limit=6)
        
        if not top_users:
            return
        
        # Configuración del panel (más pequeño)
        panel_width = 200 * self.scale
        panel_height = min(250 * self.scale, 40 * self.scale + len(top_users) * 35 * self.scale)
        panel_x = 0  # Sin margen izquierdo
        panel_y = 0  # Sin margen superior
        
        # Fondo semi-transparente
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surface.fill(self.top_bg_color)
        self.hires_surface.blit(panel_surface, (panel_x, panel_y))
        
        # Título con emoji visible - renderizar por separado para mejor compatibilidad
        emoji_text = self.emoji_font.render("🏆", True, self.text_color)
        title_text = self.font.render(" TOP USUARIOS", True, self.text_color)
        
        # Calcular posición centrada total
        total_width = emoji_text.get_width() + title_text.get_width()
        start_x = panel_x + (panel_width - total_width) // 2
        y_pos = panel_y + 8 * self.scale
        
        # Dibujar emoji y texto
        self.hires_surface.blit(emoji_text, (start_x, y_pos))
        self.hires_surface.blit(title_text, (start_x + emoji_text.get_width(), y_pos))
        
        # Lista de usuarios
        start_y = panel_y + 35 * self.scale
        for i, user in enumerate(top_users):
            y_pos = start_y + i * 35 * self.scale
            
            # Posición del ranking
            rank_text = f"{i + 1}."
            rank_surface = self.small_font.render(rank_text, True, self.text_color)
            self.hires_surface.blit(rank_surface, (panel_x + 8 * self.scale, y_pos))
            
            # Avatar del usuario (si existe) - más pequeño
            avatar_size = 24 * self.scale
            avatar_x = panel_x + 28 * self.scale
            if user.avatar_surface:
                try:
                    avatar_scaled = pygame.transform.smoothscale(user.avatar_surface, (avatar_size, avatar_size))
                    
                    # Crear máscara circular para el avatar
                    circular_avatar = pygame.Surface((avatar_size, avatar_size), pygame.SRCALPHA)
                    circular_avatar.blit(avatar_scaled, (0, 0))
                    
                    mask = pygame.Surface((avatar_size, avatar_size), pygame.SRCALPHA)
                    pygame.draw.circle(mask, (255, 255, 255, 255), (avatar_size // 2, avatar_size // 2), avatar_size // 2)
                    circular_avatar.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                    
                    self.hires_surface.blit(circular_avatar, (avatar_x, y_pos - 3 * self.scale))
                except:
                    # Si falla el avatar, dibujar un círculo
                    pygame.draw.circle(self.hires_surface, self.ball_color, 
                                     (avatar_x + avatar_size // 2, y_pos + avatar_size // 2 - 3 * self.scale), 
                                     avatar_size // 2)
            else:
                # Sin avatar, dibujar un círculo
                pygame.draw.circle(self.hires_surface, self.ball_color, 
                                 (avatar_x + avatar_size // 2, y_pos + avatar_size // 2 - 3 * self.scale), 
                                 avatar_size // 2)
            
            # Nombre del usuario - más corto para el panel pequeño
            username_text = user.username[:10] + ("..." if len(user.username) > 10 else "")
            username_surface = self.small_font.render(username_text, True, self.text_color)
            self.hires_surface.blit(username_surface, (avatar_x + avatar_size + 8 * self.scale, y_pos))
            
            # Puntuación
            score_text = f"${user.score}"
            score_surface = self.small_font.render(score_text, True, (255, 215, 0))  # Dorado
            score_rect = score_surface.get_rect(right=panel_x + panel_width - 8 * self.scale, y=y_pos)
            self.hires_surface.blit(score_surface, score_rect)

    def _render_screen_messages(self, surface: pygame.Surface) -> None:
        """Renderiza mensajes en pantalla de comandos centrados en el medio."""
        if not hasattr(self.game_state, 'command_processor'):
            return
        
        for i, msg in enumerate(self.game_state.command_processor.screen_messages):
            # Calcular alpha basado en tiempo restante
            elapsed = time.time() - msg.timestamp
            remaining = max(0, msg.duration - elapsed)
            alpha = int(255 * (remaining / msg.duration))
            
            if alpha <= 0:
                continue
            
            # Configuración del mensaje
            msg_width = 600 * self.scale
            msg_height = 80 * self.scale
            avatar_size = 50 * self.scale
            
            # Crear superficie del mensaje con bordes redondeados
            msg_surface = pygame.Surface((msg_width, msg_height), pygame.SRCALPHA)
            
            # Fondo con bordes redondeados y gradiente
            border_radius = int(15 * self.scale)
            
            # Fondo principal
            pygame.draw.rect(msg_surface, (0, 0, 0, 180), 
                           (0, 0, msg_width, msg_height), 
                           border_radius=border_radius)
            
            # Borde brillante
            pygame.draw.rect(msg_surface, (100, 200, 255, 100), 
                           (0, 0, msg_width, msg_height), 
                           width=int(3 * self.scale), 
                           border_radius=border_radius)
            
            # Avatar del usuario (circular)
            avatar_x = int(15 * self.scale)
            avatar_y = int((msg_height - avatar_size) // 2)
            
            if msg.avatar_surface:
                try:
                    # Escalar avatar
                    avatar_scaled = pygame.transform.smoothscale(
                        msg.avatar_surface, (avatar_size, avatar_size)
                    )
                    
                    # Crear máscara circular
                    circular_avatar = pygame.Surface((avatar_size, avatar_size), pygame.SRCALPHA)
                    circular_avatar.blit(avatar_scaled, (0, 0))
                    
                    mask = pygame.Surface((avatar_size, avatar_size), pygame.SRCALPHA)
                    pygame.draw.circle(mask, (255, 255, 255, 255), 
                                     (avatar_size // 2, avatar_size // 2), 
                                     avatar_size // 2)
                    circular_avatar.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                    
                    # Borde del avatar
                    pygame.draw.circle(msg_surface, (255, 255, 255, 150), 
                                     (avatar_x + avatar_size // 2, avatar_y + avatar_size // 2), 
                                     avatar_size // 2 + int(2 * self.scale), 
                                     width=int(2 * self.scale))
                    
                    msg_surface.blit(circular_avatar, (avatar_x, avatar_y))
                except:
                    # Fallback: círculo simple
                    pygame.draw.circle(msg_surface, (100, 200, 255), 
                                     (avatar_x + avatar_size // 2, avatar_y + avatar_size // 2), 
                                     avatar_size // 2)
            else:
                # Sin avatar: círculo simple
                pygame.draw.circle(msg_surface, (100, 200, 255), 
                                 (avatar_x + avatar_size // 2, avatar_y + avatar_size // 2), 
                                 avatar_size // 2)
            
            # Texto del usuario
            text_x = avatar_x + avatar_size + int(15 * self.scale)
            user_text = self.font.render(f"@{msg.username}", True, (255, 255, 255))
            msg_surface.blit(user_text, (text_x, int(15 * self.scale)))
            
            # Mensaje principal (más grande y destacado)
            message_font = self.large_font  # Usar fuente más grande
            message_text = message_font.render(msg.message, True, (255, 255, 100))
            msg_surface.blit(message_text, (text_x, int(40 * self.scale)))
            
            # Aplicar alpha
            msg_surface.set_alpha(alpha)
            
            # Posición centrada en pantalla
            # Centrar horizontalmente
            center_x = (self.hires_width - msg_width) // 2
            
            # Centrar verticalmente, pero con offset para múltiples mensajes
            base_center_y = (self.hires_height - msg_height) // 2
            offset_y = i * (msg_height + int(20 * self.scale))  # Separación entre mensajes
            final_y = base_center_y + offset_y - (len(self.game_state.command_processor.screen_messages) - 1) * (msg_height + int(20 * self.scale)) // 2
            
            # Asegurar que no se salga de la pantalla
            final_y = max(int(20 * self.scale), min(final_y, self.hires_height - msg_height - int(20 * self.scale)))
            
            surface.blit(msg_surface, (center_x, final_y)) 
    def _generate_trail_particles(self) -> None:
        """Genera partículas de estela para las pelotas."""
        for ball in self.game_state.balls:
            if ball.active:
                particles_to_generate = 2 if random.random() < 0.8 else 3
                
                for i in range(particles_to_generate):
                    trail_x = ball.x + random.uniform(-ball.radius, ball.radius)
                    trail_y = ball.y + random.uniform(0, ball.radius)
                    
                    self.particle_system.add_trail_particle(trail_x, trail_y, 0, 0, self.ball_color)

    def _handle_sound_events(self) -> None:
        """Maneja los eventos de sonido."""
        # Procesar eventos de sonido de slots
        while self.game_state.sound_events:
            sound_event = self.game_state.sound_events.pop(0)
            
            if isinstance(sound_event, tuple) and sound_event[0] == "slot_hit":
                _, x, y = sound_event
                self.audio_manager.play_slot_hit()
                self.particle_system.add_celebration_particles(x, y, count=8)
            elif sound_event == "slot_hit":
                self.audio_manager.play_slot_hit()
        
        # Verificar sonidos de pegs
        glow_duration = 0.5
        for peg in self.game_state.pegs:
            if peg.hit_timer > (glow_duration - 0.05):
                if not hasattr(peg, 'sound_played') or not peg.sound_played:
                    peg.sound_played = True
                    self.audio_manager.play_peg_hit()
                    self.particle_system.add_collision_particles(peg.x, peg.y, count=4)
            elif peg.hit_timer <= 0:
                if hasattr(peg, 'sound_played'):
                    peg.sound_played = False

    def get_clock(self) -> pygame.time.Clock:
        """Retorna el reloj del renderizador."""
        return self.clock

    def cleanup(self) -> None:
        """Limpia los recursos del renderizador."""
        self.audio_manager.cleanup()
        pygame.quit() 