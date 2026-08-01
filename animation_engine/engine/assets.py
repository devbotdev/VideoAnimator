"""Predefined reusable assets."""

from dataclasses import dataclass
from .objects import Group, Rectangle, Style
from .theme import Theme, DEFAULT_THEME
from .animation import Animation, AnimationManager


@dataclass
class Computer(Group):
    """A simple, minimal computer/workstation asset: a flat monitor on a
    small stand, both rendered as the theme's surface color with a thin
    ink outline and gently rounded corners."""

    width: float = 100.0
    height: float = 60.0

    def __post_init__(self) -> None:
        super().__post_init__()

        def body_style() -> Style:
            # A fresh Style instance per part -- screen and stand must stay
            # independently themeable, not share one mutable object.
            return Style(
                stroke_color=DEFAULT_THEME.foreground_color,
                stroke_width=DEFAULT_THEME.stroke_width,
                fill_color=DEFAULT_THEME.background_color,
            )

        self.screen = Rectangle(
            width=self.width,
            height=self.height,
            style=body_style(),
            corner_radius=DEFAULT_THEME.radius("small"),
        )
        self.stand = Rectangle(
            width=self.width * 0.2,
            height=self.height * 0.3,
            style=body_style(),
            corner_radius=DEFAULT_THEME.radius("small"),
        )
        self.stand.move_to(self.width * 0.4, self.height)

        self.extend([self.screen, self.stand])

    def apply_theme(self, theme: Theme) -> None:
        """The monitor and stand act as the device's "body": their fill
        represents a surface, not text ink, so map them explicitly rather
        than relying on BaseObject's generic ink-fill rule."""
        super().apply_theme(theme)
        for part in (self.screen, self.stand):
            part.style.fill_color = theme.background_color
            part.style.stroke_color = theme.foreground_color
            part.style.stroke_width = theme.stroke_width

    def screen_glow(self, manager: AnimationManager, duration: float) -> Animation:
        """Animate a screen glow effect."""
        return manager.animate(self.screen, "opacity", 0.5, 1.0, duration, yoyo=True, repeat=2)


@dataclass
class Book(Group):
    """A simple book/document asset."""

    width: float = 40.0
    height: float = 50.0

    def __post_init__(self) -> None:
        super().__post_init__()

        self.page = Rectangle(
            width=self.width,
            height=self.height,
            style=Style(
                stroke_color=DEFAULT_THEME.foreground_color,
                stroke_width=DEFAULT_THEME.stroke_width,
                fill_color=DEFAULT_THEME.background_color,
            ),
            corner_radius=DEFAULT_THEME.radius("small"),
        )
        self.page.scale = 0.0

        self.extend([self.page])

    def apply_theme(self, theme: Theme) -> None:
        """The page's fill represents a surface, not text ink, so map it
        explicitly rather than relying on BaseObject's generic ink-fill
        rule."""
        super().apply_theme(theme)
        self.page.style.fill_color = theme.background_color
        self.page.style.stroke_color = theme.foreground_color
        self.page.style.stroke_width = theme.stroke_width

    def reveal(self, manager: AnimationManager, duration: float) -> Animation:
        """Animate a document reveal."""
        return manager.animate(self.page, "scale", 0.0, 1.0, duration, easing="ease-out")
