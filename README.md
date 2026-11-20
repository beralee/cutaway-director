# Cutaway Director

**A Codex skill for making editable 3D explainer videos.** Give it a source and a question. It plans a camera route, renders the hardest ten seconds, then builds the film around what the viewer can actually see.

[![A teal lid lifts to reveal an orange sealing ring between the lid and base. Open the ten-second film.](examples/seal-preview.gif)](examples/seal-proof.mp4)

**[Watch the 10-second proof with English narration](examples/seal-proof.mp4)** · [English captions](examples/seal-proof.srt) · [Edit the Three.js scene](skills/explain-in-3d/assets/three-proof/scene.mjs) · [Read the directing guide](docs/directing-guide.md)

In the demo, the lid rises, the camera stops, and a callout points to the exposed ring. The lid then closes over it. The same scene renders the opening, the explanation and the closing shot. Moving the pause or changing the label takes an edit to the timeline or overlay.

## Install in Codex

Clone this repository and copy **`skills/explain-in-3d`** into **`.agents/skills/`** in the project where you want to make videos. Keep the skill folder intact. For use across projects, the user-level destination is `~/.agents/skills/`. [Codex skill locations](https://developers.openai.com/codex/skills/)

Run these commands from your video project's root for a first install on macOS or Linux.

```sh
git clone https://github.com/beralee/cutaway-director.git
mkdir -p .agents/skills
cp -R cutaway-director/skills/explain-in-3d .agents/skills/
```

On Windows, run the equivalent PowerShell commands from the same location.

```powershell
git clone https://github.com/beralee/cutaway-director.git
New-Item -ItemType Directory -Force .agents/skills | Out-Null
Copy-Item -Recurse cutaway-director/skills/explain-in-3d .agents/skills/
```

Invoke the installed skill as **`$explain-in-3d`**. The project name is Cutaway Director. The skill keeps its original invocation name so existing prompts still work.

## Try it

> Use $explain-in-3d to turn the attached product notes into a 60-second English explainer for a first-time buyer. Follow one part from the assembled product into a cutaway and back. Render the hardest ten seconds first. Keep external media spend at zero.

| What you want to explain | What to ask the camera to do |
| --- | --- |
| A device or layered system | Follow one part through disassembly, reveal its role, and reassemble the same model. |
| A scientific comparison | Hold the starting conditions constant. Freeze at the moment the outcomes diverge and label the cause. |
| A place or historical process | Use a consistent location reference. Travel from the wide view to one object that carries the explanation. |
| An abstract workflow | Follow one identifiable object through the process. Show the exact field or state that determines what happens next. |

Specify the audience, narration language, aspect ratio and spending cap in the prompt. Defaults are Chinese narration, 16:9 and 24 fps. A single-question film usually targets 45–90 seconds.

## How it makes the film

1. **Ground the story.** Read the source and tie each factual claim to a page, passage or timestamp. Annotate illustrative assumptions.
2. **Choose a rendering route.** Use Three.js and GSAP for controllable geometry and causal comparisons. Use reference-led generated footage when place, period or atmosphere carries the story.
3. **Test the difficult shot.** Make a short proof containing the camera move, the pause and the visual evidence. Review it muted, then check narration timing.
4. **Finish on separate layers.** Keep footage, labels, narration, music and effects editable. Revise the affected layer and reuse accepted assets. Include retries in the generation budget.

## What you need

| Route | Dependencies and output |
| --- | --- |
| Editable browser scene | Node.js, Three.js, GSAP and a bundler. The included starter is designed for HyperFrames preview and export. [Build the starter](skills/explain-in-3d/references/astra-method.md#render-the-included-starter) |
| Local MP4 composition | Python, Pillow, FFmpeg with H.264/AAC support, a font and per-shot audio. Accepts rendered clips or a Python frame renderer and writes an MP4 plus SRT. [Manifest and commands](skills/explain-in-3d/references/production.md) |
| YouTube as a source | The optional `youtube-transcript-api` reader retrieves available caption tracks with timestamps. [Reader](skills/explain-in-3d/scripts/read_youtube.py) |
| Generated footage or sound | Supply a configured provider and a budget if you want this route. The skill includes directing instructions. Provider accounts, API keys and subscriptions are supplied by the operator. |

The included MP4 was rendered with Three.js, GSAP, Chromium and FFmpeg, with local English speech. The bundled Windows speech helper targets Chinese. For other languages, provide per-shot audio from a suitable voice or a recording.

## Credits

Cutaway Director grew out of a practical study of FuturMinds' *GPT-6 Astra Made This 3D Explainer Video (No Editor)*. The guide links the four demonstrations to their original timestamps. [Watch the tutorial](https://www.youtube.com/watch?v=TkBZs5GOFFo) · [Study notes and implementation choices](skills/explain-in-3d/references/astra-method.md)
