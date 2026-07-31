
import pytest
from engine.action_registry import ActionRegistry

def test_action_registry():
    registry = ActionRegistry()
    
    # Mock executor
    def move_executor(manager, target, x, y, duration):
        return [f"Moved {target} to {x}, {y}", f"Moved {target} to {x}, {y}"]

    registry.register("move", {"x": float, "y": float, "duration": float}, ["Rectangle", "Circle"], move_executor)
    
    # Validation
    assert registry.validate("move", {"x": 10.0, "y": 20.0, "duration": 1.0}, "Rectangle", "scene1", 0, "rect1") == True
    
    with pytest.raises(ValueError, match="missing parameter 'x'"):
        registry.validate("move", {"y": 20.0, "duration": 1.0}, "Rectangle", "scene1", 0, "rect1")
        
    with pytest.raises(ValueError, match="is not compatible with target type 'Text'"):
        registry.validate("move", {"x": 10.0, "y": 20.0, "duration": 1.0}, "Text", "scene1", 0, "text1")

    with pytest.raises(ValueError, match="parameter 'x' must be float"):
        registry.validate("move", {"x": 10, "y": 20.0, "duration": 1.0}, "Rectangle", "scene1", 0, "rect1") # 10 is int, not float

    with pytest.raises(ValueError, match="unknown parameter 'z'"):
        registry.validate("move", {"x": 10.0, "y": 20.0, "duration": 1.0, "z": 1.0}, "Rectangle", "scene1", 0, "rect1")

    # Execution
    result = registry.execute("move", None, "rect1", {"x": 10.0, "y": 20.0, "duration": 1.0})
    assert result == ["Moved rect1 to 10.0, 20.0", "Moved rect1 to 10.0, 20.0"] # Mock returns a list
