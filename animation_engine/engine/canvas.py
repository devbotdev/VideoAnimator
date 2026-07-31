"""Canvas abstractions used by the renderer."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable
from xml.sax.saxutils import escape

from .camera import Camera
from .objects import BaseObject, Circle, Line, Rectangle, Text
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
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{self.width}" height="{self.height}" '
            f'viewBox="{" ".join(str(value) for value in self._view_box())}">'
            + "".join(elements)
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

    def _style(self, obj: BaseObject, fill: str = "#222222", stroke: str = "none") -> str:
        return f'opacity="{obj.opacity}" fill="{fill}" stroke="{stroke}"'

    def _object_to_svg(self, obj: BaseObject) -> str:
        if isinstance(obj, Circle):
            return self._circle_to_svg(obj)
        if isinstance(obj, Rectangle):
            return self._rectangle_to_svg(obj)
        if isinstance(obj, Line):
            return self._line_to_svg(obj)
        if isinstance(obj, Text):
            return self._text_to_svg(obj)
        if isinstance(obj, StickFigure):
            return "".join(self._object_to_svg(part) for part in obj.parts())
        raise TypeError(f"Unsupported object type: {type(obj)!r}")

    def _wrap(self, obj: BaseObject, element: str) -> str:
        transform = self._transform(obj)
        if transform:
            return f'<g transform="{transform}">{element}</g>'
        return element

    def _circle_to_svg(self, obj: Circle) -> str:
        element = (
            f'<circle cx="0" cy="0" r="{obj.radius}" '
            f'{self._style(obj)} />'
        )
        return self._wrap(obj, element)

    def _rectangle_to_svg(self, obj: Rectangle) -> str:
        element = (
            f'<rect x="0" y="0" width="{obj.width}" height="{obj.height}" '
            f'{self._style(obj)} />'
        )
        return self._wrap(obj, element)

    def _line_to_svg(self, obj: Line) -> str:
        element = (
            f'<line x1="0" y1="0" x2="{obj.end_x}" y2="{obj.end_y}" '
            f'stroke="#222222" stroke-width="2" opacity="{obj.opacity}" />'
        )
        return self._wrap(obj, element)

    def _text_to_svg(self, obj: Text) -> str:
        content = escape(obj.content)
        element = (
            f'<text x="0" y="0" font-size="{obj.font_size}" '
            f'fill="#222222" opacity="{obj.opacity}">{content}</text>'
        )
        return self._wrap(obj, element)
