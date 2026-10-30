"""Render a week of Dumbbell Dads Club carousels to JPEG.

Usage:  python3 tools/render.py 2026-11-09
Reads   build/<week>/<n>-<Day>.dc.html  (one file per post, same markup as templates/)
Writes  posts/<week>/<n>-<Day>_slide<k>.jpg  (1080x1350, one per <section class="s">)

Fonts (Graduate, Yellowtail, Inter) are pulled from npm @fontsource packages into .fonts/
the first time, because the workspace cannot reach Google Fonts.
"""
import base64, pathlib, re, subprocess, sys
from playwright.sync_api import sync_playwright
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
FONTS = ROOT / '.fonts'
PKGS = {'graduate': ['400'], 'yellowtail': ['400'], 'inter': ['500', '700', '800']}


def ensure_fonts():
    FONTS.mkdir(exist_ok=True)
    for pkg in PKGS:
        if (FONTS / pkg).exists():
            continue
        tgz = subprocess.run(['npm', 'pack', f'@fontsource/{pkg}@5', '-q'], cwd=FONTS,
                             capture_output=True, text=True, check=True).stdout.strip().splitlines()[-1]
        (FONTS / pkg).mkdir()
        subprocess.run(['tar', 'xzf', tgz, '-C', str(FONTS / pkg)], cwd=FONTS, check=True)


def font_css():
    css = ''
    for pkg, weights in PKGS.items():
        fam = {'graduate': 'Graduate', 'yellowtail': 'Yellowtail', 'inter': 'Inter'}[pkg]
        for w in weights:
            p = FONTS / pkg / 'package/files' / f'{pkg}-latin-{w}-normal.woff2'
            b = base64.b64encode(p.read_bytes()).decode()
            css += f"@font-face{{font-family:'{fam}';font-weight:{w};src:url(data:font/woff2;base64,{b})}}"
    return css


def main(week):
    src = ROOT / 'build' / week
    out = ROOT / 'posts' / week
    out.mkdir(parents=True, exist_ok=True)
    ensure_fonts()
    css = font_css()
    problems = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={'width': 1200, 'height': 1400})
        for f in sorted(src.glob('*.dc.html')):
            post_id = f.name.replace('.dc.html', '')
            s = f.read_text()
            s = s.replace('<script src="./support.js"></script>', '')
            s = re.sub(r'<link href="https://fonts[^>]*>', '', s)
            s = re.sub(r'<script type="text/x-dc".*?</script>', '', s, flags=re.S)
            s = s.replace('<style>', f'<style>{css}', 1)
            pg.set_content(s)
            pg.evaluate('document.fonts.ready')
            pg.wait_for_timeout(250)
            for i, el in enumerate(pg.query_selector_all('section.s'), 1):
                over = el.evaluate("""e=>{const r=e.getBoundingClientRect();return [...e.querySelectorAll('*')]
                  .filter(c=>!c.closest('.plate')&&(c.getBoundingClientRect().right>r.right-60||c.getBoundingClientRect().bottom>r.bottom-200))
                  .map(c=>c.className||c.tagName).slice(0,3)}""")
                if over:
                    problems.append(f'{post_id} slide {i}: overflow {over}')
                png = out / f'{post_id}_slide{i}.png'
                el.screenshot(path=str(png))
                Image.open(png).convert('RGB').save(png.with_suffix('.jpg'), quality=88, optimize=True)
                png.unlink()
        b.close()
    print('\n'.join(problems) if problems else 'no overflow')
    print(len(list(out.glob('*.jpg'))), 'slides in', out)


if __name__ == '__main__':
    main(sys.argv[1])
