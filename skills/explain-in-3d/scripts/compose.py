"""Compose authored 3D shots, measured speech and captions into H.264/AAC."""
import argparse
import importlib.util
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import wave
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFont


def run(command):
    return subprocess.run(command, capture_output=True, check=True).stdout


@lru_cache(maxsize=8)
def get_font(name, size):
    return ImageFont.truetype(name, size)


def wrap(text, font, width):
    lines, line = [], ""
    for character in text:
        if character == "\n" or (line and font.getlength(line + character) > width):
            lines.append(line)
            line = ""
        if character != "\n":
            line += character
    return lines + ([line] if line else [])


def caption_frame(image, text, font_path):
    width, height = image.size
    font = get_font(font_path, max(16, round(min(width, height) * 0.04)))
    lines = wrap(text, font, width * .86)
    if len(lines) > 2:
        raise ValueError(f"Shorten or time-split this caption: {text}")
    draw = ImageDraw.Draw(image)
    baseline = height * .935
    for i, line in enumerate(reversed(lines)):
        draw.text((width / 2, baseline - i * font.size * 1.4), line, font=font,
                  anchor="ms", fill="#ffffff", stroke_width=max(1, font.size // 11),
                  stroke_fill="#101920")


def stamp(milliseconds):
    seconds, ms = divmod(milliseconds, 1000)
    minutes, sec = divmod(seconds, 60)
    hour, minute = divmod(minutes, 60)
    return f"{hour:02}:{minute:02}:{sec:02},{ms:03}"


def captions_for(shot, duration):
    cues = shot.get("captions", [[0, duration, shot["line"]]])
    previous = 0
    for start, end, words in cues:
        if not (previous <= start < end <= duration + .001 and words.strip()):
            raise ValueError(f"Invalid caption timing in {shot['id']}")
        previous = end
    return cues


def sound_mix(tracks, root, film_seconds):
    if not tracks:
        return []
    inputs = []
    filters = ["[1:a]aresample=48000,aformat=channel_layouts=stereo[voice]"]
    labels = ["[voice]"]
    for index, track in enumerate(tracks):
        kind = track["kind"]
        if kind not in ("music", "sfx"):
            raise ValueError(f"Expected a music or sfx stem, got {kind}")
        start = float(track.get("start", 0))
        duration = float(track.get("duration", film_seconds - start))
        gain = float(track.get("gain_db", -18 if kind == "music" else -12))
        if not 0 <= start < film_seconds or not math.isfinite(duration) or duration <= 0 or not math.isfinite(gain):
            raise ValueError(f"Invalid timing or gain for {track['file']}")
        duration = min(duration, film_seconds - start)
        if track.get("loop"):
            inputs.extend(["-stream_loop", "-1"])
        inputs.extend(["-i", str((root / track["file"]).resolve(strict=True))])
        label = f"[stem{index}]"
        filters.append(f"[{index+2}:a]aresample=48000,aformat=channel_layouts=stereo,"
                       f"atrim=duration={duration:.6f},asetpts=PTS-STARTPTS,volume={gain:.3f}dB,"
                       f"adelay={round(start*48000)}S:all=1{label}")
        labels.append(label)
    filters.append(f"{''.join(labels)}amix=inputs={len(labels)}:duration=first:normalize=0,"
                   "alimiter=limit=0.95:level=0:latency=1[mix]")
    return inputs + ["-filter_complex", ";".join(filters), "-map", "0:v:0", "-map", "[mix]"]


def get_frames(shot, count, fps, size, root, renderer):
    if "clip" not in shot:
        if renderer is None:
            raise ValueError(f"Missing renderer or clip for {shot['id']}")
        for index in range(count):
            frame = renderer(shot, index / max(1, count - 1), size)
            if frame.size != size:
                raise ValueError(f"Unexpected frame size {frame.size}")
            yield frame.convert("RGB")
        return
    width, height = size
    path = (root / shot["clip"]).resolve(strict=True)
    filters = f"fps={fps},scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2"
    if shot.get("hold_last"):
        filters += f",tpad=stop_mode=clone:stop_duration={count/fps:.6f}"
    with subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(path), "-an", "-vf", filters,
                           "-frames:v", str(count), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                          stdout=subprocess.PIPE) as reader:
        try:
            for _ in range(count):
                pixels = reader.stdout.read(width * height * 3)
                if len(pixels) != width * height * 3:
                    raise ValueError(f"Clip too short for narration: {path.name}")
                yield Image.frombytes("RGB", size, pixels)
        finally:
            reader.stdout.close()
        if reader.wait():
            raise RuntimeError(f"Could not decode {path}")


def compose(manifest, output):
    root = manifest.resolve().parent
    plan = json.loads(manifest.read_text(encoding="utf-8-sig"))
    size, fps = tuple(plan["size"]), plan.get("fps", 24)
    if len(size) != 2 or any(not isinstance(x, int) or x <= 0 or x % 2 for x in size):
        raise ValueError("Use positive even output dimensions")
    if not isinstance(fps, int) or not 1 <= fps <= 120 or not plan["shots"]:
        raise ValueError("Provide shots and an integer frame rate from 1 to 120")
    if len({s["id"] for s in plan["shots"]}) != len(plan["shots"]):
        raise ValueError("Shot IDs must be unique")
    font_path = str((root / plan["font"]).resolve(strict=True))
    renderer = None
    if plan.get("renderer"):
        spec = importlib.util.spec_from_file_location("authored_scene", root / plan["renderer"])
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        renderer = module.render
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent) as work:
        work = Path(work)
        audio_path = work / "speech.wav"
        schedule, subtitles, timeline = [], [], 0
        with wave.open(str(audio_path), "wb") as track:
            track.setparams((1, 2, 48000, 0, "NONE", "not compressed"))
            for shot in plan["shots"]:
                audio = run(["ffmpeg", "-v", "error", "-i", str((root / shot["audio"]).resolve(strict=True)),
                             "-map", "0:a:0", "-ac", "1", "-ar", "48000", "-f", "s16le", "-"])
                seconds = len(audio) / 96000
                if seconds <= 0:
                    raise ValueError(f"Empty audio in {shot['id']}")
                tail = float(shot.get("tail", .25))
                if not math.isfinite(tail) or tail < 0:
                    raise ValueError(f"Invalid hold duration in {shot['id']}")
                frames = math.ceil((seconds + tail) * fps)
                cues = captions_for(shot, seconds)
                schedule.append((shot, frames, cues))
                for start, end, words in cues:
                    t0, t1 = [stamp(round((timeline / fps + t) * 1000)) for t in (start, end)]
                    subtitles.append(f"{len(subtitles)+1}\n{t0} --> {t1}\n{words}\n")
                track.writeframesraw(audio)
                total_samples = round((timeline + frames) / fps * 48000) - round(timeline / fps * 48000)
                track.writeframesraw(bytes((total_samples - len(audio) // 2) * 2))
                timeline += frames
        final = work / "result.mp4"
        width, height = size
        command = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pixel_format", "rgb24",
                   "-video_size", f"{width}x{height}", "-framerate", str(fps), "-i", "-",
                   "-i", str(audio_path), *sound_mix(plan.get("tracks", []), root, timeline / fps),
                   "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                   "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(final)]
        with subprocess.Popen(command, stdin=subprocess.PIPE) as encoder:
            try:
                for shot, count, cues in schedule:
                    for index, image in enumerate(get_frames(shot, count, fps, size, root, renderer)):
                        now = index / fps
                        for start, end, words in cues:
                            if start <= now < end:
                                caption_frame(image, words, font_path)
                                break
                        encoder.stdin.write(image.tobytes())
            finally:
                encoder.stdin.close()
            if encoder.wait():
                raise RuntimeError("Video encoding failed")
        srt = work / "result.srt"
        srt.write_text("\n".join(subtitles), encoding="utf-8")
        os.replace(final, output)
        os.replace(srt, output.with_suffix(".srt"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    if not shutil.which("ffmpeg"):
        parser.error("Add FFmpeg to PATH")
    if args.output.suffix.lower() != ".mp4":
        parser.error("Use an .mp4 output path")
    compose(args.manifest, args.output)
