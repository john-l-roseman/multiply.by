#!/usr/bin/env python3
"""Make the front page's strip picture for a game: open it on a 412 x 732 phone screen, answer three
questions right (as shots.py), then take a picture of the game's MAIN PICTURE only (the locomotive,
the monster, ...; for the robot, a finished robot), fit it to 5:4 and save it at 200 x 160.
The Makefile makes a thumbnail only when thumbnails/GAME-thumbnail.png is missing, so a hand-made
one put there is kept; delete a file to make it again.
Usage: thumbs.py GAME OUT.png"""
import io, re, sys
from PIL import Image
from playwright.sync_api import sync_playwright

# The main picture of each game (a CSS selector), chosen by looking at each live page; how it
# fits 5:4 ("cover": cropped around its centre; "contain": whole, the sides filled with the colour
# of its top-left corner); and how many right answers come first.
MAIN = {
    "train": ("#train-photo", "cover", 3),
    "monster": ("#munch", "contain", 3),
    "dino": ("#top-row svg", "cover", 3),
    "robot": ("#thumb", "contain", 0),  # see ROBOT below
    "plane": ("#aircraft-image", "cover", 3),
    "space": ("#scene-image", "cover", 3),
    "chinese": ("#builder", "cover", 3),
}
W, H = 200, 160
# The robot is built one part per learned fact, so a finished robot only appears late in a game.
# The game draws finished robots with its own buildMiniRobotSvg(stage, parts, powered, dancing)
# (for its hangar): draw the last stage's robot, the giant mech, complete, cropped tight.
ROBOT = """() => {
  const d = document.createElement('div'); d.id = 'thumb';
  d.style.cssText = 'position:fixed;left:0;top:0;width:250px;height:200px;z-index:99999;' +
    'background:#eff6ff;display:flex;align-items:center;justify-content:center';
  d.innerHTML = buildMiniRobotSvg(3, new Set([...Array(12).keys()]), true, false);
  document.body.appendChild(d);
  const svg = d.querySelector('svg'), b = svg.getBBox(), pad = 6;
  svg.setAttribute('viewBox', [b.x - pad, b.y - pad, b.width + 2 * pad, b.height + 2 * pad].join(' '));
  svg.style.width = '240px'; svg.style.height = '192px';
}"""

game, out = sys.argv[1], sys.argv[2]
with sync_playwright() as p:
    browser = p.chromium.launch()
    ctx = browser.new_context(viewport={"width": 412, "height": 732}, device_scale_factor=3,
                              has_touch=True)
    pg = ctx.new_page()
    pg.goto(f"https://multiply.by/{game}/", wait_until="networkidle")
    pg.wait_for_timeout(500)
    selector, fit, answers = MAIN[game]
    for move in range(answers):
        q = pg.locator("#question").inner_text().strip()
        m = re.search(r"(\d+)\s*[x×]\s*(\d+)", q)
        if not m:
            sys.exit(f"{game}: no question found in {q!r}")
        answer = str(int(m[1]) * int(m[2]))
        buttons = pg.locator("#answers button")
        texts = [t.strip() for t in buttons.all_inner_texts()]
        buttons.nth(texts.index(answer)).click()
        pg.wait_for_function("q => document.getElementById('question').innerText.trim() !== q",
                             arg=q, timeout=5000)
        pg.wait_for_timeout(700)
    pg.wait_for_timeout(1500)
    if game == "robot":
        pg.evaluate(ROBOT)
    # Hide whatever floats over the picture (labels, badges, points), but not the picture itself,
    # what is inside it, or what it sits in.
    pg.evaluate("""sel => {
      const main = document.querySelector(sel), m = main.getBoundingClientRect();
      for (const e of document.body.querySelectorAll('*')) {
        if (e === main || main.contains(e) || e.contains(main)) continue;
        const pos = getComputedStyle(e).position;
        if (pos !== 'absolute' && pos !== 'fixed' && pos !== 'sticky') continue;
        const r = e.getBoundingClientRect();
        if (r.right > m.left && r.left < m.right && r.bottom > m.top && r.top < m.bottom)
          e.style.visibility = 'hidden';
      }
    }""", selector)
    pg.wait_for_timeout(200)
    shot = Image.open(io.BytesIO(pg.locator(selector).first.screenshot())).convert("RGB")
    browser.close()

w, h = shot.size
if fit == "contain":
    # The whole picture, centred on a 5:4 canvas of its corner colour.
    cw, ch = max(w, round(h * W / H)), max(h, round(w * H / W))
    canvas = Image.new("RGB", (cw, ch), shot.getpixel((2, 2)))
    canvas.paste(shot, ((cw - w) // 2, (ch - h) // 2))
    shot, w, h = canvas, cw, ch
# Crop to 5:4 around the centre (cover), then size to W x H.
if w / h > W / H:
    nw = round(h * W / H)
    shot = shot.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
else:
    nh = round(w * H / W)
    shot = shot.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
# 256 colours: half the size or less, no visible loss at this size.
shot = shot.resize((W, H), Image.LANCZOS)
shot.quantize(256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG).save(
    out, "PNG", optimize=True)
print(f"{game}: {out}")
