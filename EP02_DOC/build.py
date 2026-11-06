"""EP02 'The AI Money Loop', full video in documentary hybrid style.

Narration = the verified EP02 script (EP02_AI_Money_Loop/scenes.json), visuals redesigned scene by scene.
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
CH = lambda data, **k: {"type": "chart", "data": data, **k}
NODES = [{"label": "CHIP MAKER", "sub": "Nvidia · AMD", "color": "blue"},
         {"label": "AI LAB", "sub": "OpenAI", "color": "green"},
         {"label": "CLOUD", "sub": "Oracle · CoreWeave", "color": "yellow"}]
LOOP = lambda **k: {"type": "loop", "nodes": NODES, "x": 960, "y": 585, "r": 300,
                    "labels": ["invests $", "rents computing", "buys chips"], **k}

VIS = [
 # 0 hook
 [V("stock market sell-off red", pixabay_id=338956), LOW("Late October 2026", sub="AI chip stocks", x=110, y=110),
  P("New York Stock Exchange", at="chip stocks", move="left", dim=0.35),
  ST(1, prefix="-$", suffix=" TRILLION", label="chip stocks, in days (estimates)", color="red", y=560, at="lost", until_at="intel"),
  P("Intel headquarters", at="intel", move="right", dim=0.3),
  HL("CNBC · Oct 29, 2026", "Intel stock plunges as chipmaker issues weak forecast", y=430, at="intel", w=1150),
  ST(28.6, prefix="-", suffix="%", decimals=1, label="Intel, in one day: worst in decades", color="red", y=820, w=900, size=150, at="single day")],
 # 1
 [V("money counting dollar bills", dim=0.3), T("The strange part isn't the *crash*", y=520, size=92, at="strange", until_at="came from"),
  V("cash flow bank transfer money", at="came from", move="left", dim=0.4), T("Follow the *money*", y=500, size=120, at="follow it"),
  CAP("some of it goes around in a circle", y=650, size=48, at="goes around")],
 # 2
 [V("artificial intelligence robot hand", dim=0.45), T("In this video", y=200, size=64, until_at="soft landing"),
  T("1  How the *money loop* works", x=900, y=400, size=64, w=1500, align="left", at="the loop", until_at="soft landing"),
  V("data center aerial view", at="bigger", move="right", dim=0.55),
  T("2  Why the boom looked *bigger*", x=900, y=540, size=64, w=1500, align="left", at="bigger", until_at="soft landing"),
  T("3  Three signals to *watch*", x=900, y=680, size=64, w=1500, align="left", at="three signals", until_at="soft landing"),
  V("airplane landing", at="soft landing", pick=1, dim=0.55), T("Soft landing, or real *bust*?", y=540, size=96, hl="red", at="soft landing")],
 # 3
 [V("data center server room", dim=0.35), T("Start with the *spending*", y=520, size=100, at="start with", until_at="microsoft"),
  P("Microsoft headquarters Redmond", at="microsoft", move="left", dim=0.3), LOW("Microsoft", x=110, y=880, at="microsoft", until_at="alphabet"),
  P("Googleplex", at="alphabet", move="right", dim=0.3), LOW("Alphabet", x=110, y=880, at="alphabet", until_at="amazon"),
  P("Amazon Spheres Seattle", at="amazon", move="left", dim=0.3), LOW("Amazon", x=110, y=880, at="amazon", until_at="meta are"),
  P("Meta headquarters Menlo Park", at="meta are", move="right", dim=0.3), LOW("Meta", x=110, y=880, at="meta are", until_at="seven hundred"),
  V("server racks data center lights", at="seven hundred", dim=0.4),
  ST(700, prefix="$", suffix="B+", label="Big Tech spending, 2026", y=500, at="seven hundred"),
  V("computer chip macro", at="chips inside", dim=0.45), CAP("mostly data centers, and the chips inside them", y=760, size=46, at="data centers")],
 # 4
 [V("construction site crane timelapse", dim=0.5),
  CH([{"label": "Alphabet", "value": 200, "valueLabel": "~$200B", "color": "blue"},
      {"label": "Meta", "value": 145, "valueLabel": "≤ $145B", "color": "yellow"},
      {"label": "Microsoft", "value": 170, "valueLabel": "~$170B", "color": "green"}],
     title="2026 spending plans", w=1300, h=640, dur=5.5, at="alphabet alone", until_at="next year"),
  V("city skyline night timelapse", at="next year", dim=0.45),
  ST(1, prefix="$", suffix=" TRILLION+", label="expected next year", y=520, at="next year")],
 # 5 perspective
 [V("earth globe rotating space", dim=0.4), T("More than most *countries* produce in a year", y=500, size=84, at="countries", until_at="four companies"),
  V("aerial data center construction", at="buildings full", dim=0.45), T("Spent by *4 companies*", y=540, size=110, at="four companies")],
 # 6 inside a data center
 [V("server room data center", pick=1, dim=0.35), T("Inside an AI *data center*", y=200, size=72, until_at="cooling"),
  LOW("Thousands of GPUs", sub="wired to work as one", x=110, y=860, at="gpus", until_at="cooling"),
  V("computer cooling fan", at="cooling", dim=0.4), LOW("Cooling", sub="the chips run hot", x=110, y=860, at="cooling", until_at="electricity"),
  V("electricity power lines", at="electricity", dim=0.4), LOW("Electricity", sub="enormous amounts", x=110, y=860, at="electricity", until_at="most expensive"),
  V("computer chip circuit board", at="most expensive", dim=0.45), T("The chips are the *expensive* part", y=520, size=88, at="most expensive")],
 # 7 why spend
 [P("Mark Zuckerberg", dim=0.4), T("Why spend like *this*?", y=200, size=80, until_at="misspending"),
  HL("Mark Zuckerberg (paraphrased)", "Misspending a couple hundred billion would be unfortunate. Falling behind would be worse.",
     y=470, at="misspending", w=1250, size=50, color="blue"),
  V("race car start", at="every company", dim=0.45), T("Nobody wants to stop *first*", y=540, size=100, at="first to stop")],
 # 8 gigawatts
 [V("power plant cooling towers", dim=0.4), T("Measured in *gigawatts*", y=520, size=110, at="measured", until_at="one gigawatt"),
  V("electricity transmission lines sunset", at="one gigawatt", dim=0.4),
  ST(1, suffix=" GIGAWATT", label="≈ several hundred thousand US homes", y=460, at="one gigawatt", until_at="ten gigawatt"),
  ST(10, suffix=" GIGAWATTS", label="≈ a few million homes", y=460, color="red", at="ten gigawatt"),
  CAP("plus new power plants and transmission lines to feed them", y=760, size=44, at="power plants")],
 # 9
 [V("computer chip macro", pick=1, dim=0.45), T("Where does the money *go*?", y=520, size=100, until_at="one company"),
  P("Nvidia headquarters", at="one company", move="in", dim=0.35), T("The *chip maker*", y=880, size=96, at="makes the chips")],
 # 10 Nvidia
 [P("Jensen Huang", dim=0.35), LOW("Nvidia", sub="the chips most AI is built on", x=110, y=860, until_at="software"),
  V("circuit board technology", at="software", dim=0.45), T("The chips *+* the software", y=500, size=96, at="software", until_at="alternatives"),
  P("Nvidia headquarters", at="alternatives", pick=1, dim=0.4), T("Few *alternatives*", y=520, size=120, at="alternatives")],
 # 11 three players
 [PANEL(), T("The three *players*", y=70, size=60), LOOP(reveal=[999, 999, 999])],
 # 12 the steps
 [PANEL(), LOOP(reveal_at=["step one", "step two", "step three"]), T("The *loop*", y=70, size=60)],
 # 13 came back
 [PANEL(), LOOP(reveal=[0, 0, 0]), T("Same dollars, counted *twice*?", y=1000, size=60, at="same dollars")],
 # 14 Nvidia → OpenAI
 [P("Jensen Huang", pick=1, dim=0.45), HL("Sept 2025", "Nvidia plans to invest up to $100 billion in OpenAI", y=330, at="nvidia announced", w=1150),
  ST(100, prefix="$", suffix="B", label="up to: Nvidia → OpenAI", y=700, w=900, size=170, at="one hundred billion", until_at="scaled back"),
  V("artificial intelligence network technology", at="scaled back", dim=0.45), LOW("Later: a reported $30B stake", sub="the pattern stayed the same", x=110, y=860, at="scaled back")],
 # 15 AMD
 [P("AMD headquarters", dim=0.4), LOW("AMD → OpenAI", x=110, y=110),
  ST(160, suffix="M SHARES", label="right to buy, ≈ 10% of AMD", y=500, at="one hundred sixty"),
  P("Lisa Su", at="six gigawatts", dim=0.4), LOW("6 gigawatts of AMD chips", x=110, y=860, at="six gigawatts")],
 # 16 Oracle
 [P("Oracle headquarters", dim=0.4), LOW("OpenAI → Oracle", sub="reported deal", x=110, y=110),
  ST(300, prefix="$", suffix="B", label="of computing, about 5 years", y=500, at="three hundred", until_at="buy enormous"),
  V("server racks data center", pick=1, at="buy enormous", dim=0.4), T("…which means buying *chips*", y=540, size=96, at="buy enormous")],
 # 17 $1.4T
 [P("Sam Altman", dim=0.4), LOW("Sam Altman", sub="OpenAI CEO", x=110, y=110, until_at="one point four"),
  ST(1.4, prefix="$", suffix=" TRILLION", decimals=1, label="computing commitments, ~8 years", y=520, at="one point four"),
  V("clock time lapse", at="eight years", dim=0.5)],
 # 18 the gap chart
 [PANEL(), T("Commitments vs. *revenue*", y=110, size=70),
  CH([{"label": "Commitments (~8 yrs)", "value": 1400, "valueLabel": "$1.4T", "color": "red"},
      {"label": "Revenue (per year)", "value": 20, "valueLabel": "~$20B", "color": "green"}],
     title="OpenAI", y=580, w=1200, h=700, dur=3.5, at="actually earns")],
 # 19 70:1
 [PANEL(), ST(70, suffix=" : 1", label="commitments vs. yearly revenue", y=380, color="red", card=False, size=260, at="seventy"),
  T("Even over 8 years: still ~*$175B a year*", y=700, size=64, at="spread over"),
  CAP("revenue would need to grow many times over, fast", y=830, size=44, at="grow many")],
 # 20 $18 a month
 [V("people looking at smartphones", dim=0.45),
  ST(800, suffix="M", label="ChatGPT weekly users (late 2025)", y=480, at="eight hundred", until_at="to cover"),
  ST(18, prefix="≈ $", suffix=" / MONTH", label="from every user, to cover $175B a year", y=480, color="red", at="eighteen dollars"),
  CAP("…and most of them pay nothing today", y=760, size=50, at="nothing")],
 # 21 losses
 [V("stock market chart red decline", dim=0.45), T("Losses for *years*", y=420, size=110, at="losing money", until_at="money yet"),
  CAP("profit target: around 2030", y=560, size=48, at="end of the decade", until_at="money yet"),
  P("Jensen Huang", pick=2, at="money yet", dim=0.5),
  HL("Jensen Huang, Nvidia CEO · 2025", "\"OpenAI doesn't have the money yet.\"", y=500, at="money yet", w=1100, size=64, color="blue")],
 # 22 where from
 [P("Wall Street sign", dim=0.4), T("So where does the money *come from*?", y=380, size=84, at="where does"),
  T("Investors", y=600, size=110, at="investors"), T("+ *debt*", y=740, size=110, hl="red", at="debt")],
 # 23 neoclouds
 [V("construction site steel building", dim=0.45), T("The *neoclouds*", y=420, size=120, at="neoclouds"),
  LOW("CoreWeave · Nebius · IREN", x=110, y=860, at="neoclouds"),
  CAP("they borrow, often without investment-grade credit ratings", y=600, size=48, at="investment-grade")],
 # 24 rates
 [V("stock exchange trading board", dim=0.45), LOW("Rates up → lenders pull back", x=110, y=110, at="interest rates"),
  ST(80, suffix="%", label="of neoclouds absorbed or gone by 2030 (Gartner)", y=520, color="red", at="eighty percent")],
 # 25 reverse
 [PANEL(), LOOP(reverse=True, reveal_at=["can't borrow", "can't buy chips", "reverse"], labels=["no loans", "no chip orders", "sales slow"]),
  T("The loop runs in *reverse*", y=1000, size=60, hl="red", at="reverse")],
 # 26 the fear
 [V("worried man looking at screen", dim=0.4), T("The fear, *last week*", y=300, size=96, until_at="negative"),
  T("Negative free *cash flow*", y=500, size=100, hl="red", at="negative"),
  CAP("Alphabet & Meta: spending more than their businesses brought in", y=660, size=46, at="spent more")],
 # 27 depreciation
 [V("computer chip macro", pick=2, dim=0.45), T("The *time* problem", y=200, size=80, until_at="outdated"),
  T("A new, faster chip *every year*", y=480, size=84, at="outdated", until_at="five to six"),
  T("Accounting life: *5–6 years*", y=480, size=96, at="five to six", until_at="three years"),
  T("Worth much less after *~3*?", y=480, size=96, hl="red", at="three years")],
 # 28 debt vs hardware
 [V("old computer hardware", dim=0.45),
  LOW("Loan: many years", x=110, y=700, color="red", at="borrow money"),
  LOW("Chips: obsolete in ~3?", x=110, y=840, color="blue", at="obsolete"),
  T("A loan backed by *old hardware*", y=400, size=88, at="lender")],
 # 29 1999
 [V("telecommunication tower antenna", dim=0.45), T("We've seen this *before*", y=300, size=88, until_at="lent money"),
  T("*1999*: the telecom boom", y=420, size=110, at="nineteen nineties", until_at="vendor financing"),
  CAP("equipment makers lent money to their own customers", y=640, size=50, at="lent money"),
  T("\"Vendor *financing*\"", y=420, size=110, at="vendor financing")],
 # 30 Cisco
 [V("stock market chart red decline", pick=1, dim=0.4), T("Sales looked *incredible*…", y=360, size=96, at="incredible", until_at="couldn't pay"),
  T("…until customers *couldn't pay*", y=360, size=96, hl="red", at="couldn't pay", until_at="cisco"),
  LOW("Cisco", sub="briefly the world's most valuable company", x=110, y=110, at="cisco"),
  ST(80, prefix="-", suffix="%+", label="Cisco's value, 2000 → 2002", y=560, color="red", at="eighty percent")],
 # 31 to be fair
 [V("office workers laptop meeting", dim=0.45), T("To be *fair*", y=220, size=96, hl="green"),
  LOW("The buyers are hugely profitable", x=110, y=560, color="green", at="profitable"),
  LOW("Real customers pay for AI", x=110, y=700, color="green", at="real people"),
  LOW("Circular deals may spread risk", x=110, y=840, color="green", at="spread risk")],
 # 32 the real question
 [V("artificial intelligence robot hand", pick=1, dim=0.5), T("Is AI useful? *Yes.*", y=380, size=100, hl="green", until_at="mistaken"),
  T("Circle money, or *customer* money?", y=560, size=96, at="mistaken")],
 # 33 bubble math
 [PANEL(), T("How a bubble *pops*", y=120, size=80),
  T("expected profit × excitement = price", y=270, size=50, upper=False, at="simple math"),
  T("$10 × 30 = *$300*", y=450, size=110, hl="green", at="ten dollars"),
  T("$8 × 20 = *$160*", y=620, size=110, hl="red", at="eight dollars"),
  ST(47, prefix="-", suffix="%", label="while still very profitable", y=870, color="red", size=120, w=800, at="nearly half")],
 # 34 Intel
 [P("Intel headquarters", pick=1, dim=0.4), LOW("Intel · Oct 30", x=110, y=110),
  T("One weak *forecast*", y=360, size=100, at="weak forecast"),
  ST(28.6, prefix="-", suffix="%", decimals=1, label="in a single day", y=640, color="red", w=800, size=170, at="single day"),
  CAP("when profit hopes and excitement drop together, prices fall fast", y=900, size=40, at="both")],
 # 35 soft landing
 [V("airplane landing", pick=2, dim=0.45), T("Ending 1: *soft landing*", y=180, size=84, hl="green"),
  LOW("AI revenue keeps growing", x=110, y=560, color="green", at="keeps growing"),
  LOW("Spending slows gradually", x=110, y=700, color="green", at="slows down"),
  LOW("The industry grows into it", x=110, y=840, color="green", at="survives")],
 # 36 hard landing
 [V("storm clouds timelapse", dim=0.45), T("Ending 2: *hard landing*", y=180, size=84, hl="red"),
  LOW("Customers don't pay enough", x=110, y=480, color="red", at="customers"),
  LOW("Lenders pull back", x=110, y=610, color="red", at="lenders"),
  LOW("Chip orders get cancelled", x=110, y=740, color="red", at="cancel"),
  CAP("which ending we get depends on three signals", y=960, size=44, at="depends")],
 # 37 signal 1
 [P("Nvidia headquarters", pick=2, dim=0.45), LOW("Signal 1", sub="Nvidia earnings · Nov 17", x=110, y=110, size=56),
  T("How much growth comes from customers it *invested in*?", y=560, size=70, w=1600, at="invested in")],
 # 38 signal 2
 [P("Wall Street sign", pick=1, dim=0.45), LOW("Signal 2", sub="can the builders still borrow?", x=110, y=110, size=56),
  T("Higher interest = the loop *slowing*", y=560, size=84, hl="red", at="slowing")],
 # 39 signal 3
 [V("business people meeting office", dim=0.45), LOW("Signal 3", sub="real customer revenue", x=110, y=110, size=56),
  T("Revenue growth *>* spending growth", y=460, size=84, at="faster than", until_at="turns this"),
  T("Loop → *business*", y=560, size=120, hl="green", at="turns this")],
 # 40 index funds
 [V("person looking at phone finance app", dim=0.45), T("Why it matters to *you*", y=240, size=84),
  ST(33, prefix="≈ ", suffix="%", label="of a typical index fund is tech (roughly a third)", y=560, at="a third"),
  CAP("your retirement account is already riding the loop", y=820, size=48, at="retirement")],
 # 41 don't panic
 [V("sunrise calm city", dim=0.45), T("Don't *panic*", y=380, size=110, hl="green", at="panic"),
  CAP("not financial advice", y=500, size=36, opacity=0.7, at="panic"),
  T("Know what you *own*", y=640, size=110, at="know what you own")],
 # 42 practical step
 [V("person laptop investment chart", dim=0.45), LOW("One practical step", x=110, y=110, color="yellow"),
  T("Check your funds' *top holdings*", y=480, size=96, at="top holdings"),
  CAP("same few tech names everywhere? you're more concentrated than you think", y=660, size=46, at="handful")],
 # 43 takeaway
 [PANEL(), LOOP(reveal_at=["chip makers fund", "ai labs rent", "cloud companies buy"]),
  T("…and *debt* keeps it spinning", y=1000, size=58, hl="red", at="debt keeps")],
 # 44 outro
 [V("people walking city street", dim=0.45), T("*Subscribe*", y=420, size=130, at="subscribe"),
  T("Bubble, or something *real*?", y=640, size=84, at="comments")],
]

src = json.loads((Path(__file__).parent.parent / "EP02_AI_Money_Loop" / "scenes.json").read_text(encoding="utf-8"))
texts = src["outputs"][0]["scenes"]
assert len(texts) == len(VIS), (len(texts), len(VIS))
SCENES = [{**({"chapter": s["chapter"]} if s.get("chapter") else {}), "text": s["text"], "elements": v}
          for s, v in zip(texts, VIS)]

MUSIC = {"url": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Investigations.mp3", "volume": 0.07,
         "credit": '"Investigations" Kevin MacLeod (incompetech.com), licensed under Creative Commons: By Attribution 4.0'}
ep = Path(__file__).parent
out = ep / "scenes.json"
prev = json.loads(out.read_text(encoding="utf-8")) if out.exists() else None
cfg = {"voice": "en-US-AndrewNeural", "rate": "-2%", "music": MUSIC,
       "outputs": [{"name": "EP02_The_AI_Money_Loop", "format": "long", "engine": "doc", "scenes": SCENES}]}
if prev:  # keep media already resolved and reviewed
    keep = {(e.get("q"), e.get("img"), e.get("pick", 0)): e for o in prev["outputs"] for s in o["scenes"]
            for e in s["elements"] if e.get("url")}
    for s in SCENES:
        for e in s["elements"]:
            k = keep.get((e.get("q"), e.get("img"), e.get("pick", 0)))
            if k:
                e.update({f: k[f] for f in ("url", "clipSeconds", "credit", "thumb", "kind") if f in k})
out.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(len(SCENES), "scenes,", sum(len(s["text"].split()) for s in SCENES), "words,",
      sum(1 for s in SCENES for e in s["elements"] if e["type"] == "shot"), "shots")
