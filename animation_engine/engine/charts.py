"""Chart and annotation primitives."""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from .objects import BaseObject, Group, Rectangle, Text, Style, Line, Polyline, Path
from .theme import Theme, DEFAULT_THEME


@dataclass
class Callout(Group):
    """Annotation text connected to a target point.

    Uses default-constructed `Line`/`Text` children, which already source
    their stroke/fill/font from `DEFAULT_THEME` (see objects.py) -- no
    theme wiring needed here at all, which is the point: components should
    inherit the engine's look for free rather than repeating it.
    """

    target_x: float = 0.0
    target_y: float = 0.0
    text: str = ""

    def __post_init__(self) -> None:
        self.add(Line(end_x=self.target_x, end_y=self.target_y))
        self.add(Text(x=self.target_x, y=self.target_y - 20, content=self.text))


@dataclass
class BarChart(Group):
    """Simple animatable bar chart."""

    data: dict[str, float] = field(default_factory=dict)
    bar_width: float = 40
    gap: float = DEFAULT_THEME.spacing_scale["medium"]
    colors: list[str] = field(default_factory=lambda: list(DEFAULT_THEME.categorical_palette))
    _bars: dict[str, Rectangle] = field(init=False, default_factory=dict)
    _labels: dict[str, Text] = field(init=False, default_factory=dict)

    def __post_init__(self) -> None:
        x = 0
        for i, (label, value) in enumerate(self.data.items()):
            color = self.colors[i % len(self.colors)]
            bar = Rectangle(
                x=x,
                y=-value,
                width=self.bar_width,
                height=value,
                style=Style(fill_color=color),
            )
            self._bars[label] = bar
            self.add(bar)

            caption = Text(
                x=x + self.bar_width / 2,
                y=DEFAULT_THEME.spacing_scale["large"],
                content=label,
                text_anchor="middle",
                font_size=DEFAULT_THEME.typography_scale["small"],
                style=Style(fill_color=DEFAULT_THEME.muted_color),
            )
            self._labels[label] = caption
            self.add(caption)

            x += self.bar_width + self.gap

    def apply_theme(self, theme: Theme) -> None:
        """Bars keep their assigned series color so a chart's data reads
        the same in light and dark mode; only the muted caption labels and
        structural defaults (stroke, corner radius) follow `theme`."""
        super().apply_theme(theme)
        for caption in self._labels.values():
            caption.style.fill_color = theme.muted_color
            caption.font_size = theme.font_size("small")

    @property
    def value(self) -> float:
        """Get the value of the first series."""
        return list(self.data.values())[0] if self.data else 0.0

    @value.setter
    def value(self, val: float) -> None:
        """Set the value of the first series and update bar."""
        if not self.data:
            return
        key = list(self.data.keys())[0]
        self.data[key] = val
        if key in self._bars:
            bar = self._bars[key]
            bar.height = val
            bar.y = -val


@dataclass
class LineChart(Group):
    """Simple animatable line chart with a soft fill under the line, in
    the spirit of a minimal dashboard sparkline."""

    data: list[float] = field(default_factory=list)
    x_step: float = 50
    y_scale: float = 1.0
    color: str = field(default_factory=lambda: DEFAULT_THEME.categorical_palette[0])
    fill_opacity: float = 0.12

    def __post_init__(self) -> None:
        points = [(i * self.x_step, -v * self.y_scale) for i, v in enumerate(self.data)]

        if len(points) >= 2:
            area_points = points + [(points[-1][0], 0.0), (points[0][0], 0.0)]
            d = "M " + " L ".join(f"{px} {py}" for px, py in area_points) + " Z"
            self._area = Path(
                d=d,
                style=Style(fill_color=self.color, stroke_color="none", opacity=self.fill_opacity),
            )
            self.add(self._area)

        self._line = Polyline(
            points=points,
            style=Style(
                fill_color="none",
                stroke_color=self.color,
                stroke_width=DEFAULT_THEME.stroke_width,
                line_cap="round",
                line_join="round",
            ),
        )
        self.add(self._line)


@dataclass
class PieChart(Group):
    """Simple animatable pie chart."""

    data: dict[str, float] = field(default_factory=dict)
    radius: float = 100
    colors: list[str] = field(default_factory=lambda: list(DEFAULT_THEME.categorical_palette))
    _wedges: list[Path] = field(init=False, default_factory=list)

    def __post_init__(self) -> None:
        total = sum(self.data.values())
        if total == 0:
            return

        angle = 0.0
        for i, (label, value) in enumerate(self.data.items()):
            sweep = (value / total) * 360
            start_rad = math.radians(angle)
            end_rad = math.radians(angle + sweep)

            x1 = self.radius * math.cos(start_rad)
            y1 = self.radius * math.sin(start_rad)
            x2 = self.radius * math.cos(end_rad)
            y2 = self.radius * math.sin(end_rad)

            large_arc = 1 if sweep > 180 else 0
            d = f"M 0 0 L {x1} {y1} A {self.radius} {self.radius} 0 {large_arc} 1 {x2} {y2} Z"

            wedge = Path(
                d=d,
                style=Style(
                    fill_color=self.colors[i % len(self.colors)],
                    # A background-colored seam between wedges reads as
                    # crisp separation instead of a busy outline.
                    stroke_color=DEFAULT_THEME.background_color,
                    stroke_width=DEFAULT_THEME.stroke_width,
                ),
            )
            self._wedges.append(wedge)
            self.add(wedge)
            angle += sweep

    def apply_theme(self, theme: Theme) -> None:
        """Wedges keep their assigned series color; only the seam between
        wedges follows `theme` so it always matches the current background."""
        super().apply_theme(theme)
        for wedge in self._wedges:
            wedge.style.stroke_color = theme.background_color
            wedge.style.stroke_width = theme.stroke_width
