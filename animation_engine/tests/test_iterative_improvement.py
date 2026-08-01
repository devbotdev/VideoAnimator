import pytest
from unittest.mock import MagicMock, patch
from animation_engine.pipeline.orchestrator import PipelineContext
from animation_engine.pipeline.iterative_improvement import IterativeImprovementStage
from animation_engine.ai.connection import AIConnection
from animation_engine.engine.action_registry import ActionRegistry
from animation_engine.engine.schema import Plan

@pytest.fixture
def mock_deps():
    mock_ai = MagicMock(spec=AIConnection)
    mock_registry = MagicMock(spec=ActionRegistry)
    
    # Setup translate to return a basic engine plan
    mock_ai.translate_to_engine_schema.return_value = {
        "version": "1.0",
        "title": "Test",
        "resolution": {"width": 1920, "height": 1080},
        "fps": 30,
        "theme": "default",
        "scenes": []
    }
    
    return mock_ai, mock_registry

@patch("animation_engine.pipeline.iterative_improvement.Plan")
def test_iterative_improvement_stops_when_good_enough(mock_plan, mock_deps):
    mock_ai, mock_registry = mock_deps
    
    # Mock Plan.from_dict
    mock_plan_instance = MagicMock(spec=Plan)
    mock_plan_instance.scenes = []
    mock_plan.from_dict.return_value = mock_plan_instance
    
    initial_plan = {"title": "Test Plan"}
    
    # Setup mock feedback to be good immediately
    mock_feedback = {
        "clarity_score": 8,
        "educational_effectiveness_score": 8,
        "visual_storytelling_score": 8,
        "timing_score": 8,
        "overall_recommendation": "Perfect."
    }
    
    mock_ai.review_plan.return_value = mock_feedback
    
    # Context
    context = PipelineContext()
    context.set("animation_plan", initial_plan)
    
    # Stage
    stage = IterativeImprovementStage(mock_ai, mock_registry, max_iterations=3)
    stage.run(context)
    
    # Assertions
    assert context.get("final_animation_plan") == initial_plan
    assert mock_ai.review_plan.call_count == 1
    assert mock_ai.translate_to_engine_schema.call_count == 1
