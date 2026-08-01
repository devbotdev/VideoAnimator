import pytest
from animation_engine.pipeline.visual_validator import VisualValidator
from animation_engine.engine.schema import Plan, SceneSpec, ObjectSpec, ActionSpec

def create_mock_plan(scenes):
    return Plan(
        version="1.0",
        title="Test Plan",
        resolution={"width": 1920, "height": 1080},
        fps=30,
        theme="light",
        scenes=scenes
    )

def test_valid_animation():
    scene = SceneSpec(
        id="scene1",
        duration=5.0,
        objects=[
            ObjectSpec(id="obj1", type="Rectangle", properties={"width": 100, "height": 100, "x": 100, "y": 100})
        ],
        actions=[
            ActionSpec(start_time=0.0, duration=1.0, target_id="obj1", action="move", parameters={"x": 200, "y": 200})
        ]
    )
    plan = create_mock_plan([scene])
    validator = VisualValidator(plan)
    results = validator.validate()
    assert results["valid"] is True
    assert len(results["errors"]) == 0

def test_object_outside_canvas():
    scene = SceneSpec(
        id="scene1",
        duration=5.0,
        objects=[
            ObjectSpec(id="obj1", type="Rectangle", properties={"width": 100, "height": 100, "x": 5000, "y": 5000})
        ]
    )
    plan = create_mock_plan([scene])
    validator = VisualValidator(plan)
    results = validator.validate()
    # Warning, not error
    assert results["valid"] is True
    assert len(results["warnings"]) > 0

def test_zero_size_object():
    scene = SceneSpec(
        id="scene1",
        duration=5.0,
        objects=[
            ObjectSpec(id="obj1", type="Rectangle", properties={"width": 0, "height": 100, "x": 100, "y": 100})
        ]
    )
    plan = create_mock_plan([scene])
    validator = VisualValidator(plan)
    results = validator.validate()
    assert results["valid"] is False
    assert len(results["errors"]) > 0

def test_empty_scene():
    scene = SceneSpec(id="scene1", duration=5.0, objects=[])
    plan = create_mock_plan([scene])
    validator = VisualValidator(plan)
    results = validator.validate()
    assert results["valid"] is True
    assert len(results["warnings"]) > 0

def test_stacked_objects():
    scene = SceneSpec(
        id="scene1",
        duration=5.0,
        objects=[
            ObjectSpec(id="obj1", type="Rectangle", properties={"width": 100, "height": 100, "x": 100, "y": 100}),
            ObjectSpec(id="obj2", type="Rectangle", properties={"width": 100, "height": 100, "x": 100, "y": 100})
        ]
    )
    plan = create_mock_plan([scene])
    validator = VisualValidator(plan)
    results = validator.validate()
    assert results["valid"] is True
    assert len(results["warnings"]) > 0
