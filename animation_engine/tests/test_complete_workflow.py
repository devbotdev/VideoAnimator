import pytest
from unittest.mock import MagicMock
from animation_engine.pipeline.orchestrator import PipelineContext
from animation_engine.pipeline.complete_workflow import CompleteWorkflow
from animation_engine.ai.connection import AIConnection
from animation_engine.engine.action_registry import ActionRegistry

def test_complete_workflow_end_to_end():
    import os
    import shutil

    debug_dir = "test_debug_output"
    if os.path.exists(debug_dir):
        shutil.rmtree(debug_dir)

    mock_ai = MagicMock(spec=AIConnection)
    mock_registry = MagicMock(spec=ActionRegistry)

    # Setup mocks for all steps
    mock_ai.generate_creative_brief.return_value = {"topic": "Photosynthesis"}
    mock_ai.generate_narrative_structure.return_value = {"narrative": "..."}
    mock_ai.generate_visual_concept.return_value = {"concept": "..."}
    mock_ai.generate_storyboard.return_value = {"storyboard": "..."}
    mock_ai.generate_animation_plan.return_value = {"animation": "..."}
    mock_ai.review_plan.return_value = {
        "clarity_score": 9,
        "educational_effectiveness_score": 9,
        "visual_storytelling_score": 9,
        "timing_score": 9,
        "overall_recommendation": "Perfect."
    }
    mock_ai.translate_to_engine_schema.return_value = {
        "version": "1.0",
        "title": "Photosynthesis",
        "resolution": {"width": 1920, "height": 1080},
        "fps": 30,
        "theme": "default",
        "scenes": []
    }

    context = PipelineContext(debug_enabled=True, debug_dir=debug_dir)
    workflow = CompleteWorkflow(mock_ai, mock_registry, "Explain photosynthesis")
    workflow.run(context)

    assert context.get("engine_plan") is not None
    assert context.get("engine_plan").title == "Photosynthesis"

    # Verify debug files
    expected_files = [
        "inputprompt.json",
        "conceptdirector.json",
        "storyarchitect.json",
        "visualmetaphordesigner.json",
        "storyboardartist.json",
        "animationplanner.json",
        "iterativeimprovementstage.json",
        "finalanimationplan.json",
        "schematranslator.json"
    ]

    for file in expected_files:
        assert os.path.exists(os.path.join(debug_dir, file)), f"Missing debug file: {file}"

    # Cleanup
    shutil.rmtree(debug_dir)

