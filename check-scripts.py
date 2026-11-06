#!/usr/bin/env python3
"""Syntax-check every inline <script> in an HTML page with `node --check`.

Usage: check-scripts.py PAGE.html
Exits non-zero if any script has a syntax error, so make stops before the
page goes live.
"""
import os
import re
import subprocess
import sys
import tempfile

page = sys.argv[1]
html = open(page, encoding="utf-8").read()
scripts = re.findall(r"<script>(.*?)</script>", html, re.S)
if not scripts:
    sys.exit(f"{page}: no inline <script> found")

failed = False
for number, code in enumerate(scripts, 1):
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
        f.write(code)
    result = subprocess.run(["node", "--check", f.name], capture_output=True, text=True)
    os.unlink(f.name)
    if result.returncode != 0:
        failed = True
        print(f"{page}: script {number} has a syntax error:", file=sys.stderr)
        print(result.stderr.strip(), file=sys.stderr)

if failed:
    sys.exit(1)
print(f"{page}: {len(scripts)} scripts OK")
