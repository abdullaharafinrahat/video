import sys, os, json, time, subprocess, traceback, importlib
import numpy as np
from PIL import Image
import timing as T
from engine import *
import imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
SCENES = {}
for m in ('scenes_a', 'scenes_b', 'scenes_c'):
    try: SCENES.update(importlib.import_module(m).SC)
    except ModuleNotFoundError: pass
NF = int(round(T.TOTAL * 30)); CH = 300
def frame(fi, log=True):
    a = fi / 30.0; n = T.scene_of(a); t0, t1 = T.scene(n); k = K(n, a - t0, fi)
    try:
        c = SCENES[n](k)
    except Exception as e:
        if log: open('out/errors.log', 'a').write(f'scene {n} frame {fi}: {traceback.format_exc()}\n')
        c = Canvas(P['navy'], 'E'); c.hud(); c.text(640, 300, f'scene {n}', 40, P['cream'], 'sans', 'c'); k.fx = {}
    kind_in = INTO.get(n, 'cut'); kind_out = INTO.get(n + 1, 'cut')
    tr = None
    if a - t0 < .2 and kind_in not in ('cut',):
        sign = 1 if n % 2 else -1; tr = lambda im: trans_fx(im, kind_in, (a - t0) / .2, False, sign)
    elif t1 - a < .2 and kind_out not in ('cut',):
        sign = 1 if (n + 1) % 2 else -1; tr = lambda im: trans_fx(im, kind_out, 1 - (t1 - a) / .2, True, sign)
    img = finish_frame(k, c, tr)
    if n < 46: img = captions(img, a)
    return img

def render_chunk(ci):
    out = f'out/seg_{ci:04d}.mp4'
    if os.path.exists(out): return
    f0 = ci * CH; f1 = min(NF, f0 + CH)
    p = subprocess.Popen([FF, '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1280x720', '-r', '30', '-i', '-',
                          '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', '-g', '30', '-bf', '0', f'out/tmp_{ci:04d}.mp4'], stdin=subprocess.PIPE)
    for fi in range(f0, f1):
        p.stdin.write(frame(fi).tobytes())
    p.stdin.close(); p.wait(); os.rename(f'out/tmp_{ci:04d}.mp4', out)

def worker(wid, nw):
    nch = (NF + CH - 1) // CH
    for ci in range(nch):
        if ci % nw != wid: continue
        t = time.time(); render_chunk(ci)
        done = len([f for f in os.listdir('out') if f.startswith('seg_')])
        json.dump(dict(done=done, total=nch, last_chunk=ci, secs=round(time.time() - t, 1), t=time.time()), open(f'out/progress_{wid}.json', 'w'))

def sheet(a, b, name):
    from PIL import ImageDraw
    rows = []
    for n in range(a, b + 1):
        t0, t1 = T.scene(n); d = t1 - t0; ims = []
        for f in (.04, .33, .66, .97):
            fi = int((t0 + d * f) * 30); ims.append(frame(fi, log=True).resize((320, 180)))
        row = Image.new('RGB', (1280, 180))
        for i, im in enumerate(ims): row.paste(im, (i * 320, 0))
        ImageDraw.Draw(row).text((4, 4), f'S{n}', fill=(255, 255, 0)); rows.append(row)
    S = Image.new('RGB', (1280, 180 * len(rows)))
    for i, r in enumerate(rows): S.paste(r, (0, i * 180))
    S.save(f'prev/{name}.png')

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'sheet': sheet(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
    elif cmd == 'frame':
        frame(int(float(sys.argv[2]) * 30)).save(f'prev/{sys.argv[3]}.png')
    elif cmd == 'worker': worker(int(sys.argv[2]), int(sys.argv[3]))
    elif cmd == 'time':
        t = time.time(); [frame(int(x) * 30) for x in sys.argv[2:]]; print((time.time() - t) / (len(sys.argv) - 2), 's/frame')
