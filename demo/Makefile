# The demo page (index.html) around the demo video. The video itself (demo.webm) is made
# separately, by an AI agent following demo.txt.
# The page is written under a temporary name and renamed into place,
# so a visitor never gets a half-written page.

index.html: prompt.txt ../check-scripts.py
	ANTHROPIC_API_KEY="$$(cat $$HOME/.anthropic_key)" python3.10 ../about/run-claude.py prompt.txt index.html.tmp
	python3 ../check-scripts.py index.html.tmp
	mv index.html.tmp index.html

# The page's complete build instructions (the file SOURCE links to): page.txt with the
# site's shared layout.txt put in at its "#include layout.txt" line.
prompt.txt: page.txt ../layout.txt ../assemble-spec
	../assemble-spec page.txt > prompt.txt.tmp
	mv prompt.txt.tmp prompt.txt
