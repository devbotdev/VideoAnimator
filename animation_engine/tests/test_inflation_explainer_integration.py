import pytest
from pathlib import Path
import json
import numpy as np
from unittest.mock import MagicMock
from engine.scene import SceneManager
from engine.renderer import SVGRenderer, RenderConfig
from engine.schema import Plan
from engine.action_registry import ActionRegistry
from examples.inflation_explainer import create_scene_from_spec

def test_inflation_explainer_integration(monkeypatch):
    # Mock svg_to_image
    monkeypatch.setattr(SVGRenderer, "svg_to_image", lambda self, markup: np.zeros((72, 128, 3), dtype=np.uint8))

    # Load and validate plan
    plan_path = Path("examples/inflation_plan.json")
    with open(plan_path, "r") as f:
        data = json.load(f)
    
    plan = Plan.from_dict(data)
    registry = ActionRegistry()
    registry.populate_defaults()
    
    # Validation should pass
    plan.validate(registry)
    
    # Build scenes
    manager = SceneManager()
    for scene_spec in plan.scenes:
        manager.add_scene(create_scene_from_spec(scene_spec))
        
    # Set low resolution for test
    config = RenderConfig(
        width=128,
        height=72,
        fps=10,
        enable_progress_reporting=False
    )
    renderer = SVGRenderer(config=config)
    
    # Render only a few frames
    total_duration = sum(s.duration for s in plan.scenes)
    # Just render the first second
    frames = renderer.render_scene(manager.current_scene, duration=1.0)
    
    assert len(frames) > 0
    assert frames[0].shape == (72, 128, 3) # RGB
