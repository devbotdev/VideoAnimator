import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Iterator

# Mocking engine parts to investigate the logic
class Scene:
    def __init__(self, name, duration):
        self.name = name
        self.duration = duration
        self.elapsed_time = 0.0
    
    @property
    def completed(self):
        return self.elapsed_time >= self.duration

    def update(self, delta_time):
        self.elapsed_time += delta_time
        print(f"Scene {self.name} elapsed: {self.elapsed_time:.2f}")

class SceneManager:
    def __init__(self):
        self.scenes = []
        self.active_index = 0
    def add_scene(self, scene):
        self.scenes.append(scene)
    @property
    def current_scene(self):
        return self.scenes[self.active_index]
    def update(self, delta_time):
        self.current_scene.update(delta_time)
        if self.current_scene.completed:
            print(f"Scene {self.current_scene.name} completed!")
            if self.active_index + 1 < len(self.scenes):
                self.active_index += 1
                print(f"Transitioned to {self.current_scene.name}")

# Test the logic
plan_data = {
  "scenes": [
    {"id": "scene1", "duration": 3.0},
    {"id": "scene2", "duration": 3.0}
  ]
}

manager = SceneManager()
for s in plan_data["scenes"]:
    manager.add_scene(Scene(s["id"], s["duration"]))

fps = 30
frame_time = 1.0 / fps
total_frames = 180

for i in range(total_frames):
    manager.update(frame_time)
    if i % 30 == 0:
        print(f"Frame {i}, current scene: {manager.current_scene.name}")
