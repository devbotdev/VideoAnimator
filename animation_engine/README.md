# Animation Engine

Initial project scaffold for a vector-based animation engine.

## Dependencies

This engine requires the following native libraries to be installed:
- Cairo (for SVG rendering)
- FFmpeg (for MP4 export)

Ensure these are installed and available in your system PATH.


```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Run the entry point:

```powershell
python main.py
```

Run the test suite:

```powershell
python -m pytest
```

## Renderer

Rendering is configured with `RenderConfig`:

```python
from engine import RenderConfig, SVGRenderer

renderer = SVGRenderer(
    RenderConfig(
        width=1280,
        height=720,
        fps=30,
        background="#ffffff",
        codec="libx264",
        quality=23,
        preset="medium",
        output_format="mp4",
        enable_progress_reporting=True,
    )
)
```

The renderer draws scene objects into SVG markup, converts frames to RGB image arrays with CairoSVG, and exports MP4 files with MoviePy/FFmpeg. MP4 export streams frames through MoviePy instead of storing the full render in memory, which is better suited to longer projects. `render_frames(...)` is still available for tests and short debugging renders.

Frame counts are deterministic: `frame_count = max(1, floor(duration * fps + 0.5))`, and exported video duration is exactly `frame_count / fps`. Negative and infinite durations are rejected.

Optional debugging and audio:

- Set `debug_export_frames=True` to write individual PNG frames. Use `debug_frames_dir=...` to choose the folder.
- Set `enable_progress_reporting=False` for quiet test runs.
- Set `audio_path=Path("narration.wav")` to attach narration to MP4 export. Missing audio files raise `FileNotFoundError` before rendering. Audio longer than the video is trimmed to the rendered duration; shorter audio is not looped.

If CairoSVG/native Cairo, MoviePy/FFmpeg, or the configured audio file is unavailable, the renderer raises a helpful exception describing the missing dependency.

## File purposes

| File | Purpose |
| --- | --- |
| `main.py` | Application entry point. |
| `requirements.txt` | Python dependency list. |
| `engine/__init__.py` | Package marker and shared exports. |
| `engine/objects.py` | Core scene/object data structures. |
| `engine/animation.py` | Animation timing and transition logic. |
| `engine/renderer.py` | SVG frame generation and MP4 export. |
| `engine/canvas.py` | SVG canvas construction and object serialization. |
| `engine/camera.py` | Scene camera and viewport controls. |
| `engine/stick_figure.py` | Composite stick figure and action helpers. |
| `engine/scene.py` | Scene grouping, timelines, and scene management. |
| `engine/timeline.py` | Timeline scheduling for scene events. |
| `engine/transition.py` | Scene transition blending. |
| `engine/ai.py` | AI plan parsing, registries, and execution framework. |
| `engine/utils.py` | Shared helper functions. |
| `assets/` | Static source assets for future animations. |
| `examples/` | Sample usage and example scenes. |
| `output/` | Generated renders and exported files. |

## Example

Run the provided examples:

- Export moving rectangle: `python main.py`
- Export basic stick-figure animation: `python animation_engine\examples\basic_animation.py`

Running the basic example will export `output/basic_animation.mp4`.

For scene management, use `Scene`, `SceneManager`, `Camera`, `Timeline`, and `FadeTransition` from `engine`.

### Sequencing example

```python
from engine.objects import Rectangle
from engine.scene import Scene
from engine.timeline import Timeline

scene = Scene(name="demo")
rect = Rectangle(x=0, y=0, width=50, height=50)
scene.add(rect)

timeline = scene.timeline("main")
timeline.animate(
    0.0,
    scene,
    rect,
    "x",
    0.0,
    200.0,
    1.0,
    delay=0.2,
    repeat=1,
    yoyo=True,
)
```

## Formalized Plan Schema

For structured animation generation, we now use a versioned JSON schema. This allows for validation of scene structure, object types, and allowed actions before passing the plan to the rendering engine.

### Structure

```json
{
  "version": "1.0",
  "title": "Animation Title",
  "resolution": {"width": 1920, "height": 1080},
  "fps": 30,
  "theme": "default",
  "scenes": [
    {
      "id": "scene1",
      "duration": 5.0,
      "background": "#ffffff",
      "objects": [
        {
          "id": "obj1",
          "type": "Rectangle",
          "properties": {"x": 0, "y": 0, "width": 100, "height": 100}
        }
      ],
      "actions": [
        {
          "start_time": 0.0,
          "duration": 2.0,
          "target_id": "obj1",
          "action": "move",
          "parameters": {"dx": 50, "dy": 50}
        }
      ]
    }
  ],
  "narration": [
    {"timestamp": 0.5, "text": "Narrator says something."}
  ]
}
```

### Validation

The engine validates this plan against an allowlist of supported object types and actions using an `ActionRegistry`. You can perform a dry-run validation of a plan without rendering.

**Dry-run Validation:**

```python
from engine.schema import Plan
from engine.action_registry import ActionRegistry

registry = ActionRegistry()
registry.populate_defaults()

plan = Plan.from_dict(data)
plan.validate(registry)  # Raises ValueError if invalid
print(plan.summary(registry))
```

- **Supported Object Types:** Rectangle, Circle, Text, StickFigure, Arrow, Group
- **Supported Actions:** walk, point, wave, move, fade_in, fade_out, scale, rotate, draw, grow, highlight, shake, camera_pan, camera_zoom, camera_focus

See `engine/schema.py` and `engine/action_registry.py` for full details. Use `Plan.from_dict(data)` to parse a plan and `plan.validate(registry)` to perform a dry-run validation.
