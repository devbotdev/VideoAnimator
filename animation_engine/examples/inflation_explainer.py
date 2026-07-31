import json
import sys
from pathlib import Path

# Fix path for imports
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.scene import Scene, SceneManager
from engine.charts import BarChart
from engine.renderer import SVGRenderer, RenderConfig
from engine.schema import Plan

def create_scene_from_spec(scene_spec) -> Scene:
    scene = Scene(name=scene_spec.id, background=scene_spec.background)
    scene.duration = scene_spec.duration
    
    # Correct camera center for 1280x720
    scene.camera.x = 640
    scene.camera.y = 360
    scene.camera.width = 1280
    scene.camera.height = 720
    
    for obj_spec in scene_spec.objects:
        if obj_spec.type == "BarChart":
            props = obj_spec.properties.copy()
            animate_to = props.pop("animate_to", None)
            easing = props.pop("easing", "linear")
            x = props.pop("x", 0.0)
            y = props.pop("y", 0.0)
            print(f"Creating BarChart with props: {props}, x={x}, y={y}")
            bar_chart = BarChart(**props)
            bar_chart.x = x
            bar_chart.y = y
            print(f"BarChart initialized: x={bar_chart.x}, y={bar_chart.y}")
            scene.add(bar_chart)
            
            if animate_to:
                # Assuming single-value animation as per plan
                start_value = bar_chart.value
                end_value = list(animate_to.values())[0]
                scene.animate(
                    target=bar_chart,
                    property_name="value",
                    start_value=start_value,
                    end_value=end_value,
                    duration=scene_spec.duration,
                    easing=easing
                )
        else:
            raise ValueError(f"Unsupported object type: {obj_spec.type}")

    return scene

def main():
    plan_path = Path("examples/inflation_plan.json")
    with open(plan_path, "r") as f:
        data = json.load(f)

    plan = Plan.from_dict(data)

    manager = SceneManager()
    for scene_spec in plan.scenes:
        manager.add_scene(create_scene_from_spec(scene_spec))

    config = RenderConfig(
        width=plan.resolution["width"],
        height=plan.resolution["height"],
        fps=plan.fps,
        output_format="mp4"
    )

    renderer = SVGRenderer(config=config)

    # Calculate total duration
    total_duration = sum(s.duration for s in plan.scenes)

    output_path = Path("output") / "inflation_explainer.mp4"
    renderer.export_scene_manager_mp4(output_path, manager, duration=total_duration)
    print(f"Exported to {output_path}")

if __name__ == "__main__":
    main()
