import pytest
from engine.transition import _lerp_color, FadeTransition, SceneFrame
from engine.camera import Camera

def test_lerp_color_valid():
    assert _lerp_color("#000000", "#ffffff", 0.0) == "#000000"
    assert _lerp_color("#000000", "#ffffff", 1.0) == "#ffffff"
    # 240 + 7.5 = 247.5, int is 247 -> f7
    assert _lerp_color("#f0f0f0", "#ffffff", 0.5) == "#f7f7f7"
    # r: 255 -> 0, 0.5 => 127.5 -> 127 -> 7f
    # g: 0 -> 255, 0.5 => 127.5 -> 127 -> 7f
    # b: 0 -> 0, 0.5 => 0
    assert _lerp_color("#ff0000", "#00ff00", 0.5) == "#7f7f00"

def test_lerp_color_invalid():
    with pytest.raises(ValueError, match="Colors must be in '#RRGGBB' format."):
        _lerp_color("invalid", "#ffffff", 0.5)
    with pytest.raises(ValueError, match="Colors must be in '#RRGGBB' format."):
        _lerp_color("#123", "#ffffff", 0.5)

def test_fade_transition_background_interpolation():
    from_frame = SceneFrame(objects=[], camera=Camera(width=100, height=100), background="#000000")
    to_frame = SceneFrame(objects=[], camera=Camera(width=100, height=100), background="#ffffff")
    
    # Need to mock elapsed/duration for FadeTransition to control progress
    transition = FadeTransition(duration=1.0)
    
    # Progress 0.0
    transition.elapsed = 0.0
    blended = transition.blend_frame(from_frame, to_frame)
    assert blended.background == "#000000"
    
    # Progress 0.5
    transition.elapsed = 0.5
    blended = transition.blend_frame(from_frame, to_frame)
    assert blended.background == "#7f7f7f"
    
    # Progress 1.0
    transition.elapsed = 1.0
    blended = transition.blend_frame(from_frame, to_frame)
    assert blended.background == "#ffffff"
