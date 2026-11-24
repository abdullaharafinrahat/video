import sys, os, subprocess, time, math
import numpy as np
from multiprocessing import Pool
from gfx import *
import imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
TOTAL = 108.4
N = int(TOTAL * FPS)
BOUNDS = [(0.0, 6.4, 'a', 'Scene1'), (6.4, 11.9, 'a', 'Scene2'), (11.9, 22.6, 'a', 'Scene3'), (22.6, 31.0, 'a', 'Scene4'),
          (31.0, 62.3, 'b', 'Scene5'), (62.3, 70.0, 'b', 'Scene6'), (70.0, 79.85, 'c', 'Scene7'), (79.85, 97.6, 'c', 'Scene8'), (97.6, TOTAL, 'c', 'Scene9')]
CAPS = [(0.0, 5.7, "Imagine waking up tomorrow… and discovering that an entire city has vanished."),
        (6.76, 11.12, "Not abandoned. Not destroyed by an invading army. Vanished."),
        (12.32, 18.98, "The houses are gone. The streets are gone. The people… are gone. And the strangest part?"),
        (19.9, 22.12, "Nobody can agree on exactly what happened."),
        (22.96, 30.58, "Over 2,300 years ago, something extraordinary happened to an ancient Greek city called Helike."),
        (31.14, 37.9, "Ancient writers described a disaster so devastating that the city supposedly disappeared beneath the water,"),
        (38.24, 39.8, "taking its inhabitants with it."),
        (40.46, 42.64, "For centuries, people searched for its remains."),
        (43.56, 45.52, "Some believed it was hiding beneath the sea."),
        (46.34, 47.92, "Others thought the story was exaggerated."),
        (48.96, 54.3, "But when archaeologists finally began investigating the area, they discovered something unexpected."),
        (55.0, 58.84, "The lost city might not have been where everyone was looking."),
        (59.6, 61.54, "And that's where this mystery gets interesting."),
        (62.48, 66.46, "To understand what happened, we need to travel back to ancient Greece."),
        (67.26, 69.9, "The year is 373 BC."),
        (70.26, 76.52, "Along the northern coast of the Peloponnese, near the Gulf of Corinth, stood a city called Helike."),
        (76.86, 79.48, "It was an important city in the region of Achaea."),
        (79.86, 86.32, "It had temples, buildings, streets, and a connection to one of the most powerful gods in Greek mythology…"),
        (87.3, 88.2, "Poseidon."),
        (88.54, 93.0, "Poseidon was the god of the sea, but he was also associated with earthquakes,"),
        (93.82, 97.16, "and that detail would become central to the story of Helike."),
        (97.62, 101.78, "According to later ancient accounts, the city was struck by a powerful earthquake."),
        (102.8, 107.4, "The ground shook, buildings collapsed, and then came the sea.")]

_cache = {}; _caps = None; _title = None
def get_scene(k):
    if k in _cache: return _cache[k]
    for kk in list(_cache):
        if abs(kk - k) > 1: del _cache[kk]
    a, b, mod, cls = BOUNDS[k]
    m = __import__('scenes_' + mod)
    _cache[k] = getattr(m, cls)()
    return _cache[k]

def make_caption(text):
    f = font('GaramondItalic.ttf', 38, 500)
    d0 = ImageDraw.Draw(Image.new('RGBA', (10, 10)))
    words = text.split(); lines = []; cur = ''
    for w in words:
        tt = (cur + ' ' + w).strip()
        if d0.textlength(tt, font=f) > 1020 and cur: lines.append(cur); cur = w
        else: cur = tt
    lines.append(cur)
    bh = 60 + 48 * len(lines)
    im = Image.new('RGBA', (W, bh), (0, 0, 0, 0))
    g = np.zeros((bh, W, 4), np.uint8); g[..., :3] = (6, 6, 12)
    g[..., 3] = (np.clip(np.linspace(-0.2, 1, bh), 0, 1) ** 1.4 * 165).astype(np.uint8)[:, None]
    im.alpha_composite(Image.fromarray(g, 'RGBA'))
    d = ImageDraw.Draw(im)
    for i, ln in enumerate(lines):
        y = 38 + i * 48
        d.text((W / 2 + 2, y + 2), ln, font=f, fill=(0, 0, 0, 200), anchor='mt')
        d.text((W / 2, y), ln, font=f, fill=(255, 250, 238, 255), anchor='mt')
    return im

def init_overlays():
    global _caps, _title
    if _caps is None:
        _caps = [(a, b, make_caption(t)) for a, b, t in CAPS]
        f = font('Cinzel.ttf', 22, 600)
        im = Image.new('RGBA', (W, 80), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        txt = 'THE CITY THAT DISAPPEARED WITHOUT A TRACE   ·   PART 1'
        d.text((W / 2 + 2, 32), txt, font=f, fill=(0, 0, 0, 180), anchor='mm'); d.text((W / 2, 30), txt, font=f, fill=(255, 244, 220, 255), anchor='mm')
        d.line([(W / 2 - 220, 54), (W / 2 + 220, 54)], fill=(255, 214, 140, 220), width=2)
        _title = im

def make_frame(i):
    init_overlays()
    t = i / FPS
    img = None
    for k, (a, b, mod, cls) in enumerate(BOUNDS):
        if a - 0.3 <= t <= b + 0.3 and (k == 0 or True):
            op = 1.0 if k == 0 else sstep(a - 0.25, a + 0.25, t)
            if op <= 0: continue
            sc = get_scene(k)
            fr = sc.render(max(t, a - 0.0))
            if img is None: img = fr.copy() if fr.mode == 'RGBA' else fr.convert('RGBA')
            else: img.alpha_composite(fade(fr, op))
    for a, b, cap in _caps:
        al = sstep(a - 0.05, a + 0.25, t) * (1 - sstep(b + 0.1, b + 0.45, t))
        if al > 0: put(img, cap, 0, H - cap.height, al)
    ta = sstep(0.4, 1.2, t) * (1 - sstep(4.2, 5.2, t))
    if ta > 0: put(img, _title, 0, 24, ta)
    arr = np.asarray(img.convert('RGB')).astype(np.float32)
    arr = arr * vignette() + grain(i)
    arr *= sstep(0.0, 0.8, t)
    return np.clip(arr, 0, 255).astype(np.uint8)

def render_chunk(args):
    ci, i0, i1 = args
    out = f'chunks/c{ci:03d}.mp4'
    if os.path.exists(out): return ci
    p = subprocess.Popen([FF, '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', '-g', '48', out + '.tmp.mp4'], stdin=subprocess.PIPE)
    t0 = time.time()
    for i in range(i0, i1):
        p.stdin.write(make_frame(i).tobytes())
    p.stdin.close(); p.wait()
    os.rename(out + '.tmp.mp4', out)
    print(f'chunk {ci} frames {i0}-{i1} done in {time.time() - t0:.1f}s', flush=True)
    return ci

if __name__ == '__main__':
    os.makedirs('chunks', exist_ok=True)
    CH = 96
    jobs = [(c, c * CH, min(N, (c + 1) * CH)) for c in range((N + CH - 1) // CH)]
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        make_frame(int(sys.argv[2]))
        sys.exit()
    with Pool(2) as pool:
        for _ in pool.imap_unordered(render_chunk, jobs): pass
    print('ALL DONE', flush=True)
