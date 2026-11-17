"""Build the static site: wraps each body in src/pages/ with the shared layout.

Usage:  python3 tools/build_pages.py
Each page file starts with a front-matter block:

    ---
    slug: service            (folder name; "" for the homepage)
    title: Seitentitel
    description: Meta-Beschreibung
    nav: service             (which menu item is active)
    ---
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
SITE = "https://alles-atlas.de"

BUSINESS = {
    "@context": "https://schema.org",
    "@type": "LocalBusiness",
    "name": "Alles-Atlas.de – Atlas Entrümpelung",
    "description": "Entrümpelung, Haushaltsauflösung, Umzüge, Transporte und Second-Hand-Ladengeschäft in Dortmund.",
    "url": SITE + "/",
    "logo": SITE + "/assets/brand/logo.svg",
    "image": SITE + "/assets/img/transporter.webp",
    "telephone": "+49 231 13091118",
    "email": "info@alles-atlas.de",
    "founder": "Aziz Nougaoui",
    "slogan": "Außergewöhnlich günstig!",
    "address": {
        "@type": "PostalAddress",
        "streetAddress": "Mozartstr. 17",
        "postalCode": "44147",
        "addressLocality": "Dortmund",
        "addressCountry": "DE",
    },
    "geo": {"@type": "GeoCoordinates", "latitude": 51.5258123, "longitude": 7.4542151},
    "areaServed": "Dortmund",
    "sameAs": ["https://facebook.alles-atlas.de/", "https://kleinanzeigen.alles-atlas.de/"],
}


def parse(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    meta = {}
    for line in m.group(1).splitlines():
        key, _, value = line.partition(":")
        meta[key.strip()] = value.strip()
    return meta, text[m.end():]


def render(template, values):
    return re.sub(r"\{\{(\w+)\}\}", lambda m: values.get(m.group(1), m.group(0)), template)


def main():
    layout = (SRC / "layout.html").read_text(encoding="utf-8")
    for page in sorted((SRC / "pages").glob("*.html")):
        meta, body = parse(page)
        slug = meta["slug"]
        base = "" if slug == "" else "../"
        nav = meta.get("nav", "")
        values = {
            "base": base,
            "home": base or "./",
            "title": meta["title"],
            "description": meta["description"],
            "canonical": f"{SITE}/{slug + '/' if slug else ''}",
            "robots": meta.get("robots", "index,follow"),
            "jsonld": json.dumps(BUSINESS, ensure_ascii=False),
            **{f"cur_{k}": ' aria-current="page"' if nav == k else ""
               for k in ("home", "service", "kontakt", "impressum", "dsgvo")},
        }
        values["body"] = render(body, values)
        out = ROOT / slug / "index.html" if slug else ROOT / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render(layout, values), encoding="utf-8")
        print("built", out.relative_to(ROOT))


if __name__ == "__main__":
    main()
