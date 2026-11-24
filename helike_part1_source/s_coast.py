from lib import *
from art import *

LW, LH = 2200, 1240
BW, BH = 1792, 1008  # layer-space size of the output window at zoom 1
_A = {}


def hy(xs):
    pts = [(0, 880), (300, 800), (600, 705), (900, 590), (1100, 478), (1300, 440), (1500, 452), (1800, 560),
           (2200, 700)]
    y = np.interp(xs, [p[0] for p in pts], [p[1] for p in pts])
    k = np.exp(-np.linspace(-3, 3, 61) ** 2)
    k /= k.sum()
    ypad = np.pad(y, 30, mode='edge')
    y = np.convolve(ypad, k, 'valid')
    return y + ridge(len(xs), 4, 0, 10, 60, 3)


def shore(xs):
    return np.interp(xs, [0, 500, 1000, 1500, 2200], [985, 962, 988, 1012, 1062])


def build():
    if _A:
        return _A
    xs = np.arange(LW)
    HY, SH = hy(xs), shore(xs)
    rng = random.Random(7)
    # ---------- sky
    sky = vgrad(LW, LH, [(0, (36, 78, 156)), (0.30, (88, 146, 206)), (0.48, (172, 206, 228)), (0.57, (252, 226, 186)),
                         (1, (252, 226, 186))])
    sky = glow_at(sky, 520, 640, 900, (255, 214, 150), 0.7, 2.2)
    _A['sky'] = sky.convert('RGBA')
    _A['clouds'] = cloud_layer(LW + 700, 520, 3, (150, 340), n=11, scale=1.0, alpha=185)
    # ---------- mountains
    S = SS(LW, LH, 1)
    m1 = ridge(LW, 11, 610, 40, 220, 5) - 70 * np.exp(-((xs - 400) / 380) ** 2) - 20 * np.exp(-((xs - 1900) / 300) ** 2)
    S.poly([(0, LH)] + [(x, m1[x]) for x in range(0, LW, 3)] + [(LW, LH)], (150, 168, 196))
    peak = 330
    m2 = ridge(LW, 5, 600, 30, 160, 5) - np.clip(1 - np.abs(xs - 1520) / 560, 0, 1) ** 1.2 * (600 - peak)
    S.gpoly([(0, LH)] + [(x, m2[x]) for x in range(0, LW, 3)] + [(LW, LH)], (126, 120, 160), (170, 160, 190))
    # snow-less rock facets on big mountain
    for i in range(26):
        cx = 1520 + rng.uniform(-300, 300)
        cy = m2[int(cx)] + rng.uniform(10, 140)
        S.poly([(cx, cy), (cx + rng.uniform(30, 90), cy + rng.uniform(40, 110)), (cx - rng.uniform(10, 50),
                                                                                  cy + rng.uniform(40, 120))],
               (104, 96, 142))
    m3 = ridge(LW, 9, 660, 26, 100, 5)
    S.gpoly([(0, LH)] + [(x, m3[x]) for x in range(0, LW, 3)] + [(LW, LH)], (112, 128, 118), (176, 176, 160))
    mt = S.get()
    # haze at the bottom of mountains
    hz = Image.new('RGBA', (LW, LH), (0, 0, 0, 0))
    ha = np.zeros((LH, LW), np.uint8)
    ha[600:760, :] = (np.linspace(0, 150, 160)[:, None]).astype(np.uint8)
    ha[760:] = 150
    hz.putalpha(Image.fromarray(ha))
    hzc = Image.new('RGBA', (LW, LH), (250, 226, 190, 255))
    hzc.putalpha(Image.fromarray(ha))
    mt = Image.alpha_composite(mt, hzc)
    _A['mount'] = mt
    # ---------- sea (opaque below horizon)
    sea = vgrad(LW, LH - 690, [(0, (214, 224, 210)), (0.05, (120, 196, 214)), (0.35, (40, 130, 176)),
                               (1, (12, 56, 108))]).convert('RGBA')
    sn = fnoise(LW, LH - 690, 18, 3, 3)
    a = np.asarray(sea, np.float32)
    a[..., :3] *= (0.93 + 0.14 * sn)[..., None]
    sea = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')
    full = Image.new('RGBA', (LW, LH), (0, 0, 0, 0))
    full.paste(sea, (0, 690))
    _A['sea'] = full
    # ---------- land
    S = SS(LW, LH, 2)
    pts_top = [(x, HY[x]) for x in range(0, LW, 4)]
    pts_bot = [(x, SH[x] + 10) for x in range(LW - 1, -1, -4)]
    S.gpoly(pts_top + pts_bot, (150, 148, 96), (118, 104, 72))
    # terraces/rocky texture
    for i in range(150):
        x = rng.uniform(0, LW)
        y = rng.uniform(HY[int(min(x, LW - 1))] + 10, SH[int(min(x, LW - 1))] - 10)
        S.ell(x, y, rng.uniform(20, 70), rng.uniform(6, 16), rng.choice([(140, 142, 90), (162, 146, 100), (122, 126, 80)]))
    # beach strip
    S.poly([(x, SH[x]) for x in range(0, LW, 4)] + [(x, SH[x] + 16) for x in range(LW - 1, -1, -4)], (226, 204, 160))
    land = multiply_noise(S.get(), 0.10, 26, 5)
    _A['land'] = land
    # ---------- buildings layer
    B = SS(LW, LH, 2)
    placed = []
    cand = []
    for i in range(1500):
        x = rng.uniform(20, LW - 60)
        ix = int(x)
        y = rng.uniform(HY[ix] + 34, SH[ix] - 20)
        if 1020 < x < 1560 and y < HY[ix] + 90:
            continue
        cand.append((y, x))
    cand.sort()
    for y, x in cand:
        s = 0.55 + 0.75 * clamp((y - 420) / 640)
        w = rng.uniform(52, 96) * s
        h = rng.uniform(40, 78) * s
        if any(abs(x - px) < (w + pw) * 0.62 and abs(y - py) < max(h, ph) * 0.55 for px, py, pw, ph in placed):
            continue
        placed.append((x, y, w, h))
        house(B, x, y, w, h, rng, flat=rng.random() < 0.25)
        if rng.random() < 0.12:
            cypress(B, x + w + 14 * s, y + 4, rng.uniform(70, 110) * s)
        elif rng.random() < 0.10:
            olive(B, x - 14 * s, y + 3, 44 * s, rng)
    # acropolis platform
    ax0, ax1 = 1060, 1560
    ay = float(HY[1300]) + 4
    B.gpoly([(ax0, ay - 14), (ax1, ay - 14), (ax1 + 40, ay + 95), (ax0 - 40, ay + 95)], (214, 192, 150),
            (170, 146, 108))
    for r in range(2):
        yy = ay + 24 + r * 34
        B.line([(ax0 - 8 * r, yy), (ax1 + 8 * r, yy)], (140, 116, 84, 160), 1.4, False)
        for k in range(26):
            xx = ax0 + (k + (r % 2) * 0.5) * (ax1 - ax0) / 25
            B.line([(xx, yy), (xx, yy + 34)], (140, 116, 84, 120), 1.0, False)
    B.rect(ax0 - 6, ay - 22, ax1 + 6, ay - 12, (236, 224, 198))
    temple(B, 1300, ay - 14, 330, 92, 8)
    temple(B, 1470, ay - 14, 100, 46, 4, pediment=True)
    for cxx in (1090, 1530):
        cypress(B, cxx, ay - 12, 90)
    # quay + harbour
    for x in range(0, LW, 4):
        pass
    B.gpoly([(0, SH[0] - 14)] + [(x, SH[x] - 8) for x in range(0, LW, 8)] + [(LW, SH[-1] - 8)] +
            [(LW, SH[-1] + 20)] + [(x, SH[x] + 22) for x in range(LW - 1, -1, -8)], (206, 190, 156), (130, 112, 88))
    for x in range(10, LW, 46):
        B.arc(x, SH[x] + 16, 12, 9, 180, 360, (84, 66, 52), 3)
    # waterfront stoa
    for i, (x, w) in enumerate([(120, 230), (520, 150), (1650, 260)]):
        y = SH[x] - 16
        B.rect(x, y - 34, x + w, y, (232, 214, 180))
        B.poly([(x - 6, y - 34), (x + w + 6, y - 34), (x + w - 8, y - 50), (x + 8, y - 50)], (190, 88, 52))
        for k in range(int(w // 22)):
            column(B, x + 12 + k * 22, y, 8, 30)
    for i in range(24):
        x = rng.uniform(0, LW)
        ix = int(min(x, LW - 1))
        if i % 2:
            cypress(B, x, SH[ix] - 12, rng.uniform(60, 120))
        else:
            olive(B, x, SH[ix] - 12, rng.uniform(40, 66), rng)
    bl = B.get()
    _A['bld'] = bl
    # empty version: scrub of trees only
    E = SS(LW, LH, 2)
    r2 = random.Random(21)
    for i in range(70):
        x = r2.uniform(0, LW)
        ix = int(min(x, LW - 1))
        y = r2.uniform(HY[ix] + 20, SH[ix] - 14)
        if r2.random() < 0.5:
            bush(E, x, y, r2.uniform(16, 34), r2, (92, 112, 66))
        else:
            olive(E, x, y, r2.uniform(26, 46), r2)
    for i in range(40):  # scattered stones
        x = r2.uniform(0, LW)
        ix = int(min(x, LW - 1))
        y = r2.uniform(HY[ix] + 20, SH[ix] - 10)
        E.ell(x, y, r2.uniform(5, 12), r2.uniform(3, 6), (176, 166, 140))
    _A['empty'] = E.get()
    # ---------- boats
    boats = []
    for (s, sails, hull) in [(1.0, 2, (120, 62, 40)), (0.8, 1, (90, 60, 50)), (1.3, 2, (150, 74, 46)),
                              (0.7, 1, (110, 70, 44))]:
        Bs = SS(150, 160, 3)
        boat(Bs, 75, 150, 1.6 * s, hull=hull, sails=sails)
        boats.append(Bs.get())
    _A['boats'] = boats
    _A['boatpos'] = [(300, 1090), (780, 1140), (1380, 1170), (1900, 1130)]
    # glints
    r3 = random.Random(2)
    _A['glints'] = [(r3.uniform(0, LW), r3.uniform(720, LH - 30), r3.uniform(0, 6.28), r3.uniform(0.8, 2.2))
                    for _ in range(420)]
    # dissolve score map at output res
    yy, xx = np.mgrid[0:H, 0:W]
    n = fnoise(W, H, 40, 12, 4)
    _A['score'] = (0.55 * (xx / W) + 0.45 * n).astype(np.float32)
    r4 = np.random.default_rng(3)
    _A['pp'] = [(r4.integers(0, W), r4.integers(0, H)) for _ in range(5000)]
    return _A


def cam_view(A, cx, cy, z):
    """render sky..sea..land at camera; returns RGB image + layer->screen map"""
    img = plane(A['sky'], LW / 2 + (cx - LW / 2) * 0.15, LH / 2 + (cy - LH / 2) * 0.1, 1 + (z - 1) * 0.25, BW, BH)
    return img


def render_coast(t, cx, cy, z, vanish=0.0, drift=0.0, show_city=True, glint=1.0, tone=0.0):
    A = build()
    img = plane(A['sky'], LW / 2 + (cx - LW / 2) * 0.15, LH / 2 + (cy - LH / 2) * 0.1, 1 + (z - 1) * 0.25, BW, BH).convert('RGB')
    # clouds
    cl = A['clouds']
    cx_ = clamp(LW / 2 + (cx - LW / 2) * 0.2 + drift + 350, BW / 2, cl.width - BW / 2)
    cv = plane(cl, cx_, 260, 1.0, BW, 520, out=(W, int(520 * W / BW)))
    img.paste(cv, (0, int(20 - (cy - 700) * 0.1)), cv)
    mv = plane(A['mount'], LW / 2 + (cx - LW / 2) * 0.45, LH / 2 + (cy - LH / 2) * 0.45, 1 + (z - 1) * 0.6, BW, BH)
    img.paste(mv, (0, 0), mv)
    # sea with animation
    sea = A['sea'].copy()
    sd = ImageDraw.Draw(sea)
    for (gx, gy, ph, sp) in A['glints']:
        v = math.sin(t * sp * 2.2 + ph)
        if v > 0.35:
            L = (10 + (gy - 700) * 0.09) * (0.5 + v * 0.5)
            c = (255, 240, 205, int(200 * v * glint))
            sd.line([(gx - L, gy), (gx + L, gy)], fill=c, width=2 if gy > 900 else 1)
    for i, (b, (bx, by)) in enumerate(zip(A['boats'], A['boatpos'])):
        yy = by + math.sin(t * 1.3 + i * 1.7) * 5
        rot = math.sin(t * 1.1 + i) * 2.5
        bb = b.rotate(rot, Image.BICUBIC, center=(75, 150))
        sea.paste(bb, (int(bx - 75 + math.sin(t * 0.2 + i) * 14), int(yy - 150)), bb)
        # wake lines
        sd.line([(bx - 55, yy + 3), (bx + 50, yy + 3)], fill=(255, 255, 255, 70), width=2)
    sv = plane(sea, LW / 2 + (cx - LW / 2), LH / 2 + (cy - LH / 2), z, BW, BH)
    img.paste(sv, (0, 0), sv)
    lv = plane(A['land'], cx, cy, z, BW, BH)
    img.paste(lv, (0, 0), lv)
    ev = plane(A['empty'], cx, cy, z, BW, BH)
    img.paste(ev, (0, 0), ev)
    if show_city:
        bv = plane(A['bld'], cx, cy, z, BW, BH)
        if vanish > 0:
            al = np.asarray(bv.getchannel('A'), np.float32)
            sc = A['score']
            gone = np.clip((vanish * 1.5 - sc) * 7, 0, 1)
            al *= (1 - gone)
            bv.putalpha(Image.fromarray(al.astype(np.uint8)))
        img.paste(bv, (0, 0), bv)
        if 0 < vanish < 1:
            d = ImageDraw.Draw(img)
            sc = A['score']
            rr = random.Random(int(t * 24))
            for (px, py) in A['pp']:
                s_ = sc[py, px]
                dd = vanish * 1.5 - s_
                if 0.0 < dd < 0.22:
                    yy = py - dd * 260 + math.sin(dd * 20 + px) * 6
                    r = 1.4 + 2.2 * (1 - dd / 0.22)
                    c = (255, int(214 + 30 * (1 - dd / 0.22)), int(120 + 80 * (1 - dd / 0.22)))
                    d.ellipse((px - r, yy - r, px + r, yy + r), fill=c)
    # light
    img = god_rays(img, W * 0.32, -80, t, 0.16 + 0.04 * tone)
    img = glow_at(img, W * 0.22, H * 0.1, 520, (255, 210, 140), 0.35 + 0.1 * tone, 2.0)
    return img


def scene1(t):
    D = 6.55
    p = t / D
    cx = 1020 + p * 120
    cy = 640
    z = 0.84 + 0.14 * ease(p)
    van = ease(prog(t, 4.2, 6.2))
    img = render_coast(t, cx, cy, z, van, drift=t * 14)
    # birds
    for i in range(5):
        bx = (t * 70 + i * 160) % (W + 200) - 100
        by = 130 + i * 34 + math.sin(t * 0.9 + i) * 12
        bird(img, bx, by, 9 - i * 0.6, t * 9 + i * 1.3)
    # dusk colour grade as city vanishes: slightly desaturate/cool
    img = tint(img, (40, 54, 90), 0.28 * van)
    # title
    a = ease(prog(t, 0.6, 1.4)) * (1 - ease(prog(t, 3.6, 4.4)))
    if a > 0:
        tt = text_img('THE CITY THAT DISAPPEARED WITHOUT A TRACE', font('cinzel', 26, 700), (255, 240, 210, 255), 4)
        sh = text_img('THE CITY THAT DISAPPEARED WITHOUT A TRACE', font('cinzel', 26, 700), (0, 0, 0, 160), 4)
        tmp = Image.new('RGBA', (W, 90), (0, 0, 0, 0))
        tx = (W - tt.width) // 2
        tmp.paste(blur(Image.merge('RGBA', (sh.split())), 3), (tx + 2, 22), blur(sh, 3))
        tmp.paste(tt, (tx, 20), tt)
        img.paste(fade_img(tmp, a), (0, 34), fade_img(tmp, a))
        # line ornament
        d = ImageDraw.Draw(img)
        ww = int(220 * eo(prog(t, 0.8, 1.8)))
        d.line([(W / 2 - ww, 82), (W / 2 + ww, 82)], fill=(236, 200, 120), width=1)
    return img


def title_layer(txt, size, t0, t, glowc=(255, 210, 120)):
    """HELIKE letter-by-letter reveal; returns RGBA overlay and its y"""
    f = font('cinzel', size, 800)
    letters = list(txt)
    sp = size * 0.10
    widths = [ImageDraw.Draw(Image.new('L', (4, 4))).textlength(c, font=f) for c in letters]
    total = sum(widths) + sp * (len(letters) - 1)
    lay = Image.new('RGBA', (W, int(size * 2.2)), (0, 0, 0, 0))
    x = (W - total) / 2
    gl = Image.new('RGBA', lay.size, (0, 0, 0, 0))
    for i, (c, w_) in enumerate(zip(letters, widths)):
        a = ease(prog(t - t0, i * 0.11, i * 0.11 + 0.5))
        if a > 0:
            L = Image.new('RGBA', (int(w_ + 80), int(size * 2)), (0, 0, 0, 0))
            d = ImageDraw.Draw(L)
            d.text((40, size * 0.3), c, font=f, fill=(0, 0, 0, 255))
            m = L.getchannel('A')
            grad = vgrad(L.width, L.height, [(0.2, (255, 244, 210)), (0.55, (242, 200, 120)), (0.8, (176, 124, 56))])
            col = Image.new('RGBA', L.size, (0, 0, 0, 0))
            col.paste(grad, (0, 0), m)
            sc = 1.0 + (1 - a) * 0.4
            col = col.resize((int(col.width * sc), int(col.height * sc)), Image.BICUBIC)
            col = fade_img(col, a)
            off = (col.width - L.width) // 2, (col.height - L.height) // 2 + int((1 - a) * -30)
            lay.paste(col, (int(x - 40 - off[0]), int(-off[1])), col)
            gl.paste(fade_img(col, 0.9), (int(x - 40 - off[0]), int(-off[1])), col)
        x += w_ + sp
    glow = blur(gl, 18)
    ga = np.asarray(glow, np.float32)
    return lay, glow, total


def scene4(t):
    D = 8.0
    p = t / D
    cx = 820 + p * 300
    cy = 640
    z = 0.88 + 0.1 * p
    img = render_coast(t, cx, cy, z, 0.0, drift=t * 16 + 200, tone=1)
    for i in range(4):
        bx = (t * 60 + i * 260 + 100) % (W + 200) - 100
        by = 90 + (i % 3) * 40 + math.sin(t * 0.8 + i) * 10
        bird(img, bx, by, 8, t * 8 + i)
    # text
    t_i = 5.0 if t > 0 else 5
    # "over 2,300 years ago"
    a = ease(prog(t, 0.3, 1.2)) * (1 - ease(prog(t, 4.6, 5.4)))
    if a > 0:
        tt = text_img('OVER 2,300 YEARS AGO', font('cinzel', 34, 600), (255, 240, 210, 255), 7)
        tmp = Image.new('RGBA', (tt.width + 40, tt.height + 40), (0, 0, 0, 0))
        tmp.paste(blur(Image.new('RGBA', tt.size, (0, 0, 0, 170)), 1), (22, 22), blur(tt, 3))
        tmp.paste(tt, (20, 20), tt)
        img.paste(fade_img(tmp, a), ((W - tmp.width) // 2, 200 - int((1 - a) * -14)), fade_img(tmp, a))
    t0 = 6.7
    if t > t0 - 0.1:
        # darken sky behind title
        dk = ease(prog(t, t0 - 0.2, t0 + 1.2)) * 0.38
        img = tint(img, (14, 20, 40), dk)
        lay, glow, total = title_layer('HELIKE', 170, t0, t)
        y = 240
        pulse = 0.55 + 0.15 * math.sin(t * 3)
        ga = Image.new('RGB', img.size, (0, 0, 0))
        gl_rgb = Image.new('RGB', glow.size, (255, 190, 90))
        gm = glow.getchannel('A').point(lambda v: int(v * pulse))
        gbase = Image.new('RGB', glow.size, (0, 0, 0))
        gbase.paste(gl_rgb, (0, 0), gm)
        reg = img.crop((0, y, W, y + lay.height))
        img.paste(ImageChops.screen(reg, gbase), (0, y))
        img.paste(lay, (0, y), lay)
        # shine sweep
        sw = prog(t, t0 + 0.9, t0 + 1.9)
        if 0 < sw < 1:
            sx = -200 + sw * (W + 400)
            shine = Image.new('RGBA', lay.size, (0, 0, 0, 0))
            ImageDraw.Draw(shine).polygon([(sx, 0), (sx + 60, 0), (sx - 20, lay.height), (sx - 80, lay.height)],
                                          fill=(255, 255, 255, 190))
            shine = blur(shine, 6)
            m = ImageChops.multiply(shine.getchannel('A'), lay.getchannel('A'))
            wh = Image.new('RGB', lay.size, (255, 255, 255))
            img.paste(wh, (0, y), m)
        ow = int(total * 0.5 * eo(prog(t, t0 + 1.0, t0 + 2.0)))
        d = ImageDraw.Draw(img)
        yy = y + 190
        d.line([(W / 2 - ow, yy), (W / 2 + ow, yy)], fill=(240, 206, 130), width=2)
        d.ellipse((W / 2 - 4, yy - 4, W / 2 + 4, yy + 4), fill=(240, 206, 130))
    return img
