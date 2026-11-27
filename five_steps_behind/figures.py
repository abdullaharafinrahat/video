"""
Character rigs for FIVE STEPS BEHIND.

A — tall, slender; long charcoal coat, rust scarf whose tails ride the wind,
    unruly dark hair.  Vertical, flowing silhouette.
B — a head shorter, broad-shouldered; short quilted olive jacket with a high
    collar, cropped ash hair, a satchel strap crossing his back.  Compact,
    planted silhouette.  His bare hands are the storytelling instrument.

All drawing is in local units: 1.0 == the character's height, feet at (0,0),
y grows downward (cairo).  Callers place/scale/rotate with the cairo matrix.
"""
import math

import cairo
import numpy as np

from core import cr_path, fill_shape, ribbon, vgrad, mix

# ---------------------------------------------------------------- palettes
A_COAT = (0.17, 0.16, 0.19)
A_COAT_HI = (0.25, 0.23, 0.26)
A_SCARF = (0.42, 0.165, 0.105)
A_SCARF_D = (0.33, 0.12, 0.08)
A_HAIR = (0.075, 0.065, 0.075)
A_SKIN = (0.40, 0.27, 0.22)
A_TROUSER = (0.11, 0.11, 0.13)
BOOT = (0.09, 0.075, 0.065)

B_JACKET = (0.21, 0.24, 0.19)
B_JACKET_HI = (0.29, 0.32, 0.25)
B_JACKET_D = (0.15, 0.17, 0.14)
B_HAIR = (0.37, 0.33, 0.28)
B_HAIR_D = (0.25, 0.22, 0.19)
B_SKIN = (0.42, 0.29, 0.24)
B_TROUSER = (0.15, 0.145, 0.13)
B_STRAP = (0.30, 0.21, 0.14)

TAU = 2 * math.pi


def _shade(c, k):
    return tuple(min(1.0, x * k) for x in c)


# ------------------------------------------------------------------ hands
def draw_hand(ctx, curl=0.0, tremble=0.0, mirror=1.0, skin=B_SKIN, t=0.0, scale=0.105):
    """Hanging hand seen from behind. Wrist at origin, fingers point +y.
    curl 0 = relaxed open, 1 = fist."""
    ctx.save()
    ctx.scale(mirror * scale, scale)   # local hand units: hand length = 1
    ctx.rotate(tremble)
    sk = skin
    skd = _shade(skin, 0.72)
    # palm / back of hand
    palm_len = 0.50 - 0.06 * curl
    palm = [(-0.20, 0.02), (0.20, 0.0), (0.27, 0.22), (0.25, palm_len), (0.0, palm_len + 0.04),
            (-0.25, palm_len - 0.01), (-0.27, 0.22)]
    # fingers first (they are hidden behind the knuckles when curled)
    fx = [-0.175, -0.06, 0.06, 0.172]
    flen = [0.40, 0.46, 0.44, 0.34]
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    for i in range(4):
        x, y = fx[i] * (1 - 0.15 * curl), palm_len - 0.02
        ang = 0.0
        segs = [0.45, 0.32, 0.23]
        jcurl = [0.95, 1.35, 0.9]
        micro = 0.08 * math.sin(t * 9.0 + i * 1.7) * (0.3 + 0.7 * abs(tremble) * 20)
        pts = [(x, y)]
        for j in range(3):
            ang += (curl * jcurl[j] + 0.12 + micro * (j == 0))
            if ang > 1.75:
                break
            L = flen[i] * segs[j]
            x += fx[i] * 0.10 * (1 - curl)
            y += math.cos(ang) * L
            pts.append((x, y))
        if len(pts) > 1:
            wd = 0.125 - 0.012 * abs(i - 1.5)
            ribbon(ctx, pts, wd, wd * 0.72, skd)
            for (px_, py_) in pts[-1:]:
                ctx.arc(px_, py_, wd * 0.36, 0, TAU)
                ctx.set_source_rgb(*skd)
                ctx.fill()
    # thumb (mostly hidden, toward the body side)
    th_ang = 0.5 + 0.7 * curl
    tx0, ty0 = -0.24, 0.22
    tx1 = tx0 - 0.08 + 0.12 * curl
    ty1 = ty0 + math.cos(th_ang) * 0.30
    ctx.set_line_width(0.13)
    ctx.set_source_rgb(*skd)
    ctx.move_to(tx0, ty0)
    ctx.line_to(tx1, ty1)
    ctx.stroke()
    g = cairo.LinearGradient(0, 0, 0, palm_len)
    g.add_color_stop_rgb(0, *sk)
    g.add_color_stop_rgb(1, *_shade(sk, 0.9))
    fill_shape(ctx, palm, sk, grad=g)
    # knuckle bumps when curled
    if curl > 0.3:
        ctx.set_source_rgba(*_shade(sk, 1.12), (curl - 0.3) * 0.8)
        for x in fx:
            ctx.arc(x * (1 - 0.15 * curl), palm_len - 0.01, 0.06, 0, TAU)
            ctx.fill()
    ctx.restore()


# ----------------------------------------------------------- back views
def draw_A_back(ctx, t, g, lean=0.0, arm_open=0.0, detail=1.0):
    """A seen from behind (wind blowing toward camera, slightly from screen right)."""
    sw = 0.004 * math.sin(t * 1.1)
    # legs + boots
    for side in (-1, 1):
        x0 = side * 0.047
        fl = 0.004 * math.sin(t * 7.3 + side) * g
        leg = [(x0 - 0.034, -0.38), (x0 + 0.031, -0.38), (x0 + 0.026 + fl, -0.075), (x0 - 0.027 + fl, -0.075)]
        fill_shape(ctx, leg, A_TROUSER)
        boot = [(x0 - 0.031, -0.09), (x0 + 0.029, -0.09), (x0 + 0.033, -0.015), (x0 + 0.025, 0.0),
                (x0 - 0.031, 0.0), (x0 - 0.036, -0.016)]
        fill_shape(ctx, boot, BOOT)
    # coat
    flare = 0.008 + 0.014 * g * (0.55 + 0.45 * math.sin(t * 3.1))
    hem = []
    for i in range(11):
        u = i / 10.0
        x = -0.152 - flare + u * (0.304 + 2 * flare)
        y = -0.285 + 0.011 * math.sin(t * 5.3 + u * 7.0) * g - 0.006 * math.sin(u * math.pi)
        hem.append((x + sw, y))
    left = [(-0.052, -0.874), (-0.104, -0.85), (-0.127, -0.815), (-0.131, -0.74), (-0.123, -0.62),
            (-0.127, -0.5), (-0.140 - flare * 0.5, -0.40)]
    right = [(-x + 0.003 * math.sin(t * 4 + y * 9) * g, y) for (x, y) in left][::-1]
    coat = left + hem + right
    fill_shape(ctx, coat, A_COAT, grad=vgrad(-0.87, -0.29, A_COAT_HI, A_COAT))
    # back seam / vent opening in the wind
    vo = 0.004 + 0.006 * g
    ctx.set_source_rgba(0.06, 0.06, 0.07, 0.9)
    cr_path(ctx, [(sw - vo, hem[5][1] + 0.002), (sw, -0.43), (sw + vo, hem[5][1] + 0.002)], True)
    ctx.fill()
    ctx.set_source_rgba(0.1, 0.1, 0.12, 0.5)
    ctx.set_line_width(0.004)
    ctx.move_to(0, -0.85)
    ctx.line_to(sw * 0.5, -0.43)
    ctx.stroke()
    # arms
    for side in (-1, 1):
        sh = (side * 0.110, -0.805)
        el = (side * (0.128 + arm_open * 0.01), -0.655)
        wr = (side * (0.133 + arm_open * 0.035), -0.515)
        ribbon(ctx, [sh, el, wr], 0.052, 0.040, _shade(A_COAT, 0.92))
        ctx.save()
        ctx.translate(wr[0], wr[1] - 0.004)
        draw_hand(ctx, curl=0.35, mirror=side, skin=A_SKIN, t=t, scale=0.085)
        ctx.restore()
    # scarf tails (behind collar, flying)
    gg = 0.45 + 0.55 * g
    c1 = []
    for i in range(9):
        s = i / 8.0
        x = 0.022 - 0.02 * s - 0.06 * s * gg * (0.7 + 0.3 * math.sin(t * 4.3)) + 0.014 * math.sin(t * 6.1 - s * 5) * s
        y = -0.862 + 0.26 * s * (1 - 0.3 * gg)
        c1.append((x, y))
    ribbon(ctx, c1, 0.042, 0.032, A_SCARF_D)
    c2 = []
    for i in range(9):
        s = i / 8.0
        x = -0.04 - 0.13 * s * gg
        y = -0.866 + 0.07 * s + 0.024 * math.sin(t * 7.2 - s * 6.5) * s
        c2.append((x, y))
    ribbon(ctx, c2, 0.036, 0.020, A_SCARF)
    # collar
    fill_shape(ctx, [(-0.06, -0.856), (-0.058, -0.886), (-0.04, -0.905), (0.04, -0.905), (0.058, -0.886),
                     (0.06, -0.856)], _shade(A_COAT_HI, 0.95))
    # scarf band
    fill_shape(ctx, [(-0.064, -0.878), (0.0, -0.885), (0.064, -0.878), (0.068, -0.851), (0.0, -0.845),
                     (-0.068, -0.851)], A_SCARF)
    # neck, ears, head
    fill_shape(ctx, [(-0.021, -0.88), (0.021, -0.88), (0.02, -0.93), (-0.02, -0.93)], _shade(A_SKIN, 0.8))
    for side in (-1, 1):
        ctx.save()
        ctx.translate(side * 0.049, -0.93)
        ctx.scale(0.011, 0.02)
        ctx.arc(0, 0, 1, 0, TAU)
        ctx.restore()
        ctx.set_source_rgb(*A_SKIN)
        ctx.fill()
    # hair: unruly mass, lock tips pushed by wind
    hair = []
    n = 34
    for i in range(n):
        a = TAU * i / n
        cx, cy = 0.0, -0.937
        rx, ry = 0.056, 0.066
        lock = 1.0 + 0.10 * abs(math.sin(a * 6.5 + 0.7)) ** 3
        x = cx + math.sin(a) * rx * lock
        y = cy - math.cos(a) * ry * lock
        if math.cos(a) < 0:   # lower half: falls to the nape
            y += (-math.cos(a)) * 0.014
            x *= 0.94 + 0.06 * math.cos(a) ** 2
        wob = 0.012 * g * math.sin(t * 5.0 + a * 3.0) * (abs(math.sin(a)) + 0.3)
        hair.append((x - wob - 0.004 * g, y - abs(wob) * 0.6))
    fill_shape(ctx, hair, A_HAIR)
    if detail > 0.5:
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        for k in range(9):
            a0 = -1.6 + k * 0.4
            bx = math.sin(a0) * 0.05
            by = -0.937 - math.cos(a0) * 0.06
            ph = t * (5.5 + k * 0.3) + k
            pts = [(bx, by)]
            for j in range(1, 4):
                s = j / 3.0
                pts.append((bx + math.sin(a0) * 0.02 * s - 0.012 * g * s + 0.006 * math.sin(ph - s * 3) * s,
                            by - 0.018 * s * (0.6 + 0.4 * math.sin(ph * 0.7)) * g))
            ctx.set_source_rgb(*A_HAIR)
            ctx.set_line_width(0.004)
            cr_path(ctx, pts)
            ctx.stroke()


def draw_B_back(ctx, t, g, curl_r=0.15, curl_l=0.2, tremble=0.0, shoulder_rise=0.0, detail=1.0,
                draw_right_hand=True):
    sr = shoulder_rise
    for side in (-1, 1):
        x0 = side * 0.055
        leg = [(x0 - 0.038, -0.48), (x0 + 0.036, -0.48), (x0 + 0.031, -0.085), (x0 - 0.032, -0.085)]
        fill_shape(ctx, leg, B_TROUSER)
        boot = [(x0 - 0.037, -0.10), (x0 + 0.035, -0.10), (x0 + 0.04, -0.02), (x0 + 0.03, 0.0),
                (x0 - 0.037, 0.0), (x0 - 0.043, -0.02)]
        fill_shape(ctx, boot, _shade(BOOT, 1.25))
        ctx.set_source_rgba(0.05, 0.04, 0.03, 0.8)
        ctx.rectangle(x0 - 0.04, -0.012, 0.08, 0.012)
        ctx.fill()
    # jacket
    pf = 0.004 * g * math.sin(t * 4.0)
    jacket = [(-0.06, -0.872 - sr), (-0.118, -0.848 - sr), (-0.150, -0.808 - sr), (-0.156, -0.74), (-0.150, -0.62),
              (-0.146 - pf, -0.52), (-0.140, -0.463), (0.0, -0.455), (0.140, -0.463), (0.146 + pf, -0.52),
              (0.150, -0.62), (0.156, -0.74), (0.150, -0.808 - sr), (0.118, -0.848 - sr), (0.06, -0.872 - sr)]
    fill_shape(ctx, jacket, B_JACKET, grad=vgrad(-0.87, -0.46, B_JACKET_HI, B_JACKET_D))
    # quilting
    ctx.set_line_width(0.0035)
    ctx.set_source_rgba(*B_JACKET_D, 0.85)
    for yq in (-0.75, -0.66, -0.57):
        ctx.move_to(-0.148, yq)
        ctx.curve_to(-0.05, yq + 0.012, 0.05, yq + 0.012, 0.148, yq)
        ctx.stroke()
    # waistband
    fill_shape(ctx, [(-0.141, -0.49), (0.141, -0.49), (0.140, -0.463), (0.0, -0.455), (-0.140, -0.463)], B_JACKET_D)
    # strap across the back
    ribbon(ctx, [(0.105, -0.83 - sr), (0.0, -0.69), (-0.135, -0.505)], 0.024, 0.024, B_STRAP)
    # arms
    for side in (-1, 1):
        sh = (side * 0.138, -0.80 - sr)
        el = (side * 0.158, -0.65)
        wr = (side * 0.160, -0.505)
        ribbon(ctx, [sh, el, wr], 0.066, 0.052, _shade(B_JACKET, 0.95))
        fill_shape(ctx, [(wr[0] - 0.027, wr[1] - 0.012), (wr[0] + 0.027, wr[1] - 0.012),
                         (wr[0] + 0.025, wr[1] + 0.008), (wr[0] - 0.025, wr[1] + 0.008)], B_JACKET_D)
        if side == 1 and not draw_right_hand:
            continue
        ctx.save()
        ctx.translate(wr[0], wr[1] + 0.004)
        draw_hand(ctx, curl=curl_r if side == 1 else curl_l, tremble=tremble if side == 1 else 0.0,
                  mirror=side, skin=B_SKIN, t=t, scale=0.098)
        ctx.restore()
    # high collar
    fill_shape(ctx, [(-0.068, -0.858 - sr), (-0.066, -0.9 - sr), (0.0, -0.906 - sr), (0.066, -0.9 - sr),
                     (0.068, -0.858 - sr)], B_JACKET_HI)
    # neck + ears
    fill_shape(ctx, [(-0.022, -0.89 - sr), (0.022, -0.89 - sr), (0.021, -0.93), (-0.021, -0.93)], _shade(B_SKIN, 0.8))
    for side in (-1, 1):
        ctx.save()
        ctx.translate(side * 0.053, -0.928)
        ctx.scale(0.012, 0.021)
        ctx.arc(0, 0, 1, 0, TAU)
        ctx.restore()
        ctx.set_source_rgb(*B_SKIN)
        ctx.fill()
    # head + cropped hair
    fill_shape(ctx, [(0.0, -1.0), (0.05, -0.985), (0.056, -0.94), (0.05, -0.905), (0.03, -0.893), (0.0, -0.89),
                     (-0.03, -0.893), (-0.05, -0.905), (-0.056, -0.94), (-0.05, -0.985)], B_HAIR,
               grad=vgrad(-1.0, -0.89, B_HAIR, B_HAIR_D))
    # crown tufts
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for k in range(11):
        a = -1.2 + k * 0.24
        bx, by = math.sin(a) * 0.048, -0.94 - math.cos(a) * 0.056
        w = 0.004 * g * math.sin(t * 6.5 + k * 1.3)
        ctx.set_source_rgb(*B_HAIR)
        ctx.set_line_width(0.010)
        ctx.move_to(bx, by + 0.006)
        ctx.line_to(bx + math.sin(a) * 0.006 - 0.003 * g + w, by - 0.004 - 0.002 * g)
        ctx.stroke()


# ------------------------------------------------------------ side view
def draw_side_figure(ctx, who, t, g, knee=0.0, arm_lift=0.0, flight=0.0, hand_curl=0.2, detail=1.0):
    """Profile facing +x. who in ('A','B'). flight 0..1 lifts coat/scarf/arms as air rushes."""
    isA = who == "A"
    coat = A_COAT if isA else B_JACKET
    coat_hi = A_COAT_HI if isA else B_JACKET_HI
    trou = A_TROUSER if isA else B_TROUSER
    skin = A_SKIN if isA else B_SKIN
    hip_y = -0.48 + 0.04 * knee
    knee_x = 0.012 + 0.07 * knee
    knee_y = -0.255 + 0.02 * knee
    # legs (back leg darker)
    for k, (dx, shade) in enumerate(((-0.035, 0.75), (0.0, 1.0))):
        hip = (dx - 0.005, hip_y)
        kn = (dx + knee_x + flight * 0.02 * (k - 0.5), knee_y + flight * 0.04)
        an = (dx + 0.0 - flight * 0.05 * (1 - k), -0.06 + flight * 0.05)
        ribbon(ctx, [hip, kn, an], 0.075 if not isA else 0.066, 0.052, _shade(trou, shade))
        bx, by = an
        boot = [(bx - 0.035, by - 0.03), (bx + 0.025, by - 0.03), (bx + 0.035, by + 0.02), (bx + 0.085, by + 0.035),
                (bx + 0.09, by + 0.06), (bx - 0.04, by + 0.06), (bx - 0.045, by + 0.03)]
        fill_shape(ctx, boot, _shade(BOOT if isA else _shade(BOOT, 1.25), shade))
    # torso / coat
    if isA:
        hem_back_y = -0.31 - 0.18 * flight
        fl = 0.03 * g * (0.6 + 0.4 * math.sin(t * 4.0)) + 0.06 * flight
        hem = [(0.085, -0.30 - 0.05 * flight + 0.012 * knee)]
        for i in range(1, 7):
            u = i / 6.0
            hem.append((0.085 - u * (0.17 + fl), mix(-0.30, hem_back_y, u) + 0.012 * math.sin(t * 6 + u * 6) * g))
        body = [(0.035, -0.865), (0.065, -0.80), (0.07, -0.66), (0.066, -0.5)] + hem + \
               [(-0.075 - fl * 0.4, -0.45), (-0.062, -0.62), (-0.058, -0.78), (-0.04, -0.85)]
    else:
        body = [(0.035, -0.87), (0.075, -0.80), (0.085, -0.66), (0.08, -0.47), (-0.075, -0.465),
                (-0.082, -0.62), (-0.072, -0.79), (-0.045, -0.86)]
    fill_shape(ctx, body, coat, grad=vgrad(-0.87, -0.3, coat_hi, coat))
    if not isA:
        ribbon(ctx, [(0.03, -0.84), (-0.02, -0.66), (-0.075, -0.5)], 0.02, 0.02, B_STRAP)
    # head
    hx, hy = 0.012, -0.93
    ctx.save()
    ctx.translate(hx, hy)
    ctx.scale(0.058, 0.066)
    ctx.arc(0, 0, 1, 0, TAU)
    ctx.restore()
    ctx.set_source_rgb(*skin)
    ctx.fill()
    fill_shape(ctx, [(hx + 0.05, hy - 0.01), (hx + 0.075, hy + 0.012), (hx + 0.052, hy + 0.025)], skin)
    fill_shape(ctx, [(hx - 0.02, hy + 0.04), (hx + 0.03, hy + 0.05), (hx + 0.02, hy + 0.09), (hx - 0.025, hy + 0.085)],
               _shade(skin, 0.8))
    if isA:
        gg = 0.5 + 0.5 * g + flight
        hair = [(hx + 0.05, hy - 0.045), (hx + 0.02, hy - 0.072), (hx - 0.03, hy - 0.07),
                (hx - 0.07 - 0.02 * gg, hy - 0.05 + 0.006 * math.sin(t * 6)),
                (hx - 0.095 - 0.03 * gg, hy - 0.02 + 0.01 * math.sin(t * 7)),
                (hx - 0.07 - 0.015 * gg, hy + 0.0), (hx - 0.08 - 0.02 * gg, hy + 0.03 + 0.008 * math.sin(t * 5)),
                (hx - 0.045, hy + 0.045), (hx - 0.02, hy + 0.0), (hx + 0.02, hy - 0.02)]
        fill_shape(ctx, hair, A_HAIR)
    else:
        hair = [(hx + 0.05, hy - 0.04), (hx + 0.02, hy - 0.07), (hx - 0.035, hy - 0.066), (hx - 0.062, hy - 0.03),
                (hx - 0.058, hy + 0.035), (hx - 0.03, hy + 0.045), (hx - 0.015, hy), (hx + 0.025, hy - 0.025)]
        fill_shape(ctx, hair, B_HAIR)
    # scarf
    if isA:
        fill_shape(ctx, [(-0.045, -0.875), (0.045, -0.88), (0.05, -0.84), (-0.05, -0.835)], A_SCARF)
        gg = 0.5 + 0.5 * g
        c = []
        for i in range(10):
            s = i / 9.0
            ang = mix(1.9, 3.05, gg) + flight * (-1.25) * s
            x = -0.03 + math.sin(ang) * 0.30 * s * 0.6
            y = -0.85 - math.cos(ang) * 0.30 * s * 0.6 + 0.03 * math.sin(t * 7.5 - s * 7) * s
            c.append((x, y))
        ribbon(ctx, c, 0.04, 0.028, A_SCARF_D)
    # arm (near side)
    sh = (0.0, -0.80)
    a = 0.06 + arm_lift
    el = (sh[0] + math.sin(a) * 0.15, sh[1] + math.cos(a) * 0.15)
    a2 = a + 0.08 + arm_lift * 0.3
    wr = (el[0] + math.sin(a2) * 0.14, el[1] + math.cos(a2) * 0.14)
    ribbon(ctx, [sh, el, wr], 0.058 if isA else 0.07, 0.045, _shade(coat, 0.9))
    ctx.save()
    ctx.translate(*wr)
    ctx.rotate(-a2)
    draw_hand(ctx, curl=hand_curl, mirror=1, skin=skin, t=t, scale=0.09)
    ctx.restore()


# ------------------------------------------------------------- A profile
def draw_A_profile(ctx, t, g, eye_close=0.0, detail=1.0):
    """Close profile of A's head & shoulders facing +x. Unit = head height (crown->chin).
    Origin at the eye."""
    ex, ey = 0.0, 0.0
    sk = A_SKIN
    # shoulders / coat / scarf (behind the neck)
    fill_shape(ctx, [(-0.80, 1.500), (-0.76, 0.86), (-0.52, 0.70), (-0.2, 0.66), (0.10, 0.71), (0.26, 0.88),
                     (0.32, 1.500)], A_COAT, grad=vgrad(0.65, 1.5, A_COAT_HI, A_COAT))
    # neck
    fill_shape(ctx, [(-0.36, 0.22), (-0.02, 0.38), (0.04, 0.520), (0.02, 0.850), (-0.38, 0.850), (-0.41, 0.500)],
               _shade(sk, 0.6))
    # scarf wrap: two loose turns of wool, folds catching the light
    sw = 0.008 * math.sin(t * 3.0) * g
    fill_shape(ctx, [(-0.50, 0.50), (-0.30, 0.47), (-0.1, 0.475), (0.05, 0.49 + sw), (0.13, 0.56), (0.12, 0.70),
                     (-0.25, 0.74), (-0.58, 0.70)], A_SCARF_D)
    fill_shape(ctx, [(-0.47, 0.42), (-0.30, 0.40), (-0.12, 0.41 + sw), (0.03, 0.43), (0.10, 0.48), (0.06, 0.56),
                     (-0.15, 0.58), (-0.48, 0.56)], A_SCARF, grad=vgrad(0.40, 0.58, _shade(A_SCARF, 1.08), A_SCARF_D))
    ctx.set_source_rgba(*_shade(A_SCARF_D, 0.8), 0.9)
    ctx.set_line_width(0.010)
    for (y0, y1) in ((0.47, 0.50), (0.60, 0.63), (0.66, 0.68)):
        ctx.move_to(-0.42, y0)
        ctx.curve_to(-0.25, y0 - 0.02, -0.05, y1 - 0.01, 0.10, y1)
        ctx.stroke()
    # coat collar (turned up at back)
    fill_shape(ctx, [(-0.70, 0.84), (-0.62, 0.52), (-0.48, 0.48), (-0.40, 0.74)], A_COAT_HI)
    # face silhouette
    face = [(-0.24, 0.22), (-0.20, 0.31), (-0.08, 0.385), (0.06, 0.405), (0.15, 0.385), (0.205, 0.33), (0.215, 0.285),
            (0.195, 0.255),  # chin hollow
            (0.215, 0.225), (0.208, 0.200), (0.185, 0.188),   # lower lip -> mouth corner
            (0.205, 0.17), (0.212, 0.145),  # upper lip
            (0.19, 0.115), (0.205, 0.10),   # philtrum -> subnasale
            (0.255, 0.085), (0.262, 0.06), (0.235, -0.01), (0.19, -0.075),  # nose
            (0.185, -0.105), (0.198, -0.14), (0.19, -0.2), (0.15, -0.33),  # brow, forehead
            (0.05, -0.47), (-0.15, -0.52), (-0.38, -0.45), (-0.5, -0.25), (-0.50, 0.0), (-0.40, 0.18), (-0.28, 0.16)]
    g_face = cairo.LinearGradient(-0.4, 0, 0.26, 0)
    g_face.add_color_stop_rgb(0, *_shade(sk, 0.72))
    g_face.add_color_stop_rgb(0.7, *sk)
    g_face.add_color_stop_rgb(1, *_shade(sk, 1.15))
    fill_shape(ctx, face, sk, grad=g_face)
    # jaw line shadow
    ctx.set_source_rgba(*_shade(sk, 0.62), 0.55)
    cr_path(ctx, [(-0.23, 0.12), (-0.14, 0.28), (0.0, 0.35), (0.13, 0.37), (0.04, 0.40), (-0.1, 0.38), (-0.21, 0.3)],
            True)
    ctx.fill()
    # cheek / eye socket soft shadow
    rg = cairo.RadialGradient(0.04, 0.02, 0.0, 0.04, 0.02, 0.12)
    rg.add_color_stop_rgba(0, *_shade(sk, 0.7), 0.5)
    rg.add_color_stop_rgba(1, *_shade(sk, 0.7), 0.0)
    ctx.set_source(rg)
    ctx.arc(0.04, 0.02, 0.12, 0, TAU)
    ctx.fill()
    # mouth line
    ctx.set_source_rgba(0.22, 0.12, 0.10, 0.85)
    ctx.set_line_width(0.007)
    ctx.move_to(0.205, 0.185)
    ctx.curve_to(0.19, 0.19, 0.175, 0.19, 0.165, 0.195)
    ctx.stroke()
    # nostril
    ctx.set_source_rgba(0.2, 0.11, 0.09, 0.7)
    ctx.save()
    ctx.translate(0.2, 0.072)
    ctx.scale(0.022, 0.011)
    ctx.arc(0, 0, 1, 0, TAU)
    ctx.restore()
    ctx.fill()
    # eye
    ec = eye_close
    ctx.save()
    ctx.translate(0.12, -0.035)
    # eye white/iris wedge (profile)
    upper_y = mix(-0.022, 0.012, ec)
    ctx.move_to(-0.04, 0.0)
    ctx.curve_to(-0.01, upper_y - 0.004, 0.03, upper_y, 0.055, 0.002 + ec * 0.006)
    ctx.curve_to(0.03, 0.016, -0.01, 0.016, -0.04, 0.0)
    ctx.close_path()
    ctx.set_source_rgb(0.62, 0.52, 0.48)
    ctx.fill_preserve()
    ctx.clip()
    ctx.set_source_rgb(0.10, 0.07, 0.06)
    ctx.arc(0.035, 0.002, 0.018, 0, TAU)
    ctx.fill()
    ctx.set_source_rgba(1, 0.9, 0.8, 0.7 * (1 - ec))
    ctx.arc(0.042, -0.004, 0.0035, 0, TAU)
    ctx.fill()
    ctx.reset_clip()
    # upper lid crease + lashes
    ctx.set_source_rgb(0.12, 0.07, 0.06)
    ctx.set_line_width(0.009)
    ctx.move_to(-0.04, 0.0)
    ctx.curve_to(-0.01, upper_y - 0.004, 0.03, upper_y, 0.058, 0.002 + ec * 0.008)
    ctx.stroke()
    ctx.set_line_width(0.006)
    for k in range(4):
        u = 0.45 + k * 0.17
        lx = mix(-0.03, 0.055, u)
        ly = mix(upper_y, 0.004, (u - 0.5) * 1.4) if ec < 0.5 else 0.008
        ctx.move_to(lx, ly)
        ctx.line_to(lx + 0.016, ly - 0.012 * (1 - ec) + 0.008 * ec)
        ctx.stroke()
    ctx.set_source_rgba(0.25, 0.15, 0.12, 0.6)
    ctx.set_line_width(0.006)
    ctx.move_to(-0.03, -0.045 + ec * 0.01)
    ctx.curve_to(0.0, -0.055 + ec * 0.012, 0.03, -0.05 + ec * 0.012, 0.05, -0.038 + ec * 0.01)
    ctx.stroke()
    ctx.restore()
    # eyebrow
    ctx.set_source_rgb(0.08, 0.06, 0.06)
    ribbon(ctx, [(0.06, -0.135), (0.11, -0.145 + ec * 0.004), (0.165, -0.13 + ec * 0.004)], 0.02, 0.012, (0.08, 0.06, 0.06))
    # ear (backlit: glows red-orange at the rim, done in comp; base here)
    ear = [(-0.24, -0.06), (-0.19, -0.10), (-0.155, -0.05), (-0.165, 0.06), (-0.19, 0.13), (-0.23, 0.11), (-0.255, 0.03)]
    fill_shape(ctx, ear, _shade(sk, 1.05))
    ctx.set_source_rgba(*_shade(sk, 0.6), 0.8)
    cr_path(ctx, [(-0.215, -0.04), (-0.18, -0.05), (-0.18, 0.03), (-0.205, 0.08)])
    ctx.set_line_width(0.012)
    ctx.stroke()
    # hair: mass + windswept locks streaming back (wind from +x)
    gg = 0.55 + 0.45 * g
    w1 = 0.03 * math.sin(t * 5.1) * gg
    w2 = 0.03 * math.sin(t * 6.3 + 1.0) * gg
    w3 = 0.025 * math.sin(t * 4.4 + 2.0) * gg
    mass = [(0.15, -0.355), (0.09, -0.50), (-0.12, -0.585), (-0.36, -0.56),
            (-0.60 - 0.05 * gg, -0.47 + w1), (-0.74 - 0.06 * gg, -0.34 + w1), (-0.58, -0.28),
            (-0.68 - 0.05 * gg, -0.14 + w2), (-0.53, -0.07), (-0.58 - 0.04 * gg, 0.08 + w3), (-0.46, 0.12),
            (-0.43, 0.27), (-0.34, 0.21), (-0.30, 0.02), (-0.22, -0.13), (-0.12, -0.10), (-0.09, 0.03),
            (-0.065, 0.03), (-0.06, -0.15), (0.02, -0.26), (0.11, -0.315)]
    fill_shape(ctx, mass, A_HAIR)
    if detail > 0.5:
        rng = np.random.RandomState(5)
        for k in range(40):
            u = rng.rand()
            ra = mix(-3.05, -1.25, u)
            rx = -0.2 + math.cos(ra) * 0.31
            ry = -0.06 + math.sin(ra) * 0.45
            length = 0.20 + 0.22 * rng.rand() * (1.2 - u * 0.5)
            ph = t * (4.0 + 2.5 * rng.rand()) + rng.rand() * 6
            pts = []
            for j in range(6):
                s_ = j / 5.0
                x = rx - length * s_ * (0.75 + 0.25 * gg)
                y = ry + length * s_ * (0.10 + 0.35 * (1 - u)) + 0.03 * math.sin(ph - s_ * 4) * s_ * gg
                pts.append((x, y))
            ribbon(ctx, pts, 0.028 + 0.02 * rng.rand(), 0.002, A_HAIR)
        # fringe tips falling over the forehead
        for k in range(5):
            ph = t * (5 + k) + k
            bx = 0.12 - k * 0.05
            ribbon(ctx, [(bx, -0.36), (bx + 0.02, -0.28), (bx - 0.01 + 0.015 * math.sin(ph) * g, -0.2 - 0.02 * k)],
                   0.035, 0.003, A_HAIR)
