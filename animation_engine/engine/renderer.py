"""Rendering entry points for vector animation output."""

from __future__ import annotations

import io
from dataclasses import dataclass
from pathlib import Path

import cairosvg
import numpy as np
from moviepy import ImageSequenceClip
from PIL import Image

from .animation import AnimationManager
from .canvas import SVGCanvas
from .camera import Camera
from .objects import BaseObject
from .scene import Scene, SceneManager
from .transition import SceneFrame


@dataclass(slots=True)
class SVGRenderer:
    """Render engine objects to SVG frames and export them as video."""

    width: int = 1920
    height: int = 1080
    fps: int = 30
    background: str = "#ffffff"

    def render_svg(self, objects: list[BaseObject]) -> str:
        """Render a single SVG frame from a list of objects."""
        return self.render_frame(
            SceneFrame(
                objects=objects,
                camera=Camera(width=self.width, height=self.height),
                background=self.background,
            )
        )

    def render_frame(self, frame: SceneFrame) -> str:
        """Render a resolved scene frame into SVG markup."""
        canvas = SVGCanvas(
            width=self.width,
            height=self.height,
            background=frame.background,
            camera=frame.camera,
        )
        return canvas.to_svg(frame.objects)

    def svg_to_image(self, svg_markup: str) -> np.ndarray:
        """Convert SVG markup into an RGB image array."""
        png_bytes = cairosvg.svg2png(bytestring=svg_markup.encode("utf-8"))
        with Image.open(io.BytesIO(png_bytes)) as image:
            return np.array(image.convert("RGB"))

    def render_frames(
        self,
        objects: list[BaseObject],
        duration: float,
        animation_manager: AnimationManager | None = None,
    ) -> list[np.ndarray]:
        """Render all frames for a scene duration."""
        total_frames = max(1, int(round(duration * self.fps)) + 1)
        frame_time = 1.0 / self.fps
        frames: list[np.ndarray] = []

        for frame_index in range(total_frames):
            if frame_index > 0 and animation_manager is not None:
                animation_manager.update(frame_time)
            svg_markup = self.render_svg(objects)
            frames.append(self.svg_to_image(svg_markup))

        return frames

    def export_mp4(
        self,
        output_path: str | Path,
        objects: list[BaseObject],
        duration: float,
        animation_manager: AnimationManager | None = None,
    ) -> Path:
        """Export a scene as an MP4 video."""
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        frames = self.render_frames(objects, duration, animation_manager)
        clip = ImageSequenceClip(frames, fps=self.fps)
        clip.write_videofile(str(output), codec="libx264", audio=False, logger=None)
        clip.close()
        return output

    def render_scene(self, scene: Scene, duration: float) -> list[np.ndarray]:
        """Render all frames for a scene."""
        total_frames = max(1, int(round(duration * self.fps)) + 1)
        frame_time = 1.0 / self.fps
        frames: list[np.ndarray] = []

        for frame_index in range(total_frames):
            if frame_index > 0:
                scene.update(frame_time)
            frames.append(self.svg_to_image(self.render_frame(scene.frame())))

        return frames

    def export_scene_mp4(self, output_path: str | Path, scene: Scene, duration: float) -> Path:
        """Export a scene directly to MP4."""
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        frames = self.render_scene(scene, duration)
        clip = ImageSequenceClip(frames, fps=self.fps)
        clip.write_videofile(str(output), codec="libx264", audio=False, logger=None)
        clip.close()
        return output

    def export_scene_manager_mp4(
        self,
        output_path: str | Path,
        scene_manager: SceneManager,
        duration: float,
    ) -> Path:
        """Export a scene manager with transitions to MP4."""
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        total_frames = max(1, int(round(duration * self.fps)) + 1)
        frame_time = 1.0 / self.fps
        frames: list[np.ndarray] = []

        for frame_index in range(total_frames):
            if frame_index > 0:
                scene_manager.update(frame_time)
            frames.append(self.svg_to_image(self.render_frame(scene_manager.frame())))

        clip = ImageSequenceClip(frames, fps=self.fps)
        clip.write_videofile(str(output), codec="libx264", audio=False, logger=None)
        clip.close()
        return output
