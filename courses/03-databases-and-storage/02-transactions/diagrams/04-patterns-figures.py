#!/usr/bin/env python3
"""Figures for M03 Ch2 §4 — concurrency patterns.

All measurements: PostgreSQL 18.6 (`postgres:18`, wal_level = logical) in Docker on a laptop, 2026-11-09, psycopg 3.3.6.
Raw data and method in 04-patterns-data/.

04-patterns-fig1.svg (occ-bench.csv): read-then-write under contention — throughput, lost updates, retries.
04-patterns-fig2.svg (idem-bench.csv): duplicate charges from client retries, four server designs.
04-patterns-fig4.svg (outbox-crash.csv): what each way of "write the database, tell the broker" loses or duplicates.
04-patterns-fig6.svg (outbox-relay.csv): outbox relay throughput and per-order reordering.

Run:  python 04-patterns-figures.py
"""
import csv
import os
import statistics
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "04-patterns-data")
INK, GREY = "#1b2430", "#64748b"
GREEN, BLUE, ORANGE, RED, PURPLE, TEAL = "#047857", "#1d4ed8", "#c2410c", "#b91c1c", "#7c3aed", "#0f766e"
plt.rcParams.update({"font.size": 10.5, "axes.edgecolor": GREY, "axes.labelcolor": INK, "xtick.color": INK,
                     "ytick.color": INK, "axes.spines.top": False, "axes.spines.right": False,
                     "svg.fonttype": "path"})


def rows(name):
    return list(csv.DictReader(open(os.path.join(DATA, name))))


def med(rs, col):
    return statistics.median(float(r[col]) for r in rs)


# ---------------------------------------------------------------- Figure 1: optimistic vs pessimistic
g = defaultdict(list)
for r in rows("occ-bench.csv"):
    g[(r["method"], int(r["rows"]))].append(r)
ns = sorted({k[1] for k in g})
STY = {"naive": (RED, "no protection (read, think, write)"),
       "pessimistic": (BLUE, "pessimistic (SELECT … FOR UPDATE)"),
       "optimistic": (ORANGE, "optimistic (version check + retry)"),
       "atomic": (GREEN, "one statement (balance = balance + 1)")}
fig, ax = plt.subplots(1, 3, figsize=(14.5, 4.6))
for m, (c, lab) in STY.items():
    ax[0].plot(ns, [med(g[(m, n)], "ops_per_s") for n in ns], "o-", color=c, label=lab, lw=2)
    ax[0].fill_between(ns, [min(float(r["ops_per_s"]) for r in g[(m, n)]) for n in ns],
                       [max(float(r["ops_per_s"]) for r in g[(m, n)]) for n in ns], color=c, alpha=0.12, lw=0)
ax[0].set_xscale("log"); ax[0].set_yscale("log")
ax[0].set_xlabel("rows the 16 clients pick from (fewer = more contention)")
ax[0].set_ylabel("updates per second")
ax[0].set_title("(a) throughput (line = median, band = min to max of 3 runs)", loc="left", color=INK, fontsize=9.5)
ax[0].legend(fontsize=8.5, frameon=False, loc="lower right")
total = 16 * 300
ax[1].plot(ns, [100 * med(g[("naive", n)], "lost") / total for n in ns], "o-", color=RED, lw=2,
           label="no protection: updates lost")
ax[1].set_xscale("log"); ax[1].set_ylim(0, 100)
ax[1].set_xlabel("rows the 16 clients pick from")
ax[1].set_ylabel("lost updates, % of 4,800")
ax[1].set_title("(b) the cost of no protection", loc="left", color=INK)
for n in ns:
    v = 100 * med(g[("naive", n)], "lost") / total
    ax[1].annotate(f"{v:.0f}%", (n, v), textcoords="offset points", xytext=(4, 6), fontsize=8.5, color=RED)
ax[2].plot(ns, [med(g[("optimistic", n)], "retries") / total for n in ns], "o-", color=ORANGE, lw=2,
           label="optimistic: retries per committed update")
ax[2].plot(ns, [med(g[("optimistic", n)], "p99_ms") / 1000 for n in ns], "s--", color=ORANGE, lw=1.5, alpha=0.7,
           label="optimistic: p99 latency (s)")
ax[2].plot(ns, [med(g[("pessimistic", n)], "p99_ms") / 1000 for n in ns], "s--", color=BLUE, lw=1.5, alpha=0.7,
           label="pessimistic: p99 latency (s)")
ax[2].set_xscale("log"); ax[2].set_yscale("log")
ax[2].set_xlabel("rows the 16 clients pick from")
ax[2].set_ylabel("retries per update  /  seconds")
ax[2].set_title("(c) the cost of being optimistic", loc="left", color=INK)
ax[2].legend(fontsize=8.5, frameon=False, loc="upper right")
fig.tight_layout()
fig.savefig(os.path.join(HERE, "04-patterns-fig1.svg"))
plt.close(fig)

# ---------------------------------------------------------------- Figure 2: idempotency
g = defaultdict(list)
for r in rows("idem-bench.csv"):
    g[r["design"]].append(r)
D = ["none", "check-first", "key-in-txn", "key-first"]
LAB = {"none": "no key", "check-first": "check key,\ncharge, save key", "key-in-txn": "key inserted first,\nsame transaction",
       "key-first": "key committed first,\n409 while in progress"}
fig, ax = plt.subplots(1, 2, figsize=(12.5, 4.4))
dups = [med(g[d], "duplicate_charges") for d in D]
bars = ax[0].bar(range(4), dups, color=[RED, ORANGE, GREEN, GREEN], width=0.6)
for b, v in zip(bars, dups):
    ax[0].text(b.get_x() + b.get_width() / 2, v + 2, f"{v:.0f}", ha="center", color=INK)
ax[0].set_xticks(range(4)); ax[0].set_xticklabels([LAB[d] for d in D], fontsize=9)
ax[0].set_ylabel("extra charges per 500 payments")
ax[0].set_title("(a) duplicate charges (median of 3 runs)", loc="left", color=INK)
att = [med(g[d], "attempts") / 500 for d in D]
c409 = [med(g[d], "client_409") / 500 for d in D]
gave = [med(g[d], "client_gave_up") for d in D]
x = range(4)
ax[1].bar([i - 0.2 for i in x], att, 0.4, color=GREY, label="requests sent per payment")
ax[1].bar([i + 0.2 for i in x], c409, 0.4, color=PURPLE, label="409 'in progress' replies per payment")
for i in x:
    ax[1].text(i - 0.2, att[i] + 0.02, f"{att[i]:.2f}", ha="center", fontsize=8.5)
    ax[1].text(i + 0.2, c409[i] + 0.02, f"{c409[i]:.2f}", ha="center", fontsize=8.5)
ax[1].set_xticks(list(x)); ax[1].set_xticklabels([LAB[d] for d in D], fontsize=9)
ax[1].set_title("(b) what the client saw", loc="left", color=INK)
ax[1].set_ylim(0, 1.75)
ax[1].legend(fontsize=8.5, frameon=False, loc="upper left")
fig.tight_layout()
fig.savefig(os.path.join(HERE, "04-patterns-fig2.svg"))
plt.close(fig)

# ---------------------------------------------------------------- Figure 4: dual write vs outbox
rs = {r["design"]: r for r in rows("outbox-crash.csv")}
D = ["commit-then-publish", "publish-then-commit", "outbox"]
LAB = {"commit-then-publish": "commit, then publish", "publish-then-commit": "publish, then commit",
       "outbox": "outbox + relay"}
M = [("lost", RED, "lost: order committed, no message"),
     ("phantom", PURPLE, "phantom: message for an order that does not exist"),
     ("duplicate_deliveries", ORANGE, "duplicate deliveries"),
     ("duplicate_effects_naive", BLUE, "duplicate effects, consumer without inbox"),
     ("duplicate_effects_inbox", GREEN, "duplicate effects, consumer with inbox")]
fig, ax = plt.subplots(figsize=(11.5, 4.4))
w = 0.16
for j, (col, c, lab) in enumerate(M):
    vals = [int(rs[d][col]) for d in D]
    xs = [i + (j - 2) * w for i in range(3)]
    ax.bar(xs, vals, w, color=c, label=lab)
    for xx, v in zip(xs, vals):
        ax.text(xx, v + 1, str(v), ha="center", fontsize=8.5)
ax.set_xticks(range(3)); ax.set_xticklabels([LAB[d] for d in D])
ax.set_ylabel("messages or effects, out of 2,000 orders")
ax.set_ylim(0, 150)
ax.legend(fontsize=8.5, frameon=False, loc="upper left", ncol=2)
fig.tight_layout()
fig.savefig(os.path.join(HERE, "04-patterns-fig4.svg"))
plt.close(fig)

# ---------------------------------------------------------------- Figure 6: relay throughput
g = defaultdict(list)
for r in rows("outbox-relay.csv"):
    g[(int(r["relays"]), int(r["batch"]))].append(r)
relays = sorted({k[0] for k in g}); batches = sorted({k[1] for k in g})
fig, ax = plt.subplots(1, 2, figsize=(12.5, 4.4))
for b, c in zip(batches, [RED, ORANGE, GREEN]):
    ax[0].plot(relays, [med(g[(n, b)], "msgs_per_s") for n in relays], "o-", color=c, lw=2,
               label=f"batch of {b} event{'s' if b > 1 else ''} per relay transaction")
    ax[1].plot(relays, [med(g[(n, b)], "out_of_order") for n in relays], "o-", color=c, lw=2,
               label=f"batch of {b}")
ax[0].set_xscale("log", base=2); ax[0].set_yscale("log")
ax[0].set_xticks(relays); ax[0].set_xticklabels(relays)
ax[0].set_xlabel("relay threads (FOR UPDATE SKIP LOCKED)"); ax[0].set_ylabel("events published per second")
ax[0].set_title("(a) relay throughput (20,000 events)", loc="left", color=INK)
ax[0].legend(fontsize=8.5, frameon=False)
ax[1].set_xscale("log", base=2); ax[1].set_xticks(relays); ax[1].set_xticklabels(relays)
ax[1].set_xlabel("relay threads"); ax[1].set_ylabel("events that reached the broker after\na later event of the same order")
ax[1].set_title("(b) events out of order (of 16,000 that could be)", loc="left", color=INK)
ax[1].legend(fontsize=8.5, frameon=False)
fig.tight_layout()
fig.savefig(os.path.join(HERE, "04-patterns-fig6.svg"))
plt.close(fig)
print("ok")
