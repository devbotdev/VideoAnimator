from ..pipeline.orchestrator import PipelineContext
from ..ai.connection import AIConnection
from ..director.concept_director import ConceptDirector
from ..director.story_architect import StoryArchitect
from ..director.visual_metaphor_designer import VisualMetaphorDesigner
from ..director.storyboard_artist import StoryboardArtist
from ..director.animation_planner import AnimationPlanner

class CreativePipeline:
    def __init__(self, ai_connection: AIConnection):
        self.stages = [
            StoryArchitect(ai_connection),
            ConceptDirector(ai_connection, "default"), # Need an idea here, though it's set in the workflow before this
            VisualMetaphorDesigner(ai_connection),
            StoryboardArtist(ai_connection),
            AnimationPlanner(ai_connection)
        ]
        self.stage_outputs = {
            "StoryArchitect": "narrative_structure",
            "ConceptDirector": "creative_brief",
            "VisualMetaphorDesigner": "visual_concept",
            "StoryboardArtist": "storyboard_sequence",
            "AnimationPlanner": "animation_plan"
        }

    def run(self, context: PipelineContext) -> None:
        for stage in self.stages:
            stage.run(context)
            key = self.stage_outputs.get(stage.name)
            if key:
                context.save_debug_data(stage.name, context.get(key))
