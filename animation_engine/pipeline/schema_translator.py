import logging
from ..pipeline.orchestrator import PipelineContext
from ..ai.connection import AIConnection
from ..engine.schema import Plan
from ..pipeline.compiler import Compiler, CompilerError

class SchemaTranslator:
    def __init__(self, ai_connection: AIConnection):
        self.name = "SchemaTranslator"
        self.ai_connection = ai_connection
        self.logger = logging.getLogger(self.name)
        self.compiler = Compiler()

    def run(self, context: PipelineContext) -> None:
        """Convert intermediate animation plan into engine Plan."""
        animation_plan = context.get("animation_plan")
        if not animation_plan:
            raise ValueError("Missing 'animation_plan' in PipelineContext")
            
        translated_plan = self.ai_connection.translate_to_engine_schema(animation_plan)
        
        try:
            plan = self.compiler.compile(translated_plan)
            context.set("engine_plan", plan)
        except CompilerError as e:
            self.logger.error(f"Compilation error: {e}")
            # Optionally trigger repair if desired:
            # repaired_plan = self.ai_connection.repair_plan(translated_plan, str(e))
            # ... re-compile ...
            raise ValueError(f"Failed to compile to engine schema: {e}")
        except Exception as e:
            raise ValueError(f"Unexpected error during compilation: {e}")
