import pytest
from engine.registry import AssetRegistry
from engine.assets import Computer, Book
from engine.stick_figure import StickFigure
from engine.canvas import SVGCanvas

def test_registry_basic():
    registry = AssetRegistry()
    registry.register("computer", Computer)
    registry.register("book", Book)
    
    comp = registry.create("computer")
    assert isinstance(comp, Computer)
    
    book = registry.create("book")
    assert isinstance(book, Book)
    
    with pytest.raises(ValueError):
        registry.create("nonexistent")

def test_asset_independence():
    registry = AssetRegistry()
    registry.register("computer", Computer)
    
    comp1 = registry.create("computer")
    comp2 = registry.create("computer")
    
    assert comp1 is not comp2
    comp1.x = 100
    assert comp2.x == 0.0

def test_stick_figure_actions():
    sf = StickFigure()
    # Basic check that pose helpers run without error
    # We need an animation manager, but for just creation, we can mock it
    from unittest.mock import MagicMock
    from engine.animation import AnimationManager
    
    manager = MagicMock(spec=AnimationManager)
    
    sf.think(manager, 1.0)
    sf.celebrate(manager, 1.0)
    sf.idle(manager, 1.0)
    sf.enter(manager, 1.0)
    sf.exit(manager, 1.0)
    
    assert manager.add.called
    assert manager.animate.called

def test_svg_output():
    canvas = SVGCanvas()
    sf = StickFigure()
    comp = Computer()
    
    canvas.add(sf)
    canvas.add(comp)
    
    svg = canvas.to_svg()
    assert "<svg" in svg
    assert "<g" in svg # StickFigure and Computer are Groups
