"""
Figures for M01 · Ch4 · §3 — Why I/O dominates latency.

fig1: "The tail at scale" — probability that a single request touches AT LEAST
one slow backend, P = 1 - p^N, as fan-out N grows, for several per-backend
"fast" probabilities p (p99 / p99.9 / p99.99). The counterintuitive result
(Dean & Barroso): at N=100 with a 1%-slow backend, ~63% of requests hit a slow
one — so the *tail* per server becomes the *common case* for the fanned-out
request. Each 10x better per-server tail buys ~10x more fan-out headroom.

fig2: "Sum vs max" — N independent I/O requests run serially (total = sum of
latencies) vs concurrently (total = max). The Little's-Law / asyncio.gather
payoff: overlapping waits collapses wall-clock from Σ to max.

Run:  python 03-why-io-dominates-latency-figures.py
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# ----------------------------------------------------------------- fig 1
N = np.logspace(0, 3, 400)                    # fan-out: 1 → 1000 backends
series = [
    (0.99,   "#C0392B", "backend p99  (1% slow)"),
    (0.999,  "#E9852E", "backend p99.9  (0.1% slow)"),
    (0.9999, "#2E7D32", "backend p99.99  (0.01% slow)"),
]

fig1, ax = plt.subplots(figsize=(10.5, 5.8))
for p, c, lab in series:
    ax.semilogx(N, 1 - p ** N, color=c, lw=2.6, label=lab, zorder=3)

# the headline point: N=100, p=0.99 → 0.634
ax.scatter([100], [1 - 0.99 ** 100], color="#C0392B", s=55, zorder=5)
ax.annotate(
    "fan out to 100 backends,\nwait for all, each 1% slow:\n→ 63% of requests hit a slow one\n(the tail becomes the common case)",
    xy=(100, 1 - 0.99 ** 100), xytext=(1.4, 0.80),
    fontsize=9.4, color="#7A1F16",
    arrowprops=dict(arrowstyle="->", color="#7A1F16", lw=1.3),
    ha="left", va="center",
)
ax.axhline(0.5, color="#999999", ls=":", lw=1.0, zorder=1)
ax.text(1.05, 0.515, "half of all requests are slow", color="#666666", fontsize=8.5, va="bottom")

ax.set_xlabel("fan-out  N  (backends contacted per request, log scale)", fontsize=11)
ax.set_ylabel("P(request waits on ≥ 1 slow backend)  =  1 − pᴺ", fontsize=11)
ax.set_title("The tail at scale: rare per-server slowness becomes common under fan-out", fontsize=12.5, pad=12)
ax.set_ylim(0, 1.02)
ax.grid(True, which="major", ls=":", color="#BBBBBB", zorder=0)
ax.grid(True, which="minor", axis="x", ls=":", color="#EEEEEE", zorder=0)
ax.set_axisbelow(True)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.legend(loc="center right", fontsize=9.8, framealpha=0.96, title="per-backend latency tail")
fig1.tight_layout()
fig1.savefig("03-why-io-dominates-latency-fig1.svg", bbox_inches="tight")
print("wrote 03-why-io-dominates-latency-fig1.svg")

# ----------------------------------------------------------------- fig 2
lat = [90, 110, 100, 130, 95]                 # ms, one straggler at 130
labels = [f"request {i+1}" for i in range(len(lat))]
serial_total = sum(lat)
conc_total = max(lat)
y = list(range(len(lat)))[::-1]

fig2, (axS, axC) = plt.subplots(2, 1, figsize=(10.5, 5.8), sharex=True)

# serial: each starts where the previous ended
start = 0
for yi, (L, lab) in zip(y, zip(lat, labels)):
    axS.barh(yi, L, left=start, height=0.6, color="#C0392B", zorder=3)
    axS.text(start + L / 2, yi, f"{L} ms", ha="center", va="center", color="white", fontsize=9)
    start += L
axS.set_yticks(y); axS.set_yticklabels(labels, fontsize=9.5)
axS.set_title(f"Serial — one after another:  total = Σ latencies = {serial_total} ms", fontsize=11, color="#7A1F16")
axS.axvline(serial_total, color="#7A1F16", ls="--", lw=1.2)

# concurrent: all start at 0
for yi, (L, lab) in zip(y, zip(lat, labels)):
    axC.barh(yi, L, left=0, height=0.6, color="#2E7D32", zorder=3)
    axC.text(L / 2, yi, f"{L} ms", ha="center", va="center", color="white", fontsize=9)
axC.set_yticks(y); axC.set_yticklabels(labels, fontsize=9.5)
axC.set_title(f"Concurrent — overlapped (one thread, epoll):  total = max = {conc_total} ms", fontsize=11, color="#1E5E22")
axC.axvline(conc_total, color="#1E5E22", ls="--", lw=1.2)
axC.set_xlabel("wall-clock time (ms)", fontsize=11)

for a in (axS, axC):
    a.set_xlim(0, serial_total * 1.05)
    a.grid(axis="x", ls=":", color="#CCCCCC", zorder=0)
    a.set_axisbelow(True)
    for s in ("top", "right"):
        a.spines[s].set_visible(False)

fig2.suptitle("Same 5 I/O-bound requests: overlapping the waits collapses Σ → max", fontsize=12.5, y=0.99)
fig2.tight_layout()
fig2.savefig("03-why-io-dominates-latency-fig2.svg", bbox_inches="tight")
print("wrote 03-why-io-dominates-latency-fig2.svg")

# ----------------------------------------------------------------- fig 3
# Applied (§9): anatomy of one cold request, from a real serverless latency
# investigation (representative dev numbers). Every large slice is a round-trip
# or a setup cost; the actual DB query — the only "real work" — is a sliver.
# Segment = (name, ms, colour, which §4 lever attacks it). Levels are mapped
# to the four levers in the §9 prose; here we label name + timing on the bar.
segs = [
    ("container init\n(imports, page-in)",     1400, "#7A1F16"),
    ("init_db bootstrap\n(schema/seed check)", 1000, "#C0392B"),
    ("first DB connect\n(TCP+TLS+auth)",        750, "#E9852E"),
    ("cert fetch\n(1 RTT)",                     360, "#F0B429"),
    ("DB query",                                 42, "#2E7D32"),
]
total = sum(s[1] for s in segs)

fig3, ax3 = plt.subplots(figsize=(11.0, 3.2))
left = 0
for name, ms, colour in segs:
    ax3.barh(0, ms, left=left, height=0.5, color=colour, zorder=3,
             edgecolor="white", lw=1.2)
    if ms >= 300:
        # wide enough: name inside (white), ms above (coloured)
        ax3.text(left + ms / 2, 0.0, name, ha="center", va="center",
                 color="white", fontsize=8.6, linespacing=1.15)
        ax3.text(left + ms / 2, 0.30, f"{ms} ms", ha="center", va="bottom",
                 color=colour, fontsize=9.6, fontweight="bold")
    left += ms

# the sliver of real work is too thin to label in place — carry it on the arrow
ax3.annotate(
    "DB query — the actual work — is 42 ms:\n~1% of the wait. Everything else is a\nround-trip or a one-time setup cost.",
    xy=(total - 21, 0.05), xytext=(total * 0.555, 1.02),
    fontsize=9.4, color="#1E5E22",
    arrowprops=dict(arrowstyle="->", color="#1E5E22", lw=1.5),
    ha="left", va="center",
)
ax3.set_xlim(0, total * 1.02)
ax3.set_ylim(-0.55, 1.35)
ax3.set_yticks([])
ax3.set_xlabel("wall-clock time within one cold request (ms)", fontsize=10.5)
ax3.set_title(
    f"Anatomy of a cold serverless request (~{total/1000:.1f} s): the compute is a sliver, the I/O and setup are everything",
    fontsize=12, pad=10)
ax3.grid(axis="x", ls=":", color="#CCCCCC", zorder=0)
ax3.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax3.spines[s].set_visible(False)
fig3.tight_layout()
fig3.savefig("03-why-io-dominates-latency-fig3.svg", bbox_inches="tight")
print("wrote 03-why-io-dominates-latency-fig3.svg")
