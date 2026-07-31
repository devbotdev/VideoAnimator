
import pytest
from engine import BarChart, LineChart, PieChart, Callout, SVGCanvas

def test_bar_chart_layout():
    data = {"A": 10, "B": 20}
    chart = BarChart(data=data, bar_width=10, gap=5)
    # Total width = (bar_width + gap) * len(data) - gap = (10+5)*2 - 5 = 25
    # Should have BarChart with children
    assert len(chart.children) == 4 # 2 bars + 2 texts

def test_line_chart_points():
    data = [10, 20, 30]
    chart = LineChart(data=data, x_step=10, y_scale=1.0)
    # Should have a Polyline as child
    from engine import Polyline
    assert isinstance(chart.children[0], Polyline)
    assert chart.children[0].points == [(0, -10), (10, -20), (20, -30)]

def test_pie_chart_svg():
    data = {"A": 50, "B": 50}
    chart = PieChart(data=data, radius=100)
    canvas = SVGCanvas()
    svg = canvas.to_svg([chart])
    assert "<path" in svg
    assert "M 0 0" in svg

def test_callout_structure():
    callout = Callout(target_x=10, target_y=20, text="hello")
    assert len(callout.children) == 2
    from engine import Line, Text
    assert isinstance(callout.children[0], Line)
    assert isinstance(callout.children[1], Text)
    assert callout.children[1].content == "hello"
