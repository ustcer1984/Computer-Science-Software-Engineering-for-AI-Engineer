#!/usr/bin/env python3
"""How many pages a crawler takes for every visitor it sends back.

ONE SOURCE, ONE UNIT, TWO DATES — deliberately, so the chart is comparable.

All numbers are Cloudflare's own published "crawl-to-refer ratio": HTML page
requests by an operator's crawlers divided by the referrals that operator sent
back to the same sites, measured across Cloudflare's network.

    Source: "The crawl-to-click gap: Cloudflare data on AI bots, training, and
    referrals", The Cloudflare Blog, 29 August 2025.
    https://blog.cloudflare.com/crawlers-click-ai-bots-training/

        operator      Jan 2025        Jul 2025
        Anthropic     286,930 : 1      38,066 : 1
        OpenAI          1,217 : 1       1,091 : 1
        Perplexity         54 : 1         195 : 1
        Microsoft        38.5 : 1        40.7 : 1
        Google            3.8 : 1         5.4 : 1
        ByteDance          18 : 1         0.9 : 1

WHAT THE CHART IS FOR. Not "AI bad" — the spread is the finding. Five orders of
magnitude separate the operators, and the split is not about politeness, it is
about business model. An operator that runs a consumer search product has to
send a click back, because the crawl exists to power a result someone clicks.
An operator that answers in place does not.

The 1:1 line is the old bargain of the web: take a page, return a visitor.

Later readings of Cloudflare Radar (secondary, different windows, so NOT plotted
here) put Anthropic near 11,000:1 and OpenAI near 900:1 by mid-2026 — the gap
narrowing, still orders of magnitude wide.

Emits a committed PNG next to the reading.
"""
import matplotlib.pyplot as plt
import numpy as np

rows = [
    # operator,      Jan 2025,  Jul 2025,  note
    ("Anthropic",     286930.0,  38066.0, "answers in place"),
    ("OpenAI",          1217.0,   1091.0, "answers in place"),
    ("Perplexity",        54.0,    195.0, "cites inline"),
    ("Microsoft",         38.5,     40.7, "runs a search product"),
    ("Google",             3.8,      5.4, "runs a search product"),
    ("ByteDance",         18.0,      0.9, "sends more than it takes"),
]

labels = [r[0] for r in rows]
jan = np.array([r[1] for r in rows])
jul = np.array([r[2] for r in rows])
y = np.arange(len(rows))[::-1]  # first row on top

fig, ax = plt.subplots(figsize=(10.2, 5.6), dpi=150)

ax.set_xscale("log")
ax.barh(y, jul, height=0.52, color="#2c5f8a", zorder=3, label="July 2025")
ax.plot(jan, y, "o", ms=8, mfc="#ffffff", mec="#c2451e", mew=2.0, zorder=4,
        label="January 2025 (for comparison)")

for yi, a, b in zip(y, jan, jul):
    ax.annotate("", xy=(b, yi), xytext=(a, yi),
                arrowprops=dict(arrowstyle="-|>", color="#c2451e", lw=1.1,
                                shrinkA=3, shrinkB=3, alpha=0.75), zorder=2)

# value labels
for yi, b, note in zip(y, jul, [r[3] for r in rows]):
    txt = f"{b:,.0f}:1" if b >= 10 else f"{b:.1f}:1"
    ax.text(b * 1.25, yi + 0.02, txt, va="center", ha="left",
            fontsize=10.5, fontweight="bold", color="#1b3d57")
    ax.text(b * 1.25, yi - 0.30, note, va="center", ha="left",
            fontsize=8.6, color="#666666", style="italic")

ax.axvline(1.0, color="#111111", lw=1.4, ls="--", zorder=5)
ax.text(1.15, -0.62, "1:1 — the old bargain of the web: take a page, send back a visitor",
        fontsize=9.5, color="#111111", va="center", ha="left")

ax.set_yticks(y)
ax.set_yticklabels(labels, fontsize=11.5)
ax.set_xlim(0.4, 3.0e6)
ax.set_ylim(-0.8, len(rows) - 0.25)
ax.set_xlabel("HTML pages crawled per referral sent back  (log scale)", fontsize=11)
ax.set_title("The crawl-to-refer ratio: five orders of magnitude, and it tracks the business model\n"
             "Cloudflare network measurements, January vs July 2025",
             fontsize=12.5, fontweight="bold", loc="left")
ax.grid(axis="x", which="major", ls=":", color="#bbbbbb", alpha=0.8, zorder=0)
ax.grid(axis="x", which="minor", ls=":", color="#dddddd", alpha=0.5, zorder=0)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.legend(loc="lower right", fontsize=9.5, framealpha=0.95)

fig.text(0.005, 0.005,
         "Data: Cloudflare, 'The crawl-to-click gap' (29 Aug 2025). Arrows show the move from January to July 2025.",
         fontsize=8.2, color="#777777")
fig.tight_layout(rect=(0, 0.025, 1, 1))
out = __file__.replace("-plot.py", "-plot.png")
fig.savefig(out, bbox_inches="tight")
print(out)
