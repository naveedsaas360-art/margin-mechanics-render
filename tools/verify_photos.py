"""Download every photo in an episode, check real pixel size, save labelled copies for visual review.

Usage: python -I tools/verify_photos.py EPxx [out_dir]
"""
import json, struct, sys, time, urllib.request
from pathlib import Path

UA = {"User-Agent": "MarginMechanics/1.0 (educational YouTube channel)"}


def dims(b):
    if b[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", b[16:24])
    if b[:4] == b"RIFF" and b[8:12] == b"WEBP":
        if b[12:16] == b"VP8X":
            return 1 + int.from_bytes(b[24:27], "little"), 1 + int.from_bytes(b[27:30], "little")
        if b[12:16] == b"VP8 ":
            return struct.unpack("<H", b[26:28])[0] & 0x3FFF, struct.unpack("<H", b[28:30])[0] & 0x3FFF
    i = 2
    while i < len(b) - 9:  # JPEG: walk markers to the SOF segment
        if b[i] != 0xFF:
            i += 1
            continue
        m = b[i + 1]
        if m in (0xC0, 0xC1, 0xC2):
            h, w = struct.unpack(">HH", b[i + 5:i + 9])
            return w, h
        i += 2 + struct.unpack(">H", b[i + 2:i + 4])[0]
    return 0, 0


ep = sys.argv[1]
out = Path(sys.argv[2] if len(sys.argv) > 2 else f"{ep}/_photo_check")
out.mkdir(parents=True, exist_ok=True)
cfg = json.loads(Path(ep, "scenes.json").read_text(encoding="utf-8"))
seen, n = set(), 0
for o in cfg["outputs"]:
    for s in o["scenes"]:
        for e in s["elements"]:
            if e.get("kind") != "image" or e["url"] in seen:
                continue
            seen.add(e["url"])
            data = None
            for attempt in range(6):
                try:
                    data = urllib.request.urlopen(urllib.request.Request(e["url"], headers=UA), timeout=60).read()
                    break
                except Exception:
                    time.sleep(10 * (attempt + 1))
            label = f"{n:02}_{e['img'].replace(' ', '-')}_p{e.get('pick', 0)}"
            if data is None:
                print(f"{label}: DOWNLOAD FAILED")
            else:
                w, h = dims(data)
                flag = "" if max(w, h) >= 1900 else "   <-- TOO SMALL"
                (out / f"{label}.jpg").write_bytes(data)
                print(f"{label}: {w}x{h}{flag}")
            n += 1
            time.sleep(3)
