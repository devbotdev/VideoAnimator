from __future__ import annotations

import pytest
from engine.scene import Scene, SceneManager
from engine.transition import FadeTransition, SlideTransition, WipeTransition
from engine.objects import BaseObject
from copy import deepcopy

def test_scene_lifecycle_hooks() -> None:
    calls: list[str] = []

    class LifecycleScene(Scene):
        def on_enter(self) -> None:
            calls.append("enter")
        def on_update(self, delta_time: float) -> None:
            calls.append("update")
        def on_exit(self) -> None:
            calls.append("exit")

    manager = SceneManager()
    s1 = LifecycleScene(name="s1", duration=1.0)
    s2 = LifecycleScene(name="s2", duration=1.0)
    manager.add_scene(s1)
    manager.add_scene(s2)

    # Initial add_scene should call on_enter for the first scene
    assert calls == ["enter"]

    manager.update(0.5)
    assert "update" in calls

    # Manually transition
    manager.transition_to(1)
    # Transition should call on_enter for the new scene
    assert "enter" in calls[1:] 

    manager.update(1.0) # Complete transition
    # Should call on_exit for s1 and s2's enter was already called
    assert "exit" in calls

def test_automatic_scene_sequencing() -> None:
    manager = SceneManager()
    s1 = Scene(name="s1", duration=1.0)
    s2 = Scene(name="s2", duration=1.0)
    manager.add_scene(s1)
    manager.add_scene(s2)

    assert manager.active_index == 0
    manager.update(1.5) # Trigger transition to s2
    
    # Should be in transition
    assert manager.transition is not None
    assert manager.transition_target_index == 1
    
    manager.update(1.0) # Finish transition
    assert manager.active_index == 1

def test_transition_returns_valid_frame() -> None:
    manager = SceneManager()
    s1 = Scene(name="s1")
    s2 = Scene(name="s2")
    s1.add(BaseObject(x=0))
    s2.add(BaseObject(x=100))
    manager.add_scene(s1)
    manager.add_scene(s2)
    
    manager.transition_to(1, transition=FadeTransition(duration=1.0))
    
    frame = manager.frame()
    assert len(frame.objects) == 2 # 1 from each scene

def test_transition_non_destructive() -> None:
    manager = SceneManager()
    s1 = Scene(name="s1")
    s2 = Scene(name="s2")
    obj1 = BaseObject(x=0, opacity=1.0)
    obj2 = BaseObject(x=100, opacity=1.0)
    s1.add(obj1)
    s2.add(obj2)
    manager.add_scene(s1)
    manager.add_scene(s2)
    
    # Store original state
    orig_obj1_x = obj1.x
    orig_obj1_opacity = obj1.opacity
    orig_obj2_x = obj2.x
    orig_obj2_opacity = obj2.opacity
    
    manager.transition_to(1, transition=FadeTransition(duration=1.0))
    
    # Take a frame mid-transition
    manager.update(0.5)
    manager.frame()
    
    # Check if original objects are untouched
    assert obj1.x == orig_obj1_x
    assert obj1.opacity == orig_obj1_opacity
    assert obj2.x == orig_obj2_x
    assert obj2.opacity == orig_obj2_opacity

def test_different_transitions() -> None:
    manager = SceneManager()
    s1 = Scene(name="s1")
    s2 = Scene(name="s2")
    s3 = Scene(name="s3")
    manager.add_scene(s1)
    manager.add_scene(s2)
    manager.add_scene(s3)
    
    manager.transition_to(1, transition=SlideTransition(duration=1.0, direction="left"))
    assert isinstance(manager.transition, SlideTransition)
    
    manager.update(1.0) # Finish transition
    assert manager.active_index == 1
    
    manager.transition_to(2, transition=WipeTransition(duration=1.0))
    assert isinstance(manager.transition, WipeTransition)
