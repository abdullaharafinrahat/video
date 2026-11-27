"""
QC pass over a rendered MP4 (no vision needed).
Streams frames (does NOT hold them all in RAM), reports per-shot mean brightness /
saturation / black-frame count, verifies duration & frame count, and dumps a few
sample frames to tests/qc/ for review.
"""
import sys, os, subprocess
import numpy as np
import imageio_ffmpeg
from core import W, H, FPS, NFRAMES
import shots
from PIL import Image

FF = imageio_ffmpeg.get_ffmpeg_exe()


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "five_steps_final.mp4"
    fr = W * H * 3
    cmd = [FF, "-i", path, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    os.makedirs("tests/qc", exist_ok=True)
    samples = {round(tg * FPS) for tg in
               (0.5, 4.0, 6.0, 8.5, 10.5, 12.5, 13.3, 14.2, 15.2, 17.0, 18.5, 19.5)}
    shots_seen = {}
    black = 0
    n = 0
    while True:
        b = p.stdout.read(fr)
        if len(b) < fr:
            break
        f = np.frombuffer(b, np.uint8).reshape(H, W, 3).astype(np.float32) / 255.0
        tg = n / FPS
        cls = shots.shot_for(tg).__name__
        mean = float(f.mean())
        sat = float(f[..., :3].std())
        if mean < 0.004:
            black += 1
        d = shots_seen.setdefault(cls, [])
        d.append((n, round(mean, 3), round(sat, 3)))
        if n in samples:
            Image.fromarray((f * 255).clip(0, 255).astype(np.uint8)).save(
                f"tests/qc/qc_{tg:04.1f}.png")
        n += 1
    p.wait()
    print(f"frames={n}  expected={NFRAMES}  dur={n/FPS:.3f}s")
    print(f"black frames: {black}  (cut-to-black from 19.25s => ~{int((20-19.25)*FPS)})")
    for cls, data in shots_seen.items():
        ms = [x[1] for x in data]
        print(f"  {cls:6s} n={len(data):3d}  bright[{min(ms):.3f}..{max(ms):.3f}]  "
              f"first={data[0][0]} last={data[-1][0]}")
    print(f"sample frames -> tests/qc/ ({len(samples)} saved)")


if __name__ == "__main__":
    main()
