#!/usr/bin/env python3
"""Figure for M03 Ch2 §3 §12a — the cost of COMMIT does not grow with the transaction.

Data: 03-mvcc-data/applied-commit-out.txt (written by `applied.py <dsn> commit`; PostgreSQL 18.6, 2026-11-09).
Figure 7: time to write N rows vs time to COMMIT them, and how much of the table was still in shared_buffers at COMMIT.

Run:  python 03-mvcc-applied-figures.py
"""
import os
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
INK, GREY, BLUE, ORANGE = "#1b2430", "#64748b", "#1d4ed8", "#c2410c"

rows = []
for line in open(os.path.join(HERE, "03-mvcc-data", "applied-commit-out.txt")):
    parts = line.split()
    if parts and parts[0].replace(",", "").isdigit():
        n = int(parts[0].replace(",", ""))
        pct = re.search(r"\(\s*([\d.]+)%\)", line).group(1)
        rows.append((n, float(parts[1]) * 1000, float(parts[2]), pct))

labels = [f"{n:,}" for n, *_ in rows]
x = range(len(rows))
fig, ax = plt.subplots(figsize=(8.6, 4.4))
w = 0.38
ins = [max(r[1], 0.05) for r in rows]
com = [r[2] for r in rows]
ax.bar([i - w / 2 for i in x], ins, w, color=BLUE, label="writing the rows (INSERT, last of 5 runs)")
ax.bar([i + w / 2 for i in x], com, w, color=ORANGE, label="COMMIT (median of 5)")
ax.set_yscale("log")
ax.set_ylim(0.05, 60000)
ax.set_xticks(list(x), labels)
ax.set_xlabel("rows written by the transaction", color=INK)
ax.set_ylabel("time, ms (log scale)", color=INK)
for i, r in enumerate(rows):
    ax.text(i + w / 2, com[i] * 1.35, f"{com[i]:.1f}", ha="center", va="bottom", fontsize=8.5, color=ORANGE)
    ax.text(i - w / 2, ins[i] * 1.35, f"{r[1]:,.0f}" if r[1] >= 1 else "<1", ha="center", va="bottom",
            fontsize=8.5, color=BLUE)
    ax.text(i, 50000, f"{float(r[3]):.0f}% of table\nin buffers\nat COMMIT", ha="center", va="top", fontsize=8, color=GREY)
ax.legend(loc="upper left", bbox_to_anchor=(0, 0.86), frameon=False, fontsize=9)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.tick_params(colors=INK)
fig.tight_layout()
fig.savefig(os.path.join(HERE, "03-mvcc-fig7.svg"))
if os.environ.get("PNG"): fig.savefig(os.environ["PNG"], dpi=110)
print("wrote 03-mvcc-fig7.svg")
