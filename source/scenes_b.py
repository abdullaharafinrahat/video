"""Scenes 16-30"""
from scenelib import *
from scenes_a import draw12, draw13, draw14
SC = {}
def scene(n):
    def d(f): SC[n] = f; return f
    return d
def plate(c, x, y, w, h, l1, l2, op=255):
    c.rect(x - w / 2, y - h / 2, w, h, CREAM, INK, 3, op); c.rect(x - w / 2, y - h / 2, 10, h, AMBER, INK, 2, op)
    c.text(x + 5, y - 12, l1, 24, INK, 'sans', 'c', op); c.text(x + 5, y + 16, l2, 20, TEAL, 'sansr', 'c', op)
def grain_post(amt=7):
    def f(im):
        a = np.asarray(im).astype(np.float32); a += grain(seed=np.random.randint(0, 50))[..., None] * amt / 4
        a = a * np.array([1.0, .96, .86]) + np.array([6, 3, 0]); return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    return f

@scene(16)
def s16(k):
    c = k.cv(vgrad(dark(NAVY, .3), dark(BROWN, .55))); u = k.t / k.d
    c.cam(lerp(590, 690, u), lerp(270, 310, u), 1 + .12 * u)
    for i in range(12): c.line([(-300, i * 70 - 100), (1700, i * 70 - 60)], dark(BROWN, .6), 2, 120)
    pins = min(4, int(k.t / (k.d / 4.4)) + 1)
    pos = board(c, 640, 290, 620, 420, pins, prog(k.t, k.d * .2, k.d * .9), k.t)
    for i, nm in enumerate(('map', 'manuscript', 'coin', 'shard')):
        if i < pins and k.t > (i + .5) * k.d / 4.4:
            x, y = pos[nm]; c.text(x, y + (62 if nm != 'shard' else 52), f'CLUE {i + 1}', 20, INK, 'sans', 'c', 255, CREAM, 3)
    return c

@scene(17)
def s17(k):
    st = [0, k.lt(37), k.lt(38), k.lt(39), k.cue(39, 'water') - .6]; b = k.beat(st)
    c = k.cv(DARK)
    walkx = lerp(1750, 3250, sstep(prog(k.t, st[2], st[3] + .3)))
    cx = 640 if b < 2 else (walkx + 120 if b == 2 else lerp(3250 + 120, 3600, sstep(prog(k.t, st[3], st[4]))))
    if b < 2: cx = strip_cam(k.t, [0], [640])
    if b == 2: cx = lerp(1000, walkx + 150, sstep(prog(k.t, st[2], st[2] + .6)))
    cy = 295 + 520 * sstep(prog(k.t, st[4], k.d - .3))
    c.cam(cx, cy, 1.0 + .06 * sstep(prog(k.t, st[1], st[2])))
    if cx < 1300:
        c.rect(-200, -100, 1500, 800, mix(NAVY, BROWN, .35)); c.rect(-200, 430, 1500, 300, mix(BROWN, INK, .4))
        c.rect(150, 410, 1000, 26, mix(BROWN, SAND, .3), INK, 3)
        hot = 2 if b >= 1 else -1
        for i, (x, y, r_) in enumerate(((260, 250, -4), (480, 300, 3), (700, 230, -2), (930, 300, 4), (1090, 240, -3))):
            sc = 1.0 + (.35 if i == hot else 0) * sstep(prog(k.t, st[1], st[1] + .8)) if b >= 1 else 1.0
            if i == hot and b >= 1: c.circ(x, y, 150, AMBER, None, op=int(60 * sstep(prog(k.t, st[1], st[1] + .8))))
            manuscript(c, x, y, 130 * sc, 170 * sc, .35 + (.4 if b >= 1 and i != hot else 0), 6, i, tilt=r_)
            helike_marker(c, x, y + 8, .6 * sc)
        person(c, 140, 440, 1.3, 'scribe', k.t, 'curious', look=1, armL=50, armR=30, seed=4, flip=1)
    if cx > 1000:
        sh = 3350
        vband(c, 1200, 4600, -300, 470, mix(AMBER, CREAM, .5), mix(CREAM, TEAL, .35), 10)
        c.L(.3); c.poly([(1200, 380), (1700, 240), (2300, 330), (2900, 230), (3500, 330), (4200, 250), (4600, 400), (1200, 420)], mix(TEAL, CREAM, .5), None); c.L(.6)
        c.poly([(1200, 420), (1800, 330), (2400, 400), (3000, 340), (3400, 420), (3400, 480), (1200, 480)], mix(TEAL, AMBER, .3), INK, 2); c.L(1.0)
        c.poly([(1200, 470), (sh, 470), (sh + 80, 540), (sh + 150, 900), (1200, 900)], SAND, INK, 3)
        c.poly([(1200, 470), (sh, 470), (sh + 30, 492), (1200, 492)], mix(TEAL, AMBER, .4), None)
        for i in range(40): c.line([(1250 + i * 60, 500), (1262 + i * 60, 486)], dark(SAND, .3), 2)
        c.rect(sh + 60, 470, 1400, 700, mix(TEAL, NAVY, .1), None)
        vband(c, sh + 80, 4800, 470, 1160, mix(TEAL, CREAM, .1), mix(NAVY, TEAL, .2), 10)
        wave_rig(c, k.t, 470, sh + 60, 4800, TEAL, ybot=1160, amp=.8, op=170)
        for i in range(5): c.poly([(sh + 200 + i * 130, 470), (sh + 260 + i * 130, 470), (sh + 420 + i * 130 + 0, 1100), (sh + 300 + i * 130, 1100)], CREAM, None, op=22)
        for (x, y_, h) in ((3560, 880, 140), (3760, 900, 100), (3940, 870, 150), (3660, 960, 60)):
            c.rect(x, y_, 26, h, mix(SAND, TEAL, .55), None, op=120); c.rect(x - 8, y_ - 6, 42, 8, mix(SAND, TEAL, .55), None, op=120)
        c.poly([(3520, 1000), (4300, 1000), (4300, 1100), (3520, 1100)], mix(SAND, TEAL, .6), None, op=130)
        for j, wx in enumerate(range(1500, 3250, 280)):
            c.rect(wx + 60, 400, 6, 70, BROWN, None)
        if b >= 2:
            px = walkx; moving = k.t < st[3] + .3 and sstep(prog(k.t, st[2], st[3] + .3)) < .995
            person(c, px, 468, 1.25, 'trav', k.t, 'curious' if not moving else 'neutral', look=0, walk=k.t * 5 if moving else 0, armL=12, armR=14, propL='staff', seed=7,
                   lean=7 if (b >= 3 and not moving) else 0)
        c.L(1.4)
        for i in range(10): c.poly([(1300 + i * 330, 640), (1330 + i * 330, 560), (1380 + i * 330, 640)], mix(TEAL, AMBER, .3), INK, 2)
        c.L(1.0)
    if b == 2:
        a_ = prog(k.t, st[2] + .2, st[2] + .8); c.hud(); c.text(640, 70, 'Pausanias', 52, CREAM, 'serif', 'c', int(255 * a_), INK, 4)
        c.text(640, 118, 'Greek traveler, centuries later', 28, AMBER, 'sans', 'c', int(255 * a_), INK, 3)
    return c

@scene(18)
def s18(k):
    c = k.cv(DARK); u = sstep(prog(k.t, .6, k.d - .4)); cy = lerp(170, 650, u)
    c.cam(640, cy, lerp(1.35, 1.0, u))
    c.push(0, 0, 1, 0, 300); sunken_street(c, k.t, silt=.3, plants=0, rays=1.0); c.pop()
    vband(c, -300, 1600, -500, 300, mix(AMBER, CREAM, .55), mix(CREAM, TEAL, .4), 8)
    wave_rig(c, k.t, 300, -300, 1600, TEAL, amp=1.8, ybot=900, op=95, speed=.7)
    c.line([(x, 300 + 6 * math.sin(x / 60 + k.t * 1.5)) for x in range(-300, 1600, 40)], CREAM, 3, 180)
    amp = 16 * math.exp(-((cy - 320) / 140) ** 2)
    k.fx['post'] = lambda im: wavy_rows(im, amp, k.t) if amp > .5 else im
    return c

@scene(19)
def s19(k):
    st = [0, k.lt(44), k.lt(45), k.lt(46)]; b = k.beat(st)
    if b == 0:
        c = k.cv(DARK); c.cam(640, 520, 1.0 + .04 * k.t / st[1])
        silt = prog(k.t, .2, st[1] * .55); pl = prog(k.t, st[1] * .35, st[1] * .95)
        c.push(0, 0, 1, 0, 0); sunken_street(c, k.t, silt=.2 + silt * .8, plants=pl, rays=1 - silt * .7); c.pop()
        c.rect(-300, -300, 1900, 1300, mix(NAVY, TEAL, .3), None, op=int(255 * prog(k.t, st[1] * .6, st[1] - .05)))
        return c
    c = k.cv(vgrad(dark(NAVY, .2), mix(NAVY, TEAL, .35))); sc = 2.2; ox, oy = 640 - 232 * sc, 295 - 264 * sc
    c.cam(640, 295, 1 + .05 * (k.t - st[1]) / 8)
    mk = greece(c, ox, oy, sc, hi=.8)
    tf = k.cue(45, 'water', end=True) - .3
    if k.t < tf: al = 1.0
    else: al = clamp(1 - prog(k.t, tf, tf + 1.3)) * (.55 + .45 * (math.sin(k.t * 38) > -.2))
    if al > .02: helike_marker(c, mk[0], mk[1], 1.2, 0, op=int(255 * al))
    if b >= 3:
        u = pop(prog(k.t, st[3], st[3] + .35), .5); c.text(mk[0], mk[1] - 20, '?', 250 * u, AMBER, 'serif', 'c', 255, INK, 6)
        c.hud(); c.text(640, 76, 'Where was Helike?', 52, CREAM, 'serif', 'c', int(255 * prog(k.t, st[3], st[3] + .6)), INK, 4)
    return c

@scene(20)
def s20(k):
    cue = k.cue(48, '1988'); st = [0, k.lt(48), cue - 3.6]; b = k.beat(st)
    c = k.cv(vgrad(mix(SAND, BROWN, .3), mix(BROWN, INK, .4))); k.fx['post'] = grain_post(8)
    if b == 0:
        c.cam(640 + 14 * k.t, 295, 1 + .02 * k.t)
        c.rect(-100, -100, 1500, 520, mix(CREAM, SAND, .5)); c.rect(-100, 410, 1500, 400, mix(BROWN, INK, .35))
        c.rect(120, 80, 180, 120, mix(NAVY, TEAL, .5), INK, 3); c.line([(130, 160), (290, 120)], light(TEAL, .5), 3)
        desk(c, 100, 1200, 400)
        for i, (x, y, r_) in enumerate(((330, 380, -3), (520, 384, 2), (720, 376, -2))):
            c.poly([(x - 90, y), (x + 90, y + r_), (x + 90, y + 18 + r_), (x - 90, y + 16)], CREAM, INK, 2)
        mini_map(c, 520, 372, 150, 22)
        c.rect(820, 340, 90, 60, dark(TEAL, .2), INK, 2.5); c.rect(930, 354, 70, 46, dark(SAND, .4), INK, 2.5)
        person(c, 420, 400, 1.55, 'crew', k.t, 'curious', look=1, armL=30, armR=70 + 8 * math.sin(k.t * 2), seed=1)
        person(c, 1020, 400, 1.55, 'phys', k.t, 'curious', look=-1, armL=60, armR=20, propR='instr', seed=2, flip=-1)
    elif b == 1:
        c.cam(2040 - 40 + 20 * (k.t - st[1]), 295, 1 + .03 * (k.t - st[1]))
        ox = 2040; vband(c, ox - 700, ox + 700, -100, 400, mix(AMBER, CREAM, .5), mix(CREAM, TEAL, .3), 8)
        c.rect(ox - 700, 380, 1400, 400, mix(TEAL, NAVY, .1), None); wave_rig(c, k.t, 392, ox - 700, ox + 700, TEAL, ybot=800, amp=.8)
        c.rect(ox - 700, 390, 520, 40, dark(SAND, .35), INK, 3); c.rect(ox - 700, 430, 520, 400, dark(SAND, .5), None)
        boat_side(c, ox + 120, 420, 1.5, k.t)
        u = prog(k.t, st[1] + .2, st[2] - .3)
        for i in range(3): c.rect(ox - 220 + i * 70, 366 - (i % 2) * 24, 52, 42 + (i % 2) * 24, dark(SAND, .45), INK, 2.5)
        person(c, lerp(ox - 330, ox - 130, u), 392, 1.4, 'crew', k.t, 'happy', walk=k.t * 5 if u < 1 else 0, propR='instr', armR=60, armL=20, seed=3)
    else:
        c.cam(3440, 295, 1 + .04 * (k.t - st[2]) / 4)
        ox = 3440; c.rect(ox - 700, -100, 1400, 800, mix(CREAM, SAND, .4)); c.rect(ox - 700, 470, 1400, 400, mix(BROWN, INK, .3))
        pw, ph_ = 330, 400; x0, y0 = ox - pw / 2, 70
        c.rect(x0 - 8, y0 - 8, pw + 16, ph_ + 16, dark(SAND, .4), INK, 3); c.rect(x0, y0, pw, 60, TERRA, INK, 3)
        fl = [cue - 2.8, cue - 2.0, cue - 1.2, cue - .45]
        def grid(cl, h):
            c.rect(x0, y0 + 60, pw, h, CREAM, INK, 2) if h > 2 else None
            for r in range(5):
                for q in range(7):
                    if 60 + r * 52 + 40 < h + 60: c.rect(x0 + 12 + q * 44, y0 + 72 + r * 52, 34, 40, None, mix(CREAM, INK, .35), 1.2)
        newp = (sum(1 for f in fl if k.t > f + .35) )
        c.rect(x0, y0 + 60, pw, ph_ - 60, CREAM, INK, 2)
        if newp >= 4: c.text(ox, y0 + 60 + (ph_ - 60) / 2, '1988', 92, INK, 'serif', 'c')
        else: grid(CREAM, ph_ - 60)
        for f in fl:
            if f < k.t < f + .35:
                u = (k.t - f) / .35; hh = (ph_ - 60) * math.cos(u * math.pi / 2)
                c.rect(x0, y0 + 60, pw, hh, light(SAND, .4), INK, 2); grid(CREAM, hh)
        if k.t > cue + .3:
            c.hud(); c.text(640, 470 + 56, '1988: The Helike Project begins', 34, CREAM, 'serif', 'c', int(255 * prog(k.t, cue + .3, cue + .9)), INK, 4)
    return c

@scene(21)
def s21(k):
    n1 = k.cue(49, 'Dora'); n2 = k.cue(49, 'Steven')
    c = k.cv(vgrad(mix(NAVY, TEAL, .4), mix(NAVY, BROWN, .3)))
    cx = lerp(580, 700, sstep(k.t / k.d)); c.cam(cx, 295, 1.0 + .04 * (k.t / k.d))
    c.rect(-100, -100, 1500, 560, mix(NAVY, TEAL, .35)); c.rect(-100, 440, 1500, 300, mix(BROWN, INK, .45))
    for i in range(3): c.rect(120 + i * 400, 150 - (i % 2) * 20, 150, 110, CREAM, INK, 2.5); c.line([(130 + i * 400, 220), (260 + i * 400, 180), (230 + i * 400, 240)], TEAL, 2)
    c.rect(560, 120, 140, 150, light(SAND, .2), INK, 2.5)
    person(c, 420, 505, 2.0, 'arch', k.t, 'curious', look=.6, armL=60, armR=30, propR='trowel', seed=1)
    person(c, 860, 505, 2.0, 'phys', k.t, 'happy', look=-.6, armL=20, armR=55, propR='instr', seed=2, flip=-1)
    for (x, n, l1, l2) in ((420, n1, 'Dora Katsonopoulou', 'Archaeologist'), (860, n2, 'Steven Soter', 'Physicist')):
        u = ease_out(prog(k.t, n - .15, n + .45))
        if u > 0: plate(c, lerp(x - 500 if x < 600 else x + 500, x, u), 105, 380, 78, l1, l2)
    return c

@scene(22)
def s22(k):
    sw = k.lt(52); c = k.cv(vgrad(mix(TEAL, NAVY, .35), mix(TEAL, NAVY, .65)))
    if k.t < sw:
        c.cam(640, 295, 1 + .1 * k.t / sw)
        for i in range(7): c.poly([(640 + 520 * math.cos(a * .35 + i * .1) * (1 - i * .12), 295 + 250 * math.sin(a * .35 + i * .1) * (1 - i * .12) + 12 * math.sin(a + i)) for a in range(19)], None, mix(TEAL, CREAM, .1 + i * .02), 1.6, 120)
        u = prog(k.t, .3, sw + 1.2) * .999
        def pos(uu):
            lane = min(3, int(uu * 4)); f = uu * 4 - lane
            xx = 200 + 880 * f if lane % 2 == 0 else 1080 - 880 * f; ly = 150 + lane * 105
            if f > .93 and lane < 3: ly = lerp(ly, 150 + (lane + 1) * 105, sstep((f - .93) / .07))
            return xx, ly
        for q in range(0, int(u * 120)):
            x1, y1 = pos(q / 120 * 1.0); c.circ(x1, y1, 22, mix(TEAL, CREAM, .12), None, op=70)
        bx, by = pos(u); pu = pos(max(0, u - .015)); dx, dy = bx - pu[0], by - pu[1]; n = math.hypot(dx, dy) or 1; dx, dy = dx / n, dy / n
        fx_, fy_ = bx - dx * 90, by - dy * 90
        c.line([(bx, by), (fx_, fy_)], CREAM, 2)
        for i in range(3):
            r = ((k.t * .9 + i / 3) % 1); c.circ(fx_, fy_, 20 + 100 * r, None, AMBER, 3, int(220 * (1 - r)))
        c.poly([(fx_, fy_ - 8), (fx_ + 8, fy_), (fx_, fy_ + 8), (fx_ - 8, fy_)], AMBER, INK, 2)
        c.poly([(bx + dx * 40, by + dy * 40), (bx - dy * 14, by + dx * 14), (bx - dx * 30 - dy * 14, by - dy * 30 + dx * 14), (bx - dx * 30 + dy * 14, by - dy * 30 - dx * 14), (bx + dy * 14, by - dx * 14)], CREAM, INK, 2.5)
        c.circ(bx, by, 5, TERRA, INK, 1.5)
    else:
        c.cam(640, 295, 1.0 + .06 * (k.t - sw) / 4); monitor(c, 240, 90, 800, 380, prog(k.t, sw, k.d - .2), False, k.t)
        person(c, 140, 520, 1.1, 'phys', k.t, 'curious', look=1, armR=30, seed=3)
    tag(c, 640, 52, 'Sonar survey of the seabed', 28)
    return c

@scene(23)
def s23(k):
    sw = k.lt(54); c = k.cv(vgrad(mix(NAVY, TEAL, .3), mix(NAVY, BROWN, .3)))
    cx = strip_cam(k.t, [0, sw - .2], [640, 2040]); c.cam(cx, 295, 1.0 + .06 * k.t / k.d)
    if cx < 1400:
        c.rect(-100, 440, 1500, 300, mix(BROWN, INK, .45)); c.rect(150, 90, 300, 200, dark(NAVY, .2), INK, 3); c.line([(160, 220), (440, 220)], (120, 170, 130), 3)
        sc_ = 160 + 8 * math.sin(k.t * 7)
        person(c, 640, 540, 2.4, 'phys', k.t, 'doubt', look=-.8 + .3 * math.sin(k.t * 3), armL=15, armR=sc_ if False else 150 + 12 * math.sin(k.t * 6), seed=2)
    if cx > 700:
        ox = 2040; c.rect(ox - 700, -100, 1400, 800, mix(NAVY, TEAL, .25)); monitor(c, ox - 400, 100, 800, 360, 1.0, True, k.t)
        if k.t > sw + 1.4: c.rect(ox - 400, 100, 800, 360, dark(NAVY, .3), None, op=int(120 * prog(k.t, sw + 1.4, sw + 2)))
    if k.t > sw + 1.0:
        c.hud(); c.text(640, 70, 'No city found.', 54, CREAM, 'serif', 'c', int(255 * prog(k.t, sw + 1.0, sw + 1.5)), INK, 4)
    return c

@scene(24)
def s24(k):
    st = [0, k.lt(56), k.lt(57), k.lt(58)]; b = k.beat(st); X0, Wd, Hh, YB = 80, 1120, 330, 560
    c = k.cv(vgrad(mix(NAVY, TEAL, .22), dark(NAVY, .3)))
    c.cam(lerp(560, 700, sstep(k.t / k.d)), 295, 1.0)
    r2 = .55 + .22 * sstep(prog(k.t, st[2] + .3, st[3] - .4)); r3 = r2 + .23 * sstep(prog(k.t, st[3] + .3, k.d - 2.0)); r = r3
    sink = 10 * sstep(prog(k.t, st[1], st[2]))
    top = YB - r * Hh
    c.push(0, 0, 1, 0, sink)
    strata(c, X0, YB - Hh, Wd, Hh, r, 0, only=(0, 2))
    c.pop()
    c.push(0, 430, .45, 110, YB - .55 * Hh - 430 + sink)
    skyline(c, k.t, dict(water=0, figs=1))
    c.pop()
    # sea at the right, rising as the land sinks
    sea_top = 372 - 22 * sstep(prog(k.t, st[1], st[2]))
    c.rect(560, sea_top, 640, YB - .55 * Hh + sink - sea_top + 2, TEAL, None, op=190); wave_rig(c, k.t, sea_top, 560, 1200, TEAL, ybot=int(YB - .55 * Hh + sink), amp=.4)
    c.push(0, 0, 1, 0, sink); strata(c, X0, YB - Hh, Wd, Hh, r, 1.0 if r > .99 else 0, only=(2, 4)); c.pop()
    if b == 2 or (b == 3 and r < .99):
        for i in range(5):
            ph = (k.t * .7 + i * .2) % 1
            c.line([(900 + i * 24 - 150 * ph, 110 + 250 * ph), (900 + i * 24 - 160 * ph - 10, 110 + 250 * ph + 30)], mix(SAND, BROWN, .4), 6, int(255 * (1 - ph)))
        c.poly([(1100, 100), (960, 100), (900, 80), (1000, 60)], mix(TEAL, SAND, .3), INK, 2)
    c.hud(); tag(c, 640, 58, ['What if the land changed?', 'What if the city hadn\'t sunk into open sea?', 'What if the land itself had changed?', 'Sealed beneath the ground?'][max(0, b)] if False else ('What if the land itself had changed?' if b >= 2 else 'The city on the shoreline'), 30)
    return c

@scene(25)
def s25(k):
    st = [0, k.lt(60), k.cue(61, 'drilling'), k.cue(61, 'geological'), k.cue(61, 'geophysical')]; b = k.beat(st)
    c = k.cv(DAY)
    if b == 0:
        c = k.cv(vgrad(dark(NAVY, .3), dark(NAVY, .1))); c.cam(640, 295, 1 + .5 * sstep(k.t / st[1]))
        monitor(c, 240, 90, 800, 380, 1.0, False, k.t)
    else:
        u = k.t - st[1]; c.cam(640, 295, lerp(1.3, 1.0, sstep(u / 2.0)) if b == 1 else 1.0 + .03 * (k.t - st[b]))
        if b in (1, 3, 4):
            c.L(.3); c.poly([(-300, 300), (200, 220), (600, 290), (1000, 210), (1500, 300), (1500, 400), (-300, 400)], mix(TEAL, CREAM, .5), None); c.L(1.0)
            c.rect(-300, 380, 1900, 400, mix(TEAL, AMBER, .4), INK, 2.5)
            for i in range(9): c.poly([(i * 190 - 300, 780), (i * 130 - 100 + 100, 380), (i * 130 - 60 + 100, 380), (i * 190 - 220, 780)], mix(SAND, TEAL, .5 + .1 * (i % 2)), None, op=150)
        if b in (1, 2):
            if b == 1:
                bx = 640; c.poly([(bx - 70, 480), (bx - 20, 140), (bx + 20, 140), (bx + 70, 480)], None, dark(SAND, .5), 5)
                for j in range(6): c.line([(bx - 60 + j * 4 + 0, 460 - j * 55), (bx + 60 - j * 4, 430 - j * 55)], dark(SAND, .5), 3)
                dr = 120 + 70 * math.sin(k.t * 3.2) ** 2
                c.rect(bx - 6, 150 + dr * .2, 12, 330 - dr * .2, dark(SAND, .6), INK, 2); c.rect(bx - 26, 140 + dr * .2, 52, 20, TERRA, INK, 2.5)
                c.rect(bx - 150, 470, 300, 70, mix(TERRA, SAND, .4), INK, 3); c.circ(bx - 100, 545, 24, INK, None); c.circ(bx + 100, 545, 24, INK, None)
                person(c, 960, 560, 1.3, 'crew', k.t, 'happy', look=-1, armL=30, armR=60, seed=2, flip=-1); person(c, 330, 560, 1.3, 'phys', k.t, 'curious', look=1, armR=20, propR='tablet', seed=3)
            else:
                c.rect(-100, -100, 1500, 520, mix(CREAM, SAND, .35)); c.rect(-100, 420, 1500, 400, mix(BROWN, INK, .35)); desk(c, 80, 1200, 410)
                for r_ in range(2):
                    y = 330 + r_ * 6 - 0
                    for q in range(2):
                        x = 160 + q * 520; c.rect(x, y - 6 - 90 * r_, 480, 70, mix(SAND, BROWN, .3), INK, 3)
                        for j in range(6):
                            col = STRATA[j % 4][2]; c.rect(x + 12 + j * 76, y - 74 * 0 - 90 * r_, 66, 52, None, INK, 1.2) if False else None
                            c.rect(x + 12 + j * 76, y - 90 * r_ - 2, 66, 54, col, INK, 1.8)
                            c.rect(x + 12 + j * 76, y - 90 * r_ + 14, 66, 12, dark(col, .18), None)
                person(c, 640, 520, 1.5, 'crew', k.t, 'happy', look=0, armL=60, armR=60, seed=2)
        if b >= 3:
            cxp = 300 + (k.t - st[3]) * 70 if b >= 3 else 300
            wk = k.t * 4
            c.line([(cxp + 40, 470), (cxp + 150, 470)], INK, 4); c.rect(cxp + 100, 410, 80, 56, dark(SAND, .3), INK, 3); c.line([(cxp + 150, 410), (cxp + 150, 340)], INK, 3); c.circ(cxp + 150, 336, 8, TERRA, INK, 2)
            c.circ(cxp + 112, 478, 18, INK, None); c.circ(cxp + 168, 478, 18, INK, None)
            person(c, cxp, 520, 1.5, 'crew', k.t, 'happy', walk=wk, armL=55, armR=55, seed=4)
        label = ['', 'Drilling', 'Core samples', 'Geological survey', 'Geophysical scans'][b] if b >= 0 else ''
        label = ['', '', 'Drilling', 'Geological survey', 'Geophysical scans'][b]
        if label: tag(c, 640, 56, label, 28)
    return c

@scene(26)
def s26(k):
    st = [0, k.lt(64), k.lt(66), k.lt(68)]; b = k.beat(st); c = k.cv(vgrad(mix(SAND, BROWN, .4), mix(BROWN, INK, .35)))
    u0 = sstep(prog(k.t, .3, st[1] - .2))
    zz = lerp(1.0, 3.0, 1) if False else lerp(1.0, 2.8, sstep(prog(k.t, st[1] - .6, st[1] + .2)) * (1 - sstep(prog(k.t, st[1] + 1.5, st[2] + .8))))
    cxx = lerp(640, 440, sstep(prog(k.t, st[1] - .6, st[1] + .2)) * (1 - sstep(prog(k.t, st[1] + 1.5, st[2] + .8))))
    cyy = lerp(295, 330, sstep(prog(k.t, st[1] - .6, st[1] + .2)) * (1 - sstep(prog(k.t, st[1] + 1.5, st[2] + .8))))
    c.cam(cxx, cyy, zz)
    for i in range(30): c.line([(-300 + i * 70, 40 + (i * 53) % 500), (-270 + i * 70, 50 + (i * 53) % 500)], dark(BROWN, .15), 3, 90)
    tw = 440 * u0 + 20
    c.poly([(640 - tw, 140 + 14 * math.sin(i)) for i in range(1)] + [(640 - tw + i * (2 * tw) / 12, 120 + 12 * math.sin(i * 2.1)) for i in range(13)] + [(640 + tw + 6 * math.sin(i), 120 + i * 30) for i in range(1, 12)] + [(640 + tw - i * (2 * tw) / 12, 480 + 10 * math.sin(i * 1.7)) for i in range(13)] + [(640 - tw + 6 * math.sin(i), 480 - i * 30) for i in range(1, 12)], mix(BROWN, INK, .3), INK, 3)
    WALLS = [(260, 170, 300, 130), (560, 170, 240, 130), (260, 300, 200, 150), (460, 300, 340, 150), (800, 190, 190, 260)]
    wl = prog(k.t, st[2] - .8, st[2] + 1.8) if b >= 1 else 0
    if u0 > .95:
        c.rect(220, 140, 840, 340, AMBER, None, op=int(26 * (1 if b >= 2 else .4)))
        for (x, y, w, h) in WALLS:
            pts = [(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)]
            n = int(5 * (wl if b < 2 else 1)) if b < 2 else 5
            if wl > 0:
                c.line(pts, INK, 28); c.line(pts, SAND, 22); c.line(pts, mix(SAND, AMBER, .4), 14, 120)
                for q in range(0, 18): c.line([(x + q * 22, y - 8), (x + q * 22, y + 8)], dark(SAND, .35), 1.5) if y < 200 and False else None
    SH = [(420, 330), (560, 380), (700, 320), (880, 400), (360, 420)]
    for i, (x, y) in enumerate(SH):
        if u0 > .9: shard(c, x, y, 1.3 + (.3 if i == 0 else 0))
    if b >= 1 and k.t < st[2] + .8:
        bx = 440 + 30 * math.sin(k.t * 6); c.line([(900, 20), (bx + 20, 300)], INK, 30); c.line([(900, 20), (bx + 20, 300)], OLIVE, 24); c.circ(bx + 18, 304, 12, SKIN, INK, 2); prop(c, 'brush', bx, 310, 1.6, k.t)
    if b >= 3:
        u = prog(k.t, st[3] + .3, k.d - .6)
        for j, (x, y, w, h) in enumerate(WALLS):
            pts = [(x - 16, y - 16), (x + w + 16, y - 16), (x + w + 16, y + h + 16), (x - 16, y + h + 16), (x - 16, y - 16)]
            uu = clamp(u * 5 - j); n = max(2, int(5 * uu) + 1)
            if uu > 0:
                c.dash(pts[:n], CREAM, 4, 14, 9)
    c.hud()
    if b >= 3: tag(c, 640, 56, 'CLUE: Buried settlement', 28, INK, AMBER, int(255 * prog(k.t, st[3] + .3, st[3] + .9)))
    return c

@scene(27)
def s27(k):
    L69 = k.lt(71); L72 = k.lt(72); L73 = k.lt(73); L74 = k.lt(74); R = k.cue(73, 'Roman'); B = k.cue(73, 'Byzantine')
    c = k.cv(vgrad(mix(NAVY, TEAL, .22), dark(NAVY, .3)))
    cy = 295 + 110 * math.sin(math.pi * sstep(k.t / k.d)) * (1 if k.t < k.d * .5 else 1) - 30
    c.cam(480, 295 - 80 * sstep(prog(k.t, 2, L72)) + 120 * sstep(prog(k.t, L72, L74)) - 40 * sstep(prog(k.t, L74, k.d)), 1.12)
    x, y, w, h = 120, 40, 560, 470
    hl = None
    if k.t > L69 and k.t < L72: hl = ['Much older', 'Classical', 'Roman', 'Byzantine'][int((k.t - L69) / .9) % 4]
    elif L72 <= k.t < R - .3: hl = 'Much older'
    elif R - .3 <= k.t < B - .2: hl = 'Roman'
    elif B - .2 <= k.t < L74: hl = 'Byzantine'
    elif k.t >= L74: hl = 'Classical'
    out = strata(c, x, y, w, h, prog(k.t, .3, L69 - .3) * 1.0 + 0.0001, 0, hl, True, 30)
    if k.t > L74 + .3 and 'Classical' in out:
        qx, qy, qw, qh = out['Classical']; u = pop(prog(k.t, L74 + .3, L74 + .7), .6); qmark(c, qx + qw / 2, qy + qh / 2, 150 * u, AMBER)
    return c

@scene(28)
def s28(k):
    c = k.cv(vgrad(dark(NAVY, .2), mix(NAVY, TEAL, .3))); c.cam(640, 295, 1 + .08 * k.t / k.d)
    u = sstep(prog(k.t, .2, k.d * .7))
    for i, (nm, fr, col) in enumerate(STRATA):
        base = 400 - i * 70; pts = []
        for j in range(31):
            xx = 150 + j * 33; pts.append((xx, base + u * (60 * math.sin(xx / 80 + i * 1.7 + k.t * .5) + 30 * math.sin(xx / 31 + i * 3)) + (i - 1.5) * u * 40))
        c.line(pts, INK, 20 + 4); c.line(pts, col, 20)
    for i in range(10):
        pts = [(120 + j * 40, 300 + u * 140 * math.sin(j * .5 + i * 1.3 + k.t * .4) + (i - 5) * 22 * u) for j in range(28)]
        c.line(pts, STRATA[i % 4][2], 3, int(220 * u))
    for i, (x, y, s_) in enumerate(((300, 200, 110), (560, 140, 160), (860, 220, 120), (1000, 340, 90), (240, 400, 80), (700, 420, 100), (430, 330, 70))):
        qa = prog(k.t, .6 + i * .35, 1.2 + i * .35); qmark(c, x, y + 10 * math.sin(k.t + i), s_, CREAM, int(230 * qa))
    c.hud(); c.text(640, 62, 'More complicated.', 52, CREAM, 'serif', 'c', int(255 * prog(k.t, k.cue(77, 'complicated') - .3, k.cue(77, 'complicated') + .4)), INK, 4)
    return c

@scene(29)
def s29(k):
    ts = k.cue(81, 'earthquake') - .1; qe = ts + 2.6; c = k.cv(DARK)
    c.cam(640, 295, 1.0)
    fu = ease_out(prog(k.t, .2, 1.0)); fx0, fy0, fw, fh = 280, 110, 720, 405
    rt = k.t - ts
    lc = Canvas(TERRA, 'L', math.floor(max(0, rt) * 10) / 10)
    if rt < 0: draw12(lc, 0.0, 4, 1.2, 2.2)
    elif rt < 1.2: draw12(lc, rt * 3.4, 4.5, 1.2, 2.2)
    elif rt < 2.6: draw13(lc, (rt - 1.2) * 3.0, .8, 2.2, 4.0)
    else: draw13(lc, 4.2, .8, 2.2, 4.0)
    img = legend_post(lc.finish(), math.floor(max(0, rt) * 10) / 10)
    yoff = (1 - fu) * -400
    c.hud(); c.rect(fx0 - 10, fy0 - 10 + yoff, fw + 20, fh + 20, CREAM, INK, 4)
    c.paste(img, fx0, fy0 + yoff, fw, fh)
    c.hud(); tag(c, 640, 76 + yoff, 'Traditional story', 30, INK, CREAM)
    if k.t > ts: c.text(640, 556, 'Earthquake + tsunami = city gone', 30, AMBER, 'serif', 'c', int(255 * prog(k.t, ts, ts + .5)), INK, 4)
    if k.t > qe:
        u = pop(prog(k.t, qe, qe + .25), .8); c.text(640, 320, '?', 330 * u, CREAM, 'serif', 'c', 120, INK, 4)
    if k.t > k.d - .25: k.fx['desat'] = .9
    return c

@scene(30)
def s30(k):
    c = k.cv(vgrad(mix(NAVY, TEAL, .35), mix(NAVY, BROWN, .35))); u = sstep(k.t / k.d); cx = lerp(560, 820, u)
    c.cam(cx, 295, 1.1)
    c.rect(-100, -100, 1500, 520, mix(NAVY, TEAL, .3)); c.rect(-100, 430, 1500, 300, mix(BROWN, INK, .4))
    for r_ in range(2):
        for i in range(14):
            col = (TERRA, TEAL, AMBER, CREAM, SAND)[(i + r_ * 2) % 5]; hh = 52 + (i * 13) % 22
            c.rect(700 + i * 22, 100 + r_ * 100 + (74 - hh), 18, hh, mix(col, INK, .25), INK, 1.5)
        c.line([(690, 175 + r_ * 100), (1020, 175 + r_ * 100)], INK, 4)
    desk(c, 80, 1200, 410)
    for i in range(4):
        x = 300 + i * 60 + 300; c.rect(x, 300, 26, 110, mix(CREAM, TEAL, .3), INK, 2)
        for j in range(4): c.rect(x + 2, 304 + j * 26, 22, 22, STRATA[j][2], None) if False else c.rect(x + 2, 410 - (j + 1) * 26 + 2, 22, 24, STRATA[j][2], None)
    c.rect(780, 330, 60, 80, dark(SAND, .5), INK, 2.5); c.circ(805, 320, 20, dark(TEAL, .2), INK, 2.5); c.line([(805, 300), (830, 270)], INK, 5); c.circ(832, 268, 9, TEAL, INK, 2)
    for i in range(3): manuscript(c, 960 + i * 18, 398 - i * 5, 120, 14, 0, 2, i)
    person(c, 740, 420, 1.5, 'phys', k.t, 'curious', look=1, armR=75, armL=20, seed=2)
    person(c, 1020, 420, 1.5, 'arch', k.t, 'doubt', look=-1, armL=60, armR=20, seed=1, flip=-1)
    sx, sy = c.T(90, 70); S_ = c.k
    lc = Canvas(TERRA, 'L', math.floor(k.t * 10) / 10); draw12(lc, k.t % 8, 8, 3.5, 5.0)
    c.d.flush(); c.rect(80, 60, 400, 235, dark(INK, 0), INK, 4)
    c.paste(legend_post(lc.finish(), math.floor(k.t * 10) / 10), sx / SS + 0, sy / SS, 380 * S_, 214 * S_)
    c.rect(90, 70, 380, 214, NAVY, None, op=int(190 * prog(k.t, 1.5, k.d - .6)))
    return c
