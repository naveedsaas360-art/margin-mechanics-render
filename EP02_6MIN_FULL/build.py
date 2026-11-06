"""'The AI Money Loop, Explained in 6 Minutes': FULL video.

Minute 1 = the approved clip A (EP02_6MIN), with the hook promise extended to 3 numbered payoffs.
Minutes 2-6 = the verified EP02 script condensed; visuals reuse the reviewed EP02_DOC scenes (same licensed media).
"""
import json, runpy
from pathlib import Path

ep = Path(__file__).parent
A = runpy.run_path(str(ep.parent / "EP02_6MIN" / "build.py"))
D = runpy.run_path(str(ep.parent / "EP02_DOC" / "build.py"))
V, T, CAP, LOOP, PANEL = A["V"], A["T"], A["CAP"], A["LOOP"], A["PANEL"]
VIS = D["VIS"]

first = [dict(s) for s in A["SCENES"]]
first[0]["chapter"] = "The trillion-dollar week"
first[2] = dict(
    text="This is the AI money loop, explained in six minutes. You'll see how the loop works, why it made the boom look bigger than it was, and three warning signs to watch for your own money.",
    elements=[PANEL(until_at="you'll see"), LOOP(reveal=[0.1, 0.5, 0.9], labels=None, until_at="you'll see"),
              T("The AI *money loop*", y=960, size=70, at="money loop", hl="yellow", until_at="you'll see"),
              V("artificial intelligence robot hand", at="you'll see", dim=0.55),
              T("In the next *6 minutes*", y=230, size=80, at="you'll see"),
              CAP("① How the loop works", y=480, size=60, at="how the loop"),
              CAP("② Why the boom looked bigger", y=600, size=60, at="bigger"),
              CAP("③ 3 warning signs for your money", y=720, size=60, at="warning signs")])

REST = [  # (chapter, text, EP02_DOC visual index)
 ("The loop", "Picture three players. A chip maker, like Nvidia or AMD. An AI lab, like OpenAI. And a cloud company, like Oracle or CoreWeave, that owns the data centers.", 11),
 (None, "Step one: the chip maker invests in the AI lab. Step two: the AI lab signs a giant contract to rent computing power from the cloud company. Step three: the cloud company uses that contract to raise money, and buy chips from the chip maker.", 12),
 (None, "And look what just happened. The chip maker's investment came back to it as sales. The same dollars, counted twice.", 13),
 (None, "This isn't a theory. In September twenty twenty-five, Nvidia announced it could invest up to one hundred billion dollars in OpenAI, while OpenAI filled data centers with Nvidia chips. That plan was later reportedly scaled back to a thirty billion dollar stake. But the pattern stayed the same.", 14),
 (None, "Weeks later, AMD gave OpenAI the right to buy up to one hundred sixty million AMD shares, about ten percent of the company, as part of a deal for six gigawatts of AMD chips.", 15),
 (None, "OpenAI also reportedly agreed to buy around three hundred billion dollars of computing from Oracle over about five years. And Oracle, to deliver it, has to buy enormous amounts of chips.", 16),
 (None, "Altogether, OpenAI's CEO has said the company is looking at about one point four trillion dollars of computing commitments over roughly eight years.", 17),
 ("The gap", "But OpenAI actually earns about twenty billion dollars a year.", 18),
 (None, "That's a seventy to one gap. Even spread over eight years, its revenue would need to grow many times over, very fast.", 19),
 (None, "ChatGPT has about eight hundred million weekly users. To cover one hundred seventy-five billion dollars a year, every one of them would need to pay about eighteen dollars a month. Most of them pay nothing today.", 20),
 (None, "OpenAI's own projections show it losing money for years, until around the end of the decade. Even Nvidia's CEO said OpenAI doesn't have the money yet.", 21),
 (None, "So where does the money come from? Investors, and debt.", 22),
 ("The debt layer", "Many data center builders, the so-called neoclouds, borrow to build, often without investment-grade credit ratings.", 23),
 (None, "As interest rates rose, lenders started pulling back. Gartner even predicts that by twenty thirty, eighty percent of these neoclouds will be absorbed or gone.", 24),
 (None, "Think about what that does to the loop. If a cloud company can't borrow, it can't buy chips. The chip maker's sales slow down. And the loop runs in reverse.", 25),
 (None, "There's also a hidden time problem. AI chips get outdated fast, because a faster one comes out every year. Yet big tech spreads their cost over five to six years. If they're worth much less after three years, today's profits look better than they really are.", 27),
 ("We've seen this before", "We've seen this before. In the late nineteen nineties, telecom equipment makers lent money to their own customers, so they could buy more equipment. It was called vendor financing.", 29),
 (None, "Sales looked incredible, right until the customers couldn't pay. And Cisco, briefly the most valuable company in the world, lost more than eighty percent of its value.", 30),
 (None, "To be fair, today is not an exact copy. The biggest buyers are hugely profitable, and real people pay for AI every day. Some economists argue these deals simply spread risk around.", 31),
 (None, "The real question isn't whether AI is useful. It clearly is. It's whether money flowing in a circle is being mistaken for money flowing in from customers.", 32),
 ("Two ways this ends", "So there are two ways this ends. A soft landing: AI revenue keeps growing, spending slows down gradually, and the industry survives and grows into it.", 35),
 (None, "Or a hard landing: customers don't pay enough, lenders pull back, cloud companies cancel chip orders, and stocks fall far more than the businesses. Which one we get depends on three warning signs.", 36),
 ("3 warning signs", "Sign one: Nvidia's earnings on November seventeenth. Watch how much of its growth comes from customers it has also invested in.", 37),
 (None, "Sign two: borrowing. If data center builders struggle to raise debt, or pay much higher interest, the loop is slowing.", 38),
 (None, "Sign three: real revenue. Watch whether sales from actual customers grow faster than spending. That's the only thing that turns this from a loop into a business.", 39),
 ("What it means for you", "And here's why this matters to you. If you own an index fund, roughly a third of it is technology. Your retirement account is already riding the loop.", 40),
 (None, "That's no reason to panic, and this isn't financial advice. It means: know what you own.", 41),
 (None, "One practical step: open your investment account and check the top holdings. If the same handful of tech names tops every fund, you're more concentrated in this one story than you think.", 42),
 (None, "So, the AI money loop: chip makers fund AI labs, AI labs rent from cloud companies, cloud companies buy chips, and debt keeps it spinning. If customers keep paying more, it holds. If not, this is where the cracks show first.", 43),
 (None, "Subscribe for the next hidden money machine, and tell me in the comments: is this a bubble, or the beginning of something real?", 44),
]
SIGN = {37: "Sign 1", 38: "Sign 2", 39: "Sign 3"}
P, ST, LOW = A["P"], A["ST"], A["LOW"]
# QA fixes (2026-11-06): no screen held > ~5 s, no off-topic photo, no text on diagram labels
OVERRIDE = {
 11: [P("Nvidia headquarters"), LOW("Chip maker", sub="Nvidia · AMD", x=110, y=860, until_at="ai lab"),
      P("Sam Altman", at="ai lab", move="left", dim=0.35), LOW("AI lab", sub="OpenAI", x=110, y=860, at="ai lab", until_at="cloud company"),
      P("Oracle headquarters", at="cloud company", move="right", dim=0.35), LOW("Cloud company", sub="Oracle · CoreWeave", x=110, y=860, at="cloud company", until_at="owns the"),
      V("server room data center", pick=1, at="owns the", dim=0.4), T("The three *players*", y=520, size=110, at="owns the")],
 14: [P("Jensen Huang", pick=1, dim=0.45),
      {"type": "headline", "source": "Sept 2025", "text": "Nvidia plans to invest up to $100 billion in OpenAI", "x": 960, "y": 330, "at": "nvidia announced", "w": 1150, "until_at": "while openai"},
      V("server racks data center lights", at="one hundred billion", dim=0.45),
      ST(100, prefix="$", suffix="B", label="up to: Nvidia → OpenAI", y=540, w=900, size=170, at="one hundred billion", until_at="scaled back"),
      P("Sam Altman", at="while openai", move="in", dim=0.4),
      V("artificial intelligence network technology", at="scaled back", dim=0.45),
      LOW("Later: a reported $30B stake", sub="the pattern stayed the same", x=110, y=860, at="scaled back")],
 15: [P("AMD headquarters", dim=0.4), LOW("AMD → OpenAI", x=110, y=110),
      V("computer chip macro", pick=1, at="one hundred sixty", dim=0.45),
      ST(160, suffix="M SHARES", label="right to buy, ≈ 10% of AMD", y=500, at="one hundred sixty", until_at="six gigawatts"),
      P("Lisa Su", at="six gigawatts", dim=0.4), LOW("6 gigawatts of AMD chips", x=110, y=860, at="six gigawatts")],
 19: [V("stock market chart red decline", pick=1, dim=0.6),
      ST(70, suffix=" : 1", label="commitments vs. yearly revenue", y=420, color="red", size=240, at="seventy", until_at="spread over"),
      V("clock time lapse", at="spread over", dim=0.55),
      T("Even over 8 years: still ~*$175B a year*", y=480, size=70, at="spread over"),
      CAP("revenue would need to grow many times over, fast", y=640, size=46, at="grow many")],
 25: [{**e, "y": 90} if e.get("type") == "title" else e for e in VIS[25]],
 37: [P("Nvidia headquarters"), LOW("Sign 1", sub="Nvidia earnings · Nov 17", x=110, y=110, size=56),
      V("computer chip macro", pick=2, at="watch how", dim=0.5),
      T("How much growth comes from customers it *invested in*?", y=560, size=70, w=1600, at="invested in")],
 39: [V("business people meeting office", dim=0.45), LOW("Sign 3", sub="real customer revenue", x=110, y=110, size=56),
      V("people looking at smartphones", at="faster than", dim=0.5),
      T("Revenue growth *>* spending growth", y=460, size=84, at="faster than", until_at="turns this"),
      V("person laptop investment chart", at="turns this", dim=0.5),
      T("Loop → *business*", y=560, size=120, hl="green", at="turns this")],
 43: [{**e, "y": 80} if e.get("type") == "title" else e for e in VIS[43]],
}
rest = []
for ch, text, i in REST:
    els = json.loads(json.dumps(OVERRIDE.get(i, VIS[i])))
    for e in els:
        if e.get("type") == "lower" and e.get("text", "").startswith("Signal"):
            e["text"] = SIGN[i]
    rest.append({**({"chapter": ch} if ch else {}), "text": text, "elements": els})
SCENES = first + rest

# media: everything already resolved + reviewed in EP02_DOC / EP02_6MIN
known = {}
for f in ("EP02_DOC", "EP02_6MIN"):
    cfg0 = json.loads((ep.parent / f / "scenes.json").read_text(encoding="utf-8"))
    for o in cfg0["outputs"]:
        for s in o["scenes"]:
            for e in s["elements"]:
                if e.get("url"):
                    known[(e.get("q"), e.get("img"), e.get("pick", 0))] = e
missing = []
for s in SCENES:
    for e in s["elements"]:
        if e["type"] == "shot" and not e.get("url"):
            k = known.get((e.get("q"), e.get("img"), e.get("pick", 0)))
            if k:
                e.update({f: k[f] for f in ("url", "clipSeconds", "credit", "thumb", "kind", "focus") if f in k})
            else:
                missing.append(e.get("q") or e.get("img"))

cfg = {**{k: v for k, v in json.loads((ep.parent / "EP02_6MIN" / "scenes.json").read_text(encoding="utf-8")).items() if k != "outputs"},
       "outputs": [{"name": "The_AI_Money_Loop_Explained_in_6_Minutes", "format": "long", "engine": "doc", "scenes": SCENES}]}
(ep / "scenes.json").write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
words = sum(len(s["text"].split()) for s in SCENES)
print(len(SCENES), "scenes,", words, "words ≈", round(words / 175, 1), "min; unresolved:", missing)
