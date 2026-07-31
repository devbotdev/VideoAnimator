import pytest
from engine.schema import Plan

def test_valid_plan():
    data = {
        "version": "1.0",
        "title": "Valid Plan",
        "resolution": {"width": 1920, "height": 1080},
        "fps": 30,
        "theme": "default",
        "scenes": [
            {
                "id": "scene1",
                "duration": 1.0,
                "objects": [
                    {"id": "obj1", "type": "Rectangle", "properties": {"width": 10, "height": 10}}
                ]
            }
        ]
    }
    plan = Plan.from_dict(data)
    assert plan.version == "1.0"
    assert len(plan.scenes) == 1
    assert plan.scenes[0].id == "scene1"
    assert len(plan.scenes[0].objects) == 1

def test_invalid_object_type():
    data = {
        "version": "1.0",
        "title": "Invalid Plan",
        "resolution": {"width": 1920, "height": 1080},
        "fps": 30,
        "theme": "default",
        "scenes": [
            {
                "id": "scene1",
                "duration": 1.0,
                "objects": [
                    {"id": "obj1", "type": "InvalidType", "properties": {}}
                ]
            }
        ]
    }
    with pytest.raises(ValueError, match="Object type 'InvalidType' is not allowed."):
        Plan.from_dict(data)

def test_invalid_action():
    data = {
        "version": "1.0",
        "title": "Invalid Plan",
        "resolution": {"width": 1920, "height": 1080},
        "fps": 30,
        "theme": "default",
        "scenes": [
            {
                "id": "scene1",
                "duration": 1.0,
                "actions": [
                    {"start_time": 0.0, "duration": 1.0, "target_id": "obj1", "action": "fly"}
                ]
            }
        ]
    }
    with pytest.raises(ValueError, match="Action 'fly' is not allowed."):
        Plan.from_dict(data)
