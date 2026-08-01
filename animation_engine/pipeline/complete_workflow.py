from ..pipeline.visual_validator import VisualValidator
from ..pipeline.orchestrator import PipelineContext
from ..ai.connection import AIConnection
from ..engine.action_registry import ActionRegistry
from ..pipeline.creative_pipeline import CreativePipeline
from ..pipeline.iterative_improvement import IterativeImprovementStage
from ..pipeline.schema_translator import SchemaTranslator
from ..director.concept_director import ConceptDirector

class CompleteWorkflow:
    def __init__(self, ai_connection: AIConnection, registry: ActionRegistry, idea: str):
        self.ai_connection = ai_connection
        self.registry = registry
        self.idea = idea
        
    def run(self, context: PipelineContext) -> None:
        context.save_debug_data("InputPrompt", {"idea": self.idea})
        
        # 1. Concept Generation (First step)
        ConceptDirector(self.ai_connection, self.idea).run(context)
        context.save_debug_data("ConceptDirector", context.get("creative_brief"))
        
        # 2. Creative Pipeline
        CreativePipeline(self.ai_connection).run(context)
        
        # 3. Iterative Improvement
        IterativeImprovementStage(self.ai_connection, self.registry).run(context)
        context.save_debug_data("IterativeImprovementStage", context.get("iteration_history"))
        context.save_debug_data("FinalAnimationPlan", context.get("final_animation_plan"))
        
        # 4. Translation
        SchemaTranslator(self.ai_connection).run(context)
        context.save_debug_data("SchemaTranslator", context.get("engine_plan"))
        
        # 5. Visual Validation
        engine_plan = context.get("engine_plan")
        if engine_plan:
             validator = VisualValidator(engine_plan)
             results = validator.validate()
             if not results["valid"]:
                 raise ValueError(f"Visual validation failed: {results['errors']}")
             context.save_debug_data("VisualValidation", results)

        # Validation is handled within IterativeImprovementStage or SchemaTranslator.
        # If successful, 'engine_plan' is now in context.
        print("Workflow completed. Plan is ready for rendering.")
