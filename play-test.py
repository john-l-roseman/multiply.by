#!/usr/bin/env python3
"""Play a live game page from start to "You Won!" and fail on anything that goes wrong.

Usage: play-test.py URL [URL ...]      (e.g. play-test.py https://multiply.by/ https://multiply.by/blocks/)
Options: --size WxH (default 360x640), --wrong 0.25 (share of wrong answers), --seed 1,
         --max 200 (moves before giving up on reaching the end)

Each question is read from #question ("7 x 8", or "56 ÷ 8" in the division game), the answer from
the #answers buttons. About a quarter of the answers are wrong on purpose (mistakes take other code
paths: corrections, retries, "Almost!" pictures). After every tap the page must move on (the
question or the answers change) within 10 s. The page passes when it reaches its end screen (the
page shows "You Won!" or "Play Again") with no console errors and no uncaught exceptions during the
WHOLE game. A layout check after a rebuild is not enough: each build is a fresh page written by the
model, and a game can break on its second question (a kimi front page did). Exit status 1 if any
page fails. Prints the move, question and answers where it stopped; a screenshot is saved as
/tmp/play-test-<n>.png.
"""
import argparse, random, re, sys
from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument("urls", nargs="+")
ap.add_argument("--size", default="360x640")
ap.add_argument("--wrong", type=float, default=0.25)
ap.add_argument("--seed", type=int, default=1)
ap.add_argument("--max", type=int, default=200)
args = ap.parse_args()
W, H = map(int, args.size.split("x"))

STATE = """() => {
  const q = document.getElementById('question');
  const b = [...document.querySelectorAll('#answers button')];
  // The answer is the button's last line (a build may show a key number above it).
  const ans = x => x.innerText.trim().split(String.fromCharCode(10)).pop().trim();
  return {q: q ? q.innerText.trim() : '', a: b.map(ans),
          enabled: b.filter(x => !x.disabled).length,
          won: /you won|play again/i.test(document.body.innerText)};
}"""


def play(browser, url, n):
    rnd = random.Random(args.seed)
    ctx = browser.new_context(viewport={"width": W, "height": H}, has_touch=True)
    pg = ctx.new_page()
    errors = []
    pg.on("pageerror", lambda e: errors.append(f"exception: {e}"))
    pg.on("console", lambda m: m.type == "error" and errors.append(f"console: {m.text}"))
    pg.goto(url, wait_until="networkidle")
    pg.wait_for_timeout(500)
    wrongs = 0
    problem = None
    for move in range(1, args.max + 1):
        s = pg.evaluate(STATE)
        if s["won"]:
            break
        m = re.search(r"(\d+)\s*([x×÷])\s*(\d+)", s["q"])
        if not m:
            problem = f"no question in #question: {s['q']!r}"
            break
        a, op, c = int(m[1]), m[2], int(m[3])
        right = str(a // c if op == "÷" else a * c)
        if right not in s["a"]:
            problem = f"the answer {right} is not among the buttons {s['a']}"
            break
        wrong = rnd.random() < args.wrong
        k = next(i for i, t in enumerate(s["a"]) if t != right) if wrong else s["a"].index(right)
        try:
            pg.locator("#answers button").nth(k).click(timeout=5000)
            pg.wait_for_function(
                """old => { const q = document.getElementById('question');
                  const a = [...document.querySelectorAll('#answers button')].map(x => x.innerText.trim().split(String.fromCharCode(10)).pop().trim()).join('|');
                  return (q ? q.innerText.trim() : '') !== old.q || a !== old.a.join('|')
                         || /you won|play again/i.test(document.body.innerText); }""",
                arg=s, timeout=10000)
        except Exception as e:
            if move == 1:
                # A first tap that changes nothing is a bug (a child's first answer is lost),
                # not a repeated question: no question has been answered yet.
                problem = f"the FIRST tap was ignored: {s['q']!r} {s['a']} (the page did not react)"
                break
            # The same question with the answers in the same order can come again by chance:
            # answer it right once more before calling it a freeze.
            try:
                t = pg.evaluate(STATE)
                pg.locator("#answers button").nth(t["a"].index(right)).click(timeout=5000)
                pg.wait_for_function("old => document.getElementById('question').innerText.trim() !== old.q"
                                     " || /you won|play again/i.test(document.body.innerText)",
                                     arg=s, timeout=10000)
            except Exception:
                problem = (f"FROZE at move {move}: {s['q']!r} {s['a']} after a "
                           f"{'wrong' if wrong else 'right'} answer ({str(e).splitlines()[0]})")
                break
        wrongs += wrong
        pg.wait_for_timeout(250)
    else:
        problem = f"no end screen after {args.max} moves"
    if errors:
        problem = (problem + "; " if problem else "") + f"{len(errors)} error(s), first: {errors[0]}"
    if problem:
        pg.screenshot(path=f"/tmp/play-test-{n}.png")
    ctx.close()
    print(f"{'FAIL' if problem else 'OK  '} {url}: {move} moves, {wrongs} wrong"
          + (f" -- {problem} (screenshot /tmp/play-test-{n}.png)" if problem else ", reached the end"))
    return not problem


with sync_playwright() as p:
    browser = p.chromium.launch()
    results = [play(browser, url, n) for n, url in enumerate(args.urls, 1)]
    browser.close()
sys.exit(0 if all(results) else 1)
