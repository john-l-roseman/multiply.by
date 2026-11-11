# The page is written under a temporary name and renamed into place,
# so a visitor never gets a half-written page.

index.html: build-instructions.txt
	ANTHROPIC_API_KEY="$$(cat $$HOME/.anthropic_key)" python3.10 run-claude.py build-instructions.txt index.html.tmp
	mv index.html.tmp index.html

