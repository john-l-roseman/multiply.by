#!/usr/bin/env python3
"""Make gamify.txt: ONE self-contained file for building a gamified game in any chatbot.

Usage: gamify-txt.py gamify.md base/prompt.txt > gamify.txt

It is a short note for human readers, then gamify.md turned into the plain-text style of the
site's specs (Markdown headings become UPPERCASE headings, code fences are dropped), then the base
build instructions, copied unchanged. A person uploads it with a line or two saying what game they
want, and needs nothing from the web.
"""
import re
import sys

guide, base = (open(p, encoding="utf-8").read() for p in sys.argv[1:3])
if not base.startswith("NOTE FOR HUMAN R"):
    sys.exit(f"{sys.argv[2]} does not start with the Note for Human Readers")

NOTE = """NOTE FOR HUMAN READERS (the person reading
this file, not the AI building the game):
To build your own gamified version of the
multiply.by times-tables game, upload this
file to your favorite chatbot, add a line or
two saying what game you want (for example:
"a train game, from steam engines to maglev,
for 8-year-olds"), and download the index.html
it produces. Open it in your browser to play.
"""


def heading(text, rule):
    text = text.upper()
    return f"{text}\n{rule * len(text)}" if rule else text


out = []
for line in guide.splitlines():
    if line.startswith("```"):
        continue  # code fences: the code inside stays, indented as it is
    m = re.match(r"(#{1,3}) (.*)", line)
    if m:
        level, text = len(m[1]), m[2]
        line = heading(text, {1: "=", 2: "-", 3: ""}[level])
    out.append(line)

sys.stdout.write(NOTE + "\n\n" + "\n".join(out).strip() + "\n\n\n"
                 + heading("The base build instructions", "=") + "\n"
                 + "The complete base build instructions (https://multiply.by/base/prompt.txt),\n"
                 + "copied unchanged. Everything from here to the end of this file is that one file.\n\n"
                 + base)
