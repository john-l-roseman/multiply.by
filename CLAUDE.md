# multiply.by

A times-tables game site, served live by nginx straight from this folder (https://multiply.by).
Every page is ONE self-contained HTML file built by an AI model from a plain-text spec. Never edit a
generated file (index.html, prompt.txt, pwa.js, sw.js, ...) by hand: change the spec and
rebuild. GitHub: john-l-roseman/multiply.by (public).

## How a page is built
- Site map: `/` is the front page: the base game with a strip of the other games under the
  answers (spec `home.txt`); `/games/` is the picture chooser (spec `games/page.txt`, the strip's
  "More games" tile); `/base/` is the base game alone (spec
  `game.txt`); each gamified game is in its own folder (`/train/`, ...);
  `/build-it/` ("Build it yourself", menu BUILD IT) shows each game's prompt, model and build time;
  `/about/`, `/demo/`. Every page's SOURCE opens the prompt.txt beside it (the front page's is
  `/prompt.txt`, the base game's `/base/prompt.txt`).
- `layout.txt` is the frame shared by every page: title band (a link to https://multiply.by/),
  share icon and desktop share menu, menu bar look, GAMES/BUILD IT/ABOUT/SOURCE items, footer.
- `footer.txt`: the three-column site info block (About Multiply.by, Feedback, Functional AI
  Inc.) above the copyright line, on the front page, About and Build It, put in by an optional
  `#include footer.txt` line.
- Each page has its own spec with one `#include layout.txt` line; `assemble-spec PAGE.txt`
  expands it into that page's `prompt.txt` (generated, git-ignored, served: it is what every
  page's SOURCE button opens, and it must stay one self-contained file a person can upload to
  any chatbot).
  - `home.txt`: the front page (/). It is `#include game.txt` (assemble-spec puts the base game's
    spec in and makes every https://multiply.by/base/ address https://multiply.by/) plus a section
    that adds the games strip (short names, pictures `thumbnails/GAME-thumbnail.png`, 200 x 160, last game
    played first, then Monster and Dinosaurs, the rest shuffled per visit, then More games).
    Same storage keys as /base/, so progress is shared.
  - `games/page.txt`: the chooser (/games/), big tiles with the short names (Monster, Train,
    Dinosaurs, Robot, Planes, Space, Great Wall, Block Craft, Base Game). Both pages save the tapped game in
    localStorage `multiply_last_game`. Build with `make` in `games/` (Claude).
  - `game.txt`: the base game (/base/). Menu: MUTE, BUILD IT, ABOUT, RULES (popup), RESET, SOURCE
    (no GAMES: the title band leads to the front page and its strip).
    Every gamified game keeps exactly this menu (gamify.md).
  - `about/about.txt`: About. Menu: GAMES, BUILD IT, ABOUT (current), SOURCE.
  - `build-it/page.txt`: Build it yourself (/build-it/, was /gallery/). `make` there retakes the
    screenshots (`shots.py`; also used by /games/) and builds the page (Claude). The front page's
    strip uses `thumbnails/GAME-thumbnail.png` instead (screenshots are illegible that small):
    `thumbs.py` crops each game's main picture (the robot: a finished one drawn by the game's own
    buildMiniRobotSvg); made only when missing, so a hand-made replacement is kept. Tracked in git.
  - `demo/page.txt`: Demo page (/demo/), plays `demo/demo.webm` in a <video> player. Menu: GAMES,
    BUILD IT, ABOUT, SOURCE (no DEMO item). Build with `make` in `demo/` (Claude, like About). The video
    itself is made from `demo/demo.txt` by an agent (`demo/record.py`), not by make. Record on the
    stopped GCE VM `demo-recorder` (us-east1-b, e2-standard-4, 10 GB disk, Playwright venv in
    /opt/rec), never on this e2-small (too slow: dropped frames, drifting sound):
    `gcloud compute instances start demo-recorder --zone us-east1-b`, scp record.py to jlr@<its
    internal IP> (`gcloud compute instances list`) with ~/.ssh/google_compute_engine, run
    `PLAYWRIGHT_BROWSERS_PATH=/opt/rec/browsers /opt/rec/bin/python record.py ~/demo.webm`, scp
    demo.webm back, then STOP the VM.
  - `FAQ/faq.txt`: the FAQ, still in progress by the user, not built yet. The URL is /faq
    (currently 404); the folder needs renaming to `faq` and a Makefile like about's.
- `make` in this folder builds the base game and the front page. Base game: game.txt ->
  `base/prompt.txt` -> the model named in `model` (e.g. kimi; `run-model`, which reuses mk-gamify's
  model calls; build/build.txt notes tokens, cost, time) -> `build/index.html` -> PWA tags from
  `PWA-build.txt` inserted -> `check-scripts.py` (node --check) -> `base/index.html`. Front page:
  home.txt (+ game.txt) -> `prompt.txt` -> the model in `home-model` (carbon; kimi's front pages froze
  after some moves; run-model) ->
  `build/home/index.html` (its own folder, so its build.txt does not overwrite the base game's
  `build/build.txt`, which Build It reads) -> PWA tags -> `index.html`. Also extracts the PWA files and renders icons and og-image.png. The installed app
  opens the front page; sw.js keeps every page opened online, so played games work offline.
- About and Demo: `make` in `about/` or `demo/` (Claude via `about/run-claude.py`, key read from
  `$HOME/.anthropic_key`).
- Custom games (e.g. `divide/`): `../mk-custom` from the game's folder; it combines game.txt +
  layout.txt + the folder's `custom.txt`, sets GAME to the folder name and SOURCE to the folder.
  Served at /<folder>/ (no redirects).
  - `divide/`: the division game (Divide.by), same game with "56 ÷ 8" questions. https://divide.by
    and www redirect (302, keeping ?12/?20) to https://multiply.by/divide/
    (/etc/nginx/sites-enabled/divide.by).
  - `monster/`: Multiply Monster, a gamified version for 2nd and 3rd graders (Munch, path,
    stickers, stars; `?easy` = 2, 5 and 10). Now built with `../mk-gamify` (see below) from
    `monster/prompt.txt` (a short prompt), model `fable`. Its `custom.txt` is the hand-made design
    of the first build (by mk-custom, kept in `monster/fable/`): it stays as the worked example
    that gamify.md links to (with its build-instructions.txt), so don't delete or regenerate
    either. mk-gamify no longer attaches it (a chat user doesn't get it, and builds copied it).
- Gamified games from a short prompt (e.g. `train/`): `../mk-gamify` from the game's folder. The
  folder's prompt.txt is a few lines of prompt (not a CUSTOMIZATION section); the game's SOURCE opens
  it. The folder's `model` file names the model (carbon, fable, opus, gpt, kimi or a full id; no
  default). Gemini runs on Vertex; an id with a `/` (gpt = openai/gpt-6.1-terra, kimi =
  moonshotai/kimi-k3.1-pro) goes through OpenRouter, key in ~/.openrouter-key. mk-gamify
  (`MK_EFFORT`, `MK_FORCE=1`) does EXACTLY what a chat does, so an API pass proves the prompt and
  gamify.txt work as published: it sends prompt.txt word for word plus the full text of each
  multiply.by file it links to (as if fetched; gamify.txt is remade by make first), nothing else:
  no added instructions, no preset SOURCE or GAME. The page in the answer becomes index.html (the
  text before it, customization.txt), checked but never changed: scripts must parse and SOURCE
  must open the folder's prompt.txt, or nothing is published; a GAME shared with another game is
  reported. It also keeps a copy of each build (index.html,
  customization.txt, build.txt with model, tokens, cost, time) in a subfolder per model
  (`train/carbon/`, `train/fable/`, served for comparison). A failed build keeps the raw answer in
  /tmp/mk-gamify-<folder>-answer.txt. Gemini 4 Carbon stops each answer at 65,536 tokens; mk-gamify
  asks it to continue.
- `gamify.md`: a guide for an AI model writing the custom.txt of a GAMIFIED version (mascot,
  rewards, progress pictures, new screen layout; Monster is the worked example). Served
  publicly; no build tooling in it. Simple customizations (branding, division, speech) are a
  hand edit of the base build instructions, not its subject. Its old name, multiply.md, is gone.
- `gamify.txt` (generated by `make gamify.txt`, served, git-ignored): ONE file for building a
  gamified game in any chatbot with no web access: a note for human readers, gamify.md as plain
  text (`gamify-txt.py`) and the base prompt.txt, unchanged. Plain `make` rebuilds it
  first whenever gamify.md or the base spec changes (no hand copying).
- nginx (`/etc/nginx/sites-enabled/multiply.by`, not in git; reapply on a new server): the main
  server block has `charset utf-8;` and a `location ~ \.md$` block with
  `default_type "text/plain; charset=utf-8";` and `try_files $uri =404;`. Without it nginx sends
  .md files as application/octet-stream, which fetch tools (e.g. claude.ai) refuse to read.
- `match/` is an older matching game with its own spec (not using layout.txt).
- Builds take a few minutes and go live as soon as they pass; run them in the background.

## Rules
- The game page must stay under 100 KB (the About page says "less than 100 KB"; make warns).
- Never print, echo or commit API keys. Don't change or commit anything in /var/www/openlang.ai
  (e.g. run-vertex.py model changes): it is not part of this repo.
- `chinese/prompt.txt` is the user's own work: commit it only when asked.
- Specs: wrap prose at about 100 columns; only code fragments and exact HTML may run longer.
- After a rebuild, test the live page with Playwright (python, chromium) at 360x640, 640x360
  (landscape), 768x1024 (tablet) and 1280x800: no console errors, nothing cut off, no page scroll
  on the game, share menu, menu bar, animations, wrong-answer distractors (position and parity).
  Then play every rebuilt game page through to "You Won!" with `./play-test.py URL ...` (a quarter
  of the answers wrong; fails on any console error or a question that stops advancing): a fresh
  build can break on its second question, which a layout check misses (a kimi front page did).
  Headless Chromium uses DejaVu Sans, about 15% wider than phone fonts.
- Commit or push only when the user asks.
