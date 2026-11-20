"""Read timestamped captions via jdepoix/youtube-transcript-api (1.x)."""
import argparse
import json
import os
from pathlib import Path
import re
import tempfile
from urllib.parse import parse_qs, urlsplit


def video_id(value):
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", value):
        return value
    parsed = urlsplit(value)
    parts = parsed.path.strip("/").split("/")
    if parsed.hostname == "youtu.be":
        result = parts[0]
    elif parsed.hostname in {"youtube.com", "www.youtube.com", "m.youtube.com", "www.youtube-nocookie.com"}:
        if parsed.path == "/watch":
            result = parse_qs(parsed.query).get("v", [""])[0]
        else:
            result = parts[1] if len(parts) == 2 and parts[0] in {"shorts", "embed", "live"} else ""
    else:
        result = ""
    if not re.fullmatch(r"[A-Za-z0-9_-]{11}", result):
        raise argparse.ArgumentTypeError("Use a YouTube watch URL or an 11-character video ID.")
    return result


def choose_track(tracks, languages):
    tracks = list(tracks)
    if not tracks:
        raise ValueError("The video lists no caption tracks.")
    def priority(track):
        code = track.language_code.casefold()
        for i, language in enumerate(languages):
            lang = language.casefold()
            if code == lang or code.startswith(lang + "-"):
                return i, track.is_generated
        return len(languages), track.is_generated
    return min(tracks, key=priority)


def retrieve(api, identifier, languages):
    selected = choose_track(api.list(identifier), languages)
    transcript = selected.fetch()
    segments = [dict(text=s.text, start=s.start, duration=s.duration, end=round(s.start+s.duration, 3))
                for s in transcript if s.text.strip()]
    if not segments:
        raise ValueError("The selected track is empty.")
    return {"video_id": identifier, "url": f"https://www.youtube.com/watch?v={identifier}",
            "language": selected.language_code, "is_generated": selected.is_generated,
            "segments": segments}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video", type=video_id)
    parser.add_argument("output", type=Path)
    parser.add_argument("--languages", nargs="+", default=["zh", "en"])
    args = parser.parse_args()
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError:
        parser.exit(2, "Install youtube-transcript-api>=1.2,<2 in this Python environment.\n")
    try:
        result = retrieve(YouTubeTranscriptApi(), args.video, args.languages)
    except Exception as error:
        parser.exit(1, f"{type(error).__name__}: {error}\n")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False,
                                     dir=args.output.parent) as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
        temp = Path(handle.name)
    try:
        os.replace(temp, args.output)
    finally:
        temp.unlink(missing_ok=True)
    print(f"{len(result['segments'])} segments; language={result['language']}; auto={result['is_generated']}")


if __name__ == "__main__":
    main()
