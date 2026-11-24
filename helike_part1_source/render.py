import sys, os, subprocess, time, json
from multiprocessing import Pool
from lib import *
import s_coast, s_early, s_mid, s_late

FPS = 24
TOTAL = 108.4
SCENES = [(0.0, 6.55, s_coast.scene1), (6.55, 12.1, s_early.scene2), (12.1, 22.9, s_early.scene3), (22.9, 30.9, s_coast.scene4),
          (30.9, 62.4, s_mid.scene5), (62.4, 70.4, s_mid.scene6), (70.4, 79.4, s_late.scene7), (79.4, 97.3, s_late.scene8),
          (97.3, 108.0, s_late.scene9)]
XF = 0.5
CAPS = [
    (0.0, 6.3, "Imagine waking up tomorrow… and discovering that an entire city has vanished."),
    (6.7, 7.9, "Not abandoned."), (8.1, 10.4, "Not destroyed by an invading army."), (10.9, 12.0, "Vanished."),
    (12.3, 13.7, "The houses are gone."), (13.8, 15.3, "The streets are gone."), (15.5, 17.4, "The people… are gone."),
    (17.95, 19.5, "And the strangest part?"), (19.7, 22.7, "Nobody can agree on exactly what happened."),
    (23.0, 28.3, "Over 2,300 years ago, something extraordinary happened"), (28.4, 30.8, "to an ancient Greek city called Helike."),
    (31.0, 36.0, "Ancient writers described a disaster so devastating that the city supposedly"),
    (36.05, 40.1, "disappeared beneath the water, taking its inhabitants with it."),
    (40.35, 43.3, "For centuries, people searched for its remains."), (43.55, 46.3, "Some believed it was hiding beneath the sea."),
    (46.45, 48.8, "Others thought the story was exaggerated."), (48.95, 52.5, "But when archaeologists finally began investigating the area,"),
    (52.7, 55.0, "they discovered something unexpected."), (55.25, 59.3, "The lost city might not have been where everyone was looking."),
    (59.6, 62.2, "And that's where this mystery gets interesting."),
    (62.55, 66.9, "To understand what happened, we need to travel back to ancient Greece."), (67.25, 69.6, "The year is 373 BC."),
    (70.7, 76.5, "Along the northern coast of the Peloponnese, near the Gulf of Corinth, stood a city called Helike."),
    (76.6, 79.3, "It was an important city in the region of Achaea."),
    (79.4, 87.2, "It had temples, buildings, streets, and a connection to one of the most powerful gods in Greek mythology…"),
    (87.4, 88.4, "Poseidon."), (88.5, 93.5, "Poseidon was the god of the sea, but he was also associated with earthquakes."),
    (93.85, 97.2, "And that detail would become central to the story of Helike."),
    (97.4, 102.5, "According to later ancient accounts, the city was struck by a powerful earthquake."),
    (102.75, 105.4, "The ground shook, buildings collapsed,"), (105.7, 107.9, "and then came the sea."),
]
_cap = {}
_grain = None


def cap_img(i):
    if i in _cap:
        return _cap[i]
    txt = CAPS[i][2]
    f = font('gar', 40, 500)
    d = ImageDraw.Draw(Image.new('L', (4, 4)))
    lines = [txt]
    if d.textlength(txt, font=f) > 1120:
        words = txt.split()
        best = None
        for k in range(1, len(words)):
            a, b = ' '.join(words[:k]), ' '.join(words[k:])
            m = max(d.textlength(a, font=f), d.textlength(b, font=f))
            if best is None or m < best[0]:
                best = (m, [a, b])
        lines = best[1]
    lay = Image.new('RGBA', (W, 200), (0, 0, 0, 0))
    g = np.zeros((200, W), np.uint8)
    g[:] = (np.linspace(0, 1, 200)[:, None] ** 1.6 * 170).astype(np.uint8)
    lay.putalpha(Image.fromarray(g))
    ld = ImageDraw.Draw(lay)
    y0 = 200 - 36 - 50 * len(lines)
    for k, ln in enumerate(lines):
        w = d.textlength(ln, font=f)
        x = (W - w) / 2
        y = y0 + k * 50
        ld.text((x + 2, y + 2), ln, font=f, fill=(0, 0, 0, 230))
        ld.text((x, y), ln, font=f, fill=(255, 248, 232, 255))
    _cap[i] = lay
    return lay


def frame(t):
    global _grain
    si = 0
    for k, (a, b, fn) in enumerate(SCENES):
        if a <= t < b or k == len(SCENES) - 1:
            si = k
            if a <= t < b:
                break
    a, b, fn = SCENES[si]
    img = fn(min(t - a, b - a)) if t < b else None
    if img is None:
        img = Image.new('RGB', (W, H), (4, 10, 20))
    if si < len(SCENES) - 1 and t > b - XF:
        nxt = SCENES[si + 1][2](0.0)
        q = ease((t - (b - XF)) / XF)
        img = Image.blend(img.convert('RGB'), nxt.convert('RGB'), q)
    img = vignette(img, 0.38)
    for i, (c0, c1, _) in enumerate(CAPS):
        if c0 - 0.05 <= t <= c1 + 0.3:
            al = min(prog(t, c0 - 0.05, c0 + 0.25), 1 - prog(t, c1, c1 + 0.3))
            lay = fade_img(cap_img(i), clamp(al))
            img = img.convert('RGB')
            img.paste(lay, (0, H - 200), lay)
    # grain + fades
    if _grain is None:
        _grain = grain_tiles()
    arr = np.asarray(img, np.float32) + _grain[int(t * FPS) % len(_grain)]
    f_in = ease(prog(t, 0.0, 0.7))
    f_out = 1 - ease(prog(t, TOTAL - 0.8, TOTAL))
    arr *= f_in * f_out
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


from art import grain_tiles


def work(args):
    k, f0, f1 = args
    out = f'/tmp/w/seg_{k:03d}.mp4'
    ff = '/tmp/w/ffmpeg'
    p = subprocess.Popen([ff, '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'fast', '-crf', '19', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for f in range(f0, f1):
        im = frame(f / FPS)
        p.stdin.write(im.convert('RGB').tobytes())
    p.stdin.close()
    p.wait()
    print('done', k, flush=True)
    return out


if __name__ == '__main__':
    n = int(TOTAL * FPS)
    cs = 60
    jobs = [(i, i * cs, min(n, (i + 1) * cs)) for i in range((n + cs - 1) // cs)]
    t0 = time.time()
    with Pool(2) as pool:
        outs = pool.map(work, jobs, chunksize=1)
    open('/tmp/w/list.txt', 'w').write(''.join(f"file '{o}'\n" for o in sorted(outs)))
    print('render done', time.time() - t0, flush=True)
