from ..pipeline.orchestrator import PipelineContext
from ..ai.connection import AIConnection
from .visual_metaphor_schema import VisualConcept

class VisualMetaphorDesigner:
    def __init__(self, ai_connection: AIConnection):
        self.name = "VisualMetaphorDesigner"
        self.ai_connection = ai_connection

    def run(self, context: PipelineContext) -> None:
        """Transform narrative structure into visual concept and add to context."""
        narrative = context.get("narrative_structure")
        if not narrative:
            raise ValueError("Missing 'narrative_structure' in PipelineContext")
            
        visual_concept = self.ai_connection.generate_visual_concept(narrative)
        context.set("visual_concept", visual_concept)
