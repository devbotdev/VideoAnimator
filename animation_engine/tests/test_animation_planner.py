import unittest
from unittest.mock import MagicMock
from ..director.animation_planner import AnimationPlanner
from ..pipeline.orchestrator import PipelineContext

class TestAnimationPlanner(unittest.TestCase):
    def test_run(self):
        # Mock AIConnection
        mock_ai_connection = MagicMock()
        
        # Define mock storyboard sequence
        storyboard = {
            "title": "Test Animation",
            "shots": [
                {
                    "scene_number": 1,
                    "purpose": "Introduce the character",
                    "camera_intention": "Zoom in",
                    "visual_focus": "Character",
                    "transition_description": "Fade in"
                }
            ]
        }
        
        # Define expected animation plan
        expected_plan = {
            "title": "Test Animation",
            "scenes": [
                {
                    "scene_number": 1,
                    "purpose": "Introduce the character",
                    "objects": [
                        {"id": "char1", "purpose": "main character", "visual_description": "simple stick figure"}
                    ],
                    "actions": [
                        {"target_id": "char1", "movement_intention": "appears", "timing_intention": "immediately"}
                    ],
                    "relationships": []
                }
            ]
        }
        
        # Set up mock to return expected plan
        mock_ai_connection.generate_animation_plan.return_value = expected_plan
        
        # Set up context
        context = PipelineContext()
        context.set("storyboard_sequence", storyboard)
        
        # Run planner
        planner = AnimationPlanner(mock_ai_connection)
        planner.run(context)
        
        # Verify
        self.assertEqual(context.get("animation_plan"), expected_plan)
        mock_ai_connection.generate_animation_plan.assert_called_once_with(storyboard)

if __name__ == "__main__":
    unittest.main()
