# Gamifying the multiply.by game

This file helps an AI model turn the multiply.by times-tables game into a GAMIFIED version from a
short prompt, e.g. "a space-travel version" or "a monster-based version for 2nd graders".

The game is fully described by its base build instructions, which follow this guide.

## G1. The steps

1. DESIGN: turn the prompt into a CUSTOMIZATION section (see G2). Write it out in full before any
   code: it is the design, and a game built from a vague design comes out plain. Where the prompt
   leaves something open, make a sensible choice and write it into the section.
2. BUILD (the usual result): one standalone `index.html`, built from the base build instructions
   with the CUSTOMIZATION section applied. Where they conflict, the section wins; everything the
   section doesn't mention follows the base file exactly (the deck, the wrong-answer rules, saved
   progress, the iOS sound fixes, the site frame). Also:
   - Set `CONFIG.GAME` to the new game's short name (letters, digits, `-` and `_`), e.g.
     `monster`. The game saves the player's progress under this name. Without a name of its own,
     it would share, and overwrite, the original game's progress.
   - SOURCE opens THIS game's own prompt: the `prompt.txt` file published next to the game's
     `index.html`. Use exactly the relative link `<a href="prompt.txt">`, which works wherever
     the game is published. CRITICAL: SOURCE never points to /gamify/, gamify.md or the base
     game's `https://multiply.by/base/prompt.txt`, even though those are the files you were given.
     (If the base file already points SOURCE to an address ending in `/prompt.txt` inside a
     game's folder, such as `https://multiply.by/train/prompt.txt`, keep that address.)
3. BUILD INSTRUCTIONS INSTEAD (only when the person asks for the build instructions, or the
   spec, rather than the game): one complete new `prompt.txt`, as a file named so.
   Copy the base file EXACTLY, word for word, with only these changes:
   - At the very top of the file, insert the line "Where this section conflicts with the rest
     of this file, this section wins.", then the CUSTOMIZATION section and one blank line.
   - Change the one line that starts with `- GAME: ` to the new game's short name.
   - Change the one SOURCE link, `https://multiply.by/base/prompt.txt`, to the relative link
     `prompt.txt` (the game's own prompt, published next to its `index.html`).
   Don't rewrite, shorten, reorder or "fix" anything else, even the parts the section replaces: a
   dropped paragraph is a broken game. If you can run code, make the file with code instead of
   retyping the base text.

## G2. Writing the CUSTOMIZATION section

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
- One section per change, each with an UPPERCASE heading. Say whether it ADDS to a rule or
  REPLACES it, naming the rule as the base file names it. For example, "WRONG ANSWERS (CRITICAL:
  replaces the whole WRONG ANSWERS rule ...)" or "SETS (replaces the three modes)".
- Always cover the NAMES: `<title>`, meta description, the title band's tagline (its text only:
  the tagline always links to the main game, https://multiply.by/), the share texts
  (`shareText()`, `siteShareText()`), and the menu items.
- End with a `CHECKS` section of extra acceptance checks. These are added to section 11
  (ACCEPTANCE CHECKS) of the base file.

### From a short prompt to a full design

A one-line prompt leaves almost everything open. Work out a complete, concrete design before
writing, and write all of it down: the model that builds the game sees only the file.
- Who plays? The age decides the sets (young children: 2 to 9, or an easier set such as 2, 5 and
  10), the reading level of every word on screen, button sizes and how loud the celebrations are.
- What is the core reward loop? Every right answer should visibly DO something (feed a monster,
  move a rocket, grow a garden, fill a stone on a path). Tie it to the game's own events: a right
  answer, a wrong answer, a fact learned, a streak, a win.
- What shows progress? A path, map or collection that fills as facts are learned. It can replace
  the progress bar and some indicators.
- What do mistakes do? For young players, keep them gentle: no lost points, a friendly face, and
  a picture that teaches (rows of dots for 3 x 6).
- What replaces things that don't fit? For example, stars from the number of mistakes instead of
  a clock for children who shouldn't be timed.
- What is dropped? Say it: "No Share my results button", "No division line". The menu is never
  changed (see "Menu" in G4: the same items as the base game).
- The look: a palette (hex colors), a font stack, the background, the mascot. Draw every picture
  as inline SVG, CSS or emoji, giving its shapes and colors and the face for each state, unless
  the prompt asks for photo-realistic pictures (see "Photo-realistic pictures" below).
- The sound: see "Sounds that match the stages" below.

### Sounds that match the stages

(CRITICAL) No background music, no ambient or looping sound, and no new kinds of sound effects
(no engine noise, horns, whooshes, animal calls, voices or noise-based sounds). The game's only
sounds are the base build instructions' own: the STREAK CHIME, sequences of rising tones played
with `playSound(name, semitones)` from the `SOUNDS` table, plus the base wrong-answer "uh-oh" and
win tune, unchanged. Keep `playSound()`, `isMutedNow()` and the iOS sound fixes exactly as the base
file gives them.

What may change is how those rising sequences fit the game's STAGES:
- Divide the game into 4 or 5 STAGES that the player can see change, tied to progress (for
  example, one stage per 12 facts learned, or per stretch of the path).
- Adjust the NUMBER and LENGTH of the rising sequences to the stages. The base game climbs 12
  semitones, then switches between the three-note ('correct') and four-note ('correct2') chime.
  A gamified game may, for example, give each stage a chime of its own (more notes, or a higher
  starting pitch, for a later stage), or set the length of a climb to match a stage. Every chime is
  still a short rising run of tones (`triangle` or `sine` notes, under 0.4 s), as in the base table.
- The chime changes at the same moment as the picture: the first right answer of a new stage plays
  the new stage's chime. Write the new `SOUNDS` entries out in full, as the base file does.
- Not louder than the base sounds; a chime must not run into the next question's.

### Photo-realistic pictures

The result must be one index.html that anyone gets by giving these files to a chat model (for
example in Google AI Studio), with no other tools. So when the prompt asks for photo-realistic
(or "as real as possible") pictures, draw them in DETAILED inline SVG, as close to a photograph as
SVG allows:
- Real proportions and details of the real thing (for a train: wheel arrangement, boiler, cab,
  pantograph, liveries of real eras), seen from one angle (e.g. a side view) and at one scale and
  ground line for all the pictures of the game.
- Light and depth: linear and radial gradients for curved metal and glass, a highlight and a
  shadow on every main shape, a soft shadow on the ground, a background with depth (sky gradient,
  distant hills or a city, a track that recedes).
- State each picture's shapes, colors (hex) and gradients in the design, so the building model
  doesn't fall back to a cartoon. Reuse shapes with `<defs>` and `<use>` to keep the file small.
- Animation stays in CSS or SVG on top: steam puffs, a rising pantograph, speed lines, a moving
  background. Parts that must line up with the picture are positioned in % of the picture box.
- No raster images and no placeholders that need a later step. Only a builder that can itself
  make photo-realistic images AND write them into the file (for example a coding agent with an
  image model) may instead embed a few small ones as data URIs (at most 480px across, WebP or
  JPEG, 15 to 40 KB each), each with `alt` text and an SVG stand-in. Otherwise, SVG.

Style (the house style of every multiply.by spec):
- Plain text, prose wrapped at about 100 columns. Only code fragments and exact HTML run longer.
- Bullets start with `- `. Mark rules that models tend to get wrong with `(CRITICAL)`.
- Give exact strings, exact HTML, exact colors (hex), sizes (rem/px) and timings (ms). A model
  fills any gap with defaults: a link with no stated style comes out with a blue underline. State
  link styles and the spacing between stacked lines.
- Where the logic is subtle, give the actual JavaScript line in backticks, e.g.
  `state.question = { ...fact, text: ..., answer: ... };`

## G3. The screen of a gamified game

The base screen is made for practice: a large question card, a progress bar, and a column of five
indicators (Score, Streak, Learned, Mistakes, Time) on the right of the top row, above the four
answer buttons. A gamified game needs room for its mascot or world, and most of the indicators mean
little to a young player. Rearrange the screen, and state the new layout exactly (flex sizes,
heights, gaps), because the building model otherwise keeps the base layout. What Monster does:

- DROP THE INDICATOR COLUMN. Show at most one number, such as the score as "Points", under the
  mascot. Keep the other indicator blocks in the page with `display: none`, so `update()` works
  unchanged. Replace what they told the player with pictures: a path or map for Learned, stars
  for Mistakes, nothing for Time (children shouldn't be timed; the clock still runs for the best
  score).
- USE THE SPACE RIGHT OF THE QUESTION for the mascot or the scene. The question card does not need
  the whole width: shrink it to half the row and give the other half to the mascot or the scene
  (both `flex: 1 1 0; min-width: 0`), with a 0.75rem gap. The question ("7 x 8") still fits in
  half, also on a 360px phone, because its font size comes from the card. (Monster gives the
  question about 60%: question card `flex: 1`, MONSTER BOX `flex: 0 0 40%`.) The mascot box is a
  centered column with the mascot, as large as fits (`flex: 1; min-height: 0; width: 100%`), and
  the Points under it.
- NAME THE MAIN PICTURE: the one element that shows the game's main picture (the mascot, the
  vehicle, the scene: an <img>, <svg> or <div>) has `id="main-picture"`, in every build. The site
  makes its small pictures of each game (the front page's strip, the Build It page) from that
  element, so the id must not change from one build to the next. It holds only the picture: no
  labels, points or buttons over it inside the element.
- KEEP THE TOP ROW SHORT, so the answers stay big: Monster's top row is `flex: 0 0 34%` of the game
  area (40% on short screens, `max-height: 500px`). The question text still fits: its size comes
  from the card, not from the screen.
- REPLACE THE PROGRESS BAR with a progress picture of fixed height between the top row and the
  answers: Monster's PATH row (`flex: 0 0 40px`, 32px on short screens) holds 12 stones and a
  landmark; stones are `flex: 1` and at most 22px across, so they fit a 360px phone.
- From top to bottom, then: the top row (question and mascot), the progress picture, the answers
  grid, which takes the rest.
- MAKE THE ANSWERS INVITING: rounded buttons with a "pressable" look (a 4px bottom border in a
  darker shade), and a color of their own for each of the four places, the same for every
  question. The right-answer green and the wrong-answer red still replace those colors while they
  show.
- GIVE FLOATING THINGS A PLACE: the floating points ("+13") rise from just right of the Points
  number (`position: absolute; left: 100%`), not over it; words and toasts pop above the mascot
  or the path, never over the question or the answers.
- A background of the game's own (Monster: a sky gradient, `linear-gradient(#e0f2fe, #fef9c3)`) and
  a rounded font for the game area; the site frame (title band, menu, footer) keeps its own look.
- Check the layout at every size in G6: the mascot must shrink, not push the answers off a
  360x640 phone or a phone held sideways (640x360).
- SHOW THE JOURNEY ON THE "YOU WON!" SCREEN: under "You Won!" and above the score, a row of
  small pictures, one per STAGE of the game, in order, so the player sees everything they went
  through (Train: a thumbnail of each train, steam to maglev; Monster: each form of the monster;
  Space: each planet). Use the game's own stage pictures, made smaller, not new ones (no extra
  size). Each picture about 56px tall (44px on short screens, `max-height: 500px`), the stage's
  short name under it in small text, joined left to right by a thin line or small arrows; the
  last stage marked as reached (a check mark or a gold ring). The row never wraps and never
  makes the overlay wider than the screen: the pictures shrink to fit (`flex: 1 1 0;
  min-width: 0`) on a 360px phone. After "Practice hard ones" ("Practice done!") the row is the
  same.

## G4. What the base game provides (names to refer to)

Use the base file's own names, so the building model ties your changes to its code:

- Config: `CONFIG.GAME`, `CONFIG.MUTED`, `CONFIG.TARGET_LANGUAGE`, `CONFIG.LANGUAGE_CODE`.
- Data:
  - `RAW_DATA` holds 120 facts with ids 1 to 120 and the fields `id | text ("7 x 8") | answer
    ("56")`.
  - Never renumber or reorder them: saved progress refers to the ids. Add new facts after them,
    starting at id 121 (monster adds 2 x 10 … 10 x 10).
  - `FACTS` is the current mode's set, built only in `applyMode`.
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
  - Speech uses `CONFIG.TARGET_LANGUAGE` / `LANGUAGE_CODE`, with the iOS fixes of section 7 of
    the base build instructions.
- Timer: `state.timerStart`, `pauseTimer()`, `resume()`, `currentPlayMs()`.
- End of a game:
  - The "You Won!" overlay: the score, best score, "Your time", the `win-buttons` (Play Again,
    "Practice hard ones"), the NEXT-LEVEL line, the DIVISION line, and SHARE MY RESULTS (a results
    card, shown only on touch devices that can share files).
  - PRACTICE HARD ONES runs a short practice of the weakest facts (`weakFacts()`, ANSWER TIMES)
    and ends with "Practice done!".
- Menu:
  - The base game shows MUTE, BUILD IT, ABOUT, RULES (a popup), RESET and SOURCE. CRITICAL: a
    gamified game keeps EXACTLY this menu, the same items in the same order: it adds no item and
    drops none. A new panel (a sticker book, a garage, a map) opens from a button inside the game
    area, not from the menu bar.
- Site frame (the SITE LAYOUT part of the file):
  - The TITLE BAND is `<h1><a id="tagline" href="https://multiply.by/"><strong>Multiply.by:</strong>
    ...</a></h1>`, sized to fit by `fitTagline()`, with the share icon and share menu. A gamified
    game changes the tagline's text, never its link: it always opens the main game,
    https://multiply.by/, not the gamified game itself.
  - Then the MENU BAR and the FOOTER.

## G5. Lessons learned

- Keep the game fast: celebrations run alongside play, never before the next question. Every added
  element gets `pointer-events: none` and is removed when done. Animate only `transform` and
  `opacity`. Respect REDUCED_MOTION.
- Everything stays in ONE file: no images, fonts or libraries from any server. Use inline SVG, CSS
  and emoji (photo-realistic pictures: detailed SVG, see G2).
- No page scroll on the game, at any screen size. Give a rule for short screens (`max-height:
  500px`, phones held sideways). Things that take room (pictures, mascots, paths) must be able to
  shrink: `flex: 1; min-height: 0`.
- Floating or popping elements need a stated position, or they land on top of labels. For
  example: "+10 rises from just right of the Points number".
- Overlays should be stated as opaque, or the game shows through.
- When a feature of the base game doesn't fit, drop it explicitly, including its checks. When you
  drop the timer, say what replaces "Your time" (monster: stars from the number of mistakes).
- Name every element id that other rules or checks refer to. Otherwise ids may differ between
  builds (e.g. `win-overlay` / `won-overlay`).
- The 100 KB limit is for the base game only: a gamified game has no size limit.
- Bigger, more visual reworkings come out better from the strongest models.

## G6. Checks to write into the CHECKS section

Write these into the CHECKS section as requirements for the finished page, and tell the building
model there, exactly: "These checks describe what the finished page must do. Do not run them or
test the page in a browser: deliver the file as soon as it is written. The site tests every page
itself." A chat model with a browser otherwise plays the whole game through before answering, and
can stall there.

- At phone (360x640), phone sideways (640x360), tablet (768x1024) and laptop (1280x800) sizes: no
  console errors, nothing cut off, no page scroll.
- A whole game can be played: right and wrong answers, the wrong-answer choices (their positions
  and parity), every new animation, the "You Won!" screen, and each mode or set.
- The game's main picture is the element with `id="main-picture"`, visible during play.
- The "You Won!" screen shows one small picture per stage, in order, all on one line at 360px,
  nothing cut off, with the title band and menu still usable above it.
- Each new feature has a check of its own, stated as something a tester can see, e.g. "after 12
  facts are learned, the first stage of the path is full and confetti falls".
- The only sounds are the rising chimes, the wrong-answer "uh-oh" and the win tune: no background
  music, no other sound. At each new stage the chime changes with the picture. MUTE silences all.
