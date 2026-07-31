"""Animation engine package."""

from .animation import Animation, AnimationManager, EasingMode, Keyframe
from .ai import AIActionSpec, AIEngine, AIPlan, ActionRegistry, SceneRegistry, register_default_action_handlers
from .canvas import SVGCanvas
from .camera import Camera
from .objects import BaseObject, Circle, Line, Rectangle, Text
from .scene import Scene, SceneManager
from .stick_figure import StickFigure
from .timeline import Timeline
from .transition import FadeTransition, SceneFrame
from .renderer import SVGRenderer

__all__ = [
    "Animation",
    "AnimationManager",
    "AIActionSpec",
    "AIEngine",
    "AIPlan",
    "ActionRegistry",
    "BaseObject",
    "Circle",
    "Camera",
    "EasingMode",
    "FadeTransition",
    "Line",
    "Keyframe",
    "Scene",
    "SceneFrame",
    "SceneManager",
    "SceneRegistry",
    "SVGCanvas",
    "SVGRenderer",
    "Rectangle",
    "Timeline",
    "StickFigure",
    "register_default_action_handlers",
    "Text",
]
