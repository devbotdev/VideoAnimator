
from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class Style:
    fill_color: str = "#222222"

@dataclass
class BaseObject:
    x: float = 0.0
    y: float = 0.0
    style: Style = field(default_factory=Style)

@dataclass
class Circle(BaseObject):
    radius: float = 1.0

def validate_properties(obj_class, properties):
    allowed_fields = set(obj_class.__dataclass_fields__.keys())
    if "style" in allowed_fields:
        allowed_fields.remove("style")
    
    invalid_properties = [k for k in properties.keys() if k not in allowed_fields]
    if invalid_properties:
        raise ValueError(f"Invalid properties for {obj_class.__name__}: {invalid_properties}")
    print("Properties valid")

validate_properties(Circle, {"x": 10, "y": 10, "radius": 5})
try:
    validate_properties(Circle, {"pos_x": 10, "y": 10, "radius": 5})
except ValueError as e:
    print(f"Caught expected error: {e}")
