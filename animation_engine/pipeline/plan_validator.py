from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from ..engine.schema import Plan, SceneSpec
from ..engine.action_registry import ActionRegistry

@dataclass
class ValidationError:
    scene_id: Optional[str]
    message: str

class PlanValidator:
    def __init__(self, registry: ActionRegistry):
        self.registry = registry

    def validate(self, plan: Plan) -> List[ValidationError]:
        errors: List[ValidationError] = []

        # Validate duplicate IDs across scenes? 
        # Actually, IDs only need to be unique *within* a scene? 
        # Let's check the schema. ObjectSpec ID is within scene.

        seen_scene_ids = set()

        for scene in plan.scenes:
            if scene.id in seen_scene_ids:
                errors.append(ValidationError(scene.id, f"Duplicate scene ID: {scene.id}"))
            seen_scene_ids.add(scene.id)
            
            if scene.duration <= 0:
                errors.append(ValidationError(scene.id, "Scene duration must be positive."))

            # Track object IDs in this scene
            object_ids = {obj.id for obj in scene.objects}
            if len(object_ids) != len(scene.objects):
                errors.append(ValidationError(scene.id, "Duplicate object IDs found in scene."))

            # Validate objects
            for obj in scene.objects:
                # The schema already validates type on instantiation, 
                # but we can add further semantic checks here if needed.
                pass

            # Validate actions
            for i, action in enumerate(scene.actions):
                if action.target_id not in object_ids:
                    errors.append(ValidationError(scene.id, f"Action refers to non-existent object: {action.target_id}"))
                    continue
                
                target_obj = next(obj for obj in scene.objects if obj.id == action.target_id)
                
                try:
                    self.registry.validate(
                        action.action,
                        action.parameters,
                        target_obj.type,
                        scene.id,
                        i,
                        action.target_id
                    )
                except ValueError as e:
                    errors.append(ValidationError(scene.id, str(e)))
                
                if action.start_time < 0 or (action.start_time + action.duration) > scene.duration:
                    errors.append(ValidationError(scene.id, f"Action timing ({action.start_time}+{action.duration}) exceeds scene duration ({scene.duration})."))

        return errors
