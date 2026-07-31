"""Scene transition helpers."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass

from .camera import Camera
from .objects import BaseObject


def _lerp(start: float, end: float, amount: float) -> float:
    return start + (end - start) * amount


@dataclass(slots=True)
class SceneFrame:
    """Resolved render state for a scene or transition."""

    objects: list[BaseObject]
    camera: Camera
    background: str


@dataclass
class FadeTransition:
    """Blend two scenes with a simple fade."""

    duration: float
    elapsed: float = 0.0
    completed: bool = False

    def update(self, delta_time: float) -> float:
        """Advance the transition and return its progress."""
        if self.completed:
            return 1.0
        self.elapsed = min(self.elapsed + delta_time, self.duration)
        if self.elapsed >= self.duration:
            self.completed = True
        return self.progress

    @property
    def progress(self) -> float:
        """Return the transition progress in the range [0, 1]."""
        if self.duration == 0:
            return 1.0
        return min(self.elapsed / self.duration, 1.0)

    def blend_frame(self, from_frame: SceneFrame, to_frame: SceneFrame) -> SceneFrame:
        """Create a blended frame from two scenes."""
        progress = self.progress
        from_objects = deepcopy(from_frame.objects)
        to_objects = deepcopy(to_frame.objects)
        for obj in from_objects:
            obj.opacity *= 1.0 - progress
        for obj in to_objects:
            obj.opacity *= progress
        return SceneFrame(
            objects=from_objects + to_objects,
            camera=Camera(
                x=_lerp(from_frame.camera.x, to_frame.camera.x, progress),
                y=_lerp(from_frame.camera.y, to_frame.camera.y, progress),
                zoom=_lerp(from_frame.camera.zoom, to_frame.camera.zoom, progress),
                rotation=_lerp(from_frame.camera.rotation, to_frame.camera.rotation, progress),
                width=from_frame.camera.width,
                height=from_frame.camera.height,
            ),
            background=from_frame.background,
        )

