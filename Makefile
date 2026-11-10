SPEC  = build-instructions.txt
PWA   = PWA-build.txt
FILES = manifest.webmanifest sw.js pwa.js icon.svg
ICONS = icon-192.png icon-512.png

all: index.html $(FILES) $(ICONS)

# The plain game page, built from build-instructions.txt (no PWA).
build/index.html: $(SPEC)
	mkdir -p build
	python3.10 /var/www/openlang.ai/SCRIPTS/run-vertex.py $(SPEC) build/index.html

# PWA files, copied verbatim from PWA-build.txt.
$(FILES) &: $(PWA) extract-files.py
	python3 extract-files.py $(PWA) . $(FILES)

build/pwa-head.html: $(PWA) extract-files.py
	python3 extract-files.py $(PWA) build pwa-head.html

# Every served file is written under a temporary name and renamed into place,
# so nginx's open-file cache never serves a stale, resized copy.

# The served page: the plain page with the PWA tags inserted before </head>.
index.html: build/index.html build/pwa-head.html check-scripts.py check-data.py
	test "$$(grep -c "</head>" build/index.html)" = 1
	sed "/<\/head>/e cat build/pwa-head.html" build/index.html > index.html.tmp
	@size=$$(wc -c < index.html.tmp); if [ $$size -ge 50000 ]; then \
	  echo "WARNING: index.html is $$size bytes; the About page says less than 50 KB"; fi
	python3 check-scripts.py index.html.tmp
	python3 check-data.py index.html.tmp
	mv index.html.tmp index.html

# App icons, rendered from icon.svg.
icon-%.png: icon.svg
	convert -background none -density 300 icon.svg -resize $*x$* -depth 8 -strip $@.tmp.png
	mv $@.tmp.png $@

.PHONY: all
