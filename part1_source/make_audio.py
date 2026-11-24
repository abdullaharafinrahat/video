import wave, numpy as np
w = wave.open('audio3a.wav'); sr = w.getframerate(); n = w.getnframes()
x = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768.0
TOTAL = 108.4
x = x[:int(TOTAL * sr)]
x = np.pad(x, (0, int(TOTAL * sr) - len(x)))
peak = float(np.percentile(np.abs(x), 99.9)); print('narration peak', peak)
T = np.arange(len(x)) / sr
rng = np.random.default_rng(1)
def filt(noise, lo=None, hi=None):
    sp = np.fft.rfft(noise); f = np.fft.rfftfreq(len(noise), 1 / sr)
    g = np.ones_like(f)
    if hi: g *= 1 / (1 + (f / hi) ** 4)
    if lo: g *= 1 / (1 + (lo / np.maximum(f, 1e-3)) ** 4)
    y = np.fft.irfft(sp * g, len(noise)); return y / (np.abs(y).max() + 1e-9)
rumble = filt(rng.standard_normal(len(x)), hi=70)
env = np.interp(T, [88.4, 92, 96, 102.6, 103.0, 106, 107.8, 108.4], [0, 0.03, 0.06, 0.10, 0.22, 0.2, 0.1, 0])
fx = rumble * env * (1 + 0.3 * np.sin(2 * np.pi * 6.5 * T)) * peak
def thud(t0, amp, f0=55, dur=1.4):
    m = (T >= t0) & (T < t0 + dur); u = T[m] - t0
    y = np.zeros_like(x); y[m] = np.sin(2 * np.pi * f0 * u * (1 - 0.3 * u)) * np.exp(-u * 3.2) * amp * peak
    return y
for t0, a in [(29.3, 0.3), (102.9, 0.55), (105.1, 0.5), (103.3, 0.25), (103.7, 0.25), (104.1, 0.28), (104.5, 0.3), (104.9, 0.3), (65.45, 0.12), (87.3, 0.18)]:
    fx += thud(t0, a, 55 if a > .15 else 110)
cr = filt(rng.standard_normal(len(x)), lo=200, hi=2500)   # crashes of stone
for t0, a in [(102.9, 0.12), (103.3, 0.08), (103.7, 0.08), (104.1, 0.09), (104.5, 0.1), (104.9, 0.1), (105.1, 0.16)]:
    m = (T >= t0) & (T < t0 + 1.5); u = T[m] - t0; fx[m] += cr[m] * np.exp(-u * 3) * a * peak
sea = filt(rng.standard_normal(len(x)), lo=300, hi=3500)
fx += sea * np.interp(T, [105.5, 107.2, 108.4], [0, 0.10, 0.0]) * peak
wh = filt(rng.standard_normal(len(x)), lo=500, hi=4000)
fx += wh * np.interp(T, [62.3, 64.0, 65.2, 65.6], [0, 0.07, 0.03, 0]) * peak
fx += wh * np.interp(T, [28.7, 29.3, 30.5], [0, 0.07, 0]) * peak
out = x + fx
out *= np.interp(T, [0, 0.3, TOTAL - 0.8, TOTAL], [0.0, 1, 1, 0])
out = np.clip(out, -1, 1)
o = wave.open('mix.wav', 'wb'); o.setnchannels(1); o.setsampwidth(2); o.setframerate(sr)
o.writeframes((out * 32767).astype(np.int16).tobytes()); o.close(); print('ok')
