from typing import TypedDict, List

class NarrativeStructure(TypedDict):
    title: str
    intro_hook: str
    progression: List[str]
    conclusion: str
