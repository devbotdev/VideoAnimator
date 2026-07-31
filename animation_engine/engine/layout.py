from typing import Tuple, List, Optional
from .objects import BaseObject, Group, Rectangle, Circle, Text, Line, Polyline, Path, Arrow

def get_bounds(obj: BaseObject) -> Tuple[float, float, float, float]:
    """Returns (x, y, width, height) of an object in its local coordinate space."""
    if isinstance(obj, Rectangle):
        return obj.x, obj.y, obj.width, obj.height
    if isinstance(obj, Circle):
        return obj.x - obj.radius, obj.y - obj.radius, obj.radius * 2, obj.radius * 2
    if isinstance(obj, Group):
        if not obj.children:
            return obj.x, obj.y, 0, 0
        min_x = min(get_bounds(c)[0] for c in obj.children)
        min_y = min(get_bounds(c)[1] for c in obj.children)
        max_x = max(get_bounds(c)[0] + get_bounds(c)[2] for c in obj.children)
        max_y = max(get_bounds(c)[1] + get_bounds(c)[3] for c in obj.children)
        return obj.x + min_x, obj.y + min_y, max_x - min_x, max_y - min_y
    if isinstance(obj, Text):
        # Text measurement approximation
        # Limitations: Does not account for font metrics accurately.
        # Assumes roughly square-ish characters based on font_size.
        approx_width = len(obj.content) * obj.font_size * 0.6
        approx_height = obj.font_size
        return obj.x, obj.y, approx_width, approx_height
    # Default for other shapes, rough estimate or 0
    return obj.x, obj.y, 0, 0

def align_left(obj: BaseObject, x: float) -> None:
    obj.x = x

def align_right(obj: BaseObject, x: float) -> None:
    _, _, w, _ = get_bounds(obj)
    obj.x = x - w

def align_top(obj: BaseObject, y: float) -> None:
    obj.y = y

def align_bottom(obj: BaseObject, y: float) -> None:
    _, _, _, h = get_bounds(obj)
    obj.y = y - h

def align_center(obj: BaseObject, x: float, y: float) -> None:
    bx, by, w, h = get_bounds(obj)
    obj.x = x - w / 2
    obj.y = y - h / 2

def distribute_horizontally(objects: List[BaseObject], x_start: float, spacing: float) -> None:
    current_x = x_start
    for obj in objects:
        obj.x = current_x
        _, _, w, _ = get_bounds(obj)
        current_x += w + spacing

def distribute_vertically(objects: List[BaseObject], y_start: float, spacing: float) -> None:
    current_y = y_start
    for obj in objects:
        obj.y = current_y
        _, _, _, h = get_bounds(obj)
        current_y += h + spacing

def stack_vertical(objects: List[BaseObject], x: float, y_start: float, spacing: float) -> None:
    current_y = y_start
    for obj in objects:
        align_center(obj, x, current_y)
        _, _, _, h = get_bounds(obj)
        current_y += h + spacing

def stack_horizontal(objects: List[BaseObject], x_start: float, y: float, spacing: float) -> None:
    current_x = x_start
    for obj in objects:
        align_center(obj, current_x, y)
        _, _, w, _ = get_bounds(obj)
        current_x += w + spacing
