"""Tiny 2D toolkit: 2x supersampled canvas in 1280x720 logical coordinates."""
import os, math, random, json, re
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
S = 2
LW, LH = 1280, 720
W, H = LW * S, LH * S
OL = (34, 22, 18)  # comic outline colour


# ----------------------------------------------------------------- helpers
def hx(c):
    if isinstance(c, tuple):
        return c
    c = c.lstrip('#')
    if len(c) == 3:
        c = ''.join(ch * 2 for ch in c)
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    a, b = hx(a), hx(b)
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def shade(c, f):
    c = hx(c)
    return tuple(max(0, min(255, int(v * f))) for v in c)


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def eo(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def seg(t, a, b):
    return clamp((t - a) / (b - a)) if b != a else 1.0


def lerp(a, b, t):
    return a + (b - a) * t


_fonts = {}


def font(name, size):
    """size in logical px (for the 2x canvas)."""
    return font_px(name, size * S)


def font_px(name, px, bold=False):
    key = (name, px, bold)
    if key not in _fonts:
        if name.startswith('DejaVu'):
            path = '/usr/share/fonts/truetype/dejavu/' + name
        else:
            path = os.path.join(HERE, 'fonts', name)
        f = ImageFont.truetype(path, int(px))
        if bold:
            try:
                f.set_variation_by_axes([700])
            except Exception:
                pass
        _fonts[key] = f
    return _fonts[key]


def vgrad(w, h, stops):
    ys = np.linspace(0, 1, h)
    pos = [p for p, _ in stops]
    cols = np.array([hx(c) for _, c in stops], float)
    arr = np.stack([np.interp(ys, pos, cols[:, i]) for i in range(3)], -1)
    arr = np.repeat(arr[:, None, :], w, 1)
    return Image.fromarray(arr.astype('uint8'), 'RGB')


_noise_cache = {}


def noise(w, h, cell, seed=0, octaves=3):
    key = (w, h, cell, seed, octaves)
    if key in _noise_cache:
        return _noise_cache[key]
    rng = np.random.default_rng(seed)
    acc = np.zeros((h, w), np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        c = max(2, int(cell / (2 ** o)))
        small = rng.random((h // c + 2, w // c + 2)).astype(np.float32)
        im = Image.fromarray((small * 255).astype('uint8')).resize((w, h), Image.BICUBIC)
        acc += amp * np.asarray(im, np.float32) / 255.0
        tot += amp
        amp *= 0.5
    acc /= tot
    acc = (acc - acc.min()) / (acc.max() - acc.min() + 1e-6)
    _noise_cache[key] = acc
    return acc


def texture(w, h, cell, seed, c1, c2, octaves=3):
    n = noise(w, h, cell, seed, octaves)[..., None]
    a, b = np.array(hx(c1), np.float32), np.array(hx(c2), np.float32)
    return Image.fromarray((a + (b - a) * n).astype('uint8'), 'RGB')


_radial = {}


def radial_mask(r):
    r = max(2, int(r // 4 * 4 + 4))
    if r not in _radial:
        ys, xs = np.mgrid[-r:r, -r:r].astype(np.float32)
        d = np.sqrt(xs * xs + ys * ys) / r
        m = np.clip(1 - d, 0, 1) ** 2
        _radial[r] = Image.fromarray((m * 255).astype('uint8'), 'L')
    return _radial[r]


# ----------------------------------------------------------------- canvas
class G:
    def __init__(self, im=None):
        self.im = im.copy() if im is not None else Image.new('RGB', (W, H))
        self.d = ImageDraw.Draw(self.im)

    # --- geometry helpers
    @staticmethod
    def P(pts):
        return [(x * S, y * S) for x, y in pts]

    def poly(self, pts, fill=None, ol=None, w=2):
        p = self.P(pts)
        self.d.polygon(p, fill=fill)
        if ol:
            self.d.line(p + [p[0]], fill=ol, width=max(1, int(w * S)), joint='curve')

    def ell(self, cx, cy, rx, ry=None, fill=None, ol=None, w=2):
        ry = rx if ry is None else ry
        self.d.ellipse([(cx - rx) * S, (cy - ry) * S, (cx + rx) * S, (cy + ry) * S],
                       fill=fill, outline=ol, width=max(1, int(w * S)) if ol else 0)

    def rect(self, x0, y0, x1, y1, fill=None, ol=None, w=2, r=0):
        box = [x0 * S, y0 * S, x1 * S, y1 * S]
        if r > 0:
            self.d.rounded_rectangle(box, radius=r * S, fill=fill, outline=ol,
                                     width=max(1, int(w * S)) if ol else 0)
        else:
            self.d.rectangle(box, fill=fill, outline=ol, width=max(1, int(w * S)) if ol else 0)

    def line(self, pts, fill, w=2, round_ends=False):
        p = self.P(pts)
        self.d.line(p, fill=fill, width=max(1, int(w * S)), joint='curve')
        if round_ends:
            r = w * S / 2
            for (x, y) in (p[0], p[-1]):
                self.d.ellipse([x - r, y - r, x + r, y + r], fill=fill)

    def arc(self, cx, cy, rx, ry, a0, a1, fill, w=2):
        self.d.arc([(cx - rx) * S, (cy - ry) * S, (cx + rx) * S, (cy + ry) * S], a0, a1,
                   fill=fill, width=max(1, int(w * S)))

    def text(self, x, y, t, f, fill, anchor='la'):
        self.d.text((x * S, y * S), t, font=f, fill=fill, anchor=anchor)

    # --- alpha primitives
    def polyA(self, pts, color, a):
        if a <= 0:
            return
        p = self.P(pts)
        xs = [q[0] for q in p]
        ys = [q[1] for q in p]
        x0, y0 = max(0, int(min(xs)) - 1), max(0, int(min(ys)) - 1)
        x1, y1 = min(W, int(max(xs)) + 2), min(H, int(max(ys)) + 2)
        if x1 <= x0 or y1 <= y0:
            return
        m = Image.new('L', (x1 - x0, y1 - y0), 0)
        ImageDraw.Draw(m).polygon([(x - x0, y - y0) for x, y in p], fill=int(255 * clamp(a)))
        self.im.paste(hx(color), (x0, y0, x1, y1), m)

    def ellA(self, cx, cy, rx, ry, color, a):
        pts = [(cx + rx * math.cos(i * math.pi / 18), cy + ry * math.sin(i * math.pi / 18)) for i in range(36)]
        self.polyA(pts, color, a)

    def rectA(self, x0, y0, x1, y1, color, a):
        self.polyA([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], color, a)

    def glow(self, cx, cy, r, color, a=1.0):
        if a <= 0:
            return
        m = radial_mask(r * S)
        n = m.size[0]
        if a < 0.999:
            lut = [int(v * a) for v in range(256)]
            m = m.point(lut)
        x0, y0 = int(cx * S - n / 2), int(cy * S - n / 2)
        cx0, cy0 = max(0, x0), max(0, y0)
        cx1, cy1 = min(W, x0 + n), min(H, y0 + n)
        if cx1 <= cx0 or cy1 <= cy0:
            return
        mm = m.crop((cx0 - x0, cy0 - y0, cx1 - x0, cy1 - y0))
        patch = self.im.crop((cx0, cy0, cx1, cy1))
        col = Image.new('RGB', patch.size, hx(color))
        lit = ImageChops.add(patch, Image.composite(col, Image.new('RGB', patch.size, (0, 0, 0)), mm))
        self.im.paste(lit, (cx0, cy0))

    def shadowblob(self, cx, cy, rx, ry, a=0.35):
        self.ellA(cx, cy, rx, ry, (10, 8, 6), a)

    def paste_rgba(self, spr, x, y, a=1.0):
        """spr is RGBA image at 2x resolution; x,y logical top-left."""
        if a < 0.999:
            al = spr.getchannel('A').point([int(v * a) for v in range(256)])
            spr = spr.copy()
            spr.putalpha(al)
        self.im.paste(spr, (int(x * S), int(y * S)), spr)

    def paste_rgb(self, img, x, y):
        self.im.paste(img, (int(x * S), int(y * S)))

    def gradrect(self, x0, y0, x1, y1, stops):
        w, h = int((x1 - x0) * S), int((y1 - y0) * S)
        self.im.paste(vgrad(w, h, stops), (int(x0 * S), int(y0 * S)))


# ----------------------------------------------------------------- camera / post
def camera(im, cx, cy, z):
    """cx,cy in logical coords: centre of view; z zoom."""
    vw, vh = W / z, H / z
    x0 = clamp(cx * S - vw / 2, 0, W - vw)
    y0 = clamp(cy * S - vh / 2, 0, H - vh)
    return im.resize((LW, LH), Image.BILINEAR, box=(x0, y0, x0 + vw, y0 + vh))


_vig = None
_grain = None


def post(img, t, fade=1.0, warm=0.0):
    global _vig, _grain
    if _vig is None:
        ys, xs = np.mgrid[0:LH, 0:LW].astype(np.float32)
        d = np.sqrt(((xs - LW / 2) / (LW / 2)) ** 2 + ((ys - LH / 2) / (LH / 2)) ** 2)
        _vig = (1 - 0.34 * np.clip(d - 0.45, 0, 1.2) ** 1.6)[..., None].astype(np.float32)
        rng = np.random.default_rng(7)
        _grain = [(rng.standard_normal((LH, LW, 1)) * 4.2).astype(np.float32) for _ in range(6)]
    a = np.asarray(img, np.float32)
    a = a * _vig
    a = a + _grain[int(t * 12) % 6]
    if warm:
        a[..., 0] *= 1 + 0.05 * warm
        a[..., 2] *= 1 - 0.07 * warm
    a *= fade
    return Image.fromarray(np.clip(a, 0, 255).astype('uint8'), 'RGB')


# ----------------------------------------------------------------- overlays (1x)
def _parchment(w, h, seed=3, jag=5):
    rng = random.Random(seed)
    pts = []
    n = 26
    for i in range(n):
        pts.append((i * w / (n - 1), rng.uniform(0, jag)))
    for i in range(n // 3):
        pts.append((w - rng.uniform(0, jag), (i + 1) * h / (n // 3 + 1)))
    for i in range(n):
        pts.append((w - i * w / (n - 1), h - rng.uniform(0, jag)))
    for i in range(n // 3):
        pts.append((rng.uniform(0, jag), h - (i + 1) * h / (n // 3 + 1)))
    big = Image.new('RGBA', (w * 2, h * 2), (0, 0, 0, 0))
    tex = texture(w * 2, h * 2, 40, seed, '#d9bd88', '#f0dcaa')
    mask = Image.new('L', (w * 2, h * 2), 0)
    ImageDraw.Draw(mask).polygon([(x * 2, y * 2) for x, y in pts], fill=255)
    big.paste(tex, (0, 0), mask)
    d = ImageDraw.Draw(big)
    d.line([(x * 2, y * 2) for x, y in pts] + [(pts[0][0] * 2, pts[0][1] * 2)], fill=(92, 58, 28, 255), width=5, joint='curve')
    for i in range(5):
        cx, cy = rng.uniform(0, w * 2), rng.uniform(0, h * 2)
        d.ellipse([cx - 30, cy - 12, cx + 30, cy + 12], fill=(150, 110, 60, 30))
    return big.resize((w, h), Image.LANCZOS)


_banner_cache = {}


def banner(text, sub=None, size=26, w=None, seed=3):
    key = (text, sub, size, w, seed)
    if key in _banner_cache:
        return _banner_cache[key]
    f = font_px('Cinzel.ttf', size, bold=True)
    f2 = font_px('Crimson.ttf', size * 0.8)
    tw = f.getbbox(text)[2]
    if sub:
        tw = max(tw, f2.getbbox(sub)[2])
    w = w or int(tw + 60)
    h = int(size * 1.9 + (size * 1.0 if sub else 0))
    p = _parchment(w, h, seed)
    d = ImageDraw.Draw(p)
    if sub:
        d.text((w / 2, size * 1.05), text, font=f, fill=(58, 34, 16, 255), anchor='mm')
        d.text((w / 2, size * 1.05 + size * 0.95), sub, font=f2, fill=(90, 56, 28, 255), anchor='mm')
    else:
        d.text((w / 2, h / 2 + 1), text, font=f, fill=(58, 34, 16, 255), anchor='mm')
    _banner_cache[key] = p
    return p


def paste_over(img, spr, x, y, a=1.0):
    if a < 0.999:
        al = spr.getchannel('A').point([int(v * a) for v in range(256)])
        spr = spr.copy()
        spr.putalpha(al)
    img.paste(spr, (int(x), int(y)), spr)


# ----------------------------------------------------------------- captions
FIX = {'katsunopoulu': 'Katsonopoulou', 'stephen': 'Steven', 'soder': 'Soter', 'helikei': 'Helike',
       'helikes': "Helike's", 'seismological': 'Seismological', 'research': 'Research', 'letters': 'Letters',
       'sorter': 'Soter', 'katsonopoulou': 'Katsonopoulou'}


def load_captions(t0, t1, path=None):
    d = json.load(open(path or os.path.join(HERE, 'tr.json')))
    chunks = []
    for sg in d:
        words = [(w, a, b) for (w, a, b) in sg['w'] if a >= t0 - 0.05 and a < t1]
        if not words:
            continue
        cleaned = []
        for w, a, b in words:
            core = re.sub(r'[^A-Za-z]', '', w)
            tok = w.strip()
            if core.lower() in FIX:
                tok = tok.replace(core, FIX[core.lower()])
            cleaned.append((tok, a, b))
        n = len(cleaned)
        per = 9
        k = max(1, round(n / per))
        sz = math.ceil(n / k)
        for i in range(0, n, sz):
            chunks.append(cleaned[i:i + sz])
    out = []
    for i, part in enumerate(chunks):
        start = part[0][1]
        end = part[-1][2] + 0.35
        if i + 1 < len(chunks):
            end = min(end, chunks[i + 1][0][1] - 0.02)
            end = max(end, part[-1][2] + 0.05)
        out.append((start, end, part))
    return out


def draw_caption(img, chunks, T, alpha=1.0):
    cur = None
    for s, e, part in chunks:
        if s - 0.08 <= T <= e:
            cur = (s, e, part)
            break
    if not cur:
        return
    s, e, part = cur
    a = clamp(min((T - (s - 0.08)) / 0.12, (e - T) / 0.12 + 0.2)) * alpha
    f = font_px('Lora.ttf', 31, bold=True)
    words = [w for w, _, _ in part]
    maxw = 1020
    lines, curl = [], []
    for i, w in enumerate(words):
        test = ' '.join([x for x, _ in curl] + [w])
        if f.getlength(test) > maxw and curl:
            lines.append(curl)
            curl = []
        curl.append((w, i))
    lines.append(curl)
    lh = 44
    th = lh * len(lines) + 16
    tw = max(f.getlength(' '.join(w for w, _ in l)) for l in lines) + 56
    cx, y0 = LW / 2, LH - 30 - th
    plate = Image.new('RGBA', (int(tw), int(th)), (0, 0, 0, 0))
    ImageDraw.Draw(plate).rounded_rectangle([0, 0, tw - 1, th - 1], radius=18, fill=(14, 10, 8, 150))
    paste_over(img, plate, cx - tw / 2, y0, a)
    d = ImageDraw.Draw(img, 'RGBA')
    for li, l in enumerate(lines):
        lw = f.getlength(' '.join(w for w, _ in l))
        x = cx - lw / 2
        y = y0 + 8 + li * lh + lh / 2
        for w, i in l:
            ws, we = part[i][1], part[i][2]
            spoken = T >= ws - 0.02
            active = ws - 0.02 <= T <= we + 0.08
            col = (255, 214, 120) if active else ((255, 255, 255) if spoken else (206, 200, 190))
            col = col + (int(255 * a),)
            d.text((x + 2, y + 2), w, font=f, fill=(0, 0, 0, int(200 * a)), anchor='lm')
            d.text((x, y), w, font=f, fill=col, anchor='lm')
            x += f.getlength(w + ' ')


def lower_third(img, name, role, a=1.0, x=48, y=470):
    spr = banner(name, role, size=24, seed=11)
    paste_over(img, spr, x - (1 - eo(a)) * 80, y, clamp(a))
