"""Render an animated 9:16 Reel from an HTML timeline.

Usage: python3 tools/reel_anim/build.py <spec.json | page.html> reels/2026-11-09/2-Tue.mp4 [--frames 0.2,1.5]
The page defines window.render(t) and window.TOTAL. Each chunk of the timeline is
captured frame by frame (JPEG piped straight into ffmpeg), chunks are joined with
the concat demuxer, and a silent stereo track is added so the apps accept it.
--frames writes stills at the given seconds instead (for checking layout).
"""
import json, os, pathlib, subprocess, sys, tempfile
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from render import ensure_fonts, font_css  # noqa: E402

FPS = 30

RULES = [
 ('01', ['Plate', 'yours', 'first'], 'Do this', 'Fill your plate before you serve the kids.', 'Use a real plate. Not the pan.'),
 ('02', ['Protein', 'first'], 'Eat in this order', 'Protein first, then the sides. It helps you feel full.', 'Mac and cheese is a side. Always has been.'),
 ('03', ['Leftovers', 'get', 'a', 'lid'], 'Swap', 'Picking at their plate for a container in the fridge.', "Half a grilled cheese is tomorrow's snack."),
 ('04', ['Sit', 'down', 'to', 'eat'], 'The rule', 'Chair. Table. Plate. No standing at the counter.', 'Kids at the table means you at the table.'),
]

NAVY, CREAM, GOLD, PANEL, RED = '#1E2B45', '#F6EEDC', '#F4B41A', '#EADFC6', '#A82A22'
ICONS = {
 1: f'''<svg class="abs pl" width="420" height="420" viewBox="0 0 420 420" style="left:190px;top:0">
   <circle cx="210" cy="210" r="196" fill="#fff" stroke="{NAVY}" stroke-width="14"/>
   <circle cx="210" cy="210" r="140" fill="none" stroke="{PANEL}" stroke-width="10"/>
   <path class="ck" d="M120 215 L185 280 L305 150" fill="none" stroke="{GOLD}" stroke-width="34" stroke-linecap="square" stroke-dasharray="400" stroke-dashoffset="400"/></svg>
   <div class="abs g k" style="left:620px;top:300px;font-size:40px;color:{RED}">You first</div>''',
 2: ''.join(f'''<div class="abs blk i" style="left:{k*270}px;top:140px;width:250px;height:190px;border-radius:10px;
   background:{bg};color:{fg};display:flex;align-items:center;justify-content:center;font-weight:800;font-size:40px;letter-spacing:.04em">{lab}</div>'''
   for k, (lab, bg, fg) in enumerate([('SIDES', PANEL, NAVY), ('SIDES', PANEL, NAVY), ('PROTEIN', NAVY, GOLD)]))
   + f'<div class="abs g one" style="left:-30px;top:20px;font-size:56px;background:{GOLD};color:{NAVY};padding:10px 18px">1st</div>',
 3: f'''<div class="abs tub" style="left:180px;top:150px;width:440px;height:240px;border:14px solid {NAVY};border-top:none;border-radius:0 0 26px 26px;background:#fff">
     <div class="i" style="position:absolute;left:40px;top:70px;font-size:36px;font-weight:700;color:{NAVY}">Half a grilled cheese</div></div>
   <div class="abs lid" style="left:160px;top:110px;width:480px;height:50px;background:{GOLD};border:14px solid {NAVY};border-radius:14px"></div>
   <div class="abs g tag" style="left:560px;top:20px;font-size:38px;background:{RED};color:{CREAM};padding:12px 18px">Tomorrow</div>''',
 4: f'''<svg class="abs chair" width="300" height="420" viewBox="0 0 300 420" style="left:60px;top:0">
     <path d="M60 20 V250 H240 V400 M60 250 V400 M60 170 H240" fill="none" stroke="{NAVY}" stroke-width="22" stroke-linecap="square"/>
     <rect x="50" y="232" width="200" height="34" fill="{GOLD}"/></svg>
   <div class="abs g stand" style="left:400px;top:120px;font-size:72px;color:{NAVY}">Standing
     <div class="strike" style="position:absolute;left:-10px;right:-10px;top:42%;height:14px;background:{RED};transform-origin:left;transform:scaleX(0)"></div></div>
   <div class="abs g ok" style="left:400px;top:240px;font-size:72px;color:{GOLD};-webkit-text-stroke:3px {NAVY}">Sitting</div>''',
}


def rules_html():
    out = []
    for n, (num, words, cap, line, tip) in enumerate(RULES, 1):
        prog = ''.join('<div><i></i></div>' for _ in RULES)
        title = ''.join(f'<span>{w}</span>' for w in words)
        out.append(f'''<div class="scene rule" id="r{n}"><div class="abs wrap" style="width:1080px;height:1920px">
  <div class="abs g ghost">{num}</div>
  <div class="abs g rbrand">Dad Fuel</div>
  <div class="abs prog">{prog}</div>
  <div class="abs g chip">Rule {num}</div>
  <div class="abs g title">{title}</div>
  <div class="abs icon">{ICONS[n]}</div>
  <div class="abs i box"><div class="cap">{cap}</div><div class="line">{line}</div></div>
  <div class="abs i tip"><b>Dad tip:</b> {tip}</div>
</div></div>''')
    return '\n'.join(out)


def page(src):
    ensure_fonts()
    if src.endswith('.json'):  # a spec for the generic engine
        s = (pathlib.Path(__file__).parent / 'engine.html').read_text()
        return s.replace('/*FONTS*/', font_css()).replace('/*SPEC*/', pathlib.Path(src).read_text())
    s = pathlib.Path(src).read_text()
    return s.replace('/*FONTS*/', font_css()).replace('<!--RULES-->', rules_html())


def main():
    src, out = sys.argv[1], sys.argv[2]
    stills = None
    if '--frames' in sys.argv:
        stills = [float(x) for x in sys.argv[sys.argv.index('--frames') + 1].split(',')]
    html = page(src)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={'width': 1080, 'height': 1920})
        pg.set_content(html)
        pg.evaluate('document.fonts.ready')
        pg.wait_for_timeout(300)
        total = pg.evaluate('window.TOTAL')
        if pg.evaluate('typeof window.layout') == 'function':
            print('overflow:', pg.evaluate('layout()') or 'none')
        if stills:
            for t in stills:
                pg.evaluate(f'render({t})')
                pg.screenshot(path=f'{out}_{t:05.2f}.jpg', type='jpeg', quality=90)
            print('stills', stills, 'total', total)
            return
        bounds = json.loads(pg.evaluate('JSON.stringify(window.BOUNDS || [0, 2.7, 2.7+12, TOTAL])'))
        with tempfile.TemporaryDirectory() as td:
            parts = []
            for c in range(len(bounds) - 1):
                part = os.path.join(td, f'c{c}.mp4'); tmp = part + '.part.mp4'
                ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', str(FPS),
                                       '-c:v', 'mjpeg', '-i', '-', '-c:v', 'libx264', '-crf', '18', '-preset', 'veryfast',
                                       '-pix_fmt', 'yuv420p', '-r', str(FPS), tmp], stdin=subprocess.PIPE)
                f0, f1 = round(bounds[c] * FPS), round(bounds[c + 1] * FPS)
                for f in range(f0, f1):
                    pg.evaluate(f'render({f / FPS})')
                    ff.stdin.write(pg.screenshot(type='jpeg', quality=92))
                ff.stdin.close()
                if ff.wait() != 0:
                    raise SystemExit('ffmpeg failed on chunk %d' % c)
                os.replace(tmp, part); parts.append(part)
            lst = os.path.join(td, 'list.txt')
            open(lst, 'w').write(''.join(f"file '{x}'\n" for x in parts))
            joined = os.path.join(td, 'joined.mp4')
            subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', joined], check=True)
            tmp = out + '.part.mp4'
            subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', joined, '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo',
                            '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-shortest', '-movflags', '+faststart', tmp], check=True)
            os.replace(tmp, out)
        b.close()
    print('wrote', out, round(total, 2), 's')


if __name__ == '__main__':
    main()
