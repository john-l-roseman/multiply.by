# The Build it page (index.html) and its screenshots (also used by the front page). Each screenshot is taken from the live game
# (shots.py: sixteen right answers, then a picture), so it is retaken when the game is rebuilt.
# The page is written under a temporary name and renamed into place,
# so a visitor never gets a half-written page.

GAMES = train monster dino space chinese robot plane blocks
SHOTS = base.png $(GAMES:%=%.png)
# The front page's strip pictures (thumbs.py: the game's main picture, 200 x 160). Made only when
# missing (no prerequisites), so a hand-made one in ../thumbnails/ is never overwritten; delete a
# file to make it again.
THUMBS = $(GAMES:%=../thumbnails/%-thumbnail.png)

all: $(SHOTS) $(THUMBS) index.html

../thumbnails/%-thumbnail.png:
	mkdir -p ../thumbnails
	python3 thumbs.py $* $@.tmp.png
	mv $@.tmp.png $@

# The base game (https://multiply.by/base/).
base.png: ../base/index.html shots.py
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
