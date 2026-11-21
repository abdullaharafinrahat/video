"""Procedural soundtrack: music bed (ducked under voice, silent in [pause]s), SFX, mix. Writes out/mix.wav"""
import numpy as np, sys
from scipy.signal import butter, sosfilt, resample_poly
from scipy.io import wavfile
import timing as T
from analyze import load, rms_env
SR = 32000
rng = np.random.default_rng(11)
TOT = T.TOTAL
N = int(TOT * SR) + SR
def noise(d): return rng.standard_normal(int(d * SR)).astype(np.float32)
def filt(x, kind, f):
    sos = butter(2, f, btype=kind, fs=SR, output='sos'); return sosfilt(sos, x).astype(np.float32)
def bp(x, lo, hi): return filt(x, 'bandpass', [lo, hi]) if True else x
def tt(d): return np.arange(int(d * SR), dtype=np.float32) / SR
def put(buf, t, sig, g=1.0):
    i = int(t * SR)
    if i < 0 or i >= len(buf): return
    j = min(len(buf), i + len(sig)); buf[i:j] += sig[:j - i] * g
def expd(d, tau, a=0.004):
    t = tt(d); return np.minimum(1, t / a) * np.exp(-t / tau)
def hump(d, p=0.5):
    t = tt(d) / d; return np.sin(np.pi * t ** (np.log(0.5) / np.log(p))) ** 2
def sine(f, d): return np.sin(2 * np.pi * f * tt(d))
# ---------------- instruments / sfx ----------------
def gull():
    d = .55; t = tt(d); f = 1900 - 900 * t / d + 120 * np.sin(2 * np.pi * 18 * t)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * hump(d, .35) * .5).astype(np.float32)
def wind(d, lo=180, hi=900):
    x = bp(noise(d), lo, hi); lfo = np.interp(tt(d), np.linspace(0, d, int(d * .6) + 3), rng.uniform(.3, 1, int(d * .6) + 3))
    return x * lfo
def water(d, f=1400):
    x = filt(noise(d), 'lowpass', f); return x * (.6 + .4 * np.sin(2 * np.pi * .35 * tt(d)))
def rumble(d):
    x = filt(noise(d), 'lowpass', 110) * 3; return (x + 0.5 * sine(38, d) * (1 + np.sin(2 * np.pi * 7 * tt(d)))) * np.minimum(1, tt(d) / .6)
def crack(d=.35):
    return bp(noise(d), 1200, 7000) * expd(d, .06, .001) * 1.6
def crash(d=.9):
    x = np.zeros(int(d * SR), np.float32)
    for k in range(9): put(x, rng.uniform(0, d * .6), bp(noise(.12), 1800, 8000) * expd(.12, .03, .001), rng.uniform(.4, 1))
    return x
def surge(d):
    x = bp(noise(d), 120, 2200); e = (tt(d) / d) ** 1.6 * np.exp(-((tt(d) / d - 1) ** 2) * 0); return x * e * 2.2
def click():
    return (bp(noise(.03), 2000, 6000) * expd(.03, .006, .0005) + sine(1900, .03) * expd(.03, .01, .0003)) * 1.5
def ping(f=1350, d=1.3): return sine(f, d) * expd(d, .35, .003) + .3 * sine(f * 2, d) * expd(d, .15, .003)
def thud(f=62, d=.7): return sine(f, d) * expd(d, .18, .003) * 1.4
def hit():
    x = thud(48, 1.4); n = bp(noise(.4), 100, 1200) * expd(.4, .08, .002) * .8; x[:len(n)] += n; return x
def chime(f=880, d=2.2):
    x = np.zeros(int(d * SR), np.float32)
    for r, g, tau in [(1, 1, .9), (2.76, .5, .5), (5.4, .3, .25), (8.9, .15, .12)]: x += g * sine(f * r, d) * expd(d, tau, .001)
    return x * .5
def gong():
    d = 6; x = np.zeros(int(d * SR), np.float32)
    for r, g, tau in [(1, 1, 2.2), (1.5, .6, 1.8), (2.02, .5, 1.4), (2.99, .35, 1), (4.1, .2, .7)]: x += g * sine(98 * r, d) * expd(d, tau, .01)
    return x * .6
def recstop(d=.7):
    t = tt(d); f = 260 * np.exp(-t * 5.5); return (np.sin(2 * np.pi * np.cumsum(f) / SR) * .7 + .25 * bp(noise(d), 300, 3000)) * np.exp(-t * 2.5) * np.minimum(1, (d - t) * 20)
def recscratch(): return bp(noise(.35), 500, 5000) * np.sin(2 * np.pi * 14 * tt(.35)) ** 2 * expd(.35, .2, .001) * 1.2
def whoosh(d=.55, lo=300, hi=3500):
    x = bp(noise(d), lo, hi); return x * hump(d, .55) * 1.4
def footstep(): return filt(noise(.1), 'lowpass', 900) * expd(.1, .03, .002) * 1.8 + bp(noise(.1), 2000, 6000) * expd(.1, .025, .001) * .5
def scratch(d): return bp(noise(d), 2000, 6000) * (.5 + .5 * np.sin(2 * np.pi * 9 * tt(d)) ** 2) * hump(d, .5) * .7
def brush(d): return bp(noise(d), 2500, 7500) * (.4 + .6 * np.abs(np.sin(2 * np.pi * 3.5 * tt(d)))) * hump(d, .5) * .8
def drill(d):
    t = tt(d); saw = 2 * ((52 * t) % 1) - 1; return (saw * .6 * (1 + .5 * np.sin(2 * np.pi * 24 * t)) + bp(noise(d), 200, 2000) * .5) * hump(d, .5)
def murmur(d): return bp(noise(d), 300, 1400) * (.4 + .6 * np.abs(np.sin(2 * np.pi * rng.uniform(1, 2) * tt(d)))) * .5
def tone(f, d, a=.5, r=1.2):
    t = tt(d); e = np.minimum(1, t / a) * np.minimum(1, (d - t) / r); return (np.sin(2 * np.pi * f * t) + .4 * np.sin(2 * np.pi * 2 * f * t)) * e * .6
def pluck(f, d=1.6):
    t = tt(d); x = sum(g * np.sin(2 * np.pi * f * h * t) * np.exp(-t * (2.5 + 1.8 * h)) for h, g in [(1, 1), (2, .5), (3, .25), (4, .12), (5, .06)])
    return (x * np.minimum(1, t / .003)).astype(np.float32) * .6
def piano(f, d=3.2):
    t = tt(d); x = sum(g * np.sin(2 * np.pi * f * h * t * (1 + 0.0004 * h * h)) * np.exp(-t * (1.1 + .9 * h)) for h, g in [(1, 1), (2, .45), (3, .22), (4, .1), (5, .05)])
    return (x * np.minimum(1, t / .004)).astype(np.float32) * .55
def padnote(f, d):
    t = tt(d); x = np.zeros_like(t)
    for h, g in [(1, 1), (2, .5), (3, .28), (4, .14)]:
        for dt in (-.0035, .0035): x += g * np.sin(2 * np.pi * f * h * (1 + dt) * t)
    e = np.minimum(1, t / 3.0) * np.minimum(1, (d - t) / 3.0); return (x * e * .12).astype(np.float32)
NOTE = lambda n: 440 * 2 ** ((n - 69) / 12)
# --------------- scene mood table: drone, pad, piano(0/1), perc, pluck ---------------
MOOD = {}
def mood(rng_, drone=0., pad=0., perc=0., pluck_=0., piano_=0.):
    for n in rng_: MOOD[n] = (drone, pad, perc, pluck_, piano_)
mood([1], .6, 0, 0); mood([2], .55, .1); mood([3], .4); mood([4], .12); mood([5], .3, .7); mood([6], .3, .5); mood([7], .35, .2)
mood([8], .15, .5); mood([9], .15, .8, 0, .8); mood([10], .15, .8, 0, .6); mood([11], .8, .3, .5)
mood([12], .8, .3, 1); mood([13], .7, .3, .8); mood([14], .3, .4); mood([15], .15, .5)
mood([16], .15, .5, 0, .3); mood([17], .1, .45, 0, .7); mood([18], .05, .1); mood([19], .12, .3)
mood([20], .2, .4, .7); mood([21], .15, .5, .6); mood([22], .15, .4, .6); mood([23], .1, .15); mood([24], .1, .8)
mood([25], .1, .7, .8); mood([26], .1, 1.0, .4); mood([27], .5, .5); mood([28], .25, .2)
mood([29], .2, .3, .3); mood([30], .2, .35, .2); mood([31], .2, .35, .2); mood([32], .2, .5)
mood([33], 0, 0); mood([34], 0, 0); mood([35], .1, .7); mood([36], .1, .4, 0, .7)
mood([37], .3, 0); mood([38], .15, .3); mood([39], .1, .45); mood([40], .1, .4)
mood([41], .05, .5, 0, 0, .8); mood([42], 0, .6, 0, 0, 1); mood([43], 0, .45, 0, 0, .8); mood([44], 0, .6, 0, 0, 1)
mood([45], 0, 0, 0, 0, 0); mood([46], .1, .7, 0, 0, 1)
def env_curve(idx):
    pts_t = [0.]; pts_v = [MOOD[1][idx]]
    for n in range(1, 47):
        a, b = T.scene(n)
        pts_t += [a + .6, b - .6] if b - a > 1.5 else [a, b]; pts_v += [MOOD[n][idx]] * 2
    tt_ = np.arange(0, N) / SR
    return np.interp(tt_, pts_t, pts_v).astype(np.float32)

def main():
    voice24, sr = load()
    voice = resample_poly(voice24, 4, 3).astype(np.float32)
    voice *= 0.708 / np.abs(voice).max()
    music = np.zeros(N, np.float32); sfx = np.zeros(N, np.float32)
    S = lambda n: T.scene(n)[0]; E = lambda n: T.scene(n)[1]
    # ---- drone (block-wise)
    drone = np.zeros(N, np.float32)
    for i in range(0, N, SR * 20):
        t = (np.arange(i, min(N, i + SR * 20), dtype=np.float32)) / SR
        drone[i:i + len(t)] = (np.sin(2 * np.pi * 55 * t) + .6 * np.sin(2 * np.pi * 82.4 * t + 1) + .3 * np.sin(2 * np.pi * 110.3 * t)) * (.8 + .2 * np.sin(2 * np.pi * .07 * t)) * .22
    music += drone * env_curve(0)
    del drone
    # ---- pad chords (A minor, F, C, G) -- S27/S28 uneasy chord
    pad = np.zeros(N, np.float32)
    chords = [[45, 52, 57, 60, 64], [41, 48, 57, 60, 65], [48, 55, 60, 64, 67], [43, 50, 59, 62, 67]]
    uneasy = [45, 51, 57, 60, 63]
    t0 = 0.; k = 0
    while t0 < TOT:
        n = T.scene_of(t0 + 5) if t0 + 5 < T.DUR else 46
        ch = uneasy if n in (27, 28) else chords[k % 4]
        for m in ch: put(pad, t0, padnote(NOTE(m), 15.0))
        t0 += 11.0; k += 1
    music += pad * env_curve(1)
    del pad
    # ---- percussion pulse grid
    perc = np.zeros(N, np.float32)
    for n in range(1, 47):
        if MOOD[n][2] > 0:
            a, b = T.scene(n); beat = .6 if n in (12, 13) else .5; tm = a; c = 0
            while tm < b:
                put(perc, tm, thud(70 if c % 4 else 52, .35), 1.0 if c % 4 == 0 else .55); tm += beat; c += 1
    music += perc * env_curve(2)
    del perc
    # ---- pluck (lyre-like) motif
    pl = np.zeros(N, np.float32)
    for n in (9, 10, 16, 17, 36):
        a, b = T.scene(n); tm = a + .3
        seq = [62, 65, 67, 65, 64, 62, 60, 62]; c = 0
        while tm < b - .5:
            put(pl, tm, pluck(NOTE(seq[c % 8] + 12)), 1); tm += [.9, .45, .45, .9, .45, .45, .9, 1.35][c % 8]; c += 1
    music += pl * env_curve(3)
    del pl
    # ---- piano motif (scene 41 first appearance .. 45)
    pn = np.zeros(N, np.float32)
    phrase = [(0, 64), (.7, 69), (1.4, 72), (2.3, 71), (3.0, 69)]
    tm = S(41) + 1.0
    while tm < S(45) - 3:
        for o, m in phrase: put(pn, tm + o, piano(NOTE(m)), 1.0)
        put(pn, tm, piano(NOTE(45), 5), .8)
        tm += 7.0
    hid = T.wfind('hidden', 127, 127)
    put(pn, hid - .05, piano(NOTE(69), 5), 1.2)
    tm = E(45) + 8.2 if False else T.DUR + .3
    for o, m in phrase: put(pn, tm + o * 1.2, piano(NOTE(m)), .9)
    put(pn, tm + 6, piano(NOTE(57), 5), .8)
    music += pn * env_curve(4) * 1.0
    del pn
    # growing motif in S36: more notes each retelling
    pl2 = np.zeros(N, np.float32); a, b = T.scene(36)
    for r in range(5):
        tm = a + 1 + r * (b - a - 5) / 5
        for o, m in phrase[:r + 1]: put(pl2, tm + o * .5, piano(NOTE(m + 12)), .5)
    music += pl2 * .6
    # ---- ducking envelope
    env = rms_env(voice24, sr); act = (20 * np.log10(env + 1e-9) > -48).astype(np.float32)
    k = 15; act = np.convolve(act, np.ones(k) / k, 'same'); act = (act > .01).astype(np.float32)
    duck_t = np.arange(len(act)) * .02
    d = np.where(duck_t < T.DUR, 0.126, 1.0).astype(np.float32)
    for a, b in T.marked_pauses():  # [pause]: music near silence
        d[(duck_t >= a - .1) & (duck_t <= b + .1)] = .012
    # extra near-silence: hero moments & drops
    for a, b in [(T.wfind('gone', 4, 4, 2), E(3)), (T.wfind('wait', 89, 89), E(34)), (S(33) + 2.5, E(33))]: d[(duck_t >= a) & (duck_t <= b)] = .01
    d = np.convolve(d, np.ones(8) / 8, 'same')
    dn = np.interp(np.arange(N) / SR, duck_t, d).astype(np.float32)
    music *= .75 / max(1e-6, np.abs(music).max()); music *= dn
    # ---- SFX
    def at(t, sig, g=1.0): put(sfx, t, sig, g)
    # whooshes on scene boundaries (not dissolve/black cuts)
    for n in range(2, 47):
        if n in (3, 8, 19, 20, 41, 42, 43, 45, 7, 4, 14, 29, 34, 36, 37, 33, 46): pass
        a = S(n)
        if n not in (2, 41, 42, 45, 46, 7, 34, 4): at(a - .25, whoosh(.5), .35)
    van = T.wfind('vanished', 0)
    at(S(1), gull(), .5); at(S(1) + 1.5, gull(), .4); at(S(1) + 3.1, gull(), .45)
    at(S(1), wind(van - S(1)), .35)
    at(S(2) + .3, thud(80, .4), .8); at(T.line_t(2)[0], thud(80, .4), .8); at(T.line_t(3)[0] - .05, hit(), .9)
    at(S(4) + .2, tone(220, 4.5, .1, 2), .5); at(S(4) + .2, ping(440, 5), .3)
    at(S(5) + .3, whoosh(1.8, 150, 2500), .5); at(S(5), water(E(5) - S(5), 1000), .22)
    at(T.wfind('beneath', 8, 8) - .1, surge(1.2), .25)
    for n in (9,): at(S(n), wind(E(n) - S(n)), .2)
    for k_ in range(5): at(S(9) + 2 + k_ * 1.7, gull(), .25)
    at(S(6), wind(8), .15)
    at(T.line_t(13)[0], tone(220, 5, .4, 2), .45)
    at(S(7) + .3, hit(), 1.0); at(S(7) + .35, gong(), .5)
    tk = S(8) + .1; c = 0
    while tk < T.wfind('373', 16, 16) - .3: at(tk, click(), .35); tk += max(.07, .35 - .02 * c); c += 1
    st = T.wfind('373', 16, 16); at(st, gong(), .9); at(st - .02, thud(90, .5), .9)
    at(S(10), murmur(E(10) - S(10)), .3); at(E(10) - 3, tone(262, 3, .4, 1.5), .4)
    ea = T.wfind('earthquakes', 22, 22); at(ea - .3, rumble(E(11) - ea + .3), .85); at(ea + .2, crack(), .6)
    at(S(11) + 4, water(5, 900), .3); at(S(11) + 7.2, hit(), .7)
    at(S(12), rumble(E(12) - S(12)), .8)
    sh = T.wfind('shook', 25, 25); at(sh, crack(), 1.0); at(sh + .3, crash(), .6)
    bu = T.wfind('collapsed', 26, 26); at(bu - .3, crack(.5), 1.0); at(bu, crash(1.2), .9); at(bu + .05, rumble(1.8), .8)
    for tmm in (S(12) + 2.2, S(12) + 4.4): at(tmm, crash(), .5)
    hush = T.wfind('sea', 27, 27, end=True)
    wv = T.wfind('massive', 28, 28); at(wv - .5, surge(E(13) - wv + .5), 1.0); at(wv + 1.5, hit(), .8)
    at(S(14), wind(E(14) - S(14)), .35); at(S(14), water(E(14) - S(14)), .25); at(S(14) + 1.0, tone(196, 5, 1.5, 2.5), .5)
    at(S(15) - .2, crack(.6), .7); at(S(15) - .2, whoosh(.8, 800, 6000), .5)
    pen = T.wfind('eyewitness', 31, 31)
    for k_, (a_, d_) in enumerate([(pen, 1.2), (pen + 2.4, 1.5), (T.line_t(32)[0], 1.8)]): at(a_, scratch(d_), .5)
    for k_ in range(4): at(S(16) + .3 + k_ * (dur16 := (E(16) - S(16) - .6) / 4), click(), 1.0)
    a17, b17 = T.scene(17); tm = T.wfind('pausanias', 38, 38)
    while tm < T.wfind('water', 39, 39, end=True) - 1.5: at(tm, footstep(), .5); tm += .55
    at(T.wfind('water', 39, 39) - .5, filt(noise(3), 'lowpass', 400), .25)
    at(S(18), filt(noise(E(18) - S(18)), 'lowpass', 350), .3)
    at(S(19) + 2, filt(noise(4), 'lowpass', 300), .2); at(T.wfind('where', 46, 46), tone(147, 4, .1, 3), .6)
    at(S(20) + 2, click(), .4); at(E(20) - 1.8, click(), .6)
    tm = S(22) + .5
    while tm < E(22): at(tm, ping(), .5); tm += 1.3
    tm = S(23); g_ = 0.4
    for k_ in range(3): at(tm, ping(), .35); tm += 1.3 + k_ * .8
    at(S(22), filt(noise(E(22) - S(22)), 'lowpass', 220), .35)
    for k_ in range(3): at(S(25) + 3 + k_ * 3.5, drill(2.5), .5)
    at(S(25) + 11, wind(3), .2)
    for k_ in range(3): at(S(26) + 3 + k_ * 3.5, brush(2.5), .5)
    at(T.wfind('catch', 70, 70) - .2, tone(185, 3, .1, 2), .4)
    at(S(29) + .2, rumble(1.2), .45); at(S(29) + 1.0, crash(), .4); at(E(29) - .01, recstop(), 1.0)
    at(S(30), tone(330, 5, 1, 2), .15)
    for tmm in (S(31) + 1.2, S(31) + 6.5): at(tmm, whoosh(.4, 1500, 6000), .35)
    at(S(32) + .3, tone(300, 5.5, 5, .3), .4)
    at(S(33) + .2, chime(), .9); at(S(33) + .3, chime(1320, 2), .35)
    w_ = T.wfind('wait', 89, 89); at(w_, recscratch(), 1.0); at(w_, hit(), 1.0); at(w_, crack(.15), .8)
    for k_ in range(4): at(w_ + 1.7 + k_ * .5, tone(520 + 40 * k_, .35, .02, .25), .3)
    at(S(35), murmur(E(35) - S(35)), .2)
    at(S(37), filt(noise(E(37) - S(37)), 'lowpass', 160), .35)
    at(S(39), water(E(39) - S(39), 700), .2); at(S(40), wind(E(40) - S(40)), .3)
    at(S(42), murmur(8), .15)
    at(S(44) + 1, tone(392, 4, 1, 2), .25)
    at(S(46), water(8, 900), .2)
    sfx_gain = np.ones(N, np.float32)
    sfx_gain[int(van * SR):int(S(2) * SR)] = 0.0  # hard silence on the cut
    # ---- mix
    mix = np.zeros(N, np.float32); mix[:len(voice)] += voice
    music *= .6 / max(1e-6, np.abs(music).max()) if False else 1.0
    sfx *= sfx_gain
    sfx *= .5 / max(1e-6, np.abs(sfx).max())
    mpk = np.abs(music).max(); print('music pk', mpk, 'sfx pk', np.abs(sfx).max())
    mix = np.zeros(N, np.float32); mix[:len(voice)] += voice
    mix += music + sfx
    print('peak before limit', 20 * np.log10(np.abs(mix).max()))
    n_out = int(TOT * SR); mix = mix[:n_out]
    wavfile.write('out/mix.wav', SR, mix.astype(np.float32))
    print('mix written', len(mix) / SR, 's, peak', 20 * np.log10(np.abs(mix).max()))

if __name__ == '__main__': main()
