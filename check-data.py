#!/usr/bin/env python3
"""Check the facts list (RAW_DATA) in a built page before it goes live.

Usage: check-data.py PAGE.html
The page must hold exactly the 48 facts of the spec: the 2 to 9 tables, 11 x 11
and the 12 times table, smaller number first, with number ids 1 to 48 and the
right answers. Exits non-zero otherwise, so make stops before the page goes live.
"""
import json
import re
import sys

page = sys.argv[1]
html = open(page, encoding="utf-8").read()
m = re.search(r"const RAW_DATA = (\[.*?\]);", html, re.S)
if not m:
    sys.exit(f"{page}: no 'const RAW_DATA = [...];' found")
try:
    data = json.loads(m.group(1))
except ValueError as e:
    sys.exit(f"{page}: RAW_DATA is not valid JSON: {e}")

want = [f"{a} x {b}" for a in range(2, 13) for b in range(a, 13)
        if b <= 9 or b == 12 or (a == 11 and b == 11)]
problems = []
if [f.get("id") for f in data] != list(range(1, len(data) + 1)):
    problems.append("ids are not the numbers 1, 2, 3, ... in order")
texts = [f.get("text") for f in data]
missing = [t for t in want if t not in texts]
extra = [t for t in texts if t not in want]
if missing:
    problems.append("missing facts: " + ", ".join(missing))
if extra:
    problems.append("unexpected facts: " + ", ".join(map(str, extra)))
if len(texts) != len(set(texts)):
    problems.append("repeated facts")
for f in data:
    t, a = f.get("text"), f.get("answer")
    if t in want and a != str(eval(t.replace("x", "*"))):
        problems.append(f"wrong answer: {t} = {a!r}")
if problems:
    print(f"{page}: RAW_DATA has problems:", file=sys.stderr)
    for p in problems:
        print("  " + p, file=sys.stderr)
    sys.exit(1)
print(f"{page}: RAW_DATA OK ({len(data)} facts)")
