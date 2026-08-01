from __future__ import annotations

from engine.animation import AnimationManager
from engine.converter import plan_to_scene_manager
from engine.objects import Rectangle
from engine.schema import Plan


def test_plan_to_scene_manager_applies_relative_move_actions() -> None:
    plan = Plan.from_dict(
        {
            "version": "1.0",
            "title": "Relative movement",
            "resolution": {"width": 1920, "height": 1080},
            "fps": 30,
            "theme": "default",
            "scenes": [
                {
                    "id": "scene1",
                    "duration": 2.0,
                    "background": "#ffffff",
                    "objects": [
                        {"id": "rect1", "type": "Rectangle", "properties": {"x": 10, "y": 20, "width": 40, "height": 20}}
                    ],
                    "actions": [
                        {
                            "start_time": 0.25,
                            "duration": 1.5,
                            "target_id": "rect1",
                            "action": "move",
                            "parameters": {"dx": 30, "dy": 40},
                        }
                    ],
                }
            ],
        }
    )

    manager = plan_to_scene_manager(plan)
    scene = manager.scenes[0]
    rect = scene.object("rect1")

    assert isinstance(rect, Rectangle)
    assert rect.x == 10.0
    assert rect.y == 20.0
    assert len(scene.animation_manager.animations) == 2

    x_animation = next(animation for animation in scene.animation_manager.animations if animation.property_name == "x")
    y_animation = next(animation for animation in scene.animation_manager.animations if animation.property_name == "y")

    assert x_animation.keyframes[0].value == 10.0
    assert x_animation.keyframes[-1].value == 40.0
    assert x_animation.delay == 0.25
    assert y_animation.keyframes[0].value == 20.0
    assert y_animation.keyframes[-1].value == 60.0
    assert y_animation.delay == 0.25


def test_action_registry_execute_supports_relative_move_and_start_time() -> None:
    from engine.action_registry import ActionRegistry

    manager = AnimationManager()
    target = Rectangle(x=5.0, y=7.0, width=10.0, height=10.0)
    registry = ActionRegistry()
    registry.populate_defaults()

    registry.execute("move", manager, target, {"dx": 15.0, "dy": 25.0, "duration": 1.0, "start_time": 0.5})

    assert len(manager.animations) == 2
    assert manager.animations[0].property_name == "x"
    assert manager.animations[0].keyframes[0].value == 5.0
    assert manager.animations[0].keyframes[-1].value == 20.0
    assert manager.animations[0].delay == 0.5
    assert manager.animations[1].property_name == "y"
    assert manager.animations[1].keyframes[0].value == 7.0
    assert manager.animations[1].keyframes[-1].value == 32.0
    assert manager.animations[1].delay == 0.5
