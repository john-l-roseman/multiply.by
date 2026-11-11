# The matching game, built from build-instructions.txt with Gemini (no PWA tags:
# the installable app is the speed game on the main page).
# The page is written under a temporary name and renamed into place,
# so a visitor never gets a half-written page.

index.html: build-instructions.txt ../check-scripts.py
	python3.10 /var/www/openlang.ai/SCRIPTS/run-vertex.py build-instructions.txt index.html.tmp
	python3 ../check-scripts.py index.html.tmp
	mv index.html.tmp index.html
