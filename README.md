# Alles-Atlas.de

New website and brand for **Alles-Atlas.de · Atlas Entrümpelung** (Dortmund).
It is a static site with no WordPress, no database, no cookies and no tracking.

## Pages (same names and structure as the old site)

| Menu | Old URL (WordPress) | New URL |
|---|---|---|
| Startseite (Willkommen) | `/` and `/?p=1` | `/` |
| Service | `/?page_id=17` | `/service/` |
| Kleinanzeigen | kleinanzeigen.alles-atlas.de | unchanged (external) |
| Kontakt | `/?page_id=7` | `/kontakt/` |
| Bewertung abgeben | bewertung.alles-atlas.de | unchanged (external) |
| Impressum (footer) | `/?page_id=14` | `/impressum/` |
| DSGVO (footer) | `/?page_id=702` | `/dsgvo/` |

`.htaccess` permanently redirects (301) the old `?page_id=` links to the new pages, so Google results and bookmarks keep working.

## Editing

The page content lives in `src/pages/*.html`. The shared header and footer live in `src/layout.html`. After you change either one, run:

```bash
python3 tools/build_pages.py        # writes index.html, service/, kontakt/, …
```

To regenerate the logo files (only needed if you change the logo design):

```bash
pip install fonttools brotli && python3 tools/build_logo.py
```

The four mood photos (`hero`, `entruempelung`, `umzuege`, `laden` in `assets/img/`) were generated with the Higgsfield API (SOUL model). To regenerate them:

```bash
export HF_CREDENTIALS="KEY_ID:KEY_SECRET"
python3 tools/generate_images.py            # or: … hero laden
```

The real photos (the van, the portrait, the flyers and the map) come from the old site.

Preview it locally with `python3 -m http.server` and open http://localhost:8000.

## Deployment

Upload everything **except** `src/`, `tools/` and `.git/` to the web root, and include `.htaccess`.

## Brand

The brand guide is at `/brand/` (hidden from search engines). The logo files are in `assets/brand/`.
