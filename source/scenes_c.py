"""Scenes 31-46"""
from scenelib import *
from scenes_a import draw12, draw13, draw14
from scenes_b import plate
SC = {}
def scene(n):
    def d(f): SC[n] = f; return f
    return d
def rich(c, y, parts, size=28, kind='sansr', col=INK):
    ws = [c.tsize(t, size, 'sans' if h > 0 else kind)[0] for t, h in parts]; sp = size * .4; tot = sum(ws) + sp * (len(ws) - 1); x = 640 - tot / 2
    for (t, h), w in zip(parts, ws):
        if h > 0: c.rect(x - 6, y - size * .7, w + 12, size * 1.4, AMBER, None, op=int(255 * h))
        c.text(x + w / 2, y, t, size, col, 'sans' if h > 0 else kind, 'c'); x += w + sp
def legend_img(fn, ta=0.0):
    lc = Canvas(TERRA, 'L', ta); fn(lc); return legend_post(lc.finish(), ta)

@scene(31)
def s31(k):
    ch = k.cue(84, 'challenged'); nt = k.cue(85, 'not'); l85 = k.lt(85)
    c = k.cv(DARK); c.cam(640, 295, 1 + .07 * k.t / k.d)
    c.hud(); c.paste(legend_img(lambda lc: draw14(lc, 7.5, 7.5)), 0, 0, 1280, 590, 70)
    c.hud(); 
    if k.t > l85 + .3:
        pts = [(640, 0), (610, 70), (650, 130), (590, 200), (640, 250), (560, 330), (610, 400), (540, 470), (580, 590)]
        c.L(1.0); crack_line(c, pts, prog(k.t, l85 + .3, l85 + 2.5), (230, 225, 210), 3)
        crack_line(c, [(640, 130), (760, 170), (820, 250)], prog(k.t, l85 + 1, l85 + 2.5), (230, 225, 210), 2)
        crack_line(c, [(590, 200), (440, 240), (380, 320)], prog(k.t, l85 + 1.2, l85 + 2.7), (230, 225, 210), 2)
    c.L(1.0); u = ease_out(prog(k.t, .2, .9)); y0 = 300
    c.rect(210, y0 - 190, 860, 380, CREAM, INK, 4, int(255 * u)); c.rect(210, y0 - 190, 860, 74, NAVY, INK, 4, int(255 * u))
    c.text(640, y0 - 153, 'Stiros, 2021, Seismological Research Letters', 29, CREAM, 'sans', 'c', int(255 * u))
    if k.t > .5:
        a = prog(k.t, .5, 1.0); h = prog(k.t, ch - .1, ch + .3)
        c.text(640, y0 - 70, 'The study', 28, INK, 'sansr', 'c', int(255 * a)) if False else None
        rich(c, y0 - 62, [('Challenges', h), ('the traditional account', 0)], 32)
    if k.t > l85 + .2:
        a = prog(k.t, l85 + .2, l85 + .8); hh = prog(k.t, nt - .2, nt + .3)
        c.rect(260, y0 - 20, 760, 2, dark(CREAM, .2), None, op=int(255 * a))
        rich(c, y0 + 28, [('The archaeology', 0), ('does not back', hh), ('the idea', 0)], 28)
        rich(c, y0 + 76, [('of a whole city destroyed', 0), ('and permanently submerged,', 0)], 28)
        rich(c, y0 + 124, [('as the later stories described.', 0)], 28)
    return c

@scene(32)
def s32(k):
    c = k.cv(vgrad(mix(NAVY, TEAL, .22), dark(NAVY, .3))); c.cam(lerp(520, 780, sstep(k.t / k.d)), 295, 1.1)
    x, y, w, h = 80, 110, 1160, 380; out = strata(c, x, y, w, h, 1.0, 0, None, False)
    sx = 640; st = .35; u = pop(prog(k.t, st, st + .2), .3)
    if k.t > st:
        c.rect(sx - 7, 70, 14, 450, TERRA, INK, 3); c.rect(sx - 70, 44, 140, 38, TERRA, INK, 3); c.text(sx, 63, '373 BC', 28, CREAM, 'serif', 'c')
        c.circ(sx, 300, 0, None, None)
    ay = out['Classical'][1] + out['Classical'][3] / 2; ap = ease_out(prog(k.t, 1.3, k.d - .5)); x1 = lerp(100, 1180, ap)
    if ap > 0:
        for lw_, op in ((34, 30), (22, 60), (12, 110)): c.line([(100, ay), (x1, ay)], AMBER, lw_, op)
        c.line([(100, ay), (x1, ay)], CREAM, 6)
        c.poly([(x1 + 34, ay), (x1 - 6, ay - 22), (x1 - 6, ay + 22)], CREAM, AMBER, 3)
    c.hud(); c.text(640, 560, 'Layers continue', 40, CREAM, 'serif', 'c', int(255 * prog(k.t, 1.0, 1.6)), INK, 4)
    return c

@scene(33)
def s33(k):
    c = k.cv(INK); z = 1 + .24 * sstep(k.t / (k.d - 1.0)); c.cam(640, 230, z)
    rot = k.t * 2.4; sh = ((k.t * .55) % 1.6) / 1.2 - .1
    c.circ(640, 230, 230, mix(COIN, INK, .85), None, op=120)
    coin(c, 640, 230, 118, rot, sh)
    c.hud(); c.text(640, 62, 'Coins linked to Helike', 44, CREAM, 'serif', 'c', 255, INK, 4)
    u = prog(k.t, 1.0, 2.2); y = 468
    c.line([(200, y), (200 + 880 * u, y)], CREAM, 4)
    c.circ(260, y, 12, TERRA, CREAM, 3); c.text(260, y - 36, '373 BC', 30, CREAM, 'serif', 'c')
    if u > .6:
        a = int(255 * prog(u, .6, 1)); c.circ(880, y, 12, AMBER, CREAM, 3, a)
        for i in range(3): coin(c, 850 + i * 30, y - 44, 15, 0, -1, a)
        c.dash([(280, y - 20), (860, y - 20)], AMBER, 3, 10, 8, a)
    if k.t > 2.2: c.text(640, 536, 'issued decades after 373 BC', 32, AMBER, 'serif', 'c', int(255 * prog(k.t, 2.2, 2.8)), INK, 4)
    return c

@scene(34)
def s34(k):
    w = k.cue(89, 'Wait'); s2 = k.lt(90); cm = k.cue(91, 'coins') - .25
    if k.t < w - .03:
        c = k.cv((6, 10, 16)); return c
    tt = k.t - w
    if k.t < s2:
        c = k.cv(INK); z = 1 + .18 * ease_out(tt / .35); sk = shake(k.t, w, 8, 9, 55)
        c.cam(640, 255, z, sk)
        coin(c, 640, 255, 128, .95, .45)
        c.hud(); c.text(640, 86, 'Wait.', 96, AMBER, 'serif', 'c', 255, INK, 6)
        k.fx['flash'] = max(0, 1 - tt / .2) if tt < .2 else 0
        return c
    def L():
        c = k.cv(UNDER); c.cam(380, 330, 1.0); skyline(c, k.t, dict(water=0))
        c.rect(-300, 200, 1700, 700, TEAL, None, op=140); wave_rig(c, k.t, 330, -300, 1500, TEAL, ybot=900, op=120)
        for i, x in enumerate((100, 330, 560)): c.poly([(x, -100), (x + 80, -100), (x + 200, 560), (x + 30, 560)], CREAM, None, op=26)
        return c.finish()
    def R():
        c = k.cv(vgrad(dark(BROWN, .3), mix(BROWN, AMBER, .3))); c.cam(640, 295, 1.0)
        c.circ(1180, 330, 140, TERRA, None, op=90); c.circ(1180, 340, 80, AMBER, None, op=120)
        c.rect(760, 430, 720, 200, mix(BROWN, INK, .5), None)
        c.poly([(1000, 440), (1130, 440), (1110, 470), (1020, 470)], dark(SAND, .6), INK, 3); c.rect(1030, 470, 70, 60, dark(SAND, .6), INK, 3)
        ph = (k.t * 3.2) % 1.0; ang = 160 - 130 * sstep(prog(ph, .55, .7)) if ph > .5 else 160
        person(c, 860, 500, 1.6, 'man', k.t, 'happy', look=1, armL=40, armR=ang if False else 120 - 90 * (1 if ph > .6 else 0), propR='hammer', seed=3)
        coin(c, 1065, 428, 24, 0)
        if .6 < ph < .85:
            for i in range(6): c.line([(1065, 420), (1065 + 38 * math.cos(i * 1.05 - .3), 420 - 30 * abs(math.sin(i * 1.05)))], AMBER, 3)
        return c.finish()
    li = L(); ri = R(); img = li.copy(); img.paste(ri.crop((640, 0, 1280, 720)), (640, 0))
    d = ImageDraw.Draw(img); gl = prog(k.t, s2, s2 + .3)
    d.rectangle((636, 0, 644, 590), fill=(250, 240, 210))
    c2 = Canvas(DARK); c2.im = img.resize((W * SS, H * SS)); c2.d = aggdraw.Draw(c2.im); c2.hud()
    c2.text(640, 66, "A drowned city can't mint coins.", 38, CREAM, 'serif', 'c', int(255 * prog(k.t, k.lt(91), k.lt(91) + .5)), INK, 4)
    if k.t > cm:
        u = ease_out(prog(k.t, cm, cm + .14)); xx = lerp(-400, 640, u) + (8 * math.sin((k.t - cm) * 50) * math.exp(-(k.t - cm) * 9))
        c2.rect(xx - 270, 270, 540, 86, AMBER, INK, 5); c2.text(xx, 313, 'contradiction?', 56, INK, 'serif', 'c')
    return c2
from PIL import ImageDraw
import aggdraw

@scene(35)
def s35(k):
    gr = vgrad(mix(NAVY, CREAM, .45), mix(CREAM, SAND, .3)); wu = sstep(prog(k.t, 0, k.d * .8))
    c = k.cv(blend_img(gr, DAY, wu)); c.cam(lerp(520, 780, sstep(k.t / k.d)), 295, 1.0)
    st = {0: 'ok', 1: 'cracked', 2: 'ruin', 3: 'ok', 4: 'cracked', 5: 'ok', 6: 'ruin', 7: 'cracked', 8: 'ok'}
    skyline(c, k.t, dict(figs=0), st, lit=wu * .5)
    for (x, wph, kd, pr) in ((410, 0, 'man', 'basket'), (480, 1, 'woman', 'basket'), (610, 2, 'man', 'hammer'), (540, 3, 'child', None)):
        y = gy(x) + 34; ox = 20 * math.sin(k.t * .8 + wph)
        person(c, x + ox, y, .5 + (.0 if kd != 'child' else -.15), kd, k.t, 'neutral', walk=k.t * 3 + wph, armR=40 + 30 * math.sin(k.t * 3 + wph), propR=pr, seed=wph + 1, flip=1 if math.cos(k.t * .8 + wph) > 0 else -1)
    for (x, w_) in ((470, 40), (590, 36)):
        yy = gy(x) + 18; c.poly([(x - w_, yy), (x - w_ * .5, yy - 12), (x, yy - 7), (x + w_ * .6, yy - 14), (x + w_, yy)], dark(CREAM, .25), INK, 2)
    c.hud(); words = [('Damaged.', 'damaged'), ('Abandoned.', 'abandoned'), ('Buried.', 'buried')]
    for i, (t_, w_) in enumerate(words):
        tc = k.cue(95, w_)
        if k.t > tc - .1: c.text(1000, 70 + i * 46, t_, 38, CREAM, 'serif', 'c', int(255 * prog(k.t, tc - .1, tc + .3)), INK, 4)
    tb = k.cue(95, 'buried', end=True)
    if k.t > tb: c.text(1000, 240, 'Partially surviving?', 34, AMBER, 'serif', 'c', int(255 * prog(k.t, tb, tb + .5)), INK, 4)
    return c

def pal(col, v):
    col = C(col); lum = sum(col) / 765; return mix(col, INK if lum < .55 else TERRA, v)
def bubble_pic(c, x, y, stage, t, v):
    c.ell(x, y, 170, 120, pal(CREAM, v), pal(INK, v), 3)
    hx, hy = x - 40, y + 60
    if stage <= 2:
        tilt = 0 if stage == 0 else 10
        c.poly([(hx - 50, hy), (hx + 50, hy - tilt), (hx + 50, hy - 70), (hx - 50, hy - 70)], pal(CREAM, v * .6), pal(INK, v), 3)
        c.rect(hx - 56, hy - 82 - tilt * .5, 112, 14, pal(TERRA, v), pal(INK, v), 2)
        pts = [(hx - 10, hy - 70), (hx - 2, hy - 44), (hx - 18, hy - 22), (hx - 8, hy)] if stage == 0 else [(hx - 20, hy - 70), (hx + 6, hy - 40), (hx - 22, hy - 16), (hx + 8, hy), (hx - 6, hy)]
        c.line(pts, pal(INK, v), 3)
        if stage == 2: c.poly([(hx + 50, hy), (hx + 90, hy - 20), (hx + 140, hy), (hx + 150, hy + 10), (hx + 50, hy + 10)], pal(TEAL, v), pal(INK, v), 2)
    elif stage == 3:
        c.poly([(hx - 50, hy), (hx + 50, hy), (hx + 50, hy - 50), (hx - 50, hy - 50)], pal(CREAM, v * .6), pal(INK, v), 3)
        c.poly([(hx - 120, hy + 10), (hx - 60, hy - 60), (hx, hy - 110), (hx + 70, hy - 70), (hx + 130, hy - 20), (hx + 140, hy + 10)], pal(TEAL, v), pal(INK, v), 3)
    else:
        for i in range(3): c.rect(hx - 60 + i * 44, hy - 40, 38, 40, pal(CREAM, v * .6), pal(INK, v), 2)
        c.poly([(x - 170, y + 90), (x - 150, y - 60), (x - 80, y - 110), (x + 20, y - 100), (x + 120, y - 70), (x + 170, y + 40), (x + 150, y + 100)], pal(TEAL, v), pal(INK, v), 3)
        for i in range(3): c.line([(x - 100 + i * 70, y - 60 + i * 10), (x - 70 + i * 70, y - 20), (x - 100 + i * 70, y + 10)], pal(INK, v), 2)
    for i, rr in enumerate((16, 10, 6)): c.circ(x - 170 + 40 - i * 26 - 20 * 0 if False else x - 150 + i * 0 - i * 24, y + 130 + i * 18, rr, pal(CREAM, v), pal(INK, v), 2) if False else None
@scene(36)
def s36(k):
    tl = k.cue(99, 'legend') - .4; kinds = ['man', 'merchant', 'scholar', 'explorer', 'woman']
    c = k.cv(DARK); cx = lerp(300, 2380, sstep(prog(k.t, 0, tl)))
    c.cam(cx, 295, 1.0)
    for i in range(5):
        X = 300 + i * 520; v = i / 4.0
        if abs(cx - X) > 900: continue
        c.wob = 1.4 * v if v > .3 else 0.0; c.ph = math.floor(k.t * 10) * 1.93
        c.rect(X - 240, 50, 480, 480, pal(mix(NAVY, TEAL, .3) if False else mix(CREAM, SAND, .3), v), pal(INK, v), 4)
        c.rect(X - 240, 440, 480, 90, pal(SAND, v), pal(INK, v), 3)
        bubble_pic(c, X + 40, 230, i, k.t, v)
        if i < 3: person(c, X - 150, 500, 1.15, kinds[i], k.t, 'curious', look=1, armR=90 + 15 * math.sin(k.t * 3 + i), seed=i)
        else: vfig(c, X - 150, 500, 1.0, 'man' if i == 3 else 'woman', k.t, 1, 'point', seed=i)
        c.wob = 0
        lab = ['Greek', 'Roman', 'Medieval', '', ''][i]
        if lab: c.text(X - 150, 80, lab, 28, INK, 'serif', 'c')
    c.hud(); c.text(640, 60, 'How a story becomes a legend', 36, CREAM, 'serif', 'c', int(255 * prog(k.t, k.lt(98), k.lt(98) + .6) * (1 - prog(k.t, tl - 1.2, tl - .4))), INK, 4)
    u = prog(k.t, tl - .8, tl + .3)
    if u > 0:
        ta = math.floor(k.t * 10) / 10; img = legend_img(lambda lc: draw13(lc, 2.0, .5, 1.0, 5.0), ta)
        return Image.blend(finish_frame(K(36, k.t, k.fi), c), img, sstep(u)) if u < 1 else img
    return c

@scene(37)
def s37(k):
    c = k.cv(vgrad((8, 14, 22), (14, 22, 34))); u = k.t / k.d
    c.cam(lerp(720, 590, sstep(u)), 295, 1.0)
    board(c, 640, 320, 600, 380, 4, 0.0, k.t, 1.0)
    c.hud(); c.text(640, 52, 'The honest answer:', 38, AMBER, 'serif', 'c', int(255 * prog(k.t, k.lt(102), k.lt(102) + .5)), INK, 4)
    c.text(640, 96, "we don't know every detail.", 34, CREAM, 'serif', 'c', int(255 * prog(k.t, k.lt(102) + .6, k.lt(102) + 1.1)), INK, 4)
    return c

@scene(38)
def s38(k):
    st = [k.lt(103), k.lt(104), k.lt(105), k.lt(106)]
    c = k.cv(vgrad(dark(NAVY, .1), mix(NAVY, TEAL, .2)))
    conv = sstep(prog(k.t, st[3], st[3] + 2.5)); cx = 640; z = 1.0 + .06 * k.t / k.d
    c.cam(cx, 295, z)
    heads = ['Found', 'Some researchers say', 'Others argue']
    kw = [['Buried', 'Classical remains'], ['Consistent with', 'a destructive event'], ['Does not prove total', 'destruction by tsunami']]
    for i in range(3):
        a = prog(k.t, st[i], st[i] + .7)
        if a <= 0: continue
        x = lerp(230 + i * 410, 640, conv); op = int(255 * a * (1 - conv) ** .6); top = 120
        c.rect(x - 175, top, 350, 360, CREAM, INK, 4, op); c.rect(x - 175, top, 350, 62, NAVY, INK, 4, op)
        c.text(x, top + 31, heads[i], 26 if i else 34, CREAM, 'sans', 'c', op)
        for j, l_ in enumerate(kw[i]): c.text(x, top + 292 + j * 30, l_, 23, INK, 'sans', 'c', op)
        if a > .9 and conv < .3:
            iy = top + 160
            if i == 0:
                c.poly([(x - 110, iy + 50), (x - 40, iy - 10), (x + 40, iy - 10), (x + 110, iy + 50)], mix(SAND, BROWN, .3), INK, 2.5); prop(c, 'trowel', x + 10 + 6 * math.sin(k.t * 4), iy - 4, 1.5, k.t); shard(c, x - 50, iy + 22, .8)
            elif i == 1:
                for r_ in range(3):
                    for q in range(4):
                        if (r_, q) in ((0, 2), (1, 3)): continue
                        c.rect(x - 100 + q * 50, iy - 30 + r_ * 36, 46, 32, SAND, INK, 2)
                c.line([(x - 10, iy - 34), (x + 6, iy), (x - 8, iy + 20), (x + 10, iy + 50)], TERRA, 3.5)
            else:
                strata(c, x - 90, iy - 40, 180, 120, 1.0)
    if conv > .2:
        for i in range(6):
            a_ = i * 1.05 + k.t; qmark(c, 640 + 7 * math.cos(a_) * (1 + conv), 300 + 7 * math.sin(a_), 300, CREAM, int(46 * conv))
    return c

@scene(39)
def s39(k):
    ts = k.lt(110); z0 = k.cue(109, 'beneath') if False else k.lt(109)
    if k.t < ts:
        c = k.cv(vgrad(dark(NAVY, .1), mix(NAVY, TEAL, .2)))
        z = lerp(1.0, 5.0, ease_in(prog(k.t, z0 + .5, ts))); c.cam(640, 440, z)
        sh = sstep(prog(k.t, k.lt(107) + .5, k.lt(108) + 3.0)); coastmap(c, k.t, sh)
        c.hud(); c.line([(300, 60), (380, 60)], INK, 5); c.line([(300, 60), (380, 60)], CREAM, 3)
        c.dash([(300, 104), (380, 104)], TERRA, 4, 10, 8); c.text(400, 60, 'Modern coastline (solid)', 28, CREAM, 'sans', 'l', 255, INK, 3); c.text(400, 104, 'Ancient coastline (dotted)', 28, CREAM, 'sans', 'l', 255, INK, 3)
        al = clamp((k.t - (ts - .45)) / .45); k.fx['fade'] = (CREAM, al) if al > 0 else None
        return c
    c = k.cv(blend_img(DAY, DAWN, .12)); u = (k.t - ts); c.cam(640 - 30 * (1 - sstep(u / 4)), 340, lerp(1.25, 1.0, sstep(u / 3)))
    plain(c, k.t, .8, 0.0)
    al = clamp(1 - u / .45); k.fx['fade'] = (CREAM, al)
    return c

def plain_img(k, fig=None, x=0, glow=0.0, ta=None):
    c = k.cv(blend_img(DAY, DAWN, .12)); c.cam(640, 295, 1.0); plain(c, k.t, .8, glow)
    return c
@scene(40)
def s40(k):
    slot = k.d / 4.0; i = min(3, int(k.t / slot)); u = (k.t - i * slot)
    def draw(j):
        c = k.cv(blend_img(DAY, DAWN, .12)); c.cam(640, 295, 1.0); plain(c, k.t, .8, .5 + .12 * math.sin(k.t * 1.3))
        tt = k.t; yb = 436
        look = math.sin(tt * .9 + j) * 1.0; doubt = 'doubt' if ((tt - j * slot) / slot) > .65 else 'curious'
        if j == 0: person(c, 520, yb, 1.8, 'trav', tt, doubt, look=look, propL='staff', armR=14, seed=7)
        elif j == 1: person(c, 600, yb, 1.8, 'scholar', tt, doubt, look=look, propR='tablet', armR=50, seed=2)
        elif j == 2: person(c, 560, yb, 1.8, 'explorer', tt, doubt, look=look, propR='map', armR=45, seed=5)
        else:
            person(c, 500, yb, 1.8, 'crew', tt, doubt, look=look, armR=40, seed=3); person(c, 650, yb, 1.8, 'phys', tt, doubt, look=-look, propL='instr', armL=50, seed=4, flip=-1)
        return c
    c = draw(i)
    if u < 1.0 and i > 0:
        return Image.blend(draw(i - 1).finish(), c.finish(), sstep(u))
    if i == 0 and u < .8: k.fx['fade'] = (NAVY, 1 - u / .8)
    return c

@scene(41)
def s41(k):
    u = k.t / k.d; c = k.cv(blend_img(DUSK, NIGHT, .6 * sstep(prog(u, 0, .6))))
    c.cam(lerp(560, 640, sstep(u)), lerp(330, 295, sstep(u)), lerp(1.4, 1.0, sstep(u)))
    fadeo = prog(u, .5, .9)
    skyline(c, k.t, dict(houses=1 - fadeo, roofs=1 - prog(u, .45, .8), streets=1 - fadeo, figs=1 - prog(u, 0, .3), temple=1 - prog(u, .6, 1.0), ships=1 - prog(u, .3, .7),
                         plants=prog(u, .2, .9), water=1), lit=1 - prog(u, 0, .7))
    if u > .62:
        dc = k.cv(blend_img(DAWN, DAY, .15)); dc.cam(640, 295, 1.0); plain(dc, k.t, 1.0, 0.0)
        return Image.blend(c.finish(), dc.finish(), sstep(prog(u, .62, .95)))
    return c

@scene(42)
def s42(k):
    st = [0, k.lt(117) + (k.le(117) - k.lt(117)) * .5, k.lt(118), k.cue(118, 'worshipped') - .3, k.lt(119)]
    b = k.beat(st); X = [640 + i * 1400 for i in range(5)]
    tu = k.cue(119, 'existed') - .3; fin = k.cue(119, 'existed', end=True) + .2
    cx = strip_cam(k.t, [s - .15 for s in st], X); zz = lerp(1.4, 1.0, sstep((k.t - st[max(b, 0)]) / (3.0 if b < 4 else 8.0)))
    def build():
        c = k.cv(GOLD); c.cam(cx, 295, zz)
        if cx < 2000:    # baker at dawn
            ox = X[0]; c.rect(ox - 700, -100, 1400, 800, mix(NAVY, AMBER, .45)); c.rect(ox - 700, 450, 1400, 300, mix(BROWN, INK, .3))
            c.poly([(ox - 330, 450), (ox - 330, 250), (ox - 200, 180), (ox - 70, 250), (ox - 70, 450)], mix(SAND, TERRA, .45), INK, 3); c.poly([(ox - 280, 450), (ox - 280, 320), (ox - 200, 280), (ox - 120, 320), (ox - 120, 450)], (60, 30, 20), INK, 3)
            for r_, o in ((120, 40), (80, 70), (50, 110)): c.circ(ox - 200, 400, r_, AMBER, None, op=o)
            c.rect(ox + 20, 400, 360, 70, BROWN, INK, 3)
            for i in range(5): c.ell(ox + 70 + i * 60, 392, 24, 11, mix(AMBER, TERRA, .35), INK, 2)
            c.rect(ox + 140, 120, 120, 150, mix(AMBER, CREAM, .6), INK, 3)
            person(c, ox + 150, 520, 1.7, 'baker', k.t, 'happy', look=-.5, armL=50, armR=60, seed=1)
        if 700 < cx < 3000:   # merchant counting coins
            ox = X[1]; c.rect(ox - 700, -100, 1400, 800, mix(SAND, AMBER, .45)); c.rect(ox - 700, 450, 1400, 300, mix(BROWN, SAND, .3))
            c.poly([(ox - 330, 100), (ox + 330, 100), (ox + 360, 190), (ox - 360, 190)], TERRA, INK, 3)
            for i in range(6): c.line([(ox - 300 + i * 120, 100), (ox - 320 + i * 124, 190)], CREAM, 12)
            c.rect(ox - 300, 380, 600, 80, BROWN, INK, 3)
            for i in range(4):
                for j in range(1 + i): coin(c, ox - 180 + i * 70, 376 - j * 7, 22, 1.25 if False else 1.5)
            person(c, ox + 160, 520, 1.7, 'merchant', k.t, 'happy', look=-1, armL=60, armR=55 + 6 * math.sin(k.t * 4), seed=2)
        if 2100 < cx < 4400:   # children running
            ox = X[2]; c.rect(ox - 700, -100, 1400, 800, mix(AMBER, CREAM, .5)); c.rect(ox - 700, 460, 1400, 300, mix(SAND, BROWN, .3))
            for i in range(3): c.rect(ox - 600 + i * 420, 170, 260, 290, CREAM, INK, 3); c.rect(ox - 610 + i * 420, 158, 280, 16, TERRA, INK, 3)
            for i in range(3): person(c, ox - 280 + ((k.t * 130 + i * 190) % 760) - 100, 540 - (i % 2) * 20, 1.0, 'child', k.t, 'happy', walk=k.t * 8 + i, armL=30 + 20 * math.sin(k.t * 8 + i), armR=40, seed=i, flip=1)
        if 3500 < cx < 5800:   # family at shrine
            ox = X[3]; c.rect(ox - 700, -100, 1400, 800, mix(NAVY, AMBER, .4)); c.rect(ox - 700, 460, 1400, 300, mix(BROWN, INK, .25))
            c.rect(ox - 120, 230, 240, 230, SAND, INK, 3); c.rect(ox - 140, 210, 280, 26, light(SAND, .25), INK, 3); trident(c, ox, 320, 2.0, dark(SAND, .6), 3.5)
            fl = 1 + .1 * math.sin(k.t * 9); c.circ(ox, 190, 54 * fl, AMBER, None, op=60); c.poly([(ox - 16, 210), (ox, 150 - 10 * fl), (ox + 16, 210)], AMBER, INK, 2)
            person(c, ox - 230, 530, 1.6, 'man', k.t, 'neutral', look=1, armL=70, armR=70, seed=3); person(c, ox + 230, 530, 1.6, 'woman', k.t, 'neutral', look=-1, armL=70, armR=70, seed=4, flip=-1); person(c, ox + 120, 540, 1.0, 'child', k.t, 'neutral', look=-1, armL=70, armR=70, seed=5, flip=-1)
        if cx > 4800:
            ox = X[4]; fld = False
            c.L(1.0); c.push(0, 0, 1, X[4] - 640, 0)
            plain(c, k.t, .3, 0.0); c.rect(540, 400, 460, 28, dark(SAND, .25), INK, 3)
            for j, (sx, ss) in enumerate(((100, .9), (260, .7), (380, .8))): c.L(.6); ship(c, sx, 392, ss, j == 1, k.t, j); c.L(1.0)
            tn = k.t > tu; person(c, 800, 428, 1.5, 'woman', k.t, 'curious' if tn else 'neutral', look=0 if tn else -1, back=not tn, armL=12, armR=12, seed=6, flip=-1 if not tn else 1)
            c.pop()
        return c
    c = build()
    if b == 4 and k.t > fin - .2:
        fc = k.cv(GOLD); fc.cam(cx, 295, zz); fc.push(0, 0, 1, X[4] - 640, 0); plain(fc, k.t, 1.0, 0.0); fc.pop()
        return Image.blend(c.finish(), fc.finish(), sstep(prog(k.t, fin - .2, fin + 1.6)))
    return c

@scene(43)
def s43(k):
    end = k.lt(121); c = k.cv(GOLD); u = k.t / k.d
    zz = 1.0 if k.t < end else lerp(1.0, 1.3, sstep((k.t - end) / 2.5))
    cxx = 560 + 150 * math.sin(u * 2.4) if k.t < end else lerp(640, 720, sstep((k.t - end) / 2.5))
    c.cam(cxx, 330, zz)
    plain(c, k.t, .8, 0.0, sea=True)
    c.rect(400, 440, 520, 90, mix(BROWN, INK, .5), INK, 3)
    for i in range(3): c.rect(440 + i * 150, 452, 120, 16, SAND, INK, 2)
    if k.t < end:
        person(c, 500, 470, 1.35, 'arch', k.t, 'curious', look=.5, armR=60 + 15 * math.sin(k.t * 5), propR='brush', armL=20, seed=1)
        person(c, 720, 470, 1.35, 'phys', k.t, 'neutral', look=-.6, armL=70, propL='tablet', armR=30, seed=2)
        person(c, 880, 470, 1.35, 'crew', k.t, 'happy', look=-1, armR=70, propR='camera', armL=20, seed=3, flip=-1)
    else:
        person(c, 640, 480, 1.5, 'arch', k.t, 'curious', back=True, armL=14, armR=14, seed=1)
    return c

@scene(44)
def s44(k):
    t1, t2, t3 = k.lt(122), k.lt(123), k.lt(124); tb = k.cue(124, 'found', end=True) + .3
    c = k.cv(DARK); c.cam(640, 295, 1.0 + .05 * k.t / k.d)
    lon0 = kf(k.t, [(0, (-120,)), (t1 + .6, (-95,)), (t2 + .8, (60,)), (t3 + .9, (125,)), (tb + .3, (125,)), (k.d - .3, (22,))])[0]
    dots = [(-100, 40, pop(prog(k.t, t1 + .2, t1 + .7), 0) if k.t > t1 + .2 else 0), (75, 30, pop(prog(k.t, t2 + .2, t2 + .7), 0) if k.t > t2 + .2 else 0), (135, -26, pop(prog(k.t, t3 + .2, t3 + .7), 0) if k.t > t3 + .2 else 0)]
    dots = [(a, b_, clamp(prog(k.t, tt_, tt_ + .5))) for (a, b_, _), tt_ in zip(dots, (t1 + .2, t2 + .2, t3 + .2))]
    c.circ(640, 290, 215, TEAL, None, op=26)
    dd = [(a, b_, u_) for a, b_, u_ in dots]
    gl = globe(c, 640, 290, 190, lon0, 26, sea=mix(NAVY, TEAL, .35), land=mix(NAVY, TEAL, .6), dots=dd)
    if k.t > tb + .5 and lon0 < 60:
        x, y, z = proj(22, 38.3, lon0, 26, 190)
        if z > 0: helike_marker(c, 640 + x, 290 + y, .8, (k.t * .8) % 1, op=int(255 * prog(k.t, tb + .5, tb + 1.2)))
    c.hud(); c.text(640, 548, 'How many are still waiting?', 34, AMBER, 'serif', 'c', int(255 * prog(k.t, t3, t3 + .6)), INK, 4)
    return c

@scene(45)
def s45(k):
    t6, t7 = k.lt(126), k.lt(127); te = k.cue(127, 'hidden', end=True)
    c = k.cv(DAWN); u = k.t / k.d; c.cam(640, 420, 1.0 + .12 * u)
    glow = sstep(prog(k.t, .5, 1.6)) * (1 - sstep(prog(k.t, te - 1.3, te)))
    plain(c, k.t, .9, glow, mist=1 - prog(k.t, 0, 3.4))
    c.hud(); c.text(640, 70, "The past isn't gone.", 46, CREAM, 'serif', 'c', int(255 * prog(k.t, t6, t6 + .5)), INK, 4)
    c.text(640, 128, "It's just hidden.", 46, AMBER, 'serif', 'c', int(255 * prog(k.t, t7, t7 + .5)), INK, 4)
    k.fx['fade'] = (INK, prog(k.t, k.d - .13, k.d))
    return c

@scene(46)
def s46(k):
    c = k.cv(NIGHT); c.cam(640, 295, 1.0 + .03 * math.sin(k.t * .5))
    c.hud()
    c.text(640, 80, 'THE VANISHED CITY OF HELIKE', 46, CREAM, 'serif', 'c', 255, INK, 4)
    c.text(640, 150, 'SOURCES', 22, AMBER, 'sans', 'c', 255, INK, 3, spacing=10)
    for i, t_ in enumerate(('Stiros, 2021, Seismological Research Letters', 'The Helike Project: Dora Katsonopoulou and Steven Soter', 'Pausanias, Greek traveler')):
        c.text(640, 198 + i * 40, t_, 26, CREAM, 'sansr', 'c', int(255 * prog(k.t, .5 + i * .5, 1.0 + i * .5)), INK, 3)
    c.text(640, 380, 'Thanks for watching', 40, CREAM, 'serif', 'c', int(255 * prog(k.t, 2.4, 3.0)), INK, 4)
    c.text(640, 436, 'Next video: coming soon', 28, AMBER, 'sans', 'c', int(255 * prog(k.t, 3.2, 3.8)), INK, 3)
    c.L(1.0); wave_rig(c, k.t, 480, -300, 1600, TEAL, amp=.9, ybot=900, depth_cols=[(10, 24, 36), (14, 40, 52), (18, 56, 66)])
    k.fx['fade'] = (INK, 1 - prog(k.t, 0, .7))
    return c
