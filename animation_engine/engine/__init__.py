"""Animation engine package."""

from .animation import Animation, AnimationCallback, AnimationManager, EasingMode, Keyframe
from .ai import AIActionSpec, AIEngine, AIPlan, ActionRegistry, SceneRegistry, register_default_action_handlers
from .canvas import SVGCanvas
from .camera import Camera
from .objects import Arrow, BaseObject, Circle, Group, Line, Rectangle, Style, Text, Polyline, Path
from .charts import BarChart, LineChart, PieChart, Callout
from .renderer import RenderConfig, RenderDependencyError, SVGRenderer
from .scene import Scene, SceneManager
from .stick_figure import StickFigure
from .timeline import Timeline
from .transition import FadeTransition, SceneFrame
from .registry import AssetRegistry
from .assets import Computer, Book

__all__ = [
    "Animation",
    "AnimationCallback",
    "AnimationManager",
    "AIActionSpec",
    "AIEngine",
    "AIPlan",
    "ActionRegistry",
    "Arrow",
    "BaseObject",
    "BarChart",
    "Callout",
    "Circle",
    "Camera",
    "EasingMode",
    "FadeTransition",
    "Group",
    "Line",
    "LineChart",
    "Keyframe",
    "Path",
    "PieChart",
    "Polyline",
    "Scene",
    "SceneFrame",
    "SceneManager",
    "SceneRegistry",
    "SVGCanvas",
    "Rectangle",
    "RenderConfig",
    "RenderDependencyError",
    "Style",
    "Timeline",
    "StickFigure",
    "SVGRenderer",
    "register_default_action_handlers",
    "Text",
    "AssetRegistry",
    "Computer",
    "Book",
]
