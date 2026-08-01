from ..pipeline.orchestrator import PipelineContext
from ..ai.connection import AIConnection
from .schema import CreativeBrief

class ConceptDirector:
    def __init__(self, ai_connection: AIConnection, idea: str):
        self.name = "ConceptDirector"
        self.ai_connection = ai_connection
        self.idea = idea

    def run(self, context: PipelineContext) -> None:
        """Process the idea into a creative brief and add it to context."""
        brief = self.ai_connection.generate_creative_brief(self.idea)
        context.set("creative_brief", brief)
