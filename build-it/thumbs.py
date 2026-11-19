#!/usr/bin/env python3
"""Make the front page's strip picture for a game: open it on a 412 x 732 phone screen, answer sixteen
questions right (as shots.py), then take a picture of the game's MAIN PICTURE only (the locomotive,
the monster, ...), fit it to 5:4 and save it at 200 x 160.
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
    "train": ("#train-photo", "cover", 16),
    "monster": ("#monster", "contain", 16),
    "dino": ("#top-row svg", "cover", 16),
    "robot": ("#robot-stage", "contain", 16),
    "plane": ("#aircraft-photo", "contain", 16),
    "space": ("#planet-image", "cover", 16),
    "chinese": ("#wall-svg", "cover", 16),
    "blocks": ("#world-svg", "cover", 16),
}
W, H = 200, 160
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
        q = pg.locator("#question, #question-text").first.inner_text().strip()
        m = re.search(r"(\d+)\s*[x×]\s*(\d+)", q)
        if not m:
            sys.exit(f"{game}: move {move + 1}: no question found in {q!r}")
        answer = str(int(m[1]) * int(m[2]))
        buttons = pg.locator("#answers button")
        texts = [t.strip().split("\n")[-1].strip() for t in buttons.all_inner_texts()]
        buttons.nth(texts.index(answer)).click()
        try:  # the same question can come twice in a row: then just answer it again
            pg.wait_for_function("q => (document.getElementById('question') || document.getElementById('question-text')).innerText.trim() !== q",
                                 arg=q, timeout=5000)
        except Exception:
            pass
        pg.wait_for_timeout(700)
    pg.wait_for_timeout(1500)
    # A build made from the current gamify.md marks its main picture with id="main-picture";
    # MAIN above is only for older builds.
    if pg.locator("#main-picture").count():
        selector = "#main-picture"
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
