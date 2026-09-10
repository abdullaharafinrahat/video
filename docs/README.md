# Pre-Production Analyses — Green-Screen Motion-Graphics Packages

Clean documentation of every pre-production analysis performed on the clips in this
repository. Each analysis contains: full video breakdown, per-segment topic
identification with transcript keywords, placement decisions, copy-pasteable
text-to-video generation prompts (each with embedded `Timecode pairing:` +
`Duration:` lines), raw-footage warnings, and 9-step editor compositing
instructions.

**Branch note:** This documentation lives on the `docs/pre-production-analyses`
branch (not `main`). To use it: merge this branch into `main`, or simply open the
files from the branch.

## Index

| # | Clip | Resolution / Duration | Topic (from transcript) | Segments | Doc |
|---|------|----------------------|--------------------------|----------|-----|
| 1 | `Man_speaking_to_camera_202609100125.mp4` | 640×360 / 10.0s | Elon Musk — "re-engineering the blueprint for the next 100 years of human civilization" | 3 | [01-man-speaking-elon-musk.md](01-man-speaking-elon-musk.md) |
| 2 | `Man_speaking_to_camera_202609092208.mp4` | 1280×720 / 10.0s | AI humanizer — "breaks down that stiff… natural human rhythm… undetectable in one click" | 3 | [02-man-speaking-ai-humanizer.md](02-man-speaking-ai-humanizer.md) |
| 3 | `Man_walking_through_alley_20260910150228.mp4` | 640×360 / 10.0s | Anime monologue — "carry peace… bear the world's hatred… burden… Sasuke" | 3 | [03-man-walking-alley-monologue.md](03-man-walking-alley-monologue.md) |
| 4 | `Person_speaking_in_dark_room_20260910165223.mp4` | 640×360 / 10.0s | Discipline — "motivation gets you through the door… show up anyway" | 3 | [04-person-dark-room-discipline.md](04-person-dark-room-discipline.md) |

## Common technical spec (all packages)

- **Key color:** flat `#00B140`-style saturated green background, evenly lit, no
  gradients/hotspots/shadows.
- **Foreground restriction:** no green, teal, or lime in any graphic element.
- **Keying:** applied to the *generated* clips only — never to the raw footage.
- **Layering:** raw footage ABOVE keyed graphic (graphics are floating overlay
  cards in measured empty zones).
- **Feather:** 1–3 px on keyed edges.
- **Transitions:** 3–5 frame opacity fades at segment boundaries.
- **Timestamp enforcement:** every generation prompt block carries (a) a
  timestamp range in its bracket label, (b) a `Timecode pairing:` line as the
  first line inside the prompt, and (c) a `Duration:` line as the second line —
  the three always appear together so prompts are self-contained when
  copy-pasted.
- **Tool minimums:** if your video-gen tool enforces a minimum length longer
  than a stated Duration, generate the next-longest supported duration and trim
  to the exact Duration in the editor.
