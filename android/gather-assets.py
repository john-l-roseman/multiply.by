#!/usr/bin/env python3
"""Copies the multiply.by pages the app bundles into OUT (the app's assets folder).

Usage: python3 gather-assets.py [--web] [OUT]

OUT defaults to app/src/main/assets/site (next to this script). The pages come from the site's
web folder when this script runs inside it (on the multiply.by server), otherwise, or with --web,
they are downloaded from https://multiply.by: the built pages are not in the git repo.

Starts from the front page (/) and the chooser (/games/) and follows every link to a page or file
on https://multiply.by that exists, so a new game reaches the app as soon as the front page or
/games/ links to it. Pages that carry (or will carry) ads, and pages that are not for children,
are never bundled: the app sends them to the browser behind the parental gate.
Writes OUT/files.txt, the list the app serves from.
"""
import os
import posixpath
import re
import shutil
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
URL = "https://multiply.by"
START = ["/", "/games/"]
# Never bundled: About and Build It (ads planned), the build guide, the service worker, these notes.
EXCLUDE = ("/about", "/build-it/index.html", "/build-it/prompt.txt", "/gamify", "/sw.js",
           "/FAQ", "/faq", "/android", "/ANDROID")

ABS = re.compile(r"https://multiply\.by(/[A-Za-z0-9._/-]*)")
ROOT = re.compile(r"""["'](/[A-Za-z0-9_-][A-Za-z0-9._/-]*\.(?:png|svg|jpg|webp|js|txt|webmanifest|json|mp3|ogg|wav))["']""")
LINK = re.compile(r"""(?:href|src)=["'](/[A-Za-z0-9._/-]*)["']""")
RELATIVE = re.compile(r"""(?:href|src)=["']([A-Za-z0-9_-][A-Za-z0-9._-]*\.(?:txt|png|svg|js))["']""")


class Local:
    """The site's web folder, on the multiply.by server."""
    name = SITE

    def get(self, path):
        full = os.path.join(SITE, path.lstrip("/"))
        if not os.path.isfile(full):
            return None
        with open(full, "rb") as f:
            return f.read()


class Web:
    """The live site, for anyone building from a clone of the repo."""
    name = URL

    def __init__(self):
        self.cache = {}

    def get(self, path):
        if path not in self.cache:
            req = urllib.request.Request(URL + path, headers={"User-Agent": "gather-assets"})
            try:
                with urllib.request.urlopen(req, timeout=30) as r:
                    self.cache[path] = r.read()
            except urllib.error.HTTPError as e:
                if e.code != 404:
                    raise
                self.cache[path] = None
        return self.cache[path]


def main():
    args = sys.argv[1:]
    web = "--web" in args
    args = [a for a in args if a != "--web"]
    if len(args) > 1 or any(a.startswith("-") for a in args):
        sys.exit(__doc__)
    out = args[0] if args else os.path.join(HERE, "app", "src", "main", "assets", "site")
    on_server = os.path.isfile(os.path.join(SITE, "index.html")) and os.path.isfile(
        os.path.join(SITE, "games", "index.html"))
    source = Web() if web or not on_server else Local()
    print(f"gathering from {source.name}")

    def resolve(path):
        """(site path of the file, its bytes), or None if excluded or not on the site."""
        if re.search(r"(^|/)\.\.?(/|$)", path):  # "/." or "/a/../b/": a folder
            path = posixpath.normpath(path).rstrip("/") + "/"
        if path.endswith("/"):
            path += "index.html"
        elif "." not in path.rsplit("/", 1)[-1]:
            path += "/index.html"            # "/train" is the folder /train/
        if any(path.startswith(e) for e in EXCLUDE):
            return None
        data = source.get(path)
        return None if data is None else (path, data)

    found, queue, missing = {}, list(START), set()
    while queue:
        ref = queue.pop()
        hit = resolve(ref)
        if hit is None:
            if not any(ref.startswith(e) for e in EXCLUDE):
                missing.add(ref)
            continue
        path, data = hit
        if path in found:
            continue
        found[path] = data
        if not path.endswith(".html"):
            continue
        html = data.decode("utf-8")
        folder = path.rsplit("/", 1)[0] + "/"
        queue += ABS.findall(html) + ROOT.findall(html) + LINK.findall(html)
        queue += [folder + r for r in RELATIVE.findall(html)]

    if os.path.isdir(out):
        shutil.rmtree(out)
    for path, data in found.items():
        dest = os.path.join(out, path.lstrip("/"))
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "wb") as f:
            f.write(data)
    with open(os.path.join(out, "files.txt"), "w") as f:
        f.write("".join(p.lstrip("/") + "\n" for p in sorted(found)))

    total = sum(len(d) for d in found.values())
    pages = sorted(p[:-10] for p in found if p.endswith("index.html"))
    print(f"{len(found)} files, {total:,} bytes, in {out}")
    print("pages: " + " ".join(pages))
    if missing:
        print("linked but not on the site (the app will gate or 404 them): "
              + " ".join(sorted(missing)))


if __name__ == "__main__":
    main()
