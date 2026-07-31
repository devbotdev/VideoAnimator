"""Canvas abstractions used by the renderer."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Iterable
from xml.sax.saxutils import escape, quoteattr

from .camera import Camera
from .objects import Arrow, BaseObject, Circle, Group, Line, Rectangle, Text, Polyline, Path
from .stick_figure import StickFigure


@dataclass(slots=True)
class SVGCanvas:
    """Create SVG markup for a collection of engine objects."""

    width: int = 1920
    height: int = 1080
    background: str = "#ffffff"
    camera: Camera | None = None
    objects: list[BaseObject] = field(default_factory=list)

    def add(self, obj: BaseObject) -> BaseObject:
        """Add an object to the canvas."""
        self.objects.append(obj)
        return obj

    def extend(self, objects: Iterable[BaseObject]) -> None:
        """Add multiple objects to the canvas."""
        self.objects.extend(objects)

    def clear(self) -> None:
        """Remove all objects from the canvas."""
        self.objects.clear()

    def to_svg(self, objects: Iterable[BaseObject] | None = None) -> str:
        """Convert the canvas and objects into SVG markup."""
        svg_objects = self.objects if objects is None else list(objects)
        elements = [self._background_rect()]
        for obj in svg_objects:
            if obj.visibility:
                elements.append(self._object_to_svg(obj))

        content = "".join(elements)
        if self.camera and self.camera.rotation != 0:
            # Apply rotation around the camera center
            content = f'<g transform="rotate({-self.camera.rotation} {self.camera.x} {self.camera.y})">{content}</g>'

        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{self.width}" height="{self.height}" '
            f'viewBox="{" ".join(str(value) for value in self._view_box())}">'
            + content
            + "</svg>"
        )

    def _view_box(self) -> tuple[float, float, float, float]:
        if self.camera is None:
            return 0.0, 0.0, float(self.width), float(self.height)
        return self.camera.view_box()

    def _background_rect(self) -> str:
        return (
            f'<rect x="0" y="0" width="{self.width}" height="{self.height}" '
            f'fill="{self.background}" />'
        )

    def _transform(self, obj: BaseObject) -> str:
        transforms: list[str] = []
        if obj.x or obj.y:
            transforms.append(f"translate({obj.x} {obj.y})")
        if obj.rotation:
            transforms.append(f"rotate({obj.rotation})")
        if obj.scale != 1.0:
            transforms.append(f"scale({obj.scale})")
        return " ".join(transforms)

    def _style_attrs(
        self,
        obj: BaseObject,
        *,
        fill: str | None = None,
        stroke: str | None = None,
        stroke_width: float | None = None,
    ) -> str:
        style = obj.style
        attrs = {
            "opacity": obj.opacity,
            "fill": style.fill_color if fill is None else fill,
            "stroke": style.stroke_color if stroke is None else stroke,
            "stroke-width": style.stroke_width if stroke_width is None else stroke_width,
        }
        if style.line_cap is not None:
            attrs["stroke-linecap"] = style.line_cap
        if style.line_join is not None:
            attrs["stroke-linejoin"] = style.line_join
        return self._attrs(attrs)

    def _attrs(self, attrs: dict[str, object]) -> str:
        return " ".join(f"{name}={quoteattr(str(value))}" for name, value in attrs.items())

    def _object_to_svg(self, obj: BaseObject) -> str:
        if isinstance(obj, Circle):
            return self._circle_to_svg(obj)
        if isinstance(obj, Rectangle):
            return self._rectangle_to_svg(obj)
        if isinstance(obj, Arrow):
            return self._arrow_to_svg(obj)
        if isinstance(obj, Line):
            return self._line_to_svg(obj)
        if isinstance(obj, Polyline):
            return self._polyline_to_svg(obj)
        if isinstance(obj, Path):
            return self._path_to_svg(obj)
        if isinstance(obj, Text):
            return self._text_to_svg(obj)
        if isinstance(obj, Group):
            return self._group_to_svg(obj)
        raise TypeError(f"Unsupported object type: {type(obj)!r}")

    def _wrap(self, obj: BaseObject, element: str) -> str:
        transform = self._transform(obj)
        if transform:
            return f'<g transform="{transform}">{element}</g>'
        return element

    def _circle_to_svg(self, obj: Circle) -> str:
        element = (
            f'<circle cx="0" cy="0" r="{obj.radius}" '
            f'{self._style_attrs(obj)} />'
        )
        return self._wrap(obj, element)

    def _rectangle_to_svg(self, obj: Rectangle) -> str:
        rounded = ""
        if obj.corner_radius:
            radius = max(0.0, obj.corner_radius)
            rounded = f' rx="{radius}" ry="{radius}"'
        element = (
            f'<rect x="0" y="0" width="{obj.width}" height="{obj.height}"{rounded} '
            f'{self._style_attrs(obj)} />'
        )
        return self._wrap(obj, element)

    def _line_to_svg(self, obj: Line) -> str:
        element = (
            f'<line x1="0" y1="0" x2="{obj.end_x}" y2="{obj.end_y}" '
            f'{self._style_attrs(obj, fill="none")} />'
        )
        return self._wrap(obj, element)

    def _polyline_to_svg(self, obj: Polyline) -> str:
        points_attr = " ".join(f"{x},{y}" for x, y in obj.points)
        element = (
            f'<polyline points={quoteattr(points_attr)} '
            f'{self._style_attrs(obj, fill="none")} />'
        )
        return self._wrap(obj, element)

    def _path_to_svg(self, obj: Path) -> str:
        element = (
            f'<path d={quoteattr(obj.d)} '
            f'{self._style_attrs(obj)} />'
        )
        return self._wrap(obj, element)

    def _text_to_svg(self, obj: Text) -> str:
        content = escape(obj.content)
        element = (
            f'<text x="0" y="0" font-size="{obj.font_size}" '
            f'font-family={quoteattr(obj.font_family)} '
            f'font-weight={quoteattr(obj.font_weight)} '
            f'text-anchor={quoteattr(obj.text_anchor)} '
            f'dominant-baseline={quoteattr(obj.text_alignment)} '
            f'{self._style_attrs(obj)}>{content}</text>'
        )
        return self._wrap(obj, element)

    def _group_to_svg(self, obj: Group) -> str:
        children = "".join(self._object_to_svg(child) for child in obj.children if child.visibility)
        attrs: dict[str, object] = {}
        transform = self._transform(obj)
        if transform:
            attrs["transform"] = transform
        if obj.opacity != 1.0:
            attrs["opacity"] = obj.opacity
        if not attrs:
            return f"<g>{children}</g>"
        return f'<g {self._attrs(attrs)}>{children}</g>'

    def _arrow_to_svg(self, obj: Arrow) -> str:
        line = (
            f'<line x1="{obj.start_x}" y1="{obj.start_y}" '
            f'x2="{obj.end_x}" y2="{obj.end_y}" '
            f'{self._style_attrs(obj, fill="none")} />'
        )
        head = self._arrowhead_to_svg(obj)
        return self._wrap(obj, line + head)

    def _arrowhead_to_svg(self, obj: Arrow) -> str:
        dx = obj.end_x - obj.start_x
        dy = obj.end_y - obj.start_y
        length = math.hypot(dx, dy)
        if length == 0:
            return ""

        size = max(0.0, obj.arrowhead_size)
        if size == 0:
            return ""

        ux = dx / length
        uy = dy / length
        px = -uy
        py = ux
        base_x = obj.end_x - ux * size
        base_y = obj.end_y - uy * size
        half_width = size * 0.5
        points = [
            (obj.end_x, obj.end_y),
            (base_x + px * half_width, base_y + py * half_width),
            (base_x - px * half_width, base_y - py * half_width),
        ]
        point_attr = " ".join(f"{x},{y}" for x, y in points)
        return (
            f'<polygon points={quoteattr(point_attr)} '
            f'fill={quoteattr(obj.stroke_color)} '
            f'stroke={quoteattr(obj.stroke_color)} '
            f'stroke-width={quoteattr(str(obj.stroke_width))} '
            f'opacity={quoteattr(str(obj.opacity))} />'
        )
