#!/usr/bin/env python3
"""Figures for M02 Ch2 §2 — Caching & conditional requests.

fig1: the latency cliff. The SAME logical fetch in three cache states, on a
realistic cross-ocean path, broken into the round-trips it costs:

  - COLD      — nothing cached: DNS + TCP + TLS + full transfer (the Ch1 budget).
  - 304       — stale but unchanged: one conditional round-trip, empty body.
  - FRESH HIT — within max-age: served from cache, NO network at all.

Shows the two wins stacking: validation removes the payload; freshness removes
the network. Mirrors the Ch1 §1 fig1 idiom (stacked horizontal RTT segments).

Run:  python3 02-caching-figures.py   (or the repo .venv/bin/python)
Outputs SVG next to this script (committed alongside the doc).
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "02-caching-fig1.svg")

# phases (ms) on a ~160 ms cross-ocean RTT, reusing Ch1 §1's numbers so the
# two figures are directly comparable.
PHASES = ["DNS", "TCP handshake", "TLS 1.3 handshake",
          "request round-trip", "payload transfer (200 KB)"]
COLORS = ["#b9770e", "#c0392b", "#8e44ad", "#1e8449", "#2471a3"]

# scenario -> per-phase milliseconds (0 = skipped in that state)
SCENARIOS = [
    ("COLD\n(nothing cached)",           [30, 160, 160, 160, 220]),
    ("304 revalidated\n(stale, unchanged)", [0,  0,   0,   160, 0]),
    ("FRESH hit\n(within max-age)",      [0,  0,   0,   0,   0]),
]


def fig1():
    fig, ax = plt.subplots(figsize=(9.6, 4.6))
    y = list(range(len(SCENARIOS)))[::-1]  # top-to-bottom

    for yi, (_, vals) in zip(y, SCENARIOS):
        left = 0.0
        total = sum(vals)
        for v, c in zip(vals, COLORS):
            if v > 0:
                ax.barh(yi, v, left=left, color=c, edgecolor="white", height=0.5)
            left += v
        if total > 0:
            ax.text(total + 12, yi, f"{total:.0f} ms", va="center", ha="left",
                    fontsize=11, fontweight="bold", color="#222")
        else:
            # the fresh hit: draw a marker at 0 so the "no network" case is visible
            ax.text(12, yi, "~0 ms  —  no network", va="center", ha="left",
                    fontsize=11, fontweight="bold", color="#1e8449")

    ax.set_yticks(y)
    ax.set_yticklabels([s[0] for s in SCENARIOS], fontsize=10)
    ax.set_xlabel("time to usable response (ms)  —  each setup segment is one round-trip",
                  fontsize=10)
    ax.set_xlim(0, 820)
    ax.set_title("Caching's two wins stack: revalidation drops the payload, freshness drops the network",
                 fontsize=11.5, fontweight="bold", pad=12)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="x", color="#ddd", linewidth=0.8)
    ax.set_axisbelow(True)

    legend = [Patch(facecolor=c, label=p) for c, p in zip(COLORS, PHASES)]
    ax.legend(handles=legend, loc="lower right", fontsize=9, frameon=False,
              title="cost of the fetch")

    fig.tight_layout()
    fig.savefig(OUT, format="svg", bbox_inches="tight")
    print("wrote", OUT)


if __name__ == "__main__":
    fig1()
