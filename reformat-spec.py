#!/usr/bin/env python3
"""Reformat a build spec so that it is easier for people to read.

Only whitespace changes; every word stays the same and in the same order:
  - Long lines are wrapped, with continuation lines aligned under the text of
    their list item ("- " or "1. ").
  - A blank line goes before each wrapped line, so long items stand apart.
  - A note for human readers at the top of the file is wrapped much narrower,
    so it can be read on a phone when zoomed in.
  - A line is never broken inside a `code span`, an <html tag> or a whole
    <title>...</title>, so one of those can stick out past the width when it
    is longer than a line.
  - Left exactly as they are: lines already short enough, lines that start with
    an HTML tag (exact markup), and BEGIN FILE/END FILE blocks (exact files).

Usage: reformat-spec.py INPUT [OUTPUT] [--width N]
Writes to stdout without an OUTPUT. OUTPUT may be the same file as INPUT.
"""
import argparse
import os
import re
import shutil
import sys

NOTE_START = "NOTE FOR HUMAN READERS"
NOTE_WIDTH = 45
LIST_ITEM = re.compile(r"(\s*)((?:[-*]|\d+\.)\s+)?")
# One unbreakable chunk: any run of whole <title> elements, code spans, HTML tags
# and non-space characters.
CHUNK = re.compile(r"(?:<title>.*?</title>|`[^`]*`|<[a-zA-Z/!][^>]*>|\S)+")
BEGIN_FILE = re.compile(r"^----- BEGIN FILE: (.+) -----$")
# After these the next line already reads as attached: heading underlines,
# "Rules, in order:" and "[TURN 1: ...]".
INTRODUCES_NEXT = re.compile(r"^(?:-+|=+)$|[:\]]$")


def wrap_line(line, width):
    """Return the screen lines for one line of the spec."""
    if len(line) <= width or line.lstrip().startswith("<"):
        return [line]

    match = LIST_ITEM.match(line)
    indent, marker = match.group(1), match.group(2) or ""
    first_prefix = indent + marker
    next_prefix = " " * len(first_prefix)

    lines = []
    current = first_prefix
    has_text = False
    for chunk in CHUNK.findall(line[len(first_prefix):]):
        if has_text and len(current) + 1 + len(chunk) > width:
            lines.append(current)
            current = next_prefix + chunk
        else:
            current += (" " if has_text else "") + chunk
            has_text = True
    lines.append(current)
    return lines


def reformat(text, width):
    out = []
    end_marker = None  # the END FILE line we are looking for, inside a file block
    in_note = text.startswith(NOTE_START)  # the note runs up to the first blank line
    for line in text.split("\n"):
        in_note = in_note and bool(line.strip())
        if in_note:
            out.extend(wrap_line(line, NOTE_WIDTH))
            continue

        if end_marker:
            out.append(line)
            if line == end_marker:
                end_marker = None
            continue

        begin = BEGIN_FILE.match(line)
        if begin:
            end_marker = f"----- END FILE: {begin.group(1)} -----"
            out.append(line)
            continue

        wrapped = wrap_line(line, width)
        if len(wrapped) > 1 and out and out[-1].strip():
            if not INTRODUCES_NEXT.search(out[-1].strip()):
                out.append("")
        out.extend(wrapped)
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(description="Reformat a build spec for human readers.")
    parser.add_argument("input")
    parser.add_argument("output", nargs="?")
    parser.add_argument("--width", type=int, default=100)
    args = parser.parse_args()

    with open(args.input, encoding="utf-8") as f:
        text = f.read()

    result = reformat(text, args.width)
    if result.split() != text.split():
        sys.exit(f"{args.input}: reformatting would change the text; nothing written")

    if args.output:
        # Write a new file and rename it into place, so the web server never
        # serves a half-written or resized copy of the old one. A replaced file
        # keeps its permissions and date: only whitespace changed, so builds and
        # the sitemap must not see it as new.
        tmp = args.output + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(result)
        if os.path.exists(args.output):
            shutil.copystat(args.output, tmp)
        os.replace(tmp, args.output)
    else:
        sys.stdout.write(result)


if __name__ == "__main__":
    main()
