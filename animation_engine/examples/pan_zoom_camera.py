from engine.scene import Scene
from engine.objects import Rectangle, Text
from engine.renderer import SVGRenderer
import os

# Create a scene
scene = Scene(name="Camera Animation")

# Add a title
title = scene.register_object("title", Text(x=960, y=540, content="Title", font_size=100))

# Add a chart (rectangle)
chart = scene.register_object("chart", Rectangle(x=3000, y=540, width=500, height=300, fill_color="#ff0000"))

# Animation: Pan from title to chart, Zoom into chart
scene.animate_camera("x", start_value=960.0, end_value=3000.0, duration=2.0)
scene.animate_camera("zoom", start_value=1.0, end_value=2.0, duration=2.0)

# Render
renderer = SVGRenderer(width=1920, height=1080)
renderer.export_scene_mp4("output/pan_zoom_camera.mp4", scene, duration=2.0)
