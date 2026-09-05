#!/usr/bin/env python3
"""Figures for M02 Ch3 §2 — TLS in operation.

fig1: what each "TLS is slow" fix actually buys, measured in ROUND-TRIPS on the
same cross-ocean path used by Ch1 §1, Ch2 §2 and Ch3 §1 (~160 ms RTT), so all
four figures are directly comparable.

Bars are "time until the client can send the first byte of application data",
which is the number that shows up as time-to-first-byte in production:

  - COLD, full handshake        — DNS + TCP + TLS 1.3   (the Ch3 §1 budget)
  - SESSION RESUMPTION          — still TCP + 1-RTT TLS: saves CPU, NOT a trip
  - RESUMPTION + 0-RTT          — early data rides with the ClientHello
  - QUIC / HTTP/3, first visit  — transport and TLS handshakes are the SAME trip
  - QUIC / HTTP/3, 0-RTT        — nothing before the data
  - WARM CONNECTION REUSE       — the connection is already open

The point of the figure is the second bar: TLS 1.3 session resumption is widely
believed to remove a round-trip and it does not. Only 0-RTT, QUIC, and keeping
the connection open remove round-trips.

Run:  python3 02-tls-in-operation-figures.py   (or the repo .venv/bin/python)
Outputs SVG next to this script (committed alongside the doc).
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "02-tls-in-operation-fig1.svg")

RTT = 160  # ms, cross-ocean — the same number as Ch1 §1 / Ch2 §2 / Ch3 §1

PHASES = ["DNS lookup", "TCP handshake", "TLS 1.3 handshake", "QUIC handshake (transport + TLS together)"]
COLORS = ["#b9770e", "#c0392b", "#8e44ad", "#16a085"]

#            label                                    DNS  TCP  TLS  QUIC
SCENARIOS = [
    ("COLD — full handshake\n(first visit, HTTP/2 over TCP)",        [30, RTT, RTT, 0]),
    ("SESSION RESUMPTION\n(TLS 1.3 PSK, 1-RTT)",                     [0,  RTT, RTT, 0]),
    ("RESUMPTION + 0-RTT early data\n(replay risk — idempotent only)", [0, RTT, 0,   0]),
    ("QUIC / HTTP-3 — first visit\n(one combined handshake)",         [30, 0,   0,   RTT]),
    ("QUIC / HTTP-3 — 0-RTT resumption",                              [0,  0,   0,   0]),
    ("WARM CONNECTION REUSE\n(the connection is already open)",       [0,  0,   0,   0]),
]

fig, ax = plt.subplots(figsize=(11, 5.8))
ys = range(len(SCENARIOS))

for i, (_, parts) in enumerate(SCENARIOS):
    left = 0
    for val, color in zip(parts, COLORS):
        if val:
            ax.barh(i, val, left=left, color=color, edgecolor="white", height=0.62)
            left += val
    total = sum(parts)
    ax.text(total + 8, i, f"{total} ms" if total else "0 ms — no setup at all",
            va="center", fontsize=10.5,
            fontweight="bold" if total == 0 else "normal",
            color="#1e8449" if total == 0 else "#222")

ax.set_yticks(list(ys))
ax.set_yticklabels([s for s, _ in SCENARIOS], fontsize=10)
ax.set_ylim(len(SCENARIOS) - 0.35, -0.65)
ax.set_xlabel(f"milliseconds before the first byte of application data can be sent  "
              f"(~{RTT} ms round-trip)", fontsize=10.5)
ax.set_title("What each TLS performance fix actually buys\n"
             "Session resumption saves CPU, not a round-trip —\n"
             "only 0-RTT, QUIC and connection reuse remove trips",
             fontsize=12, fontweight="bold", pad=12)
ax.set_xlim(0, 430)
ax.grid(axis="x", linestyle=":", alpha=0.5)
ax.set_axisbelow(True)
for side in ("top", "right", "left"):
    ax.spines[side].set_visible(False)

ax.legend(handles=[Patch(facecolor=c, label=p) for p, c in zip(PHASES, COLORS)],
          loc="center right", bbox_to_anchor=(1.0, 0.42), fontsize=9.5, frameon=True)

fig.tight_layout()
fig.savefig(OUT)
print(f"wrote {OUT}")
