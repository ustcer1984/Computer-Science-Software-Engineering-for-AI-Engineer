#!/usr/bin/env python3
"""Figures for M03 Ch2 §3 — MVCC and locks in PostgreSQL.

All measurements: PostgreSQL 18.6 (`postgres:18`) in Docker on a laptop, 2026-11-02, psycopg 3.3.6.
Raw data and method in 03-mvcc-data/.

Figure 2 (table-lock-matrix.csv): the eight table-lock modes, which pairs conflict (measured with LOCK TABLE ... NOWAIT).
Figure 4 (pileup.csv, pileup-waiting.csv): latency of point SELECTs while a long reader and an ALTER TABLE meet.
Figure 5 (queue-bench.csv): job-queue throughput against the number of workers, six ways of claiming a job.

Run:  .venv/bin/python 03-mvcc-figures.py
"""
import csv
import os
import statistics
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "03-mvcc-data")
INK, GREY = "#1b2430", "#64748b"
GREEN, BLUE, ORANGE, RED, PURPLE, TEAL = "#047857", "#1d4ed8", "#c2410c", "#b91c1c", "#7c3aed", "#0f766e"

# =============================================================================
# Figure 2 — table-lock conflict matrix
# =============================================================================
rows = list(csv.reader(open(os.path.join(DATA, "table-lock-matrix.csv"))))
modes = rows[0][1:]
cells = [[int(x) for x in r[1:]] for r in rows[1:]]
TAKEN_BY = {
    "ACCESS SHARE": "SELECT",
    "ROW SHARE": "SELECT … FOR UPDATE / FOR SHARE",
    "ROW EXCLUSIVE": "INSERT, UPDATE, DELETE, MERGE",
    "SHARE UPDATE EXCLUSIVE": "VACUUM, ANALYZE, CREATE INDEX CONCURRENTLY",
    "SHARE": "CREATE INDEX",
    "SHARE ROW EXCLUSIVE": "CREATE TRIGGER, ADD FOREIGN KEY",
    "EXCLUSIVE": "REFRESH MATERIALIZED VIEW CONCURRENTLY",
    "ACCESS EXCLUSIVE": "ALTER TABLE (most), TRUNCATE, DROP, VACUUM FULL",
}
fig, ax = plt.subplots(figsize=(12.0, 5.6))
for i, row in enumerate(cells):
    for j, v in enumerate(row):
        ax.add_patch(plt.Rectangle((j, i), 0.94, 0.9, facecolor="#fee2e2" if v else "#d1fae5",
                                   edgecolor=RED if v else GREEN, lw=1.0))
        ax.text(j + 0.47, i + 0.45, "conflict" if v else "ok", ha="center", va="center", fontsize=8.4,
                color=RED if v else GREEN, fontweight="bold" if v else "normal")
    ax.text(-0.1, i + 0.32, modes[i], ha="right", va="center", fontsize=9.6, color=INK, fontweight="bold")
    ax.text(-0.1, i + 0.66, TAKEN_BY[modes[i]], ha="right", va="center", fontsize=8.0, color=GREY)
for j, mname in enumerate(modes):
    ax.text(j + 0.47, -0.15, mname.replace(" ", "\n"), ha="center", va="bottom", fontsize=8.4, color=INK)
ax.text(4.0, -1.35, "lock requested by a second transaction", ha="center", fontsize=10, color=INK)
ax.text(-4.6, 4.0, "lock held by one transaction  (and the statements that take it)", rotation=90,
        ha="center", va="center", fontsize=10, color=INK)
ax.set_xlim(-5.0, 8.1)
ax.set_ylim(8.1, -1.6)
ax.axis("off")
fig.tight_layout()
out = os.path.join(HERE, "03-mvcc-fig2.svg")
fig.savefig(out, format="svg", bbox_inches="tight")
print("wrote", out)

# =============================================================================
# Figure 4 — the lock-queue pile-up
# =============================================================================
pts = defaultdict(list)
for r in csv.DictReader(open(os.path.join(DATA, "pileup.csv"))):
    pts[r["scenario"]].append((float(r["start_s"]), float(r["latency_ms"])))
wait = defaultdict(list)
for r in csv.DictReader(open(os.path.join(DATA, "pileup-waiting.csv"))):
    wait[r["scenario"]].append((float(r["t_s"]), int(r["waiting_sessions"])))
SCEN = [("no DDL", "1. A 7-second report, no DDL"),
        ("DDL, no lock_timeout", "2. The same report, plus ALTER TABLE at t = 2 s"),
        ("DDL, lock_timeout 200 ms + retry", "3. ALTER TABLE with lock_timeout = 200 ms, retried every second")]
fig, axes = plt.subplots(3, 1, figsize=(11.5, 8.2), sharex=True)
for ax, (key, title) in zip(axes, SCEN):
    xs, ys = zip(*pts[key])
    ax.axvspan(1, 8, color="#e0e7ff", alpha=0.6, lw=0)
    ax.text(1.05, 6500, "report holds ACCESS SHARE (t = 1 to 8 s)", fontsize=8.2, color=BLUE, va="top")
    if key != "no DDL":
        ax.text(2.1, 25, "ALTER TABLE\nissued", fontsize=8.2, color=RED, va="center",
                bbox=dict(facecolor="white", edgecolor="none", pad=1.0))
        ax.axvline(2, color=RED, lw=1.0, ls="--")
    ax.scatter(xs, ys, s=5, color=INK, alpha=0.55, lw=0)
    slow = [(x, y) for x, y in pts[key] if y > 50]
    if slow:
        ax.scatter(*zip(*slow), s=26, color=RED, lw=0, zorder=5, label="a SELECT that waited > 50 ms (plotted at its start)")
        ax.legend(loc="center right", fontsize=8, frameon=False)
    ax.set_yscale("log")
    ax.set_ylim(0.1, 10000)
    ax.set_ylabel("SELECT latency, ms", fontsize=9)
    ax.set_title(title, fontsize=10, color=INK, loc="left")
    ax2 = ax.twinx()
    tx, n = zip(*wait[key])
    ax2.step(tx, n, where="post", color=ORANGE, lw=1.3)
    ax2.set_ylim(0, 10)
    ax2.set_ylabel("sessions waiting\nfor a lock", fontsize=9, color=ORANGE)
    ax2.tick_params(axis="y", colors=ORANGE, labelsize=8)
    ax.tick_params(labelsize=8)
    ax.grid(axis="y", color="#e5e7eb", lw=0.6)
    lat = [y for _, y in pts[key]]
    ax.text(11.9, 3000, f"{len(lat):,} SELECTs, max {max(lat):,.0f} ms", ha="right", fontsize=8.4, color=INK)
axes[-1].set_xlabel("time, s (8 clients, each a point SELECT every 20 ms)", fontsize=9)
axes[-1].set_xlim(0, 12)
fig.tight_layout()
out = os.path.join(HERE, "03-mvcc-fig4.svg")
fig.savefig(out, format="svg", bbox_inches="tight")
print("wrote", out)

# =============================================================================
# Figure 5 — job-queue throughput
# =============================================================================
qb = defaultdict(list)
dup = defaultdict(list)
for r in csv.DictReader(open(os.path.join(DATA, "queue-bench.csv"))):
    qb[(r["method"], int(r["workers"]))].append(float(r["jobs_per_s"]))
    dup[(r["method"], int(r["workers"]))].append(int(r["duplicates"]))
LAB = [("naive", "SELECT, then UPDATE (no lock): runs jobs twice", RED, "x", ":"),
       ("for_update", "FOR UPDATE (no SKIP LOCKED)", ORANGE, "s", "-"),
       ("claim_update", "conditional UPDATE … AND status = 'pending'", PURPLE, "D", "-"),
       ("advisory", "pg_try_advisory_xact_lock(id) in WHERE: ran some jobs twice", "#ca8a04", "^", "--"),
       ("skip_locked", "FOR UPDATE SKIP LOCKED, lock held while working", BLUE, "o", "-"),
       ("claim_skip", "claim row: UPDATE … (SKIP LOCKED) RETURNING", GREEN, "v", "-")]
W = sorted({w for _, w in qb})
fig, ax = plt.subplots(figsize=(10.5, 5.6))
for key, lab, col, mk, ls in LAB:
    ys = [statistics.median(qb[(key, w)]) for w in W]
    ax.plot(W, ys, marker=mk, color=col, lw=1.6, ls=ls, label=lab, ms=5)
ideal = [statistics.median(qb[("skip_locked", 1)]) * w for w in W]
ax.plot(W, ideal, color=GREY, lw=0.8, ls="--", label="perfect scaling from 1 worker")
ax.set_xscale("log", base=2)
ax.set_yscale("log")
ax.set_xticks(W)
ax.set_xticklabels([str(w) for w in W])
ax.set_yticks([100, 200, 500, 1000, 2000, 4000])
ax.set_yticklabels(["100", "200", "500", "1,000", "2,000", "4,000"])
ax.set_xlabel("workers (one connection each); 1,000 jobs, 5 ms of work per job", fontsize=9)
ax.set_ylabel("jobs completed per second (median of 3)", fontsize=9)
ax.grid(color="#e5e7eb", lw=0.6, which="both")
ax.legend(fontsize=8.3, loc="upper left", frameon=False)
ax.tick_params(labelsize=8.5)
fig.tight_layout()
out = os.path.join(HERE, "03-mvcc-fig5.svg")
fig.savefig(out, format="svg", bbox_inches="tight")
print("wrote", out)
