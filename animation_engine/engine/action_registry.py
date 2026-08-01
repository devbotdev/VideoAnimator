
from typing import Any, Callable, Dict, List, Type


class ActionRegistry:
    def __init__(self):
        self._actions = {}

    def register(
        self,
        name: str,
        parameters: Dict[str, Type],
        compatible_targets: List[str],
        executor: Callable,
        extra_parameters: List[str] | None = None,
    ):
        self._actions[name] = {
            "parameters": parameters,
            "compatible_targets": compatible_targets,
            "executor": executor,
            "extra_parameters": extra_parameters or [],
        }

    def populate_defaults(self):
        def _animation_kwargs(duration: float, start_time: float | None = None, easing: str = "linear", repeat: int | None = None, yoyo: bool = False) -> Dict[str, Any]:
            kwargs: Dict[str, Any] = {"duration": float(duration), "easing": easing}
            if repeat is not None:
                kwargs["repeat"] = repeat
            if yoyo:
                kwargs["yoyo"] = True
            if start_time is not None:
                kwargs["start_time"] = float(start_time)
            return kwargs

        def _move(manager, t, duration, start_time=None, x=None, y=None, dx=None, dy=None, **_kwargs):
            start_x = getattr(t, "x")
            start_y = getattr(t, "y")
            end_x = float(x) if x is not None else start_x + float(dx or 0.0)
            end_y = float(y) if y is not None else start_y + float(dy or 0.0)
            return [
                manager.animate(t, "x", start_x, end_x, **_animation_kwargs(duration, start_time=start_time)),
                manager.animate(t, "y", start_y, end_y, **_animation_kwargs(duration, start_time=start_time)),
            ]

        def _fade(manager, t, duration, start_time=None, end_value: float = 1.0):
            return [manager.animate(t, "opacity", getattr(t, "opacity"), end_value, **_animation_kwargs(duration, start_time=start_time))]

        def _scale(manager, t, duration, start_time=None, scale=None, **_kwargs):
            target_scale = float(scale) if scale is not None else getattr(t, "scale")
            return [manager.animate(t, "scale", getattr(t, "scale"), target_scale, **_animation_kwargs(duration, start_time=start_time))]

        def _grow(manager, t, duration, start_time=None, factor=None, **_kwargs):
            target_factor = float(factor) if factor is not None else 1.0
            return [manager.animate(t, "scale", getattr(t, "scale"), getattr(t, "scale") * target_factor, **_animation_kwargs(duration, start_time=start_time))]

        def _rotate(manager, t, duration, start_time=None, angle=None, **_kwargs):
            target_angle = float(angle) if angle is not None else getattr(t, "rotation")
            return [manager.animate(t, "rotation", getattr(t, "rotation"), target_angle, **_animation_kwargs(duration, start_time=start_time))]

        def _draw(manager, t, duration, start_time=None, **_kwargs):
            return [manager.animate(t, "opacity", 0.0, getattr(t, "opacity"), **_animation_kwargs(duration, start_time=start_time))]

        def _highlight(manager, t, duration, start_time=None, factor: float = 1.1, **_kwargs):
            start_scale = getattr(t, "scale")
            end_scale = start_scale * float(factor)
            return [manager.animate(t, "scale", start_scale, end_scale, **_animation_kwargs(duration, start_time=start_time, repeat=1, yoyo=True))]

        def _shake(manager, t, duration, start_time=None, amplitude: float = 8.0, **_kwargs):
            start_x = getattr(t, "x")
            start_y = getattr(t, "y")
            return [
                manager.animate(t, "x", start_x, start_x + float(amplitude), **_animation_kwargs(duration, start_time=start_time, repeat=1, yoyo=True)),
                manager.animate(t, "y", start_y, start_y + float(amplitude) / 2.0, **_animation_kwargs(duration, start_time=start_time, repeat=1, yoyo=True)),
            ]

        def _camera_pan(manager, t, duration, start_time=None, x=None, y=None, **_kwargs):
            start_x = getattr(t, "x")
            start_y = getattr(t, "y")
            end_x = float(x) if x is not None else start_x
            end_y = float(y) if y is not None else start_y
            return [
                manager.animate(t, "x", start_x, end_x, **_animation_kwargs(duration, start_time=start_time)),
                manager.animate(t, "y", start_y, end_y, **_animation_kwargs(duration, start_time=start_time)),
            ]

        def _camera_zoom(manager, t, duration, start_time=None, zoom=None, **_kwargs):
            target_zoom = float(zoom) if zoom is not None else getattr(t, "zoom")
            return [manager.animate(t, "zoom", getattr(t, "zoom"), target_zoom, **_animation_kwargs(duration, start_time=start_time))]

        def _camera_focus(manager, t, duration, start_time=None, x=None, y=None, **_kwargs):
            start_x = getattr(t, "x")
            start_y = getattr(t, "y")
            end_x = float(x) if x is not None else start_x
            end_y = float(y) if y is not None else start_y
            return [
                manager.animate(t, "x", start_x, end_x, **_animation_kwargs(duration, start_time=start_time)),
                manager.animate(t, "y", start_y, end_y, **_animation_kwargs(duration, start_time=start_time)),
            ]

        def _walk(manager, t, duration, start_time=None, distance=160.0, easing="ease-in-out", **_kwargs):
            return t.walk(manager, duration, distance=float(distance), easing=easing)

        def _point(manager, t, duration, start_time=None, arm="right", easing="ease-out", **_kwargs):
            return t.point(manager, duration, arm=arm, easing=easing)

        def _wave(manager, t, duration, start_time=None, arm="right", easing="ease-in-out", **_kwargs):
            return t.wave(manager, duration, arm=arm, easing=easing)

        self.register(
            "walk",
            {"duration": float},
            ["StickFigure"],
            _walk,
            extra_parameters=["distance", "easing", "start_time"],
        )
        self.register(
            "move",
            {"duration": float},
            ["BaseObject", "Rectangle", "Circle", "Line", "Polyline", "Path", "Text", "Group", "StickFigure", "Arrow"],
            lambda manager, t, duration, start_time=None, **_kwargs: _move(manager, t, duration, start_time=start_time, x=_kwargs.get("x"), y=_kwargs.get("y"), dx=_kwargs.get("dx"), dy=_kwargs.get("dy")),
            extra_parameters=["x", "y", "dx", "dy", "start_time"],
        )
        self.register(
            "point",
            {"duration": float},
            ["StickFigure"],
            _point,
            extra_parameters=["arm", "easing", "start_time"],
        )
        self.register(
            "wave",
            {"duration": float},
            ["StickFigure"],
            _wave,
            extra_parameters=["arm", "easing", "start_time"],
        )

        self.register(
            "fade_in",
            {"duration": float},
            ["BaseObject", "Rectangle", "Circle", "Line", "Polyline", "Path", "Text", "Group", "StickFigure", "Arrow"],
            lambda manager, t, duration, start_time=None, **_kwargs: _fade(manager, t, duration, start_time=start_time, end_value=1.0),
            extra_parameters=["start_time"],
        )

        self.register(
            "fade_out",
            {"duration": float},
            ["BaseObject", "Rectangle", "Circle", "Line", "Polyline", "Path", "Text", "Group", "StickFigure", "Arrow"],
            lambda manager, t, duration, start_time=None, **_kwargs: _fade(manager, t, duration, start_time=start_time, end_value=0.0),
            extra_parameters=["start_time"],
        )

        self.register(
            "scale",
            {"duration": float},
            ["BaseObject", "Rectangle", "Circle", "Line", "Polyline", "Path", "Text", "Group", "StickFigure", "Arrow"],
            lambda manager, t, duration, start_time=None, **_kwargs: _scale(manager, t, duration, start_time=start_time, scale=_kwargs.get("scale")),
            extra_parameters=["scale", "start_time"],
        )

        self.register(
            "grow",
            {"duration": float},
            ["BaseObject", "Rectangle", "Circle", "Line", "Polyline", "Path", "Text", "Group", "StickFigure", "Arrow"],
            lambda manager, t, duration, start_time=None, **_kwargs: _grow(manager, t, duration, start_time=start_time, factor=_kwargs.get("factor")),
            extra_parameters=["factor", "start_time"],
        )

        self.register(
            "rotate",
            {"duration": float},
            ["BaseObject", "Rectangle", "Circle", "Line", "Polyline", "Path", "Text", "Group", "StickFigure", "Arrow"],
            lambda manager, t, duration, start_time=None, **_kwargs: _rotate(manager, t, duration, start_time=start_time, angle=_kwargs.get("angle")),
            extra_parameters=["angle", "start_time"],
        )

        self.register(
            "draw",
            {"duration": float},
            ["Path"],
            lambda manager, t, duration, start_time=None, **_kwargs: _draw(manager, t, duration, start_time=start_time),
            extra_parameters=["start_time"],
        )
        self.register(
            "highlight",
            {"duration": float},
            ["BaseObject"],
            lambda manager, t, duration, start_time=None, **_kwargs: _highlight(manager, t, duration, start_time=start_time, factor=_kwargs.get("factor", 1.1)),
            extra_parameters=["factor", "start_time"],
        )
        self.register(
            "shake",
            {"duration": float},
            ["BaseObject"],
            lambda manager, t, duration, start_time=None, **_kwargs: _shake(manager, t, duration, start_time=start_time, amplitude=_kwargs.get("amplitude", 8.0)),
            extra_parameters=["amplitude", "start_time"],
        )

        self.register(
            "camera_pan",
            {"duration": float},
            ["Camera"],
            lambda manager, t, duration, start_time=None, **_kwargs: _camera_pan(manager, t, duration, start_time=start_time, x=_kwargs.get("x"), y=_kwargs.get("y")),
            extra_parameters=["x", "y", "start_time"],
        )

        self.register(
            "camera_zoom",
            {"duration": float},
            ["Camera"],
            lambda manager, t, duration, start_time=None, **_kwargs: _camera_zoom(manager, t, duration, start_time=start_time, zoom=_kwargs.get("zoom")),
            extra_parameters=["zoom", "start_time"],
        )

        self.register(
            "camera_focus",
            {"duration": float},
            ["Camera"],
            lambda manager, t, duration, start_time=None, **_kwargs: _camera_focus(manager, t, duration, start_time=start_time, x=_kwargs.get("x"), y=_kwargs.get("y")),
            extra_parameters=["x", "y", "start_time"],
        )

    def validate(self, action_name: str, params: Dict[str, Any], target_type: str, scene_id: str, action_index: int, target_id: str):
        if action_name not in self._actions:
            raise ValueError(f"Action '{action_name}' is not registered.")

        action_meta = self._actions[action_name]

        if target_type not in action_meta["compatible_targets"]:
            raise ValueError(f"Action '{action_name}' is not compatible with target type '{target_type}'. (Scene: {scene_id}, Action Index: {action_index}, Target ID: {target_id})")

        if action_name == "move":
            if "duration" not in params:
                raise ValueError(f"Action '{action_name}' missing parameter 'duration'. (Scene: {scene_id}, Action Index: {action_index}, Target ID: {target_id})")
            if "x" in params and "y" in params:
                for param_name in ("x", "y"):
                    if not isinstance(params[param_name], float):
                        raise ValueError(f"Action '{action_name}' parameter '{param_name}' must be float, got {type(params[param_name]).__name__}. (Scene: {scene_id}, Action Index: {action_index}, Target ID: {target_id})")
            elif "dx" in params and "dy" in params:
                for param_name in ("dx", "dy"):
                    if not isinstance(params[param_name], float):
                        raise ValueError(f"Action '{action_name}' parameter '{param_name}' must be float, got {type(params[param_name]).__name__}. (Scene: {scene_id}, Action Index: {action_index}, Target ID: {target_id})")
            elif "x" not in params and "dx" not in params:
                raise ValueError(f"Action '{action_name}' missing parameter 'x'. (Scene: {scene_id}, Action Index: {action_index}, Target ID: {target_id})")
            elif "y" not in params and "dy" not in params:
                raise ValueError(f"Action '{action_name}' missing parameter 'y'. (Scene: {scene_id}, Action Index: {action_index}, Target ID: {target_id})")

        for param_name, param_type in action_meta["parameters"].items():
            if param_name not in params:
                raise ValueError(f"Action '{action_name}' missing parameter '{param_name}'. (Scene: {scene_id}, Action Index: {action_index}, Target ID: {target_id})")

            if not isinstance(params[param_name], param_type):
                raise ValueError(f"Action '{action_name}' parameter '{param_name}' must be {param_type.__name__}, got {type(params[param_name]).__name__}. (Scene: {scene_id}, Action Index: {action_index}, Target ID: {target_id})")

        allowed_parameters = set(action_meta["parameters"]) | set(action_meta["extra_parameters"])
        for param_name in params:
            if param_name not in allowed_parameters:
                raise ValueError(f"Action '{action_name}' received unknown parameter '{param_name}'. (Scene: {scene_id}, Action Index: {action_index}, Target ID: {target_id})")

        return True

    def is_action_registered(self, name: str) -> bool:
        return name in self._actions

    def execute(self, action_name: str, manager: Any, target: Any, params: Dict[str, Any]):
        action_params = dict(params)
        start_time = action_params.pop("start_time", None)
        executor = self._actions[action_name]["executor"]
        if start_time is not None:
            return executor(manager, target, start_time=start_time, **action_params)
        return executor(manager, target, **action_params)
