
import pytest
from engine.theme import LIGHT_THEME, DARK_THEME
from engine.objects import Rectangle, Text, Group, Circle
from engine.scene import Scene
from engine.layout import get_bounds, align_center, stack_vertical


def test_theme_application():
    scene = Scene(theme=LIGHT_THEME)
    rect = Rectangle(width=100, height=50)
    scene.add(rect)
    assert rect.style.stroke_width == LIGHT_THEME.stroke_width
    assert rect.style.stroke_color == LIGHT_THEME.foreground_color

    text = Text(content="Hello")
    scene.add(text)
    assert text.font_family == LIGHT_THEME.font_family

def test_layout_bounds():
    rect = Rectangle(x=10, y=20, width=100, height=50)
    assert get_bounds(rect) == (10, 20, 100, 50)
    
    circle = Circle(x=50, y=50, radius=20)
    assert get_bounds(circle) == (30, 30, 40, 40)
    
    group = Group(x=0, y=0)
    group.add(rect)
    group.add(circle)
    # Group bounds should encompass children
    bx, by, bw, bh = get_bounds(group)
    assert bx <= 10 and by <= 20
    assert bx + bw >= 50 + 20 and by + bh >= 50 + 20

def test_layout_helpers():
    rect1 = Rectangle(width=100, height=50)
    rect2 = Rectangle(width=100, height=50)
    
    align_center(rect1, 500, 500)
    assert rect1.x == 450
    assert rect1.y == 475
    
    stack_vertical([rect1, rect2], 500, 100, 20)
    # rect1 at 100
    # rect2 at 100 + 50 + 20 = 170
    assert rect1.y == 75 # 100 - 50/2
    assert rect2.y == 145 # 170 - 50/2
