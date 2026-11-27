"""
FIVE STEPS BEHIND — master render.

Each shot is rendered in its OWN subprocess so Python/glibc memory is fully
released between shots (the sandbox cgroup is tight and the cumulative RSS of a
single long-lived process otherwise OOM-kills the heavy Shot6). Segments are
then concatenated into the final MP4 (and audio is muxed by finalize.py).

Worker mode:  python3 render.py --shot Shot6 312 384 seg06.mp4
Master mode:  python3 render.py five_steps.mp4
"""
import sys, time, subprocess, os
sys.path.insert(0, ".")
import numpy as np
from core import W, H, FPS, NFRAMES
from core import post
import imageio_ffmpeg
import shots

FF = imageio_ffmpeg.get_ffmpeg_exe()


def rss_mb():
    try:
        import resource
        return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
    except Exception:
        return 0.0


def write_segment(cls_name, f0, f1, out_path, log_every=12):
    """Render frames [f0, f1) for one shot to a standalone mp4 (rawvideo -> ffmpeg)."""
    cls = getattr(shots, cls_name)
    # low-memory encode: the cgroup limit is shared with the master + ffmpeg +
    # other services, so keep the per-segment encoder tiny (final pass re-encodes).
    cmd = [FF, "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-an",
           "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
           "-threads", "1", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out_path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    import gc
    sh = cls()                      # one shot per process: memory fully released after
    t0 = time.time()
    black = np.zeros((H, W, 3), np.uint8)
    print(f"[{cls_name}] init {time.time()-t0:.2f}s rss={rss_mb():.0f}MB", flush=True)
    for fi in range(f0, f1):
        tg = fi / FPS
        tl = tg - cls.T0
        img, gr = sh.frame(tl, tg, fi)
        frame = post(img, fi, gr) if img is not None else black
        p.stdin.write(frame.tobytes())
        del img, frame
        gc.collect()
        if log_every and (fi - f0) % log_every == 0:
            print(f"  f{fi:3d} {tg:5.2f}s rss={rss_mb():.0f}MB {time.time()-t0:6.1f}s", flush=True)
    p.stdin.close()
    rc = p.wait()
    print(f"[{cls_name}] done rc={rc} {time.time()-t0:.1f}s -> {out_path}", flush=True)
    return rc


def shot_ranges():
    """(name, f0, f1) for every shot in order, covering [0, NFRAMES)."""
    ranges = []
    for cls in shots.SHOTS:
        f0 = int(round(cls.T0 * FPS))
        f1 = int(round(cls.T1 * FPS))
        ranges.append((cls.__name__, f0, f1))
    # ensure full coverage (tuple layout is (name, f0, f1))
    ranges[0] = (ranges[0][0], 0, ranges[0][2])
    ranges[-1] = (ranges[-1][0], ranges[-1][1], NFRAMES)
    return ranges


def master(out_path):
    segs = []
    for i, (name, f0, f1) in enumerate(shot_ranges()):
        seg = f"tests/seg_{i:02d}_{name}.mp4"
        print(f"=== shot {i} {name} frames {f0}..{f1} -> {seg} ===", flush=True)
        # spawn a SEPARATE process per shot so memory fully resets between shots
        rc = subprocess.run([sys.executable, os.path.abspath(__file__),
                             "--shot", name, str(f0), str(f1), seg],
                            stderr=subprocess.STDOUT).returncode
        if rc != 0:
            raise SystemExit(f"segment {name} failed rc={rc}")
        segs.append(seg)
    # concatenate
    lst = "tests/seg_list.txt"
    with open(lst, "w") as f:
        for s in segs:
            f.write(f"file '{os.path.abspath(s)}'\n")
    cmd = [FF, "-y", "-f", "concat", "-safe", "0", "-i", lst,
           "-c:v", "libx264", "-preset", "slower", "-crf", "16",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", out_path]
    print("concat ->", out_path, flush=True)
    r = subprocess.run(cmd, stderr=subprocess.PIPE)
    if r.returncode != 0:
        print(r.stderr.decode(errors="ignore")[-2000:])
        raise SystemExit("concat failed")
    print("FINAL", out_path, flush=True)


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "--shot":
        # worker: --shot <Name> <f0> <f1> <out>
        rc = write_segment(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5])
        sys.exit(rc)
    out = sys.argv[1] if len(sys.argv) > 1 else "five_steps.mp4"
    master(out)
