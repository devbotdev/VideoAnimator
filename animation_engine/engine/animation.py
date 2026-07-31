"""Keyframe-based animation primitives and manager."""

from __future__ import annotations

from dataclasses import dataclass, field
import numbers
from typing import TYPE_CHECKING, Callable, Literal

if TYPE_CHECKING:
    from .objects import BaseObject

EasingMode = Literal["linear", "ease-in", "ease-out", "ease-in-out"]
AnimationCallback = Callable[["Animation"], None]


@dataclass(frozen=True, slots=True)
class Keyframe:
    """A single value at a specific time in an animation."""

    time: float
    value: float


def _lerp(start: float, end: float, amount: float) -> float:
    return start + (end - start) * amount


def _keyframe_animation(
    target: "BaseObject",
    property_name: str,
    values: list[float],
    duration: float,
    easing: EasingMode = "linear",
) -> Animation:
    if duration < 0:
        raise ValueError("Animation duration must be non-negative.")
    if len(values) < 2:
        raise ValueError("At least two values are required for keyframe animation.")

    step = duration / (len(values) - 1) if len(values) > 1 else 0.0
    animation = Animation(
        target=target,
        property_name=property_name,
        keyframes=[Keyframe(index * step, value) for index, value in enumerate(values)],
        easing=easing,
    )
    setattr(target, property_name, values[0])
    return animation


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
    delay: float = 0.0
    repeat_count: int | None = None
    yoyo: bool = False
    on_start: AnimationCallback | None = None
    on_complete: AnimationCallback | None = None

    def __post_init__(self) -> None:
        self.keyframes.sort(key=lambda keyframe: keyframe.time)
        if len(self.keyframes) < 2:
            raise ValueError("An animation requires at least two keyframes.")
        if self.keyframes[0].time < 0:
            raise ValueError("Animation keyframes must start at time 0 or later.")
        self._validate_property()
        self._time_since_started = 0.0
        self._started = False
        self._pending_delay = self.delay

    @staticmethod
    def _validate_numeric(value: object, name: str) -> None:
        if isinstance(value, bool) or not isinstance(value, numbers.Real):
            raise TypeError(f"{name} must be numeric, got {type(value).__name__}.")

    def _validate_property(self) -> None:
        if not hasattr(self.target, self.property_name):
            raise AttributeError(f"Target object '{type(self.target).__name__}' has no property '{self.property_name}'.")
        current_value = getattr(self.target, self.property_name)
        if isinstance(current_value, bool) or not isinstance(current_value, numbers.Real):
            raise TypeError(
                f"Target property '{self.property_name}' must be numeric, got {type(current_value).__name__}."
            )

    @property
    def duration(self) -> float:
        """Return the base animation duration."""
        return self.keyframes[-1].time

    @property
    def active_duration(self) -> float:
        """Return the time spent animating after delays and before completion."""
        if self.duration == 0:
            return 0.0
        cycle_duration = self.duration * 2.0 if self.yoyo else self.duration
        cycle_count = 1 if self.repeat_count is None else self.repeat_count + 1
        return cycle_duration * cycle_count

    @property
    def absolute_duration(self) -> float:
        """Return the total time from scheduling to completion including delay."""
        return self.delay + self.active_duration

    @property
    def state(self) -> str:
        """Return the animation's current lifecycle state."""
        if self.completed:
            return "completed"
        if self._pending_delay > 0.0:
            return "pending"
        return "running"

    @classmethod
    def from_values(
        cls,
        target: "BaseObject",
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
    ) -> "Animation":
        """Create a two-keyframe animation from start and end values."""
        cls._validate_numeric(start_value, "start_value")
        cls._validate_numeric(end_value, "end_value")
        if duration < 0:
            raise ValueError("Animation duration must be non-negative.")
        if delay < 0:
            raise ValueError("Animation delay must be non-negative.")
        if repeat is not None:
            if isinstance(repeat, bool) or not isinstance(repeat, int) or repeat < 0:
                raise ValueError("Animation repeat count must be a non-negative integer.")
        animation = cls(
            target=target,
            property_name=property_name,
            keyframes=[
                Keyframe(0.0, start_value),
                Keyframe(duration, end_value),
            ],
            easing=easing,
            delay=delay,
            repeat_count=repeat,
            yoyo=yoyo,
            on_start=on_start,
            on_complete=on_complete,
        )
        setattr(target, property_name, start_value)
        return animation

    def value_at(self, time_position: float) -> float:
        """Compute the animated value at a specific time."""
        if self.active_duration == 0:
            return self.keyframes[-1].value
        if time_position <= 0.0:
            return self.keyframes[0].value
        if time_position >= self.active_duration:
            return self.keyframes[-1].value

        cycle_duration = self.duration * 2.0 if self.yoyo else self.duration
        cycle_count = 1 if self.repeat_count is None else self.repeat_count + 1
        if cycle_duration == 0:
            return self.keyframes[-1].value

        cycle_index = int(time_position // cycle_duration)
        if cycle_index >= cycle_count:
            return self.keyframes[-1].value

        cycle_time = time_position - cycle_index * cycle_duration
        if self.yoyo:
            if cycle_time <= self.duration:
                base_time = cycle_time
            else:
                base_time = cycle_duration - cycle_time
            return self._value_at_base(base_time)

        return self._value_at_base(cycle_time)

    def _value_at_base(self, time_position: float) -> float:
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

        if self._pending_delay > 0.0:
            if delta_time <= self._pending_delay:
                self._pending_delay -= delta_time
                self._time_since_started += delta_time
                return False
            self._time_since_started += self._pending_delay
            delta_time -= self._pending_delay
            self._pending_delay = 0.0

        if not self._started:
            self._started = True
            if self.on_start is not None:
                self.on_start(self)

        self.elapsed = min(self.elapsed + delta_time, self.active_duration)
        if self.active_duration == 0:
            setattr(self.target, self.property_name, self.keyframes[-1].value)
        else:
            setattr(self.target, self.property_name, self.value_at(self.elapsed))
        self.target.update(delta_time)
        if self.elapsed >= self.active_duration:
            self.completed = True
            if self.on_complete is not None:
                self.on_complete(self)
        return self.completed


@dataclass
class AnimationManager:
    """Track and update all active animations."""

    animations: list[Animation] = field(default_factory=list)
    elapsed_time: float = 0.0

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
        delay: float = 0.0,
        repeat: int | None = None,
        yoyo: bool = False,
        on_start: AnimationCallback | None = None,
        on_complete: AnimationCallback | None = None,
        start_time: float | None = None,
    ) -> Animation:
        """Create and register a new animation."""
        if start_time is not None and delay != 0.0:
            raise ValueError("Provide either start_time or delay, not both.")
        if start_time is not None:
            if start_time < 0:
                raise ValueError("Animation start_time must be non-negative.")
            delay = max(0.0, start_time - self.elapsed_time)
        animation = Animation.from_values(
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
        )
        return self.add(animation)

    def update(self, delta_time: float) -> None:
        """Advance all active animations and drop completed ones."""
        self.elapsed_time += delta_time
        active_animations: list[Animation] = []
        for animation in self.animations:
            if not animation.update(delta_time):
                active_animations.append(animation)
        self.animations = active_animations

    def clear(self) -> None:
        """Remove all tracked animations."""
        self.animations.clear()
