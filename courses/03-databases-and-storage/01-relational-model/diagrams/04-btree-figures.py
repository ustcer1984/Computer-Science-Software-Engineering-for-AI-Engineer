#!/usr/bin/env python3
"""Figures for M03 Ch1 §4 — the B-tree index.

All measurements: PostgreSQL 18.6 in Docker on a laptop, 2026-10-16, default
settings (shared_buffers = 128 MB, so a 10,000,000-row index does NOT fit in
PostgreSQL's own cache), max_wal_size raised to 8 GB so checkpoints did not
interrupt the load. Raw data in 04-btree-data/.

fig1: how tall does a B-tree get? The staircase is computed from the fan-out
      MEASURED on the 10,000,000-row bigint primary key (pgstatindex): 27,323
      leaf pages under 97 internal pages, i.e. about 366 keys per leaf page and
      about 282 children per internal page. Height h holds about
      366 * 282^(h-1) keys. The two measured points are real indexes: the
      1,000-row primary key (2 levels) and the 10,000,000-row one (3 levels).

fig3 (insert-batches.csv, index-shape.csv): 10,000,000 rows inserted into a
      table whose primary key is a sequential bigint, a uuidv7() or a uuidv4(),
      in 20 committed batches of 500,000. Left: time per batch. Right: the
      resulting index - size and leaf density.

Run:  .venv/bin/python 04-btree-figures.py
The doc's Figure 2 is a Mermaid diagram, so the files here are fig1 and fig3.
"""
import csv
import math
import os
from collections import defaultdict
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "04-btree-data")
INK, GREY = "#1b2430", "#64748b"
COL = {"big": "#047857", "v7": "#1d4ed8", "v4": "#c2410c"}
LAB = {"big": "bigint, sequential", "v7": "UUID version 7 (time-ordered)", "v4": "UUID version 4 (random)"}

# =============================================================================
# fig1 — height staircase
# =============================================================================
LEAF, FAN = 27323, 97
keys_per_leaf = 10_000_000 / LEAF          # ~366
fanout = LEAF / FAN                        # ~282
caps = [keys_per_leaf * fanout ** (h - 1) for h in range(1, 7)]
fig, ax = plt.subplots(figsize=(11.2, 5.0))
xs, ys = [1], [1]
for h, c in enumerate(caps, start=1):
    xs += [c, c]
    ys += [h, h + 1]
ax.plot(xs[:-1], ys[:-1], color=INK, lw=2.2, drawstyle="default")
nice = ["~366", "~103,000", "~29 million", "~8.2 billion", "~2.3 trillion"]
for h, (c, t) in enumerate(zip(caps[:5], nice), start=1):
    ax.annotate(f"{h} level{'s hold' if h > 1 else ' holds'} up to\n{t} keys", xy=(c, h), xytext=(c / 60, h + 0.32),
                fontsize=8.6, color=GREY)
ax.scatter([1000, 10_000_000], [2, 3], s=110, color="#c2410c", zorder=5, label="measured indexes (pageinspect / pgstatindex)")
ax.annotate("1,000 rows: root + 3 leaves", xy=(1000, 2), xytext=(3, 2.55), fontsize=9, color="#c2410c",
            arrowprops=dict(arrowstyle="->", color="#c2410c", lw=0.9))
ax.annotate("10,000,000 rows: 3 levels,\n97 internal pages, 27,323 leaves", xy=(1e7, 3), xytext=(30, 3.45),
            fontsize=9, color="#c2410c", arrowprops=dict(arrowstyle="->", color="#c2410c", lw=0.9))
for label, n in [("world population", 8.2e9), ("1 trillion", 1e12)]:
    ax.axvline(n, color=GREY, lw=0.8, ls=":")
    ax.text(n * 1.15, 1.15, label, fontsize=8.5, color=GREY, rotation=90, va="bottom")
ax.set_xscale("log")
ax.set_xlim(1, 1e15)
ax.set_ylim(0.8, 6.6)
ax.set_xlabel("keys in the index (log scale)")
ax.set_ylabel("levels from root to leaf")
ax.set_yticks(range(1, 7))
ax.grid(alpha=0.25, which="major")
ax.legend(loc="upper left", fontsize=9)
ax.set_title("A B-tree on 8-byte keys stays shallow: each level multiplies capacity by about 282\n"
             f"(fan-out measured on a 10,000,000-row PostgreSQL 18 primary key: ~{keys_per_leaf:.0f} keys per leaf, "
             f"~{fanout:.0f} children per internal page)", fontsize=11, color=INK)
fig.tight_layout()
out = os.path.join(HERE, "04-btree-fig1.svg")
fig.savefig(out, format="svg", bbox_inches="tight")
print("wrote", out, [f"{c:.3g}" for c in caps])

# =============================================================================
# fig3 — insert pattern
# =============================================================================
rows = list(csv.DictReader(open(os.path.join(DATA, "insert-batches.csv"))))
series = defaultdict(list)
for r in rows:
    series[r["key_type"]].append((int(r["batch"]), float(r["ms"])))
shape = {r["key_type"]: r for r in csv.DictReader(open(os.path.join(DATA, "index-shape.csv")))}
fig, (a1, a2) = plt.subplots(1, 2, figsize=(13.2, 5.2), gridspec_kw={"width_ratios": [1.5, 1]})
for k in ["big", "v7", "v4"]:
    pts = sorted(series[k])
    a1.plot([p[0] * 0.5 for p in pts], [p[1] / 1000 for p in pts], marker="o", ms=4, lw=2.3, color=COL[k], label=LAB[k])
a1.set_xlabel("rows in the table after the batch (millions)")
a1.set_ylabel("seconds to insert the next 500,000 rows")
a1.set_ylim(0, 4.2)
a1.grid(alpha=0.25)
a1.legend(fontsize=9, loc="center left", bbox_to_anchor=(0.0, 0.62))
a1.annotate("random keys: every insert lands on a random leaf,\nso the whole index is the working set - and it\n"
            "outgrows the 128 MB cache a few million rows in", xy=(9.45, 3.84), xytext=(3.9, 3.55), fontsize=8.8,
            color=COL["v4"], arrowprops=dict(arrowstyle="->", color=COL["v4"], lw=0.9))
a1.set_title("Insert speed as the table grows (total: 8.6 s, 13.9 s, 44.5 s)", fontsize=10.5, color=INK)
names = ["bigint\nsequential", "UUID v7", "UUID v4", "UUID v4\nafter REINDEX"]
keys = ["bigint sequential", "uuid v7", "uuid v4", "uuid v4 after REINDEX"]
cols = [COL["big"], COL["v7"], COL["v4"], "#fdba74"]
sizes = [float(shape[k]["index_mb"]) for k in keys]
bars = a2.bar(names, sizes, color=cols)
for b, k in zip(bars, keys):
    a2.text(b.get_x() + b.get_width() / 2, b.get_height() + 6,
            f"{shape[k]['index_mb']} MB\nleaves {float(shape[k]['avg_leaf_density_pct']):.0f}% full",
            ha="center", fontsize=8.8, color=INK)
a2.set_ylim(0, 470)
a2.set_ylabel("primary-key index size after 10,000,000 rows (MB)")
a2.set_title("The index it leaves behind", fontsize=10.5, color=INK)
a2.grid(axis="y", alpha=0.25)
fig.suptitle("The same 10,000,000 inserts, three kinds of primary key — PostgreSQL 18, measured 2026-10-16",
             fontsize=12, color=INK)
fig.tight_layout()
out = os.path.join(HERE, "04-btree-fig3.svg")
fig.savefig(out, format="svg", bbox_inches="tight")
print("wrote", out)
