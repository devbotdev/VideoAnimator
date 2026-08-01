import pytest
from pipeline.orchestrator import PipelineContext, PipelineStage, PipelineOrchestrator

class MockStage:
    def __init__(self, name: str, action):
        self.name = name
        self.action = action

    def run(self, context: PipelineContext) -> None:
        self.action(context)

def test_pipeline_execution_order():
    execution_order = []

    def action1(ctx): execution_order.append("stage1")
    def action2(ctx): execution_order.append("stage2")

    orchestrator = PipelineOrchestrator()
    orchestrator.add_stage(MockStage("Stage1", action1))
    orchestrator.add_stage(MockStage("Stage2", action2))

    orchestrator.run(PipelineContext())
    assert execution_order == ["stage1", "stage2"]

def test_data_passing():
    def action1(ctx): ctx.set("key", "value")
    def action2(ctx): ctx.set("result", ctx.get("key") + "_transformed")

    orchestrator = PipelineOrchestrator()
    orchestrator.add_stage(MockStage("Stage1", action1))
    orchestrator.add_stage(MockStage("Stage2", action2))

    context = PipelineContext()
    orchestrator.run(context)
    assert context.get("result") == "value_transformed"

def test_failure_reporting():
    def action1(ctx): pass
    def action2(ctx): raise ValueError("Stage 2 failed")

    orchestrator = PipelineOrchestrator()
    orchestrator.add_stage(MockStage("Stage1", action1))
    orchestrator.add_stage(MockStage("Stage2", action2))

    with pytest.raises(ValueError, match="Stage 2 failed"):
        orchestrator.run(PipelineContext())
