from __future__ import annotations

import pytest
import numpy as np

from engine.objects import Circle
from engine.renderer import RenderConfig, RenderDependencyError, SVGRenderer


def test_render_config_validation() -> None:
    with pytest.raises(ValueError, match="Width and height"):
        RenderConfig(width=0)

    with pytest.raises(ValueError, match="FPS"):
        RenderConfig(fps=0)

    with pytest.raises(ValueError, match="Quality"):
        RenderConfig(quality=99)

    with pytest.raises(ValueError, match="MP4"):
        RenderConfig(output_format="gif")


def test_render_duration_validation() -> None:
    renderer = SVGRenderer(RenderConfig(width=32, height=24, fps=10))

    with pytest.raises(ValueError, match="non-negative"):
        renderer.frame_count(-0.1)

    with pytest.raises(ValueError, match="finite"):
        renderer.frame_count(float("inf"))


@pytest.mark.parametrize(
    ("fps", "duration", "expected_frames", "expected_duration"),
    [
        (24, 1.0, 24, 1.0),
        (30, 0.5, 15, 0.5),
        (60, 1.25, 75, 1.25),
        (10, 0.25, 3, 0.3),
        (10, 0.0, 1, 0.1),
    ],
)
def test_frame_count_and_output_duration_are_deterministic(
    fps: int,
    duration: float,
    expected_frames: int,
    expected_duration: float,
) -> None:
    renderer = SVGRenderer(RenderConfig(width=32, height=24, fps=fps))

    assert renderer.frame_count(duration) == expected_frames
    assert renderer.output_duration(duration) == pytest.approx(expected_duration)


def test_renderer_produces_valid_svg_and_image_array() -> None:
    renderer = SVGRenderer(RenderConfig(width=32, height=24, fps=2))
    objects = [Circle(x=16, y=12, radius=6)]

    svg = renderer.render_svg(objects)

    assert svg.startswith("<svg")
    assert "<circle" in svg

    try:
        frames = renderer.render_frames(objects, duration=0.5)
    except RenderDependencyError as exc:
        pytest.skip(f"Cairo is unavailable in this environment: {exc}")

    assert len(frames) == 1
    assert frames[0].shape == (24, 32, 3)


def test_audio_path_validation_without_render(tmp_path) -> None:
    missing_audio = tmp_path / "missing.wav"

    with pytest.raises(FileNotFoundError, match="Audio file not found"):
        RenderConfig(audio_path=missing_audio)

    audio_file = tmp_path / "narration.wav"
    audio_file.write_bytes(b"placeholder")

    config = RenderConfig(audio_path=audio_file)

    assert config.audio_path == audio_file


def test_export_uses_audio_and_disabled_progress_without_real_ffmpeg(tmp_path, monkeypatch) -> None:
    audio_file = tmp_path / "narration.wav"
    audio_file.write_bytes(b"placeholder")
    renderer = SVGRenderer(RenderConfig(width=4, height=3, fps=4, audio_path=audio_file, enable_progress_reporting=False))
    render_times: list[float] = []

    class DummyAudioClip:
        def __init__(self, filename: str) -> None:
            self.filename = filename
            self.duration = 10.0
            self.trimmed_to: float | None = None
            self.closed = False

        def subclipped(self, start: float, end: float) -> "DummyAudioClip":
            self.trimmed_to = end - start
            self.duration = end - start
            return self

        def close(self) -> None:
            self.closed = True

    class DummyVideoClip:
        created: "DummyVideoClip | None" = None

        def __init__(self, make_frame, duration: float) -> None:
            self.make_frame = make_frame
            self.duration = duration
            self.audio = None
            self.write_kwargs = {}
            DummyVideoClip.created = self

        def with_audio(self, audio_clip: DummyAudioClip) -> "DummyVideoClip":
            self.audio = audio_clip
            return self

        def write_videofile(self, filename: str, **kwargs) -> None:
            self.write_kwargs = kwargs
            render_times.extend([0.0, 0.25])
            self.make_frame(0.0)
            self.make_frame(0.25)

        def close(self) -> None:
            pass

    monkeypatch.setattr(SVGRenderer, "_load_moviepy", staticmethod(lambda: (DummyVideoClip, DummyAudioClip)))
    monkeypatch.setattr(SVGRenderer, "svg_to_image", lambda _self, _svg: np.zeros((3, 4, 3), dtype=np.uint8))

    renderer.export_mp4(tmp_path / "out.mp4", [], duration=0.5)

    clip = DummyVideoClip.created
    assert clip is not None
    assert clip.duration == pytest.approx(0.5)
    assert clip.write_kwargs["logger"] is None
    assert clip.write_kwargs["audio"] is True
    assert clip.audio is not None
    assert clip.audio.trimmed_to == pytest.approx(0.5)
    assert render_times == [0.0, 0.25]
