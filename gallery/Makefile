# The gallery page (index.html) and its screenshots. Each screenshot is taken from the live game
# (shots.py: three right answers, then a picture), so it is retaken when the game is rebuilt.
# The page is written under a temporary name and renamed into place,
# so a visitor never gets a half-written page.

GAMES = train monster dino space chinese robot plane
SHOTS = base.png $(GAMES:%=%.png)

all: $(SHOTS) index.html

# The base game (https://multiply.by/), built in the site folder itself.
base.png: ../index.html shots.py
	python3 shots.py base $@.tmp.png
	mv $@.tmp.png $@

%.png: ../%/index.html shots.py
	python3 shots.py $* $@.tmp.png
	mv $@.tmp.png $@

index.html: prompt.txt ../check-scripts.py
	ANTHROPIC_API_KEY="$$(cat $$HOME/.anthropic_key)" python3.10 ../about/run-claude.py prompt.txt index.html.tmp
	python3 ../check-scripts.py index.html.tmp
	mv index.html.tmp index.html

# The page's complete build instructions (the file SOURCE links to): page.txt with the
# site's shared layout.txt put in at its "#include layout.txt" line.
prompt.txt: page.txt ../layout.txt ../footer.txt ../assemble-spec
	../assemble-spec page.txt > prompt.txt.tmp
	mv prompt.txt.tmp prompt.txt

.PHONY: all
