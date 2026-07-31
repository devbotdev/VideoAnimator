"""Keyframe-based animation primitives and manager."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from .objects import BaseObject

EasingMode = Literal["linear", "ease-in", "ease-out", "ease-in-out"]


@dataclass(frozen=True, slots=True)
class Keyframe:
    """A single value at a specific time in an animation."""

    time: float
    value: float


def _lerp(start: float, end: float, amount: float) -> float:
    return start + (end - start) * amount


def _ease(progress: float, easing: EasingMode) -> float:
    if easing == "linear":
        return progress
    if easing == "ease-in":
        return progress * progress
    if easing == "ease-out":
        inverse = 1.0 - progress
        return 1.0 - inverse * inverse
    if easing == "ease-in-out":
        if progress < 0.5:
            return 2.0 * progress * progress
        inverse = -2.0 * progress + 2.0
        return 1.0 - (inverse * inverse) / 2.0
    raise ValueError(f"Unsupported easing mode: {easing}")


@dataclass
class Animation:
    """Keyframe-based interpolation for one object property."""

    target: "BaseObject"
    property_name: str
    keyframes: list[Keyframe]
    easing: EasingMode = "linear"
    elapsed: float = 0.0
    completed: bool = False

    def __post_init__(self) -> None:
        self.keyframes.sort(key=lambda keyframe: keyframe.time)
        if len(self.keyframes) < 2:
            raise ValueError("An animation requires at least two keyframes.")
        if self.keyframes[0].time < 0:
            raise ValueError("Animation keyframes must start at time 0 or later.")

    @property
    def duration(self) -> float:
        """Return the total animation duration."""
        return self.keyframes[-1].time

    @classmethod
    def from_values(
        cls,
        target: "BaseObject",
        property_name: str,
        start_value: float,
        end_value: float,
        duration: float,
        easing: EasingMode = "linear",
    ) -> "Animation":
        """Create a two-keyframe animation from start and end values."""
        if duration < 0:
            raise ValueError("Animation duration must be non-negative.")
        animation = cls(
            target=target,
            property_name=property_name,
            keyframes=[
                Keyframe(0.0, start_value),
                Keyframe(duration, end_value),
            ],
            easing=easing,
        )
        setattr(target, property_name, start_value)
        return animation

    def value_at(self, time_position: float) -> float:
        """Compute the animated value at a specific time."""
        if self.duration == 0:
            return self.keyframes[-1].value
        if time_position <= self.keyframes[0].time:
            return self.keyframes[0].value
        if time_position >= self.keyframes[-1].time:
            return self.keyframes[-1].value

        for index in range(len(self.keyframes) - 1):
            start = self.keyframes[index]
            end = self.keyframes[index + 1]
            if start.time <= time_position <= end.time:
                span = end.time - start.time
                if span == 0:
                    return end.value
                progress = (time_position - start.time) / span
                eased_progress = _ease(progress, self.easing)
                return _lerp(start.value, end.value, eased_progress)

        return self.keyframes[-1].value

    def update(self, delta_time: float) -> bool:
        """Advance the animation and apply the interpolated value."""
        if self.completed:
            return True

        self.elapsed = min(self.elapsed + delta_time, self.duration)
        if self.duration == 0:
            setattr(self.target, self.property_name, self.keyframes[-1].value)
        else:
            setattr(self.target, self.property_name, self.value_at(self.elapsed))
        self.target.update(delta_time)
        if self.elapsed >= self.duration:
            self.completed = True
        return self.completed


@dataclass
class AnimationManager:
    """Track and update all active animations."""

    animations: list[Animation] = field(default_factory=list)

    def add(self, animation: Animation) -> Animation:
        """Register an animation with the manager."""
        self.animations.append(animation)
        return animation

    def animate(
        self,
        target: "BaseObject",
        property_name: str,
        start_value: float,
        end_value: float,
        duration: float,
        easing: EasingMode = "linear",
    ) -> Animation:
        """Create and register a new animation."""
        animation = Animation.from_values(
            target=target,
            property_name=property_name,
            start_value=start_value,
            end_value=end_value,
            duration=duration,
            easing=easing,
        )
        return self.add(animation)

    def update(self, delta_time: float) -> None:
        """Advance all active animations and drop completed ones."""
        active_animations: list[Animation] = []
        for animation in self.animations:
            if not animation.update(delta_time):
                active_animations.append(animation)
        self.animations = active_animations

    def clear(self) -> None:
        """Remove all tracked animations."""
        self.animations.clear()
