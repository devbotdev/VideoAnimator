
"""Versioned plan schema and validation for the animation engine."""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
from .action_registry import ActionRegistry

# Allowlists for validation
ALLOWED_OBJECT_TYPES = {"Rectangle", "Circle", "Text", "StickFigure", "Arrow", "Group", "BarChart"}

ALLOWED_ACTIONS = {"walk", "point", "wave", "move", "fade_in", "fade_out", "scale", "rotate", "draw", "grow", "highlight", "shake", "camera_pan", "camera_zoom", "camera_focus"}

@dataclass
class ActionSpec:
    start_time: float
    duration: float
    target_id: str
    action: str
    parameters: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ActionSpec":
        if data["action"] not in ALLOWED_ACTIONS:
            raise ValueError(f"Action '{data['action']}' is not allowed.")
        return cls(**data)

@dataclass
class ObjectSpec:
    id: str
    type: str
    properties: Dict[str, Any] = field(default_factory=dict)
    style: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ObjectSpec":
        if data["type"] not in ALLOWED_OBJECT_TYPES:
            raise ValueError(f"Object type '{data['type']}' is not allowed.")
        return cls(**data)

@dataclass
class SceneSpec:
    id: str
    duration: float
    background: str = "#ffffff"
    camera: Dict[str, Any] = field(default_factory=dict)
    objects: List[ObjectSpec] = field(default_factory=list)
    actions: List[ActionSpec] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SceneSpec":
        return cls(
            id=data["id"],
            duration=data["duration"],
            background=data.get("background", "#ffffff"),
            camera=data.get("camera", {}),
            objects=[ObjectSpec.from_dict(o) for o in data.get("objects", [])],
            actions=[ActionSpec.from_dict(a) for a in data.get("actions", [])],
        )

@dataclass
class NarrationCue:
    timestamp: float
    text: str

@dataclass
class Plan:
    version: str
    title: str
    resolution: Dict[str, int]
    fps: int
    theme: str
    scenes: List[SceneSpec]
    narration: List[NarrationCue] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Plan":
        # Basic validation
        if "version" not in data:
            raise ValueError("Plan must have a version.")

        return cls(
            version=data["version"],
            title=data["title"],
            resolution=data["resolution"],
            fps=data["fps"],
            theme=data["theme"],
            scenes=[SceneSpec.from_dict(s) for s in data["scenes"]],
            narration=[NarrationCue(**n) for n in data.get("narration", [])],
        )

    def validate(self, registry: ActionRegistry):
        for scene in self.scenes:
            # Create mapping for object types
            obj_map = {obj.id: obj.type for obj in scene.objects}
            for i, action in enumerate(scene.actions):
                if action.target_id not in obj_map:
                    raise ValueError(f"Target object '{action.target_id}' not found in scene '{scene.id}'.")

                registry.validate(
                    action.action,
                    action.parameters,
                    obj_map[action.target_id],
                    scene.id,
                    i,
                    action.target_id
                )

    def summary(self, registry: ActionRegistry) -> Dict[str, Any]:
        total_duration = sum(scene.duration for scene in self.scenes)
        scene_summaries = []
        
        all_actions = []
        for scene in self.scenes:
            scene_summaries.append({
                "id": scene.id,
                "objects": len(scene.objects),
                "actions": len(scene.actions),
                "duration": scene.duration
            })
            all_actions.extend(scene.actions)
        
        # Check for unsupported actions
        unsupported = []
        for action in all_actions:
            if not registry.is_action_registered(action.action):
                unsupported.append(action.action)

        return {
            "title": self.title,
            "scenes": len(self.scenes),
            "total_duration": total_duration,
            "scenes_summary": scene_summaries,
            "total_actions": len(all_actions),
            "unsupported_actions": list(set(unsupported))
        }

