
import sys
from pathlib import Path

# Add animation_engine to path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.schema import Plan, SceneSpec, ObjectSpec, ActionSpec
from engine.converter import plan_to_scene_manager
from engine.renderer import SVGRenderer, RenderConfig

from engine.theme import LIGHT_THEME

def test_rendering():
    plan_dict = {
        "version": "1.0",
        "title": "Test Rendering",
        "resolution": {"width": 1920, "height": 1080},
        "fps": 30,
        "theme": "light", # Use theme
        "scenes": [
            {
                "id": "scene_1",
                "duration": 2.0,
                "background": "#ffffff",
                "objects": [
                    {
                        "id": "protagonist",
                        "type": "Circle",
                        "properties": {"color": "red", "x": 500, "y": 540, "radius": 50},
                        "style": {"fill": "solid"}
                    }
                ],
                "actions": []
            }
        ],
        "narration": []
    }
    
    plan = Plan.from_dict(plan_dict)
    manager = plan_to_scene_manager(plan)
    # Apply theme
    for scene in manager.scenes:
        scene.theme = LIGHT_THEME
        for obj in scene.objects:
            obj.apply_theme(LIGHT_THEME)
    
    config = RenderConfig(width=1920, height=1080, fps=30)
    renderer = SVGRenderer(config=config)
    
    output_path = Path("output") / "test_scene.svg"
    # Export first frame as SVG
    frame = manager.current_scene.frame()
    svg_data = renderer.render_frame(frame)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_data)
    print(f"Rendered to {output_path}")

if __name__ == "__main__":
    test_rendering()
