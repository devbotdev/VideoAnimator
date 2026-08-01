"""Predefined reusable assets."""

from dataclasses import dataclass, field
from .objects import Group, Rectangle, Line, Style
from .animation import Animation, AnimationManager, _keyframe_animation

@dataclass
class Computer(Group):
    """A simple computer/workstation asset."""
    width: float = 100.0
    height: float = 60.0
    
    def __post_init__(self) -> None:
        super().__post_init__()
        
        style = Style(stroke_color="#222222", stroke_width=2.0, fill_color="white")
        
        # Screen
        self.screen = Rectangle(width=self.width, height=self.height, style=style)
        # Stand
        stand = Rectangle(width=self.width * 0.2, height=self.height * 0.3, style=style)
        stand.move_to(self.width * 0.4, self.height)
        
        self.extend([self.screen, stand])

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
        
        style = Style(stroke_color="#222222", stroke_width=2.0, fill_color="white")
        
        self.page = Rectangle(width=self.width, height=self.height, style=style)
        self.page.scale = 0.0
        
        self.extend([self.page])
        
    def reveal(self, manager: AnimationManager, duration: float) -> Animation:
        """Animate a document reveal."""
        return manager.animate(self.page, "scale", 0.0, 1.0, duration, easing="ease-out")
