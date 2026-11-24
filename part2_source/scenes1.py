"""Scenes 19-23"""
import math, random
from gfx import *
from art import *


class Scene:
    num = 0
    title = ''
    warm = 0.0

    def __init__(self, start, end):
        self.start, self.end = start, end
        self.dur = end - start
        self.build()

    def build(self):
        self.bg = Image.new('RGB', (W, H))

    def draw(self, t):
        raise NotImplementedError


def map_sheet(g, pts, t, seedv=1):
    g.poly(pts, fill='#e6d3a2', ol='#6a4a28', w=2.5)
    (x0, y0), (x1, y1), (x2, y2), (x3, y3), (x4, y4) = pts
    # coastline & contour lines
    rng = random.Random(seedv)
    cx = [(x0 + x2) / 2 + 20, (y0 + y3) / 2 + 20]
    line1 = [(x0 + 30 + i * 30, y0 + 70 + 18 * math.sin(i * 0.9) + i * 2) for i in range(10)]
    g.line(line1, '#5a8cb0', 2.4)
    for k in range(3):
        g.line([(x + 0, y + 14 * (k + 1)) for x, y in line1], '#9fbccc', 1.4)
    for i in range(7):
        g.line([(x0 + 60 + i * 40, y0 + 120), (x0 + 74 + i * 40, y0 + 160)], '#a98d62', 1.4)
    g.line([(x0 + 70, y0 + 150), (x0 + 130, y0 + 110), (x0 + 210, y0 + 150), (x0 + 270, y0 + 120)], '#b3422c', 2, False)
    g.text(x0 + 285, y0 + 118, '✕', font('DejaVuSans-Bold.ttf', 20), '#b3422c', 'mm')
    g.line([(x0 + 40, y0 + 190), (x0 + 330, y0 + 196)], '#c6ae7e', 1.5)
    # folds
    g.line([(x1 - 10, y1), (x4 + 8, y4)], (190, 160, 110), 1.4)


def total_station(g, x, y, t, s=1.0):
    wood = '#8a5a30'
    for fx in (-70, 0, 62):
        g.line([(x, y), (x + fx * s, y + 215 * s)], OL, 9 * s, True)
        g.line([(x, y), (x + fx * s, y + 215 * s)], wood, 6 * s, True)
    g.rect(x - 24 * s, y - 14 * s, x + 24 * s, y + 6 * s, fill='#555a60', ol=OL, w=2)
    g.rect(x - 22 * s, y - 70 * s, x + 22 * s, y - 14 * s, fill='#e3b422', ol=OL, w=2.4, r=4)
    g.rect(x - 16 * s, y - 100 * s, x + 16 * s, y - 70 * s, fill='#e3b422', ol=OL, w=2.4, r=4)
    a = 0.4 * math.sin(t * 0.9)
    g.ell(x + a * 8 * s, y - 85 * s, 9 * s, fill='#1a2430', ol=OL, w=2)
    g.ell(x + a * 8 * s - 3 * s, y - 88 * s, 3 * s, fill='#9fd0f2')
    g.rect(x - 8 * s, y - 118 * s, x + 8 * s, y - 100 * s, fill='#c49a1c', ol=OL, w=1.8)
    # laser dot sweep
    g.line([(x, y - 85 * s), (x - 520 * s, y - 40 * s + math.sin(t) * 12)], (255, 70, 60), 1.4)
    g.ell(x, y - 85 * s, 3 * s, fill=(255, 80, 60))
    g.text(x, y - 56 * s, 'TOTAL STATION', font('DejaVuSansMono-Bold.ttf', 6 * s), '#6a4e08', 'mm')


class S19(Scene):
    num, title = 19, 'The Helike Project'

    def build(self):
        g = G()
        g.gradrect(0, 0, 1280, 720, [(0, '#2c74c8'), (0.3, '#63a9e2'), (0.47, '#d4ecf7'), (1, '#d4ecf7')])
        g.glow(1010, 120, 200, (255, 232, 170), 0.45)
        mountains(g, 352, ['#93abcc', '#7592b6', '#5a7f9e'], [70, 95, 55], seed=3)
        self.bg = g.im

    def draw(self, t):
        g = G(self.bg)
        clouds(g, t, seed=2, y0=60, y1=210, n=5, speed=7)
        birds(g, t, seed=4, n=4)
        sea(g, 338, 560, t, '#3aa0d8', '#1b69a6', seed=2)
        # sailboat far
        bx = 960 + math.sin(t * 0.4) * 10
        g.poly([(bx - 28, 372), (bx + 30, 372), (bx + 20, 384), (bx - 18, 384)], fill='#f2f2f2', ol=OL, w=1.5)
        g.poly([(bx, 370), (bx, 330), (bx + 22, 368)], fill='#ffffff', ol=OL, w=1.2)
        g.poly([(bx - 2, 370), (bx - 2, 340), (bx - 18, 368)], fill='#f0c0a0', ol=OL, w=1.2)
        # beach foreground
        g.poly([(0, 520), (200, 505), (500, 515), (900, 500), (1300, 520), (1300, 730), (0, 730)], fill='#b79d74')
        g.polyA([(0, 600), (1300, 590), (1300, 730), (0, 730)], (80, 60, 40), 0.25)
        rng = random.Random(8)
        for i in range(60):
            px, py = rng.uniform(0, 1280), rng.uniform(530, 720)
            g.ell(px, py, rng.uniform(3, 9), rng.uniform(2, 5), fill=shade('#a38a62', rng.uniform(0.8, 1.2)))
        # background workers
        figure(g, 120, 520, 0.8, t, hat='brim', hatc='#d9c27a', shirt='#6c8aa8', pants='#60667a', anim='idle', ph=1, face=1)
        figure(g, 200, 530, 0.85, t, hat='brim', hatc='#d9c27a', shirt='#8d9a74', pants='#515a68', anim='point', ph=2, face=1)
        g.line([(228, 535), (238, 410)], '#d33', 4, True)
        for i in range(5):
            g.line([(228 + i * 2.4, 535 - i * 25), (233 + i * 2.4, 535 - i * 25 - 12)], '#fff', 3)
        total_station(g, 1070, 432, t, 1.0)
        # --- main characters
        dz = math.sin(t * 1.3) * 3
        bust(g, 330, 305, 1.05, 'dora', t, turn=0.45, talk=0.0, look=(0.4 + 0.5 * seg(t, 5, 6), 0.7 - 0.6 * seg(t, 5, 6)), nod=dz,
             brow=0.2, shirt='#aaa188')
        # steven + pointing arm
        sx, sy, ss = 660, 322, 1.1
        bust(g, sx, sy, ss, 'steven', t, turn=-0.55 + 0.9 * ease(seg(t, 2.6, 3.4)), talk=talk_amt(t, 3.5 < t < 7.5), look=(-0.3, 0.7 - 1.3 * ease(seg(t, 2.6, 3.4))),
             nod=-dz, shirt='#b0a78d')
        # map held between
        sway = math.sin(t * 1.1) * 2
        pts = [(268, 570 + sway), (560, 528 - sway), (760, 585), (722, 730), (240, 730)]
        map_sheet(g, pts, t)
        for hx_, hy_ in ((300, 600), (700, 600)):
            g.ell(hx_, hy_ + sway, 17, 13, fill=SK['dora'] if hx_ < 500 else SK['steven'], ol=OL, w=2)
        # pointing arm
        up = ease(seg(t, 2.6, 3.6)) * (1 - ease(seg(t, 8.5, 9.5)))
        sh = (sx + 150 * ss, sy + 200 * ss)
        hand = (lerp(sh[0] + 20, 930, up), lerp(sh[1] + 150, 372 + math.sin(t * 3) * 4, up))
        elbow = (lerp(sh[0] + 40, 830, up), lerp(sh[1] + 90, 480, up))
        if up > 0.01:
            limb(g, sh, elbow, 36, '#b0a78d')
            limb(g, elbow, hand, 28, '#b0a78d')
            g.ell(hand[0], hand[1], 16, 13, fill=SK['steven'], ol=OL, w=2)
            g.line([(hand[0], hand[1]), (hand[0] + 24, hand[1] - 3)], SK['steven'], 7, True)
        # title text
        a = ease(seg(t, 0.6, 1.8)) * (1 - ease(seg(t, 8.8, 10.5)))
        if a > 0:
            f = font('Cinzel.ttf', 112)
            g.text(644, 112, '1988', f, (40, 24, 12), 'mm')
            g.text(640, 108, '1988', f, (255, 232, 170), 'mm')
            g.glow(640, 108, 190, (255, 190, 90), 0.25 * a)
        # dust motes / light
        dust(g, t, 3, 26, 0, 120, 1280, 500, (255, 250, 220), speed=8, size=1.8)
        zoom = 1.0 + 0.1 * ease(t / self.dur)
        return g.im, (640 + 20 * t / self.dur * 10, 380, zoom)


class S20(Scene):
    num, title = 20, 'Searching the Seabed'

    def build(self):
        g = G()
        g.gradrect(0, 0, 1280, 175, [(0, '#5ea9e0'), (1, '#cfe9f5')])
        g.gradrect(0, 160, 1280, 720, [(0, '#1f93c6'), (0.35, '#136fa8'), (1, '#04203f')])
        # seabed
        pts = [(0, 650)]
        rng = random.Random(4)
        for x in range(0, 1320, 40):
            pts.append((x, 618 + 22 * math.sin(x * 0.011) + rng.uniform(-8, 8)))
        pts += [(1320, 740), (0, 740)]
        g.poly(pts, fill='#6b5a46')
        g.polyA(pts, '#0a2a44', 0.28)
        for i in range(40):
            x = rng.uniform(0, 1280)
            y = 625 + 22 * math.sin(x * 0.011) + rng.uniform(8, 80)
            g.ell(x, y, rng.uniform(5, 26), rng.uniform(3, 10), fill=shade('#7b6a55', rng.uniform(0.7, 1.1)), ol=(30, 24, 20), w=1)
        for i in range(24):
            x = rng.uniform(20, 1260)
            y = 622 + 22 * math.sin(x * 0.011)
            self_h = rng.uniform(26, 60)
            g.line([(x, y + 6), (x + rng.uniform(-8, 8), y - self_h)], '#2f8c5a', 3, True)
        self.bg = g.im
        self.seabed = lambda x: 618 + 22 * math.sin(x * 0.011)

    def draw(self, t):
        g = G(self.bg)
        # light rays
        for i in range(7):
            x = 100 + i * 190 + math.sin(t * 0.5 + i) * 30
            g.polyA([(x, 165), (x + 50, 165), (x + 210, 620), (x + 90, 620)], (200, 240, 255), 0.07)
        # surface waves
        pts = [(x, 168 + math.sin(x * 0.03 + t * 2.2) * 3.5) for x in range(-20, 1300, 20)]
        g.line(pts, (230, 248, 255), 3)
        # fish
        rng = random.Random(11)
        for i in range(26):
            fx = (rng.uniform(0, 1400) + t * rng.uniform(30, 50) * (1 if i % 2 else -1)) % 1400 - 60
            fy = 260 + rng.uniform(0, 260) + math.sin(t * 1.5 + i) * 8
            d = 1 if i % 2 else -1
            c = '#f6b04a' if i % 3 else '#c8e4f4'
            g.ell(fx, fy, 9, 4.2, fill=c)
            g.poly([(fx - d * 8, fy), (fx - d * 15, fy - 4 + math.sin(t * 10 + i) * 2), (fx - d * 15, fy + 4)], fill=c)
        # towfish & cable
        sway = math.sin(t * 0.9) * 10
        shipx = 330 + 18 * t
        shipy = 150 + math.sin(t * 1.6) * 3
        tx, ty = shipx + 330 + sway, 440 + math.sin(t * 1.2) * 6
        # sonar fan
        sea_y = lambda x: self.seabed(x)
        gx0, gx1 = tx - 230, tx + 230
        g.polyA([(tx, ty + 12), (gx0, sea_y(gx0) + 4), (gx1, sea_y(gx1) + 4)], (130, 255, 220), 0.17)
        for k in range(4):
            ph = (t * 0.9 + k * 0.25) % 1.0
            rr = 60 + ph * 220
            pts = []
            for a in range(-62, 63, 6):
                ang = math.radians(90 + a)
                pts.append((tx + math.cos(ang) * rr, ty + math.sin(ang) * rr))
            g.line(pts, (170, 255, 230), 2.2)
        for sgn in (-1, 1):
            g.line([(tx, ty + 12), (tx + sgn * 230, sea_y(tx + sgn * 230) + 4)], (190, 255, 235), 1.6)
        # scan line on seabed
        pts = [(x, self.seabed(x) - 4) for x in range(int(tx - 230), int(tx + 230), 10)]
        g.line(pts, (255, 255, 160), 3)
        # cable
        g.line([(shipx + 175, shipy - 20), (shipx + 215, shipy + 20), (tx - 20, ty - 20)], (30, 30, 36), 2.4)
        g.ell(tx - 22, ty - 24, 5, fill=(30, 30, 36))
        # towfish body
        g.poly([(tx - 34, ty - 8), (tx + 28, ty - 12), (tx + 36, ty), (tx + 28, ty + 12), (tx - 34, ty + 8)], fill='#e3a31c', ol=OL, w=2.4)
        g.poly([(tx - 34, ty - 8), (tx - 52, ty - 20), (tx - 46, ty), (tx - 52, ty + 20), (tx - 34, ty + 8)], fill='#c08210', ol=OL, w=2)
        g.ell(tx + 16, ty, 5, fill='#222')
        g.glow(tx, ty + 14, 40, (120, 255, 200), 0.35 + 0.2 * math.sin(t * 8))
        # ship (above waterline)
        x, y = shipx, shipy
        g.poly([(x - 170, y - 8), (x + 190, y - 14), (x + 150, y + 26), (x - 130, y + 26)], fill='#27394f', ol=OL, w=3)
        g.poly([(x - 170, y - 8), (x + 190, y - 14), (x + 188, y - 2), (x - 164, y + 4)], fill='#b13a2a')
        g.rect(x - 70, y - 62, x + 40, y - 12, fill='#f1efe8', ol=OL, w=2.4)
        g.rect(x - 40, y - 96, x + 20, y - 62, fill='#f1efe8', ol=OL, w=2.4)
        for i in range(5):
            g.rect(x - 62 + i * 21, y - 52, x - 48 + i * 21, y - 40, fill='#3a6f9f', ol=OL, w=1.4)
        for i in range(3):
            g.rect(x - 34 + i * 19, y - 88, x - 22 + i * 19, y - 76, fill='#3a6f9f', ol=OL, w=1.4)
        g.line([(x - 10, y - 96), (x - 10, y - 150)], OL, 3)
        g.line([(x - 30, y - 134), (x + 10, y - 134)], OL, 2)
        g.poly([(x + 20, y - 130), (x + 20, y - 112), (x + 50, y - 121)], fill='#d44')
        # crane / A-frame
        g.line([(x + 140, y - 12), (x + 175, y - 70), (x + 190, y - 12)], '#d6a82a', 5)
        g.line([(x + 175, y - 70), (x + 175, y - 20)], '#d6a82a', 3)
        # smoke
        for i in range(5):
            ph = (t * 0.5 + i * 0.2) % 1
            g.ellA(x + 6 + ph * 40, y - 150 - ph * 50, 6 + ph * 12, 5 + ph * 8, (210, 210, 215), 0.5 * (1 - ph))
        # bubbles
        for i in range(9):
            ph = (t * 0.35 + i * 0.11) % 1
            g.ell(tx + math.sin(ph * 12 + i) * 8, ty - ph * 250, 2.5 + (i % 3), fill=(220, 245, 255))
        # waterline foam over hull
        g.polyA([(x - 175, y + 14), (x + 190, y + 10), (x + 190, y + 40), (x - 175, y + 40)], (20, 120, 175), 0.6)
        # HUD
        a = ease(seg(t, 1.5, 2.5))
        if a > 0:
            f = font('DejaVuSansMono-Bold.ttf', 15)
            g.rect(shipx + 190, 270, shipx + 480, 322, fill=(6, 30, 40), ol=(110, 255, 210), w=1.6, r=4)
            g.text(shipx + 202, 280, 'SIDE-SCAN SONAR', f, (140, 255, 215))
            g.text(shipx + 202, 300, 'SCANNING SEABED ' + '.' * (int(t * 3) % 4), f, (140, 255, 215))
        zoom = 1.0 + 0.08 * (t / self.dur)
        return g.im, (700 + 60 * (t / self.dur), 400, zoom)


class S21(Scene):
    num, title = 21, 'Nothing?'

    def build(self):
        g = G()
        g.gradrect(0, 0, 1280, 720, [(0, '#1b2638'), (1, '#0e1522')])
        # windows band
        for i in range(4):
            x0 = 40 + i * 310
            g.gradrect(x0, 40, x0 + 280, 190, [(0, '#69b4de'), (0.55, '#2b84b8'), (1, '#16567f')])
            g.rect(x0, 40, x0 + 280, 190, ol='#0a1018', w=8)
            g.line([(x0 + 140, 40), (x0 + 140, 190)], '#0a1018', 6)
        g.rect(0, 580, 1280, 720, fill='#1a2331')
        g.rect(0, 572, 1280, 584, fill='#31405a')
        # pipes / panels on wall
        for i in range(6):
            g.rect(30 + i * 215, 230, 150 + i * 215, 262, fill='#222d40', ol='#0a1018', w=2)
            for k in range(6):
                g.ell(46 + i * 215 + k * 18, 246, 4, fill=['#2fe27a', '#e24f3a', '#e2c23a'][(i + k) % 3] if (i + k) % 4 else '#334')
        self.bg = g.im
        self.screen_noise = noise(420, 230, 14, 5, 3)

    def draw(self, t):
        g = G(self.bg)
        # sea through windows (animated)
        for i in range(4):
            x0 = 40 + i * 310
            for k in range(5):
                y = 90 + k * 20 + math.sin(t * 1.5 + i + k) * 3
                g.line([(x0 + 6, y), (x0 + 274, y + math.sin(t + k) * 2)], (180, 230, 250), 1.2)
        # desk consoles
        g.rect(80, 520, 330, 590, fill='#233049', ol=OL, w=2.5, r=6)
        g.rect(950, 520, 1200, 590, fill='#233049', ol=OL, w=2.5, r=6)
        for k in range(8):
            g.rect(98 + k * 28, 534, 112 + k * 28, 548, fill=['#e24f3a', '#2fe27a', '#e2c23a'][k % 3] if (int(t * 2) + k) % 4 else '#333')
        # monitor
        mx0, my0, mx1, my1 = 360, 150, 920, 490
        g.glow(640, 320, 420, (40, 120, 190), 0.35)
        g.rect(mx0 - 18, my0 - 18, mx1 + 18, my1 + 18, fill='#10151e', ol='#04070c', w=4, r=14)
        g.rect(mx0, my0, mx1, my1, fill='#031826')
        # screen content: scanning seabed picture
        sc = int((mx1 - mx0) * S), int((my1 - my0) * S)
        img = Image.new('RGB', sc, (3, 24, 38))
        arr = np.asarray(texture(sc[0], sc[1], 56, 12, '#052b45', '#16a1b8'), np.float32)
        yy = np.linspace(0, 1, sc[1])[:, None, None]
        arr = arr * (0.9 + 0.9 * yy)
        sweep = ((t * 0.3 + 0.05) % 1.0)
        xx = np.linspace(0, 1, sc[0])[None, :, None]
        mask = np.clip((sweep - xx) * 3 + 0.0, 0, 1)
        mask = np.where(xx > sweep, 0.25, 0.55 + 0.6 * np.clip(1 - (sweep - xx) * 1.4, 0, 1))
        arr = arr * mask
        # grid lines
        arr[::90, :, :] = arr[::90, :, :] * 0.5 + 50
        arr[:, ::90, :] = arr[:, ::90, :] * 0.5 + 50
        img = Image.fromarray(np.clip(arr, 0, 255).astype('uint8'))
        g.paste_rgb(img, mx0, my0)
        # scan line
        sx = mx0 + (mx1 - mx0) * sweep
        g.line([(sx, my0), (sx, my1)], (160, 255, 220), 3)
        g.glow(sx, (my0 + my1) / 2, 60, (80, 255, 190), 0.25)
        # seabed contour trace
        pts = [(mx0 + (mx1 - mx0) * i / 40, my0 + 230 + 26 * math.sin(i * 0.5) + 10 * math.sin(i * 1.7)) for i in range(41)]
        n = int(41 * sweep)
        if n > 1:
            g.line(pts[:n], (255, 240, 130), 2.4)
        # message
        a = ease(seg(t, 3.6, 4.3))
        if a > 0:
            blink = 0.55 + 0.45 * math.sin(t * 7)
            f = font('DejaVuSansMono-Bold.ttf', 26)
            g.rect(mx0 + 60, my0 + 120, mx1 - 60, my0 + 215, fill=(40, 6, 8), ol=(255, 80, 70), w=3, r=4)
            g.text(640, my0 + 150, 'NO BURIED CITY FOUND', f, (255, 90, 80) if blink > 0.6 else (160, 50, 44), 'mm')
            g.text(640, my0 + 190, '0 STRUCTURES  ·  0 WALLS', font('DejaVuSansMono-Bold.ttf', 18), (255, 160, 150), 'mm')
        # characters (profile busts)
        look_wobble = math.sin(t * 2.2)
        # left man
        lx, ly = 190, 360
        bust(g, lx, ly, 0.82, 'man', t, turn=0.75, talk=0, look=(0.9, 0.2), coat='#2f4468', nod=math.sin(t * 1.2) * 2)
        cap(g, lx + 3, ly - 16 * 0.82 + math.sin(t * 1.2) * 2, 0.82, '#25395a', 1)
        # hood detail
        # right man (beard, glasses)
        rx_, ry_ = 1090, 350
        shake = math.sin(t * 6) * 0.25 * ease(seg(t, 4.8, 5.2)) * (1 - ease(seg(t, 7.2, 7.6)))
        bust(g, rx_, ry_, 0.88, 'steven', t, turn=-0.75 + shake, talk=talk_amt(t, 0.5 < t < 3.5), look=(-0.9, 0.2), coat='#33415b', nod=math.sin(t * 1.3 + 1) * 2)
        cap(g, rx_ - 3, ry_ - 16 * 0.88 + math.sin(t * 1.3 + 1) * 2, 0.88, '#2a2f3a', -1)
        # pointing hand
        ph_ = ease(seg(t, 1.0, 1.8)) * (1 - ease(seg(t, 3.8, 4.4)))
        if ph_ > 0.01:
            sh = (rx_ - 120, ry_ + 190)
            hand = (lerp(sh[0] - 30, 940, ph_), lerp(sh[1] + 100, 380, ph_))
            limb(g, sh, ((sh[0] + hand[0]) / 2, (sh[1] + hand[1]) / 2 + 40), 34, '#33415b')
            limb(g, ((sh[0] + hand[0]) / 2, (sh[1] + hand[1]) / 2 + 40), hand, 26, '#33415b')
            g.ell(hand[0], hand[1], 15, 12, fill=SK['steven'], ol=OL, w=2)
        # question mark
        a = ease(seg(t, 5.6, 6.4))
        if a > 0:
            qmark(g, 250, 190, 0.7 * a, t)
        zoom = 1.0 + 0.12 * ease(t / self.dur)
        return g.im, (640, 340, zoom)


class S22(Scene):
    num, title = 22, 'A New Theory'
    warm = 0.5

    def build(self):
        g = G()
        g.gradrect(0, 0, 1280, 460, [(0, '#3d86d0'), (0.55, '#a9d4ec'), (1, '#f6e6c0')])
        g.glow(1060, 140, 190, (255, 230, 160), 0.4)
        mountains(g, 330, ['#8aa3c6', '#6d8fa8', '#4c7a68'], [80, 100, 70], seed=11)
        self.bg = g.im
        self.k = 0.0

    def surf(self, x, k):
        ytop = 585 - 235 * k
        xs = lerp(60, 330, k)
        return min(610, ytop + max(0, (xs + 120 - x)) * 0.55 + 6 * math.sin(x * 0.02))

    def draw(self, t):
        g = G(self.bg)
        k = ease(seg(t, 4.0, 9.0))
        p3 = ease(seg(t, 9.0, 11.0))
        clouds(g, t, seed=5, y0=70, y1=200, n=4, speed=5, a=0.85)
        # sea body
        sea_level = 385
        pts = [(x, sea_level) for x in range(-20, 1300, 40)]
        poly = pts + [(x, max(sea_level, self.surf(x, k))) for x in range(1280, -40, -40)]
        g.poly(poly, fill='#2a86bd')
        # animated sea surface
        wp = [(x, sea_level + math.sin(x * 0.03 + t * 2) * 2.5) for x in range(-20, 1300, 20)]
        g.line(wp, (225, 245, 255), 2.4)
        for i in range(8):
            yy = sea_level + 25 + i * 22
            g.line([(x, yy + math.sin(x * 0.02 + t * 1.2 + i) * 3) for x in range(-20, 700, 30)], (120, 195, 230), 1.2)
        # ruins on the sea floor / buried (base y 575)
        base = 578
        gh = 1.0
        for (rx, hh, kind) in ((470, 115, 'col'), (540, 90, 'col'), (610, 130, 'col'), (680, 100, 'col'), (750, 120, 'col')):
            column(g, rx, base, hh, 22, '#d9cdb0', broken=0.0 if kind == 'col' else 0)
        g.rect(440, base - 150, 790, base - 118, fill='#d9cdb0', ol='#8a7c5c', w=2)
        g.poly([(430, base - 150), (800, base - 150), (615, base - 215)], fill='#e1d6bb', ol='#8a7c5c', w=2)
        for (hx0, hw, hh) in ((850, 70, 70), (930, 60, 52), (360, 60, 58), (300, 50, 40)):
            g.rect(hx0, base - hh, hx0 + hw, base, fill='#c3a77e', ol='#6f5a3c', w=2)
            g.poly([(hx0 - 6, base - hh), (hx0 + hw + 6, base - hh), (hx0 + hw / 2, base - hh - 24)], fill='#a8553a', ol='#6f3a24', w=2)
        # water tint over the ruins (while submerged)
        sub = 1 - ease(seg(t, 4.5, 8.0))
        g.rectA(0, sea_level, 1280, 640, (30, 110, 170), 0.55 * sub)
        # fish above ruins
        for i in range(6):
            fx = (i * 230 + t * 40 * (1 if i % 2 else -1)) % 1300
            fy = 470 + 30 * math.sin(i * 2 + t)
            g.ell(fx, fy, 8, 3.6, fill=(255, 190, 80))
        # overburden / sediment with layers
        top = [(x, self.surf(x, k)) for x in range(-20, 1300, 20)]
        g.poly(top + [(1300, 740), (-20, 740)], fill='#b98b58')
        bands = [('#a97b4a', 40), ('#8f6a3f', 90), ('#c79d62', 140), ('#7a5736', 190), ('#9a7142', 240)]
        for c, off in bands:
            ptsb = [(x, self.surf(x, k) + off * (0.5 + 0.5 * k) + 8 * math.sin(x * 0.012 + off)) for x in range(-20, 1300, 20)]
            g.poly(ptsb + [(1300, 740), (-20, 740)], fill=c)
            g.line(ptsb, shade(c, 0.7), 2)
        # grass on top when land
        grass = ease(seg(t, 7.5, 9.0))
        gp = [(x, self.surf(x, k)) for x in range(-20, 1300, 20) if self.surf(x, k) < 560]
        if grass > 0 and len(gp) > 2:
            g.line(gp, '#5f9a3a', 10 * grass)
            for i in range(0, len(gp), 2):
                x, y = gp[i]
                g.line([(x, y), (x - 2, y - 8 * grass)], '#7bb948', 2)
        # arrows of sediment
        if 4.0 < t < 9.4:
            for i in range(7):
                ph = (t * 0.6 + i * 0.15) % 1
                ax = 140 + i * 170
                ay = 700 - ph * 150
                g.ellA(ax, ay, 8, 8, (255, 230, 170), 0.5 * (1 - ph))
                g.poly([(ax, ay - 16), (ax - 9, ay), (ax + 9, ay)], fill=(255, 235, 190))
        # trees on land at the end
        if grass > 0.5:
            for tx_, h_ in ((1000, 60), (1100, 80), (1180, 56)):
                ty_ = self.surf(tx_, k)
                g.line([(tx_, ty_), (tx_, ty_ - h_ * 0.5)], '#5a3a22', 6)
                g.ell(tx_, ty_ - h_ * 0.7, h_ * 0.38, h_ * 0.46, fill='#4b8f3a', ol='#2f5e24', w=2)
        # x-ray glow of buried ruins
        if p3 > 0:
            g.glow(615, base - 80, 300, (255, 190, 80), 0.42 * p3 * (0.8 + 0.2 * math.sin(t * 4)))
            for (rx, hh) in ((470, 115), (540, 90), (610, 130), (680, 100), (750, 120)):
                g.rectA(rx - 10, base - hh, rx + 10, base, (255, 214, 120), 0.75 * p3)
            g.polyA([(430, base - 150), (800, base - 150), (615, base - 215)], (255, 214, 120), 0.75 * p3)
            g.rectA(440, base - 150, 790, base - 118, (255, 214, 120), 0.75 * p3)
            for i in range(14):
                a = t * 1.4 + i
                g.line([(430 + i * 28, base - 220 - 6 * math.sin(a)), (440 + i * 28, base - 226 - 6 * math.sin(a))], (255, 235, 170), 0)
        # red cross while "sea" theory
        cr = ease(seg(t, 1.0, 1.8)) * (1 - ease(seg(t, 3.4, 4.0)))
        if cr > 0.01:
            cx_, cy_ = 620, 470
            ln = 120 * cr
            g.line([(cx_ - ln, cy_ - ln), (cx_ + ln, cy_ + ln)], (230, 50, 40), 24 * cr, True)
            g.line([(cx_ + ln, cy_ - ln), (cx_ - ln, cy_ + ln)], (230, 50, 40), 24 * cr, True)
        # land changed label
        a = ease(seg(t, 5.2, 6.0)) * (1 - ease(seg(t, 8.6, 9.0)))
        if a > 0.01:
            label(g, 'THE LAND CHANGED', 640, 250, a, size=30)
        a2 = ease(seg(t, 9.3, 10.0))
        if a2 > 0.01:
            label(g, 'BURIED, NOT DROWNED', 640, 250, a2, size=30, seed=5)
            qmark(g, 1130, 210, 0.75 * a2, t)
        if t < 1.0:
            pass
        zoom = 1.0 + 0.2 * p3 + 0.04 * (t / self.dur)
        return g.im, (640, 400 + 80 * p3, zoom)


class S23(Scene):
    num, title = 23, 'A Different Search'
    warm = 0.4

    def build(self):
        g = G()
        g.gradrect(0, 0, 1280, 460, [(0, '#3e88d3'), (0.6, '#a6d3ee'), (1, '#f4e3bc')])
        mountains(g, 420, ['#97a8c4', '#7d94ae', '#667f8a'], [90, 80, 60], seed=21)
        # ground
        g.poly([(-10, 470), (300, 462), (700, 470), (1000, 460), (1290, 470), (1290, 730), (-10, 730)], fill='#a36a3a')
        g.polyA([(-10, 560), (1290, 545), (1290, 730), (-10, 730)], (70, 40, 20), 0.28)
        rng = random.Random(3)
        for i in range(80):
            x, y = rng.uniform(0, 1280), rng.uniform(480, 720)
            g.ell(x, y, rng.uniform(2, 8), rng.uniform(1.5, 4), fill=shade('#b27a47', rng.uniform(0.7, 1.2)))
        # distant olive trees
        for x in (60, 140, 1150, 1230):
            g.line([(x, 470), (x, 440)], '#5a3a22', 5)
            g.ell(x, 430, 26, 22, fill='#6a8a40', ol='#3c5524', w=2)
        self.bg = g.im

    def rig(self, g, t, x, base):
        # tracks and body
        g.rect(x - 150, base - 24, x + 120, base + 6, fill='#2b2b2d', ol=OL, w=3, r=12)
        for i in range(8):
            g.ell(x - 130 + i * 34, base - 9, 9, fill='#444')
        g.rect(x - 140, base - 90, x + 100, base - 22, fill='#e58a1a', ol=OL, w=3, r=6)
        g.rect(x - 140, base - 60, x + 100, base - 52, fill='#b86a10')
        # cab
        g.poly([(x + 20, base - 90), (x + 20, base - 152), (x + 110, base - 152), (x + 130, base - 90)], fill='#e58a1a', ol=OL, w=3)
        g.poly([(x + 32, base - 96), (x + 32, base - 142), (x + 104, base - 142), (x + 120, base - 96)], fill='#8fd0ee', ol=OL, w=2)
        g.line([(x + 40, base - 138), (x + 60, base - 100)], (255, 255, 255), 2)
        figure(g, x + 78, base - 80, 0.5, t, hat='hard', anim='idle', shirt='#e8e8e8', shadow=False)
        # engine
        g.rect(x - 140, base - 120, x - 40, base - 90, fill='#cf7410', ol=OL, w=3)
        for i in range(5):
            g.line([(x - 130 + i * 20, base - 116), (x - 130 + i * 20, base - 94)], '#7a4208', 2)
        # tower (lattice)
        tx0, tx1, ttop = x - 12, x + 22, base - 330
        g.line([(tx0, base - 90), (tx0 + 4, ttop)], OL, 7)
        g.line([(tx1, base - 90), (tx1 - 4, ttop)], OL, 7)
        g.line([(tx0, base - 90), (tx0 + 4, ttop)], '#f0a020', 4)
        g.line([(tx1, base - 90), (tx1 - 4, ttop)], '#f0a020', 4)
        n = 10
        for i in range(n):
            ya = base - 90 - (base - 90 - ttop) * i / n
            yb = base - 90 - (base - 90 - ttop) * (i + 1) / n
            if i % 2 == 0:
                g.line([(tx0, ya), (tx1, yb)], '#f0a020', 2)
            else:
                g.line([(tx1, ya), (tx0, yb)], '#f0a020', 2)
        g.rect(x - 22, ttop - 12, x + 32, ttop + 6, fill='#d07410', ol=OL, w=2.4)
        # drill rod & carriage
        depth = 40 + 55 * (0.5 + 0.5 * math.sin(t * 0.9))
        cy = base - 270 + depth * 1.2
        rod_x = x + 5
        g.line([(rod_x, cy), (rod_x, base - 6 + depth * 0.4)], OL, 9)
        g.line([(rod_x, cy), (rod_x, base - 6 + depth * 0.4)], '#8c9298', 6)
        for i in range(8):
            yy = cy + 12 + i * 18 + (t * 90 % 18)
            if yy < base - 8:
                g.line([(rod_x - 3, yy), (rod_x + 3, yy + 5)], '#d0d4d8', 1.6)
        g.rect(x - 16, cy - 30, x + 26, cy + 4, fill='#b85a10', ol=OL, w=2.4)
        g.ell(x + 5, cy - 18, 4, fill='#222')
        # dust puffs at ground
        for i in range(10):
            ph = (t * 0.9 + i * 0.1) % 1
            g.ellA(rod_x + (i - 5) * 6 * ph + math.sin(i) * 12, base - 10 - ph * 50, 10 + ph * 26, 8 + ph * 18, (194, 150, 105), 0.55 * (1 - ph))

    def draw(self, t):
        g = G(self.bg)
        clouds(g, t, seed=7, y0=60, y1=200, n=4, speed=6, a=0.8)
        # rig
        self.rig(g, t, 430, 535)
        # workers
        wx = 120 + (t * 22) % 1500 * 0.0
        figure(g, 170 + 40 * math.sin(t * 0.5), 590, 1.05, t, hat='hard', vest='#f06a1a', shirt='#6c7f98', pants='#3d4a60', anim='walk', ph=0, face=1, tool='clip')
        figure(g, 760, 600, 1.1, t, hat='hard', hatc='#f2c230', vest='#f06a1a', shirt='#6a7a90', pants='#3a4258', anim='idle', face=-1, ph=1, tool='clip')
        figure(g, 640, 640, 0.98, t, hat='hard', hatc='#f2d230', vest='#f08a1a', shirt='#8892a0', pants='#3f4a5c', anim='dig', face=-1, ph=2, tool='shovel')
        # GPR cart moving
        cx = 880 + 60 * math.sin(t * 0.4)
        g.rect(cx - 40, 626, cx + 40, 654, fill='#2d6fb0', ol=OL, w=2.4, r=5)
        g.ell(cx - 26, 660, 13, fill='#222', ol=OL, w=2)
        g.ell(cx + 26, 660, 13, fill='#222', ol=OL, w=2)
        g.line([(cx + 30, 626), (cx + 88, 560)], '#333', 4)
        g.line([(cx + 78, 560), (cx + 100, 556)], '#333', 5)
        g.rect(cx - 20, 612, cx + 14, 626, fill='#e8d33a', ol=OL, w=1.6)
        for k in range(4):
            ph = (t * 1.2 + k * 0.25) % 1
            g.arc(cx, 668, 30 + ph * 80, 14 + ph * 40, 20, 160, (120, 255, 200), 2)
        figure(g, cx + 108, 650, 0.95, t, hat='hard', vest='#f06a1a', shirt='#6c7f98', pants='#3d4a60', anim='walk', ph=0.4, face=-1)
        # core boxes foreground
        for i in range(4):
            g.rect(980 + i * 66, 610 + i * 6, 1034 + i * 66, 650 + i * 6, fill='#c9a46a', ol=OL, w=2)
            for k in range(3):
                g.rect(986 + i * 66, 618 + k * 9 + i * 6, 1028 + i * 66, 624 + k * 9 + i * 6, fill=['#8a5a3a', '#caa46a', '#6a4a30'][k])
        dust(g, t, 9, 40, 0, 440, 1280, 700, (255, 235, 200), speed=14, size=1.8)
        zoom = 1.05 + 0.05 * (t / self.dur)
        return g.im, (560 + 90 * (t / self.dur), 400, zoom)
