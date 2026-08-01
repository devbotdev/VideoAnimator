"""Usage paradigm: a themed, animated bar chart.

Shows the core paradigm for every component in the engine: build it once,
then call `apply_theme(...)` to make it match a Theme. The bars pick up a
harmonious set of colors from `theme.categorical_palette` automatically
(no colors are specified by hand), and re-theming to dark mode adapts the
chart's structural details (caption color, corner rounding, stroke) while
deliberately leaving each bar's own data color untouched, so a chart reads
the same in both modes.

Assumes this script lives alongside theme.py, objects.py, charts.py,
assets.py, stick_figure.py, animation.py, and canvas.py (e.g. run as
`python usage_bar_chart.py` from inside the engine package directory).
Adjust the import prefix below if your project exposes these as a package.
"""

from engine.theme import LIGHT_THEME, DARK_THEME
from engine.charts import BarChart
from engine.animation import AnimationManager
from engine.canvas import SVGCanvas


def build_and_render(theme, out_path: str) -> None:
    chart = BarChart(
        data={"Jan": 24, "Feb": 40, "Mar": 32, "Apr": 58, "May": 46},
        bar_width=48,
    )
    chart.move_to(60, 260)  # baseline near the bottom of the canvas

    # A single call adapts every bar, caption, and corner radius to the
    # active theme -- no per-object styling required.
    chart.apply_theme(theme)

    # Animate the first series growing in, using the same AnimationManager
    # pattern the rest of the engine uses (see assets.py's screen_glow).
    manager = AnimationManager()
    manager.animate(chart, "value", 0, chart.value, duration=0.6, easing="ease-out")

    canvas = SVGCanvas(width=400, height=300, background_color=theme.background_color)
    canvas.render(chart)
    canvas.save(out_path)


if __name__ == "__main__":
    build_and_render(LIGHT_THEME, "bar_chart_light.svg")
    build_and_render(DARK_THEME, "bar_chart_dark.svg")
    print("Wrote bar_chart_light.svg and bar_chart_dark.svg")
