# Production notes

## Source intake

For a YouTube input, install `youtube-transcript-api>=1.2,<2` in the Python environment used to run the reader. The script takes a URL or video ID and a destination JSON path.

```sh
python -m pip install "youtube-transcript-api>=1.2,<2"
python scripts/read_youtube.py VIDEO_URL source/transcript.json --languages en zh
```

Set language priority to match the speaker. The default is Chinese, then English, then another available original track. Among equivalent language matches, manual captions take priority. Check `video_id`, `language`, `is_generated` and the nonempty `segments` array. Each segment contains text, start, duration and end in seconds. Captions can omit on-screen prompts or actions. Verify those against frames before attributing them to the creator.

If yt-dlp is already available, use `yt-dlp --list-subs URL` to inspect language codes. Then use `yt-dlp --skip-download --write-subs --write-auto-subs --sub-langs CODE --sub-format vtt URL`. A connection failure leaves caption availability unknown. If captions are absent and an authorized media file is available, transcribe it locally and identify the result as machine transcription.

## Plan each shot

Record the source passage or timestamp, viewer question, object ID, starting state, trigger, result, camera route, narration, sound cue and one frame that would prove the point. Give every shot a recognizable connection to the last. Keep units and axis scales stable in comparisons. Put a label on artistic reconstructions, invented example records and visual metaphors.

For generated shots, first approve a subject reference and location view. Specify opening and closing states, one action, camera position and framing, direction of motion, lighting and continuity constraints. Add precision text, markings and arrows after generation. If an output changes the count, orientation, mechanism or identity that carries the explanation, replace that shot with a controllable model.

## Local composition

The compositor needs Python, Pillow, FFmpeg with libx264 and AAC, and a font covering the caption language. Use a new project directory for each film. Resolve paths in the manifest relative to the manifest itself. Point to a real font on the target machine.

```json
{
  "size": [1280, 720],
  "fps": 24,
  "font": "fonts/your-font.ttf",
  "shots": [
    {
      "id": "s1",
      "line": "The same order number appears on both records.",
      "audio": "voice/s1.wav",
      "clip": "clips/s1.mp4",
      "tail": 0.25
    }
  ]
}
```

Record or synthesize each voice line before export. For Chinese audio on Windows with a compatible installed voice, run `& "$skillDir/scripts/speak-zh.ps1" -Plan ./plan.json` in PowerShell. Use your own per-shot recordings or another speech provider for English and other languages.

```sh
python /path/to/explain-in-3d/scripts/compose.py plan.json film.mp4
ffprobe -v error -show_streams -show_format -of json film.mp4
```

The measured speech determines the shot length. The default tail is 0.25 seconds. Supply enough video for speech and tail, or set `"hold_last": true` to intentionally freeze the last frame. Use short captions. When a shot needs multiple cues, supply `"captions": [[0, 1.8, "First phrase."], [1.8, 3.0, "Second phrase."]]` with local times within the actual speech duration. Export produces burned-in captions and a UTF-8 SRT sidecar.

For a computed scene, set a top-level `"renderer": "scene.py"`, omit `clip` from its shots and implement `render(shot, progress, size)`. Return a Pillow image of the requested size for progress values from zero to one. Only run scene code you authored or reviewed. The renderer owns the camera, occlusion and diagrams. The compositor owns timing, captions and audio.

To mix independent music or effects, add a top-level `tracks` array. Each start is measured in seconds on the full film timeline. The following is an example value for that key.

```json
[
  {"kind":"music","file":"audio/bed.wav","start":0,"gain_db":-20,"loop":true},
  {"kind":"sfx","file":"audio/click.wav","start":4.25,"duration":0.45,"gain_db":-12}
]
```

Clip audio is omitted by default. To keep location sound, supply that clip as an explicit effects input. Keep the original stems in the project. The MP4 carries the mix.

## Review

Check the start, center and end of every important hold. Read the muted proof at small size. Reframe the scene for vertical output. Confirm the selected object stays identifiable and the caption fits within safe margins. Decode the entire film, check the last spoken line and verify that affected cues still line up after any edit. Deliver the actual result and identify any stage that could not be verified.
