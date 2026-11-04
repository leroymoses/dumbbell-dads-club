"""Turn one carousel's slides into a 9:16 Instagram Reel.

Usage:  python3 tools/render_reel.py OUT.mp4 slide1.jpg slide2.jpg ...
Each 4:5 slide sits centered on a 1080x1920 navy frame (inside Instagram's
safe area), with a slow push-in. Hook 2.0 s, middle slides 3.0 s (time to
read), last slide 2.5 s. Hard cuts. Silent audio track so Leroy can add a
trending sound in the Instagram app.
"""
import os, subprocess, sys, tempfile
from PIL import Image

NAVY = (0x1E, 0x2B, 0x45)
W, H, FPS = 1080, 1920, 30


def frame(src, dst):
    bg = Image.new('RGB', (W, H), NAVY)
    s = Image.open(src).convert('RGB').resize((1080, 1350), Image.LANCZOS)
    bg.paste(s, (0, (H - 1350) // 2 - 60))  # a little above center: IG covers the bottom
    bg.save(dst, quality=92)


def scene(img, secs, out):
    n = int(round(secs * FPS))
    tmp = out + '.part.mp4'
    vf = (f"scale={W*2}:{H*2},zoompan=z='1+0.035*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
          f":d={n}:s={W}x{H}:fps={FPS},format=yuv420p")
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', img, '-vf', vf, '-frames:v', str(n),
                    '-c:v', 'libx264', '-crf', '18', '-preset', 'veryfast', '-pix_fmt', 'yuv420p',
                    '-r', str(FPS), tmp], check=True)
    os.replace(tmp, out)


def main(out, slides):
    with tempfile.TemporaryDirectory() as td:
        parts = []
        for i, s in enumerate(slides):
            f = os.path.join(td, f'f{i}.jpg'); frame(s, f)
            secs = 2.0 if i == 0 else (2.5 if i == len(slides) - 1 else 3.0)
            p = os.path.join(td, f's{i}.mp4'); scene(f, secs, p); parts.append(p)
        lst = os.path.join(td, 'list.txt')
        open(lst, 'w').write(''.join(f"file '{p}'\n" for p in parts))
        joined = os.path.join(td, 'joined.mp4')
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', joined], check=True)
        tmp = out + '.part.mp4'
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', joined, '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo',
                        '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-shortest', '-movflags', '+faststart', tmp], check=True)
        os.replace(tmp, out)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2:])
