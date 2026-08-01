import pytest
from unittest.mock import MagicMock
from animation_engine.pipeline.orchestrator import PipelineContext
from animation_engine.review.reviewer import Reviewer
from animation_engine.ai.connection import AIConnection

def test_reviewer_provides_feedback():
    # Mock AI connection
    mock_ai = MagicMock(spec=AIConnection)
    mock_plan = {
        "title": "Test Animation",
        "scenes": [
            {"id": "s1", "duration": 10, "objects": [], "actions": []}
        ]
    }
    mock_feedback = {
        "clarity_score": 8,
        "clarity_feedback": "Clear explanation.",
        "educational_effectiveness_score": 9,
        "educational_effectiveness_feedback": "Well-structured.",
        "visual_storytelling_score": 7,
        "visual_storytelling_feedback": "Good visuals.",
        "timing_score": 9,
        "timing_feedback": "Good pacing.",
        "missing_explanations": [],
        "overall_recommendation": "Looks good."
    }
    mock_ai.review_plan.return_value = mock_feedback
    
    # Context
    context = PipelineContext()
    context.set("animation_plan", mock_plan)
    
    # Reviewer
    reviewer = Reviewer(mock_ai)
    reviewer.run(context)
    
    # Assertions
    assert context.get("review_feedback") == mock_feedback
    mock_ai.review_plan.assert_called_once_with(mock_plan)
