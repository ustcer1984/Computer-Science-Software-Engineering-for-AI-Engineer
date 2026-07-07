"""
Figures for M01 · Ch4 · §2 — Blocking vs non-blocking I/O & multiplexing.

fig1: "Why epoll won" — cost of one readiness-check call as the number of
monitored connections grows, for select/poll (O(n): the kernel rescans every
registered fd on every call) vs epoll (O(ready): the kernel keeps the interest
list and hands back only the fds that fired). Log-log, so O(n) is a slope-1
line and O(ready) is flat. This is the mechanism behind the C10k fix: at 10k
mostly-idle connections, select/poll do ~10k units of work per call while
epoll does ~(a few). Illustrative order-of-magnitude units, not a benchmark of
any one machine.

Run:  python 02-blocking-nonblocking-and-multiplexing-figures.py
"""

import numpy as np
import matplotlib.pyplot as plt

fds = np.logspace(1, 5, 200)          # 10 → 100,000 monitored connections
ACTIVE = 50                            # typical: only a handful are ready at once

# select/poll: the kernel walks EVERY registered fd on EVERY call → O(n)
poll_cost = fds
# select: same O(n), but the fd_set bitmask caps out at FD_SETSIZE = 1024
select_fds = fds[fds <= 1024]
select_cost = select_fds
# epoll: kernel returns only the ready fds → cost ∝ number ACTIVE, not total
epoll_cost = np.full_like(fds, ACTIVE)

fig, ax = plt.subplots(figsize=(10.5, 5.8))
ax.loglog(fds, poll_cost, color="#C0392B", lw=2.4, label="select / poll  —  O(n): rescan every fd, every call", zorder=3)
ax.loglog(select_fds, select_cost, color="#C0392B", lw=2.4, ls=(0, (1, 1)), zorder=3)
ax.loglog(fds, epoll_cost, color="#2E7D32", lw=2.6, label="epoll  —  O(ready): kernel returns only fds that fired", zorder=3)

# FD_SETSIZE wall for select
ax.axvline(1024, color="#7A1F16", ls=":", lw=1.3, zorder=2)
ax.text(1024 * 1.15, 2.4, "select's wall:\nFD_SETSIZE = 1024", color="#7A1F16", fontsize=9, va="bottom")

# the C10k line
ax.axvline(10_000, color="#555555", ls="--", lw=1.2, zorder=2)
ax.text(10_000 * 1.15, 3.2e4, "C10k:\n10,000 connections", color="#333333", fontsize=9.5, va="top")

# annotate the gap at 10k
ax.annotate(
    "at 10k connections:\nselect/poll do ~10,000 units of work per call\nepoll does ~50 — the fix isn't faster hardware,\nit's not rescanning idle connections",
    xy=(10_000, 10_000), xytext=(70, 1.1e4),
    fontsize=9.3, color="#7A1F16",
    arrowprops=dict(arrowstyle="->", color="#7A1F16", lw=1.3),
    ha="left", va="center",
)

ax.set_xlabel("monitored connections  (file descriptors, log scale)", fontsize=11)
ax.set_ylabel("work per readiness-check call\n(arbitrary units, log scale)", fontsize=11)
ax.set_title("Why epoll won the C10k problem: O(n) rescan vs O(ready) notification", fontsize=12.5, pad=12)
ax.grid(True, which="major", ls=":", color="#BBBBBB", zorder=0)
ax.grid(True, which="minor", ls=":", color="#EEEEEE", zorder=0)
ax.set_axisbelow(True)
for spine in ("top", "right"):
    ax.spines[spine].set_visible(False)
ax.legend(loc="upper left", fontsize=9.8, framealpha=0.96)
ax.set_ylim(1, 2e5)

fig.tight_layout()
fig.savefig("02-blocking-nonblocking-and-multiplexing-fig1.svg", bbox_inches="tight")
print("wrote 02-blocking-nonblocking-and-multiplexing-fig1.svg")
