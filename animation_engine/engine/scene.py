"""Scene management for grouping objects, timelines, and transitions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from .animation import Animation, AnimationManager, EasingMode
from .camera import Camera
from .objects import BaseObject
from .timeline import Timeline
from .transition import FadeTransition, SceneFrame


@dataclass
class Scene:
    """A collection of objects with its own timeline and camera."""

    name: str = "Scene"
    background: str = "#ffffff"
    camera: Camera = field(default_factory=Camera)
    objects: list[BaseObject] = field(default_factory=list)
    named_objects: dict[str, BaseObject] = field(default_factory=dict)
    animation_manager: AnimationManager = field(default_factory=AnimationManager)
    timelines: dict[str, Timeline] = field(default_factory=lambda: {"main": Timeline()})

    def add(self, obj: BaseObject) -> BaseObject:
        """Add an object to the scene."""
        self.objects.append(obj)
        return obj

    def register_object(self, name: str, obj: BaseObject) -> BaseObject:
        """Add a named object to the scene."""
        self.named_objects[name] = obj
        return self.add(obj)

    def object(self, name: str) -> BaseObject:
        """Return a named object."""
        try:
            return self.named_objects[name]
        except KeyError as exc:
            raise KeyError(f"Unknown object '{name}' in scene '{self.name}'.") from exc

    def extend(self, objects: Iterable[BaseObject]) -> None:
        """Add multiple objects to the scene."""
        self.objects.extend(objects)

    def timeline(self, name: str = "main") -> Timeline:
        """Get or create a named timeline."""
        if name not in self.timelines:
            self.timelines[name] = Timeline()
        return self.timelines[name]

    def animate(
        self,
        target: BaseObject,
        property_name: str,
        start_value: float,
        end_value: float,
        duration: float,
        easing: EasingMode = "linear",
    ) -> Animation:
        """Create an animation within the scene."""
        return self.animation_manager.animate(
            target=target,
            property_name=property_name,
            start_value=start_value,
            end_value=end_value,
            duration=duration,
            easing=easing,
        )

    def update(self, delta_time: float) -> None:
        """Advance timelines and active animations."""
        for timeline in self.timelines.values():
            timeline.update(delta_time, self)
        self.animation_manager.update(delta_time)

    def frame(self) -> SceneFrame:
        """Resolve the current renderable scene frame."""
        return SceneFrame(objects=self.objects, camera=self.camera, background=self.background)


@dataclass
class SceneManager:
    """Manage multiple scenes and transitions between them."""

    scenes: list[Scene] = field(default_factory=list)
    active_index: int = 0
    transition: FadeTransition | None = None
    transition_target_index: int | None = None

    def add_scene(self, scene: Scene) -> Scene:
        """Register a scene with the manager."""
        self.scenes.append(scene)
        return scene

    @property
    def current_scene(self) -> Scene:
        """Return the active scene."""
        if not self.scenes:
            raise IndexError("No scenes have been registered.")
        return self.scenes[self.active_index]

    def transition_to(self, index: int, duration: float) -> None:
        """Start transitioning to another scene."""
        if index < 0 or index >= len(self.scenes):
            raise IndexError("Transition target is out of range.")
        if index == self.active_index:
            return
        self.transition = FadeTransition(duration=duration)
        self.transition_target_index = index

    def update(self, delta_time: float) -> None:
        """Update the active scene and any transition."""
        if not self.scenes:
            return
        self.current_scene.update(delta_time)
        if self.transition is not None and self.transition_target_index is not None:
            target_scene = self.scenes[self.transition_target_index]
            target_scene.update(delta_time)
            self.transition.update(delta_time)
            if self.transition.completed:
                self.active_index = self.transition_target_index
                self.transition = None
                self.transition_target_index = None

    def frame(self) -> SceneFrame:
        """Return the frame to render for the current manager state."""
        current_frame = self.current_scene.frame()
        if self.transition is None or self.transition_target_index is None:
            return current_frame
        target_frame = self.scenes[self.transition_target_index].frame()
        return self.transition.blend_frame(current_frame, target_frame)
