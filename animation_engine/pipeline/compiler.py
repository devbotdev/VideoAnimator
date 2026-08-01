import logging
from typing import Any, Dict, List, Optional
from ..engine.schema import ALLOWED_OBJECT_TYPES, ALLOWED_ACTIONS, ObjectSpec, ActionSpec, SceneSpec, Plan

class CompilerError(Exception):
    pass

class Compiler:
    def __init__(self):
        self.logger = logging.getLogger("Compiler")

    def compile(self, raw_plan: Dict[str, Any]) -> Plan:
        """Compiles raw AI output into a strict Plan object."""
        
        # 1. Validation and Transformation
        scenes = []
        for scene_data in raw_plan.get("scenes", []):
            scenes.append(self._compile_scene(scene_data))
            
        # 2. Construct Plan
        # We need to fill in metadata if missing or use defaults
        plan_data = {
            "version": raw_plan.get("version", "1.0"),
            "title": raw_plan.get("title", "Generated Plan"),
            "resolution": raw_plan.get("resolution", {"width": 1920, "height": 1080}),
            "fps": raw_plan.get("fps", 30),
            "theme": raw_plan.get("theme", "default"),
            "scenes": scenes,
            "narration": raw_plan.get("narration", [])
        }
        
        return Plan.from_dict(plan_data)

    def _compile_scene(self, scene_data: Dict[str, Any]) -> Dict[str, Any]:
        # Validate/Transform Objects
        new_objects = []
        for obj in scene_data.get("objects", []):
            obj_type = obj.get("type")
            if obj_type not in ALLOWED_OBJECT_TYPES:
                # Try transformation
                transformed_type = self._transform_object_type(obj_type)
                if transformed_type:
                    self.logger.warning(f"Transforming unsupported object {obj_type} to {transformed_type}")
                    obj["type"] = transformed_type
                else:
                    raise CompilerError(f"Unsupported object type: {obj_type}")
            new_objects.append(obj)
            
        scene_data["objects"] = new_objects
        
        # Validate/Transform Actions
        new_actions = []
        for action in scene_data.get("actions", []):
            action_name = action.get("action")
            if action_name not in ALLOWED_ACTIONS:
                raise CompilerError(f"Unsupported action: {action_name}")
            new_actions.append(action)
            
        scene_data["actions"] = new_actions
        
        return scene_data

    def _transform_object_type(self, obj_type: str) -> Optional[str]:
        mapping = {
            "Sphere": "Circle",
            "Plane": "Rectangle",
        }
        return mapping.get(obj_type)
