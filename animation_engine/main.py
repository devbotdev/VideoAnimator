"""Entry point for the animation engine application."""

from __future__ import annotations

from pathlib import Path

from engine.animation import AnimationManager
from engine.objects import Rectangle
from engine.renderer import SVGRenderer


def main() -> int:
    """Run the example SVG animation export."""
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
    output_path = Path("output") / "moving_rectangle.mp4"
    renderer.export_mp4(output_path, [rectangle], duration=3.0, animation_manager=manager)
    print(f"Exported video to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
