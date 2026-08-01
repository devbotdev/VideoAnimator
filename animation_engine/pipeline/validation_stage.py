from ..pipeline.orchestrator import PipelineContext
from ..pipeline.plan_validator import PlanValidator
from ..engine.action_registry import ActionRegistry

class ValidationStage:
    def __init__(self, registry: ActionRegistry):
        self.name = "ValidationStage"
        self.validator = PlanValidator(registry)

    def run(self, context: PipelineContext) -> None:
        plan = context.get("engine_plan")
        if not plan:
            raise ValueError("Missing 'engine_plan' in PipelineContext")
            
        errors = self.validator.validate(plan)
        if errors:
            error_messages = "\n".join([f"- Scene {e.scene_id}: {e.message}" for e in errors])
            raise ValueError(f"Plan validation failed:\n{error_messages}")
