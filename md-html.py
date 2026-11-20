#!/usr/bin/env python3
"""Render a Markdown file as one plain, self-contained web page.

Usage: md-html.py FILE.md > DIR/index.html

Used for /android/ (from ANDROID.md). The Markdown is rendered by markdown-it (the Debian package
python3-markdown-it), CommonMark plus tables; any HTML written in the file is shown as text, never
used as markup. The page title is the file's first "# " heading.
"""
import html
import re
import sys

from markdown_it import MarkdownIt

text = open(sys.argv[1], encoding="utf-8").read()
m = re.search(r"^# (.+)$", text, flags=re.M)
title = m.group(1).strip() if m else "multiply.by"

STYLE = """
body { margin: 0 auto; max-width: 52rem; padding: 1rem 16px 3rem; background: #fff; color: #1a1a1a;
  font: 16px/1.55 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; overflow-wrap: anywhere; }
h1, h2, h3 { line-height: 1.25; margin: 1.6em 0 0.5em; }
a { color: #1e40af; }
code { font: 0.9em ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; background: #f3f3f3;
  padding: 0.1em 0.3em; border-radius: 3px; }
pre { background: #f6f6f6; border: 1px solid #e3e3e3; border-radius: 6px; padding: 0.8em 1em;
  overflow-x: auto; font: 0.85em/1.45 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
pre code { background: none; padding: 0; font: inherit; }
table { border-collapse: collapse; margin: 0.5em 0 1em; display: block; overflow-x: auto; }
th, td { border: 1px solid #e3e3e3; padding: 0.3em 0.6em; text-align: left; vertical-align: top; }
th { background: #f6f6f6; }
@media (prefers-color-scheme: dark) {
  body { background: #161616; color: #e6e6e6; }
  a { color: #93c5fd; }
  code, pre, th { background: #222; }
  pre, th, td { border-color: #333; }
}
"""
body = MarkdownIt("commonmark", {"html": False}).enable("table").render(text)
sys.stdout.write(
    '<!doctype html>\n<html lang="en">\n<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    '<link rel="icon" type="image/svg+xml" href="/icon.svg">\n'
    f"<title>{html.escape(title)}</title>\n<style>{STYLE}</style>\n{body}</html>\n")
