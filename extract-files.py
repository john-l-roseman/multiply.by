#!/usr/bin/env python3
"""Copy files embedded in a spec (such as PWA-build.txt) into a folder.

Each file sits in the spec between two marker lines:
    ----- BEGIN FILE: <name> -----
    ----- END FILE: <name> -----
Usage: extract-files.py SPEC OUT_DIR NAME [NAME ...]
Every NAME must be present in SPEC, and only plain file names are allowed.
"""
import os
import re
import sys


def main():
    if len(sys.argv) < 4:
        sys.exit("usage: extract-files.py SPEC OUT_DIR NAME [NAME ...]")
    spec_path, out_dir, names = sys.argv[1], sys.argv[2], sys.argv[3:]
    with open(spec_path, encoding="utf-8") as f:
        spec = f.read()

    os.makedirs(out_dir, exist_ok=True)
    for name in names:
        if os.path.basename(name) != name or name.startswith("."):
            sys.exit(f"refusing unsafe file name: {name}")
        pattern = re.compile(
            r"^----- BEGIN FILE: " + re.escape(name) + r" -----\n(.*?)^----- END FILE: "
            + re.escape(name) + r" -----$",
            re.DOTALL | re.MULTILINE,
        )
        matches = pattern.findall(spec)
        if len(matches) != 1:
            sys.exit(f"{spec_path}: expected exactly one block for {name}, found {len(matches)}")
        # Write a new file and rename it into place, so the web server never
        # serves a half-written or resized copy of the old one.
        path = os.path.join(out_dir, name)
        with open(path + ".tmp", "w", encoding="utf-8") as f:
            f.write(matches[0])
        os.replace(path + ".tmp", path)
        print(f"wrote {name}")


if __name__ == "__main__":
    main()
