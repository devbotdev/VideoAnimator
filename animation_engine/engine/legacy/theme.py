from dataclasses import dataclass, field
from typing import Dict

@dataclass
class Theme:
    """Theming information for engine objects."""
    name: str
    background_color: str = "#ffffff"
    foreground_color: str = "#222222"
    semantic_palette: Dict[str, str] = field(default_factory=lambda: {
        "primary": "#007bff",
        "secondary": "#6c757d",
        "success": "#28a745",
        "danger": "#dc3545",
        "warning": "#ffc107",
        "info": "#17a2b8"
    })
    font_family: str = "sans-serif"
    typography_scale: Dict[str, float] = field(default_factory=lambda: {
        "small": 10.0,
        "medium": 14.0,
        "large": 20.0,
        "xlarge": 28.0
    })
    stroke_width: float = 2.0
    spacing_scale: Dict[str, float] = field(default_factory=lambda: {
        "small": 4.0,
        "medium": 8.0,
        "large": 16.0,
        "xlarge": 32.0
    })

LIGHT_THEME = Theme(
    name="light",
    background_color="#ffffff",
    foreground_color="#222222",
)

DARK_THEME = Theme(
    name="dark",
    background_color="#222222",
    foreground_color="#ffffff",
    semantic_palette={
        "primary": "#0d6efd",
        "secondary": "#6c757d",
        "success": "#198754",
        "danger": "#dc3545",
        "warning": "#ffc107",
        "info": "#0dcaf0"
    }
)
