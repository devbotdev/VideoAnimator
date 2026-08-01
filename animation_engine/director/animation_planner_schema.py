from typing import TypedDict, List, Dict, Any

class AnimationPlanObject(TypedDict):
    id: str
    purpose: str
    visual_description: str

class AnimationPlanAction(TypedDict):
    target_id: str
    movement_intention: str
    timing_intention: str

class AnimationPlanScene(TypedDict):
    scene_number: int
    purpose: str
    objects: List[AnimationPlanObject]
    actions: List[AnimationPlanAction]
    relationships: List[Dict[str, str]]

class AnimationPlan(TypedDict):
    title: str
    scenes: List[AnimationPlanScene]
