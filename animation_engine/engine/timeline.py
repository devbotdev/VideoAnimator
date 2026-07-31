"""Timeline scheduling for scenes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable

from .animation import EasingMode

if TYPE_CHECKING:
    from .objects import BaseObject
    from .scene import Scene


TimelineCallback = Callable[["Scene"], None]


@dataclass(slots=True)
class TimelineEvent:
    """A scheduled callback in a scene timeline."""

    time: float
    callback: TimelineCallback
    triggered: bool = False


@dataclass
class Timeline:
    """Schedule scene events over time."""

    events: list[TimelineEvent] = field(default_factory=list)
    elapsed: float = 0.0

    def schedule(self, time: float, callback: TimelineCallback) -> TimelineEvent:
        """Add a timeline event."""
        if time < 0:
            raise ValueError("Timeline event time must be non-negative.")
        event = TimelineEvent(time=time, callback=callback)
        self.events.append(event)
        self.events.sort(key=lambda item: item.time)
        return event

    def schedule_animation(
        self,
        time: float,
        scene: "Scene",
        target: "BaseObject",
        property_name: str,
        start_value: float,
        end_value: float,
        duration: float,
        easing: EasingMode = "linear",
        delay: float = 0.0,
        repeat: int | None = None,
        yoyo: bool = False,
        on_start: Callable[[object], None] | None = None,
        on_complete: Callable[[object], None] | None = None,
        start_time: float | None = None,
    ) -> TimelineEvent:
        """Schedule an animation callback declaratively on a timeline."""

        def callback(scene_instance: "Scene") -> None:
            scene_instance.animate(
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

        return self.schedule(time, callback)

    def animate(
        self,
        time: float,
        scene: "Scene",
        target: "BaseObject",
        property_name: str,
        start_value: float,
        end_value: float,
        duration: float,
        easing: EasingMode = "linear",
        delay: float = 0.0,
        repeat: int | None = None,
        yoyo: bool = False,
        on_start: Callable[[object], None] | None = None,
        on_complete: Callable[[object], None] | None = None,
        start_time: float | None = None,
    ) -> TimelineEvent:
        """Alias for schedule_animation."""
        return self.schedule_animation(
            time=time,
            scene=scene,
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

    def update(self, delta_time: float, scene: "Scene") -> None:
        """Advance the timeline and trigger due events."""
        self.elapsed += delta_time
        for event in self.events:
            if not event.triggered and event.time <= self.elapsed:
                event.callback(scene)
                event.triggered = True

    def reset(self) -> None:
        """Reset the timeline to the beginning."""
        self.elapsed = 0.0
        for event in self.events:
            event.triggered = False

