from ..pipeline.orchestrator import PipelineContext
from ..ai.connection import AIConnection
from .storyboard_schema import StoryboardSequence

class StoryboardArtist:
    def __init__(self, ai_connection: AIConnection):
        self.name = "StoryboardArtist"
        self.ai_connection = ai_connection

    def run(self, context: PipelineContext) -> None:
        """Transform visual concept into storyboard sequence and add to context."""
        visual_concept = context.get("visual_concept")
        if not visual_concept:
            raise ValueError("Missing 'visual_concept' in PipelineContext")
            
        storyboard = self.ai_connection.generate_storyboard(visual_concept)
        context.set("storyboard_sequence", storyboard)
