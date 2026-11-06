"""'The AI Money Loop, Explained in 6 Minutes': FIRST MINUTE, illustrated storybook documentary.

Images: FLUX illustrations from tools/gen_images.py ({char} = our own recurring character).
Style: warm hand-drawn ink + watercolor (storybook documentary). Every shot <= ~4 s, always moving.
"""
import json
from pathlib import Path

AI = lambda prompt, at=None, seed=11, **k: {"type": "shot", "ai": prompt, "seed": seed, "base": 1.04, "dim": 0.12,
                                            **({"at": at} if at else {}), **k}
FX = lambda kind, **k: {"type": "fx", "kind": kind, **k}
SLAM = lambda text, **k: {"type": "slam", "text": text, **k}
T = lambda text, x=960, y=540, size=96, **k: {"type": "title", "text": text, "x": x, "y": y, "size": size, **k}
CAP = lambda text, x=960, y=760, **k: {"type": "caption", "text": text, "x": x, "y": y, **k}
ST = lambda value, x=960, y=540, **k: {"type": "stat", "value": value, "x": x, "y": y, **k}
LOW = lambda text, **k: {"type": "lower", "text": text, **k}

SCENES = [
 dict(text="One trillion dollars. Gone, in just a few days. In the next six minutes, you'll see where that money went, why some of it was moving in a circle, and the one warning sign that shows if your own savings are exposed.",
      elements=[AI("{char} sitting at a desk staring in shock at a computer monitor showing a red line chart that plunges steeply downward to the bottom right, papers flying around, dramatic", seed=27, move="out"),
                FX("dust", n=30, flicker=True),
                SLAM("$1 TRILLION", color="red", size=230, until_at="gone"),
                SLAM("GONE.", color="red", size=260, at="gone", until_at="next six"),
                AI("a busy stock exchange trading floor with many small round-headed traders panicking, big boards on the wall with red down arrows, {char} standing in the middle looking up", at="next six", seed=21),
                T("In the next *6 minutes*", y=180, size=96, at="next six"),
                AI("green dollar bills flying in a big circular loop through the sky above a city of tall office buildings, curved arrows showing the circle", at="circle", seed=23, move="left"),
                AI("{char} at a kitchen table in the evening worriedly looking at a glass savings jar full of coins and a phone showing a red chart", at="warning sign", seed=24, move="in"),
                CAP("① Where the money went", y=700, size=54, at="where that"),
                CAP("② Why it moved in a circle", y=790, size=54, at="circle"),
                CAP("③ The warning sign for your savings", y=880, size=54, at="warning sign")]),
 dict(text="Late October. Intel falls almost thirty percent, in a single day. Its worst day in decades.",
      elements=[AI("a large plain modern glass office building with no signs on a grey rainy day, {char} standing outside under an umbrella holding a phone", seed=36),
                LOW("Late October 2026", sub="AI chip stocks", x=110, y=150),
                ST(28.6, prefix="-", suffix="%", decimals=1, label="Intel, in one day", color="red", y=780, w=760, size=140, at="thirty percent"),
                AI("close-up of {char} with a shocked face and wide eyes holding a phone whose screen shows a big red arrow pointing straight down", at="worst day", seed=38, move="in"),
                CAP("its worst day in decades", y=920, size=52, at="worst day")]),
 dict(text="To understand why, we have to follow the money. Starting with one dollar.",
      elements=[AI("a single green dollar bill lying on a wooden detective desk under a desk lamp, with a magnifying glass, notebook and pencil beside it", seed=41),
                FX("dust"), T("Follow the *money*", y=200, size=110, at="follow"),
                AI("{char} holding up a green dollar bill and studying it closely through a big magnifying glass, curious expression", at="starting", seed=42, move="out")]),
 dict(text="This year, Microsoft, Alphabet, Amazon and Meta plan to spend more than seven hundred billion dollars, mostly on data centers.",
      elements=[AI("four giant glass office towers of big technology companies side by side in a city, with streams of dollar bills pouring out of their windows", seed=51),
                CAP("Microsoft · Alphabet · Amazon · Meta", y=200, size=56, at="microsoft"),
                AI("a huge data center construction site with cranes, trucks and many tiny workers, enormous grey warehouse buildings rising", at="seven hundred", seed=52, move="right"),
                ST(700, prefix="$", suffix="B+", label="Big Tech spending, 2026", y=470, at="seven hundred"),
                AI("{char} wearing a yellow hard hat looking up in awe at a gigantic data center building under construction", at="data centers", seed=53, move="in"),
                FX("dust", n=40)]),
 dict(text="Inside those buildings: endless rows of computers, all running on one kind of chip.",
      elements=[AI("inside a data center, endless rows of tall server racks with small green and blue lights stretching into the distance, one-point perspective", seed=61),
                FX("dust", n=50),
                AI("{char} walking down a long aisle between tall server racks with blinking lights, looking around amazed", at="one kind", seed=62, move="in")]),
 dict(text="And most of those chips come from one company: Nvidia.",
      elements=[AI("a giant green computer chip displayed on a museum pedestal with spotlights, small round-headed visitors gathered around it in admiration", seed=71),
                FX("dust", n=40), T("One company: *Nvidia*", y=880, size=100, at="one company")]),
 dict(text="But here's the twist. Nvidia takes some of that money, and sends it right back out.",
      elements=[AI("a giant green computer chip shooting a fountain of dollar bills up into the sky like fireworks", seed=81),
                SLAM("THE TWIST", color="red", size=240, until_at="nvidia takes"),
                AI("{char} with wide surprised eyes and open mouth as dollar bills fly past him in the wind", at="sends it", seed=82, move="in"),
                T("…it sends the money *back out*", y=880, size=84, hl="red", at="sends it")]),
 dict(text="To the very companies that buy its chips.",
      elements=[AI("a river of dollar bills flowing in a big circle from a giant computer chip into a data center building and back again, curved arrows showing the loop", seed=91),
                T("…to the companies that *buy its chips*", y=860, size=84, at="very companies")]),
]

TICKER = ["INTEL −28.6% IN ONE DAY (OCT 30)", "CHIP STOCKS ≈ −$1 TRILLION IN DAYS (EST.)", "BIG TECH AI SPENDING 2026: $700B+",
          "OPENAI COMPUTE COMMITMENTS ≈ $1.4 TRILLION", "NVIDIA EARNINGS: NOV 17"]
MUSIC = {"url": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Investigations.mp3", "volume": 0.08,
         "credit": '"Investigations" Kevin MacLeod (incompetech.com), licensed under Creative Commons: By Attribution 4.0'}
ep = Path(__file__).parent
out = ep / "scenes.json"
prev = json.loads(out.read_text(encoding="utf-8")) if out.exists() else None
cfg = {"voice": "en-US-AndrewNeural", "rate": "+2%", "music": MUSIC, "countdown": 360, "ticker": TICKER,
       "outputs": [{"name": "AI_Money_Loop_6min_ILLUSTRATED_FIRST_MINUTE", "format": "long", "engine": "doc", "scenes": SCENES}]}
if prev:  # keep images already generated for unchanged prompts
    known = {(e.get("ai"), e.get("seed")): e for o in prev["outputs"] for s in o["scenes"] for e in s["elements"] if e.get("local")}
    for s in SCENES:
        for e in s["elements"]:
            k = known.get((e.get("ai"), e.get("seed")))
            if k and (ep.parent / k["local"]).exists():
                e.update(type="shot", kind="image", local=k["local"], credit=k["credit"])
out.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(len(SCENES), "scenes,", sum(len(s["text"].split()) for s in SCENES), "words,",
      sum(1 for s in SCENES for e in s["elements"] if e.get("ai")), "illustrations")
