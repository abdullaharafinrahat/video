from lib import *
from art import *
from people import *

_A = {}


# ---------------------------------------------------------------- scene 2
def helmet(S, x, y, s):
    br = (176, 124, 60)
    # crest
    S.poly([(x - 60 * s, y - 70 * s), (x - 40 * s, y - 120 * s), (x + 20 * s, y - 138 * s), (x + 64 * s, y - 112 * s),
            (x + 54 * s, y - 80 * s), (x + 10 * s, y - 100 * s), (x - 30 * s, y - 84 * s)], (176, 36, 36))
    for i in range(12):
        a = -50 + i * 10
        S.line([(x + a * s, y - 86 * s), (x + (a + 6) * s, y - (118 - abs(a) * 0.3 + (i % 2) * 6) * s)], (120, 20, 24), 2 * s, False)
    # dome
    S.gpoly([(x - 56 * s, y - 20 * s), (x - 60 * s, y - 62 * s), (x - 34 * s, y - 90 * s), (x + 34 * s, y - 90 * s),
             (x + 60 * s, y - 62 * s), (x + 56 * s, y - 20 * s)], (232, 188, 104), (130, 84, 36), True, mid=(190, 140, 72))
    # face opening + cheek guards
    S.poly([(x - 42 * s, y - 50 * s), (x - 20 * s, y - 56 * s), (x - 8 * s, y - 14 * s), (x - 18 * s, y + 8 * s),
            (x - 44 * s, y + 4 * s)], (40, 30, 26))
    S.poly([(x + 42 * s, y - 50 * s), (x + 20 * s, y - 56 * s), (x + 8 * s, y - 14 * s), (x + 18 * s, y + 8 * s),
            (x + 44 * s, y + 4 * s)], (40, 30, 26))
    S.poly([(x - 8 * s, y - 56 * s), (x + 8 * s, y - 56 * s), (x + 6 * s, y - 4 * s), (x - 6 * s, y - 4 * s)], br)
    S.poly([(x - 56 * s, y - 20 * s), (x - 44 * s, y + 4 * s), (x - 18 * s, y + 8 * s), (x - 28 * s, y - 22 * s)], shade(br, 0.9))
    S.poly([(x + 56 * s, y - 20 * s), (x + 44 * s, y + 4 * s), (x + 18 * s, y + 8 * s), (x + 28 * s, y - 22 * s)], shade(br, 0.8))
    S.line([(x - 50 * s, y - 72 * s), (x - 20 * s, y - 86 * s)], (255, 236, 170), 2.5 * s, False)
    S.line([(x - 56 * s, y - 20 * s), (x + 56 * s, y - 20 * s)], (90, 56, 24), 1.5 * s, False)


def build2():
    if 'p2' in _A:
        return
    rng = random.Random(4)
    # ---- left: abandoned house
    S = SS(W, H, 2)
    S.im.paste(vgrad(W * 2, H * 2, [(0, (146, 188, 222)), (0.55, (228, 224, 206)), (1, (176, 170, 120))]), (0, 0))
    S.poly([(0, 470)] + [(x, 450 + 30 * math.sin(x / 90)) for x in range(0, 700, 20)] + [(700, H), (0, H)], (150, 160, 130))
    S.gpoly([(0, 560), (700, 540), (700, H), (0, H)], (120, 136, 84), (70, 92, 56))
    bx, by = 130, 610
    # walls
    S.poly([(bx, by), (bx, 330), (bx + 40, 300), (bx + 90, 336), (bx + 150, 312), (bx + 210, 360), (bx + 260, 346), (bx + 300, 380),
            (bx + 300, by)], (200, 186, 152))
    S.grect(bx, 340, bx + 300, by, (212, 196, 158), (150, 132, 100))
    for r in range(8):
        yy = 340 + r * 34
        S.line([(bx, yy), (bx + 300, yy)], (130, 112, 84), 1.2, False)
        for c in range(7):
            xx = bx + (c + (r % 2) * 0.5) * 46
            S.line([(xx, yy), (xx, yy + 34)], (130, 112, 84), 1.0, False)
    S.rect(bx + 30, 410, bx + 90, 490, (38, 30, 28))
    S.rect(bx + 22, 402, bx + 98, 412, (150, 134, 104))
    S.poly([(bx + 190, by), (bx + 190, 480), (bx + 205, 450), (bx + 245, 450), (bx + 260, 480), (bx + 260, by)], (30, 24, 24))
    # broken roof beams + tiles
    S.line([(bx - 20, 340), (bx + 120, 250), (bx + 190, 296)], (86, 60, 40), 10)
    S.line([(bx + 90, 270), (bx + 230, 330)], (86, 60, 40), 8)
    for i in range(10):
        tx, ty = bx + rng.uniform(-30, 330), rng.uniform(580, 640)
        S.poly([(tx, ty), (tx + 30, ty - 4), (tx + 24, ty + 14), (tx - 4, ty + 12)], rng.choice(ROOFS))
    for i in range(110):  # grass
        gx = rng.uniform(0, 640)
        gy = rng.uniform(560, 720)
        S.line([(gx, gy), (gx + rng.uniform(-8, 8), gy - rng.uniform(14, 40))], shade((100, 140, 70), rng.uniform(0.7, 1.2)), 2.4)
    olive(S, 560, 600, 130, rng)
    # ivy blobs
    for i in range(34):
        x = bx + rng.uniform(-10, 310)
        y = rng.uniform(330, 600)
        S.ell(x, y, rng.uniform(7, 16), rng.uniform(5, 12), shade((72, 128, 56), rng.uniform(0.7, 1.3)))
    _A['L'] = S.get().convert('RGB')
    # ---- middle: aftermath of battle
    S = SS(W, H, 2)
    S.im.paste(vgrad(W * 2, H * 2, [(0, (52, 38, 54)), (0.35, (150, 80, 62)), (0.6, (232, 150, 80)), (1, (176, 120, 70))]), (0, 0))
    S.poly([(0, 470)] + [(x, 450 + 20 * math.sin(x / 120)) for x in range(0, W, 20)] + [(W, H), (0, H)], (72, 52, 50))
    S.gpoly([(0, 520), (W, 520), (W, H), (0, H)], (120, 84, 56), (60, 44, 36))
    for i in range(9):  # spears
        x = 440 + rng.uniform(0, 420)
        y = rng.uniform(540, 640)
        a = rng.uniform(-0.35, 0.35)
        S.line([(x, y), (x + math.sin(a) * 260, y - math.cos(a) * 260)], (70, 46, 34), 4)
        S.poly([(x + math.sin(a) * 260, y - math.cos(a) * 260), (x + math.sin(a) * 292 + 7, y - math.cos(a) * 292 + 4),
                (x + math.sin(a) * 292 - 7, y - math.cos(a) * 292 - 4)] if False else
               [(x + math.sin(a) * 255 - 6, y - math.cos(a) * 255), (x + math.sin(a) * 300, y - math.cos(a) * 300),
                (x + math.sin(a) * 255 + 6, y - math.cos(a) * 255)], (210, 200, 190))
    for (sx, sy, r) in [(520, 640, 52), (800, 620, 44)]:  # shields
        S.ell(sx, sy, r, r * 0.35, (150, 100, 50), (60, 36, 24), 3)
        S.ell(sx, sy, r * 0.5, r * 0.18, (190, 150, 90))
    for i in range(30):  # rubble
        x, y = rng.uniform(420, 880), rng.uniform(590, 710)
        S.ell(x, y, rng.uniform(6, 20), rng.uniform(3, 9), rng.choice([(90, 70, 60), (120, 96, 74), (60, 48, 44)]))
    # distant burning silhouettes
    for i in range(6):
        x = 430 + i * 80
        S.rect(x, 440, x + 40, 470, (46, 30, 36))
        S.poly([(x - 4, 440), (x + 20, 410), (x + 44, 440)], (46, 30, 36))
    helmet(S, 640, 640, 1.25)
    _A['M'] = S.get().convert('RGB')
    # ---- right: nothing left
    S = SS(W, H, 2)
    S.im.paste(vgrad(W * 2, H * 2, [(0, (180, 160, 138)), (0.5, (236, 214, 176)), (1, (214, 184, 140))]), (0, 0))
    S.gpoly([(0, 470), (W, 480), (W, H), (0, H)], (222, 196, 150), (186, 154, 108))
    for i in range(60):
        S.ell(rng.uniform(800, 1300), rng.uniform(490, 710), rng.uniform(30, 110), rng.uniform(3, 9), (206, 176, 130))
    _A['R'] = S.get().convert('RGB')
    rs = SS(W, H, 2)  # ghost foundations
    for (x, y, w, h) in [(930, 520, 120, 50), (1090, 540, 90, 40), (1000, 600, 150, 54), (880, 640, 70, 36)]:
        rs.rect(x, y, x + w, y + h, None, (120, 90, 60, 255), 3)
        rs.line([(x + w / 2, y), (x + w / 2, y + h)], (120, 90, 60, 255), 2, False)
    _A['Rghost'] = rs.get()
    _A['p2'] = 1


PANELS = [[(0, 0), (470, 0), (400, H), (0, H)], [(486, 0), (880, 0), (810, H), (416, H)], [(896, 0), (W, 0), (W, H), (826, H)]]


def red_x(img, cx, cy, size, p):
    d = ImageDraw.Draw(img, 'RGBA')
    for (k, (a, b)) in enumerate([((-1, -1), (1, 1)), ((1, -1), (-1, 1))]):
        q = clamp(p * 2 - k)
        if q <= 0:
            continue
        x0, y0 = cx + a[0] * size, cy + a[1] * size
        x1, y1 = cx + a[0] * size + (b[0] - a[0]) * size * q, cy + a[1] * size + (b[1] - a[1]) * size * q
        d.line([(x0 + 4, y0 + 6), (x1 + 4, y1 + 6)], fill=(0, 0, 0, 110), width=26)
        d.line([(x0, y0), (x1, y1)], fill=(196, 34, 34, 255), width=20)
        d.line([(x0, y0 - 5), (x1, y1 - 5)], fill=(236, 80, 70, 255), width=6)
        d.ellipse((x1 - 10, y1 - 10, x1 + 10, y1 + 10), fill=(196, 34, 34, 255))
    return img


def scene2(t):
    build2()
    base = Image.new('RGB', (W, H), (16, 14, 20))
    dim = ease(prog(t, 4.3, 5.0))
    shk = 0
    for i, (poly, key, t0) in enumerate(zip(PANELS, ['L', 'M', 'R'], [0.05, 1.45, 3.75])):
        e = eo(prog(t, t0, t0 + 0.7))
        if e <= 0:
            continue
        pan = _A[key].copy()
        d = ImageDraw.Draw(pan, 'RGBA')
        if key == 'L':
            for k in range(7):
                x0 = 150 + k * 48
                pts = [(x0 + math.sin(t * 1.6 + k + j * 0.7) * (4 + j * 1.6), 330 + j * 24) for j in range(9 + (k % 3) * 2)]
                d.line(pts, fill=(60, 112, 48, 255), width=4)
                for j, p_ in enumerate(pts[2::2]):
                    d.ellipse((p_[0] - 7, p_[1] - 4, p_[0] + 7, p_[1] + 4), fill=(86, 146, 60, 255))
            for k in range(30):
                px = (k * 97 + t * 14) % 700
                py = (k * 53 + t * 6 * (1 + k % 3)) % 500 + 100
                d.ellipse((px - 1.5, py - 1.5, px + 1.5, py + 1.5), fill=(255, 250, 220, 120))
        elif key == 'M':
            for k in range(34):
                age = (t * 0.28 + k / 34.0) % 1
                x0 = 600 + math.sin(age * 5 + k) * 36 * age + age * 70
                y0 = 470 - age * 430
                r = 16 + age * 64
                a = int(190 * (1 - age) ** 1.2)
                c = int(50 + 60 * age)
                d.ellipse((x0 - r, y0 - r, x0 + r, y0 + r), fill=(c, c - 8, c - 14, a))
            for k in range(26):
                age = (t * 0.5 + k * 0.137) % 1
                ex = 520 + (k * 53) % 300 + math.sin(age * 8 + k) * 16
                ey = 600 - age * 380
                d.ellipse((ex - 2, ey - 2, ex + 2, ey + 2), fill=(255, 190 - int(age * 80), 70, int(255 * (1 - age))))
            d.ellipse((560, 585, 720, 615), fill=(255, 150, 60, 28))
        else:
            gh = _A['Rghost'].copy()
            ga = gh.getchannel('A').point(lambda v: int(v * (0.9 * (1 - ease(prog(t, 4.5, 5.55))))))
            gh.putalpha(ga)
            pan.paste(gh, (0, 0), gh)
            for k in range(70):
                px = (k * 131 + t * (160 + k % 5 * 60)) % (W + 200) - 100
                py = 440 + (k * 47) % 280
                L = 30 + (k % 4) * 24
                d.line([(px, py), (px + L, py - L * 0.08)], fill=(255, 240, 210, 70), width=2)
            dust = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            dd = ImageDraw.Draw(dust)
            for k in range(8):
                cx = (k * 260 + t * 70) % (W + 500) - 250
                dd.ellipse((cx - 160, 440 + (k % 3) * 80 - 60, cx + 160, 440 + (k % 3) * 80 + 60), fill=(236, 214, 176, 120))
            dust = blur(dust, 30)
            pan.paste(dust, (0, 0), dust)
        # status marks
        xs = {'L': (200, 330, 1.4, 2.1), 'M': (640, 360, 3.3, 3.95)}
        if key in xs and t > xs[key][2]:
            red_x(pan, xs[key][0], xs[key][1], 70, prog(t, xs[key][2], xs[key][3]))
        if key != 'R':
            pan = Image.blend(pan, Image.new('RGB', pan.size, (20, 20, 30)), 0.55 * dim)
            pan = Image.blend(pan.convert('L').convert('RGB'), pan, 1 - 0.7 * dim)
        m = Image.new('L', (W, H), 0)
        ImageDraw.Draw(m).polygon(poly, fill=255)
        off = int((1 - e) * -H)
        pan2 = Image.new('RGB', (W, H), (0, 0, 0))
        pan2.paste(pan, (0, off))
        m2 = Image.new('L', (W, H), 0)
        m2.paste(m, (0, off))
        base.paste(pan2, (0, 0), m2)
    d = ImageDraw.Draw(base)
    for (x0, y0, x1, y1) in [(470, 0, 400, H), (486, 0, 416, H), (880, 0, 810, H), (896, 0, 826, H)]:
        pass
    for (xa, xb) in [(470, 400), (880, 810)]:
        if t > (0.8 if xa == 470 else 4.0):
            d.line([(xa + 8, 0), (xb + 8, H)], fill=(250, 240, 220), width=8)
            d.line([(xa + 8, 0), (xb + 8, H)], fill=(60, 44, 36), width=2)
    # VANISHED word
    if t > 4.35:
        a = ease(prog(t, 4.35, 5.0))
        tt = text_img('VANISHED', font('cinzel', 84, 800), (255, 246, 226, 255), 10)
        gl = blur(Image.new('RGBA', (tt.width + 120, tt.height + 120), (0, 0, 0, 0)), 1)
        lay = Image.new('RGBA', (tt.width + 120, tt.height + 120), (0, 0, 0, 0))
        lay.paste(tt, (60, 60), tt)
        glow = blur(lay, 16)
        sc = 1.12 - 0.12 * a
        lay2 = lay.resize((int(lay.width * sc), int(lay.height * sc)), Image.BICUBIC)
        glow2 = glow.resize(lay2.size)
        pos = ((W - lay2.width) // 2 + 60, 250 - (lay2.height - lay.height) // 2)
        g_rgb = Image.new('RGB', glow2.size, (255, 200, 120))
        gm = glow2.getchannel('A').point(lambda v: int(min(255, v * 1.6 * a)))
        reg = base.crop((pos[0], pos[1], pos[0] + glow2.width, pos[1] + glow2.height))
        gb = Image.new('RGB', glow2.size, (0, 0, 0))
        gb.paste(g_rgb, (0, 0), gm)
        base.paste(ImageChops.screen(reg, gb), pos)
        base.paste(fade_img(lay2, a), pos, fade_img(lay2, a))
    # camera shake / handheld
    ox, oy = math.sin(t * 2.2) * 2, math.cos(t * 1.7) * 2
    base = base.transform((W, H), Image.AFFINE, (1, 0, ox, 0, 1, oy), Image.BILINEAR)
    return base


# ---------------------------------------------------------------- scene 3
F3, VX, VY, CH = 540.0, 640.0, 292.0, 1.55


def prj(lat, y, z):
    return (VX + lat * F3 / z, VY + (CH - y) * F3 / z)


def build3():
    if 'sky3' in _A:
        return
    sky = vgrad(W, H, [(0, (40, 88, 140)), (0.25, (112, 150, 180)), (0.40, (250, 200, 130)), (0.5, (255, 222, 160)),
                       (1, (200, 168, 124))])
    sky = glow_at(sky, VX, VY, 560, (255, 214, 140), 0.8, 1.6)
    S = SS(W, H, 1)
    r = ridge(W, 8, 262, 20, 90, 4)
    S.poly([(0, VY + 8)] + [(x, r[x]) for x in range(0, W, 4)] + [(W, VY + 8)], (196, 160, 150))
    r2 = ridge(W, 3, 280, 10, 60, 4)
    S.poly([(0, VY + 10)] + [(x, r2[x]) for x in range(0, W, 4)] + [(W, VY + 10)], (178, 142, 128))
    sky.paste(S.im, (0, 0), S.im)
    _A['sky3'] = sky
    _A['sp'] = [(random.Random(i).uniform(0, W), random.Random(i + 99).uniform(0, H), random.Random(i + 5).uniform(0.3, 1.2)) for i in range(70)]


def fog(c, z, amt=0.045):
    return mix(c, (246, 208, 150), clamp(z * amt))


def draw_side(Hs, Rs, Cs, sgn, n, z0, z1, ruin, t):
    r = random.Random(n * 7 + (3 if sgn > 0 else 0))
    hh = 1.9 + r.random() * 0.9
    wall = r.choice(WALLS)
    broken = r.random()
    lat = sgn * 1.62
    zm = (z0 + z1) / 2
    # ruins: low wall stubs
    stub = 0.18 + 0.35 * r.random()
    pts = [prj(lat, 0, z0), prj(lat, stub * 0.7, z0)]
    k = 5
    for i in range(1, k):
        zz = z0 + (z1 - z0) * i / k
        pts.append(prj(lat, stub * (0.4 + 0.9 * r.random()), zz))
    pts += [prj(lat, stub * 0.5, z1), prj(lat, 0, z1)]
    Rs.poly(pts, fog(shade(wall, 0.75), zm))
    for i in range(4):  # rubble
        zz = z0 + r.random() * (z1 - z0)
        lt = sgn * (1.1 + 1.2 * r.random())
        px, py = prj(lt, 0.05, zz)
        sz = 0.2 * F3 / zz
        Rs.ell(px, py, sz * 0.8, sz * 0.4, fog(shade(wall, 0.6 + 0.2 * r.random()), zz))
    # intact house
    a, b = prj(lat, 0, z0), prj(lat, hh, z0)
    c, d = prj(lat, hh, z1), prj(lat, 0, z1)
    Hs.gpoly([a, b, c, d], fog(shade(wall, 1.05), z0), fog(shade(wall, 0.82), z1), True)
    # cornice
    e1, e2 = prj(lat, hh, z0), prj(lat, hh + 0.12, z0)
    e3, e4 = prj(lat, hh + 0.12, z1), prj(lat, hh, z1)
    Hs.poly([e1, e2, e3, e4], fog((200, 90, 54), zm))
    # door and windows
    for (zf, w_) in [(0.25, 0.22), (0.62, 0.22)]:
        zz0, zz1 = z0 + (z1 - z0) * zf, z0 + (z1 - z0) * (zf + w_ * 0.9)
        if r.random() < 0.5 and zf < 0.5:
            Hs.poly([prj(lat, 0, zz0), prj(lat, 1.25, zz0), prj(lat, 1.25, zz1), prj(lat, 0, zz1)], fog((60, 40, 32), zm))
        else:
            Hs.poly([prj(lat, 0.9, zz0), prj(lat, 1.5, zz0), prj(lat, 1.5, zz1), prj(lat, 0.9, zz1)], fog((52, 40, 38), zm))
    # columns
    cwid = 0.13
    xl = lat - sgn * 0.38
    top = 1.55
    top2 = top * (1 - ruin * (0.75 if broken > 0.45 else 0.0))
    px0, py0 = prj(xl, 0, z0)
    pxt, pyt = prj(xl, top2, z0)
    w_px = cwid * F3 / z0
    col = fog(STONE, z0)
    if py0 > -50:
        Cs.grect(px0 - w_px / 2, pyt, px0 + w_px / 2, py0, shade(col, 0.82), shade(col, 0.96), True, mid=shade(col, 1.08))
        for i in range(1, 4):
            lx = px0 - w_px / 2 + w_px * i / 4
            Cs.line([(lx, pyt), (lx, py0)], shade(col, 0.76), max(0.6, w_px * 0.04), False)
        if top2 > top - 0.01:
            Cs.rect(px0 - w_px * 0.72, pyt - w_px * 0.28, px0 + w_px * 0.72, pyt, shade(col, 1.02))
            if z0 < 1.3:
                return
            # lintel to next
            nxp, _ = prj(xl, top, z1)
            Cs.rect(min(px0, nxp) - 1, pyt - w_px * 0.7, max(px0, nxp) + 1, pyt - w_px * 0.28, shade(col, 0.98))
        else:
            Cs.poly([(px0 - w_px / 2, pyt), (px0 - w_px * 0.2, pyt - w_px * 0.2), (px0 + w_px * 0.1, pyt + w_px * 0.1),
                     (px0 + w_px / 2, pyt - w_px * 0.1), (px0 + w_px / 2, pyt + 4), (px0 - w_px / 2, pyt + 4)], shade(col, 0.95))
            Cs.ell(px0 + sgn * w_px * 1.6, py0 - w_px * 0.2, w_px * 0.9, w_px * 0.35, shade(col, 0.9))


def scene3(t):
    build3()
    cam = 0.26 * t
    ruin = ease(prog(t, 0.5, 2.8))
    img = _A['sky3'].copy()
    Bs = SS(W, H, 2)
    # ground + road
    Bs.gpoly([(0, VY), (W, VY), (W, H), (0, H)], (226, 186, 132), (150, 120, 88))
    r0, r1 = prj(-1.0, 0, 0.32), prj(-1.0, 0, 30)
    q0, q1 = prj(1.0, 0, 0.32), prj(1.0, 0, 30)
    Bs.gpoly([r1, q1, q0, r0], (236, 196, 140), (166, 134, 100))
    for lt in (-1.0, -0.6, -0.2, 0.2, 0.6, 1.0):
        a, b = prj(lt, 0, 0.32), prj(lt, 0, 40)
        Bs.line([a, b], (120, 92, 66), 1.4, False)
    zl = 0.35
    for m in range(0, 40):
        zz = (m / 2.0) - (cam % 0.5) + 0.35
        if zz < 0.36:
            continue
        a, b = prj(-1.0, 0, zz), prj(1.0, 0, zz)
        Bs.line([a, b], (120, 92, 66), max(0.8, 2.4 / zz), False)
    for sgn in (-1, 1):  # sidewalks
        pa, pb = prj(sgn * 1.0, 0, 0.32), prj(sgn * 1.0, 0, 30)
        pc, pd = prj(sgn * 1.6, 0, 30), prj(sgn * 1.6, 0, 0.32)
        Bs.gpoly([pa, pb, pc, pd], (206, 176, 132), (236, 204, 150))
    Hs = SS(W, H, 2)
    Cs = SS(W, H, 2)
    Rs = Bs
    base_n = int(cam)
    for j in range(16, -1, -1):
        n = base_n + j
        z0 = n - cam + 0.5
        z1 = z0 + 0.94
        if z0 < 0.36:
            continue
        for sgn in (-1, 1):
            draw_side(Hs, Rs, Cs, sgn, n, z0, z1, ruin, t)
    img = img.convert('RGBA')
    img = Image.alpha_composite(img, Bs.get())
    houses = Hs.get()
    houses = fade_img(houses, 1 - ruin)
    img = Image.alpha_composite(img, houses)
    img = img.convert('RGB')
    # ghost people
    ga = 0.85 * (1 - ease(prog(t, 3.3, 4.9)))
    people = [(11, -0.5, 7.0, 0.20, False), (12, 0.45, 5.5, -0.16, True), (13, -0.15, 9.5, 0.12, False), (14, 0.7, 8.0, -0.2, True),
              (15, -0.75, 4.6, 0.1, False), (16, 0.1, 6.5, -0.12, True), (17, 0.3, 11, 0.15, False)]
    if ga > 0.01:
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        for (sd, lt, zs, sp_, fl) in sorted(people, key=lambda p: -(p[2] - p[3] * t)):
            z = max(1.5, zs - sp_ * t * 2.2)
            hpx = 1.72 * F3 / z
            spr = walk_sprite(sd, t, 0.8, 260, flip=fl, female=(sd % 2 == 0))
            sc = hpx / (260 * 1.0)
            s2 = spr.resize((max(2, int(spr.width * sc)), max(2, int(spr.height * sc))), Image.BILINEAR)
            sil = silhouette(s2, (255, 232, 196), ga * clamp(1.2 - z * 0.05))
            px, py = prj(lt, 0, z)
            fl_ = 0.8 + 0.2 * math.sin(t * 9 + sd)
            sil = fade_img(sil, fl_)
            lay.paste(sil, (int(px - sil.width / 2), int(py - sil.height + 6)), sil)
        glw = blur(lay, 6)
        img.paste(glw, (0, 0), glw)
        img.paste(lay, (0, 0), lay)
        # sparkles rising off ghosts as they fade
        if t > 3.3:
            d = ImageDraw.Draw(img, 'RGBA')
            for k in range(60):
                age = (t * 0.6 + k * 0.173) % 1
                px = 300 + (k * 211) % 700 + math.sin(age * 6 + k) * 10
                py = 500 - age * 260 - (k * 37) % 120
                d.ellipse((px - 2, py - 2, px + 2, py + 2), fill=(255, 226, 150, int(220 * (1 - age) * clamp((ga + 0.1) * 2) * ease(prog(t, 3.3, 4.2)))))
    # columns on top
    colimg = Cs.get()
    img.paste(colimg, (0, 0), colimg)
    # light shafts + dust
    img = god_rays(img, VX, VY - 30, t, 0.22, (255, 214, 140), 9, 1200)
    d = ImageDraw.Draw(img, 'RGBA')
    for (x, y, s_) in _A['sp']:
        px = (x + t * 14 * s_) % W
        py = (y - t * 6 * s_) % H
        d.ellipse((px - s_ * 1.8, py - s_ * 1.8, px + s_ * 1.8, py + s_ * 1.8), fill=(255, 238, 190, 110))
    # the question mark
    q0_ = 5.7
    if t > q0_:
        a = ease(prog(t, q0_, q0_ + 1.6))
        sz = int(120 + 200 * a)
        pulse = 0.75 + 0.25 * math.sin(t * 3.2)
        img = glow_at(img, VX, 250 + math.sin(t * 1.4) * 8, int(260 * a + 40), (255, 200, 110), 0.9 * pulse, 1.8)
        qm = text_img('?', font('cinzel', sz, 800), (255, 250, 232, 255))
        lay = Image.new('RGBA', (qm.width + 200, qm.height + 200), (0, 0, 0, 0))
        lay.paste(qm, (100, 100), qm)
        gl = blur(lay, 20)
        gm = gl.getchannel('A').point(lambda v: int(min(255, v * 2.0 * pulse)))
        pos = (int(VX - lay.width / 2), int(250 - lay.height / 2 + math.sin(t * 1.4) * 8))
        gb = Image.new('RGB', lay.size, (0, 0, 0))
        gb.paste(Image.new('RGB', lay.size, (255, 196, 100)), (0, 0), gm)
        reg = img.crop((pos[0], pos[1], pos[0] + lay.width, pos[1] + lay.height))
        img.paste(ImageChops.screen(reg, gb), pos)
        img.paste(fade_img(lay, a), pos, fade_img(lay, a))
    img = tint(img, (30, 20, 60), 0.0)
    return img
