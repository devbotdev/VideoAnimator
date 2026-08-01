from typing import TypedDict, List

class Shot(TypedDict):
    scene_number: int
    purpose: str
    camera_intention: str
    visual_focus: str
    transition_description: str

class StoryboardSequence(TypedDict):
    title: str
    shots: List[Shot]
