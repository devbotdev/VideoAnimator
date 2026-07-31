"""Core object model for the animation engine."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .animation import Animation


@dataclass
class BaseObject:
    """Base class for all animatable objects."""

    x: float = 0.0
    y: float = 0.0
    rotation: float = 0.0
    scale: float = 1.0
    opacity: float = 1.0
    visibility: bool = True

    def move_to(self, x: float, y: float) -> None:
        """Move the object to an absolute position."""
        self.x = x
        self.y = y

    def translate(self, dx: float, dy: float) -> None:
        """Move the object relative to its current position."""
        self.x += dx
        self.y += dy

    def set_rotation(self, rotation: float) -> None:
        """Set the rotation angle in degrees."""
        self.rotation = rotation

    def rotate_by(self, delta: float) -> None:
        """Adjust the rotation angle by a relative amount."""
        self.rotation += delta

    def set_scale(self, scale: float) -> None:
        """Set the uniform scale factor."""
        self.scale = scale

    def scale_by(self, factor: float) -> None:
        """Multiply the current scale by a factor."""
        self.scale *= factor

    def set_opacity(self, opacity: float) -> None:
        """Set the opacity value."""
        self.opacity = opacity

    def animate(
        self,
        property_name: str,
        start_value: float,
        end_value: float,
        duration: float,
        easing: str = "linear",
    ) -> Animation:
        """Create a keyframe animation for one of the object's properties."""
        from .animation import Animation

        return Animation.from_values(
            target=self,
            property_name=property_name,
            start_value=start_value,
            end_value=end_value,
            duration=duration,
            easing=easing,
        )

    def show(self) -> None:
        """Make the object visible."""
        self.visibility = True

    def hide(self) -> None:
        """Hide the object."""
        self.visibility = False

    def update(self, delta_time: float) -> None:
        """Update the object's state for a simulation step."""

    def draw(self, canvas: Any) -> None:
        """Draw the object on a canvas placeholder."""
        raise NotImplementedError("Rendering is not implemented yet.")


@dataclass
class Circle(BaseObject):
    """Circular object definition."""

    radius: float = 1.0


@dataclass
class Rectangle(BaseObject):
    """Rectangular object definition."""

    width: float = 1.0
    height: float = 1.0


@dataclass
class Line(BaseObject):
    """Line object definition."""

    end_x: float = 0.0
    end_y: float = 0.0


@dataclass
class Text(BaseObject):
    """Text object definition."""

    content: str = ""
    font_size: float = 12.0
