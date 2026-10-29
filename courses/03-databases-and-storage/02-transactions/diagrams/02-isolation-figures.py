#!/usr/bin/env python3
"""Figures for M03 Ch2 §2 — isolation levels, reproduced.

All measurements: PostgreSQL 18.6 and MySQL 8.4.13 (InnoDB) in Docker on a laptop,
2026-10-29, default settings. Raw data and method in 02-isolation-data/.

Figure 1: what happened to each anomaly's schedule at each level, both engines. The cells
      are transcribed from results-pg.txt and results-my.txt (one run per cell; the
      schedules are deterministic).
Figure 3 (ssi-bench.csv): the price of each level — share of transactions that failed
      with a serialization error, and committed transactions per second, for a transfer
      workload over 10 to 100,000 accounts.

Run:  .venv/bin/python 02-isolation-figures.py
"""
import csv
import os
import statistics
from collections import defaultdict
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "02-isolation-data")
INK, GREY = "#1b2430", "#64748b"
GREEN, BLUE, ORANGE, RED = "#047857", "#1d4ed8", "#c2410c", "#b91c1c"

# =============================================================================
# Figure 1 — the outcome matrix
# =============================================================================
OK, WAIT, ABORT, BAD = "ok", "wait", "abort", "bad"
STYLE = {OK: ("#d1fae5", GREEN, "prevented"), WAIT: ("#dbeafe", BLUE, "prevented: waits"),
         ABORT: ("#ffedd5", ORANGE, "aborted"), BAD: ("#fee2e2", RED, "HAPPENED")}
COLS = ["READ\nCOMMITTED", "REPEATABLE\nREAD", "SERIALIZABLE",
        "READ\nUNCOMMITTED", "READ\nCOMMITTED", "REPEATABLE\nREAD", "SERIALIZABLE"]
# (anomaly, PostgreSQL RC/RR/SER, InnoDB RU/RC/RR/SER); "abort" text says which error
ROWS = [
    ("dirty write",          [WAIT, ABORT, ABORT],   [WAIT, WAIT, WAIT, WAIT]),
    ("dirty read",           [OK, OK, OK],           [BAD, OK, OK, WAIT]),
    ("non-repeatable read",  [BAD, OK, OK],          [BAD, BAD, OK, WAIT]),
    ("read skew",            [BAD, OK, OK],          [BAD, BAD, OK, WAIT]),
    ("phantom",              [BAD, OK, OK],          [BAD, BAD, OK, WAIT]),
    ("lost update",          [BAD, ABORT, ABORT],    [BAD, BAD, BAD, ABORT]),
    ("write skew",           [BAD, BAD, ABORT],      [BAD, BAD, BAD, ABORT]),
    ("write skew, inserts",  [BAD, BAD, ABORT],      [BAD, BAD, BAD, ABORT]),
    ("read-only anomaly",    [BAD, BAD, ABORT],      [BAD, BAD, BAD, ABORT]),
]
fig, ax = plt.subplots(figsize=(12.6, 6.2))
for r, (name, pg, my) in enumerate(ROWS):
    for c, v in enumerate(pg + my):
        x = c + (0.35 if c >= 3 else 0)
        face, edge, text = STYLE[v]
        if v == ABORT:
            text = "aborted\n40001" if c < 3 else "aborted\ndeadlock 1213"
        ax.add_patch(plt.Rectangle((x, r), 0.94, 0.9, facecolor=face, edgecolor=edge, lw=1.1))
        ax.text(x + 0.47, r + 0.45, text, ha="center", va="center", fontsize=8.2, color=edge,
                fontweight="bold" if v == BAD else "normal")
    ax.text(-0.08, r + 0.45, name, ha="right", va="center", fontsize=9.6, color=INK)
for c, lab in enumerate(COLS):
    x = c + (0.35 if c >= 3 else 0)
    ax.text(x + 0.47, -0.25, lab, ha="center", va="bottom", fontsize=8.6, color=INK)
ax.text(1.5, -1.25, "PostgreSQL 18", ha="center", fontsize=10.5, color=INK, fontweight="bold")
ax.text(3.35 + 2.0, -1.25, "MySQL 8.4, InnoDB", ha="center", fontsize=10.5, color=INK, fontweight="bold")
ax.plot([3.17, 3.17], [-1.3, len(ROWS)], color=GREY, lw=0.8)
ax.set_xlim(-2.4, 7.4)
ax.set_ylim(len(ROWS) + 0.1, -1.6)
ax.axis("off")
ax.legend(handles=[Patch(facecolor=STYLE[k][0], edgecolor=STYLE[k][1], label=STYLE[k][2]) for k in (OK, WAIT, ABORT, BAD)]
          + [Patch(facecolor="white", edgecolor="white", label="default level: PostgreSQL READ COMMITTED, InnoDB REPEATABLE READ")],
          loc="lower center", bbox_to_anchor=(0.5, -0.1), ncol=5, fontsize=8.6, frameon=False)
ax.set_title("Each anomaly's schedule, run at each level: what actually happened (two or three sessions, one run per cell)",
             fontsize=10.5, color=INK)
fig.tight_layout()
out = os.path.join(HERE, "02-isolation-fig1.svg")
fig.savefig(out, format="svg", bbox_inches="tight")
print("wrote", out)

# =============================================================================
# Figure 3 — what each level costs on a transfer workload (Figure 2 is the Mermaid diagram)
# =============================================================================
path = os.path.join(DATA, "ssi-bench.csv")
if os.path.exists(path):
    runs = defaultdict(list)
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            if r["workload"] == "transfer" and r["committed"]:
                runs[(r["level"], int(r["accounts"]))].append(r)
    levels = [("read committed", "READ COMMITTED", GREEN), ("repeatable read", "REPEATABLE READ", BLUE),
              ("serializable", "SERIALIZABLE", ORANGE)]
    ns = sorted({n for (_, n) in runs})
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12.4, 4.9))
    for key, lab, col in levels:
        fail = [statistics.median(100 * int(r["failed"]) / (int(r["committed"]) + int(r["failed"])) for r in runs[(key, n)])
                for n in ns]
        tps = [statistics.median(float(r["tps"]) for r in runs[(key, n)]) for n in ns]
        pts = [(n, v) for n, v in zip(ns, fail) if v > 0]        # log axis: READ COMMITTED reaches 0
        a1.plot([p[0] for p in pts], [p[1] for p in pts], "o-", color=col, lw=2, label=lab)
        a2.plot(ns, tps, "o-", color=col, lw=2, label=lab)
        if key != "read committed":
            for n, v in pts:
                a1.annotate(f"{v:.2f}%" if v < 1 else f"{v:.0f}%" if v >= 10 else f"{v:.1f}%", (n, v),
                            textcoords="offset points", xytext=(6, 6 if key == "serializable" else -13),
                            fontsize=8.2, color=col)
    a1.annotate("READ COMMITTED: deadlocks only,\nnone at all from 10,000 accounts", (100, 0.045), xytext=(300, 0.006),
                fontsize=8.4, color=GREEN, arrowprops=dict(arrowstyle="->", color=GREEN, lw=0.9))
    a1.set_xscale("log")
    a1.set_yscale("log")
    a1.set_ylim(0.004, 300)
    a1.set_xlabel("accounts the transfers are spread over (log scale)")
    a1.set_ylabel("transactions that failed, % of attempts (log scale)\n(serialization failure or deadlock)")
    a1.set_title("Failures track contention; SERIALIZABLE adds little here", fontsize=10.5, color=INK)
    a1.grid(alpha=0.25, which="both")
    a1.legend(fontsize=9, loc="upper right")
    a2.set_xscale("log")
    a2.set_yscale("log")
    a2.set_xlabel("accounts the transfers are spread over (log scale)")
    a2.set_ylabel("committed transactions per second (log scale)")
    a2.set_title("Throughput: the level matters far less than contention", fontsize=10.5, color=INK)
    a2.grid(alpha=0.25, which="both")
    fig.suptitle("8 clients for 10 s, each transaction: read a balance, move 1 between two random accounts; no retries "
                 "(PostgreSQL 18, medians of 3 runs)", fontsize=10.5, color=INK)
    fig.tight_layout()
    out = os.path.join(HERE, "02-isolation-fig3.svg")
    fig.savefig(out, format="svg", bbox_inches="tight")
    print("wrote", out)
