"""Frame engine: scene context, post effects (legend grain/frame, scrim, captions, transitions)."""
import math, bisect
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import timing as T
from gfx import *

class K:
    def __init__(s, n, t, fi):
        s.n = n; s.t = t; s.fi = fi; s.t0, s.t1 = T.scene(n); s.d = s.t1 - s.t0; s.a = s.t0 + t
        s.ta = math.floor(t * 10) / 10; s.fx = {}
    def cue(s, li, word=None, occ=0, end=False):
        if word is None: return T.line_t(li)[1 if end else 0] - s.t0
        return T.wfind(word, li, li, occ, end) - s.t0
    def lt(s, li, k=0): return T.wt(li, k) - s.t0
    def le(s, li, k=-1): return T.wte(li, k) - s.t0
    def beat(s, starts):
        """index of the current beat given ascending local start times (-1 before first)"""
        return bisect.bisect_right(starts, s.t) - 1
    def p(s, a, b): return prog(s.t, a, b)
    def cv(s, bg=None, mode='E'): return Canvas(bg, mode, s.ta)
    def pause_t(s, li): a, b = T.pause_after(li); return a - s.t0, b - s.t0

def shake(t, t0, amp=8, decay=7, freq=40):
    if t < t0: return (0, 0)
    e = amp * math.exp(-(t - t0) * decay)
    return (e * math.sin((t - t0) * freq), e * math.cos((t - t0) * freq * 1.3))
def ease_out(u): u = clamp(u); return 1 - (1 - u) ** 3
def ease_in(u): u = clamp(u); return u ** 3
def pop(u, over=.25):  # overshoot scale 0..1
    u = clamp(u); return 1 + over * math.sin(u * math.pi) * (1 - u) if u < 1 else 1.0

# ---------- HUD text helpers (screen space, always inside y<585) ----------
def title(c, txt, y=120, size=64, col=CREAM, kind='serif', spacing=0, op=255, ow=4):
    c.hud(); c.text(640, y, txt, size, col, kind, 'c', op, INK, ow, spacing)
def tag(c, x, y, txt, size=26, col=INK, bg=CREAM, op=255, anchor='c'):
    c.hud(); w, h = c.tsize(txt, size, 'sans'); pad = 12
    x0 = x - w / 2 if anchor == 'c' else x
    c.poly([(x0 - pad, y - h / 2 - 6), (x0 + w + pad, y - h / 2 - 6), (x0 + w + pad, y + h / 2 + 6), (x0 - pad, y + h / 2 + 6)], bg, INK, 2.5, op)
    c.text(x0 + w / 2, y, txt, size, col, 'sans', 'c', op)
    return x0, w

# ---------- legend post (grain + meander frame) ----------
_lfi = None
def legend_post(img, ta):
    global _lfi
    fr, mask = legend_frame()
    img = img.copy(); img.paste(fr, (0, 0), mask)
    a = np.asarray(img).astype(np.float32)
    g = grain(seed=int(ta * 10))
    a += g[..., None] * np.array([1.0, .9, .8], np.float32)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
_scrim = None
def scrim(arr):
    global _scrim
    if _scrim is None:
        y = np.arange(H); al = np.clip((y - 556) / 44, 0, 1) * .62; _scrim = al[:, None, None].astype(np.float32)
    nv = np.array(P['navy'], np.float32)
    a = arr[540:].astype(np.float32); s = _scrim[540:]
    arr[540:] = (a * (1 - s) + nv * s).astype(np.uint8); return arr

# ---------- captions ----------
_CH = T.caption_chunks(); _CHT = [c['t0'] for c in _CH]
_cf = ImageFont.truetype(FONTS['sans'], 40)
def captions(img, a):
    if a >= T.DUR - .05: return img
    i = bisect.bisect_right(_CHT, a) - 1
    if i < 0: return img
    ch = _CH[i]
    if a > ch['t1']: return img
    ws = ch['words']; sp = _cf.getlength(' ')
    wl = [_cf.getlength(w[0]) for w in ws]; tot = sum(wl) + sp * (len(ws) - 1)
    lines = [list(range(len(ws)))]
    if tot > 1120:
        best = None
        for k in range(1, len(ws)):
            l1 = sum(wl[:k]) + sp * (k - 1); l2 = sum(wl[k:]) + sp * (len(ws) - k - 1)
            sc = max(l1, l2)
            if best is None or sc < best[0]: best = (sc, k)
        lines = [list(range(best[1])), list(range(best[1], len(ws)))]
    cur = max([j for j, w in enumerate(ws) if w[1] <= a] or [0])
    d = ImageDraw.Draw(img)
    ys = [650] if len(lines) == 1 else [626, 674]
    for ln, y in zip(lines, ys):
        wid = sum(wl[j] for j in ln) + sp * (len(ln) - 1); x = 640 - wid / 2
        for j in ln:
            col = P['amber'] if j == cur else P['cream']
            d.text((x, y), ws[j][0], font=_cf, fill=col, stroke_width=5, stroke_fill=INK, anchor='lm'); x += wl[j] + sp
    return img

# ---------- transitions ----------
INTO = {2: 'cut', 3: 'whip', 4: 'zoom', 5: 'whip', 6: 'zoom', 7: 'cut', 8: 'whip', 9: 'zoom', 10: 'whip', 11: 'whip', 12: 'whip', 13: 'cut', 14: 'zoom',
        15: 'whip', 16: 'zoom', 17: 'whip', 18: 'zoom', 19: 'whip', 20: 'whip', 21: 'cut', 22: 'whip', 23: 'cut', 24: 'whip', 25: 'match', 26: 'zoom',
        27: 'whip', 28: 'cut', 29: 'whip', 30: 'cut', 31: 'zoom', 32: 'whip', 33: 'whip', 34: 'cut', 35: 'zoom', 36: 'whip', 37: 'whip', 38: 'cut',
        39: 'zoom', 40: 'whip', 41: 'cut', 42: 'cut', 43: 'cut', 44: 'whip', 45: 'cut', 46: 'cut'}
def _zoom(img, z):
    if abs(z - 1) < 1e-3: return img
    w, h = W / z, H / z; x0 = (W - w) / 2; y0 = CY - h * CY / H
    return img.transform((W, H), Image.EXTENT, (x0, y0, x0 + w, y0 + h), Image.BILINEAR)
def trans_fx(img, kind, u, out, sign):
    """u 0..1 progress of transition; out=True for leaving scene"""
    if kind in ('cut', 'match'):
        if kind == 'match': return _zoom(img, 1 + .08 * (u if out else (1 - u)))
        return img
    e = ease_in(u) if out else 1 - ease_out(1 - u) if False else (1 - ease_out(u)) if False else None
    if kind == 'whip':
        e = ease_in(u) if out else (1 - ease_out(u))
        dx = int(W * .95 * e * (-sign if out else sign))
        a = np.asarray(img).astype(np.float32); acc = 0
        for f in (0.55, .7, .85, 1.0): acc = acc + np.roll(a, int(dx * f), axis=1)
        return Image.fromarray((acc / 4).astype(np.uint8))
    if kind == 'zoom':
        e = ease_in(u) if out else (1 - ease_out(u))
        z = 1 + (.9 if out else -.35) * e * (1 if out else 1)
        acc = np.zeros((H, W, 3), np.float32)
        for f in (0, .04, .08, .12): acc += np.asarray(_zoom(img, max(.4, z + f * e * (1 if out else -1) * 2))).astype(np.float32)
        return Image.fromarray((acc / 4).astype(np.uint8))
    return img

def finish_frame(k, c, trans=None):
    """Canvas/PIL -> final 1280x720 PIL frame with post-fx"""
    img = c.finish() if hasattr(c, 'finish') else c
    mode = k.fx.get('mode', 'E')
    if k.fx.get('mode') == 'L':
        img = legend_post(img, k.ta)
    else:
        arr = np.asarray(img).copy(); arr = scrim(arr); img = Image.fromarray(arr)
    ds = k.fx.get('desat')
    if ds:
        a = np.asarray(img).astype(np.float32); g = a.mean(2, keepdims=True); img = Image.fromarray((a * (1 - ds) + g * ds).astype(np.uint8))
    if k.fx.get('post'): img = k.fx['post'](img)
    if trans: img = trans(img)
    fd = k.fx.get('fade')
    if fd:
        col, al = fd
        if al > 0: img = Image.blend(img, Image.new('RGB', (W, H), C(col)), clamp(al))
    fl = k.fx.get('flash', 0)
    if fl > 0: img = Image.blend(img, Image.new('RGB', (W, H), (255, 255, 255)), clamp(fl))
    return img
