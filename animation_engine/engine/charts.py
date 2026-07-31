"""Chart and annotation primitives."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .objects import BaseObject, Group, Rectangle, Text, Style, Line


@dataclass
class Callout(Group):
    """Annotation text connected to a target point."""
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
    gap: float = 10
    colors: list[str] = field(default_factory=lambda: ["#555555"])
    _bars: dict[str, Rectangle] = field(init=False, default_factory=dict)

    def __post_init__(self) -> None:
        x = 0
        for i, (label, value) in enumerate(self.data.items()):
            color = self.colors[i % len(self.colors)]
            bar = Rectangle(
                x=x, 
                y=-value, 
                width=self.bar_width, 
                height=value,
                style=Style(fill_color=color)
            )
            self._bars[label] = bar
            self.add(bar)
            self.add(Text(x=x + self.bar_width/2, y=20, content=label, text_anchor="middle"))
            x += self.bar_width + self.gap

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
import math

@dataclass
class LineChart(Group):
    """Simple animatable line chart."""
    data: list[float] = field(default_factory=list)
    x_step: float = 50
    y_scale: float = 1.0
    
    def __post_init__(self) -> None:
        from .objects import Polyline
        points = [(i * self.x_step, -v * self.y_scale) for i, v in enumerate(self.data)]
        self.add(Polyline(points=points))

@dataclass
class PieChart(Group):
    """Simple animatable pie chart."""
    data: dict[str, float] = field(default_factory=dict)
    radius: float = 100
    
    def __post_init__(self) -> None:
        from .objects import Path
        total = sum(self.data.values())
        if total == 0:
            return
        
        angle = 0
        for label, value in self.data.items():
            sweep = (value / total) * 360
            start_rad = math.radians(angle)
            end_rad = math.radians(angle + sweep)
            
            x1 = self.radius * math.cos(start_rad)
            y1 = self.radius * math.sin(start_rad)
            x2 = self.radius * math.cos(end_rad)
            y2 = self.radius * math.sin(end_rad)
            
            large_arc = 1 if sweep > 180 else 0
            
            d = f"M 0 0 L {x1} {y1} A {self.radius} {self.radius} 0 {large_arc} 1 {x2} {y2} Z"
            self.add(Path(d=d))
            angle += sweep
