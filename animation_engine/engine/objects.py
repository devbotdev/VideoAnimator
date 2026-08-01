"""Core object model for the animation engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Iterable

from .theme import Theme, DEFAULT_THEME

if TYPE_CHECKING:
    from .animation import Animation, AnimationCallback


@dataclass
class Style:
    """Reusable visual style information for engine objects.

    `fill_color`, `stroke_color`, and `stroke_width` default either to
    `DEFAULT_THEME`'s values or to the structural "none"/0.0 markers used
    by line-type shapes ("none"/0.0 are rendering keywords -- "no stroke"
    -- not colors a theme would ever supply differently, so they stay
    literal). `BaseObject.apply_theme()` compares a style's current value
    against these same `DEFAULT_THEME` values to detect whether it is
    still at its engine default and safe to re-theme, so a caller's
    explicit choices are always preserved.

    NOTE: `line_cap` / `line_join` are rendered by the (not editable here)
    SVGCanvas layer; this refactor sets them to "round" on line-type
    shapes for a softer, more contemporary stroke, assuming that plumbing
    already exists since the fields predate this change.
    """

    fill_color: str = DEFAULT_THEME.foreground_color
    stroke_color: str = "none"
    stroke_width: float = 0.0
    opacity: float = 1.0
    line_cap: str | None = None
    line_join: str | None = None

    def __post_init__(self) -> None:
        self.opacity = self._clamp_opacity(self.opacity)

    def __setattr__(self, name: str, value: Any) -> None:
        if name == "opacity":
            value = self._clamp_opacity(value)
        super().__setattr__(name, value)

    @staticmethod
    def _clamp_opacity(opacity: float) -> float:
        if not isinstance(opacity, (int, float)) or isinstance(opacity, bool):
            raise TypeError("Opacity must be numeric.")
        return max(0.0, min(1.0, float(opacity)))


@dataclass
class BaseObject:
    """Base class for all animatable objects."""

    x: float = 0.0
    y: float = 0.0
    rotation: float = 0.0
    scale: float = 1.0
    opacity: float = 1.0
    visibility: bool = True
    style: Style = field(default_factory=Style)

    def __post_init__(self) -> None:
        if self.opacity == 1.0 and self.style.opacity != 1.0:
            self.opacity = self.style.opacity
        else:
            self.opacity = self.opacity

    def __setattr__(self, name: str, value: Any) -> None:
        if name == "opacity":
            value = self._clamp_opacity(value)
            super().__setattr__(name, value)
            if hasattr(self, "style") and self.style is not None:
                self.style.opacity = value
            return
        super().__setattr__(name, value)

    @staticmethod
    def _clamp_opacity(opacity: float) -> float:
        if not isinstance(opacity, (int, float)) or isinstance(opacity, bool):
            raise TypeError("Opacity must be numeric.")
        return max(0.0, min(1.0, float(opacity)))

    @property
    def fill_color(self) -> str:
        return self.style.fill_color

    @fill_color.setter
    def fill_color(self, value: str) -> None:
        self.style.fill_color = value

    @property
    def stroke_color(self) -> str:
        return self.style.stroke_color

    @stroke_color.setter
    def stroke_color(self, value: str) -> None:
        self.style.stroke_color = value

    @property
    def stroke_width(self) -> float:
        return self.style.stroke_width

    @stroke_width.setter
    def stroke_width(self, value: float) -> None:
        self.style.stroke_width = value

    @property
    def line_cap(self) -> str | None:
        return self.style.line_cap

    @line_cap.setter
    def line_cap(self, value: str | None) -> None:
        self.style.line_cap = value

    @property
    def line_join(self) -> str | None:
        return self.style.line_join

    @line_join.setter
    def line_join(self, value: str | None) -> None:
        self.style.line_join = value

    def move_to(self, x: float, y: float) -> None:
        """Move the object to an absolute position."""
        self.x = x
        self.y = y

    def translate(self, dx: float, dy: float) -> None:
        """Move the object relative to its current position."""
        self.x += dx
        self.y += dy

    def set_rotation(self, rotation: float) -> None:
        """Set the rotation angle in degrees."""
        self.rotation = rotation

    def rotate_by(self, delta: float) -> None:
        """Adjust the rotation angle by a relative amount."""
        self.rotation += delta

    def set_scale(self, scale: float) -> None:
        """Set the uniform scale factor."""
        self.scale = scale

    def scale_by(self, factor: float) -> None:
        """Multiply the current scale by a factor."""
        self.scale *= factor

    def set_opacity(self, opacity: float) -> None:
        """Set the opacity value."""
        self.opacity = opacity

    def apply_theme(self, theme: Theme) -> None:
        """Resolve style values still at their engine defaults using `theme`.

        Objects fall into two kinds, distinguished by whether they have a
        fill:
        - Filled shapes (`fill_color != "none"`, e.g. Circle/Rectangle/
          Text/Path) inherit their fill from the theme's ink color and are
          left stroke-free, which keeps flat shapes calm and uncluttered.
        - Stroke-based shapes (`fill_color == "none"`, e.g. Line/Polyline/
          Arrow) inherit their stroke color and width instead.
        Either way, a value the caller has already customized away from
        the engine default is left untouched -- explicit choices always
        win over theme defaults.
        """
        if self.style.fill_color == "none":
            if self.style.stroke_color == DEFAULT_THEME.foreground_color:
                self.style.stroke_color = theme.foreground_color
            if self.style.stroke_width == DEFAULT_THEME.stroke_width:
                self.style.stroke_width = theme.stroke_width
        else:
            if self.style.fill_color == DEFAULT_THEME.foreground_color:
                self.style.fill_color = theme.foreground_color

    def animate(
        self,
        property_name: str,
        start_value: float,
        end_value: float,
        duration: float,
        easing: str = "linear",
        delay: float = 0.0,
        repeat: int | None = None,
        yoyo: bool = False,
        on_start: "AnimationCallback | None" = None,
        on_complete: "AnimationCallback | None" = None,
    ) -> Animation:
        """Create a keyframe animation for one of the object's properties."""
        from .animation import Animation

        return Animation.from_values(
            target=self,
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

    def show(self) -> None:
        """Make the object visible."""
        self.visibility = True

    def hide(self) -> None:
        """Hide the object."""
        self.visibility = False

    def update(self, delta_time: float) -> None:
        """Update the object's state for a simulation step."""

    def draw(self, canvas: Any) -> None:
        """Draw the object on a canvas placeholder."""
        raise NotImplementedError("Rendering is not implemented yet.")


@dataclass
class Circle(BaseObject):
    """Circular object definition."""

    radius: float = 50.0


@dataclass
class Rectangle(BaseObject):
    """Rectangular object definition."""

    width: float = 1.0
    height: float = 1.0
    corner_radius: float = 0.0

    def apply_theme(self, theme: Theme) -> None:
        super().apply_theme(theme)
        # Subtly rounded corners are a core part of the engine's modern,
        # minimalist look. Only touch it if the caller left it at the
        # engine default (0.0 == sharp corners); an explicit value always
        # wins. NOTE: this assumes the rendering layer (SVGCanvas, not
        # editable here) already maps `corner_radius` onto an SVG rect's
        # rx/ry -- that plumbing predates this refactor.
        if self.corner_radius == 0.0:
            self.corner_radius = theme.radius("small")


@dataclass
class Line(BaseObject):
    """Line object definition."""

    style: Style = field(
        default_factory=lambda: Style(
            fill_color="none",
            stroke_color=DEFAULT_THEME.foreground_color,
            stroke_width=DEFAULT_THEME.stroke_width,
            line_cap="round",
            line_join="round",
        )
    )
    end_x: float = 0.0
    end_y: float = 0.0


@dataclass
class Polyline(BaseObject):
    """Polyline object definition."""

    style: Style = field(
        default_factory=lambda: Style(
            fill_color="none",
            stroke_color=DEFAULT_THEME.foreground_color,
            stroke_width=DEFAULT_THEME.stroke_width,
            line_cap="round",
            line_join="round",
        )
    )
    points: list[tuple[float, float]] = field(default_factory=list)


@dataclass
class Path(BaseObject):
    """Path object definition."""

    style: Style = field(
        default_factory=lambda: Style(
            fill_color=DEFAULT_THEME.foreground_color,
            stroke_color="none",
            stroke_width=0.0,
        )
    )
    d: str = ""


@dataclass
class Text(BaseObject):
    """Text object definition."""

    content: str = ""
    font_size: float = DEFAULT_THEME.typography_scale["medium"]
    font_family: str = "sans-serif"
    font_weight: str = "normal"
    text_anchor: str = "start"
    text_alignment: str = "start"

    def apply_theme(self, theme: Theme) -> None:
        super().apply_theme(theme)
        if self.font_family == "sans-serif":
            self.font_family = theme.font_family
        if self.font_size == DEFAULT_THEME.typography_scale["medium"]:
            self.font_size = theme.font_size("medium")


@dataclass
class Group(BaseObject):
    """Composite object that groups children under a shared transform."""

    children: list[BaseObject] = field(default_factory=list)

    def add(self, child: BaseObject) -> BaseObject:
        """Add a child object to the group."""
        self.children.append(child)
        return child

    def extend(self, children: Iterable[BaseObject]) -> None:
        """Add multiple child objects to the group."""
        self.children.extend(children)

    def apply_theme(self, theme: Theme) -> None:
        super().apply_theme(theme)
        for child in self.children:
            child.apply_theme(theme)


@dataclass
class Arrow(BaseObject):
    """Line with an arrowhead."""

    style: Style = field(
        default_factory=lambda: Style(
            fill_color="none",
            stroke_color=DEFAULT_THEME.foreground_color,
            stroke_width=DEFAULT_THEME.stroke_width,
            line_cap="round",
            line_join="round",
        )
    )
    start_x: float = 0.0
    start_y: float = 0.0
    end_x: float = 10.0
    end_y: float = 0.0
    arrowhead_size: float = 12.0
