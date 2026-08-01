"""Conversion logic from Plan schema to engine objects."""
from .action_registry import ActionRegistry
from .objects import Arrow, Circle, Group, Rectangle, Text
from .charts import BarChart
from .registry import AssetRegistry
from .scene import Scene, SceneManager
from .schema import Plan
from .stick_figure import StickFigure

OBJECT_TYPE_MAP = {
    "Rectangle": Rectangle,
    "Circle": Circle,
    "Text": Text,
    "StickFigure": StickFigure,
    "Arrow": Arrow,
    "Group": Group,
    "BarChart": BarChart,
}


def plan_to_scene_manager(plan: Plan) -> SceneManager:
    manager = SceneManager()
    registry = ActionRegistry()
    registry.populate_defaults()

    for scene_spec in plan.scenes:
        scene = Scene(
            name=scene_spec.id,
            background=scene_spec.background,
            duration=scene_spec.duration,
            pacing=scene_spec.pacing,
            reset_on_enter=scene_spec.reset_on_enter,
        )

        for obj_spec in scene_spec.objects:
            obj_class = OBJECT_TYPE_MAP[obj_spec.type]
            properties = dict(obj_spec.properties)
            style = dict(obj_spec.style)
            
            # Map common properties to style
            if "color" in properties:
                style["fill_color"] = properties.pop("color")
            if "stroke_color" in properties:
                style["stroke_color"] = properties.pop("stroke_color")
            if "fill" in properties:
                style["fill_color"] = properties.pop("fill")
            if "fill_color" in properties:
                style["fill_color"] = properties.pop("fill_color")
            
            # Specific mappings
            if obj_class is Text:
                if "text" in properties:
                    properties["content"] = properties.pop("text")
                if "font_color" in properties:
                    style["fill_color"] = properties.pop("font_color")
            
            # Filter properties that the object doesn't support
            allowed_fields = set(obj_class.__dataclass_fields__.keys())
            filtered_properties = {k: v for k, v in properties.items() if k in allowed_fields}
            
            obj = obj_class(**filtered_properties)
            # Apply style if the object accepts it (BaseObject defines style)
            if hasattr(obj, "style") and style:
                for key, value in style.items():
                    setattr(obj.style, key, value)
                    
            if isinstance(obj, Group) and "objects" in properties:
                # If the plan contained object definitions for the group,
                # they should have been registered differently or
                # this property is misused in the plan.
                # For now, we clear them to avoid initialization errors.
                properties.pop("objects")
                
            scene.register_object(obj_spec.id, obj)

        for action_spec in scene_spec.actions:
            if action_spec.action.startswith("camera_"):
                target = scene.camera
            else:
                target = scene.object(action_spec.target_id)

            params = dict(action_spec.parameters)
            params.setdefault("duration", action_spec.duration)
            if action_spec.start_time is not None:
                params["start_time"] = action_spec.start_time
            registry.execute(action_spec.action, scene.animation_manager, target, params)

        manager.add_scene(scene)

    return manager