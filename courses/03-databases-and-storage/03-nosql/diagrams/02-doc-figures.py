#!/usr/bin/env python3
"""Figures for M03 Ch3 §2 — document stores.

All measurements: MongoDB 8.2.12 (`mongo:8.2`, single-node replica set, WiredTiger cache 1 GB) and PostgreSQL 18.6
(`postgres:18`, shared_buffers 1 GB) in Docker on a laptop, 2026-11-19; Python clients pymongo 4.20.0, psycopg 3.3.9.
Raw data and method in 02-doc-data/.

02-doc-fig2.svg (update-bench.csv): bytes written to change one counter, by document size.
02-doc-fig3.svg (query-out.txt): five questions, p50 latency per store and access path.

Run:  python 02-doc-figures.py
"""
import csv
import os
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "02-doc-data")
INK, GREY = "#1b2430", "#64748b"
GREEN, BLUE, ORANGE, RED, PURPLE, TEAL = "#047857", "#1d4ed8", "#c2410c", "#b91c1c", "#7c3aed", "#0f766e"
plt.rcParams.update({"font.size": 10.5, "axes.edgecolor": GREY, "axes.labelcolor": INK, "xtick.color": INK,
                     "ytick.color": INK, "axes.spines.top": False, "axes.spines.right": False,
                     "svg.fonttype": "path"})


def save(fig, name):
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, name), format="svg", bbox_inches="tight")
    plt.close(fig)


def human(v):
    return f"{v / 1024:.0f} KB" if v >= 10_240 else (f"{v / 1024:.1f} KB" if v >= 1024 else f"{v:.0f} B")


# ---------------------------------------------------------------- Figure 2: update cost by document size
rows = list(csv.DictReader(open(os.path.join(DATA, "update-bench.csv"))))
sizes = sorted({int(r["doc_bytes"]) for r in rows})
series = [("MongoDB $inc", RED, "MongoDB: $inc on a field inside the document"),
          ("PostgreSQL jsonb_set inside doc", BLUE, "PostgreSQL: jsonb_set on a field inside the jsonb"),
          ("PostgreSQL counter in own column", GREEN, "PostgreSQL: counter in its own column beside the jsonb")]
fig, ax = plt.subplots(1, 2, figsize=(13, 4.6), sharey=True)
w = 0.26
for p, (col, title) in enumerate((("log_bytes_per_update", "(a) log written at commit: journal / WAL"),
                                  ("data_file_bytes_per_update", "(b) data files written at the next checkpoint"))):
    for k, (store, colr, lab) in enumerate(series):
        vals = [max(1, float(next(r[col] for r in rows if r["store"] == store and int(r["doc_bytes"]) == s)))
                for s in sizes]
        bars = ax[p].bar([i + (k - 1) * w for i in range(len(sizes))], vals, w, color=colr, label=lab)
        for b, v in zip(bars, vals):
            ax[p].text(b.get_x() + b.get_width() / 2, v * 1.15, human(v), ha="center", fontsize=8, color=INK)
    ax[p].set_yscale("log"); ax[p].set_ylim(8, 2_000_000)
    ax[p].set_xticks(range(len(sizes))); ax[p].set_xticklabels([f"{s // 1024} KB document" for s in sizes])
    ax[p].set_title(title, loc="left", color=INK, fontsize=9.5)
ax[0].set_ylabel("bytes written per update (log scale)")
ax[0].legend(frameon=False, fontsize=8.5, loc="upper left")
save(fig, "02-doc-fig2.svg")

# ---------------------------------------------------------------- Figure 3: five questions
txt = open(os.path.join(DATA, "query-out.txt")).read()
lat = {}
q = None
for line in txt.splitlines():
    m = re.match(r"(Q\d) ", line)
    if m:
        q = m.group(1)
        continue
    m = re.match(r"\s+(Mongo|PG)\s+(.+?)\s+p50\s+([\d.]+) ms", line)
    if m:
        lat[(q, m.group(1), m.group(2).strip())] = float(m.group(3))
qs = [("Q1", "one item\nby id"), ("Q2", "brand AND\ncolour"), ("Q3", "has two\ntags"), ("Q4", "price in a\nrange"),
      ("Q5", "two fields with\nno targeted index")]
best = {  # the access path each store would use if you designed for the question
    "Q1": ("_id", "jsonb, primary key", "columns, primary key"),
    "Q2": ("compound index", "jsonb, expression index", "columns, B-tree"),
    "Q3": ("multikey index, $all", "jsonb, GIN containment @>", "columns, GIN on text[] @>"),
    "Q4": ("price index", "jsonb, expression index", "columns, B-tree"),
    "Q5": ("no index -> collection scan", "jsonb, GIN containment @>", "columns (no index)"),
}
fig, ax = plt.subplots(figsize=(12, 4.8))
w = 0.26
for k, (store, colr, lab, idx) in enumerate((("Mongo", RED, "MongoDB", 0),
                                             ("PG", BLUE, "PostgreSQL jsonb", 1),
                                             ("PG", GREEN, "PostgreSQL plain columns", 2))):
    vals = [lat[(qq, store, best[qq][idx])] for qq, _ in qs]
    bars = ax.bar([i + (k - 1) * w for i in range(len(qs))], vals, w, color=colr, label=lab)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v * 1.12, f"{v:.2f}" if v < 10 else f"{v:.0f}", ha="center",
                fontsize=8, color=INK)
ax.set_yscale("log"); ax.set_ylim(0.02, 400)
ax.set_xticks(range(len(qs))); ax.set_xticklabels([l for _, l in qs])
ax.set_ylabel("p50 latency, ms (log scale)")
ax.legend(frameon=False, fontsize=9, loc="upper left")
save(fig, "02-doc-fig3.svg")
print("ok")
