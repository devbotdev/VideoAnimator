from animation_engine.engine.scene import Scene
from animation_engine.engine.theme import DARK_THEME
from animation_engine.engine.charts import BarChart, LineChart
from animation_engine.engine.layout import stack_horizontal, align_center
from animation_engine.engine.canvas import SVGCanvas

def create_example():
    scene = Scene(name="Charts Comparison", theme=DARK_THEME)
    
    bar_chart = BarChart(data={"A": 50, "B": 80, "C": 30})
    line_chart = LineChart(data=[10, 30, 20, 50, 40])
    
    scene.add(bar_chart)
    scene.add(line_chart)
    
    # Layout them side-by-side
    stack_horizontal([bar_chart, line_chart], x_start=200, y=500, spacing=100)
    
    canvas = SVGCanvas(width=800, height=600, background=DARK_THEME.background_color)
    canvas.extend(scene.objects)
    
    with open("output/theme_layout_example.svg", "w") as f:
        f.write(canvas.to_svg())

if __name__ == "__main__":
    create_example()
