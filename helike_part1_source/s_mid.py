from lib import *
from art import *

_A = {}
INK = (74, 46, 28, 255)
PAPER = (238, 220, 178, 255)


# =============================================================== scene 5
def prof(x):
    pts = [(300, 540), (480, 436), (600, 352), (740, 272), (820, 232), (900, 272), (1000, 360), (1100, 438), (1280, 480)]
    return float(np.interp(x, [p[0] for p in pts], [p[1] for p in pts]))


def sk_house(S, x, y, w, h, rng):
    d = w * 0.25
    S.poly([(x + w, y), (x + w + d, y - 5), (x + w + d, y - h - 5), (x + w, y - h)], (214, 190, 146), INK, 1.4)
    S.rect(x, y - h, x + w, y, PAPER, INK, 1.6)
    S.poly([(x - 3, y - h), (x + w + 3, y - h), (x + w - 5, y - h - h * 0.4), (x + 5, y - h - h * 0.4)], (206, 150, 106), INK, 1.5)
    S.poly([(x + w + 3, y - h), (x + w + d + 3, y - h - 5), (x + w + d - 5, y - h - 5 - h * 0.4), (x + w - 5, y - h - h * 0.4)],
           (176, 120, 84), INK, 1.4)
    S.rect(x + w * 0.4, y - h * 0.55, x + w * 0.65, y, (96, 66, 44), INK, 1.0)
    for k in range(3):
        S.line([(x + 3, y - h * 0.3 - k * 6), (x + w * 0.3, y - h * 0.3 - k * 6)], (150, 120, 84), 1, False)


def build_parch():
    if 'parch' in _A:
        return
    rng = random.Random(12)
    base = vgrad(W, H, [(0, (232, 212, 168)), (1, (210, 182, 134))])
    n = fnoise(W, H, 90, 3, 5)
    n2 = fnoise(W, H, 6, 9, 2)
    a = np.asarray(base, np.float32) * (0.86 + 0.24 * n + 0.04 * n2)[..., None]
    yy, xx = np.mgrid[0:H, 0:W]
    ed = np.minimum(np.minimum(xx, W - xx), np.minimum(yy, H - yy)).astype(np.float32)
    burn = np.clip(ed / 150.0, 0, 1) ** 0.8
    a *= (0.45 + 0.55 * burn)[..., None]
    _A['paper'] = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    S = SS(W, H, 2)
    # waves left & bottom
    for r in range(9):
        for c in range(14):
            x = 40 + c * 52 + (r % 2) * 26
            y = 330 + r * 38
            if x + 30 < 330 - (r * 6) or (y > 590):
                S.arc(x, y, 22, 8, 200, 340, (60, 100, 130, 255), 2)
    # skyline drawn by sorted objects
    objs = []
    for row in range(1, 6):
        x = 330 + row * 20
        while x < 1150:
            y = prof(x) + 14 + row * 30
            if y < 600:
                objs.append((y, 'h', x + rng.uniform(-8, 8), rng.uniform(34, 52), rng.uniform(26, 38)))
            x += rng.uniform(52, 66)
    objs.sort()
    # hill outline
    S.line([(x, prof(x)) for x in range(300, 1281, 10)], INK, 3)
    for y, k, x, w, h in objs:
        sk_house(S, x, y, w, h, rng)
    # walls with towers
    for i in range(9):
        x = 360 + i * 85
        y = prof(x) + 165
        if y < 600:
            S.rect(x, y - 24, x + 22, y, PAPER, INK, 1.4)
            S.line([(x, y - 24), (x + 4, y - 30), (x + 8, y - 24), (x + 12, y - 30), (x + 16, y - 24), (x + 20, y - 30)], INK, 1.2)
    # temple
    cx = 820
    S.rect(cx - 90, 226, cx + 90, 244, (220, 196, 150), INK, 1.5)
    S.rect(cx - 82, 204, cx + 82, 226, (210, 184, 140), INK, 1.2)
    for i in range(7):
        x = cx - 76 + i * 25.3
        S.rect(x - 4, 174, x + 4, 226, PAPER, INK, 1.4)
    S.rect(cx - 86, 160, cx + 86, 174, PAPER, INK, 1.5)
    S.poly([(cx - 92, 160), (cx + 92, 160), (cx, 126)], PAPER, INK, 1.6)
    # trees inland
    for x in (1160, 1210, 1240, 1190):
        S.line([(x, 520), (x, 490)], INK, 2)
        S.ell(x, 478, 14, 16, (150, 168, 108, 255), INK, 1.4)
    # boats
    for (bx, by) in [(120, 440), (220, 520)]:
        S.poly([(bx - 26, by), (bx + 26, by), (bx + 16, by + 12), (bx - 16, by + 12)], (180, 130, 96, 255), INK, 1.5)
        S.line([(bx, by), (bx, by - 44)], INK, 1.6)
        S.poly([(bx + 2, by - 42), (bx + 2, by - 4), (bx + 30, by - 6)], PAPER, INK, 1.4)
    ink = S.get()
    _A['ink'] = ink
    # skyline for quill
    # flood water tint overlays
    # underwater scene
    U = SS(W, H, 2)
    U.im.paste(vgrad(W * 2, H * 2, [(0, (30, 130, 156)), (0.5, (14, 82, 120)), (1, (6, 36, 70))]), (0, 0))
    U.gpoly([(0, 560), (W, 540), (W, H), (0, H)], (86, 128, 126), (24, 54, 66))
    rr = random.Random(5)
    for i in range(40):
        U.line([(rr.uniform(0, W), rr.uniform(580, 710))] * 1 + [(rr.uniform(0, W), rr.uniform(580, 710))], (110, 150, 142), 1.4, False) if False else None
        x = rr.uniform(0, W)
        y = rr.uniform(570, 712)
        U.arc(x, y, rr.uniform(30, 80), 5, 190, 350, (110, 156, 148), 2)
    st = (150, 190, 188)
    # ruins: standing column + fallen drums + wall
    U.poly([(820, 600), (1200, 586), (1220, 620), (800, 628)], (60, 98, 104))
    for i in range(4):
        U.rect(930 + i * 30, 560 - i * 3, 970 + i * 30, 604 - i * 3, shade(st, 0.7 + i * 0.05), (30, 60, 70), 1.5)
    column(U, 760, 612, 54, 330, shade(st, 0.95))
    column(U, 1040, 618, 46, 150, shade(st, 0.8))
    for i in range(3):
        U.ell(520 + i * 70, 640 + (i % 2) * 14, 36, 14, shade(st, 0.75), (30, 60, 70), 1.5)
        U.rect(484 + i * 70, 620 + (i % 2) * 14, 556 + i * 70, 640 + (i % 2) * 14, shade(st, 0.75))
    for (x, y, w, h) in [(300, 620, 120, 40), (330, 592, 80, 30), (1100, 640, 140, 36), (140, 640, 100, 30)]:
        U.rect(x, y, x + w, y + h, shade(st, 0.62), (30, 60, 70), 1.5)
        U.line([(x, y + h / 2), (x + w, y + h / 2)], (30, 60, 70), 1.4, False)
    U.ell(640, 660, 18, 22, (150, 82, 56), (50, 40, 40), 1.5)
    S2 = U.get().convert('RGB')
    a = np.asarray(S2, np.float32)
    a *= (0.88 + 0.24 * fnoise(W, H, 40, 4, 3))[..., None]
    _A['uw'] = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    _A['fish'] = [(rr.uniform(0, W), rr.uniform(160, 520), rr.uniform(30, 70), rr.uniform(0.6, 1.4), rr.uniform(0, 6.28)) for _ in range(22)]
    _A['weed'] = [(rr.uniform(0, W), rr.uniform(590, 700), rr.uniform(60, 150), rr.uniform(0, 6.28)) for _ in range(34)]
    _A['bub'] = [(rr.uniform(0, W), rr.uniform(0, 1), rr.uniform(0.04, 0.12), rr.uniform(2, 5)) for _ in range(50)]
    # parchment rods
    _A['parch'] = 1


def paper_frame(t, ink_p, flood, lens=None, extras=None):
    build_parch()
    img = _A['paper'].copy().convert('RGBA')
    ink = _A['ink']
    if ink_p > 0:
        xr = int(ink_p * (W + 40))
        part = ink.crop((0, 0, min(xr, W), H))
        img.paste(part, (0, 0), part)
    img = img.convert('RGB')
    d = ImageDraw.Draw(img, 'RGBA')
    # quill
    if 0 < ink_p < 1:
        x = ink_p * (W + 40)
        y = min(prof(x) - 8 + 20 * math.sin(t * 22), 500) if x > 300 else 330 + 40 * math.sin(t * 9)
        d.line([(x, y), (x + 70, y - 110)], fill=(236, 230, 214, 255), width=4)
        d.polygon([(x, y), (x + 8, y - 22), (x + 14, y - 18)], fill=(60, 40, 30, 255))
        d.line([(x + 70, y - 110), (x + 120, y - 190)], fill=(210, 200, 186, 255), width=7)
    # flood
    if flood > 0:
        lvl = H - flood * 430
        pts = [(0, H)] + [(x, lvl + math.sin(x / 40 + t * 2.4) * 8 + math.sin(x / 17 - t * 3) * 3) for x in range(0, W + 20, 20)] + [(W, H)]
        ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(ov).polygon(pts, fill=(36, 110, 170, 150))
        ImageDraw.Draw(ov).line(pts[1:-1], fill=(190, 230, 250, 220), width=3)
        ov = Image.blend(Image.new('RGBA', ov.size, (0, 0, 0, 0)), ov, 1.0)
        img.paste(ov, (0, 0), ov)
    # rods
    rods = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rods)
    for y0 in (0, H - 26):
        for k in range(26):
            f = 1 - abs(k - 13) / 13
            rd.line([(0, y0 + k), (W, y0 + k)], fill=(int(88 + 70 * f), int(56 + 44 * f), int(34 + 26 * f), 255))
    img.paste(rods, (0, 0), rods)
    return img


def draw_lens(img, mx, my, r, zoom, gold):
    # magnified crop
    box = (mx - r / zoom, my - r / zoom, mx + r / zoom, my + r / zoom)
    big = img.resize((2 * r, 2 * r), Image.BICUBIC, box=box)
    if gold > 0:
        d = ImageDraw.Draw(big, 'RGBA')
        cx, cy = r, r + 10
        for i, (dx, dw, dh) in enumerate([(-60, 40, 30), (-10, 52, 40), (50, 40, 26), (-30, 80, 12)]):
            d.rectangle((cx + dx, cy - dh + 22, cx + dx + dw, cy + 22), outline=(255, 214, 120, int(255 * gold)), width=3,
                        fill=(255, 190, 80, int(70 * gold)))
        for i in range(5):
            x = cx - 70 + i * 30
            d.rectangle((x, cy - 56, x + 8, cy - 8), outline=(255, 226, 150, int(255 * gold)), width=2)
        big = glow_at(big, r, r, int(r * 0.95), (255, 190, 90), 0.5 * gold, 1.6)
    m = Image.new('L', (2 * r, 2 * r), 0)
    ImageDraw.Draw(m).ellipse((2, 2, 2 * r - 2, 2 * r - 2), fill=255)
    # handle
    d = ImageDraw.Draw(img, 'RGBA')
    hx, hy = mx + r * 0.7, my + r * 0.7
    d.line([(hx, hy), (hx + 110, hy + 110)], fill=(0, 0, 0, 70), width=26)
    d.line([(hx, hy), (hx + 110, hy + 110)], fill=(96, 62, 36, 255), width=22)
    d.line([(hx + 4, hy + 2), (hx + 106, hy + 104)], fill=(150, 100, 60, 255), width=6)
    img.paste(big, (int(mx - r), int(my - r)), m)
    d = ImageDraw.Draw(img, 'RGBA')
    d.ellipse((mx - r - 3, my - r - 3, mx + r + 3, my + r + 3), outline=(168, 118, 56, 255), width=10)
    d.ellipse((mx - r + 6, my - r + 6, mx + r - 6, my + r - 6), outline=(240, 214, 140, 160), width=2)
    d.arc((mx - r + 14, my - r + 14, mx + r - 14, my + r - 14), 200, 260, fill=(255, 255, 255, 150), width=5)


SEA_X, LAND = (250, 500), (1010, 500)


def scene5(t):
    build_parch()
    # split boundary
    xb = W
    if 6.9 < t < 18.9:
        xb = W - (W - 650) * ease(prog(t, 6.9, 8.0)) + (W - 650) * ease(prog(t, 17.9, 18.9)) if True else W
    ink_p = prog(t, 0.3, 5.0)
    flood = ease(prog(t, 4.6, 6.4)) * (1 - ease(prog(t, 17.7, 19.2)))
    img = paper_frame(t, ink_p, flood)
    d = ImageDraw.Draw(img, 'RGBA')
    # handwritten annotation (exaggerated?)
    if 15.4 < t < 19:
        a = prog(t, 15.4, 17.2)
        txt = 'exaggerated?'
        f = font('gari', 54, 500)
        n = int(len(txt) * a)
        tx = Image.new('RGBA', (440, 90), (0, 0, 0, 0))
        ImageDraw.Draw(tx).text((6, 4), txt[:n], font=f, fill=(120, 30, 24, 255))
        if a >= 1:
            ImageDraw.Draw(tx).line([(0, 50), (int(330 * prog(t, 17.0, 17.5)), 40)], fill=(150, 30, 24, 255), width=4)
        al = 1 - ease(prog(t, 17.7, 18.7))
        tx = fade_img(tx, al)
        tx = tx.rotate(6, Image.BICUBIC, expand=True)
        img.paste(tx, (100, 200), tx)
    # underwater panel
    if xb < W - 1:
        uw = _A['uw'].copy()
        ud = ImageDraw.Draw(uw, 'RGBA')
        for (x, y, h, ph) in _A['weed']:
            pts = [(x + math.sin(t * 1.4 + ph + j * 0.6) * (j * 3.5), y - j * h / 6) for j in range(7)]
            ud.line(pts, fill=(52, 120, 84, 255), width=5)
        for (x, y, s, sp, ph) in _A['fish']:
            fx = (x + t * 50 * sp * (1 if int(ph) % 2 else -1)) % (W + 200) - 100
            fy = y + math.sin(t * 1.5 + ph) * 18
            dr = 1 if int(ph) % 2 else -1
            col = (250, 190, 90, 220) if ph > 3 else (170, 210, 230, 200)
            ud.ellipse((fx - s * 0.5, fy - s * 0.2, fx + s * 0.5, fy + s * 0.2), fill=col)
            ud.polygon([(fx - dr * s * 0.5, fy), (fx - dr * s * 0.85, fy - s * 0.22 * (1 + math.sin(t * 9 + ph))),
                        (fx - dr * s * 0.85, fy + s * 0.22)], fill=col)
        for (x, p0, sp, r) in _A['bub']:
            by = H - ((p0 + t * sp) % 1) * (H + 40)
            ud.ellipse((x + math.sin(t + x) * 8 - r, by - r, x + math.sin(t + x) * 8 + r, by + r), outline=(220, 245, 255, 190), width=1)
        uw = god_rays(uw, 700, -60, t, 0.28, (140, 220, 230), 8, 1100)
        sweep = prog(t, 9.2, 13.0)
        if 0 < sweep < 1:
            sx = 100 + sweep * 1100
            uw = glow_at(uw, sx, 620, 190, (255, 232, 170), 0.9, 1.4)
        if 12.6 < t < 15.5:
            uw = glow_at(uw, 760, 480, 230, (255, 226, 150), 0.5 * math.sin((t - 12.6) / 2.9 * math.pi), 1.5)
        uw = tint(uw, (8, 40, 70), 0.12)
        m = Image.new('L', (W, H), 0)
        ImageDraw.Draw(m).polygon([(xb + 60, 0), (W, 0), (W, H), (xb - 60, H)], fill=255)
        img.paste(uw, (0, 0), m)
        d = ImageDraw.Draw(img)
        d.line([(xb + 60, 0), (xb - 60, H)], fill=(250, 238, 210), width=7)
        d.line([(xb + 60, 0), (xb - 60, H)], fill=(70, 46, 28), width=2)
    # beat C/D
    if t > 18.9:
        lt = t
        # lens path
        if lt < 21.2:
            p = prog(lt, 19.0, 21.2)
            mx = 150 + (SEA_X[0] - 150) * eo(p) + math.sin(lt * 3) * 26 * p
            my = 320 + (SEA_X[1] - 320) * eo(p) + math.cos(lt * 2.6) * 20 * p
        elif lt < 23.6:
            p = ease(prog(lt, 21.2, 23.6))
            mx = SEA_X[0] + (LAND[0] - SEA_X[0]) * p
            my = SEA_X[1] + (LAND[1] - SEA_X[1]) * p - math.sin(p * math.pi) * 90
        else:
            mx, my = LAND[0] + math.sin(lt * 1.2) * 6, LAND[1] + math.cos(lt * 1.4) * 5
        gold = ease(prog(lt, 22.6, 24.0))
        # annotations: arrow + X
        if lt > 24.6:
            pa = prog(lt, 24.6, 26.6)
            pts = []
            for k in range(0, int(60 * pa) + 1):
                s = k / 60.0
                x = SEA_X[0] + (LAND[0] - SEA_X[0]) * s
                y = SEA_X[1] + (LAND[1] - SEA_X[1]) * s - math.sin(s * math.pi) * 140
                if k % 3 != 2:
                    pts.append((x, y))
            for (x, y) in pts:
                d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=(150, 40, 30, 255))
        if lt > 26.4:
            red_pa = prog(lt, 26.4, 27.4)
            cx, cy = SEA_X
            for k, (a_, b_) in enumerate([((-1, -1), (1, 1)), ((1, -1), (-1, 1))]):
                q = clamp(red_pa * 2 - k)
                if q > 0:
                    d.line([(cx + a_[0] * 44, cy + a_[1] * 44), (cx + a_[0] * 44 + (b_[0] - a_[0]) * 44 * q,
                                                                   cy + a_[1] * 44 + (b_[1] - a_[1]) * 44 * q)], fill=(180, 30, 28, 255), width=12)
        if lt > 24.2:
            ft = font('gari', 40, 500)
            for (txt, pos, col, aa) in [('where everyone looked', (SEA_X[0] - 150, SEA_X[1] + 62), (110, 30, 26), prog(lt, 26.6, 27.6)),
                                         ('buried, inland', (LAND[0] - 330, LAND[1] + 108), (130, 90, 20), prog(lt, 25.6, 26.8))]:
                if aa > 0:
                    tx = Image.new('RGBA', (460, 70), (0, 0, 0, 0))
                    ImageDraw.Draw(tx).text((6, 4), txt, font=ft, fill=col + (255,))
                    tx = fade_img(tx, aa)
                    img.paste(tx, pos, tx)
        r_ = 120
        if lt > 24.0:
            pulse = lt - 24.0
            for k in range(3):
                q = ((lt * 0.5 + k / 3.0) % 1)
                rr_ = 130 + q * 260
                d.ellipse((LAND[0] - rr_, LAND[1] - rr_, LAND[0] + rr_, LAND[1] + rr_), outline=(255, 206, 110, int(160 * (1 - q) * ease(prog(lt, 24.0, 25.0)))), width=4)
        draw_lens(img, mx, my, r_, 1.8, gold)
        if lt > 28.2:
            a = ease(prog(lt, 28.4, 31.0))
            img = glow_at(img, LAND[0], LAND[1], int(300 + a * 900), (255, 220, 150), a, 1.3)
    return img


# =============================================================== scene 6
S6 = 110
MW, MH = int(28 * 0.79 * S6) + 1, int(16 * S6) + 1


def mp(lon, lat):
    return ((lon - 8) * 0.79 * S6, (46 - lat) * S6)


LAND_POLY = [(13.6, 46.5), (13.6, 45.6), (15, 44.5), (16.5, 43.3), (18.5, 42.4), (19.4, 41.8), (19.4, 40.4), (20.2, 39.6),
             (20.7, 38.8), (21.1, 38.4), (21.5, 38.35), (21.8, 38.36), (22.4, 38.4), (22.9, 38.3), (22.95, 38.1), (22.4, 38.16), (21.9, 38.2),
             (21.5, 38.2), (21.4, 37.9), (21.1, 37.6), (21.6, 36.9), (22.0, 36.8), (22.4, 36.5), (22.5, 36.4), (22.8, 36.8), (23.2, 36.45),
             (23.0, 37.2), (22.8, 37.5), (23.2, 37.55), (23.3, 37.8), (23.1, 37.95), (23.5, 37.95), (23.8, 37.7), (24.0, 37.65), (24.0, 38.1),
             (23.6, 38.3), (23.2, 38.5), (22.9, 38.8), (23.2, 39.0), (22.9, 39.35), (22.6, 40.1), (22.9, 40.5), (23.5, 40.3), (23.9, 40.0),
             (23.8, 40.4), (24.4, 40.6), (25.5, 40.9), (26.2, 40.5), (26.2, 40.0), (26.2, 39.5), (26.7, 39.3), (26.7, 38.7), (26.8, 38.3),
             (27.2, 38.2), (27.3, 37.5), (27.2, 37.0), (28.2, 36.7), (29, 36.6), (30, 36.2), (31, 36.8), (32.5, 36.1), (36, 36.2), (36, 46.5)]
OTHERS = [
    [(12.2, 42), (13.5, 42.4), (14.5, 42), (16, 41.8), (16.0, 41.0), (18.5, 40.2), (17.2, 40.4), (16.6, 39.7), (17.1, 39), (16.6, 38.4), (16, 37.9),
     (15.7, 38.1), (15.8, 39.3), (15.4, 40), (14.5, 40.6), (13.5, 41.2), (12.5, 41.8)],
    [(12.4, 38), (15.6, 38.3), (15.1, 36.7), (14.3, 37), (12.6, 37.6)],
    [(23.5, 35.3), (26.3, 35.3), (26.2, 35.0), (24, 35.0)],
    [(8, 29), (8, 33), (11, 33.2), (15, 32.4), (19, 30.6), (20.5, 32.2), (23, 32.7), (25, 31.8), (29, 30.9), (32, 31.2), (36, 31.3), (36, 29)],
    [(23.5, 38.5), (24.0, 38.0), (24.6, 38.0), (24.6, 38.3), (23.9, 39.0), (23.2, 39.2)],
    [(32.3, 35.1), (34.6, 35.6), (33.0, 34.6)],
    [(26.3, 39.4), (26.6, 39.2), (26.3, 39.0)],
]
ISL = [(25.2, 37.1, 7), (24.9, 37.5, 5), (25.4, 36.4, 6), (25.5, 37.0, 6), (24.5, 37.4, 5), (26.0, 37.7, 6), (28.0, 36.2, 8),
       (19.7, 39.6, 6), (20.6, 38.2, 7), (26.0, 38.4, 6), (26.8, 37.7, 6)]


def build6():
    if 'map' in _A:
        return
    k = 2
    sea = vgrad(MW, MH, [(0, (22, 80, 118)), (1, (14, 56, 96))]).convert('RGB')
    a = np.asarray(sea, np.float32) * (0.9 + 0.2 * fnoise(MW, MH, 80, 6, 4))[..., None]
    sea = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    mask = SS(MW, MH, 2)
    for poly in [LAND_POLY] + OTHERS:
        mask.poly([mp(*p) for p in poly], (255, 255, 255, 255))
    for lon, lat, r in ISL:
        x, y = mp(lon, lat)
        mask.ell(x, y, r * 1.2, r * 0.9, (255, 255, 255, 255))
    lm = mask.get().getchannel('A')
    # shallows
    sh = blur(lm, 14).point(lambda v: min(255, int(v * 1.6)))
    sea.paste(Image.new('RGB', (MW, MH), (60, 140, 160)), (0, 0), sh.point(lambda v: int(v * 0.55)))
    # land
    land = vgrad(MW, MH, [(0, (170, 150, 98)), (0.5, (196, 172, 112)), (1, (150, 128, 84))])
    la = np.asarray(land, np.float32) * (0.82 + 0.3 * fnoise(MW, MH, 50, 8, 5))[..., None]
    land = Image.fromarray(np.clip(la, 0, 255).astype(np.uint8))
    edge = ImageChops.subtract(lm, lm.filter(ImageFilter.MinFilter(9)))
    sea.paste(Image.new('RGB', (MW, MH), (244, 232, 190)), (0, 0), blur(edge, 1.2).point(lambda v: min(255, v * 2)))
    sea.paste(land, (0, 0), lm)
    d = ImageDraw.Draw(sea, 'RGBA')
    for lon in range(8, 37, 2):
        x, _ = mp(lon, 40)
        d.line([(x, 0), (x, MH)], fill=(220, 236, 244, 36), width=2)
    for lat in range(30, 47, 2):
        _, y = mp(10, lat)
        d.line([(0, y), (MW, y)], fill=(220, 236, 244, 36), width=2)
    # mountains hint
    rr = random.Random(2)
    for i in range(160):
        lon, lat = rr.uniform(19.5, 24), rr.uniform(37.5, 41.5)
        x, y = mp(lon, lat)
        if lm.getpixel((int(x), int(y))) > 200:
            d.polygon([(x - 9, y + 6), (x, y - 10), (x + 9, y + 6)], fill=(120, 96, 64, 190))
            d.polygon([(x, y - 10), (x + 9, y + 6), (x + 2, y + 6)], fill=(90, 70, 46, 190))
    ft = font('cinzel', 26, 600)
    for txt, lon, lat, sz, col in [('GREECE', 21.6, 39.9, 34, (84, 56, 28)), ('AEGEAN SEA', 25.0, 38.8, 26, (190, 224, 236)),
                                   ('IONIAN SEA', 17.4, 37.9, 26, (190, 224, 236)), ('MEDITERRANEAN SEA', 15.5, 34.3, 36, (190, 224, 236)),
                                   ('PELOPONNESE', 21.2, 37.55, 14, (84, 56, 28)), ('ITALY', 14.8, 41.0, 24, (84, 56, 28)),
                                   ('ANATOLIA', 31.0, 38.5, 30, (84, 56, 28)), ('CRETE', 24.8, 34.6, 18, (190, 224, 236))]:
        ti = text_img(txt, font('cinzel', sz, 600), col + (230,), 5)
        x, y = mp(lon, lat)
        sea.paste(ti, (int(x - ti.width / 2), int(y - ti.height / 2)), ti)
    _A['map'] = sea
    _A['pin'] = mp(22.15, 38.22)


def scene6(t):
    build6()
    mapi = _A['map']
    px, py = _A['pin']
    p = ease(prog(t, 0.5, 4.5))
    # scale from full map to close on Greece (log-interp)
    sc0, sc1 = W / MW, 1.45
    sc = math.exp(math.log(sc0) + (math.log(sc1) - math.log(sc0)) * p)
    cx0, cy0 = MW / 2, MH / 2
    cx = cx0 + (px - cx0) * p + 40 * p
    cy = cy0 + (py - cy0) * p
    bw, bh = W / sc, H / sc
    bx = clamp(cx - bw / 2, 0, MW - bw)
    by = clamp(cy - bh / 2, 0, MH - bh)
    if bh > MH:
        by = 0
        bh = MH
    img = mapi.resize((W, H), Image.BILINEAR, box=(bx, by, bx + bw, by + bh)) if bh <= MH else mapi.resize((W, H))
    sx = (px - bx) / bw * W
    sy = (py - by) / bh * H
    d = ImageDraw.Draw(img, 'RGBA')
    # time-travel vortex at the start
    v = 1 - ease(prog(t, 0.2, 1.8))
    if v > 0.01:
        ov = Image.new('RGBA', (W, H), (10, 8, 24, int(255 * v)))
        od = ImageDraw.Draw(ov)
        for i in range(14):
            r = 80 + i * 60 + (t * 120) % 60
            ang = t * (0.8 + i * 0.07) * (1 if i % 2 else -1)
            col = (255, 214, 130, int(200 * v * (1 - i / 16)))
            od.ellipse((W / 2 - r, H / 2 - r, W / 2 + r, H / 2 + r), outline=col, width=3)
            for k in range(12):
                a = ang + k * math.pi / 6
                od.line([(W / 2 + math.cos(a) * (r - 14), H / 2 + math.sin(a) * (r - 14)),
                         (W / 2 + math.cos(a) * r, H / 2 + math.sin(a) * r)], fill=col, width=3)
        for hand, (L, sp_) in enumerate([(220, 6.0), (150, 0.5)]):
            a = -math.pi / 2 - t * sp_
            od.line([(W / 2, H / 2), (W / 2 + math.cos(a) * L, H / 2 + math.sin(a) * L)], fill=(255, 236, 190, int(255 * v)), width=8)
        img.paste(ov, (0, 0), ov)
    # pin
    if t > 3.7:
        q = prog(t, 3.7, 4.4)
        drop = (1 - eo(q)) * -260
        bounce = abs(math.sin(prog(t, 4.2, 5.0) * math.pi * 2)) * 10 * (1 - prog(t, 4.2, 5.0)) if t > 4.2 else 0
        yy = sy + drop - bounce
        if t > 4.3:
            for k in range(3):
                r = ((t - 4.3) * 60 + k * 30) % 90
                a = int(200 * (1 - r / 90))
                d.ellipse((sx - r * 1.4, sy - r * 0.5, sx + r * 1.4, sy + r * 0.5), outline=(255, 235, 180, a), width=3)
        d.ellipse((sx - 12, sy - 4, sx + 12, sy + 4), fill=(0, 0, 0, 90))
        d.ellipse((sx - 24, yy - 74, sx + 24, yy - 26), fill=(204, 36, 40, 255))
        d.polygon([(sx - 22, yy - 40), (sx + 22, yy - 40), (sx, yy)], fill=(204, 36, 40, 255))
        d.ellipse((sx - 9, yy - 58, sx + 9, yy - 40), fill=(250, 220, 210, 255))
        d.arc((sx - 18, yy - 68, sx + 18, yy - 32), 200, 260, fill=(255, 150, 140, 255), width=3)
        if t > 4.6:
            ft = text_img('HELIKE', font('cinzel', 26, 800), (255, 246, 220, 255), 4)
            a = ease(prog(t, 4.6, 5.3))
            lay = Image.new('RGBA', (ft.width + 8, ft.height + 8), (0, 0, 0, 0))
            lay.paste(ft, (4, 4), ft)
            sh_ = blur(Image.merge('RGBA', (Image.new('L', lay.size, 0),) * 3 + (lay.getchannel('A'),)), 3)
            img.paste(fade_img(sh_, a), (int(sx + 34), int(sy - 54)), fade_img(sh_, a))
            img.paste(fade_img(lay, a), (int(sx + 32), int(sy - 56)), fade_img(lay, a))
    # 373 BC sign
    if t > 4.6:
        a = eo(prog(t, 4.6, 5.4))
        yr = 2025 - (2025 + 373) * ease(prog(t, 4.9, 6.5))
        txt = (str(int(yr)) + ' AD') if yr > 0 else (str(int(abs(yr))) + ' BC')
        if t >= 6.5:
            txt = '373 BC'
        sign = Image.new('RGBA', (440, 210), (0, 0, 0, 0))
        sd = ImageDraw.Draw(sign)
        sd.polygon([(8, 20), (60, 6), (140, 18), (230, 4), (320, 16), (430, 8), (436, 100), (426, 196), (330, 204), (230, 192), (120, 204), (20, 196), (4, 110)],
                   fill=(236, 212, 164, 255), outline=(110, 74, 40, 255))
        n_ = fnoise(440, 210, 20, 4, 3)
        sg = np.asarray(sign, np.float32)
        sg[..., :3] *= (0.85 + 0.25 * n_)[..., None]
        sign = Image.fromarray(np.clip(sg, 0, 255).astype(np.uint8), 'RGBA')
        tt = text_img(txt, font('cinzel', 96, 800), (84, 40, 22, 255))
        sign.paste(tt, ((440 - tt.width) // 2, (210 - tt.height) // 2 + 4), tt)
        stamp = 1.0
        if t > 6.5:
            stamp = 1.0 + 0.16 * max(0, 1 - (t - 6.5) * 4)
        sg2 = sign.resize((int(440 * stamp), int(210 * stamp)), Image.BICUBIC)
        pos = (int(W - 500 + (1 - a) * 700 - (sg2.width - 440) / 2), int(430 - (sg2.height - 210) / 2))
        shadow = blur(Image.merge('RGBA', (Image.new('L', sg2.size, 0),) * 3 + (sg2.getchannel('A').point(lambda v: int(v * 0.5)),)), 8)
        img.paste(shadow, (pos[0] + 8, pos[1] + 12), shadow)
        img.paste(sg2, pos, sg2)
        if 6.5 < t < 7.2:
            img = glow_at(img, pos[0] + sg2.width / 2, pos[1] + sg2.height / 2, 300, (255, 220, 150), 0.5 * (1 - (t - 6.5) / 0.7), 1.5)
    # shake on stamp
    if 6.5 < t < 6.9:
        k = (1 - (t - 6.5) / 0.4) * 6
        img = img.transform((W, H), Image.AFFINE, (1, 0, math.sin(t * 90) * k, 0, 1, math.cos(t * 77) * k), Image.BILINEAR)
    return img
