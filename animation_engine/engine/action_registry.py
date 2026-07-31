
from typing import Any, Dict, List, Callable, Type
from .objects import BaseObject
from .stick_figure import StickFigure
from .camera import Camera
from .animation import AnimationManager

class ActionRegistry:
    def __init__(self):
        self._actions = {}

    def register(self, name: str, parameters: Dict[str, Type], compatible_targets: List[str], executor: Callable):
        self._actions[name] = {
            "parameters": parameters,
            "compatible_targets": compatible_targets,
            "executor": executor
        }

    def populate_defaults(self):
        # BaseObject actions
        self.register("move", {"x": float, "y": float, "duration": float}, ["BaseObject", "Rectangle", "Circle", "Line", "Polyline", "Path", "Text", "Group", "StickFigure", "Arrow"], 
                      lambda manager, t, x, y, duration: [manager.animate(t, "x", t.x, x, duration), manager.animate(t, "y", t.y, y, duration)])
        
        self.register("fade_in", {"duration": float}, ["BaseObject", "Rectangle", "Circle", "Line", "Polyline", "Path", "Text", "Group", "StickFigure", "Arrow"], 
                      lambda manager, t, duration: [manager.animate(t, "opacity", t.opacity, 1.0, duration)])

        self.register("fade_out", {"duration": float}, ["BaseObject", "Rectangle", "Circle", "Line", "Polyline", "Path", "Text", "Group", "StickFigure", "Arrow"], 
                      lambda manager, t, duration: [manager.animate(t, "opacity", t.opacity, 0.0, duration)])
        
        self.register("scale", {"scale": float, "duration": float}, ["BaseObject", "Rectangle", "Circle", "Line", "Polyline", "Path", "Text", "Group", "StickFigure", "Arrow"],
                      lambda manager, t, scale, duration: [manager.animate(t, "scale", t.scale, scale, duration)])

        self.register("grow", {"factor": float, "duration": float}, ["BaseObject", "Rectangle", "Circle", "Line", "Polyline", "Path", "Text", "Group", "StickFigure", "Arrow"],
                      lambda manager, t, factor, duration: [manager.animate(t, "scale", t.scale, t.scale * factor, duration)])

        self.register("rotate", {"angle": float, "duration": float}, ["BaseObject", "Rectangle", "Circle", "Line", "Polyline", "Path", "Text", "Group", "StickFigure", "Arrow"],
                      lambda manager, t, angle, duration: [manager.animate(t, "rotation", t.rotation, angle, duration)])

        # Other base object actions (simplified)
        self.register("draw", {"duration": float}, ["Path"], lambda manager, t, duration: []) # Placeholder
        self.register("highlight", {"duration": float}, ["BaseObject"], lambda manager, t, duration: []) # Placeholder
        self.register("shake", {"duration": float}, ["BaseObject"], lambda manager, t, duration: []) # Placeholder

        # Camera actions
        self.register("camera_pan", {"x": float, "y": float, "duration": float}, ["Camera"],
                      lambda manager, t, x, y, duration: [manager.animate(t, "x", t.x, x, duration), manager.animate(t, "y", t.y, y, duration)])
        
        self.register("camera_zoom", {"zoom": float, "duration": float}, ["Camera"],
                      lambda manager, t, zoom, duration: [manager.animate(t, "zoom", t.zoom, zoom, duration)])
        
        self.register("camera_focus", {"duration": float}, ["Camera"], lambda manager, t, duration: []) # Needs object, too complex for now

    def validate(self, action_name: str, params: Dict[str, Any], target_type: str, scene_id: str, action_index: int, target_id: str):
        if action_name not in self._actions:
            raise ValueError(f"Action '{action_name}' is not registered.")
        
        action_meta = self._actions[action_name]
        
        if target_type not in action_meta["compatible_targets"]:
            raise ValueError(f"Action '{action_name}' is not compatible with target type '{target_type}'. (Scene: {scene_id}, Action Index: {action_index}, Target ID: {target_id})")
        
        # Parameter validation
        for param_name, param_type in action_meta["parameters"].items():
            if param_name not in params:
                raise ValueError(f"Action '{action_name}' missing parameter '{param_name}'. (Scene: {scene_id}, Action Index: {action_index}, Target ID: {target_id})")
            
            if not isinstance(params[param_name], param_type):
                 raise ValueError(f"Action '{action_name}' parameter '{param_name}' must be {param_type.__name__}, got {type(params[param_name]).__name__}. (Scene: {scene_id}, Action Index: {action_index}, Target ID: {target_id})")
        
        # Check for extra parameters
        for param_name in params:
            if param_name not in action_meta["parameters"]:
                raise ValueError(f"Action '{action_name}' received unknown parameter '{param_name}'. (Scene: {scene_id}, Action Index: {action_index}, Target ID: {target_id})")
        
        return True

    def is_action_registered(self, name: str) -> bool:
        return name in self._actions

    def execute(self, action_name: str, manager: Any, target: Any, params: Dict[str, Any]):
        return self._actions[action_name]["executor"](manager, target, **params)
