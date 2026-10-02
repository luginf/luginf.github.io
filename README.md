# Personal site

Source-only personal page (project showcase), meant to be hosted as static
files on Neocities. Bilingual: French (primary) and English, each page
linking to the other in the header.

## Files

- `index.t2t` / `index.en.t2t` - home page content: a short intro linking to
  each topic page below. Built as `index.fr.html` (French) and `index.html`
  (English, default page served at the site root).
- `writing.t2t`, `audio.t2t`, `rpg.t2t`, `tools.t2t`, `graphics.t2t`,
  `games.t2t` (each with an `.en.t2t` counterpart) - one page per topic,
  with the full project entries.
  These `.t2t` files hold *only* page content (headings, paragraphs, images,
  links) - no title, no navigation. They start with a blank line on purpose:
  see the Makefile comment below for why.
- `_shell-top.fr.html` / `_shell-top.en.html` - the shared header (site
  name, language switch, topic nav), identical across every page of that
  language. Edit these to change the site title, add/remove/rename a topic,
  or restyle the header markup.
- `_shell-bottom.html` - shared closing tags, same for both languages.
- `style.css` - stylesheet, light/dark aware.
- `fontawesome/` - self-hosted Font Awesome Free (solid style only), used for
  the `fa-microchip` separator between project entries on topic pages.
- `conf.t2t` - shared txt2tags config, pulled in via `%!includeconf: conf.t2t`
  as the second line (after the mandatory leading blank one) of any `.t2t`
  file with more than one project entry. Currently defines only the
  `----@@----` macro, which expands to the `fa-microchip` separator - see
  the comment above that directive for why it has to be a preproc, not a
  postproc.
- `images/` - one screenshot per project, referenced from the `.t2t` files.
- `upload/` - downloadable files (Casio CDP-S360 MIDI definitions), linked from the audio page.
- `*.html` (English) / `*.fr.html` (French) - generated, do not edit by hand.
- `Makefile` - assembles every page from the shell + content files.

## Workflow

1. Edit content in a `.t2t` file, or the header/nav in `_shell-top.*.html`.
2. Run `make` (builds every page).
3. Upload all `*.html` files, `style.css`, `fontawesome/`, `images/`, and `upload/` to
   Neocities. Don't
   upload the `_shell-*.html` or `.t2t` files - they're build inputs, not
   pages.

## How a page is built

Each page is assembled by the Makefile, not by txt2tags alone:

```
{ sed 's/@@EN@@/writing.html/' _shell-top.fr.html;
  perl ~/src/txt2tags-ports/txt2tags-ports/txt2tags_perl/txt2tags.pl \
       -t html5 --no-headers --encoding utf-8 -o - writing.t2t;
  cat _shell-bottom.html; } > writing.fr.html
```

`--no-headers` makes txt2tags emit just the content fragment (no doctype,
`<head>`, or its own `<header>`) - that's what lets the `.t2t` files stay
pure content. The one page-specific value in the shared header (the
language-switch target) is filled in from the target's own filename stem
via `sed`, so no per-page info needs to live in `_shell-top.*.html` either.

Built with our own txt2tags port (see the `Makefile`'s `T2T` variable), not
the system-installed one.

### `.t2t` files start with a blank line

txt2tags treats a document's first 1-3 lines as title/author/date and
strips them from the body - even with `--no-headers`, even when the file
never meant to declare a title. A leading blank line disables that (title
detection requires a non-blank first line), so the whole file is read as
plain body content. Drop that blank line and the first heading (and part
of the following paragraph) silently vanishes from the output.

### Why not `-o file.html` directly to a real file

We use `-o -` (stdout) so the Makefile can pipe the fragment straight
into the `{ ... } > $@` concatenation. This exposed a real encoding bug in
our Perl port: writing to STDOUT never applied a UTF-8 output layer (unlike
writing to a real file, which correctly uses `:encoding(UTF-8)` in
`Savefile()`), so accented characters came out mangled. Fixed in
`txt2tags_perl/txt2tags.pl`'s STDOUT branch of `finish_him()` with a
`binmode(STDOUT, ':encoding(UTF-8)')` before printing.
