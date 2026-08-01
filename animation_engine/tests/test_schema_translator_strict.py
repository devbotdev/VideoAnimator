import unittest
from ..pipeline.compiler import Compiler, CompilerError

class TestCompiler(unittest.TestCase):
    def setUp(self):
        self.compiler = Compiler()

    def test_compile_valid_plan(self):
        raw_plan = {
            "title": "Valid Plan",
            "scenes": [
                {
                    "id": "s1",
                    "duration": 5.0,
                    "objects": [{"id": "o1", "type": "Circle"}],
                    "actions": [{"start_time": 0.0, "duration": 1.0, "target_id": "o1", "action": "move", "parameters": {"x": 10.0, "y": 10.0}}]
                }
            ]
        }
        plan = self.compiler.compile(raw_plan)
        self.assertEqual(plan.title, "Valid Plan")
        self.assertEqual(len(plan.scenes), 1)

    def test_compile_transformable_object(self):
        raw_plan = {
            "scenes": [
                {
                    "id": "s1",
                    "duration": 5.0,
                    "objects": [{"id": "o1", "type": "Sphere"}], # Sphere -> Circle
                    "actions": []
                }
            ]
        }
        plan = self.compiler.compile(raw_plan)
        self.assertEqual(plan.scenes[0].objects[0].type, "Circle")

    def test_compile_unsupported_object_fails(self):
        raw_plan = {
            "scenes": [
                {
                    "id": "s1",
                    "duration": 5.0,
                    "objects": [{"id": "o1", "type": "Unicorn"}],
                    "actions": []
                }
            ]
        }
        with self.assertRaises(CompilerError):
            self.compiler.compile(raw_plan)

    def test_compile_unsupported_action_fails(self):
        raw_plan = {
            "scenes": [
                {
                    "id": "s1",
                    "duration": 5.0,
                    "objects": [{"id": "o1", "type": "Circle"}],
                    "actions": [{"start_time": 0.0, "duration": 1.0, "target_id": "o1", "action": "teleport", "parameters": {}}]
                }
            ]
        }
        with self.assertRaises(CompilerError):
            self.compiler.compile(raw_plan)

if __name__ == "__main__":
    unittest.main()
