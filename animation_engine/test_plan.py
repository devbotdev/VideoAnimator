import json
from engine.schema import Plan
from engine.converter import plan_to_scene_manager

with open("examples/sample_plan.json", "r") as f:
    data = json.load(f)

plan = Plan.from_dict(data)
print("Plan validated.")

manager = plan_to_scene_manager(plan)
print(f"Manager created with {len(manager.scenes)} scenes.")
print(f"Scene 1 background: {manager.scenes[0].background}")
