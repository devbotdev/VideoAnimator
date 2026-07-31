
from engine import Scene, BarChart, Callout, Text, Arrow, Style

def create_economic_scene():
    scene = Scene()
    
    # Title
    scene.add(Text(x=960, y=100, content="Economic Growth Explainer", text_anchor="middle", font_size=40))
    
    # Bar Chart
    data = {"Q1": 50, "Q2": 70, "Q3": 90, "Q4": 120}
    chart = BarChart(data=data, x=400, y=700)
    scene.add(chart)
    
    # Annotation
    callout = Callout(target_x=800, target_y=580, text="Significant growth in Q4")
    scene.add(callout)
    
    # Arrow
    scene.add(Arrow(start_x=400, start_y=800, end_x=900, end_y=800))
    
    return scene

if __name__ == "__main__":
    from engine.renderer import SVGRenderer
    scene = create_economic_scene()
    renderer = SVGRenderer()
    renderer.export_scene_mp4("output/economic_explainer.mp4", scene, duration=2.0)
    print("Example scene exported successfully.")
