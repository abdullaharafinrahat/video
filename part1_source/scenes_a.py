"""Scenes 1-4: empty world, not abandoned, the question, the reveal."""
import math, random
import numpy as np
from gfx import *

def view(layer, zoom, cx, cy, out=(W, H), rot=0.0):
    lw, lh = layer.size
    hw, hh = out[0] / 2 / zoom, out[1] / 2 / zoom
    cx = clamp(cx, hw, lw - hw) if lw > 2 * hw else lw / 2
    cy = clamp(cy, hh, lh - hh) if lh > 2 * hh else lh / 2
    return cam(layer, zoom, cx, cy, out, rot)

def boat(h=34, sail=(244,238,222), hull=(110,70,50)):
    cv = Canvas(int(h * 2.2), int(h * 1.6), 3)
    w = h * 2.2
    cv.line([(w * 0.5, h * 1.2), (w * 0.5, h * 0.1)], (70, 50, 40, 255), 1.6)
    cv.poly([(w * 0.5 + 2, h * 0.15), (w * 0.5 + 2, h * 1.05), (w * 0.88, h * 1.05)], sail + (255,))
    cv.poly([(w * 0.5 - 2, h * 0.3), (w * 0.5 - 2, h * 1.05), (w * 0.2, h * 1.05)], shade(sail, 0.85) + (255,))
    cv.poly([(w * 0.1, h * 1.18), (w * 0.9, h * 1.18), (w * 0.8, h * 1.45), (w * 0.2, h * 1.45)], hull + (255,))
    cv.rect(w * 0.1, h * 1.14, w * 0.9, h * 1.2, shade(hull, 1.4) + (255,))
    return cv.image()

class Coast:
    """Greek coastal city. v=1: acropolis hill (daylight). v=4: golden hour with great mountain."""
    def __init__(s, v):
        s.v = v
        rnd = random.Random(30 + v)
        X = np.arange(LW, dtype=np.float32)
        if v == 1:
            hy = 610 - 310 * np.exp(-((X - 760) / 300) ** 2) - 55 * np.exp(-((X - 1250) / 260) ** 2) - 45 * np.exp(-((X - 220) / 230) ** 2)
            shore = 660 - 18 * X / LW
            stops = [(0, (52, 104, 196)), (0.42, (126, 176, 230)), (0.6, (222, 234, 238)), (1, (240, 226, 200))]
            sun = (1200, 150, (255, 246, 215)); hor = 520
        else:
            hy = np.interp(X, [0, 380, 700, 1100, 1536], [900, 780, 625, 575, 555])
            shore = hy + 100
            stops = [(0, (40, 80, 160)), (0.38, (110, 150, 205)), (0.58, (250, 214, 160)), (1, (250, 190, 120))]
            sun = (420, 400, (255, 220, 160)); hor = 515
        s.hy, s.shore = hy, shore
        sky = vgrad_img(LW, LH, stops)
        put(sky, blob(420, sun[2], 255, 2.4), sun[0] - 420, sun[1] - 420, 0.9)
        put(sky, blob(60, (255, 255, 240), 255, 1.2), sun[0] - 60, sun[1] - 60, 0.95)
        s.sky = sky
        cc = (255, 255, 255) if v == 1 else (255, 238, 214)
        sc = (186, 202, 232) if v == 1 else (232, 168, 140)
        s.cl1 = clouds(LW, 430, 5 + v, 9, cc, sc, 225, 1.1)
        s.cl2 = clouds(LW, 300, 9 + v, 3, cc, sc, 150, 1.0)
        # mountains
        cv = Canvas(LW, LH, 2)
        if v == 1:
            far = ridge(LW, 430, 60, 3) - 70 * np.exp(-((X - 1380) / 200) ** 2) - 50 * np.exp(-((X - 180) / 240) ** 2)
            fill_ridge(cv, far, (146, 164, 204), (196, 208, 226), hor + 20, rim=(236, 238, 245))
            mid = ridge(LW, 480, 36, 7) - 60 * np.exp(-((X - 1100) / 260) ** 2)
            fill_ridge(cv, mid, (104, 126, 170), (160, 176, 200), hor + 30, rim=(214, 224, 238))
        else:
            far = ridge(LW, 470, 30, 3) - 40 * np.exp(-((X - 200) / 250) ** 2)
            fill_ridge(cv, far, (150, 140, 170), (230, 190, 160), hor + 20, rim=(255, 220, 180))
            big = ridge(LW, 470, 34, 11, rough=0.6) - 330 * np.exp(-((X - 930) / 330) ** 2) * (1 - 0.18 * np.sin(X / 37.0))
            fill_ridge(cv, big, (92, 98, 150), (186, 132, 138), hor + 40, rim=(255, 214, 160))
        s.mount = paint_tex(cv.image(), 0.035, 1)
        # sea
        cv = Canvas(LW, LH, 1)
        sea_top, sea_bot = ((150, 204, 224), (24, 84, 150)) if v == 1 else ((250, 206, 150), (36, 70, 130))
        sea = vgrad_img(LW, LH - hor, [(0, sea_top), (0.35, mix(sea_top, sea_bot, 0.55)), (1, sea_bot)])
        cv.im.paste(sea, (0, hor))
        s.sea = cv.im
        # wave texture
        s.waves = []
        for layer in range(2):
            wc = Canvas(LW, LH, 1)
            for _ in range(900 if layer == 0 else 420):
                x = rnd.uniform(0, LW); y = rnd.uniform(hor + 10, LH)
                k = (y - hor) / (LH - hor)
                wd = (6 + 70 * k * rnd.uniform(0.4, 1.2)) * (1.0 + layer * 0.5); ht = 1 + 3.2 * k
                col = (255, 255, 255) if v == 1 else (255, 230, 190)
                for dx in (-LW, 0, LW):
                    wc.ellipse(x + dx - wd / 2, y, x + dx + wd / 2, y + ht, col + (int(40 + 70 * k * rnd.random()),))
            s.waves.append(wc.im)
        # land
        cv = Canvas(LW, LH, 2)
        pts = [(x, float(hy[x])) for x in range(0, LW, 6)] + [(LW, float(hy[-1]))] + [(x, float(shore[x])) for x in range(LW - 1, -1, -6)]
        top, bot = ((166, 150, 104), (128, 124, 82)) if v == 1 else ((150, 118, 90), (110, 96, 70))
        cv.grad_poly(pts, top, bot, 330 if v == 1 else 500, 700)
        for i in range(70):  # olive groves / scrub
            x = rnd.uniform(0, LW); yy = float(np.interp(x, X, hy)) + rnd.uniform(0, 1) * float(np.interp(x, X, shore - hy))
            if v == 1 and 560 < x < 980 and yy < 480: continue
            tree(cv, x, yy, rnd.uniform(14, 26), (84, 112, 66))
        s.land = paint_tex(cv.image(), 0.07, 2)
        # city
        cv = Canvas(LW, LH, 2)
        walls = [(244, 238, 224), (236, 224, 200), (226, 206, 170), (240, 230, 210), (214, 190, 150), (250, 246, 236)]
        roofs = [(196, 112, 80), (176, 96, 70), (208, 130, 90)]
        hs = []
        n = 330 if v == 1 else 240
        for i in range(n):
            x = rnd.uniform(40, LW - 60) if v == 1 else rnd.uniform(380, LW - 40)
            t = rnd.random() ** 0.85
            y0 = float(np.interp(x, X, hy)) + 10; y1 = float(np.interp(x, X, shore)) - 6
            if y1 - y0 < 16: continue
            y = y0 + t * (y1 - y0)
            sc_ = lerp(0.8, 1.7, clamp((y - 300) / 380)) * (1 if v == 1 else 0.9)
            hs.append((y, x, sc_))
        if v == 1:   # walls + temples on acropolis
            xs = list(range(540, 1010, 8))
            wp = [(x, float(hy[x]) + 6) for x in xs] + [(x, float(hy[x]) + 30) for x in reversed(xs)]
            cv.grad_poly(wp, (216, 200, 168), (170, 152, 124))
            for x in xs[::5]:
                cv.rect(x, hy[x] + 3, x + 5, hy[x] + 8, (226, 210, 178, 255))
            yt = float(hy[770]) + 8
            temple_front(cv, 770, yt, 8, 70, 9, 28, steps=3)
            temple_front(cv, 620, float(hy[620]) + 8, 5, 40, 6, 20, steps=2, seed=4)
            temple_front(cv, 925, float(hy[925]) + 8, 4, 32, 5, 18, steps=2, seed=8)
        for y, x, sc_ in sorted(hs):
            w_ = rnd.uniform(26, 46) * sc_; h_ = rnd.uniform(20, 34) * sc_
            house(cv, x, y, w_, h_, rnd.choice(walls), rnd.choice(roofs), rnd.randint(0, 999), rnd.random() < 0.55)
            if rnd.random() < 0.08: cypress(cv, x + w_ + 6, y + 2, rnd.uniform(24, 40) * sc_)
        # quay + piers
        for x0, x1 in ((60, LW - 50),):
            qp = [(x, float(shore[x]) - 12) for x in range(int(x0), int(x1), 8)] + [(x, float(shore[x]) + 8) for x in range(int(x1) - 1, int(x0), -8)]
            if v == 1: cv.grad_poly(qp, (200, 186, 156), (120, 108, 92))
        s.city = cv.image()
        s.city_px = np.asarray(s.city).copy()
        # dissolve map
        rng = np.random.default_rng(4)
        nz = np.asarray(Image.fromarray(rng.standard_normal((18, 32)).astype(np.float32), 'F').resize((LW, LH), Image.BICUBIC))
        nz2 = rng.standard_normal((LH // 3, LW // 3)).astype(np.float32)
        nz2 = np.asarray(Image.fromarray(nz2, 'F').resize((LW, LH), Image.BILINEAR))
        s.dis = np.clip(0.45 * (np.arange(LW)[None, :] / LW) + 0.28 * (nz * 0.5 + 0.5) + 0.12 * (nz2 * 0.3 + 0.5), 0, 1)
        # boats
        s.boats = [(boat(rnd.uniform(26, 44)), rnd.uniform(120, 1400), rnd.uniform(700, 820), rnd.uniform(0, 6)) for _ in range(7)]
        # foreground rocks
        cv = Canvas(LW, LH, 2)
        if v == 1:
            cv.poly([(0, LH), (0, 780), (60, 765), (150, 790), (260, 830), (330, LH)], (60, 66, 70, 255))
            cv.poly([(0, LH), (0, 800), (90, 800), (200, 840), (260, LH)], (84, 90, 92, 255))
            cv.poly([(LW, LH), (LW, 790), (1440, 770), (1380, 810), (1300, LH)], (60, 66, 70, 255))
            tree(cv, 40, 790, 90, (60, 92, 58)); cypress(cv, 1480, 800, 150, 16)
        else:
            cv.poly([(0, LH), (0, 640), (80, 630), (180, 660), (300, 720), (460, 790), (640, LH)], (34, 50, 44, 255))
            cv.poly([(0, LH), (0, 700), (150, 700), (320, 770), (470, LH)], (24, 38, 36, 255))
            for tx, ty, th in [(50, 650, 160), (170, 680, 120), (300, 730, 90), (20, 720, 200)]:
                tree(cv, tx, ty, th, (36, 66, 44))
            cypress(cv, 120, 680, 220, 24, (22, 46, 36))
        s.fg = paint_tex(cv.image(), 0.05, 3)
        s.rnd = rnd
        # city particles (dissolve sparks)
        s.sparks = []
        for i in range(260):
            x = rnd.uniform(60, LW - 60); y = rnd.uniform(300, 660)
            if s.city_px[int(y), int(x), 3] > 60: s.sparks.append((x, y, s.dis[int(y), int(x)], rnd.uniform(0.6, 1.6), rnd.uniform(-20, 40)))

    def frame(s, t, zf, pan=(0, 0), city_alpha=1.0, dis_p=None, boat_alpha=1.0, tint=None, dust=0.0):
        z0 = 0.9
        zf_ = lambda k: z0 * (1 + (zf - 1) * k)
        cx0, cy0 = LW / 2 + pan[0], LH / 2 + pan[1]
        base = Image.new('RGBA', (W, H), (0, 0, 0, 255))
        def L(img, k, ox=0, oy=0):
            put(base, view(img, zf_(k), LW / 2 + (cx0 - LW / 2) * k + ox, LH / 2 + (cy0 - LH / 2) * k + oy), 0, 0)
        L(s.sky, 0.2)
        L(tile_scroll(s.cl1, t * 6), 0.3, 0, -60)
        L(s.mount, 0.5)
        L(s.sea, 0.8)
        for i, wv in enumerate(s.waves):
            L(ImageChops.offset(wv, int(t * (14 + i * 18)) % LW, int(2.5 * math.sin(t * 1.3 + i))), 0.85)
        L(s.land, 1.0)
        city = s.city
        if dis_p is not None and dis_p > 0:
            m = np.clip((dis_p * 1.7 - s.dis) / 0.16, 0, 1)
            px = s.city_px.copy()
            px[..., 3] = (px[..., 3] * (1 - m)).astype(np.uint8)
            city = Image.fromarray(px, 'RGBA')
        if city_alpha < 1: city = fade(city, city_alpha)
        if city_alpha > 0.01: L(city, 1.0)
        if boat_alpha > 0.02:
            ov = Image.new('RGBA', (LW, LH), (0, 0, 0, 0))
            for b, x, y, ph in s.boats:
                bob = 3 * math.sin(t * 1.4 + ph)
                put(ov, b.rotate(2.5 * math.sin(t * 1.1 + ph), resample=Image.BICUBIC), x, y + bob)
            L(fade(ov, boat_alpha), 1.0)
        # cloud shadow layer
        L(tile_scroll(s.cl2, t * 12 + 400), 1.1, 0, -330)
        if dis_p is not None and dis_p > 0:   # golden sparks
            ov = Image.new('RGBA', (LW, LH), (0, 0, 0, 0))
            for x, y, d, sp, dx in s.sparks:
                life = (dis_p * 1.7 - d) / 0.9
                if 0 < life < 1:
                    put(ov, blob(5, (255, 230, 170), 255, 1.4), x + dx * life - 5, y - 130 * sp * life - 5, math.sin(life * math.pi))
            L(ov, 1.0)
        L(s.fg, 1.25)
        if tint:
            base.alpha_composite(Image.new('RGBA', (W, H), tint))
        return base

# =========================================================================== SCENE 1
class Scene1:
    start, end = 0.0, 6.4
    def __init__(s): s.c = Coast(1)
    def render(s, t):
        p = t / 6.4
        zf = 1 + 0.16 * sstep(0, 1, p)
        dp = sstep(3.6, 6.2, t)
        im = s.c.frame(t, zf, pan=(-30 + 60 * p, 8 * p), dis_p=dp if t > 3.6 else None,
                       boat_alpha=1 - sstep(4.6, 6.0, t))
        # sun-ray light & birds
        for i in range(4):
            bird(im, 300 + i * 90 + t * 40 + 20 * math.sin(i), 160 + i * 18 - t * 5, 7 + i, t * 9 + i * 1.7)
        # mist rising as the city vanishes
        if dp > 0:
            mist = Image.new('RGBA', (W, H), (235, 232, 226, int(110 * sstep(0, 1, dp))))
            im.alpha_composite(mist)
        return im

# =========================================================================== SCENE 2
def helmet(cv, cx, cy, s_):
    br = (176, 124, 62); hi = (232, 190, 110); lo = (96, 62, 36)
    # crest
    cv.poly([(cx - 0.55 * s_, cy - 0.45 * s_), (cx - 0.3 * s_, cy - 1.0 * s_), (cx + 0.2 * s_, cy - 1.12 * s_), (cx + 0.55 * s_, cy - 0.9 * s_), (cx + 0.45 * s_, cy - 0.6 * s_), (cx, cy - 0.7 * s_)], (150, 28, 30, 255))
    for i in range(12):
        a = i / 11
        cv.line([(cx - 0.45 * s_ + 0.95 * s_ * a, cy - 0.5 * s_ - 0.55 * s_ * math.sin(a * 3.14)), (cx - 0.4 * s_ + 0.9 * s_ * a, cy - 0.2 * s_)], (200, 54, 50, 255), 0.03 * s_)
    # dome
    cv.ellipse(cx - 0.62 * s_, cy - 0.65 * s_, cx + 0.62 * s_, cy + 0.4 * s_, br + (255,))
    cv.ellipse(cx - 0.55 * s_, cy - 0.6 * s_, cx + 0.15 * s_, cy + 0.1 * s_, shade(br, 1.15) + (255,))
    cv.ellipse(cx - 0.4 * s_, cy - 0.55 * s_, cx - 0.05 * s_, cy - 0.2 * s_, hi + (255,))
    # face opening
    cv.poly([(cx - 0.34 * s_, cy - 0.12 * s_), (cx + 0.34 * s_, cy - 0.12 * s_), (cx + 0.3 * s_, cy + 0.05 * s_), (cx + 0.07 * s_, cy + 0.05 * s_), (cx + 0.08 * s_, cy + 0.5 * s_), (cx - 0.08 * s_, cy + 0.5 * s_), (cx - 0.07 * s_, cy + 0.05 * s_), (cx - 0.3 * s_, cy + 0.05 * s_)], (14, 10, 10, 255))
    # cheek guards
    cv.poly([(cx - 0.62 * s_, cy + 0.05 * s_), (cx - 0.3 * s_, cy + 0.05 * s_), (cx - 0.12 * s_, cy + 0.55 * s_), (cx - 0.45 * s_, cy + 0.62 * s_), (cx - 0.6 * s_, cy + 0.35 * s_)], shade(br, 0.9) + (255,))
    cv.poly([(cx + 0.62 * s_, cy + 0.05 * s_), (cx + 0.3 * s_, cy + 0.05 * s_), (cx + 0.12 * s_, cy + 0.55 * s_), (cx + 0.45 * s_, cy + 0.62 * s_), (cx + 0.6 * s_, cy + 0.35 * s_)], lo + (255,))
    cv.line([(cx - 0.35 * s_, cy - 0.12 * s_), (cx + 0.35 * s_, cy - 0.12 * s_)], hi + (255,), 0.025 * s_)
    cv.poly([(cx - 0.62 * s_, cy + 0.3 * s_), (cx - 0.1 * s_, cy + 0.75 * s_), (cx + 0.6 * s_, cy + 0.32 * s_), (cx + 0.7 * s_, cy + 0.9 * s_), (cx - 0.7 * s_, cy + 0.9 * s_)], (70, 50, 36, 255))  # dirt mound

class Scene2:
    start, end = 6.4, 11.9
    SL = 90   # slant
    def __init__(s):
        rnd = random.Random(2)
        # ---- panel 1: abandoned house
        cv = Canvas(W, H, 2)
        cv.im.paste(vgrad_img(W * 2, H * 2, [(0, (118, 168, 214)), (0.6, (214, 226, 226)), (1, (190, 190, 150))]), (0, 0))
        cv.poly([(0, 470), (200, 430), (420, 460), (700, 420), (W, 470), (W, H), (0, H)], (118, 140, 130, 255))
        cv.poly([(0, 520), (300, 500), (600, 530), (W, 500), (W, H), (0, H)], (96, 128, 84, 255))
        cv.grad_poly([(0, 560), (W, 560), (W, H), (0, H)], (100, 130, 72), (60, 86, 48))
        hx, hy_, hw, hh = 40, 600, 420, 280
        cv.rect(hx, hy_ - hh, hx + hw, hy_, (206, 186, 150, 255))
        cv.rect(hx + hw, hy_ - hh + 20, hx + hw + 110, hy_ + 12, (150, 132, 108, 255))
        for i in range(70):   # crumbled plaster & stones
            x = hx + rnd.random() * hw; y = hy_ - hh + rnd.random() * hh
            ww, hh2 = rnd.uniform(14, 44), rnd.uniform(8, 20)
            cv.rect(x, y, x + ww, y + hh2, shade((206, 186, 150), rnd.uniform(0.72, 1.0)) + (255,))
        cv.poly([(hx - 20, hy_ - hh + 10), (hx + 150, hy_ - hh - 70), (hx + 230, hy_ - hh - 40), (hx + 300, hy_ - hh - 90), (hx + hw + 20, hy_ - hh + 10)], (160, 88, 62, 255))
        cv.poly([(hx + 150, hy_ - hh - 70), (hx + 190, hy_ - hh - 20), (hx + 230, hy_ - hh - 40)], (40, 30, 30, 255))  # hole in roof
        cv.poly([(hx + 180, hy_ - hh - 30), (hx + 250, hy_ - hh - 10), (hx + 240, hy_ - hh + 10), (hx + 170, hy_ - hh)], (36, 26, 26, 255))
        cv.rect(hx + 40, hy_ - 190, hx + 130, hy_, (28, 20, 18, 255))               # broken door
        cv.poly([(hx + 130, hy_ - 190), (hx + 150, hy_ - 170), (hx + 150, hy_ - 10), (hx + 130, hy_)], (96, 66, 44, 255))
        cv.rect(hx + 230, hy_ - 210, hx + 320, hy_ - 120, (26, 22, 28, 255))      # window
        cv.line([(hx + 230, hy_ - 210), (hx + 320, hy_ - 120)], (160, 120, 80, 255), 4)
        cv.poly([(hx + 320, hy_ - 210), (hx + 350, hy_ - 200), (hx + 350, hy_ - 110), (hx + 320, hy_ - 120)], (110, 80, 54, 255))
        for k in range(26):    # vines
            x = hx + rnd.uniform(0, hw); y = hy_ - rnd.uniform(0, hh)
            pts = [(x, y)]
            for j in range(rnd.randint(4, 9)):
                x += rnd.uniform(-14, 14); y += rnd.uniform(10, 26); pts.append((x, y))
            cv.line(pts, (48, 90, 44, 255), 3)
            for px_, py_ in pts[1:]:
                cv.ellipse(px_ - 8, py_ - 5, px_ + 8, py_ + 5, (70 + rnd.randint(0, 40), 130 + rnd.randint(0, 40), 60, 255))
        for i in range(260):   # weeds
            x = rnd.uniform(0, W); y = rnd.uniform(580, H)
            h_ = rnd.uniform(18, 56)
            cv.line([(x, y), (x + rnd.uniform(-8, 8), y - h_)], (70 + rnd.randint(0, 60), 120 + rnd.randint(0, 50), 56, 255), 2)
        cypress(cv, 640, 640, 260, 30, (34, 64, 44))
        s.p1 = paint_tex(cv.image(), 0.06, 5)
        s.cl = clouds(W, 300, 21, 6, (255, 255, 255), (190, 205, 230), 200, 0.8)
        # ---- panel 2: aftermath of battle
        cv = Canvas(W, H, 2)
        cv.im.paste(vgrad_img(W * 2, H * 2, [(0, (60, 36, 40)), (0.45, (176, 84, 52)), (0.62, (240, 150, 70)), (1, (90, 60, 44))]), (0, 0))
        add = blob(300, (255, 190, 90), 255, 2)
        put(cv.im, blob(560, (255, 176, 80), 255, 2.2).resize((1120, 1120)), 640, 140, 0.8)
        cv.poly([(0, 470), (160, 450), (360, 478), (520, 440), (740, 470), (1000, 440), (W, 470), (W, H), (0, H)], (58, 36, 36, 255))
        cv.grad_poly([(0, 520), (W, 500), (W, H), (0, H)], (82, 58, 44), (34, 24, 22))
        for i in range(34):   # spears and broken shields
            x = rnd.uniform(0, W); y = rnd.uniform(520, 700); a = rnd.uniform(-0.35, 0.35); L_ = rnd.uniform(110, 260)
            cv.line([(x, y), (x + math.sin(a) * L_, y - math.cos(a) * L_)], (30, 20, 18, 255), 3)
            cv.poly([(x + math.sin(a) * L_, y - math.cos(a) * L_), (x + math.sin(a) * (L_ + 18) + 3, y - math.cos(a) * (L_ + 18)), (x + math.sin(a) * L_ - 3, y - math.cos(a) * L_ + 2)], (110, 100, 96, 255))
        for i in range(14):
            x = rnd.uniform(0, W); y = rnd.uniform(600, 710)
            cv.ellipse(x, y, x + rnd.uniform(40, 80), y + rnd.uniform(14, 26), (110, 70, 40, 255))
        helmet(cv, 640, 520, 220)
        s.p2 = paint_tex(cv.image(), 0.07, 6)
        s.smoke = [(rnd.uniform(60, W - 60), rnd.uniform(440, 480), rnd.uniform(0, 4)) for _ in range(5)]
        # ---- panel 3: vanished -> bare land (no city)
        c = Coast(1)
        s.c3 = c
        # ---- brush slashes drawn live
    def panel_poly(s, i, grow=0.0):
        w = (W + 2 * s.SL) / 3.0
        x0 = -s.SL + i * w + (i > 0) * -0
        x1 = x0 + w + 6
        if i == 0: x0 = -s.SL - 10
        if i == 2: x1 = W + s.SL + 10
        # grow: panel 2 (index 2) expands to cover everything
        if i == 2: x0 = lerp(x0, -s.SL - 20, grow)
        pts = [(x0 + s.SL, 0), (x1 + s.SL, 0), (x1, H), (x0, H)]
        return pts
    def mask_for(s, pts):
        m = Image.new('L', (W * 2, H * 2), 0)
        ImageDraw.Draw(m).polygon([(x * 2, y * 2) for x, y in pts], fill=255)
        return m.resize((W, H), Image.LANCZOS)
    def render(s, t):
        base = Image.new('RGBA', (W, H), (10, 8, 14, 255))
        # time windows
        r = [sstep(6.4, 7.0, t), sstep(7.9, 8.5, t), sstep(10.6, 11.1, t)]
        grow = sstep(11.0, 11.8, t)
        # panel 1
        zoom = 1.0 + 0.06 * (t - 6.4) / 5.5
        sky = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        p1 = s.p1.copy()
        p1b = Image.new('RGBA', (W, H), (0, 0, 0, 255)); p1b.alpha_composite(s.p1.crop((0, 0, W, H)))
        c1 = tile_scroll(s.cl, t * 14)
        pn = Image.new('RGBA', (W, H), (0, 0, 0, 255))
        pn.alpha_composite(s.p1.crop((0, 0, W, H)))
        # clouds behind house are baked; add drifting clouds on top of sky using low alpha
        put(pn, fade(c1, 0.5), 0, 20)
        for i in range(3):
            bird(pn, (t * 60 + i * 140) % (W + 200) - 100, 150 + i * 30, 9, t * 10 + i)
        for i in range(10):   # falling leaves
            lx = (i * 131 + t * 40 + 60 * math.sin(t * 2 + i)) % W; ly = (i * 97 + t * 55) % H
            glow(pn, lx, ly, 5, (130, 160, 60), 0.9, 1.0)
        pn = cam(pn, zoom, W / 2, H / 2)
        d = ImageDraw.Draw(pn)
        # slash 1
        sl = sstep(7.35, 7.8, t)
        if sl > 0:
            x0, y0, x1, y1 = 40, 120, 40 + 520 * sl, 120 + 480 * sl
            d.line([(x0, y0), (x1, y1)], fill=(190, 30, 30, 235), width=22)
            d.line([(x0 + 4, y0 + 8), (x1 + 4, y1 + 8)], fill=(120, 14, 14, 200), width=8)
        # panel 2
        z2 = 1.0 + 0.07 * (t - 7.9) / 4
        p2 = Image.new('RGBA', (W, H), (0, 0, 0, 255)); p2.alpha_composite(s.p2.crop((0, 0, W, H)))
        for x, y, ph in s.smoke:
            for k in range(14):
                u = ((t * 0.28 + ph * 0.2 + k / 14.0) % 1.0)
                rr = 24 + 90 * u
                glow(p2, x + 40 * math.sin(u * 5 + ph) + u * 100, y - u * 380, rr, (50, 40, 44), 0.55 * (1 - u), 1.0)
        for i in range(60):   # embers
            u = (t * 0.2 + i * 0.137) % 1.0
            ex = (i * 193) % W + 30 * math.sin(t + i); ey = H - u * H * 0.9
            glow(p2, ex, ey, 3, (255, 170, 70), 1 - u, 1.0)
        if 8.4 < t:   # distant flare
            add_light(p2, 960, 480, 220 + 20 * math.sin(t * 7), (255, 150, 60), 0.5)
        p2 = cam(p2, z2, W / 2, H / 2)
        d2 = ImageDraw.Draw(p2)
        sl2 = sstep(9.7, 10.2, t)
        if sl2 > 0:
            x0, y0, x1, y1 = 420, 80, 420 + 470 * sl2, 80 + 500 * sl2
            d2.line([(x0, y0), (x1, y1)], fill=(200, 36, 30, 235), width=24)
            d2.line([(x0 + 4, y0 + 8), (x1 + 4, y1 + 8)], fill=(120, 14, 14, 200), width=8)
        # panel 3 (vanished land)
        p3 = s.c3.frame(t, 1.0 + 0.05 * (t - 6.4) / 5, city_alpha=0.0, boat_alpha=0.0)
        haze = Image.new('RGBA', (W, H), (214, 186, 140, 90)); p3.alpha_composite(haze)
        for i in range(36):  # dust streaks
            y = (i * 53) % H; x = ((t * 500 + i * 211) % (W + 400)) - 200
            glow(p3, x, y, 34, (238, 214, 170), 0.16, 1.0)
        # composite panels
        base.alpha_composite(Image.new('RGBA', (W, H), (14, 12, 18, 255)))
        # panel 1
        if r[0] > 0:
            pts = s.panel_poly(0)
            off = (1 - ease_out(r[0])) * -H
            m = s.mask_for(pts)
            tmp = Image.new('RGBA', (W, H), (0, 0, 0, 0)); put(tmp, pn, 0, off)
            tmp.putalpha(ImageChops.multiply(tmp.getchannel('A'), m)); base.alpha_composite(tmp)
        if r[1] > 0:
            pts = s.panel_poly(1)
            off = (1 - ease_out(r[1])) * H
            m = s.mask_for(pts)
            tmp = Image.new('RGBA', (W, H), (0, 0, 0, 0)); put(tmp, p2, 0, off)
            tmp.putalpha(ImageChops.multiply(tmp.getchannel('A'), m)); base.alpha_composite(tmp)
        if r[2] > 0:
            pts = s.panel_poly(2, grow)
            off = (1 - ease_out(r[2])) * -H
            m = s.mask_for(pts)
            tmp = Image.new('RGBA', (W, H), (0, 0, 0, 0)); put(tmp, p3, 0, off)
            tmp.putalpha(ImageChops.multiply(tmp.getchannel('A'), m)); base.alpha_composite(tmp)
        # white diagonal dividers
        dv = ImageDraw.Draw(base)
        w = (W + 2 * s.SL) / 3.0
        fadeout = 1 - sstep(11.2, 11.8, t)
        for i in (1, 2):
            if r[i] > 0 and fadeout > 0:
                x = -s.SL + i * w
                dv.line([(x + s.SL, 0), (x, H)], fill=(250, 246, 236, int(255 * fadeout)), width=5)
        return base

# =========================================================================== SCENE 3
class Scene3:
    start, end = 11.9, 22.6
    VP = (768, 340)
    def __init__(s):
        rnd = random.Random(33)
        VX, VY = s.VP
        # sky
        sky = vgrad_img(LW, LH, [(0, (30, 44, 104)), (0.25, (96, 74, 130)), (0.38, (232, 140, 96)), (0.42, (255, 188, 110)), (1, (255, 200, 130))])
        put(sky, blob(520, (255, 200, 120), 255, 2.2), VX - 520, VY - 520, 0.95)
        put(sky, blob(110, (255, 244, 210), 255, 1.4), VX - 110, VY - 130, 1.0)
        s.sky = sky
        cv = Canvas(LW, LH, 2)
        far = ridge(LW, VY - 20, 26, 8)
        fill_ridge(cv, far, (92, 62, 98), (150, 90, 90), VY + 10, rim=(255, 190, 120))
        for i in range(18):   # distant ruined skyline
            x = rnd.uniform(380, 1180); h_ = rnd.uniform(14, 40); w_ = rnd.uniform(6, 22)
            cv.rect(x, VY - h_, x + w_, VY + 4, (70, 46, 84, 255))
        s.far = cv.image()
        # bare ground
        cv = Canvas(LW, LH, 2)
        cv.grad_poly([(0, VY), (LW, VY), (LW, LH), (0, LH)], (176, 120, 84), (86, 58, 50), VY, LH)
        for i in range(400):
            z = rnd.uniform(1.1, 14); x = VX + rnd.uniform(-1, 1) * 900 / z; y = VY + 524 / z
            cv.ellipse(x - 8 / z * 3, y, x + 8 / z * 3, y + 3 / z, (70, 46, 40, 160))
        s.ground = paint_tex(cv.image(), 0.07, 7)
        # road with cobbles
        cv = Canvas(LW, LH, 2)
        RW = 480
        cv.grad_poly([(VX, VY), (VX + RW * 0.012 * 524 / 524 * 5, VY), (VX + RW * 2.4, LH), (VX - RW * 2.4, LH), (VX - RW * 0.06, VY)], (255, 190, 120), (126, 92, 78), VY, LH)
        n = 34
        for i in range(n):
            u = i / n; y = VY + (LH - VY) * u ** 2.2
            half = (y - VY) / (LH - VY) * RW * 2.4
            cv.line([(VX - half, y), (VX + half, y)], (84, 58, 56, 130), 1 + 3 * u)
        for k in range(-14, 15):
            cv.line([(VX + k * 4, VY), (VX + k * 175, LH)], (84, 58, 56, 110), 2)
        s.road = paint_tex(cv.image(), 0.08, 8)
        # buildings / colonnades (both sides), far to near
        cv = Canvas(LW, LH, 2); cv2 = Canvas(LW, LH, 2)   # cv: houses (fade), cv2: columns (persist)
        G = LH - VY
        def sx(z): return 1.0 / z
        zs = [14, 11.5, 9.5, 8, 6.7, 5.6, 4.7, 3.9, 3.2, 2.6, 2.1, 1.7, 1.4, 1.15]
        pal = [(244, 200, 150), (236, 170, 130), (226, 190, 140), (240, 150, 120), (214, 176, 140)]
        for side in (-1, 1):
            for j in range(len(zs) - 1):
                z0, z1 = zs[j], zs[j + 1]
                s0, s1 = sx(z0), sx(z1)
                xe0 = VX + side * 330 * s0 * 2.2; xe1 = VX + side * 330 * s1 * 2.2
                g0 = VY + G * s0; g1 = VY + G * s1
                col_block = (j + (0 if side < 0 else 1)) % 3 == 0
                if col_block:
                    for q in range(3):
                        zq = lerp(z0, z1, (q + 0.5) / 3); sq = sx(zq)
                        x = VX + side * 330 * sq * 2.2 + side * 20 * sq; gq = VY + G * sq
                        column(cv2, x, gq, 380 * sq, 56 * sq, (240, 190, 140), broken=(0.0 if rnd.random() < 0.5 else rnd.uniform(0.2, 0.55)), seed=j * 7 + q)
                    continue
                hgt = rnd.choice([300, 340, 420]); wall = rnd.choice(pal)
                # side wall (faces road)
                top0 = g0 - hgt * s0; top1 = g1 - hgt * s1
                cv.poly([(xe0, top0), (xe1, top1), (xe1, g1), (xe0, g0)], shade(wall, 0.6) + (255,))
                cv.poly([(xe0, g0 - 18 * s0), (xe1, g1 - 18 * s1), (xe1, g1), (xe0, g0)], (60, 40, 50, 120))
                # door on side wall
                for q in (0.3, 0.7):
                    zq = lerp(z0, z1, q); sq = sx(zq); xq = VX + side * 330 * sq * 2.2; gq = VY + G * sq
                    cv.rect(min(xq, xq + side * 0), gq - 150 * sq, xq + 0.1, gq, (40, 26, 30, 0))
                    cv.poly([(xq, gq - 170 * sq), (xq, gq), (xq + side * 55 * sq * 0.35, gq - 6 * sq), (xq + side * 55 * sq * 0.35, gq - 160 * sq)], (50, 32, 36, 255))
                # near end facade (faces viewer)
                bw = 380 * s1
                fx0, fx1 = (xe1, xe1 + side * bw)
                fx0, fx1 = min(fx0, fx1), max(fx0, fx1)
                cv.rect(fx0, g1 - hgt * s1, fx1, g1, wall + (255,))
                cv.rect(fx0, g1 - hgt * s1 - 8 * s1, fx1, g1 - hgt * s1, (176, 92, 70, 255))
                for wq in range(2):
                    wx = fx0 + (fx1 - fx0) * (0.2 + 0.4 * wq)
                    cv.rect(wx, g1 - hgt * s1 * 0.72, wx + 55 * s1, g1 - hgt * s1 * 0.38, (50, 40, 60, 255))
                cv.rect(fx0, g1 - hgt * s1 * 0.2, fx1, g1, shade(wall, 0.9) + (255,))
        s.houses = paint_tex(cv.image(), 0.05, 9)
        s.cols = paint_tex(cv2.image(), 0.05, 10)
        # ruin stumps in the foreground that stay
        cv = Canvas(LW, LH, 2)
        for x, h_, w_ in [(120, 340, 66), (1430, 300, 62), (300, 150, 60), (1260, 120, 60)]:
            column(cv, x, LH - 60 + (x % 40), h_, w_, (214, 160, 120), broken=0.3 if h_ < 200 else 0.0, seed=int(x))
        for i in range(10):
            x = rnd.uniform(0, LW); y = rnd.uniform(LH - 60, LH - 10)
            cv.poly([(x, y), (x + 40, y - 12), (x + 80, y), (x + 70, y + 20), (x + 10, y + 22)], (126, 96, 84, 255))
        s.fg = paint_tex(cv.image(), 0.06, 11)
        # people (dark silhouettes lit from behind)
        s.walkers = [Walker(h=160, tunic=(98, 62, 76), cloak=(70, 50, 78), skin=(110, 70, 66), hair=(30, 22, 28), beard=True),
                     Walker(h=160, tunic=(120, 80, 70), female=True, skin=(120, 78, 70), hair=(30, 20, 20), carry='amphora'),
                     Walker(h=160, tunic=(84, 60, 80), skin=(110, 70, 66), hair=(30, 22, 28))]
        s.ppl = [(rnd.choice([-1, 1]) * rnd.uniform(0.1, 0.8), rnd.uniform(0, 1), rnd.choice([0, 1, 2]), rnd.choice([1, -1])) for _ in range(9)]
        # question mark
        q = Canvas(520, 640, 1)
        f = font('Cinzel.ttf', 520, 700)
        q.text((260, 320), '?', f, (255, 232, 170, 255), 'mm')
        qi = q.im
        gl = qi.filter(ImageFilter.GaussianBlur(26))
        gl2 = qi.filter(ImageFilter.GaussianBlur(10))
        s.q = qi; s.qg = gl; s.qg2 = gl2
        s.motes = [(rnd.uniform(0, LW), rnd.uniform(0, LH), rnd.uniform(0.3, 1.0)) for _ in range(80)]
    def render(s, t):
        VX, VY = s.VP
        L = t - 11.9
        p = clamp(L / 10.6)
        zoom = 0.9 * (1 + 0.20 * p)
        fcam = lambda k: zoom * (1 + 0.0 * k)
        base = Image.new('RGBA', (W, H), (0, 0, 0, 255))
        cy = 405 + 10 * p
        def Lr(img, k=1.0, op=1.0):
            z = 0.9 * (1 + 0.20 * p * k)
            put(base, fade(view(img, z, VX + 6 * math.sin(L * 0.3), cy), op) if op < 0.999 else view(img, z, VX + 6 * math.sin(L * 0.3), cy), 0, 0)
        houses_a = 1 - sstep(12.7, 14.3, t)
        road_a = 1 - sstep(14.4, 15.9, t)
        ppl_a = 1 - sstep(15.9, 17.2, t)
        Lr(s.sky, 0.05)
        Lr(s.far, 0.2)
        Lr(s.ground, 0.9)
        Lr(s.road, 1.0, road_a)
        # dissolving houses with golden sparks
        if houses_a > 0.01:
            Lr(s.houses, 1.0, houses_a)
        Lr(s.cols, 1.0)
        # people
        if ppl_a > 0.01:
            ov = Image.new('RGBA', (LW, LH), (0, 0, 0, 0))
            for off, ph, kind, d in s.ppl:
                z = lerp(7.5, 1.7, (ph + L * 0.02 * d) % 1.0 if d > 0 else (1 - (ph + L * 0.02) % 1.0))
                sc = 1.0 / z
                spr = s.walkers[kind].get(((L * 0.9 + ph * 5) % 1.0))
                size = (int(spr.width * sc * 1.9), int(spr.height * sc * 1.9))
                if size[0] < 2: continue
                spr = spr.resize(size, Image.BILINEAR)
                x = VX + off * 400 * sc * 2.2; y = VY + 524 * sc
                put(ov, spr, x - size[0] / 2, y - size[1])
            Lr(ov, 1.0, ppl_a)
        Lr(s.fg, 1.3)
        # light & dust
        add_light(base, 640, 300, 520, (255, 170, 80), 0.35 + 0.05 * math.sin(L))
        for x, y, k in s.motes:
            mx = (x + L * 25 * k) % LW; my = (y - L * 14 * k) % LH
            glow(base, mx * 0.8, my * 0.8, 3 + 2 * k, (255, 220, 170), 0.55, 1.0)
        # question mark
        qa = sstep(17.3, 18.4, t)
        if qa > 0:
            sc = 0.55 + 0.45 * ease_back((t - 17.3) / 1.1)
            pulse = 0.75 + 0.25 * math.sin(L * 3.1)
            fl = 8 * math.sin(L * 1.3)
            for im_, op in ((s.qg, 0.9 * pulse), (s.qg2, 0.8), (s.q, 1.0)):
                sz = (int(im_.width * sc * 0.85), int(im_.height * sc * 0.85))
                spr = im_.resize(sz, Image.BILINEAR)
                put(base, spr, 640 - sz[0] / 2, 232 - sz[1] / 2 + fl, op * qa)
            add_light(base, 640, 235 + fl, 260, (255, 210, 120), 0.6 * qa * pulse)
        base.alpha_composite(Image.new('RGBA', (W, H), (20, 10, 40, int(70 * p))))
        return base

# =========================================================================== SCENE 4
class Scene4:
    start, end = 22.6, 31.0
    def __init__(s):
        s.c = Coast(4)
        t_ = Canvas(1100, 360, 2)
        f = font('Cinzel.ttf', 380, 700)
        s.letters = []
        word = 'HELIKE'
        sp = 16
        widths = [f.getlength(ch) / 2 for ch in word]
        total = sum(widths) + sp * (len(word) - 1)
        x = 550 - total / 2
        for ch, w_ in zip(word, widths):
            cv = Canvas(int(w_ + 80), 300, 2)
            # gold gradient letter
            m = Canvas(int(w_ + 80), 300, 2); m.text((40, 150), ch, f, (255, 255, 255, 255), 'lm')
            alpha = m.im.getchannel('A')
            g = vgrad_img(m.im.width, m.im.height, [(0, (255, 244, 205)), (0.55, (240, 206, 130)), (1, (170, 118, 52))])
            g.putalpha(alpha)
            sh = Image.new('RGBA', g.size, (30, 14, 8, 0)); sh.putalpha(alpha.filter(ImageFilter.GaussianBlur(10)).point(lambda v: v * 3 // 4))
            glw = Image.new('RGBA', g.size, (255, 214, 120, 0)); glw.putalpha(alpha.filter(ImageFilter.GaussianBlur(26)))
            full = Image.new('RGBA', g.size, (0, 0, 0, 0))
            full.alpha_composite(sh, (6, 12)); full.alpha_composite(glw); full.alpha_composite(g)
            full = full.resize((g.size[0] // 2, g.size[1] // 2), Image.LANCZOS)
            s.letters.append((full, x - 40))
            x += w_ + sp
        s.fx = font('Cinzel.ttf', 40, 600)
        s.rays = [(math.radians(a), 0.5 + 0.5 * random.Random(a).random()) for a in range(-80, 81, 8)]
    def render(s, t):
        L = t - 22.6
        p = L / 8.4
        zf = 1.0 + 0.10 * p
        im = s.c.frame(t, zf, pan=(40 - 80 * p, 10 - 10 * p), boat_alpha=1.0, tint=None)
        # warm bloom
        add_light(im, 350, 330, 420, (255, 200, 120), 0.35)
        for i in range(3):
            bird(im, 820 + i * 70 - L * 18, 130 + i * 20 + L * 6, 7 + i, t * 9 + i)
        # "2,300 years" tag
        ya = sstep(23.2, 24.2, t) * (1 - sstep(27.5, 28.5, t))
        if ya > 0:
            ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
            f = font('Cinzel.ttf', 54, 600)
            txt = 'OVER 2,300 YEARS AGO'
            tw = d.textlength(txt, font=f)
            d.text((640 - tw / 2 + 3, 128 + 3), txt, font=f, fill=(20, 10, 10, int(160 * ya)))
            d.text((640 - tw / 2, 128), txt, font=f, fill=(255, 238, 200, int(255 * ya)))
            d.line([(640 - 150, 200), (640 + 150, 200)], fill=(255, 220, 150, int(220 * ya)), width=2)
            im.alpha_composite(ov)
        # HELIKE reveal
        ta = 29.0
        if t > ta - 0.1:
            k = t - ta
            dark = sstep(0, 1.0, k)
            im.alpha_composite(Image.new('RGBA', (W, H), (10, 8, 24, int(90 * dark))))
            ra = sstep(0, 1.2, k)
            ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            for ang, ln in s.rays:
                a = ang + 0.03 * math.sin(L * 0.7 + ang * 5)
                px, py = 640, 520
                pts = [(px, py), (px + math.sin(a - 0.02) * 1500, py - math.cos(a - 0.02) * 1500), (px + math.sin(a + 0.02) * 1500, py - math.cos(a + 0.02) * 1500)]
                ImageDraw.Draw(ov).polygon(pts, fill=(255, 226, 160, int(34 * ln * ra)))
            im.alpha_composite(ov)
            for i, (img, x) in enumerate(s.letters):
                lk = clamp((k - i * 0.11) / 0.7)
                if lk <= 0: continue
                sc = 1.0 + 0.5 * (1 - ease_out(lk))
                sz = (int(img.width * sc), int(img.height * sc))
                spr = img.resize(sz, Image.BILINEAR)
                cx = 90 + x + img.width / 2 + 0 ; cy = 480
                put(im, spr, cx - sz[0] / 2, cy - sz[1] / 2 + 14 * (1 - ease_out(lk)), ease_out(lk))
            add_light(im, 640, 482, 380, (255, 214, 130), 0.28 * ra * (0.8 + 0.2 * math.sin(L * 3)))
            # shimmer sweep
            sw = (k * 420 - 200) % 1800 - 200
            if k < 3.5:
                ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
                ImageDraw.Draw(ov).polygon([(sw, 380), (sw + 40, 380), (sw - 20, 580), (sw - 60, 580)], fill=(255, 255, 255, 70))
                im.alpha_composite(ov)
        return im
