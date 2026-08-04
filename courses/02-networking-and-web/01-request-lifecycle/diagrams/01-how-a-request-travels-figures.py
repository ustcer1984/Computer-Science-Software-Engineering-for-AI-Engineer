#!/usr/bin/env python3
"""Figures for M02 Ch1 §1 — How a request travels.

fig1: latency budget — time-to-first-byte broken into DNS / TCP / TLS / HTTP
round-trips, for three scenarios, showing that on a long path the handshakes
dominate a first request and connection reuse removes three of the four RTTs.

Run:  python3 01-how-a-request-travels-figures.py
Outputs SVG(s) next to this script (committed alongside the doc).
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

HERE = os.path.dirname(os.path.abspath(__file__))
BASENAME = "01-how-a-request-travels"

# phases (ms). HTTP = the round-trip that actually carries application data.
PHASES = ["DNS", "TCP handshake", "TLS 1.3 handshake", "HTTP (to first byte)"]
COLORS = ["#b9770e", "#c0392b", "#8e44ad", "#1e8449"]  # 3 "setup" hues + green = the useful work

# scenario -> per-phase milliseconds
SCENARIOS = [
    ("Same-region\ncold", [5, 2, 2, 3]),
    ("Cross-ocean\ncold", [30, 160, 160, 170]),
    ("Cross-ocean\nwarm (keep-alive\n+ DNS cached)", [0, 0, 0, 160]),
]


def fig1():
    fig, ax = plt.subplots(figsize=(9.2, 4.4))
    labels = [s[0] for s in SCENARIOS]
    y = list(range(len(SCENARIOS)))[::-1]  # top-to-bottom

    for yi, (_, vals) in zip(y, SCENARIOS):
        left = 0.0
        total = sum(vals)
        for v, c in zip(vals, COLORS):
            if v > 0:
                ax.barh(yi, v, left=left, color=c, edgecolor="white", height=0.55)
            left += v
        # total label at the end of each bar
        ax.text(total + 8, yi, f"{total:.0f} ms", va="center", ha="left",
                fontsize=11, fontweight="bold", color="#222")

    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=10)
    ax.set_xlabel("time to first byte (ms)  —  each segment is one round-trip", fontsize=10)
    ax.set_xlim(0, 620)
    ax.set_title("A first HTTPS request is mostly handshakes; reuse removes three of the four round-trips",
                 fontsize=11.5, fontweight="bold", pad=12)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="x", color="#ddd", linewidth=0.8)
    ax.set_axisbelow(True)

    legend = [Patch(facecolor=c, label=p) for c, p in zip(COLORS, PHASES)]
    ax.legend(handles=legend, loc="lower right", fontsize=9, frameon=False,
              title="request phase (green = the actual data)")

    # annotation: the warm bar keeps only the data round-trip
    ax.annotate("only the data round-trip survives",
                xy=(160, y[2]), xytext=(250, y[2] - 0.05),
                fontsize=9, color="#1e8449",
                arrowprops=dict(arrowstyle="->", color="#1e8449", lw=1.2))

    fig.tight_layout()
    out = os.path.join(HERE, f"{BASENAME}-fig1.svg")
    fig.savefig(out, format="svg", bbox_inches="tight")
    plt.close(fig)
    print("wrote", out)


if __name__ == "__main__":
    fig1()
