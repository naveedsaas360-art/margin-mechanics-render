# The Video Production Workflow (repeatable, zero-cost, no installs)

One pipeline that turns a topic into a finished, quality-checked 1440p documentary-style video.
Works for any channel or niche: only the research inputs and the scene file change.

```
 1 RESEARCH ─▶ 2 SCRIPT ─▶ 3 SCENE PLAN ─▶ 4 MEDIA ─▶ 5 PILOT (1 min) ─▶ 6 QA ─▶ 7 FULL VIDEO ─▶ 8 QA ─▶ 9 PACKAGE ─▶ 10 UPLOAD ─▶ 11 LEARN
     PC          Claude        Claude          PC          cloud          Claude      cloud          Claude     Claude        you         Claude
```

---

## The stack (all free)
| Job | Tool | Where it runs |
|---|---|---|
| Niche/topic research | `ChannelResearch/scrape.py`, `analyze.py` (reads public YouTube pages) | your PC (Python stdlib, nothing installed) |
| Fact research | web search: filings, CNBC, company statements | Claude |
| Voice | edge-tts (Microsoft neural) or Kokoro-82M (open source) | cloud |
| Stock video | Pixabay API (4K), free key | key stays on PC |
| Real photos | Openverse API → Wikimedia Commons / Flickr CC (commercial-use licenses) | no key |
| Music | Kevin MacLeod / incompetech (CC BY, credited) | cloud |
| Animation & graphics | Remotion (React video), our `Doc` composition | cloud |
| Rendering | GitHub Actions: prepare → 8 machines in parallel → assemble | cloud (≈2,000 free min/month) |
| QA | preview frames (1 per second for pilots) + contact sheets | Claude reviews by eye |

Files: `C:\Users\dell\YouTube\MarginMechanics\` (private repo `margin-mechanics` on GitHub).
Keys (never in the repo): `C:\Users\dell\YouTube\github_token.txt`, `pixabay_key.txt`.

---

## The steps

### 1. Research: pick a topic people want *now*
- Check demand: median views of this month's videos for each candidate topic.
  This picked "AI bubble" (782K median) over "how X makes money" (≈0, flooded by AI clones).
- Check saturation: search the exact title idea. If 5+ fresh copies get <1K views, change the angle.
- Gate: proven demand, low copy-saturation, YouTube-policy safe.

### 2. Script: story first, 10–15 minutes
- Hook in the first 15 seconds: a number plus a surprise. Promise what the viewer will learn.
- Chapters every 1–2 minutes, a re-hook every 60–90 seconds, and a "what it means for you" section with real math.
- Every number is sourced. Anything uncertain is worded "reported" or "estimated", or cut.
- Gate: every figure has a link in `upload.md`.

### 3. Scene plan: `EPxx/build.py` writes `scenes.json`
One scene = one narration paragraph + its visuals. Visuals cut on spoken **cue words** (`at="..."`).
```python
V("data center server room", move="in")                 # stock video (Pixabay)
P("Intel headquarters", at="intel", move="right")        # real photo (Openverse)
T("Follow the *money*", at="follow it")                  # kinetic headline, *highlight*
ST(700, prefix="$", suffix="B+", label="...", at="seven hundred")  # animated stat card
HL("CNBC · Oct 29, 2026", "Headline text", at="intel")   # news card (recreated text, source named)
LOW("Microsoft", at="microsoft", until_at="alphabet")    # lower-third label
CH([...bars...], title="...", at="alphabet alone")       # animated chart
```
Rules: a new shot every 3–4 s; text always above footage; one idea per screen.

### 4. Media: find and review footage
```
python -I tools/resolve_clips.py EPxx                    # Pixabay video + Openverse photos, credits recorded
powershell -File tools/clip_sheet.ps1 -Episode EPxx      # contact sheet of every shot
```
- Claude checks the sheet. Off-topic, cartoon, green-screen or wrong-mood shots get re-queried, or pinned to an exact ID (`pixabay_id=`).
- Gate: every shot matches its sentence.

### 5. Pilot: always render the first minute first
- A `PILOT_xx` folder with the first ~60 s (A/B voices if the voice isn't decided yet).
- `bash tools/cloud_render.sh PILOT_xx` pushes, renders on 8 cloud machines, and downloads to `renders\PILOT_xx_<date>\`.

### 6. Pilot QA: one frame per second, every second
```
powershell -File tools/preview_sheet.ps1 -Dir renders\...\qaA
```
- Look for: empty or black frames, overlapping or clipped text, literal markup, wrong-mood footage, late or early graphics, transition glitches.
- Fix the engine (once, for all future videos) or the scene file, then re-render. Repeat until clean.
- **You approve the pilot.** Nothing longer is built before that.

### 7. Full video: same engine, whole script
`bash tools/cloud_render.sh EPxx` takes about 25–35 min for a 10–15 min video.

### 8. Full QA: 36 evenly spaced frames plus spot checks at every chapter start
- Same checklist as the pilot.

### 9. Package
- **Thumbnail:** a real photo plus a bold 2–4 word hook and a number.
- **`upload.md`:** title, 2 backup titles, description with real chapter times, every source, footage and photo credits, music credit, tags, pinned comment.
- **Captions file (`.srt`)** for upload.

### 10. Upload (you, about 3 minutes)
- Drag the MP4, paste from `upload.md`, add the thumbnail and `.srt`.
- Tick "altered or synthetic content".
- Publish at the suggested time.

### 11. Learn: weekly
- Export YouTube Studio analytics and give them to Claude.
- Claude adjusts topics, hooks, titles, thumbnails and pacing based on click-through and retention drop-off points.

---

## Using it anywhere (new episode or new channel)
1. Copy `PILOT_DOC/build.py` into a new folder, e.g. `EP03_Topic/build.py`.
2. Replace the scenes (text + visuals), music and voice.
3. Run steps 4 → 10.

For a new channel: copy the whole repo, change the brand colors and fonts in `whiteboard/src/Doc.jsx`, and run the research in step 1 for the new niche.

## Quality gates (non-negotiable)
- Licensed media only: Pixabay, Openverse (CC0 / CC BY / CC BY-SA), public domain. **Never** Google Images or YouTube clips (copyright strikes).
- Pilot first, approved by you.
- Every second of the pilot checked; nothing ships with a known flaw.
- Every fact sourced; disclose AI narration.
