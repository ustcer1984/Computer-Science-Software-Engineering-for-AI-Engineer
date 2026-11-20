#!/usr/bin/env python3
"""Figures for M03 Ch3 §3 — graph databases.

All measurements: Neo4j 2026.10.2 Community (`neo4j:community`, page cache 1 GB, heap 1 GB, store format
record-aligned-1.1) and PostgreSQL 18.6 (`postgres:18`, shared_buffers 1 GB) in Docker on a laptop, 2026-11-20;
Python clients neo4j 6.4.1, psycopg 3.3.9. Raw data and method in 03-graph-data/.

03-graph-fig2.svg (reach-bench.csv): k-hop reach, users reached and p50 latency per method.

Run:  python 03-graph-figures.py
"""
import csv
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "03-graph-data")
INK, GREY = "#1b2430", "#64748b"
GREEN, BLUE, ORANGE, RED, PURPLE = "#047857", "#1d4ed8", "#c2410c", "#b91c1c", "#7c3aed"
plt.rcParams.update({"font.size": 10.5, "axes.edgecolor": GREY, "axes.labelcolor": INK, "xtick.color": INK,
                     "ytick.color": INK, "axes.spines.top": False, "axes.spines.right": False,
                     "svg.fonttype": "path"})


def save(fig, name):
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, name), format="svg", bbox_inches="tight")
    plt.close(fig)


rows = list(csv.DictReader(open(os.path.join(DATA, "reach-bench.csv"))))
depths = sorted({int(r["depth"]) for r in rows})


def series(method, col="p50_ms"):
    return [float(next(r[col] for r in rows if r["method"] == method and int(r["depth"]) == k)) for k in depths]


fig, ax = plt.subplots(1, 2, figsize=(13, 4.8))
reached = series("neo4j_bfs", "reached_median")
ax[0].bar(depths, reached, color=GREY, width=0.6)
for k, v in zip(depths, reached):
    ax[0].text(k, v * 1.25, f"{v:,.0f}", ha="center", fontsize=9, color=INK)
ax[0].set_yscale("log"); ax[0].set_ylim(1, 5_000_000)
ax[0].set_xlabel("hops k"); ax[0].set_ylabel("distinct users reached (median of 20 starts, log)")
ax[0].set_title("(a) the answer grows 6–10× per hop, out of 1,000,000 users", loc="left", fontsize=9.5, color=INK)

for method, colr, lab in (("neo4j_bfs", RED, "Neo4j: variable-length pattern, count(DISTINCT b) → pruning BFS"),
                          ("pg_cte", BLUE, "PostgreSQL: recursive CTE, UNION over (id, depth)"),
                          ("pg_bfs", PURPLE, "PostgreSQL: PL/pgSQL BFS with a visited table"),
                          ("csr", GREEN, "two numpy arrays in the application process (CSR)")):
    ys = series(method)
    ax[1].plot(depths, ys, "o-", color=colr, label=lab, lw=2)
    ax[1].text(depths[-1] + 0.12, ys[-1], f"{ys[-1]:.0f} ms", va="center", fontsize=9, color=colr)
ax[1].set_yscale("log"); ax[1].set_xlim(0.7, 6.9)
ax[1].set_xlabel("hops k"); ax[1].set_ylabel("p50 latency, ms (log)")
ax[1].set_title("(b) time follows the answer's size; the engines differ by a small factor",
                loc="left", fontsize=9.5, color=INK)
ax[1].legend(frameon=False, fontsize=8.3, loc="upper left")
save(fig, "03-graph-fig2.svg")
print("wrote 03-graph-fig2.svg")
