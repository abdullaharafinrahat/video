"""
Shared world: the promontory, its grass, the backdrop and character placement.
Geography (metres, +Z = toward the distant range / the sun side, Y up):
    cliff tip edge ............ Z = 0
    A stands .................. (0.0, -0.6)    0.6 m from the drop
    B stands .................. (-0.9, -4.9)   five long steps behind
"""
import math

import cairo
import numpy as np

import core
from core import (S, SUN_AZ, SUN_COL, SUN_EL, MIST, View, sky, mountains, CloudSea, HighCloud, over, over_pm,
                  new_surface, surface_to_np, light_layer, blur_layer, fbm_tex, sample, sstep, mix, rgb,
                  fbm1, sun_prox, _plane_coords, clamp01)
from figures import draw_A_back, draw_B_back

A_POS = (0.0, -0.6)
B_POS = (-0.9, -4.9)
A_HEIGHT = 1.82
B_HEIGHT = 1.74


def W():
    return core.W


def H():
    return core.H


# ------------------------------------------------------------------ backdrop
class Backdrop:
    def __init__(self, yaw, f, cy, cam_h=140.0, pad_x=0, pad_top=0, pad_bot=0, hc_height=2600.0):
        self.cw = W() + 2 * pad_x
        self.ch = H() + pad_top + pad_bot
        self.px, self.pt = pad_x, pad_top
        self.view = View(self.cw, self.ch, yaw, f, self.cw / 2.0, cy + pad_top)
        self.sky = sky(self.view)
        self.mc, self.ma = mountains(self.view, cam_h)
        self.cs = CloudSea(self.view, cam_h)
        self.hc = HighCloud(self.view, hc_height)
        self.yaw, self.f, self.cy = yaw, f, cy

    def canvas(self, t):
        img = self.sky.copy()
        c, a = self.hc.render(t)
        img = over(img, c, a)
        c, a = self.cs.render(t)
        img = over(img, c, a)
        return over_pm(img, self.mc, self.ma)

    def crop(self, img, ox=0.0, oy=0.0, scale=1.0, center=None):
        import cv2
        cx, cy = center if center else (W() / 2.0, H() / 2.0)
        # frame (x,y) -> canvas ((x-cx)/scale + cx + px + ox, ...)
        M = np.float32([[scale, 0, -scale * (cx + self.px + ox) + cx],
                        [0, scale, -scale * (cy + self.pt + oy) + cy]])
        return cv2.warpAffine(img, M, (W(), H()), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

    def render(self, t, ox=0.0, oy=0.0, scale=1.0, center=None):
        return self.crop(self.canvas(t), ox, oy, scale, center)

    def sun_screen(self, oy=0.0):
        x = self.cw / 2.0 + self.f * math.tan(SUN_AZ - self.yaw) - self.px
        y = self.cy - self.f * math.tan(SUN_EL) / math.cos(SUN_AZ - self.yaw) - oy
        return x, y


# --------------------------------------------------------------- promontory
def promontory_contour():
    left, right = [], []
    for Z in np.linspace(-220, -1.7, 70):
        d = -Z
        nl = float(fbm1(d * 0.18, 41, 4096, 4)) * 2 - 1
        nr = float(fbm1(d * 0.18 + 50, 42, 4096, 4)) * 2 - 1
        wl = 2.3 + 0.10 * d + 0.012 * d * d
        wr = 1.9 + 0.09 * d + 0.010 * d * d
        left.append((-(min(wl, 60) + (0.55 + 0.05 * d) * nl), Z))
        right.append((min(wr, 55) + (0.5 + 0.05 * d) * nr, Z))
    tip = [(-1.8, -0.75), (-1.2, -0.12), (-0.55, 0.10), (0.1, 0.02), (0.7, -0.25), (1.35, -0.85)]
    return np.array(left + tip + right[::-1], np.float64)


def point_in_poly(px, pz, poly):
    inside = np.zeros(px.shape, bool)
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, zi = poly[i]
        xj, zj = poly[j]
        cond = ((zi > pz) != (zj > pz)) & (px < (xj - xi) * (pz - zi) / (zj - zi + 1e-12) + xi)
        inside ^= cond
        j = i
    return inside


def to_cam(view, cam, X, Y, Z):
    x, y, z = X - cam[0], Y - cam[1], Z - cam[2]
    c, s = math.cos(view.yaw), math.sin(view.yaw)
    return x * c - z * s, y, x * s + z * c


def clip_near(pts, near):
    out = []
    n = len(pts)
    for i in range(n):
        a, b = pts[i], pts[(i + 1) % n]
        ain, bin_ = a[2] >= near, b[2] >= near
        if ain:
            out.append(a)
        if ain != bin_:
            t = (near - a[2]) / (b[2] - a[2])
            out.append(tuple(a[k] + (b[k] - a[k]) * t for k in range(3)))
    return out


class Ground:
    def __init__(self, view, n_near=2600, n_far=1400, seed=7):
        self.view = view
        self.poly = promontory_contour()
        self.tex = fbm_tex(1024, 1.25, 81)
        self.tex2 = fbm_tex(512, 0.9, 82)
        rng = np.random.RandomState(seed)
        pts = []
        # dense grass close to the tip, sparse further back
        for (n, z0, z1) in ((n_near, -9.0, 0.2), (n_far, -60.0, -9.0)):
            X = rng.uniform(-8, 8, n * 3) * (1 + (z0 < -10) * 3)
            Z = rng.uniform(z0, z1, n * 3)
            ok = point_in_poly(X, Z, self.poly)
            pts.append(np.stack([X[ok][:n], Z[ok][:n]], 1))
        # fringe tufts right along the tip edge (silhouetted against the void)
        fr = []
        tip = self.poly[64:76] if len(self.poly) > 76 else self.poly
        for k in range(len(self.poly) - 1):
            a, b = self.poly[k], self.poly[k + 1]
            if max(a[1], b[1]) < -12:
                continue
            seg = math.hypot(b[0] - a[0], b[1] - a[1])
            m = int(seg * 26)
            for i in range(m):
                u = rng.rand()
                p = a + (b - a) * u
                # nudge inward
                cxp = np.array([0.0, -6.0])
                d = cxp - p
                d /= (np.linalg.norm(d) + 1e-9)
                fr.append(p + d * rng.uniform(0.02, 0.25))
        pts.append(np.array(fr))
        P = np.concatenate(pts, 0)
        self.bx, self.bz = P[:, 0], P[:, 1]
        n = len(P)
        self.bh = rng.uniform(0.10, 0.30, n) * np.where(rng.rand(n) < 0.10, 1.5, 1.0)
        self.bw = rng.uniform(0.010, 0.018, n)
        self.bph = rng.uniform(0, 6.28, n)
        self.bshade = rng.uniform(0.0, 1.0, n)
        self.blean = rng.uniform(-0.25, 0.25, n)

    # ---- ground surface
    def surface(self, cam, walls=False):
        v = self.view
        def proj(p):
            return v.cx + v.f * p[0] / p[2], v.cy - v.f * p[1] / p[2]
        wa = None
        if walls:
            # the mountain mass below the lip: successively wider, mistier contours
            ws, wctx = new_surface()
            P = self.poly
            prev_ = np.roll(P, 1, 0)
            next_ = np.roll(P, -1, 0)
            tang = next_ - prev_
            nrm = np.stack([-tang[:, 1], tang[:, 0]], 1)       # outward for clockwise polygon
            nrm /= (np.linalg.norm(nrm, axis=1, keepdims=True) + 1e-9)
            rngw = np.random.RandomState(17)
            jag = rngw.uniform(0.7, 1.3, len(P))
            Xc0, Yc0, Zc0 = to_cam(v, cam, P[:, 0], np.zeros(len(P)), P[:, 1])
            cp0 = clip_near(list(zip(Xc0, np.full(len(P), -cam[1]), Zc0)), 0.3)
            rock = np.array([0.10, 0.095, 0.12])
            mistc = np.array([0.62, 0.58, 0.68])
            steps = 9
            tx_ = to_cam(v, cam, 0.0, 0.0, 0.0)
            xtip = v.cx + v.f * tx_[0] / max(tx_[2], 0.3)
            for k in range(steps, 0, -1):
                u = k / steps
                wctx.new_path()
                for j, p_ in enumerate(cp0):
                    x_, y_ = proj(p_)
                    hh = v.f * 26.0 / max(p_[2], 0.3) * 0.42 * u * (0.85 + 0.3 * math.sin(j * 1.7 + k))
                    dxs = float(np.clip((x_ - xtip) / (40 * S), -1, 1)) * hh * 0.9
                    if j == 0:
                        wctx.move_to(x_ + dxs, y_ + hh)
                    else:
                        wctx.line_to(x_ + dxs, y_ + hh)
                wctx.close_path()
                c_ = rock * (1 - u ** 1.4) + mistc * u ** 1.4
                wctx.set_source_rgb(*c_)
                wctx.fill()
            wpm, wa = surface_to_np(ws)
            streak = sample(fbm_tex(512, 1.0, 83, ax=1.0, ay=0.3), v.az * 2500.0, v.el * 1400.0)
            wpm = wpm * (0.82 + 0.36 * streak)[..., None]
            wpm, wa = blur_layer(wpm, wa, 2.5 * S)
        Xc, Yc, Zc = to_cam(v, cam, self.poly[:, 0], 0.0 * self.poly[:, 0], self.poly[:, 1])
        pts = clip_near(list(zip(Xc, np.full_like(Xc, -cam[1]), Zc)), 0.3)
        surf, ctx = new_surface()
        if len(pts) > 2:
            ctx.move_to(*proj(pts[0]))
            for p in pts[1:]:
                ctx.line_to(*proj(p))
            ctx.close_path()
            ctx.set_source_rgba(1, 1, 1, 1)
            ctx.fill()
        _, a = surface_to_np(surf)
        X, Z, dist, valid = _plane_coords(v, -cam[1], (cam[0], cam[2]))
        t1 = sample(self.tex, X * 18.0, Z * 18.0)
        t2 = sample(self.tex2, X * 70.0, Z * 70.0)
        t3 = sample(self.tex, X * 3.0 + 300, Z * 3.0)
        base = mix(rgb(0.10, 0.12, 0.07), rgb(0.27, 0.24, 0.12), clamp01(t1 * 0.8 + t3 * 0.4 - 0.2)[..., None])
        base = base * (0.85 + 0.3 * t2)[..., None]
        graze = sstep(-0.45, -0.02, v.el)
        sheen = sun_prox(v.az, k=1.8) * graze * (0.25 + 0.5 * t2)
        col = base + SUN_COL * (sheen * 0.45)[..., None]
        col = mix(col, MIST * 0.75, (sstep(25, 400, dist) * 0.45)[..., None])
        a = a * valid
        if wa is not None:
            col = col * a[..., None] + wpm * (1 - a[..., None])
            a = a + wa * (1 - a)
            col = col / np.maximum(a, 1e-4)[..., None]
        return col.astype(np.float32), a.astype(np.float32)

    # ---- grass blades
    def blades(self, cam, t, g, near_split=None, zmax=None):
        v = self.view
        X, Z, h = self.bx, self.bz, self.bh
        ph = self.bph
        wave = np.sin(t * 2.3 + ph + X * 0.9 + Z * 0.6) * 0.5 + 0.5
        flick = np.sin(t * 7.0 + ph * 3) * 0.06
        bend = 0.18 + (0.30 + 0.25 * wave) * g + flick
        sx = 0.12 * np.sin(t * 3.1 + ph) * g + self.blean * 0.3
        tipX = X + sx * h
        tipY = h * np.cos(bend)
        tipZ = Z - h * np.sin(bend)
        midX = X + sx * h * 0.35
        midY = h * 0.55 * np.cos(bend * 0.45)
        midZ = Z - h * 0.55 * np.sin(bend * 0.45)
        bxc, byc, bzc = to_cam(v, cam, X, 0.0, Z)
        txc, tyc, tzc = to_cam(v, cam, tipX, tipY, tipZ)
        mxc, myc, mzc = to_cam(v, cam, midX, midY, midZ)
        ok = (bzc > 0.35) & (tzc > 0.3)
        if zmax is not None:
            ok &= bzc < zmax
        f, cx, cy = v.f, v.cx, v.cy
        bxs = cx + f * bxc / np.maximum(bzc, 1e-3)
        bys = cy - f * byc / np.maximum(bzc, 1e-3)
        ok &= (bxs > -200) & (bxs < W() + 200) & (bys > -100) & (bys < H() + 400)
        idx = np.nonzero(ok)[0]
        idx = idx[np.argsort(-bzc[idx])]
        far_s, far_c = new_surface()
        near_s, near_c = (new_surface() if near_split else (None, None))
        for i in idx:
            z = bzc[i]
            ctx = near_c if (near_split and z < near_split) else far_c
            w = max(f * self.bw[i] / z, 0.6 * S)
            x0, y0 = bxs[i], bys[i]
            x1, y1 = cx + f * mxc[i] / mzc[i], cy - f * myc[i] / mzc[i]
            x2, y2 = cx + f * txc[i] / tzc[i], cy - f * tyc[i] / tzc[i]
            sh = self.bshade[i]
            col = (0.06 + 0.07 * sh, 0.075 + 0.06 * sh, 0.04 + 0.025 * sh)
            ctx.move_to(x0 - w / 2, y0)
            ctx.curve_to(x1 - w * 0.35, y1, x1 - w * 0.2, y1, x2, y2)
            ctx.curve_to(x1 + w * 0.2, y1, x1 + w * 0.35, y1, x0 + w / 2, y0)
            ctx.close_path()
            ctx.set_source_rgba(col[0], col[1], col[2], 0.95)
            ctx.fill()
        far = surface_to_np(far_s)
        near = surface_to_np(near_s) if near_split else None
        return far, near


def project_feet(view, cam, X, Z):
    xc, yc, zc = to_cam(view, cam, X, 0.0, Z)
    return view.cx + view.f * xc / zc, view.cy - view.f * yc / zc, zc


def contact_shadow(ctx, x, y, scale, wfac=0.32, alpha=0.55):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(scale * wfac, scale * 0.035)
    g = cairo.RadialGradient(0, 0, 0, 0, 0, 1)
    g.add_color_stop_rgba(0, 0, 0, 0, alpha)
    g.add_color_stop_rgba(1, 0, 0, 0, 0)
    ctx.set_source(g)
    ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.fill()
    ctx.restore()


RIM = rgb(1.0, 0.74, 0.45)


def char_layer(draw_fn, x, y, scale, rot=0.0, sx=1.0, sy=1.0):
    surf, ctx = new_surface()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(scale * sx, scale * sy)
    draw_fn(ctx)
    return surface_to_np(surf)


def lit(layer, sun_xy, at_xy, width, strength=1.3, col=RIM, wrap=0.45):
    pm, a = layer
    d = (sun_xy[0] - at_xy[0], sun_xy[1] - at_xy[1])
    pm = light_layer(pm, a, d, width, col, strength, wrap=wrap)
    return pm, a


def world_scene(img, bd, ground, cam, t, g, chars, near_split=None, near_blur=0.0, far_grass_blur=0.0,
                ground_rim=2.5, shadow_alpha=0.55, char_fn=None, walls=False):
    """chars: list of dict(draw=callable(ctx), X, Z, height, blur, rim_w, rot, sx, sy)"""
    sun = bd.sun_screen()
    col, a = ground.surface(cam, walls=walls)
    # contact shadows
    ss, sctx = new_surface()
    for c in chars:
        x, y, z = project_feet(bd.view, cam, c["X"], c["Z"])
        sc = bd.view.f * c["height"] / z
        contact_shadow(sctx, x, y, sc, alpha=shadow_alpha)
    _, sa = surface_to_np(ss)
    col = col * (1 - sa[..., None])
    pm = col * a[..., None]
    pm = light_layer(pm, a, (sun[0] - W() / 2, sun[1] - H()), ground_rim * S, RIM * 0.9, 0.9, wrap=0.2)
    img = over_pm(img, pm, a)
    (fpm, fa), near = ground.blades(cam, t, g, near_split=near_split)
    fpm = light_layer(fpm, fa, (sun[0] - W() / 2, sun[1] - H() * 0.8), 1.3 * S, RIM, 0.8, wrap=0.3)
    if far_grass_blur > 0:
        fpm, fa = blur_layer(fpm, fa, far_grass_blur)
    img = over_pm(img, fpm, fa)
    # characters, far to near
    order = sorted(chars, key=lambda c: -project_feet(bd.view, cam, c["X"], c["Z"])[2])
    for c in order:
        x, y, z = project_feet(bd.view, cam, c["X"], c["Z"])
        sc = bd.view.f * c["height"] / z
        layer = char_layer(c["draw"], x, y, sc, c.get("rot", 0.0), c.get("sx", 1.0), c.get("sy", 1.0))
        layer = lit(layer, sun, (x, y - sc * 0.6), c.get("rim_w", max(1.2, sc * 0.006)) * 1.0,
                    c.get("rim_s", 1.3))
        pm2, a2 = blur_layer(*layer, c.get("blur", 0.0))
        img = over_pm(img, pm2, a2)
    if near is not None:
        npm, na = near
        npm = light_layer(npm, na, (sun[0] - W() / 2, sun[1] - H()), 3 * S, RIM, 1.2, wrap=0.6)
        npm, na = blur_layer(npm, na, near_blur)
        img = over_pm(img, npm, na)
    return img
