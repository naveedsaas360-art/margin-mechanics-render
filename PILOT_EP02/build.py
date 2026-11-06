"""1-minute pilot of EP02 (first minute, redesigned). Two outputs: A = edge voice, B = Kokoro voice."""
import json
from pathlib import Path

W = lambda text, x, y, size=72, **k: {"type": "write", "text": text, "x": x, "y": y, "size": size, **k}
M = lambda text, x, y, size=100, **k: W(text, x, y, size, font="marker", **k)
I = lambda name, x, y, size=240, **k: {"type": "icon", "name": name, "x": x, "y": y, "size": size, **k}
C = lambda value, x, y, size=180, **k: {"type": "count", "value": value, "x": x, "y": y, "size": size, **k}
A = lambda f, t, **k: {"type": "arrow", "from": f, "to": t, **k}
O = lambda x, y, w, h, **k: {"type": "circle", "x": x, "y": y, "w": w, "h": h, **k}
UL = lambda x, y, w, **k: {"type": "underline", "x": x, "y": y, "w": w, **k}
BOX = lambda x, y, w, h, **k: {"type": "box", "x": x, "y": y, "w": w, "h": h, **k}
BARS = lambda x, y, w, h, data, **k: {"type": "bars", "x": x, "y": y, "w": w, "h": h, "data": data, **k}
FULL = lambda q, **k: {"type": "clip", "q": q, "full": True, "dim": 0.55, **k}
PEEP = lambda body, face, x, y, size=560, **k: {"type": "peep", "body": body, "face": face, "x": x, "y": y, "size": size, **k}
react = lambda at, face=None, body=None: {k: v for k, v in (("at", at), ("face", face), ("body", body)) if v}

SCENES = [
 dict(chapter="The trillion-dollar week",
      text="In just a few days at the end of October, chip stocks lost roughly a trillion dollars in value. Intel fell almost thirty percent in a single day, its worst day in decades.",
      elements=[FULL("stock market sell-off red", pixabay_id=338956),
                M("LATE OCTOBER 2026", 330, 110, 64, color="yellow", w=560),
                PEEP("Computer", "Calm", 1590, 790, 540, head="ShortOne", reacts=[react("lost", "Fear"), react("worst day", "Awe")]),
                C(1, 820, 300, 220, prefix="-$", suffix=" TRILLION", color="red", w=1300, at="lost"),
                W("chip stocks, late October (estimates)", 820, 470, 64, color="white", w=1200),
                M("INTEL: -28.6% IN ONE DAY", 760, 720, 92, color="yellow", w=1250, at="intel"),
                UL(260, 800, 1000, color="yellow", at="worst day")]),
 dict(text="But the strange part isn't the crash. It's where a lot of that money came from in the first place. Because when you follow it, some of it goes around in a circle.",
      elements=[PEEP("PointingUp", "Suspicious", 330, 640, 640, head="Pomp", reacts=[react("follow it", "Driven"), react("circle", "Awe")]),
                M("FOLLOW THE MONEY", 1150, 110, 100, color="blue"),
                I("coin", 1150, 330, 170, color="green", at="came from"),
                A([1260, 380], [1400, 600], bend=-40, color="green"),
                I("coin", 1440, 700, 170, color="green"),
                A([1350, 770], [980, 770], bend=-40, color="green"),
                I("coin", 860, 700, 170, color="green"),
                A([900, 600], [1040, 380], bend=-40, color="green", at="goes around"),
                O(1150, 560, 900, 620, color="red", at="circle"),
                W("the same dollars, around and around", 1150, 960, 70, color="red", w=1300)]),
 dict(text="By the end of this video, you'll understand the loop, why it made the AI boom look even bigger than it was, and the three signals that tell you whether this ends in a soft landing or a real bust.",
      elements=[PEEP("Explaining", "Explaining", 1590, 640, 640, head="MediumStraight",
                     reacts=[react("real bust", "Concerned")]),
                M("IN THIS VIDEO", 640, 110, 92, color="blue"),
                I("arrows-exchange", 190, 300, 150, color="blue", at="the loop"),
                W("how the money loop works", 720, 300, 92, w=880, at="the loop"),
                I("trending-up", 190, 480, 150, color="green", at="bigger"),
                W("why the boom looked bigger", 720, 480, 92, w=880),
                I("eye", 190, 660, 150, color="red", at="three signals"),
                W("3 signals to watch", 720, 660, 92, w=880),
                W("soft landing?", 430, 880, 84, color="green", w=600, at="soft landing"),
                W("or real bust?", 980, 880, 84, color="red", w=600, at="real bust")]),
 dict(chapter="The biggest building spree in history",
      text="Start with the spending. Microsoft, Alphabet, Amazon and Meta are on track to spend more than seven hundred billion dollars this year, mostly on data centers and the chips inside them.",
      elements=[FULL("data center server room"),
                M("BIG TECH SPENDING, 2026", 960, 140, 88, color="white"),
                W("Microsoft  ·  Alphabet  ·  Amazon  ·  Meta", 960, 300, 76, color="white", at="microsoft"),
                C(700, 960, 520, 240, prefix="$", suffix="B+", color="yellow", at="seven hundred"),
                W("mostly data centers + the chips inside", 960, 780, 76, color="white", at="data centers"),
                UL(470, 850, 980, color="yellow", at="chips inside")]),
 dict(text="Alphabet alone guided to around two hundred billion. Meta, up to one hundred forty-five. Microsoft, about one hundred seventy. And next year, the total is expected to top one trillion dollars.",
      elements=[PEEP("Paper", "Calm", 1630, 700, 560, head="Bun", reacts=[react("next year", "Awe"), react("one trillion", "Fear")]),
                W("2026 spending plans ($ billions)", 700, 100, 70, w=1200),
                BARS(120, 900, 1150, 560, [
                    {"label": "Alphabet", "value": 200, "valueLabel": "~$200B", "color": "blue"},
                    {"label": "Meta", "value": 145, "valueLabel": "up to $145B", "color": "orange"},
                    {"label": "Microsoft", "value": 170, "valueLabel": "~$170B", "color": "green"}],
                    at="alphabet alone", dur=5.5, labelSize=62, valueSize=72),
                M("NEXT YEAR:\n$1 TRILLION+", 1600, 230, 80, color="red", w=560, at="next year"),
                BOX(1300, 120, 600, 230, color="red")]),
]

MUSIC = {"url": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Investigations.mp3", "volume": 0.07,
         "credit": '"Investigations" Kevin MacLeod (incompetech.com), licensed under Creative Commons: By Attribution 4.0'}
ep = Path(__file__).parent
out = ep / "scenes.json"
prev = json.loads(out.read_text(encoding="utf-8")) if out.exists() else None
cfg = {"voice": "en-US-AndrewNeural", "rate": "-2%", "music": MUSIC, "outputs": [
    {"name": "PILOT_A_voice_andrew", "format": "long", "engine": "whiteboard", "scenes": SCENES},
    {"name": "PILOT_B_voice_kokoro", "format": "long", "engine": "whiteboard", "tts": "kokoro", "voice": "am_michael",
     "scenes": json.loads(json.dumps(SCENES))}]}
if prev:  # keep clip URLs already resolved for the same queries
    urls = {e["q"]: e for o in prev["outputs"] for s in o["scenes"] for e in s["elements"] if e.get("url")}
    for o in cfg["outputs"]:
        for s in o["scenes"]:
            for e in s["elements"]:
                if e.get("q") in urls:
                    e.update({k: urls[e["q"]][k] for k in ("url", "clipSeconds", "credit", "thumb") if k in urls[e["q"]]})
out.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(len(SCENES), "scenes,", sum(len(s["text"].split()) for s in SCENES), "words")
