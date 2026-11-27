"""
The seven shots of FIVE STEPS BEHIND.
Each shot: __init__ precomputes static paintings; frame(tl, tg, fi) -> (float image, grade dict).
tl = local seconds into the shot, tg = global seconds.
"""
import math

import cairo
import cv2
import numpy as np

import core
from core import (S, W, H, gust, jitter, ease, ease_io, ease_in, ease_out, mix, rgb, sstep, clamp01, new_surface,
                  surface_to_np, light_layer, blur_layer, blur, over_pm, over, fbm_tex, sample, cr_path, fill_shape,
                  SUN_COL, MIST, fbm1)
from figures import (draw_A_back, draw_B_back, draw_side_figure, draw_A_profile, draw_hand, B_JACKET, B_JACKET_D,
                     B_SKIN, B_JACKET_HI)
from world import (Backdrop, Ground, world_scene, A_POS, B_POS, A_HEIGHT, B_HEIGHT, project_feet, RIM, lit,
                   char_layer)

# ----------------------------------------------------------- colour script
GRADES = {
    1: dict(exposure=1.00, sat=1.00, lift=rgb(0.020, 0.016, 0.030), gain=rgb(1.00, 0.98, 0.95), gamma=1.0, bloom=0.55),
    2: dict(exposure=0.98, sat=0.97, lift=rgb(0.018, 0.017, 0.032), gain=rgb(0.99, 0.97, 0.95), gamma=1.0, bloom=0.5),
    3: dict(exposure=1.00, sat=1.00, lift=rgb(0.022, 0.016, 0.026), gain=rgb(1.00, 0.97, 0.93), gamma=1.0, bloom=0.5),
    4: dict(exposure=1.02, sat=1.04, lift=rgb(0.024, 0.016, 0.022), gain=rgb(1.00, 0.97, 0.92), gamma=1.0, bloom=0.6),
    5: dict(exposure=0.97, sat=0.90, lift=rgb(0.012, 0.016, 0.036), gain=rgb(0.98, 0.96, 0.95), gamma=1.04, bloom=0.45),
    6: dict(exposure=0.95, sat=0.84, lift=rgb(0.012, 0.018, 0.040), gain=rgb(0.96, 0.95, 0.96), gamma=1.05, bloom=0.4),
    7: dict(exposure=0.92, sat=0.72, lift=rgb(0.016, 0.022, 0.044), gain=rgb(0.92, 0.93, 0.96), gamma=1.07, bloom=0.35),
}

# ------------------------------------------------------------ performances
LEAN_START = 11.55          # A begins to shift his weight (global seconds)
LEAN_S5_END = 0.15          # lean (rad) reached at the cut into shot 6


def a_lean(tg):
    """Forward lean during shot 5 (rad)."""
    u = (tg - LEAN_START) / (13.0 - LEAN_START)
    return LEAN_S5_END * ease_in(u) ** 0.8 if u > 0 else 0.0


def A_back_draw(tg, lean=0.0, arm_open=0.0, detail=1.0):
    g = gust(tg)
    return lambda ctx: draw_A_back(ctx, tg, g, lean=lean, arm_open=arm_open, detail=detail)


def B_back_draw(tg, **kw):
    g = gust(tg)
    return lambda ctx: draw_B_back(ctx, tg, g, **kw)


def breath(tg, period=3.8, amp=1.0):
    return math.sin(tg * 2 * math.pi / period) * amp


# =================================================================== SHOT 1
class Shot1:
    """00:00-00:03  Extreme wide. The world first; two small figures at the end of the land."""
    T0, T1 = 0.0, 3.0

    def __init__(self):
        self.bd = Backdrop(-0.174, 1350 * S, 0.40 * H)
        self.ground = Ground(self.bd.view, n_near=3000, n_far=3000)

    def cam(self, tl):
        u = tl / 3.0
        e = 0.55 * u + 0.45 * ease_out(u)
        return (mix(9.0, 8.4, e), mix(7.5, 7.0, e), mix(-36.0, -32.5, e))

    def frame(self, tl, tg, fi):
        g = gust(tg)
        cam = self.cam(tl)
        img = self.bd.render(tg)
        chars = [
            dict(draw=A_back_draw(tg, detail=0.0), X=A_POS[0], Z=A_POS[1], height=A_HEIGHT, rim_w=1.3 * S),
            dict(draw=B_back_draw(tg, detail=0.0), X=B_POS[0], Z=B_POS[1], height=B_HEIGHT, rim_w=1.3 * S),
        ]
        img = world_scene(img, self.bd, self.ground, cam, tg, g, chars, ground_rim=2.0, walls=True)
        return img, GRADES[1]


# =================================================================== SHOT 2
class Shot2:
    """00:03-00:05  Over B's right shoulder. Between them: the sun, and five steps of grass."""
    T0, T1 = 3.0, 5.0

    def __init__(self):
        self.bd = Backdrop(-0.105, 1250 * S, 0.47 * H)
        self.ground = Ground(self.bd.view, n_near=6500, n_far=600, seed=8)

    def cam(self, tl):
        u = tl / 2.0
        return (B_POS[0] + 0.72 + 0.10 * ease_io(u), 1.62 + 0.006 * math.sin(tl * 1.7), B_POS[1] - 1.15)

    def frame(self, tl, tg, fi):
        g = gust(tg)
        cam = self.cam(tl)
        img = self.bd.render(tg)
        img = blur(img, 1.6 * S)
        chars = [
            dict(draw=A_back_draw(tg), X=A_POS[0], Z=A_POS[1], height=A_HEIGHT, rim_w=2.6 * S, rim_s=1.4),
            dict(draw=B_back_draw(tg, curl_r=0.2, detail=1.0), X=B_POS[0], Z=B_POS[1], height=B_HEIGHT,
                 blur=9 * S, rim_w=7 * S, rim_s=1.0),
        ]
        img = world_scene(img, self.bd, self.ground, cam, tg, g, chars, near_split=2.6, near_blur=6 * S,
                          ground_rim=2.5)
        return img, GRADES[2]


# =================================================================== SHOT 5
class Shot5:
    """00:10-00:13  Hip-height, beside B. His hand drifts into frame and will not keep still.
    Beyond it, A begins to lean."""
    T0, T1 = 10.0, 13.0

    def __init__(self):
        self.bd = Backdrop(-0.015, 1300 * S, 0.62 * H)
        self.ground = Ground(self.bd.view, n_near=6500, n_far=500, seed=9)

    def cam(self, tl):
        return (B_POS[0] + 0.55, 1.05 + 0.004 * math.sin(tl * 1.3), B_POS[1] - 0.45)

    def frame(self, tl, tg, fi):
        g = gust(tg)
        cam = self.cam(tl)
        img = self.bd.render(tg)
        img = blur(img, 1.2 * S)
        lean = a_lean(tg)
        arm_open = sstep(11.2, 12.8, tg) * 0.6
        chars = [
            dict(draw=A_back_draw(tg, lean=lean, arm_open=arm_open), X=A_POS[0], Z=A_POS[1], height=A_HEIGHT,
                 rim_w=2.8 * S, rim_s=1.45, rot=-lean * 0.45, sy=math.cos(lean * 1.3) * (1 + 0.012 * sstep(11.3, 12.0, tg))),
        ]
        img = world_scene(img, self.bd, self.ground, cam, tg, g, chars, near_split=1.6, near_blur=5 * S)
        sun = self.bd.sun_screen()
        # B's body: a dark out-of-focus mass at the left edge
        surf, ctx = new_surface()
        fill_shape(ctx, [(-0.3 * W, -0.1 * H), (0.035 * W, -0.1 * H), (0.06 * W, 0.3 * H), (0.075 * W, 0.62 * H),
                         (0.06 * W, 1.1 * H), (-0.3 * W, 1.1 * H)], B_JACKET_D)
        body = surface_to_np(surf)
        body = lit(body, sun, (0.0, 0.5 * H), 10 * S, 0.7)
        bpm, ba = blur_layer(*body, 18 * S)
        img = over_pm(img, bpm, ba)
        # the hand: rises into frame (an impulse that goes nowhere), then trembles
        rise = ease_out((tl - 0.25) / 1.1)
        settle = 0.04 * ease_io((tl - 1.6) / 1.2)
        hx = 0.20 * W + 0.02 * W * rise
        hy = mix(1.15 * H, 0.76 * H, rise) + settle * H
        intensity = sstep(0.6, 2.4, tl)
        trem = (0.022 * math.sin(tl * 2 * math.pi * 8.7) + 0.012 * math.sin(tl * 2 * math.pi * 13.1 + 1.3)) * intensity \
            + 0.02 * jitter(tg, 3, 2.0) * intensity
        curl = 0.18 + 0.10 * math.sin(tl * 1.9) * intensity + 0.12 * sstep(1.8, 2.9, tl)
        # sleeve (closer to the lens than the hand: softer)
        surf, ctx = new_surface()
        ctx.save()
        ctx.translate(hx, hy)
        ctx.rotate(-0.30 + trem * 0.4 + 0.04 * (1 - rise))
        fill_shape(ctx, [(-0.05 * H, -0.75 * H), (0.058 * H, -0.75 * H), (0.048 * H, -0.02 * H), (0.044 * H, 0.012 * H),
                         (-0.044 * H, 0.012 * H), (-0.048 * H, -0.02 * H)], B_JACKET_D,
                   grad=core.vgrad(-0.75 * H, 0.0, B_JACKET, B_JACKET_D))
        fill_shape(ctx, [(-0.047 * H, -0.03 * H), (0.047 * H, -0.03 * H), (0.045 * H, 0.014 * H),
                         (-0.045 * H, 0.014 * H)], (0.10, 0.11, 0.09))
        ctx.restore()
        sleeve = surface_to_np(surf)
        sleeve = lit(sleeve, sun, (hx, hy), 6 * S, 0.9, wrap=0.6)
        spm, sa = blur_layer(*sleeve, 7 * S)
        img = over_pm(img, spm, sa)
        surf, ctx = new_surface()
        ctx.save()
        ctx.translate(hx, hy)
        ctx.rotate(-0.30 + trem * 0.4 + 0.04 * (1 - rise))
        ctx.translate(0, 0.004 * H)
        draw_hand(ctx, curl=curl, tremble=trem, mirror=1.0, skin=B_SKIN, t=tg, scale=0.25 * H)
        ctx.restore()
        hand = surface_to_np(surf)
        hand = lit(hand, sun, (hx, hy), 5 * S, 1.5, wrap=0.6)
        hpm, ha = blur_layer(*hand, 3.4 * S)
        img = over_pm(img, hpm, ha)
        return img, GRADES[5]


# =================================================================== SHOT 7
class Shot7:
    """00:16-00:20  Static. B alone, the empty edge five steps ahead. His hand closes."""
    T0, T1 = 16.0, 20.0
    BLACK = 19.25

    def __init__(self):
        self.bd = Backdrop(-0.105, 1150 * S, 0.45 * H)
        self.ground = Ground(self.bd.view, n_near=6500, n_far=800, seed=10)
        self.cam_ = (B_POS[0] + 1.6, 1.45, B_POS[1] - 4.6)

    def frame(self, tl, tg, fi):
        if tg >= self.BLACK:
            return None, GRADES[7]
        g = gust(tg)
        img = self.bd.render(tg)
        img = blur(img, 0.8 * S)
        curl = 0.15 + 0.85 * ease_io((tl - 0.9) / 1.9)
        trem = 0.006 * math.sin(tg * 2 * math.pi * 7.3) * (1 - sstep(1.0, 2.6, tl))
        rise = 0.004 * sstep(0.9, 2.2, tl)
        chars = [
            dict(draw=B_back_draw(tg, curl_r=curl, curl_l=0.25, tremble=trem, shoulder_rise=rise),
                 X=B_POS[0], Z=B_POS[1], height=B_HEIGHT, rim_w=2.6 * S, rim_s=1.25),
        ]
        img = world_scene(img, self.bd, self.ground, self.cam_, tg, g, chars, near_split=2.2, near_blur=4 * S)
        gr = dict(GRADES[7])
        gr["exposure"] = gr["exposure"] * (1 - 0.10 * ease_io((tl - 0.4) / 2.8))   # a cloud crosses the sun
        return img, gr


# =================================================================== SHOT 3
class Shot3:
    """00:05-00:07  Ground level. Five steps of grass between B's boots and A's, and A's toes at the lip."""
    T0, T1 = 5.0, 7.0

    def __init__(self):
        self.bd = Backdrop(-0.92, 2300 * S, 0.60 * H, pad_x=int(60 * S))
        rng = np.random.RandomState(12)
        self.edge_x = 0.80 * W
        self.ground_y = 0.735 * H
        n = 1600
        self.gx = rng.uniform(-0.2 * W, self.edge_x + 0.01 * W, n)
        self.gdepth = rng.uniform(0, 1, n)        # 0 = far (near the A plane), 1 = near camera
        self.gh = rng.uniform(0.03, 0.09, n) * H
        self.gph = rng.uniform(0, 6.28, n)
        self.rock = fbm_tex(512, 1.1, 33)

    def frame(self, tl, tg, fi):
        g = gust(tg)
        u = tl / 2.0
        dolly = ease_io(u) * 0.6 + u * 0.4            # lateral slide to the right
        bg_shift = dolly * 10 * S
        mid_shift = dolly * 45 * S                    # A plane
        near_shift = dolly * 150 * S                  # B plane / foreground grass
        img = self.bd.render(tg, ox=bg_shift)
        img = blur(img, 2.2 * S)
        sun = (1.3 * W, 0.45 * H)
        ex = self.edge_x - mid_shift
        gy = self.ground_y
        # --- ground (cliff top seen edge-on) with the drop at ex
        surf, ctx = new_surface()
        pts = [(-50, gy + 4 * S)]
        for i in range(30):
            x = mix(-50, ex - 8 * S, i / 29)
            y = gy + 6 * S * math.sin(i * 1.3) * 0.5 + (i / 29) ** 3 * -6 * S
            pts.append((x, y))
        pts += [(ex, gy - 4 * S), (ex + 8 * S, gy + 4 * S), (ex + 30 * S, gy + 40 * S), (ex + 70 * S, gy + 90 * S),
                (ex + 120 * S, gy + 120 * S), (ex + 190 * S, gy + 190 * S), (ex + 330 * S, H + 50), (-50, H + 50)]
        ctx.move_to(*pts[0])
        for p in pts[1:]:
            ctx.line_to(*p)
        ctx.close_path()
        grd = cairo.LinearGradient(0, gy, 0, H)
        grd.add_color_stop_rgb(0, 0.26, 0.23, 0.12)
        grd.add_color_stop_rgb(0.15, 0.15, 0.15, 0.08)
        grd.add_color_stop_rgb(1, 0.07, 0.075, 0.05)
        ctx.set_source(grd)
        ctx.fill()
        gl = surface_to_np(surf)
        gl = lit(gl, sun, (ex, gy), 3 * S, 1.2, wrap=0.3)
        img = over_pm(img, *gl)
        # --- back grass row (between the boots, behind them)
        def grass_layer(sel, scale, shift, yoff, alpha=0.95):
            s, c = new_surface()
            for i in sel:
                x = self.gx[i] - shift
                if x > ex - 4 * S:
                    continue
                d = self.gdepth[i]
                h = self.gh[i] * scale
                bend = -(0.25 + 0.35 * g * (0.5 + 0.5 * math.sin(tg * 2.4 + self.gph[i] - x * 0.004)))
                bend += 0.06 * math.sin(tg * 7 + self.gph[i] * 2)
                sh = 0.6 + 0.4 * d
                core.blade(c, x, gy + yoff + d * 6 * S, h, (2.5 + 2 * d) * S * scale ** 0.5, bend,
                           (0.07 * sh, 0.085 * sh, 0.05 * sh), alpha)
            return surface_to_np(s)
        idx = np.arange(len(self.gx))
        back = grass_layer(idx[self.gdepth < 0.5], 1.0, mid_shift, 2 * S)
        back = lit(back, sun, (W / 2, gy), 1.8 * S, 1.5, wrap=0.6)
        img = over_pm(img, *back)
        # --- A: feet and legs at the lip, in focus
        sc_a = 1213 * S
        ax = ex - 0.115 * W
        def drawA(ctx):
            draw_side_figure(ctx, "A", tg, g)
        la = char_layer(drawA, ax, gy + 2 * S, sc_a)
        la = lit(la, sun, (ax, gy - 300 * S), 3.2 * S, 1.4)
        img = over_pm(img, *la)
        # pebble loosened at the edge, rolls and drops (6.15s ..)
        pt = tl - 1.15
        if pt > -1:
            px0 = ax + 0.098 * sc_a
            if pt < 0:
                px, py = px0, gy - 3 * S
            else:
                roll = min(pt / 0.35, 1.0)
                px = mix(px0, ex + 6 * S, ease_in(roll))
                py = gy - 3 * S
                if pt > 0.35:
                    ft = pt - 0.35
                    px = ex + 6 * S + ft * 40 * S
                    py = gy - 3 * S + 0.5 * 2400 * S * ft * ft
            if py < H + 20:
                s, c = new_surface()
                c.arc(px, py, 3.2 * S, 0, 2 * math.pi)
                c.set_source_rgb(0.12, 0.11, 0.1)
                c.fill()
                peb = surface_to_np(s)
                peb = lit(peb, sun, (px, py), 1.5 * S, 1.2)
                img = over_pm(img, *peb)
        # --- front grass (near row)
        front = grass_layer(idx[self.gdepth >= 0.5], 1.3, mid_shift * 1.6, 10 * S)
        front = lit(front, sun, (W / 2, gy), 2 * S, 1.3, wrap=0.6)
        fpm, fa = blur_layer(*front, 1.0 * S)
        img = over_pm(img, fpm, fa)
        # --- B: huge, near, out of focus
        sc_b = 2400 * S
        bx = 0.19 * W - near_shift
        def drawB(ctx):
            draw_side_figure(ctx, "B", tg, g)
        lb = char_layer(drawB, bx, 0.94 * H, sc_b)
        lb = lit(lb, sun, (bx, 0.5 * H), 8 * S, 1.1)
        bpm, ba = blur_layer(*lb, 8 * S)
        img = over_pm(img, bpm, ba)
        # --- extreme foreground blades
        s, c = new_surface()
        rng = np.random.RandomState(99)
        for k in range(26):
            x = rng.uniform(-0.1, 1.1) * W - near_shift * 1.5
            h = rng.uniform(0.15, 0.35) * H
            bend = -(0.2 + 0.3 * g * (0.5 + 0.5 * math.sin(tg * 2.0 + k))) + 0.05 * math.sin(tg * 6 + k)
            core.blade(c, x, H + 20 * S, h, rng.uniform(14, 26) * S, bend, (0.05, 0.06, 0.035), 0.95)
        fg = surface_to_np(s)
        fg = lit(fg, sun, (W / 2, H * 0.7), 6 * S, 1.0, wrap=0.6)
        fpm, fa = blur_layer(*fg, 14 * S)
        img = over_pm(img, fpm, fa)
        return img, GRADES[3]


# =================================================================== SHOT 4
class Shot4:
    """00:07-00:10  A in profile, close. The wind in his hair. He closes his eyes."""
    T0, T1 = 7.0, 10.0
    CLOSE_START, CLOSE_DUR = 8.25, 1.15

    def __init__(self):
        self.bd = Backdrop(-0.72, 1800 * S, 0.47 * H, pad_x=int(40 * S), pad_top=int(30 * S), pad_bot=int(30 * S))

    def frame(self, tl, tg, fi):
        g = gust(tg)
        u = tl / 3.0
        push = 1.0 + 0.045 * (0.5 * u + 0.5 * ease_io(u))
        canvas = self.bd.canvas(tg)
        small = cv2.resize(canvas, (canvas.shape[1] // 4, canvas.shape[0] // 4), interpolation=cv2.INTER_AREA)
        small = cv2.GaussianBlur(small, (0, 0), 3.2 * S)
        canvas = cv2.resize(small, (canvas.shape[1], canvas.shape[0]), interpolation=cv2.INTER_LINEAR)
        ex, ey = 0.545 * W, 0.42 * H
        img = self.bd.crop(canvas, scale=1 + (push - 1) * 0.3, center=(ex, ey))
        ec = ease_io((tg - self.CLOSE_START) / self.CLOSE_DUR)
        exhale = 3 * S * ease_io((tg - self.CLOSE_START - 0.4) / 1.4)
        tilt = -0.012 * ease_io((tg - self.CLOSE_START - 0.2) / 1.8)
        sway = 1.5 * S * math.sin(tg * 0.9) + breath(tg, 4.2, 1.2 * S)
        surf, ctx = new_surface()
        ctx.translate(ex, ey)
        ctx.scale(push, push)
        ctx.translate(sway * 0.3, sway + exhale)
        ctx.rotate(tilt)
        hs = 0.53 * H
        ctx.scale(hs, hs)
        ctx.translate(-0.12, 0.035)   # put the eye at the anchor
        draw_A_profile(ctx, tg, g, eye_close=ec)
        lay = surface_to_np(surf)
        sun = (1.35 * W, 0.30 * H)
        pm, a = lay
        pm = light_layer(pm, a, (1.0, -0.35), 6 * S, RIM, 1.6, wrap=0.35)
        pm = light_layer(pm, a, (1.0, -0.2), 18 * S, RIM * 0.5, 0.35, soft=10 * S, wrap=0.2)
        img = over_pm(img, pm, a)
        return img, GRADES[4]


# =================================================================== SHOT 6
class Shot6:
    """00:13-00:16  Wide, from the side. He goes. The camera starts to follow, then stops."""
    T0, T1 = 13.0, 16.0
    TILT = 500

    def __init__(self):
        self.tilt = self.TILT * S
        self.bd = Backdrop(-0.55, 1300 * S, 0.34 * H, pad_bot=int(self.tilt + 30 * S), cam_h=120.0)
        self.tip = (0.54 * W, 0.47 * H)
        self.px_m = 54 * S / A_HEIGHT
        self.cloud_top = self.tip[1] + 0.86 * H
        self._paint_cliff()
        self._sim_fall()

    # ---- static cliff painting (canvas coords)
    def _paint_cliff(self):
        cw, ch = self.bd.cw, self.bd.ch
        tx, ty = self.tip
        hw, hh = cw // 2, ch // 2
        stx, sty = tx * 0.5, ty * 0.5
        scloud = self.cloud_top * 0.5
        # full-res top contour (cap blades) + half-res copy for the painting pass
        top_full = [(-40, ty + 70 * S)]
        for i in range(1, 30):
            u = i / 29
            x = mix(-40, tx - 6 * S, u)
            y = ty + 70 * S * (1 - u ** 0.55) + 4 * S * math.sin(i * 2.1) + 10 * S * math.sin(u * 7.0) * (1 - u)
            top_full.append((x, y))
        top_full.append((tx, ty))
        top_h = [(x * 0.5, y * 0.5) for (x, y) in top_full]
        face_raw = [(tx + 6 * S, ty + 3 * S), (tx + 3 * S, ty + 16 * S), (tx - 14 * S, ty + 34 * S), (tx - 10 * S, ty + 70 * S),
                   (tx - 2 * S, ty + 110 * S), (tx + 10 * S, ty + 150 * S), (tx - 18 * S, ty + 215 * S), (tx - 30 * S, ty + 300 * S),
                   (tx - 14 * S, ty + 360 * S), (tx - 46 * S, ty + 470 * S), (tx - 38 * S, ty + 560 * S), (tx - 80 * S, ty + 700 * S),
                   (tx - 66 * S, ty + 820 * S), (tx - 120 * S, ty + 980 * S), (tx - 120 * S, ch + 10)]
        face_h = [(x * 0.5, y * 0.5) for (x, y) in face_raw]
        poly = top_h + face_h + [(-20, hh + 5)]
        surf, ctx = new_surface(hw, hh)
        ctx.move_to(*poly[0])
        for p in poly[1:]:
            ctx.line_to(*p)
        ctx.close_path()
        ctx.set_source_rgb(1, 1, 1)
        ctx.fill()
        _, a = surface_to_np(surf)
        yy, xx = np.mgrid[0:hh, 0:hw].astype(np.float32)
        tex = fbm_tex(512, 1.0, 44, ax=1.0, ay=0.30)
        tex2 = fbm_tex(512, 1.3, 45)
        tex3 = fbm_tex(512, 1.6, 47, ax=0.25, ay=1.0)
        t1 = sample(tex, xx * 1.6, yy * 1.6)
        t2 = sample(tex2, xx * 0.6, yy * 0.6)
        t3 = sample(tex3, xx * 0.5, yy * 1.2)
        facet = np.floor((t3 * 0.7 + t2 * 0.5) * 6.0) / 6.0
        inside = (a > 0.5)
        rev = inside[:, ::-1]
        has = rev.any(axis=1)
        redge = np.where(has, hw - 1 - rev.argmax(axis=1), -1).astype(np.float32)[:, None]
        wface = (8 * S + 0.16 * np.clip(yy - sty, 0, None)) * (0.75 + 0.5 * t3)
        facem = sstep(redge - wface - 1.5 * S, redge - wface + 1.5 * S, xx) * inside
        crev = sstep(0.62, 0.78, sample(tex3, xx * 1.8 + 40, yy * 0.44)) * (0.6 + 0.4 * t1)
        blot = sample(tex2, xx * 0.24 + 77, yy * 0.24)
        shadow_col = rgb(0.22, 0.21, 0.27) * (0.55 + 0.75 * facet + 0.3 * (t1 - 0.5) + 0.3 * (blot - 0.5)
                                              - 0.35 * crev)[..., None]
        lit_col = rgb(0.62, 0.42, 0.31) * (0.6 + 0.6 * facet + 0.3 * (t1 - 0.5) - 0.4 * crev)[..., None]
        strata = np.sin((yy + 9 * S * t2) / (10.5 * S)) * 0.5 + 0.5
        ledge = sstep(0.82, 0.96, strata)[..., None]
        shadow_col = shadow_col * (0.92 + 0.14 * ledge)
        lit_col = lit_col * (0.85 + 0.3 * ledge)
        rock = mix(shadow_col, lit_col, facem[..., None])
        depth_t = sstep(sty - 10 * S, scloud, yy)
        rock = mix(rock, rgb(0.50, 0.46, 0.56), (depth_t ** 0.8 * 0.6)[..., None])
        dist = cv2.distanceTransform(inside.astype(np.uint8), cv2.DIST_L2, 5)
        topline = np.full((hw,), 1e9, np.float32)
        colhas = inside.any(axis=0)
        topline = np.where(colhas, inside.argmax(axis=0), 1e5).astype(np.float32)[None, :]
        cap = sstep(topline + 7 * S, topline + 4 * S, yy) * inside
        rock = mix(rock, rgb(0.17, 0.17, 0.09) * (0.8 + 0.4 * t2)[..., None], cap[..., None])
        mist = sstep(scloud - 150 * S, scloud + 20 * S, yy)
        rock = mix(rock, mix(MIST, rgb(0.62, 0.58, 0.68), 0.6), (mist * 0.85)[..., None])
        pm = rock * a[..., None]
        pm = light_layer(pm, a, (1.0, -0.6), 1.1 * S, RIM, 1.1, wrap=0.3)
        # distant pinnacle rising out of the cloud sea
        surf, ctx = new_surface(hw, hh)
        sxh = 0.43 * W
        spur0 = [(sxh - 47 * S, hh + 5), (sxh - 35 * S, sty + 260 * S), (sxh - 26 * S, sty + 235 * S),
                 (sxh - 22 * S, sty + 205 * S), (sxh - 13 * S, sty + 196 * S), (sxh - 9 * S, sty + 175 * S),
                 (sxh - 2 * S, sty + 169 * S), (sxh + 3 * S, sty + 181 * S), (sxh + 11 * S, sty + 186 * S),
                 (sxh + 15 * S, sty + 210 * S), (sxh + 24 * S, sty + 222 * S), (sxh + 30 * S, sty + 270 * S),
                 (sxh + 55 * S, hh + 5)]
        spur = [(sxh + (x - sxh) * 0.75, sty + 45 * S + (y - sty) * 1.0) for (x, y) in spur0]
        fill_shape(ctx, spur, (1, 1, 1))
        _, sa = surface_to_np(surf)
        sins = sa > 0.5
        rv = sins[:, ::-1]
        sre = np.where(rv.any(axis=1), hw - 1 - rv.argmax(axis=1), -1).astype(np.float32)[:, None]
        sface = sstep(sre - 7 * S - 0.1 * np.clip(yy - sty - 169 * S, 0, None), sre - 4 * S, xx) * sins
        scol = mix(rgb(0.27, 0.26, 0.35), rgb(0.58, 0.45, 0.42), sface[..., None]) * (0.8 + 0.4 * facet)[..., None]
        scol = mix(scol, mix(MIST, rgb(0.6, 0.57, 0.68), 0.5),
                   (sstep(sty + 180 * S, scloud + 20 * S, yy) * 0.85)[..., None])
        spm = scol * sa[..., None]
        spm = light_layer(spm, sa, (1.0, -0.4), 0.7 * S, RIM, 0.7)
        # upscale the half-res paintings to the full canvas
        self.cliff = (cv2.resize(pm.astype(np.float32), (cw, ch), cv2.INTER_LINEAR),
                      cv2.resize(a.astype(np.float32), (cw, ch), cv2.INTER_LINEAR))
        self.spur = (cv2.resize(spm.astype(np.float32), (cw, ch), cv2.INTER_LINEAR),
                     cv2.resize(sa.astype(np.float32), (cw, ch), cv2.INTER_LINEAR))
        # cap blades (full-res coords)
        rng = np.random.RandomState(21)
        n = 260
        self.cap_x = rng.uniform(-30, tx, n)
        self.cap_y = np.interp(self.cap_x, [p[0] for p in top_full], [p[1] for p in top_full])
        self.cap_h = rng.uniform(5, 11, n) * S
        self.cap_ph = rng.uniform(0, 6.28, n)
        # foreground mist bank tex
        self.mist_tex = fbm_tex(512, 1.4, 46)
        fyy, fxx = np.mgrid[0:ch, 0:cw].astype(np.float32)
        self.yy, self.xx = fyy, fxx

    def _sim_fall(self):
        dt = 1.0 / 240
        g = 9.81
        L = A_HEIGHT * 0.55
        th = LEAN_S5_END
        om = 0.30
        t = 0.0
        self.track = []
        phase = "pivot"
        cx = cy = 0.0
        vx = vy = 0.0
        knee = 0.0
        while t < 3.2:
            if phase == "pivot":
                knee = 0.35 * math.sin(math.pi * min(max((t - 0.12) / 0.30, 0), 1))
                al = (g / L) * math.sin(th) * 0.9
                if 0.27 < t < 0.42:
                    al += 3.5           # a small push from the ankles: he goes, he does not slip
                om += al * dt
                th += om * dt
                cx = math.sin(th) * L
                cy = -math.cos(th) * L
                if th > 0.62:
                    phase = "air"
                    self.t_leave = t
                    vx = om * L * math.cos(th) + 0.6
                    vy = om * L * math.sin(th)
            else:
                vy += g * 1.32 * dt
                cx += vx * dt
                cy += vy * dt
                om += (0.85 - th) * 6.0 * dt - om * 3.0 * dt
                th += om * dt
                knee = max(knee - dt * 1.5, 0.0)
            self.track.append((t, th, cx, cy, knee))
            t += dt

    def a_state(self, tl):
        i = min(int(tl * 240), len(self.track) - 1)
        return self.track[i]

    def frame(self, tl, tg, fi):
        g = gust(tg)
        t, th, cxm, cym, knee = self.a_state(tl)
        tleave = self.t_leave
        # A's centre of mass in canvas px
        tipx, tipy = self.tip
        foot_x = tipx - 0.07 * 54 * S * 0
        com_x = foot_x + cxm * self.px_m
        com_y = tipy + cym * self.px_m
        drop = max(com_y - (tipy - 0.55 * A_HEIGHT * self.px_m * math.cos(LEAN_S5_END)), 0)
        oy = self.tilt * math.tanh(0.85 * drop / self.tilt) * 1.06
        oy = min(oy, self.tilt)
        canvas = self.bd.canvas(tg)
        canvas = over_pm(canvas, *self.spur)
        canvas = over_pm(canvas, *self.cliff)
        img_c = canvas
        # grass cap blades (canvas space)
        s, c = new_surface(self.bd.cw, self.bd.ch)
        for i in range(len(self.cap_x)):
            bend = -(0.3 + 0.4 * g * (0.5 + 0.5 * math.sin(tg * 2.5 + self.cap_ph[i] - self.cap_x[i] * 0.01)))
            core.blade(c, self.cap_x[i], self.cap_y[i] + 2 * S, self.cap_h[i], 2.0 * S, bend, (0.08, 0.09, 0.055), 0.95)
        gl = surface_to_np(s)
        gl = (light_layer(gl[0], gl[1], (1, -0.7), 1.2 * S, RIM, 1.4, wrap=0.6), gl[1])
        img_c = over_pm(img_c, *gl)
        # figures (canvas space)
        sun = self.bd.sun_screen()
        sun = (sun[0], sun[1])
        flight = sstep(tleave, tleave + 0.7, tl)
        s, c = new_surface(self.bd.cw, self.bd.ch)
        # B, five steps behind, motionless
        bx = tipx - 4.3 * self.px_m - 0.6 * self.px_m
        c.save()
        c.translate(bx, self.cap_y[np.argmin(np.abs(self.cap_x - bx))] + 1.5 * S)
        c.scale(B_HEIGHT * self.px_m, B_HEIGHT * self.px_m)
        draw_side_figure(c, "B", tg, g, hand_curl=0.25)
        c.restore()
        # A
        c.save()
        if tl < tleave:
            c.translate(tipx - 0.09 * A_HEIGHT * self.px_m, tipy + 1.0 * S)
            c.rotate(th)
            c.scale(A_HEIGHT * self.px_m, A_HEIGHT * self.px_m)
            draw_side_figure(c, "A", tg, g, knee=knee)
        else:
            c.translate(com_x, com_y)
            c.rotate(th)
            c.scale(A_HEIGHT * self.px_m, A_HEIGHT * self.px_m)
            c.translate(0, 0.5)
            draw_side_figure(c, "A", tg, g, knee=knee, arm_lift=0.9 * flight, flight=flight)
        c.restore()
        figs = surface_to_np(s)
        figs = (light_layer(figs[0], figs[1], (1.0, -0.5), 1.4 * S, RIM, 1.5, wrap=0.4), figs[1])
        img_c = over_pm(img_c, *figs)
        # foreground mist bank (in front of the falling figure)
        drift = tg * 12 * S
        yy, xx = self.yy, self.xx
        m = sample(self.mist_tex, (xx + drift) * 0.5, yy * 0.9)
        top = self.cloud_top - 60 * S * m
        ma = sstep(top - 40 * S, top + 70 * S, yy) * 0.97
        mcol = mix(rgb(0.70, 0.64, 0.70), rgb(1.0, 0.85, 0.72), (0.4 + 0.6 * m)[..., None] *
                   (1 - sstep(top, top + 200 * S, yy))[..., None])
        img_c = over(img_c, mcol.astype(np.float32), ma.astype(np.float32))
        img = self.bd.crop(img_c, oy=oy)
        return img, GRADES[6]


SHOTS = [Shot1, Shot2, Shot3, Shot4, Shot5, Shot6, Shot7]


def shot_for(tg):
    for cls in SHOTS:
        if cls.T0 <= tg < cls.T1:
            return cls
    return SHOTS[-1]
