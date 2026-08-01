from ..pipeline.orchestrator import PipelineContext
from ..ai.connection import AIConnection
from .animation_planner_schema import AnimationPlan
from .storyboard_schema import StoryboardSequence

class AnimationPlanner:
    def __init__(self, ai_connection: AIConnection):
        self.name = "AnimationPlanner"
        self.ai_connection = ai_connection

    def run(self, context: PipelineContext) -> None:
        """Transform storyboard sequence into an intermediate animation plan."""
        storyboard = context.get("storyboard_sequence")
        if not storyboard:
            raise ValueError("Missing 'storyboard_sequence' in PipelineContext")
            
        # For now, we use the AI connection to perform the mapping from storyboard to animation plan.
        # This is a simplification and assumes the connection has a method to generate a plan.
        # In reality, we might need a specific prompt.
        animation_plan = self.ai_connection.generate_animation_plan(storyboard)
        context.set("animation_plan", animation_plan)
