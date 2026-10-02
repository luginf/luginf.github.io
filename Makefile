T2T := perl $(HOME)/src/txt2tags-ports/txt2tags-ports/txt2tags_perl/txt2tags.pl

# Naming: X.fr.html = French, X.html = English (default; index.html is what
# GitHub Pages serves at the root). Sources: X.t2t (French), X.en.t2t (English).
PAGES   := index writing audio rpg tools graphics games
FR_HTML := $(addsuffix .fr.html,$(PAGES))
EN_HTML := $(addsuffix .html,$(PAGES))
HTML    := $(FR_HTML) $(EN_HTML)

all: $(HTML)

# Each page is built by wrapping the .t2t file's raw content (--no-headers:
# no doctype/head/header, just the body) between the shared header/footer
# shell for its language. The FR/EN shells are near-identical except for
# nav labels and the lang-switch target, which is filled in per page from
# the target's own stem ($*) - no lang info needs to live in the .t2t files.
$(FR_HTML): %.fr.html: %.t2t _shell-top.fr.html _shell-bottom.html
	{ sed 's/@@EN@@/$*.html/' _shell-top.fr.html; \
	  $(T2T) -t html5 --no-headers --encoding utf-8 -o - $<; \
	  cat _shell-bottom.html; } > $@

$(EN_HTML): %.html: %.en.t2t _shell-top.en.html _shell-bottom.html
	{ sed 's/@@FR@@/$*.fr.html/' _shell-top.en.html; \
	  $(T2T) -t html5 --no-headers --encoding utf-8 -o - $<; \
	  cat _shell-bottom.html; } > $@

.PHONY: all clean
clean:
	rm -f $(HTML)
