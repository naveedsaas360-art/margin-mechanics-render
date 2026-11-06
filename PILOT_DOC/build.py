"""1-minute pilot, documentary hybrid style (real footage + photos + motion graphics).

Shots: video from Pixabay (q / pixabay_id) or real photos via Openverse (img). A = edge voice, B = Kokoro.
"""
import json
from pathlib import Path

V = lambda q, at=None, **k: {"type": "shot", "q": q, **({"at": at} if at else {}), **k}        # stock video
P = lambda img, at=None, **k: {"type": "shot", "img": img, **({"at": at} if at else {}), **k}  # real photo
T = lambda text, x=960, y=540, size=96, **k: {"type": "title", "text": text, "x": x, "y": y, "size": size, **k}
CAP = lambda text, x=960, y=540, **k: {"type": "caption", "text": text, "x": x, "y": y, **k}
ST = lambda value, x=960, y=540, **k: {"type": "stat", "value": value, "x": x, "y": y, **k}
HL = lambda source, text, x=960, y=540, **k: {"type": "headline", "source": source, "text": text, "x": x, "y": y, **k}
LOW = lambda text, **k: {"type": "lower", "text": text, **k}
CH = lambda data, **k: {"type": "chart", "data": data, **k}

SCENES = [
 dict(chapter="The trillion-dollar week",
      text="In just a few days at the end of October, chip stocks lost roughly a trillion dollars in value. Intel fell almost thirty percent in a single day, its worst day in decades.",
      elements=[V("stock market sell-off red", pixabay_id=338956, move="in"),
                LOW("Late October 2026", sub="AI chip stocks", x=110, y=110),
                P("New York Stock Exchange", at="chip stocks", move="left", dim=0.35),
                ST(1, prefix="-$", suffix=" TRILLION", label="chip stocks, in days (estimates)", color="red",
                   y=560, at="lost", until_at="intel"),
                P("Intel headquarters", at="intel", move="right", dim=0.3),
                HL("CNBC · Oct 29, 2026", "Intel stock plunges as chipmaker issues weak forecast", y=430, at="intel", w=1150),
                ST(28.6, prefix="-", suffix="%", decimals=1, label="Intel, in one day: worst in decades", color="red",
                   y=820, w=900, size=150, at="single day")]),
 dict(text="But the strange part isn't the crash. It's where a lot of that money came from in the first place. Because when you follow it, some of it goes around in a circle.",
      elements=[V("money counting dollar bills", move="in", dim=0.3),
                T("The strange part isn't the *crash*", y=520, size=92, at="strange", until_at="came from"),
                V("cash flow bank transfer money", at="came from", move="left", dim=0.4),
                T("Follow the *money*", y=500, size=120, at="follow it"),
                CAP("some of it goes around in a circle", y=650, size=48, at="goes around")]),
 dict(text="By the end of this video, you'll understand the loop, why it made the AI boom look even bigger than it was, and the three signals that tell you whether this ends in a soft landing or a real bust.",
      elements=[V("artificial intelligence robot hand", move="in", dim=0.45),
                T("In this video", x=960, y=200, size=64, until_at="soft landing"),
                T("1  How the *money loop* works", x=900, y=400, size=64, w=1500, align="left", at="the loop", until_at="soft landing"),
                P("data center", at="bigger", move="right", dim=0.55),
                T("2  Why the boom looked *bigger*", x=900, y=540, size=64, w=1500, align="left", at="bigger", until_at="soft landing"),
                T("3  Three signals to *watch*", x=900, y=680, size=64, w=1500, align="left", at="three signals", until_at="soft landing"),
                V("airplane landing", at="soft landing", pick=1, move="in", dim=0.55),
                T("Soft landing, or real *bust*?", y=540, size=96, hl="red", at="soft landing")]),
 dict(chapter="The biggest building spree in history",
      text="Start with the spending. Microsoft, Alphabet, Amazon and Meta are on track to spend more than seven hundred billion dollars this year, mostly on data centers and the chips inside them.",
      elements=[V("data center server room", move="in", dim=0.35),
                T("Start with the *spending*", y=520, size=100, at="start with", until_at="microsoft"),
                P("Microsoft headquarters Redmond", at="microsoft", move="left", dim=0.3),
                LOW("Microsoft", x=110, y=880, at="microsoft", until_at="alphabet"),
                P("Googleplex", at="alphabet", move="right", dim=0.3),
                LOW("Alphabet", x=110, y=880, at="alphabet", until_at="amazon"),
                P("Amazon Spheres Seattle", at="amazon", move="left", dim=0.3),
                LOW("Amazon", x=110, y=880, at="amazon", until_at="meta are"),
                P("Meta headquarters Menlo Park", at="meta are", move="right", dim=0.3),
                LOW("Meta", x=110, y=880, at="meta are", until_at="seven hundred"),
                V("server racks data center lights", at="seven hundred", move="in", dim=0.4),
                ST(700, prefix="$", suffix="B+", label="Big Tech spending, 2026", color="yellow", y=500, at="seven hundred"),
                V("computer chip macro", at="chips inside", move="in", dim=0.45),
                CAP("mostly data centers, and the chips inside them", y=760, size=46, at="data centers")]),
 dict(text="Alphabet alone guided to around two hundred billion. Meta, up to one hundred forty-five. Microsoft, about one hundred seventy. And next year, the total is expected to top one trillion dollars.",
      elements=[V("construction site crane timelapse", move="in", dim=0.5),
                CH([{"label": "Alphabet", "value": 200, "valueLabel": "~$200B", "color": "blue"},
                    {"label": "Meta", "value": 145, "valueLabel": "≤ $145B", "color": "yellow"},
                    {"label": "Microsoft", "value": 170, "valueLabel": "~$170B", "color": "green"}],
                   title="2026 spending plans", x=960, y=540, w=1300, h=640, dur=5.5, at="alphabet alone", until_at="next year"),
                V("city skyline night timelapse", at="next year", move="in", dim=0.45),
                ST(1, prefix="$", suffix=" TRILLION+", label="expected next year", color="yellow", y=520, at="next year"),
                CAP("Sources: company earnings guidance, CNBC", y=1010, size=26, opacity=0.7, at="next year")]),
]

MUSIC = {"url": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Investigations.mp3", "volume": 0.07,
         "credit": '"Investigations" Kevin MacLeod (incompetech.com), licensed under Creative Commons: By Attribution 4.0'}
ep = Path(__file__).parent
out = ep / "scenes.json"
prev = json.loads(out.read_text(encoding="utf-8")) if out.exists() else None
cfg = {"voice": "en-US-AndrewNeural", "rate": "-2%", "music": MUSIC, "outputs": [
    {"name": "DOC_A_voice_andrew", "format": "long", "engine": "doc", "scenes": SCENES},
    {"name": "DOC_B_voice_kokoro", "format": "long", "engine": "doc", "tts": "kokoro", "voice": "am_michael",
     "scenes": json.loads(json.dumps(SCENES))}]}
if prev:  # keep media already resolved and reviewed
    keep = {(e.get("q"), e.get("img"), e.get("pick", 0)): e for o in prev["outputs"] for s in o["scenes"]
            for e in s["elements"] if e.get("url")}
    for o in cfg["outputs"]:
        for s in o["scenes"]:
            for e in s["elements"]:
                k = keep.get((e.get("q"), e.get("img"), e.get("pick", 0)))
                if k:
                    e.update({f: k[f] for f in ("url", "clipSeconds", "credit", "thumb", "kind") if f in k})
out.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(len(SCENES), "scenes,", sum(len(s["text"].split()) for s in SCENES), "words,",
      sum(1 for s in SCENES for e in s["elements"] if e["type"] == "shot"), "shots")
