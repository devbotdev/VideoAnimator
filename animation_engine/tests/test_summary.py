
import pytest
from engine.schema import Plan
from engine.action_registry import ActionRegistry

def test_plan_summary():
    data = {
        "version": "1.0",
        "title": "Test Plan",
        "resolution": {"width": 1920, "height": 1080},
        "fps": 30,
        "theme": "default",
        "scenes": [
            {
                "id": "scene1",
                "duration": 5.0,
                "objects": [
                    {"id": "obj1", "type": "Rectangle"}
                ],
                "actions": [
                    {"start_time": 0.0, "duration": 1.0, "target_id": "obj1", "action": "move", "parameters": {"x": 10.0, "y": 20.0, "duration": 1.0}}
                ]
            }
        ]
    }
    plan = Plan.from_dict(data)
    registry = ActionRegistry()
    registry.populate_defaults()
    
    summary = plan.summary(registry)
    
    assert summary["title"] == "Test Plan"
    assert summary["scenes"] == 1
    assert summary["total_duration"] == 5.0
    assert summary["total_actions"] == 1
    assert len(summary["unsupported_actions"]) == 0
