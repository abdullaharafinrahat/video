import sys, subprocess, time, os
from gfx import *
import scenes_all as SA
import imageio_ffmpeg

FPS = 24
START, END = 189.5, 364.3
NF = int(round((END - START) * FPS))
part, nparts = int(sys.argv[1]), int(sys.argv[2])
limit = int(sys.argv[3]) if len(sys.argv) > 3 else None
a = NF * part // nparts
b = NF * (part + 1) // nparts
if limit:
    b = min(b, a + limit)
caps = load_captions(START - 0.1, END)
TIMES = SA.TIMES
cache = {}


def scene_for(T):
    for n, (s, e) in TIMES.items():
        if s <= T < e:
            return n
    return 32


def get(n):
    if n not in cache:
        cache.clear()
        cache[n] = SA.CLASSES[n](*TIMES[n])
    return cache[n]


TITLES = {19: 'The Helike Project', 20: 'Searching the Seabed', 21: 'Nothing?', 22: 'A New Theory', 23: 'A Different Search',
          24: 'Something is Buried', 25: 'The First Discovery', 26: 'The Clues', 27: 'The Catch', 28: 'Not Every Ruin is Helike',
          29: 'The Mystery Gets Bigger', 30: 'Was the Story True?', 31: 'The 2021 Study', 32: 'The Unexpected Twist'}
ff = imageio_ffmpeg.get_ffmpeg_exe()
out = f'seg_{part}.mp4'
p = subprocess.Popen([ff, '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{LW}x{LH}', '-r', str(FPS), '-i', '-',
                      '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
t0 = time.time()
for f in range(a, b):
    T = START + f / FPS
    n = scene_for(T)
    sc = get(n)
    t = T - sc.start
    im, (cx, cy, z) = sc.draw(t)
    v = camera(im, cx, cy, z)
    fin = 0.6 if n == 19 else 0.3
    fade = min(1.0, t / fin, (sc.end - T) / 0.28)
    if n == 32:
        fade = min(fade, (END - T) / 1.1)
    fade = clamp(0.0 + fade) ** 0.8
    v = post(v, T, fade, sc.warm)
    # overlays
    ta = ease(seg(t, 0.3, 0.9)) * (1 - ease(seg(t, 3.6, 4.2)))
    if ta > 0:
        spr = banner(f'{n}. {TITLES[n]}', size=27, seed=n)
        paste_over(v, spr, 24 - (1 - ta) * 60, 20, ta)
    if n == 19:
        pa = ease(seg(t, 0.4, 1.2)) * (1 - ease(seg(t, 6.4, 7.2)))
        if pa > 0:
            spr = banner('Part 2: The Investigation', 'Scenes 19 – 32', size=30, seed=40)
            paste_over(v, spr, LW - spr.size[0] - 24 + (1 - pa) * 60, 20, pa)
        l1 = ease(seg(t, 4.3, 4.9)) * (1 - ease(seg(t, 6.8, 7.2)))
        if l1 > 0:
            lower_third(v, 'Dr. Dora Katsonopoulou', 'Archaeologist', l1)
        l2 = ease(seg(t, 7.0, 7.6)) * (1 - ease(seg(t, 9.8, 10.3)))
        if l2 > 0:
            lower_third(v, 'Steven Soter', 'Physicist', l2)
    cf = fade
    draw_caption(v, caps, T, cf)
    p.stdin.write(v.tobytes())
    if (f - a) % 100 == 0:
        print(part, f - a, b - a, round(time.time() - t0), flush=True)
p.stdin.close()
p.wait()
print('done', part, round(time.time() - t0), flush=True)
