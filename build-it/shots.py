#!/usr/bin/env python3
"""Screenshot a game for the Build it page and the front page: open it on a 412 x 732 phone screen,
answer three questions right, let the animations settle, and keep only the game's own scene: from
just below the menu bar to just above the answer buttons (the title band, menu, answers and footer
look the same in every game). The scene is fitted onto one fixed shape, 412 x 330 (saved at twice
that, 824 x 660, for sharp phone screens): a shorter scene sits at the top and the rest is filled
with the game's background colour; a taller one is scaled down to fit, centred.
Usage: shots.py GAME OUT.png   (GAME is the folder, e.g. train: https://multiply.by/train/,
or base for the base game at https://multiply.by/base/)"""
import io, re, sys
from PIL import Image
from playwright.sync_api import sync_playwright

game, out = sys.argv[1], sys.argv[2]
url = "https://multiply.by/base/" if game == "base" else f"https://multiply.by/{game}/"

def question(pg):
    return pg.locator("#question").inner_text().strip()

with sync_playwright() as p:
    browser = p.chromium.launch()
    # A fresh context each time: no saved progress, so every game starts from the beginning.
    ctx = browser.new_context(viewport={"width": 412, "height": 732}, device_scale_factor=2,
                              has_touch=True)
    pg = ctx.new_page()
    pg.goto(url, wait_until="networkidle")
    pg.wait_for_timeout(500)
    for move in range(3):
        q = question(pg)
        m = re.search(r"(\d+)\s*[x×]\s*(\d+)", q)
        if not m:
            sys.exit(f"{game}: no question found in {q!r}")
        answer = str(int(m[1]) * int(m[2]))
        buttons = pg.locator("#answers button")
        texts = [t.strip() for t in buttons.all_inner_texts()]
        if answer not in texts:
            sys.exit(f"{game}: answer {answer} not among {texts}")
        buttons.nth(texts.index(answer)).click()
        pg.wait_for_function("q => document.getElementById('question').innerText.trim() !== q",
                             arg=q, timeout=5000)
        pg.wait_for_timeout(700)
    pg.wait_for_timeout(1500)
    top, bottom = pg.evaluate("""() => [document.getElementById('menu-bar').getBoundingClientRect().bottom,
                                        document.getElementById('answers').getBoundingClientRect().top]""")
    shot = Image.open(io.BytesIO(pg.screenshot())).convert("RGB")
    browser.close()

W, H, SCALE = 412, 330, 2
scene = shot.crop((0, round(top * SCALE), W * SCALE, round(bottom * SCALE) - 2 * SCALE))
if scene.height < 50 * SCALE:
    sys.exit(f"{game}: the scene between the menu and the answers is only {scene.height} pixels")
# The background: the colour just below the scene's bottom-left corner, in the game's own page.
fill = shot.getpixel((4 * SCALE, round(bottom * SCALE) - 3 * SCALE))
canvas = Image.new("RGB", (W * SCALE, H * SCALE), fill)
if scene.height > H * SCALE:
    scene = scene.resize((round(scene.width * H * SCALE / scene.height), H * SCALE), Image.LANCZOS)
canvas.paste(scene, ((W * SCALE - scene.width) // 2, 0))
canvas.save(out, "PNG", optimize=True)
print(f"{game}: {out}")
