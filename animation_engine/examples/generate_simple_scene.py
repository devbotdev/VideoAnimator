"""Example of generating a simple scene plan using AIConnection."""

import sys
from pathlib import Path
import json

# Add animation_engine to path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ai.connection import AIConnection
from engine.schema import Plan
from engine.converter import plan_to_scene_manager
from engine.renderer import SVGRenderer

def generate_and_print_plan():
    connection = AIConnection()
    
    print("Generating simple scene plan...")
    try:
        # Load the script for the idea
        script_path = ROOT / "assets" / "script"
        with open(script_path, "r", encoding="utf-8") as f:
            idea = f.read()

        brief = connection.generate_creative_brief(idea)
        narrative = connection.generate_narrative_structure(brief)
        visual_concept = connection.generate_visual_concept(narrative)
        storyboard = connection.generate_storyboard(visual_concept)
        animation_plan = connection.generate_animation_plan(storyboard)
        plan_dict = connection.translate_to_engine_schema(animation_plan)
        
        # Validate and repair if necessary
        try:
            Plan.from_dict(plan_dict)
        except Exception as e:
            print(f"Plan validation failed, attempting repair: {e}")
            plan_dict = connection.repair_plan(plan_dict, str(e))
        
        # Ensure version is present
        if "version" not in plan_dict:
            plan_dict["version"] = "1.0"
            
        # Parse and render
        plan = Plan.from_dict(plan_dict)
        manager = plan_to_scene_manager(plan)
        
        # Need to know the total duration from the plan
        total_duration = sum(scene.duration for scene in plan.scenes)
        
        # Use existing render config or default if needed
        from engine.renderer import RenderConfig
        config = RenderConfig(width=plan.resolution["width"], height=plan.resolution["height"], fps=plan.fps)
        renderer = SVGRenderer(config=config)
        output_path = Path("output") / "generated_scene.mp4"
        renderer.export_scene_manager_mp4(output_path, manager, total_duration)
        
        print(f"Successfully exported {output_path}")
    except Exception as e:
        print(f"Error generating plan: {e}")


if __name__ == "__main__":
    generate_and_print_plan()
