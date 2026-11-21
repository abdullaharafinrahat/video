"""Step 1: decode audio, RMS envelope, pause detection, ASR (vosk) + DP alignment to script."""
import wave, json, re, os, difflib, sys
import numpy as np
from script_data import LINES, SC, scene_lines

SR = 24000
def load():
    w = wave.open('audio3a.wav'); n = w.getnframes()
    x = np.frombuffer(w.readframes(n), dtype='<i2').astype(np.float32) / 32768
    return x, w.getframerate()

def rms_env(x, sr, win=0.02):
    k = int(sr * win); n = len(x) // k
    return np.sqrt((x[:n * k].reshape(n, k) ** 2).mean(1) + 1e-12)

def find_pauses(env, win=0.02, minlen=0.45):
    db = 20 * np.log10(env + 1e-9)
    speech = np.percentile(db, 90)
    thr = max(speech - 38, np.percentile(db, 5) + 8)
    sil = db < thr
    out = []; i = 0
    while i < len(sil):
        if sil[i]:
            j = i
            while j < len(sil) and sil[j]: j += 1
            if (j - i) * win >= minlen: out.append((i * win, j * win))
            i = j
        else: i += 1
    return out, float(thr), float(speech)

def run_asr(x, sr):
    p = 'out/asr.json'
    if os.path.exists(p): return json.load(open(p))
    from vosk import Model, KaldiRecognizer, SetLogLevel
    from scipy.signal import resample_poly
    SetLogLevel(-1)
    y = resample_poly(x, 2, 3)  # 24k -> 16k
    pcm = (np.clip(y, -1, 1) * 32767).astype('<i2').tobytes()
    rec = KaldiRecognizer(Model('vosk-model'), 16000); rec.SetWords(True)
    words = []
    for i in range(0, len(pcm), 16000):
        if rec.AcceptWaveform(pcm[i:i + 16000]):
            words += json.loads(rec.Result()).get('result', [])
    words += json.loads(rec.FinalResult()).get('result', [])
    json.dump(words, open(p, 'w'))
    return words

def norm(w): return re.sub(r'[^a-z0-9]', '', w.lower())
def syl(w):
    w = norm(w)
    if not w: return 1
    if w.isdigit(): return 4
    return max(1, len(re.findall(r'[aeiouy]+', w)) - (1 if w.endswith('e') and len(w) > 3 else 0))

def align(script, asr):
    n, m = len(script), len(asr)
    S = [norm(s) for s in script]; A = [norm(a['word']) for a in asr]
    def sc(a, b):
        if a == b: return 3
        if a and b and difflib.SequenceMatcher(None, a, b).ratio() >= .72: return 1.5
        return -2
    G = -1.5
    H = np.zeros((n + 1, m + 1), dtype=np.float32); P = np.zeros((n + 1, m + 1), dtype=np.int8)
    H[:, 0] = np.arange(n + 1) * G; H[0, :] = np.arange(m + 1) * G; P[1:, 0] = 1; P[0, 1:] = 2
    for i in range(1, n + 1):
        si = S[i - 1]; Hi = H[i]; Hp = H[i - 1]; Pi = P[i]
        for j in range(1, m + 1):
            d = Hp[j - 1] + sc(si, A[j - 1]); u = Hp[j] + G; l = Hi[j - 1] + G
            if d >= u and d >= l: Hi[j] = d; Pi[j] = 0
            elif u >= l: Hi[j] = u; Pi[j] = 1
            else: Hi[j] = l; Pi[j] = 2
    i, j = n, m; match = {}
    while i > 0 or j > 0:
        p = P[i, j]
        if i > 0 and j > 0 and p == 0:
            if sc(S[i - 1], A[j - 1]) > 0: match[i - 1] = j - 1
            i -= 1; j -= 1
        elif i > 0 and (p == 1 or j == 0): i -= 1
        else: j -= 1
    return match

def main():
    x, sr = load(); dur = len(x) / sr
    env = rms_env(x, sr)
    pauses, thr, speech = find_pauses(env)
    asr = run_asr(x, sr)
    # tokens
    toks = []  # (display, line)
    for li, (t, pz, tag) in enumerate(LINES):
        t = t.replace('...', ' ... ')
        for w in t.split():
            if w == '...': continue
            toks.append((w, li))
    match = align([t[0] for t in toks], asr)
    N = len(toks)
    T0 = [None] * N; T1 = [None] * N
    for i, j in match.items(): T0[i] = asr[j]['start']; T1[i] = asr[j]['end']
    # speech-time interpolation for unmatched runs
    def speech_len(a, b):
        tot = b - a
        for (p0, p1) in pauses: tot -= max(0, min(b, p1) - max(a, p0))
        return max(tot, 0.05)
    def advance(a, s):  # time reached after s seconds of speech starting at a
        t = a
        for (p0, p1) in pauses:
            if p1 <= t: continue
            if p0 > t:
                if p0 - t >= s: return t + s
                s -= p0 - t; t = p1
            else: t = p1
        return t + s
    i = 0
    while i < N:
        if T0[i] is None:
            j = i
            while j < N and T0[j] is None: j += 1
            a = T1[i - 1] if i > 0 else 0.0
            b = T0[j] if j < N else dur
            tot = sum(syl(toks[k][0]) for k in range(i, j)); L = speech_len(a, b); acc = 0; cur = a
            # skip a pause directly after anchor
            for (p0, p1) in pauses:
                if p0 - 0.05 <= cur < p1: cur = p1
            for k in range(i, j):
                s = L * syl(toks[k][0]) / tot
                T0[k] = cur; cur = advance(cur, s); T1[k] = cur
            i = j
        else: i += 1
    # enforce monotonic
    for k in range(N):
        if k and T0[k] < T1[k - 1] - 1e-3: T0[k] = T1[k - 1]
        if T1[k] < T0[k] + 0.06: T1[k] = T0[k] + 0.06
    words = [dict(w=toks[k][0], line=toks[k][1], t0=round(T0[k], 3), t1=round(T1[k], 3),
                  asr=(k in match)) for k in range(N)]
    # line spans
    lines = []
    for li in range(len(LINES)):
        ws = [w for w in words if w['line'] == li]
        lines.append(dict(t0=ws[0]['t0'], t1=ws[-1]['t1']))
    # scene boundaries in the middle of the gap between lines
    bounds = [0.0]
    for n in range(2, 46):
        a, b = scene_lines(n)
        bounds.append(round((lines[a - 1]['t1'] + lines[a]['t0']) / 2, 3))
    bounds.append(round(dur, 3))
    scenes = [dict(n=n + 1, t0=bounds[n], t1=bounds[n + 1]) for n in range(45)]
    scenes.append(dict(n=46, t0=round(dur, 3), t1=round(dur + 8, 3)))
    json.dump(dict(dur=dur, words=words, lines=lines, scenes=scenes, pauses=pauses), open('out/timing.json', 'w'))
    nm = sum(1 for k in range(N) if k in match)
    print(f'dur {dur:.2f}s  RMS thr {thr:.1f} dB speech {speech:.1f} dB  pauses>=0.45s: {len(pauses)}')
    print(f'script words {N}, ASR words {len(asr)}, directly matched {nm} ({100 * nm / N:.1f}%)')
    for s in scenes: print(s['n'], round(s['t0'], 2), round(s['t1'], 2), round(s['t1'] - s['t0'], 1))

if __name__ == '__main__': main()
