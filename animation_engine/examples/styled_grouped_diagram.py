"""Render a styled grouped SVG diagram."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.canvas import SVGCanvas
from engine.objects import Arrow, Group, Rectangle, Style, Text


def render_example() -> Path:
    """Render a nested vector scene as an SVG file."""
    canvas = SVGCanvas(width=960, height=540, background="#f7f8fb")

    diagram = Group(x=120.0, y=90.0, opacity=0.96)
    source = Group(x=0.0, y=0.0)
    source.add(
        Rectangle(
            width=240.0,
            height=120.0,
            corner_radius=18.0,
            style=Style(fill_color="#ffffff", stroke_color="#4361ee", stroke_width=3.0),
        )
    )
    source.add(
        Text(
            x=120.0,
            y=66.0,
            content="Storyboard",
            font_size=26.0,
            font_family="Inter, Arial, sans-serif",
            font_weight="700",
            text_anchor="middle",
            text_alignment="middle",
            style=Style(fill_color="#172033"),
        )
    )

    target = Group(x=460.0, y=210.0, rotation=-3.0)
    target.add(
        Rectangle(
            width=260.0,
            height=130.0,
            corner_radius=22.0,
            style=Style(fill_color="#fff7ed", stroke_color="#f97316", stroke_width=3.0),
        )
    )
    target.add(
        Text(
            x=130.0,
            y=72.0,
            content="Animated Scene",
            font_size=26.0,
            font_family="Inter, Arial, sans-serif",
            font_weight="700",
            text_anchor="middle",
            text_alignment="middle",
            style=Style(fill_color="#431407"),
        )
    )

    connector = Arrow(
        start_x=250.0,
        start_y=80.0,
        end_x=455.0,
        end_y=245.0,
        arrowhead_size=20.0,
        style=Style(
            fill_color="none",
            stroke_color="#0f766e",
            stroke_width=5.0,
            line_cap="round",
            line_join="round",
        ),
    )

    diagram.extend([source, connector, target])

    output = Path("output") / "styled_grouped_diagram.svg"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(canvas.to_svg([diagram]), encoding="utf-8")
    return output


if __name__ == "__main__":
    print(render_example())
