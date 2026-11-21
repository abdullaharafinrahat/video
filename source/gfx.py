"""Vector canvas (aggdraw, 2x supersampled) with virtual camera, parallax layers, legend wobble."""
import math, aggdraw, numpy as np
from PIL import Image
W, H, SS = 1280, 720, 2
CX, CY = 640, 295           # camera pivot: content window is y 0..590, captions live below
def C(c):
    if isinstance(c, str):
        h = c.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    return tuple(int(v) for v in c)
P = {k: C(v) for k, v in dict(navy='#0F1B2D', teal='#1F6F78', sand='#D9C9A3', terra='#C8553D',
                              amber='#F2A93B', cream='#F4EDE0', ink='#101418').items()}
INK = P['ink']; CREAM = P['cream']; NAVY = P['navy']; TEAL = P['teal']; SAND = P['sand']; TERRA = P['terra']; AMBER = P['amber']
def mix(a, b, t):
    a = C(a); b = C(b); t = max(0, min(1, t)); return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
def dark(c, f): return mix(c, INK, f)
def light(c, f): return mix(c, P['cream'], f)
def clamp(x, a=0., b=1.): return a if x < a else b if x > b else x
def sstep(x): x = clamp(x); return x * x * (3 - 2 * x)
def lerp(a, b, t): return a + (b - a) * t
def prog(t, a, b): return clamp((t - a) / max(1e-6, b - a))
def kf(t, keys):
    """keyframes [(t,(v..)),...] smooth interpolation (tuples)"""
    if t <= keys[0][0]: return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t <= t1:
            u = sstep((t - t0) / max(1e-6, t1 - t0)); return tuple(lerp(a, b, u) for a, b in zip(v0, v1))
    return keys[-1][1]
def lin(t, keys):
    if t <= keys[0][0]: return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t <= t1:
            u = (t - t0) / max(1e-6, t1 - t0); return tuple(lerp(a, b, u) for a, b in zip(v0, v1))
    return keys[-1][1]
def smooth(pts, n=5):
    out = []; m = len(pts)
    for i in range(m - 1):
        p0 = pts[max(0, i - 1)]; p1 = pts[i]; p2 = pts[i + 1]; p3 = pts[min(m - 1, i + 2)]
        for s in range(n):
            u = s / n
            out.append((.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * u + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * u * u + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * u ** 3),
                        .5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * u + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * u * u + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * u ** 3)))
    out.append(pts[-1]); return out
_grads = {}
def vgrad(top, bot, h=H, w=W, y0=0.0, y1=1.0):
    k = (C(top), C(bot), h, w, y0, y1)
    if k not in _grads:
        t = np.clip((np.linspace(0, 1, h * SS) - y0) / max(1e-6, y1 - y0), 0, 1)[:, None, None]
        a = np.array(C(top), np.float32)[None, None, :]; b = np.array(C(bot), np.float32)[None, None, :]
        arr = (a + (b - a) * t).astype(np.uint8); arr = np.repeat(arr, w * SS, axis=1)
        _grads[k] = Image.fromarray(arr, 'RGB')
    return _grads[k]
_fonts = {}; _pens = {}; _brushes = {}
FONTS = dict(sans='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', sansr='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
             serif='/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf', serifr='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf')
def pen(c, w, op=255):
    k = (c, round(w, 1), op)
    if k not in _pens:
        if len(_pens) > 3000: _pens.clear()
        _pens[k] = aggdraw.Pen(c, max(.5, w), op)
    return _pens[k]
def brush(c, op=255):
    k = (c, op)
    if k not in _brushes:
        if len(_brushes) > 3000: _brushes.clear()
        _brushes[k] = aggdraw.Brush(c, op)
    return _brushes[k]
def font(c, kind, size, op=255):
    k = (c, kind, int(size), op)
    if k not in _fonts:
        if len(_fonts) > 400: _fonts.clear()
        _fonts[k] = aggdraw.Font(c, FONTS[kind], int(size), op)
    return _fonts[k]

class Canvas:
    def __init__(s, bg=None, mode='E', ta=0.0):
        if isinstance(bg, Image.Image): s.im = bg.copy()
        else: s.im = Image.new('RGB', (W * SS, H * SS), C(bg if bg is not None else P['navy']))
        s.d = aggdraw.Draw(s.im); s.mode = mode; s.ta = ta
        s.cx, s.cy, s.z = CX, CY, 1.0; s.shx = s.shy = 0.; s.hudm = False
        s.wob = 0.0; s.ph = 0.0; s.loc = None
        if mode == 'L': s.wob = 1.3; s.ph = math.floor(ta * 10) * 1.93
        s.L(1.0)
    # camera
    def cam(s, x, y, z=1.0, shake=(0, 0)):
        s.cx, s.cy, s.z = x, y, z; s.shx, s.shy = shake; s.L(s.p if hasattr(s, 'p') else 1.0)
    def L(s, p):
        s.p = p; s.k = 1 + (s.z - 1) * p; s.ax = CX + (s.cx - CX) * p; s.ay = CY + (s.cy - CY) * p; s.hudm = False
    def hud(s): s.hudm = True; s.k = 1.0
    def push(s, ox, oy, sc=1.0, dx=0.0, dy=0.0): s.loc = (ox, oy, sc, dx, dy)
    def pop(s): s.loc = None
    def T(s, x, y):
        if s.hudm: return x * SS, y * SS
        if s.loc: ox, oy, sc, dx, dy = s.loc; x = ox + (x - ox) * sc + dx; y = oy + (y - oy) * sc + dy
        X = (x - s.ax) * s.k + CX + s.shx; Y = (y - s.ay) * s.k + CY + s.shy
        if s.wob:
            X += s.wob * math.sin(y * .05 + s.ph) + .6 * math.sin(y * .13 + s.ph * 1.7)
            Y += s.wob * math.sin(x * .05 + s.ph * 1.3) + .6 * math.sin(x * .11 + s.ph)
        return X * SS, Y * SS
    def lw(s, w): return w * SS * (1.0 if s.hudm else clamp(s.k, .7, 2.2))
    def _ps(s, f, l, lw, op):
        a = []
        if l is not None: a.append(pen(C(l), s.lw(lw), op))
        if f is not None: a.append(brush(C(f), op))
        return a
    def poly(s, pts, f=None, l=None, lw=2.5, op=255):
        flat = []
        for x, y in pts:
            X, Y = s.T(x, y); flat += [X, Y]
        a = s._ps(f, l, lw, op)
        if a: s.d.polygon(flat, *a)
    def line(s, pts, col=INK, lw=2.5, op=255):
        flat = []
        for x, y in pts:
            X, Y = s.T(x, y); flat += [X, Y]
        s.d.line(flat, pen(C(col), s.lw(lw), op))
    def rect(s, x, y, w, h, f=None, l=None, lw=2.5, op=255):
        s.poly([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], f, l, lw, op)
    def ell(s, x, y, rx, ry, f=None, l=None, lw=2.5, op=255):
        X0, Y0 = s.T(x - rx, y - ry); X1, Y1 = s.T(x + rx, y + ry)
        if s.wob or abs(X1 - X0) < 1: return s.poly([(x + rx * math.cos(a * .5236), y + ry * math.sin(a * .5236)) for a in range(12)], f, l, lw, op)
        a = s._ps(f, l, lw, op)
        if a: s.d.ellipse((X0, Y0, X1, Y1), *a)
    def circ(s, x, y, r, f=None, l=None, lw=2.5, op=255): s.ell(x, y, r, r, f, l, lw, op)
    def dash(s, pts, col, lw=2, on=8, off=7, op=255):
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            d = math.hypot(x1 - x0, y1 - y0); n = max(1, int(d / (on + off)))
            for i in range(n):
                a = i * (on + off) / d; b = min(1, (i * (on + off) + on) / d)
                s.line([(x0 + (x1 - x0) * a, y0 + (y1 - y0) * a), (x0 + (x1 - x0) * b, y0 + (y1 - y0) * b)], col, lw, op)
    def tsize(s, txt, size, kind='sans'):
        f = font(INK, kind, size * SS); w, h = s.d.textsize(txt, f); return w / SS, h / SS
    def text(s, x, y, txt, size=30, col=P['cream'], kind='sans', anchor='c', op=255, outline=None, ow=3, spacing=0):
        zs = 1.0 if s.hudm else s.k
        sz = size * zs
        X, Y = s.T(x, y)
        if spacing:
            ws = [s.tsize(ch, sz, kind)[0] + spacing * zs for ch in txt]; tot = sum(ws) - spacing * zs
            cx = X - tot * SS / 2 if anchor == 'c' else X
            for ch, w in zip(txt, ws):
                s._dt(cx, Y, ch, sz, col, kind, 'l', op, outline, ow); cx += w * SS
            return
        s._dt(X, Y, txt, sz, col, kind, anchor, op, outline, ow)
    def _dt(s, X, Y, txt, sz, col, kind, anchor, op, outline, ow):
        f = font(C(col), kind, sz * SS, op); w, h = s.d.textsize(txt, f)
        if anchor == 'c': X -= w / 2
        elif anchor == 'r': X -= w
        Y -= h / 2
        if outline is not None:
            fo = font(C(outline), kind, sz * SS, op)
            for a in range(8):
                s.d.text((X + math.cos(a * .785) * ow * SS, Y + math.sin(a * .785) * ow * SS), txt, fo)
        s.d.text((X, Y), txt, f)
    def paste(s, img, x, y, w, h, op=255, border=None):
        """paste a 1280x720 PIL image scaled into a box (screen space)"""
        s.d.flush()
        im = img.resize((int(w * SS), int(h * SS)), Image.BILINEAR)
        if op < 255: im.putalpha(op); s.im.paste(im, (int(x * SS), int(y * SS)), im)
        else: s.im.paste(im, (int(x * SS), int(y * SS)))
        s.d = aggdraw.Draw(s.im)
    def finish(s):
        s.d.flush(); return s.im.reduce(SS)

# ---------------- shared rigs ----------------
def wave_rig(c, t, y, x0, x1, col, depth_cols=None, amp=1.0, level=0.0, ybot=700, calm=1.0, op=255, speed=1.0):
    """one looping wave-line system, three parallax layers; used for every sea/gulf"""
    cols = depth_cols or [mix(col, P['navy'], .35), col, light(col, .12)]
    for i, (p, a, wl, sp, yo) in enumerate([(.82, 5, 150, .5, -9), (1.0, 7, 110, .8, 0), (1.18, 9, 80, 1.1, 11)]):
        c.L(p); pts = []
        n = int((x1 - x0) / 30) + 2
        for j in range(n + 1):
            x = x0 + (x1 - x0) * j / n
            pts.append((x, y + level + yo * (1 if i else 1) + amp * calm * a * math.sin(x / wl * 6.283 + t * sp * speed * 1.3 + i * 2) + amp * calm * a * .4 * math.sin(x / wl * 13 - t * sp * speed * .9)))
        c.poly(pts + [(x1, ybot), (x0, ybot)], cols[i], None, op=op)
        c.line(pts, light(cols[i], .35), 1.8, op=int(op * .7))
    c.L(1.0)

_noise = None
def grain(shape=(H, W), seed=0):
    global _noise
    if _noise is None:
        r = np.random.default_rng(5)
        n = r.normal(0, 1, (H + 64, W + 64)).astype(np.float32)
        from scipy.ndimage import gaussian_filter
        _noise = (gaussian_filter(n, .8) * 2.4 + gaussian_filter(r.normal(0, 1, (H + 64, W + 64)).astype(np.float32), 6) * 14).astype(np.float32)
    ox = (seed * 37) % 60; oy = (seed * 23) % 60
    return _noise[oy:oy + H, ox:ox + W]

_lf = None
def legend_frame():
    """Greek-key border around the content window + darker terracotta caption band (cached)"""
    global _lf
    if _lf: return _lf
    img = Image.new('RGB', (W * SS, H * SS), (0, 0, 0)); mask = Image.new('L', (W * SS, H * SS), 0)
    d = aggdraw.Draw(img); m = aggdraw.Draw(mask)
    band = dark(P['terra'], .38)
    m.rectangle((0, 0, W * SS, 28 * SS), brush(255)); m.rectangle((0, 0, 28 * SS, 590 * SS), brush(255))
    m.rectangle(((W - 28) * SS, 0, W * SS, 590 * SS), brush(255)); m.rectangle((0, 562 * SS, W * SS, H * SS), brush(255))
    d.rectangle((0, 0, W * SS, H * SS), brush(band))
    u = 4.0
    def key_strip(a0, b0, length, vertical):
        n = int(length / (8 * u))
        for i in range(n + 1):
            pts = [(0, 6 * u), (0, 0), (6 * u, 0), (6 * u, 4 * u), (2 * u, 4 * u), (2 * u, 2 * u), (4 * u, 2 * u)]
            flat = []
            for px, py in pts:
                al = a0 + i * 8 * u + px; cr = b0 + py
                X, Y = (al, cr) if not vertical else (cr, al)
                flat += [X * SS, Y * SS]
            d.line(flat, pen(dark(P['terra'], .75), 2.2 * SS))
    for (x0, y0, ln, v) in [(32, 4, W - 64, False), (4, 32, 560 - 32, True), (W - 28, 32, 560 - 32, True)]:
        key_strip(x0, y0, ln, v)
    for (x0, y0, x1, y1) in [(28, 28, W - 28, 28), (28, 28, 28, 562), (W - 28, 28, W - 28, 562), (28, 562, W - 28, 562)]:
        d.line((x0 * SS, y0 * SS, x1 * SS, y1 * SS), pen(INK, 3 * SS))
    d.line((28 * SS, 3 * SS, (W - 28) * SS, 3 * SS), pen(INK, 2 * SS)); d.line((28 * SS, 24 * SS, (W - 28) * SS, 24 * SS), pen(INK, 2 * SS))
    d.flush(); m.flush()
    _lf = (img.reduce(SS), mask.reduce(SS)); return _lf
