"""Scenes 5-6: the lost city (scroll / underwater / buried), travel back in time (map)."""
import math, random
import numpy as np
from gfx import *
from scenes_a import view, boat

def outline(cv, pts, col, w=1.5):
    cv.line(list(pts) + [pts[0]], col, w)

def hatch(cv, x0, y0, x1, y1, n, col, w=1.0, slope=0.4):
    for i in range(n):
        x = x0 + (x1 - x0) * i / max(1, n - 1)
        cv.line([(x, y1), (x + (y1 - y0) * slope, y0)], col, w)

# ---------------------------------------------------------------- parchment + sketch
def make_parchment(PW, PH, seed=1):
    rnd = random.Random(seed)
    cv = Canvas(PW, PH, 2)
    pts = [(0, 0)]
    for x in range(0, PW, 14): pts.append((x, rnd.uniform(0, 7)))
    for y in range(0, PH, 14): pts.append((PW - rnd.uniform(0, 7), y))
    for x in range(PW, 0, -14): pts.append((x, PH - rnd.uniform(0, 7)))
    for y in range(PH, 0, -14): pts.append((rnd.uniform(0, 7), y))
    cv.grad_poly(pts, (236, 214, 166), (208, 176, 122), 0, PH)
    im = cv.image()
    # burnt edges + stains
    arr = np.asarray(im).astype(np.float32)
    yy, xx = np.mgrid[0:PH, 0:PW].astype(np.float32)
    d = np.minimum(np.minimum(xx, PW - xx) / PW, np.minimum(yy, PH - yy) / PH)
    burn = np.clip(1 - d / 0.07, 0, 1) ** 1.5
    arr[..., :3] *= (1 - 0.45 * burn)[..., None] * np.array([1, 0.92, 0.8])[None, None, :] + (burn[..., None] * 0)
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGBA')
    st = Canvas(PW, PH, 1)
    for i in range(16):
        st.circle(rnd.uniform(0, PW), rnd.uniform(0, PH), rnd.uniform(20, 80), (150, 110, 60, rnd.randint(14, 34)))
    st.im = st.im.filter(ImageFilter.GaussianBlur(18))
    im.alpha_composite(st.im)
    return paint_tex(im, 0.07, seed)

def make_sketch(PW, PH):
    rnd = random.Random(8)
    ink = (70, 44, 26, 235); ink2 = (70, 44, 26, 120)
    cv = Canvas(PW, PH, 2)
    # hill
    X = np.arange(0, PW, 4)
    hy = 400 - 250 * np.exp(-((X - 480) / 190.0) ** 2) - 40 * np.exp(-((X - 150) / 130.0) ** 2) - 30 * np.exp(-((X - 820) / 140.0) ** 2)
    cv.line([(float(x), float(y)) for x, y in zip(X, hy)], ink, 2.2)
    for k in range(5):
        cv.line([(float(x), float(y) + 16 + k * 18) for x, y in zip(X, hy)], ink2, 1.0)
    # temple
    tx, ty = 480, float(hy[120]) + 6
    cv.line([(tx - 90, ty), (tx + 90, ty)], ink, 2)
    cv.line([(tx - 98, ty + 5), (tx + 98, ty + 5)], ink, 2)
    for i in range(8):
        x = tx - 80 + i * 22.8
        cv.line([(x - 4, ty), (x - 4, ty - 56)], ink, 1.6); cv.line([(x + 4, ty), (x + 4, ty - 56)], ink, 1.6)
        hatch(cv, x - 4, ty - 54, x + 4, ty - 4, 4, ink2, 0.7, 0.0)
    cv.line([(tx - 96, ty - 58), (tx + 96, ty - 58)], ink, 2)
    cv.line([(tx - 96, ty - 66), (tx + 96, ty - 66)], ink, 1.6)
    outline(cv, [(tx - 98, ty - 66), (tx + 98, ty - 66), (tx, ty - 98)], ink, 2)
    hatch(cv, tx - 60, ty - 92, tx + 60, ty - 70, 16, ink2, 0.7, 0.2)
    # houses
    hs = []
    for i in range(140):
        x = rnd.uniform(40, PW - 80); y0 = float(np.interp(x, X, hy)) + 20; y = rnd.uniform(y0, 470)
        if y > 470 or (330 < x < 640 and y < 330): continue
        hs.append((y, x))
    for y, x in sorted(hs):
        w_ = rnd.uniform(22, 38); h_ = rnd.uniform(16, 26)
        cv.rect(x, y - h_, x + w_, y, (236, 214, 166, 255))
        outline(cv, [(x, y - h_), (x + w_, y - h_), (x + w_, y), (x, y)], ink, 1.4)
        cv.line([(x - 3, y - h_), (x + w_ / 2, y - h_ - 9), (x + w_ + 3, y - h_)], ink, 1.4)
        cv.rect(x + w_ * 0.2, y - h_ * 0.5, x + w_ * 0.4, y, ink)
    # sea waves + boats
    for r in range(5):
        for k in range(9):
            x = 40 + k * 100 + (r % 2) * 50 + rnd.uniform(-10, 10); y = 490 + r * 14
            cv.line([(x, y), (x + 12, y - 5), (x + 24, y), (x + 36, y - 5), (x + 48, y)], ink2, 1.2)
    for bx in (160, 700):
        cv.line([(bx, 520), (bx, 478)], ink, 1.6); cv.line([(bx + 2, 480), (bx + 22, 512), (bx + 2, 512)], ink, 1.4)
        cv.line([(bx - 22, 518), (bx + 26, 518), (bx + 16, 532), (bx - 12, 532), (bx - 22, 518)], ink, 1.6)
    # greek title + compass
    f = font('Garamond.ttf', 62, 500)
    cv.text((PW / 2, 46), 'Ε Λ Ι Κ Η', f, ink, 'mm')
    cv.line([(PW / 2 - 140, 86), (PW / 2 + 140, 86)], ink2, 1.4)
    cx, cy = PW - 90, 100
    cv.circle(cx, cy, 36, (0, 0, 0, 0)); cv.arc((cx - 36, cy - 36, cx + 36, cy + 36), 0, 360, ink, 1.4)
    for a in range(0, 360, 90):
        r = math.radians(a)
        cv.poly([(cx + math.sin(r) * 50, cy - math.cos(r) * 50), (cx + math.cos(r) * 7, cy + math.sin(r) * 7), (cx - math.cos(r) * 7, cy - math.sin(r) * 7)], ink)
    return paint_tex(cv.image(), 0.02, 3)

def make_rolls(PW, PH):
    cv = Canvas(PW + 70, 46, 2)
    cv.hgrad_rect(0, 8, PW + 70, 38, [(0, (116, 80, 44)), (0.3, (228, 198, 146)), (0.55, (190, 150, 98)), (1, (96, 64, 36))])
    cv.ellipse(0, 6, 22, 40, (150, 110, 64, 255)); cv.ellipse(PW + 48, 6, PW + 70, 40, (110, 76, 42, 255))
    cv.ellipse(4, 14, 18, 32, (216, 184, 130, 255)); cv.ellipse(PW + 52, 14, PW + 66, 32, (190, 160, 110, 255))
    cv.circle(11, 23, 4, (90, 60, 34, 255)); cv.circle(PW + 59, 23, 4, (70, 46, 28, 255))
    return cv.image()

# ---------------------------------------------------------------- underwater
def water_haze(im, col, h):
    arr = np.asarray(im).astype(np.float32)
    arr[..., :3] = arr[..., :3] * (1 - h) + np.array(col, np.float32) * h
    return Image.fromarray(arr.astype(np.uint8), 'RGBA')

class Underwater:
    def __init__(s):
        rnd = random.Random(55); s.rnd = rnd
        WL, WH = 1400, 790
        wc = (22, 92, 128)
        s.bg = vgrad_img(WL, WH, [(0, (52, 168, 196)), (0.3, (30, 122, 160)), (0.7, (14, 72, 112)), (1, (6, 34, 66))])
        # far ruins
        cv = Canvas(WL, WH, 2)
        for i in range(10):
            x = rnd.uniform(0, WL); h_ = rnd.uniform(70, 190)
            column(cv, x, 600, h_, 26, (170, 210, 214), broken=rnd.choice([0, 0, 0.3]), seed=i)
        for i in range(6):
            x = rnd.uniform(0, WL); cv.rect(x, 560, x + rnd.uniform(60, 160), 612, (150, 196, 202, 255))
        s.far = water_haze(paint_tex(cv.image(), 0.04, 2), wc, 0.72)
        # mid ruins
        cv = Canvas(WL, WH, 2)
        cv.poly([(0, 640), (300, 618), (700, 640), (1100, 612), (WL, 630), (WL, WH), (0, WH)], (122, 156, 150, 255))
        # temple platform + steps
        for i in range(4):
            cv.rect(250 - i * 14, 640 - i * 14, 1130 + i * 14, 654 - i * 14 + 14 * 0, shade((150, 196, 196), 0.8 + 0.07 * i) + (255,))
        for i in range(7):
            x = 330 + i * 120
            column(cv, x, 584, rnd.choice([130, 180, 240, 330, 150, 90, 210]), 54, (160, 206, 208), broken=rnd.choice([0.0, 0.0, 0.25]), seed=i * 3)
        # the hero column (tall)
        column(cv, 860, 600, 470, 104, (164, 210, 212), broken=0.0, seed=99)
        cv.rect(760, 584, 960, 604, (150, 196, 198, 255)); cv.rect(776, 566, 944, 586, (170, 214, 214, 255))
        # fallen drums
        for i in range(5):
            x = 430 + i * 70 + rnd.uniform(-20, 20); y = 640 + rnd.uniform(6, 40)
            cv.ellipse(x, y, x + 84, y + 36, (152, 196, 196, 255)); cv.rect(x + 14, y - 10, x + 100, y + 18, (130, 176, 178, 255))
        # algae patches
        for i in range(60):
            x = rnd.uniform(240, 1130); y = rnd.uniform(380, 620)
            cv.ellipse(x, y, x + rnd.uniform(8, 30), y + rnd.uniform(4, 12), (46, 130, 96, 110))
        s.mid = water_haze(paint_tex(cv.image(), 0.05, 3), wc, 0.28)
        # foreground
        cv = Canvas(WL, WH, 2)
        cv.poly([(0, WH), (0, 700), (200, 690), (500, 720), (800, 700), (1100, 726), (WL, 700), (WL, WH)], (176, 168, 128, 255))
        cv.poly([(0, WH), (0, 760), (300, 748), (700, 770), (1000, 750), (WL, 764), (WL, WH)], (146, 140, 104, 255))
        for i in range(10):
            x = rnd.uniform(0, WL); y = rnd.uniform(710, 780)
            cv.poly([(x, y), (x + rnd.uniform(40, 100), y - rnd.uniform(20, 50)), (x + rnd.uniform(110, 170), y + 4)], (58, 84, 86, 255))
        for i in range(40):
            x = rnd.uniform(0, WL); y = rnd.uniform(712, 784)
            cv.circle(x, y, rnd.uniform(1, 4), (214, 204, 168, 200))
        s.fg = water_haze(paint_tex(cv.image(), 0.05, 4), wc, 0.08)
        s.weeds = [(rnd.uniform(0, WL), rnd.uniform(720, 780), rnd.uniform(60, 150), rnd.uniform(0, 6), rnd.choice([(52, 130, 84), (70, 150, 96), (40, 104, 74)])) for _ in range(34)]
        s.fish = []
        for g in range(3):
            cx = rnd.uniform(0, WL); cy = rnd.uniform(200, 500)
            for i in range(8):
                s.fish.append((g, rnd.uniform(-60, 60), rnd.uniform(-30, 30), rnd.uniform(0, 6), rnd.uniform(0.8, 1.2)))
        fc = Canvas(26, 14, 4)
        fc.ellipse(2, 2, 19, 12, (240, 176, 96, 255)); fc.poly([(17, 7), (26, 1), (26, 13)], (214, 130, 70, 255)); fc.circle(6, 6, 1.3, (30, 20, 20, 255))
        s.fish_spr = fc.image()
        rr = random.Random(6)
        cc = Canvas(WL, 300, 1)
        for i in range(160):
            x = rr.uniform(0, WL); y = rr.uniform(0, 300); r_ = rr.uniform(8, 30)
            for dx in (-WL, 0, WL): cc.arc((x + dx - r_, y - r_ * 0.6, x + dx + r_, y + r_ * 0.6), rr.uniform(0, 360), rr.uniform(0, 360) + 120, (220, 255, 255, 90), 2)
        s.caus = cc.im.filter(ImageFilter.GaussianBlur(1.2))
        s.rays = [(rr.uniform(0, WL), rr.uniform(40, 150), rr.uniform(0.5, 1)) for _ in range(9)]

    def render(s, t, pan=0.0, zoom=1.0, tint=None):
        base = Image.new('RGBA', (W, H), (0, 0, 0, 255))
        cxm = 700 + pan; cy = 395
        def L(img, k, op=1.0):
            put(base, view(img, 0.92 * zoom * (1 + (zoom - 1) * k * 0.2), 700 + pan * k, cy), 0, 0, op)
        L(s.bg, 0.1)
        # god rays
        ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        for x, w_, a in s.rays:
            sw = 40 * math.sin(t * 0.4 + x)
            xx = (x - 60) * 0.9 + sw
            d.polygon([(xx, 0), (xx + w_, 0), (xx + w_ * 2.4 + 200 + sw, H), (xx - 80 + sw, H)], fill=(190, 255, 250, int(26 * a)))
        base.alpha_composite(ov.filter(ImageFilter.GaussianBlur(6)))
        L(s.far, 0.4)
        L(s.mid, 0.8)
        # caustics on seabed
        cs = ImageChops.offset(s.caus, int(t * 20) % 1400, int(6 * math.sin(t)))
        put(base, view(cs, 0.92, 700 + pan * 0.9, 80), 0, 470, 0.55)
        # fish
        for g, ox, oy, ph, sp in s.fish:
            x = ((t * (40 + g * 16) * sp + g * 600 + ox) % (W + 200)) - 100
            y = 220 + g * 110 + oy + 24 * math.sin(t * 1.4 + ph)
            put(base, s.fish_spr, x, y, 0.95)
        L(s.fg, 1.2)
        d = ImageDraw.Draw(base, 'RGBA')
        for x, y, h_, ph, col in s.weeds:
            px = (x - 700) * 0.92 * 1.1 + 640 - pan * 1.2 * 0.92; py = (y - cy) * 0.92 * 1.1 + 360
            pts = []
            for k in range(8):
                u = k / 7
                pts.append((px + math.sin(t * 1.6 + ph + u * 2.5) * 16 * u, py - u * h_))
            d.line(pts, fill=col + (255,), width=5, joint='curve')
        # bubbles
        for i in range(34):
            u = (t * 0.12 + i * 0.311) % 1.0
            bx = (i * 173) % W + 14 * math.sin(t * 2 + i); by = H + 20 - u * (H + 40)
            r = 2 + (i % 4)
            d.ellipse([bx - r, by - r, bx + r, by + r], outline=(220, 255, 255, int(150 * (1 - u))), width=1)
        base.alpha_composite(Image.new('RGBA', (W, H), (4, 40, 70, 40)))
        return base

# ---------------------------------------------------------------- buried ground
class Ground:
    def __init__(s):
        rnd = random.Random(77)
        cv = Canvas(W, H, 2)
        cv.im.paste(vgrad_img(W * 2, 600, [(0, (36, 54, 120)), (0.5, (214, 130, 112)), (1, (250, 200, 130))]), (0, 0))
        put(cv.im, blob(380, (255, 220, 150), 255, 2.0).resize((900, 900)), 1100, 200, 0.9)
        # distant sea at left & mountains
        cv.poly([(0, 270), (200, 250), (500, 262), (800, 240), (1100, 262), (W, 250), (W, 320), (0, 320)], (96, 90, 130, 255))
        cv.rect(0, 296, 420, 330, (70, 130, 170, 255))
        # surface
        X = np.arange(0, W + 8, 8)
        sy = 310 + 12 * np.sin(X / 140.0) + 6 * np.sin(X / 47.0)
        cv.grad_poly([(float(x), float(y)) for x, y in zip(X, sy)] + [(W, H), (0, H)], (112, 98, 62), (46, 32, 26), 300, H)
        cv.poly([(float(x), float(y)) for x, y in zip(X, sy)] + [(float(x), float(y) + 9) for x, y in zip(X[::-1], sy[::-1])], (92, 120, 62, 255))
        for i in range(24):
            x = rnd.uniform(430, W); y = float(np.interp(x, X, sy))
            if rnd.random() < 0.5: tree(cv, x, y + 3, rnd.uniform(26, 46), (60, 100, 56))
            else: cypress(cv, x, y + 3, rnd.uniform(36, 60), None, (30, 66, 46))
        # strata
        for i in range(7):
            y0 = 360 + i * 54
            pts = [(float(x), y0 + 14 * math.sin(x / (90 + i * 20) + i)) for x in range(0, W + 16, 16)]
            col = [(126, 96, 62), (150, 116, 74), (98, 74, 54), (166, 136, 92), (84, 62, 48), (138, 104, 70), (70, 52, 44)][i]
            cv.poly(pts + [(W, y0 + 90), (0, y0 + 90)], col + (255,))
        for i in range(520):
            x = rnd.uniform(0, W); y = rnd.uniform(340, H)
            r = rnd.uniform(1.5, 5); c = rnd.choice([(190, 160, 120), (70, 52, 44), (214, 186, 140), (100, 78, 60)])
            cv.ellipse(x - r, y - r * 0.7, x + r, y + r * 0.7, c + (190,))
        s.base = paint_tex(cv.image(), 0.06, 5)
        # buried city (stones)
        cv = Canvas(W, H, 2)
        sand = (226, 206, 160)
        y0 = 560
        cv.poly([(250, y0 + 70), (1020, y0 + 70), (1020, y0 + 90), (250, y0 + 90)], shade(sand, 0.7) + (255,))
        for i in range(5):  # steps
            cv.rect(300 + i * 10, y0 + 70 - i * 12, 980 - i * 10, y0 + 70 - i * 12 + 12, shade(sand, 0.85 + 0.04 * i) + (255,))
        for i in range(6):
            column(cv, 400 + i * 100, y0 + 4, 120 if i not in (2, 4) else 80, 28, sand, broken=0.0 if i not in (2, 4) else 0.25, seed=i)
        cv.rect(380, y0 - 130, 970, y0 - 112, shade(sand, 0.95) + (255,))
        for i in range(8):
            x = 420 + i * 70; cv.rect(x, y0 - 112, x + 10, y0 - 100, shade(sand, 0.6) + (255,))
        for i in range(5):
            bx = 120 + i * 40; cv.rect(bx, y0 + 40, bx + 36, y0 + 70, shade(sand, 0.8 + 0.05 * (i % 2)) + (255,))
        for x, y in ((1090, y0 + 60), (1150, y0 + 66), (1030, y0 + 80)):   # pottery
            cv.ellipse(x, y - 30, x + 34, y + 10, (190, 100, 60, 255)); cv.rect(x + 11, y - 42, x + 23, y - 28, (170, 90, 56, 255))
        s.city = cv.image()
        s.city_glow = s.city.filter(ImageFilter.GaussianBlur(14))
        s.spark = [(rnd.uniform(260, 1040), rnd.uniform(430, 640), rnd.uniform(0, 6)) for _ in range(46)]

    def render(s, t):
        base = s.base.copy()
        L = t - 56.4
        reveal = sstep(57.8, 60.6, t)
        # buried city faintly visible, brighter as reveal grows
        base.alpha_composite(fade(s.city, 0.18 + 0.82 * reveal))
        gl = fade(s.city_glow, (0.3 + 0.7 * reveal) * (0.7 + 0.3 * math.sin(t * 2.4)) * 0.8)
        # warm light (additive-ish)
        arr = np.asarray(gl).astype(np.float32)
        base.alpha_composite(Image.fromarray(np.dstack([np.full(arr.shape[:2], 255), np.full(arr.shape[:2], 200), np.full(arr.shape[:2], 100), arr[..., 3] * 0.55]).astype(np.uint8), 'RGBA'))
        for x, y, ph in s.spark:
            u = (t * 0.18 + ph * 0.17) % 1.0
            glow(base, x + 12 * math.sin(t + ph), y - u * 200, 4, (255, 220, 140), (1 - u) * reveal, 1.2)
        # searching spotlight (darkness with a hole)
        dk = 1 - sstep(59.4, 61.0, t)
        if dk > 0:
            px = lerp(180, 640, sstep(57.0, 59.4, t)) + 40 * math.sin(t * 1.7)
            py = lerp(420, 570, sstep(57.0, 59.4, t)) + 24 * math.sin(t * 2.3)
            dark = Image.new('RGBA', (W, H), (6, 10, 24, int(170 * dk)))
            hole = Image.new('L', (W, H), 0)
            r = 190
            b = blob(r, (255, 255, 255), 255, 0.8).getchannel('A')
            hole.paste(b, (int(px - r), int(py - r)))
            a = ImageChops.subtract(dark.getchannel('A'), hole)
            dark.putalpha(a)
            base.alpha_composite(dark)
            ring = ImageDraw.Draw(base, 'RGBA')
            ring.ellipse([px - r * 0.62, py - r * 0.62, px + r * 0.62, py + r * 0.62], outline=(255, 232, 170, int(200 * dk)), width=3)
            ring.line([(px + r * 0.44, py + r * 0.44), (px + r * 0.82, py + r * 0.82)], fill=(255, 232, 170, int(200 * dk)), width=7)
        return base

# =========================================================================== SCENE 5
class Scene5:
    start, end = 31.0, 62.3
    def __init__(s):
        rnd = random.Random(5)
        # wooden desk
        cv = Canvas(W, H, 2)
        cv.im.paste(vgrad_img(W * 2, H * 2, [(0, (62, 40, 28)), (1, (34, 22, 18))]), (0, 0))
        for i in range(70):
            y = rnd.uniform(0, H); cv.line([(0, y), (W, y + rnd.uniform(-10, 10))], (20, 12, 10, rnd.randint(40, 100)), rnd.uniform(1, 4))
        s.desk = paint_tex(cv.image(), 0.08, 4)
        s.PW, s.PH = 960, 560
        s.parch = make_parchment(s.PW, s.PH)
        s.sketch = make_sketch(s.PW, s.PH)
        s.rolls = make_rolls(s.PW, s.PH)
        s.uw = Underwater()
        s.gr = Ground()
        s.cand = font('Garamond.ttf', 20)
        s.spot = blob(500, (255, 220, 160), 255, 2.2)

    def scroll_group(s, t):
        PW, PH = s.PW, s.PH
        u = ease_out((t - 31.0) / 1.4)
        vis = max(4, int(PH * u))
        group = Image.new('RGBA', (PW + 70, PH + 100), (0, 0, 0, 0))
        top = 50 + (PH - vis) // 2
        # sketch reveal
        sk = s.sketch.copy()
        xr = lerp(-80, PW + 80, clamp((t - 32.2) / 3.8))
        xx = np.arange(PW)[None, :]
        m = np.clip((xr - xx) / 90.0, 0, 1)
        a = np.asarray(sk).copy().astype(np.float32); a[..., 3] *= m
        # water rise
        wl = lerp(PH + 30, -40, ease_out(clamp((t - 35.7) / 4.2)) if t > 35.7 else 0)
        yy = np.arange(PH)[:, None]
        surf = wl + 8 * np.sin(xx / 46.0 + t * 3.0) + 4 * np.sin(xx / 17.0 - t * 4.0)
        depth = np.clip((yy - surf) / 30.0, 0, 1)
        a[..., 3] *= (1 - 0.9 * depth)
        pr = np.asarray(s.parch).astype(np.float32).copy()
        sk_im = Image.fromarray(a.astype(np.uint8), 'RGBA')
        comp = s.parch.copy(); comp.alpha_composite(sk_im)
        c = np.asarray(comp).astype(np.float32)
        wcol = np.array([40, 120, 170], np.float32)
        k = (depth * 0.62)[..., None]
        c[..., :3] = c[..., :3] * (1 - k) + (c[..., :3] * wcol / 255.0 * 1.1) * k
        edge = np.clip(1 - np.abs(yy - surf) / 3.0, 0, 1)[..., None] * (wl < PH + 10)
        c[..., :3] = c[..., :3] * (1 - edge * 0.5) + np.array([210, 240, 255]) * edge * 0.5
        comp = Image.fromarray(np.clip(c, 0, 255).astype(np.uint8), 'RGBA')
        comp = comp.crop((0, (PH - vis) // 2, PW, (PH - vis) // 2 + vis))
        group.alpha_composite(comp, (35, top))
        group.alpha_composite(s.rolls, (0, top - 22))
        group.alpha_composite(s.rolls, (0, top + vis - 18))
        return group, xr, wl

    def render(s, t):
        L = t - 31.0
        base = s.desk.copy()
        # warm candle light
        put(base, s.spot, 640 - 500, 340 - 500, 0.55)
        group, xr, wl = s.scroll_group(t)
        # layout: centered then shifts left when split view starts
        sh = sstep(40.2, 41.4, t)
        sc = lerp(1.0, 0.64, sh) * (1 + 0.025 * (t - 31) / 9 if t < 40.4 else 1)
        sz = (int(group.width * sc), int(group.height * sc))
        g = group.resize(sz, Image.LANCZOS)
        cx = lerp(640, 330, sh); cy = lerp(366, 360, sh)
        # shadow
        shd = shadow_ell(int(sz[0] * 0.9), 50, 120)
        put(base, shd, cx - shd.width / 2, cy + sz[1] / 2 - 26)
        put(base, g, cx - sz[0] / 2, cy - sz[1] / 2 + 6 * math.sin(t * 0.8) * (1 - sh))
        # pen glint at reveal front
        if 32.2 < t < 36.1 and wl > 500:
            px = (xr_ := (lerp(-80, s.PW + 80, clamp((t - 32.2) / 3.8)))) + 35
            glow(base, cx - sz[0] / 2 + px * sc, cy - sz[1] / 2 + (300 + 40 * math.sin(t * 6)) * sc, 28, (255, 214, 120), 0.8, 1.6)
        # underwater panel
        b0 = sstep(40.4, 41.5, t); b1 = sstep(48.9, 50.2, t)
        up = sstep(56.2, 57.6, t)
        if t > 40.3 and up < 1:
            xb = lerp(W + 140, 600, ease_out(b0)) if t < 48.9 else lerp(600, -220, b1)
            slant = 90
            uw = s.uw.render(t, pan=30 * math.sin(t * 0.25) + 14 * (t - 40), zoom=1.0 + 0.1 * clamp((t - 48) / 8))
            # sonar
            if 49.0 < t < 57.6:
                d = ImageDraw.Draw(uw, 'RGBA')
                sa = sstep(49.0, 49.8, t) * (1 - sstep(55.8, 57.0, t))
                px = lerp(640, 760, sstep(52, 56, t)); py = lerp(560, 600, sstep(52, 56, t))
                for k in range(4):
                    u = ((t - 49) * 0.45 + k / 4.0) % 1.0
                    r = 40 + u * 760
                    d.ellipse([px - r, py - r * 0.42, px + r, py + r * 0.42], outline=(150, 255, 230, int(210 * (1 - u) * sa)), width=3)
                ang = (t - 49) * 2.4
                d.line([(px, py), (px + math.cos(ang) * 600, py + math.sin(ang) * 250)], fill=(150, 255, 230, int(120 * sa)), width=3)
                glow(uw, px, py, 38, (160, 255, 230), sa, 1.5)
            # 'where everyone was looking' dims the sea slightly after 55
            m = Image.new('L', (W * 2, H * 2), 0)
            ImageDraw.Draw(m).polygon([((xb + slant) * 2, 0), (W * 2 + 400, 0), (W * 2 + 400, H * 2), (xb * 2, H * 2)], fill=255)
            m = m.resize((W, H), Image.LANCZOS)
            tmp = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            put(tmp, uw, 0, -up * H)
            tmp.putalpha(ImageChops.multiply(tmp.getchannel('A'), m))
            if up > 0:
                base.alpha_composite(s.gr.render(t))
            base.alpha_composite(tmp)
            dv = ImageDraw.Draw(base, 'RGBA')
            if xb > -100:
                dv.line([(xb + slant, 0), (xb, H)], fill=(255, 244, 220, 255), width=5)
        elif up >= 1:
            base = s.gr.render(t)
        return base

# =========================================================================== SCENE 6
GREECE = [(17.0, 45), (19.0, 42.0), (19.4, 41.4), (19.5, 40.6), (19.9, 40.1), (20.0, 39.7), (20.2, 39.3), (20.75, 38.95), (21.0, 38.65), (21.3, 38.45),
          (21.45, 38.33), (21.75, 38.36), (22.1, 38.4), (22.4, 38.38), (22.7, 38.33), (23.0, 38.2), (23.25, 38.05), (23.5, 38.0), (23.9, 37.9), (24.04, 37.65),
          (23.98, 37.95), (24.1, 38.2), (24.35, 38.1), (24.0, 38.4), (23.6, 38.7), (23.3, 39.0), (22.95, 39.25), (23.0, 39.4), (22.85, 39.8), (22.6, 40.05),
          (22.6, 40.55), (22.95, 40.6), (23.35, 40.25), (23.6, 40.0), (23.9, 40.2), (23.75, 40.4), (24.0, 40.25), (24.35, 40.1), (24.4, 40.35), (24.0, 40.55),
          (24.6, 40.85), (25.6, 40.85), (26.1, 40.8), (26.25, 40.4), (26.2, 40.0), (26.65, 39.5), (26.8, 39.1), (26.9, 38.6), (27.1, 38.4), (26.85, 38.2), (27.25, 37.8),
          (27.45, 37.3), (27.2, 37.05), (27.6, 36.95), (28.2, 36.7), (28.9, 36.65), (29.4, 36.3), (30.2, 36.3), (31, 36.3), (31, 45)]
PELOP = [(22.9, 37.95), (22.4, 38.15), (22.0, 38.2), (21.75, 38.3), (21.4, 38.2), (21.1, 37.9), (21.1, 37.65), (21.3, 37.45), (21.65, 37.2), (21.7, 36.85),
         (21.95, 36.75), (22.3, 36.6), (22.4, 36.4), (22.55, 36.7), (22.75, 36.55), (23.2, 36.45), (23.0, 36.85), (22.75, 37.05), (22.75, 37.5), (23.2, 37.4), (23.1, 37.7), (23.15, 37.95)]
ISL = [[(19.8, 39.8), (19.95, 39.7), (19.9, 39.5), (19.7, 39.6)], [(20.55, 38.8), (20.7, 38.75), (20.65, 38.55), (20.5, 38.65)], [(20.35, 38.35), (20.8, 38.2), (20.7, 38.05), (20.45, 38.1)],
       [(20.85, 37.8), (21.05, 37.75), (20.95, 37.65), (20.8, 37.7)], [(23.3, 38.0), (24.2, 38.5), (24.5, 38.3), (23.5, 37.85)],
       [(25.2, 37.1), (25.5, 37.15), (25.4, 36.95), (25.15, 37.0)], [(24.9, 37.5), (25.1, 37.5), (25.0, 37.3)], [(24.4, 37.4), (24.5, 37.2), (24.3, 37.2)], [(25.0, 36.5), (25.5, 36.5), (25.3, 36.3), (25.0, 36.35)],
       [(23.5, 35.3), (24.1, 35.5), (25.0, 35.4), (25.8, 35.35), (26.3, 35.25), (26.0, 35.0), (25.0, 35.0), (24.0, 35.2), (23.55, 35.15)],
       [(26.1, 39.35), (26.5, 39.35), (26.4, 39.05), (26.1, 39.1)], [(24.9, 39.95), (25.2, 39.95), (25.1, 39.8)], [(25.95, 38.55), (26.15, 38.5), (26.05, 38.25)], [(26.6, 37.8), (26.9, 37.8), (26.8, 37.65)],
       [(27.7, 36.35), (28.2, 36.3), (28.1, 36.1), (27.8, 36.05)], [(25.9, 39.9), (26.3, 40.1), (26.1, 40.0)]]
ITALY = [(15.5, 41.5), (16.5, 41.0), (17.0, 40.6), (17.8, 40.4), (18.4, 40.15), (18.5, 39.85), (18.2, 39.9), (17.4, 40.3), (16.6, 40.0), (16.2, 39.0), (15.8, 38.5), (15.5, 38.5)]

def proj(lon, lat): return ((lon - 15.5) * 128.0, (42.4 - lat) * 150.0)

def year_str(t):
    if t < 66.4: v = lerp(2025, 1100, ease_out((t - 62.3) / 4.1)) if t > 62.3 else 2025
    else:
        v = lerp(1100, -373, sstep(66.6, 67.55, t)) if t < 67.55 else -373
    v = int(round(v))
    return (str(v) + ' AD' if v > 0 else str(-v) + ' BC') if abs(v) != 373 or v > 0 else '373 BC'

class Scene6:
    start, end = 62.3, 70.0
    MW, MH = 1800, 1160
    def __init__(s):
        rnd = random.Random(66)
        MW, MH = s.MW, s.MH
        # sea
        sea = vgrad_img(MW, MH, [(0, (34, 108, 140)), (0.5, (28, 92, 128)), (1, (20, 66, 104))])
        cv = Canvas(MW, MH, 1); cv.im = sea
        # land mask at 2x
        m = Image.new('L', (MW * 2, MH * 2), 0); dm = ImageDraw.Draw(m)
        def P(poly): return [(proj(*p)[0] * 2, proj(*p)[1] * 2) for p in poly]
        for poly in [GREECE, PELOP, ITALY] + ISL: dm.polygon(P(poly), fill=255)
        dm.polygon(P([(22.85, 38.1), (23.25, 38.1), (23.25, 37.9), (22.85, 37.9)]), fill=255)
        m = m.resize((MW, MH), Image.LANCZOS)
        # shallow water halo
        halo = m.filter(ImageFilter.GaussianBlur(26)).point(lambda v: min(255, v * 2))
        ha = Image.new('RGBA', (MW, MH), (120, 214, 214, 0)); ha.putalpha(halo.point(lambda v: v * 150 // 255))
        sea.alpha_composite(ha)
        # land color + texture
        land = vgrad_img(MW, MH, [(0, (214, 190, 126)), (0.5, (196, 160, 98)), (1, (176, 134, 82))])
        ln = np.asarray(land).astype(np.float32)
        rng = np.random.default_rng(3)
        n = np.asarray(Image.fromarray(rng.standard_normal((30, 45)).astype(np.float32), 'F').resize((MW, MH), Image.BICUBIC))
        ln[..., :3] *= (1 + 0.1 * n)[..., None]
        # inner shade
        inner = m.filter(ImageFilter.GaussianBlur(10))
        ia = np.asarray(inner).astype(np.float32) / 255.0
        ln[..., :3] *= (0.78 + 0.22 * ia)[..., None]
        land = Image.fromarray(np.clip(ln, 0, 255).astype(np.uint8), 'RGBA'); land.putalpha(m)
        sh = Image.new('RGBA', (MW, MH), (10, 30, 44, 0)); sh.putalpha(m.filter(ImageFilter.GaussianBlur(6)).point(lambda v: v * 120 // 255))
        sea.alpha_composite(sh, (6, 8))
        sea.alpha_composite(land)
        # coast ink line
        edge = ImageChops.subtract(m.filter(ImageFilter.MaxFilter(5)), m)
        el = Image.new('RGBA', (MW, MH), (70, 44, 26, 0)); el.putalpha(edge.point(lambda v: min(255, v * 2)))
        sea.alpha_composite(el)
        # mountain glyphs
        cv = Canvas(MW, MH, 2)
        mpx = np.asarray(m)
        for i in range(420):
            lon = rnd.uniform(18.5, 29); lat = rnd.uniform(35.2, 42)
            x, y = proj(lon, lat)
            if x < 0 or y < 0 or x >= MW or y >= MH or mpx[int(y), int(x)] < 250: continue
            if mpx[int(max(0, y - 22)), int(x)] < 250: continue
            sz = rnd.uniform(9, 17)
            cv.poly([(x - sz, y + sz * 0.5), (x, y - sz), (x + sz, y + sz * 0.5)], (150, 110, 70, 255))
            cv.poly([(x, y - sz), (x + sz, y + sz * 0.5), (x + sz * 0.1, y + sz * 0.5)], (110, 76, 50, 255))
        sea.alpha_composite(cv.image())
        # sea decoration: compass + ship + wave strokes
        cv = Canvas(MW, MH, 2)
        for i in range(160):
            x = rnd.uniform(0, MW); y = rnd.uniform(0, MH)
            if mpx[int(y), int(x)] > 10: continue
            cv.line([(x, y), (x + 9, y - 4), (x + 18, y), (x + 27, y - 4), (x + 36, y)], (210, 240, 240, 90), 1.6)
        sea.alpha_composite(cv.image())
        s.map = paint_tex(sea, 0.04, 6)
        px, py = proj(22.08, 38.25)
        s.pin_pos = (px, py)
        s.ship = boat(40, (240, 226, 196), (96, 64, 44))
        # compass rose
        cv = Canvas(300, 300, 3)
        cx = cy = 150
        cv.circle(cx, cy, 120, (240, 226, 190, 40)); cv.arc((cx - 120, cy - 120, cx + 120, cy + 120), 0, 360, (240, 226, 190, 220), 2)
        cv.arc((cx - 100, cy - 100, cx + 100, cy + 100), 0, 360, (240, 226, 190, 150), 1)
        for a in range(0, 360, 45):
            r = math.radians(a); L_ = 120 if a % 90 == 0 else 74
            cv.poly([(cx + math.sin(r) * L_, cy - math.cos(r) * L_), (cx + math.cos(r) * 11, cy + math.sin(r) * 11), (cx, cy), (cx - math.cos(r) * 11, cy - math.sin(r) * 11)], (244, 228, 188, 235) if a % 90 == 0 else (200, 180, 140, 200))
        cv.text((cx, cy - 138), 'N', font('Cinzel.ttf', 26, 700), (244, 228, 188, 255), 'mm')
        s.compass = cv.image()
        # clock rings for vortex
        cv = Canvas(900, 900, 2)
        c0 = 450
        for r, wd, a in ((430, 3, 230), (380, 1.5, 180), (300, 2, 160), (210, 1.5, 150)):
            cv.arc((c0 - r, c0 - r, c0 + r, c0 + r), 0, 360, (250, 220, 150, a), wd)
        for i in range(60):
            r = math.radians(i * 6); l = 28 if i % 5 == 0 else 12
            cv.line([(c0 + math.sin(r) * 430, c0 - math.cos(r) * 430), (c0 + math.sin(r) * (430 - l), c0 - math.cos(r) * (430 - l))], (250, 220, 150, 220), 2.4 if i % 5 == 0 else 1.2)
        rom = ['XII', 'I', 'II', 'III', 'IIII', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI']
        f = font('Cinzel.ttf', 34, 600)
        for i, rn in enumerate(rom):
            r = math.radians(i * 30)
            cv.text((c0 + math.sin(r) * 345, c0 - math.cos(r) * 345), rn, f, (250, 220, 150, 235), 'mm')
        s.clock = cv.image()
        cv = Canvas(900, 900, 2)
        cv.poly([(c0 - 8, c0 + 40), (c0, c0 - 300), (c0 + 8, c0 + 40)], (255, 232, 170, 255)); cv.circle(c0, c0, 14, (255, 232, 170, 255))
        s.hand_l = cv.image()
        cv = Canvas(900, 900, 2)
        cv.poly([(c0 - 6, c0 + 30), (c0, c0 - 200), (c0 + 6, c0 + 30)], (255, 200, 120, 255))
        s.hand_s = cv.image()
        s.stars = [(rnd.uniform(0, math.tau), rnd.uniform(60, 900), rnd.uniform(0.5, 1.5)) for _ in range(160)]
        s.sign = None
        cv = Canvas(560, 220, 2)
        pts = [(10, 14)] + [(10 + i * 22, 14 + rnd.uniform(-5, 5)) for i in range(1, 25)] + [(550, 18)] + [(550 - rnd.uniform(0, 8), 14 + i * 20) for i in range(1, 10)] + [(548, 206)] + [(548 - i * 22, 206 + rnd.uniform(-5, 4)) for i in range(1, 25)] + [(8, 202)]
        cv.grad_poly(pts, (240, 218, 168), (212, 178, 120), 0, 220)
        s.sign = paint_tex(cv.image(), 0.09, 7)
        s.mapfont = font('Cinzel.ttf', 92, 700)

    def render(s, t):
        L = t - 62.3
        base = Image.new('RGBA', (W, H), (6, 8, 22, 255))
        vort = 1 - sstep(64.1, 65.4, t)
        mapa = sstep(63.8, 65.2, t)
        # --- map
        if mapa > 0:
            z = lerp(0.72, 1.18, ease_out(clamp((t - 64.0) / 5.5)))
            px, py = s.pin_pos
            fx = lerp(s.MW / 2, px + 130, ease_out(clamp((t - 64.0) / 5.5)))
            fy = lerp(s.MH / 2, py + 10, ease_out(clamp((t - 64.0) / 5.5)))
            mp = view(s.map, z, fx, fy)
            put(base, mp, 0, 0, mapa)
            # ship
            ship_x = (lerp(300, 1700, (t - 62.3) / 7.7), lerp(900, 800, (t - 62.3) / 7.7))
            def tr(x, y): return ((x - clamp(fx, W / 2 / z, s.MW - W / 2 / z)) * z + W / 2, (y - clamp(fy, H / 2 / z, s.MH - H / 2 / z)) * z + H / 2)
            sx, sy = tr(*ship_x)
            sp = s.ship.resize((int(s.ship.width * z * 1.5), int(s.ship.height * z * 1.5)), Image.BILINEAR)
            put(base, sp.rotate(3 * math.sin(t * 1.5), resample=Image.BICUBIC), sx, sy + 4 * math.sin(t * 1.9), mapa)
            # compass
            cp = s.compass.rotate(6 * math.sin(t * 0.6), resample=Image.BICUBIC)
            put(base, cp, 70, 410, 0.85 * mapa)
            # pin drop
            qx, qy = tr(px, py)
            pa = ease_out((t - 65.3) / 0.5)
            if t > 65.25:
                dy = (1 - ease_back((t - 65.3) / 0.7)) * -220
                for k in range(3):
                    u = ((t - 65.8) * 0.9 + k / 3) % 1.0
                    r = 14 + u * 90
                    if t > 65.8: ImageDraw.Draw(base, 'RGBA').ellipse([qx - r, qy - r * 0.45, qx + r, qy + r * 0.45], outline=(255, 90, 70, int(220 * (1 - u))), width=3)
                d = ImageDraw.Draw(base, 'RGBA')
                d.ellipse([qx - 10, qy - 4, qx + 10, qy + 4], fill=(0, 0, 0, 100))
                py_ = qy + min(0, dy)
                d.polygon([(qx - 15, py_ - 40), (qx + 15, py_ - 40), (qx, py_)], fill=(214, 40, 38, 255))
                d.ellipse([qx - 18, py_ - 62, qx + 18, py_ - 26], fill=(226, 54, 46, 255))
                d.ellipse([qx - 7, py_ - 50, qx + 7, py_ - 36], fill=(250, 226, 220, 255))
                d.ellipse([qx - 12, py_ - 58, qx - 3, py_ - 49], fill=(255, 150, 140, 200))
            # labels
            for txt, lon, lat, size, a0, ang in (('GREECE', 21.7, 39.7, 62, 65.6, 0), ('Gulf of Corinth', 22.6, 38.55, 22, 67.0, 0), ('PELOPONNESE', 21.5, 37.2, 24, 66.4, -12)):
                la = sstep(a0, a0 + 0.8, t)
                if la > 0:
                    lx, ly = tr(*proj(lon, lat))
                    f = font('Cinzel.ttf', size if size > 30 else size, 600)
                    ti = Image.new('RGBA', (600, 140), (0, 0, 0, 0)); dd = ImageDraw.Draw(ti)
                    tw = dd.textlength(txt, font=f)
                    dd.text((300 - tw / 2 + 2, 70 + 2), txt, font=f, fill=(20, 12, 8, 150), anchor='lm')
                    dd.text((300 - tw / 2, 70), txt, font=f, fill=(255, 238, 200, 255), anchor='lm')
                    if ang: ti = ti.rotate(ang, resample=Image.BICUBIC)
                    put(base, ti, lx - 300, ly - 70, la * 0.95)
        # --- time vortex
        if vort > 0:
            ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            bg = Image.new('RGBA', (W, H), (8, 10, 34, int(255 * vort)))
            ov.alpha_composite(bg)
            spin = -L * (1.2 + 5 * (L / 4) ** 2)
            for ang, r, sp in s.stars:
                a = ang + spin * 0.35 * sp
                rr = ((r - L * 140 * sp) % 900)
                x = 640 + math.cos(a) * rr * 1.2; y = 360 + math.sin(a) * rr * 0.7
                tail = 0.05 + 0.02 * L
                x2 = 640 + math.cos(a - tail) * rr * 1.2; y2 = 360 + math.sin(a - tail) * rr * 0.7
                ImageDraw.Draw(ov, 'RGBA').line([(x, y), (x2, y2)], fill=(255, 224, 160, int(220 * vort * clamp(rr / 500))), width=2)
            cl = s.clock.rotate(math.degrees(spin * 0.15), resample=Image.BICUBIC)
            put(ov, cl, 640 - 450, 360 - 450, 0.9 * vort)
            put(ov, s.hand_l.rotate(math.degrees(spin * 3.3), resample=Image.BICUBIC), 640 - 450, 360 - 450, vort)
            put(ov, s.hand_s.rotate(math.degrees(spin * 0.55), resample=Image.BICUBIC), 640 - 450, 360 - 450, vort)
            add_light(ov, 640, 360, 420, (255, 190, 110), 0.5 * vort)
            f = font('Cinzel.ttf', 74, 700)
            d = ImageDraw.Draw(ov, 'RGBA'); ys = year_str(t)
            d.text((640 + 3, 360 + 3), ys, font=f, fill=(0, 0, 0, int(200 * vort)), anchor='mm')
            d.text((640, 360), ys, font=f, fill=(255, 240, 200, int(255 * vort)), anchor='mm')
            base.alpha_composite(ov)
        # --- sign
        sa = sstep(66.3, 67.0, t)
        if sa > 0:
            u = ease_back((t - 66.3) / 0.8)
            sw = s.sign.copy()
            d = ImageDraw.Draw(sw)
            ys = year_str(t) if t < 67.6 else '373 BC'
            if t > 67.5: ys = '373 BC'
            d.text((280 + 3, 112 + 3), ys, font=s.mapfont, fill=(60, 30, 14, 90), anchor='mm')
            d.text((280, 112), ys, font=s.mapfont, fill=(98, 46, 22, 255), anchor='mm')
            d.line([(70, 176), (490, 176)], fill=(120, 74, 40, 200), width=2)
            rot = 4 - 4 * u + 2 * math.sin(t * 1.5)
            sw = sw.rotate(rot, resample=Image.BICUBIC, expand=True)
            put(base, sw, 690 + (1 - u) * 500 - 20, 380 + math.sin(t * 1.2) * 4, sa)
            if 67.5 < t < 68.4:
                add_light(base, 970, 490, 340, (255, 230, 160), 0.45 * (1 - (t - 67.5) / 0.9))
        # vignette (warm sepia edges on map)
        return base
