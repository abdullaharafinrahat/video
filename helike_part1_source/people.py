from lib import *

SKINS = [(226, 170, 124), (208, 150, 106), (190, 128, 88), (236, 188, 148)]
TUNICS = [(238, 228, 206), (196, 84, 60), (60, 104, 150), (224, 188, 96), (112, 140, 92), (152, 78, 120), (242, 236, 224)]
HAIRS = [(40, 28, 24), (66, 44, 30), (28, 24, 26), (92, 66, 40), (120, 118, 118)]
OL = (58, 38, 30)
_cache = {}


def mk_style(seed, female=None, beard=None, carry=None, cloak=True):
    r = random.Random(seed)
    female = r.random() < 0.4 if female is None else female
    return dict(skin=r.choice(SKINS), tunic=r.choice(TUNICS), cloak=r.choice(TUNICS) if cloak and r.random() < 0.55 else None,
                hair=r.choice(HAIRS), female=female, beard=(r.random() < 0.55 and not female) if beard is None else beard,
                carry=carry, hem=r.choice([(190, 150, 70), (150, 60, 50), (60, 90, 130)]), hh=r.uniform(0.94, 1.06))


def pt(o, L, a):
    return (o[0] + L * math.sin(a), o[1] + L * math.cos(a))


def limb(S, p0, p1, p2, w, col):
    S.line([p0, p1, p2], OL, w + 2.4)
    S.line([p0, p1, p2], col, w)


def amphora(S, x, y, s, col=(190, 104, 60)):
    # y = bottom
    S.poly([(x - 3 * s, y - 36 * s), (x - 3.5 * s, y - 28 * s), (x + 3.5 * s, y - 28 * s), (x + 3 * s, y - 36 * s)], shade(col, 0.8))
    S.ell(x, y - 18 * s, 11 * s, 14 * s, col, OL, 0.8)
    S.rect(x - 4 * s, y - 4 * s, x + 4 * s, y + 1, shade(col, 0.8))
    S.ell(x, y - 38 * s, 5 * s, 2 * s, shade(col, 0.7), OL, 0.8)
    S.line([(x - 4 * s, y - 36 * s), (x - 15 * s, y - 28 * s), (x - 10 * s, y - 20 * s)], OL, 2.6 * s, False)
    S.line([(x + 4 * s, y - 36 * s), (x + 15 * s, y - 28 * s), (x + 10 * s, y - 20 * s)], OL, 2.6 * s, False)
    S.line([(x - 9 * s, y - 24 * s), (x + 9 * s, y - 24 * s)], shade(col, 0.6), 2 * s, False)
    S.line([(x - 10 * s, y - 15 * s), (x + 10 * s, y - 15 * s)], (236, 214, 170), 1.6 * s, False)


def draw_person(S, ox, oy, u, st, mode='walk', ph=0.0, panic_t=0.0):
    skin, tun = st['skin'], st['tunic']
    fem = st['female']
    ph = ph * 2 * math.pi
    lean = 0.0
    if mode == 'run':
        A, F, lean = 0.95, 1.2, 0.22
    elif mode == 'panic':
        A, F, lean = 0.8, 1.0, 0.18
    elif mode == 'stand':
        A, F = 0.0, 0.0
    else:
        A, F = 0.5, 0.8
    bob = abs(math.sin(ph)) * (3 if mode == 'walk' else 6 if mode != 'stand' else 0.6) * u
    if mode == 'stand':
        bob = math.sin(ph) * 0.6 * u
    hip = (ox + 0, oy - 86 * u * st['hh'] - bob)
    sh = pt(hip, 54 * u, math.pi + lean)
    sh = (sh[0], sh[1])
    leglen = 41 * u * st['hh']

    def leg(sign):
        a = A * math.sin(ph) * sign
        flex = F * max(0, math.cos(ph) * sign) if mode != 'stand' else 0
        k = pt(hip, leglen, a)
        f = pt(k, leglen, a - flex)
        return k, f, a

    legs = [leg(-1), leg(1)]
    # back leg first
    order = sorted(legs, key=lambda L: L[2])
    for k, f, a in order:
        col = shade(skin, 0.86 if (k, f, a) == order[0] else 1.0)
        limb(S, hip, k, f, 11 * u, col)
        # sandal
        S.ell(f[0] + 4 * u, f[1] + 1 * u, 9 * u, 3.5 * u, (112, 72, 44), OL, 0.7)
    # back arm
    def arm(sign, front):
        if mode == 'panic':
            a1 = 2.5 + 0.35 * math.sin(ph * 1.0 + (0 if sign > 0 else 2))
            a2 = a1 + 0.25
        elif mode == 'run':
            a1 = -sign * 0.9 * math.sin(ph)
            a2 = a1 + 1.4
        else:
            a1 = -sign * 0.42 * math.sin(ph) * (1 if mode == 'walk' else 0.3)
            a2 = a1 + 0.35 + 0.2 * max(0, math.sin(ph) * sign)
        e = pt(sh, 33 * u, a1)
        h = pt(e, 31 * u, a2)
        return sh, e, h
    car = st.get('carry')
    bk = arm(-1, False)
    limb(S, bk[0], bk[1], bk[2], 9 * u, shade(skin, 0.84))
    S.ell(bk[2][0], bk[2][1], 5 * u, 5 * u, shade(skin, 0.84), OL, 0.6)
    # torso / tunic
    top_w = 17 * u
    nx, ny = math.cos(lean), math.sin(lean)
    shL = (sh[0] - top_w * 0.75, sh[1] + 4 * u)
    shR = (sh[0] + top_w * 0.75, sh[1] + 4 * u)
    hemy = oy - (14 * u if fem else 46 * u * st['hh']) - bob * 0.3
    sw = math.sin(ph) * 6 * u if mode != 'stand' else 0
    flare = 22 * u if fem else 20 * u
    body = [shL, shR, (hip[0] + flare * 0.8 + sw, hemy), (hip[0] - flare * 0.8 + sw, hemy)]
    S.gpoly(body, shade(tun, 1.08), shade(tun, 0.82))
    S.poly(body + [body[0]], None, OL, 0.9) if False else S.line(body + [body[0]], OL, 1.1, False)
    # hem band
    S.line([(hip[0] - flare * 0.8 + sw, hemy - 2 * u), (hip[0] + flare * 0.8 + sw, hemy - 2 * u)], st['hem'], 3 * u, False)
    # belt
    S.line([((hip[0] + sh[0]) / 2 - 14 * u, hip[1] - 14 * u), ((hip[0] + sh[0]) / 2 + 14 * u, hip[1] - 14 * u)],
           shade(tun, 0.6), 3 * u, False)
    if st['cloak']:
        c = st['cloak']
        S.poly([shL, (shL[0] + 10 * u, shL[1] - 5 * u), shR, (hip[0] + 15 * u + sw, hip[1] + 26 * u),
                (hip[0] - 6 * u + sw, hip[1] + 30 * u)], shade(c, 0.95))
        S.line([shL, (hip[0] - 6 * u + sw, hip[1] + 30 * u)], OL, 1.0, False)
    # head
    hd = pt(sh, 20 * u, math.pi + lean * 0.5)
    S.rect(hd[0] - 4 * u, hd[1] + 6 * u, hd[0] + 4 * u, sh[1], shade(skin, 0.86))
    if st['hair'] and not fem:
        S.ell(hd[0] - 2 * u, hd[1] - 2 * u, 15.5 * u, 15 * u, st['hair'])
    if fem:
        S.ell(hd[0] - 6 * u, hd[1] + 3 * u, 11 * u, 14 * u, st['hair'])
        S.ell(hd[0] - 12 * u, hd[1] - 6 * u, 7 * u, 7 * u, st['hair'])
    S.ell(hd[0] + 2 * u, hd[1] + 1 * u, 13.5 * u, 14.5 * u, skin, OL, 0.8)
    if st['hair']:
        S.poly([(hd[0] - 12 * u, hd[1] - 5 * u), (hd[0] + 2 * u, hd[1] - 16 * u), (hd[0] + 14 * u, hd[1] - 6 * u),
                (hd[0] + 6 * u, hd[1] - 9 * u), (hd[0] - 4 * u, hd[1] - 7 * u)], st['hair'])
    S.poly([(hd[0] + 14 * u, hd[1] + 1 * u), (hd[0] + 19 * u, hd[1] + 5 * u), (hd[0] + 14 * u, hd[1] + 6 * u)], shade(skin, 0.92))
    S.ell(hd[0] + 8 * u, hd[1] - 1.5 * u, 1.9 * u, 1.9 * u, (30, 22, 20))
    S.line([(hd[0] + 5 * u, hd[1] - 5 * u), (hd[0] + 11 * u, hd[1] - 5.5 * u)], OL, 1.3 * u, False)
    if mode in ('panic',):
        S.ell(hd[0] + 9 * u, hd[1] + 9 * u, 3.5 * u, 4 * u, (90, 30, 30))
    else:
        S.line([(hd[0] + 7 * u, hd[1] + 9 * u), (hd[0] + 12 * u, hd[1] + 8.4 * u)], (150, 70, 60), 1.2 * u, False)
    if st['beard']:
        S.poly([(hd[0] - 6 * u, hd[1] + 6 * u), (hd[0] + 13 * u, hd[1] + 5 * u), (hd[0] + 11 * u, hd[1] + 15 * u),
                (hd[0] + 2 * u, hd[1] + 22 * u), (hd[0] - 6 * u, hd[1] + 14 * u)], st['hair'])
    if fem:
        S.line([(hd[0] - 12 * u, hd[1] - 7 * u), (hd[0] + 10 * u, hd[1] - 10 * u)], (230, 190, 90), 2 * u, False)
    # front arm
    fr = arm(1, True)
    if car == 'amphora':
        e = pt(sh, 24 * u, 1.9)
        h = (hd[0] + 22 * u, hd[1] + 22 * u)
        limb(S, fr[0], e, h, 9 * u, skin)
        amphora(S, h[0] + 2 * u, h[1] + 14 * u, u * 1.35)
        limb(S, fr[0], e, h, 9 * u, skin)
        S.ell(h[0], h[1], 5 * u, 5 * u, skin, OL, 0.6)
    else:
        limb(S, fr[0], fr[1], fr[2], 9 * u, skin)
        S.ell(fr[2][0], fr[2][1], 5 * u, 5 * u, skin, OL, 0.6)


def sprite(style_seed, mode='walk', ph=0.0, h=230, female=None, carry=None, beard=None, flip=False, cloak=True):
    key = (style_seed, mode, round(ph, 3), h, female, carry, beard, flip, cloak)
    if key in _cache:
        return _cache[key]
    st = mk_style(style_seed, female, beard, carry, cloak)
    u = h / 200.0
    S = SS(int(h * 0.8), int(h * 1.12), 3)
    draw_person(S, S.w / 2, S.h - 6, u, st, mode, ph)
    im = S.get()
    if flip:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    _cache[key] = im
    return im


def walk_sprite(seed, t, speed=1.0, h=230, offset=0.0, mode='walk', **kw):
    n = 16
    ph = ((t * speed + offset) % 1.0)
    ph = round(ph * n) % n / n
    return sprite(seed, mode, ph, h, **kw)


def silhouette(im, col, a=1.0):
    al = im.getchannel('A').point(lambda v: int(v * a))
    out = Image.new('RGBA', im.size, col + (0,))
    out.putalpha(al)
    return out
