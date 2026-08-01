"""Usage paradigm: a composed scene mixing every element type in one theme.

This is the capstone example: a full background canvas, an elevated
"surface" card (using `theme.surface_color`, distinct from the page
background), a divider line (`theme.border_color`), heading text, a bar
chart, a computer asset, and a stick figure -- all built independently,
then brought into visual agreement with two lines:

    for obj in scene.children:
        obj.apply_theme(theme)

Because every primitive and component sources its defaults from the same
Theme, the result reads as one cohesive, sleek, minimalist illustration
rather than a collage of mismatched parts. Swapping `LIGHT_THEME` for
`DARK_THEME` restyles the whole scene without touching a single object.

Assumes this script lives alongside theme.py, objects.py, charts.py,
assets.py, stick_figure.py, animation.py, and canvas.py (e.g. run as
`python usage_background_scene.py` from inside the engine package
directory). Adjust the import prefix below if your project exposes these
as a package.
"""

from engine.theme import Theme, LIGHT_THEME, DARK_THEME
from engine.objects import Group, Rectangle, Text, Line, Style
from engine.charts import BarChart
from engine.assets import Computer
from engine.stick_figure import StickFigure
from engine.canvas import SVGCanvas

CANVAS_WIDTH = 640
CANVAS_HEIGHT = 420


def build_scene(theme: Theme) -> Group:
    scene = Group()

    # Full-bleed canvas background.
    scene.add(Rectangle(
        x=0, y=0, width=CANVAS_WIDTH, height=CANVAS_HEIGHT,
        style=Style(fill_color=theme.background_color),
    ))

    # An elevated "surface" card, inset from the edges, with a subtle
    # border -- the classic light-card-on-soft-canvas minimalist layout.
    margin = theme.spacing_scale["large"]
    card = Rectangle(
        x=margin, y=margin,
        width=CANVAS_WIDTH - 2 * margin, height=CANVAS_HEIGHT - 2 * margin,
        style=Style(fill_color=theme.surface_color, stroke_color=theme.border_color,
                    stroke_width=theme.stroke_width),
        corner_radius=theme.radius("medium"),
    )
    scene.add(card)

    heading = Text(
        x=margin * 2, y=margin * 3,
        content="Weekly Standup",
        font_size=theme.font_size("large"),
        style=Style(fill_color=theme.foreground_color),
    )
    scene.add(heading)

    divider = Line(
        x=margin * 2, y=margin * 4,
        end_x=CANVAS_WIDTH - margin * 4, end_y=0,
        style=Style(stroke_color=theme.border_color, stroke_width=theme.stroke_width),
    )
    scene.add(divider)

    chart = BarChart(data={"Mon": 12, "Tue": 18, "Wed": 9, "Thu": 22, "Fri": 15}, bar_width=28)
    chart.move_to(margin * 2, CANVAS_HEIGHT - margin * 3)
    scene.add(chart)

    computer = Computer(width=70, height=44)
    computer.move_to(CANVAS_WIDTH - margin * 6, margin * 5)
    scene.add(computer)

    figure = StickFigure()
    figure.scale = 0.6
    figure.move_to(CANVAS_WIDTH - margin * 10, CANVAS_HEIGHT - margin * 4)
    scene.add(figure)

    # One call, every object -- primitives, chart, asset, and figure --
    # adopts the same theme.
    for obj in scene.children:
        obj.apply_theme(theme)

    return scene


if __name__ == "__main__":
    for theme, out_path in [(LIGHT_THEME, "background_scene_light.svg"),
                             (DARK_THEME, "background_scene_dark.svg")]:
        scene = build_scene(theme)
        canvas = SVGCanvas(width=CANVAS_WIDTH, height=CANVAS_HEIGHT, background_color=theme.background_color)
        canvas.render(scene)
        canvas.save(out_path)
    print("Wrote background_scene_light.svg and background_scene_dark.svg")
