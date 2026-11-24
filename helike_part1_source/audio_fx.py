import numpy as np, wave
SR = 44100
T = 108.4
n = int(SR * T)
tt = np.arange(n) / SR
rng = np.random.default_rng(1)


def env(a, b, fi=1.0, fo=1.0):
    return np.clip((tt - a) / fi, 0, 1) * np.clip((b - tt) / fo, 0, 1)


def fft_filter(x, lo=None, hi=None):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    m = np.ones_like(f)
    if lo: m *= 1 / (1 + (lo / np.maximum(f, 1e-3)) ** 4)
    if hi: m *= 1 / (1 + (f / hi) ** 4)
    return np.fft.irfft(X * m, len(x))


def noise():
    return rng.standard_normal(n)


out = np.zeros(n)
# pad: slow evolving minor chord
for f, a in [(55, .5), (82.4, .35), (110, .25), (164.8, .12), (220, .1), (261.6, .08), (329.6, .05)]:
    lfo = 0.6 + 0.4 * np.sin(2 * np.pi * (0.05 + f / 4000) * tt + f)
    out += a * 0.05 * np.sin(2 * np.pi * f * tt) * lfo * env(0, T, 3, 3)
# bright shimmer under reveal & map
for f in (440, 659.3, 880):
    out += 0.012 * np.sin(2 * np.pi * f * tt + 3 * np.sin(2 * np.pi * 0.3 * tt)) * env(22.9, 31, 2, 2)
    out += 0.01 * np.sin(2 * np.pi * f * tt) * env(62.4, 70.4, 1.5, 2)
# sea
sea = fft_filter(noise(), 80, 900)
swell = 0.5 + 0.5 * np.sin(2 * np.pi * 0.11 * tt)
for a, b in [(0, 8), (22.9, 31), (70.4, 97.3)]:
    out += sea * swell * 0.05 * env(a, b, 1.5, 2)
# wind
wind = fft_filter(noise(), 200, 1800)
out += wind * (0.5 + 0.5 * np.sin(2 * np.pi * 0.2 * tt + 1)) * 0.05 * env(12.1, 23, 2, 2)
# underwater hum
out += fft_filter(noise(), 40, 300) * 0.07 * env(37, 50, 2, 2)
# clock ticks
for k in range(int(62.4 * 8), int(64.6 * 8)):
    s = int(k / 8 * SR)
    L = int(0.03 * SR)
    out[s:s + L] += np.sin(2 * np.pi * 1800 * tt[:L]) * np.exp(-tt[:L] * 150) * 0.08
# whoosh for title reveal and sign stamp
w_ = fft_filter(noise(), 400, 5000) * env(29.0, 30.6, 1.2, 0.4) * 0.06
out += w_
for tm in (68.95,):
    i = int(tm * SR)
    L = int(1.2 * SR)
    out[i:i + L] += np.sin(2 * np.pi * (70 * np.exp(-tt[:L] * 3)) * tt[:L] * 1.0) * np.exp(-tt[:L] * 4) * 0.5
# earthquake foreshadow rumble
rum = fft_filter(noise(), 20, 70)
out += rum * 6 * (np.clip((tt - 91) / 4, 0, 1) ** 2) * env(0, 108, 1, 1.5) * (tt < 106.3)
# impacts
for tm, amp in [(100.2, 0.7), (101.0, 0.6), (102.9, .8), (104.3, .7), (105.2, .6)]:
    i = int(tm * SR)
    L = int(2.2 * SR)
    if i + L > n: L = n - i
    tl = tt[:L]
    out[i:i + L] += np.sin(2 * np.pi * (36 + 70 * np.exp(-tl * 6)) * tl) * np.exp(-tl * 2.2) * amp
crumb = fft_filter(noise(), 150, 4000)
clicks = (rng.random(n) < 0.0009) * 1.0
crumb = crumb * np.convolve(clicks + 0.12, np.exp(-np.arange(2000) / 500.0), 'same') * 3
out += crumb * 0.25 * env(100.2, 106.5, 0.5, 1.0)
# shaking rumble loud 100-106
out += fft_filter(noise(), 25, 120) * 8 * env(100.0, 106.4, 0.4, 1.0)
# sea roar at end
roar = fft_filter(noise(), 60, 1500)
out += roar * 0.45 * (np.clip((tt - 105.6) / 2.4, 0, 1) ** 1.5) * env(0, T, 1, 0.8)
# fade
out *= env(0, T, 1.5, 1.2)
out = np.tanh(out * 1.4) * 0.5
st = np.stack([out, np.roll(out, 40)], 1)
st = (st / max(np.abs(st).max(), 1e-6) * 0.6 * 32767).astype(np.int16)
w = wave.open('/tmp/w/ambience.wav', 'wb')
w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes(st.tobytes()); w.close()
print('ok')
