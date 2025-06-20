# Arquitectura del Proyecto TikTok Plinko Battle

## Estructura Modular

El proyecto ha sido refactorizado siguiendo principios de arquitectura limpia y modularidad. La nueva estructura permite fácil extensión y mantenimiento.

```
src/
├── core/                    # Lógica central del juego
│   ├── __init__.py
│   ├── config.py           # Configuración centralizada
│   └── game_logic.py       # Estados, entidades y lógica del juego
├── events/                  # Sistema de eventos de streaming
│   ├── __init__.py
│   ├── base.py             # Interfaz abstracta para eventos
│   ├── dummy.py            # Generador de eventos para pruebas
│   └── tiktok.py           # Eventos de TikTok Live
├── rendering/               # Sistema de renderizado y gráficos
│   ├── __init__.py
│   ├── audio.py            # Manejo de audio
│   ├── particles.py        # Sistema de partículas
│   └── pygame_renderer.py  # Renderizador principal
├── app/                     # Aplicación principal y coordinación
│   ├── __init__.py
│   ├── event_coordinator.py # Coordinador de eventos
│   └── game_app.py         # Aplicación principal
└── utils/                   # Utilidades y helpers
    ├── __init__.py
    ├── avatar_loader.py     # Cargador de avatares con cache
    └── team_inference.py    # Inferencia de equipos
```

## Principios de Diseño

### 1. Separación de Responsabilidades
- **Core**: Lógica del juego pura, sin dependencias externas
- **Events**: Manejo de eventos de diferentes fuentes de streaming
- **Rendering**: Todo lo relacionado con gráficos, audio y efectos visuales
- **App**: Coordinación y orquestación de componentes
- **Utils**: Funciones auxiliares reutilizables

### 2. Inversión de Dependencias
- Las clases abstractas definen contratos claros
- Los módulos de alto nivel no dependen de implementaciones específicas
- Fácil intercambio de implementaciones (ej: TikTok vs Dummy events)

### 3. Extensibilidad
- Nuevas fuentes de eventos se pueden agregar implementando `EventSource`
- Nuevos tipos de eventos se manejan en el `EventCoordinator`
- Efectos visuales se pueden extender en el sistema de partículas

## Componentes Principales

### Core Module
```python
from src.core import GameState, GameConfig, Team
```
- `GameState`: Estado completo del juego
- `GameConfig`: Configuración del tablero y física
- `Team`: Enumeración de equipos
- `Ball`, `Peg`: Entidades del juego

### Events Module
```python
from src.events import EventSource, TikTokEventSource, DummyEventSource
```
- `EventSource`: Interfaz abstracta para fuentes de eventos
- `TikTokEventSource`: Conexión a TikTok Live
- `DummyEventSource`: Generador de eventos para pruebas

### Rendering Module
```python
from src.rendering import PygameRenderer, AudioManager, SimpleParticleSystem
```
- `PygameRenderer`: Renderizador principal con supersampling
- `AudioManager`: Manejo centralizado de audio
- `SimpleParticleSystem`: Efectos visuales de partículas

### App Module
```python
from src.app import GameApp, EventCoordinator
```
- `GameApp`: Aplicación principal y loop del juego
- `EventCoordinator`: Conecta eventos con el estado del juego

## Flujo de Datos

```
[TikTok Live] → [EventSource] → [EventCoordinator] → [GameState]
                                                         ↓
[Pygame Display] ← [PygameRenderer] ← [ParticleSystem] ← [GameState]
                         ↓
                   [AudioManager]
```

## Extensiones Futuras

### Nuevos Tipos de Eventos
Para agregar un nuevo tipo de evento (ej: subscripciones):

1. Agregar callback en `EventSource.base`:
```python
def on_subscription(self, cb: Callable[[str, str], None]) -> None:
    self._on_subscription_cb = cb
```

2. Implementar en fuentes específicas (`TikTokEventSource`)
3. Manejar en `EventCoordinator`

### Nuevas Fuentes de Streaming
Para agregar soporte a YouTube Live, Twitch, etc:

1. Crear nueva clase heredando de `EventSource`
2. Implementar métodos `run()` y `stop()`
3. Emitir eventos usando los métodos `_emit_*`

### Nuevos Efectos Visuales
Para agregar nuevos efectos:

1. Extender `SimpleParticleSystem` con nuevos métodos
2. Llamar desde `PygameRenderer` según eventos del juego
3. Agregar sonidos correspondientes en `AudioManager`

## Configuración

La configuración centralizada está en `src/core/config.py`:

```python
from src.core.config import app_config

# Modificar configuración
app_config.TARGET_FPS = 120
app_config.DEFAULT_SCALE = 4
```

## Testing

La estructura modular facilita el testing:

```python
# Test de lógica pura
from src.core import GameState, GameConfig
game_state = GameState(GameConfig())

# Test de eventos
from src.events import DummyEventSource
event_source = DummyEventSource(interval=0.1)

# Test de renderizado (con mock)
from src.rendering import AudioManager
audio = AudioManager()
```

## Comandos de Ejecución

```bash
# Ejecutar con eventos dummy
python main.py

# Ejecutar con TikTok Live
python main.py --tiktok username

# Ejecutar con logging detallado
python main.py --verbose

# Controles en juego
# ESC: Salir
# R: Reiniciar
# SPACE: Pausa (futuro)
``` 