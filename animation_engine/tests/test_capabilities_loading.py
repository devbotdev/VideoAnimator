import pytest
from pathlib import Path
from animation_engine.ai.connection import AIConnection

def test_capabilities_loading():
    # Arrange
    connection = AIConnection()
    
    # Act
    # Access the loaded prompt directly. Note that 'connection' loads all of them on init.
    planner_prompt = connection.prompts["animation_planner"]
    
    # Assert
    assert "{{ENGINE_CAPABILITIES}}" not in planner_prompt
    assert "Engine Capabilities" in planner_prompt
    assert "Available Objects" in planner_prompt
    assert "Available Animations & Actions" in planner_prompt
