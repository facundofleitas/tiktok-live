"""
Sistema de partículas para efectos visuales.
"""

import math
import random
from typing import List, Tuple


class SimpleParticle:
    """Partícula simple para efectos visuales."""
    
    def __init__(self, x: float, y: float, vx: float, vy: float, life: float, color: Tuple[int, int, int], size: float):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.color = color
        self.size = size
    
    def update(self, dt: float) -> bool:
        """Actualiza la partícula. Retorna False si debe eliminarse."""
        # Mover la partícula
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Gravedad ligera
        gravity_force = 25 * dt
        self.vy += gravity_force
        
        # Limitar velocidad hacia abajo
        if self.vy > 20:
            self.vy = 20
        
        # Resistencia del aire
        damping = 0.96
        self.vx *= damping
        self.vy *= damping
        
        # Reducir vida
        self.life -= dt
        
        return self.life > 0


class SimpleParticleSystem:
    """Sistema de gestión de partículas."""
    
    def __init__(self):
        self.particles: List[SimpleParticle] = []
    
    def add_trail_particle(self, ball_x: float, ball_y: float, ball_vx: float, ball_vy: float, ball_color: Tuple[int, int, int]) -> None:
        """Agrega una partícula de estela detrás de una pelota."""
        # Posición con poca dispersión
        offset_x = random.uniform(-2, 2)
        offset_y = random.uniform(-20, 2)
        
        # Velocidad hacia arriba con variación lateral
        angle = random.uniform(-2.35, -0.785)  # -135° a -45°
        speed = random.uniform(10, 30)
        
        particle_vx = math.cos(angle) * speed
        particle_vy = math.sin(angle) * speed
        
        particle = SimpleParticle(
            x=ball_x + offset_x,
            y=ball_y + offset_y,
            vx=particle_vx,
            vy=particle_vy,
            life=random.uniform(0.8, 1.5),
            color=ball_color,
            size=random.uniform(1.5, 3.5)
        )
        self.particles.append(particle)
    
    def add_collision_particles(self, x: float, y: float, count: int = 6) -> None:
        """Agrega partículas cuando hay una colisión."""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(30, 80)
            
            particle = SimpleParticle(
                x=x,
                y=y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                life=random.uniform(0.4, 1.0),
                color=(255, 255, 100),  # Amarillo brillante
                size=random.uniform(1.5, 3.5)
            )
            self.particles.append(particle)
    
    def add_celebration_particles(self, x: float, y: float, count: int = 10) -> None:
        """Agrega partículas de celebración cuando llega a un slot."""
        colors = [(255, 215, 0), (255, 140, 0), (255, 69, 0), (255, 255, 0)]
        
        for _ in range(count):
            angle = random.uniform(-math.pi/3, -2*math.pi/3)  # Hacia arriba
            speed = random.uniform(60, 120)
            
            particle = SimpleParticle(
                x=x + random.uniform(-10, 10),
                y=y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                life=random.uniform(0.8, 1.5),
                color=random.choice(colors),
                size=random.uniform(2, 6)
            )
            self.particles.append(particle)
    
    def add_donation_particles(self, x: float, y: float, count: int = 15) -> None:
        """Agrega partículas especiales para donaciones."""
        colors = [(255, 215, 0), (255, 165, 0), (255, 69, 0), (255, 20, 147)]  # Dorados y rosa
        
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(40, 100)
            
            particle = SimpleParticle(
                x=x + random.uniform(-15, 15),
                y=y + random.uniform(-15, 15),
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                life=random.uniform(1.0, 2.0),  # Vida más larga
                color=random.choice(colors),
                size=random.uniform(3, 8)  # Partículas más grandes
            )
            self.particles.append(particle)
    
    def update(self, dt: float) -> None:
        """Actualiza todas las partículas y elimina las que expiraron."""
        self.particles = [p for p in self.particles if p.update(dt)]
    
    def get_particles(self) -> List[SimpleParticle]:
        """Retorna la lista de partículas activas."""
        return self.particles
    
    def clear(self) -> None:
        """Limpia todas las partículas."""
        self.particles.clear() 