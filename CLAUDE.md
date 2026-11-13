# multiply.by

A times-tables game site, served live by nginx straight from this folder (https://multiply.by).
Every page is ONE self-contained HTML file built by an AI model from a plain-text spec. Never edit a
generated file (index.html, build-instructions.txt, pwa.js, sw.js, ...) by hand: change the spec and
rebuild. GitHub: john-l-roseman/multiply.by (public).

## How a page is built
- `layout.txt` is the frame shared by every page: title band (a link to https://multiply.by/),
  share icon and desktop share menu, menu bar look, PLAY/DEMO/ABOUT/SOURCE items, footer.
- Each page has its own spec with one `#include layout.txt` line; `assemble-spec PAGE.txt`
  expands it into that page's `build-instructions.txt` (generated, git-ignored, served: it is
  what the SOURCE button opens, and it must stay one self-contained file a person can upload to
  any chatbot).
  - `game.txt`: the game (main page). Menu: MUTE, DEMO, ABOUT, RULES (popup), RESET, SOURCE.
  - `about/about.txt`: About. Menu: PLAY, DEMO, ABOUT (current), SOURCE.
  - `demo/page.txt`: Demo page (/demo/), plays `demo/demo.webm` in a <video> player. Menu: PLAY,
    DEMO (current), ABOUT, SOURCE. Build with `make` in `demo/` (Claude, like About). The video
    itself is made from `demo/demo.txt` by an agent (`demo/record.py`), not by make. Record on the
    stopped GCE VM `demo-recorder` (us-east1-b, e2-standard-4, 10 GB disk, Playwright venv in
    /opt/rec), never on this e2-small (too slow: dropped frames, drifting sound):
    `gcloud compute instances start demo-recorder --zone us-east1-b`, scp record.py to jlr@<its
    internal IP> (`gcloud compute instances list`) with ~/.ssh/google_compute_engine, run
    `PLAYWRIGHT_BROWSERS_PATH=/opt/rec/browsers /opt/rec/bin/python record.py ~/demo.webm`, scp
    demo.webm back, then STOP the VM.
  - `FAQ/faq.txt`: the FAQ, still in progress by the user, not built yet. The URL is /faq
    (currently 404); the folder needs renaming to `faq` and a Makefile like about's.
- Main game: `make` in this folder. Spec -> Gemini (`/var/www/openlang.ai/SCRIPTS/run-vertex.py`)
  -> `build/index.html` -> PWA tags from `PWA-build.txt` inserted -> `check-scripts.py`
  (node --check) -> `index.html`. Also extracts the PWA files and renders icons and og-image.png.
- About and Demo: `make` in `about/` or `demo/` (Claude via `about/run-claude.py`, key read from
  `$HOME/.anthropic_key`).
- Custom games (e.g. `chinese/`): `../mk-custom` from the game's folder; it combines game.txt +
  layout.txt + the folder's `custom.txt`, sets GAME to the folder name and SOURCE to the folder.
  Served at /<folder>/ (no redirects).
- `match/` is an older matching game with its own spec (not using layout.txt).
- Builds take a few minutes and go live as soon as they pass; run them in the background.

## Rules
- The game page must stay under 60 KB (the About page says "less than 60 KB"; make warns).
- Never print, echo or commit API keys. Don't change or commit anything in /var/www/openlang.ai
  (e.g. run-vertex.py model changes): it is not part of this repo.
- `chinese/custom.txt` is the user's own work: commit it only when asked.
- Specs: wrap prose at about 100 columns; only code fragments and exact HTML may run longer.
- After a rebuild, test the live page with Playwright (python, chromium) at 360x640, 640x360
  (landscape), 768x1024 (tablet) and 1280x800: no console errors, nothing cut off, no page scroll
  on the game, share menu, menu bar, animations, wrong-answer distractors (position and parity).
  Headless Chromium uses DejaVu Sans, about 15% wider than phone fonts.
- Commit or push only when the user asks.
