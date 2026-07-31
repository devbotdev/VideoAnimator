"""Scene transition helpers."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from .camera import Camera
from .objects import BaseObject


@dataclass(slots=True)
class SceneFrame:
    """Resolved render state for a scene or transition."""

    objects: list[BaseObject]
    camera: Camera
    background: str


@runtime_checkable
class Transition(Protocol):
    """Protocol for scene transitions."""

    duration: float
    completed: bool

    def update(self, delta_time: float) -> float:
        """Advance the transition and return its progress."""
        ...

    @property
    def progress(self) -> float:
        """Return the transition progress in the range [0, 1]."""
        ...

    def blend_frame(self, from_frame: SceneFrame, to_frame: SceneFrame) -> SceneFrame:
        """Create a blended frame from two scenes."""
        ...


def _lerp(start: float, end: float, amount: float) -> float:
    return start + (end - start) * amount


def _lerp_color(start: str, end: str, amount: float) -> str:
    """Interpolate between two hex colors."""
    if (
        not start.startswith("#")
        or len(start) != 7
        or not end.startswith("#")
        or len(end) != 7
    ):
        raise ValueError("Colors must be in '#RRGGBB' format.")

    def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
        return int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)

    def rgb_to_hex(r: int, g: int, b: int) -> str:
        return f"#{r:02x}{g:02x}{b:02x}"

    start_rgb = hex_to_rgb(start)
    end_rgb = hex_to_rgb(end)

    r = int(_lerp(start_rgb[0], end_rgb[0], amount))
    g = int(_lerp(start_rgb[1], end_rgb[1], amount))
    b = int(_lerp(start_rgb[2], end_rgb[2], amount))

    return rgb_to_hex(r, g, b)


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
                rotation=_lerp(
                    from_frame.camera.rotation, to_frame.camera.rotation, progress
                ),
                width=from_frame.camera.width,
                height=from_frame.camera.height,
            ),
            background=_lerp_color(from_frame.background, to_frame.background, progress),
        )



@dataclass
class SlideTransition:
    """Slide one scene out to make room for another."""
    
    duration: float
    direction: str = "left"  # "left" or "right"
    elapsed: float = 0.0
    completed: bool = False

    def update(self, delta_time: float) -> float:
        if self.completed:
            return 1.0
        self.elapsed = min(self.elapsed + delta_time, self.duration)
        if self.elapsed >= self.duration:
            self.completed = True
        return self.progress

    @property
    def progress(self) -> float:
        if self.duration == 0:
            return 1.0
        return min(self.elapsed / self.duration, 1.0)

    def blend_frame(self, from_frame: SceneFrame, to_frame: SceneFrame) -> SceneFrame:
        progress = self.progress
        from_objects = deepcopy(from_frame.objects)
        to_objects = deepcopy(to_frame.objects)
        
        # Slide logic: modify positions
        offset = progress * from_frame.camera.width
        if self.direction == "left":
            for obj in from_objects:
                obj.x -= offset
            for obj in to_objects:
                obj.x += (from_frame.camera.width - offset)
        else: # "right"
            for obj in from_objects:
                obj.x += offset
            for obj in to_objects:
                obj.x -= (from_frame.camera.width - offset)
                
        return SceneFrame(
            objects=from_objects + to_objects,
            camera=from_frame.camera,
            background=from_frame.background,
        )


@dataclass
class WipeTransition:
    """Wipe one scene with another."""
    
    duration: float
    elapsed: float = 0.0
    completed: bool = False

    def update(self, delta_time: float) -> float:
        if self.completed:
            return 1.0
        self.elapsed = min(self.elapsed + delta_time, self.duration)
        if self.elapsed >= self.duration:
            self.completed = True
        return self.progress

    @property
    def progress(self) -> float:
        if self.duration == 0:
            return 1.0
        return min(self.elapsed / self.duration, 1.0)

    def blend_frame(self, from_frame: SceneFrame, to_frame: SceneFrame) -> SceneFrame:
        # Simple implementation: clip objects based on progress
        progress = self.progress
        from_objects = deepcopy(from_frame.objects)
        to_objects = deepcopy(to_frame.objects)
        
        # A simple wipe could just be masking or partial opacity
        # Given we don't have explicit clipping support for objects, 
        # let's use opacity for a simple wipe effect
        for obj in from_objects:
            if obj.x < from_frame.camera.width * progress:
                obj.opacity = 0.0
        for obj in to_objects:
            if obj.x > from_frame.camera.width * (1.0 - progress):
                obj.opacity = 1.0
            else:
                obj.opacity = 0.0
                
        return SceneFrame(
            objects=from_objects + to_objects,
            camera=from_frame.camera,
            background=from_frame.background,
        )
