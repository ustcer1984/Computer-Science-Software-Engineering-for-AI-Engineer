"""
Figures for M01 · Ch4 · §1 — The kernel boundary & the system call.

fig1: "The latency landscape" — a log-scale horizontal bar of the operations that
matter for this chapter, coloured by which side of the kernel boundary they live on.
The teaching point is the *two gaps*: a syscall is ~hundreds× a function call (so you
batch syscalls), and a device I/O is ~hundreds-to-100,000× a syscall (so you park a
waiting task instead of spinning — the whole justification for the async model of Ch3).

Numbers are the canonical "Latency Numbers Every Programmer Should Know" order of
magnitude (Jeff Dean / Peter Norvig; Colin Scott's updated interactive edition), plus
a KPTI-era syscall round-trip. They are order-of-magnitude teaching figures, not a
benchmark of any specific machine.

Run:  python 01-the-kernel-boundary-and-syscalls-figures.py
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# --- data: (label, latency in nanoseconds, tier) -------------------------------
# tiers: 0 = on-CPU / in-RAM (no boundary), 1 = crossing the kernel boundary,
#        2 = a real device (disk / network) on the far side of the boundary
rows = [
    ("Function call (same process)",        2,           0),
    ("Read from main memory (RAM)",          100,         0),
    ("System call round trip (KPTI era)",    600,         1),
    ("Thread context switch",                3_000,       1),
    ("SSD random read (NVMe)",               100_000,     2),
    ("Round trip, same datacentre",          500_000,     2),
    ("Disk (HDD) seek",                      10_000_000,  2),
    ("Internet round trip (intercontinental)", 150_000_000, 2),
]

tier_colour = {0: "#2E7D32", 1: "#E9852E", 2: "#C0392B"}  # green / amber / red
tier_name = {
    0: "On the CPU / in RAM (no boundary)",
    1: "Crossing the kernel boundary",
    2: "A real device, past the boundary",
}

labels = [r[0] for r in rows]
values = [r[1] for r in rows]
colours = [tier_colour[r[2]] for r in rows]
y = list(range(len(rows)))[::-1]  # top-to-bottom = cheap-to-expensive

fig, ax = plt.subplots(figsize=(11, 5.6))
ax.barh(y, values, color=colours, height=0.62, zorder=3)
ax.set_xscale("log")
ax.set_yticks(y)
ax.set_yticklabels(labels, fontsize=11)
ax.set_xlabel("latency  (nanoseconds, log scale)", fontsize=11)
ax.set_xlim(1, 1e9)


def human(ns: float) -> str:
    if ns < 1_000:
        return f"{ns:.0f} ns"
    if ns < 1_000_000:
        return f"{ns/1_000:.0f} µs"
    return f"{ns/1_000_000:.0f} ms"


for yi, v in zip(y, values):
    ax.text(v * 1.6, yi, human(v), va="center", ha="left", fontsize=10, zorder=4)

ax.grid(axis="x", which="major", ls=":", color="#BBBBBB", zorder=0)
ax.set_axisbelow(True)
for spine in ("top", "right"):
    ax.spines[spine].set_visible(False)

# annotate the two gaps that drive the chapter's engineering rules
ax.annotate(
    "≈ 300× a function call\n→ so you BATCH syscalls\n(buffer; big reads, not byte-at-a-time)",
    xy=(600, 5.0), xytext=(1.6e3, 6.15),
    fontsize=9.2, color="#7A4A12",
    arrowprops=dict(arrowstyle="->", color="#7A4A12", lw=1.3),
    ha="left", va="center",
)
ax.annotate(
    "≈ 150× to 250,000× a syscall\n→ so you PARK the waiting task\n(don't spin — this is why async exists)",
    xy=(5e5, 2.0), xytext=(1.3e4, 4.35),
    fontsize=9.2, color="#7A1F16",
    arrowprops=dict(arrowstyle="->", color="#7A1F16", lw=1.3),
    ha="left", va="center",
)

legend_handles = [Patch(facecolor=tier_colour[t], label=tier_name[t]) for t in (0, 1, 2)]
ax.legend(handles=legend_handles, loc="upper right", fontsize=9.5, framealpha=0.95)

ax.set_title(
    "The latency landscape: the kernel boundary sits between compute and the real world",
    fontsize=12.5, pad=12,
)
fig.tight_layout()
fig.savefig("01-the-kernel-boundary-and-syscalls-fig1.svg", bbox_inches="tight")
print("wrote 01-the-kernel-boundary-and-syscalls-fig1.svg")
