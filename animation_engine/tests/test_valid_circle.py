
import sys
from pathlib import Path

# Add animation_engine to path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.objects import Circle
from engine.converter import plan_to_scene_manager
from engine.schema import Plan

def test_valid_circle():
    # Correct properties
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
                        "properties": {"x": 100, "y": 100, "radius": 50},
                        "style": {"fill_color": "#ff0000"}
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
    assert circle.x == 100
    assert circle.y == 100
    assert circle.radius == 50
    assert circle.style.fill_color == "#ff0000"
    print("Test passed: Valid circle constructed correctly.")

if __name__ == "__main__":
    test_valid_circle()
