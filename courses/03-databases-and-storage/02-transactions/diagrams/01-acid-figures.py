#!/usr/bin/env python3
"""Figures for M03 Ch2 §1 — what a transaction guarantees.

All measurements: PostgreSQL 18.6 in Docker on a laptop (SK hynix consumer NVMe
SSD), 2026-10-24, default settings. Raw data and method in 01-acid-data/.

Figure 2 (commit-cost.csv): what a commit costs. Left: rows committed per second
      for one row per commit, 100 rows per commit, and one row per commit with
      synchronous_commit = off. Right: group commit — transactions per second
      against the number of concurrent clients, each committing one row.
Figure 4 (lost-update.csv): 8 clients each add 1 to the same counter 2,000 times;
      the final value per method, against the 16,000 it should be.

Run:  .venv/bin/python 01-acid-figures.py
"""
import csv
import os
import statistics
from collections import defaultdict
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "01-acid-data")
INK, GREY = "#1b2430", "#64748b"
GREEN, BLUE, ORANGE, RED = "#047857", "#1d4ed8", "#c2410c", "#b91c1c"


def rows(name):
    with open(os.path.join(DATA, name), newline="") as f:
        return list(csv.DictReader(f))


# =============================================================================
# Figure 2 — commit cost and group commit
# =============================================================================
tps = defaultdict(list)
for r in rows("commit-cost.csv"):
    if r["tps"]:
        tps[(r["pattern"], int(r["clients"]))].append(float(r["tps"]))

fig, (a1, a2) = plt.subplots(1, 2, figsize=(12.4, 5.0), gridspec_kw={"width_ratios": [1, 1.25]})

bars = [
    ("1 row per commit\nsynchronous_commit\n= on", [t for t in tps[("per-row sync on", 1)]], ORANGE),
    ("100 rows per commit\nsynchronous_commit\n= on", [t * 100 for t in tps[("100 rows per commit", 1)]], BLUE),
    ("1 row per commit\nsynchronous_commit\n= off", [t for t in tps[("per-row sync off", 1)]], GREEN),
]
for i, (lab, vals, col) in enumerate(bars):
    med = statistics.median(vals)
    a1.bar(i, med, color=col, width=0.62)
    a1.errorbar(i, med, yerr=[[med - min(vals)], [max(vals) - med]], color=INK, capsize=4, lw=1)
    a1.text(i, max(vals) * 1.25, f"{med:,.0f} rows/s", ha="center", fontsize=9.5, color=INK)
a1.set_yscale("log")
a1.set_ylim(100, 300000)
a1.set_xticks(range(3))
a1.set_xticklabels([b[0] for b in bars], fontsize=8.8)
a1.set_ylabel("rows committed per second, one client (log scale)")
a1.set_title("Each commit waits for the disk to confirm a write", fontsize=10.5, color=INK)
a1.grid(axis="y", alpha=0.25, which="both")

clients = sorted(c for (p, c) in tps if p == "per-row sync on")
med = [statistics.median(tps[("per-row sync on", c)]) for c in clients]
lo = [min(tps[("per-row sync on", c)]) for c in clients]
hi = [max(tps[("per-row sync on", c)]) for c in clients]
a2.fill_between(clients, lo, hi, color=ORANGE, alpha=0.18, lw=0, label="range of 3 runs")
a2.plot(clients, med, "o-", color=ORANGE, lw=2, label="median of 3 runs")
a2.axhline(620, color=GREY, ls="--", lw=1)
a2.text(1.05, 680, "one flush per commit: about 620 per second (pg_test_fsync, 1.6 ms)", fontsize=8.6, color=GREY)
a2.annotate(f"{med[-1]:,.0f} commits/s with 64 clients —\nabout 3.5 ms each, many commits per flush",
            xy=(clients[-1], med[-1]), xytext=(1.6, 22000), fontsize=8.8, color=ORANGE,
            arrowprops=dict(arrowstyle="->", color=ORANGE, lw=0.9))
a2.set_xscale("log", base=2)
a2.set_yscale("log")
a2.set_xticks(clients)
a2.set_xticklabels([str(c) for c in clients])
a2.set_ylim(300, 60000)
a2.set_xlabel("concurrent clients, each committing one row at a time")
a2.set_ylabel("commits per second, all clients (log scale)")
a2.set_title("Group commit: concurrent commits share one flush", fontsize=10.5, color=INK)
a2.grid(alpha=0.25, which="both")
a2.legend(loc="lower right", fontsize=8.8)
fig.suptitle("What a durable commit costs — PostgreSQL 18 on a laptop NVMe SSD", fontsize=11.5, color=INK)
fig.tight_layout()
out = os.path.join(HERE, "01-acid-fig2.svg")
fig.savefig(out, format="svg", bbox_inches="tight")
print("wrote", out, [(b[0].split(chr(10))[0], statistics.median(b[1])) for b in bars], list(zip(clients, med)))

# =============================================================================
# Figure 4 — lost updates
# =============================================================================
final = defaultdict(list)
for r in rows("lost-update.csv"):
    final[(r["script"], r["synchronous_commit"])].append(int(r["final"]))
methods = [
    (("rmw", "off"), "read, then write\nautocommit,\nsync commit off", RED),
    (("rmw", "on"), "read, then write\nautocommit,\nsync commit on", RED),
    (("rmw_tx", "on"), "read, then write\ninside\nBEGIN … COMMIT", RED),
    (("atomic", "on"), "UPDATE … SET\nn = n + 1", GREEN),
    (("forupdate", "on"), "SELECT … FOR UPDATE,\nthen write", GREEN),
    (("rr", "on"), "REPEATABLE READ\n+ retry", GREEN),
]
fig, ax = plt.subplots(figsize=(11.6, 4.9))
for i, (key, lab, col) in enumerate(methods):
    m = statistics.median(final[key])
    ax.bar(i, m, color=col, width=0.62)
    ax.text(i, m + 300 if m < 10000 else m - 1400, f"{m:,}", ha="center", fontsize=10, color=INK if m < 10000 else "white")
ax.axhline(16000, color=INK, lw=1, ls="--")
ax.text(-0.35, 16350, "correct answer: 16,000", fontsize=9, color=INK, ha="left")
ax.set_xticks(range(len(methods)))
ax.set_xticklabels([m[1] for m in methods], fontsize=8.8)
ax.set_ylim(0, 18200)
ax.set_ylabel("counter value after 16,000 increments")
ax.set_title("Lost updates: 8 clients each add 1 to the same row 2,000 times (PostgreSQL 18, READ COMMITTED unless noted)",
             fontsize=10.5, color=INK)
ax.grid(axis="y", alpha=0.25)
fig.tight_layout()
out = os.path.join(HERE, "01-acid-fig4.svg")
fig.savefig(out, format="svg", bbox_inches="tight")
print("wrote", out)
