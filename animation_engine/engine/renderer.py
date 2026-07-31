"""Rendering entry points for vector animation output."""

from __future__ import annotations

import io
import math
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from .animation import AnimationManager
from .canvas import SVGCanvas
from .camera import Camera
from .objects import BaseObject
from .scene import Scene, SceneManager
from .transition import SceneFrame


class RenderDependencyError(RuntimeError):
    """Raised when an optional rendering dependency is not available."""


@dataclass(slots=True)
class RenderConfig:
    """Configuration for rendering and exporting."""

    width: int = 1920
    height: int = 1080
    fps: int = 30
    background: str = "#ffffff"
    codec: str = "libx264"
    quality: int | None = 20
    preset: str = "slow"
    output_format: str = "mp4"
    audio_path: Path | None = None
    debug_export_frames: bool = False
    debug_frames_dir: Path | None = None
    enable_progress_reporting: bool = True

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Width and height must be positive.")
        if self.fps <= 0:
            raise ValueError("FPS must be positive.")
        if self.quality is not None and not 0 <= self.quality <= 51:
            raise ValueError("Quality must be a CRF value from 0 to 51 when provided.")
        self.output_format = self.output_format.lower().lstrip(".")
        if self.output_format != "mp4":
            raise ValueError("Only MP4 output is currently supported.")
        if self.audio_path is not None:
            self.audio_path = Path(self.audio_path)
        if self.debug_frames_dir is not None:
            self.debug_frames_dir = Path(self.debug_frames_dir)
        if self.audio_path and not self.audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {self.audio_path}")


@dataclass(slots=True)
class SVGRenderer:
    """Render engine objects to SVG frames and export them as video."""

    config: RenderConfig

    def __init__(self, config: RenderConfig | None = None, **kwargs):
        if config:
            self.config = config
        else:
            self.config = RenderConfig(**kwargs)

    def render_svg(self, objects: list[BaseObject]) -> str:
        """Render a single SVG frame from a list of objects."""
        return self.render_frame(
            SceneFrame(
                objects=objects,
                camera=Camera(width=self.config.width, height=self.config.height),
                background=self.config.background,
            )
        )

    def render_frame(self, frame: SceneFrame) -> str:
        """Render a resolved scene frame into SVG markup."""
        canvas = SVGCanvas(
            width=self.config.width,
            height=self.config.height,
            background=frame.background,
            camera=frame.camera,
        )
        return canvas.to_svg(frame.objects)

    def svg_to_image(self, svg_markup: str) -> np.ndarray:
        """Convert SVG markup into an RGB image array."""
        cairosvg = self._load_cairosvg()
        try:
            png_bytes = cairosvg.svg2png(bytestring=svg_markup.encode("utf-8"))
        except (OSError, ImportError) as exc:
            raise RenderDependencyError(
                "CairoSVG is installed, but Cairo could not render this SVG. "
                "Install the native Cairo library and ensure it is available on PATH."
            ) from exc
        with Image.open(io.BytesIO(png_bytes)) as image:
            return np.array(image.convert("RGB"))

    @staticmethod
    def frame_count_for_duration(duration: float, fps: int) -> int:
        """Return the deterministic frame count for a duration/FPS pair."""
        SVGRenderer._validate_duration(duration)
        if fps <= 0:
            raise ValueError("FPS must be positive.")
        return max(1, int(math.floor(duration * fps + 0.5)))

    def frame_count(self, duration: float) -> int:
        """Return the frame count for the renderer's configured FPS."""
        return self.frame_count_for_duration(duration, self.config.fps)

    def output_duration(self, duration: float) -> float:
        """Return the exact video duration implied by frame count and FPS."""
        return self.frame_count(duration) / self.config.fps

    def render_frames(
        self,
        objects: list[BaseObject],
        duration: float,
        animation_manager: AnimationManager | None = None,
    ) -> list[np.ndarray]:
        """Render all frames for a scene duration."""
        return list(self.iter_frames(objects, duration, animation_manager))

    def iter_frames(
        self,
        objects: list[BaseObject],
        duration: float,
        animation_manager: AnimationManager | None = None,
    ) -> Iterator[np.ndarray]:
        """Yield rendered object frames without keeping the full sequence in memory."""
        frame_time = 1.0 / self.config.fps

        def update() -> None:
            if animation_manager is not None:
                animation_manager.update(frame_time)

        yield from self._iter_images(duration, lambda: self.render_svg(objects), update)

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
        frame_time = 1.0 / self.config.fps

        def update() -> None:
            if animation_manager is not None:
                animation_manager.update(frame_time)

        return self._export_mp4(output, duration, lambda: self.render_svg(objects), update)

    def render_scene(self, scene: Scene, duration: float) -> list[np.ndarray]:
        """Render all frames for a scene."""
        return list(self.iter_scene_frames(scene, duration))

    def iter_scene_frames(self, scene: Scene, duration: float) -> Iterator[np.ndarray]:
        """Yield rendered scene frames without keeping the full sequence in memory."""
        frame_time = 1.0 / self.config.fps
        yield from self._iter_images(duration, lambda: self.render_frame(scene.frame()), lambda: scene.update(frame_time))

    def export_scene_mp4(self, output_path: str | Path, scene: Scene, duration: float) -> Path:
        """Export a scene directly to MP4."""
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        frame_time = 1.0 / self.config.fps
        return self._export_mp4(output, duration, lambda: self.render_frame(scene.frame()), lambda: scene.update(frame_time))

    def export_scene_manager_mp4(
        self,
        output_path: str | Path,
        scene_manager: SceneManager,
        duration: float,
    ) -> Path:
        """Export a scene manager with transitions to MP4."""
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        frame_time = 1.0 / self.config.fps
        return self._export_mp4(
            output,
            duration,
            lambda: self.render_frame(scene_manager.frame()),
            lambda: scene_manager.update(frame_time),
        )

    @staticmethod
    def _validate_duration(duration: float) -> None:
        if duration < 0:
            raise ValueError("Render duration must be non-negative.")
        if not math.isfinite(duration):
            raise ValueError("Render duration must be finite.")

    @staticmethod
    def _load_cairosvg() -> Any:
        try:
            import cairosvg
        except (ImportError, OSError) as exc:
            raise RenderDependencyError(
                "CairoSVG is required to convert SVG frames to images. "
                "Install cairosvg and the native Cairo library."
            ) from exc
        return cairosvg

    @staticmethod
    def _load_moviepy() -> tuple[type[Any], type[Any]]:
        try:
            from moviepy import AudioFileClip, VideoClip
        except ImportError as exc:
            raise RenderDependencyError("MoviePy is required for MP4 export.") from exc
        return VideoClip, AudioFileClip

    def _iter_images(
        self,
        duration: float,
        svg_factory: Callable[[], str],
        update: Callable[[], None],
        debug_dir: Path | None = None,
    ) -> Iterator[np.ndarray]:
        total_frames = self.frame_count(duration)
        for frame_index in range(total_frames):
            if frame_index > 0:
                update()
            image = self.svg_to_image(svg_factory())
            if self.config.debug_export_frames:
                self._save_debug_frame(image, frame_index, debug_dir or self.config.debug_frames_dir)
            yield image

    def _export_mp4(
        self,
        output: Path,
        duration: float,
        svg_factory: Callable[[], str],
        update: Callable[[], None],
    ) -> Path:
        VideoClip, AudioFileClip = self._load_moviepy()
        total_frames = self.frame_count(duration)
        effective_duration = total_frames / self.config.fps
        debug_dir = self.config.debug_frames_dir or output.parent / f"{output.stem}_frames"
        current_index = -1
        current_image: np.ndarray | None = None

        def make_frame(time_position: float) -> np.ndarray:
            nonlocal current_index, current_image
            # Map time to requested frame index
            requested_index = min(int(math.floor(time_position * self.config.fps + 1e-9)), total_frames - 1)
            
            # If we've already rendered this frame, return it immediately
            if current_index == requested_index and current_image is not None:
                return current_image
                
            # If we are requested an earlier frame, we cannot seek backward in this streaming model
            if requested_index < current_index:
                if current_image is not None:
                    return current_image
                raise RuntimeError("MoviePy requested frames out of order; streaming renderer cannot seek backward.")
                
            # Advance the state and render frame-by-frame up to the requested index
            while current_index < requested_index:
                # Before rendering the next frame, advance the scene/animation state
                update()
                current_index += 1
                current_image = self.svg_to_image(svg_factory())
                if self.config.debug_export_frames:
                    self._save_debug_frame(current_image, current_index, debug_dir)
            
            # If this is the first frame (index 0), render it now
            if current_index == -1:
                current_index = 0
                current_image = self.svg_to_image(svg_factory())
                if self.config.debug_export_frames:
                    self._save_debug_frame(current_image, current_index, debug_dir)
                    
            return current_image

        clip = VideoClip(make_frame, duration=effective_duration)
        audio_clip = None
        try:
            if self.config.audio_path is not None:
                audio_clip = AudioFileClip(str(self.config.audio_path))
                if audio_clip.duration and audio_clip.duration > effective_duration:
                    audio_clip = audio_clip.subclipped(0, effective_duration)
                clip = clip.with_audio(audio_clip)
            ffmpeg_params = ["-crf", str(self.config.quality)] if self.config.quality is not None else None
            clip.write_videofile(
                str(output),
                fps=self.config.fps,
                codec=self.config.codec,
                preset=self.config.preset,
                audio=self.config.audio_path is not None,
                ffmpeg_params=ffmpeg_params,
                logger="bar" if self.config.enable_progress_reporting else None,
            )
        except FileNotFoundError as exc:
            raise RenderDependencyError("FFmpeg is required for MP4 export but was not found.") from exc
        except OSError as exc:
            if "ffmpeg" in str(exc).lower():
                raise RenderDependencyError("FFmpeg failed during MP4 export. Check that FFmpeg is installed.") from exc
            raise
        finally:
            if audio_clip is not None:
                audio_clip.close()
            clip.close()
        return output

    @staticmethod
    def _save_debug_frame(image: np.ndarray, frame_index: int, debug_dir: Path | None) -> None:
        target_dir = debug_dir or Path("debug_frames")
        target_dir.mkdir(parents=True, exist_ok=True)
        Image.fromarray(image).save(target_dir / f"frame_{frame_index:06d}.png")
