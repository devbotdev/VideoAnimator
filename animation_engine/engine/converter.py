"""Conversion logic from Plan schema to engine objects."""
from .schema import Plan
from .scene import Scene, SceneManager
from .objects import Rectangle, Circle, Text, Arrow, Group
from .stick_figure import StickFigure
from .registry import AssetRegistry

OBJECT_TYPE_MAP = {
    "Rectangle": Rectangle,
    "Circle": Circle,
    "Text": Text,
    "StickFigure": StickFigure,
    "Arrow": Arrow,
    "Group": Group,
}

def plan_to_scene_manager(plan: Plan) -> SceneManager:
    manager = SceneManager()
    
    for scene_spec in plan.scenes:
        # Create scene
        scene = Scene(name=scene_spec.id, background=scene_spec.background, duration=scene_spec.duration)
        
        # Add objects
        for obj_spec in scene_spec.objects:
            obj_class = OBJECT_TYPE_MAP[obj_spec.type]
            # Simple instantiation, ignoring properties/style for now
            obj = obj_class(**obj_spec.properties)
            scene.register_object(obj_spec.id, obj)
            
        # Add actions
        for action_spec in scene_spec.actions:
            target = scene.object(action_spec.target_id)
            # This is a simplified application of actions
            # For a real implementation, this would require action handler registry
            if hasattr(target, action_spec.action):
                method = getattr(target, action_spec.action)
                # Assuming all actions take animation_manager as first argument (based on ai.py)
                # But actions in schema are not fully mapped to this engine's action handlers yet
                pass
            
        manager.add_scene(scene)
        
    return manager
