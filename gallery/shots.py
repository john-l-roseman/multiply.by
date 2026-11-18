#!/usr/bin/env python3
"""Screenshot a game for the gallery: open it on a 412 x 732 phone screen (wide enough for the copyright line
to fit on one line), answer three
questions right, let the animations settle, and save a PNG.
Usage: shots.py GAME OUT.png   (GAME is the folder, e.g. train: https://multiply.by/train/,
or base for the base game at https://multiply.by/)"""
import re, sys
from playwright.sync_api import sync_playwright

game, out = sys.argv[1], sys.argv[2]
# "base" is the base game, at the site's root.
url = "https://multiply.by/" if game == "base" else f"https://multiply.by/{game}/"

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
    pg.screenshot(path=out)
    browser.close()
print(f"{game}: {out}")
