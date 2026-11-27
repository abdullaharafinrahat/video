"""
FIVE STEPS BEHIND — sound design (dependency-free).
Builds a 20s soundscape from numpy only:
  * wind  : low-passed noise, amplitude driven by core.gust()
  * grass : band-passed rustle, modulated by gust()
  * cloth : short filtered transients on gust peaks
  * score : a minimalist piano + string drone that BUILDS, then is cut to
            pure silence at the jump (~13.3s). After that: only wind/ambience,
            slowly fading. Silence is the choice.
Writes a 16-bit WAV ready to be muxed into the MP4.
"""
import sys, wave, struct
sys.path.insert(0, ".")
import numpy as np
from core import gust

SR = 44100
DUR = 20.0
N = int(SR * DUR)
T = np.linspace(0, DUR, N, endpoint=False)
JUMP = 13.3          # global seconds of the leap
END_SILENCE = 19.25  # cut-to-black: let the ambience die fully


def gust_env(rate=120.0):
    """Sample the shared wind signal at `rate` Hz and resample to N."""
    nt = int(DUR * rate)
    tt = np.linspace(0, DUR, nt, endpoint=False)
    g = np.array([gust(x) for x in tt], dtype=np.float32)
    g = np.clip((g - 0.28) / 0.9, 0, 1)          # 0..1
    idx = np.clip((T * rate).astype(int), 0, nt - 1)
    return g[idx]


def noise(n):
    rng = np.random.default_rng(7)
    return rng.standard_normal(n).astype(np.float32)


def one_pole(x, a):
    y = np.empty_like(x)
    y[0] = x[0]
    for i in range(1, len(x)):
        y[i] = y[i - 1] + a * (x[i] - y[i - 1])
    return y


def bandpass(x, lo, hi):
    a1 = 1.0 / (1 + 2 * np.pi * lo / SR)
    a2 = 1.0 / (1 + 2 * np.pi * hi / SR)
    lp = one_pole(x, a1)
    return one_pole(lp, a2) - lp


def note(freq, t0, dur, gain, harm=4, dec=5.0):
    """A soft struck tone (piano-ish) with a few decaying harmonics."""
    out = np.zeros(N, np.float32)
    s0 = int(t0 * SR); s1 = min(N, int((t0 + dur) * SR))
    local = np.arange(s0, s1) / SR
    for h in range(1, harm + 1):
        env = np.exp(-dec * (local) * (1.0 / h))
        out[s0:s1] += gain / h * np.sin(2 * np.pi * freq * h * local) * env
    return out


def drone(freq, t0, t1, gain):
    """A slowly swelling string-like tone with vibrato."""
    out = np.zeros(N, np.float32)
    s0 = int(t0 * SR); s1 = int(min(t1, END_SILENCE) * SR)
    if s1 <= s0:
        return out
    local = np.arange(s0, s1) / SR
    vib = 1 + 0.004 * np.sin(2 * np.pi * 5.0 * local)
    swell = np.clip((local - 0) / 1.5, 0, 1) * np.clip((t1 - 0 - local) / 1.5, 0, 1)
    for h, g in ((1, 1.0), (2, 0.35), (3, 0.18)):
        out[s0:s1] += gain * g * np.sin(2 * np.pi * freq * h * vib * local) * swell
    return out


def build():
    rng = np.random.default_rng(3)
    g = gust_env()

    # --- wind: stacked low-passed noise, amplitude follows the gust ---
    w = noise(N)
    wind_lp = one_pole(w, 1.0 / (1 + 2 * np.pi * 420 / SR))
    wind_deep = one_pole(w, 1.0 / (1 + 2 * np.pi * 120 / SR))
    g_smooth = one_pole(g, 0.01)
    wind_amp = 0.06 + 0.5 * g_smooth + 0.12 * np.gradient(g_smooth)
    wind = (wind_lp * 0.6 + wind_deep * 0.4) * wind_amp
    # a faint whistle on the strongest gusts
    whistle = one_pole(w, 1.0 / (1 + 2 * np.pi * 1400 / SR))
    wind += np.clip(g_smooth - 0.6, 0, None) * whistle * 0.05
    wind *= 0.9

    # --- grass / cloth: high bandpass rustle, only when the wind blows ---
    grass = bandpass(w, 2500, 9000) * (0.015 + 0.06 * g)
    cloth = bandpass(noise(N), 1800, 6000) * (0.01 + 0.05 * np.clip(np.gradient(g) * 40, 0, 1))

    # --- score: minimalist piano motif + string drone, cut at the jump ---
    score = np.zeros(N, np.float32)
    # a quiet, patient minor figure (A2-ish root, falling seconds)
    motif = [
        (5.0, 110.0, 1.6, 0.10),
        (6.6, 130.8, 1.4, 0.09),
        (8.2, 98.0, 1.8, 0.10),
        (9.8, 146.8, 1.2, 0.08),
        (11.0, 110.0, 1.6, 0.11),
    ]
    for t0, f, d, gn in motif:
        if t0 + d < JUMP:
            score += note(f, t0, d, gn, harm=4, dec=4.0)
    # strings enter around 6s and swell until the jump, then silence
    score += drone(82.4, 6.0, JUMP, 0.05)     # E2
    score += drone(123.5, 7.5, JUMP, 0.035)   # B2
    score += drone(164.8, 9.0, JUMP, 0.03)    # E3
    score = np.clip(score, -1, 1) * np.clip((T - 4.0) / 2.0, 0, 1)
    # hard cut at the jump: everything musical stops
    score[T >= JUMP] = 0.0

    # --- assemble. After the jump: only the dying wind/grass, fading to black. ---
    mix = wind + grass + cloth + score
    fade = np.ones(N, np.float32)
    # ambience gently fades from the jump to the cut-to-black
    die = np.clip((END_SILENCE - T) / (END_SILENCE - JUMP), 0, 1)
    amb = np.where(T >= JUMP, die, 1.0)
    mix = (wind + grass + cloth) * amb + score

    # soft master limiter + normalise to ~ -3 dBFS
    mix = np.tanh(mix * 1.4)
    peak = np.max(np.abs(mix)) + 1e-6
    mix = mix / peak * 0.85
    return (mix * 32767).astype(np.int16)


def write_wav(path, samples):
    with wave.open(path, "w") as wv:
        wv.setnchannels(1)
        wv.setsampwidth(2)
        wv.setframerate(SR)
        wv.writeframes(samples.tobytes())


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "five_steps.wav"
    write_wav(out, build())
    print("wrote", out)
