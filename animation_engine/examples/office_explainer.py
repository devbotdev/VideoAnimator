from engine import SVGCanvas, AssetRegistry, StickFigure, Computer, Book
from engine.animation import AnimationManager

def main():
    registry = AssetRegistry()
    registry.register("stickman", StickFigure)
    registry.register("computer", Computer)
    registry.register("book", Book)
    
    canvas = SVGCanvas()
    manager = AnimationManager()
    
    # Create assets
    man = registry.create("stickman")
    comp = registry.create("computer")
    doc = registry.create("book")
    
    comp.move_to(500, 400)
    doc.move_to(600, 450)
    man.move_to(200, 400)
    
    canvas.add(comp)
    canvas.add(doc)
    canvas.add(man)
    
    # Animate
    man.enter(manager, 1.0)
    man.walk(manager, 2.0, distance=300)
    man.point(manager, 1.0, arm="right")
    man.think(manager, 1.0)
    man.celebrate(manager, 1.0)
    man.idle(manager, 1.0)
    man.exit(manager, 1.0)
    
    # Output SVG for current frame (at time 0)
    # The canvas.to_svg() renders the state
    with open("office_scene.svg", "w") as f:
        f.write(canvas.to_svg())

if __name__ == "__main__":
    main()
