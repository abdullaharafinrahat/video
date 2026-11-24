"""Scenes 30-32"""
import math, random
from gfx import *
from art import *
from scenes1 import Scene
from scenes2 import rot, pin, amphora

INK = (58, 38, 22)


# ---------------------------------------------------------------- helpers
_stamp_cache = {}


def stamp(g, text, x, y, angle, scale, a, col=(200, 40, 34), size=54):
    key = (text, size, col)
    if key not in _stamp_cache:
        f = font_px('Cinzel.ttf', size * 2, bold=True)
        bb = f.getbbox(text)
        w, h = bb[2] + 80, bb[3] + 60
        im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([6, 6, w - 7, h - 7], radius=18, outline=col + (255,), width=10)
        d.rounded_rectangle([22, 22, w - 23, h - 23], radius=10, outline=col + (255,), width=3)
        d.text((w / 2, h / 2 + 4), text, font=f, fill=col + (255,), anchor='mm')
        # grunge
        rng = np.random.default_rng(3)
        al = np.asarray(im.getchannel('A'), np.float32)
        holes = (rng.random(al.shape) > 0.9).astype(np.float32)
        al = al * (1 - 0.55 * holes)
        im.putalpha(Image.fromarray(al.astype('uint8')))
        _stamp_cache[key] = im
    im = _stamp_cache[key]
    w, h = im.size
    k = scale * 0.5
    sp = im.resize((max(2, int(w * k)), max(2, int(h * k))), Image.BILINEAR).rotate(angle, expand=True, resample=Image.BILINEAR)
    g.paste_rgba(sp, x - sp.size[0] / S / 2, y - sp.size[1] / S / 2, a)


_circ = {}


def magnify(g, cx, cy, r, zoom=1.7):
    """glass lens at (cx,cy) logical radius r: magnifies what is already drawn"""
    R = int(r * S)
    if R not in _circ:
        m = Image.new('L', (R * 2, R * 2), 0)
        ImageDraw.Draw(m).ellipse([0, 0, R * 2 - 1, R * 2 - 1], fill=255)
        _circ[R] = m
    sw = int(R * 2 / zoom)
    x0, y0 = int(cx * S - sw / 2), int(cy * S - sw / 2)
    x0 = max(0, min(W - sw, x0))
    y0 = max(0, min(H - sw, y0))
    crop = g.im.crop((x0, y0, x0 + sw, y0 + sw)).resize((R * 2, R * 2), Image.BILINEAR)
    g.im.paste(crop, (int(cx * S - R), int(cy * S - R)), _circ[R])
    # glass
    g.ell(cx, cy, r, r, ol='#5a3a1c', w=9)
    g.ell(cx, cy, r - 4, r - 4, ol='#d7b25a', w=3)
    g.arc(cx, cy, r - 14, r - 14, 200, 260, (255, 255, 255), 5)
    g.ellA(cx - r * 0.35, cy - r * 0.4, r * 0.18, r * 0.1, (255, 255, 255), 0.35)
    # handle
    a = math.radians(45)
    hx_, hy_ = cx + math.cos(a) * r, cy + math.sin(a) * r
    g.line([(hx_, hy_), (hx_ + 86, hy_ + 86)], OL, 24, True)
    g.line([(hx_, hy_), (hx_ + 86, hy_ + 86)], '#7a4a24', 18, True)
    g.line([(hx_ + 2, hy_ + 2), (hx_ + 30, hy_ + 30)], '#d7b25a', 20, True)


def house(g, x, y, w, h, col='#8a6a44', roof='#6a3a24', jx=0):
    g.rect(x + jx, y - h, x + w + jx, y, fill=col, ol=INK, w=2)
    g.poly([(x - 6 + jx, y - h), (x + w + 6 + jx, y - h), (x + w / 2 + jx, y - h - w * 0.35)], fill=roof, ol=INK, w=2)
    g.rect(x + w * 0.4 + jx, y - h * 0.55, x + w * 0.62 + jx, y, fill=INK)


# ---------------------------------------------------------------- 30
class S30(Scene):
    num, title = 30, 'Was the Story True?'
    warm = 1.0

    def build(self):
        g = G()
        g.gradrect(0, 0, 1280, 720, [(0, '#2a1d14'), (1, '#140e0a')])
        # wooden desk
        tex = texture(W, H, 90, 8, '#4a3020', '#6a4630', 3)
        g.im.paste(tex, (0, 0))
        for i in range(14):
            g.line([(0, 50 + i * 52), (1280, 40 + i * 52 + 8 * math.sin(i))], (50, 32, 20), 2)
        g.rectA(0, 0, 1280, 720, (0, 0, 0), 0.25)
        self.bg = g.im
        self.ptex = texture(1100 * S, 480 * S, 70, 21, '#d8bc84', '#efd9a2', 4)

    def city(self, g, t, jit, flood):
        base = 470
        ox = 250
        # ground line
        g.line([(ox, base), (ox + 760, base)], INK, 3)
        for (x, w, h) in ((ox + 20, 56, 44), (ox + 100, 60, 56), (ox + 180, 50, 40), (ox + 540, 60, 52), (ox + 620, 56, 44), (ox + 690, 52, 38)):
            house(g, x, base, w, h, jx=jit * math.sin(t * 38 + x))
        # temple
        temple(g, ox + 390, base, 210, 120, col='#9a7a50', n=6, steps=2)
        # sea waves ink
        for k in range(3):
            pts = [(ox + i * 20, base + 22 + k * 20 + 4 * math.sin(i * 0.8 + t * 2 + k)) for i in range(0, 39)]
            g.line(pts, (60, 80, 100), 2)
        if flood > 0:
            lvl = base + 20 - flood * 190
            top = [(ox - 10 + i * 20, lvl + 12 * math.sin(i * 0.7 - t * 4) + 6 * math.sin(i * 1.9 + t * 6)) for i in range(0, 40)]
            g.polyA(top + [(ox + 770, 560), (ox - 10, 560)], '#2a4a68', 0.9)
            g.line(top, (210, 235, 245), 3)
            for i in range(0, 40, 3):
                x, y = top[i]
                g.ellA(x, y - 4, 7, 4, (240, 250, 255), 0.7)

    def draw(self, t):
        g = G(self.bg)
        flick = 0.85 + 0.15 * math.sin(t * 8) * math.sin(t * 2.3)
        g.glow(640, 80, 600, (255, 190, 100), 0.4 * flick)
        # unrolling scroll
        wr = 1050 * ease(seg(t, 0.3, 3.2))
        cx, cy, hh = 640, 380, 480
        shake = ease(seg(t, 13.2, 14.0)) * (1 - ease(seg(t, 15.4, 16.0)))
        sx, sy = shake * math.sin(t * 45) * 5, shake * math.sin(t * 52) * 4
        if wr > 10:
            x0 = cx - wr / 2
            crop = self.ptex.crop((int((1100 - wr) / 2 * S), 0, int((1100 + wr) / 2 * S), int(hh * S)))
            g.paste_rgb(crop, x0 + sx, cy - hh / 2 + sy)
            g.polyA([(x0 + sx, cy - hh / 2 + sy), (x0 + 40 + sx, cy - hh / 2 + sy), (x0 + 40 + sx, cy + hh / 2 + sy), (x0 + sx, cy + hh / 2 + sy)], (90, 50, 20), 0.25)
            g.line([(x0 + sx, cy - hh / 2 + sy), (x0 + wr + sx, cy - hh / 2 + sy)], '#6a4a28', 4)
            g.line([(x0 + sx, cy + hh / 2 + sy), (x0 + wr + sx, cy + hh / 2 + sy)], '#6a4a28', 4)
            for xr in (x0, x0 + wr):
                g.rect(xr - 20 + sx, cy - hh / 2 - 22 + sy, xr + 20 + sx, cy + hh / 2 + 22 + sy, fill='#7a4a24', ol=OL, w=3, r=16)
                g.rect(xr - 20 + sx, cy - hh / 2 - 22 + sy, xr - 6 + sx, cy + hh / 2 + 22 + sy, fill='#a06a38', r=10)
                g.ell(xr + sx, cy - hh / 2 - 22 + sy, 20, 8, fill='#caa064', ol=OL, w=2)
                g.ell(xr + sx, cy + hh / 2 + 22 + sy, 20, 8, fill='#5a3418', ol=OL, w=2)
            # content (only once opened)
            if wr > 900:
                # temporarily draw onto copy shifted by shake: draw direct
                a = ease(seg(t, 3.2, 4.2))
                f = font('Cinzel.ttf', 62)
                g.text(640 + sx, 205 + sy, '373 BC', f, INK, 'mm')
                g.line([(420 + sx, 244 + sy), (860 + sx, 244 + sy)], INK, 2)
                flood = ease(seg(t, 16.0, 19.6))
                jit = shake * 5
                self.city(g, t, jit, flood)
                if flood > 0.1:
                    f2 = font('Lora.ttf', 26)
                    g.text(640, 335, '“…and the city vanished beneath the sea.”', f2, INK, 'mm') if flood > 0.8 else None
                # quake zigzags
                if 13.2 < t < 16.2:
                    for k in range(3):
                        zz = []
                        for i in range(20):
                            zz.append((300 + i * 38, 520 + k * 22 + (8 if i % 2 else -8) * math.sin(t * 20 + k)))
                        g.line(zz, (150, 40, 30), 3)
                    label(g, 'EARTHQUAKE', 640, 300, ease(seg(t, 13.4, 13.9)) * (1 - ease(seg(t, 15.6, 16.0))), size=22, seed=3)
        # magnifier scanning
        ma = ease(seg(t, 5.0, 5.8)) * (1 - ease(seg(t, 12.0, 12.8)))
        if ma > 0.01:
            mx = 640 + 330 * math.sin(t * 0.9)
            my = 400 + 40 * math.sin(t * 1.7)
            magnify(g, mx, my - (1 - ma) * 300, 100 * (0.4 + 0.6 * ma), 1.8)
        # stamp "TRUE?"
        sa = seg(t, 8.4, 8.8)
        if sa > 0 and t < 12.8:
            sc = lerp(2.4, 1.0, eo(sa))
            stamp(g, 'COMPLETELY TRUE?', 640, 330, -9, sc * 0.8, ease(sa) * (1 - ease(seg(t, 12.2, 12.8))))
        # end question
        ea = ease(seg(t, 19.8, 20.6))
        if ea > 0:
            stamp(g, 'LEGEND?', 640, 330, 6, 0.9 * (0.6 + 0.4 * ea), ea * 0.95, col=(120, 50, 20))
        dust(g, t, 5, 40, 0, 0, 1280, 720, (255, 220, 160), speed=6, size=1.6, drift=(1, -0.3))
        zoom = 1.0 + 0.1 * (t / self.dur)
        return g.im, (640, 380, zoom)


# ---------------------------------------------------------------- 31
LAYERS = [('#b8925a', 0), ('#9a7444', 1), ('#c2a06a', 2), ('#7c5c38', 3), ('#a88458', 4)]


def strata_card(g, x0, y0, x1, y1, t, wave=1.0):
    g.polyA([(x0 + 10, y0 + 12), (x1 + 10, y0 + 12), (x1 + 10, y1 + 12), (x0 + 10, y1 + 12)], (0, 0, 0), 0.45)
    g.rect(x0 - 10, y0 - 10, x1 + 10, y1 + 10, fill='#f0e6c8', ol=OL, w=3, r=6)
    n = len(LAYERS)
    hh = (y1 - y0) / n
    for i, (c, k) in enumerate(LAYERS):
        ya = y0 + i * hh
        top = [(x, ya + wave * (4 * math.sin(x * 0.02 + k * 2))) for x in range(int(x0), int(x1) + 20, 20)]
        top = [(min(x, x1), y) for x, y in top]
        g.poly(top + [(x1, ya + hh + 2), (x0, ya + hh + 2)], fill=c)
        g.line(top, shade(c, 0.6), 2)
    rng = random.Random(4)
    for i in range(70):
        x = rng.uniform(x0 + 8, x1 - 8)
        y = rng.uniform(y0 + 8, y1 - 8)
        g.ell(x, y, rng.uniform(2, 6), rng.uniform(1.5, 3.5), fill=shade('#b8925a', rng.uniform(0.6, 1.2)))
    # artifacts: shards, charcoal
    for (fx, fy, kind) in ((0.15, 0.1, 'pot'), (0.7, 0.3, 'wall'), (0.35, 0.5, 'pot'), (0.82, 0.7, 'pot'), (0.2, 0.9, 'wall'), (0.55, 0.12, 'wall'), (0.6, 0.7, 'pot')):
        x, y = x0 + (x1 - x0) * fx, y0 + (y1 - y0) * fy
        if kind == 'pot':
            g.poly([(x - 12, y - 4), (x + 4, y - 10), (x + 14, y + 2), (x - 2, y + 9)], fill='#cf6f2c', ol=OL, w=1.6)
            g.line([(x - 8, y), (x + 8, y - 2)], '#1c1210', 2)
        else:
            g.rect(x - 22, y - 8, x + 22, y + 8, fill='#cdbf9e', ol='#6a5a40', w=1.6, r=2)


class S31(Scene):
    num, title = 31, 'The 2021 Study'
    warm = 0.5

    def build(self):
        g = G()
        g.gradrect(0, 0, 1280, 720, [(0, '#16233a'), (1, '#0b1220')])
        for i in range(8):
            g.line([(0, 80 + i * 90), (1280, 80 + i * 90)], (26, 40, 66), 1.6)
        g.rect(0, 600, 1280, 730, fill='#4a3020')
        g.rectA(0, 600, 1280, 640, (0, 0, 0), 0.3)
        self.bg = g.im

    def paper(self, g, t, px, py, ang, hl):
        w, h = 430, 560
        pts = rot([(px - w / 2, py - h / 2), (px + w / 2, py - h / 2), (px + w / 2, py + h / 2), (px - w / 2, py + h / 2)], px, py, ang)
        g.polyA([(x + 12, y + 14) for x, y in pts], (0, 0, 0), 0.5)
        g.poly(pts, fill='#f6f2e6', ol='#8a8470', w=3)

        def R(pp):
            return rot([pp], px, py, ang)[0]
        # masthead
        mh = rot([(px - w / 2, py - h / 2), (px + w / 2, py - h / 2), (px + w / 2, py - h / 2 + 90), (px - w / 2, py - h / 2 + 90)], px, py, ang)
        g.poly(mh, fill='#7a1f24')
        mp = R((px, py - h / 2 + 34))
        g.text(mp[0], mp[1], 'SEISMOLOGICAL', font('Cinzel.ttf', 25), (250, 235, 200), 'mm')
        mp = R((px, py - h / 2 + 64))
        g.text(mp[0], mp[1], 'RESEARCH LETTERS', font('Cinzel.ttf', 25), (250, 235, 200), 'mm')
        yp = R((px + w / 2 - 60, py - h / 2 + 130))
        g.text(yp[0], yp[1], '2021', font('Cinzel.ttf', 40), '#7a1f24', 'mm')
        # title lines
        for i, wd in enumerate((330, 360, 250)):
            a = R((px - w / 2 + 24, py - h / 2 + 150 + i * 28))
            b = R((px - w / 2 + 24 + wd, py - h / 2 + 150 + i * 28))
            g.line([a, b], (40, 40, 50), 12, True)
        # author
        ap = R((px - w / 2 + 24, py - h / 2 + 252))
        auth = 'Stathis Stiros'
        n = int(len(auth) * ease(seg(t, 12.1, 13.2)))
        g.text(ap[0], ap[1], auth[:n], font('Lora.ttf', 26), '#40404c', 'lm')
        # body lines with highlights
        for i in range(10):
            yy = py - h / 2 + 290 + i * 24
            a = R((px - w / 2 + 24, yy))
            b = R((px - w / 2 + 24 + (360 if i % 4 != 3 else 220), yy))
            ph = clamp(hl * 10 - i)
            if ph > 0 and i in (1, 2, 3, 5, 6, 7):
                bb = R((px - w / 2 + 24 + (360 if i % 4 != 3 else 220) * ph, yy))
                g.line([a, bb], (255, 232, 90), 16)
            g.line([a, b], (150, 150, 160), 5, True)

    def draw(self, t):
        g = G(self.bg)
        g.glow(640, 60, 560, (255, 200, 120), 0.3)
        # PHASE A: examining the evidence (0 - 7.2)
        A = 1 - ease(seg(t, 6.6, 7.6))
        if A > 0.01:
            off = (1 - A) * -900
            strata_card(g, 340 + off, 170, 940 + off, 520, t)
            f = font('Cinzel.ttf', 26)
            if A > 0.5:
                label(g, 'EXAMINING THE EVIDENCE', 640 + off, 120, ease(seg(t, 0.4, 1.0)), size=26, seed=5)
            ma = ease(seg(t, 0.8, 1.6))
            mx = 480 + 300 * (0.5 + 0.5 * math.sin(t * 0.8)) + off
            my = 340 + 80 * math.sin(t * 1.3)
            magnify(g, mx, my - (1 - ma) * 400, 110, 1.9)
            qa = ease(seg(t, 4.4, 5.2))
            if qa > 0:
                qmark(g, 1010 + off, 300, 0.7 * qa, t)
                label(g, 'SERIOUS QUESTIONS', 1010 + off, 410, qa, size=20, seed=8)
        # PHASE B: the journal paper (7.2 - 25)
        B = ease(seg(t, 7.2, 8.4)) * (1 - ease(seg(t, 24.0, 25.0)))
        if B > 0.01:
            px = lerp(1500, 420, eo(seg(t, 7.2, 8.4))) - ease(seg(t, 24.0, 25.0)) * 800
            hl = seg(t, 15.4, 22.5)
            self.paper(g, t, px, 360 + math.sin(t * 1.1) * 5, -0.04 + 0.01 * math.sin(t * 0.7), hl)
            # callouts
            c1 = ease(seg(t, 17.2, 17.8)) * (1 - ease(seg(t, 24.0, 24.6)))
            c2 = ease(seg(t, 20.8, 21.4)) * (1 - ease(seg(t, 24.0, 24.6)))
            x = 960 - (1 - eo(c1)) * -300
            for (cc, yy, txt, sub) in ((c1, 270, 'ENTIRE CITY DESTROYED', 'not supported'), (c2, 440, 'PERMANENTLY SUBMERGED', 'not supported')):
                if cc > 0:
                    label(g, txt, 950 + (1 - eo(cc)) * 400, yy, cc, size=22, sub=sub, seed=int(yy))
                    xx = 950 + (1 - eo(cc)) * 400
                    f = font('DejaVuSans-Bold.ttf', 60)
                    g.text(xx - 250, yy, '✕', f, (220, 50, 40), 'mm')
            ca = ease(seg(t, 14.6, 15.2)) * (1 - ease(seg(t, 17.0, 17.6)))
            label(g, 'CHALLENGED THE TRADITIONAL ACCOUNT', 900, 160, ca, size=22, seed=14)
            # year glow
            ya = ease(seg(t, 7.8, 8.4)) * (1 - ease(seg(t, 10.5, 11.2)))
            if ya > 0:
                label(g, 'PUBLISHED 2021', 950, 360, ya, size=30, seed=2)
        # PHASE C: continuous layers (25 - end)
        C = ease(seg(t, 24.4, 25.6))
        if C > 0.01:
            off = (1 - C) * 900
            x0, y0, x1, y1 = 240 + off, 200, 1040 + off, 520
            strata_card(g, x0, y0, x1, y1, t, wave=0.8)
            lx = 640 + off
            # dashed disaster line
            p = ease(seg(t, 26.2, 27.4))
            yb = y0 - 40 + (y1 - y0 + 80) * p
            for yy in range(int(y0 - 40), int(yb), 24):
                g.line([(lx, yy), (lx, yy + 12)], (230, 50, 40), 4)
            la = ease(seg(t, 26.4, 27.0))
            label(g, '373 BC', lx, y0 - 70, la, size=28, seed=4)
            # arrows across layers
            hh = (y1 - y0) / 5
            for i in range(5):
                a = ease(seg(t, 27.6 + i * 0.45, 28.2 + i * 0.45))
                if a > 0:
                    yy = y0 + hh * (i + 0.5)
                    xa = lx - 300 * a
                    xb = lx + 300 * a
                    g.line([(xa, yy), (xb, yy)], (255, 255, 255), 5, True)
                    g.poly([(xb + 12, yy), (xb - 6, yy - 10), (xb - 6, yy + 10)], fill=(255, 255, 255))
            ga = ease(seg(t, 29.8, 30.4))
            if ga > 0:
                label(g, 'LAYERS CONTINUE', 640 + off, 590, ga, size=30, seed=6)
                g.text(870 + off, 590, '✔', font('DejaVuSans-Bold.ttf', 60), (90, 220, 120), 'mm')
        dust(g, t, 3, 30, 0, 0, 1280, 700, (200, 220, 255), speed=6, size=1.4, drift=(1, -0.3))
        zoom = 1.0 + 0.06 * (t / self.dur)
        return g.im, (640, 360, zoom)


# ---------------------------------------------------------------- 32
def make_coin_faces():
    R = 190
    faces = []
    for side in (0, 1):
        g = G()
        cx, cy = 200, 200
        # metal disc
        for i in range(10):
            rr = R - i * 1.2
            g.ell(cx, cy, rr, rr, fill=mix('#8e8668', '#d9d0aa', i / 10))
        g.ell(cx, cy, R, R, ol='#2a2418', w=4)
        g.ell(cx, cy, R - 24, R - 24, ol='#6e664c', w=3)
        for i in range(60):
            a = i / 60 * math.tau
            g.ell(cx + math.cos(a) * (R - 12), cy + math.sin(a) * (R - 12), 3.2, fill='#f2ecd0')
        base = '#e8e0c0'
        dk = '#6e664c'
        if side == 0:
            # Poseidon profile (facing right)
            P = [(-14, -112), (36, -118), (70, -92), (82, -62), (88, -44), (104, -26), (88, -18), (92, 2), (104, 10), (90, 22), (86, 40), (70, 60), (58, 92), (18, 112), (-34, 132), (-80, 142), (-98, 70), (-104, -20), (-84, -86)]
            g.poly([(cx + x * 0.8, cy + y * 0.8 - 8) for x, y in P], fill=base, ol=dk, w=3)
            # hair curls
            for i in range(16):
                a = math.radians(170 + i * 12)
                g.ell(cx + math.cos(a) * 82 * 0.8 - 8, cy - 8 + math.sin(a) * 100 * 0.8 - 6, 17, fill=base, ol=dk, w=2.4)
            for i in range(9):
                a = math.radians(-10 + i * 20)
                g.ell(cx + 60 + math.cos(a) * 30 - 18, cy + 40 + i * 5, 12, fill=base, ol=dk, w=2.2)
            g.ell(cx + 56, cy - 40, 7, 4, fill='#fffdf0', ol=dk, w=2)
            g.ell(cx + 58, cy - 40, 2.4, fill='#2a2418')
            g.line([(cx + 52, cy - 58), (cx + 74, cy - 56)], dk, 4, True)
            g.line([(cx + 74, cy + 6), (cx + 84, cy + 8)], dk, 3, True)
            # wreath band
            g.line([(cx - 60, cy - 78), (cx + 40, cy - 90)], dk, 5, True)
            # trident small left
            g.line([(cx - 150, cy - 90), (cx - 150, cy + 80)], dk, 5, True)
            for dx in (-18, 0, 18):
                g.line([(cx - 150 + dx, cy - 108), (cx - 150 + dx, cy - 80)], dk, 4, True)
            g.line([(cx - 168, cy - 82), (cx - 132, cy - 82)], dk, 4)
        else:
            # trident big + fish
            g.line([(cx, cy - 110), (cx, cy + 90)], dk, 9, True)
            for dx in (-44, 0, 44):
                g.line([(cx + dx, cy - 100), (cx + dx, cy - 150 if dx == 0 else cy - 135)], dk, 8, True)
            g.line([(cx - 44, cy - 96), (cx - 44, cy - 52), (cx + 44, cy - 52), (cx + 44, cy - 96)], dk, 8)
            g.poly([(cx - 44, cy - 136), (cx - 52, cy - 120), (cx - 36, cy - 120)], fill=dk)
            g.poly([(cx + 44, cy - 136), (cx + 52, cy - 120), (cx + 36, cy - 120)], fill=dk)
            g.poly([(cx, cy - 158), (cx - 9, cy - 140), (cx + 9, cy - 140)], fill=dk)
            # dolphin
            pts = [(cx + 70 + 40 * math.cos(a), cy + 36 + 22 * math.sin(a * 1.0 + 1) - 40 * math.sin(a * 0.5)) for a in np.linspace(0.3, 3.0, 12)]
            g.line([(cx - 110 + i * 14, cy + 60 + 16 * math.sin(i * 0.9)) for i in range(16)], dk, 7, True)
            f = font('DejaVuSerif-Bold.ttf', 36)
            g.text(cx - 100, cy + 12, 'Ε', f, dk, 'mm')
            g.text(cx - 100, cy + 52, 'Λ', f, dk, 'mm')
            g.text(cx + 100, cy + 12, 'Ι', f, dk, 'mm')
            g.text(cx + 100, cy + 52, 'Κ', f, dk, 'mm')
        # patina shading
        g.ellA(cx + 60, cy + 70, 150, 120, (40, 36, 20), 0.18)
        box = (0, 0, 400 * S, 400 * S)
        face = g.im.crop(box)
        m = Image.new('L', face.size, 0)
        ImageDraw.Draw(m).ellipse([int((cx - R) * S), int((cy - R) * S), int((cx + R) * S), int((cy + R) * S)], fill=255)
        face = face.convert('RGBA')
        face.putalpha(m)
        faces.append(face)
    return faces


class S32(Scene):
    num, title = 32, 'The Unexpected Twist'
    warm = 1.2

    def build(self):
        g = G()
        g.gradrect(0, 0, 1280, 720, [(0, '#3a2a54'), (0.35, '#c4603a'), (0.62, '#f6b45a'), (1, '#4a2a1a')])
        g.glow(900, 330, 420, (255, 210, 130), 0.9)
        g.ell(900, 330, 70, 70, fill='#fff1c0')
        mountains(g, 470, ['#7a4a50', '#5a3a48', '#3a2a3a'], [90, 70, 50], seed=51, bottom=720)
        self.bg = g.im
        self.faces = make_coin_faces()

    def coin(self, g, cx, cy, size, ang, a=1.0):
        if size < 0.03:
            return
        c = math.cos(ang)
        face = self.faces[0 if c >= 0 else 1]
        w = max(2, int(abs(c) * 400 * S * size))
        h = max(2, int(400 * S * size))
        spr = face.resize((w, h), Image.BILINEAR)
        if c < 0:
            spr = spr.transpose(Image.FLIP_LEFT_RIGHT)
        # edge thickness
        th = 14 * size * (1 - abs(c)) * S
        if th > 1:
            ex = int(th)
            edge = Image.new('RGBA', (w + ex * 2, h), (0, 0, 0, 0))
            d = ImageDraw.Draw(edge)
            d.ellipse([0, int(h * 0.025), w + ex * 2 - 1, int(h * 0.975)], fill=(110, 98, 66, 255))
            g.paste_rgba(edge, cx - (w + ex * 2) / S / 2, cy - h / S / 2, a)
        g.paste_rgba(spr, cx - w / S / 2, cy - h / S / 2, a)
        # glint
        gl = (math.sin(ang * 2 + 0.5) * 0.5 + 0.5) ** 6
        if gl > 0.05:
            g.glow(cx + 70 * size * c, cy - 80 * size, 90 * size, (255, 250, 220), 0.5 * gl)

    def draw(self, t):
        g = G(self.bg)
        # ruins background
        sway = math.sin(t * 0.3) * 0.0
        temple(g, 930, 640, 520, 330, col='#d9a77a', n=7, steps=3)
        for x, h, br in ((560, 160, 0.4), (640, 120, 0.6), (1290, 220, 0.0)):
            column(g, x, 650, h, 46, '#cf9d70', broken=br)
        g.polyA([(0, 650), (1280, 640), (1280, 720), (0, 720)], (20, 10, 10), 0.8)
        g.glow(930, 520, 380, (255, 190, 100), 0.25)
        # light rays
        for i in range(5):
            x = 900 + (i - 2) * 140
            g.polyA([(900, 330), (900 + (i - 2) * 30, 330), (x + 80, 700), (x - 80, 700)], (255, 220, 150), 0.04)
        # shake at "Wait."
        wt = seg(t, 7.3, 8.1)
        flash = max(0.0, 1 - abs(t - 7.5) / 0.35)
        # coin position / size by phase
        big = 1 - ease(seg(t, 7.3, 8.3))
        back = ease(seg(t, 15.2, 16.2))
        sz = lerp(0.45, 1.0, max(big, back * 1.0)) if t < 15.2 else lerp(0.45, 1.0, back)
        if t < 7.3:
            sz = 1.0
        cx = lerp(300, 330, max(big, back)) if t >= 7.3 else 330
        cy = lerp(220, 360, max(big, back)) if t >= 7.3 else 360
        cx = cx + (math.sin(t * 60) * 6 * flash)
        spin = t * 1.9
        if t > 8.3:
            spin = 1.9 * 8.3 + (t - 8.3) * 1.1
        self.coin(g, cx, cy + math.sin(t * 1.5) * 8, sz * 0.95, spin)
        # labels early
        a = ease(seg(t, 1.0, 1.8)) * (1 - ease(seg(t, 6.6, 7.2)))
        label(g, 'COINS ISSUED DECADES LATER', 880, 130, a, size=28, seed=3)
        # timeline (7.8 - 15.2)
        T = ease(seg(t, 8.0, 8.8)) * (1 - ease(seg(t, 14.8, 15.4)))
        if T > 0.01:
            g.rectA(120, 470, 1180, 690, (12, 6, 10), 0.6 * T)
            p = ease(seg(t, 8.2, 9.6))
            g.line([(160, 590), (160 + 960 * p, 590)], (250, 235, 200), 5, True)
            m1 = ease(seg(t, 9.3, 9.9))
            if m1 > 0:
                g.ell(330, 590, 14 * m1, 14 * m1, fill=(220, 50, 40), ol=(255, 255, 255), w=3)
                label(g, '373 BC', 330, 530, m1, size=24, seed=3)
                label(g, 'ALLEGED DESTRUCTION', 330, 650, m1, size=18, seed=5)
                g.text(330 + 70, 590, '✕', font('DejaVuSans-Bold.ttf', 40), (230, 60, 50), 'mm')
            m2 = ease(seg(t, 11.0, 11.7))
            if m2 > 0:
                # decades bracket
                g.line([(350, 620), (350, 630), (860, 630), (860, 620)], (255, 214, 120), 3)
                g.text(605, 640, 'DECADES LATER', font('Cinzel.ttf', 20), (255, 214, 120), 'mm')
                self.coin(g, 880, 560, 0.22 * m2, t * 3)
                label(g, 'COINS STILL ISSUED', 880, 505, m2, size=22, seed=7)
            m3 = ease(seg(t, 12.6, 13.3))
            if m3 > 0:
                qmark(g, 1080, 520, 0.55 * m3, t)
        # wait flash
        if flash > 0:
            g.rectA(0, 0, 1280, 720, (255, 255, 255), 0.55 * flash)
            f = font('Cinzel.ttf', 150)
            g.text(642, 362, 'WAIT.', f, (30, 20, 10), 'mm')
            g.text(640, 360, 'WAIT.', f, (255, 236, 190), 'mm')
        # conclusion labels
        a1 = ease(seg(t, 15.9, 16.5)) * (1 - ease(seg(t, 19.0, 19.5)))
        label(g, 'SOMETHING MAY HAVE HAPPENED…', 880, 180, a1, size=30, seed=4)
        a2 = ease(seg(t, 19.2, 19.9))
        label(g, 'BUT THE STORY IS MORE COMPLICATED', 880, 180, a2, size=30, seed=9)
        dust(g, t, 6, 50, 0, 0, 1280, 720, (255, 225, 160), speed=9, size=1.8, drift=(1, -0.5))
        zoom = 1.0 + 0.06 * (t / self.dur) + 0.05 * flash
        return g.im, (640, 360, zoom)
