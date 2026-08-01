import pytest
from unittest.mock import MagicMock
from animation_engine.pipeline.orchestrator import PipelineContext
from animation_engine.pipeline.complete_workflow import CompleteWorkflow
from animation_engine.ai.connection import AIConnection
from animation_engine.engine.action_registry import ActionRegistry
from animation_engine.engine.schema import Plan
from animation_engine.engine.renderer import SVGRenderer, RenderConfig

# --- Mocking Setup ---

class MockAIConnection:
    """A mock AI connection that returns predefined valid structures."""
    
    def generate_creative_brief(self, idea): return {"topic": idea}
    def generate_narrative_structure(self, brief): return {"narrative": "Test narrative"}
    def generate_visual_concept(self, narrative): return {"concept": "Test concept"}
    def generate_storyboard(self, concept): return {"storyboard": "Test storyboard"}
    def generate_animation_plan(self, storyboard): return {"animation": "Test animation"}
    def review_plan(self, plan): 
        return {
            "clarity_score": 10, 
            "educational_effectiveness_score": 10,
            "visual_storytelling_score": 10,
            "timing_score": 10,
            "overall_recommendation": "Accept"
        }
    
    def improve_plan(self, plan, feedback): return plan
    def repair_plan(self, plan, error): return plan
    
    def translate_to_engine_schema(self, animation_plan):
        return {
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
                        {"start_time": 0.0, "duration": 1.0, "target_id": "rect1", "action": "move", "parameters": {"x": 50.0, "y": 50.0, "duration": 1.0}}
                    ]
                }
            ]
        }

# --- Tests ---

def test_full_pipeline_end_to_end_with_mocks():
    # 1. Setup
    mock_ai = MockAIConnection()
    
    registry = ActionRegistry()
    registry.populate_defaults()
    
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
    
    assert renderer.config.width == engine_plan.resolution["width"]
    assert renderer.config.height == engine_plan.resolution["height"]
    assert renderer.config.fps == engine_plan.fps
