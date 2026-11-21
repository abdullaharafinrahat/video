import json, re
from script_data import LINES, SC, scene_lines
TJ = json.load(open('out/timing.json'))
DUR = TJ['dur']; TOTAL = DUR + 8.0
WORDS = TJ['words']; LINEI = TJ['lines']; SCENES = TJ['scenes']; PAUSES = TJ['pauses']
FPS = 30
def _n(w): return re.sub(r'[^a-z0-9]', '', w.lower())
def scene(n): s = SCENES[n - 1]; return s['t0'], s['t1']
def dur(n): s = SCENES[n - 1]; return s['t1'] - s['t0']
def line_t(li): return LINEI[li]['t0'], LINEI[li]['t1']
def line_words(li): return [w for w in WORDS if w['line'] == li]
def wt(li, k=0):
    """start time of k-th word (negative = from end) of line li; end time via wte"""
    return line_words(li)[k]['t0']
def wte(li, k=-1): return line_words(li)[k]['t1']
def wfind(text, li0=0, li1=None, occ=0, end=False):
    """time of word containing `text` in lines li0..li1 (inclusive)"""
    li1 = li0 if li1 is None else li1
    c = 0
    for w in WORDS:
        if li0 <= w['line'] <= li1 and _n(text) in _n(w['w']):
            if c == occ: return w['t1'] if end else w['t0']
            c += 1
    raise KeyError((text, li0, li1))
def pause_after(li):
    """(start,end) of the silent gap after line li"""
    t1 = LINEI[li]['t1']
    for a, b in PAUSES:
        if abs(a - t1) < 0.5 or (a <= t1 <= b): return (max(a, t1), b)
    return (t1, t1 + 0.5)
def marked_pauses():
    return [pause_after(i) for i, l in enumerate(LINES) if l[1]]
def scene_of(t):
    for s in SCENES:
        if s['t0'] <= t < s['t1']: return s['n']
    return 46
def caption_chunks():
    """list of dict(words=[(text,t0,t1)], t0, t1)"""
    chunks = []; cur = []
    def flush():
        nonlocal cur
        if cur: chunks.append(cur); cur = []
    for li in range(len(LINES)):
        ws = line_words(li)
        for w in ws:
            cur.append(w)
            ln = sum(len(x['w']) + 1 for x in cur)
            endp = w['w'][-1] in '.?!' or w['w'].endswith('...')
            comma = w['w'][-1] in ',;'
            if endp or ln > 40 or (comma and len(cur) >= 3 and ln > 22): flush()
        flush()
    out = []
    for i, ch in enumerate(chunks):
        t0 = ch[0]['t0'] - 0.05
        t1 = ch[-1]['t1'] + 0.3
        if i + 1 < len(chunks): t1 = min(t1, chunks[i + 1][0]['t0'] - 0.02)
        out.append(dict(words=[(w['w'], w['t0'], w['t1']) for w in ch], t0=t0, t1=t1))
    return out
