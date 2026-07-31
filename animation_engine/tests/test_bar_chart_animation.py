import pytest
from engine.scene import Scene
from engine.charts import BarChart

def test_bar_chart_animation():
    scene = Scene()
    bar = BarChart(data={"Inflation": 10})
    scene.add(bar)
    
    # Animate from 10 to 50 over 2 seconds
    scene.animate(bar, "value", 10, 50, duration=2.0)
    
    # Check start (at time 0)
    assert bar.value == 10
    assert bar._bars["Inflation"].height == 10
    assert bar._bars["Inflation"].y == -10
    
    # Update at 1.0s (midpoint)
    scene.update(1.0)
    assert bar.value == 30 # Linear interpolation (10+50)/2 = 30
    assert bar._bars["Inflation"].height == 30
    assert bar._bars["Inflation"].y == -30
    
    # Update at 1.0s (end)
    scene.update(1.0)
    assert bar.value == 50
    assert bar._bars["Inflation"].height == 50
    assert bar._bars["Inflation"].y == -50
