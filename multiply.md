# Writing a custom.txt for multiply.by

This file helps you write a `custom.txt`: a short spec that turns the multiply.by times-tables
game into a game of your own. The game itself is fully described by its build instructions,
https://multiply.by/build-instructions.txt. custom.txt describes only how your game differs from
it.

To use a custom.txt:
1. Insert it into `build-instructions.txt` right after the Note for Human Readers (at the first
   blank line).
2. Put this line directly before it: "Where this section conflicts with the rest of this file,
   this section wins."
3. Give the combined file to an AI model, which builds the game as one `index.html`.

Working examples (each is the full build instructions with its custom section near the top):
- https://multiply.by/divide/build-instructions.txt: division questions ("56 ÷ 8"), new wrong
  answers and new branding.
- https://multiply.by/monster/build-instructions.txt: a big visual reworking for 7- to
  9-year-olds (a monster to feed, a path to walk, stickers, stars, two easier sets).
- https://multiply.by/chinese/build-instructions.txt: a small one: spoken Chinese encouragement
  and a flip animation.

## 1. The shape of custom.txt

Start with this banner and an opening paragraph that says what the game is and what stays the same:

```
-------------
CUSTOMIZATION
-------------
This is <NAME>, <one sentence: what it is, for whom>, served at <address>.
It is the same game as the rest of this file (<list what is kept>) with the changes below:
<one-line list of the changes>.
```

Then:
- GAME NAME (needed whenever the game will sit next to another version on the same website): set
  `CONFIG.GAME` to a short name of your own (letters, digits, `-`, `_`), e.g. "- GAME: monster".
  The saved progress is stored under this name. Without a name of its own, your game would share
  (and overwrite) the original game's progress.
- SOURCE: give the address where your combined build instructions will be published, to
  replace the SOURCE link (https://multiply.by/build-instructions.txt).
- One section per change, each with an UPPERCASE heading. Say whether it ADDS to a rule or
  REPLACES it, naming the rule as the main spec names it. For example, "WRONG ANSWERS (CRITICAL:
  replaces the whole WRONG ANSWERS rule ...)" or "SETS (replaces the three modes)".
- End with a `CHECKS` section of extra acceptance checks. These are added to section 11 of the
  main spec.

Style (the house style of every multiply.by spec):
- Plain text, prose wrapped at about 100 columns. Only code fragments and exact HTML run longer.
- Bullets start with `- `. Mark rules that models tend to get wrong with `(CRITICAL)`.
- Give exact strings, exact HTML, exact colors (hex), sizes (rem/px) and timings (ms). A model
  fills any gap with defaults: a link with no stated style comes out with a blue underline. State
  link styles and the spacing between stacked lines.
- Where the logic is subtle, give the actual JavaScript line in backticks, e.g.
  `state.question = { ...fact, text: ..., answer: ... };`
- Say what is REMOVED as clearly as what is added, e.g. "No Share my results button", "No DEMO or
  ABOUT in the menu".

## 2. What the main game provides (names to refer to)

Use the main spec's own names, so the model ties your changes to its code:

- Config: `CONFIG.GAME`, `CONFIG.MUTED`, `CONFIG.TARGET_LANGUAGE`, `CONFIG.LANGUAGE_CODE`.
- Data:
  - `RAW_DATA` holds 120 facts with ids 1 to 120 and the fields `id | text ("7 x 8") | answer
    ("56")`.
  - Never renumber or reorder them: saved progress refers to the ids. Add new facts after them,
    starting at id 121 (monster adds 2 x 10 … 10 x 10).
  - `FACTS` is the current mode's set, built only in `applyMode`.
  - A new kind of question can keep the ids and change the fields. divide does this with
    `a | b | product`, and asks either division of each fact family.
- Modes:
  - `MODE` is 9, 12 or 20. `applyMode(mode)` sets MODE, GAME_NAME, FACTS, STORAGE_KEY, BEST_KEY and
    `document.title`. `switchMode(mode)` changes mode in place, with no page load.
  - The address picks the mode (`?12`, `?20`). A custom game may define its own sets (monster has
    9 and 5, with `?easy`).
- Storage:
  - The progress key is `openlang_Math_<GAME_NAME>_progress`, where GAME_NAME is CONFIG.GAME, plus
    the mode for any mode other than the default. BEST_KEY holds the best score.
  - Everything goes through the SAFE STORAGE wrappers. A new store (e.g. a sticker collection)
    should follow the same pattern.
- State and rendering:
  - There is one `state` object: `state.deck`, `state.question`, `state.choices`,
    `state.learnedIds`, `state.score`, `state.streak`, `state.feedback`, `state.isWon`,
    `state.practice`, `state.answerLog`, and more.
  - The screen is always drawn from state by `update()`. New elements should be drawn there too.
- Flow:
  - `nextQuestion()` deals the next fact. `renderQuestion()` draws it.
  - The answer is checked against `state.choices[index]` (RIGHT ANSWER, WRONG ANSWER, MISSED
    QUESTIONS: a missed fact comes back at the end of the deck).
  - After a right answer, the next question comes 200ms later. Nothing may delay that.
- Wrong answers:
  - `wrongAnswers(fact)` returns three distractors. The rules: same parity as the answer, "SAME
    LAST DIGIT" when a factor is 10 or more, within the mode's range, and the right answer spread
    evenly over the four positions.
  - A new kind of question needs its own rule.
- Screen:
  - The top row holds the question card, the PROGRESS BAR and the INDICATORS: `#ind-score`,
    `#ind-streak`, `#ind-learned`, `#ind-mistakes` and `#ind-time`. If you hide indicators, keep
    them in the page with `display: none`, so `update()` keeps working.
  - Below the top row, the four answer buttons are in `#answers`.
- Feedback:
  - FEEDBACK classes (green for right, red for wrong), ANIMATIONS (POP, FLOATING POINTS,
    `celebrateStreak()`), all checked against `REDUCED_MOTION`.
  - Sounds are tables of notes: `SOUNDS = { name: [wave, [[freq, start, dur], ...], volume] }`,
    played with `playSound(name, semitones)`, which checks `isMutedNow()`. Add a sound as one more
    entry, e.g. `nom: ['triangle', [[523, 0, 0.06], [392, 0.08, 0.1]], 0.25]`.
  - Speech uses `CONFIG.TARGET_LANGUAGE` / `LANGUAGE_CODE`, with the iOS fixes of section 7.
- Timer: `state.timerStart`, `pauseTimer()`, `resume()`, `currentPlayMs()`.
- End of a game:
  - The "You Won!" overlay: the score, best score, "Your time", the `win-buttons` (Play Again,
    "Practice hard ones"), the NEXT-LEVEL line, the DIVISION line, and SHARE MY RESULTS (a results
    card, shown only on touch devices that can share files).
  - PRACTICE HARD ONES runs a short practice of the weakest facts (`weakFacts()`, ANSWER TIMES)
    and ends with "Practice done!".
- Menu:
  - The main game shows MUTE, DEMO, ABOUT, RULES (a popup), RESET and SOURCE. A custom game lists
    its own items from left to right. SOURCE is always last, in the far right corner.
- Site frame (the SITE LAYOUT part of the spec):
  - The TITLE BAND is `<h1><a id="tagline" href=...><strong>Multiply.by:</strong> ...</a></h1>`,
    sized to fit by `fitTagline()`, with the share icon and share menu.
  - The share texts come from `shareText()` and `siteShareText()`. Then the MENU BAR and the
    FOOTER.
  - A custom game usually rewrites the tagline, `<title>`, the meta description and the share
    texts.

## 3. Lessons learned

- Keep the game fast: celebrations run alongside play, never before the next question. Every added
  element gets `pointer-events: none` and is removed when done. Animate only `transform` and
  `opacity`. Respect REDUCED_MOTION.
- Everything stays in ONE file: no images, fonts or libraries from any server. Use inline SVG, CSS
  and emoji.
- No page scroll on the game, at any screen size. Give a rule for short screens (`max-height:
  500px`, phones held sideways). Things that take room (pictures, mascots, paths) must be able to
  shrink: `flex: 1; min-height: 0`.
- Floating or popping elements need a stated position, or they land on top of labels. For
  example: "+10 rises from just right of the Points number".
- Overlays should be stated as opaque, or the game shows through.
- When a feature of the main game doesn't fit, drop it explicitly, including its checks. When you
  drop the timer, say what replaces "Your time" (monster: stars from the number of mistakes).
- Name any element id your tests or other rules depend on. Otherwise ids may differ between
  builds (e.g. `win-overlay` / `won-overlay`).
- The original game's main page must stay under 60 KB; a custom game may be larger, but ask it to
  stay lean.
- Bigger, more visual reworkings come out better from the strongest models.

## 4. Testing a build

- Open the page at phone (360x640), phone sideways (640x360), tablet (768x1024) and laptop
  (1280x800) sizes: no console errors, nothing cut off, no page scroll.
- Play a whole game: right and wrong answers, the wrong-answer choices (their positions and
  parity), the animations, the "You Won!" screen, and each mode or set.
- To start from a saved state (e.g. one answer from winning), write the progress key to
  localStorage before the page loads. The game saves when the page is left, so a value written
  while it is open gets overwritten.
