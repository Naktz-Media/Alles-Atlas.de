"""Generate the website photos with the Higgsfield API (model: SOUL).

Usage:
    export HF_CREDENTIALS="KEY_ID:KEY_SECRET"
    python3 tools/generate_images.py            # all images
    python3 tools/generate_images.py hero laden # only some

Writes assets/img/<name>.webp. Images are AI-generated mood photos: they show
no logos, no readable text and no recognisable faces, so they are never
mistaken for photos of the real team, van or shop.
"""
import io
import json
import os
import sys
import time
import urllib.request
import uuid
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "img"
API = "https://api.higgsfield.ai"
ENDPOINT = API + "/higgsfield-ai/soul/standard"
CREDS = os.environ.get("HF_CREDENTIALS", "proxy-injected")

STYLE = ("Professional editorial photograph, natural daylight, realistic colours, "
         "shallow depth of field, clean composition, high detail. "
         "No text, no logos, no watermarks, no recognisable faces.")

IMAGES = {
    "hero": ("3:2", 1600,
             "A bright, completely empty and freshly cleaned room in a German Altbau "
             "apartment: herringbone parquet floor, tall white walls, high window with "
             "warm morning sunlight casting soft shadows. In one corner three neatly "
             "stacked closed brown cardboard moving boxes and a wooden broom leaning "
             "against the wall. Calm, tidy, hopeful mood."),
    "entruempelung": ("4:3", 1400,
                      "Clearing out a dusty attic with wooden roof beams: two workers in plain "
                      "dark red work clothes and gloves, seen from behind, carry an old wooden "
                      "dresser towards the stairs. Old furniture, boxes and a rolled carpet "
                      "are partly cleared, light falls through a small roof window."),
    "umzuege": ("4:3", 1400,
                "Close-up of gloved hands sealing a brown cardboard moving box with packing "
                "tape on a wooden floor. In the background an armchair and a sideboard "
                "wrapped in grey quilted moving blankets with straps. Organised, careful, "
                "professional."),
    "haushaltsaufloesung": ("4:3", 1000,
                            "A living room in the middle of a household clearance: a sofa and armchair "
                            "covered with protective sheets, stacked closed cardboard boxes, rolled carpet, "
                            "framed pictures leaning against the wall, soft window light. Orderly and calm."),
    "kellerraeumung": ("4:3", 1000,
                       "A freshly cleared, swept basement cellar room with whitewashed brick walls, "
                       "an empty metal shelf, a single bare bulb and a broom; a few remaining boxes "
                       "by the door ready to be carried out. Clean and bright for a cellar."),
    "geschaeftsaufloesung": ("4:3", 1000,
                             "An office being cleared out: desks pushed together, office chairs stacked, "
                             "monitors and files packed in boxes on a trolley, large windows, daylight. "
                             "No people."),
    "betriebsaufloesung": ("4:3", 1000,
                           "A workshop warehouse being cleared: empty pallet racks, a pallet jack, "
                           "shrink-wrapped pallets of goods ready for transport, concrete floor, "
                           "high windows with daylight. No people."),
    "laden": ("4:3", 1400,
              "Inside a cosy second-hand furniture and antiques shop: vintage wooden "
              "cabinets, a leather sofa, armchairs, brass lamps, framed paintings, ceramic "
              "vases and porcelain on shelves, warm light, inviting and well organised. "
              "No people."),
}


def call(method, url, body=None):
    req = urllib.request.Request(url, method=method, data=json.dumps(body).encode() if body else None)
    req.add_header("Authorization", f"Key {CREDS}")
    req.add_header("Content-Type", "application/json")
    if method == "POST":
        req.add_header("Idempotency-Key", str(uuid.uuid4()))
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


def main(names):
    OUT.mkdir(parents=True, exist_ok=True)
    pending = {}
    for name in names:
        ratio, _, prompt = IMAGES[name]
        res = call("POST", ENDPOINT, {
            "prompt": f"{prompt} {STYLE}",
            "aspect_ratio": ratio,
            "resolution": "1080p",
            "batch_size": 1,
        })
        print(f"{name}: submitted {res['request_id']}", flush=True)
        pending[name] = res["status_url"]

    while pending:
        time.sleep(5)
        for name, status_url in list(pending.items()):
            res = call("GET", status_url)
            if res["status"] in ("queued", "in_progress"):
                continue
            del pending[name]
            if res["status"] != "completed":
                print(f"{name}: {res['status']} {res.get('error', '')}", flush=True)
                continue
            url = res["images"][0]["url"]
            print(f"{name}: done {url}", flush=True)
            try:
                with urllib.request.urlopen(url, timeout=120) as r:
                    im = Image.open(io.BytesIO(r.read())).convert("RGB")
            except Exception as exc:  # e.g. CDN host blocked by the network policy
                print(f"{name}: download failed ({exc})", flush=True)
                continue
            width = IMAGES[name][1]
            if im.width > width:
                im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
            im.save(OUT / f"{name}.webp", "WEBP", quality=82)
            print(f"{name}: saved assets/img/{name}.webp {im.size}", flush=True)


if __name__ == "__main__":
    main(sys.argv[1:] or list(IMAGES))
