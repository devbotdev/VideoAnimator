from ..pipeline.orchestrator import PipelineContext
from ..ai.connection import AIConnection

class Reviewer:
    def __init__(self, ai_connection: AIConnection):
        self.name = "Reviewer"
        self.ai_connection = ai_connection

    def run(self, context: PipelineContext) -> None:
        """Review animation plan and add feedback to context."""
        plan = context.get("animation_plan")
        if not plan:
            raise ValueError("Missing 'animation_plan' in PipelineContext")
            
        feedback = self.ai_connection.review_plan(plan)
        context.set("review_feedback", feedback)
