"""Usage paradigm: a themed stick figure performing a short action sequence.

Demonstrates that a composite, multi-part object (six limbs, all built
from Circle/Line primitives) still gets a single, coherent look from one
`apply_theme()` call -- every limb inherits the same ink color, stroke
width, and rounded line caps/joins, because `stick_figure.py` sources its
defaults from `theme.py` rather than hardcoding them per limb.

Assumes this script lives alongside theme.py, objects.py, charts.py,
assets.py, stick_figure.py, animation.py, and canvas.py (e.g. run as
`python usage_stick_figure.py` from inside the engine package directory).
Adjust the import prefix below if your project exposes these as a package.
"""

from engine.theme import LIGHT_THEME, DARK_THEME
from engine.stick_figure import StickFigure
from engine.animation import AnimationManager
from engine.canvas import SVGCanvas


def build_and_render(theme, out_path: str) -> None:
    figure = StickFigure()
    figure.move_to(150, 220)
    figure.apply_theme(theme)

    manager = AnimationManager()
    figure.walk(manager, duration=1.2, distance=120)
    figure.wave(manager, duration=0.8, arm="right")

    canvas = SVGCanvas(width=400, height=320, background_color=theme.background_color)
    canvas.render(figure)
    canvas.save(out_path)


if __name__ == "__main__":
    build_and_render(LIGHT_THEME, "stick_figure_light.svg")
    build_and_render(DARK_THEME, "stick_figure_dark.svg")
    print("Wrote stick_figure_light.svg and stick_figure_dark.svg")
