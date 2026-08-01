from ..pipeline.orchestrator import PipelineContext
from ..ai.connection import AIConnection
from .story_architect_schema import NarrativeStructure

class StoryArchitect:
    def __init__(self, ai_connection: AIConnection):
        self.name = "StoryArchitect"
        self.ai_connection = ai_connection

    def run(self, context: PipelineContext) -> None:
        """Transform creative brief into narrative structure and add to context."""
        brief = context.get("creative_brief")
        if not brief:
            raise ValueError("Missing 'creative_brief' in PipelineContext")
            
        narrative = self.ai_connection.generate_narrative_structure(brief)
        context.set("narrative_structure", narrative)
