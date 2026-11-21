"""Shared scene helpers (backgrounds, repeated settings)."""
import math
import numpy as np
from PIL import Image
from gfx import *
from assets import *
from assets2 import *
from engine import *

DAY = vgrad(mix(AMBER, CREAM, .55), mix(CREAM, TEAL, .32), y1=.62)
DUSK = vgrad(mix(NAVY, TERRA, .35), mix(AMBER, TERRA, .35), y1=.65)
NIGHT = vgrad(NAVY, mix(NAVY, TEAL, .28), y1=.7)
DAWN = vgrad(mix(NAVY, TEAL, .3), mix(AMBER, CREAM, .5), y1=.7)
UNDER = vgrad(mix(TEAL, CREAM, .12), mix(NAVY, TEAL, .2), y1=.9)
DARK = vgrad(NAVY, dark(NAVY, .4))
GOLD = vgrad(mix(AMBER, TERRA, .45), mix(CREAM, AMBER, .5), y1=.6)
def blend_img(a, b, u): return Image.blend(a, b, clamp(u))
def vband(c, x0, x1, y0, y1, top, bot, n=10, op=255):
    for i in range(n):
        a = y0 + (y1 - y0) * i / n
        c.rect(x0, a, x1 - x0, (y1 - y0) / n + 1.5, mix(top, bot, i / (n - 1)), None, op=op)
def strip_cam(t, starts, centers, d=.55):
    """camera x that glides (whip pan) to centers[i] at starts[i]"""
    x = centers[0]
    for i in range(1, len(starts)):
        u = prog(t, starts[i] - d * .3, starts[i] + d * .7)
        if u > 0: x = lerp(centers[i - 1] if u < 1 else x, centers[i], sstep(u)) if u < 1 else centers[i]
    return x
def ltitle(c, txt, y=100, size=44, op=255):
    c.hud(); c.text(640, y, txt, size, INK, 'serif', 'c', op, light(TERRA, .35), 2)
def wavy_rows(img, amp, t, freq=14.0):
    a = np.asarray(img); ys = np.arange(H)
    sh = (amp * np.sin(ys / freq + t * 3) + amp * .5 * np.sin(ys / 5.0 - t * 4)).astype(int)
    xs = (np.arange(W)[None, :] + sh[:, None]) % W
    return Image.fromarray(a[ys[:, None], xs])
def birds(c, t, n=3, y0=120, x0=200, spread=300):
    for i in range(n):
        x = (x0 + i * spread * .6 + t * 30 * (1 + i * .2)) % 1500 - 100; y = y0 + 30 * math.sin(i * 2 + t * .5) + i * 14
        f = math.sin(t * 6 + i) * 6
        c.line([(x - 12, y - f), (x, y), (x + 12, y - f)], INK, 2.2)
def temple(c, x, yb, s=1.0, col=None):
    """same temple design (6 columns, trident carved in the pediment) at any scale"""
    col = col or light(CREAM, .1)
    c.rect(x - 130 * s, yb - 10 * s, 260 * s, 10 * s, light(SAND, .25), INK, 2); c.rect(x - 120 * s, yb - 18 * s, 240 * s, 9 * s, light(SAND, .25), INK, 2)
    c.rect(x - 106 * s, yb - 76 * s, 212 * s, 58 * s, dark(SAND, .12), INK, 2); c.rect(x - 17 * s, yb - 58 * s, 34 * s, 40 * s, INK, INK, 1.5)
    for i in range(6): column(c, x - 96 * s + i * 38.4 * s, yb - 74 * s, yb - 18 * s, 14 * s, col)
    c.rect(x - 118 * s, yb - 92 * s, 236 * s, 16 * s, light(SAND, .3), INK, 2)
    c.poly([(x - 122 * s, yb - 92 * s), (x + 122 * s, yb - 92 * s), (x, yb - 138 * s)], light(SAND, .2), INK, 2.2)
    trident(c, x, yb - 106 * s, 1.1 * s, dark(SAND, .6))
BURIED = [(250, 470, 120, 60), (420, 482, 90, 50), (560, 468, 150, 70), (760, 482, 110, 50), (900, 472, 130, 60), (1060, 484, 100, 50)]
def plain(c, t, plants=1.0, glow=0.0, mist=0.0, ground_y=400, sea=True):
    """quiet plain (same place every time): far mountains, gulf strip, grass over soil, buried walls glow below"""
    c.L(.3); c.poly([(-300, 380), (100, 300), (300, 340), (560, 270), (800, 340), (1100, 290), (1500, 380)], mix(TEAL, CREAM, .5), None)
    c.L(.6)
    if sea: c.rect(-400, 372, 1100, 40, TEAL, None); c.line([(-400, 374), (700, 374)], light(TEAL, .4), 2)
    c.L(1.0)
    gy_ = lambda x: ground_y + 10 * math.sin(x / 200)
    pts = [(x, gy_(x)) for x in range(-400, 1800, 50)]
    c.poly(pts + [(1800, 800), (-400, 800)], mix(SAND, BROWN, .5), INK, 2.5)       # soil
    c.poly(pts + [(x, y + 40) for x, y in reversed(pts)], mix(TEAL, AMBER, .3 + .1 * (1 - plants)), None)  # grass
    c.line(pts, INK, 2.5)
    for k in range(int(26 * plants)):
        px = -300 + k * 83 % 1900; py = gy_(px)
        c.poly([(px, py), (px + 3, py - 14 - k % 9), (px + 7, py)], mix(TEAL, AMBER, .5), None)
    if glow > 0:
        for lw_, op in ((16, 25), (10, 45), (5, 90), (2, 200)):
            for (bx, by, bw, bh) in BURIED:
                c.line([(bx, by + bh), (bx, by), (bx + bw, by), (bx + bw, by + bh)], AMBER, lw_, int(op * glow))
            c.line([(240, 540), (1200, 540)], AMBER, lw_ * .7, int(op * glow * .7))
        for i in range(6): c.line([(300 + i * 150, 545), (300 + i * 150, 600)], AMBER, 3, int(120 * glow))
    if mist > 0:
        for k in range(5):
            c.poly([(-300 + k * 300 + 40 * math.sin(t * .3 + k), 330 + k * 14)] + [(-300 + k * 300 + 250 + 30 * math.sin(t * .4 + k), 340 + k * 14), (-300 + k * 300 + 200, 400), (-300 + k * 300, 400)], CREAM, None, op=int(70 * mist))
def sunken_street(c, t, silt=0.0, plants=0.0, rays=1.0):
    vband(c, -200, 1500, -100, 760, mix(TEAL, CREAM, .18), mix(NAVY, TEAL, .25), 14)
    if rays > 0:
        for i, x in enumerate((180, 420, 700, 980)):
            c.L(.7); c.poly([(x, -100), (x + 80, -100), (x + 200 + 30 * math.sin(t * .4 + i), 560), (x + 40, 560)], CREAM, None, op=int(34 * rays))
    c.L(.5)
    for x in (260, 520, 900): c.rect(x, 300, 22, 200, mix(SAND, TEAL, .6), None, op=130)
    c.L(1.0)
    c.poly([(-200, 480), (1500, 480), (1500, 760), (-200, 760)], mix(SAND, TEAL, .45), None)
    c.poly([(100, 480), (1100, 480), (1300, 600), (-100, 600)], mix(SAND, TEAL, .3), INK, 2)
    for k in range(8): c.line([(20 + k * 160 - 40, 600), (100 + k * 130, 480)], dark(mix(SAND, TEAL, .3), .25), 2)
    for i, x in enumerate((180, 430, 700, 960)):
        h = 150 - 30 * (i % 2)
        c.rect(x - 15, 480 - h, 30, h, mix(SAND, TEAL, .2), INK, 2.2); c.rect(x - 22, 480 - h - 8, 44, 9, mix(SAND, TEAL, .2), INK, 2)
        for dx in (-5, 5): c.line([(x + dx, 480 - h + 4), (x + dx, 478)], dark(SAND, .35), 1.2)
        c.poly([(x - 60, 482), (x - 20, 480 - 30 * silt - 6), (x + 20, 480 - 30 * silt - 6), (x + 60, 482)], mix(SAND, TEAL, .5), None, op=int(255 * min(1, silt * 3 + .4)))
    if silt > 0:
        c.poly([(-200, 520 - 140 * silt)] + [(x, 520 - 140 * silt + 10 * math.sin(x / 60)) for x in range(-200, 1500, 60)] + [(1500, 760), (-200, 760)], mix(SAND, TEAL, .55), None, op=int(255 * min(1, silt * 2)))
    for k in range(int(18 * plants)):
        px = -100 + (k * 151) % 1400; ph = 90 + 50 * ((k * 7) % 5) / 5 * plants + 60 * plants
        c.poly([(px - 6, 530), (px + 12 * math.sin(t + k), 530 - ph * .6), (px + 5 + 8 * math.sin(t * 1.2 + k), 530 - ph), (px + 8, 530)], mix(TEAL, AMBER, .3 + .1 * (k % 3)), INK, 1.6)
    return
def tilt_title(c, txt, x, y, size=34): c.hud(); c.text(x, y, txt, size, CREAM, 'sans', 'c', 255, INK, 3)
def lamp(c, x, y, s=1.0, t=0.0):
    f = 1 + .06 * math.sin(t * 9) + .03 * math.sin(t * 17)
    for r, o in ((60, 30), (40, 55), (24, 90)): c.circ(x, y - 14 * s, r * s * f, AMBER, None, op=o)
    c.poly([(x - 14 * s, y), (x + 14 * s, y), (x + 8 * s, y - 8 * s), (x - 8 * s, y - 8 * s)], dark(SAND, .3), INK, 2)
    c.poly([(x - 4 * s, y - 8 * s), (x, y - 24 * s * f), (x + 4 * s, y - 8 * s)], AMBER, INK, 1.5)
def desk(c, x0, x1, y):
    c.rect(x0, y, x1 - x0, 140, mix(BROWN, SAND, .25), INK, 3); c.line([(x0, y + 12), (x1, y + 12)], dark(BROWN, .3), 2)
def crack_line(c, pts, prog_, col=(255, 255, 255), lw=4):
    n = max(2, int(len(pts) * prog_) + 1); c.line(pts[:n], col, lw)
