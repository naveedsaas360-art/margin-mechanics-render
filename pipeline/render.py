"""Render an episode folder into finished videos.

Reads <episode>/scenes.json, voices each scene with edge-tts, animates its image
with a slow zoom (FFmpeg zoompan), and joins the scenes. Long videos also get an
SRT caption file for upload; Shorts get captions burned in.

Usage: python pipeline/render.py EP01_Costco
"""
import asyncio, json, math, os, re, subprocess, sys, time
import xml.etree.ElementTree as ET
from pathlib import Path

import edge_tts

FPS = 30
PAD = 0.35  # seconds of breathing room after each scene
INK = "0x0E1116"


def run(cmd, cwd=None):
    cmd = [str(c) for c in cmd]
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True, cwd=cwd)


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(path)], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


async def speak(text, voice, rate, mp3):
    """Write narration to mp3 and return word timings [(start, end, word)]."""
    for attempt in range(4):
        try:
            try:
                com = edge_tts.Communicate(text, voice, rate=rate, boundary="WordBoundary")
            except TypeError:  # older edge-tts without the boundary argument
                com = edge_tts.Communicate(text, voice, rate=rate)
            words = []
            with open(mp3, "wb") as f:
                async for ch in com.stream():
                    if ch["type"] == "audio":
                        f.write(ch["data"])
                    elif ch["type"] == "WordBoundary":
                        start = ch["offset"] / 1e7
                        words.append((start, start + ch["duration"] / 1e7, ch["text"]))
            return words
        except Exception as e:  # network hiccups
            print(f"tts retry {attempt + 1}: {e}", flush=True)
            await asyncio.sleep(5)
    raise RuntimeError(f"TTS failed for: {text[:60]}")


def ts(t):
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h):02}:{int(m):02}:{s:06.3f}".replace(".", ",")


def cues(words, offset=0.0, max_words=8):
    """Group word timings into caption cues."""
    out, cur = [], []
    for j, w in enumerate(words):
        cur.append(w)
        # word timings carry no punctuation, so a pause before the next word marks a phrase end
        pause = j + 1 < len(words) and words[j + 1][0] - w[1] > 0.2
        if len(cur) >= max_words or pause or w[2][-1:] in ".?!,":
            out.append((cur[0][0] + offset, cur[-1][1] + offset, " ".join(x[2] for x in cur)))
            cur = []
    if cur:
        out.append((cur[0][0] + offset, cur[-1][1] + offset, " ".join(x[2] for x in cur)))
    return out


def write_srt(path, items):
    with open(path, "w", encoding="utf-8") as f:
        for i, (a, b, t) in enumerate(items, 1):
            f.write(f"{i}\n{ts(a)} --> {ts(b)}\n{t}\n\n")


def render_scene(img, mp3, out, vertical, zoom_in, srt=None):
    dur = duration(mp3) + PAD
    n = math.ceil(dur * FPS)
    z = f"1+0.08*on/{n}" if zoom_in else f"1.08-0.08*on/{n}"
    pan = f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:fps={FPS}"
    if vertical:
        vf = (f"scale=3240:-2,{pan}:s=1080x608,"
              f"pad=1080:1920:0:420:color={INK}")
        if srt:
            vf += (f",subtitles={srt}:force_style='FontName=DejaVu Sans,Bold=1,FontSize=15,"
                   "PrimaryColour=&H0031C5FF,OutlineColour=&H00000000,BorderStyle=1,Outline=3,"
                   "Shadow=0,Alignment=2,MarginV=70'")
    else:
        vf = f"scale=3840:-2,{pan}:s=1920x1080"
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", img, "-i", mp3,
         "-filter_complex", f"[0:v]{vf},format=yuv420p[v];[1:a]apad,aresample=48000[a]",
         "-map", "[v]", "-map", "[a]", "-t", f"{dur:.3f}",
         "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-r", FPS,
         "-c:a", "aac", "-b:a", "192k", "-ac", "2", out])
    return dur


async def render_output(ep, spec, cfg, outdir, work):
    name, vertical = spec["name"], spec.get("format") == "short"
    total, caption_items, parts, chapters = 0.0, [], [], []
    for i, sc in enumerate(spec["scenes"]):
        if sc.get("chapter"):
            chapters.append(f"{int(total // 60)}:{int(total % 60):02} {sc['chapter']}")
        mp3 = work / f"{name}_{i:02}.mp3"
        words = await speak(sc["text"], cfg["voice"], cfg.get("rate", "+0%"), mp3)
        clip = work / f"{name}_{i:02}.mp4"
        srt = None
        if vertical:
            srt = f"{name}_{i:02}.srt"  # relative: keeps the subtitles filter path simple
            write_srt(work / srt, cues(words, max_words=3))
        zoom_in = sc.get("zoom", "in" if i % 2 == 0 else "out") == "in"
        # subtitles filter resolves relative paths against cwd, so render from work/
        dur = render_in(work, ep / sc["image"], mp3, clip, vertical, zoom_in, srt)
        caption_items += cues(words, offset=total)
        total += dur
        parts.append(clip)
    lst = work / f"{name}.txt"
    lst.write_text("".join(f"file '{p.name}'\n" for p in parts))
    final = outdir / f"{name}.mp4"
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
         "-c:v", "copy", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
         "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", final])
    if not vertical:
        write_srt(outdir / f"{name}.srt", caption_items)
    if chapters:
        (outdir / f"{name}_chapters.txt").write_text("\n".join(chapters) + "\n", encoding="utf-8")
    print(f"DONE {final} ({total / 60:.1f} min)", flush=True)


THEME = {
    "primaryColor": "#FFC531", "accentColor": "#2BD67B", "backgroundColor": "#0E1116",
    "surfaceColor": "#1C212A", "textColor": "#FFFFFF", "mutedTextColor": "#969EAA",
    "headingFont": "Inter", "bodyFont": "Inter", "monoFont": "JetBrains Mono",
    "chartColors": ["#FFC531", "#2BD67B", "#FF4D4D", "#969EAA", "#4DA3FF", "#FFFFFF"],
    "springConfig": {"damping": 18, "stiffness": 110, "mass": 1},
    "transitionDuration": 0.35,
    "captionHighlightColor": "#FFC531", "captionBackgroundColor": "rgba(14,17,22,0.8)",
}


async def render_remotion(ep, spec, cfg, outdir, work, composer):
    """Animated version: OpenMontage's Remotion 'Explainer' composition.

    A scene's optional "cut" dict (type bar_chart, stat_card, comparison, ...)
    becomes an animated component; scenes without one show their image.
    """
    name = spec["name"]
    pub = composer / "public" / "mm" / name
    pub.mkdir(parents=True, exist_ok=True)
    t, cuts, chapters, wavs, caption_items = 0.0, [], [], [], []
    for i, sc in enumerate(spec["scenes"]):
        if sc.get("chapter"):
            chapters.append(f"{int(t // 60)}:{int(t % 60):02} {sc['chapter']}")
        mp3 = work / f"{name}_{i:02}.mp3"
        words = await speak(sc["text"], cfg["voice"], cfg.get("rate", "+0%"), mp3)
        d = duration(mp3) + PAD
        wav = work / f"{name}_{i:02}.wav"
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp3, "-af", "apad", "-t", f"{d:.3f}",
             "-ar", "48000", "-ac", "2", wav])
        wavs.append(wav)
        cut = dict(sc.get("cut") or {})
        if "type" not in cut:
            img = Path(sc["image"]).name
            (pub / img).write_bytes((ep / sc["image"]).read_bytes())
            cut.update(source=f"mm/{name}/{img}", animation="ken-burns")
        cut.setdefault("source", "")
        cut.update(id=f"s{i:02}", in_seconds=round(t, 3), out_seconds=round(t + d, 3))
        cuts.append(cut)
        caption_items += cues(words, offset=t)
        t += d
    lst = work / f"{name}_wav.txt"
    lst.write_text("".join(f"file '{w.name}'\n" for w in wavs))
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
         "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", pub / "narration.wav"])
    props = {"cuts": cuts, "themeConfig": THEME,
             "audio": {"narration": {"src": f"mm/{name}/narration.wav"}}}
    props_path = work / f"{name}_props.json"
    props_path.write_text(json.dumps(props, indent=1), encoding="utf-8")
    final = outdir / f"{name}.mp4"
    run(["npx", "remotion", "render", "src/index.tsx", "Explainer", final,
         f"--props={props_path}", "--codec=h264", "--crf=20"], cwd=composer)
    write_srt(outdir / f"{name}.srt", caption_items)
    if chapters:
        (outdir / f"{name}_chapters.txt").write_text("\n".join(chapters) + "\n", encoding="utf-8")
    print(f"DONE {final} ({t / 60:.1f} min)", flush=True)


DRAW_SECONDS = {"write": 0.9, "count": 1.2, "icon": 1.0, "bars": 2.0, "arrow": 0.6, "circle": 0.6,
                "underline": 0.5, "box": 0.7, "highlight": 0.4, "line": 0.5}
SILENT_TYPES = {"count", "highlight"}  # no marker-squeak sound
LEAD = 0.45  # start drawing slightly before the cue word, so the eye arrives as the word does


def norm(w):
    return re.sub(r"[^a-z0-9$%.]", "", w.lower()).strip(".")


def cue_time(at, words, after):
    """Start time of the first occurrence of phrase `at` at/after word index `after`."""
    target = [norm(x) for x in at.split()]
    keys = [norm(w[2]) for w in words]
    for start in (after, 0):
        for i in range(start, len(keys) - len(target) + 1):
            if keys[i:i + len(target)] == target:
                return words[i][0], i
    print(f"  ! cue '{at}' not found; placing after previous element", flush=True)
    return None, after


def svg_paths(svg_file):
    """Tabler icon -> list of path 'd' strings (shapes converted to paths)."""
    root = ET.parse(svg_file).getroot()
    out = []
    for e in root.iter():
        tag, a = e.tag.split("}")[-1], e.attrib
        if a.get("stroke") == "none" and tag == "path" and a.get("d", "").startswith("M0 0h24v24H0z"):
            continue  # tabler's invisible bounding box
        if tag == "path":
            out.append(a["d"])
        elif tag == "circle":
            cx, cy, r = (float(a[k]) for k in ("cx", "cy", "r"))
            out.append(f"M {cx - r} {cy} a {r} {r} 0 1 0 {2 * r} 0 a {r} {r} 0 1 0 {-2 * r} 0")
        elif tag == "ellipse":
            cx, cy, rx, ry = (float(a[k]) for k in ("cx", "cy", "rx", "ry"))
            out.append(f"M {cx - rx} {cy} a {rx} {ry} 0 1 0 {2 * rx} 0 a {rx} {ry} 0 1 0 {-2 * rx} 0")
        elif tag == "line":
            out.append(f"M {a['x1']} {a['y1']} L {a['x2']} {a['y2']}")
        elif tag == "rect":
            x, y, w, h = (float(a.get(k, 0)) for k in ("x", "y", "width", "height"))
            out.append(f"M {x} {y} h {w} v {h} h {-w} Z")
        elif tag in ("polyline", "polygon"):
            pts = a["points"].replace(",", " ").split()
            d = "M " + " L ".join(f"{pts[j]} {pts[j + 1]}" for j in range(0, len(pts), 2))
            out.append(d + (" Z" if tag == "polygon" else ""))
    return out


def fetch_media(url, dest):
    """Download with retries; Wikimedia 4K renditions fall back to the original file."""
    urls = [url]
    m = re.match(r"(https://upload\.wikimedia\.org/wikipedia/commons)/thumb/(\w/\w\w/[^/]+)/\d+px-[^/]+$", url)
    if m:
        urls.append(f"{m.group(1)}/{m.group(2)}")
    for u in urls:
        r = subprocess.run(["curl", "-sfL", "--retry", "6", "--retry-delay", "10", "--retry-all-errors",
                            "-A", "MarginMechanics/1.0 (educational YouTube channel)", "-o", str(dest), u])
        time.sleep(1.5)  # polite: Wikimedia rate-limits bursts of large downloads
        if r.returncode == 0 and dest.exists() and dest.stat().st_size > 10000:
            return True
        print(f"  ! download failed ({r.returncode}): {u}", flush=True)
    dest.unlink(missing_ok=True)
    return False


def normalize_video(src):
    """Re-encode a stock clip to light 1080p H.264 (short GOP, no audio): fast, reliable decoding while rendering."""
    out = src.with_name(src.stem + "_1080.mp4")
    if not out.exists():
        r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-t", "40",
                            "-vf", "scale=-2:1080:flags=lanczos,fps=30", "-an", "-c:v", "libx264", "-preset", "veryfast",
                            "-crf", "18", "-g", "30", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out)])
        if r.returncode != 0 or not out.exists():
            print(f"  ! could not normalize {src.name}; using original", flush=True)
            return src
    src.unlink(missing_ok=True)  # keep the artifact small
    return out


def pen_sfx(intervals, total, out):
    """Soft marker-squeak noise during each drawing interval."""
    if not intervals:
        return False
    gate = "+".join(f"between(t,{a:.2f},{b:.2f})" for a, b in intervals)
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i",
         f"anoisesrc=d={total:.2f}:c=pink:a=0.6:r=48000",
         "-af", f"highpass=f=1800,lowpass=f=6000,tremolo=f=11:d=0.8,"
                f"volume='if({gate},0.05,0)':eval=frame,afade=t=in:d=0.1",
         "-ac", "2", out])
    return True


_kokoro = None


def speak_kokoro(text, voice, speed, mp3):
    """Kokoro-82M (Apache-2.0) voice; returns word timings like speak()."""
    global _kokoro
    import numpy as np
    import soundfile as sf
    from kokoro import KPipeline
    _kokoro = _kokoro or KPipeline(lang_code="a")
    chunks, words, offset = [], [], 0.0
    for r in _kokoro(text, voice=voice, speed=speed):
        audio = r.audio.numpy() if hasattr(r.audio, "numpy") else np.asarray(r.audio)
        toks = [tk for tk in (getattr(r, "tokens", None) or []) if getattr(tk, "start_ts", None) is not None
                and any(ch.isalnum() for ch in tk.text)]
        if toks:
            words += [(offset + tk.start_ts, offset + (tk.end_ts or tk.start_ts + 0.25), tk.text) for tk in toks]
        else:  # no timestamps: spread this chunk's words by character length
            ws = r.graphemes.split()
            total = sum(len(w) + 1 for w in ws) or 1
            pos = 0.0
            for w in ws:
                dur = len(audio) / 24000 * (len(w) + 1) / total
                words.append((offset + pos, offset + pos + dur, w))
                pos += dur
        chunks.append(audio)
        offset += len(audio) / 24000
    wav = Path(str(mp3).replace(".mp3", "_k.wav"))
    sf.write(wav, np.concatenate(chunks), 24000)
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-b:a", "192k", mp3])
    return words


async def voice_for(text, cfg, spec, mp3):
    tts = spec.get("tts", cfg.get("tts", "edge"))
    if tts == "kokoro":
        return speak_kokoro(text, spec.get("voice", "am_michael"), spec.get("speed", 1.0), mp3)
    return await speak(text, spec.get("voice", cfg["voice"]), spec.get("rate", cfg.get("rate", "+0%")), mp3)


def fetch_music(cfg, spec, pub):
    """Download the background track once; returns its file name (or None)."""
    m = spec.get("music", cfg.get("music"))
    if not m:
        return None
    f = pub / ("music_" + m["url"].split("/")[-1].replace("%20", "_"))
    if not f.exists():
        run(["curl", "-sfL", "-A", "Mozilla/5.0", "-o", f, m["url"]])
    return {"file": f.name, "volume": m.get("volume", 0.08)}


async def render_whiteboard(ep, spec, cfg, outdir, work, wb):
    """Hand-drawn whiteboard video: each element is drawn when its cue word is spoken."""
    name = spec["name"]
    vertical = spec.get("format") == "short"
    doc = spec.get("engine") in ("doc", "story3d")  # Doc-family styles: 1440p, cue-timed overlays
    pub = wb / "public" / "mm"
    pub.mkdir(parents=True, exist_ok=True)
    icons = wb / "node_modules" / "@tabler" / "icons" / "icons" / "outline"
    t, scenes, wavs, chapters, caption_items, words_all, draws = 0.0, [], [], [], [], [], []
    credits = set()
    for i, sc in enumerate(spec["scenes"]):
        if sc.get("chapter"):
            chapters.append(f"{int(t // 60)}:{int(t % 60):02} {sc['chapter']}")
        mp3 = work / f"{name}_{i:02}.mp3"
        words = await voice_for(sc["text"], cfg, spec, mp3)
        d = duration(mp3) + PAD
        wav = work / f"{name}_{i:02}.wav"
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp3, "-af", "apad", "-t", f"{d:.3f}",
             "-ar", "48000", "-ac", "2", wav])
        wavs.append(wav)
        els, prev_end, idx = [], 0.25, 0
        for el in sc.get("elements", []):
            el = dict(el)
            el.setdefault("dur", DRAW_SECONDS.get(el["type"], 0.8))
            start = None
            if el.get("at"):
                start, idx = cue_time(el.pop("at"), words, idx)
                if start is not None:
                    start = max(0.0, start - LEAD)
            if start is None:
                start = prev_end + 0.15
            el["t"] = round(start, 3)
            prev_end = start + el["dur"]
            if el.get("reveal_at"):  # staged animations (e.g. loop arrows): one time per cue
                el["reveal"] = []
                for cue in el.pop("reveal_at"):
                    rt, _ = cue_time(cue, words, 0)
                    el["reveal"].append(round(max(0.0, rt - LEAD), 3) if rt is not None else None)
            if el.get("until_at"):  # remove this element when a later cue word is spoken
                ut, _ = cue_time(el.pop("until_at"), words, 0)
                if ut is not None:
                    el["until"] = round(max(start + 0.5, ut - LEAD - 0.05), 3)  # gone before the next item starts
            if el["type"] == "shot" and el.get("local"):  # pre-made image committed with the episode
                src_img = Path(el["local"])
                dest = pub / "clips" / src_img.name
                dest.parent.mkdir(exist_ok=True)
                if not dest.exists():
                    # upscale to 1440p-ready size with a light sharpen (Lanczos)
                    r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src_img), "-vf",
                                        "scale=2880:-2:flags=lanczos,unsharp=5:5:0.6", "-q:v", "2", str(dest)])
                    if r.returncode != 0:
                        dest.write_bytes(src_img.read_bytes())
                el["src"] = f"mm/clips/{dest.name}"
                credits.add(el.get("credit", ""))
            elif el["type"] in ("clip", "shot"):
                if not el.get("url"):
                    print(f"  ! clip '{el.get('q')}' has no url (run tools/resolve_clips.py)", flush=True)
                    continue
                clip_file = pub / "clips" / (el["url"].split("/")[-1].split("?")[0])
                clip_file.parent.mkdir(exist_ok=True)
                if not clip_file.exists() and not fetch_media(el["url"], clip_file):
                    print(f"  ! skipped shot, media unavailable: {el['url']}", flush=True)
                    continue
                if clip_file.suffix.lower() == ".mp4":
                    clip_file = normalize_video(clip_file)
                el["src"] = f"mm/clips/{clip_file.name}"
                credits.add(el.get("credit", ""))
            for r in el.get("reacts", []):  # character changes face/pose on a cue word
                rt, _ = cue_time(r.pop("at"), words, 0) if r.get("at") else (None, 0)
                r["t"] = round(max(0.0, (rt if rt is not None else start + 1.0) - LEAD / 2), 3)
            if el["type"] == "icon":
                svg = icons / f"{el['name']}.svg"
                el["paths"] = svg_paths(svg) if svg.exists() else []
                if not el["paths"]:
                    print(f"  ! icon '{el['name']}' missing", flush=True)
            els.append(el)
        # Never open on a blank board: the first drawing starts right away.
        drawn = [e for e in els if e["type"] not in ("clip", "shot", "bg", "panel")]
        if drawn and min(e["t"] for e in drawn) > 0.6:
            min(drawn, key=lambda e: e["t"])["t"] = 0.15
        if doc:  # each shot holds until the next cut (plus a little overlap for the crossfade)
            shots = sorted((e for e in els if e["type"] == "shot"), key=lambda e: e["t"])
            if shots:
                shots[0]["t"] = 0.0  # scenes always open on footage
            for e in els:  # backgrounds without a cue are there from the first frame
                if e["type"] in ("bg", "panel") and e["t"] < 0.6:
                    e["t"] = 0.0
            for a, b in zip(shots, shots[1:] + [None]):
                a["life"] = round(((b["t"] if b else d) - a["t"]) + 0.6, 3)
        else:
            draws += [(t + e["t"], t + e["t"] + e["dur"]) for e in els if e["type"] not in SILENT_TYPES | {"clip"}]
        scenes.append({"start": round(t, 3), "end": round(t + d, 3), "elements": els})
        caption_items += cues(words, offset=t)
        words_all += [{"w": w, "s": round(a + t, 3), "e": round(b + t, 3)} for a, b, w in words]
        t += d
    lst = work / f"{name}_wav.txt"
    lst.write_text("".join(f"file '{w.name}'\n" for w in wavs))
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
         "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", pub / f"{name}.wav"])
    w, h = (1080, 1920) if vertical else ((2560, 1440) if doc else (1920, 1080))
    props = {"duration": round(t, 3), "scenes": scenes, "audio": f"mm/{name}.wav", "width": w, "height": h}
    for key in ("countdown", "ticker"):  # channel identity overlays (Doc style)
        if spec.get(key, cfg.get(key)):
            props[key] = spec.get(key, cfg.get(key))
    if pen_sfx(draws, t, pub / f"{name}_sfx.wav"):
        props["sfx"] = f"mm/{name}_sfx.wav"
    if vertical:
        props["captions"] = words_all
    props_path = pub / f"{name}_props.json"
    props_path.write_text(json.dumps(props), encoding="utf-8")
    final = outdir / f"{name}.mp4"
    if os.environ.get("WB_STAGE") == "prepare":
        # Parallel mode: the workflow renders frame chunks on several machines, then
        # assemble.py joins them and adds the audio.
        (outdir / f"{name}_job.json").write_text(json.dumps({
            "name": name, "comp": {"doc": "Doc", "story3d": "Story3D"}.get(spec.get("engine"), "Board"), "frames": math.ceil(t * FPS), "duration": round(t, 3),
            "audio": f"{name}.wav", "sfx": f"{name}_sfx.wav" if "sfx" in props else None,
            "music": fetch_music(cfg, spec, pub)}), encoding="utf-8")
    else:
        run(["npx", "remotion", "render", "src/index.js", "Board", final, f"--props={props_path}",
             "--codec=h264", "--crf=18", "--concurrency=100%"], cwd=wb)
    if not vertical:
        write_srt(outdir / f"{name}.srt", caption_items)
    if chapters:
        (outdir / f"{name}_chapters.txt").write_text("\n".join(chapters) + "\n", encoding="utf-8")
    if credits - {""}:
        (outdir / f"{name}_footage_credits.txt").write_text(
            "Footage: Pixabay (Pixabay Content License)\n" + "\n".join(sorted(credits - {""})) + "\n", encoding="utf-8")
    print(f"DONE {final} ({t / 60:.1f} min)", flush=True)


def render_in(work, img, mp3, clip, vertical, zoom_in, srt):
    cwd = os.getcwd()
    os.chdir(work)
    try:
        return render_scene(Path(img).resolve(), mp3.name, clip.name, vertical, zoom_in, srt)
    finally:
        os.chdir(cwd)


async def main(episode):
    ep = Path(episode).resolve()
    cfg = json.loads((ep / "scenes.json").read_text(encoding="utf-8"))
    outdir = Path("out").resolve(); outdir.mkdir(exist_ok=True)
    work = Path("work").resolve(); work.mkdir(exist_ok=True)
    only = sys.argv[2] if len(sys.argv) > 2 else None
    composer = os.environ.get("OM_COMPOSER")
    for spec in cfg["outputs"]:
        if only and spec["name"] != only:
            continue
        if spec.get("engine") in ("whiteboard", "doc", "story3d"):
            await render_whiteboard(ep, spec, cfg, outdir, work, Path("whiteboard").resolve())
        elif spec.get("engine") == "remotion":
            if not composer:
                print(f"skip {spec['name']}: OM_COMPOSER not set", flush=True)
                continue
            await render_remotion(ep, spec, cfg, outdir, work, Path(composer).resolve())
        else:
            await render_output(ep, spec, cfg, outdir, work)


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1]))
