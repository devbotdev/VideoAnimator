from __future__ import annotations
from typing import Any, Protocol, TypeVar, runtime_checkable
from dataclasses import dataclass, field
import logging

# Configure logging for pipeline visibility
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("pipeline")

@dataclass
class PipelineContext:
    """Shared state container for pipeline stages."""
    data: dict[str, Any] = field(default_factory=dict)
    debug_enabled: bool = False
    debug_dir: str = "debug_output"

    def set(self, key: str, value: Any) -> None:
        self.data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def save_debug_data(self, stage_name: str, data: Any) -> None:
        if not self.debug_enabled:
            return
        
        import os
        import json
        from dataclasses import asdict, is_dataclass
        
        def _serialize(obj):
            if is_dataclass(obj):
                return asdict(obj)
            try:
                return str(obj)
            except Exception:
                return f"Non-serializable: {type(obj)}"
            
        os.makedirs(self.debug_dir, exist_ok=True)
        file_path = os.path.join(self.debug_dir, f"{stage_name.replace(' ', '_').lower()}.json")
        
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2, default=_serialize)
        logger.info(f"Saved debug data for stage '{stage_name}' to {file_path}")

@runtime_checkable
class PipelineStage(Protocol):
    """Interface for a pipeline processing stage."""
    name: str

    def run(self, context: PipelineContext) -> None:
        """Process the context."""
        ...

class PipelineOrchestrator:
    """Executes ordered pipeline stages."""
    def __init__(self):
        self._stages: list[PipelineStage] = []

    def add_stage(self, stage: PipelineStage) -> None:
        self._stages.append(stage)
        logger.info(f"Registered stage: {stage.name}")

    def run(self, context: PipelineContext) -> None:
        """Run all stages in registered order."""
        logger.info("Starting pipeline execution.")
        for stage in self._stages:
            logger.info(f"Executing stage: {stage.name}")
            try:
                stage.run(context)
            except Exception as e:
                logger.error(f"Stage '{stage.name}' failed: {e}")
                raise
        logger.info("Pipeline execution completed successfully.")
