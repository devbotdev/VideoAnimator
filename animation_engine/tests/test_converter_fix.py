from engine.converter import plan_to_scene_manager
from engine.objects import Circle
from engine.schema import Plan

def test_plan_to_scene_manager_maps_fill_to_style() -> None:
    plan = Plan.from_dict(
        {
            "version": "1.0",
            "title": "Fill test",
            "resolution": {"width": 1920, "height": 1080},
            "fps": 30,
            "theme": "default",
            "scenes": [
                {
                    "id": "scene1",
                    "duration": 2.0,
                    "background": "#ffffff",
                    "objects": [
                        {
                            "id": "circle1", 
                            "type": "Circle", 
                            "properties": {"x": 10, "y": 20, "radius": 40, "fill": "#ff0000"}
                        }
                    ],
                    "actions": [],
                }
            ],
        }
    )

    manager = plan_to_scene_manager(plan)
    scene = manager.scenes[0]
    circle = scene.object("circle1")

    assert isinstance(circle, Circle)
    assert circle.x == 10.0
    assert circle.y == 20.0
    assert circle.radius == 40.0
    assert circle.style.fill_color == "#ff0000"
