"""Scenes 24-29"""
import math, random
from gfx import *
from art import *
from scenes1 import Scene


def rot(pts, cx, cy, a):
    c, s = math.cos(a), math.sin(a)
    return [(cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c) for x, y in pts]


def glove(g, x, y, s=1.0, col='#8d9298'):
    g.poly([(x - 40 * s, y + 60 * s), (x - 52 * s, y - 10 * s), (x - 30 * s, y - 40 * s), (x + 30 * s, y - 36 * s), (x + 48 * s, y + 10 * s), (x + 30 * s, y + 60 * s)], fill=col, ol=OL, w=3 * s)
    for i in range(4):
        fx = x - 26 * s + i * 17 * s
        g.rect(fx - 8 * s, y - 62 * s + abs(i - 1.5) * 8 * s, fx + 8 * s, y - 22 * s, fill=col, ol=OL, w=2.4 * s, r=8 * s)
    g.ell(x - 48 * s, y + 6 * s, 11 * s, 22 * s, fill=col, ol=OL, w=2.4 * s)
    g.line([(x - 30 * s, y + 20 * s), (x + 20 * s, y + 24 * s)], shade(col, 0.7), 2 * s)


def amphora(g, cx, cy, s=1.0, a=0.0):
    """cy = centre of the body"""
    def T(pts):
        return rot([(cx + x * s, cy + y * s) for x, y in pts], cx, cy, a)
    body = [(-24, -150), (-26, -120), (-56, -96), (-86, -40), (-88, 20), (-70, 80), (-36, 128), (-26, 150), (-40, 160), (40, 160), (26, 150), (36, 128),
            (70, 80), (88, 20), (86, -40), (56, -96), (26, -120), (24, -150), (44, -158), (-44, -158)]
    # handles
    for k in (-1, 1):
        h = [(k * 26, -140), (k * 82, -150), (k * 100, -112), (k * 74, -92), (k * 66, -100), (k * 84, -118), (k * 76, -134), (k * 30, -128)]
        g.poly(T(h), fill='#b85a22', ol=OL, w=3 * s)
    g.poly(T(body), fill='#cf6f2c', ol=OL, w=3.4 * s)
    g.polyA(T([(30, -100), (60, -80), (88, 20), (70, 80), (36, 128), (24, 150), (40, 150), (60, 100), (80, 40)]), (60, 20, 0), 0.22)
    # black bands
    g.poly(T([(-26, -120), (26, -120), (56, -96), (-56, -96)]), fill='#1c1210')
    g.poly(T([(-34, 124), (34, 124), (28, 146), (-28, 146)]), fill='#1c1210')
    # figure panel
    g.poly(T([(-70, -70), (70, -70), (78, 60), (-78, 60)]), fill='#e0a060', ol='#1c1210', w=2.4 * s)
    for k, fx in enumerate((-36, 36)):
        px, py = fx, -8
        g.ell(*rot([(cx + px * s, cy + (py - 38) * s)], cx, cy, a)[0], 9 * s, fill='#1c1210')
        g.poly(T([(px - 10, py - 28), (px + 10, py - 28), (px + 14, py + 8), (px - 14, py + 8)]), fill='#1c1210')
        g.line(T([(px - 6, py + 8), (px - 14, py + 44)]), '#1c1210', 6 * s, True)
        g.line(T([(px + 6, py + 8), (px + 12 * (1 if k else -1), py + 44)]), '#1c1210', 6 * s, True)
        g.line(T([(px - 12, py - 18), (px - 34 + k * 40, py - 36)]), '#1c1210', 5 * s, True)
        g.line(T([(px + 12, py - 18), (px + 34 + k * 40 - 40, py - 2)]), '#1c1210', 5 * s, True)
    g.line(T([(-70, -70), (70, -70)]), '#1c1210', 4 * s)
    g.line(T([(-78, 60), (78, 60)]), '#1c1210', 4 * s)
    g.polyA(T([(-60, -60), (-46, -60), (-52, 50), (-66, 50)]), (255, 230, 190), 0.25)


def pin(g, x, y, col='#d8342a'):
    g.ell(x + 2, y + 3, 7, fill=(60, 40, 20))
    g.ell(x, y, 7, fill=col, ol=OL, w=1.4)
    g.ell(x - 2, y - 2, 2, fill=(255, 220, 210))


# ======================================================== 24
class S24(Scene):
    num, title = 24, 'Something is Buried'
    warm = 0.7

    def build(self):
        g = G()
        g.paste_rgb(texture(W, H, 60, 4, '#5c3a22', '#8d5e38', 4), 0, 0)
        rng = random.Random(5)
        for i in range(120):
            x, y = rng.uniform(0, 1280), rng.uniform(0, 720)
            g.ell(x, y, rng.uniform(3, 14), rng.uniform(2, 8), fill=shade('#7a5030', rng.uniform(0.6, 1.3)))
        # rocks
        for (x, y, r) in ((90, 520, 70), (220, 660, 55), (1180, 140, 80), (1100, 640, 60)):
            g.ell(x, y, r, r * 0.7, fill='#9a8a78', ol=(40, 28, 20), w=3)
            g.ellA(x + r * 0.2, y + r * 0.2, r * 0.7, r * 0.45, (30, 20, 10), 0.25)
        # shard
        sh = [(-210, -60), (-160, -140), (-40, -170), (100, -150), (210, -90), (230, 20), (150, 110), (20, 150), (-110, 120), (-200, 40)]
        cx, cy, a = 660, 400, -0.35
        S_ = rot([(cx + x, cy + y) for x, y in sh], cx, cy, a)
        g.polyA([(x + 12, y + 14) for x, y in S_], (10, 5, 0), 0.5)
        g.poly(S_, fill='#c8662c', ol=OL, w=4)
        g.polyA(rot([(cx + x, cy + y) for x, y in [(-200, 40), (-110, 120), (20, 150), (150, 110), (230, 20), (100, 60), (-60, 80)]], cx, cy, a), (60, 20, 0), 0.25)
        # pattern bands
        for k, (y0, y1) in enumerate(((-120, -90), (70, 100))):
            pts = [(cx - 190, cy + y0), (cx + 200, cy + y0)]
            g.poly(rot([(cx - 190, cy + y0), (cx + 200, cy + y0 - 4), (cx + 200, cy + y1), (cx - 190, cy + y1)], cx, cy, a), fill='#1c1210')
            xs = cx - 170
            while xs < cx + 190:
                seg_ = rot([(xs, cy + y0 + 6), (xs + 18, cy + y0 + 6), (xs + 18, cy + y1 - 6), (xs + 6, cy + y1 - 6), (xs + 6, cy + y0 + 16)], cx, cy, a)
                g.line(seg_, '#e49b58', 3)
                xs += 30
        # frieze figures
        for k in range(3):
            fx = cx - 120 + k * 110
            body = rot([(fx - 12, cy - 60), (fx + 12, cy - 60), (fx + 16, cy + 10), (fx - 16, cy + 10)], cx, cy, a)
            g.poly(body, fill='#1c1210')
            hd = rot([(fx, cy - 78)], cx, cy, a)[0]
            g.ell(hd[0], hd[1], 11, fill='#1c1210')
            for dx, dy in ((-22, -50), (22, -30)):
                g.line(rot([(fx, cy - 50), (fx + dx, cy + dy)], cx, cy, a), '#1c1210', 6, True)
            g.line(rot([(fx - 6, cy + 10), (fx - 14 + k * 8, cy + 58)], cx, cy, a), '#1c1210', 7, True)
            g.line(rot([(fx + 6, cy + 10), (fx + 14 + k * 5, cy + 58)], cx, cy, a), '#1c1210', 7, True)
        self.bg = g.im
        self.shard_c = (cx, cy)
        # dirt blobs
        rng = random.Random(12)
        self.blobs = []
        for i in range(260):
            bx, by = rng.uniform(430, 900), rng.uniform(230, 560)
            self.blobs.append((bx, by, rng.uniform(14, 34), rng.uniform(0.7, 1.15), rng.uniform(-1, 1)))

    def draw(self, t):
        g = G(self.bg)
        r = ease(seg(t, 0.2, 3.3))
        bx0 = 410 + r * 520
        brush_y = 330 + 170 * (0.5 + 0.5 * math.sin(t * 6.3)) + 20 * math.sin(t * 2)
        bxp = bx0 + 18 * math.sin(t * 6.3 + 1)
        for (x, y, rr, sh, k) in self.blobs:
            d = bxp - x
            if d < -rr:
                a = 1.0
                ox = oy = 0
            elif d < 90:
                p = clamp((d + rr) / (90 + rr))
                a = 1 - p
                ox, oy = p * 70 * k, -p * 50 - p * p * 40
            else:
                continue
            col = shade('#7a5030', sh)
            if a > 0.97:
                g.ell(x, y, rr, rr * 0.75, fill=col)
                g.ellA(x - rr * .2, y - rr * .2, rr * .55, rr * .35, (170, 120, 80), 0.35)
            elif a > 0.02:
                g.ellA(x + ox, y + oy, rr, rr * 0.75, col, a)
        # brush + glove (angled down-right)
        px, py = bxp, brush_y
        g.line([(px, py), (px - 34, py - 40)], '#d8c27a', 36, True)
        g.line([(px - 4, py - 4), (px - 26, py - 30)], '#f0e0a0', 10, True)
        g.poly([(px - 22, py - 54), (px - 54, py - 28), (px - 64, py - 40), (px - 36, py - 68)], fill='#a8aeb4', ol=OL, w=2.4)
        g.line([(px - 56, py - 54), (px - 176, py - 176)], OL, 17, True)
        g.line([(px - 56, py - 54), (px - 176, py - 176)], '#9a6a38', 12, True)
        glove(g, px - 175, py - 190, 1.2)
        for i in range(10):
            ph = (t * 2 + i * 0.1) % 1
            g.ellA(px + 10 + ph * 70, py + 20 - ph * 40 - math.sin(i) * 20, 6 + ph * 14, 5 + ph * 10, (190, 140, 96), 0.5 * (1 - ph))
        # ruler
        g.rect(300, 640, 1000, 676, fill='#e8e0c4', ol=OL, w=2)
        for i in range(0, 71):
            g.line([(300 + i * 10, 640), (300 + i * 10, 640 + (22 if i % 5 == 0 else 12))], OL, 1.4)
        g.text(1010, 658, 'cm', font('DejaVuSansMono-Bold.ttf', 16), '#e8e0c4', 'lm')
        # reveal flash
        fl = seg(t, 3.0, 3.6) * (1 - seg(t, 3.6, 4.0))
        g.glow(660, 400, 340, (255, 200, 120), 0.4 * fl)
        zoom = 1.18 - 0.14 * ease(t / self.dur)
        return g.im, (680, 420, zoom)


# ======================================================== 25
def kneeler(g, x, y, s, t):
    skin = SK['w3']
    sw = math.sin(t * 7)
    g.shadowblob(x, y + 2, 70 * s, 8 * s, 0.35)
    limb(g, (x - 8 * s, y - 40 * s), (x + 22 * s, y - 4 * s), 17 * s, '#756a54')
    limb(g, (x + 22 * s, y - 4 * s), (x - 44 * s, y - 2 * s), 14 * s, '#756a54')
    g.ell(x - 48 * s, y - 3 * s, 12 * s, 6 * s, fill=(40, 30, 24), ol=OL, w=1.5)
    sh = (x + 24 * s, y - 84 * s)
    hip = (x - 12 * s, y - 42 * s)
    limb(g, hip, sh, 34 * s, '#a49a80')
    g.line([hip, ((hip[0] + sh[0]) / 2 + 4, (hip[1] + sh[1]) / 2 + 3)], shade('#a49a80', 0.8), 6 * s)
    hand = (x + 88 * s + sw * 7 * s, y - 10 * s + abs(sw) * -5 * s)
    limb(g, sh, ((sh[0] + hand[0]) / 2 - 6 * s, y - 40 * s), 12 * s, '#a49a80')
    limb(g, ((sh[0] + hand[0]) / 2 - 6 * s, y - 40 * s), hand, 10 * s, SK['w3'])
    g.ell(hand[0], hand[1], 6 * s, fill=skin, ol=OL, w=1.4)
    g.poly([(hand[0], hand[1] + 2), (hand[0] + 24 * s, hand[1] + 9 * s), (hand[0] + 4 * s, hand[1] + 13 * s)], fill='#c8ccd0', ol=OL, w=1.4)
    hd = (x + 52 * s, y - 102 * s)
    g.ell(hd[0], hd[1], 20 * s, 22 * s, fill=skin, ol=OL, w=2)
    g.poly([(hd[0] - 12 * s, hd[1] + 6 * s), (hd[0] + 14 * s, hd[1] + 20 * s), (hd[0] + 4 * s, hd[1] + 24 * s), (hd[0] - 12 * s, hd[1] + 18 * s)], fill='#3a2a22')
    g.ell(hd[0] + 10 * s, hd[1] - 2 * s, 2.4 * s, fill=(30, 20, 16))
    g.ell(hd[0] + 2 * s, hd[1] - 20 * s, 34 * s, 7 * s, fill='#d8c07a', ol=OL, w=2)
    g.poly([(hd[0] - 18 * s, hd[1] - 20 * s), (hd[0] - 14 * s, hd[1] - 36 * s), (hd[0] + 14 * s, hd[1] - 36 * s), (hd[0] + 20 * s, hd[1] - 20 * s)], fill='#d8c07a', ol=OL, w=2)
    g.line([(hd[0] - 17 * s, hd[1] - 24 * s), (hd[0] + 18 * s, hd[1] - 24 * s)], '#7a5a30', 3 * s)
    return hand


class S25(Scene):
    num, title = 25, 'The First Discovery'
    warm = 0.8

    def build(self):
        g = G()
        g.gradrect(0, 0, 1280, 420, [(0, '#5c9ede'), (0.6, '#cfe4ee'), (1, '#f8e8c4')])
        g.glow(300, 120, 220, (255, 224, 160), 0.4)
        mountains(g, 330, ['#9ab0c8', '#7e9aa8', '#6a8a6a'], [70, 60, 40], seed=31)
        # distant ruin temple
        temple(g, 930, 335, 170, 90, col='#e3d7b6', n=5, steps=2)
        for x in (780, 1130, 1220):
            g.line([(x, 338), (x, 318)], '#5a3a22', 4)
            g.ell(x, 310, 18, 16, fill='#6a8a40', ol='#3c5524', w=2)
        # ground
        g.poly([(-10, 330), (1290, 335), (1290, 730), (-10, 730)], fill='#b98c58')
        g.polyA([(-10, 480), (1290, 470), (1290, 730), (-10, 730)], (80, 50, 20), 0.2)
        rng = random.Random(9)
        for i in range(120):
            x, y = rng.uniform(0, 1280), rng.uniform(345, 720)
            g.ell(x, y, rng.uniform(2, 8), rng.uniform(1.5, 4), fill=shade('#c7996a', rng.uniform(0.7, 1.2)))
        # trench
        g.poly([(250, 430), (1080, 420), (1180, 700), (170, 710)], fill='#8a5e38', ol=(60, 36, 20), w=4)
        g.polyA([(250, 430), (1080, 420), (1060, 470), (270, 480)], (30, 15, 5), 0.3)
        stonewall(g, 330, 470, 980, 530, '#a8987a', 17, rows=2)
        stonewall(g, 300, 600, 700, 670, '#a8987a', 19, rows=2)
        g.poly([(700, 540), (1020, 535), (1090, 640), (760, 650)], fill='#7a5230')
        stonewall(g, 800, 560, 1050, 620, '#a8987a', 23, rows=2)
        # string grid
        for x in (330, 560, 860):
            g.line([(x, 350), (x + 10, 700)], (240, 240, 230), 1.5)
        g.line([(200, 560), (1200, 555)], (240, 240, 230), 1.5)
        self.bg = g.im

    def draw(self, t):
        g = G(self.bg)
        clouds(g, t, seed=9, y0=50, y1=190, n=3, speed=5, a=0.7)
        # background workers
        figure(g, 640 + 40 * math.sin(t * 0.6), 400, 0.55, t, hat='brim', hatc='#d9c27a', shirt='#6c8aa8', pants='#555', anim='walk', ph=0, face=1)
        figure(g, 1030, 392, 0.55, t, hat='hard', vest='#f06a1a', shirt='#778', pants='#445', anim='dig', ph=1, face=-1, tool='shovel')
        figure(g, 890, 440, 0.62, t, hat='brim', hatc='#d9c27a', shirt='#8a9a74', pants='#555a68', anim='idle', ph=2, face=-1)
        # kneeler
        hand = kneeler(g, 470, 640, 2.0, t)
        # glint at tool tip
        a = ease(seg(t, 1.4, 2.0))
        if a > 0:
            gx, gy = 700, 620
            sz = 40 * a * (0.8 + 0.2 * math.sin(t * 10))
            g.glow(gx, gy, 80 * a, (255, 240, 180), 0.8)
            g.line([(gx - sz, gy), (gx + sz, gy)], (255, 255, 240), 3, True)
            g.line([(gx, gy - sz), (gx, gy + sz)], (255, 255, 240), 3, True)
            g.line([(gx - sz * .6, gy - sz * .6), (gx + sz * .6, gy + sz * .6)], (255, 255, 240), 2, True)
            g.line([(gx + sz * .6, gy - sz * .6), (gx - sz * .6, gy + sz * .6)], (255, 255, 240), 2, True)
            f = font('DejaVuSerif-Bold.ttf', 64)
            g.text(gx + 4, gy - 110 + 4, '!', f, OL, 'mm')
            g.text(gx, gy - 110, '!', f, (255, 232, 130), 'mm')
        dust(g, t, 4, 30, 200, 400, 1100, 700, (255, 235, 190), speed=10, size=1.8)
        zoom = 1.0 + 0.25 * ease(t / self.dur)
        return g.im, (lerp(640, 560, t / self.dur), lerp(380, 520, t / self.dur), zoom)


# ======================================================== 26
def ghost(g, x, y, s, t, a, ph=0.0):
    c = (255, 224, 150)
    sw = math.sin(t * 5 + ph)
    g.ellA(x, y - 108 * s, 11 * s, 12 * s, c, a)
    g.polyA([(x - 14 * s, y - 94 * s), (x + 14 * s, y - 94 * s), (x + 12 * s, y - 52 * s), (x - 12 * s, y - 52 * s)], c, a)
    for k in (-1, 1):
        g.polyA([(x + k * 3 * s - 5 * s, y - 52 * s), (x + k * 3 * s + 5 * s, y - 52 * s), (x + k * 3 * s + sw * k * 14 * s + 5 * s, y), (x + k * 3 * s + sw * k * 14 * s - 5 * s, y)], c, a)
        g.polyA([(x + k * 12 * s - 4 * s, y - 92 * s), (x + k * 12 * s + 4 * s, y - 92 * s), (x + k * 14 * s - sw * k * 8 * s + 4 * s, y - 56 * s), (x + k * 14 * s - sw * k * 8 * s - 4 * s, y - 56 * s)], c, a)


def pop(t, t0, dur=0.7):
    """returns (scale, yoffset) bouncy entrance"""
    p = seg(t, t0, t0 + dur)
    if p <= 0:
        return 0, 0
    s = 1 - (1 - p) ** 3
    bounce = math.sin(p * math.pi * 2.2) * (1 - p) * 0.12
    return s + bounce, (1 - p) * -220


class S26(Scene):
    num, title = 26, 'The Clues'
    warm = 0.9

    def build(self):
        g = G()
        g.paste_rgb(texture(W, H, 80, 2, '#2e2824', '#4a4038', 3), 0, 0)
        stonewall(g, -20, 0, 1300, 640, '#6e6252', 14, rows=17)
        g.rectA(0, 0, 1280, 720, (10, 6, 4), 0.55)
        g.poly([(-10, 640), (1290, 630), (1290, 730), (-10, 730)], fill='#2a2018')
        g.polyA([(-10, 640), (1290, 630), (1290, 660), (-10, 666)], (255, 190, 100), 0.1)
        self.bg = g.im

    def draw(self, t):
        g = G(self.bg)
        # lantern light sweep
        lx = 640 + 520 * math.sin(t * 0.55)
        g.glow(lx, 330, 420, (255, 190, 110), 0.55 * (1 - 0.6 * seg(t, 2.5, 4)))
        base_glow = ease(seg(t, 2.6, 5.5))
        g.glow(640, 380, 560, (255, 180, 90), 0.5 * base_glow)
        # walls (stones)
        s_, dy = pop(t, 4.1)
        if s_ > 0:
            for (x, y, w, h, c) in ((690, 520, 190, 120, '#d6cdb8'), (810, 590, 160, 90, '#c7bda4'), (760, 440, 120, 80, '#d9d1be')):
                xs = x + (1 - s_) * 0
                g.rect(xs - w / 2 * s_, y + dy - h * s_ / 2 + (0), xs + w / 2 * s_, y + dy + h * s_ / 2, fill=c, ol=shade(c, 0.5), w=3, r=10)
                g.line([(xs - w * .3 * s_, y + dy - h * .15 * s_), (xs + w * .1 * s_, y + dy - h * .12 * s_), (xs + w * .2 * s_, y + dy + h * .2 * s_)], shade(c, 0.6), 2)
                g.polyA([(xs - w / 2 * s_, y + dy + h * s_ * .1), (xs + w / 2 * s_, y + dy + h * s_ * .1), (xs + w / 2 * s_, y + dy + h * s_ / 2), (xs - w / 2 * s_, y + dy + h * s_ / 2)], (60, 40, 20), 0.2)
            label(g, 'WALLS', 760, 360, ease(seg(t, 4.5, 5.0)) * (1 - ease(seg(t, 8.8, 9.3))), size=22, seed=4)
        # amphora
        s_, dy = pop(t, 2.9)
        if s_ > 0:
            g.shadowblob(380, 640, 90 * s_, 12 * s_, 0.4)
            amphora(g, 380, 470 + dy, 1.35 * s_, a=math.sin(t * 1.4) * 0.03)
            label(g, 'POTTERY', 380, 255, ease(seg(t, 3.3, 3.8)) * (1 - ease(seg(t, 8.8, 9.3))), size=22, seed=7)
        # column
        s_, dy = pop(t, 5.4)
        if s_ > 0:
            g.shadowblob(1020, 640, 100 * s_, 12 * s_, 0.4)
            column(g, 1020, 640 + dy, 340 * s_, 96 * s_, '#e8dfc6')
            # ionic volutes
            ytop = 640 + dy - 340 * s_
            for k in (-1, 1):
                g.ell(1020 + k * 62 * s_, ytop + 20 * s_, 20 * s_, fill='#ede4cb', ol='#8a7c5c', w=3)
                g.ell(1020 + k * 62 * s_, ytop + 20 * s_, 9 * s_, ol='#8a7c5c', w=2)
            label(g, 'BUILDINGS', 1020, 200, ease(seg(t, 5.8, 6.3)) * (1 - ease(seg(t, 8.8, 9.3))), size=22, seed=9)
        # ghost people (evidence that people lived here)
        ga = ease(seg(t, 8.6, 9.8)) * 0.55 * (1 - ease(seg(t, 10.8, 11.4)))
        if ga > 0:
            for i in range(5):
                gx = (i * 260 + t * 50) % 1500 - 100
                ghost(g, gx, 600 + (i % 2) * 20, 1.5, t, ga, i)
            label(g, 'PEOPLE LIVED HERE', 640, 90, ease(seg(t, 9.2, 9.8)) * (1 - ease(seg(t, 10.8, 11.4))), size=30, seed=12)
        dust(g, t, 8, 50, 0, 0, 1280, 700, (255, 220, 160), speed=8, size=1.8, drift=(1, -0.3))
        zoom = 1.0 + 0.08 * (t / self.dur)
        return g.im, (640, 380, zoom)


# ======================================================== 27
class S27(Scene):
    num, title = 27, 'The Catch'
    warm = 0.6

    BANDS = [('Byzantine', 'c. 330 – 1453 AD', 150, 300, '#a97c4c'),
             ('Roman', '146 BC – 330 AD', 300, 470, '#8d6642'),
             ('Classical', 'c. 480 – 323 BC', 470, 720, '#6f4e34')]

    def edge(self, x, y0, k):
        return y0 + 7 * math.sin(x * 0.015 + k * 2.3) + 4 * math.sin(x * 0.04 + k)

    def build(self):
        g = G()
        g.gradrect(0, 0, 1280, 200, [(0, '#4a8ed4'), (1, '#e6f0f0')])
        mountains(g, 150, ['#8fa8c0', '#6f9080'], [60, 45], seed=41, bottom=300)
        # bands
        for k, (n, sub, y0, y1, c) in enumerate(self.BANDS):
            pts = [(x, self.edge(x, y0, k)) for x in range(-20, 1300, 20)]
            g.poly(pts + [(1300, 740), (-20, 740)], fill=c)
            g.line(pts, shade(c, 0.55), 3)
        # pebbles / texture
        rng = random.Random(3)
        for i in range(260):
            x, y = rng.uniform(0, 1280), rng.uniform(160, 720)
            k = 0 if y < 300 else (1 if y < 470 else 2)
            c = self.BANDS[k][4]
            g.ell(x, y, rng.uniform(2, 7), rng.uniform(1.5, 4), fill=shade(c, rng.uniform(0.7, 1.25)))
        self.bg = g.im

    def draw(self, t):
        g = G(self.bg)
        clouds(g, t, seed=3, y0=30, y1=120, n=3, speed=4, a=0.7)
        # grass top
        pts = [(x, self.edge(x, 150, 0)) for x in range(-20, 1300, 20)]
        g.line(pts, '#6a9e3a', 7)
        # Byzantine: chapel
        by = 292
        g.rect(230, by - 100, 360, by, fill='#d8c8a4', ol='#6a583a', w=3)
        g.poly([(220, by - 100), (370, by - 100), (295, by - 140)], fill='#b25a3a', ol='#6a3a24', w=3)
        g.ell(295, by - 120, 36, 34, fill='#c4623e', ol='#6a3a24', w=3)
        g.rect(290, by - 70, 300, by - 20, fill='#4a3424')
        g.line([(295, by - 170), (295, by - 148)], '#f0e0a0', 4)
        g.line([(286, by - 162), (304, by - 162)], '#f0e0a0', 4)
        g.rect(250, by - 80, 266, by - 56, fill='#3a2a1c', r=8)
        g.rect(324, by - 80, 340, by - 56, fill='#3a2a1c', r=8)
        for (x0, w) in ((420, 110), (580, 90), (900, 130)):
            g.rect(x0, by - 62, x0 + w, by, fill='#c9b690', ol='#6a583a', w=3)
            g.poly([(x0 - 8, by - 62), (x0 + w + 8, by - 62), (x0 + w / 2, by - 92)], fill='#a8553a', ol='#6a3a24', w=3)
        # Roman: arches
        ry = 462
        arch_ruin(g, 200, ry, 230, 130, '#b9764a', 1)
        arch_ruin(g, 470, ry, 190, 110, '#b9764a', 2)
        arch_ruin(g, 740, ry, 230, 125, '#b9764a', 3)
        column(g, 1050, ry, 120, 30, '#d4b08a', fluted=False)
        column(g, 1110, ry, 100, 28, '#d4b08a', fluted=False, broken=0.2)
        g.rect(980, ry - 10, 1180, ry, fill='#a8683a', ol='#5a3a20', w=2)
        # mosaic floor
        mosaic_pattern(g, 190, ry - 14, 960, ry - 4, '#a05a30', '#e8c070')
        # Classical: temple remains
        cy_ = 700
        for i, x in enumerate((180, 260, 340, 420, 500, 580, 660)):
            column(g, x, cy_, 150 - (i % 3) * 30, 38, '#d8cdae', broken=[0, 0.3, 0.5, 0, 0.4, 0.2, 0.6][i])
        g.rect(160, cy_ - 190, 420, cy_ - 160, fill='#d8cdae', ol='#8a7c5c', w=2)
        g.poly([(150, cy_ - 190), (430, cy_ - 190), (290, cy_ - 240)], fill='#e0d6ba', ol='#8a7c5c', w=2)
        for (x, y, w, h) in ((760, 640, 140, 60), (940, 660, 110, 44), (1090, 610, 90, 70)):
            g.rect(x, y, x + w, y + h, fill='#cdbf9e', ol='#8a7c5c', w=2, r=6)
        # highlight bands in sync with narration
        hb = [seg(t, 5.0, 5.4) * (1 - seg(t, 7.0, 7.4)),   # all multiple periods
              ]
        for k, (n, sub, y0, y1, c) in enumerate(self.BANDS):
            # scanning highlight during "multiple periods"
            ts = 5.2 + k * 0.7
            a = ease(seg(t, ts, ts + 0.3)) * (1 - ease(seg(t, ts + 0.7, ts + 1.1)))
            g.rectA(0, y0 + 6, 1280, min(720, y1), (255, 230, 150), 0.22 * a)
        # classical emphasis
        ca = ease(seg(t, 8.8, 9.2)) * (1 - ease(seg(t, 11.0, 11.5)))
        g.rectA(0, 476, 1280, 720, (255, 220, 120), 0.2 * ca * (0.7 + 0.3 * math.sin(t * 6)))
        ra = ease(seg(t, 11.7, 12.1)) * (1 - ease(seg(t, 14.4, 14.9)))
        g.rectA(0, 150, 1280, 470, (255, 220, 120), 0.18 * ra * (0.7 + 0.3 * math.sin(t * 6)))
        # tags
        tag_t = [12.2, 12.0, 8.6]
        names = [0, 1, 2]
        for k, (n, sub, y0, y1, c) in enumerate(self.BANDS):
            a = ease(seg(t, tag_t[k], tag_t[k] + 0.5))
            if a > 0:
                x = 1130 + (1 - eo(a)) * 120
                yy = (y0 + min(y1, 700)) / 2 - 10 if k < 2 else 590
                yy = [225, 395, 560][k]
                g.line([(x - 90, yy), (x - 150, yy + 20)], (255, 235, 190), 2.6)
                g.ell(x - 150, yy + 20, 6, fill=(255, 235, 190))
                label(g, n.upper(), x, yy, a, size=24, sub=sub, seed=2 + k)
        # intro "but there was a catch": pulsing warning
        wa = ease(seg(t, 0.8, 1.4)) * (1 - ease(seg(t, 4.6, 5.0)))
        if wa > 0:
            qmark(g, 1120, 120, 0.55 * wa, t)
        dust(g, t, 2, 50, 0, 160, 1280, 720, (255, 225, 170), speed=6, size=1.6, drift=(0.5, -0.5))
        # camera: start top, drift downward then pull out
        p = ease(seg(t, 0, 5))
        q = ease(seg(t, 5, 9.5))
        z = lerp(lerp(1.5, 1.4, p), 1.0, q)
        cy = lerp(lerp(230, 330, p), 360, q)
        cx = lerp(lerp(500, 440, p), 640, q)
        return g.im, (cx, cy, z)


# ======================================================== 28
class S28(Scene):
    num, title = 28, 'Not Every Ruin is Helike'
    warm = 1.0

    def build(self):
        g = G()
        g.gradrect(0, 0, 1280, 720, [(0, '#3a2a20'), (1, '#1e1612')])
        stonewall(g, 0, 0, 1280, 420, '#5a4a3c', 6, rows=12)
        g.rectA(0, 0, 1280, 720, (15, 8, 4), 0.5)
        # shelves with pots
        for y in (170, 330):
            g.rect(760, y, 1280, y + 12, fill='#6a4a2c', ol=OL, w=2)
            for i in range(6):
                x = 800 + i * 76
                h = 40 + (i * 13) % 30
                g.poly([(x - 10, y), (x - 20, y - h * .5), (x - 8, y - h), (x + 8, y - h), (x + 20, y - h * .5), (x + 10, y)], fill=shade('#b86a38', 0.7 + (i % 3) * 0.1), ol=OL, w=1.6)
        self.bg = g.im

    def draw(self, t):
        g = G(self.bg)
        flick = 0.85 + 0.15 * math.sin(t * 9) * math.sin(t * 3.1)
        g.glow(1000, 60, 520, (255, 190, 100), 0.5 * flick)
        # lamp
        g.line([(1000, 0), (1000, 40)], OL, 3)
        g.poly([(970, 100), (1030, 100), (1015, 50), (985, 50)], fill='#d9a43a', ol=OL, w=2.4)
        # table
        g.poly([(0, 560), (1280, 540), (1280, 730), (0, 730)], fill='#5a3c24')
        g.polyA([(0, 560), (1280, 540), (1280, 580), (0, 590)], (255, 200, 120), 0.15)
        # map on table
        mp = [(700, 440), (1180, 420), (1250, 640), (660, 660)]
        g.poly(mp, fill='#e6d3a2', ol='#6a4a28', w=3)
        g.line([(790, 500), (870, 470), (960, 520), (1040, 480), (1140, 500)], '#5a8cb0', 3)
        for k in range(3):
            g.line([(780 + k * 6, 530 + k * 14), (870, 504 + k * 14), (950, 550 + k * 14), (1040, 514 + k * 14), (1150, 530 + k * 14)], '#a9c4d0', 1.5)
        for i in range(8):
            g.line([(760 + i * 54, 590), (770 + i * 54, 620)], '#a98d62', 1.5)
        # candidate sites: pins with ruin icons
        sites = [(830, 560), (1010, 590), (1150, 575)]
        which = int(t / 2.4) % 3
        for i, (x, y) in enumerate(sites):
            if i == which:
                g.glow(x, y, 80, (255, 230, 120), 0.5)
            pin(g, x, y - 12, '#d8342a' if i == which else '#7a7a82')
        wx, wy = sites[which]
        g.ellA(wx, wy - 12, 34 + 4 * math.sin(t * 5), 34 + 4 * math.sin(t * 5), (255, 220, 100), 0.18)
        label(g, 'HELIKE?', wx, wy - 80, 1.0, size=18, seed=6 + which)
        # bearded archaeologist
        cyc = (t % 4.8)
        to_tab = 1 - ease(seg(cyc, 1.8, 2.3)) + ease(seg(cyc, 4.3, 4.8))
        to_tab = clamp(to_tab)
        turn = lerp(0.9, 0.2, to_tab)
        look = (lerp(0.9, 0.2, to_tab), lerp(0.4, 0.9, to_tab))
        bust(g, 400, 250, 1.55, 'steven', t, turn=turn * 0.7, talk=0.0, look=look, shirt='#8d836a', nod=2 * math.sin(t * 1.4) + 6 * to_tab, brow=0.6 - 0.8 * (1 - to_tab))
        # tablet in hands
        ang = 0.25 * math.sin(t * 1.1) + 0.2
        cx, cy = 470, 600
        tab = rot([(cx - 85, cy - 110), (cx + 80, cy - 100), (cx + 95, cy + 100), (cx - 70, cy + 108)], cx, cy, ang)
        g.polyA([(x + 10, y + 12) for x, y in tab], (10, 5, 0), 0.4)
        g.poly(tab, fill='#c06a30', ol=OL, w=4)
        for r_ in range(5):
            y0 = -80 + r_ * 36
            g.line(rot([(cx - 60, cy + y0), (cx + 70, cy + y0 + 6)], cx, cy, ang), '#2a1610', 6)
            xs = -60
            while xs < 60:
                g.line(rot([(cx + xs, cy + y0 + 12), (cx + xs + 10, cy + y0 + 22)], cx, cy, ang), '#e8a868', 2)
                xs += 18
        g.polyA(tab[:1] + [tab[1], rot([(cx + 60, cy - 60)], cx, cy, ang)[0]], (255, 230, 180), 0.2)
        for hx_, hy_ in ((cx - 100, cy + 10), (cx + 115, cy + 30)):
            p = rot([(hx_, hy_)], cx, cy, ang)[0]
            g.ell(p[0], p[1], 22, 28, fill=SK['steven'], ol=OL, w=3)
            g.ell(p[0] + (10 if hx_ < cx else -10), p[1] - 6, 10, 20, fill=SK['steven'], ol=OL, w=2.4)
        # thought bubble
        a = ease(seg(t, 2.5, 3.2))
        if a:
            for i, (r, dx, dy) in enumerate(((8, 640, 250), (13, 670, 220), (20, 710, 185))):
                g.ellA(dx, dy, r * a, r * a, (255, 250, 235), 0.9)
            g.ellA(770, 120, 90 * a, 56 * a, (255, 250, 235), 0.92)
            if a > 0.8:
                g.text(770, 120, 'Helike?', font('Lora.ttf', 34), (60, 40, 24), 'mm')
        zoom = 1.0 + 0.08 * (t / self.dur)
        return g.im, (640, 360, zoom)


# ======================================================== 29
def thumb(g, x, y, w, h, kind, t=0, tilt=0.0):
    g.polyA([(x - w / 2 + 6, y - h / 2 + 8), (x + w / 2 + 6, y - h / 2 + 8), (x + w / 2 + 6, y + h / 2 + 8), (x - w / 2 + 6, y + h / 2 + 8)], (0, 0, 0), 0.4)
    g.rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, fill='#f2ecd8', ol=(80, 60, 40), w=2)
    ix0, iy0, ix1, iy1 = x - w / 2 + 6, y - h / 2 + 6, x + w / 2 - 6, y + h / 2 - h * 0.2
    if kind == 'sea':
        g.gradrect(ix0, iy0, ix1, iy1, [(0, '#8cc8ee'), (0.5, '#3f9ad0'), (1, '#1a5f9a')])
        g.line([(ix0 + 4, (iy0 + iy1) / 2 + 6), (ix1 - 4, (iy0 + iy1) / 2 + 6)], '#e0f4ff', 2)
    elif kind == 'ruin':
        g.gradrect(ix0, iy0, ix1, iy1, [(0, '#f4c88a'), (1, '#d79a58')])
        for k in range(3):
            column(g, ix0 + 14 + k * (w - 40) / 2.5, iy1, (iy1 - iy0) * 0.7, 10, '#e8dcc0')
    elif kind == 'pot':
        g.gradrect(ix0, iy0, ix1, iy1, [(0, '#5a4030'), (1, '#8a5a3a')])
        g.ell((ix0 + ix1) / 2, (iy0 + iy1) / 2 + 2, (ix1 - ix0) * 0.22, (iy1 - iy0) * 0.38, fill='#cf6f2c', ol=OL, w=1.6)
    elif kind == 'dig':
        g.gradrect(ix0, iy0, ix1, iy1, [(0, '#a6d0ec'), (0.5, '#e8d4a8'), (1, '#a8774a')])
        g.rect(ix0 + 10, iy1 - 20, ix1 - 10, iy1, fill='#7a5230')
    elif kind == 'coast':
        g.gradrect(ix0, iy0, ix1, iy1, [(0, '#bfe0f0'), (1, '#6aa8d0')])
        g.poly([(ix0, iy1), (ix0, iy0 + 20), (ix1 - 20, iy1)], fill='#b9a070')
    else:
        g.gradrect(ix0, iy0, ix1, iy1, [(0, '#3a3a48'), (1, '#1a1a22')])
        g.ell((ix0 + ix1) / 2, (iy0 + iy1) / 2, 18, fill='#d8b84a', ol=OL, w=1.6)


class S29(Scene):
    num, title = 29, 'The Mystery Gets Bigger'
    warm = 0.8

    PINS = [(210, 220), (420, 150), (620, 250), (860, 170), (1040, 260), (300, 470), (520, 520), (760, 470), (980, 520), (640, 380)]
    LINKS = [(9, 2, 0.6), (9, 7, 1.0), (9, 6, 1.4), (2, 1, 1.8), (1, 0, 2.2), (2, 3, 2.6), (3, 4, 3.0), (7, 8, 3.4), (6, 5, 3.8), (5, 0, 4.2), (4, 8, 4.6)]

    def build(self):
        g = G()
        g.paste_rgb(texture(W, H, 70, 14, '#8a5a34', '#b57e4a', 4), 0, 0)
        rng = random.Random(7)
        for i in range(400):
            x, y = rng.uniform(0, 1280), rng.uniform(0, 720)
            g.ell(x, y, rng.uniform(1, 3), fill=shade('#a8723e', rng.uniform(0.6, 1.3)))
        g.rect(8, 8, 1272, 712, ol='#4a2c16', w=18)
        g.rect(22, 22, 1258, 698, ol='#2a180c', w=3)
        self.bg = g.im

    def draw(self, t):
        g = G(self.bg)
        # photos
        kinds = ['sea', 'ruin', 'pot', 'dig', 'coast', 'ruin', 'pot', 'sea', 'dig', 'coin']
        for i, (x, y) in enumerate(self.PINS):
            if i == 9:
                continue
            pa = ease(seg(t, 0.1 + i * 0.12, 0.5 + i * 0.12))
            if pa <= 0:
                continue
            thumb(g, x, y + (1 - eo(pa)) * -60, 150, 120, kinds[i], t)
        # central map
        mx, my = 640, 380
        g.polyA([(mx - 130 + 8, my - 100 + 10), (mx + 130 + 8, my - 100 + 10), (mx + 130 + 8, my + 100 + 10), (mx - 130 + 8, my + 100 + 10)], (0, 0, 0), 0.4)
        g.rect(mx - 130, my - 100, mx + 130, my + 100, fill='#e6d3a2', ol='#6a4a28', w=3)
        g.line([(mx - 100, my + 20), (mx - 40, my - 20), (mx + 30, my + 10), (mx + 100, my - 30)], '#5a8cb0', 3)
        for k in range(3):
            g.line([(mx - 100, my + 36 + k * 14), (mx - 40, my - 4 + k * 14), (mx + 30, my + 26 + k * 14), (mx + 100, my - 14 + k * 14)], '#a9c4d0', 1.4)
        g.text(mx + 70, my + 60, '✕', font('DejaVuSans-Bold.ttf', 28), '#b3422c', 'mm')
        g.text(mx - 70, my + 60, '✕', font('DejaVuSans-Bold.ttf', 28), '#b3422c', 'mm')
        # sticky notes
        for (x, y, c, txt, ts) in ((120, 360, '#f4e46a', '?', 2.0), (1170, 420, '#f09a8a', '?!', 3.4), (880, 360, '#9ad4f0', '??', 4.4)):
            a = ease(seg(t, ts, ts + 0.4))
            if a > 0:
                g.polyA([(x - 40 + 5, y - 40 + 6), (x + 40 + 5, y - 40 + 6), (x + 40 + 5, y + 40 + 6), (x - 40 + 5, y + 40 + 6)], (0, 0, 0), 0.35 * a)
                g.rect(x - 40, y - 40 - (1 - a) * 30, x + 40, y + 40 - (1 - a) * 30, fill=c, ol=shade(c, 0.6), w=2)
                g.text(x, y - (1 - a) * 30, txt, font('Lora.ttf', 44), (70, 40, 20), 'mm')
        # strings
        for (a_, b_, ts) in self.LINKS:
            p = ease(seg(t, ts, ts + 0.45))
            if p <= 0:
                continue
            x0, y0 = self.PINS[a_]
            x1, y1 = self.PINS[b_]
            sag = 10 * math.sin(t * 2 + a_)
            xm, ym = (x0 + x1) / 2, (y0 + y1) / 2 + 14 + sag * 0.3
            pts = []
            for k in range(11):
                u = k / 10 * p
                px = (1 - u) ** 2 * x0 + 2 * u * (1 - u) * xm + u * u * x1
                py = (1 - u) ** 2 * y0 + 2 * u * (1 - u) * ym + u * u * y1
                pts.append((px, py))
            g.line([(x + 2, y + 3) for x, y in pts], (50, 20, 10), 3)
            g.line(pts, '#d42a24', 3)
        for i, (x, y) in enumerate(self.PINS):
            if i == 9 or t > 0.3 + i * 0.12:
                pin(g, x, y - 52 if i != 9 else y - 100)
        # silhouette man at right
        mx_, my_ = 1130, 520
        turn = math.sin(t * 0.9) * 6
        g.poly([(mx_ - 150, 740), (mx_ - 140, 620), (mx_ - 90, 578), (mx_ + 90, 578), (mx_ + 140, 620), (mx_ + 150, 740)], fill='#171c28', ol='#05070b', w=3)
        g.rect(mx_ - 18 + turn * .3, 540, mx_ + 18 + turn * .3, 586, fill='#241c1a')
        g.ell(mx_ + turn, 515, 46, 54, fill='#1c1818', ol='#05070b', w=3)
        g.poly([(mx_ - 48 + turn, 505), (mx_ - 30 + turn, 462), (mx_ + 30 + turn, 462), (mx_ + 48 + turn, 505), (mx_ + 30 + turn, 484), (mx_ - 30 + turn, 484)], fill='#0a0808')
        g.ell(mx_ - 34 + turn, 520, 6, 14, fill='#2a2422')
        # lamp glow flicker
        flick = 0.85 + 0.15 * math.sin(t * 8) * math.sin(t * 2.7)
        g.glow(640, 60, 560, (255, 200, 120), 0.35 * flick)
        # big ? appears at end
        a = ease(seg(t, 5.2, 6.0))
        if a > 0:
            qmark(g, 1020, 150, 0.9 * a, t)
        zoom = 1.0 + 0.12 * ease(t / self.dur)
        return g.im, (lerp(640, 760, t / self.dur), 380, zoom)
