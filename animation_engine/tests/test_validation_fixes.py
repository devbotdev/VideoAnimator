
import sys
from pathlib import Path
import pytest

# Add animation_engine to path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.objects import Circle
from engine.converter import plan_to_scene_manager
from engine.schema import Plan

def create_base_plan(objects):
    return Plan.from_dict({
        "version": "1.0",
        "title": "Test Plan",
        "resolution": {"width": 1920, "height": 1080},
        "fps": 30,
        "theme": "default",
        "scenes": [
            {
                "id": "scene1",
                "duration": 1.0,
                "background": "#ffffff",
                "objects": objects,
                "actions": []
            }
        ]
    })

def test_invalid_properties_rejected():
    # Test that invalid properties cause a ValueError
    objects = [
        {
            "id": "circle1",
            "type": "Circle",
            "properties": {"pos_x": 100}, # 'pos_x' is invalid
            "style": {}
        }
    ]
    plan = create_base_plan(objects)
    with pytest.raises(ValueError, match="Invalid properties for Circle: \['pos_x'\]"):
        plan_to_scene_manager(plan)

def test_valid_circle_renders():
    # Test that a valid circle is accepted and rendered
    objects = [
        {
            "id": "circle1",
            "type": "Circle",
            "properties": {"x": 100, "y": 100, "radius": 50},
            "style": {"fill_color": "#ff0000"}
        }
    ]
    plan = create_base_plan(objects)
    manager = plan_to_scene_manager(plan)
    
    scene = manager.scenes[0]
    circle = scene.object("circle1")
    
    assert isinstance(circle, Circle)
    assert circle.x == 100
    assert circle.y == 100
    assert circle.radius == 50
    assert circle.style.fill_color == "#ff0000"

if __name__ == "__main__":
    pytest.main([__file__])
