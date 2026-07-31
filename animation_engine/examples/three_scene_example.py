from engine.scene import Scene, SceneManager
from engine.transition import SlideTransition
from engine.objects import Rectangle, Style

def run_example():
    manager = SceneManager()
    
    # Scene 1
    s1 = Scene(name="Scene 1", duration=2.0)
    s1.add(Rectangle(x=100, y=100, width=50, height=50, style=Style(fill_color="red")))
    manager.add_scene(s1)
    
    # Scene 2
    s2 = Scene(name="Scene 2", duration=2.0)
    s2.add(Rectangle(x=200, y=200, width=50, height=50, style=Style(fill_color="blue")))
    manager.add_scene(s2)
    
    # Scene 3
    s3 = Scene(name="Scene 3", duration=2.0)
    s3.add(Rectangle(x=300, y=300, width=50, height=50, style=Style(fill_color="green")))
    manager.add_scene(s3)
    
    # Run loop
    total_time = 8.0 # Sufficient time for all transitions
    delta_time = 0.5
    for _ in range(int(total_time / delta_time)):
        manager.update(delta_time)
        print(f"Current scene: {manager.current_scene.name}")
        
if __name__ == "__main__":
    run_example()
