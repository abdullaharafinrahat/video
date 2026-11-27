"""
Finalize: mux the rendered silent MP4 with the WAV score, then QC the result
and build a contact sheet from sampled frames.
"""
import sys, subprocess, os
import numpy as np
import imageio_ffmpeg
from core import W, H, FPS, NFRAMES
from PIL import Image

FF = imageio_ffmpeg.get_ffmpeg_exe()


def mux(video, audio, out):
    # copy video (already H.264), encode audio to AAC
    cmd = [FF, "-y", "-i", video, "-i", audio,
           "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
           "-movflags", "+faststart", out]
    print("mux:", " ".join(cmd))
    r = subprocess.run(cmd, stderr=subprocess.PIPE)
    if r.returncode != 0:
        print(r.stderr.decode(errors="ignore")[-1500:])
        raise SystemExit("mux failed")
    print("wrote", out)


def decode_frames(path, tgs):
    cmd = [FF, "-i", path, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    fr = W * H * 3
    want = {int(tg * FPS): tg for tg in tgs}
    out = {}
    i = 0
    while True:
        b = p.stdout.read(fr)
        if len(b) < fr:
            break
        if i in want:
            out[want[i]] = np.frombuffer(b, np.uint8).reshape(H, W, 3)
        i += 1
    p.wait()
    return out


def build_contact(frames, out="docs/contact_sheet.png"):
    tgs = sorted(frames)
    cols = 4
    rows = (len(tgs) + cols - 1) // cols
    tw, th = W // 3, H // 3
    sheet = Image.new("RGB", (cols * tw, rows * th), (20, 20, 24))
    for k, tg in enumerate(tgs):
        im = Image.fromarray(frames[tg]).resize((tw, th), Image.LANCZOS)
        x = (k % cols) * tw
        y = (k // cols) * th
        sheet.paste(im, (x, y))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    sheet.save(out)
    print("contact sheet ->", out)


def main():
    video = sys.argv[1] if len(sys.argv) > 1 else "five_steps.mp4"
    audio = sys.argv[2] if len(sys.argv) > 2 else "five_steps.wav"
    final = sys.argv[3] if len(sys.argv) > 3 else "five_steps_final.mp4"
    mux(video, audio, final)
    tgs = [0.5, 1.5, 4.0, 6.0, 8.5, 10.5, 12.5, 13.3, 14.2, 15.2, 17.0, 18.5, 19.5]
    frames = decode_frames(final, tgs)
    build_contact(frames)
    print("QC: frames decoded", len(frames), "of", len(tgs))


if __name__ == "__main__":
    main()
