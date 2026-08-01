import pytest
from unittest.mock import MagicMock
from animation_engine.pipeline.orchestrator import PipelineContext
from animation_engine.director.story_architect import StoryArchitect
from animation_engine.ai.connection import AIConnection

def test_story_architect_generates_structure():
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
    mock_narrative = {
        "title": "Test Animation",
        "intro_hook": "Hook to testing.",
        "progression": ["Beat 1", "Beat 2"],
        "conclusion": "Final test."
    }
    mock_ai.generate_narrative_structure.return_value = mock_narrative
    
    # Context
    context = PipelineContext()
    context.set("creative_brief", mock_brief)
    
    # Architect
    architect = StoryArchitect(mock_ai)
    architect.run(context)
    
    # Assertions
    assert context.get("narrative_structure") == mock_narrative
    mock_ai.generate_narrative_structure.assert_called_once_with(mock_brief)
