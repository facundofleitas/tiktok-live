# Guía de Migración - TikTok Plinko Battle

## Resumen de Cambios

El proyecto ha sido completamente refactorizado para mejorar la modularidad, mantenibilidad y extensibilidad. Esta guía te ayudará a entender los cambios y cómo migrar al nuevo sistema.

## Estructura Anterior vs Nueva

### Antes (Estructura Monolítica)
```
tiktok-live/
├── main.py                 # Todo el código mezclado (649 líneas)
├── tiktok_plinko/
│   ├── event_sources.py    # Eventos básicos
│   ├── game_logic.py       # Lógica del juego
│   └── tiktok_source.py    # Solo TikTok
└── content/                # Assets
```

### Después (Estructura Modular)
```
tiktok-live/
├── main_new.py             # Punto de entrada simple
├── src/
│   ├── core/               # Lógica central
│   ├── events/             # Sistema de eventos extensible
│   ├── rendering/          # Gráficos y audio separados
│   ├── app/                # Coordinación de componentes
│   └── utils/              # Utilidades reutilizables
├── docs/                   # Documentación
└── content/                # Assets (sin cambios)
```

## Cambios Principales

### 1. Separación de Responsabilidades

**Antes**: Todo mezclado en `main.py`
```python
# 649 líneas con renderizado, lógica, eventos, audio, etc.
class PygameRenderer:
    def __init__(self, game_state):
        # Inicialización de pygame
        # Carga de sonidos
        # Configuración de colores
        # Sistema de partículas
        # Todo mezclado...
```

**Después**: Cada responsabilidad en su módulo
```python
# src/rendering/pygame_renderer.py - Solo renderizado
# src/rendering/audio.py - Solo audio
# src/rendering/particles.py - Solo partículas
# src/core/game_logic.py - Solo lógica del juego
```

### 2. Sistema de Eventos Mejorado

**Antes**: Callbacks básicos
```python
class EventSource(ABC):
    def on_comment(self, cb): ...
    def on_like(self, cb): ...
    def on_follow(self, cb): ...
```

**Después**: Sistema extensible con nuevos eventos
```python
class EventSource(ABC):
    def on_comment(self, cb): ...
    def on_like(self, cb): ...
    def on_follow(self, cb): ...
    def on_donation(self, cb): ...    # ¡NUEVO!
    def on_share(self, cb): ...       # ¡NUEVO!
    async def stop(self): ...         # ¡NUEVO!
```

### 3. Configuración Centralizada

**Antes**: Configuración dispersa
```python
# En main.py
sounds_path = "content/sounds"
images_path = "content/images"
scale = 3
TARGET_FPS = 60
# Valores hardcodeados por todo el código...
```

**Después**: Configuración centralizada
```python
# src/core/config.py
@dataclass
class AppConfig:
    SOUNDS_DIR: Path = Path("content/sounds")
    IMAGES_DIR: Path = Path("content/images")
    DEFAULT_SCALE: int = 3
    TARGET_FPS: int = 60

# Uso en cualquier módulo
from src.core.config import app_config
```

## Cómo Migrar

### 1. Ejecutar la Nueva Versión

```bash
# Ahora simplemente usar:
python main.py

# Con TikTok:
python main.py --tiktok username

# Con logging detallado:
python main.py --verbose
```

### 2. Importaciones Actualizadas

**Antes**:
```python
from tiktok_plinko.game_logic import GameState, GameConfig, Team
from tiktok_plinko.event_sources import DummyEventSource
from tiktok_plinko.tiktok_source import TikTokEventSource
```

**Después**:
```python
from src.core import GameState, GameConfig, Team
from src.events import DummyEventSource, TikTokEventSource
from src.rendering import PygameRenderer, AudioManager
from src.app import GameApp, EventCoordinator
```

### 3. Nuevas Funcionalidades

#### Manejo de Donaciones
```python
# Ahora las donaciones están soportadas nativamente
event_source.on_donation(lambda username, amount, avatar: 
    print(f"¡{username} donó ${amount}!"))
```

#### Sistema de Audio Mejorado
```python
from src.rendering import AudioManager

audio = AudioManager()
audio.initialize()
audio.play_donation()  # Nuevo sonido para donaciones
audio.set_volume(0.8)  # Control de volumen
```

#### Cache de Avatares
```python
from src.utils import AvatarLoader

loader = AvatarLoader()
avatar = loader.load_avatar(url)  # Con cache automático
print(f"Cache size: {loader.get_cache_size()}")
```

#### Inferencia de Equipos Mejorada
```python
from src.utils import TeamInference

inference = TeamInference()
team = inference.infer_team_from_comment("¡Vamos chicas!")
stats = inference.get_keyword_stats("Las mujeres son las mejores")
```

## Ventajas de la Nueva Estructura

### ✅ Mantenibilidad
- Cada archivo tiene una responsabilidad específica
- Más fácil encontrar y modificar código
- Menos riesgo de romper funcionalidades no relacionadas

### ✅ Extensibilidad
- Agregar nuevas fuentes de eventos es trivial
- Nuevos efectos visuales se agregan fácilmente
- Sistema de configuración flexible

### ✅ Testabilidad
- Cada módulo se puede testear independientemente
- Mocking más fácil para pruebas unitarias
- Lógica del juego separada del renderizado

### ✅ Reutilización
- Utilidades como `AvatarLoader` se pueden usar en otros proyectos
- Sistema de eventos se puede adaptar a otras plataformas
- Renderizador se puede intercambiar por otras implementaciones

## Compatibilidad

### ✅ Mantiene Compatibilidad
- Los archivos de contenido (`content/`) no cambian
- Los comandos básicos funcionan igual
- El gameplay es idéntico

### ⚠️ Cambios Menores
- Nuevo archivo de entrada: `main_new.py`
- Nuevas opciones de línea de comandos
- Logging mejorado

## Próximos Pasos

1. **Probar la nueva versión**: `python main.py`
2. **Revisar la documentación**: `docs/ARCHITECTURE.md`
3. **Experimentar con nuevas funcionalidades**:
   - Donaciones
   - Shares
   - Cache de avatares
   - Inferencia de equipos mejorada

## Solución de Problemas

### Error: "No module named 'src'"
```bash
# Asegúrate de estar en el directorio raíz del proyecto
cd /path/to/tiktok-live
python main.py
```

### Error: "TikTokLive no está disponible"
```bash
pip install TikTokLive
```

### Problemas de audio
```bash
# Verifica que los archivos de sonido existan
ls content/sounds/
```

### Performance issues
```python
# Ajustar configuración en src/core/config.py
app_config.DEFAULT_SCALE = 2  # Reducir de 3 a 2
app_config.TARGET_FPS = 30    # Reducir de 60 a 30
```

## Migración Gradual

Puedes mantener ambas versiones durante la transición:

1. **Fase 1**: Probar la nueva estructura modular
2. **Fase 2**: Adaptar cualquier código personalizado
3. **Fase 3**: Migración completada
4. **Fase 4**: Optimizar y personalizar

¡La nueva estructura está lista para futuras extensiones como YouTube Live, Twitch, y muchas más funcionalidades! 