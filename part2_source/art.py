"""Characters, scenery and ruin building blocks."""
import math, random
from gfx import *

SK = {'dora': '#d49a76', 'steven': '#dfae88', 'man': '#c68a63', 'w1': '#d9a67f', 'w2': '#b9825c',
      'w3': '#e2b490', 'kid': '#d9a67f'}
KHAKI = '#a89f84'


# ------------------------------------------------------------------ scenery
def ridge_pts(x0, x1, base, amp, seed, step=16):
    rng = random.Random(seed)
    f = [rng.uniform(0.004, 0.009), rng.uniform(0.012, 0.02), rng.uniform(0.03, 0.05)]
    p = [rng.uniform(0, 6) for _ in range(3)]
    pts = []
    x = x0
    while x <= x1 + step:
        y = base - amp * (0.55 * math.sin(x * f[0] + p[0]) + 0.3 * math.sin(x * f[1] + p[1]) + 0.15 * math.sin(x * f[2] + p[2]) + 0.6)
        pts.append((x, y))
        x += step
    return pts


def mountains(g, base, cols, amps, seed=1, x0=-40, x1=1320, bottom=None):
    bottom = bottom if bottom is not None else base + 200
    for i, (c, a) in enumerate(zip(cols, amps)):
        pts = ridge_pts(x0, x1, base - i * 14, a, seed + i * 7)
        g.poly(pts + [(x1 + 16, bottom), (x0, bottom)], fill=c)
        # light edge on ridge
        g.line(pts, mix(c, '#ffffff', 0.18), 1.6)


def clouds(g, t, seed=1, y0=60, y1=200, n=6, speed=6, col=(255, 255, 255), a=0.9):
    rng = random.Random(seed)
    for i in range(n):
        x = (rng.uniform(0, 1500) + t * speed * rng.uniform(0.6, 1.4)) % 1500 - 120
        y = rng.uniform(y0, y1)
        sc = rng.uniform(0.7, 1.5)
        for dx, dy, r in [(0, 0, 38), (34, -12, 34), (70, 0, 40), (30, 10, 36), (-30, 8, 28), (104, 8, 26)]:
            g.ellA(x + dx * sc, y + dy * sc, r * sc, r * 0.62 * sc, col, a)
        g.ellA(x + 36 * sc, y + 22 * sc, 80 * sc, 12 * sc, (200, 214, 232), a * 0.5)


def sea(g, y0, y1, t, top='#1f7fb0', bottom='#0c3a66', amp=2.5, lines=14, seed=2, sparkle=True, x0=-20, x1=1300):
    g.gradrect(x0, y0, x1, y1, [(0, top), (1, bottom)])
    rng = random.Random(seed)
    for i in range(lines):
        f = (i + 1) / lines
        y = y0 + (y1 - y0) * f ** 1.4
        ph = rng.uniform(0, 6.28)
        sp = rng.uniform(0.6, 1.4)
        pts = []
        for x in range(x0, x1 + 20, 24):
            pts.append((x, y + math.sin(x * 0.02 * (0.6 + f) + t * sp * 1.4 + ph) * amp * (0.4 + f)))
        g.line(pts, mix(top, '#ffffff', 0.35 - 0.2 * f), 1.2 + f * 1.6)
    if sparkle:
        for i in range(34):
            sx = (rng.uniform(0, 1300) + i * 3) % 1300
            sy = y0 + (y1 - y0) * rng.random() ** 1.5
            k = 0.5 + 0.5 * math.sin(t * 3 + i * 1.7)
            if k > 0.55:
                L = 5 + 7 * k
                g.line([(sx - L, sy), (sx + L, sy)], (255, 255, 235), 1.5)


def birds(g, t, seed=4, n=4, y0=60, y1=180, col=(40, 40, 50)):
    rng = random.Random(seed)
    for i in range(n):
        x = (rng.uniform(0, 1400) + t * rng.uniform(26, 44)) % 1400 - 60
        y = rng.uniform(y0, y1) + math.sin(t * 0.8 + i) * 6
        fl = math.sin(t * 7 + i * 2) * 5
        s = rng.uniform(0.8, 1.3)
        g.line([(x - 12 * s, y - fl), (x - 5 * s, y - 3 * s), (x, y), (x + 5 * s, y - 3 * s), (x + 12 * s, y - fl)], col, 2)


def dust(g, t, seed, n, x0, y0, x1, y1, col=(255, 235, 190), speed=10, size=2.2, drift=(1, -0.4)):
    rng = random.Random(seed)
    for i in range(n):
        bx, by = rng.uniform(x0, x1), rng.uniform(y0, y1)
        sp = rng.uniform(0.4, 1.2)
        x = x0 + (bx - x0 + t * speed * sp * drift[0]) % (x1 - x0)
        y = y0 + (by - y0 + t * speed * sp * drift[1]) % (y1 - y0)
        r = size * rng.uniform(0.5, 1.3) * (0.7 + 0.3 * math.sin(t * 2 + i))
        g.ell(x, y, r, r, fill=col)


def stonewall(g, x0, y0, x1, y1, base='#9c8c72', seed=5, rows=None, ol=True):
    rng = random.Random(seed)
    rows = rows or max(2, int((y1 - y0) / 34))
    rh = (y1 - y0) / rows
    for r in range(rows):
        x = x0 - rng.uniform(0, 40)
        y = y0 + r * rh
        while x < x1:
            w = rng.uniform(46, 110)
            c = shade(base, rng.uniform(0.82, 1.12))
            xa, xb = max(x0, x), min(x1, x + w - 2)
            if xb - xa > 3:
                g.rect(xa, y + 1, xb, y + rh - 1, fill=c, ol=shade(base, 0.55) if ol else None, w=1.5, r=3)
                g.line([(xa + 3, y + 4), (xb - 3, y + 4)], shade(c, 1.18), 1.5)
            x += w


def column(g, x, yb, h, w, col='#e6dcc2', fluted=True, broken=0.0, tilt=0):
    dark = shade(col, 0.72)
    top = yb - h * (1 - broken)
    # base
    g.rect(x - w * 0.78, yb - h * 0.04, x + w * 0.78, yb, fill=shade(col, 0.9), ol=dark, w=1.4)
    # shaft (slight entasis)
    pts = [(x - w * 0.5, yb - h * 0.04), (x - w * 0.45, top + (h * 0.07 if not broken else 0)),
           (x + w * 0.45, top + (h * 0.07 if not broken else 0)), (x + w * 0.5, yb - h * 0.04)]
    if broken:
        zz = []
        n = 6
        for i in range(n + 1):
            zz.append((x - w * 0.45 + w * 0.9 * i / n, top + (6 if i % 2 else -4)))
        pts = [pts[0]] + [(x - w * 0.5 + 1, top)] + zz + [pts[3]]
    g.poly(pts, fill=col, ol=dark, w=1.4)
    g.polyA([(x + w * 0.12, yb - h * 0.05), (x + w * 0.12, top + 4), (x + w * 0.46, top + 4), (x + w * 0.5, yb - h * 0.05)], (60, 40, 20), 0.18)
    if fluted:
        for k in range(-3, 4):
            xx = x + k * w * 0.13
            g.line([(xx, yb - h * 0.06), (xx, top + 6)], shade(col, 0.82), 1.1)
    if not broken:
        g.rect(x - w * 0.72, top, x + w * 0.72, top + h * 0.045, fill=shade(col, 0.95), ol=dark, w=1.4)
        g.ell(x, top + h * 0.075, w * 0.58, h * 0.03, fill=shade(col, 0.92), ol=dark, w=1.2)


def temple(g, cx, yb, width, height, col='#e9dfc6', n=6, glow=None, steps=3):
    dark = shade(col, 0.7)
    sh = height * 0.05
    for i in range(steps):
        g.rect(cx - width / 2 - (steps - i) * 8, yb - sh * (i + 1), cx + width / 2 + (steps - i) * 8, yb - sh * i,
               fill=shade(col, 0.96 - i * 0.04), ol=dark, w=1.4)
    ybase = yb - sh * steps
    colh = height * 0.62
    ent = height * 0.1
    g.rect(cx - width / 2 - 6, ybase - colh - ent, cx + width / 2 + 6, ybase - colh, fill=shade(col, 0.98), ol=dark, w=1.6)
    for k in range(7):
        xx = cx - width / 2 + 10 + k * (width - 20) / 6
        g.rect(xx - 4, ybase - colh - ent * 0.8, xx + 4, ybase - colh - ent * 0.2, fill=shade(col, 0.82))
    g.poly([(cx - width / 2 - 14, ybase - colh - ent), (cx + width / 2 + 14, ybase - colh - ent), (cx, ybase - colh - ent - height * 0.2)],
           fill=shade(col, 1.0), ol=dark, w=1.6)
    g.poly([(cx - width / 2 + 24, ybase - colh - ent - 5), (cx + width / 2 - 24, ybase - colh - ent - 5), (cx, ybase - colh - ent - height * 0.145)],
           fill=shade(col, 0.82))
    for k in range(n):
        xx = cx - width / 2 + 14 + k * (width - 28) / (n - 1)
        column(g, xx, ybase, colh, width / n * 0.36, col)
    if glow:
        g.rectA(cx - width / 2 + 10, ybase - colh, cx + width / 2 - 10, ybase, glow, 0.0)


def arch_ruin(g, x, yb, w, h, col='#b9764a', seed=1):
    rng = random.Random(seed)
    dark = shade(col, 0.6)
    g.rect(x, yb - h, x + w * 0.2, yb, fill=col, ol=dark, w=1.5)
    g.rect(x + w * 0.8, yb - h * 0.7, x + w, yb, fill=col, ol=dark, w=1.5)
    pts = []
    for i in range(0, 19):
        a = math.pi * i / 18
        pts.append((x + w / 2 - math.cos(a) * w * 0.4, yb - h * 0.62 - math.sin(a) * h * 0.36))
    g.poly(pts + [(x + w * 0.9, yb - h * 0.62), (x + w * 0.1, yb - h * 0.62)][::-1][:0] + [(x + w * 0.9, yb - h * 0.55), (x + w * 0.1, yb - h * 0.55)], fill=col, ol=dark, w=1.5)
    for i in range(5):
        g.line([(x + 4, yb - h * (0.2 + i * 0.18)), (x + w * 0.2 - 4, yb - h * (0.2 + i * 0.18))], dark, 1.2)


def mosaic_pattern(g, x0, y0, x1, y1, col1, col2, n=7):
    """greek key (meander) band"""
    h = y1 - y0
    cw = h / 1.0
    x = x0
    while x + cw <= x1:
        pts = [(x, y1), (x, y0), (x + cw * 0.8, y0), (x + cw * 0.8, y0 + h * 0.7), (x + cw * 0.25, y0 + h * 0.7),
               (x + cw * 0.25, y0 + h * 0.35), (x + cw * 0.5, y0 + h * 0.35)]
        g.line(pts, col2, max(1.2, h * 0.12))
        x += cw


# ------------------------------------------------------------------ people
def limb(g, p0, p1, w, col):
    g.line([p0, p1], OL, w + 2.6, True)
    g.line([p0, p1], col, w, True)


def figure(g, x, y, s=1.0, t=0.0, shirt='#8e9aa8', pants='#4c5668', skin='w1', hat=None, hatc='#f2c230',
           vest=None, anim='idle', face=1, ph=0.0, hair='#2b1c14', tool=None, shadow=True):
    """Small full-body person. (x,y) = feet. Height ~ 110*s."""
    skin = SK.get(skin, skin)
    if shadow:
        g.shadowblob(x, y + 2 * s, 24 * s, 5 * s, 0.3)
    walk = anim == 'walk'
    sw = math.sin(t * 6.5 + ph) if walk else 0.0
    bob = abs(sw) * 2.2 * s if walk else math.sin(t * 2 + ph) * 0.8 * s
    hipy = y - 52 * s - bob
    shy = y - 90 * s - bob
    # legs
    for k, c in ((-1, shade(pants, 0.82)), (1, pants)):
        sk = sw * k * 14 * s * face
        foot = (x + sk, y - (2 * s if (walk and sk * face * k < 0) else 0))
        if anim == 'dig' and k == -1:
            foot = (x + face * 10 * s, y)
        limb(g, (x + k * 4 * s, hipy), foot, 9 * s, c)
        g.ell(foot[0] + face * 4 * s, foot[1], 8 * s, 3.6 * s, fill=(34, 26, 22))
    # back arm
    def arm(a, col, L=34 * s, side=1):
        sx = x + side * 11 * s
        hand = (sx + face * math.sin(a) * L, shy + 4 * s + math.cos(a) * L)
        limb(g, (sx, shy + 4 * s), hand, 7 * s, col)
        g.ell(hand[0], hand[1], 4.2 * s, fill=skin, ol=OL, w=1)
        return hand
    if anim == 'walk':
        arm(-sw * 0.6, shade(shirt, 0.8), side=-1)
    elif anim == 'dig':
        arm(0.5 + 0.4 * math.sin(t * 5 + ph), shade(shirt, 0.8), side=-1)
    elif anim == 'point':
        arm(0.1, shade(shirt, 0.8), side=-1)
    else:
        arm(0.15 + 0.05 * math.sin(t + ph), shade(shirt, 0.8), side=-1)
    # torso
    g.poly([(x - 13 * s, shy), (x + 13 * s, shy), (x + 11 * s, hipy + 4 * s), (x - 11 * s, hipy + 4 * s)], fill=shirt, ol=OL, w=1.6)
    if vest:
        g.poly([(x - 12 * s, shy + 1), (x - 4 * s, shy + 1), (x - 3 * s, hipy + 3 * s), (x - 10 * s, hipy + 3 * s)], fill=vest)
        g.poly([(x + 12 * s, shy + 1), (x + 4 * s, shy + 1), (x + 3 * s, hipy + 3 * s), (x + 10 * s, hipy + 3 * s)], fill=vest)
        g.line([(x - 11 * s, hipy - 14 * s), (x + 11 * s, hipy - 14 * s)], (240, 240, 220), 2 * s)
    # head
    hy = shy - 14 * s
    g.rect(x - 3.5 * s, shy - 6 * s, x + 3.5 * s, shy + 2 * s, fill=shade(skin, 0.85))
    g.ell(x, hy, 10 * s, 11.5 * s, fill=skin, ol=OL, w=1.4)
    g.ell(x + face * 4 * s, hy - 1 * s, 1.3 * s, fill=(30, 20, 16))
    if hat == 'hard':
        g.poly([(x - 11 * s, hy - 3 * s), (x - 9 * s, hy - 11 * s), (x, hy - 15 * s), (x + 9 * s, hy - 11 * s), (x + 11 * s, hy - 3 * s)], fill=hatc, ol=OL, w=1.4)
        g.rect(x - 13 * s + face * 3 * s, hy - 4.5 * s, x + 13 * s + face * 3 * s, hy - 1.5 * s, fill=shade(hatc, 0.85), ol=OL, w=1.2)
    elif hat == 'brim':
        g.poly([(x - 9 * s, hy - 5 * s), (x - 7 * s, hy - 15 * s), (x + 7 * s, hy - 15 * s), (x + 9 * s, hy - 5 * s)], fill=hatc, ol=OL, w=1.3)
        g.ell(x, hy - 5 * s, 19 * s, 4 * s, fill=shade(hatc, 0.92), ol=OL, w=1.3)
    elif hat == 'cap':
        g.poly([(x - 10 * s, hy - 3 * s), (x - 8 * s, hy - 12 * s), (x + 8 * s, hy - 12 * s), (x + 10 * s, hy - 3 * s)], fill=hatc, ol=OL, w=1.3)
        g.poly([(x + face * 2 * s, hy - 4 * s), (x + face * 16 * s, hy - 2 * s), (x + face * 2 * s, hy - 1 * s)], fill=shade(hatc, 0.8), ol=OL, w=1.1)
    else:
        g.poly([(x - 10 * s, hy - 2 * s), (x - 8 * s, hy - 11 * s), (x + 8 * s, hy - 11 * s), (x + 10 * s, hy - 2 * s), (x, hy - 7 * s)], fill=hair)
    # front arm
    if anim == 'walk':
        h = arm(sw * 0.6, shirt)
    elif anim == 'dig':
        h = arm(0.9 + 0.6 * math.sin(t * 5 + ph), shirt)
    elif anim == 'point':
        h = arm(1.45 + 0.05 * math.sin(t * 3), shirt, L=38 * s)
    elif anim == 'hold':
        h = arm(1.0, shirt)
    else:
        h = arm(0.1 + 0.05 * math.sin(t + ph + 1), shirt)
    if tool == 'clip':
        g.rect(h[0] - 1 * s + face * 2 * s, h[1] - 10 * s, h[0] + 11 * s + face * 2 * s, h[1] + 8 * s, fill=(236, 226, 200), ol=OL, w=1.3)
    elif tool == 'shovel':
        g.line([(h[0], h[1] - 30 * s), (h[0] + face * 6 * s, h[1] + 20 * s)], (120, 84, 50), 3 * s, True)
        g.poly([(h[0] + face * 2 * s, h[1] + 20 * s), (h[0] + face * 14 * s, h[1] + 20 * s), (h[0] + face * 8 * s, h[1] + 34 * s)], fill=(150, 156, 160), ol=OL, w=1)
    return h


def head(g, cx, cy, s, who, t=0.0, turn=0.0, talk=0.0, look=(0, 0), blink=None, brow=0.0, glasses=True, smile=0.0):
    skin = SK[who]
    dk = shade(skin, 0.78)
    rx, ry = 46 * s, 56 * s
    fx = turn * 15 * s
    if blink is None:
        ph = (t * 0.33 + (0.3 if who == 'dora' else 0.0)) % 1.0
        blink = 1.0 if ph < 0.025 else 0.0
    # back hair
    if who == 'dora':
        hc = '#2a1712'
        rng = random.Random(9)
        for i in range(34):
            a = math.radians(rng.uniform(140, 400))
            rr = rng.uniform(0.95, 1.18)
            px, py = cx + math.cos(a) * rx * rr * 1.02, cy - 4 * s + math.sin(a) * ry * rr * 0.98
            if math.sin(a) > 0.1:
                py += 30 * s * math.sin(a)
            g.ell(px, py, rng.uniform(15, 22) * s, fill=hc if i % 3 else '#38201a', ol=None)
        for i in range(12):
            a = math.radians(rng.uniform(150, 390))
            g.ell(cx + math.cos(a) * rx * 1.25, cy + 10 * s + math.sin(a) * ry * 1.05, 20 * s, fill=hc)
    # neck
    g.poly([(cx - 17 * s, cy + 36 * s), (cx + 17 * s, cy + 36 * s), (cx + 22 * s, cy + 90 * s), (cx - 22 * s, cy + 90 * s)], fill=dk, ol=OL, w=2 * s)
    # ears
    for k in (-1, 1):
        g.ell(cx + k * (rx - 1 * s) + fx * 0.5, cy + 6 * s, 7 * s, 11 * s, fill=skin, ol=OL, w=1.8 * s)
    # head
    g.ell(cx, cy, rx, ry, fill=dk, ol=OL, w=2.4 * s)
    g.ell(cx - 5 * s - turn * 3 * s, cy - 2 * s, rx - 6 * s, ry - 5 * s, fill=skin)
    # cheeks
    g.ellA(cx + fx - 28 * s, cy + 26 * s, 11 * s, 7 * s, (220, 120, 100), 0.2)
    g.ellA(cx + fx + 28 * s, cy + 26 * s, 11 * s, 7 * s, (220, 120, 100), 0.2)
    # beard (steven / man)
    if who in ('steven', 'man'):
        bc = '#2c231e' if who == 'steven' else '#241c18'
        pts = [(cx - rx + 2 * s, cy - 2 * s), (cx - rx + 3 * s, cy + 30 * s), (cx - 30 * s, cy + 56 * s), (cx, cy + 66 * s),
               (cx + 30 * s, cy + 56 * s), (cx + rx - 3 * s, cy + 30 * s), (cx + rx - 2 * s, cy - 2 * s), (cx + 34 * s, cy + 18 * s),
               (cx + 18 * s + fx * .5, cy + 22 * s), (cx + fx * .5, cy + 20 * s), (cx - 18 * s + fx * .5, cy + 22 * s), (cx - 34 * s, cy + 18 * s)]
        g.poly(pts, fill=bc)
        g.ellA(cx - 20 * s, cy + 46 * s, 10 * s, 8 * s, '#6b5b50', 0.25)
    # eyes
    for k in (-1, 1):
        ex, ey = cx + fx + k * 19 * s, cy - 6 * s
        if blink > 0.5:
            g.line([(ex - 8 * s, ey), (ex + 8 * s, ey)], OL, 2 * s)
        else:
            g.ell(ex, ey, 9 * s, 7 * s, fill=(250, 248, 242), ol=OL, w=1.4 * s)
            g.ell(ex + look[0] * 3.2 * s, ey + look[1] * 2.5 * s, 4.6 * s, fill=(70, 44, 26))
            g.ell(ex + look[0] * 3.2 * s, ey + look[1] * 2.5 * s, 2.2 * s, fill=(12, 8, 6))
            g.ell(ex + look[0] * 3.2 * s - 1.5 * s, ey + look[1] * 2.5 * s - 2 * s, 1.2 * s, fill=(255, 255, 255))
        by = ey - 14 * s - brow * 4 * s * (1 if k == 1 else 0.6)
        g.line([(ex - 10 * s, by + 3 * s - k * brow * 2 * s * -1), (ex + 10 * s, by - 1 * s + k * brow * 2 * s * -1)] if k == 1 else
               [(ex - 10 * s, by - 1 * s + brow * 2 * s), (ex + 10 * s, by + 3 * s)], '#2a1c14' if who != 'steven' else '#2b221d', 4 * s, True)
    # nose
    g.line([(cx + fx, cy + 0 * s), (cx + fx + 5 * s, cy + 16 * s), (cx + fx - 3 * s, cy + 19 * s)], shade(skin, 0.6), 2 * s)
    # mouth
    my = cy + 36 * s
    if who in ('steven', 'man'):
        g.poly([(cx + fx - 24 * s, my - 8 * s), (cx + fx, my - 12 * s), (cx + fx + 24 * s, my - 8 * s), (cx + fx + 18 * s, my - 2 * s), (cx + fx - 18 * s, my - 2 * s)], fill='#2c231e')
    if talk > 0.05:
        g.ell(cx + fx, my + 2 * s, 10 * s, 3 * s + talk * 7 * s, fill=(88, 22, 28), ol=OL, w=1.4 * s)
        g.rect(cx + fx - 7 * s, my + 2 * s - 3 * s - talk * 7 * s + 3 * s, cx + fx + 7 * s, my + 2 * s - talk * 7 * s + 6 * s, fill=(248, 246, 240))
    else:
        c = (130, 60, 56) if who == 'dora' else (160, 110, 92)
        g.line([(cx + fx - 10 * s, my), (cx + fx, my + 2 * s + smile * 3 * s), (cx + fx + 10 * s, my - smile * 2 * s)], c, 2.4 * s, True)
    # glasses
    if glasses:
        for k in (-1, 1):
            ex, ey = cx + fx + k * 19 * s, cy - 6 * s
            g.ellA(ex, ey, 15 * s, 13 * s, '#bfe4ff', 0.18)
            g.ell(ex, ey, 15 * s, 13 * s, ol='#1f1814', w=2.6 * s)
            g.line([(ex - 9 * s, ey - 5 * s), (ex - 3 * s, ey - 9 * s)], (255, 255, 255), 1.6 * s, True)
        g.line([(cx + fx - 5 * s, cy - 8 * s), (cx + fx + 5 * s, cy - 8 * s)], '#1f1814', 2.4 * s)
        g.line([(cx + fx - 34 * s, cy - 8 * s), (cx - rx, cy - 6 * s)], '#1f1814', 2.2 * s)
        g.line([(cx + fx + 34 * s, cy - 8 * s), (cx + rx, cy - 6 * s)], '#1f1814', 2.2 * s)
    # front hair
    if who == 'dora':
        hc = '#2a1712'
        rng = random.Random(21)
        for i in range(16):
            a = math.radians(200 + i * 10.5 + rng.uniform(-3, 3))
            px = cx + math.cos(a) * rx * 0.98
            py = cy - 8 * s + math.sin(a) * ry * 0.95
            g.ell(px, py, rng.uniform(13, 18) * s, fill=hc if i % 2 else '#34201a')
        for i in range(5):
            g.ell(cx - 30 * s + i * 15 * s + fx * .3, cy - ry + 6 * s + (i % 2) * 5 * s, 15 * s, fill='#34201a')
        g.glow(cx - 20 * s, cy - ry - 4 * s, 26 * s, (50, 40, 36), 0.2)
    elif who == 'steven':
        hc = '#3a3028'
        pts = []
        for i in range(0, 21):
            a = math.radians(188 + i * 8.7)
            pts.append((cx + math.cos(a) * (rx + 3 * s), cy - 4 * s + math.sin(a) * (ry + 5 * s)))
        inner = [(cx + 34 * s, cy - 26 * s), (cx + 14 * s + fx * .3, cy - 32 * s), (cx - 14 * s + fx * .3, cy - 34 * s), (cx - 34 * s, cy - 26 * s)]
        g.poly(pts + inner, fill=hc)
        g.poly([(cx - rx - 2 * s, cy - 8 * s), (cx - rx + 8 * s, cy - 8 * s), (cx - rx + 6 * s, cy + 10 * s), (cx - rx - 1 * s, cy + 8 * s)], fill='#6b625a')
    elif who == 'man':
        hc = '#241c18'
        pts = [(cx + math.cos(math.radians(190 + i * 8.5)) * (rx + 3 * s), cy - 4 * s + math.sin(math.radians(190 + i * 8.5)) * (ry + 4 * s)) for i in range(21)]
        g.poly(pts + [(cx + 36 * s, cy - 24 * s), (cx - 36 * s, cy - 24 * s)], fill=hc)


def bust(g, cx, cy, s, who, t=0.0, turn=0.0, talk=0.0, look=(0, 0), shirt=KHAKI, nod=0.0, brow=0.0, smile=0.0, dy=0.0, coat=None):
    """cx, cy = head centre."""
    cy = cy + dy
    skin = SK[who]
    col = coat or shirt
    br = math.sin(t * 1.8) * 2 * s
    pts = [(cx - 190 * s, cy + 420 * s), (cx - 176 * s, cy + 190 * s + br), (cx - 120 * s, cy + 128 * s + br), (cx - 24 * s, cy + 92 * s),
           (cx + 24 * s, cy + 92 * s), (cx + 120 * s, cy + 128 * s + br), (cx + 176 * s, cy + 190 * s + br), (cx + 190 * s, cy + 420 * s)]
    g.poly(pts, fill=col, ol=OL, w=3 * s)
    g.polyA([(cx + 40 * s, cy + 100 * s), (cx + 120 * s, cy + 128 * s), (cx + 176 * s, cy + 190 * s), (cx + 190 * s, cy + 420 * s), (cx + 60 * s, cy + 420 * s)], (30, 20, 10), 0.18)
    # collar + undershirt
    g.poly([(cx - 34 * s, cy + 88 * s), (cx + 34 * s, cy + 88 * s), (cx, cy + 150 * s)], fill=shade(skin, 0.8), ol=OL, w=2 * s)
    g.poly([(cx - 36 * s, cy + 84 * s), (cx - 4 * s, cy + 150 * s), (cx - 62 * s, cy + 150 * s), (cx - 74 * s, cy + 108 * s)], fill=shade(col, 1.1), ol=OL, w=2 * s)
    g.poly([(cx + 36 * s, cy + 84 * s), (cx + 4 * s, cy + 150 * s), (cx + 62 * s, cy + 150 * s), (cx + 74 * s, cy + 108 * s)], fill=shade(col, 1.1), ol=OL, w=2 * s)
    g.line([(cx, cy + 150 * s), (cx, cy + 420 * s)], shade(col, 0.6), 2 * s)
    # pocket
    g.rect(cx + 70 * s, cy + 220 * s, cx + 130 * s, cy + 280 * s, fill=shade(col, 1.05), ol=shade(col, 0.55), w=2 * s, r=3 * s)
    head(g, cx + turn * 4 * s, cy + nod, s, who, t=t, turn=turn, talk=talk, look=look, brow=brow, smile=smile)


def speech_dots(g, x, y, t, col=(255, 255, 255)):
    for i in range(3):
        k = 0.5 + 0.5 * math.sin(t * 5 - i * 0.9)
        g.ell(x + i * 14, y - k * 4, 4.5, fill=col)


def qmark(g, x, y, s, t, col=(255, 250, 235), a=1.0, ol=(30, 22, 18)):
    if s < 0.06:
        return
    f = font('DejaVuSerif-Bold.ttf', 120 * s)
    bob = math.sin(t * 3) * 4
    for dx, dy in ((-3, -3), (3, -3), (-3, 3), (3, 3), (0, 4)):
        g.text(x + dx, y + dy + bob, '?', f, ol, 'mm')
    g.text(x, y + bob, '?', f, col, 'mm')


def talk_amt(t, on=True, sp=9.0):
    if not on:
        return 0.0
    return max(0.0, math.sin(t * sp) * 0.5 + 0.5) * (0.6 + 0.4 * math.sin(t * 2.3))


_lab = {}


def label(g, text, x, y, a=1.0, size=24, sub=None, anchor='c', seed=3, scale=1.0):
    """parchment tag placed on 2x canvas (logical coords)."""
    key = (text, sub, size, seed)
    if key not in _lab:
        _lab[key] = banner(text, sub, size=size * 2, seed=seed)
    spr = _lab[key]
    w, h = spr.size
    k = scale
    if k != 1.0:
        spr = spr.resize((int(w * k), int(h * k)), Image.LANCZOS)
        w, h = spr.size
    lx = x - (w / S / 2 if anchor == 'c' else 0)
    ly = y - h / S / 2
    g.paste_rgba(spr, lx, ly, a)
    return (lx, ly, w / S, h / S)


def cap(g, cx, cy, s, col='#2f4a7a', d=1):
    rx = 46 * s
    g.poly([(cx - rx - 2 * s, cy - 14 * s), (cx - rx * .8, cy - 52 * s), (cx, cy - 66 * s), (cx + rx * .8, cy - 52 * s), (cx + rx + 2 * s, cy - 14 * s)], fill=col, ol=OL, w=2.4 * s)
    g.poly([(cx + d * 10 * s, cy - 16 * s), (cx + d * (rx + 34 * s), cy - 8 * s), (cx + d * (rx + 30 * s), cy - 2 * s), (cx + d * 10 * s, cy - 8 * s)], fill=shade(col, 0.8), ol=OL, w=2 * s)
    g.line([(cx - rx * .5, cy - 62 * s), (cx - rx * .4, cy - 20 * s)], shade(col, 1.3), 1.6 * s)
