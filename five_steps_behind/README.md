# FIVE STEPS BEHIND

A 20-second cinematic 2D animated short, rendered entirely in Python.

- **Format:** 16:9 · 1920×1080 · 24 fps · 00:20.0
- **Deliverable:** `five_steps_final.mp4` (H.264 video + AAC score)
- **Pipeline:** cairo vector character rigs · FFT-synthesised fractal landscapes ·
  a hand-rolled compositor · ffmpeg for encoding · numpy-only sound design.
- **Style:** intimate, mysterious, restrained. No dialogue, no text, no explanation.

## Two friends, a cliff, a step into the unknown

A stands at the edge of a vast mountain promontory, looking out. B stands five
steps behind. A steps off. B does not move. We never learn why. The film is the
opening mystery of a larger philosophical series — built as a slow exhale:
beauty → discomfort → tension → wrongness → shock → silence.

## The seven beats

1. **Establishing** — extreme wide, slow dolly; two tiny silhouettes at the tip.
2. **The Distance** — over B's shoulder; A a small figure at the far edge.
3. **Five Steps** — low-angle ground strip; the recurring five-step motif.
4. **The Final Look** — side profile of A, windswept hair, eyes slowly close.
5. **The Realization** — B's POV; his hand rises, trembles, curls.
6. **The Fall** — wide side view; A leaps, one controlled tilt-down then stop;
   mist swallows the fall (non-graphic).
7. **Five Steps Remain** — static from behind B; the hand closes; cut to black.

## Project layout

```
five_steps_behind/
  core.py        rendering toolkit (noise, camera, sky, cloud-sea, compositing, post)
  figures.py     cairo vector character rigs (A, B, hands, profile)
  world.py       the shared world (promontory, ground, grass, characters in scene)
  shots.py       the seven shots + colour script + shot dispatcher
  render.py      master render (per-shot subprocesses -> ffmpeg -> concat)
  audio.py       numpy-only sound design (wind/grass/cloth + minimalist score)
  qc.py          programmatic QC (frame count, duration, per-shot brightness)
  finalize.py    mux video + audio, build a contact sheet
  docs/          PRE_PRODUCTION.md (full director's package) + contact_sheet.png
  tests/         frame/render test harness (t_frame.py etc.)
  five_steps_final.mp4   the finished film (video + audio)
  five_steps.wav         the isolated score
  requirements.txt
```

## Reproduce from this folder

```bash
pip install -r requirements.txt
python3 render.py five_steps.mp4            # ~16 min on 2 cores, streams to ffmpeg
python3 audio.py five_steps.wav             # 20 s soundscape
python3 finalize.py five_steps.mp4 five_steps.wav five_steps_final.mp4
python3 qc.py five_steps_final.mp4
```

`render.py` renders each shot in its **own subprocess** so memory resets between
shots (the sandbox cgroup is tight). The heavy Shot 6 paints the cliff at half
resolution and upscales. Output is exactly 480 frames / 20.000 s.

## Bringing it back

Everything needed to rebuild the film lives in this folder. To restore it:

```bash
git clone https://github.com/abdullaharafinrahat/video.git
# the project is under: video/five_steps_behind/
```
