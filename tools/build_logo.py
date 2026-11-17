"""Generate the Alles-Atlas.de logo files (SVG) with the wordmark outlined.

Usage:  pip install fonttools brotli && python3 tools/build_logo.py
Writes to assets/brand/.
"""
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "brand"
FONT = ROOT / "assets" / "fonts" / "bricolage-grotesque.woff2"

RED = "#D52B1E"
YELLOW = "#F7C21B"
INK = "#1D1B19"
WHITE = "#FFFFFF"


def mark(x=0, y=0, size=64, bg=RED, fg=WHITE, box=YELLOW):
    """The A-mark: a roof-shaped 'A' whose crossbar is a moving box."""
    s = size / 64
    return f"""<g transform="translate({x} {y}) scale({s})">
  <rect width="64" height="64" rx="15" fill="{bg}"/>
  <path d="M13.5 51 L32 13.5 L50.5 51" fill="none" stroke="{fg}" stroke-width="8.5" stroke-linecap="round" stroke-linejoin="round"/>
  <rect x="22" y="33" width="20" height="15" rx="2" fill="{box}" stroke="{bg}" stroke-width="3" paint-order="stroke"/>
  <path d="M22 38 H42" stroke="{bg}" stroke-width="2"/>
</g>"""


def text_paths(font, text, x, baseline, size, colors):
    """Outline text. colors: list of (substring_length, color) runs."""
    gs = font.getGlyphSet()
    cmap = font.getBestCmap()
    upm = font["head"].unitsPerEm
    sc = size / upm
    hmtx = font["hmtx"]
    out, cursor, i = [], x, 0
    for run_len, color in colors:
        d = []
        for ch in text[i:i + run_len]:
            gname = cmap[ord(ch)]
            pen = SVGPathPen(gs, ntos=lambda v: f"{v:.2f}".rstrip("0").rstrip("."))
            tpen = TransformPen(pen, (sc, 0, 0, -sc, cursor, baseline))
            gs[gname].draw(tpen)
            d.append(pen.getCommands())
            cursor += hmtx[gname][0] * sc
        out.append(f'<path fill="{color}" d="{" ".join(d)}"/>')
        i += run_len
    return "\n".join(out), cursor


def svg(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" '
            f'role="img" aria-labelledby="t"><title id="t">{title}</title>\n{body}\n</svg>\n')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    font = TTFont(str(FONT))
    heavy = instantiateVariableFont(TTFont(str(FONT)), {"wght": 800})
    medium = instantiateVariableFont(font, {"wght": 600})

    # Mark only
    (OUT / "mark.svg").write_text(svg(64, 64, mark(), "Alles-Atlas.de"))
    (OUT / "favicon.svg").write_text(svg(64, 64, mark(), "Alles-Atlas.de"))

    # Horizontal logo, positive + negative
    for name, ink, de, tag in (("logo.svg", INK, RED, "#6B635B"),
                               ("logo-white.svg", WHITE, YELLOW, "#E8DFD3")):
        word, end = text_paths(heavy, "Alles-Atlas.de", 92, 50, 46,
                               [(11, ink), (3, de)])
        sub, end2 = text_paths(medium, "Außergewöhnlich günstig!", 94, 76, 17.5,
                               [(24, tag)])
        w = max(end, end2) + 6
        (OUT / name).write_text(svg(w, 84, mark(0, 4, 76) + "\n" + word + "\n" + sub,
                                    "Alles-Atlas.de: Außergewöhnlich günstig!"))

    # Stacked logo (for flyers, vans, social)
    word, end = text_paths(heavy, "Alles-Atlas.de", 0, 0, 46, [(11, INK), (3, RED)])
    wordw = end
    W = wordw + 40
    word, _ = text_paths(heavy, "Alles-Atlas.de", 20, 170, 46, [(11, INK), (3, RED)])
    sub, e2 = text_paths(medium, "Außergewöhnlich günstig!", 0, 0, 17.5, [(24, "#6B635B")])
    sub, _ = text_paths(medium, "Außergewöhnlich günstig!", (W - e2) / 2, 198, 17.5,
                        [(24, "#6B635B")])
    body = mark((W - 108) / 2, 10, 108) + "\n" + word + "\n" + sub
    (OUT / "logo-stacked.svg").write_text(svg(W, 212, body, "Alles-Atlas.de"))
    print("written:", sorted(p.name for p in OUT.glob("*.svg")))


if __name__ == "__main__":
    main()
