import os, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

W, H, FPS = 1280, 720, 24
HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = {'cinzel': 'Cinzel.ttf', 'gar': 'EBGaramond.ttf', 'gari': 'EBGaramond-Italic.ttf'}
_fc = {}


def font(k, size, w=None):
    key = (k, size, w)
    if key not in _fc:
        f = ImageFont.truetype(os.path.join(HERE, 'fonts', FONTS[k]), size)
        if w:
            try:
                f.set_variation_by_axes([w])
            except Exception:
                pass
        _fc[key] = f
    return _fc[key]


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def eo(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def prog(t, a, b):
    return clamp((t - a) / (b - a))


def mix(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(min(len(c1), len(c2))))


def shade(c, f):
    return tuple(int(clamp(v * f, 0, 255)) for v in c[:3]) + tuple(c[3:])


def vgrad(w, h, stops):
    ys = np.linspace(0, 1, max(h, 1))
    pos = [s[0] for s in stops]
    arr = np.zeros((max(h, 1), 3), np.float32)
    for ch in range(3):
        arr[:, ch] = np.interp(ys, pos, [s[1][ch] for s in stops])
    return Image.fromarray(np.repeat(arr[:, None, :], max(w, 1), 1).astype(np.uint8), 'RGB')


def hgrad(w, h, stops):
    return vgrad(h, w, stops).transpose(Image.TRANSPOSE)


def fnoise(w, h, scale, seed=0, octs=4, persist=0.5):
    rng = np.random.default_rng(seed)
    out = np.zeros((h, w), np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octs):
        s = max(scale / (2 ** o), 2)
        gw, gh = int(w / s) + 3, int(h / s) + 3
        g = (rng.random((gh, gw)) * 255).astype(np.uint8)
        im = Image.fromarray(g).resize((w, h), Image.BICUBIC)
        out += np.asarray(im, np.float32) / 255 * amp
        tot += amp
        amp *= persist
    return out / tot


def ridge(n, seed, base, amp, scale=120, octs=4):
    rng = np.random.default_rng(seed)
    out = np.zeros(n)
    a, tot = 1.0, 0.0
    for o in range(octs):
        s = max(scale / (2 ** o), 3)
        g = rng.random(int(n / s) + 3)
        out += np.interp(np.arange(n) / s, np.arange(len(g)), g) * a
        tot += a
        a *= 0.5
    return base + (out / tot - 0.5) * 2 * amp


class SS:
    """Supersampled RGBA canvas; all coordinates are in output pixels."""

    def __init__(s, w, h, k=2, bg=(0, 0, 0, 0)):
        s.w, s.h, s.k = w, h, k
        s.im = Image.new('RGBA', (int(w * k), int(h * k)), bg)
        s.d = ImageDraw.Draw(s.im)

    def _p(s, pts):
        return [(x * s.k, y * s.k) for x, y in pts]

    def poly(s, pts, fill, outline=None, ow=1):
        if outline:
            s.d.polygon(s._p(pts), fill=fill, outline=outline, width=max(1, int(ow * s.k)))
        else:
            s.d.polygon(s._p(pts), fill=fill)

    def line(s, pts, fill, w=1, round_=True):
        P = s._p(pts)
        s.d.line(P, fill=fill, width=max(1, int(w * s.k)), joint='curve')
        if round_:
            r = w * s.k / 2
            for (x, y) in (P[0], P[-1]):
                s.d.ellipse((x - r, y - r, x + r, y + r), fill=fill)

    def ell(s, cx, cy, rx, ry=None, fill=None, outline=None, ow=1):
        ry = rx if ry is None else ry
        s.d.ellipse((s.k * (cx - rx), s.k * (cy - ry), s.k * (cx + rx), s.k * (cy + ry)), fill=fill,
                    outline=outline, width=max(1, int(ow * s.k)))

    def rect(s, x0, y0, x1, y1, fill=None, outline=None, ow=1):
        s.d.rectangle((s.k * x0, s.k * y0, s.k * x1, s.k * y1), fill=fill, outline=outline,
                      width=max(1, int(ow * s.k)))

    def rrect(s, x0, y0, x1, y1, r, fill=None, outline=None, ow=1):
        s.d.rounded_rectangle((s.k * x0, s.k * y0, s.k * x1, s.k * y1), radius=r * s.k, fill=fill, outline=outline,
                              width=max(1, int(ow * s.k)))

    def arc(s, cx, cy, rx, ry, a0, a1, fill, w=1):
        s.d.arc((s.k * (cx - rx), s.k * (cy - ry), s.k * (cx + rx), s.k * (cy + ry)), a0, a1, fill=fill,
                width=max(1, int(w * s.k)))

    def gpoly(s, pts, c1, c2, horizontal=False, mid=None):
        P = s._p(pts)
        xs, ys = [p[0] for p in P], [p[1] for p in P]
        x0, y0, x1, y1 = int(min(xs)), int(min(ys)), int(max(xs)) + 2, int(max(ys)) + 2
        w, h = max(x1 - x0, 2), max(y1 - y0, 2)
        stops = [(0, c1[:3]), (1, c2[:3])] if mid is None else [(0, c1[:3]), (0.5, mid[:3]), (1, c2[:3])]
        g = hgrad(w, h, stops) if horizontal else vgrad(w, h, stops)
        m = Image.new('L', (w, h), 0)
        ImageDraw.Draw(m).polygon([(x - x0, y - y0) for x, y in P], fill=255)
        s.im.paste(g, (x0, y0), m)

    def grect(s, x0, y0, x1, y1, c1, c2, horizontal=False, mid=None):
        s.gpoly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], c1, c2, horizontal, mid)

    def get(s):
        if s.k == 1:
            return s.im
        return s.im.reduce(int(s.k)) if float(s.k).is_integer() else s.im.resize((s.w, s.h), Image.LANCZOS)


def over(base, layer, xy=(0, 0)):
    """paste RGBA layer onto RGB base (in place) and return base"""
    base.paste(layer, xy, layer if layer.mode == 'RGBA' else None)
    return base


def fade_img(img, a):
    if a >= 0.999:
        return img
    r, g, b, al = img.split()
    al = al.point(lambda v: int(v * a))
    return Image.merge('RGBA', (r, g, b, al))


def blur(img, r):
    return img.filter(ImageFilter.GaussianBlur(r))


_rad = {}


def radial(r, color, power=2.0):
    key = (r, color, power)
    if key not in _rad:
        n = int(2 * r)
        yy, xx = np.mgrid[0:n, 0:n]
        d = np.sqrt((xx - r) ** 2 + (yy - r) ** 2) / r
        a = np.clip(1 - d, 0, 1) ** power
        arr = np.stack([a * color[0], a * color[1], a * color[2]], -1).astype(np.uint8)
        _rad[key] = Image.fromarray(arr, 'RGB')
    return _rad[key]


def glow_at(base, cx, cy, r, color, a=1.0, power=2.0):
    """screen-blend radial glow at (cx,cy) on RGB base (in place)"""
    r = int(max(r, 2))
    sp = radial(r, tuple(color[:3]), power)
    if a < 1:
        sp = sp.point(lambda v: int(v * a))
    x0, y0 = int(cx - r), int(cy - r)
    bx0, by0 = max(x0, 0), max(y0, 0)
    bx1, by1 = min(x0 + 2 * r, base.width), min(y0 + 2 * r, base.height)
    if bx1 <= bx0 or by1 <= by0:
        return base
    sub = sp.crop((bx0 - x0, by0 - y0, bx1 - x0, by1 - y0))
    reg = base.crop((bx0, by0, bx1, by1))
    base.paste(ImageChops.screen(reg, sub), (bx0, by0))
    return base


def plane(layer, cx, cy, zoom, bw=None, bh=None, out=(W, H)):
    bw = bw or out[0]
    bh = bh or out[1]
    w, h = bw / zoom, bh / zoom
    x0 = clamp(cx - w / 2, 0, layer.width - w)
    y0 = clamp(cy - h / 2, 0, layer.height - h)
    return layer.resize(out, Image.BILINEAR, box=(x0, y0, x0 + w, y0 + h))


_vig = {}


def vignette(img, strength=0.45):
    if strength not in _vig:
        yy, xx = np.mgrid[0:H, 0:W]
        d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / 1.41
        _vig[strength] = (1 - strength * np.clip(d, 0, 1) ** 2.2).astype(np.float32)[..., None]
    a = np.asarray(img.convert('RGB'), np.float32) * _vig[strength]
    return Image.fromarray(a.astype(np.uint8))


def tint(img, color, a):
    return Image.blend(img.convert('RGB'), Image.new('RGB', img.size, color), clamp(a))


def multiply_noise(img, amt=0.08, scale=30, seed=1):
    n = fnoise(img.width, img.height, scale, seed, 4)
    n = (1 - amt + amt * 2 * n)[..., None]
    a = np.asarray(img.convert('RGBA'), np.float32)
    a[..., :3] *= n
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')


def text_img(txt, f, fill, spacing=0, stroke=0, stroke_fill=None):
    tmp = Image.new('RGBA', (int(f.size * len(txt) * 1.3) + 60, int(f.size * 2) + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    x = 10
    if spacing == 0:
        d.text((10, 10), txt, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
    else:
        for ch in txt:
            d.text((x, 10), ch, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
            x += d.textlength(ch, font=f) + spacing
    bb = tmp.getbbox()
    return tmp.crop(bb) if bb else tmp
