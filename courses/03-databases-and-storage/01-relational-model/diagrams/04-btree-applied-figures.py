#!/usr/bin/env python3
"""Figure for M03 Ch1 §4 §14b (Applied) — the "best" B-tree page size per device.

The model is Gray & Graefe's node-utility optimization (Gray & Graefe 1997;
Graefe, "The Five-Minute Rule 20 Years Later", CACM 52(7), 2009, Tables 4-5):

    utility(P)  = log2(records per node)       records = 0.7 * P / 20 bytes
    time(P)     = latency + P / bandwidth      (one random read of a P-byte page)
    best P      = argmax utility(P) / time(P)

20-byte entries at ~70% fill is Graefe's own assumption, and it happens to match
§1 of this section: a bigint index entry is 20 bytes including its line pointer,
and PostgreSQL fills internal pages to 70%.

Devices: the two from Graefe 2009 (a 2007 disk: 12 ms, 300 MB/s; a 2007 flash
disk: 0.1 ms, 66 MB/s), plus an illustrative modern NVMe drive (0.08 ms random
read latency, 3,000 MB/s). Each curve is normalized to its own maximum, because
the absolute values differ by two orders of magnitude.

Run:  .venv/bin/python 04-btree-applied-figures.py
"""
import math
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
INK, GREY = "#1b2430", "#64748b"
DEVICES = [  # label, latency (s), bandwidth (bytes/s), colour
    ("hard disk, 2007 (12 ms, 300 MB/s)", 12e-3, 300e6, "#c2410c"),
    ("flash disk, 2007 (0.1 ms, 66 MB/s)", 0.1e-3, 66e6, "#1d4ed8"),
    ("NVMe SSD, illustrative (0.08 ms, 3,000 MB/s)", 0.08e-3, 3000e6, "#047857"),
]


def score(p, lat, bw):
    return math.log2(0.7 * p / 20) / (lat + p / bw)


sizes = [2 ** (e / 8) for e in range(8 * 9, 8 * 21 + 1)]   # 512 B .. 2 MB
fig, ax = plt.subplots(figsize=(10.5, 5.6))
for label, lat, bw, col in DEVICES:
    ys = [score(p, lat, bw) for p in sizes]
    top = max(ys)
    best = sizes[ys.index(top)]
    ax.plot(sizes, [y / top for y in ys], color=col, lw=2.2, label=label)
    ax.scatter([best], [1.0], color=col, s=60, zorder=5)
    txt = f"best ≈ {best / 1024:.0f} KB" if best >= 1024 else f"best ≈ {best:.0f} B"
    ax.annotate(txt, xy=(best, 1.0), xytext=(best, 1.045), ha="center", fontsize=9, color=col)
    print(f"{label}: best {best / 1024:.1f} KB; 8 KB scores {score(8192, lat, bw) / top:.2f} of best")
ax.axvline(8192, color=INK, lw=1.0, ls="--")
ax.text(8192 * 1.07, 0.30, "PostgreSQL's\n8 KB page", fontsize=9, color=INK)
ax.axvline(16384, color=GREY, lw=0.8, ls=":")
ax.text(16384 * 1.07, 0.16, "InnoDB's\n16 KB page", fontsize=9, color=GREY)
ax.set_xscale("log", base=2)
ticks = [2 ** e for e in range(9, 22, 2)]
ax.set_xticks(ticks)
ax.set_xticklabels([f"{t // 1024} KB" if t >= 1024 else f"{t} B" for t in ticks])
ax.set_ylim(0, 1.12)
ax.set_xlabel("B-tree page size (log scale)")
ax.set_ylabel("search progress per second of I/O\n(each curve relative to its own best)")
ax.grid(alpha=0.25)
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=3, fontsize=9, frameon=False)
ax.set_title("The page size that makes each read most useful depends on the device\n"
             "Gray & Graefe's node-utility model: log2(entries per page) / time to read the page; "
             "20-byte entries, 70% full", fontsize=10.5, color=INK)
fig.tight_layout()
out = os.path.join(HERE, "04-btree-fig4.svg")
fig.savefig(out, format="svg", bbox_inches="tight")
print("wrote", out)
