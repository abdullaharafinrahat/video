"""Core 2D graphics engine: supersampled canvas, camera, painterly texture, sprites."""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops, ImageOps

W, H, FPS = 1280, 720, 24
LW, LH = 1536, 864          # standard "world layer" size (1.2x output)
FONT_DIR = 'fonts/'

_fc = {}
def font(name, size, wght=None):
    k = (name, size, wght)
    if k not in _fc:
        f = ImageFont.truetype(FONT_DIR + name, size)
        if wght:
            try: f.set_variation_by_axes([wght])
            except Exception: pass
        _fc[k] = f
    return _fc[k]

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def lerp(a, b, t): return a + (b - a) * t
def sstep(a, b, x):
    if b == a: return 1.0 if x >= b else 0.0
    t = clamp((x - a) / (b - a)); return t * t * (3 - 2 * t)
def ease_out(t): t = clamp(t); return 1 - (1 - t) ** 3
def ease_back(t):
    c = 1.70158; t = clamp(t) - 1; return 1 + (c + 1) * t ** 3 + c * t ** 2
def mix(c1, c2, t): return tuple(int(lerp(a, b, t)) for a, b in zip(c1, c2))
def rgb(h):
    h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
def shade(c, f): return tuple(int(clamp(v * f, 0, 255)) for v in c[:3]) + tuple(c[3:])

# ------------------------------------------------------------------ canvas
class Canvas:
    def __init__(self, w, h, ss=2, bg=(0, 0, 0, 0)):
        self.w, self.h, self.ss = w, h, ss
        self.im = Image.new('RGBA', (int(w * ss), int(h * ss)), bg)
        self.d = ImageDraw.Draw(self.im, 'RGBA')

    def _p(self, pts): return [(x * self.ss, y * self.ss) for x, y in pts]
    def poly(self, pts, fill): self.d.polygon(self._p(pts), fill=fill)
    def rect(self, x0, y0, x1, y1, fill):
        self.d.rectangle([min(x0, x1) * self.ss, min(y0, y1) * self.ss, max(x0, x1) * self.ss, max(y0, y1) * self.ss], fill=fill)
    def ellipse(self, x0, y0, x1, y1, fill):
        self.d.ellipse([min(x0, x1) * self.ss, min(y0, y1) * self.ss, max(x0, x1) * self.ss, max(y0, y1) * self.ss], fill=fill)
    def circle(self, x, y, r, fill): self.ellipse(x - r, y - r, x + r, y + r, fill)
    def line(self, pts, fill, width=1):
        self.d.line(self._p(pts), fill=fill, width=max(1, int(width * self.ss)), joint='curve')
    def rrect(self, x0, y0, x1, y1, r, fill):
        self.d.rounded_rectangle([x0 * self.ss, y0 * self.ss, x1 * self.ss, y1 * self.ss], radius=r * self.ss, fill=fill)
    def arc(self, box, a0, a1, fill, width=1):
        x0, y0, x1, y1 = box
        self.d.arc([x0 * self.ss, y0 * self.ss, x1 * self.ss, y1 * self.ss], a0, a1, fill=fill, width=max(1, int(width * self.ss)))
    def text(self, xy, s, f, fill, anchor='la'):
        self.d.text((xy[0] * self.ss, xy[1] * self.ss), s, font=f, fill=fill, anchor=anchor)

    def _blit(self, arr, x, y):
        ss = self.ss; x = int(x * ss); y = int(y * ss)
        h, w = arr.shape[:2]
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.im.width, x + w), min(self.im.height, y + h)
        if x1 <= x0 or y1 <= y0: return
        sub = arr[y0 - y:y1 - y, x0 - x:x1 - x]
        self.im.alpha_composite(Image.fromarray(sub, 'RGBA'), (x0, y0))

    def grad_poly(self, pts, top, bot, y0=None, y1=None, hshade=None):
        """polygon filled with vertical gradient top->bot between y0..y1 (1x coords)."""
        ss = self.ss
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        bx0, bx1 = int(max(0, min(xs))), int(min(self.w, max(xs)) + 2)
        by0, by1 = int(max(0, min(ys))), int(min(self.h, max(ys)) + 2)
        if bx1 <= bx0 or by1 <= by0: return
        if y0 is None: y0 = min(ys)
        if y1 is None: y1 = max(ys)
        bw, bh = (bx1 - bx0) * ss, (by1 - by0) * ss
        m = Image.new('L', (bw, bh), 0)
        ImageDraw.Draw(m).polygon([((x - bx0) * ss, (y - by0) * ss) for x, y in pts], fill=255)
        yy = (np.arange(bh) / ss + by0 - y0) / max(1e-6, (y1 - y0))
        yy = np.clip(yy, 0, 1)[:, None, None]
        t = np.array(top, np.float32)[None, None, :]; b = np.array(bot, np.float32)[None, None, :]
        if len(top) == 3: t = np.concatenate([t, [[[255]]]], 2); b = np.concatenate([b, [[[255]]]], 2)
        col = t + (b - t) * yy
        col = np.broadcast_to(col, (bh, bw, 4)).copy()
        if hshade is not None:
            xx = np.linspace(0, 1, bw)[None, :, None]
            col[..., :3] *= (1 + hshade * (0.5 - xx))
        col[..., 3] *= np.asarray(m, np.float32) / 255.0
        self._blit(np.clip(col, 0, 255).astype(np.uint8), bx0, by0)

    def hgrad_rect(self, x0, y0, x1, y1, stops):
        """horizontal gradient rect. stops: [(pos, rgba)]"""
        ss = self.ss
        w, h = int((x1 - x0) * ss), int((y1 - y0) * ss)
        if w <= 0 or h <= 0: return
        xs = np.linspace(0, 1, w)
        ps = [s[0] for s in stops]
        arr = np.zeros((h, w, 4), np.float32)
        for ch in range(4):
            vals = [(s[1] + (255,))[ch] for s in stops]
            arr[:, :, ch] = np.interp(xs, ps, vals)[None, :]
        self._blit(arr.astype(np.uint8), x0, y0)

    def image(self, scale=1.0):
        if self.ss == 1: return self.im
        return self.im.resize((int(self.w * scale), int(self.h * scale)), Image.LANCZOS)


def vgrad_img(w, h, stops):
    """vertical gradient RGB image; stops: [(pos 0..1, rgb)]"""
    ys = np.linspace(0, 1, h); ps = [s[0] for s in stops]
    arr = np.zeros((h, w, 4), np.uint8); arr[..., 3] = 255
    for ch in range(3):
        arr[:, :, ch] = np.interp(ys, ps, [s[1][ch] for s in stops])[:, None]
    return Image.fromarray(arr, 'RGBA')

# ------------------------------------------------------------------ texture
def _noise(w, h, gw, gh, rng):
    g = rng.standard_normal((gh, gw)).astype(np.float32)
    return np.asarray(Image.fromarray(g, 'F').resize((w, h), Image.BICUBIC))

def paint_tex(img, amt=0.07, seed=0):
    """painterly brush-like texture on an RGBA image (keeps alpha)."""
    rng = np.random.default_rng(seed)
    w, h = img.size
    arr = np.asarray(img).astype(np.float32)
    n = _noise(w, h, max(2, w // 60), max(2, h // 60), rng) * 0.6
    n += _noise(w, h, max(2, w // 120), max(2, h // 6), rng) * 0.22     # vertical strokes
    n += _noise(w, h, max(2, w // 6), max(2, h // 120), rng) * 0.25     # horizontal strokes
    n += _noise(w, h, w // 2, h // 2, rng) * 0.35
    arr[..., :3] *= (1 + amt * n)[..., None]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGBA')

# ------------------------------------------------------------------ camera / compositing
def cam(layer, zoom, cx, cy, out=(W, H), rot=0.0):
    a = 1.0 / zoom
    if rot == 0.0:
        return layer.transform(out, Image.AFFINE, (a, 0, cx - out[0] / 2 * a, 0, a, cy - out[1] / 2 * a), resample=Image.BILINEAR)
    c, s = math.cos(rot) * a, math.sin(rot) * a
    ox, oy = out[0] / 2, out[1] / 2
    return layer.transform(out, Image.AFFINE, (c, -s, cx - c * ox + s * oy, s, c, cy - s * ox - c * oy), resample=Image.BILINEAR)

def put(base, spr, x, y, op=1.0):
    """alpha-composite sprite at (x,y) top-left with opacity & clipping."""
    x = int(round(x)); y = int(round(y))
    sw, sh = spr.size
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(base.width, x + sw), min(base.height, y + sh)
    if x1 <= x0 or y1 <= y0 or op <= 0: return
    s = spr.crop((x0 - x, y0 - y, x1 - x, y1 - y))
    if op < 0.999:
        a = s.getchannel('A').point([int(i * op) for i in range(256)])
        s = s.copy(); s.putalpha(a)
    base.alpha_composite(s, (x0, y0))

def fade(img, op):
    if op >= 0.999: return img
    a = img.getchannel('A').point([int(i * op) for i in range(256)])
    o = img.copy(); o.putalpha(a); return o

_blobs = {}
def blob(r, color=(255, 255, 255), alpha=255, power=2.0):
    r = int(max(2, r)); k = (r // 2 * 2, color, alpha, power)
    if k not in _blobs:
        yy, xx = np.mgrid[-r:r, -r:r].astype(np.float32)
        d = np.sqrt(xx * xx + yy * yy) / r
        a = np.clip(1 - d, 0, 1) ** power * alpha
        arr = np.zeros((2 * r, 2 * r, 4), np.uint8)
        arr[..., 0], arr[..., 1], arr[..., 2] = color
        arr[..., 3] = a.astype(np.uint8)
        _blobs[k] = Image.fromarray(arr, 'RGBA')
        if len(_blobs) > 400: _blobs.pop(next(iter(_blobs)))
    return _blobs[k]

def glow(base, x, y, r, color=(255, 230, 160), op=1.0, power=2.0):
    b = blob(r, color, 255, power); put(base, b, x - r, y - r, op)

def add_light(base, x, y, r, color, op=1.0):
    """additive glow (screen-like) directly into base RGBA."""
    r = int(r); x = int(x); y = int(y)
    x0, y0, x1, y1 = max(0, x - r), max(0, y - r), min(base.width, x + r), min(base.height, y + r)
    if x1 <= x0 or y1 <= y0: return
    b = np.asarray(blob(r, color, 255, 2.0).crop((x0 - (x - r), y0 - (y - r), x1 - (x - r), y1 - (y - r)))).astype(np.float32)
    reg = np.asarray(base.crop((x0, y0, x1, y1))).astype(np.float32)
    a = (b[..., 3:4] / 255.0) * op
    reg[..., :3] = 255 - (255 - reg[..., :3]) * (1 - a * b[..., :3] / 255.0)
    base.paste(Image.fromarray(np.clip(reg, 0, 255).astype(np.uint8), 'RGBA'), (x0, y0))

# ------------------------------------------------------------------ terrain helpers
def ridge(n, base, amp, seed, rough=0.55, octaves=6, scale=1.0):
    rng = np.random.default_rng(seed)
    y = np.zeros(n, np.float32); a = 1.0; tot = 0
    for o in range(octaves):
        k = 3 * 2 ** o
        y += np.interp(np.linspace(0, k, n), np.arange(k + 1), rng.standard_normal(k + 1)) * a
        tot += a; a *= rough
    y /= tot
    return base + y * amp

def fill_ridge(cv, ys, top, bot, ybot, rim=None, ss=None):
    """fill below a ridge polyline (ys per 1x-pixel column) w/ vertical gradient."""
    ss = cv.ss
    n = cv.im.width
    ysx = np.interp(np.linspace(0, len(ys) - 1, n), np.arange(len(ys)), ys) * ss
    Y = np.arange(cv.im.height)[:, None].astype(np.float32)
    t = np.clip((Y - ysx[None, :]) / max(1, (ybot * ss - ysx.min())), 0, 1)
    arr = np.zeros((cv.im.height, n, 4), np.float32)
    for ch in range(3): arr[..., ch] = top[ch] + (bot[ch] - top[ch]) * t
    mask = np.clip(Y - ysx[None, :] + 0.5, 0, 1)
    if rim is not None:
        rt = np.clip(1 - (Y - ysx[None, :]) / (6 * ss), 0, 1) * mask
        for ch in range(3): arr[..., ch] = arr[..., ch] * (1 - rt * 0.6) + rim[ch] * rt * 0.6
    arr[..., 3] = mask * 255
    cv.im.alpha_composite(Image.fromarray(arr.astype(np.uint8), 'RGBA'))

def clouds(w, h, seed, n=14, col=(255, 255, 255), shade_col=(200, 212, 235), alpha=235, scale=1.0):
    """horizontally tileable soft cloud layer (no dark halos)."""
    rnd = random.Random(seed)
    body = Image.new('L', (w, h), 0); shd = Image.new('L', (w, h), 0)
    db, ds = ImageDraw.Draw(body), ImageDraw.Draw(shd)
    for _ in range(n):
        cx, cy = rnd.uniform(0, w), rnd.uniform(h * 0.15, h * 0.85)
        sc = rnd.uniform(0.6, 1.2) * scale
        blobs = [(rnd.uniform(-90, 90) * sc, rnd.uniform(-12, 8) * sc, rnd.uniform(16, 34) * sc) for _ in range(11)]
        for dx in (-w, 0, w):
            for bx, by, br in blobs:
                ds.ellipse([cx + dx + bx - br * 1.2, cy + by - br * 0.2, cx + dx + bx + br * 1.2, cy + by + br * 0.75], fill=255)
                db.ellipse([cx + dx + bx - br, cy + by - br * 0.75, cx + dx + bx + br, cy + by + br * 0.5], fill=255)
    body = body.filter(ImageFilter.GaussianBlur(4)); shd = shd.filter(ImageFilter.GaussianBlur(6))
    b = np.asarray(body, np.float32) / 255; sh = np.asarray(shd, np.float32) / 255
    under = np.clip(sh - b * 0.9, 0, 1)            # shadow only where body is absent -> underside
    k = np.clip(under * 1.6, 0, 1)[..., None]
    arr = np.zeros((h, w, 4), np.float32)
    arr[..., :3] = np.array(col, np.float32) * (1 - k) + np.array(shade_col, np.float32) * k
    arr[..., 3] = np.clip(np.maximum(b, sh * 0.85), 0, 1) * alpha
    return Image.fromarray(arr.astype(np.uint8), 'RGBA')

def tile_scroll(layer, dx):
    return ImageChops.offset(layer, int(dx) % layer.width, 0)

# ------------------------------------------------------------------ architecture
STONE = (232, 222, 200)
def column(cv, cx, base, h, w, stone=STONE, broken=0.0, seed=0, flutes=True, capital=True):
    """Doric column; broken in [0,1) = fraction of height missing from top."""
    top = base - h * (1 - broken)
    L = shade(stone, 1.06); M = stone; D = shade(stone, 0.72)
    cv.hgrad_rect(cx - w / 2, top, cx + w / 2, base, [(0, L + (255,)), (0.35, M + (255,)), (1, D + (255,))])
    if flutes:
        n = 5
        for i in range(1, n):
            x = cx - w / 2 + w * i / n
            cv.line([(x, top), (x, base)], shade(stone, 0.8 - 0.12 * i / n) + (90,), 0.8)
    if broken > 0.02:
        r = random.Random(seed)
        pts = [(cx - w / 2, top + r.uniform(0, 6))]
        for i in range(1, 5): pts.append((cx - w / 2 + w * i / 4, top + r.uniform(-4, 8)))
        pts += [(cx + w / 2, top + r.uniform(0, 6))]
        cv.poly(pts + [(cx + w / 2, top + 14), (cx - w / 2, top + 14)], D + (255,))
        cv.poly(pts + [(cx + w / 2, top + 4), (cx - w / 2, top + 4)], shade(stone, 0.88) + (255,))
    elif capital:
        cv.rect(cx - w * 0.5, top - 2, cx + w * 0.5, top + 1, shade(stone, 0.9) + (255,))
        cv.poly([(cx - w * 0.55, top - 4), (cx + w * 0.55, top - 4), (cx + w * 0.48, top), (cx - w * 0.48, top)], shade(stone, 0.95) + (255,))
        cv.rect(cx - w * 0.72, top - 8, cx + w * 0.72, top - 4, L + (255,))
    # base shadow
    cv.ellipse(cx - w * 0.8, base - 2, cx + w * 1.2, base + 3, (40, 30, 20, 70))

def temple_front(cv, cx, base, ncols, col_h, col_w, gap, stone=STONE, roof=(196, 120, 84), ruin=0.0, seed=1, steps=3, pediment=True):
    r = random.Random(seed)
    total = (ncols - 1) * gap + col_w
    x0, x1 = cx - total / 2, cx + total / 2
    # steps
    for i in range(steps):
        sh = 5
        cv.rect(x0 - 12 - (steps - i) * 6, base - (steps - i) * sh, x1 + 12 + (steps - i) * 6, base - (steps - i - 1) * sh, shade(stone, 0.96 - 0.05 * i) + (255,))
        cv.rect(x0 - 12 - (steps - i) * 6, base - (steps - i - 1) * sh - 1, x1 + 12 + (steps - i) * 6, base - (steps - i - 1) * sh, shade(stone, 1.1) + (255,))
    yb = base - steps * 5
    # back wall (cella) shadow
    cv.rect(x0 + col_w, yb - col_h, x1 - col_w, yb, shade(stone, 0.45) + (255,))
    cv.rect(x0 + col_w, yb - col_h, x1 - col_w, yb - col_h + 10, (30, 22, 18, 120))
    for i in range(ncols):
        b = ruin * r.random() if ruin else 0
        column(cv, x0 + col_w / 2 + i * gap, yb, col_h, col_w, stone, broken=b, seed=seed + i)
    if ruin: return
    # entablature
    ah = col_h * 0.1
    ytop = yb - col_h - 8
    cv.rect(x0 - 8, ytop - ah, x1 + 8, ytop, shade(stone, 0.93) + (255,))
    fh = col_h * 0.1
    cv.rect(x0 - 8, ytop - ah - fh, x1 + 8, ytop - ah, shade(stone, 1.02) + (255,))
    for i in range(int((x1 - x0) / (gap / 2.2))):
        xx = x0 - 4 + i * gap / 2.2
        cv.rect(xx, ytop - ah - fh + 2, xx + col_w * 0.18, ytop - ah - 2, shade(stone, 0.55) + (255,))
    cv.rect(x0 - 14, ytop - ah - fh - 5, x1 + 14, ytop - ah - fh, shade(stone, 1.08) + (255,))
    if pediment:
        yp = ytop - ah - fh - 5
        ph = col_h * 0.2
        cv.poly([(x0 - 14, yp), (x1 + 14, yp), (cx, yp - ph)], shade(stone, 1.05) + (255,))
        cv.poly([(x0 + 8, yp - 2), (x1 - 8, yp - 2), (cx, yp - ph + 7)], shade(stone, 0.62) + (255,))
        for k in range(7):  # relief figures
            fx = cx + (k - 3) * total / 11
            hh = ph * 0.4 * (1 - abs(k - 3) / 5)
            cv.rect(fx - 2, yp - 4 - hh, fx + 2, yp - 4, shade(stone, 0.95) + (255,))
        cv.poly([(x0 - 14, yp), (x1 + 14, yp), (x1 + 14, yp - 4), (cx, yp - ph - 4), (x0 - 14, yp - 4)], roof + (255,))
        cv.poly([(x0 - 14, yp - 4), (cx, yp - ph - 4), (cx, yp - ph - 9), (x0 - 18, yp - 6)], shade(roof, 1.15) + (255,))
        cv.poly([(cx, yp - ph - 4), (x1 + 14, yp - 4), (x1 + 18, yp - 6), (cx, yp - ph - 9)], shade(roof, 0.85) + (255,))
        cv.circle(cx, yp - ph - 10, 4, shade(stone, 1.0) + (255,))

def house(cv, x, y, w, h, wall, roof, seed=0, flat=True):
    """little white-washed house, light from the left."""
    r = random.Random(seed)
    sw = w * 0.32
    cv.rect(x, y - h, x + w, y, wall + (255,))
    cv.poly([(x + w, y - h), (x + w + sw, y - h * 0.9), (x + w + sw, y + h * 0.1), (x + w, y)], shade(wall, 0.72) + (255,))
    if flat:
        cv.poly([(x - 2, y - h), (x + w + 2, y - h), (x + w + sw + 2, y - h * 0.9), (x + sw - 1, y - h * 0.9)], shade(wall, 1.05) + (255,))
        cv.rect(x - 1, y - h - 2, x + w + 1, y - h, shade(roof, 0.9) + (255,))
    else:
        cv.poly([(x - 3, y - h), (x + w + 3, y - h), (x + w + sw + 3, y - h * 0.88), (x + w * 0.5 + sw * 0.5, y - h - w * 0.28)], roof + (255,))
        cv.poly([(x - 3, y - h), (x + w * 0.5 + sw * 0.5, y - h - w * 0.28), (x + w * 0.5, y - h - w * 0.28 + 1)], shade(roof, 1.15) + (255,))
    # door + windows
    dw = max(3, w * 0.2)
    cv.rect(x + w * 0.15, y - h * 0.5, x + w * 0.15 + dw, y, (70, 50, 40, 255))
    if w > 22:
        cv.rect(x + w * 0.6, y - h * 0.65, x + w * 0.6 + dw * 0.8, y - h * 0.35, (60, 70, 90, 255))
        cv.rect(x + w * 0.6 - 1, y - h * 0.66, x + w * 0.6 + dw * 0.8 + 1, y - h * 0.65, shade(wall, 0.8) + (255,))
    cv.rect(x, y - 1.5, x + w + sw, y + 1, (60, 45, 35, 70))

def cypress(cv, x, y, h, w=None, col=(36, 74, 52)):
    w = w or h * 0.22
    cv.poly([(x, y - h), (x + w, y - h * 0.4), (x + w * 0.7, y), (x - w * 0.7, y), (x - w, y - h * 0.4)], col + (255,))
    cv.poly([(x, y - h), (x - w, y - h * 0.4), (x - w * 0.7, y), (x, y)], shade(col, 1.25) + (255,))

def tree(cv, x, y, h, col=(70, 100, 60)):
    cv.rect(x - h * 0.04, y - h * 0.45, x + h * 0.04, y, (80, 62, 48, 255))
    for dx, dy, r in [(-0.2, -0.65, .24), (0.2, -0.62, .22), (0, -0.82, .26), (-0.05, -0.55, .22)]:
        cv.circle(x + dx * h, y + dy * h, r * h, col + (255,))
    for dx, dy, r in [(-0.22, -0.7, .12), (0.0, -0.9, .14)]:
        cv.circle(x + dx * h, y + dy * h, r * h, shade(col, 1.3) + (255,))

# ------------------------------------------------------------------ people
SKINS = [(228, 176, 130), (206, 150, 104), (182, 124, 84), (240, 196, 158)]

def person(h=220, phase=0.0, tunic=(240, 235, 225), cloak=None, hair=(50, 36, 28), skin=(206, 150, 104),
           female=False, beard=False, facing=1, mood='calm', carry=None, run=0.0, arms_up=0.0, ss=3, belt=(150, 110, 60)):
    pad = 0.24 * h if (carry or arms_up > 0) else 0
    w = int(h * 0.95 + pad * 0.6); hh = int(h * 1.06 + pad)
    c = Canvas(w, hh, ss)
    s = float(h); cx = w / 2 - pad * 0.1; top = 0.04 * s + pad
    lean = run * 0.10 * s
    head = (cx + lean * 1.3, top + 0.07 * s)
    shy = top + 0.19 * s; hipy = top + 0.50 * s
    shx = cx + lean * 0.8
    sw = math.sin(phase)
    bob = abs(math.cos(phase)) * 0.012 * s * (1 + run)
    # legs
    leg_col = skin
    feet = []
    for side in (0, 1):
        ph = phase + side * math.pi
        a = math.sin(ph) * (0.34 + 0.35 * run)
        k = (cx + math.sin(a) * 0.24 * s, hipy + math.cos(a) * 0.24 * s)
        bend = max(0.0, -math.cos(ph)) * (0.55 + 0.6 * run)
        b = a - bend
        f = (k[0] + math.sin(b) * 0.25 * s, k[1] + math.cos(b) * 0.25 * s)
        feet.append((k, f, side))
    for k, f, side in sorted(feet, key=lambda z: z[2]):
        col = shade(leg_col, 0.85 if side else 1.0)
        c.line([(cx, hipy), k, f], col + (255,), 0.065 * s)
        c.ellipse(f[0] - 0.06 * s, f[1] - 0.02 * s, f[0] + 0.09 * s, f[1] + 0.035 * s, (96, 66, 44, 255))
    # back arm
    def arm(side, up, front):
        sx = shx + side * 0.095 * s
        sy = shy + 0.02 * s
        ang = -sw * 0.5 * side * (1 + run * 0.6)
        if up > 0:
            ang = lerp(ang, math.pi * (0.75 + 0.1 * math.sin(phase * 2 + side)) * -side, up)
        e = (sx + math.sin(ang) * 0.16 * s, sy + math.cos(ang) * 0.16 * s)
        ang2 = ang + (0.5 if up == 0 else -0.3 * side)
        hnd = (e[0] + math.sin(ang2) * 0.15 * s, e[1] + math.cos(ang2) * 0.15 * s)
        col = shade(skin, 0.9 if not front else 1.0)
        c.line([(sx, sy), e, hnd], col + (255,), 0.05 * s)
        c.circle(hnd[0], hnd[1], 0.03 * s, col + (255,))
        return hnd
    if carry != 'amphora': arm(-1, arms_up, False)
    # body
    sway = sw * 0.012 * s
    hem_y = top + (0.95 if female else 0.68) * s
    flare = 0.2 if female else 0.15
    hw = 0.115 * s
    body = [(shx - hw, shy), (shx + hw, shy), (cx + 0.1 * s, hipy), (cx + flare * s + sway, hem_y), (cx - flare * s + sway, hem_y), (cx - 0.1 * s, hipy)]
    c.poly(body, tunic + (255,))
    c.poly([(shx - hw, shy), (shx - hw * 0.2, shy), (cx - 0.02 * s, hem_y), (cx - flare * s + sway, hem_y), (cx - 0.1 * s, hipy)], shade(tunic, 1.06) + (255,))
    c.poly([(shx + hw * 0.4, shy), (shx + hw, shy), (cx + 0.1 * s, hipy), (cx + flare * s + sway, hem_y), (cx + flare * 0.4 * s + sway, hem_y)], shade(tunic, 0.82) + (255,))
    for i in range(4):  # drapery folds
        fx = cx + (i - 1.5) * flare * 0.45 * s
        c.line([(fx * 0.3 + cx * 0.7, hipy + 0.04 * s), (fx + sway, hem_y - 0.01 * s)], shade(tunic, 0.78) + (130,), 0.008 * s + 0.6)
    c.hem_y = hem_y
    c.line([(cx - 0.1 * s, hipy - 0.05 * s), (cx + 0.1 * s, hipy - 0.05 * s)], belt + (255,), 0.022 * s)
    if cloak:
        pts = [(shx - hw * 1.1, shy - 0.01 * s), (shx + hw * 0.6, shy - 0.01 * s), (cx + 0.16 * s, hipy + 0.12 * s + sway), (cx + 0.05 * s, top + 0.72 * s), (cx - 0.15 * s, hipy + 0.02 * s)]
        c.poly(pts, cloak + (255,))
        c.poly([pts[0], pts[1], (shx, shy + 0.1 * s)], shade(cloak, 1.2) + (255,))
        for i in range(3):
            c.line([(shx - hw * 0.5 + i * 0.07 * s, shy + 0.04 * s), (cx + (i - 0.5) * 0.08 * s + sway, hipy + 0.1 * s)], shade(cloak, 0.7) + (150,), 0.01 * s + 0.6)
    # neck + head
    c.rect(head[0] - 0.025 * s, head[1] + 0.04 * s, head[0] + 0.025 * s, shy + 0.01 * s, shade(skin, 0.9) + (255,))
    hr = 0.066 * s
    if female:
        c.ellipse(head[0] - hr * 1.25, head[1] - hr * 1.15 + bob, head[0] + hr * 1.25, head[1] + hr * 2.0 + bob, hair + (255,))
    c.ellipse(head[0] - hr * 0.88, head[1] - hr + bob, head[0] + hr * 0.88, head[1] + hr * 1.1 + bob, skin + (255,))
    # hair cap
    c.poly([(head[0] - hr * 0.95, head[1] - hr * 0.1 + bob), (head[0] - hr * 0.8, head[1] - hr * 0.9 + bob), (head[0], head[1] - hr * 1.3 + bob),
            (head[0] + hr * 0.8, head[1] - hr * 0.9 + bob), (head[0] + hr * 0.95, head[1] - hr * 0.1 + bob), (head[0] + hr * 0.4, head[1] - hr * 0.5 + bob),
            (head[0] - hr * 0.5, head[1] - hr * 0.55 + bob)], hair + (255,))
    if beard:
        c.poly([(head[0] - hr * 0.85, head[1] + hr * 0.2 + bob), (head[0] + hr * 0.85, head[1] + hr * 0.2 + bob), (head[0] + hr * 0.5, head[1] + hr * 1.7 + bob), (head[0], head[1] + hr * 1.9 + bob), (head[0] - hr * 0.5, head[1] + hr * 1.7 + bob)], hair + (255,))
        c.poly([(head[0] - hr * 0.4, head[1] + hr * 0.45 + bob), (head[0] + hr * 0.4, head[1] + hr * 0.45 + bob), (head[0], head[1] + hr * 0.55 + bob)], shade(hair, 1.3) + (255,))
    if s > 120:
        ey = head[1] - hr * 0.05 + bob
        fx = head[0] + hr * 0.18
        for ex in (fx - hr * 0.38, fx + hr * 0.38):
            if mood == 'scared':
                c.ellipse(ex - hr * 0.2, ey - hr * 0.2, ex + hr * 0.2, ey + hr * 0.2, (250, 250, 245, 255))
                c.circle(ex + hr * 0.03, ey, hr * 0.08, (30, 20, 15, 255))
            else:
                c.circle(ex, ey, hr * 0.09, (30, 20, 15, 255))
        by = ey - hr * (0.38 if mood == 'scared' else 0.25)
        c.line([(fx - hr * 0.6, by + (hr * 0.1 if mood == 'scared' else 0)), (fx - hr * 0.15, by - (hr * 0.1 if mood == 'scared' else 0))], hair + (255,), hr * 0.1)
        c.line([(fx + hr * 0.15, by - (hr * 0.1 if mood == 'scared' else 0)), (fx + hr * 0.6, by + (hr * 0.1 if mood == 'scared' else 0))], hair + (255,), hr * 0.1)
        if mood == 'scared':
            c.ellipse(fx - hr * 0.22, ey + hr * 0.5, fx + hr * 0.22, ey + hr * 0.95, (60, 20, 20, 255))
        elif not beard:
            c.line([(fx - hr * 0.2, ey + hr * 0.55), (fx + hr * 0.2, ey + hr * 0.55)], (150, 70, 60, 255), hr * 0.08)
    # front arm (+ carry)
    if carry == 'amphora':
        sx = shx + 0.095 * s; sy = shy + 0.02 * s
        hnd = (sx + 0.12 * s, sy - 0.15 * s)
        c.line([(sx, sy), (sx + 0.14 * s, sy + 0.1 * s), hnd], shade(skin, 1.0) + (255,), 0.05 * s)
        ax, ay = hnd[0] + 0.02 * s, hnd[1] - 0.04 * s
        am = (200, 110, 62)
        c.ellipse(ax - 0.1 * s, ay - 0.16 * s, ax + 0.1 * s, ay + 0.12 * s, am + (255,))
        c.ellipse(ax - 0.07 * s, ay - 0.14 * s, ax + 0.03 * s, ay + 0.06 * s, shade(am, 1.2) + (255,))
        c.rect(ax - 0.04 * s, ay - 0.26 * s, ax + 0.04 * s, ay - 0.14 * s, shade(am, 0.9) + (255,))
        c.rect(ax - 0.06 * s, ay - 0.28 * s, ax + 0.06 * s, ay - 0.25 * s, shade(am, 1.1) + (255,))
        c.arc((ax + 0.06 * s, ay - 0.24 * s, ax + 0.14 * s, ay - 0.08 * s), 270, 90, shade(am, 0.8) + (255,), 0.02 * s)
        c.line([(ax - 0.1 * s, ay - 0.05 * s), (ax + 0.1 * s, ay - 0.05 * s)], (90, 40, 25, 255), 0.012 * s)
        c.line([(ax - 0.095 * s, ay + 0.02 * s), (ax + 0.095 * s, ay + 0.02 * s)], (90, 40, 25, 255), 0.012 * s)
        c.circle(hnd[0], hnd[1], 0.03 * s, skin + (255,))
        arm(-1, 0, True)
    else:
        arm(1, arms_up, True)
    im = c.image()
    if facing < 0: im = ImageOps.mirror(im)
    return im

class Walker:
    """pre-rendered walk cycle."""
    def __init__(self, n=12, **kw):
        self.frames = [person(phase=2 * math.pi * i / n, **kw) for i in range(n)]
        self.n = n
    def get(self, ph):
        return self.frames[int(ph * self.n) % self.n]

def shadow_ell(w, h, a=90):
    c = Canvas(w, h, 1); c.ellipse(0, 0, w, h, (0, 0, 0, 255))
    im = c.im.filter(ImageFilter.GaussianBlur(max(1, h / 5)))
    r, g, b, al = im.split()
    return Image.merge('RGBA', (r, g, b, al.point(lambda v: v * a // 255)))

def bird(base, x, y, size, flap, col=(40, 40, 50)):
    d = ImageDraw.Draw(base, 'RGBA')
    f = math.sin(flap) * size * 0.5
    d.line([(x - size, y - f), (x - size * 0.4, y - size * 0.15 + f * 0.2), (x, y), (x + size * 0.4, y - size * 0.15 + f * 0.2), (x + size, y - f)], fill=col + (255,), width=max(1, int(size / 6)), joint='curve')

# ------------------------------------------------------------------ vignette / grade
_vig = None
def vignette():
    global _vig
    if _vig is None:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        d = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.68)) ** 2)
        _vig = (1 - 0.55 * np.clip(d - 0.45, 0, 1) ** 1.6)[..., None]
    return _vig

_grain = None
def grain(i):
    global _grain
    if _grain is None:
        rng = np.random.default_rng(5)
        _grain = [(rng.standard_normal((H, W, 1)) * 3.2).astype(np.float32) for _ in range(6)]
    return _grain[i % 6]
