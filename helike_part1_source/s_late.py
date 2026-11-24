from lib import *
from art import *
from people import *

_A = {}
LW7 = 2300
SKY_STOPS = [(0, (46, 104, 188)), (0.4, (120, 176, 226)), (0.75, (214, 228, 238)), (1, (244, 232, 204))]


def spr_house(w, h, seed):
    r = random.Random(seed)
    S = SS(int(w * 1.4 + 24), int(h * 1.5 + 24), 2)
    house(S, 10, S.h - 6, w, h, r, wall=r.choice([(246, 240, 226), (240, 230, 208), (250, 244, 232)]), flat=r.random() < 0.3)
    return S.get(), 10 + w / 2


def spr_temple(w, h, n, steps=3):
    S = SS(int(w * 1.2), int(h * 2.0), 2)
    temple(S, S.w / 2, S.h - 4, w, h, n, steps=steps)
    im = S.get()
    bb = im.getbbox()
    return im, im.width / 2


OBJS = [('house', 90, 160, 140, 1), ('house', 300, 170, 190, 2), ('house', 520, 150, 130, 3), ('temple', 940, 520, 170, 6),
        ('house', 1330, 170, 160, 4), ('house', 1560, 190, 180, 5), ('house', 1800, 150, 140, 6), ('house', 2020, 170, 170, 7),
        ('house', 2230, 140, 130, 8)]
GROUND = 520


def make_objs():
    if 'objs' in _A:
        return _A['objs']
    out = []
    for kind, x, w, h, sd in OBJS:
        if kind == 'house':
            im, ax = spr_house(w, h, sd)
        else:
            im, ax = spr_temple(w, h, 6)
        out.append((kind, x, im, ax, sd))
    _A['objs'] = out
    return out


def build_town():
    if 'sky' in _A:
        return
    rng = random.Random(3)
    sky = vgrad(1900, H, SKY_STOPS)
    sky = glow_at(sky, 500, 330, 700, (255, 236, 190), 0.5, 2)
    _A['sky'] = sky.convert('RGBA')
    cl = cloud_layer(1900, 400, 8, (80, 260), n=7, scale=0.9, alpha=200)
    _A['cl'] = cl
    S = SS(LW7, H, 2)
    r1 = ridge(LW7, 4, 440, 36, 300, 4)
    S.gpoly([(0, 600)] + [(x, r1[x]) for x in range(0, LW7, 4)] + [(LW7, 600)], (118, 142, 160), (170, 188, 190))
    r2 = ridge(LW7, 6, 490, 20, 160, 4)
    S.gpoly([(0, 600)] + [(x, r2[x]) for x in range(0, LW7, 4)] + [(LW7, 600)], (112, 140, 96), (152, 170, 112))
    for x in range(0, LW7, 60):
        if rng.random() < 0.6:
            cypress(S, x + rng.uniform(0, 40), 500, rng.uniform(70, 130))
    _A['far'] = S.get()
    # ground + stalls (static)
    S = SS(LW7, H, 2)
    S.gpoly([(0, GROUND - 6), (LW7, GROUND - 6), (LW7, H), (0, H)], (232, 202, 156), (188, 152, 108))
    for r_ in range(6):
        y = GROUND + 10 + r_ ** 1.7 * 14
        S.line([(0, y), (LW7, y)], (176, 142, 100), 1.2 + r_ * 0.3, False)
        for c in range(0, LW7, 70 + r_ * 24):
            xx = c + (r_ % 2) * 30
            S.line([(xx, y), (xx + (xx - LW7 / 2) * 0.03, y + 14 + r_ * 6)], (176, 142, 100), 1.0, False)
    for sx in (240, 700, 1250, 1700, 2100):
        yb = GROUND + 36
        for dx in (-62, 62):
            S.rect(sx + dx - 3, yb - 90, sx + dx + 3, yb, (96, 66, 44))
        cols = [(200, 64, 52), (246, 238, 220)]
        for i in range(7):
            x0 = sx - 76 + i * 22
            S.poly([(x0, yb - 96), (x0 + 22, yb - 96), (x0 + 28, yb - 66), (x0 + 6, yb - 66)], cols[i % 2])
        S.rect(sx - 70, yb - 36, sx + 70, yb - 28, (140, 100, 62))
        for i in range(9):
            S.ell(sx - 58 + i * 14.5, yb - 42, 6, 6, rng.choice([(210, 70, 46), (236, 180, 60), (120, 160, 70), (190, 100, 60)]))
        S.rect(sx - 64, yb - 28, sx - 56, yb, (96, 66, 44))
        S.rect(sx + 56, yb - 28, sx + 64, yb, (96, 66, 44))
        amphora(S, sx + 90, yb + 6, 1.0)
    _A['ground'] = S.get()
    _A['gl'] = None


def town_frame(t, cam, crowd, hide=None, collapse=None, panic_t=None):
    """compose far/mid layers. returns RGB and cam offset."""
    build_town()
    objs = make_objs()
    sky = plane(_A['sky'], 950 + cam * 0.12, H / 2, 1.0, 1280, 720).convert('RGB')
    cl = _A['cl']
    cv = plane(cl, clamp(640 + 60 + cam * 0.2 + t * 8, 640, 1260), 200, 1.0, 1280, 400, (W, 400))
    sky.paste(cv, (0, 20), cv)
    fv = plane(_A['far'], 640 + cam * 0.5, H / 2, 1.0, 1280, 720)
    sky.paste(fv, (0, 0), fv)
    return sky


def paste_obj(img, im, ax, x, cam, ybase=GROUND, alpha=None):
    px = int(x - cam - ax)
    py = int(ybase - im.height + 6)
    img.paste(im, (px, py), im)


def crowd_list(seed, n):
    r = random.Random(seed)
    out = []
    for i in range(n):
        out.append(dict(seed=r.randint(1, 60), y=r.uniform(GROUND + 26, GROUND + 130), x=r.uniform(0, LW7), dir=r.choice([-1, 1]),
                        sp=r.uniform(0.7, 1.1), off=r.random(), fem=r.random() < 0.4, car=('amphora' if r.random() < 0.15 else None)))
    return out


def draw_crowd(img, t, cam, crowd, mode='walk', alpha=1.0, scale_extra=1.0, speed_mul=1.0):
    for c in sorted(crowd, key=lambda c: c['y']):
        sc = (0.42 + (c['y'] - GROUND) / 140 * 0.5) * scale_extra
        hpx = 215 * sc
        x = (c['x'] + c['dir'] * t * 38 * sc * c['sp'] * speed_mul) % (LW7 + 200) - 100
        sx = x - cam
        if sx < -120 or sx > W + 120:
            continue
        spr = walk_sprite(c['seed'], t, 0.9 * c['sp'] * speed_mul, 200, offset=c['off'], mode=mode, female=c['fem'], carry=c['car'],
                          flip=(c['dir'] < 0))
        k = hpx / 200.0
        s2 = spr.resize((int(spr.width * k), int(spr.height * k)), Image.BILINEAR)
        img.paste(s2, (int(sx - s2.width / 2), int(c['y'] + 10 - s2.height)), s2)


# ============================================================ scene 7
def scene7(t):
    D = 9.0
    build_town()
    objs = make_objs()
    cam = 200 + t * 36
    img = town_frame(t, cam, None)
    gv = plane(_A['ground'], 640 + cam, H / 2, 1.0, 1280, 720)
    mid = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    for kind, x, im, ax, sd in objs:
        paste_obj(mid, im, ax, x, cam)
    img.paste(mid, (0, 0), mid)
    img.paste(gv, (0, 0), gv)
    if 'crowd7' not in _A:
        _A['crowd7'] = crowd_list(11, 16)
    draw_crowd(img, t, cam, _A['crowd7'])
    # foreground characters (parallax faster)
    man = sprite(21, 'stand', 0.0, 620, female=False, beard=True, cloak=True)
    wom = sprite(22, 'stand', 0.25, 600, female=True, carry='amphora', flip=True)
    bob = math.sin(t * 1.8) * 4
    mx = -60 - t * 6
    img.paste(man, (int(mx), int(H - man.height * 0.80 + bob)), man)
    wx = 860 + math.sin(t * 0.6) * 6 - t * 4
    img.paste(wom, (int(wx), int(H - wom.height * 0.80 + bob * 0.6)), wom)
    img = god_rays(img, 200, -100, t, 0.18)
    img = glow_at(img, 260, 60, 500, (255, 224, 160), 0.35, 2)
    d = ImageDraw.Draw(img)
    for i in range(4):
        bx = (t * 60 + i * 300) % (W + 200) - 100
        bird(img, bx, 90 + i * 24 + math.sin(t + i) * 10, 8, t * 8 + i)
    a = ease(prog(t, 0.3, 1.2))
    return img


# ============================================================ scene 8
LW8, LH8 = 2000, 1100
YB = 960


def poseidon(S, cx, yb, H_):
    M = (238, 232, 220)
    Sh = (176, 168, 160)
    Hi = (252, 248, 238)
    # pedestal
    for i, (w, h) in enumerate([(0.62, 0.07), (0.52, 0.09)]):
        y0 = yb - sum([0.07, 0.09][:i]) * H_
        S.grect(cx - w * H_ / 2, y0 - h * H_, cx + w * H_ / 2, y0, shade(M, 1.0 - 0.06 * i), shade(Sh, 0.92), True, mid=Hi)
        S.line([(cx - w * H_ / 2, y0 - h * H_), (cx + w * H_ / 2, y0 - h * H_)], Hi, 2, False)
    yb = yb - 0.16 * H_
    # trident shaft
    tx = cx + 0.30 * H_
    S.grect(tx - 5, yb - 1.55 * H_, tx + 5, yb, (230, 190, 90), (150, 106, 40), True, mid=(255, 232, 150))
    # robe
    S.gpoly([(cx - 0.11 * H_, yb - 0.50 * H_), (cx + 0.11 * H_, yb - 0.50 * H_), (cx + 0.17 * H_, yb - 0.02 * H_), (cx - 0.17 * H_, yb - 0.02 * H_)],
            Hi, Sh, True, mid=M)
    for i in range(7):
        a = -0.8 + i * 0.27
        S.line([(cx + a * 0.1 * H_, yb - 0.49 * H_), (cx + a * 0.15 * H_ + math.sin(i) * 6, yb - 0.04 * H_)], shade(Sh, 0.85), 3, False)
        S.line([(cx + a * 0.1 * H_ + 6, yb - 0.49 * H_), (cx + a * 0.15 * H_ + 8, yb - 0.1 * H_)], Hi, 2, False)
    # feet
    for dx in (-0.08, 0.08):
        S.ell(cx + dx * H_, yb - 0.015 * H_, 0.045 * H_, 0.02 * H_, shade(M, 0.9), shade(Sh, 0.8), 1.5)
    # torso
    S.gpoly([(cx - 0.12 * H_, yb - 0.80 * H_), (cx + 0.12 * H_, yb - 0.80 * H_), (cx + 0.10 * H_, yb - 0.50 * H_), (cx - 0.10 * H_, yb - 0.50 * H_)],
            Hi, Sh, True, mid=M)
    for sx in (-1, 1):
        S.arc(cx + sx * 0.045 * H_, yb - 0.70 * H_, 0.05 * H_, 0.04 * H_, 20, 160, Sh, 3)
    S.line([(cx, yb - 0.74 * H_), (cx, yb - 0.52 * H_)], Sh, 2, False)
    for i in range(3):
        S.line([(cx - 0.05 * H_, yb - (0.64 - i * 0.05) * H_), (cx + 0.05 * H_, yb - (0.64 - i * 0.05) * H_)], shade(Sh, 0.95), 2, False)
    # cloak
    S.gpoly([(cx - 0.13 * H_, yb - 0.80 * H_), (cx - 0.02 * H_, yb - 0.74 * H_), (cx + 0.1 * H_, yb - 0.50 * H_), (cx + 0.2 * H_, yb - 0.14 * H_),
             (cx - 0.15 * H_, yb - 0.12 * H_), (cx - 0.20 * H_, yb - 0.50 * H_)], M, Sh, False)
    for i in range(5):
        S.line([(cx - 0.12 * H_ + i * 0.03 * H_, yb - 0.74 * H_), (cx - 0.18 * H_ + i * 0.05 * H_, yb - 0.16 * H_)], Sh, 2.5, False)
    # arms
    S.line([(cx - 0.13 * H_, yb - 0.78 * H_), (cx - 0.24 * H_, yb - 0.64 * H_), (cx - 0.33 * H_, yb - 0.58 * H_)], shade(Sh, 0.95), 0.07 * H_)
    S.line([(cx - 0.13 * H_, yb - 0.78 * H_), (cx - 0.24 * H_, yb - 0.64 * H_), (cx - 0.33 * H_, yb - 0.58 * H_)], M, 0.055 * H_)
    S.ell(cx - 0.345 * H_, yb - 0.575 * H_, 0.03 * H_, 0.025 * H_, M, Sh, 1.2)
    S.line([(cx + 0.13 * H_, yb - 0.78 * H_), (cx + 0.24 * H_, yb - 0.70 * H_), (cx + 0.30 * H_, yb - 0.80 * H_)], shade(Sh, 0.95), 0.07 * H_)
    S.line([(cx + 0.13 * H_, yb - 0.78 * H_), (cx + 0.24 * H_, yb - 0.70 * H_), (cx + 0.30 * H_, yb - 0.80 * H_)], M, 0.055 * H_)
    S.ell(tx, yb - 0.80 * H_, 0.032 * H_, 0.03 * H_, M, Sh, 1.2)
    # head
    hx, hy = cx, yb - 0.91 * H_
    S.rect(hx - 0.025 * H_, hy + 0.04 * H_, hx + 0.025 * H_, hy + 0.1 * H_, Sh)
    for i in range(12):
        a = i / 12 * math.tau
        S.ell(hx + math.cos(a) * 0.065 * H_, hy - 0.01 * H_ + math.sin(a) * 0.075 * H_, 0.03 * H_, 0.03 * H_, shade(M, 0.92), Sh, 1.0)
    S.ell(hx, hy + 0.005 * H_, 0.055 * H_, 0.068 * H_, Hi, Sh, 1.5)
    # beard
    S.poly([(hx - 0.055 * H_, hy + 0.02 * H_), (hx + 0.055 * H_, hy + 0.02 * H_), (hx + 0.05 * H_, hy + 0.09 * H_), (hx, hy + 0.17 * H_),
            (hx - 0.05 * H_, hy + 0.09 * H_)], shade(M, 0.94), Sh, 1.2)
    for i in range(6):
        S.arc(hx - 0.04 * H_ + i * 0.016 * H_, hy + 0.09 * H_, 0.016 * H_, 0.04 * H_, 20, 160, Sh, 2.2)
    S.line([(hx - 0.04 * H_, hy - 0.012 * H_), (hx - 0.012 * H_, hy - 0.006 * H_)], Sh, 3, False)
    S.line([(hx + 0.04 * H_, hy - 0.012 * H_), (hx + 0.012 * H_, hy - 0.006 * H_)], Sh, 3, False)
    S.line([(hx, hy - 0.01 * H_), (hx - 0.006 * H_, hy + 0.03 * H_)], Sh, 2.2, False)
    S.line([(hx - 0.03 * H_, hy + 0.05 * H_), (hx + 0.03 * H_, hy + 0.05 * H_)], Sh, 2.2, False)
    # crown
    for i in range(-3, 4):
        x = hx + i * 0.018 * H_
        S.poly([(x - 0.01 * H_, hy - 0.055 * H_), (x, hy - (0.12 - abs(i) * 0.012) * H_), (x + 0.01 * H_, hy - 0.055 * H_)], (232, 196, 100), (150, 106, 40), 1.2)
    S.rect(hx - 0.06 * H_, hy - 0.06 * H_, hx + 0.06 * H_, hy - 0.045 * H_, (232, 196, 100), (150, 106, 40), 1.2)
    # trident head
    ty = yb - 1.55 * H_
    G, GD = (240, 204, 100), (150, 106, 40)
    S.line([(tx - 0.07 * H_, ty + 0.02 * H_), (tx - 0.07 * H_, ty - 0.1 * H_)], GD, 9)
    S.line([(tx + 0.07 * H_, ty + 0.02 * H_), (tx + 0.07 * H_, ty - 0.1 * H_)], GD, 9)
    S.line([(tx, ty), (tx, ty - 0.14 * H_)], GD, 9)
    S.line([(tx - 0.07 * H_, ty + 0.02 * H_), (tx - 0.07 * H_, ty - 0.1 * H_)], G, 6)
    S.line([(tx + 0.07 * H_, ty + 0.02 * H_), (tx + 0.07 * H_, ty - 0.1 * H_)], G, 6)
    S.line([(tx, ty), (tx, ty - 0.14 * H_)], G, 6)
    S.arc(tx, ty + 0.02 * H_, 0.07 * H_, 0.06 * H_, 0, 180, GD, 9)
    S.arc(tx, ty + 0.02 * H_, 0.07 * H_, 0.06 * H_, 0, 180, G, 6)
    for dx, y_ in [(-0.07, -0.1), (0, -0.14), (0.07, -0.1)]:
        S.poly([(tx + dx * H_ - 0.015 * H_, ty + y_ * H_), (tx + dx * H_, ty + (y_ - 0.045) * H_), (tx + dx * H_ + 0.015 * H_, ty + y_ * H_)], G, GD, 1.2)
    return tx, ty


def build8():
    if 'sky8' in _A:
        return
    rng = random.Random(15)
    sky = vgrad(LW8, LH8, [(0, (30, 92, 190)), (0.5, (92, 160, 224)), (0.8, (190, 220, 238)), (1, (240, 236, 214))])
    _A['sky8'] = sky.convert('RGBA')
    _A['cl8'] = cloud_layer(LW8 + 600, 700, 21, (120, 560), n=12, scale=1.4, alpha=230)
    S = SS(LW8, LH8, 2)
    r = ridge(LW8, 2, 760, 36, 260, 4)
    S.gpoly([(0, LH8)] + [(x, r[x]) for x in range(0, LW8, 4)] + [(LW8, LH8)], (96, 130, 150), (170, 196, 196))
    S.rect(0, 800, LW8, 870, (60, 150, 196))  # sea strip
    r2 = ridge(LW8, 8, 840, 20, 140, 4)
    S.gpoly([(0, LH8)] + [(x, r2[x]) for x in range(0, LW8, 4)] + [(LW8, LH8)], (84, 124, 84), (140, 160, 104))
    for x in range(0, LW8, 55):
        cypress(S, x + rng.uniform(0, 30), 900, rng.uniform(80, 150))
    _A['far8'] = S.get()
    S = SS(LW8, LH8, 2)
    S.gpoly([(0, YB - 4), (LW8, YB - 4), (LW8, LH8), (0, LH8)], (232, 214, 176), (190, 164, 120))
    for r_ in range(8):
        y = YB + 6 + r_ ** 1.6 * 8
        S.line([(0, y), (LW8, y)], (176, 148, 108), 1.4, False)
    # temple
    temple(S, 600, YB, 780, 300, 8, steps=5)
    # trees
    for x, h in [(60, 160), (1020, 200), (1960, 140)]:
        cypress(S, x, YB, h)
    olive(S, 1900, YB, 100, rng)
    tx, ty = poseidon(S, 1500, YB, 520)
    _A['tri'] = (tx, ty)
    _A['near8'] = S.get()
    # cracks (revealed over time)
    rr = random.Random(9)
    cr = []
    for k in range(6):
        x, y = rng.uniform(900, 1800), YB + 40
        pts = [(x, y)]
        for j in range(14):
            x += rr.uniform(-34, 34)
            y += rr.uniform(6, 24)
            pts.append((x, y))
        cr.append(pts)
    _A['cracks'] = cr


def cam8(t):
    keys = [(0, 640, 760, 1.0), (4.2, 600, 560, 1.05), (7.4, 1100, 560, 1.06), (9.0, 1230, 520, 1.1), (14.0, 1260, 480, 1.18), (17.9, 1300, 420, 1.42)]
    for i in range(len(keys) - 1):
        a, b = keys[i], keys[i + 1]
        if a[0] <= t <= b[0]:
            q = ease((t - a[0]) / (b[0] - a[0]))
            return tuple(a[j] + (b[j] - a[j]) * q for j in (1, 2, 3))
    return keys[-1][1:]


def scene8(t):
    build8()
    cx, cy, z = cam8(t)
    quake = ease(prog(t, 11.7, 12.6)) * (1 - ease(prog(t, 14.2, 15.3)))
    img = plane(_A['sky8'], LW8 / 2 + (cx - LW8 / 2) * 0.2, LH8 / 2 + (cy - LH8 / 2) * 0.2, 1 + (z - 1) * 0.3, 1500, 844).convert('RGB')
    cl = _A['cl8']
    cc = plane(cl, LW8 / 2 + 300 + (cx - LW8 / 2) * 0.35 + t * 14, 350, 1 + (z - 1) * 0.5, 1500, 700, (W, int(700 * W / 1500)))
    img.paste(cc, (0, int(30 - (cy - 560) * 0.1)), cc)
    fv = plane(_A['far8'], LW8 / 2 + (cx - LW8 / 2) * 0.6, LH8 / 2 + (cy - LH8 / 2) * 0.6, 1 + (z - 1) * 0.7, 1500, 844)
    img.paste(fv, (0, 0), fv)
    nv = plane(_A['near8'], cx, cy, z, 1500, 844)
    img.paste(nv, (0, 0), nv)
    # layer->screen map
    bw, bh = 1500 / z, 844 / z
    x0 = clamp(cx - bw / 2, 0, LW8 - bw)
    y0 = clamp(cy - bh / 2, 0, LH8 - bh)
    ks = W / bw
    L2S = lambda x, y: ((x - x0) * ks, (y - y0) * ks)
    tx, ty = _A['tri']
    # trident glow + aura
    gp = ease(prog(t, 7.6, 9.2))
    flick = 1.0 if quake < 0.05 else 0.6 + 0.4 * math.sin(t * 40)
    if gp > 0:
        sx, sy = L2S(tx, ty - 40)
        img = glow_at(img, sx, sy, int(230 * ks * (0.9 + 0.1 * math.sin(t * 3))), (255, 214, 120), 0.85 * gp * flick, 1.6)
        scx, scy = L2S(1500, 700)
        for k in range(3):
            q = ((t * 0.35 + k / 3.0) % 1)
            rr_ = (160 + q * 560) * ks
            d = ImageDraw.Draw(img, 'RGBA')
            if 9.0 < t < 12.5:
                a = int(120 * (1 - q) * ease(prog(t, 9.0, 9.8)) * (1 - ease(prog(t, 11.4, 12.5))))
                d.ellipse((scx - rr_, scy - rr_, scx + rr_, scy + rr_), outline=(150, 220, 255, a), width=4)
    # quake effects
    if quake > 0.02:
        d = ImageDraw.Draw(img, 'RGBA')
        for pts in _A['cracks']:
            n = int(len(pts) * quake)
            if n > 1:
                P = [L2S(*p) for p in pts[:n]]
                d.line(P, fill=(40, 28, 20, 255), width=max(2, int(4 * ks)))
        for k in range(70):
            age = (t * 0.9 + k * 0.137) % 1
            px = (k * 331) % 1300
            py = 120 + age * 560 + (k * 17) % 90
            r = 2 + (k % 4)
            d.ellipse((px - r, py - r, px + r, py + r), fill=(214, 190, 150, int(200 * quake * (1 - age))))
        sdim = Image.new('RGBA', (W, H), (150, 110, 70, int(70 * quake)))
        img.paste(sdim, (0, 0), sdim)
    for i in range(3):
        bx = (t * 50 + i * 380) % (W + 200) - 100
        bird(img, bx, 100 + i * 30 + math.sin(t + i) * 10, 9, t * 8 + i)
    # name card
    a = ease(prog(t, 8.1, 9.0)) * (1 - ease(prog(t, 16.2, 17.2)))
    if a > 0:
        c1 = text_img('POSEIDON', font('cinzel', 64, 800), (255, 244, 214, 255), 10)
        sub = 'GOD OF THE SEA' if t < 11.8 else 'GOD OF THE SEA  ·  LORD OF EARTHQUAKES'
        c2 = text_img(sub, font('cinzel', 26, 600), (210, 232, 246, 255), 6)
        lay = Image.new('RGBA', (max(c1.width, c2.width) + 60, 170), (0, 0, 0, 0))
        lay.paste(c1, (30, 14), c1)
        ImageDraw.Draw(lay).line([(30, 100), (30 + int((lay.width - 60) * eo(prog(t, 8.3, 9.3))), 100)], fill=(236, 200, 120, 255), width=2)
        lay.paste(c2, (30, 114), c2)
        sh_ = blur(Image.merge('RGBA', (Image.new('L', lay.size, 0),) * 3 + (lay.getchannel('A').point(lambda v: int(v * 0.7)),)), 5)
        img.paste(fade_img(sh_, a), (62, 82), fade_img(sh_, a))
        img.paste(fade_img(lay, a), (60, 80), fade_img(lay, a))
    if quake > 0.02:
        k = quake * 9
        img = img.transform((W, H), Image.AFFINE, (1, 0, math.sin(t * 61) * k, 0, 1, math.cos(t * 53) * k), Image.BILINEAR)
    return img


# ============================================================ scene 9
def dust_cloud(img, x, y, r, a, col=(196, 170, 134)):
    lay = Image.new('RGBA', (int(r * 3), int(r * 2.4)), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    rr = random.Random(int(x))
    for i in range(7):
        cx, cy = r * 1.5 + rr.uniform(-r * 0.6, r * 0.6), r * 1.2 + rr.uniform(-r * 0.5, r * 0.4)
        rad = r * rr.uniform(0.4, 0.7)
        d.ellipse((cx - rad, cy - rad, cx + rad, cy + rad), fill=col + (int(180 * a),))
    lay = blur(lay, r * 0.18)
    img.paste(lay, (int(x - lay.width / 2), int(y - lay.height / 2)), lay)


def collapse_paste(img, im, ax, x, cam, t_since, seed, ybase=GROUND):
    """vertical slices that sink/tilt as they collapse"""
    r = random.Random(seed)
    n = 3
    sw = im.width / n
    for i in range(n):
        d_ = r.uniform(0, 0.8)
        q = ease((t_since - d_) / 1.5)
        sl = im.crop((int(i * sw), 0, int((i + 1) * sw), im.height))
        bb = sl.getbbox()
        if bb is None:
            continue
        keep = max(2, int(sl.height - (sl.height - (sl.height - bb[1])) * 0 - q * (sl.height - bb[1]) * 0.86))
        top = sl.crop((0, 0, sl.width, keep)) if q > 0 else sl
        # slide visible content: remove bottom part
        vis_h = (sl.height - bb[1]) * (1 - 0.86 * q)
        piece = sl.crop((0, sl.height - int((sl.height - bb[1])), sl.width, sl.height)) if q == 0 else \
            sl.crop((0, bb[1], sl.width, bb[1] + max(2, int(vis_h))))
        ang = r.choice([-1, 1]) * q * r.uniform(0.15, 0.5) * 57.3
        pc = piece.rotate(ang, Image.BICUBIC, expand=True)
        px = int(x - cam - ax + i * sw + (r.uniform(-1, 1) * 36 * q) + (sw - pc.width) / 2)
        py = int(ybase + 6 - pc.height + (pc.height - piece.height) * 0.4)
        img.paste(pc, (px, py), pc)
    # rubble
    q = ease(t_since / 1.8)
    if q > 0:
        d = ImageDraw.Draw(img, 'RGBA')
        for k in range(14):
            rx = x - cam - ax + r.uniform(0, im.width)
            rw = r.uniform(10, 34) * q
            d.ellipse((rx - rw, ybase + 6 - rw * 0.5 - r.uniform(0, 14) * q, rx + rw, ybase + 6 + rw * 0.2), fill=r.choice([(186, 160, 124, 255), (150, 126, 100, 255), (206, 180, 140, 255)]))


def scene9(t):
    D = 10.7
    build_town()
    objs = make_objs()
    cam = 330 + t * 8
    q0 = 2.9
    img = town_frame(t, cam, None)
    # sky darkens with dust
    dk = ease(prog(t, 3.0, 5.5)) * 0.4
    img = tint(img, (140, 96, 60), dk)
    gv = plane(_A['ground'], 640 + cam, H / 2, 1.0, 1280, 720)
    mid = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    order = 0
    for kind, x, im, ax, sd in objs:
        sx = x - cam
        if sx < -400 or sx > W + 400:
            continue
        tf = 3.3 + abs(x - 940) / 1000.0 * 2.8 + (0.0 if kind == 'temple' else 0.4)
        if t < tf:
            jit = math.sin(t * 70 + x) * 2.5 * ease(prog(t, q0, q0 + 0.5))
            tmp_cam = cam - jit
            paste_obj(mid, im, ax, x, tmp_cam)
        else:
            collapse_paste(mid, im, ax, x, cam, t - tf, sd)
    img.paste(mid, (0, 0), mid)
    img.paste(gv, (0, 0), gv)
    # cracks in ground
    cr = ease(prog(t, 3.2, 5.2))
    d = ImageDraw.Draw(img, 'RGBA')
    if cr > 0:
        rr = random.Random(4)
        for k in range(7):
            x = rr.uniform(100, 1200)
            y = GROUND + rr.uniform(40, 160)
            pts = [(x, y)]
            for j in range(int(10 * cr) + 1):
                x += rr.uniform(-40, 40)
                y += rr.uniform(-6, 18)
                pts.append((x, y))
            d.line(pts, fill=(40, 26, 20, 255), width=int(3 + k % 3))
    # crowd
    if 'crowd9' not in _A:
        _A['crowd9'] = crowd_list(31, 18)
    panic = t > 3.1
    draw_crowd(img, t, cam, _A['crowd9'], 'panic' if panic else 'walk', speed_mul=(3.0 if panic else 1.0))
    # dust clouds at each collapse
    for kind, x, im, ax, sd in objs:
        tf = 3.3 + abs(x - 940) / 1000.0 * 2.8 + (0.0 if kind == 'temple' else 0.4)
        ts = t - tf
        sx = x - cam
        if 0 < ts < 4.5 and -200 < sx < W + 200:
            p = ts / 4.5
            dust_cloud(img, sx, GROUND - 50 - p * 120, 90 + p * 170, (1 - p) ** 1.3 * 0.9)
    # falling debris
    if t > 3.4:
        rr = random.Random(7)
        d = ImageDraw.Draw(img, 'RGBA')
        for k in range(90):
            t0 = 3.4 + rr.uniform(0, 4.0)
            ts = t - t0
            if ts < 0 or ts > 1.6:
                continue
            x0 = rr.uniform(0, W)
            vy = rr.uniform(-380, -120)
            vx = rr.uniform(-160, 160)
            xx = x0 + vx * ts
            yy = GROUND - 20 + vy * ts + 900 * ts * ts
            s_ = rr.uniform(3, 10)
            d.polygon([(xx, yy - s_), (xx + s_, yy), (xx, yy + s_), (xx - s_, yy - 2)], fill=(210, 188, 150, 255))
    # foreground panicking man
    if t > 3.0:
        a = eo(prog(t, 3.0, 3.8))
        ph = ((t * 1.6) % 1.0)
        ph = round(ph * 16) % 16 / 16
        fgm = sprite(41, 'panic', ph, 620, female=False, beard=True, cloak=False, flip=True)
        sh = math.sin(t * 38) * 5
        img.paste(fgm, (int(W - 520 + (1 - a) * 500 + sh), int(H - fgm.height * 0.66 + math.cos(t * 31) * 5)), fgm)
    # quake colour + vignette punch
    qk = ease(prog(t, q0, q0 + 0.4)) * (1 - ease(prog(t, 8.8, 9.8))) * 0.9
    # the sea
    ps = ease(prog(t, 8.5, 10.2))
    if ps > 0:
        d = ImageDraw.Draw(img, 'RGBA')
        lvl = H * (1 - 0.88 * ps)
        pts = [(0, H)] + [(x, lvl + math.sin(x / 70 + t * 3) * (16 + 20 * ps) + math.sin(x / 23 - t * 5) * 6) for x in range(0, W + 20, 16)] + [(W, H)]
        d.polygon(pts, fill=(18, 84, 128, 215))
        d.line(pts[1:-1], fill=(224, 244, 250, 255), width=7)
        for k in range(40):
            x = (k * 83 + t * 40) % W
            y = lvl + 20 + (k * 41) % int(max(H - lvl, 40))
            d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(220, 244, 250, 120))
    fo = ease(prog(t, 10.1, 10.7))
    if fo > 0:
        img = Image.blend(img, Image.new('RGB', img.size, (4, 10, 20)), fo)
    shk = (1 + 2.0 * ease(prog(t, q0, q0 + 0.3))) * (1 - 0.6 * ease(prog(t, 7.5, 9.5))) if t > q0 else 0.3
    k = shk * (6 if t > q0 else 0.0)
    if k > 0:
        img = img.transform((W, H), Image.AFFINE, (1, 0, math.sin(t * 67) * k + math.sin(t * 29) * k * 0.6, 0, 1, math.cos(t * 59) * k), Image.BILINEAR)
    return img
