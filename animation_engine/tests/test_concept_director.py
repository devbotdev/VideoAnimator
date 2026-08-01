import pytest
from unittest.mock import MagicMock
from animation_engine.pipeline.orchestrator import PipelineContext
from animation_engine.director.concept_director import ConceptDirector
from animation_engine.ai.connection import AIConnection

def test_concept_director_generates_brief():
    # Mock AI connection
    mock_ai = MagicMock(spec=AIConnection)
    mock_brief = {
        "title": "Test Animation",
        "core_narrative": "A test narrative.",
        "educational_goal": "Understand testing.",
        "target_audience": "Developers",
        "visual_metaphor": "A blueprint.",
        "scene_outline": ["Scene 1: Introduction", "Scene 2: Explanation"]
    }
    mock_ai.generate_creative_brief.return_value = mock_brief
    
    # Context
    context = PipelineContext()
    
    # Director
    director = ConceptDirector(mock_ai, "Test idea")
    director.run(context)
    
    # Assertions
    assert context.get("creative_brief") == mock_brief
    mock_ai.generate_creative_brief.assert_called_once_with("Test idea")
