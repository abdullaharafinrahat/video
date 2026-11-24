"""Scenes 7-9: the city of Helike, the god of the sea, the disaster."""
import math, random
import numpy as np
from gfx import *
from scenes_a import view

def mirrored(w):
    from copy import copy
    m = copy(w); m.frames = [ImageOps.mirror(f) for f in w.frames]; return m

def noise_s(t, a=1.0):
    return (math.sin(t * 37.1) + 0.6 * math.sin(t * 61.7 + 1.0)) * a, (math.cos(t * 43.3) + 0.5 * math.sin(t * 71.3)) * a

# ===================================================================== SCENE 7
class Scene7:
    start, end = 70.0, 79.9
    WL, WH = 1700, 864
    def __init__(s):
        rnd = random.Random(7); WL, WH = s.WL, s.WH
        s.sky = vgrad_img(WL, WH, [(0, (56, 124, 212)), (0.5, (146, 196, 236)), (0.72, (238, 234, 216)), (1, (240, 220, 184))])
        put(s.sky, blob(380, (255, 244, 210), 255, 2.2), 1250 - 380, 150 - 380, 0.8)
        s.cl = clouds(WL, 380, 71, 8, (255, 255, 255), (196, 208, 232), 225, 1.0)
        cv = Canvas(WL, WH, 2)
        far = ridge(WL, 380, 46, 12) - 90 * np.exp(-((np.arange(WL) - 300) / 260.0) ** 2)
        fill_ridge(cv, far, (118, 150, 156), (206, 218, 206), 560, rim=(236, 240, 228))
        near = ridge(WL, 440, 30, 14)
        fill_ridge(cv, near, (88, 130, 88), (180, 184, 124), 580, rim=(206, 214, 156))
        s.hills = paint_tex(cv.image(), 0.04, 1)
        # distant city
        cv = Canvas(WL, WH, 2)
        yb = 575
        for i in range(60):
            x = rnd.uniform(0, WL); w_ = rnd.uniform(26, 56)
            house(cv, x, yb + rnd.uniform(-14, 4), w_, rnd.uniform(26, 56), rnd.choice([(246, 242, 232), (236, 226, 204), (228, 210, 176)]), (196, 112, 80), i, rnd.random() < 0.6)
        temple_front(cv, 1170, yb + 6, 8, 120, 16, 30, steps=3)
        temple_front(cv, 360, yb + 6, 6, 80, 11, 24, steps=2, seed=3)
        # long stoa
        x0 = 560
        cv.rect(x0, yb - 92, x0 + 440, yb, (92, 80, 70, 255))
        for i in range(18): column(cv, x0 + 10 + i * 25, yb, 90, 11, STONE)
        cv.rect(x0 - 6, yb - 106, x0 + 446, yb - 90, (236, 226, 204, 255)); cv.poly([(x0 - 14, yb - 106), (x0 + 454, yb - 106), (x0 + 430, yb - 130), (x0 + 10, yb - 130)], (190, 108, 78, 255))
        for x, h_ in [(60, 120), (140, 90), (1000, 100), (1600, 130), (1500, 90)]: cypress(cv, x, yb + 6, h_)
        for x in (220, 520, 1060, 1380): tree(cv, x, yb + 8, 70, (84, 120, 70))
        s.bg = paint_tex(cv.image(), 0.04, 2)
        # ground
        cv = Canvas(WL, WH, 2)
        cv.grad_poly([(0, 575), (WL, 575), (WL, WH), (0, WH)], (226, 204, 160), (178, 146, 106), 575, WH)
        for i in range(24):
            u = i / 24; y = 575 + (WH - 575) * u ** 1.6
            cv.line([(0, y), (WL, y)], (150, 120, 88, 70), 1 + 2 * u)
        for k in range(-26, 27):
            cv.line([(850 + k * 14, 575), (850 + k * 90, WH)], (150, 120, 88, 50), 1.5)
        # steps on the right
        for i in range(5):
            cv.rect(1330 + i * 18, 575 + i * 6, WL, 575 + i * 6 + 20, shade(STONE, 1.0 - i * 0.05) + (255,))
        s.ground = paint_tex(cv.image(), 0.06, 3)
        # market stalls
        cv = Canvas(WL, WH, 2)
        cols = [((196, 64, 52), (250, 240, 220)), ((44, 104, 160), (250, 240, 220)), ((220, 170, 60), (250, 240, 220)), ((70, 130, 90), (250, 240, 220)), ((160, 70, 110), (250, 240, 220))]
        for i, xc in enumerate([180, 520, 870, 1230, 1560]):
            a, b = cols[i % 5]; yb2 = 650
            w_ = 190; h_ = 120
            cv.rect(xc - w_ / 2, yb2 - h_, xc - w_ / 2 + 7, yb2, (96, 66, 44, 255)); cv.rect(xc + w_ / 2 - 7, yb2 - h_, xc + w_ / 2, yb2, (96, 66, 44, 255))
            for k in range(8):
                x0 = xc - w_ / 2 - 10 + k * (w_ + 20) / 8
                cv.poly([(x0, yb2 - h_), (x0 + (w_ + 20) / 8, yb2 - h_), (x0 + (w_ + 20) / 8 + 3, yb2 - h_ + 38), (x0 - 3, yb2 - h_ + 38)], (a if k % 2 == 0 else b) + (255,))
                cv.ellipse(x0 - 3, yb2 - h_ + 32, x0 + (w_ + 20) / 8 + 3, yb2 - h_ + 44, (a if k % 2 == 0 else b) + (255,))
            cv.poly([(xc - w_ / 2 - 12, yb2 - h_ - 22), (xc + w_ / 2 + 12, yb2 - h_ - 22), (xc + w_ / 2 + 10, yb2 - h_), (xc - w_ / 2 - 10, yb2 - h_)], shade(a, 1.1) + (255,))
            cv.rect(xc - w_ / 2 + 8, yb2 - 44, xc + w_ / 2 - 8, yb2 - 36, (130, 92, 60, 255)); cv.rect(xc - w_ / 2 + 12, yb2 - 36, xc + w_ / 2 - 12, yb2, (110, 76, 50, 255))
            for k in range(7):  # goods
                gx = xc - w_ / 2 + 20 + k * 24
                if i % 2 == 0: cv.ellipse(gx, yb2 - 74, gx + 18, yb2 - 44, (196, 104, 62, 255)); cv.rect(gx + 6, yb2 - 82, gx + 12, yb2 - 72, (170, 86, 52, 255))
                else: cv.circle(gx + 9, yb2 - 52, 9, [(214, 70, 50, 255), (230, 170, 50, 255), (110, 160, 60, 255)][k % 3])
        s.stalls = paint_tex(cv.image(), 0.04, 4)
        # people
        base_cols = [dict(tunic=(246, 242, 230), beard=True), dict(tunic=(214, 176, 100), cloak=(60, 90, 150), beard=True),
                     dict(tunic=(214, 120, 120), female=True, carry='amphora'), dict(tunic=(120, 140, 170), female=True),
                     dict(tunic=(100, 150, 110)), dict(tunic=(246, 240, 226), cloak=(176, 52, 46), beard=True),
                     dict(tunic=(250, 246, 236), female=True, hair=(70, 40, 28)), dict(tunic=(214, 186, 140), cloak=(246, 240, 230), beard=True)]
        s.walk = []
        for i, kw in enumerate(base_cols):
            kw2 = dict(kw); kw2.setdefault('hair', rnd.choice([(40, 30, 24), (70, 50, 36), (30, 24, 22)]))
            w = Walker(n=12, h=200, skin=SKINS[i % 4], **kw2)
            s.walk.append((w, mirrored(w)))
        s.crowd = []
        for i in range(22):
            y = rnd.uniform(615, 770); hgt = lerp(112, 250, (y - 600) / 190)
            sp = rnd.choice([-1, 1]) * rnd.uniform(18, 60) * hgt / 200
            s.crowd.append((rnd.uniform(0, WL + 200), y, hgt, sp, rnd.randrange(8), rnd.uniform(0, 1)))
        # foreground heroes
        s.hero1 = Walker(n=16, h=640, tunic=(232, 218, 188), cloak=(128, 96, 70), skin=SKINS[1], beard=True, hair=(36, 26, 22), mood='calm')
        s.hero2 = Walker(n=16, h=700, tunic=(222, 152, 90), skin=SKINS[0], female=True, carry='amphora', hair=(40, 28, 24))
        s.tagf = font('Cinzel.ttf', 34, 600); s.tagf2 = font('Garamond.ttf', 28)
        s.shadow = shadow_ell(300, 40, 110)
    def render(s, t):
        L = t - 70.0
        WL, WH = s.WL, s.WH
        zoom = 0.92 + 0.05 * L / 9.9
        pan = -L * 6
        base = Image.new('RGBA', (W, H), (0, 0, 0, 255))
        def Lr(img, k, oy=0):
            put(base, view(img, zoom, WL / 2 + pan * k, 432 + oy), 0, 0)
        Lr(s.sky, 0.1)
        Lr(tile_scroll(s.cl, t * 5), 0.15, -40)
        Lr(s.hills, 0.3)
        Lr(s.bg, 0.5)
        Lr(s.ground, 0.8)
        Lr(s.stalls, 0.9)
        ov = Image.new('RGBA', (WL, WH), (0, 0, 0, 0))
        items = []
        for x0, y, hgt, sp, kind, ph in s.crowd:
            x = (x0 + sp * L) % (WL + 200) - 100
            items.append((y, x, hgt, sp, kind, ph))
        for y, x, hgt, sp, kind, ph in sorted(items):
            w, wm = s.walk[kind]
            spr = (w if sp > 0 else wm).get(((L * abs(sp) / (hgt * 0.55)) + ph) % 1.0)
            sz = (int(spr.width * hgt / 200), int(spr.height * hgt / 200))
            spr = spr.resize(sz, Image.BILINEAR)
            sh = s.shadow.resize((int(hgt * 0.7), int(hgt * 0.09)), Image.BILINEAR)
            put(ov, sh, x - sh.width / 2, y - sh.height / 2)
            put(ov, spr, x - sz[0] / 2, y - sz[1] * 0.97 + 2 * abs(math.sin(L * 5 + ph * 6)))
        Lr(ov, 1.0)
        # foreground heroes (screen space, parallax)
        for hero, x, ph, sc, k in ((s.hero1, -150 - 10 * L + 40 * ease_out(L / 2), 0.0, 1.0, 0.07), (s.hero2, 820 + 6 * L - 70 * (1 - ease_out(L / 2.5)), 0.3, 1.0, 0.06)):
            spr = hero.get((L * k * 3.2 + ph) % 1.0)
            sh = s.shadow.resize((int(spr.width * 0.8), 48), Image.BILINEAR)
            put(base, sh, x + spr.width * 0.1, H - 40)
            put(base, spr, x, H - spr.height + (40 if hero is s.hero1 else 125) + 6 * math.sin(L * 2.2 + ph))
        # light shafts + dust
        ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        for i in range(5):
            x = 760 + i * 150 + 20 * math.sin(L * 0.5 + i)
            d.polygon([(x, 0), (x + 90, 0), (x - 260, H), (x - 420, H)], fill=(255, 240, 190, 20))
        base.alpha_composite(ov.filter(ImageFilter.GaussianBlur(10)))
        for i in range(36):
            mx = (i * 211 + L * 20 * (1 + i % 3)) % W; my = (i * 97 - L * 10) % H
            glow(base, mx, my, 3, (255, 240, 200), 0.5, 1.0)
        for i in range(5):
            bird(base, (L * 70 + i * 160) % (W + 200) - 100, 120 + i * 24 + 10 * math.sin(L * 2 + i), 7, L * 9 + i)
        # location tag
        ta = sstep(70.6, 71.4, t) * (1 - sstep(74.6, 75.4, t))
        if ta > 0:
            ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
            d.rectangle([60, 56, 64, 128], fill=(255, 214, 130, int(255 * ta)))
            d.text((82 + 2, 58 + 2), 'HELIKE', font=s.tagf, fill=(20, 12, 8, int(170 * ta)))
            d.text((82, 58), 'HELIKE', font=s.tagf, fill=(255, 244, 214, int(255 * ta)))
            d.text((82, 98), 'Achaea · Northern Peloponnese', font=s.tagf2, fill=(255, 232, 190, int(235 * ta)))
            base.alpha_composite(ov)
        return base

# ===================================================================== SCENE 8
def poseidon(cv, cx, by, S):
    def P(x, y): return (cx + x * S, by - y * S)
    ml, mm, md = (246, 242, 232), (216, 210, 198), (158, 150, 140)
    # pedestal
    for i, (w_, h0, h1) in enumerate([(190, 0, 24), (166, 24, 48)]):
        cv.poly([P(-w_, h0), P(w_, h0), P(w_, h1), P(-w_, h1)], shade(mm, 0.95 - 0.06 * i) + (255,))
        cv.poly([P(-w_, h1), P(w_, h1), P(w_ - 6, h1 + 3), P(-w_ + 6, h1 + 3)], shade(ml, 1.0) + (255,))
    cv.grad_poly([P(-130, 48), P(130, 48), P(130, 190), P(-130, 190)], ml, md, by - 190 * S, by - 48 * S, hshade=0.55)
    for k in range(-2, 3):   # relief on pedestal
        cv.rect(*P(k * 46 - 10, 150), *P(k * 46 + 10, 84), shade(mm, 0.82) + (255,))
    cv.poly([P(-146, 190), P(146, 190), P(140, 206), P(-140, 206)], shade(ml, 1.02) + (255,))
    g = 206
    # drapery
    hip = g + 230
    pts = [P(-58, hip), P(58, hip), P(80, g + 24), P(74, g), P(-74, g), P(-82, g + 26)]
    cv.grad_poly(pts, ml, mm, by - hip * S, by - g * S, hshade=0.6)
    for k in range(-5, 6):
        cv.line([P(k * 11, hip - 10), P(k * 13, g + 6)], md + (130,), 3 * S)
    cv.poly([P(-58, hip), P(58, hip), P(40, hip - 36), P(-40, hip - 24)], shade(mm, 0.9) + (255,))
    cv.poly([P(-58, hip - 12), P(70, hip - 34), P(84, hip - 100), P(30, hip - 140), P(10, hip - 60)], shade(mm, 0.78) + (255,))  # sash
    for fx in (-40, -22, 0, 22, 40):
        cv.ellipse(*P(fx - 12, g + 8), *P(fx + 12, g - 8), shade(mm, 0.7) + (255,))
    # torso
    sh = hip + 170
    cv.grad_poly([P(-66, sh), P(66, sh), P(50, hip + 4), P(-50, hip + 4)], ml, mm, by - sh * S, by - hip * S, hshade=0.7)
    cv.line([P(0, sh - 14), P(0, hip + 10)], md + (160,), 3 * S)
    for yy in (sh - 44, sh - 84, sh - 120):
        cv.line([P(-44, yy), P(-6, yy - 8)], md + (150,), 3 * S); cv.line([P(44, yy), P(6, yy - 8)], md + (150,), 3 * S)
    cv.ellipse(*P(-66, sh + 14), *P(-38, sh - 24), ml + (255,)); cv.ellipse(*P(38, sh + 14), *P(66, sh - 24), mm + (255,))
    # arms (viewer-left arm raised to the trident)
    hx = -128
    cv.line([P(-62, sh - 6), P(-98, sh - 80), P(hx, sh - 40)], mm + (255,), 28 * S)
    cv.line([P(-62, sh - 6), P(-98, sh - 80)], ml + (255,), 14 * S)
    cv.circle(*P(hx, sh - 40), 15 * S, ml + (255,))
    cv.line([P(62, sh - 6), P(88, sh - 100), P(70, sh - 170)], md + (255,), 26 * S)
    cv.line([P(62, sh - 6), P(88, sh - 100)], mm + (255,), 13 * S)
    # head
    hc = (0, sh + 54)
    cv.rect(*P(-14, sh + 6), *P(14, sh + 28), md + (255,))
    cv.ellipse(*P(-30, hc[1] + 40), *P(30, hc[1] - 38), ml + (255,))
    for a in range(0, 360, 36):
        r = math.radians(a)
        if 20 < a < 160 or True:
            cv.circle(*P(math.cos(r) * 33, hc[1] + 20 + math.sin(r) * 34), 11 * S, shade(mm, 0.94) + (255,))
    cv.ellipse(*P(-28, hc[1] + 34), *P(28, hc[1] - 36), ml + (255,))
    cv.poly([P(-30, hc[1] + 6), P(-24, hc[1] - 30), P(0, hc[1] - 72), P(24, hc[1] - 30), P(30, hc[1] + 6), P(24, hc[1] - 4), P(0, hc[1] - 14), P(-24, hc[1] - 4)], mm + (255,))
    cv.poly([P(-28, hc[1] - 6), P(28, hc[1] - 6), P(24, hc[1] - 40), P(10, hc[1] - 70), P(0, hc[1] - 80), P(-10, hc[1] - 70), P(-24, hc[1] - 40)], shade(mm, 0.82) + (255,))
    for k in range(-2, 3):  # beard curls
        cv.circle(*P(k * 11, hc[1] - 36 - (2 - abs(k)) * 6), 13 * S, shade(mm, 0.9) + (255,))
    cv.poly([P(-6, hc[1] - 6), P(6, hc[1] - 6), P(0, hc[1] - 30)], shade(ml, 0.92) + (255,))
    cv.line([P(-20, hc[1] + 12), P(-6, hc[1] + 10)], md + (255,), 3 * S); cv.line([P(6, hc[1] + 10), P(20, hc[1] + 12)], md + (255,), 3 * S)
    cv.ellipse(*P(-18, hc[1] + 6), *P(-8, hc[1] + 2), (90, 84, 80, 255)); cv.ellipse(*P(8, hc[1] + 6), *P(18, hc[1] + 2), (90, 84, 80, 255))
    # crown
    cv.rect(*P(-30, hc[1] + 38), *P(30, hc[1] + 26), (214, 176, 84, 255))
    for k in range(-2, 3):
        cv.poly([P(k * 12 - 6, hc[1] + 38), P(k * 12 + 6, hc[1] + 38), P(k * 12, hc[1] + 62 - abs(k) * 6)], (230, 196, 100, 255))
    # trident
    gold, gold2 = (214, 176, 84), (255, 232, 150)
    top = sh + 250
    cv.line([P(hx, g), P(hx, top)], gold + (255,), 9 * S)
    cv.line([P(hx - 2, g), P(hx - 2, top)], gold2 + (255,), 3 * S)
    cv.circle(*P(hx, sh - 40), 11 * S, ml + (255,))
    for tx_ in (-1, 0, 1):
        pass
    cv.poly([P(hx - 7, top), P(hx + 7, top), P(hx, top + 100)], gold + (255,))
    for sgn in (-1, 1):
        cv.line([P(hx, top - 6), P(hx + sgn * 40, top + 8), P(hx + sgn * 44, top + 70)], gold + (255,), 8 * S)
        cv.poly([P(hx + sgn * 44 - 8, top + 70), P(hx + sgn * 44 + 8, top + 70), P(hx + sgn * 44, top + 112)], gold + (255,))
    cv.ellipse(*P(hx - 12, top + 4), *P(hx + 12, top - 12), gold2 + (255,))
    return P(hx, top + 60), P(0, sh + 54)

class Scene8:
    start, end = 79.8, 97.6
    WL, WH = 2300, 864
    def __init__(s):
        rnd = random.Random(8); WL, WH = s.WL, s.WH
        s.sky = vgrad_img(WL, WH, [(0, (36, 96, 206)), (0.45, (92, 156, 232)), (0.75, (190, 220, 242)), (1, (236, 230, 208))])
        s.cl = clouds(WL, 440, 81, 10, (255, 255, 255), (186, 204, 232), 235, 1.25)
        cv = Canvas(WL, WH, 2)
        X = np.arange(WL)
        far = ridge(WL, 470, 40, 21) - 90 * np.exp(-((X - 1100) / 500.0) ** 2)
        fill_ridge(cv, far, (110, 140, 176), (190, 206, 214), 600, rim=(236, 240, 244))
        sea = vgrad_img(WL, 100, [(0, (150, 206, 226)), (1, (46, 130, 180))])
        cv.im.alpha_composite(sea.resize((WL * 2, 200)), (0, 548 * 2 + 0))
        for i in range(260):
            x = rnd.uniform(900, WL); y = rnd.uniform(556, 640); k = (y - 548) / 92
            cv.line([(x, y), (x + 14 + 40 * k, y)], (255, 255, 255, 110), 1 + k * 2)
        near = ridge(WL, 540, 22, 23) + 110 * np.clip((X - 1050) / 380.0, 0, 1)
        fill_ridge(cv, near, (74, 120, 90), (176, 184, 130), 650, rim=(200, 214, 156))
        s.far = paint_tex(cv.image(), 0.04, 5)
        cv = Canvas(WL, WH, 2)
        cv.grad_poly([(0, 650), (WL, 650), (WL, WH), (0, WH)], (226, 208, 170), (166, 138, 104), 650, WH)
        for i in range(20):
            u = i / 20; y = 650 + (WH - 650) * u ** 1.5
            cv.line([(0, y), (WL, y)], (140, 110, 80, 70), 1 + 2 * u)
        for k in range(-30, 40):
            cv.line([(1150 + k * 20, 650), (1150 + k * 110, WH)], (140, 110, 80, 45), 1.5)
        for x, h_ in [(120, 220), (1010, 260), (1330, 180), (2230, 240)]: cypress(cv, x, 660, h_, h_ * 0.16)
        for x in (60, 1260, 2100): tree(cv, x, 666, 120, (74, 116, 70))
        temple_front(cv, 590, 668, 8, 270, 36, 62, steps=4)
        s.gtrident, s.ghead = poseidon(cv, 1710, 722, 0.7)
        s.main = paint_tex(cv.image(), 0.04, 6)
        s.rays = [(rnd.uniform(0, math.tau), rnd.uniform(0.5, 1)) for _ in range(12)]
        # cracks
        s.cracks = []
        for a in (-1, 1, -1, 1, 0):
            pts = [(1710 + a * 20, 706)]; x, y = pts[0]
            for i in range(24):
                x += (a if a else rnd.choice([-1, 1])) * rnd.uniform(26, 60); y += rnd.uniform(-8, 20)
                y = clamp(y, 700, 850); pts.append((x, y))
            s.cracks.append(pts)
        s.rock = [(rnd.uniform(0, 1), rnd.uniform(0, 1), rnd.uniform(0, 1)) for _ in range(70)]
    def render(s, t):
        WL, WH = s.WL, s.WH
        L = t - 79.8
        # camera
        z1 = lerp(1.5, 1.0, ease_out(L / 3.0))
        cx = 640; cy = 600
        if t < 82.4: cx, cy, z = 640, lerp(640, 520, sstep(79.8, 82.4, t)), z1
        else:
            p = sstep(82.2, 87.0, t); cx = lerp(640, 1560, p); cy = lerp(520, 470, p); z = 1.0
        if t > 87.0:
            p = sstep(87.0, 88.6, t); z = lerp(1.0, 0.95, p); cx = 1560 + 20 * p; cy = lerp(470, 400, p)
        if t > 88.6:
            q = sstep(88.6, 93.0, t); z = lerp(0.95, 1.1, q); cx = lerp(1580, 1600, q); cy = lerp(400, 380, q)
        if t > 93.0:
            p = sstep(93.0, 97.6, t); z = lerp(1.1, 1.45, p); cx = lerp(1600, 1630, p); cy = lerp(380, 290, p)
        amp = 0 if t < 89.8 else lerp(0.0, 3.0, sstep(89.8, 92.6, t)) + lerp(0, 8, sstep(92.6, 97.6, t))
        dx, dy = noise_s(t, amp)
        cx += dx; cy += dy
        base = Image.new('RGBA', (WL if False else W, H), (0, 0, 0, 255))
        def Lr(img, k=1.0, op=1.0):
            zz = z * (1 + 0.0 * k)
            put(base, view(img, zz, cx * k + WL / 2 * (1 - k), cy * k + 432 * (1 - k)), 0, 0, op)
        Lr(s.sky, 0.15)
        Lr(tile_scroll(s.cl, t * 6), 0.25)
        Lr(s.far, 0.6)
        # wave aura
        rise = sstep(88.6, 90.4, t) * (1 - sstep(92.0, 93.6, t))
        ov = Image.new('RGBA', (WL, WH), (0, 0, 0, 0))
        if rise > 0.01:
            d = ImageDraw.Draw(ov, 'RGBA')
            for layer, (colr, off, spd) in enumerate([((24, 90, 160, 120), 0, 3.0), ((60, 150, 210, 150), 22, -2.5), ((170, 226, 246, 120), 46, 4.0)]):
                pts = []
                for x in range(1200, 2300, 10):
                    bump = max(0.0, math.sin(math.pi * (x - 1200) / 1100.0)) ** 0.7
                    y = 646 - rise * (300 * bump + 70 * math.sin(x / 80.0 - t * spd) + 36 * math.sin(x / 33.0 + t * spd * 1.3)) * bump + off * (1 - bump * 0.5)
                    pts.append((x, y))
                d.polygon(pts + [(2300, 650), (1200, 650)], fill=colr)
                d.line(pts, fill=(235, 252, 255, int(200 * rise)), width=5)
                if layer == 2:
                    for (x, y), k in zip(pts[::5], range(1000)):
                        d.ellipse([x - 8, y - 8 - (k % 3) * 3, x + 8, y + 5], fill=(255, 255, 255, int(190 * rise)))
            for i in range(18):   # swirl arcs
                r = 60 + i * 24 + 10 * math.sin(t * 2 + i)
                d.arc([1625 - r, 430 - r, 1625 + r, 430 + r], 200 + i * 20 + t * 40, 260 + i * 20 + t * 40, fill=(210, 245, 255, int(130 * rise)), width=3)
            Lr(ov.filter(ImageFilter.GaussianBlur(1.2)), 1.0)
        Lr(s.main, 1.0)
        # cracks + trident glow in world space
        ov = Image.new('RGBA', (WL, WH), (0, 0, 0, 0)); d = ImageDraw.Draw(ov, 'RGBA')
        cg = sstep(91.4, 96.6, t)
        if cg > 0:
            for pts in s.cracks:
                n = max(2, int(len(pts) * cg))
                d.line(pts[:n], fill=(255, 214, 120, int(150 * sstep(93.5, 95.5, t))), width=9, joint='curve')
                d.line(pts[:n], fill=(30, 20, 16, 255), width=5, joint='curve')
        tg = sstep(87.0, 87.7, t) * 0.5 + sstep(92.5, 95.0, t) * 0.5
        tx, ty = s.gtrident
        pulse = 0.75 + 0.25 * math.sin(t * 6)
        if tg > 0:
            add_light(ov, tx, ty, int(150 + 150 * tg), (255, 220, 120), tg * pulse)
            for i in range(10):
                a = i * 0.628 + t * 1.5; r = 40 + 60 * tg
                glow(ov, tx + math.cos(a) * r, ty + math.sin(a) * r, 6, (255, 240, 180), tg * 0.9, 1.2)
        # falling debris from the temple
        if t > 90.6:
            dd = ImageDraw.Draw(ov, 'RGBA')
            for a, b, c in s.rock:
                u = ((t - 90.6) * (0.5 + c) + b * 3) % 3.0
                x = 380 + a * 480 if c < 0.6 else 1500 + a * 500
                y = 330 + u * 220 + 100 * b
                if y < 700:
                    r = 2 + 4 * c
                    dd.polygon([(x, y - r), (x + r, y), (x, y + r), (x - r, y - r * 0.3)], fill=(190, 170, 140, int(255 * clamp(amp / 4 + 0.3))))
        Lr(ov, 1.0)
        # god rays on statue reveal
        if 87.0 < t < 97.6:
            ra = sstep(87.0, 88.0, t) * (1 - 0.4 * sstep(92, 94, t))
            ov2 = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov2)
            for ang, k in s.rays:
                a = -1.1 + (ang / math.tau) * 2.2
                px, py = 520, -40
                d.polygon([(px, py), (px + math.sin(a - 0.03) * 1800, py + math.cos(a - 0.03) * 1800), (px + math.sin(a + 0.03) * 1800, py + math.cos(a + 0.03) * 1800)], fill=(255, 240, 190, int(22 * k * ra)))
            base.alpha_composite(ov2)
        # mood shift to dusty/unsettling
        mood = sstep(91.0, 97.5, t)
        base.alpha_composite(Image.new('RGBA', (W, H), (150, 96, 60, int(95 * mood))))
        flash = max(0.0, 1 - abs(t - 93.3) * 3) * 0.0
        return base

# ===================================================================== SCENE 9
def col_sprite(h, w, stone, broken=0.0):
    S = int(h * 2 + 40)
    cv = Canvas(S, S, 1)
    column(cv, S / 2, S / 2, h, w, stone, broken=broken, seed=int(h))
    return cv.im

def rock_sprite(sz, rnd):
    cv = Canvas(sz * 2, sz * 2, 3)
    pts = [(sz + math.cos(a) * sz * rnd.uniform(0.6, 1.0), sz + math.sin(a) * sz * rnd.uniform(0.5, 0.95)) for a in np.linspace(0, math.tau, 8, endpoint=False)]
    col = rnd.choice([(196, 176, 146), (170, 150, 124), (214, 196, 164)])
    cv.poly(pts, col + (255,)); cv.poly([pts[0], pts[1], pts[2], (sz, sz)], shade(col, 1.15) + (255,)); cv.poly([pts[4], pts[5], pts[6], (sz, sz)], shade(col, 0.7) + (255,))
    return cv.image()

class Scene9:
    start, end = 97.6, 108.4
    WL, WH = 1536, 864
    def __init__(s):
        rnd = random.Random(9); WL, WH = s.WL, s.WH; s.rnd = rnd
        s.sky = vgrad_img(WL, WH, [(0, (74, 52, 56)), (0.4, (186, 118, 80)), (0.65, (240, 170, 100)), (1, (196, 140, 94))])
        put(s.sky, blob(500, (255, 200, 120), 255, 2.2), 1000 - 500, 320 - 500, 0.7)
        s.smoke = clouds(WL, 520, 91, 11, (112, 84, 70), (60, 46, 42), 215, 1.6)
        cv = Canvas(WL, WH, 2)
        far = ridge(WL, 470, 40, 31)
        fill_ridge(cv, far, (110, 78, 78), (170, 112, 92), 600, rim=(240, 170, 110))
        s.hills = paint_tex(cv.image(), 0.04, 1)
        cv = Canvas(WL, WH, 2)
        for i in range(36):
            x = rnd.uniform(0, WL); house(cv, x, 600 + rnd.uniform(-8, 10), rnd.uniform(28, 60), rnd.uniform(30, 56), rnd.choice([(190, 160, 130), (176, 146, 118), (204, 176, 142)]), (130, 84, 66), i, rnd.random() < 0.5)
        s.city = paint_tex(cv.image(), 0.05, 2)
        cv = Canvas(WL, WH, 2)
        cv.grad_poly([(0, 610), (WL, 610), (WL, WH), (0, WH)], (156, 122, 90), (84, 64, 52), 610, WH)
        for i in range(18):
            u = i / 18; y = 610 + (WH - 610) * u ** 1.5; cv.line([(0, y), (WL, y)], (80, 60, 48, 70), 1 + 2 * u)
        s.ground = paint_tex(cv.image(), 0.07, 3)
        # standing temple: columns as sprites
        s.cols = []
        xs = [380 + i * 100 for i in range(8)]
        for i, x in enumerate(xs):
            tf = [100.2, 104.0, 103.3, 103.7, 104.3, 104.9, 103.0, 104.6][i]
            s.cols.append(dict(x=x, base=650, h=300, w=42, tf=tf, dir=1 if i % 2 else -1, spr=col_sprite(300, 42, (226, 204, 170)), tilt=rnd.uniform(0.7, 1.3)))
        for i, x in enumerate((1230, 1310, 1390)):
            s.cols.append(dict(x=x, base=640, h=240, w=36, tf=[101.2, 101.9, 102.4][i], dir=1, spr=col_sprite(240, 36, (216, 190, 156), 0.0), tilt=1.0))
        # roof (entablature + pediment) sprite
        cv = Canvas(860, 260, 2)
        x0, x1 = 20, 840
        cv.rect(x0, 130, x1, 160, shade(STONE, 0.9) + (255,)); cv.rect(x0, 100, x1, 130, shade(STONE, 1.0) + (255,))
        for i in range(30): cv.rect(x0 + 8 + i * 27, 106, x0 + 20 + i * 27, 126, shade(STONE, 0.55) + (255,))
        cv.poly([(x0 - 10, 100), (x1 + 10, 100), ((x0 + x1) / 2, 8)], shade(STONE, 1.06) + (255,))
        cv.poly([(x0 + 40, 94), (x1 - 40, 94), ((x0 + x1) / 2, 34)], shade(STONE, 0.6) + (255,))
        cv.poly([(x0 - 10, 100), (x1 + 10, 100), (x1 + 10, 92), ((x0 + x1) / 2, 0), (x0 - 10, 92)], (190, 112, 80, 255))
        s.roof = cv.image()
        # roof pivot hangs above columns at y=650-300-?; it falls at t=105.0
        # runners
        mk = lambda tun, **kw: Walker(n=10, h=200, tunic=tun, run=1.0, arms_up=0.5, **kw)
        s.run = []
        for i, tun in enumerate([(246, 240, 226), (120, 140, 176), (214, 150, 110), (100, 150, 110), (226, 190, 100), (176, 70, 64)]):
            w = mk(tun, skin=SKINS[i % 4], female=(i in (2,)), beard=(i % 2 == 0), mood='scared')
            s.run.append((w, mirrored(w)))
        s.crowd = []
        for i in range(20):
            y = rnd.uniform(640, 790); hgt = lerp(120, 270, (y - 620) / 190)
            s.crowd.append((rnd.uniform(0, WL), y, hgt, rnd.choice([-1, 1]) * rnd.uniform(110, 190) * hgt / 200, rnd.randrange(6), rnd.uniform(0, 1)))
        s.hero = Walker(n=10, h=640, tunic=(116, 124, 150), cloak=(86, 70, 60), skin=SKINS[1], beard=True, hair=(34, 26, 22), mood='scared', run=1.0, arms_up=0.9, facing=-1)
        s.hero2 = Walker(n=10, h=520, tunic=(214, 190, 140), skin=SKINS[0], mood='scared', run=1.0, arms_up=0.7, hair=(60, 40, 30), beard=True)
        s.rocks = [rock_sprite(rnd.randint(8, 22), rnd) for _ in range(8)]
        s.chunks = []
        for i in range(190):
            c = rnd.choice(s.cols)
            ts = c['tf'] + rnd.uniform(0.15, 0.7)
            s.chunks.append((ts, c['x'] + rnd.uniform(-30, 30), c['base'] - rnd.uniform(40, 300), rnd.uniform(-220, 220), rnd.uniform(-420, -60), rnd.uniform(-8, 8), rnd.randrange(8)))
        for i in range(90):
            ts = rnd.uniform(98, 104); s.chunks.append((ts, rnd.uniform(200, 1400), rnd.uniform(0, 80), rnd.uniform(-30, 30), rnd.uniform(40, 120), rnd.uniform(-5, 5), rnd.randrange(8)))
        s.shadow = shadow_ell(260, 36, 120)
        s.cracks = []
        for a in range(7):
            pts = [(rnd.uniform(300, 1200), 640 + rnd.uniform(0, 40))]; x, y = pts[0]
            for k in range(14):
                x += rnd.uniform(-60, 60); y += rnd.uniform(8, 26); pts.append((x, y))
            s.cracks.append(pts)
        s.dust = [(rnd.choice(s.cols)['x'] + rnd.uniform(-60, 60), rnd.uniform(560, 680), rnd.uniform(0, 1)) for _ in range(40)]

    def render(s, t):
        WL, WH = s.WL, s.WH
        L = t - 97.6
        amp = np.interp(t, [97.6, 99.5, 102.6, 102.9, 106.0, 108.4], [0.0, 1.8, 4.0, 14.0, 16.0, 6.0])
        dx, dy = noise_s(t, amp)
        base = Image.new('RGBA', (W, H), (0, 0, 0, 255))
        zoom = 0.9 + 0.03 * L / 10.8
        def Lr(img, k=1.0, ox=0, oy=0):
            put(base, view(img, zoom, WL / 2 + dx * k * 0.8 + ox, 432 + dy * k * 0.8 + oy), 0, 0)
        Lr(s.sky, 0.1)
        Lr(tile_scroll(s.smoke, t * 10), 0.3, 0, -90)
        Lr(s.hills, 0.4)
        # city sinks/crumbles
        sink = sstep(101.5, 106.5, t)
        city = s.city
        if sink > 0:
            c2 = Image.new('RGBA', city.size, (0, 0, 0, 0)); c2.paste(city, (0, int(110 * sink)))
            city = fade(c2, 1 - 0.6 * sink)
        Lr(city, 0.6)
        Lr(s.ground, 1.0)
        ov = Image.new('RGBA', (WL, WH), (0, 0, 0, 0))
        # ground cracks
        cg = sstep(102.7, 104.5, t)
        if cg > 0:
            d = ImageDraw.Draw(ov, 'RGBA')
            for pts in s.cracks:
                n = max(2, int(len(pts) * cg)); d.line(pts[:n], fill=(24, 16, 14, 255), width=6, joint='curve')
        # standing / falling columns
        shk = amp * 0.5
        for c in sorted(s.cols, key=lambda c: c['base']):
            S_ = c['spr'].width
            tf = c['tf']
            px, py = c['x'], c['base']
            if t < tf:
                ang = c['dir'] * math.radians(clamp((t - (tf - 2.5)) / 2.5) ** 2 * 3.0 * c['tilt']) + math.radians(0.4 * math.sin(t * 30 + px) * min(1, amp / 5))
            else:
                u = t - tf
                ang = c['dir'] * math.radians(3 + 87 * clamp(u / 1.0) ** 2 * (1 if u < 1 else 1)) * 1.0
                if u > 1.0: ang += c['dir'] * math.radians(-6 * math.exp(-(u - 1) * 6) * math.sin((u - 1) * 18))
            spr = c['spr'].rotate(-math.degrees(ang), resample=Image.BILINEAR)
            alpha = 1.0 if t < tf + 1.8 else 1 - sstep(tf + 1.8, tf + 3.0, t) * 0.0
            put(ov, spr, px - S_ / 2, py - S_ / 2, alpha)
        # roof
        tr = 105.0
        if t < tr:
            ry = 650 - 300 - 6 + (2 * math.sin(t * 40) * min(1, amp / 6))
            put(ov, s.roof, 380 - 30, ry - 130)
        else:
            u = t - tr
            ry = 650 - 306 + 4.5 * 380 * min(u, 0.62) ** 2 * 1.0
            ang = 8 * clamp(u / 0.6)
            spr = s.roof.rotate(ang, resample=Image.BILINEAR, expand=True)
            put(ov, spr, 350 - (spr.width - 860) / 2, min(ry, 640 - 80) - 130, 1 - sstep(tr + 1.5, tr + 3.0, t))
        Lr(ov, 1.0)
        # rubble piles
        # chunks/debris (screen-space-ish in world)
        ov = Image.new('RGBA', (WL, WH), (0, 0, 0, 0))
        for ts, x0, y0, vx, vy, rot, k in s.chunks:
            u = t - ts
            if u < 0 or u > 2.6: continue
            x = x0 + vx * u; y = y0 + vy * u + 900 * u * u * 0.5
            if y > 700: y = 700 - abs(vy) * 0.1 * math.sin(u * 8) ** 2; x = x0 + vx * (ts and min(u, 1.0))
            spr = s.rocks[k].rotate(rot * u * 60, resample=Image.BILINEAR)
            put(ov, spr, x - spr.width / 2, y - spr.height / 2, 1 - sstep(1.8, 2.6, u))
        # dust clouds
        for x, y, ph in s.dust:
            tf0 = 102.6 + ph * 2.6
            u = t - tf0
            if u > 0:
                r = 50 + 110 * clamp(u / 2.5)
                glow(ov, x + 60 * u * (ph - 0.5) * 2, y - 90 * clamp(u / 3), int(r), (206, 176, 138), 0.55 * (1 - sstep(2.0, 4.5, u)), 1.0)
        for c in s.cols:
            u = t - c['tf']
            if 0 < u < 3.2:
                glow(ov, c['x'] + c['dir'] * 120 * clamp(u), c['base'] - 20, int(70 + 110 * clamp(u / 1.5)), (206, 178, 142), 0.8 * (1 - sstep(1.0, 3.2, u)), 1.0)
        if 105.0 < t < 108.4:
            u = t - 105.0
            glow(ov, 640, 560, int(160 + 260 * clamp(u / 1.6)), (214, 186, 150), 0.8 * (1 - sstep(1.6, 3.4, u)), 1.0)
        Lr(ov, 1.0)
        # panicked crowd (screen-space layer)
        ov = Image.new('RGBA', (WL, WH), (0, 0, 0, 0))
        panic = sstep(98.2, 99.6, t)
        for x0, y, hgt, sp, kind, ph in sorted(s.crowd, key=lambda c: c[1]):
            sp2 = sp * panic * (0.3 + 0.7 * sstep(98.0, 101.0, t))
            x = (x0 + sp2 * (t - 97.6) + (sp > 0) * 0) % (WL + 300) - 150
            w, wm = s.run[kind]
            spr = (w if sp > 0 else wm).get(((t - 97.6) * 1.4 * (0.4 + panic) + ph) % 1.0)
            sz = (int(spr.width * hgt / 200), int(spr.height * hgt / 200))
            spr = spr.resize(sz, Image.BILINEAR)
            sh = s.shadow.resize((int(hgt * 0.7), int(hgt * 0.08)), Image.BILINEAR)
            put(ov, sh, x - sh.width / 2, y - sh.height / 2)
            put(ov, spr, x - sz[0] / 2, y - sz[1] * 0.97 + 3 * abs(math.sin(t * 9 + ph * 7)))
        Lr(ov, 1.0)
        # foreground heroes
        shx, shy = noise_s(t * 1.7, amp * 0.9)
        for hero, x, ph in ((s.hero, 800 + 26 * L ** 0.5 * 0 + 20 * math.sin(t * 3), 0.0), (s.hero2, -140 + 40 * ease_out(L / 3), 0.5)):
            spr = hero.get(((t - 97.6) * 1.1 * (0.2 + panic) + ph) % 1.0)
            shd = s.shadow.resize((int(spr.width * 0.9), 56), Image.BILINEAR)
            put(base, shd, x + spr.width * 0.05 + shx, H - 54)
            put(base, spr, x + shx, H - spr.height + 54 + shy + 8 * abs(math.sin(t * 6 + ph * 5)))
        # haze
        dust_a = sstep(99.5, 104.5, t) * 0.55
        base.alpha_composite(Image.new('RGBA', (W, H), (190, 142, 98, int(150 * dust_a))))
        # flashes
        fl = max(0.0, 1 - abs(t - 102.9) * 4) * 0.5 + max(0.0, 1 - abs(t - 105.15) * 4) * 0.35
        if fl > 0: base.alpha_composite(Image.new('RGBA', (W, H), (255, 244, 220, int(255 * fl))))
        # the sea arrives
        if t > 105.6:
            u = ease_out((t - 105.6) / 2.0)
            yf = H + 60 - (H + 140) * u
            ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov, 'RGBA')
            for off, colr in (((-62, (150, 214, 226, 255)), (-34, (36, 108, 140, 255)), (0, (14, 60, 96, 255)))[i] for i in range(3)):
                pts = [(x, yf + off * (1 - 0.5 * u) + 24 * math.sin(x / 70.0 + t * 4) + 14 * math.sin(x / 29.0 - t * 6)) for x in range(-20, W + 40, 16)]
                d.polygon(pts + [(W + 40, H + 80), (-20, H + 80)], fill=colr)
            top = [(x, yf - 62 * (1 - 0.5 * u) + 24 * math.sin(x / 70.0 + t * 4) + 14 * math.sin(x / 29.0 - t * 6)) for x in range(-20, W + 40, 16)]
            for i, (x, y) in enumerate(top):
                if i % 2 == 0: d.ellipse([x - 14, y - 12, x + 14, y + 6], fill=(255, 255, 255, 235))
            for i in range(50):
                sx = (i * 131) % W; sy_ = yf - 80 - ((t * 120 + i * 37) % 160)
                d.ellipse([sx - 3, sy_ - 3, sx + 3, sy_ + 3], fill=(255, 255, 255, 190))
            base.alpha_composite(ov)
        # dark fade-out
        fo = sstep(107.55, 108.35, t)
        if fo > 0: base.alpha_composite(Image.new('RGBA', (W, H), (4, 8, 14, int(255 * fo))))
        return base
