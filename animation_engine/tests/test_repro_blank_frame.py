
import sys
from pathlib import Path
import pytest

# Add animation_engine to path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.objects import Circle
from engine.converter import plan_to_scene_manager
from engine.schema import Plan, SceneSpec, ObjectSpec

def test_circle_missing_required_properties():
    # Attempt to create a plan with a circle, but provide invalid property names 
    # that would be filtered out by the current implementation of plan_to_scene_manager.
    
    # "pos_x" and "pos_y" are not valid Circle properties (should be "x" and "y").
    # If filtered out, it might still render at default (0,0).
    
    plan_dict = {
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
                "objects": [
                    {
                        "id": "circle1",
                        "type": "Circle",
                        "properties": {"pos_x": 100, "pos_y": 100, "radius": 50},
                        "style": {"color": "#ff0000"}
                    }
                ],
                "actions": []
            }
        ]
    }
    
    plan = Plan.from_dict(plan_dict)
    manager = plan_to_scene_manager(plan)
    
    scene = manager.scenes[0]
    circle = scene.object("circle1")
    
    assert isinstance(circle, Circle)
    # With the current implementation, "pos_x" and "pos_y" are filtered out.
    # So the circle should be at (0, 0)
    print(f"Circle position: {circle.x}, {circle.y}")
    
    # We WANT this to fail if required properties are missing or misnamed,
    # but currently it might not.
    # The requirement is: "Implement fixes so invalid plans fail loudly instead of silently rendering blank frames."

if __name__ == "__main__":
    test_circle_missing_required_properties()
