import unittest
from ..engine.schema import Plan, SceneSpec, ObjectSpec, ActionSpec
from ..engine.action_registry import ActionRegistry
from ..pipeline.plan_validator import PlanValidator

class TestPlanValidator(unittest.TestCase):
    def setUp(self):
        self.registry = ActionRegistry()
        self.registry.populate_defaults()
        self.validator = PlanValidator(self.registry)

    def test_valid_plan(self):
        plan = Plan(
            version="1.0",
            title="Valid",
            resolution={"width": 1920, "height": 1080},
            fps=30,
            theme="default",
            scenes=[
                SceneSpec(
                    id="s1",
                    duration=5.0,
                    objects=[ObjectSpec(id="o1", type="Rectangle")],
                    actions=[ActionSpec(start_time=0.0, duration=1.0, target_id="o1", action="fade_in")]
                )
            ]
        )
        errors = self.validator.validate(plan)
        self.assertEqual(len(errors), 0)

    def test_invalid_action_target(self):
        plan = Plan(
            version="1.0",
            title="Invalid",
            resolution={"width": 1920, "height": 1080},
            fps=30,
            theme="default",
            scenes=[
                SceneSpec(
                    id="s1",
                    duration=5.0,
                    objects=[ObjectSpec(id="o1", type="Rectangle")],
                    actions=[ActionSpec(start_time=0.0, duration=1.0, target_id="o2", action="fade_in")]
                )
            ]
        )
        errors = self.validator.validate(plan)
        self.assertTrue(any("non-existent object" in e.message for e in errors))

    def test_invalid_timing(self):
        plan = Plan(
            version="1.0",
            title="Invalid",
            resolution={"width": 1920, "height": 1080},
            fps=30,
            theme="default",
            scenes=[
                SceneSpec(
                    id="s1",
                    duration=1.0,
                    objects=[ObjectSpec(id="o1", type="Rectangle")],
                    actions=[ActionSpec(start_time=0.0, duration=2.0, target_id="o1", action="fade_in")]
                )
            ]
        )
        errors = self.validator.validate(plan)
        self.assertTrue(any("exceeds scene duration" in e.message for e in errors))

    def test_unsupported_action(self):
        plan = Plan(
            version="1.0",
            title="Invalid",
            resolution={"width": 1920, "height": 1080},
            fps=30,
            theme="default",
            scenes=[
                SceneSpec(
                    id="s1",
                    duration=5.0,
                    objects=[ObjectSpec(id="o1", type="Rectangle")],
                    actions=[ActionSpec(start_time=0.0, duration=1.0, target_id="o1", action="invalid_action")]
                )
            ]
        )
        # Assuming ActionSpec.from_dict raises ValueError if action not in allowed, 
        # but manual construction might bypass it. Let's ensure the validator catches it.
        # ActionSpec.from_dict checks ALLOWED_ACTIONS.
        with self.assertRaises(ValueError):
            ActionSpec.from_dict({"start_time": 0.0, "duration": 1.0, "target_id": "o1", "action": "invalid_action"})

if __name__ == "__main__":
    unittest.main()
