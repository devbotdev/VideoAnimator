from __future__ import annotations

from xml.etree import ElementTree as ET

import pytest

from engine.ai import AIPlan
from engine.animation import Animation, AnimationManager
from engine.camera import Camera
from engine.canvas import SVGCanvas
from engine.objects import Arrow, BaseObject, Circle, Group, Line, Rectangle, Style, Text
from engine.scene import Scene
from engine.stick_figure import StickFigure
from engine.timeline import Timeline


def test_animation_value_at_supports_all_easing_modes() -> None:
    expected_values = {
        "linear": 50.0,
        "ease-in": 25.0,
        "ease-out": 75.0,
        "ease-in-out": 50.0,
    }

    for easing, expected_value in expected_values.items():
        target = BaseObject()
        animation = Animation.from_values(
            target=target,
            property_name="x",
            start_value=0.0,
            end_value=100.0,
            duration=10.0,
            easing=easing,
        )
        assert animation.value_at(5.0) == pytest.approx(expected_value)


def test_animation_manager_updates_and_removes_completed_animations() -> None:
    target = BaseObject()
    manager = AnimationManager()

    manager.animate(target, "x", 0.0, 10.0, 1.0)
    manager.animate(target, "y", 0.0, 20.0, 2.0)

    manager.update(1.5)

    assert target.x == pytest.approx(10.0)
    assert target.y == pytest.approx(15.0)
    assert len(manager.animations) == 1
    assert manager.animations[0].property_name == "y"


def test_timeline_events_order_once_and_reset() -> None:
    scene = Scene()
    calls: list[str] = []
    timeline = Timeline()
    timeline.schedule(0.5, lambda _scene: calls.append("late"))
    timeline.schedule(0.3, lambda _scene: calls.append("early"))

    timeline.update(0.6, scene)
    assert calls == ["early", "late"]

    timeline.update(0.1, scene)
    assert calls == ["early", "late"]

    timeline.reset()
    timeline.update(0.6, scene)
    assert calls == ["early", "late", "early", "late"]


def test_delayed_animation_waits_before_changing_target() -> None:
    target = BaseObject()
    manager = AnimationManager()

    manager.animate(target, "x", 0.0, 10.0, 1.0, delay=0.5)

    manager.update(0.4)
    assert target.x == pytest.approx(0.0)

    manager.update(0.2)
    assert target.x == pytest.approx(1.0)


def test_repeat_and_yoyo_values_are_correct() -> None:
    target = BaseObject()
    animation = Animation.from_values(target, "x", 0.0, 10.0, 2.0, repeat=1, yoyo=True)

    assert animation.active_duration == pytest.approx(8.0)
    assert animation.value_at(1.0) == pytest.approx(5.0)
    assert animation.value_at(3.0) == pytest.approx(5.0)
    assert animation.value_at(4.0) == pytest.approx(0.0)


def test_completion_callback_runs_once() -> None:
    target = BaseObject()
    manager = AnimationManager()
    calls: list[str] = []

    manager.animate(target, "x", 0.0, 10.0, 1.0, on_complete=lambda _animation: calls.append("done"))
    manager.update(1.0)
    manager.update(0.1)

    assert calls == ["done"]


def test_invalid_property_names_and_values_raise_clear_errors() -> None:
    target = BaseObject()

    with pytest.raises(AttributeError, match="no property"):
        Animation.from_values(target, "missing", 0.0, 10.0, 1.0)

    with pytest.raises(TypeError, match="must be numeric"):
        Animation.from_values(target, "x", "bad", 10.0, 1.0)


def test_multiple_overlapping_animations_are_predictable() -> None:
    target = BaseObject()
    manager = AnimationManager()

    manager.animate(target, "x", 0.0, 10.0, 1.0)
    manager.animate(target, "y", 0.0, 20.0, 2.0, delay=0.5)

    manager.update(1.0)

    assert target.x == pytest.approx(10.0)
    assert target.y == pytest.approx(5.0)


def test_scene_registers_named_objects_and_raises_for_missing_name() -> None:
    scene = Scene(name="Main")
    circle = Circle(radius=4.0)

    registered = scene.register_object("hero", circle)

    assert registered is circle
    assert scene.objects == [circle]
    assert scene.object("hero") is circle

    with pytest.raises(KeyError, match="Unknown object"):
        scene.object("missing")


def test_camera_validation_and_view_box() -> None:
    camera = Camera(x=10.0, y=20.0, zoom=2.0, width=1000, height=500)

    with pytest.raises(ValueError):
        camera.zoom_to(0.0)

    camera.zoom_to(4.0)

    # Center (10, 20), Zoom 4.0 => visible width 250, visible height 125.
    # Top-left = (10 - 125, 20 - 62.5) = (-115, -42.5)
    assert camera.view_box() == (-115.0, -42.5, 250.0, 125.0)

def test_camera_pan_zoom_rotation() -> None:
    camera = Camera(x=0.0, y=0.0, zoom=1.0)
    
    camera.pan_to(100.0, 200.0)
    assert camera.x == 100.0 and camera.y == 200.0
    
    camera.pan_by(50.0, -50.0)
    assert camera.x == 150.0 and camera.y == 150.0
    
    camera.zoom_to(2.0)
    assert camera.zoom == 2.0
    
    camera.zoom_by(2.0)
    assert camera.zoom == 4.0
    
    camera.rotation = 90.0
    assert camera.rotation == 90.0

def test_camera_focus_on() -> None:
    camera = Camera(x=0.0, y=0.0)
    obj = Circle(x=50.0, y=100.0, radius=10.0)
    
    camera.focus_on(obj)
    
    assert camera.x == 50.0 and camera.y == 100.0


@pytest.mark.parametrize(
    ("obj", "expected_fragment"),
    [
        (Circle(radius=3.0), "<circle"),
        (Rectangle(width=4.0, height=5.0), "<rect"),
        (Line(end_x=10.0, end_y=20.0), "<line"),
        (Text(content="Hello", font_size=24.0), "<text"),
    ],
)
def test_svg_canvas_renders_supported_shapes(obj: object, expected_fragment: str) -> None:
    canvas = SVGCanvas(width=640, height=480, background="#000000")
    canvas.add(obj)

    svg = canvas.to_svg()

    ET.fromstring(svg)
    assert expected_fragment in svg


def test_svg_canvas_renders_stick_figure_parts() -> None:
    canvas = SVGCanvas(width=640, height=480, background="#000000")
    canvas.add(StickFigure())

    svg = canvas.to_svg()

    ET.fromstring(svg)
    assert "<circle" in svg
    assert "<line" in svg


def test_svg_canvas_renders_shared_style_attributes() -> None:
    canvas = SVGCanvas(width=200, height=100)
    line = Line(
        end_x=100.0,
        end_y=0.0,
        opacity=2.0,
        style=Style(
            fill_color="#ffeecc",
            stroke_color="#123456",
            stroke_width=4.0,
            line_cap="round",
            line_join="bevel",
        ),
    )
    line.opacity = -1.0
    line.opacity = 0.4
    canvas.add(line)

    svg = canvas.to_svg()

    ET.fromstring(svg)
    assert 'opacity="0.4"' in svg
    assert 'fill="none"' in svg
    assert 'stroke="#123456"' in svg
    assert 'stroke-width="4.0"' in svg
    assert 'stroke-linecap="round"' in svg
    assert 'stroke-linejoin="bevel"' in svg


def test_style_opacity_assignment_clamps_and_rejects_invalid_values() -> None:
    style = Style(opacity=5.0)
    assert style.opacity == pytest.approx(1.0)

    style.opacity = -2.0
    assert style.opacity == pytest.approx(0.0)

    with pytest.raises(TypeError, match="Opacity must be numeric"):
        style.opacity = "bad"  # type: ignore[assignment]


def test_style_opacity_initializes_object_opacity() -> None:
    circle = Circle(style=Style(opacity=0.35))

    assert circle.opacity == pytest.approx(0.35)


def test_svg_canvas_renders_group_transforms_and_nested_children() -> None:
    group = Group(x=10.0, y=20.0, rotation=30.0, scale=2.0, opacity=0.5)
    nested = Group(x=5.0, y=6.0)
    nested.add(Circle(radius=4.0, style=Style(fill_color="#44aa88")))
    group.add(nested)

    svg = SVGCanvas(width=200, height=100).to_svg([group])

    ET.fromstring(svg)
    assert '<g transform="translate(10.0 20.0) rotate(30.0) scale(2.0)" opacity="0.5">' in svg
    assert '<g transform="translate(5.0 6.0)">' in svg
    assert '<circle cx="0" cy="0" r="4.0"' in svg
    assert 'fill="#44aa88"' in svg


def test_svg_canvas_skips_hidden_group_children() -> None:
    hidden = Circle(radius=4.0, visibility=False)
    visible = Circle(radius=6.0)
    group = Group(children=[hidden, visible])

    svg = SVGCanvas(width=200, height=100).to_svg([group])

    ET.fromstring(svg)
    assert 'r="4.0"' not in svg
    assert 'r="6.0"' in svg


def test_svg_canvas_renders_arrowhead_output() -> None:
    arrow = Arrow(
        start_x=10.0,
        start_y=20.0,
        end_x=70.0,
        end_y=20.0,
        arrowhead_size=12.0,
        style=Style(fill_color="none", stroke_color="#dd3355", stroke_width=3.0),
    )

    svg = SVGCanvas(width=100, height=80).to_svg([arrow])

    ET.fromstring(svg)
    assert '<line x1="10.0" y1="20.0" x2="70.0" y2="20.0"' in svg
    assert '<polygon points="70.0,20.0 58.0,26.0 58.0,14.0"' in svg
    assert 'stroke="#dd3355"' in svg
    assert 'stroke-width="3.0"' in svg


def test_svg_canvas_renders_rectangle_corners_and_text_options() -> None:
    canvas = SVGCanvas(width=320, height=180)
    canvas.add(Rectangle(width=100.0, height=50.0, corner_radius=8.0))
    canvas.add(
        Text(
            content="Title",
            font_family="Inter",
            font_weight="700",
            text_anchor="middle",
            text_alignment="central",
        )
    )

    svg = canvas.to_svg()

    ET.fromstring(svg)
    assert 'rx="8.0" ry="8.0"' in svg
    assert 'font-family="Inter"' in svg
    assert 'font-weight="700"' in svg
    assert 'text-anchor="middle"' in svg
    assert 'dominant-baseline="central"' in svg


def test_svg_canvas_escapes_text_content_safely() -> None:
    text = Text(content='<script>alert("x")</script> & data')

    svg = SVGCanvas(width=200, height=100).to_svg([text])

    ET.fromstring(svg)
    assert "<script>" not in svg
    assert "&lt;script&gt;" in svg
    assert "&amp; data" in svg


def test_ai_plan_parses_valid_payloads_and_rejects_invalid_ones() -> None:
    plan = AIPlan.from_mapping(
        {
            "scene": "office",
            "actions": [{"object": "stickman", "action": "walk", "parameters": {"duration": 3.5}}],
        }
    )

    assert plan.scene == "office"
    assert plan.actions[0].object == "stickman"
    assert plan.actions[0].parameters["duration"] == 3.5

    invalid_payloads = [
        {"scene": "", "actions": []},
        {"scene": "office", "actions": {}},
        {"scene": "office", "actions": [{"action": "walk"}]},
        {"scene": "office", "actions": ["bad"]},
    ]

    for payload in invalid_payloads:
        with pytest.raises(ValueError):
            AIPlan.from_mapping(payload)
