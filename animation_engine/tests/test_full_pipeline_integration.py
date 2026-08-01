import pytest
from unittest.mock import MagicMock
from pathlib import Path

from animation_engine.pipeline.orchestrator import PipelineContext
from animation_engine.pipeline.complete_workflow import CompleteWorkflow
from animation_engine.ai.connection import AIConnection
from animation_engine.engine.action_registry import ActionRegistry
from animation_engine.engine.schema import Plan
from animation_engine.engine.renderer import SVGRenderer, RenderConfig

def test_full_pipeline_to_renderer_compatibility():
    # 1. Setup
    mock_ai = MagicMock(spec=AIConnection)
    registry = ActionRegistry()
    registry.populate_defaults()
    
    # Define a valid minimal plan
    valid_plan_dict = {
        "version": "1.0",
        "title": "Test Animation",
        "resolution": {"width": 800, "height": 600},
        "fps": 30,
        "theme": "default",
        "scenes": [
            {
                "id": "scene1",
                "duration": 2.0,
                "background": "#ffffff",
                "objects": [
                    {"id": "rect1", "type": "Rectangle", "properties": {"width": 100.0, "height": 100.0}, "style": {"fill": "red"}}
                ],
                "actions": [
                    {"start_time": 0.0, "duration": 1.0, "target_id": "rect1", "action": "move", "parameters": {"duration": 1.0, "x": 50.0, "y": 50.0}}
                ]
            }
        ]
    }

    # Setup mocks
    mock_ai.generate_creative_brief.return_value = {"topic": "Test"}
    mock_ai.generate_narrative_structure.return_value = {"narrative": "..."}
    mock_ai.generate_visual_concept.return_value = {"concept": "..."}
    mock_ai.generate_storyboard.return_value = {"storyboard": "..."}
    mock_ai.generate_animation_plan.return_value = {"animation": "..."}
    mock_ai.review_plan.return_value = {
        "clarity_score": 9, "educational_effectiveness_score": 9,
        "visual_storytelling_score": 9, "timing_score": 9,
        "overall_recommendation": "Good"
    }
    mock_ai.translate_to_engine_schema.return_value = valid_plan_dict

    # 2. Run Pipeline
    context = PipelineContext()
    workflow = CompleteWorkflow(mock_ai, registry, "Test idea")
    workflow.run(context)

    # 3. Validation
    engine_plan = context.get("engine_plan")
    assert engine_plan is not None
    assert isinstance(engine_plan, Plan)
    
    # Ensure plan is valid according to registry
    engine_plan.validate(registry)
    
    # 4. Renderer Compatibility Check
    config = RenderConfig(
        width=engine_plan.resolution["width"],
        height=engine_plan.resolution["height"],
        fps=engine_plan.fps,
        output_format="mp4"
    )
    renderer = SVGRenderer(config=config)
    
    # Just verify renderer can be initialized and config matches plan
    assert renderer.config.width == 800
    assert renderer.config.height == 600
    
    # We don't run full render to avoid file I/O, but verify the schema is ready for it.
