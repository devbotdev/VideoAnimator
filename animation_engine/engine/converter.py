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
            # TODO: Should we validate that these are NOT in properties, 
            # and that all properties are valid?
            
            # Clean up known invalid AI-generated properties
            if "position" in properties:
                properties.pop("position")

            # Validate allowed properties
            allowed_fields = set(obj_class.__dataclass_fields__.keys())
            if "style" in allowed_fields:
                allowed_fields.remove("style")
            
            # Allow mapped properties to exist in properties,
            # but only if they are not explicitly forbidden or if they are to be mapped.
            # Actually, the simplest check is to ensure that anything in `properties`
            # is either in `allowed_fields` OR is a property we know we map to style.
            
            mapped_to_style = {"color", "stroke_color", "fill", "fill_color", "text", "font_color", "style", "stroke"}
            
            invalid_properties = [k for k in properties.keys() 
                                  if k not in allowed_fields and k not in mapped_to_style]
            
            if invalid_properties:
                raise ValueError(f"Invalid properties for {obj_class.__name__}: {invalid_properties}")
            
            # Now perform the mapping
            if "style" in properties:
                val = properties.pop("style")
                if isinstance(val, dict):
                    style.update(val)
            if "color" in properties:
                style["fill_color"] = properties.pop("color")
            if "stroke" in properties:
                style["stroke_color"] = properties.pop("stroke")
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
            
            # The remaining properties should be valid as we already checked
            filtered_properties = properties
            
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