"""'The AI Money Loop, Explained in 6 Minutes': FIRST MINUTE ONLY (for review).

Reuses media already resolved and reviewed in EP02_DOC. Every shot <= ~4 s; graphics always moving.
"""
import json
from pathlib import Path

V = lambda q, at=None, **k: {"type": "shot", "q": q, **({"at": at} if at else {}), **k}
P = lambda img, at=None, **k: {"type": "shot", "img": img, **({"at": at} if at else {}), **k}
PANEL = lambda **k: {"type": "panel", **k}
T = lambda text, x=960, y=540, size=96, **k: {"type": "title", "text": text, "x": x, "y": y, "size": size, **k}
CAP = lambda text, x=960, y=760, **k: {"type": "caption", "text": text, "x": x, "y": y, **k}
ST = lambda value, x=960, y=540, **k: {"type": "stat", "value": value, "x": x, "y": y, **k}
HL = lambda source, text, x=960, y=500, **k: {"type": "headline", "source": source, "text": text, "x": x, "y": y, **k}
LOW = lambda text, **k: {"type": "lower", "text": text, **k}
NODES = [{"label": "CHIP MAKER", "sub": "Nvidia · AMD", "color": "blue"},
         {"label": "AI LAB", "sub": "OpenAI", "color": "green"},
         {"label": "CLOUD", "sub": "Oracle · CoreWeave", "color": "yellow"}]
LOOP = lambda **k: {"type": "loop", "nodes": NODES, "x": 960, "y": 500, "r": 290,
                    "labels": ["invests $", "rents computing", "buys chips"], **k}

SCENES = [
 dict(text="One trillion dollars. Gone, in just a few days. That's how much chip stocks lost at the end of October. And Intel fell almost thirty percent, in a single day.",
      elements=[V("stock market sell-off red", pixabay_id=338956, dim=0.45),
                {"type": "slam", "text": "$1 TRILLION", "color": "red", "size": 320, "at": "one trillion", "until_at": "gone"},
                V("stock exchange trading board", at="gone", move="in", dim=0.5),
                {"type": "slam", "text": "GONE.", "size": 360, "at": "gone", "until_at": "that's how"},
                P("New York Stock Exchange", at="that's how", move="left", dim=0.35),
                LOW("Late October 2026", sub="AI chip stocks", x=110, y=150, at="that's how"),
                ST(1, prefix="-$", suffix=" TRILLION", label="chip stocks, in days (estimates)", color="red", y=540, at="chip stocks", until_at="intel"),
                P("Intel headquarters", at="intel", move="right", dim=0.3),
                HL("CNBC · Oct 29, 2026", "Intel stock plunges as chipmaker issues weak forecast", y=400, at="intel", w=1150),
                ST(28.6, prefix="-", suffix="%", decimals=1, label="Intel, in one day", color="red", y=780, w=760, size=140, at="thirty percent")]),
 dict(text="But the real story is where that money came from. Because some of it travels in a circle.",
      elements=[V("money counting dollar bills", dim=0.3), T("The real story is *where it came from*", y=520, size=86, until_at="circle"),
                V("cash flow bank transfer money", at="travels", move="left", dim=0.4),
                T("Some of it travels in a *circle*", y=520, size=100, at="circle")]),
 dict(text="This is the AI money loop, explained in six minutes.",
      elements=[PANEL(), LOOP(reveal=[0.1, 0.5, 0.9], labels=None),
                T("The AI *money loop*", y=960, size=70, at="money loop", hl="yellow")]),
 dict(text="It starts with spending. Microsoft, Alphabet, Amazon and Meta are on track to spend more than seven hundred billion dollars this year, mostly on data centers and the chips inside them.",
      elements=[V("data center server room", dim=0.35), T("It starts with *spending*", y=520, size=100, until_at="microsoft"),
                P("Microsoft headquarters Redmond", at="microsoft", move="left", dim=0.3), LOW("Microsoft", x=110, y=860, at="microsoft", until_at="alphabet"),
                P("Googleplex", at="alphabet", move="right", dim=0.3), LOW("Alphabet", x=110, y=860, at="alphabet", until_at="amazon"),
                P("Amazon Spheres Seattle", at="amazon", move="left", dim=0.3), LOW("Amazon", x=110, y=860, at="amazon", until_at="meta are"),
                P("Meta headquarters Menlo Park", at="meta are", move="right", dim=0.3), LOW("Meta", x=110, y=860, at="meta are", until_at="seven hundred"),
                V("server racks data center lights", at="seven hundred", dim=0.4),
                ST(700, prefix="$", suffix="B+", label="Big Tech spending, 2026", y=480, at="seven hundred"),
                V("computer chip macro", at="chips inside", dim=0.45), CAP("mostly data centers, and the chips inside them", y=720, size=46, at="data centers")]),
 dict(text="And a big share of that money flows to one company: the one that makes the chips.",
      elements=[V("computer chip macro", pick=2, dim=0.4), T("A big share flows to *one company*", y=520, size=88, until_at="makes the chips"),
                P("Nvidia headquarters", at="makes the chips", move="in", dim=0.35), T("The *chip maker*", y=860, size=96, at="makes the chips")]),
 dict(text="Nvidia makes the chips most of the world's AI runs on. That's how it became one of the most valuable companies on Earth. And here's the twist: Nvidia also invests in its own customers.",
      elements=[P("Jensen Huang", pick=1, dim=0.35), LOW("Nvidia", sub="the chips most AI runs on", x=110, y=150),
                V("circuit board technology", at="most valuable", dim=0.45),
                T("One of the most *valuable* companies on Earth", y=520, size=80, at="most valuable", until_at="twist"),
                P("Nvidia headquarters", pick=1, at="twist", dim=0.45), T("The *twist*", y=420, size=120, hl="red", at="twist"),
                CAP("Nvidia also invests in its own customers", y=580, size=56, at="invests")]),
 dict(text="Let's follow the money.",
      elements=[V("money counting dollar bills", dim=0.35), T("Let's follow the *money*", y=520, size=120)]),
]

ep = Path(__file__).parent
src = json.loads((ep.parent / "EP02_DOC" / "scenes.json").read_text(encoding="utf-8"))
known = {(e.get("q"), e.get("img"), e.get("pick", 0)): e for o in src["outputs"] for s in o["scenes"]
         for e in s["elements"] if e.get("url")}
missing = []
for s in SCENES:
    for e in s["elements"]:
        if e["type"] == "shot":
            k = known.get((e.get("q"), e.get("img"), e.get("pick", 0)))
            if k:
                e.update({f: k[f] for f in ("url", "clipSeconds", "credit", "thumb", "kind", "focus") if f in k})
            else:
                missing.append(e.get("q") or e.get("img"))
TICKER = ["INTEL −28.6% IN ONE DAY (OCT 30)", "CHIP STOCKS ≈ −$1 TRILLION IN DAYS (EST.)", "BIG TECH AI SPENDING 2026: $700B+",
          "OPENAI COMPUTE COMMITMENTS ≈ $1.4 TRILLION", "NVIDIA EARNINGS: NOV 17"]
MUSIC = {"url": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Investigations.mp3", "volume": 0.07,
         "credit": '"Investigations" Kevin MacLeod (incompetech.com), licensed under Creative Commons: By Attribution 4.0'}
cfg = {"voice": "en-US-AndrewNeural", "rate": "+2%", "music": MUSIC, "countdown": 360, "ticker": TICKER,
       "outputs": [{"name": "AI_Money_Loop_6min_FIRST_MINUTE", "format": "long", "engine": "doc", "scenes": SCENES}]}
(ep / "scenes.json").write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(len(SCENES), "scenes,", sum(len(s["text"].split()) for s in SCENES), "words; unresolved:", missing)
