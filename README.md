# TikTok Plinko Battle

Juego 2D estilo Plinko para competiciones en directo entre **Mujeres** y **Hombres**.
Las bolas se generan en función de los **comentarios**, **likes**, **follows** u otros
triggers de tu stream. Pensado para TikTok Live pero extensible a otras
plataformas gracias a la abstracción `EventSource`.

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Uso

### Modo local (sin stream)

Genera eventos aleatorios para hacer pruebas:

```bash
python main.py
```

### Modo TikTok Live

Necesitas el paquete `tiktok-live` y el nombre de usuario de la cuenta que
esté emitiendo en directo:

```bash
python main.py --tiktok NOMBRE_DE_USUARIO
```

## Arquitectura

- `tiktok_plinko/game_logic.py`  ➜ Reglas y física del juego, completamente desacopladas de la interfaz.
- `tiktok_plinko/event_sources.py` ➜  `EventSource` abstracta + `DummyEventSource` para testing.
- `tiktok_plinko/tiktok_source.py` ➜ Implementación real para TikTok Live.
- `main.py` ➜  Renderizado con `pygame` y pegado de todo.

## Pruebas unitarias

Como la lógica del juego está desacoplada de la parte gráfica, puedes probarla
directamente:

```python
from tiktok_plinko.game_logic import GameState, GameConfig, Team

game = GameState(GameConfig())
game.spawn_ball(Team.MEN)
for _ in range(1000):
    game.update(1/60)
print(game.scores)
```

## Extender a otras plataformas

Crea tu propia subclase de `EventSource` (por ejemplo `TwitchEventSource`) y
emite los callbacks correspondientes (`_emit_comment`, `_emit_like`, etc.).

```python
class TwitchEventSource(EventSource):
    async def run(self):
        ...  # Conectar a la API de Twitch y llamar a _emit_comment(...)
```

¡Listo! 🎉 