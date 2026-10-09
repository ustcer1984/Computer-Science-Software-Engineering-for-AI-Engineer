#!/usr/bin/env python3
"""Figures for M03 Ch1 §3 — how a query is planned and executed.

All numbers are MEASURED, not estimated: PostgreSQL 18.6 in Docker on a
22-core / 62 GB laptop, 2026-10-09, shared_buffers = 2 GB (so every table was
memory-resident), max_parallel_workers_per_gather = 0 (serial plans, so the
three methods are compared like for like), every other setting at its default
(random_page_cost = 4, work_mem = 4 MB, JIT on). Each point is the median of
3-7 runs. The raw data is in 03-query-planning-data/.

fig3 (scan-sweep.csv): a 5,000,000-row table (about 600 MB) with two indexed integer
      columns. `r` is random, so its physical order has correlation 0 with the
      index; `c` = id / 5, so rows sit on disk in index order (correlation 1).
      Query: SELECT sum(length(pad)) FROM t WHERE <col> < k, for a sweep of
      selectivities, forcing each access method in turn with enable_* = off,
      and recording which one the planner picks unforced.

fig4 (join-sweep.csv): outer table `o` (1,000,000 rows, random foreign ids)
      joined to `t` (5,000,000 rows, primary key on id). Query:
      SELECT sum(length(t.pad)) FROM o JOIN t ON t.id = o.tid WHERE o.n <= k,
      forcing nested loop / hash / merge join in turn.

Run:  .venv/bin/python 03-query-planning-figures.py
Outputs SVGs next to this script (committed alongside the doc). The doc's
Figures 1 and 2 are Mermaid diagrams, so the files here are fig3 and fig4.
"""
import csv
import os
from collections import defaultdict
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "03-query-planning-data")
INK, GREY = "#1b2430", "#64748b"
COL = {"seq": "#c2410c", "index": "#1d4ed8", "bitmap": "#047857",
       "nestloop": "#1d4ed8", "hashjoin": "#c2410c", "mergejoin": "#7c3aed"}
NODE = {"Seq Scan": "seq", "Index Scan": "index", "Bitmap Heap Scan": "bitmap",
        "Nested Loop": "nestloop", "Hash Join": "hashjoin", "Merge Join": "mergejoin"}

# =============================================================================
# fig3 — access-path crossover
# =============================================================================
rows = list(csv.DictReader(open(os.path.join(DATA, "scan-sweep.csv"))))
series = defaultdict(lambda: defaultdict(list))
choice = defaultdict(dict)
for r in rows:
    f = float(r["fraction"]) * 100
    series[r["column"]][r["method"]].append((f, float(r["median_ms"])))
    choice[r["column"]][f] = NODE[r["planner_choice"]]

label = {"seq": "sequential scan", "index": "index scan", "bitmap": "bitmap heap scan"}
fig, axes = plt.subplots(1, 2, figsize=(13.2, 5.4), sharey=True)
titles = {"r": "Column in RANDOM physical order (correlation 0)",
          "c": "Column in INDEX order on disk (correlation 1)"}
for ax, col in zip(axes, ["r", "c"]):
    for m in ["seq", "index", "bitmap"]:
        pts = sorted(series[col][m])
        ax.plot([p[0] for p in pts], [max(p[1], 0.01) for p in pts], marker="o", ms=4,
                lw=2.2, color=COL[m], label=label[m])
    # ring the method the planner actually chose at each point
    for f, m in choice[col].items():
        y = dict(series[col][m])[f]
        ax.scatter([f], [max(y, 0.01)], s=170, facecolors="none", edgecolors=INK, lw=1.6, zorder=5)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("share of the 5,000,000 rows the query selects (%)")
    ax.set_title(titles[col], fontsize=10.5, color=INK)
    ax.grid(alpha=0.25, which="both")
axes[0].set_ylabel("median time, ms (log scale)")
axes[0].annotate("index scan stops paying\nbetween 3% and 10% of rows", xy=(3, 124), xytext=(0.004, 400),
                 fontsize=9, color=COL["index"], arrowprops=dict(arrowstyle="->", color=COL["index"], lw=0.9))
axes[0].annotate("at 10% the planner picks bitmap\n(220 ms) over the scan (196 ms)", xy=(10, 220),
                 xytext=(0.002, 2000), fontsize=9, color=INK, arrowprops=dict(arrowstyle="->", color=INK, lw=0.9))
axes[1].annotate("same query, ordered data:\nthe index still wins at 30%", xy=(30, 245), xytext=(0.003, 1200),
                 fontsize=9, color=COL["index"], arrowprops=dict(arrowstyle="->", color=COL["index"], lw=0.9))
axes[0].scatter([], [], s=170, facecolors="none", edgecolors=INK, lw=1.6, label="the planner's own choice")
axes[0].legend(fontsize=9, loc="lower right")
fig.suptitle("When does an index help? It depends on how many rows you want, and on how they lie on disk",
             fontsize=12.5, color=INK)
fig.text(0.5, -0.01, "PostgreSQL 18, 5,000,000 rows (about 600 MB) held in memory, serial plans, default cost settings; "
         "measured 2026-10-09.", ha="center", fontsize=9, color=GREY)
fig.tight_layout()
out = os.path.join(HERE, "03-query-planning-fig3.svg")
fig.savefig(out, format="svg", bbox_inches="tight")
print("wrote", out)

# =============================================================================
# fig4 — join algorithms
# =============================================================================
rows = list(csv.DictReader(open(os.path.join(DATA, "join-sweep.csv"))))
js = defaultdict(list)
jchoice = {}
for r in rows:
    k = int(r["outer_rows"])
    js[r["method"]].append((k, float(r["median_ms"])))
    jchoice[k] = NODE[r["planner_choice"]]
jl = {"nestloop": "nested loop (index lookup per outer row)", "hashjoin": "hash join",
      "mergejoin": "merge join (sort, then walk both in order)"}
fig, ax = plt.subplots(figsize=(11.6, 5.6))
for m in ["nestloop", "hashjoin", "mergejoin"]:
    pts = sorted(js[m])
    ax.plot([p[0] for p in pts], [p[1] for p in pts], marker="o", ms=4.5, lw=2.3, color=COL[m], label=jl[m])
for k, m in jchoice.items():
    ax.scatter([k], [dict(js[m])[k]], s=190, facecolors="none", edgecolors=INK, lw=1.6, zorder=5)
ax.scatter([], [], s=190, facecolors="none", edgecolors=INK, lw=1.6, label="the planner's own choice")
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlabel("rows on the outer side of the join")
ax.set_ylabel("median time, ms (log scale)")
ax.grid(alpha=0.25, which="both")
ax.annotate("100,000 rows: nested loop 249 ms,\nbut the planner picks hash (295 ms)", xy=(100000, 295),
            xytext=(300, 1100), fontsize=9, color=INK, arrowprops=dict(arrowstyle="->", color=INK, lw=0.9))
ax.annotate("1,000,000 rows: merge 740 ms,\nbut the planner picks hash (1,347 ms)", xy=(1000000, 1347),
            xytext=(1500, 3000), fontsize=9, color=INK, arrowprops=dict(arrowstyle="->", color=INK, lw=0.9))
ax.legend(fontsize=9, loc="lower right")
ax.set_ylim(0.02, 8000)
ax.set_title("Three join algorithms against a 5,000,000-row table, as the outer side grows\n"
             "PostgreSQL 18, data in memory, serial plans, random_page_cost = 4 (default); measured 2026-10-09",
             fontsize=11, color=INK)
fig.tight_layout()
out = os.path.join(HERE, "03-query-planning-fig4.svg")
fig.savefig(out, format="svg", bbox_inches="tight")
print("wrote", out)
