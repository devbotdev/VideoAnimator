import pytest
from unittest.mock import MagicMock
from animation_engine.pipeline.orchestrator import PipelineContext
from animation_engine.director.visual_metaphor_designer import VisualMetaphorDesigner
from animation_engine.ai.connection import AIConnection

def test_visual_metaphor_designer_generates_concept():
    # Mock AI connection
    mock_ai = MagicMock(spec=AIConnection)
    mock_narrative = {
        "title": "Test Animation",
        "intro_hook": "Hook to testing.",
        "progression": ["Beat 1", "Beat 2"],
        "conclusion": "Final test."
    }
    mock_visual_concept = {
        "title": "Test Animation",
        "metaphor_description": "A blueprint representation.",
        "visual_elements": ["Nodes", "Connections"],
        "symbolic_representation": "Nodes are tests.",
        "why_it_works": "Clear mapping."
    }
    mock_ai.generate_visual_concept.return_value = mock_visual_concept
    
    # Context
    context = PipelineContext()
    context.set("narrative_structure", mock_narrative)
    
    # Designer
    designer = VisualMetaphorDesigner(mock_ai)
    designer.run(context)
    
    # Assertions
    assert context.get("visual_concept") == mock_visual_concept
    mock_ai.generate_visual_concept.assert_called_once_with(mock_narrative)
