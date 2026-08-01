from typing import List, Dict, Any
from dataclasses import dataclass
import logging
import json
from pathlib import Path

from ..pipeline.orchestrator import PipelineContext
from ..ai.connection import AIConnection
from ..engine.action_registry import ActionRegistry
from ..pipeline.plan_validator import PlanValidator
from ..engine.schema import Plan

logger = logging.getLogger("pipeline")

@dataclass
class IterationLog:
    iteration: int
    plan: Dict[str, Any]
    feedback: Dict[str, Any]
    validation_errors: List[str]

class IterativeImprovementStage:
    def __init__(self, ai_connection: AIConnection, registry: ActionRegistry, max_iterations: int = 3, output_dir: str = "animation_engine/output/intermediate"):
        self.name = "IterativeImprovementStage"
        self.ai_connection = ai_connection
        self.validator = PlanValidator(registry)
        self.max_iterations = max_iterations
        self.iteration_history: List[IterationLog] = []
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run(self, context: PipelineContext) -> None:
        plan = context.get("animation_plan")
        if not plan:
            raise ValueError("Missing 'animation_plan' in PipelineContext")

        self.iteration_history = []

        for i in range(self.max_iterations):
            logger.info(f"Starting iteration {i + 1}/{self.max_iterations}")

            # 1. Save intermediate
            self._save_plan(plan, i + 1)

            # 2. Review
            feedback = self.ai_connection.review_plan(plan)
            
            # 3. Check if good enough
            if self._is_good_enough(feedback):
                logger.info("Plan is good enough. Stopping iteration.")
                # Also do a final validation/translation before finishing
                final_plan = self._get_validated_plan(plan)
                context.set("final_animation_plan", plan)
                context.set("engine_plan", final_plan)
                break
                
            # 4. Improve
            logger.info(f"Improving plan based on feedback: {feedback.get('overall_recommendation')}")
            plan = self._improve_plan(plan, feedback)
            context.set("animation_plan", plan)

            # 5. Validate/Repair
            validation_errors = []
            try:
                final_plan = self._get_validated_plan(plan)
            except Exception as e:
                logger.warning(f"Plan validation failed: {e}. Attempting repair.")
                # Repair based on validation error
                plan = self.ai_connection.repair_plan(plan, str(e))
                validation_errors = [str(e)]
                context.set("animation_plan", plan)

            # Store history
            self.iteration_history.append(IterationLog(
                iteration=i + 1,
                plan=plan,
                feedback=feedback,
                validation_errors=validation_errors
            ))
            context.set("iteration_history", [log.__dict__ for log in self.iteration_history])

        context.set("final_animation_plan", plan)

    def _get_validated_plan(self, plan: Dict[str, Any]) -> Plan:
        # Translate
        engine_plan_dict = self.ai_connection.translate_to_engine_schema(plan)
        # Validate
        engine_plan = Plan.from_dict(engine_plan_dict)
        errors = self.validator.validate(engine_plan)
        if errors:
            raise ValueError("\n".join([f"- Scene {e.scene_id}: {e.message}" for e in errors]))
        return engine_plan

    def _save_plan(self, plan: Dict[str, Any], iteration: int) -> None:
        file_path = self.output_dir / f"iteration_{iteration}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(plan, f, indent=2)
        logger.info(f"Saved intermediate plan to {file_path}")

    def _is_good_enough(self, feedback: Dict[str, Any]) -> bool:
        scores = [
            feedback.get("clarity_score", 0),
            feedback.get("educational_effectiveness_score", 0),
            feedback.get("visual_storytelling_score", 0),
            feedback.get("timing_score", 0)
        ]
        return all(score >= 7 for score in scores)

    def _improve_plan(self, plan: Dict[str, Any], feedback: Dict[str, Any]) -> Dict[str, Any]:
        return self.ai_connection.improve_plan(plan, feedback)
