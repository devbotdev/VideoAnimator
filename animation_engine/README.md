# Animation Engine

Initial project scaffold for a vector-based animation engine.

## Setup

1. Create a virtual environment:
   ```powershell
   python -m venv .venv
   ```
2. Activate it:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
3. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
4. Run the entry point:
   ```powershell
   python main.py
   ```

## Renderer

- Resolution: `1920x1080`
- FPS: `30`

The renderer draws scene objects into SVG markup, converts each SVG frame into an image, and exports the resulting frame sequence as MP4 with `moviepy`.

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

Run `python main.py` to export `output/moving_rectangle.mp4`.

For scene management, use `Scene`, `SceneManager`, `Camera`, `Timeline`, and `FadeTransition` from `engine`.

## AI connection framework

The AI bridge is scaffolded in `engine/ai.py` and does not include any model integration yet. It expects an external client to return JSON like:

```json
{
  "scene": "office",
  "actions": [
    { "object": "stickman", "action": "walk" }
  ]
}
```

### Exact next steps

1. Implement a real provider by creating a class that satisfies `engine.ai.AIModelClient.generate(prompt)`.
2. Register a scene factory in `engine.ai.SceneRegistry` for each scene name your model can emit, starting with `office`.
3. Register action handlers with `engine.ai.register_default_action_handlers(...)` and add any new actions beside `walk`, `point`, and `wave`.
4. Build named scene objects with `Scene.register_object(...)` so AI actions can target them by name.
5. Call `AIEngine.execute_prompt(...)` once a model client is wired in, or `AIEngine.execute_plan(...)` if you already have decoded JSON.

### Pointer map

| File | What to change |
| --- | --- |
| `engine/ai.py` | Add the real model client and any new action handlers. |
| `engine/scene.py` | Register named objects for AI targets. |
| `engine/stick_figure.py` | Extend the stick figure actions if new motion verbs are needed. |
| `examples/ai_framework_example.py` | Replace the stub plan source with your model client when ready. |
