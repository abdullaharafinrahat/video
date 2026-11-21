"""More continuity assets: strata, coin, evidence board, map kit, globe, marker, manuscript, instruments."""
import math
from gfx import *
from assets import *

# ---------------- strata cross-section (fixed order, colours, thickness) ----------------
STRATA = [('Much older', .30, mix(SAND, INK, .5)), ('Classical', .25, mix(SAND, AMBER, .7)),
          ('Roman', .22, mix(SAND, TERRA, .38)), ('Byzantine', .23, mix(SAND, TEAL, .22))]
def strata(c, x, y, w, h, reveal=1.0, grass=0.0, hl=None, labels=False, lab_size=24, dim=None, shift=0.0, only=(0, 4)):
    """y = top of block, h = total height. Returns {name:(x,y,w,h)}. Classical layer is amber-tinted."""
    out = {}; yy = y + h
    for i, (nm, fr, col) in enumerate(STRATA):
        lh = h * fr; yy -= lh
        if reveal <= i / 4 or not (only[0] <= i < only[1]): continue
        vis = clamp(reveal * 4 - i); hh = lh * vis
        oy = yy + lh - hh
        cc = col if dim is None or dim == nm else mix(col, P['navy'], .0)
        c.rect(x, oy, w, hh, cc, INK, 2.5)
        for k in range(4):   # texture strokes (fixed positions)
            ly = oy + hh * (k + 1) / 5
            c.line([(x + 8 + j * 26, ly + 3 * math.sin(j * 1.7 + i + k)) for j in range(int(w / 26))], dark(cc, .22), 1.6, 150)
        for k in range(int(w / 40)):
            c.circ(x + 14 + (k * 37 + i * 11) % max(20, int(w - 28)), oy + hh * (.25 + .5 * ((k * 7 + i) % 5) / 5), 2.2, dark(cc, .3))
        if hl == nm: c.rect(x - 5, oy - 5, w + 10, hh + 10, None, AMBER, 5)
        out[nm] = (x, oy, w, hh)
        if labels: c.text(x + w + 18, oy + hh / 2, nm if nm != 'Classical' else 'Classical Helike?', lab_size, CREAM, 'sans', 'l', outline=INK, ow=3)
    if grass > 0:
        c.poly([(x, y + 1)] + [(x + j * 20, y - 7 * grass + 3 * math.sin(j)) for j in range(int(w / 20) + 1)] + [(x + w, y + 1)], mix(TEAL, AMBER, .35), INK, 2)
    return out

# ---------------- coin (identical every time) ----------------
COIN = mix(AMBER, TERRA, .32)
def coin(c, x, y, r, rot=0.0, shine=-1.0, op=255):
    cs = math.cos(rot); sn = math.sin(rot); rx = max(r * abs(cs), 1.5); th = r * .17
    ex = th * abs(sn) * (1 if sn >= 0 else -1)
    c.ell(x + ex, y, rx, r, dark(COIN, .35), INK, 3, op)       # thick edge
    c.ell(x, y, rx, r, COIN, INK, 3, op)
    c.ell(x, y, rx * .86, r * .86, None, dark(COIN, .35), 2.5, op)
    # emblem: three wave lines and a trident (abstract)
    s = r / 60.0
    for k in range(3):
        c.line([(x + (-26 + j * 6.5) * s * cs, y + (26 + k * 8 + 3 * math.sin(j * 1.6 + k)) * s) for j in range(9)], dark(COIN, .45), 3 * s + .8, op)
    if abs(cs) > .12:
        c.line([(x, y + 14 * s), (x, y - 34 * s)], dark(COIN, .45), 4 * s + .8, op)
        for dx in (-13, 13):
            c.line([(x + dx * s * cs, y - 6 * s), (x + dx * s * cs, y - 34 * s)], dark(COIN, .45), 3.4 * s + .6, op)
        c.line([(x - 13 * s * cs, y - 6 * s), (x + 13 * s * cs, y - 6 * s)], dark(COIN, .45), 3.4 * s + .6, op)
    if shine >= 0 and rx > 8:
        xa = x - rx + 2 * rx * (shine - .18); xb = x - rx + 2 * rx * shine
        xa = max(x - rx * .96, xa); xb = min(x + rx * .96, xb)
        if xb - xa > 2:
            xs = [xa + (xb - xa) * i / 8 for i in range(9)]
            top = [(u, y - r * .92 * math.sqrt(max(0, 1 - ((u - x) / rx) ** 2))) for u in xs]
            bot = [(u, y + r * .92 * math.sqrt(max(0, 1 - ((u - x) / rx) ** 2))) for u in xs]
            c.poly(top + bot[::-1], light(COIN, .75), None, op=int(op * .45))

# ---------------- evidence board (same positions in 16 and 37) ----------------
BOARD_ITEMS = [('map', -.30, -.06), ('manuscript', .02, -.20), ('coin', .30, .02), ('shard', -.04, .20)]
def manuscript(c, x, y, w, h, faded=0.0, lines=6, seed=0, tilt=0.0):
    col = mix(CREAM, SAND, .25 + .4 * faded)
    c.poly([(x - w / 2, y - h / 2 + tilt), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2 - tilt), (x - w / 2, y + h / 2)], col, INK, 2)
    for k in range(lines):
        yy = y - h / 2 + 12 + k * (h - 24) / max(1, lines - 1); n = int(w / 9) - 2
        pts = [(x - w / 2 + 8 + j * 9, yy + (3 if (j * 7 + k * 3 + seed) % 3 == 0 else -2) * (1 if j % 2 else -1)) for j in range(n)]
        c.line(pts, mix(INK, col, .35 + .4 * faded), 1.5)
def shard(c, x, y, s=1.0):
    c.poly([(x - 30 * s, y - 8 * s), (x - 6 * s, y - 28 * s), (x + 26 * s, y - 14 * s), (x + 32 * s, y + 14 * s), (x - 4 * s, y + 24 * s), (x - 24 * s, y + 12 * s)], mix(TERRA, SAND, .25), INK, 2.2)
    c.line([(x - 22 * s, y - 2 * s), (x + 24 * s, y + 2 * s)], INK, 2.2); c.line([(x - 18 * s, y + 8 * s), (x + 18 * s, y + 10 * s)], INK, 1.8)
def mini_map(c, x, y, w, h):
    c.rect(x - w / 2, y - h / 2, w, h, CREAM, INK, 2); c.poly([(x - w / 2 + 4, y - h / 2 + 4), (x + w * .1, y - h / 2 + 4), (x - w * .1, y + 4), (x - w / 2 + 4, y + 8)], light(SAND, .2), INK, 1.5)
    c.poly([(x - w * .25, y + 8), (x + w * .2, y + 4), (x + w * .1, y + h * .35), (x - w * .15, y + h * .3)], light(SAND, .2), INK, 1.5); c.circ(x - w * .08, y + 2, 4, AMBER, INK, 1.5)
def board(c, cx, cy, w=620, h=420, pins=4, thread=1.0, t=0.0, lit=1.0, glow=False):
    cork = mix(SAND, CREAM, .45)
    c.rect(cx - w / 2 - 12, cy - h / 2 - 12, w + 24, h + 24, dark(BROWN, .1), INK, 3)
    c.rect(cx - w / 2, cy - h / 2, w, h, cork, INK, 2)
    for k in range(40): c.circ(cx - w / 2 + (k * 97) % int(w), cy - h / 2 + (k * 53) % int(h), 2, dark(cork, .12))
    pos = {}
    for i, (nm, fx, fy) in enumerate(BOARD_ITEMS):
        x = cx + fx * w; y = cy + fy * h; pos[nm] = (x, y)
        if i >= pins: continue
        if nm == 'map': mini_map(c, x, y, 120, 90)
        elif nm == 'manuscript': manuscript(c, x, y, 96, 120, 0, 6, 2)
        elif nm == 'coin': coin(c, x, y, 40)
        else: shard(c, x, y, 1.5)
        c.circ(x, y - 40 if nm != 'coin' else y - 44, 6, TERRA if False else (200, 40, 40), INK, 1.8)
    if thread > 0:
        seq = ['map', 'manuscript', 'coin', 'shard', 'map']; segs = (len(seq) - 1) * thread
        for i in range(len(seq) - 1):
            if i >= pins: break
            a = pos[seq[i]]; b = pos[seq[i + 1]]; u = clamp(segs - i)
            if u <= 0: continue
            e = (a[0] + (b[0] - a[0]) * u, a[1] - 40 + (b[1] - 40 - (a[1] - 40)) * u)
            c.line([(a[0], a[1] - 40), ((a[0] + e[0]) / 2, (a[1] + e[1]) / 2 - 36 + 36 * (1 - u) - 6), e], (200, 40, 40), 2.2)
    return pos
# ---------------- map kit ----------------
def helike_marker(c, x, y, s=1.0, pulse=0.0, op=255):
    if pulse > 0:
        c.circ(x, y, 9 * s + 30 * s * pulse, None, AMBER, 2.5, int(180 * (1 - pulse) * op / 255))
    c.poly([(x - 8 * s, y - 14 * s), (x + 8 * s, y - 14 * s), (x, y + 2 * s)], AMBER, INK, 2, op)
    c.circ(x, y - 18 * s, 10 * s, AMBER, INK, 2.2, op); c.circ(x, y - 18 * s, 3.6 * s, CREAM, INK, 1.2, op)
LAND = light(SAND, .15)
def greece(c, ox, oy, sc=1.0, hi=0.0, sea=None):
    """schematic Greece (abstract, not survey-accurate): mainland, Peloponnese, Gulf of Corinth, Achaea highlight"""
    def T(p): return [(ox + a * sc, oy + b * sc) for a, b in p]
    A = [(-200, -200), (800, -200), (800, 150), (700, 190), (640, 150), (560, 215), (470, 180), (400, 232), (330, 236), (150, 240), (60, 262), (-200, 262)]
    B = [(110, 270), (330, 262), (372, 304), (356, 364), (304, 432), (242, 474), (192, 424), (122, 382), (82, 322)]
    c.poly(T(A), LAND, INK, 2.5); c.poly(T(B), LAND, INK, 2.5)
    c.poly(T([(330, 236), (360, 236), (350, 266), (330, 262)]), LAND, None)
    c.poly(T([(140, 272), (326, 266), (322, 298), (150, 316), (112, 290)]), mix(LAND, TERRA, .45 * hi), None, op=255)
    if hi > .02: c.line(T([(140, 272), (326, 266)]), TERRA, 4, int(255 * hi))
    return (ox + 232 * sc, oy + 264 * sc)
CONT = {'eu': [(-10, 36), (-8, 44), (0, 50), (10, 56), (30, 60), (60, 66), (100, 70), (140, 66), (160, 60), (140, 40), (120, 25), (100, 10), (80, 10), (70, 25), (55, 28), (40, 36), (28, 38), (22, 36), (10, 38)],
        'af': [(-17, 20), (-10, 35), (10, 36), (32, 31), (43, 12), (51, 11), (40, -15), (32, -30), (18, -34), (10, -5), (-8, 5)],
        'am': [(-165, 62), (-125, 50), (-120, 32), (-100, 20), (-85, 12), (-80, 8), (-77, 0), (-70, -15), (-60, -50), (-72, -52), (-80, -15), (-95, 16), (-110, 28), (-125, 45), (-140, 60), (-100, 70)],
        'au': [(114, -22), (130, -12), (150, -20), (153, -30), (140, -38), (120, -33)]}
def proj(lon, lat, lon0, lat0, r):
    lo = math.radians(lon - lon0); la = math.radians(lat); l0 = math.radians(lat0)
    x = math.cos(la) * math.sin(lo); y = math.cos(l0) * math.sin(la) - math.sin(l0) * math.cos(la) * math.cos(lo)
    z = math.sin(l0) * math.sin(la) + math.cos(l0) * math.cos(la) * math.cos(lo)
    return x * r, -y * r, z
def globe(c, cx, cy, r, lon0, lat0=28, sea=None, land=None, dots=(), marker=None, line=None, op=255):
    sea = sea or mix(TEAL, CREAM, .1); land = land or LAND
    c.circ(cx, cy, r, sea, INK, 3, op)
    for name, poly_ in CONT.items():
        pts = []; vis = 0
        for lon, lat in poly_:
            x, y, z = proj(lon, lat, lon0, lat0, r)
            if z < 0:
                n = math.hypot(x, y) or 1; x, y = x / n * r, y / n * r
            else: vis += 1
            pts.append((cx + x, cy + y))
        if vis >= 2: c.poly(pts, land, dark(land, .45), 1.6, op)
    for lo in range(-180, 180, 30):
        pts = [proj(lo, la, lon0, lat0, r) for la in range(-80, 81, 10)]
        seg = [(cx + x, cy + y) for x, y, z in pts if z > 0]
        if len(seg) > 1: c.line(seg, light(sea, .35), 1.2, int(op * .5))
    for la in range(-60, 61, 30):
        seg = [(cx + x, cy + y) for x, y, z in [proj(lo, la, lon0, lat0, r) for lo in range(-180, 181, 10)] if z > 0]
        if len(seg) > 1: c.line(seg, light(sea, .35), 1.2, int(op * .5))
    out = []
    for (lo, la, u) in dots:
        x, y, z = proj(lo, la, lon0, lat0, r)
        if z > 0 and u > 0:
            c.circ(cx + x, cy + y, 11 * u + 8 * (1 - u) * 0, AMBER, INK, 2, op); c.circ(cx + x, cy + y, 22 * u, None, AMBER, 2, int(120 * (1 - abs(u - .5) * 2)))
    return proj(22, 38.3, lon0, lat0, r)
def coast_y(x, delta=0.0, ancient=False):
    base = 340 + 26 * math.sin(x / 150) + 14 * math.sin(x / 61 + 1)
    g = math.exp(-((x - 640) / 170) ** 2)
    return base + (-70 if ancient else 0) * g + (70 * delta if not ancient else 0) * g * 0
def coastmap(c, t, shift=1.0, ox=0, label=True):
    """top-down coast: sea above, land below. shift 0..1 = delta grows (modern coast moves seaward)."""
    xs = list(range(-100, 1400, 25))
    mod = [(x, coast_y(x) - 0 + 0) for x in xs]
    def cy_(x, sh): g = math.exp(-((x - 640) / 190) ** 2); return coast_y(x) + 60 * g * (1 - sh) - 40 * g * 0 + 0
    # moving shoreline: at shift 0 the shore sits inland (ancient); at 1 it is the modern coast
    cur = [(x, cy_(x, shift) - 70 * math.exp(-((x - 640) / 190) ** 2) * shift * 0) for x in xs]
    c.poly([(-100, -100), (1400, -100)] + [(x, y) for x, y in reversed(cur)], mix(TEAL, NAVY, .1), None)
    c.poly(cur + [(1400, 800), (-100, 800)], LAND, None)
    c.line(cur, INK, 3.5)
    anc = [(x, cy_(x, 0) + 0) for x in xs]
    if shift > .6: c.dash(anc, TERRA, 3.5, 12, 9, int(255 * clamp((shift - .6) * 4)))
    # relief + plain
    for k in range(10):
        c.line([(k * 140 - 40 + j * 20, 520 + 40 * (k % 3) + 6 * math.sin(j + k)) for j in range(6)], dark(LAND, .12), 2)
    return cur, anc
def manuscript_page(c, x, y, w, h, t, scribbles=7, seed=1): manuscript(c, x, y, w, h, 0, scribbles, seed)
def monitor(c, x, y, w, h, prog_=1.0, flat=False, t=0.0):
    c.rect(x - 14, y - 14, w + 28, h + 28, dark(SAND, .55), INK, 3); c.rect(x, y, w, h, (20, 40, 36), INK, 2)
    for k in range(7): c.line([(x, y + h * k / 7), (x + w, y + h * k / 7)], (36, 64, 56), 1.2)
    n = 24; pts = []
    for j in range(n + 1):
        px = x + w * j / n
        if px > x + w * prog_: break
        py = y + h * (.62 + (0 if flat else .1 * math.sin(j * .8) * (1 if j % 5 else -1)))
        pts.append((px, py))
    if len(pts) > 1:
        c.poly(pts + [(pts[-1][0], y + h), (x, y + h)], mix((90, 130, 100), CREAM, .1), None, op=210); c.line(pts, (170, 210, 170), 2.5)
    for k in range(int(prog_ * 14)):
        yy = y + h * (.7 + .25 * ((k * 5) % 7) / 7); c.line([(x + 8 + k * w / 15, yy), (x + 20 + k * w / 15, yy)], (120, 170, 130), 2, 160)
    sx = x + (t * 90 % w)
    c.line([(sx, y + 2), (sx, y + h - 2)], (190, 230, 190), 2, 120)
def boat_side(c, x, y, s=1.0, t=0.0):
    b = math.sin(t * 1.5) * 3; y += b
    c.poly([(x - 90 * s, y - 20 * s), (x + 100 * s, y - 24 * s), (x + 70 * s, y + 14 * s), (x - 70 * s, y + 14 * s)], dark(SAND, .35), INK, 2.5)
    c.rect(x - 20 * s, y - 62 * s, 50 * s, 40 * s, CREAM, INK, 2.5); c.rect(x - 10 * s, y - 52 * s, 14 * s, 14 * s, light(TEAL, .5), INK, 1.8)
    c.line([(x - 70 * s, y - 20 * s), (x - 70 * s, y - 72 * s), (x - 20 * s, y - 40 * s)], INK, 2.5)
def qmark(c, x, y, size=120, col=CREAM, op=255, outline=INK):
    c.text(x, y, '?', size, col, 'serif', 'c', op, outline, 4)
