"""Basic stick-figure animation example.

Creates a canvas, adds a stick figure and text, animates the figure across the screen,
and exports the result as an MP4.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.animation import AnimationManager
from engine.renderer import SVGRenderer
from engine.stick_figure import StickFigure
from engine.objects import Text


def export_basic_animation() -> Path:
    """Build and export a short stick-figure walking animation."""
    renderer = SVGRenderer(width=1920, height=1080, fps=30, background="#ffffff")
    manager = AnimationManager()

    # Place the stick figure on the left-center of the canvas
    figure = StickFigure(x=120.0, y=540.0)

    # Make the figure walk across the screen
    figure.walk(manager, duration=4.0, distance=1500.0, easing="ease-in-out")

    # Add a title text centered near the top
    title = Text(x=960.0, y=100.0, content="Stick Figure Walk", font_size=48.0)

    output = renderer.export_mp4(Path("output") / "basic_animation.mp4", [figure, title], duration=4.0, animation_manager=manager)
    return output


if __name__ == "__main__":
    print(export_basic_animation())
