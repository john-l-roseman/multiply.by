# The page is written under a temporary name and renamed into place,
# so a visitor never gets a half-written page.

index.html: build-instructions.txt ../check-scripts.py
	ANTHROPIC_API_KEY="$$(cat $$HOME/.anthropic_key)" python3.10 run-claude.py build-instructions.txt index.html.tmp
	python3 ../check-scripts.py index.html.tmp
	mv index.html.tmp index.html

# The page's complete build instructions (the file SOURCE links to): about.txt with the
# site's shared layout.txt put in at its "#include layout.txt" line.
build-instructions.txt: about.txt ../layout.txt ../assemble-spec
	../assemble-spec about.txt > build-instructions.txt.tmp
	mv build-instructions.txt.tmp build-instructions.txt

