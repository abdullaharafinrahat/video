"""
FIVE STEPS BEHIND — core rendering toolkit.
Procedural painted-landscape engine, compositing, lighting and post utilities.
Everything is resolution independent: S = H / 1080.
"""
import math
from functools import lru_cache

import cairo
import cv2
import numpy as np

W, H = 1920, 1080
S = H / 1080.0
FPS = 24
DURATION = 20.0
NFRAMES = int(FPS * DURATION)

SUN_AZ = 0.30     # sun sits a little left of the direction the friends face (+Z)
SUN_EL = 0.034    # sun sits just above the far range


def set_resolution(w, h):
    global W, H, S
    W, H, S = w, h, h / 1080.0


# ----------------------------------------------------------------- math utils
def clamp01(x):
    return np.clip(x, 0.0, 1.0)


def sstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def ease(t):
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)


def ease_io(t):
    t = min(max(t, 0.0), 1.0)
    return 4 * t * t * t if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2


def ease_out(t):
    t = min(max(t, 0.0), 1.0)
    return 1 - (1 - t) ** 3


def ease_in(t):
    t = min(max(t, 0.0), 1.0)
    return t * t * t


def mix(a, b, t):
    return a + (b - a) * t


def rgb(*c):
    return np.array(c, dtype=np.float32)


# ---------------------------------------------------------------------- noise
@lru_cache(None)
def _lat(seed, n):
    return np.random.RandomState(seed).rand(n).astype(np.float32)


def vnoise1(x, seed, period):
    v = _lat(seed, period)
    x = np.asarray(x, dtype=np.float64)
    i = np.floor(x).astype(np.int64)
    f = (x - i).astype(np.float32)
    u = f * f * (3 - 2 * f)
    return v[i % period] * (1 - u) + v[(i + 1) % period] * u


def fbm1(x, seed, period, octaves=5, gain=0.5, ridged=False):
    tot, amp, norm = 0.0, 1.0, 0.0
    for o in range(octaves):
        n = vnoise1(np.asarray(x) * (2 ** o), seed + 31 * o, int(period * 2 ** o))
        if ridged:
            n = (1.0 - np.abs(2 * n - 1)) ** 2
        tot = tot + amp * n
        norm += amp
        amp *= gain
    return tot / norm


def gust(t):
    """Shared wind-gust signal (0.3..1.0). Drives grass, cloth, hair AND the wind audio."""
    g = fbm1(t * 0.55 + 3.0, 777, 4096, octaves=3)
    return float(0.28 + 0.9 * sstep(0.25, 0.8, g))


def jitter(t, seed, freq=1.0):
    """Smooth -1..1 noise for micro motion."""
    return float(fbm1(t * freq + seed * 13.37, seed, 4096, octaves=2) * 2 - 1)


@lru_cache(None)
def fbm_tex(n, beta, seed, ax=1.0, ay=1.0, lowcut=2.0):
    """Tileable fractal texture (FFT synthesised), normalised to 0..1."""
    rng = np.random.RandomState(seed)
    wn = rng.standard_normal((n, n)).astype(np.float32)
    F = np.fft.rfft2(wn)
    ky = np.fft.fftfreq(n)[:, None] * n
    kx = np.fft.rfftfreq(n)[None, :] * n
    k = np.sqrt((kx * ax) ** 2 + (ky * ay) ** 2)
    k[0, 0] = 1.0
    amp = k ** (-beta) * (1 - np.exp(-(k / lowcut) ** 2))
    t = np.fft.irfft2(F * amp, s=(n, n)).astype(np.float32)
    lo, hi = np.percentile(t, 1), np.percentile(t, 99)
    return np.clip((t - lo) / (hi - lo), 0, 1).astype(np.float32)


def sample(tex, u, v):
    n = tex.shape[0]
    return cv2.remap(tex, np.mod(u, n).astype(np.float32), np.mod(v, n).astype(np.float32),
                     cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)


# ------------------------------------------------------------- view / camera
class View:
    """Pinhole camera that only yaws; pitch is expressed through the principal point."""

    def __init__(self, w, h, yaw, f, cx, cy):
        self.w, self.h, self.yaw, self.f, self.cx, self.cy = w, h, yaw, f, cx, cy
        xs = ((np.arange(w, dtype=np.float32) - cx) / f)[None, :]
        ys = ((cy - np.arange(h, dtype=np.float32)) / f)[:, None]
        cy_, sy_ = math.cos(yaw), math.sin(yaw)
        self.dx = (xs * cy_ + sy_) * np.ones((h, 1), np.float32)
        self.dz = (-xs * sy_ + cy_) * np.ones((h, 1), np.float32)
        self.dy = ys * np.ones((1, w), np.float32)
        hor = np.sqrt(self.dx ** 2 + self.dz ** 2)
        self.az = np.arctan2(self.dx, self.dz).astype(np.float32)
        self.el = np.arctan2(self.dy, hor).astype(np.float32)

    def project(self, X, Y, Z, cam):
        """world point -> canvas pixel for camera at cam=(cx,cy,cz)."""
        x, y, z = X - cam[0], Y - cam[1], Z - cam[2]
        c, s = math.cos(self.yaw), math.sin(self.yaw)
        xc = x * c - z * s
        zc = x * s + z * c
        zc = max(zc, 1e-3)
        return self.cx + self.f * xc / zc, self.cy - self.f * y / zc, zc


def sun_prox(az, el=None, k=1.0):
    d = np.abs(az - SUN_AZ)
    if el is not None:
        d = np.sqrt(d ** 2 + (el - SUN_EL) ** 2)
    return np.exp(-d * k)


# palette (display-referred floats, may exceed 1 for bloom)
ZENITH = rgb(0.20, 0.30, 0.46)
UPPER = rgb(0.47, 0.55, 0.66)
HOR_WARM = rgb(1.00, 0.80, 0.55)
HOR_COOL = rgb(0.86, 0.69, 0.66)
SUN_COL = rgb(1.00, 0.86, 0.62)
MIST = rgb(0.88, 0.74, 0.66)


def horizon_col(az):
    w = np.exp(-np.abs(az - SUN_AZ) * 1.6)[..., None]
    return mix(HOR_COOL, HOR_WARM, w)


def sky(view):
    az, el = view.az, view.el
    hc = horizon_col(az)
    t1 = sstep(0.0, 0.22, el)[..., None]
    t2 = sstep(0.12, 0.75, el)[..., None]
    col = mix(hc, UPPER, t1 ** 0.8)
    col = mix(col, ZENITH, t2)
    # below horizon (only visible through gaps) = mist
    col = np.where((el < 0)[..., None], mix(hc, MIST, sstep(0, -0.05, el)[..., None]), col)
    d = np.sqrt(((az - SUN_AZ) * np.cos(el)) ** 2 + (el - SUN_EL) ** 2)
    glow = 0.6 * np.exp(-d / 0.02) + 0.32 * np.exp(-d / 0.09) + 0.14 * np.exp(-d / 0.45)
    col = col + SUN_COL * glow[..., None]
    disc = sstep(0.0105, 0.0085, d)
    col = mix(col, rgb(1.9, 1.75, 1.45), disc[..., None])
    return col.astype(np.float32)


# mountain ranges: (distance_m, seed, base_el, amp, period, dark colour, haze)
RANGES = [
    dict(D=16000, seed=11, base=0.006, amp=0.075, period=22, dark=rgb(0.40, 0.40, 0.55), haze=0.66,
         peaks=[(0.16, 0.07, 0.09), (-0.45, 0.04, 0.07)]),
    dict(D=7000, seed=23, base=-0.010, amp=0.055, period=30, dark=rgb(0.25, 0.26, 0.38), haze=0.45,
         peaks=[(0.45, 0.04, 0.08), (-0.75, 0.05, 0.12)]),
    dict(D=2600, seed=37, base=-0.048, amp=0.05, period=36, dark=rgb(0.13, 0.15, 0.21), haze=0.24,
         peaks=[], sides=0.12),
]


def range_profile(r, az):
    x = (az / (2 * math.pi)) * r["period"]
    e = r["base"] + r["amp"] * (0.8 * fbm1(x, r["seed"], r["period"], octaves=7, gain=0.56, ridged=True)
                                + 0.25 * fbm1(x * 0.5, r["seed"] + 3, max(r["period"] // 2, 1), octaves=2))
    for (pa, ph, pw) in r["peaks"]:
        e = e + ph * np.exp(-((az - pa) / pw) ** 2) * (0.8 + 0.2 * fbm1(x * 3, r["seed"] + 5, r["period"] * 3))
    if "sides" in r:
        e = e + r["sides"] * sstep(0.15, 0.75, np.abs(az + 0.1))
    return e.astype(np.float32)


def mountains(view, cam_h=140.0):
    """Static RGBA (premultiplied) of all distant ranges, back to front."""
    az, el, f = view.az, view.el, view.f
    hgt, wid = az.shape
    out_c = np.zeros((hgt, wid, 3), np.float32)
    out_a = np.zeros((hgt, wid), np.float32)
    gully = fbm_tex(512, 1.05, 91, ax=0.25, ay=1.0)
    speck = fbm_tex(512, 0.8, 92)
    hc = horizon_col(az)
    for li, r in enumerate(RANGES):
        ridge_row = range_profile(r, az[0:1, :])  # profile depends on column only (yaw-only cam)
        ridge = np.repeat(ridge_row, hgt, axis=0)
        depth = ridge - el
        alpha = clamp01(depth * f / (1.2 * S) + 0.5)
        e_mist = -cam_h / r["D"]
        haze = r["haze"]
        base = mix(r["dark"], hc, haze)
        # painted sub-planes: a second, nearer ridge inside each range
        sub = ridge_row - 0.02 - 0.025 * fbm1((az[0:1, :] / (2 * math.pi)) * r["period"] * 2, r["seed"] + 9,
                                            r["period"] * 2, octaves=4)
        sub = np.repeat(sub, hgt, axis=0)
        in_sub = sstep(0.0, 0.006, sub - el)
        col = mix(base, mix(r["dark"], hc, haze * 0.92), (in_sub * 0.5)[..., None])
        # gullies / rock texture, brush-like streaks
        u = az * 900.0 / (1 + li)
        v = depth * 2600.0 / (1 + 0.5 * li)
        g = sample(gully, u, v)
        sp = sample(speck, u * 2.0, v * 2.0)
        col = col * (1 + ((g - 0.5) * 0.22 + (sp - 0.5) * 0.08) * (1 - haze))[..., None]
        # lit flanks: crude facet light from ridge slope (sun ahead -> faces turned to the sun glow)
        sp_az = sun_prox(az, k=3.0)
        # backlit rim + atmospheric glow at the crest
        dpos = np.maximum(depth, 0)
        rim = np.exp(-dpos * f / (1.1 * S)) * (0.05 + 1.3 * sp_az) * (1.2 - haze)
        crest_glow = np.exp(-dpos / 0.006) * (0.02 + 0.3 * sp_az) * (1.2 - haze)
        rim_sub = np.exp(-np.maximum(sub - el, 0) * f / (1.0 * S)) * in_sub * (0.0 + 0.2 * sp_az)
        col = col + (SUN_COL * (rim + crest_glow + rim_sub)[..., None]) * (0.35 + 0.65 * haze)
        # valley mist pooling toward the base
        mist_t = sstep(e_mist + 0.035, e_mist - 0.002, el)
        col = mix(col, mix(MIST, hc, 0.5), (mist_t * 0.9)[..., None])
        a = alpha * (1 - sstep(e_mist + 0.008, e_mist - 0.012, el))
        out_c = out_c * (1 - a[..., None]) + col * a[..., None]
        out_a = out_a * (1 - a) + a
    return out_c, out_a


# --------------------------------------------------------- animated cloud planes
def _plane_coords(view, height, cam_xz=(0.0, 0.0)):
    dy = view.dy
    sgn = np.sign(height)
    with np.errstate(divide="ignore", invalid="ignore"):
        t = height / np.where(np.abs(dy) < 1e-4, 1e-4 * sgn, dy)
    valid = (t > 0) & (np.abs(dy) > 1e-4)
    t = np.where(valid, t, 1e7)
    X = cam_xz[0] + t * view.dx
    Z = cam_xz[1] + t * view.dz
    dist = t * np.sqrt(view.dx ** 2 + view.dz ** 2)
    return X.astype(np.float32), Z.astype(np.float32), dist.astype(np.float32), valid


class CloudSea:
    """The sea of cloud below the cliff, a perspective plane that drifts with the wind."""

    def __init__(self, view, cam_h=140.0, cam_xz=(0.0, 0.0)):
        self.view = view
        X, Z, dist, valid = _plane_coords(view, -cam_h, cam_xz)
        self.X, self.Z, self.dist, self.valid = X, Z, dist, valid
        self.tex = fbm_tex(1024, 1.45, 51)
        self.tex2 = fbm_tex(512, 1.1, 52)
        az, el = view.az, view.el
        self.hc = horizon_col(az)
        self.sunpath = (np.exp(-np.abs(az - SUN_AZ) / 0.10) * 0.9 + np.exp(-np.abs(az - SUN_AZ) / 0.4) * 0.3)
        self.far = sstep(350, 6000, dist) ** 0.7

    def render(self, t):
        sc = 1024 / 3200.0
        drift = t * 5.0
        u = (self.X + drift) * sc
        v = (self.Z - t * 2.0) * sc * 1.1
        c = sample(self.tex, u, v)
        cs_ = sample(self.tex, u, v + 4.0)          # sample toward the sun (+Z)
        c2 = sample(self.tex2, u * 3 - t * 2, v * 3)
        dens = clamp01(c * 0.95 + (c2 - 0.5) * 0.10)
        shade = clamp01(0.5 + (c - cs_) * 9.0)     # billow faces turned to the sun light up
        shadow = rgb(0.58, 0.55, 0.66)
        lit = rgb(1.00, 0.85, 0.72)
        k = clamp01(0.6 * sstep(0.25, 0.8, dens) + 0.5 * (shade - 0.5) + 0.2)
        k = mix(k, 0.55, self.far * 0.7)
        col = mix(shadow, lit, k[..., None])
        col = col + SUN_COL * (self.sunpath * (0.15 + 0.6 * k))[..., None] * 0.5
        col = mix(col, mix(self.hc, MIST, 0.4), (self.far * 0.9)[..., None])
        a = np.where(self.valid, 1.0, 0.0).astype(np.float32)
        return col.astype(np.float32), a


class HighCloud:
    """Thin stratus deck lit from below by the low sun."""

    def __init__(self, view, height=2600.0):
        X, Z, dist, valid = _plane_coords(view, height)
        self.X, self.Z, self.dist, self.valid = X, Z, dist, valid
        self.tex = fbm_tex(1024, 1.5, 61, ax=1.0, ay=4.0)
        self.det = fbm_tex(512, 1.2, 62, ax=1.0, ay=3.0)
        self.view = view
        self.sp = sun_prox(view.az, view.el, k=4.0)
        self.hc = horizon_col(view.az)
        self.fade = sstep(70000, 12000, dist) * sstep(0.015, 0.07, view.el) * (1 - sstep(0.35, 0.8, view.el))

    def render(self, t):
        sc = 1024 / 9000.0
        u = (self.X + t * 9.0) * sc
        v = (self.Z) * sc
        c = sample(self.tex, u, v) * 0.9 + (sample(self.det, u * 3, v * 3) - 0.5) * 0.2
        a = sstep(0.52, 0.88, c) * self.fade * 0.8
        under = rgb(0.80, 0.56, 0.58)
        col = mix(under, self.hc * 1.05, 0.45)
        thin = (1 - sstep(0.55, 0.95, c))
        col = col + SUN_COL * (self.sp * (0.6 + 1.6 * thin))[..., None]
        return col.astype(np.float32), a.astype(np.float32)


# --------------------------------------------------------------- compositing
def over(dst, col, a):
    """dst RGB, straight colour col, alpha a."""
    return dst * (1 - a[..., None]) + col * a[..., None]


def over_pm(dst, pm, a):
    """premultiplied colour."""
    return dst * (1 - a[..., None]) + pm


def new_surface(w=None, h=None):
    w = w or W
    h = h or H
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    ctx = cairo.Context(surf)
    ctx.set_antialias(cairo.ANTIALIAS_BEST)
    return surf, ctx


def surface_to_np(surf):
    surf.flush()
    w, h, st = surf.get_width(), surf.get_height(), surf.get_stride()
    buf = np.ndarray((h, st // 4, 4), np.uint8, surf.get_data())[:, :w, :]
    pm = buf[..., [2, 1, 0]].astype(np.float32) / 255.0
    a = buf[..., 3].astype(np.float32) / 255.0
    return pm, a


def shift(img, dx, dy):
    m = np.float32([[1, 0, dx], [0, 1, dy]])
    return cv2.warpAffine(img, m, (img.shape[1], img.shape[0]), flags=cv2.INTER_LINEAR,
                          borderMode=cv2.BORDER_CONSTANT, borderValue=0)


def rim_light(alpha, light_dir, width, soft=None, wrap=0.35):
    """Edge-light from mask: strongest on edges facing light_dir (screen vector)."""
    lx, ly = light_dir
    n = math.hypot(lx, ly) or 1.0
    lx, ly = lx / n, ly / n
    r = np.zeros_like(alpha)
    for ang, wgt in ((0, 1.0), (0.6, 0.6), (-0.6, 0.6), (1.4, wrap), (-1.4, wrap)):
        c, s = math.cos(ang), math.sin(ang)
        dx, dy = (lx * c - ly * s) * width, (lx * s + ly * c) * width
        r = np.maximum(r, wgt * clamp01(alpha - shift(alpha, -dx, -dy)))
    soft = soft if soft is not None else width * 0.45
    if soft > 0.3:
        r = cv2.GaussianBlur(r, (0, 0), soft)
    return r * alpha


def blur(img, sigma):
    if sigma < 0.3:
        return img
    return cv2.GaussianBlur(img, (0, 0), sigma)


def blur_layer(pm, a, sigma):
    if sigma < 0.3:
        return pm, a
    return blur(pm, sigma), blur(a, sigma)


def light_layer(pm, a, light_dir, width, rim_col, strength=1.0, soft=None, wrap=0.35):
    r = rim_light(a, light_dir, width, soft, wrap)
    return pm + rim_col[None, None, :] * (r * strength)[..., None]


# --------------------------------------------------------------- cairo helpers
def cr_path(ctx, pts, closed=False):
    n = len(pts)
    if n < 2:
        return
    if closed:
        P = [pts[-1]] + list(pts) + [pts[0], pts[1]]
    else:
        P = [pts[0]] + list(pts) + [pts[-1]]
    ctx.move_to(*P[1])
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6.0, p1[1] + (p2[1] - p0[1]) / 6.0)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6.0, p2[1] - (p3[1] - p1[1]) / 6.0)
        ctx.curve_to(c1[0], c1[1], c2[0], c2[1], p2[0], p2[1])
    if closed:
        ctx.close_path()


def fill_shape(ctx, pts, col, closed=True, alpha=1.0, grad=None):
    cr_path(ctx, pts, closed)
    if grad is not None:
        ctx.set_source(grad)
    else:
        ctx.set_source_rgba(col[0], col[1], col[2], alpha)
    ctx.fill()


def vgrad(y0, y1, c0, c1):
    g = cairo.LinearGradient(0, y0, 0, y1)
    g.add_color_stop_rgb(0, *c0)
    g.add_color_stop_rgb(1, *c1)
    return g


def ribbon(ctx, center, w0, w1, col, alpha=1.0):
    """Tapered ribbon along a centre polyline."""
    pts = np.asarray(center, np.float64)
    n = len(pts)
    left, right = [], []
    for i in range(n):
        a = pts[max(i - 1, 0)]
        b = pts[min(i + 1, n - 1)]
        d = b - a
        L = math.hypot(*d) or 1
        nx, ny = -d[1] / L, d[0] / L
        w = mix(w0, w1, i / max(n - 1, 1)) / 2
        left.append((pts[i][0] + nx * w, pts[i][1] + ny * w))
        right.append((pts[i][0] - nx * w, pts[i][1] - ny * w))
    poly = left + right[::-1]
    fill_shape(ctx, poly, col, True, alpha)


def blade(ctx, x, y, h, w, bend, col, alpha=1.0, lean_dir=1.0):
    """A single grass blade; bend in radians."""
    tipx = x + math.sin(bend) * h
    tipy = y - math.cos(bend) * h * 0.97
    mx = x + math.sin(bend * 0.45) * h * 0.55
    my = y - math.cos(bend * 0.45) * h * 0.55
    ctx.move_to(x - w / 2, y)
    ctx.curve_to(mx - w * 0.3, my, mx, my, tipx, tipy)
    ctx.curve_to(mx + w * 0.1, my, mx + w * 0.3, my, x + w / 2, y)
    ctx.close_path()
    ctx.set_source_rgba(col[0], col[1], col[2], alpha)
    ctx.fill()


# --------------------------------------------------------------------- post
@lru_cache(None)
def _grain_pool(w, h, n=6):
    rng = np.random.RandomState(4)
    pool = []
    for _ in range(n):
        g = rng.standard_normal((h // 2 + 2, w // 2 + 2)).astype(np.float32)
        g = cv2.resize(g, (w + 4, h + 4), interpolation=cv2.INTER_LINEAR)
        pool.append(g)
    return pool


@lru_cache(None)
def _vignette(w, h):
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    nx, ny = (x - w / 2) / (w / 2), (y - h / 2) / (h / 2)
    r = np.sqrt(nx ** 2 * 0.85 + ny ** 2 * 1.1)
    return (1 - 0.38 * sstep(0.45, 1.45, r)).astype(np.float32)


@lru_cache(None)
def _paper(w, h):
    t = fbm_tex(1024, 0.75, 71)
    t2 = fbm_tex(512, 1.3, 72)
    big = cv2.resize(t, (w, h), interpolation=cv2.INTER_LINEAR)
    small = np.tile(t2, (h // 512 + 1, w // 512 + 1))[:h, :w]
    return ((big - 0.5) * 0.035 + (small - 0.5) * 0.025).astype(np.float32)


def post(img, frame, grade):
    """grade: dict(exposure, sat, lift(rgb), gain(rgb), gamma, bloom, warmth)"""
    h, w = img.shape[:2]
    img = np.maximum(img, 0)
    # bloom from highlights
    lum = img @ np.float32([0.3, 0.55, 0.15])
    hi = np.clip(lum - 0.85, 0, None)[..., None] * img / (lum[..., None] + 1e-4)
    small = cv2.resize(hi, (w // 4, h // 4), interpolation=cv2.INTER_AREA)
    b1 = cv2.GaussianBlur(small, (0, 0), 6 * S)
    b2 = cv2.GaussianBlur(small, (0, 0), 22 * S)
    bl = cv2.resize(b1 * 0.6 + b2 * 0.6, (w, h), interpolation=cv2.INTER_LINEAR)
    img = img + bl * grade.get("bloom", 0.5) * rgb(1.0, 0.85, 0.65)
    img = img * grade.get("exposure", 1.0)
    # painterly paper texture (subtle, multiplicative)
    img = img * (1 + _paper(w, h)[..., None])
    # soft shoulder tone-map
    img = np.where(img > 0.8, 0.8 + 0.2 * np.tanh((img - 0.8) / 0.2), img)
    # grade
    lum = (img @ np.float32([0.3, 0.59, 0.11]))[..., None]
    img = mix(lum, img, grade.get("sat", 1.0))
    lift = grade.get("lift", rgb(0, 0, 0))
    gain = grade.get("gain", rgb(1, 1, 1))
    img = lift + img * (gain - lift)
    img = np.clip(img, 0, 1) ** grade.get("gamma", 1.0)
    img = img * _vignette(w, h)[..., None]
    # film grain (luma-weighted, stronger in mids)
    pool = _grain_pool(w, h)
    g = pool[frame % len(pool)]
    ox, oy = (frame * 7) % 4, (frame * 3) % 4
    g = g[oy:oy + h, ox:ox + w]
    lum = img.mean(axis=2, keepdims=True)
    img = img + g[..., None] * 0.022 * (0.4 + lum * (1 - lum) * 2.4)
    return np.clip(img * 255 + 0.5, 0, 255).astype(np.uint8)
