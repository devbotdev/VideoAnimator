"""Scene management for grouping objects, timelines, and transitions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from .animation import Animation, AnimationManager, AnimationCallback, EasingMode
from .camera import Camera
from .objects import BaseObject
from .timeline import Timeline
from .transition import Transition, FadeTransition, SceneFrame


from .theme import Theme

@dataclass
class Scene:
    """A collection of objects with its own timeline and camera."""

    name: str = "Scene"
    background: str = "#ffffff"
    theme: Theme | None = None
    camera: Camera = field(default_factory=Camera)
    objects: list[BaseObject] = field(default_factory=list)
    named_objects: dict[str, BaseObject] = field(default_factory=dict)
    animation_manager: AnimationManager = field(default_factory=AnimationManager)
    timelines: dict[str, Timeline] = field(default_factory=lambda: {"main": Timeline()})
    
    # New fields
    duration: float | None = None
    elapsed_time: float = 0.0
    
    def on_enter(self) -> None:
        """Called when entering the scene."""
        pass

    def on_update(self, delta_time: float) -> None:
        """Custom update logic for the scene."""
        pass

    def on_exit(self) -> None:
        """Called when exiting the scene."""
        pass
    
    @property
    def completed(self) -> bool:
        """Check if the scene has completed its duration."""
        if self.duration is None:
            return False
        return self.elapsed_time >= self.duration

    def add(self, obj: BaseObject) -> BaseObject:
        """Add an object to the scene."""
        if self.theme:
            obj.apply_theme(self.theme)
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
        delay: float = 0.0,
        repeat: int | None = None,
        yoyo: bool = False,
        on_start: AnimationCallback | None = None,
        on_complete: AnimationCallback | None = None,
        start_time: float | None = None,
    ) -> Animation:
        """Create an animation within the scene."""
        return self.animation_manager.animate(
            target=target,
            property_name=property_name,
            start_value=start_value,
            end_value=end_value,
            duration=duration,
            easing=easing,
            delay=delay,
            repeat=repeat,
            yoyo=yoyo,
            on_start=on_start,
            on_complete=on_complete,
            start_time=start_time,
        )

    def animate_camera(
        self,
        property_name: str,
        start_value: float,
        end_value: float,
        duration: float,
        easing: EasingMode = "linear",
        delay: float = 0.0,
        repeat: int | None = None,
        yoyo: bool = False,
        on_start: AnimationCallback | None = None,
        on_complete: AnimationCallback | None = None,
        start_time: float | None = None,
    ) -> Animation:
        """Create an animation for the scene camera."""
        return self.animation_manager.animate(
            target=self.camera,
            property_name=property_name,
            start_value=start_value,
            end_value=end_value,
            duration=duration,
            easing=easing,
            delay=delay,
            repeat=repeat,
            yoyo=yoyo,
            on_start=on_start,
            on_complete=on_complete,
            start_time=start_time,
        )

    def update(self, delta_time: float) -> None:
        """Advance timelines and active animations."""
        self.elapsed_time += delta_time
        self.on_update(delta_time)
        
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
    transition: Transition | None = None
    transition_target_index: int | None = None
    
    # Optional: default transition
    default_transition_type: type[Transition] = FadeTransition
    default_transition_duration: float = 1.0

    def add_scene(self, scene: Scene) -> Scene:
        """Register a scene with the manager."""
        if not self.scenes:
            scene.on_enter()
        self.scenes.append(scene)
        return scene

    @property
    def current_scene(self) -> Scene:
        """Return the active scene."""
        if not self.scenes:
            raise IndexError("No scenes have been registered.")
        return self.scenes[self.active_index]

    def transition_to(self, index: int, transition: Transition | None = None) -> None:
        """Start transitioning to another scene."""
        if index < 0 or index >= len(self.scenes):
            raise IndexError("Transition target is out of range.")
        if index == self.active_index:
            return
        
        if transition is None:
            transition = self.default_transition_type(duration=self.default_transition_duration)
            
        self.transition = transition
        self.transition_target_index = index
        self.scenes[index].on_enter()

    def update(self, delta_time: float) -> None:
        """Update the active scene, transition, and handle sequencing."""
        if not self.scenes:
            return
            
        if self.transition is None:
            self.current_scene.update(delta_time)
            
            # Check for automatic transition
            if self.current_scene.completed:
                next_index = self.active_index + 1
                if next_index < len(self.scenes):
                    self.current_scene.on_exit()
                    self.transition_to(next_index)
        else:
            # Updating transition
            target_scene = self.scenes[self.transition_target_index]
            self.current_scene.update(delta_time)
            target_scene.update(delta_time)
            self.transition.update(delta_time)
            
            if self.transition.completed:
                self.current_scene.on_exit()
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
