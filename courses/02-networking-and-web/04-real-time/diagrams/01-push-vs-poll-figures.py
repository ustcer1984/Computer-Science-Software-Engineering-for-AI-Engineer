#!/usr/bin/env python3
"""Figures for M02 Ch4 §1 — pushing data to the client.

fig1: the polling trade-off, drawn as the actual curves rather than described.

For short polling with N clients and poll period T (seconds):

    request rate  R(T) = N / T                      [requests per second]
    mean staleness S(T) = T / 2                     [seconds, uniform arrivals]

Both are exact for a fixed-interval poller and independent event arrivals, and
they move in OPPOSITE directions, so there is no interval that is good at both.
The left panel plots them together on a log-x axis; the right panel plots them
AGAINST EACH OTHER, which is the shape that matters: a hyperbola, R x S = N/2.
Every short-polling design is a point on that curve. Push (SSE/WebSocket) is
not on the curve at all -- it is the origin-ish point marked in the right panel,
because a pushed update costs no repeat request and adds no waiting.

N = 10,000 concurrent clients throughout (a mid-size dashboard / chat app).

Run:  .venv/bin/python 01-push-vs-poll-figures.py
Outputs SVG next to this script (committed alongside the doc).
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

N = 10_000                      # concurrent clients
T = np.logspace(-0.3, 2.7, 400)  # poll period: 0.5 s .. 500 s
R = N / T                        # requests per second
S = T / 2                        # mean staleness, seconds

HERE = os.path.dirname(os.path.abspath(__file__))
INK, ACC1, ACC2, ACC3 = "#1b2430", "#c2410c", "#1d4ed8", "#047857"

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.6, 5.0))

# ---- left panel: both quantities vs the one knob you control -----------------
ax1.set_xscale("log"); ax1.set_yscale("log")
ax1.plot(T, R, color=ACC1, lw=2.6, label="request rate  $R = N/T$  (req/s)")
ax1.set_xlabel("poll period  $T$  (seconds, log scale)")
ax1.set_ylabel("requests per second", color=ACC1)
ax1.tick_params(axis="y", labelcolor=ACC1)

ax1b = ax1.twinx()
ax1b.set_yscale("log")
ax1b.plot(T, S, color=ACC2, lw=2.6, ls="--",
          label="mean staleness  $S = T/2$  (s)")
ax1b.set_ylabel("mean staleness (seconds)", color=ACC2)
ax1b.tick_params(axis="y", labelcolor=ACC2)

for t, note in [(1.0, "1 s poll\n10,000 req/s\n0.5 s stale"),
                (60.0, "60 s poll\n167 req/s\n30 s stale")]:
    ax1.axvline(t, color="#94a3b8", lw=1.0, ls=":")
    ax1.annotate(note, xy=(t, N / t), xytext=(t * 1.25, N / t * 0.9),
                 fontsize=8.5, color=INK, va="top")

ax1.set_title(f"One knob, two costs — short polling, N = {N:,} clients",
              fontsize=11, color=INK)
ax1.grid(alpha=0.25, which="both")
h1, l1 = ax1.get_legend_handles_labels()
h2, l2 = ax1b.get_legend_handles_labels()
ax1.legend(h1 + h2, l1 + l2, fontsize=9, loc="lower left")

# ---- right panel: the trade-off itself ---------------------------------------
ax2.set_xscale("log"); ax2.set_yscale("log")
ax2.plot(S, R, color=ACC3, lw=2.8)
ax2.set_xlabel("mean staleness (seconds)")
ax2.set_ylabel("requests per second")
ax2.set_title("The trade-off is a hyperbola:  $R \\times S = N/2$",
              fontsize=11, color=INK)
ax2.grid(alpha=0.25, which="both")

for t, lab in [(1.0, "$T$ = 1 s"), (10.0, "$T$ = 10 s"), (60.0, "$T$ = 60 s")]:
    ax2.plot(t / 2, N / t, "o", color=ACC3, ms=7)
    ax2.annotate(lab, xy=(t / 2, N / t), xytext=(6, 8),
                 textcoords="offset points", fontsize=9, color=INK)

# push is off the curve
ax2.plot(0.35, 2.0, "*", color=ACC1, ms=20, zorder=5)
ax2.annotate("push (SSE / WebSocket):\nnot on this curve —\nno repeat requests,\nno waiting.\nThe cost moves to\nOPEN CONNECTIONS",
             xy=(0.35, 2.0), xytext=(0.55, 4.0), fontsize=9, color=ACC1,
             arrowprops=dict(arrowstyle="->", color=ACC1, lw=1.2))

fig.suptitle("Why polling has no good setting — and what push actually changes",
             fontsize=13, color=INK, y=0.99)
fig.tight_layout(rect=(0, 0, 1, 0.95))
out = os.path.join(HERE, "01-push-vs-poll-fig1.svg")
fig.savefig(out, format="svg", bbox_inches="tight")
print("wrote", out)
