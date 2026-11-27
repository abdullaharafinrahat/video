# FIVE STEPS BEHIND — Pre-Production Package

**Format:** 2D cinematic animated short · 16:9 · 24 fps · 00:00–00:20
**Toolchain:** Python (cairo vector rigs, FFT fractal landscapes, hand-rolled compositor) → MP4 via ffmpeg.
**Tone:** intimate, mysterious, restrained. The power comes from what is *not* shown.

---

## 1. Logline / Creative Thesis

Two young men stand at the end of the world. One steps off. The other does not move.
We never learn why. The film is the opening mystery of a larger philosophical series —
a study of friendship, distance, and the silence between people who know each other completely.

The sequence is built as a slow exhale: beauty → discomfort → tension → wrongness → shock → silence.
Every decision serves that arc. There is no explanation, no dialogue, no score that tells you how to feel.

---

## 2. Character Design Sheets

Both characters are original inhabitants of the same world: slender-built mountain people,
dressed for a cold wind at altitude. Silhouette-first design.

### Character A — "the one who leaves"
- **Build:** tall, slender, a little stooped — a thinker's posture.
- **Clothing:** long charcoal coat (matte, wind-reactive), rust/oxblood scarf wound twice,
  dark trousers. Coat hem lifts in gusts (follow-through + secondary motion).
- **Hair:** unruly dark hair, windswept, animated per-strand-ish with a low-frequency sway.
- **Face (profile):** calm, unreadable. Eyes close slowly in Shot 4 — the only explicit
  emotional beat he is given.
- **Palette:** coat `(0.16,0.16,0.19)`, scarf `(0.42,0.165,0.105)`, hair near-black.
- **Signature silhouette:** narrow vertical column + scarf knot at the nape + lifted coat tail.

### Character B — "the one who stays"
- **Build:** a head shorter, broader through the shoulders. Stocky, grounded.
- **Clothing:** quilted olive jacket, cropped ash-blond hair (darkened for read against light sky),
  cross-body satchel strap.
- **Hands:** bare, pale — the storytelling instrument of the whole film.
- **Face:** mostly hidden / behind. Tension lives in the shoulders and the hands.
- **Palette:** jacket `(0.30,0.31,0.23)` / `(0.22,0.23,0.17)`, skin `(0.78,0.69,0.61)`.
- **Signature silhouette:** rounded bulky torso + satchel diagonal + the trembling hand.

**Continuity rule:** proportions, palettes, and hair are defined once in `figures.py` and reused
across every shot. The same `gust(t)` signal drives the wind in both characters and the audio,
so motion and sound stay in lockstep.

---

## 3. Environment Concept

An enormous temperate mountain promontory jutting into a sea of cloud at late afternoon
(low warm sun, cool zenith — "golden hour without the cliché glow").

- **Geography:** the land narrows to a tip. A stands 0.6 m from the lip; B is 4.3 m behind and
  0.9 m to the left. The drop below is rendered as a **single lit rock face turning toward the
  low sun** (right side warm, left side in shadow) swallowed at its base by the cloud sea — no
  cartoon cliff, no floating slab.
- **Depth layers:** near grass → promontory cap → mid ridge → distant blue-grey ranges →
  high drifting cloud bands → sky. Atmospheric perspective flattens far layers toward the
  horizon haze colour.
- **Sky:** warm horizon band, cool desaturated zenith, a low sun disc upper-right casting the
  promontory's right face into light.
- **Vegetation:** short, dark, wind-bent grass blades in near + far bands; a few pebbles.
  Nothing decorative.
- **Atmosphere:** FFT fractal cloud-sea texture at two scales, slowly scrolling; high cloud
  bands drifting; mist banks that periodically swallow the base of the cliff and the fall.

---

## 4. Color Script

| Shot | Time | Key colour | Exposure | Sat | Read |
|------|------|-----------|----------|-----|------|
| 1 | 0:00–0:03 | warm gold horizon / cool zenith | 1.00 | 1.00 | vast, inviting |
| 2 | 0:03–0:05 | cooler, B's shoulder silhouette | 0.98 | 0.97 | distance |
| 3 | 0:05–0:07 | low warm ground, deep shadow | 1.00 | 1.00 | earthy, intimate |
| 4 | 0:07–0:10 | warm on A's profile, gentle bloom | 1.02 | 1.04 | intimacy, uncertainty |
| 5 | 0:10–0:13 | desaturated, cooler, the hand pale | 0.97 | 0.90 | dread |
| 6 | 0:13–0:16 | desaturated, colder, fall swallowed by mist | 0.95 | 0.84 | shock, emptiness beginning |
| 7 | 0:16–0:20 | cool, dimming, then black | 0.92→dip | 0.72 | silence / void |

The grade cools and desaturates as the tragedy lands; brightness dips as a cloud crosses the sun
in the final shot, then cuts to black at 19.25 s.

---

## 5. Storyboard (7 beats)

1. **S1 — Establishing (0–3):** extreme wide, slow forward dolly. Two tiny figures at the tip
   of a vast land. Scale + isolation established immediately.
2. **S2 — The Distance (3–5):** over B's right shoulder. A a small figure at the far edge
   facing the horizon; B's dark shoulder fills the left foreground.
3. **S3 — Five Steps (5–7):** low-angle ground strip. A's feet near the lip, B's blurred feet
   five steps back. Subtle lateral parallax; a pebble tumbles. The recurring motif.
4. **S4 — The Final Look (7–10):** side-profile of A, hair in wind, eyes slowly close.
   4.5% push-in. Maximum intimacy.
5. **S5 — The Realization (10–13):** B's POV. B's hand rises into frame, trembling, curling.
   A shifts his weight forward (anticipation).
6. **S6 — The Fall (13–16):** wide side view. A leaps; a single controlled camera tilt-down
   follows briefly then **stops**; a mist bank swallows the fall. No impact, no body, no graphic.
7. **S7 — Five Steps Remain (16–20):** static wide from behind B. The edge is empty. B's hand
   slowly closes. Environment keeps breathing. Hold, then cut to black at 19.25 s.

---

## 6. Camera Plan

| Shot | Lens (35mm-eq) | Move | Rationale |
|------|----------------|------|-----------|
| 1 | ~35mm wide | slow dolly-in (~3.5 m) | reveal scale, no shake |
| 2 | ~50mm | locked, slight breathing | over-the-shoulder, stable |
| 3 | ~35mm low | subtle lateral parallax | ground motif, low angle |
| 4 | ~85mm | 4.5% push-in | compress, intimate |
| 5 | ~50mm | locked | hand is the subject |
| 6 | ~40mm | tilt-down, decel, stop | follow then abandon |
| 7 | ~35mm | static | stillness as statement |

No constant zooming. Every move is motivated by emotional progression. The camera *withholds*
during the fall — it looks away with B, never sensationalizing.

---

## 7. Animation Timing Sheet

- **S1:** dolly ease-in over 3 s; grass/cloud ambient motion continuous.
- **S3:** pebble drop at ~6.0 s, 0.9 s fall, subtle bounce settle.
- **S4:** eyes begin closing at 8.25 s, complete ~9.9 s (ease_io). Hair sway continuous.
- **S5:** hand rises tl 0.25–1.35 (≈10.25–11.35 s), then tremor + curl through the beat;
  A's lean begins 11.55 s.
- **S6:** launch at 13.3 s; 0.45 s to apex; fall over ~1.4 s; camera tilt-down starts at launch,
  stops ~14.2 s; mist bank crosses 14.5–15.2 s.
- **S7:** hand closes from tl 0.9 (≈16.9 s) over ~1.9 s; breath cycle continuous; exposure dip
  ~18.0 s; black from 19.25 s.

---

## 8. Lighting & Compositing Direction

- Single key: low warm sun upper-right (azimuth 0.30, elevation 0.034).
- Rim/back light on figures and grass from the sun direction (warm, narrow wrap) to separate
  them from the sky — silhouette storytelling.
- Aerial perspective: far layers mixed toward horizon haze.
- Compositing: hand-painted paper grain (subtle, multiplicative), controlled film-grain
  (luma-weighted), soft shoulder tone-map, gentle vignette, conservative bloom (no neon).
- No excessive glow, no particles, no random VFX.

---

## 9. Sound Design Plan

- **Wind:** low-passed noise, amplitude driven by the *same* `gust(t)` that moves the hair/grass.
- **Grass / cloth:** band-passed rustle on gusts; cloth transients on gust peaks.
- **Score:** minimalist piano motif (a patient falling figure) + a string drone that swells
  from ~6 s. Restrained, never dictating emotion.
- **The cut:** at the jump (13.3 s) **all music stops**. After that, only the dying wind and
  grass, fading to nothing by the cut-to-black. Silence is the artistic decision.
- No dialogue, narration, or text.

---

## 10. Director's Self-Review (gate before final render)

- [x] Opening composition immediately establishes the world (extreme wide, tiny figures).
- [x] The five-step gap is physically legible (S3 ground motif + S2 over-the-shoulder).
- [x] Each camera angle contributes something new (no repeated setups).
- [x] The jump is shocking but non-graphic (mist swallows it; camera looks away).
- [x] B's final stillness is believable (breath + hand close only).
- [x] The ending holds with breathing room before black.
- [x] No story explanation introduced; ambiguity preserved.
- [x] Exactly 20 s · 480 frames · 24 fps · 16:9.
