"""Scenes 1-15"""
from scenelib import *
SC = {}
def scene(n):
    def d(f): SC[n] = f; return f
    return d

# 01 ---- the empty window
@scene(1)
def s01(k):
    van = k.cue(0, 'vanished'); live = k.t < van
    c = k.cv(DAY if live else NIGHT)
    z = 1 + .2 * sstep(min(k.t, van) / van); c.cam(640, 295, z)
    if live:
        skyline(c, k.t, lit=0); birds(c, k.t, 3, 90, 300)
        for i, x in enumerate((420, 520, 600)): pass
    else:
        c.L(1.0); vband(c, -400, 1700, 340, 760, mix(NAVY, TEAL, .22), mix(NAVY, TEAL, .08), 8)
        c.line([(-400, 340), (1700, 340)], mix(NAVY, TEAL, .4), 2)
    c.L(1.6); wall = mix(SAND, INK, .62)
    c.rect(-900, -900, 3200, 930, wall); c.rect(-900, 510, 3200, 900, wall); c.rect(-900, 0, 1020, 600, wall); c.rect(1160, 0, 900, 600, wall)
    c.rect(100, 500, 1080, 24, light(SAND, .1), INK, 3)
    c.line([(120, 30), (1160, 30)], INK, 6); c.line([(120, 30), (120, 510)], INK, 6); c.line([(1160, 30), (1160, 510)], INK, 6)
    c.line([(640, 30), (640, 510)], INK, 7); c.line([(120, 270), (1160, 270)], INK, 7)
    c.L(1.0); k.fx['mode'] = 'E'
    return c

# 02 ---- not abandoned / not destroyed / vanished (three panels, whip between)
def street(c, ox, t, fade=0.0, dust=1.0):
    vband(c, ox - 700, ox + 700, -100, 560, mix(SAND, CREAM, .3), mix(SAND, TEAL, .2), 8)
    vp = (ox, 250)
    for side in (-1, 1):
        for i, (w, h) in enumerate(((150, 330), (130, 250), (100, 190))):
            x0 = ox + side * (230 + i * 120 - (i * 8)); col = mix(CREAM, SAND, .25 + .18 * i)
            c.poly([(x0, 470 - i * 70), (x0 + side * w, 470 - i * 55), (x0 + side * w, 470 - h * .9), (x0, 470 - h)], col, INK, 2.2)
            for j in range(2): c.rect(x0 + side * (w * .3), 400 - j * 90 - i * 40, 22 * side if side > 0 else -22, 34, dark(col, .5), INK, 1.5)
    c.poly([(ox - 640, 560), (ox + 640, 560), (ox + 120, 300), (ox - 120, 300)], dark(SAND, .18), INK, 2.5)
    for j in range(6): c.line([(ox - 640 + j * 256, 560), (ox - 100 + j * 40, 300)], dark(SAND, .35), 1.6)
    if dust > 0:
        for i in range(7):
            y = 330 + i * 28; x = ((t * 160 * (1 + i * .15) + i * 210) % 1500) - 100 + ox - 640
            c.line([(x, y), (x + 80, y - 6), (x + 170, y + 3), (x + 240, y - 2)], light(SAND, .4), 4, 140)
    if fade > 0:
        for i in range(8):
            c.poly([(ox - 700, 120 + i * 60 + 18 * math.sin(t * .5 + i))] + [(ox - 700 + j * 100, 120 + i * 60 + 22 * math.sin(j + t * .4 + i)) for j in range(1, 15)] + [(ox + 700, 640), (ox - 700, 640)], mix(NAVY, TEAL, .45), None, op=int(min(255, fade * 90)))
        c.rect(ox - 700, -100, 1400, 800, mix(NAVY, TEAL, .35), None, op=int(255 * clamp(fade - 2.2)))
@scene(2)
def s02(k):
    c = k.cv(DARK); st = [0, k.lt(2), k.lt(3)]
    cx = strip_cam(k.t, [s - .2 for s in st], [640, 2040, 3440]); z = 1 + .05 * ((k.t - st[max(0, k.beat(st))]) / 3)
    c.cam(cx, 295, z)
    if cx < 1300: street(c, 640, k.t)
    if 700 < cx < 2800:
        ox = 2040; vband(c, ox - 700, ox + 700, -100, 560, mix(NAVY, TERRA, .5), mix(TERRA, AMBER, .5), 10)
        bs = [(-560, 130, 200), (-420, 90, 280), (-320, 140, 190), (-170, 100, 330), (-60, 150, 230), (110, 90, 300), (200, 130, 210), (330, 100, 270), (440, 140, 180)]
        for dx, w, h in bs: c.rect(ox + dx, 480 - h, w, h, INK, None)
        for i, (dx, w, h) in enumerate(bs):
            fl = 1 + .25 * math.sin(k.t * 11 + i * 2)
            for j in range(3): c.poly([(ox + dx + j * w / 3, 480 - h), (ox + dx + w / 6 + j * w / 3, 480 - h - (50 + 30 * j) * fl), (ox + dx + w / 3 + j * w / 3, 480 - h)], mix(TERRA, AMBER, .4 + .2 * j), None)
        c.rect(ox - 700, 480, 1400, 200, INK, None)
        u = pop(prog(k.t, st[1] + .9, st[1] + 1.15), .4)
        if k.t > st[1] + .9:
            c.line([(ox - 190 * u, 190), (ox + 190 * u, 440)], (200, 40, 40), 28); c.line([(ox + 190 * u, 190), (ox - 190 * u, 440)], (200, 40, 40), 28)
    if cx > 2800: street(c, 3440, k.t, fade=prog(k.t, st[2] - .3, st[2] + 3.5) * 3.5, dust=0.4)
    k.fx['mode'] = 'E'
    if k.t > st[2]:
        c.hud(); c.text(640, 250, 'VANISHED', 84, CREAM, 'sansr', 'c', int(255 * prog(k.t, st[2], st[2] + .8)), INK, 3, spacing=26)
    return c

# 03 ---- gone, gone, gone
@scene(3)
def s03(k):
    g = [k.cue(4, 'gone', i) for i in range(3)]
    night = prog(k.t, g[2] + .2, g[2] + 2.4); u = sstep(k.t / k.d)
    c = k.cv(blend_img(DAY, NIGHT, night)); c.cam(lerp(520, 640, u), lerp(350, 270, u), lerp(1.3, .95, u))
    fadeall = 1 - prog(k.t, g[2] + .4, g[2] + 2.2)
    vis = dict(houses=1 - prog(k.t, g[0] - .3, g[0] + .45), roofs=1 - prog(k.t, g[0] - .5, g[0] + .1), streets=1 - prog(k.t, g[1] - .3, g[1] + .45),
               figs=1 - prog(k.t, g[2] - .3, g[2] + .3), temple=fadeall, ships=fadeall, mount=fadeall, water=0)
    if k.t < g[0] - .3: vis['houses'] = 1
    skyline(c, k.t, vis)
    wave_rig(c, k.t, SEA_Y + 4, -600, 2000, mix(TEAL, NAVY, .75 * night), ybot=900)
    return c

# 04 ---- question made of ripples
@scene(4)
def s04(k):
    c = k.cv(vgrad(dark(NAVY, .3), mix(NAVY, TEAL, .22))); c.cam(640, 295, 1 + .08 * k.t / k.d)
    pa = k.pause_t(6)[0]; ph = min(k.t, pa)
    wave_rig(c, k.t * .3, 470, -400, 1700, mix(TEAL, NAVY, .7), amp=.5, ybot=900, op=120)
    for i in range(5):
        u = ((ph * .22) + i / 5) % 1; r = 1 + .55 * u
        sz = 250 * r; op = int(255 * (1 - u) ** 1.3 * min(1, u * 6))
        bgc = vgrad(dark(NAVY, .3), mix(NAVY, TEAL, .22)) if False else (14, 30, 44)
        c.text(640, 290, '?', sz, bgc, 'serif', 'c', op, light(TEAL, .25 + .5 * (1 - u)), 3)
    c.text(640, 290, '?', 250, (14, 30, 44), 'serif', 'c', 255, light(TEAL, .45), 3)
    return c

# 05 ---- globe -> Greece -> marker sinks
@scene(5)
def s05(k):
    c = k.cv(vgrad(dark(NAVY, .2), mix(NAVY, TEAL, .3)))
    t_st = k.lt(7, 0); ago = k.cue(7, 'ago', end=True); a_end = k.cue(7, 'extraordinary'); hel = k.cue(7, 'Helike')
    ms = k.cue(8, 'disappeared'); m_end = k.cue(8, 'water', end=True)
    c.cam(640, 295, 1 + .25 * sstep(prog(k.t, a_end, k.d)))
    ox, oy, sc = 230, -10, 1.25; mk = (ox + 232 * sc, oy + 264 * sc)
    e = ease_in(prog(k.t, 0, a_end)) if False else sstep(prog(k.t, .2, a_end + .3))
    r = lerp(150, 1600, e ** 1.6)
    lon0 = lerp(-110, 22, e); lat0 = lerp(15, 38, e)
    gx, gy_, z_ = proj(22, 38.3, lon0, lat0, r)
    gc = (lerp(640, 640 - gx + (mk[0] - 640), e), lerp(300, 300 - gy_ + (mk[1] - 300), e))
    if r > 700:
        c.rect(-800, -400, 3000, 1600, mix(TEAL, NAVY, .25)); greece(c, ox, oy, sc, hi=prog(k.t, a_end + .4, a_end + 1.2))
    op = int(255 * (1 - prog(k.t, a_end - .2, a_end + .5)))
    if op > 0: globe(c, gc[0], gc[1], r, lon0, lat0, op=op)
    # sink
    sink = sstep(prog(k.t, ms, m_end + .3))
    pulse = ((k.t - hel) * 1.1) % 1 if k.t > hel and sink == 0 else 0
    if k.t > a_end + .6:
        helike_marker(c, mk[0], mk[1] + 80 * sink, 1.2, pulse)
    wl = lerp(640, 250, sink)
    if sink > 0: wave_rig(c, k.t, wl, -800, 2200, mix(TEAL, NAVY, .35), ybot=1200, op=225)
    # texts
    c.hud(); n = int(2300 * sstep(prog(k.t, t_st + .1, ago)))
    c.text(640, 70 if k.t < a_end else 55, f'{n:,}', 96 if k.t < ago + 2 else 64, CREAM, 'serif', 'c', 255, INK, 4)
    c.text(640, 128 if k.t < ago + 2 else 100, 'YEARS AGO', 28, AMBER, 'sans', 'c', 255, INK, 3, spacing=8)
    if k.t > a_end + .5: c.L(1.0); c.text(ox + 480 * sc, oy + 150 * sc, 'GREECE', 54, CREAM, 'serif', 'c', int(255 * prog(k.t, a_end + .5, a_end + 1.1)), INK, 4, spacing=12)
    if k.t > ago + .3: c.text(ox + 232 * sc, oy + 330 * sc, 'Achaea', 34, INK, 'sans', 'c', int(255 * prog(k.t, ago + .3, ago + .9)), CREAM, 3)
    if k.t > hel: c.text(mk[0], mk[1] - 68 + 80 * sink, 'HELIKE', 36, AMBER, 'sans', 'c', int(255 * prog(k.t, hel, hel + .4) * (1 - sink)), INK, 4, spacing=6)
    if k.t > k.lt(8, 0):
        u = ease_out(prog(k.t, k.lt(8, 0), k.lt(8, 0) + .9)); c.hud()
        manuscript(c, lerp(1500, 1050, u), 280, 250, 340, 0, 8, 3, tilt=6)
    return c

# 06 ---- the search (five beats along a strip)
@scene(6)
def s06(k):
    st = [0] + [k.lt(li) for li in (10, 11, 12, 13)]; b = k.beat(st)
    cx = strip_cam(k.t, [s - .15 for s in st[:4]], [640, 2040, 3440, 5300])
    if b == 4: cx = lerp(4250, 5750, sstep(prog(k.t, st[4], k.d)))
    c = k.cv(DARK); c.cam(cx, 295, 1.0 + .06 * sstep(prog(k.t, st[b], st[b] + 3)))
    if cx < 1400:   # engraving map
        ink = mix(BROWN, INK, .3); c.rect(-100, -100, 1500, 700, mix(CREAM, SAND, .35))
        for i in range(60): c.line([(i * 24 - 100, 40), (i * 24 - 60 + 40, 600)], mix(CREAM, SAND, .6), 1.2, 90)
        c.poly([(100, 380), (260, 250), (420, 280), (560, 180), (760, 230), (900, 160), (1100, 300), (1160, 420), (900, 520), (500, 500)], mix(SAND, CREAM, .3), ink, 3)
        for i in range(30): c.line([(200 + i * 28, 300 + 12 * math.sin(i)), (212 + i * 28, 312 + 12 * math.sin(i))], ink, 1.4)
        for i in range(10): c.line([(120 + i * 110, 540), (150 + i * 110, 530), (180 + i * 110, 540)], ink, 1.5)
        cx_, cy_ = 1080, 110; c.circ(cx_, cy_, 46, None, ink, 2.5); c.poly([(cx_, cy_ - 62), (cx_ + 10, cy_ - 10), (cx_, cy_), (cx_ - 10, cy_ - 10)], ink); c.poly([(cx_, cy_ + 62), (cx_ + 10, cy_ + 10), (cx_, cy_), (cx_ - 10, cy_ + 10)], ink)
        c.line([(cx_ - 62, cy_), (cx_ + 62, cy_)], ink, 2.5)
        helike_marker(c, 640, 330, .9, ((k.t * .8) % 1) if b == 0 else 0)
    if 1000 < cx < 3000:   # sea + diver
        ox = 2040; vband(c, ox - 700, ox + 700, -100, 700, mix(TEAL, CREAM, .15), dark(TEAL, .45), 12)
        for i, dx in enumerate((-300, 0, 300)): c.poly([(ox + dx, -100), (ox + dx + 90, -100), (ox + dx + 240, 600), (ox + dx + 20, 600)], CREAM, None, op=26)
        wave_rig(c, k.t, 60, ox - 700, ox + 700, TEAL, ybot=140, amp=.7)
        dy = lerp(110, 440, prog(k.t, st[1], st[2])); dx_ = ox + 20 * math.sin(k.t * .8)
        c.ell(dx_, dy, 20, 44, INK, None); c.circ(dx_ + 6, dy - 50, 17, INK, None); c.circ(dx_ + 12, dy - 52, 7, light(TEAL, .4), None)
        c.line([(dx_ - 8, dy + 36), (dx_ - 24, dy + 80 + 6 * math.sin(k.t * 3))], INK, 7); c.line([(dx_ + 8, dy + 36), (dx_ + 22, dy + 80 + 6 * math.sin(k.t * 3 + 1))], INK, 7)
        c.line([(dx_ - 18, dy - 10), (dx_ - 48, dy + 20)], INK, 7); c.line([(dx_ + 18, dy - 10), (dx_ + 34, dy + 14)], INK, 7)
        c.circ(dx_ + 34, dy + 14, 8, AMBER, None, op=230)
        c.rect(ox - 700, 540, 1400, 200, mix(SAND, TEAL, .5), None)
        for i in range(7): c.poly([(ox - 560 + i * 190, 540), (ox - 540 + i * 190, 520), (ox - 500 + i * 190, 540)], mix(SAND, TEAL, .35), None)
    if 2300 < cx < 4600:   # scholar
        ox = 3440; c.rect(ox - 700, -100, 1400, 800, mix(NAVY, TEAL, .35)); c.rect(ox - 700, 430, 1400, 300, mix(BROWN, INK, .35))
        c.rect(ox - 520, 110, 160, 220, mix(NAVY, TEAL, .6), INK, 3); c.line([(ox - 440, 110), (ox - 440, 330)], INK, 3)
        desk(c, ox - 380, ox + 380, 390); lamp(c, ox - 250, 392, 1.1, k.t)
        sh = math.sin(k.t * 7.5) * (1 if b == 2 else .3)
        person(c, ox + 60, 395, 1.55, 'scholar', k.t, 'doubt', look=sh, armL=40, armR=40, seed=2, lean=sh * 6)
        manuscript(c, ox + 60, 372, 190, 40, .1, 3, 5)
    if cx > 3800:    # plain with archaeologists and the sea at left
        ox = 5300; vband(c, 3600, 7000, -100, 420, mix(AMBER, CREAM, .55), mix(CREAM, TEAL, .3), 8)
        c.L(.5); c.poly([(3600, 400), (4200, 280), (4800, 330), (5400, 250), (6200, 330), (7000, 260), (7000, 420), (3600, 420)], mix(TEAL, CREAM, .45), None); c.L(1.0)
        c.rect(3600, 385, 900, 215, mix(TEAL, NAVY, .1), None); wave_rig(c, k.t, 392, 3600, 4520, TEAL, ybot=600, amp=.7)
        c.poly([(4480, 410)] + [(4480 + i * 100, 400 + 14 * math.sin(i)) for i in range(0, 28)] + [(7300, 700), (4480, 700)], mix(TEAL, AMBER, .35), INK, 2.5)
        for i in range(26): c.poly([(4600 + i * 97, 430), (4606 + i * 97, 414 - i % 6), (4612 + i * 97, 430)], mix(TEAL, AMBER, .55), None)
        for i, (kind, dx, pr) in enumerate((('arch', -110, 'trowel'), ('crew', 60, 'basket'), ('phys', 190, 'instr'))):
            person(c, ox + dx, 500, 1.3, kind, k.t, 'curious' if kind == 'arch' else 'happy', look=math.sin(k.t * .7 + i), armR=40 + 20 * math.sin(k.t * 2 + i), propR=pr if pr != 'basket' else None, seed=i + 3)
    txt = [None, 'Under the sea?', 'Exaggerated?', None, 'Somewhere else?'][b]
    if b == 3: txt = 'Unexpected'
    if txt:
        al = prog(k.t, st[b], st[b] + .5); tag(c, 640, 70, txt, 36, INK, CREAM, int(255 * al))
    return c

# 07 ---- title card
@scene(7)
def s07(k):
    c = k.cv((6, 12, 20)); c.cam(640 + 10 * math.sin(k.t), 295, 1.0)
    u = ease_out(prog(k.t, .3, 2.2)); c.hud()
    y0 = lerp(420, 200, u)
    c.text(640, y0, 'THE VANISHED CITY', 64, CREAM, 'serif', 'c', 255, INK, 4); c.text(640, y0 + 80, 'OF HELIKE', 64, AMBER, 'serif', 'c', 255, INK, 4)
    c.L(1.0)
    wl = 330
    wave_rig(c, k.t, wl, -300, 1600, mix(TEAL, NAVY, .7), amp=.8, ybot=900, depth_cols=[(8, 16, 26), (10, 22, 34), (12, 28, 40)])
    return c

# 08 ---- 373 BC (HERO 2)
@scene(8)
def s08(k):
    st = k.cue(16, '373'); u = ease_out(prog(k.t, .5, st - .1)); u = 1 - (1 - u) ** 1.6 if u < 1 else 1
    X1 = 6400; cx = lerp(300, X1, ease_out(prog(k.t, .4, st - .05)))
    sk = shake(k.t, st, 10, 8); pz = 1 + .16 * math.exp(-max(0, k.t - st) * 4) * (1 if k.t >= st else 0)
    c = k.cv(vgrad(mix(NAVY, SAND, .15), mix(NAVY, BROWN, .3))); c.cam(cx, 295, pz, sk)
    spd = abs(cx - lerp(300, X1, ease_out(prog(k.t - .03, .4, st - .05)))) * 30
    c.L(.5)
    for i in range(70): c.line([(i * 110 - 200, 120), (i * 110 - 200, 140 + 40 * (i % 3))], mix(SAND, NAVY, .5), 2)
    c.L(1.0)
    c.rect(-600, 190, X1 + 1400, 210, mix(CREAM, SAND, .25), INK, 3)
    for i in range(0, int(X1 / 80) + 8): c.line([(i * 80, 190), (i * 80, 215 + (20 if i % 5 == 0 else 0))], INK, 2 if i % 5 else 3)
    c.text(0, 330, 'Today', 46, INK, 'serif', 'c')
    c.circ(0, 300, 7, TERRA, INK, 2)
    if spd > 60:
        for i in range(10): c.line([(cx - 700 + (i * 173) % 1400, 170 + i * 24), (cx - 500 + (i * 173) % 1400, 170 + i * 24)], CREAM, 2, int(min(120, spd / 8)))
    if k.t >= st:
        s_ = pop(prog(k.t, st, st + .14), 1.2) if k.t < st + .14 else 1.0; sz = 1 + 1.6 * max(0, 1 - (k.t - st) / .12)
        c.circ(X1, 295, 100 * sz, mix(TERRA, INK, .12), INK, 4); c.circ(X1, 295, 76 * sz, None, mix(TERRA, CREAM, .3), 3)
        c.text(X1, 295, '373 BC', 78 * sz if sz < 1.1 else 78 * sz, CREAM, 'serif', 'c', 255, INK, 4)
        c.text(X1, 130, '373 BC', 1, CREAM, 'serif', 'c', 0)
    if k.t > st + .3:
        c.hud(); c.text(640, 82, 'THE YEAR', 28, AMBER, 'sans', 'c', int(255 * prog(k.t, st + .3, st + .9)), INK, 3, spacing=12)
    return c

# 09 ---- coast of Achaea: map zoom, then dissolve into the panorama
@scene(9)
def s09(k):
    dis = k.cue(17, 'stood') - .2; u = prog(k.t, dis, dis + .9)
    ox, oy, sc = 408, 31, 1.0
    def mapimg():
        c = k.cv(mix(TEAL, NAVY, .25)); z = lerp(1.0, 3.0, sstep(prog(k.t, 0, dis + .5)))
        c.cam(640, 295, z); hi = prog(k.t, 0, 1.5)
        mk = greece(c, ox, oy, sc, hi=hi)
        wave_rig(c, k.t * .5, 700, -200, 1500, TEAL, amp=.4, ybot=900, op=0)
        helike_marker(c, mk[0], mk[1], .55, ((k.t * .8) % 1) if k.t > k.cue(17, 'Helike') else 0, op=int(255 * prog(k.t, k.cue(17, 'Helike') - .1, k.cue(17, 'Helike') + .3)))
        c.text(mk[0] + 90, mk[1] + 70, 'Achaea', 17, INK, 'sans', 'c', int(255 * prog(k.t, .4, 1.0)), CREAM, 2)
        c.text(mk[0] - 30, mk[1] - 16 * 1, 'Gulf of Corinth', 11, CREAM, 'sans', 'c', int(255 * prog(k.t, k.cue(17, 'Gulf') - .2, k.cue(17, 'Gulf') + .4)), INK, 2)
        c.hud(); return c.finish()
    def pano():
        c = k.cv(DAY); c.cam(lerp(470, 760, sstep(k.t / k.d)), 295, 1.0)
        skyline(c, k.t, dict(figs=1)); birds(c, k.t, 3, 90, 500); helike_marker(c, 230, 120, .9, (k.t * .7) % 1)
        c.hud(); c.text(300, 70, 'Helike', 40, CREAM, 'serif', 'c', 255, INK, 4)
        if k.t > k.lt(18): c.text(660, 70, 'Achaea', 30, CREAM, 'serif', 'c', 255, INK, 4)
        return c.finish()
    img = mapimg() if u <= 0 else pano() if u >= 1 else Image.blend(mapimg(), pano(), sstep(u))
    return img

# 10 ---- temples and streets
@scene(10)
def s10(k):
    tl = k.cue(19, 'connection'); t1 = k.le(19)
    u = sstep(prog(k.t, tl - .5, t1 + .8)); tr = prog(k.t, 0, tl)
    c = k.cv(DAY); c.cam(lerp(420, 1150, sstep(tr)) if k.t < tl else 1150, lerp(295, -140, u), lerp(1.0, 1.25, u))
    c.L(.3); c.poly([(-400, 340), (100, 230), (500, 300), (900, 200), (1500, 320), (2000, 240), (2100, 340)], mix(TEAL, CREAM, .5), None)
    c.L(.55)
    for i in range(14): c.rect(i * 150 - 200, 330 - (i * 37) % 70, 90, 140, mix(CREAM, SAND, .5), INK, 2); c.rect(i * 150 - 206, 322 - (i * 37) % 70, 102, 10, mix(TERRA, CREAM, .3), INK, 1.5)
    c.L(1.0)
    c.poly([(780, -60), (1000, -70), (1300, -60), (1650, 20), (1900, 470), (700, 470)], SAND, INK, 3)
    c.rect(-600, 470, 2900, 400, dark(SAND, .2), INK, 3)
    for i in range(14): c.line([(i * 210 - 500, 470), (i * 260 - 700, 700)], dark(SAND, .4), 2)
    for i in range(8):
        bx = 300 + i * 210; h = 190 + (i * 53) % 70
        if bx > 1000 and bx < 1350: continue
        c.rect(bx, 470 - h, 150, h, CREAM, INK, 2.5); c.rect(bx - 8, 470 - h - 10, 166, 12, TERRA, INK, 2.5); c.rect(bx + 52, 470 - 100, 46, 100, dark(SAND, .55), INK, 2); c.rect(bx + 14, 470 - h + 40, 26, 30, light(TEAL, .5), INK, 2)
    for i, bx in enumerate((470, 880, 1290)):
        for dx in (-50, 50): c.line([(bx + dx, 470), (bx + dx, 360)], BROWN, 6)
        c.poly([(bx - 70, 360), (bx + 70, 360), (bx + 78, 392), (bx - 78, 392)], TERRA if i % 2 else CREAM, INK, 2.5)
        for j in range(5): c.line([(bx - 60 + j * 30, 360), (bx - 62 + j * 30, 392)], TERRA if i % 2 == 0 else CREAM, 5) if False else None
        for j in range(4): c.circ(bx - 36 + j * 24, 447, 11, (AMBER, TERRA, SAND, AMBER)[j], INK, 1.8)
        c.rect(bx - 60, 450, 120, 24, BROWN, INK, 2)
    temple(c, 1150, -60, 1.8)
    c.L(1.0)
    kinds = ['woman', 'man', 'merchant', 'child', 'baker', 'man']
    for i, kd in enumerate(kinds):
        sp = (1 if i % 2 else -1) * (18 + 5 * i); x = 380 + ((i * 260 + k.t * sp) % 1500)
        person(c, x, 545 + (i % 2) * 22, 1.0 if kd != 'child' else .65, kd, k.t, 'happy' if i % 2 else 'neutral', walk=k.t * 4 + i, armL=14, armR=14, seed=i, flip=1 if sp > 0 else -1, propR='basket' if kd == 'woman' else None)
    c.L(1.35); c.rect(cx_ := c.cx - 740 + 0, -300, 90, 1200, dark(SAND, .35), INK, 3) if False else None
    for i in range(3):
        x = 300 + i * 620; c.rect(x, -300, 70, 1100, dark(SAND, .3), INK, 3)
    c.L(1.0)
    return c

# 11 ---- Poseidon (vase)
@scene(11)
def s11(k):
    ts = k.cue(22, 'earthquakes'); k.fx['mode'] = 'L'
    c = k.cv(TERRA, 'L'); u = prog(k.t, ts, ts + 2.5)
    c.cam(lerp(640, 520, sstep(prog(k.t, ts - .3, k.d))), lerp(295, 380, sstep(prog(k.t, ts - .3, k.d))), 1 + .5 * sstep(prog(k.t, ts - .3, ts + 2.2)), shake(k.t, ts, 11, 6))
    sw = prog(k.t, k.lt(21, 3), k.cue(21, 'sea', end=True) + 1)
    vwater(c, k.t, 330 - 30 * sw, -400, 1800, 120, 4 + 36 * sw)
    c.rect(-600, 500, 2600, 400, VK); c.line([(-600, 500), (1800, 500)], VT, 2)
    for i in range(10): c.line([(i * 140 - 300, 530), (i * 140 - 240, 548), (i * 140 - 170, 530)], VT, 1.4)
    if k.t > ts:
        pts = [(430, 500), (480, 512), (520, 506), (600, 524), (650, 516), (760, 540), (840, 530), (960, 556), (1100, 548), (1260, 570)]
        crack_line(c, pts, prog(k.t, ts, ts + 1.6), VT, 3)
        for i in range(4):
            rr = max(0, k.t - ts - i * .35) * 260
            if rr > 0: c.ell(450 + rr * .15, 506, rr, rr * .12, None, VT, 1.6, int(255 * clamp(1 - rr / 800)))
        for i in range(3):
            rr = max(0, k.t - ts - .3 - i * .5) * 180
            if rr > 0: c.ell(900 + rr * .1, 380, rr, rr * .05, None, VT, 1.4, int(255 * clamp(1 - rr / 500)))
    c.rect(150, 40, 440, 462, light(TERRA, .3), None); c.line([(150, 40), (590, 40), (590, 502), (150, 502), (150, 40)], VK, 4)
    for i in range(5): c.line([(160, 70 + i * 90), (580, 70 + i * 90)], TERRA, 1.5)
    pose = 'up' if k.t < ts else 'strike'
    vfig(c, 380, 500, 1.55, 'poseidon', k.t, 1, pose, 'trident')
    ltitle(c, 'Poseidon: sea and earthquakes', 70, 40, int(255 * prog(k.t, k.cue(21, 'Poseidon'), k.cue(21, 'Poseidon') + .6)))
    return c

# 12 ---- the earthquake (vase)
def draw12(c, t, d=8.0, l25=3.5, l26=5.0):
    q = lerp(.25, .6, prog(t, 0, l25)) + .4 * prog(t, l25, l26 + 2)
    col = prog(t, l26 - .1, l26 + 3.2)
    zoomc = sstep(prog(t, l25 - .1, l25 + .1)) * (1 - sstep(prog(t, l26 - .1, l26 + .1)))
    amp = 2 + 8 * prog(t, 0, d)
    c.cam(lerp(640, 230, zoomc), lerp(295, 240, zoomc), lerp(1.0, 2.5, zoomc), (amp * math.sin(t * 43), amp * math.cos(t * 37)))
    vskyline(c, t, quake=q, collapse=col); vwater(c, t, 425, -600, 2000, 120)
    for i, x in enumerate((470, 540, 620)):
        if t > l26 - .2:
            vfig(c, x + (t - l26) * 30, gy(x) + 20, .55, 'run', t, 1 if i != 1 else -1, 'run', seed=i)
            for j in range(3): c.line([(x - 30 + j * 14, gy(x) + 4 - j * 3), (x - 6 + j * 14, gy(x) + 2 - j * 3)], VT, 1.6)
    for i in range(3):
        if t > l25 + .3:
            u = prog(t, l25 + .3 + i * .5, l25 + 1.4 + i * .5); vjar(c, 160 + i * 70, lerp(190, 440, u * u), 1.0, u * 4 * (1 if i % 2 else -1))
@scene(12)
def s12(k):
    k.fx['mode'] = 'L'; c = k.cv(TERRA, 'L')
    draw12(c, k.t, k.d, k.lt(25), k.lt(26))
    ltitle(c, 'According to later ancient accounts...', 80, 38, int(255 * (prog(k.t, .2, .8) * (1 - prog(k.t, 3.2, 4.0)))))
    return c

# 13 ---- the sea returns (vase)
def draw13(c, t, mas, hit, d):
    rec = sstep(prog(t, 0, mas - .4)); fl = sstep(prog(t, hit, hit + 2.8))
    z = 1 + .55 * sstep(prog(t, hit - .5, hit + .6)); sk = shake(t, hit, 9, 5) if t > hit else (0, 0)
    c.cam(lerp(640, 420, sstep(prog(t, hit - .5, hit + .6))), lerp(295, 330, sstep(prog(t, hit - .5, hit + .6))), z, sk)
    vskyline(c, t, quake=0.0, collapse=0.0)
    wy = 425 + 75 * rec
    c.poly([(700, 420), (1500, 470 + 60 * rec), (1500, 700), (700, 700)], VK)
    for i in range(6): c.line([(760 + i * 110, 470 + 20 * rec + i * 5), (800 + i * 110, 486 + 20 * rec)], VT, 1.4)
    vwater(c, t, wy, 600 + 0 * rec, 2200, 120, 3)
    c.rect(-600, wy + 5 if False else 430, 700, 200, VK)
    e = prog(t, mas, hit)
    if t > mas - .2 and fl < 1:
        xw = lerp(1650, 120, ease_in(e) if e < 1 else 1) if t < hit else lerp(120, -500, prog(t, hit, hit + 2.5))
        H_ = 40 + 150 * min(1, e * 1.1)
        top = [(xw + 900, wy - 20), (xw + 460, wy - 40), (xw + 200, wy - H_ * .55), (xw + 50, wy - H_ * .95), (xw - 10, wy - H_), (xw - 55, wy - H_ * .85), (xw - 60, wy - H_ * .55), (xw - 35, wy - H_ * .2), (xw - 10, wy)]
        c.poly(top + [(xw + 900, 800), (xw - 20, 800)], VK)
        for i in range(4): c.line([(xw + 20 + i * 70, wy - H_ * (.55 - i * .08)), (xw + 55 + i * 70, wy - H_ * (.35 - i * .07)), (xw + 25 + i * 70, wy - H_ * (.2 - i * .05))], VT, 1.5)
        c.ell(xw + 10, wy - H_ * .55, 26, 26, None, VT, 1.6)
    if fl > 0:
        lv = lerp(425, 100, fl); c.poly([(-600, lv)] + [(x, lv + 6 * math.sin(x / 50 + t * 2)) for x in range(-600, 2000, 60)] + [(2000, 900), (-600, 900)], VK)
        for i in range(5): c.line([(x, lv + 20 + i * 30) for x in range(-600, 2000, 120)], VT, 1.4)
@scene(13)
def s13(k):
    k.fx['mode'] = 'L'; c = k.cv(TERRA, 'L')
    draw13(c, k.t, k.cue(28, 'massive'), k.cue(28, 'flooded'), k.d)
    c.hud(); c.text(300, 540, 'Said to have...', 30, INK, 'serif', 'c', int(255 * prog(k.t, k.lt(28) + .5, k.lt(28) + 1.2)), light(TERRA, .4), 2)
    return c

# 14 ---- cities swallowed (vase)
def draw14(c, t, d=7.5):
    u = sstep(t / d); c.cam(640, lerp(430, 295, u), lerp(1.7, 1.0, u))
    c.circ(1010, 150, 48, VK); [c.line([(1010 + 62 * math.cos(a * .52), 150 + 62 * math.sin(a * .52)), (1010 + 80 * math.cos(a * .52), 150 + 80 * math.sin(a * .52))], VK, 3) for a in range(12)]
    c.circ(1010, 150, 30, None, VT, 1.3)
    vwater(c, t, 430, -800, 2200, 400, 5)
    vcol(c, 640, 290, 436, 30, tilt=3)
    for i in range(5):
        x = 200 + i * 230 + 20 * math.sin(t * .7 + i); y = 428 + 3 * math.sin(t * 1.3 + i); c.rect(x, y - 4, 70, 7, VK)
    vjar(c, 940, 424 + 3 * math.sin(t * 1.4), 1.2, .5 * math.sin(t))
    for i, (hx, hw, hh, ro) in enumerate(HOUSES[:6]):
        sk = prog(t, 0, d) * 90 + i * 8; op = int(200 * (1 - prog(t, 0, d)) * .9)
        x0 = 120 + i * 110; y0 = 330 + sk * .5
        if op > 8: c.line([(x0, y0 + 90), (x0, y0), (x0 + hw, y0), (x0 + hw, y0 + 90)], VK, 2, op); c.line([(x0 - 4, y0), (x0 + hw / 2, y0 - 12), (x0 + hw + 4, y0)], VK, 2, op)
@scene(14)
def s14(k):
    k.fx['mode'] = 'L'; c = k.cv(TERRA, 'L'); draw14(c, k.t, k.d); return c

# 15 ---- the caveat: vase freezes, crack wipe, scribe, empty gulf
@scene(15)
def s15(k):
    tw0 = k.le(30) - .9; tw1 = k.lt(31) + .6; g = k.lt(33)
    def legend():
        c = k.cv(TERRA, 'L'); draw14(c, 7.5, 7.5); im = legend_post(c.finish(), 0.0)
        a = np.asarray(im).astype(np.float32); ds = sstep(prog(k.t, .3, tw0)); gr = a.mean(2, keepdims=True)
        return a * (1 - ds) + gr * ds * 1.0
    def flat():
        c = k.cv(vgrad(dark(NAVY, .2), mix(NAVY, BROWN, .3)))
        cxx = strip_cam(k.t, [0, g - .2], [640, 2040]); zz = 1 + .3 * sstep(prog(k.t, tw1, g - .3))
        c.cam(cxx + (60 if k.t < g else 0) * sstep(prog(k.t, tw1, g - .3)), 295 + 30 * sstep(prog(k.t, tw1, g - .3)), zz)
        if cxx < 1500:
            c.rect(-300, 100, 1700, 500, mix(NAVY, BROWN, .35)); c.rect(-300, 420, 1700, 300, mix(BROWN, INK, .35))
            for i, (x, y, r_) in enumerate(((260, 170, -3), (410, 230, 2), (130, 300, 3), (1020, 190, -2), (1130, 280, 3))):
                manuscript(c, x, y, 120, 150, .75, 5, i, tilt=r_); c.circ(x, y - 66, 5, (200, 40, 40), INK, 1.5)
            desk(c, 280, 1000, 440); lamp(c, 400, 442, 1.4, k.t)
            wr = math.sin(k.t * 9) * 10
            person(c, 700, 448, 1.7, 'scribe', k.t, 'curious', look=.5, armL=60, armR=50 - 6 * math.sin(k.t * 9), propR=None, seed=1, lean=4)
            manuscript(c, 700, 428, 240, 40, 0, 3, 1)
            c.line([(738, 410), (760 + wr, 425)], BROWN, 4)
        c.push(0, 0, 1, 1400, 0); skyline(c, k.t, dict(temple=0, houses=0, streets=0, figs=0, ships=0), lit=0); c.pop()
        c.rect(1400, 380, 1280, 400, mix(TEAL, NAVY, .3), None, op=0)
        k.fx['mode'] = 'E'
        c.hud()
        if k.t > k.cue(31, 'eyewitness') - .2: c.text(640, 50, 'No known eyewitness account.', 40, CREAM, 'serif', 'c', int(255 * prog(k.t, k.cue(31, 'eyewitness') - .2, k.cue(31, 'eyewitness') + .5)) if k.t < g - .3 else 0, INK, 4)
        if k.t > k.lt(32): c.text(640, 96, 'Written down later.', 36, AMBER, 'serif', 'c', int(255 * prog(k.t, k.lt(32), k.lt(32) + .5)) if k.t < g - .3 else 0, INK, 4)
        if k.t > g: c.text(640, 190, 'What actually happened?', 56, CREAM, 'serif', 'c', int(255 * prog(k.t, g, g + .6)), INK, 4)
        return c.finish()
    if k.t >= tw1: return flat()
    fl = flat(); lg = legend()
    if k.t < tw0 - .05: return Image.fromarray(np.clip(lg, 0, 255).astype(np.uint8))
    u = prog(k.t, tw0, tw1); cr = -150 + (W + 400) * ease_out(u)
    ys = np.arange(H)[:, None]; xs = np.arange(W)[None, :]
    bnd = cr + 50 * np.sin(ys / 37.0) + 35 * np.sin(ys / 11.0 + 2) + 25 * np.sin(ys / 83.0)
    d = xs - bnd; fa = np.asarray(fl).astype(np.float32)
    out = np.where((d < 0)[..., None], fa, lg)
    glow = np.exp(-np.abs(d) / 14.0)[..., None] * 255 * (1 - u * .3)
    out = np.clip(out + glow * (np.abs(d)[..., None] < 90), 0, 255)
    return Image.fromarray(out.astype(np.uint8))
