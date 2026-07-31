"""Camera controls for scene rendering."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Camera:
    """Define the visible region of a scene."""

    x: float = 0.0
    y: float = 0.0
    zoom: float = 1.0
    rotation: float = 0.0
    width: int = 1920
    height: int = 1080

    def pan_to(self, x: float, y: float) -> None:
        """Move the camera to a new top-left position."""
        self.x = x
        self.y = y

    def zoom_to(self, zoom: float) -> None:
        """Set the zoom level."""
        if zoom <= 0:
            raise ValueError("Camera zoom must be greater than zero.")
        self.zoom = zoom

    def view_box(self) -> tuple[float, float, float, float]:
        """Return the SVG viewBox for the camera."""
        return self.x, self.y, self.width / self.zoom, self.height / self.zoom

