"""'The AI Money Loop, Explained in 6 Minutes': FIRST MINUTE in 3D-illustration storytelling (Story3D)."""
import json
from pathlib import Path

SET = lambda name, **k: {"type": "set3d", "set": name, **k}
T = lambda text, x=960, y=540, size=96, **k: {"type": "title", "text": text, "x": x, "y": y, "size": size, **k}
CAP = lambda text, x=960, y=760, **k: {"type": "caption", "text": text, "x": x, "y": y, **k}
ST = lambda value, x=960, y=540, **k: {"type": "stat", "value": value, "x": x, "y": y, **k}
LOW = lambda text, **k: {"type": "lower", "text": text, **k}
BUB = lambda text, x, y, **k: {"type": "bubble", "text": text, "x": x, "y": y, **k}

SCENES = [
 dict(text="Meet Maya.", elements=[SET("room"), LOW("Maya", sub="an ordinary investor", x=110, y=840)]),
 dict(text="Maya has never bought a single tech stock. But like millions of people, her retirement money sits in an index fund.",
      elements=[SET("piggy", reveal_at=["index fund"]),
                BUB("Tech stocks? Not me.", 620, 300, at="never bought", until_at="retirement", w=720, size=64),
                T("…but her index fund is full of *tech*", y=880, size=72, w=1500, at="index fund")]),
 dict(text="In the last week of October, she opens her app, and sees red.",
      elements=[SET("phone", reveal_at=["opens her app", "sees red"])]),
 dict(text="Chip stocks lost roughly a trillion dollars in just a few days. Intel fell almost thirty percent, in a single day.",
      elements=[SET("crash", reveal_at=["chip stocks"]),
                ST(1, prefix="-$", suffix=" TRILLION", label="chip stocks, in days (estimates)", color="red", y=250, at="trillion", until_at="intel"),
                ST(28.6, prefix="-", suffix="%", decimals=1, label="Intel, in one day", color="red", y=250, w=820, at="thirty percent")]),
 dict(text="So Maya asks the question nobody on TV answers. Where did all that money come from in the first place?",
      elements=[SET("question"), BUB("Where did all that money COME FROM?", 640, 280, thought=True, at="where did", w=900, size=64)]),
 dict(text="To find out, we'll follow one dollar.",
      elements=[SET("dollar"), T("Follow *one dollar*", y=200, size=110, at="follow")]),
 dict(text="Our dollar starts at Big Tech. This year, Microsoft, Alphabet, Amazon and Meta plan to spend more than seven hundred billion dollars.",
      elements=[SET("city", reveal_at=["microsoft", "alphabet", "amazon", "meta plan", "seven hundred"]),
                T("It starts at *Big Tech*", y=150, size=84, until_at="microsoft"),
                LOW("Microsoft", x=110, y=840, at="microsoft", until_at="alphabet"),
                LOW("Alphabet", x=110, y=840, at="alphabet", until_at="amazon"),
                LOW("Amazon", x=110, y=840, at="amazon", until_at="meta plan"),
                LOW("Meta", x=110, y=840, at="meta plan", until_at="seven hundred"),
                ST(700, prefix="$", suffix="B+", label="Big Tech spending, 2026", y=210, at="seven hundred")]),
 dict(text="Most of it goes to data centers, and the chips inside them.",
      elements=[SET("datacenter", reveal_at=["data centers"]),
                CAP("data centers… and the chips inside them", y=900, size=56, at="data centers")]),
 dict(text="So our dollar lands at the company that makes those chips: Nvidia.",
      elements=[SET("nvidia", reveal_at=["lands"]), LOW("Nvidia", sub="makes the chips most AI runs on", x=110, y=150, at="nvidia")]),
 dict(text="And that's where the story gets strange. Because Nvidia sends part of that dollar right back out.",
      elements=[SET("boomerang", reveal_at=["sends", "strange"]),
                T("Wait… it goes *back out*?", x=760, y=880, size=80, w=1250, hl="red", at="right back")]),
]

TICKER = ["INTEL −28.6% IN ONE DAY (OCT 30)", "CHIP STOCKS ≈ −$1 TRILLION IN DAYS (EST.)", "BIG TECH AI SPENDING 2026: $700B+",
          "OPENAI COMPUTE COMMITMENTS ≈ $1.4 TRILLION", "NVIDIA EARNINGS: NOV 17"]
MUSIC = {"url": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Investigations.mp3", "volume": 0.07,
         "credit": '"Investigations" Kevin MacLeod (incompetech.com), licensed under Creative Commons: By Attribution 4.0'}
cfg = {"voice": "en-US-AndrewNeural", "rate": "+2%", "music": MUSIC, "countdown": 360, "ticker": TICKER,
       "outputs": [{"name": "AI_Money_Loop_6min_3D_FIRST_MINUTE", "format": "long", "engine": "story3d", "scenes": SCENES}]}
ep = Path(__file__).parent
(ep / "scenes.json").write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(len(SCENES), "scenes,", sum(len(s["text"].split()) for s in SCENES), "words")
