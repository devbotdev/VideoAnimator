"""Basic SVG animation example."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.animation import AnimationManager
from engine.objects import Rectangle
from engine.renderer import SVGRenderer


def export_example() -> Path:
    """Export a simple moving rectangle animation."""
    renderer = SVGRenderer(width=1920, height=1080, fps=30, background="#ffffff")
    rectangle = Rectangle(x=120, y=500, width=240, height=140)
    manager = AnimationManager()
    manager.animate(
        rectangle,
        "x",
        start_value=120.0,
        end_value=1560.0,
        duration=3.0,
        easing="ease-in-out",
    )
    return renderer.export_mp4(
        Path("output") / "moving_rectangle.mp4",
        [rectangle],
        duration=3.0,
        animation_manager=manager,
    )


if __name__ == "__main__":
    print(export_example())
