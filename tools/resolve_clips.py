"""Find Pixabay footage for every clip element and store its download URL in scenes.json.

Runs locally so the API key (../../pixabay_key.txt) never leaves this PC; the cloud
render downloads the public CDN files. A clip element looks like:
  {"type": "clip", "q": "forklift warehouse", "full": true}
Optional "pick": n skips to the n-th best match (to avoid repeats or a bad shot).
Usage: python -I tools/resolve_clips.py EP01_Costco
"""
import json, re, sys, time, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KEY = (ROOT.parent / "pixabay_key.txt").read_text().strip()
_cache = {}


def search(q, vid=None):
    """vid pins one exact Pixabay video id (for a shot already reviewed)."""
    if vid:
        q = f"id:{vid}"
    if q not in _cache:
        params = {"key": KEY, "id": vid} if vid else {"key": KEY, "q": q, "per_page": 30, "safesearch": "true", "order": "popular"}
        url = "https://pixabay.com/api/videos/?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (MarginMechanics clip resolver)"})
        with urllib.request.urlopen(req, timeout=30) as r:
            hits = json.load(r)["hits"]
        # landscape, long enough to sit under narration, HD, no green-screen/alpha assets
        bad = ("green screen", "greenscreen", "chroma", "alpha", "overlay", "transparent",
               "cartoon", "illustration", "vector", "infographic", "flat design", "icon")
        good = [h for h in hits if h["duration"] >= 6 and h["videos"]["medium"]["width"] >= 1280
                and h["videos"]["medium"]["width"] > h["videos"]["medium"]["height"]
                and not any(b in h["tags"].lower() for b in bad)]
        _cache[q] = good
        time.sleep(0.4)
    return _cache[q]


def photos(q, min_w=2400):
    """High-res photos with commercial-use licenses via Openverse (Wikimedia Commons, Flickr CC...)."""
    if ("ov", q) in _cache:
        return _cache[("ov", q)]
    params = {"q": q, "license_type": "commercial", "size": "large", "page_size": 10}
    req = urllib.request.Request("https://api.openverse.org/v1/images/?" + urllib.parse.urlencode(params),
                                 headers={"User-Agent": "MarginMechanics/1.0 (educational YouTube channel)"})
    results = []
    for attempt in range(6):  # Openverse's anonymous API is occasionally flaky; smaller pages help
        if attempt >= 3:
            params["page_size"] = 5
            req = urllib.request.Request("https://api.openverse.org/v1/images/?" + urllib.parse.urlencode(params),
                                         headers={"User-Agent": "MarginMechanics/1.0 (educational YouTube channel)"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                results = json.load(r).get("results", [])
            break
        except Exception as e:
            print(f"  openverse retry {attempt + 1} for '{q}': {e}", flush=True)
            time.sleep(3 * (attempt + 1))
    found = []
    for x in results:
        if x.get("source") in ("rawpixel",):
            continue  # serves only low-res previews regardless of the listed size
        w, h = x.get("width") or 0, x.get("height") or 0
        portrait = h > w
        if (not portrait and w < min_w) or (portrait and h < min_w):
            continue  # big enough to fill a 1440p frame
        lic = {"cc0": "CC0", "pdm": "Public domain"}.get(x["license"], f"CC {x['license'].upper()}")
        lic = f"{lic} {x.get('license_version') or ''}".strip()
        url = x["url"]
        m = re.match(r"https://upload\.wikimedia\.org/wikipedia/commons/(\w/\w\w)/([^/]+)$", url)
        if m and x["width"] > 3840:  # Wikimedia's standard 4K rendition: sharp at 1440p, far smaller download
            url = f"https://upload.wikimedia.org/wikipedia/commons/thumb/{m.group(1)}/{m.group(2)}/3840px-{m.group(2)}"
        found.append({"id": x["id"], "url": url, "thumb": x.get("thumbnail") or url, "portrait": portrait,
                      "credit": f"\"{x.get('title') or 'photo'}\" by {x.get('creator') or 'unknown'}, {lic}, via {x.get('source')}"})
    _cache[("ov", q)] = found
    time.sleep(0.5)
    return found


def main(episode):
    path = ROOT / episode / "scenes.json"
    cfg = json.loads(path.read_text(encoding="utf-8"))
    used, missing, chosen = set(), [], {}
    for out in cfg["outputs"]:
        for sc in out["scenes"]:
            for el in sc.get("elements", []):
                if el.get("url") and "--force" not in sys.argv:
                    continue
                if el.get("type") == "shot" and el.get("img"):  # real photo (Openverse: Wikimedia Commons, Flickr CC)
                    key = ("img", el["img"], el.get("pick", 0))
                    if key not in chosen:
                        allh = [h for h in photos(el["img"]) if ("ov", h["id"]) not in used]
                        hits = [h for h in allh if not h["portrait"]] or allh
                        if not hits:
                            missing.append(el["img"])
                            continue
                        chosen[key] = hits[min(el.get("pick", 0), len(hits) - 1)]
                        used.add(("ov", chosen[key]["id"]))
                    h = chosen[key]
                    el.update(url=h["url"], thumb=h["thumb"], credit=h["credit"], kind="image")
                    if h["portrait"]:
                        el.setdefault("focus", "center 25%")
                    continue
                if el.get("type") not in ("clip", "shot") or not el.get("q"):
                    continue
                key = (el["q"], el.get("pick", 0))
                if key in chosen:  # same shot for the same request (e.g. A/B versions)
                    h = chosen[key]
                else:
                    vid = el.get("pixabay_id")
                    hits = [h for h in search(el["q"], vid) if h["id"] not in used] or search(el["q"], vid)
                    if not hits:
                        missing.append(el["q"])
                        continue
                    h = chosen[key] = hits[min(el.get("pick", 0), len(hits) - 1)]
                    used.add(h["id"])
                # best quality available: 4K when it exists, else 1080p
                # 1080p source: sharp at 1440p output and ~4x cheaper to decode than 4K
                v = next((h["videos"][k] for k in ("medium", "large") if h["videos"][k].get("width") == 1920), None)                     or (h["videos"]["large"] if h["videos"]["large"].get("url") else h["videos"]["medium"])
                el.update(url=v["url"], clipSeconds=h["duration"], credit=f"Pixabay #{h['id']} by {h['user']}",
                          thumb=v.get("thumbnail", ""), kind="video")
    path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"clips resolved: {len(used)}; no match: {missing}")


if __name__ == "__main__":
    main(sys.argv[1])
