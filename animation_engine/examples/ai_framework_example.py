"""AI planning framework example without model integration."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine import AIEngine, AIPlan, ActionRegistry, Scene, SceneRegistry, SVGRenderer, StickFigure, register_default_action_handlers


def build_scene() -> Scene:
    """Create the scene referenced by the AI plan."""
    scene = Scene(name="office", background="#ffffff")
    scene.register_object("stickman", StickFigure(x=180, y=540))
    return scene


def export_example() -> Path:
    """Execute a fixed AI plan through the framework."""
    renderer = SVGRenderer(width=1920, height=1080, fps=30, background="#ffffff")
    scene_registry = SceneRegistry()
    scene_registry.register("office", build_scene)
    action_registry = register_default_action_handlers(ActionRegistry())
    engine = AIEngine(
        renderer=renderer,
        scene_registry=scene_registry,
        action_registry=action_registry,
    )
    plan = AIPlan.from_json(
        """
        {
          "scene": "office",
          "actions": [
            {
              "object": "stickman",
              "action": "walk",
              "parameters": {
                "duration": 2.5,
                "distance": 220
              }
            }
          ]
        }
        """
    )
    return engine.execute_plan(plan, Path("output") / "ai_framework_example.mp4", duration=2.5)


if __name__ == "__main__":
    print(export_example())
