"""Stick figure composition and simple actions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal

from .animation import Animation, AnimationManager, EasingMode, Keyframe, _keyframe_animation
from .objects import BaseObject, Circle, Line, Group, Style
from .theme import DEFAULT_THEME

if TYPE_CHECKING:
    from .canvas import SVGCanvas


ActionName = Literal["walk", "point", "wave"]


@dataclass
class StickFigure(Group):
    """A simple stick figure built from basic engine objects."""

    head_radius: float = 24.0
    body_length: float = 120.0
    arm_length: float = 90.0
    leg_length: float = 100.0
    head_gap: float = 18.0
    arm_swing: float = 30.0
    leg_swing: float = 25.0

    stroke_color: str = DEFAULT_THEME.foreground_color
    stroke_width: float = DEFAULT_THEME.stroke_width

    head: Circle = field(init=False)
    body: Line = field(init=False)
    left_arm: Line = field(init=False)
    right_arm: Line = field(init=False)
    left_leg: Line = field(init=False)
    right_leg: Line = field(init=False)

    def __post_init__(self) -> None:
        super().__post_init__()

        style = Style(
            stroke_color=self.stroke_color,
            stroke_width=self.stroke_width,
            fill_color="none",
            line_cap="round",
            line_join="round",
        )

        self.head = Circle(radius=self.head_radius, style=style)
        self.body = Line(end_x=0.0, end_y=self.body_length, style=style)
        self.left_arm = Line(end_x=-self.arm_length, end_y=0.0, style=style)
        self.right_arm = Line(end_x=self.arm_length, end_y=0.0, style=style)
        self.left_leg = Line(end_x=-self.leg_length * 0.25, end_y=self.leg_length, style=style)
        self.right_leg = Line(end_x=self.leg_length * 0.25, end_y=self.leg_length, style=style)

        self.extend([self.head, self.body, self.left_arm, self.right_arm, self.left_leg, self.right_leg])
        self._sync_parts()

    def _sync_parts(self) -> None:
        """Position all body parts relative to the figure origin."""
        # Note: In Group, objects are relative to the group origin (0,0)
        self.head.move_to(0.0, -self.head_radius - self.head_gap)
        self.body.move_to(0.0, 0.0)
        # Body is a line from 0,0 to 0,body_length.
        # Arms/legs should be positioned relative to this.
        self.left_arm.move_to(0.0, self.body_length * 0.2)
        self.right_arm.move_to(0.0, self.body_length * 0.2)
        self.left_leg.move_to(0.0, self.body_length)
        self.right_leg.move_to(0.0, self.body_length)

    def update(self, delta_time: float) -> None:
        """Keep the figure parts aligned after animation updates."""
        self._sync_parts()

    def walk(
        self,
        manager: AnimationManager,
        duration: float,
        distance: float = 160.0,
        easing: EasingMode = "ease-in-out",
    ) -> list[Animation]:
        """Animate a simple walking cycle."""
        animations = [
            manager.animate(self, "x", self.x, self.x + distance, duration, easing=easing),
            manager.add(
                _keyframe_animation(
                    self.left_arm,
                    "rotation",
                    [self.arm_swing, -self.arm_swing, self.arm_swing],
                    duration,
                    easing,
                )
            ),
            manager.add(
                _keyframe_animation(
                    self.right_arm,
                    "rotation",
                    [-self.arm_swing, self.arm_swing, -self.arm_swing],
                    duration,
                    easing,
                )
            ),
            manager.add(
                _keyframe_animation(
                    self.left_leg,
                    "rotation",
                    [-self.leg_swing, self.leg_swing, -self.leg_swing],
                    duration,
                    easing,
                )
            ),
            manager.add(
                _keyframe_animation(
                    self.right_leg,
                    "rotation",
                    [self.leg_swing, -self.leg_swing, self.leg_swing],
                    duration,
                    easing,
                )
            ),
        ]
        return animations

    def point(
        self,
        manager: AnimationManager,
        duration: float,
        arm: Literal["left", "right"] = "right",
        easing: EasingMode = "ease-out",
    ) -> list[Animation]:
        """Animate the figure into a pointing pose."""
        active_arm = self.right_arm if arm == "right" else self.left_arm
        other_arm = self.left_arm if arm == "right" else self.right_arm
        target_angle = -75.0 if arm == "right" else 75.0
        return [
            manager.add(_keyframe_animation(active_arm, "rotation", [active_arm.rotation, target_angle], duration, easing)),
            manager.add(_keyframe_animation(other_arm, "rotation", [other_arm.rotation, 0.0], duration, easing)),
        ]

    def wave(
        self,
        manager: AnimationManager,
        duration: float,
        arm: Literal["left", "right"] = "right",
        easing: EasingMode = "ease-in-out",
    ) -> list[Animation]:
        """Animate a waving motion with repeated keyframes."""
        active_arm = self.right_arm if arm == "right" else self.left_arm
        start_angle = active_arm.rotation
        return [
            manager.add(
                _keyframe_animation(
                    active_arm,
                    "rotation",
                    [start_angle, start_angle - 30.0, start_angle + 20.0, start_angle - 25.0, start_angle],
                    duration,
                    easing,
                )
            )
        ]

    def think(self, manager: AnimationManager, duration: float) -> list[Animation]:
        """Animate a thinking pose."""
        return self.point(manager, duration, arm="right")

    def celebrate(self, manager: AnimationManager, duration: float) -> list[Animation]:
        """Animate a celebration pose."""
        return [
            manager.add(_keyframe_animation(self.left_arm, "rotation", [0.0, -150.0, 0.0], duration, "ease-in-out")),
            manager.add(_keyframe_animation(self.right_arm, "rotation", [0.0, -150.0, 0.0], duration, "ease-in-out")),
        ]

    def idle(self, manager: AnimationManager, duration: float) -> list[Animation]:
        """Animate an idle pose."""
        return [
            manager.add(_keyframe_animation(self.head, "rotation", [0.0, 5.0, -5.0, 0.0], duration, "linear")),
        ]

    def enter(self, manager: AnimationManager, duration: float) -> list[Animation]:
        """Animate entering the scene."""
        self.opacity = 0.0
        return [
            manager.animate(self, "opacity", 0.0, 1.0, duration, easing="ease-in"),
        ]

    def exit(self, manager: AnimationManager, duration: float) -> list[Animation]:
        """Animate exiting the scene."""
        return [
            manager.animate(self, "opacity", 1.0, 0.0, duration, easing="ease-out"),
        ]
