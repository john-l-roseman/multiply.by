#!/usr/bin/env python3
"""Write sitemap.xml for https://multiply.by/ to standard output: one <url> per public page, its
<lastmod> the date its file last changed (so a rebuild updates it). Run by make.
Pages are listed by hand below: the model-comparison copies (e.g. /train/carbon/) are left out on
purpose, and a new game is added here."""
import os, sys, time

SITE = "https://multiply.by/"
ROOT = os.path.dirname(os.path.abspath(__file__))
# (path, the file served there, priority)
PAGES = [
    ("", "index.html", "1.0"),             # the front page: the game with the strip of games
    ("games/", "games/index.html", "0.9"),
    ("monster/", "monster/index.html", "0.8"),
    ("train/", "train/index.html", "0.8"),
    ("dino/", "dino/index.html", "0.8"),
    ("robot/", "robot/index.html", "0.8"),
    ("plane/", "plane/index.html", "0.8"),
    ("space/", "space/index.html", "0.8"),
    ("chinese/", "chinese/index.html", "0.8"),
    ("blocks/", "blocks/index.html", "0.8"),
    ("base/", "base/index.html", "0.7"),
    ("divide/", "divide/index.html", "0.7"),
    ("build-it/", "build-it/index.html", "0.6"),
    ("about/", "about/index.html", "0.5"),
    ("match/", "match/index.html", "0.3"),
    ("gamify/", "gamify/index.html", "0.5"),  # the same as a page (Gemini takes .html, not .txt)
    ("gamify.txt", "gamify.txt", "0.5"),  # one file for building a gamified game in any chatbot
]

out = ['<?xml version="1.0" encoding="UTF-8"?>',
       '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for path, file, priority in PAGES:
    page = os.path.join(ROOT, file)
    if not os.path.isfile(page):
        sys.exit(f"make-sitemap: {page} is missing")
    lastmod = time.strftime("%Y-%m-%d", time.gmtime(os.path.getmtime(page)))
    out += ["  <url>", f"    <loc>{SITE}{path}</loc>", f"    <lastmod>{lastmod}</lastmod>",
            f"    <priority>{priority}</priority>", "  </url>"]
out.append("</urlset>")
print("\n".join(out))
