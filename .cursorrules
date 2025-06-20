# TikTok Plinko Top Users - Prompt para CURSOR

## 🎮 Descripción del Proyecto

**TikTok Plinko Top Users** es un juego interactivo en tiempo real que conecta con streams de TikTok Live para crear una experiencia de juego colaborativa. Los espectadores del stream pueden influir en el juego a través de sus interacciones (comentarios, follows, likes, donaciones), creando un ranking de usuarios basado en sus puntuaciones individuales en un tablero de Plinko.

### Concepto Principal
- **Plinko Game**: Tablero con pegs donde caen pelotas que rebotan hasta llegar a slots de puntuación
- **Interactividad en Tiempo Real**: Los eventos del stream de TikTok generan pelotas en el juego
- **Sistema de Ranking**: Los espectadores compiten individualmente por el top de puntuaciones
- **Efectos Visuales**: Partículas, avatares de usuarios, sonidos y animaciones
- **Cantidad Configurable de Pelotas**: Cada tipo de evento genera diferente cantidad de pelotas
- **Sistema de Comandos**: Los usuarios pueden gastar puntos acumulados en comandos especiales

## 🏗️ Estructura del Proyecto

```
tiktok-live/
├── main.py                     # Punto de entrada principal
├── src/                        # Código fuente modular
│   ├── __init__.py
│   ├── core/                   # Lógica central del juego
│   │   ├── __init__.py
│   │   ├── config.py          # Configuración centralizada
│   │   ├── game_logic.py      # Estados, entidades y física del juego
│   │   └── commands.py        # Sistema de comandos con costo de puntos
│   ├── events/                 # Sistema de eventos de streaming
│   │   ├── __init__.py
│   │   ├── base.py            # Interfaz abstracta para eventos
│   │   ├── dummy.py           # Generador de eventos para pruebas
│   │   └── tiktok.py          # Eventos de TikTok Live
│   ├── rendering/              # Sistema de renderizado y gráficos
│   │   ├── __init__.py
│   │   ├── audio.py           # Manejo de audio
│   │   ├── particles.py       # Sistema de partículas
│   │   └── pygame_renderer.py # Renderizador principal con Pygame
│   ├── app/                    # Aplicación principal y coordinación
│   │   ├── __init__.py
│   │   ├── event_coordinator.py # Coordinador de eventos
│   │   └── game_app.py        # Aplicación principal
│   └── utils/                  # Utilidades y helpers
│       ├── __init__.py
│       └── avatar_loader.py   # Cargador de avatares con cache
├── content/                    # Assets del juego
│   ├── images/
│   │   └── backgroundS.png    # Imagen de fondo
│   └── sounds/
│       ├── happy-pop-sonido.wav    # Sonido de colisión
│       └── sonido-ganador.wav      # Sonido de puntuación
├── docs/                       # Documentación
│   └── ARCHITECTURE.md        # Documentación de arquitectura
├── MIGRATION_GUIDE.md         # Guía de migración
├── requirements.txt           # Dependencias de Python
└── README.md                  # Documentación principal
```

## ⭐ Features Principales

### 🎯 Gameplay Core
- **Tablero Plinko Dinámico**: Tablero triangular con pegs que generan rebotes físicos realistas
- **Sistema de Puntuación Individual**: Cada usuario acumula puntos según donde caigan sus pelotas
- **Física Realista**: Gravedad, rebotes, amortiguación y colisiones precisas
- **Top de Usuarios**: Ranking en tiempo real de los mejores jugadores

### 🔴 Integración TikTok Live
- **Conexión en Tiempo Real**: Escucha eventos de TikTok Live usando TikTokLive API
- **Múltiples Tipos de Eventos con Pelotas Configurables**:
  - **Comentarios** → 1 pelota por defecto (o comando especial)
  - **Likes** → 1 pelota por defecto
  - **Follows** → 2 pelotas por defecto
  - **Shares** → 3 pelotas por defecto
  - **Regalos/Donaciones** → 5 pelotas base + bonus según el monto

### 💬 Sistema de Comandos Interactivos
- **Comando `msg`**: Los usuarios pueden gastar 25 puntos para mostrar un mensaje personalizado en el centro de la pantalla
- **Formato**: `msg <mensaje>` (ejemplo: `msg Follow Me`)
- **Características**:
  - Mensaje centrado en pantalla con posición absoluta
  - Incluye avatar circular del usuario
  - Fondo elegante con bordes redondeados y efectos de brillo
  - Duración de 6 segundos con fade out gradual
  - Límite de 50 caracteres por mensaje
  - Múltiples mensajes se apilan verticalmente centrados
- **Verificación Automática**: Solo se ejecuta si el usuario tiene suficientes puntos
- **Cobro Automático**: Los puntos se descuentan automáticamente al ejecutar el comando

### 🎨 Sistema de Renderizado Avanzado
- **Supersampling 3x**: Renderizado en alta resolución para mejor calidad visual
- **Efectos Visuales**:
  - Sombras difuminadas en pegs y slots
  - Efectos de brillo (glow) cuando los pegs son golpeados
  - Sistema de partículas para estelas, colisiones y celebraciones
  - Avatares circulares de usuarios en las pelotas
  - Mensajes de comandos superpuestos en el centro de la pantalla
- **Top de Usuarios en Tiempo Real**: Panel lateral mostrando el ranking actual
- **Audio Dinámico**: Sonidos de colisión y puntuación sincronizados

### 🛠️ Arquitectura Modular
- **Separación de Responsabilidades**: Cada módulo tiene una función específica
- **Extensibilidad**: Fácil agregar nuevas fuentes de eventos (YouTube, Twitch)
- **Configuración Centralizada**: Todos los parámetros en un lugar, incluyendo cantidad de pelotas por evento
- **Sistema de Cache de Avatares**: Los avatares se cargan una vez y se reutilizan por usuario
- **Manejo de Errores Robusto**: Fallbacks para conexiones perdidas
- **Sistema de Comandos Extensible**: Arquitectura preparada para agregar más comandos

### 🎮 Controles y Funcionalidades
- **Controles de Teclado**:
  - `ESC`: Salir del juego
  - `R`: Reiniciar puntuaciones de todos los usuarios
  - `M`: Mutear/Desmutear audio
  - `SPACE`: Pausa (preparado para futuro)
- **Modos de Ejecución**:
  - Modo dummy (eventos simulados para pruebas)
  - Modo TikTok Live (conexión real)
  - Modo verbose (logging detallado)

### 📊 Sistema de Eventos Extensible
- **Interfaz Abstracta**: Fácil implementar nuevas fuentes de streaming
- **Coordinador de Eventos**: Conecta eventos con la lógica del juego
- **Callbacks Flexibles**: Sistema de callbacks para diferentes tipos de eventos
- **Manejo Asíncrono**: Eventos procesados sin bloquear el renderizado
- **Configuración de Pelotas**: Cantidad de pelotas por tipo de evento configurable
- **Procesamiento de Comandos**: Detección automática de comandos en comentarios

## 🚀 Tecnologías Utilizadas

- **Python 3.11+**: Lenguaje principal
- **Pygame**: Renderizado, audio y manejo de eventos
- **TikTokLive**: API para conectar con TikTok Live streams
- **asyncio**: Programación asíncrona para eventos
- **dataclasses**: Estructuras de datos modernas
- **pathlib**: Manejo moderno de rutas
- **urllib**: Descarga de avatares desde URLs

## 🎯 Casos de Uso

### Para Streamers
- Crear contenido interactivo en TikTok Live
- Aumentar engagement con la audiencia
- Gamificar el stream con competencias individuales entre usuarios
- Visualizar la participación de la comunidad en tiempo real
- Mostrar un top de usuarios más activos/exitosos

### Para Desarrolladores
- Base sólida para juegos interactivos de streaming
- Arquitectura modular fácil de extender
- Sistema de eventos reutilizable para otras plataformas
- Ejemplo de integración con APIs de streaming
- Sistema de ranking y puntuaciones escalable

### Para la Audiencia
- Participar activamente en el contenido del streamer
- Ver su avatar aparecer en el juego
- Competir individualmente con otros espectadores
- Influir en el resultado del juego con sus acciones
- Aparecer en el top de usuarios del stream

## 🔧 Comandos de Desarrollo

```bash
# Ejecutar el juego con eventos simulados
python main.py

# Conectar a un stream de TikTok Live
python main.py --tiktok @username

# Modo debug con logging detallado
python main.py --verbose

# Instalar dependencias
pip install -r requirements.txt
```

## ⚙️ Configuración de Pelotas por Evento

En `src/core/config.py` se pueden configurar la cantidad de pelotas que genera cada tipo de evento:

```python
# Configuración de pelotas por evento
BALLS_PER_COMMENT: int = 1
BALLS_PER_LIKE: int = 1
BALLS_PER_FOLLOW: int = 2
BALLS_PER_SHARE: int = 3
BALLS_PER_DONATION: int = 5  # Base, se multiplica por el monto
```

## 💰 Configuración de Comandos

En `src/core/config.py` se pueden configurar los costos de los comandos:

```python
# Configuración de costos de comandos
COMMAND_COSTS: Dict[str, int] = {
    'msg': 25,      # Mostrar mensaje personalizado en pantalla
    'rain': 80,     # Lluvia de pelotas especiales (preparado)
    'boost': 60,    # Pelotas más grandes (preparado)
    'glow': 20,     # Efecto de brillo (preparado)
    'fireworks': 120, # Fuegos artificiales (preparado)
    'freeze': 150,  # Congelar pelotas (preparado)
    'mega': 200,    # Pelota gigante (preparado)
    'rainbow': 90,  # Pelotas arcoíris (preparado)
}
```

## 📈 Futuras Extensiones

El proyecto está diseñado para ser fácilmente extensible:

- **Nuevas Plataformas**: YouTube Live, Twitch, Instagram Live
- **Nuevos Juegos**: Diferentes mecánicas de juego manteniendo la interactividad
- **Más Efectos**: Animaciones 3D, shaders, efectos de iluminación
- **Analytics**: Estadísticas de engagement y participación
- **Personalización**: Temas, colores y assets personalizables por streamer
- **Persistencia**: Guardar puntuaciones entre sesiones
- **Logros**: Sistema de logros y recompensas para usuarios

---

## 🔄 Cambios Recientes

### Sistema de Comandos con Puntos
- **Agregado**: Sistema completo de comandos que consumen puntos acumulados
- **Implementado**: Comando `msg` para mostrar mensajes personalizados en pantalla
- **Características del comando `msg`**:
  - Costo: 25 puntos
  - Formato: `msg <mensaje>` (máximo 50 caracteres)
  - Renderizado centrado en pantalla con avatar del usuario
  - Duración de 6 segundos con fade out gradual
  - Múltiples mensajes se apilan verticalmente
- **Arquitectura**: Sistema extensible preparado para más comandos
- **Integración**: Procesamiento automático en comentarios de TikTok Live
- **Verificación**: Solo se ejecuta si el usuario tiene suficientes puntos
- **Feedback**: Logging detallado de comandos ejecutados

### Control de Audio con Tecla M
- **Agregado**: Funcionalidad de mute/unmute con la tecla M
- **Mejorado**: AudioManager con estado de mute interno
- **Actualizado**: Controles de teclado y documentación

### Migración de Equipos a Top de Usuarios
- **Eliminado**: Sistema de equipos (Hombres vs Mujeres)
- **Agregado**: Sistema de ranking individual de usuarios
- **Mejorado**: Cache de avatares por usuario
- **Configurado**: Cantidad de pelotas por tipo de evento
- **Actualizado**: Interfaz para mostrar top 5 usuarios en tiempo real

Cualquier modificación al código, docúmentala en el archivo CURSOR_PROMPT.md

Este proyecto demuestra cómo crear experiencias interactivas modernas que conectan el streaming en vivo con gaming, usando principios de arquitectura limpia y programación modular.
