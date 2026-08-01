"""Theming information for the animation engine.

`theme.py` is the single source of truth for every visual default used
across the engine: surface/ink colors, the semantic and categorical
palettes, typography, stroke weight, spacing, and corner radii. Other
modules (`objects.py`, `charts.py`, `assets.py`, `stick_figure.py`) should
never hardcode a color, font, or stroke value directly -- they source their
dataclass-field defaults from the module-level `DEFAULT_THEME` instance
below, and `apply_theme()` implementations compare a style's current value
against that same `DEFAULT_THEME` value to tell whether it is still at its
engine default (and therefore safe to re-theme) or was explicitly set by a
caller (and therefore left alone).
"""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Theme:
    """A complete, self-contained design system for the animation engine.

    Tokens are grouped the way a small product design system usually is:
    a handful of surface/ink colors, a semantic palette for status colors,
    a categorical palette for data visualization, a type scale, a spacing
    scale, and a corner-radius scale. Component files look these up either
    directly (`theme.foreground_color`) or through the accessor methods
    below (`color`, `font_size`, `font_weight`, `spacing`, `radius`), which
    fall back gracefully instead of raising `KeyError` if a custom theme
    omits a token.
    """

    name: str

    # --- Surfaces & ink ---------------------------------------------------
    background_color: str = "#fafafa"
    # A slightly elevated surface for cards/panels drawn atop background_color.
    surface_color: str = "#ffffff"
    foreground_color: str = "#18181b"
    # Secondary ink for captions, axis labels, and other supporting text.
    muted_color: str = "#71717a"
    # Subtle dividers and hairlines between surfaces.
    border_color: str = "#e4e4e7"

    # --- Palettes -----------------------------------------------------
    semantic_palette: Dict[str, str] = field(default_factory=lambda: {
        "primary": "#4f46e5",
        "secondary": "#71717a",
        "success": "#16a34a",
        "danger": "#dc2626",
        "warning": "#d97706",
        "info": "#0891b2",
    })
    # A curated, harmonious sequence for multi-series data (bars, pie
    # slices, line series) -- distinct from semantic_palette so a chart's
    # third category doesn't accidentally read as a "danger" status color.
    categorical_palette: List[str] = field(default_factory=lambda: [
        "#4f46e5",  # indigo
        "#0891b2",  # cyan
        "#d97706",  # amber
        "#16a34a",  # emerald
        "#db2777",  # rose
        "#7c3aed",  # violet
    ])

    # --- Typography ---------------------------------------------------
    font_family: str = "'Inter', 'Helvetica Neue', Arial, sans-serif"
    typography_scale: Dict[str, float] = field(default_factory=lambda: {
        "small": 11.0,
        "medium": 14.0,
        "large": 20.0,
        "xlarge": 28.0,
    })
    font_weight_scale: Dict[str, str] = field(default_factory=lambda: {
        "regular": "400",
        "medium": "500",
        "semibold": "600",
        "bold": "700",
    })

    # --- Strokes, spacing, radii ---------------------------------------
    stroke_width: float = 1.5
    spacing_scale: Dict[str, float] = field(default_factory=lambda: {
        "small": 4.0,
        "medium": 8.0,
        "large": 16.0,
        "xlarge": 32.0,
    })
    corner_radius_scale: Dict[str, float] = field(default_factory=lambda: {
        "none": 0.0,
        "small": 6.0,
        "medium": 12.0,
        "large": 20.0,
        "full": 9999.0,
    })

    # --- Graceful accessors ---------------------------------------------
    def color(self, key: str) -> str:
        """Look up a semantic color by name, falling back to the ink color."""
        return self.semantic_palette.get(key, self.foreground_color)

    def font_size(self, key: str) -> float:
        """Look up a type-scale size by name, falling back to 'medium'."""
        return self.typography_scale.get(key, self.typography_scale.get("medium", 14.0))

    def font_weight(self, key: str) -> str:
        """Look up a font weight by name, falling back to 'regular'."""
        return self.font_weight_scale.get(key, self.font_weight_scale.get("regular", "400"))

    def spacing(self, key: str) -> float:
        """Look up a spacing token by name, falling back to 'medium'."""
        return self.spacing_scale.get(key, self.spacing_scale.get("medium", 8.0))

    def radius(self, key: str) -> float:
        """Look up a corner-radius token by name, falling back to sharp corners."""
        return self.corner_radius_scale.get(key, 0.0)


LIGHT_THEME = Theme(
    name="light",
    background_color="#fafafa",
    surface_color="#ffffff",
    foreground_color="#18181b",
    muted_color="#71717a",
    border_color="#e4e4e7",
)

DARK_THEME = Theme(
    name="dark",
    background_color="#121214",
    surface_color="#1c1c1f",
    foreground_color="#f4f4f5",
    muted_color="#a1a1aa",
    border_color="#27272a",
    semantic_palette={
        "primary": "#6366f1",
        "secondary": "#a1a1aa",
        "success": "#22c55e",
        "danger": "#ef4444",
        "warning": "#f59e0b",
        "info": "#22d3ee",
    },
    categorical_palette=[
        "#818cf8",  # indigo
        "#22d3ee",  # cyan
        "#fbbf24",  # amber
        "#4ade80",  # emerald
        "#f472b6",  # rose
        "#a78bfa",  # violet
    ],
)

# The engine's baseline theme. Other modules import this to source their
# dataclass-field defaults from Theme rather than hardcoding literal
# colors/fonts/stroke widths, and `apply_theme()` implementations compare a
# style's current value against the matching DEFAULT_THEME value to decide
# whether that value is still "unset" and safe to re-theme.
DEFAULT_THEME: Theme = LIGHT_THEME
