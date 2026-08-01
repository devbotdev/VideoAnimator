import pytest
from unittest.mock import MagicMock
from animation_engine.pipeline.orchestrator import PipelineContext
from animation_engine.director.storyboard_artist import StoryboardArtist
from animation_engine.ai.connection import AIConnection

def test_storyboard_artist_generates_sequence():
    # Mock AI connection
    mock_ai = MagicMock(spec=AIConnection)
    mock_visual_concept = {
        "title": "Test Animation",
        "metaphor_description": "A blueprint representation.",
        "visual_elements": ["Nodes", "Connections"],
        "symbolic_representation": "Nodes are tests.",
        "why_it_works": "Clear mapping."
    }
    mock_storyboard = {
        "title": "Test Animation",
        "shots": [
            {
                "scene_number": 1,
                "purpose": "Introduce test.",
                "camera_intention": "Wide shot.",
                "visual_focus": "Blueprint.",
                "transition_description": "Fade."
            }
        ]
    }
    mock_ai.generate_storyboard.return_value = mock_storyboard
    
    # Context
    context = PipelineContext()
    context.set("visual_concept", mock_visual_concept)
    
    # Artist
    artist = StoryboardArtist(mock_ai)
    artist.run(context)
    
    # Assertions
    assert context.get("storyboard_sequence") == mock_storyboard
    mock_ai.generate_storyboard.assert_called_once_with(mock_visual_concept)
