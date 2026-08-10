#!/usr/bin/env python3
"""Does "watch 5 minutes of ads for 1 million tokens" clear? Not for a frontier model.

THE CLAIM BEING TESTED (his, from the session): advertising does not die with the
ad-supported page — it migrates into the token provider's pipeline, in the form
of a barter, e.g. "watch 5 minutes of ads, get 1 million tokens."

The direction turned out to be right and is already shipping (OpenAI began ad
tests in ChatGPT on 9 Feb 2026). The *barter mechanism* is what this chart tests,
and it is short by one to one-and-a-half orders of magnitude.

THE SUPPLY SIDE — what 5 minutes of a person's attention is worth.
Rewarded video is the right comparison: it is the format where a user
*voluntarily* trades attention for a reward, and completion rates clear ~90%.
US / tier-1 rewarded-video eCPM runs about $15-$40 (AppLovin publisher
benchmarks; ~$24 average across mediation). At 30 s per view, 5 minutes is
10 completed views:

        low   $15 eCPM -> 10 x $0.015 = $0.15
        mid   $25 eCPM -> 10 x $0.025 = $0.25      <- used for the bars
        high  $40 eCPM -> 10 x $0.040 = $0.40      <- the error bars

THE DEMAND SIDE — what 1M tokens costs, at list.
Published Anthropic list prices (Aug 2026), blended at 85% input / 15% output,
which is the shape of consumer assistant traffic (long context and history in,
short answer out):

        Claude Opus 5    $5 / $25 per MTok  ->  0.85*5  + 0.15*25 = $8.00
        Claude Sonnet 5  $3 / $15 per MTok  ->  0.85*3  + 0.15*15 = $4.80
        Claude Haiku 4.5 $1 / $5  per MTok  ->  0.85*1  + 0.15*5  = $1.60

WHAT THE CHART SHOWS. For each tier, how many tokens 5 minutes of ads actually
buys, against the 1,000,000 the barter promises. The gap survives the whole
eCPM range, so the conclusion is not an artifact of the rate assumption.

The annotation on each bar inverts it: how long you would really have to watch.
At $25 eCPM a continuous hour of 30-second ads earns 120 x $0.025 = $3.00.

WHY THE BARTER NEVER NEEDED TO CLEAR (the point of the chart, not a defect in
his idea): ad value tracks *intent*, and the highest-intent moment is inside the
answer, not before it. A recommendation slot in a commercial-intent answer
monetizes like search - dollars per click - not like rewarded video's cents per
view. So the money arrived in the pipeline exactly as he predicted; it attached
to the recommendation rather than to the compute.

Emits a committed PNG next to the reading.
"""
import matplotlib.pyplot as plt
import numpy as np

ECPM_MID, ECPM_LO, ECPM_HI = 25.0, 15.0, 40.0
VIEWS_5MIN = 10           # 5 minutes at 30 s per completed view
VIEWS_PER_HOUR = 120

def ad_dollars(ecpm, views):
    return views * ecpm / 1000.0

REV_MID = ad_dollars(ECPM_MID, VIEWS_5MIN)   # $0.25
REV_LO = ad_dollars(ECPM_LO, VIEWS_5MIN)     # $0.15
REV_HI = ad_dollars(ECPM_HI, VIEWS_5MIN)     # $0.40

# model, input $/MTok, output $/MTok
TIERS = [
    ("Claude Opus 5", 5.0, 25.0),
    ("Claude Sonnet 5", 3.0, 15.0),
    ("Claude Haiku 4.5", 1.0, 5.0),
]
IN_SHARE, OUT_SHARE = 0.85, 0.15

labels, mid, lo, hi, hours = [], [], [], [], []
for name, pin, pout in TIERS:
    cost_per_mtok = IN_SHARE * pin + OUT_SHARE * pout
    labels.append(f"{name}\n(${cost_per_mtok:.2f} per 1M tokens, blended)")
    mid.append(REV_MID / cost_per_mtok * 1e6)
    lo.append(REV_LO / cost_per_mtok * 1e6)
    hi.append(REV_HI / cost_per_mtok * 1e6)
    hours.append(cost_per_mtok / (ad_dollars(ECPM_MID, VIEWS_PER_HOUR)))

mid, lo, hi = np.array(mid), np.array(lo), np.array(hi)
y = np.arange(len(TIERS))[::-1]

fig, ax = plt.subplots(figsize=(10.4, 5.2), dpi=150)
ax.set_xscale("log")

ax.barh(y, mid, height=0.5, color="#2c5f8a", zorder=3)
ax.errorbar(mid, y, xerr=[mid - lo, hi - mid], fmt="none", ecolor="#1b3d57",
            elinewidth=1.6, capsize=5, zorder=5)

for yi, m, h in zip(y, mid, hours):
    ax.text(m * 1.18, yi + 0.10, f"{m:,.0f} tokens", va="center", ha="left",
            fontsize=11, fontweight="bold", color="#1b3d57")
    ax.text(m * 1.18, yi - 0.17,
            f"1M tokens would need ≈ {h:.1f} h of ads" if h >= 1
            else f"1M tokens would need ≈ {h*60:.0f} min of ads",
            va="center", ha="left", fontsize=9.2, color="#666666", style="italic")

ax.axvline(1e6, color="#c2451e", lw=2.0, ls="--", zorder=6)
ax.text(1.06e6, y[0] + 0.42, "the claim:\n1,000,000 tokens", color="#c2451e",
        fontsize=10.5, fontweight="bold", va="center", ha="left")

ax.set_yticks(y)
ax.set_yticklabels(labels, fontsize=10.5)
ax.set_xlim(5e3, 6e6)
ax.set_ylim(-0.75, len(TIERS) - 0.15)
ax.set_xlabel("tokens actually bought by 5 minutes of rewarded-video ads  (log scale)", fontsize=11)
ax.set_title("\"Watch 5 minutes of ads for 1 million tokens\" — the exchange rate is off by 6× to 32×\n"
             "bars at $25 eCPM; whiskers span the $15–$40 tier-1 range, so the gap is not an artifact of the rate",
             fontsize=12.3, fontweight="bold", loc="left")
ax.grid(axis="x", which="major", ls=":", color="#bbbbbb", alpha=0.8, zorder=0)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)

fig.text(0.005, 0.005,
         "Supply: rewarded-video eCPM $15–40 tier-1, 30 s per view. Demand: Anthropic list prices (Aug 2026) "
         "blended 85% input / 15% output. Both sides are list-rate estimates, not any provider's actual unit economics.",
         fontsize=8.0, color="#777777")
fig.tight_layout(rect=(0, 0.035, 1, 1))
out = __file__.replace("-plot.py", "-plot.png")
fig.savefig(out, bbox_inches="tight")
print(out)
