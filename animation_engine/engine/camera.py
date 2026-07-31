"""Camera controls for scene rendering."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
import math

if TYPE_CHECKING:
    from .objects import BaseObject

@dataclass
class Camera:
    """Define the visible region of a scene."""

    x: float = 960.0  # Center X
    y: float = 540.0  # Center Y
    zoom: float = 1.0
    rotation: float = 0.0
    width: int = 1920
    height: int = 1080

    def pan_to(self, x: float, y: float) -> None:
        """Move the camera center to a new position."""
        self.x = x
        self.y = y

    def pan_by(self, dx: float, dy: float) -> None:
        """Move the camera center relative to current position."""
        self.x += dx
        self.y += dy

    def zoom_to(self, zoom: float) -> None:
        """Set the zoom level."""
        if zoom <= 0:
            raise ValueError("Camera zoom must be greater than zero.")
        self.zoom = zoom

    def zoom_by(self, factor: float) -> None:
        """Multiply current zoom by a factor."""
        self.zoom_to(self.zoom * factor)

    def focus_on(self, obj: BaseObject, padding: float = 0.0) -> None:
        """Focus the camera on the given object."""
        # Note: This implementation assumes simple bounds based on object position/size if available.
        # This is a basic implementation and might need refinement for complex objects.
        self.x = obj.x
        self.y = obj.y

    def view_box(self) -> tuple[float, float, float, float]:
        """Return the SVG viewBox for the camera."""
        visible_width = self.width / self.zoom
        visible_height = self.height / self.zoom
        return (
            self.x - visible_width / 2,
            self.y - visible_height / 2,
            visible_width,
            visible_height,
        )

