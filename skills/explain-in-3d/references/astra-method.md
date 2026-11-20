# The directing method

FuturMinds demonstrated four explainer formats in *GPT-6 Astra Made This 3D Explainer Video (No Editor)*. These notes summarize the creator's narrated process and visible chapter frames. The prompts below are original examples written for this skill. [Source video](https://www.youtube.com/watch?v=TkBZs5GOFFo) · [Chapter frames](https://moderncreator.app/2026-09-12-futurminds-gpt-6-astra-made-this-3d-explainer-video-no-editor) · [Creator's community](https://www.skool.com/ai-architects-8928/about)

| Source | What the creator did | What to carry to a new subject |
| --- | --- | --- |
| [The stack, 00:35](https://www.youtube.com/watch?v=TkBZs5GOFFo&t=35) | Codex coordinated Three.js geometry, GSAP motion and HyperFrames composition. For generated shots, a location reference and a motion prompt went to Veo via fal. The explanatory freeze, outline, label and sound were added in post. | Keep the plate independent of the explanation, so the words and emphasis remain editable. |
| [Project setup, 01:38](https://www.youtube.com/watch?v=TkBZs5GOFFo&t=98) | The project was prepared once. New sessions reused the tooling and optional fal and Gemini integrations. | Retain tested versions, fonts, project assets and provider configuration across episodes. |
| [GPU teardown, 02:20](https://www.youtube.com/watch?v=TkBZs5GOFFo&t=140) | The camera moved from the cooling assembly and board into a schematic of the chip. A revision addressed detail, camera continuity, music and effects. | Track one physical part across changes in scale. Explicitly mark the transition from physical hardware to a schematic. |
| [Pyramid, 04:23](https://www.youtube.com/watch?v=TkBZs5GOFFo&t=263) | Consistent references connected a descent past the Nile to a worksite and a stone on a sledge. The creator used Veo 3.1 Fast, ElevenLabs v3, Stable Audio 3 and HyperFrames. Camera pacing was revised with existing footage. | Anchor a large setting in one small object that demonstrates the mechanism. |
| [Falling spheres, 06:27](https://www.youtube.com/watch?v=TkBZs5GOFFo&t=387) | Equal-size spheres of different mass fell through air. A freeze revealed force arrows, followed by a comparison without air. The creator reported local visuals and externally generated audio. | Hold the geometry and initial conditions fixed. Change a single variable and identify the conditions at the instant of comparison. |
| [Orbital debris, 07:54](https://www.youtube.com/watch?v=TkBZs5GOFFo&t=474) | A connected flight past satellites and debris was tested with a ten-second proof. Labels and narration were added later. | Validate camera speed, scale transitions and reading time before committing to a full-length film. |

The creator recommended budgeting for retries and reusing good assets. The recorded examples varied widely. The GPU piece had no recorded external paid-generation charge, the pyramid used about $3.88 under a $4 cap, the sphere demo about $0.03 across versions, and the orbital film about $6.50. These are figures from that specific production. Track the current project's spending separately. [Budget discussion](https://www.youtube.com/watch?v=TkBZs5GOFFo&t=540)

## Render the included starter

Copy the two files from `assets/three-proof/` into a fresh video project. The starter lifts a lid, holds on an orange sealing ring with a screen-space callout, then closes the lid. The template is silent. The published example adds a local English voice track.

Run the following in the new video project, using compatible versions already pinned in your project when available.

```sh
npm init -y
npm install --save-exact three gsap hyperframes esbuild
npx esbuild scene.mjs --bundle --outfile=scene.bundle.js
npx hyperframes doctor
npx hyperframes lint
npx hyperframes render --output proof.mp4
```

Use `npx hyperframes preview` for interactive review. The scene and annotation both derive from the current timeline time. Check that seeking backward returns to the same pose and label position. After editing an object, recheck the callout anchor at the pause. The running demo in this repository exercises the scene with Chromium and FFmpeg. HyperFrames CLI setup and export depend on the installed release. [HyperFrames repository](https://github.com/heygen-com/hyperframes) · [CLI reference](https://github.com/heygen-com/hyperframes/blob/main/docs/packages/cli.mdx)

## Prompts to adapt

**Storyboard.** Explain [question] for [audience] using [source]. Follow [object] from [starting point], through [mechanism], to [result]. Write down the frame at which a viewer can first see the evidence. Include source locations, paths, captions, assumptions and the generation budget.

**Proof.** Render the most difficult continuous ten seconds. Show the precondition, stop on the decisive action, label the relevant relationship, then continue into the resulting state. Preserve the object and reference landmarks. Check the shot muted and with speech.

**Revision.** At [time range], adjust [specific camera move, label or sound]. Keep the accepted footage and other layers. Render one second either side of the change to check continuity. Account for any regeneration before spending the remaining budget.
