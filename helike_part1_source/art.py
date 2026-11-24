from lib import *

STONE = (240, 232, 212)
WALLS = [(240, 228, 204), (232, 214, 182), (246, 238, 222), (226, 200, 160), (236, 206, 170), (220, 196, 160)]
ROOFS = [(196, 92, 52), (178, 78, 46), (206, 110, 64), (168, 70, 44), (188, 84, 56)]
OUT = (70, 48, 34, 150)


def house(S, x, yb, w, h, rng, wall=None, roof=None, flat=False):
    wall = wall or rng.choice(WALLS)
    roof = roof or rng.choice(ROOFS)
    d = w * 0.30
    sy = d * 0.30
    # side wall
    S.poly([(x + w, yb), (x + w + d, yb - sy), (x + w + d, yb - h - sy), (x + w, yb - h)], shade(wall, 0.74))
    # front wall
    S.grect(x, yb - h, x + w, yb, shade(wall, 1.04), shade(wall, 0.86))
    S.rect(x, yb - h, x + w, yb, outline=OUT, ow=0.7)
    if flat:
        S.poly([(x - 2, yb - h), (x + w + d + 2, yb - h - sy), (x + w + d + 2, yb - h - sy - 4), (x - 2, yb - h - 4)],
               shade(wall, 1.1))
    else:
        rh = h * 0.42
        ins = w * 0.22
        S.gpoly([(x - 4, yb - h), (x + w + 4, yb - h), (x + w - ins, yb - h - rh), (x + ins, yb - h - rh)],
                shade(roof, 1.12), shade(roof, 0.92))
        S.poly([(x + w + 4, yb - h), (x + w + d + 4, yb - h - sy), (x + w + d - ins, yb - h - sy - rh),
                (x + w - ins, yb - h - rh)], shade(roof, 0.68))
        for i in range(1, 4):
            yy = yb - h - rh * i / 4
            S.line([(x + ins * i / 4 - 1, yy), (x + w - ins * i / 4 + 1, yy)], shade(roof, 0.74), max(0.6, w * 0.012),
                   False)
    # door + windows
    dw, dh = w * 0.2, h * 0.5
    dx = x + w * rng.uniform(0.2, 0.6)
    S.poly([(dx, yb), (dx, yb - dh * 0.8)] + [(dx + dw / 2 + math.cos(a) * dw / 2, yb - dh * 0.8 - math.sin(a) * dw / 2)
                                              for a in np.linspace(math.pi, 0, 7)] + [(dx + dw, yb)], (74, 50, 40))
    for wx in (0.12, 0.68):
        if abs((x + w * wx) - dx) > w * 0.22 and rng.random() < 0.85:
            ww = w * 0.13
            S.rect(x + w * wx, yb - h * 0.72, x + w * wx + ww, yb - h * 0.72 + ww * 1.4, (60, 46, 44))
            if rng.random() < 0.6:
                S.rect(x + w * wx - ww * 0.45, yb - h * 0.72, x + w * wx, yb - h * 0.72 + ww * 1.4, (66, 120, 150))
                S.rect(x + w * wx + ww, yb - h * 0.72, x + w * wx + ww * 1.45, yb - h * 0.72 + ww * 1.4, (66, 120, 150))


def column(S, x, yb, w, h, stone=STONE, base=True):
    S.grect(x - w / 2, yb - h, x + w / 2, yb, shade(stone, 0.80), shade(stone, 0.9), True, mid=shade(stone, 1.08))
    n = 4
    for i in range(1, n + 1):
        lx = x - w / 2 + w * i / (n + 1)
        S.line([(lx, yb - h + w * 0.2), (lx, yb - w * 0.15)], shade(stone, 0.76), max(0.5, w * 0.045), False)
    S.rect(x - w * 0.72, yb - h - w * 0.26, x + w * 0.72, yb - h - w * 0.06, shade(stone, 1.04))
    S.rect(x - w * 0.62, yb - h - w * 0.07, x + w * 0.62, yb - h + w * 0.14, shade(stone, 0.92))
    if base:
        S.rect(x - w * 0.62, yb - w * 0.2, x + w * 0.62, yb, shade(stone, 0.88))


def temple(S, cx, yb, w, h, n=6, stone=STONE, tymp=(104, 160, 196), steps=3, pediment=True):
    st = h * 0.075
    for i in range(steps):
        sw = w * (1.0 + 0.045 * (steps - i))
        y1 = yb - st * i
        S.gpoly([(cx - sw / 2, y1), (cx + sw / 2, y1), (cx + sw / 2, y1 - st), (cx - sw / 2, y1 - st)],
                shade(stone, 1.03 - 0.05 * i), shade(stone, 0.86 - 0.04 * i))
        S.line([(cx - sw / 2, y1 - st), (cx + sw / 2, y1 - st)], shade(stone, 1.1), 1, False)
    ytop = yb - st * steps
    cw = w * 0.94 / (n * 1.95)
    S.rect(cx - w * 0.43, ytop - h, cx + w * 0.43, ytop, (116, 96, 78))  # cella shadow
    S.grect(cx - w * 0.43, ytop - h, cx + w * 0.43, ytop, (92, 76, 66), (150, 124, 98))
    sp = (w * 0.94 - cw) / (n - 1)
    xs = [cx - w * 0.47 + cw / 2 + i * sp for i in range(n)]
    for x in xs:
        column(S, x, ytop, cw, h, stone)
    ya = ytop - h - cw * 0.3
    S.rect(cx - w * 0.5, ya - h * 0.09, cx + w * 0.5, ya, shade(stone, 0.95))  # architrave
    fz = h * 0.12
    S.rect(cx - w * 0.5, ya - h * 0.09 - fz, cx + w * 0.5, ya - h * 0.09, shade(stone, 1.05))
    k = 0
    while True:
        tx = cx - w * 0.5 + sp * 0.25 + k * sp / 2
        if tx > cx + w * 0.5 - 3:
            break
        S.rect(tx, ya - h * 0.09 - fz + 2, tx + sp * 0.12, ya - h * 0.09 - 2, shade(stone, 0.7))
        k += 1
    yc = ya - h * 0.09 - fz
    S.rect(cx - w * 0.53, yc - h * 0.05, cx + w * 0.53, yc, shade(stone, 1.08))
    if pediment:
        ph = h * 0.30
        S.gpoly([(cx - w * 0.53, yc - h * 0.05), (cx + w * 0.53, yc - h * 0.05), (cx, yc - h * 0.05 - ph)],
                shade(stone, 1.06), shade(stone, 0.92))
        t0 = 0.12
        S.poly([(cx - w * 0.53 * (1 - t0), yc - h * 0.06), (cx + w * 0.53 * (1 - t0), yc - h * 0.06),
                (cx, yc - h * 0.05 - ph * (1 - t0 * 1.1))], tymp)
        for i in range(-3, 4):  # relief figures
            fx = cx + i * w * 0.07
            hh = ph * (0.55 - abs(i) * 0.09)
            S.rect(fx - 2, yc - h * 0.06 - hh, fx + 2, yc - h * 0.06, (236, 226, 204))
            S.ell(fx, yc - h * 0.06 - hh, 3, 3, (236, 226, 204))
        S.line([(cx - w * 0.53, yc - h * 0.05), (cx, yc - h * 0.05 - ph), (cx + w * 0.53, yc - h * 0.05)],
               shade(stone, 0.7), 1.2, False)
    return xs, ytop


def cypress(S, x, yb, h, w=None):
    w = w or h * 0.22
    pts = []
    for a in np.linspace(0, math.pi, 12):
        pts.append((x - math.sin(a) * w / 2 * (0.6 + 0.4 * math.sin(a)), yb - h * (1 - math.cos(a)) / 2))
    for a in np.linspace(math.pi, 0, 12):
        pts.append((x + math.sin(a) * w / 2 * (0.6 + 0.4 * math.sin(a)), yb - h * (1 - math.cos(a)) / 2))
    S.gpoly(pts, (32, 66, 44), (20, 44, 32), True, mid=(44, 88, 56))
    S.line([(x, yb), (x, yb - h * 0.1)], (70, 46, 30), max(1, w * 0.1))


def olive(S, x, yb, s, rng):
    S.line([(x, yb), (x - s * 0.1, yb - s * 0.35), (x + s * 0.05, yb - s * 0.6)], (88, 66, 48), max(2, s * 0.1))
    for i in range(9):
        cx = x + rng.uniform(-0.45, 0.45) * s
        cy = yb - s * rng.uniform(0.5, 1.0)
        r = s * rng.uniform(0.2, 0.33)
        S.ell(cx, cy, r, r * 0.8, (84, 104, 70))
    for i in range(10):
        cx = x + rng.uniform(-0.4, 0.4) * s
        cy = yb - s * rng.uniform(0.65, 1.15)
        r = s * rng.uniform(0.12, 0.22)
        S.ell(cx, cy, r, r * 0.75, rng.choice([(138, 156, 104), (118, 138, 92), (154, 168, 116)]))


def bush(S, x, yb, s, rng, col=(70, 98, 58)):
    for i in range(5):
        S.ell(x + rng.uniform(-s, s) * 0.6, yb - s * rng.uniform(0.2, 0.6), s * rng.uniform(0.3, 0.5), s * 0.35,
              shade(col, rng.uniform(0.85, 1.25)))


def boat(S, x, yb, s, sail=(246, 238, 222), hull=(120, 62, 40), sails=1):
    S.poly([(x - 34 * s, yb - 12 * s), (x + 36 * s, yb - 12 * s), (x + 26 * s, yb), (x - 24 * s, yb)], hull)
    S.poly([(x - 34 * s, yb - 12 * s), (x + 36 * s, yb - 12 * s), (x + 34 * s, yb - 16 * s), (x - 38 * s, yb - 17 * s)],
           (210, 170, 110))
    S.line([(x, yb - 14 * s), (x, yb - 84 * s)], (80, 56, 40), 2 * s)
    S.gpoly([(x + 2 * s, yb - 82 * s), (x + 2 * s, yb - 20 * s), (x + 40 * s, yb - 22 * s)], shade(sail, 1.05),
            shade(sail, 0.8))
    if sails > 1:
        S.gpoly([(x - 3 * s, yb - 70 * s), (x - 3 * s, yb - 20 * s), (x - 30 * s, yb - 22 * s)], shade(sail, 0.98),
                shade(sail, 0.78))
    S.poly([(x, yb - 84 * s), (x - 12 * s, yb - 80 * s), (x, yb - 76 * s)], (196, 54, 44))


def sky_img(w, h, stops):
    return vgrad(w, h, stops)


def cloud_layer(w, h, seed, ys, col=(255, 246, 232), n=14, scale=1.0, alpha=200):
    rng = random.Random(seed)
    S = SS(w, h, 1)
    for i in range(n):
        cx = rng.uniform(0, w)
        cy = rng.uniform(*ys)
        for j in range(rng.randint(6, 11)):
            rx = rng.uniform(50, 130) * scale
            S.ell(cx + rng.uniform(-170, 170) * scale, cy + rng.uniform(-18, 16) * scale, rx, rx * 0.34,
                  col + (alpha,))
    im = blur(S.im, 14 * scale)
    # shaded underside
    a = np.asarray(im, np.float32)
    return Image.fromarray(a.astype(np.uint8), 'RGBA')


def bird(img, x, y, s, flap, col=(40, 36, 44)):
    d = ImageDraw.Draw(img)
    f = math.sin(flap) * s * 0.55
    d.line([(x - s, y + f * 0.2 - s * 0.1), (x - s * 0.5, y - f), (x, y), (x + s * 0.5, y - f),
            (x + s, y + f * 0.2 - s * 0.1)], fill=col, width=max(1, int(s * 0.16)), joint='curve')


def god_rays(base, cx, cy, t, a=0.25, color=(255, 232, 170), n=7, length=1400):
    ov = Image.new('RGB', base.size, (0, 0, 0))
    d = ImageDraw.Draw(ov)
    for i in range(n):
        ang = math.radians(60 + i * 11 + 4 * math.sin(t * 0.4 + i * 1.7))
        wd = math.radians(2.6 + 1.3 * math.sin(t * 0.7 + i))
        d.polygon([(cx, cy), (cx + math.cos(ang - wd) * length, cy + math.sin(ang - wd) * length),
                   (cx + math.cos(ang + wd) * length, cy + math.sin(ang + wd) * length)],
                  fill=tuple(int(c * a * (0.5 + 0.5 * math.sin(t * 0.5 + i * 2.3) ** 2)) for c in color))
    ov = ov.filter(ImageFilter.GaussianBlur(14))
    return ImageChops.screen(base, ov)


def grain_tiles(n=6, seed=5):
    rng = np.random.default_rng(seed)
    return [rng.normal(0, 5.0, (H, W, 1)).astype(np.float32) for _ in range(n)]
