import unittest
from unittest.mock import MagicMock
from ..pipeline.schema_translator import SchemaTranslator
from ..pipeline.orchestrator import PipelineContext
from ..engine.schema import Plan

class TestSchemaTranslator(unittest.TestCase):
    def test_run(self):
        # Mock AIConnection
        mock_ai_connection = MagicMock()
        
        # Define mock animation plan
        animation_plan = {
            "title": "Test Animation",
            "scenes": [
                {
                    "scene_number": 1,
                    "purpose": "Introduce the character",
                    "objects": [
                        {"id": "char1", "type": "StickFigure", "initial_properties": {"x": 0, "y": 0}}
                    ],
                    "events": [
                        {"event_type": "fade_in", "target_id": "char1", "start_time": 0.0, "duration": 1.0, "parameters": {}}
                    ],
                    "relationships": []
                }
            ]
        }
        
        # Define expected engine plan
        expected_engine_plan = {
            "version": "1.0",
            "title": "Test Animation",
            "resolution": {"width": 1920, "height": 1080},
            "fps": 30,
            "theme": "default",
            "scenes": [
                {
                    "id": "1",
                    "duration": 1.0,
                    "background": "#ffffff",
                    "objects": [
                        {"id": "char1", "type": "StickFigure", "properties": {"x": 0, "y": 0}, "style": {}}
                    ],
                    "actions": [
                        {"start_time": 0.0, "duration": 1.0, "target_id": "char1", "action": "fade_in", "parameters": {}}
                    ]
                }
            ]
        }
        
        # Set up mock to return expected plan
        mock_ai_connection.translate_to_engine_schema.return_value = expected_engine_plan
        
        # Set up context
        context = PipelineContext()
        context.set("animation_plan", animation_plan)
        
        # Run translator
        translator = SchemaTranslator(mock_ai_connection)
        translator.run(context)
        
        # Verify
        engine_plan = context.get("engine_plan")
        self.assertIsInstance(engine_plan, Plan)
        self.assertEqual(engine_plan.title, "Test Animation")
        mock_ai_connection.translate_to_engine_schema.assert_called_once_with(animation_plan)

if __name__ == "__main__":
    unittest.main()
