"""Continuity bible assets: each drawn once here, reused by every scene."""
import math
from gfx import *

TERRA, NAVY, TEAL, SAND, AMBER, CREAM = P['terra'], P['navy'], P['teal'], P['sand'], P['amber'], P['cream']
SKIN = mix(SAND, TERRA, .42); OLIVE = mix(AMBER, TEAL, .6); ORANGE = mix(TERRA, AMBER, .5)
BROWN = mix(TERRA, INK, .6); JACKET = mix(NAVY, TEAL, .3); STONE = mix(SAND, INK, .12)
def blink(t, seed=0): return ((t + seed * 1.7) % (3.2 + (seed % 3) * .7)) < .14
def breath(t, seed=0): return math.sin(t * 2 * math.pi / 3.4 + seed)

# ---------------------------------------------------------------- people (evidence mode)
KINDS = {  # continuity: same outfits everywhere
    'arch': dict(body=OLIVE, legs=mix(SAND, INK, .35), hat='wide', hatc=SAND),
    'phys': dict(body=JACKET, legs=dark(NAVY, .3), hat=None, hair=INK, glasses=True),
    'crew': dict(body=ORANGE, under=JACKET, legs=dark(NAVY, .2), hat='cap', hatc=ORANGE),
    'trav': dict(body=BROWN, legs=dark(BROWN, .4), hat='wide', hatc=BROWN, cloak=True),
    'scribe': dict(body=CREAM, legs=SAND, hat=None, hair=dark(BROWN, .3)),
    'scholar': dict(body=mix(TEAL, INK, .3), legs=dark(NAVY, .2), hat=None, hair=mix(CREAM, INK, .3)),
    'baker': dict(body=light(SAND, .3), legs=SAND, hat='cap', hatc=CREAM),
    'merchant': dict(body=mix(TERRA, CREAM, .25), legs=SAND, hat=None, hair=BROWN),
    'woman': dict(body=mix(TEAL, CREAM, .4), legs=mix(TEAL, CREAM, .4), hat=None, hair=dark(BROWN, .3), dress=True),
    'child': dict(body=mix(AMBER, CREAM, .2), legs=SAND, hat=None, hair=BROWN),
    'man': dict(body=mix(SAND, TERRA, .3), legs=dark(SAND, .3), hat=None, hair=dark(BROWN, .2)),
    'explorer': dict(body=mix(BROWN, SAND, .3), legs=dark(BROWN, .3), hat='wide', hatc=mix(BROWN, SAND, .3)),
}
def limb(c, p0, p1, w, col, lw=2.2):
    c.line([p0, p1], INK, w + lw * 2); c.line([p0, p1], col, w)
def prop(c, kind, hx, hy, s, t=0, ang=0):
    if kind == 'trowel':
        c.poly([(hx, hy - 4 * s), (hx + 14 * s, hy - 24 * s), (hx + 20 * s, hy - 22 * s), (hx + 8 * s, hy - 2 * s)], P['sand'], INK, 1.8); c.line([(hx, hy), (hx + 5 * s, hy - 8 * s)], BROWN, 5 * s)
    elif kind == 'brush':
        c.line([(hx, hy), (hx + 12 * s, hy - 24 * s)], BROWN, 4 * s); c.poly([(hx + 10 * s, hy - 22 * s), (hx + 15 * s, hy - 22 * s), (hx + 17 * s, hy - 32 * s), (hx + 11 * s, hy - 30 * s)], AMBER, INK, 1.5)
    elif kind == 'instr':
        c.rect(hx - 4 * s, hy - 22 * s, 20 * s, 26 * s, dark(TEAL, .2), INK, 1.8); c.rect(hx, hy - 17 * s, 12 * s, 9 * s, light(TEAL, .6), None); c.line([(hx + 6 * s, hy - 22 * s), (hx + 6 * s, hy - 38 * s)], INK, 2)
    elif kind == 'staff':
        c.line([(hx, hy + 40 * s), (hx + 4 * s, hy - 70 * s)], BROWN, 5 * s)
    elif kind == 'pen':
        c.line([(hx, hy), (hx + 14 * s, hy + 12 * s)], BROWN, 3 * s)
    elif kind == 'map':
        c.poly([(hx - 6 * s, hy - 30 * s), (hx + 30 * s, hy - 34 * s), (hx + 32 * s, hy), (hx - 4 * s, hy + 4 * s)], CREAM, INK, 1.8); c.line([(hx + 2 * s, hy - 20 * s), (hx + 14 * s, hy - 16 * s), (hx + 22 * s, hy - 24 * s)], TEAL, 2)
    elif kind == 'tablet':
        c.rect(hx - 4 * s, hy - 24 * s, 24 * s, 30 * s, CREAM, INK, 1.8); c.line([(hx + 1 * s, hy - 16 * s), (hx + 15 * s, hy - 16 * s)], TEAL, 2); c.line([(hx + 1 * s, hy - 8 * s), (hx + 12 * s, hy - 8 * s)], TEAL, 2)
    elif kind == 'hammer':
        c.line([(hx, hy), (hx + 4 * s, hy - 26 * s)], BROWN, 4 * s); c.rect(hx - 6 * s, hy - 34 * s, 22 * s, 10 * s, dark(SAND, .4), INK, 1.8)
    elif kind == 'camera':
        c.rect(hx - 8 * s, hy - 22 * s, 28 * s, 20 * s, dark(SAND, .6), INK, 1.8); c.circ(hx + 6 * s, hy - 12 * s, 6 * s, TEAL, INK, 1.5)
    elif kind == 'basket':
        c.poly([(hx - 12 * s, hy - 14 * s), (hx + 14 * s, hy - 14 * s), (hx + 10 * s, hy + 8 * s), (hx - 8 * s, hy + 8 * s)], mix(SAND, BROWN, .3), INK, 1.8)

def person(c, x, y, s=1.0, kind='arch', t=0.0, emo='neutral', look=0, armL=8, armR=8, propL=None, propR=None,
           seed=0, walk=0.0, mouth=None, flip=1, lean=0.0, back=False):
    """Flat-mode character: ink outlines, blink + breathing loop, face always alive. (x,y)=feet."""
    K = KINDS[kind]; br = breath(t, seed) * .02
    f = flip
    def X(v): return x + v * s * f
    def Y(v): return y + v * s
    sw = math.sin(walk) * 11 if walk else 0
    # legs
    if K.get('dress'):
        c.poly([(X(-17), Y(-62)), (X(17), Y(-62)), (X(24), Y(-4)), (X(-24), Y(-4))], K['body'], INK, 2.5)
    else:
        for sg, col in ((-1, dark(K['legs'], .15)), (1, K['legs'])):
            lx = sg * 8 + sg * sw * (1 if sg > 0 else -1) * .0
            off = sw * sg
            limb(c, (X(sg * 8), Y(-62)), (X(sg * 9 + off), Y(-6)), 11 * s, col)
            c.ell(X(sg * 9 + off + 3), Y(-3), 9 * s, 4.5 * s, dark(INK, 0), INK, 1.5)
    top = -116 - br * 60 + lean
    # cloak behind
    if K.get('cloak'):
        c.poly([(X(-22), Y(top + 4)), (X(22), Y(top + 4)), (X(30), Y(-18)), (X(-30), Y(-18))], dark(K['body'], .15), INK, 2.5)
    # torso
    body = K['body']
    c.poly([(X(-20), Y(top + 2)), (X(20), Y(top + 2)), (X(17), Y(-58)), (X(-17), Y(-58))], body, INK, 2.5)
    if K.get('under'): c.poly([(X(-6), Y(top + 2)), (X(6), Y(top + 2)), (X(5), Y(-58)), (X(-5), Y(-58))], K['under'], None)
    if kind == 'arch': c.line([(X(0), Y(top + 6)), (X(0), Y(-60))], dark(OLIVE, .4), 2); c.poly([(X(-13), Y(-58)), (X(13), Y(-58)), (X(13), Y(-52)), (X(-13), Y(-52))], dark(K['legs'], .1), None)
    if kind == 'scribe': c.line([(X(-17), Y(-60)), (X(17), Y(-60))], AMBER, 3)
    if kind == 'trav':  # satchel on LEFT shoulder (viewer's right when facing us), strap
        c.line([(X(-18), Y(top + 6)), (X(14), Y(-70))], dark(SAND, .5), 3); c.rect(X(9) if f > 0 else X(9) - 18 * s, Y(-74), 18 * s, 20 * s, mix(SAND, BROWN, .5), INK, 2)
    # arms
    for sg, a, pr in ((-1, armL, propL), (1, armR, propR)):
        sx_, sy_ = X(sg * 19), Y(top + 8)
        r = math.radians(a); L = 50 * s
        hx, hy = sx_ + math.sin(r) * L * sg * f * (1 if f > 0 else 1) * 1.0 * (1), sy_ + math.cos(r) * L
        limb(c, (sx_, sy_), (hx, hy), 9 * s, body if kind != 'phys' else body)
        c.circ(hx, hy, 5.5 * s, SKIN, INK, 1.8)
        if pr: prop(c, pr, hx, hy, s, t)
    # head
    hy0 = top - 20; hxc = X(0) + lean * .3
    c.circ(hxc, Y(hy0 + 2) if False else y + (hy0 + 2) * s, 17 * s, SKIN, INK, 2.5)
    hc = y + (hy0 + 2) * s
    if K.get('hair'): c.poly([(hxc - 17 * s, hc - 2 * s), (hxc - 14 * s, hc - 15 * s), (hxc, hc - 19 * s), (hxc + 14 * s, hc - 15 * s), (hxc + 17 * s, hc - 2 * s), (hxc + 10 * s, hc - 10 * s), (hxc - 10 * s, hc - 10 * s)], K['hair'], INK, 1.8)
    if K.get('dress'): c.circ(hxc + 11 * s * f, hc - 12 * s, 7 * s, K['hair'], INK, 1.8)
    # face
    ex = 6.5 * s; lk = look * 3 * s
    if back:
        c.circ(hxc, hc, 17.5 * s, K.get('hair') or mix(BROWN, INK, .3), INK, 2.5)
    bl = blink(t, seed)
    for sg in ((-1, 1) if not back else ()):
        ecx = hxc + sg * ex + lk; ecy = hc - 1 * s
        if bl: c.line([(ecx - 3 * s, ecy), (ecx + 3 * s, ecy)], INK, 1.8)
        else: c.circ(ecx, ecy, 2.1 * s * (1.4 if emo == 'surprise' else 1), INK, None)
        if K.get('glasses'): c.circ(ecx, ecy, 5.5 * s, None, INK, 1.3)
        by = ecy - (8 if emo != 'surprise' else 11) * s
        if emo == 'curious': by -= (4 * s if sg > 0 else 0); c.line([(ecx - 4 * s, by + (0 if sg < 0 else 1 * s)), (ecx + 4 * s, by - (1 if sg < 0 else 3) * s)], INK, 1.8)
        elif emo == 'doubt': c.line([(ecx - 4 * s, by + (3 if sg > 0 else -1) * s), (ecx + 4 * s, by + (-2 if sg > 0 else 2) * s)], INK, 1.8)
        elif emo == 'surprise': c.line([(ecx - 4 * s, by + 1 * s), (ecx, by - 2 * s), (ecx + 4 * s, by + 1 * s)], INK, 1.8)
        else: c.line([(ecx - 4 * s, by), (ecx + 4 * s, by)], INK, 1.8)
    m = None if back else mouth or {'surprise': 'o', 'curious': 'smile', 'doubt': 'flat', 'happy': 'smile'}.get(emo, 'flat')
    my = hc + 8 * s; mx = hxc + lk
    if m is None: pass
    elif m == 'smile': c.line([(mx - 4 * s, my - 1 * s), (mx, my + 2 * s), (mx + 4 * s, my - 1 * s)], INK, 1.8)
    elif m == 'o': c.ell(mx, my, 2.6 * s, 3.2 * s, INK, None)
    elif m == 'frown': c.line([(mx - 4 * s, my + 2 * s), (mx, my - 1 * s), (mx + 4 * s, my + 2 * s)], INK, 1.8)
    else: c.line([(mx - 3.5 * s, my), (mx + 3.5 * s, my + (1 if emo == 'doubt' else 0) * s)], INK, 1.8)
    # hats
    h = K.get('hat')
    if h == 'wide':
        c.ell(hxc, hc - 13 * s, 30 * s, 6 * s, K['hatc'], INK, 2.2); c.poly([(hxc - 15 * s, hc - 14 * s), (hxc - 12 * s, hc - 30 * s), (hxc + 12 * s, hc - 30 * s), (hxc + 15 * s, hc - 14 * s)], K['hatc'], INK, 2.2)
        c.line([(hxc - 14 * s, hc - 17 * s), (hxc + 14 * s, hc - 17 * s)], dark(K['hatc'], .45), 2.5)
    elif h == 'cap':
        c.poly([(hxc - 16 * s, hc - 8 * s), (hxc - 12 * s, hc - 22 * s), (hxc + 12 * s, hc - 22 * s), (hxc + 16 * s, hc - 8 * s)], K['hatc'], INK, 2.2)

# ---------------------------------------------------------------- Helike skyline (continuity)
HOUSES = [  # (x, w, h, rowoffset) -- exactly 9 whitewashed flat-roof houses
    (350, 52, 44, 0), (420, 48, 40, 0), (485, 54, 46, 0), (553, 46, 38, 0), (612, 52, 42, 0),
    (385, 50, 40, 15), (455, 52, 38, 15), (525, 48, 36, 15), (590, 50, 36, 15)]
SHIPS = [(715, 1.0), (805, 1.15), (905, 0.95)]   # exactly 3 ships, ship #2 has the striped sail
def gy(x):
    if x < 340: return 290.0
    return 290 + (min(x, 700) - 340) * .335
SEA_Y = 425
def trident(c, x, y, s, col=INK, lw=2.2):
    c.line([(x, y + 14 * s), (x, y - 12 * s)], col, lw); c.line([(x - 6 * s, y - 6 * s), (x - 6 * s, y - 12 * s)], col, lw)
    c.line([(x + 6 * s, y - 6 * s), (x + 6 * s, y - 12 * s)], col, lw); c.line([(x - 6 * s, y - 6 * s), (x + 6 * s, y - 6 * s)], col, lw)
def column(c, x, y0, y1, w, col, line=INK):
    c.rect(x - w / 2, y0, w, y1 - y0, col, line, 1.8); c.rect(x - w * .72, y0 - 4, w * 1.44, 5, col, line, 1.5); c.rect(x - w * .72, y1 - 1, w * 1.44, 5, col, line, 1.5)
    for k in (-1, 0, 1): c.line([(x + k * w * .25, y0 + 2), (x + k * w * .25, y1 - 2)], dark(col, .2), 1)
def ship(c, x, y, s, striped, t, ph=0):
    b = math.sin(t * 1.2 + ph) * 3
    y += b; hull = dark(BROWN, .1)
    c.poly([(x - 34 * s, y - 10 * s), (x + 36 * s, y - 12 * s), (x + 26 * s, y + 8 * s), (x - 24 * s, y + 8 * s)], hull, INK, 2.2)
    c.line([(x, y - 10 * s), (x, y - 70 * s)], INK, 3)
    pts = [(x + 3 * s, y - 66 * s), (x + 34 * s, y - 20 * s), (x + 3 * s, y - 20 * s)]
    c.poly(pts, CREAM, INK, 2)
    if striped:
        for k in range(3):
            u0 = k * .3 + .05; u1 = u0 + .15
            c.poly([(x + 3 * s + 31 * s * u0 * (1) , y - 20 * s - 46 * s * u0 * 0 - 0), ], None, None) if False else None
        for k, yy in enumerate((-30, -42, -54)):
            wdt = (yy + 66) / 46 * 0 + (66 + yy) / 46
            c.poly([(x + 3 * s, y + yy * s), (x + 3 * s + 31 * s * (1 - (-yy - 20) / 46) , y + yy * s), (x + 3 * s + 31 * s * (1 - (-yy - 20) / 46), y + (yy + 6) * s), (x + 3 * s, y + (yy + 6) * s)], TERRA, None)
def tiny(c, x, y, s, col, ph, t):
    sw = math.sin(t * 5 + ph) * 2
    c.line([(x, y), (x + sw, y - 9 * s)], INK, 2.5 * s + 1); c.line([(x, y - 8 * s), (x, y - 15 * s)], col, 3 * s + 1); c.circ(x, y - 18 * s, 2.8 * s, SKIN, INK, 1.2)

def skyline(c, t, vis=None, states=None, lit=0.0):
    """Evidence-mode skyline. vis: dict of layer visibilities 0..1; states: per-house 'ok'/'cracked'/'ruin'."""
    v = dict(mount=1, temple=1, houses=1, roofs=1, streets=1, figs=1, ships=1, water=1, plants=0, sea_level=0.0)
    if vis: v.update(vis)
    # mountains (parallax 0.3 / 0.5)
    mo = int(255 * clamp(v['mount']))
    c.L(.3); c.poly([(500, 430), (640, 250), (760, 170), (880, 240), (1010, 140), (1130, 230), (1260, 160), (1420, 300), (1500, 430)], mix(TEAL, CREAM, .5), None, op=mo)
    c.L(.5); c.poly([(560, 430), (700, 300), (840, 210), (960, 300), (1090, 190), (1230, 290), (1400, 250), (1500, 430)], mix(TEAL, CREAM, .3), INK, 2, op=mo)
    c.poly([(840, 210), (870, 245), (835, 280), (800, 252)], dark(mix(TEAL, CREAM, .3), .18), None, op=mo)
    c.L(1.0)
    # hill + ground
    if v['temple'] or v['houses']:
        a = max(v['temple'], v['houses'])
        c.poly([(20, 430), (50, 300), (180, 284), (340, 288), (420, 332), (700, 410), (730, 430)], SAND, INK, 2.5, op=int(255 * a))
        if v['plants'] > 0:
            for k in range(int(40 * v['plants'])):
                px = 40 + k * 17 % 640; py = gy(px) + 2
                c.poly([(px, py), (px + 4, py - 12 - k % 7), (px + 8, py)], mix(TEAL, AMBER, .5 if k % 2 else .3), None)
    # temple
    if v['temple'] > 0:
        o = int(255 * v['temple'])
        c.rect(104, 280, 252, 10, light(SAND, .25), INK, 2, o); c.rect(112, 272, 236, 9, light(SAND, .25), INK, 2, o)
        c.rect(124, 214, 212, 58, dark(SAND, .12), INK, 2, o)
        c.rect(213, 232, 34, 40, INK, INK, 1.5, o); trident(c, 230, 226, 1.0, AMBER if False else dark(SAND, .6)) if False else None
        for i in range(6): column(c, 134 + i * 38.4, 216, 272, 14, light(CREAM, .1))
        c.rect(112, 198, 236, 16, light(SAND, .3), INK, 2, o)
        c.poly([(108, 198), (352, 198), (230, 152)], light(SAND, .2), INK, 2.2, o)
        trident(c, 230, 184, 1.1, dark(SAND, .6))      # trident carved above the door, in the pediment
    if v['houses'] > 0:
        for i, (hx, hw, hh, ro) in enumerate(HOUSES):
            stt = (states or {}).get(i, 'ok') if states else 'ok'
            by = gy(hx + hw / 2) + ro * .6 + 4
            o = int(255 * v['houses'])
            if stt == 'ruin':
                c.poly([(hx, by), (hx + 6, by - 12), (hx + 18, by - 8), (hx + 28, by - 16), (hx + hw - 6, by - 6), (hx + hw, by)], dark(CREAM, .25), INK, 2, o); continue
            c.rect(hx, by - hh, hw, hh, CREAM, INK, 2, o)
            if v['roofs'] > 0: c.rect(hx - 4, by - hh - 8, hw + 8, 9, TERRA, INK, 2, int(255 * v['roofs'] * v['houses']))
            c.rect(hx + hw * .42, by - hh * .48, hw * .2, hh * .48, dark(SAND, .55), INK, 1.5, o)
            wl = (i / 9.0) < lit
            c.rect(hx + 6, by - hh * .75, 9, 9, AMBER if wl else mix(NAVY, TEAL, .4) if lit > 0 else light(TEAL, .5), INK, 1.5, o)
            if stt == 'cracked': c.line([(hx + hw * .3, by - hh), (hx + hw * .4, by - hh * .6), (hx + hw * .25, by - hh * .3), (hx + hw * .36, by)], INK, 2.2)
    if v['streets'] > 0:
        o = int(255 * v['streets'])
        pts = [(346, 300), (372, 304), (400, 322), (470, 340), (520, 362), (600, 386), (690, 412)]
        c.line(pts, dark(SAND, .22), 7, o)
    if v['figs'] > 0:
        for k, (u, col) in enumerate(((.12, AMBER), (.4, TERRA), (.65, CREAM), (.85, AMBER))):
            ph = (u + t * .02 * (1 if k % 2 else -1)) % 1; px = 360 + ph * 330; tiny(c, px, gy(px) + 12, 1.0, col, k, t) if v['figs'] > .5 else None
    # harbor + ships (parallax 1.15)
    c.L(1.12)
    if v['ships'] > 0:
        o = int(255 * v['ships'])
        c.poly([(660, 412), (780, 418), (780, 432), (650, 432)], dark(SAND, .15), INK, 2, o)
        for k, (sx, ss) in enumerate(SHIPS): ship(c, sx + 40, SEA_Y + 2, ss, k == 1, t, k)
    c.L(1.0)
    if v['water']:
        wave_rig(c, t, SEA_Y + 4, -200, 1700, TEAL, amp=1.0, level=v['sea_level'], ybot=760)

# ---------------------------------------------------------------- vase-mode (legend) drawing
VT = TERRA; VK = INK
def vwater(c, t, y, x0=-200, x1=1700, band=70, amp=6):
    """black water band with incised curl pattern (legend). Reuses wave-rig timing."""
    pts = [(x, y + amp * math.sin(x / 90 + t * 1.1)) for x in range(int(x0), int(x1) + 40, 40)]
    c.poly(pts + [(x1, y + band), (x0, y + band)], VK, None)
    for k in range(3):
        yy = y + 14 + k * 18
        c.line([(x, yy + amp * .7 * math.sin(x / 70 + t * 1.3 + k)) for x in range(int(x0), int(x1) + 30, 30)], VT, 1.4)
    for x in range(int(x0), int(x1), 60):
        c.line([(x, y + 6), (x + 12, y - 2), (x + 24, y + 6), (x + 22, y + 14)], VT, 1.3)
def vcol(c, x, y0, y1, w, tilt=0.0, broken=0.0):
    top = y0 + broken * (y1 - y0) * .6
    c.poly([(x - w / 2 + tilt, top), (x + w / 2 + tilt, top), (x + w / 2, y1), (x - w / 2, y1)], VK, None)
    c.rect(x - w * .75 + tilt, top - 5, w * 1.5, 6, VK, None)
    c.line([(x - w * .15 + tilt * .5, top + 4), (x - w * .15, y1 - 3)], VT, 1.1); c.line([(x + w * .2 + tilt * .5, top + 4), (x + w * .2, y1 - 3)], VT, 1.1)
def vskyline(c, t, quake=0.0, collapse=0.0, water_y=None, figs=True, ghost=0.0):
    """same layout as the flat skyline, redrawn as black silhouettes; collapse 0..1"""
    rnd = lambda k: math.sin(k * 12.9898 + c.ph * 3.1)
    c.L(.4); c.poly([(560, 430), (700, 300), (840, 210), (960, 300), (1090, 190), (1230, 290), (1400, 250), (1500, 430)], VK, None)
    c.line([(840, 230), (870, 270), (850, 300)], VT, 1.3); c.line([(1090, 210), (1120, 260), (1100, 300)], VT, 1.3)
    c.L(1.0)
    qx = lambda k: quake * 5 * rnd(k)
    c.poly([(20, 430), (50, 300), (180, 284), (340, 288), (420, 332), (700, 410), (730, 430)], VK, None)
    for k in range(5): c.line([(60 + k * 120 + qx(k), 300 + k * 6), (90 + k * 120, 318 + k * 6)], VT, 1.2)
    c.rect(104 + qx(1), 280, 252, 10, VK); c.rect(112 + qx(2), 272, 236, 9, VK)
    c.rect(124 + qx(3), 214 + 40 * collapse, 212, 58 - 40 * collapse, VK)
    for i in range(6):
        br = collapse * (.2 + .6 * ((i * 37) % 10) / 10)
        vcol(c, 134 + i * 38.4 + qx(i + 4), 216, 272, 14, tilt=quake * 6 * rnd(i) + collapse * (i - 2.5) * 5, broken=br)
    if collapse < .6:
        c.poly([(108 + qx(8), 198 + 70 * collapse), (352 + qx(9), 198 + 100 * collapse), (230 + qx(7), 152 + 90 * collapse)], VK)
        trident(c, 230, 184 + 70 * collapse, 1.1, VT, 1.5)
    for i, (hx, hw, hh, ro) in enumerate(HOUSES):
        by = gy(hx + hw / 2) + ro * .6 + 4
        cc = clamp(collapse * 1.3 - (i % 3) * .12); h = hh * (1 - .8 * cc)
        tl = cc * (6 if i % 2 else -6) * 2
        c.poly([(hx + qx(i), by - h), (hx + hw + qx(i), by - h + tl), (hx + hw, by), (hx, by)], VK)
        c.rect(hx - 4 + qx(i), by - h - 7 + tl * .5, hw + 8, 8, VK)
        c.line([(hx + 8, by - h * .7), (hx + 16, by - h * .7)], VT, 1.4); c.line([(hx + hw * .5, by - h * .4), (hx + hw * .5, by - 1)], VT, 1.4)
        if quake > .4 and i % 2 == 0: c.line([(hx + 12, by - h), (hx + 18, by - h * .5), (hx + 14, by - h * .2)], VT, 1.6)
    c.L(1.12)
    for k, (sx, ss) in enumerate(SHIPS):
        x = sx + 40; y = SEA_Y + 2 + math.sin(t * 1.2 + k) * 3
        c.poly([(x - 34 * ss, y - 10 * ss), (x + 36 * ss, y - 12 * ss), (x + 26 * ss, y + 8 * ss), (x - 24 * ss, y + 8 * ss)], VK)
        c.line([(x, y - 10 * ss), (x, y - 70 * ss)], VK, 3); c.poly([(x + 3, y - 66 * ss), (x + 34 * ss, y - 20 * ss), (x + 3, y - 20 * ss)], VK)
        c.line([(x + 6, y - 28 * ss), (x + 26 * ss, y - 28 * ss)], VT, 1.2)
    c.L(1.0)
def vfig(c, x, y, s=1.0, kind='man', t=0.0, flip=1, pose='stand', prop_=None, seed=0):
    """black-figure human in profile (no expression). kind: poseidon, man, woman, run"""
    f = flip
    def X(v): return x + v * s * f
    def Y(v): return y + v * s
    ph = math.sin(t * 8 + seed) if pose in ('run', 'walk') else 0
    def P2(pts): return [(X(a), Y(b)) for a, b in pts]
    stride = 18 * ph
    # legs
    lw_ = 10 * s
    c.poly(P2([(-3, -64), (7, -64), (7 + stride, -4), (-2 + stride, -4)]), VK); c.poly(P2([(-1 + stride, -4), (14 + stride, -2), (14 + stride, 2), (-2 + stride, 2)]), VK)
    c.poly(P2([(-6, -64), (4, -64), (-7 - stride, -4), (-16 - stride, -4)]), VK); c.poly(P2([(-14 - stride, -4), (3 - stride, -2), (3 - stride, 2), (-16 - stride, 2)]), VK)
    # robe / torso
    top = -118 + (3 if pose == 'run' else 0)
    if kind == 'woman' or kind == 'poseidon':
        c.poly(P2([(-12, top + 4), (11, top + 4), (14, -62), (18, -6), (-18, -6), (-14, -62)]), VK)
        for k in range(4): c.line(P2([(-10 + k * 7, -58), (-12 + k * 8, -9)]), VT, 1.0)
        c.line(P2([(-17, -12), (17, -12)]), VT, 1.2); c.line(P2([(-16, -9), (16, -9)]), VT, 1.0)
    else:
        c.poly(P2([(-12, top + 4), (11, top + 4), (11, -62), (-11, -62)]), VK); c.poly(P2([(-11, -66), (11, -66), (15, -42), (-15, -42)]), VK)
        c.line(P2([(-14, -44), (14, -44)]), VT, 1.1)
    c.line(P2([(-9, top + 12), (9, top + 24)]), VT, 1.1)
    # head profile (facing +x*flip)
    hc = top - 14
    head = [(-10, -12), (-3, -17), (7, -14), (9, -7), (14, -3), (9, 0), (10, 4), (8, 9), (4, 13), (-3, 13), (-9, 7), (-11, -2)]
    c.poly([(X(a), y + (hc + b) * s) for a, b in head], VK)
    c.line([(X(2), y + (hc - 5) * s), (X(6), y + (hc - 6) * s), (X(3), y + (hc - 3) * s)], VT, 1.1)  # eye (incised almond)
    if kind == 'poseidon':
        c.poly([(X(5), y + (hc + 8) * s), (X(13), y + (hc + 8) * s), (X(11), y + (hc + 26) * s), (X(0), y + (hc + 30) * s), (X(-4), y + (hc + 14) * s)], VK)
        for k in range(3): c.line([(X(2 + k * 3), y + (hc + 13) * s), (X(2 + k * 2), y + (hc + 25) * s)], VT, 1.0)
        c.poly([(X(-11), y + (hc - 8) * s), (X(-4), y + (hc - 18) * s), (X(5), y + (hc - 16) * s), (X(-2), y + (hc - 10) * s)], VK)
    elif kind == 'woman': c.circ(X(-10), y + (hc - 4) * s, 6 * s, VK)
    # arms
    ang = {'stand': 20, 'walk': 25 * ph + 20, 'run': 150, 'up': 160, 'strike': 50, 'point': 85}.get(pose, 20)
    r = math.radians(ang); sh = (X(2), Y(top + 10)); L = 46 * s
    hand = (sh[0] + math.sin(r) * L * f, sh[1] + math.cos(r) * L * -1 * -1)
    hand = (sh[0] + math.sin(r) * L * f, sh[1] + math.cos(r) * L)
    c.line([sh, hand], VK, 9 * s)
    if prop_ == 'trident':   # Poseidon: trident in the RIGHT hand (figure's right = front arm when facing +x)
        c.line([(hand[0], hand[1] + 80 * s), (hand[0], hand[1] - 70 * s)], VK, 3.2 * s)
        tx, ty = hand[0], hand[1] - 70 * s
        for dx in (-9, 0, 9):
            c.line([(tx + dx * s, ty), (tx + dx * s, ty - 18 * s)], VK, 2.6 * s)
        c.line([(tx - 9 * s, ty), (tx + 9 * s, ty)], VK, 2.6 * s); c.line([(tx, ty), (tx, ty + 8 * s)], VT, 1)
        c.poly([(tx - 9 * s, ty - 18 * s), (tx - 12 * s, ty - 24 * s), (tx - 6 * s, ty - 21 * s)], VK); c.poly([(tx + 9 * s, ty - 18 * s), (tx + 12 * s, ty - 24 * s), (tx + 6 * s, ty - 21 * s)], VK); c.poly([(tx - 3 * s, ty - 18 * s), (tx, ty - 26 * s), (tx + 3 * s, ty - 18 * s)], VK)
    return hand
def vjar(c, x, y, s, rot=0.0):
    pts = [(-8, -22), (8, -22), (11, -14), (12, 0), (7, 10), (-7, 10), (-12, 0), (-11, -14)]
    cr, sr = math.cos(rot), math.sin(rot)
    c.poly([(x + (a * cr - b * sr) * s, y + (a * sr + b * cr) * s) for a, b in pts], VK)
    c.line([(x + (-9 * cr + 2 * sr) * s, y + (-9 * sr - 2 * cr) * s), (x + (9 * cr + 2 * sr) * s, y + (9 * sr - 2 * cr) * s)], VT, 1.1)
