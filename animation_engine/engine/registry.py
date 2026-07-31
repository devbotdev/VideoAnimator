"""Asset registry for the animation engine."""

from __future__ import annotations

from typing import Callable, Dict, TypeVar

from .objects import Group

T = TypeVar("T", bound=Group)


class AssetRegistry:
    """Central registry for reusable asset factories."""

    def __init__(self) -> None:
        self._factories: Dict[str, Callable[[], Group]] = {}

    def register(self, name: str, factory: Callable[[], Group]) -> None:
        """Register an asset factory."""
        self._factories[name] = factory

    def create(self, name: str) -> Group:
        """Create a new instance of an asset by name."""
        if name not in self._factories:
            raise ValueError(f"Asset '{name}' not registered.")
        return self._factories[name]()
