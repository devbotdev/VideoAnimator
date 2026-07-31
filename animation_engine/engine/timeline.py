"""Timeline scheduling for scenes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
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

