"""Scene management example with multiple objects and a fade transition."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine import Camera, Circle, FadeTransition, Rectangle, Scene, SceneManager, SVGRenderer


def build_scene_manager() -> SceneManager:
    """Create a simple two-scene setup."""
    first_scene = Scene(name="Intro", background="#ffffff")
    first_scene.camera = Camera(x=0, y=0, width=1920, height=1080)
    first_scene.add(Rectangle(x=180, y=420, width=220, height=140))
    first_scene.add(Circle(x=640, y=480, radius=60))

    first_scene.timeline().schedule(
        0.0,
        lambda scene: scene.animate(
            scene.objects[0],
            "x",
            start_value=180.0,
            end_value=760.0,
            duration=3.0,
            easing="ease-in-out",
        ),
    )

    second_scene = Scene(name="Outtro", background="#ffffff")
    second_scene.camera = Camera(x=160, y=0, width=1920, height=1080)
    second_scene.add(Rectangle(x=960, y=420, width=240, height=140))
    second_scene.add(Circle(x=1280, y=480, radius=80))

    manager = SceneManager()
    manager.add_scene(first_scene)
    manager.add_scene(second_scene)
    manager.transition = FadeTransition(duration=1.5)
    manager.transition_target_index = 1
    return manager


def export_example() -> Path:
    """Export the scene example to MP4."""
    renderer = SVGRenderer(width=1920, height=1080, fps=30, background="#ffffff")
    return renderer.export_scene_manager_mp4(
        Path("output") / "scene_management_example.mp4",
        build_scene_manager(),
        duration=4.5,
    )


if __name__ == "__main__":
    print(export_example())
