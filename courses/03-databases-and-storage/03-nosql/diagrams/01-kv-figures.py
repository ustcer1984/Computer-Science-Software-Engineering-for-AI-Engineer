#!/usr/bin/env python3
"""Figures for M03 Ch3 §1 — key-value stores.

All measurements: Redis 8.10.3 (`redis:8`), DynamoDB Local 3.3.2 and PostgreSQL 18.6 in Docker on a laptop,
2026-11-19, Python clients redis-py 8.1.0, boto3 1.44.6, psycopg 3.3.6. Raw data and method in 01-kv-data/.

01-kv-fig2.svg (lookup-bench.csv, server-ceiling-out.txt): one key, one value — Redis vs PostgreSQL.
01-kv-fig3.svg (block-bench-out.txt): what one slow command does to everybody else's GET.
01-kv-fig5.svg (partition-sim.csv): the highest table write rate before the busiest partition saturates.
01-kv-fig6.svg (ttl-bench.csv): expired keys being reclaimed with nobody reading them.

Run:  python 01-kv-figures.py
"""
import csv
import os
import re
import statistics
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "01-kv-data")
INK, GREY = "#1b2430", "#64748b"
GREEN, BLUE, ORANGE, RED, PURPLE, TEAL = "#047857", "#1d4ed8", "#c2410c", "#b91c1c", "#7c3aed", "#0f766e"
plt.rcParams.update({"font.size": 10.5, "axes.edgecolor": GREY, "axes.labelcolor": INK, "xtick.color": INK,
                     "ytick.color": INK, "axes.spines.top": False, "axes.spines.right": False,
                     "svg.fonttype": "path"})


def rows(name):
    return list(csv.DictReader(open(os.path.join(DATA, name))))


def save(fig, name):
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, name), format="svg", bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------- Figure 1: Redis vs PostgreSQL lookups
g = defaultdict(list)
for r in rows("lookup-bench.csv"):
    g[(r["store"], r["mode"], int(r["clients"]))].append(float(r["lookups_per_s"]))
cases = [("seq", 1, "1 client,\none at a time"), ("batch100", 1, "1 client,\nbatches of 100"),
         ("procs", 4, "4 clients"), ("procs", 16, "16 clients")]
txt = open(os.path.join(DATA, "server-ceiling-out.txt")).read()
cpu = defaultdict(list)
for m in re.finditer(r"redis P=(\d+) rep=\d server_cpu_s=([\d.]+)", txt):
    cpu[f"Redis, pipeline {m.group(1)}"].append(float(m.group(2)) / 2_000_000 * 1e6)
for m in re.finditer(r"pgbench c=(\d+) rep=\d server_cpu_s=([\d.]+) number of transactions actually processed: (\d+)", txt):
    cpu[f"PostgreSQL, {m.group(1)} clients"].append(float(m.group(2)) / int(m.group(3)) * 1e6)

fig, ax = plt.subplots(1, 2, figsize=(13, 4.6), gridspec_kw={"width_ratios": [1.5, 1]})
x = range(len(cases)); w = 0.38
for off, store, col, lab in ((-w / 2, "redis", RED, "Redis GET"), (w / 2, "postgres", BLUE, "PostgreSQL SELECT by primary key")):
    vals = [statistics.median(g[(store, m, c)]) for m, c, _ in cases]
    bars = ax[0].bar([i + off for i in x], vals, w, color=col, label=lab)
    for b, v in zip(bars, vals):
        ax[0].text(b.get_x() + b.get_width() / 2, v * 1.08, f"{v/1000:.0f}k", ha="center", fontsize=8.5, color=INK)
ax[0].set_yscale("log"); ax[0].set_ylim(5_000, 600_000)
ax[0].set_xticks(list(x)); ax[0].set_xticklabels([c[2] for c in cases])
ax[0].set_ylabel("lookups per second (Python clients)")
ax[0].set_title("(a) what the application sees (median of 3 runs)", loc="left", color=INK, fontsize=9.5)
ax[0].legend(frameon=False, fontsize=9, loc="upper left")
order = ["Redis, pipeline 16", "Redis, pipeline 1", "PostgreSQL, 16 clients", "PostgreSQL, 50 clients"]
vals = [statistics.median(cpu[k]) for k in order]
bars = ax[1].barh(order, vals, color=[RED, RED, BLUE, BLUE])
for b, v in zip(bars, vals):
    ax[1].text(v * 1.1, b.get_y() + b.get_height() / 2, f"{v:.1f} µs", va="center", fontsize=9, color=INK)
ax[1].set_xscale("log"); ax[1].set_xlim(0.2, 300)
ax[1].invert_yaxis()
ax[1].set_xlabel("server CPU time per lookup (µs, log scale)")
ax[1].set_title("(b) what the server spends (C benchmark clients)", loc="left", color=INK, fontsize=9.5)
save(fig, "01-kv-fig2.svg")

# ---------------------------------------------------------------- Figure 2: blocking
b = defaultdict(list); took = defaultdict(list)
for line in open(os.path.join(DATA, "block-bench-out.txt")):
    m = re.match(r"(.+?)\s+command\s+([\d.]+) ms \| probe p50\s+([\d.]+) ms max\s+([\d.]+) ms", line)
    if m:
        b[m.group(1).strip()].append(float(m.group(4))); took[m.group(1).strip()].append(float(m.group(2)))
order = ["KEYS *", "SCAN loop", "DEL bighash", "UNLINK bighash"]
labels = ["KEYS *\n(1M keys, one call)", "SCAN, COUNT 1000\n(same keys, 1,000 calls)", "DEL\n(hash, 1M fields)",
          "UNLINK\n(same hash)"]
fig, ax = plt.subplots(figsize=(9.5, 4.2))
vals = [statistics.median(b[k]) for k in order]
bars = ax.bar(labels, vals, color=[RED, GREEN, RED, GREEN], width=0.55)
for bb, v, k in zip(bars, vals, order):
    ax.text(bb.get_x() + bb.get_width() / 2, v * 1.12, f"{v:.1f} ms", ha="center", fontsize=9.5, color=INK)
ax.axhline(0.12, color=GREY, ls=":", lw=1, label="a GET with nothing else running ≈ 0.12 ms")
ax.legend(frameon=False, fontsize=8.8, loc="upper right")
ax.set_yscale("log"); ax.set_ylim(0.08, 400)
ax.set_ylabel("slowest GET of another client (ms, log scale)")
ax.set_title("A GET probe every 1 ms while one other client runs the command (median of 3 runs)", loc="left",
             color=INK, fontsize=9.5)
save(fig, "01-kv-fig3.svg")

# ---------------------------------------------------------------- Figure 3: hot partitions
g = defaultdict(list)
for r in rows("partition-sim.csv"):
    g[r["workload"]].append((int(r["partitions"]), float(r["max_table_wcu_per_s"])))
STY = {"uniform": (GREEN, "1M customers, equally busy"),
       "zipf-1.1": (ORANGE, "1M customers, a few very busy (Zipf 1.1)"),
       "sharded-100": (PURPLE, "today's date + suffix 0–99"),
       "sharded-10": (BLUE, "today's date + suffix 0–9"),
       "one-key": (RED, "today's date as the key")}
fig, ax = plt.subplots(figsize=(9.5, 4.8))
for k, (c, lab) in STY.items():
    ps, vs = zip(*g[k])
    ax.plot(ps, vs, "o-", color=c, lw=2, label=lab)
ax.plot([1, 128], [1000, 128_000], color=GREY, ls=":", lw=1)
ax.text(40, 52_000, "perfect spread", color=GREY, fontsize=8.5, rotation=27)
ax.set_xscale("log", base=2); ax.set_yscale("log")
ax.set_xticks([1, 2, 4, 8, 16, 32, 64, 128]); ax.set_xticklabels(["1", "2", "4", "8", "16", "32", "64", "128"])
ax.set_xlabel("number of partitions the table is split into")
ax.set_ylabel("highest table write rate (write units/s)")
ax.set_title("Writes/s the table can take before its busiest partition reaches 1,000 write units/s (simulation)",
             loc="left", color=INK, fontsize=9.5)
ax.legend(frameon=False, fontsize=8.8, loc="upper left")
save(fig, "01-kv-fig5.svg")

# ---------------------------------------------------------------- Figure 4: TTL reclaim
fig, ax = plt.subplots(figsize=(9.5, 4.2))
for hz, c in ((10, BLUE), (100, ORANGE)):
    rs = [r for r in rows("ttl-bench.csv") if r["hz"] == str(hz) and r["expired_keys"]]
    ax.plot([float(r["t_s"]) for r in rs], [int(r["dbsize"]) / 1e6 for r in rs], color=c, lw=2,
            label=f"hz {hz} (background expiry cycle {hz} times a second)")
ax.axvspan(0, 7.8, color=GREY, alpha=0.10, lw=0)
ax.text(0.3, 0.5, "writing 1.1M keys", color=GREY, fontsize=8.5)
ax.axvspan(10, 17.8, color=RED, alpha=0.07, lw=0)
ax.text(10.2, 0.5, "the 1M keys' TTLs run out\n(10 s after each was written)", color=RED, fontsize=8.5)
ax.axvline(25, color=GREY, ls=":", lw=1)
ax.text(25.2, 0.6, "GET 1,000 expired keys:\nall nil", color=GREY, fontsize=8.5)
ax.set_xlim(0, 30); ax.set_ylim(0, 1.45)
ax.set_xlabel("seconds since the first write")
ax.set_ylabel("keys held by the server (millions)")
ax.set_title("1,000,000 keys with a 10 s TTL and 100,000 without one; nobody reads them", loc="left", color=INK,
             fontsize=9.5)
ax.legend(frameon=False, fontsize=9, loc="upper right")
save(fig, "01-kv-fig6.svg")
print("wrote 01-kv-fig2, 3, 5, 6 .svg")
