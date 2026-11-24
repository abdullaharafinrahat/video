"""Mix narration (cut from audio3a.wav) with an ambient score and sound effects."""
import wave, numpy as np
from scipy import signal

SR = 24000
START, END = 189.5, 364.3
w = wave.open('/tmp/audio3a.wav')
assert w.getframerate() == SR
raw = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
a, b = int(START * SR), int(END * SR)
nar = raw[a:b].copy()
N = len(nar)
tt = np.arange(N) / SR
# narration fades
fi, fo = int(0.35 * SR), int(1.0 * SR)
nar[:fi] *= np.linspace(0, 1, fi)
nar[-fo:] *= np.linspace(1, 0, fo)
peak = np.abs(nar).max()
nar = nar / peak * 0.88

rng = np.random.default_rng(1)


def T(abs_t):
    return abs_t - START


def add(buf, t0, sig, gain=1.0):
    i = int(t0 * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(sig))
    if i < 0:
        sig = sig[-i:]
        i = 0
        j = min(len(buf), i + len(sig))
    buf[i:j] += sig[:j - i] * gain


def lp(x, fc, order=2):
    sos = signal.butter(order, fc, 'low', fs=SR, output='sos')
    return signal.sosfilt(sos, x)


def bp(x, f0, f1):
    sos = signal.butter(2, [f0, f1], 'band', fs=SR, output='sos')
    return signal.sosfilt(sos, x)


# ------------------------------------------------ ambient pad (Dm – Bb – Gm – A)
chords = [(73.42, 110.0, 146.83, 174.61), (58.27, 116.54, 146.83, 174.61), (49.0, 98.0, 146.83, 196.0), (55.0, 110.0, 138.59, 164.81)]
pad = np.zeros(N, np.float32)
seg_len = 11.0
nseg = int(np.ceil((END - START) / seg_len)) + 1
for k in range(nseg):
    ch = chords[k % 4]
    t0 = k * seg_len
    n = int((seg_len + 3) * SR)
    x = np.arange(n) / SR
    env = np.minimum(1, x / 3.0) * np.minimum(1, (seg_len + 3 - x) / 3.0)
    s = np.zeros(n, np.float32)
    for i, f in enumerate(ch):
        vib = 1 + 0.002 * np.sin(2 * np.pi * (0.2 + 0.05 * i) * x + i)
        s += (np.sin(2 * np.pi * f * x * vib) + 0.35 * np.sin(2 * np.pi * 2 * f * x) + 0.12 * np.sin(2 * np.pi * 3 * f * x)) / (1 + i * 0.3)
    add(pad, t0, (s * env).astype(np.float32), 1.0)
pad *= 0.045 / np.abs(pad).max() * 1.0
pad *= (0.85 + 0.15 * np.sin(2 * np.pi * tt / 17.0))
# gentle wind
wind = lp(rng.standard_normal(N).astype(np.float32), 600) * 0.03 * (0.5 + 0.5 * np.sin(2 * np.pi * tt / 9.0 + 1))
sfx = np.zeros(N, np.float32)


def ping(t0, f=1300, gain=0.16):
    n = int(1.6 * SR)
    x = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * x) * np.exp(-x * 3.2)
    s += 0.35 * np.sin(2 * np.pi * f * 2.01 * x) * np.exp(-x * 5)
    echo = np.zeros(n + int(0.5 * SR), np.float32)
    echo[:n] += s
    echo[int(0.28 * SR):int(0.28 * SR) + n] += 0.4 * s
    add(sfx, T(t0), echo.astype(np.float32), gain)


def whoosh(t0, dur=0.9, gain=0.07, up=True):
    n = int(dur * SR)
    x = np.arange(n) / SR
    noise = rng.standard_normal(n).astype(np.float32)
    out = np.zeros(n, np.float32)
    blocks = 12
    for k in range(blocks):
        a_, b_ = k * n // blocks, (k + 1) * n // blocks
        fc = 300 + (2600 * ((k + 1) / blocks if up else 1 - k / blocks))
        sos = signal.butter(2, [max(80, fc * 0.5), min(SR / 2 - 100, fc)], 'band', fs=SR, output='sos')
        out[a_:b_] = signal.sosfilt(sos, noise[a_:b_])
    env = np.sin(np.pi * x / dur) ** 2
    add(sfx, T(t0) - dur / 2, (out * env).astype(np.float32), gain * 6)


def thump(t0, gain=0.5, f=70):
    n = int(1.0 * SR)
    x = np.arange(n) / SR
    s = np.sin(2 * np.pi * (f * np.exp(-x * 5) + 35) * x) * np.exp(-x * 5)
    s += 0.2 * lp(rng.standard_normal(n).astype(np.float32), 400) * np.exp(-x * 14)
    add(sfx, T(t0), s.astype(np.float32), gain)


def chime(t0, notes=(880, 1318.5), gain=0.12, decay=2.4):
    n = int(3 * SR)
    x = np.arange(n) / SR
    s = np.zeros(n, np.float32)
    for i, f in enumerate(notes):
        d = int(i * 0.18 * SR)
        y = np.sin(2 * np.pi * f * x) * np.exp(-x * decay) + 0.3 * np.sin(2 * np.pi * f * 2.76 * x) * np.exp(-x * decay * 2)
        s[d:] += y[:n - d]
    add(sfx, T(t0), s.astype(np.float32), gain)


def rumble(t0, dur, gain=0.2, fc=120, mod=7.0):
    n = int(dur * SR)
    x = np.arange(n) / SR
    s = lp(rng.standard_normal(n).astype(np.float32), fc, 3)
    s = s / (np.abs(s).max() + 1e-6)
    env = np.minimum(1, x / 0.6) * np.minimum(1, (dur - x) / 0.8) * (0.7 + 0.3 * np.sin(2 * np.pi * mod * x))
    add(sfx, T(t0), (s * env).astype(np.float32), gain)


def scratch(t0, dur, gain=0.08, rate=6.0):
    n = int(dur * SR)
    x = np.arange(n) / SR
    s = bp(rng.standard_normal(n).astype(np.float32), 2500, 7000)
    env = (0.5 + 0.5 * np.sin(2 * np.pi * rate * x)) ** 2 * np.minimum(1, x / 0.2) * np.minimum(1, (dur - x) / 0.3)
    add(sfx, T(t0), (s * env).astype(np.float32), gain)


def drill(t0, dur, gain=0.12):
    n = int(dur * SR)
    x = np.arange(n) / SR
    s = (signal.square(2 * np.pi * 46 * x) * 0.5 + lp(rng.standard_normal(n).astype(np.float32), 900) * 0.8)
    s = lp(s.astype(np.float32), 700)
    env = np.minimum(1, x / 0.5) * np.minimum(1, (dur - x) / 0.6) * (0.75 + 0.25 * np.sin(2 * np.pi * 1.1 * x))
    add(sfx, T(t0), (s * env).astype(np.float32), gain)


TIMES = {19: 189.5, 20: 201.7, 21: 210.0, 22: 219.5, 23: 232.3, 24: 240.6, 25: 244.6, 26: 248.2, 27: 259.6, 28: 274.6,
         29: 281.8, 30: 288.4, 31: 309.6, 32: 341.2}
for n, tt0 in TIMES.items():
    if n != 19:
        whoosh(tt0, 0.8, 0.05)

# 19: sea ambience handled by wind
# 20-21 sonar
for k in range(8):
    ping(202.2 + k * 1.05, 1300, 0.11)
for k in range(4):
    ping(210.2 + k * 2.1, 900, 0.09)
thump(210.0 + 3.6, 0.22, 90)
# 22 land changing rumble
rumble(219.5 + 4.0, 5.5, 0.18, 90, 3.0)
chime(219.5 + 9.4, (523.25, 784), 0.08)
# 23 drilling
drill(232.3, 8.4, 0.12)
# 24 brush
scratch(240.6, 3.9, 0.1)
# 25 discovery
chime(244.6 + 1.5, (1046.5, 1568, 2093), 0.12)
# 26 pops
for tp in (248.2 + 2.9, 248.2 + 4.1, 248.2 + 5.4):
    thump(tp + 0.3, 0.2, 110)
    chime(tp + 0.3, (659.25,), 0.05, 4)
# 27 reveal tags
for tp in (259.6 + 8.6, 259.6 + 12.0, 259.6 + 12.2):
    chime(tp, (440, 660), 0.05, 3)
# 28/29
chime(281.8 + 5.2, (330, 392), 0.07)
for k, ts in enumerate([0.6, 1.0, 1.4, 1.8, 2.2, 2.6, 3.0, 3.4, 3.8, 4.2, 4.6]):
    scratch(281.8 + ts, 0.3, 0.06, 12)
# 30 stamp, quake, wave
whoosh(288.4 + 4.0, 1.2, 0.04)
thump(288.4 + 8.5, 0.55, 75)
rumble(288.4 + 13.2, 3.0, 0.3, 80, 11.0)
whoosh(288.4 + 16.2, 3.0, 0.09)
thump(288.4 + 19.9, 0.3, 60)
# 31 paper & verdicts
whoosh(309.6 + 7.2, 0.7, 0.05)
thump(309.6 + 17.5, 0.28, 95)
thump(309.6 + 21.1, 0.28, 95)
whoosh(309.6 + 24.4, 0.7, 0.05)
chime(309.6 + 29.8, (523.25, 659.25, 783.99), 0.08)
# 32 coin
chime(341.2 + 0.2, (1318.5, 1760, 2349), 0.1, 1.6)
whoosh(341.2 + 6.9, 0.8, 0.07)
thump(341.2 + 7.4, 0.7, 65)
chime(341.2 + 11.4, (987.77, 1318.5), 0.07)
chime(341.2 + 16.0, (440, 554.37, 659.25), 0.07, 1.2)
chime(341.2 + 19.4, (392, 466.16, 587.33), 0.07, 1.2)

music = pad + wind
# mild duck under narration
env = np.abs(nar)
env = lp(env, 4)
duck = 1 - 0.45 * np.clip(env / 0.3, 0, 1)
mix = nar + music * duck * 1.0 + sfx * 1.0
mix = np.tanh(mix * 1.1) / np.tanh(1.1) * 0.92
out = (mix * 32767).astype(np.int16)
wo = wave.open('mix.wav', 'wb')
wo.setnchannels(1)
wo.setsampwidth(2)
wo.setframerate(SR)
wo.writeframes(out.tobytes())
wo.close()
print('ok', N / SR)
