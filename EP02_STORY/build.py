"""'The AI Money Loop, Explained in 6 Minutes': FIRST MINUTE, animated storytelling version.

Story device: Maya (an ordinary investor) and a living dollar bill we follow through the loop.
Same verified facts as EP02; every screen changes within 3–5 s and always has motion.
"""
import json
from pathlib import Path

BG = lambda a, b, **k: {"type": "bg", "colors": [a, b], **k}
PEEP = lambda body, face, x, y, size=640, **k: {"type": "peep", "body": body, "face": face, "x": x, "y": y, "size": size, **k}
REACT = lambda at, face=None, body=None: {k: v for k, v in (("at", at), ("face", face), ("body", body)) if v}
T = lambda text, x=960, y=540, size=96, **k: {"type": "title", "text": text, "x": x, "y": y, "size": size, **k}
CAP = lambda text, x=960, y=760, **k: {"type": "caption", "text": text, "x": x, "y": y, **k}
ST = lambda value, x=960, y=540, **k: {"type": "stat", "value": value, "x": x, "y": y, **k}
LOW = lambda text, **k: {"type": "lower", "text": text, **k}
BUB = lambda text, x, y, **k: {"type": "bubble", "text": text, "x": x, "y": y, **k}
IC = lambda name, x, y, size=240, **k: {"type": "icon", "name": name, "x": x, "y": y, "size": size, **k}
DOL = lambda **k: {"type": "dollar", **k}
PHONE = lambda x, y, **k: {"type": "phone", "x": x, "y": y, **k}
CRASH = lambda **k: {"type": "crash", **k}
MAYA = dict(head="LongHair")

SCENES = [
 dict(text="Meet Maya.",
      elements=[BG("#2a4b8d", "#0d1530"), PEEP("Coffee", "Smile", 960, 560, 760, **MAYA),
                LOW("Maya", sub="an ordinary investor", x=110, y=820)]),
 dict(text="Maya has never bought a single tech stock. But like millions of people, her retirement money sits in an index fund.",
      elements=[BG("#3b2a6b", "#120b26"), PEEP("Explaining", "Calm", 520, 600, 700, reacts=[REACT("index fund", "Smile")], **MAYA),
                BUB("Tech stocks? Not me.", 1240, 330, at="never bought", until_at="retirement", w=720, size=64),
                IC("pig-money", 1300, 470, 300, color="yellow", at="retirement"),
                T("…but her index fund is full of *tech*", x=1250, y=800, size=64, w=1100, at="index fund")]),
 dict(text="In the last week of October, she opens her app, and sees red.",
      elements=[BG("#1e2a3a", "#0a0f16"), PEEP("Computer", "Calm", 560, 610, 700, reacts=[REACT("sees red", "Fear")], **MAYA),
                PHONE(1340, 560, at="opens her app", crash=2.6, ticker="CHIP STOCKS")]),
 dict(text="Chip stocks lost roughly a trillion dollars in just a few days. Intel fell almost thirty percent, in a single day.",
      elements=[BG("#4a0f12", "#140405"), CRASH(x=330, y=980),
                ST(1, prefix="-$", suffix=" TRILLION", label="chip stocks, in days (estimates)", color="red", y=330, at="trillion", until_at="intel"),
                ST(28.6, prefix="-", suffix="%", decimals=1, label="Intel, in one day", color="red", y=330, w=820, at="thirty percent"),
                PEEP("Paper", "Fear", 1620, 640, 520, at="intel", **MAYA)]),
 dict(text="So Maya asks the question nobody on TV answers. Where did all that money come from in the first place?",
      elements=[BG("#33204f", "#0f0918"), PEEP("PointingUp", "Suspicious", 520, 600, 720, **MAYA),
                IC("device-tv", 1350, 640, 260, color="white", at="nobody on tv", until_at="where did"),
                BUB("Where did all that money COME FROM?", 1280, 360, thought=True, at="where did", w=900, size=64)]),
 dict(text="To find out, we'll follow one dollar.",
      elements=[BG("#0f3d2a", "#05140d"), T("Follow *one dollar*", y=230, size=110, at="follow"),
                DOL(from_=None, **{"from": [960, 620]}, size=1.8, at="one dollar")]),
 dict(text="Our dollar starts at Big Tech. This year, Microsoft, Alphabet, Amazon and Meta plan to spend more than seven hundred billion dollars.",
      elements=[BG("#1c2f5e", "#0a1124"), T("It starts at *Big Tech*", y=150, size=84, until_at="seven hundred"),
                IC("building-skyscraper", 330, 540, 230, label="Microsoft", at="microsoft"),
                IC("building-skyscraper", 730, 540, 230, label="Alphabet", at="alphabet"),
                IC("building-skyscraper", 1130, 540, 230, label="Amazon", at="amazon"),
                IC("building-skyscraper", 1530, 540, 230, label="Meta", at="meta plan"),
                DOL(**{"from": [330, 820], "to": [930, 820]}, travel=2.2, hop=60, at="microsoft"),
                ST(700, prefix="$", suffix="B+", label="Big Tech spending, 2026", y=250, at="seven hundred"),
                DOL(**{"from": [960, 820]}, copies=9, size=0.8, at="seven hundred")]),
 dict(text="Most of it goes to data centers, and the chips inside them.",
      elements=[BG("#0e3b47", "#04141a"),
                IC("server", 960, 480, 280, color="white", label="data centers", at="data centers"),
                DOL(**{"from": [250, 720], "to": [880, 720]}, travel=1.0, at="data centers"),
                IC("cpu", 1560, 480, 260, color="green", label="chips", at="chips"),
                DOL(**{"from": [960, 720], "to": [1520, 720]}, travel=0.9, at="chips")]),
 dict(text="So our dollar lands at the company that makes those chips: Nvidia.",
      elements=[BG("#103b1c", "#051408"), IC("cpu", 960, 460, 400, color="green", label="NVIDIA", at="company"),
                DOL(**{"from": [260, 760], "to": [960, 760]}, travel=1.2, hop=220, at="lands"),
                LOW("Nvidia", sub="makes the chips most AI runs on", x=110, y=150, at="nvidia")]),
 dict(text="And that's where the story gets strange. Because Nvidia sends part of that dollar right back out.",
      elements=[BG("#3a1450", "#100516"), IC("cpu", 640, 470, 320, color="green", label="NVIDIA"),
                DOL(**{"from": [680, 720], "to": [1420, 360]}, travel=1.0, hop=260, at="sends"),
                PEEP("Explaining", "Awe", 1600, 680, 520, at="strange", **MAYA),
                T("Wait… it goes *back out*?", x=760, y=880, size=80, w=1250, hl="red", at="right back")]),
]
for s in SCENES:  # tidy helper artefacts
    for e in s["elements"]:
        e.pop("from_", None)

TICKER = ["INTEL −28.6% IN ONE DAY (OCT 30)", "CHIP STOCKS ≈ −$1 TRILLION IN DAYS (EST.)", "BIG TECH AI SPENDING 2026: $700B+",
          "OPENAI COMPUTE COMMITMENTS ≈ $1.4 TRILLION", "NVIDIA EARNINGS: NOV 17"]
MUSIC = {"url": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Investigations.mp3", "volume": 0.07,
         "credit": '"Investigations" Kevin MacLeod (incompetech.com), licensed under Creative Commons: By Attribution 4.0'}
cfg = {"voice": "en-US-AndrewNeural", "rate": "+2%", "music": MUSIC, "countdown": 360, "ticker": TICKER,
       "outputs": [{"name": "AI_Money_Loop_6min_STORY_FIRST_MINUTE", "format": "long", "engine": "doc", "scenes": SCENES}]}
ep = Path(__file__).parent
(ep / "scenes.json").write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(len(SCENES), "scenes,", sum(len(s["text"].split()) for s in SCENES), "words")
