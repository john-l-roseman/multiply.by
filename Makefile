SPEC  = base/prompt.txt
PWA   = PWA-build.txt
FILES = manifest.webmanifest sw.js pwa.js icon.svg og-image.svg
ICONS = icon-192.png icon-512.png

all: gamify/index.html base/index.html index.html $(FILES) $(ICONS) og-image.png sitemap.xml

# THE BASE GAME (https://multiply.by/base/)
# Its complete prompt (base/prompt.txt, the file its SOURCE links to): game.txt with the
# site's shared layout.txt put in at its "#include layout.txt" line.
$(SPEC): game.txt layout.txt assemble-spec
	mkdir -p base
	./assemble-spec game.txt > $(SPEC).tmp
	mv $(SPEC).tmp $(SPEC)

# https://multiply.by/gamify/: ONE file for building a GAMIFIED game in any chatbot: gamify.md (as
# plain text) followed by the base game's complete prompt, HTML-escaped in a <pre> (Gemini's web app
# refuses a .txt upload but takes an .html one). No AI model involved.
gamify/index.html: gamify.md $(SPEC) gamify-html.py
	mkdir -p gamify
	python3 gamify-html.py gamify.md $(SPEC) > gamify/index.html.tmp
	mv gamify/index.html.tmp gamify/index.html

# The plain game page, built from base/prompt.txt (no PWA) by the model named in the
# file "model" (carbon, fable, ...; see run-model).
build/index.html: $(SPEC) model run-model
	mkdir -p build
	./run-model $(SPEC) build/index.html

# THE FRONT PAGE (https://multiply.by/): the base game with a strip of the other games under it.
# home.txt includes game.txt (its /base/ addresses made the root's) and adds the strip. Its
# complete prompt is prompt.txt, at the site's root, built by the model named in home-model
# (carbon: kimi's front pages froze after some moves; the base game stays on kimi, in model).
# (The games chooser is /games/, built in games/.)
prompt.txt: home.txt game.txt layout.txt assemble-spec
	./assemble-spec home.txt > prompt.txt.tmp
	mv prompt.txt.tmp prompt.txt

# build/home/ so that its build.txt does not overwrite the base game's build/build.txt.
build/home/index.html: prompt.txt home-model run-model
	mkdir -p build/home
	./run-model prompt.txt build/home/index.html home-model

# PWA files, copied verbatim from PWA-build.txt.
$(FILES) &: $(PWA) extract-files.py
	python3 extract-files.py $(PWA) . $(FILES)

build/pwa-head.html: $(PWA) extract-files.py
	python3 extract-files.py $(PWA) build pwa-head.html

# Every served file is written under a temporary name and renamed into place,
# so a visitor never gets a half-written page.

# The served pages: the plain page with the PWA tags inserted before </head>.
base/index.html: build/index.html build/pwa-head.html check-scripts.py
	test "$$(grep -c "</head>" build/index.html)" = 1
	sed "/<\/head>/e cat build/pwa-head.html" build/index.html > base/index.html.tmp
	@size=$$(wc -c < base/index.html.tmp); if [ $$size -ge 100000 ]; then \
	  echo "WARNING: base/index.html is $$size bytes; the About page says less than 100 KB"; fi
	python3 check-scripts.py base/index.html.tmp
	mv base/index.html.tmp base/index.html

index.html: build/home/index.html build/pwa-head.html check-scripts.py
	test "$$(grep -c "</head>" build/home/index.html)" = 1
	sed "/<\/head>/e cat build/pwa-head.html" build/home/index.html > index.html.tmp
	@size=$$(wc -c < index.html.tmp); if [ $$size -ge 100000 ]; then \
	  echo "WARNING: index.html is $$size bytes; the About page says less than 100 KB"; fi
	python3 check-scripts.py index.html.tmp
	mv index.html.tmp index.html

# App icons, rendered from icon.svg.
icon-%.png: icon.svg
	convert -background none -density 300 icon.svg -resize $*x$* -depth 8 -strip $@.tmp.png
	mv $@.tmp.png $@

# Link preview picture (Open Graph), rendered from og-image.svg.
og-image.png: og-image.svg
	convert -background none -density 96 og-image.svg -depth 8 -strip og-image.tmp.png
	mv og-image.tmp.png og-image.png

# sitemap.xml for search engines (robots.txt points to it): the public pages, each dated by its
# index.html. Remade on every make (it takes a moment); it never depends on a page, so making it
# never starts a page build. Pages are listed in make-sitemap.py.
sitemap.xml:
	python3 make-sitemap.py > sitemap.xml.tmp
	mv sitemap.xml.tmp sitemap.xml

.PHONY: all sitemap.xml
