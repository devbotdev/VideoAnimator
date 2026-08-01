from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from ..engine.schema import Plan, SceneSpec, ObjectSpec
from ..engine.action_registry import ActionRegistry

@dataclass
class VisualValidationError:
    scene_id: str
    message: str
    is_error: bool = True

class VisualValidator:
    def __init__(self, plan: Plan):
        self.plan = plan
        self.errors: List[VisualValidationError] = []
        self.warnings: List[VisualValidationError] = []

    def validate(self) -> Dict[str, Any]:
        width = self.plan.resolution.get("width", 1920)
        height = self.plan.resolution.get("height", 1080)
        
        for scene in self.plan.scenes:
            self._validate_scene(scene, width, height)
            
        return {
            "valid": len(self.errors) == 0,
            "errors": [e.message for e in self.errors],
            "warnings": [w.message for w in self.warnings]
        }

    def _validate_scene(self, scene: SceneSpec, canvas_width: int, canvas_height: int):
        # 1. Object validation
        if not scene.objects:
            self.warnings.append(VisualValidationError(scene.id, "Scene contains no objects."))
        
        object_positions = []
        
        for obj in scene.objects:
            # Check for invisible/zero-size
            props = obj.properties
            if obj.type == "Rectangle":
                if props.get("width", 0) <= 0 or props.get("height", 0) <= 0:
                    self.errors.append(VisualValidationError(scene.id, f"Object {obj.id} has zero or negative size."))
            elif obj.type == "Circle":
                if props.get("radius", 0) <= 0:
                    self.errors.append(VisualValidationError(scene.id, f"Object {obj.id} has zero or negative radius."))
            elif obj.type == "Text":
                if not props.get("content"):
                    self.warnings.append(VisualValidationError(scene.id, f"Text object {obj.id} is empty.", is_error=False))
            
            # Position check (assuming properties have x/y or similar)
            x = props.get("x", 0)
            y = props.get("y", 0)
            object_positions.append((x, y))
            
            if not (0 <= x <= canvas_width and 0 <= y <= canvas_height):
                self.warnings.append(VisualValidationError(scene.id, f"Object {obj.id} is likely outside canvas bounds ({x}, {y}).", is_error=False))
        
        # Check for stacked objects
        if len(object_positions) > 1 and len(set(object_positions)) == 1:
            self.warnings.append(VisualValidationError(scene.id, "All objects are stacked at the same location.", is_error=False))

        # 3. Action validation (simple checks)
        for action in scene.actions:
            if action.duration <= 0:
                self.errors.append(VisualValidationError(scene.id, f"Action {action.action} on {action.target_id} has non-positive duration."))
            
            # Check if action actually changes something (this is harder to do thoroughly without simulation)
            # For now, just a basic check if duration is very small
            if action.duration < 0.01:
                self.warnings.append(VisualValidationError(scene.id, f"Action {action.action} on {action.target_id} has very short duration.", is_error=False))
