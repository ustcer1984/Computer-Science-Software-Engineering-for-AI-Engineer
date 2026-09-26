#!/usr/bin/env python3
"""Figures for M02 Ch4 §2 — running a real-time system.

fig1: the reconnect storm, simulated. N clients lose their connections at t = 0
      (a deploy, a load-balancer blip, a region failover) and all try to come
      back through a front door that admits at most C new connections per
      second. Three client retry policies:

        A  fixed 1 s retry, no backoff, no jitter
        B  exponential backoff (1, 2, 4, ... capped at 60 s), NO jitter
        C  exponential backoff with FULL jitter: sleep ~ Uniform(0, min(cap, base*2^k))
           (Marc Brooker, AWS Architecture Blog, 2015)

      Every attempt also gets a small natural spread (network + client scheduling,
      normal with sd 0.15 s) so policy B is not artificially perfect-lockstep.
      C = 500 per second is API Gateway WebSocket's default new-connection quota
      per account per Region, so N / C = 120 s is a hard floor: no policy can
      reconnect 60,000 clients faster than that.

fig2: backpressure, drawn. A producer emits 20 messages/s to one client. The
      client drains up to 40 messages/s, but its network stalls completely from
      t = 10 s to t = 40 s (bad hotel Wi-Fi). The per-connection outbound queue
      under four policies:

        unbounded buffer              - the default you get by not choosing
        bounded (200) + disconnect    - client resumes from the log on reconnect
        drop oldest (cap 200)         - bounded memory, silently loses messages
        coalesce to latest value      - for state, not events: queue <= 1

      plus the "dead but open" case: a client that never drains and whose
      connection is never closed. Unbounded buffering then grows forever.

Run:  .venv/bin/python 02-running-a-real-time-system-figures.py
Outputs SVGs next to this script (committed alongside the doc).
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
INK, ACC1, ACC2, ACC3, GREY = "#1b2430", "#c2410c", "#1d4ed8", "#047857", "#94a3b8"

# =============================================================================
# fig1 — reconnect storm
# =============================================================================
N = 60_000          # clients dropped at t = 0
C = 500             # admissions per second (API Gateway default quota)
DT = 0.1            # simulation bin, seconds
HORIZON = 600.0     # seconds simulated
BASE, CAP = 1.0, 60.0
SPREAD = 0.15       # natural timing noise, seconds (sd)
nbins = int(HORIZON / DT)
per_bin = int(C * DT)


def simulate(policy, seed=7):
    rng = np.random.default_rng(seed)
    if policy == "C":
        nxt = rng.uniform(0, BASE, N)                      # even the first try is jittered
    else:
        nxt = np.abs(rng.normal(0, SPREAD, N))             # everyone tries "at once"
    tries = np.zeros(N, dtype=int)
    done = np.zeros(N, dtype=bool)
    offered = np.zeros(nbins)
    connected = np.zeros(nbins)
    for b in range(nbins):
        t0, t1 = b * DT, (b + 1) * DT
        idx = np.flatnonzero((~done) & (nxt >= t0) & (nxt < t1))
        offered[b] = len(idx) / DT
        if len(idx):
            rng.shuffle(idx)
            ok, fail = idx[:per_bin], idx[per_bin:]
            done[ok] = True
            k = tries[fail]
            tries[fail] += 1
            if policy == "A":
                delay = np.full(len(fail), BASE)
            elif policy == "B":
                delay = np.minimum(CAP, BASE * 2.0 ** k)
            else:
                delay = rng.uniform(0, np.minimum(CAP, BASE * 2.0 ** k))
            nxt[fail] = t1 + delay + np.abs(rng.normal(0, SPREAD, len(fail)))
        connected[b] = done.sum()
    return offered, connected


t = np.arange(nbins) * DT
runs = {
    "A": ("fixed 1 s retry, no jitter", ACC1, "--"),
    "B": ("exponential backoff, NO jitter", ACC2, "-"),
    "C": ("exponential backoff + full jitter", ACC3, "-"),
}
results = {p: simulate(p) for p in runs}

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.8, 5.0))

# left: what the front door sees (smoothed to 1 s for legibility)
k = int(1.0 / DT)
for p, (lab, col, ls) in runs.items():
    off = results[p][0]
    sm = np.convolve(off, np.ones(k) / k, mode="same")
    ax1.plot(t, np.maximum(sm, 1), color=col, lw=1.6, ls=ls, label=lab)
ax1.axhline(C, color=INK, lw=1.2, ls="--")
ax1.annotate(f"front-door capacity  C = {C}/s", xy=(250, C), xytext=(185, C * 2.6),
             fontsize=8.5, color=INK, arrowprops=dict(arrowstyle="->", color=INK, lw=0.9))
ax1.set_yscale("log")
ax1.set_xlim(0, 300)
ax1.set_ylim(1, 2e5)
ax1.set_xlabel("seconds after the disconnect")
ax1.set_ylabel("connection attempts per second (log scale)")
ax1.set_title("What the front door sees", fontsize=11, color=INK)
ax1.grid(alpha=0.25, which="both")
ax1.legend(fontsize=8.5, loc="upper right")

# right: how many clients are back
for p, (lab, col, ls) in runs.items():
    ax2.plot(t, results[p][1] / N * 100, color=col, lw=2.4, ls=ls, label=lab)
floor = N / C
ax2.axvline(floor, color=INK, lw=1.2, ls="--")
ax2.annotate(f"hard floor  N / C = {floor:.0f} s\n(no policy can beat it)",
             xy=(floor, 72), xytext=(floor + 30, 78), fontsize=8.5, color=INK,
             arrowprops=dict(arrowstyle="->", color=INK, lw=0.9))
b_final = results["B"][1][-1] / N * 100
ax2.annotate(f"no jitter: waves stay in lockstep,\nonly {b_final:.0f}% back after {HORIZON:.0f} s",
             xy=(HORIZON * 0.9, b_final), xytext=(250, b_final + 14), fontsize=8.5, color=ACC2,
             arrowprops=dict(arrowstyle="->", color=ACC2, lw=0.9))
ax2.set_xlim(0, HORIZON)
ax2.set_ylim(0, 102)
ax2.set_xlabel("seconds after the disconnect")
ax2.set_ylabel("clients reconnected (%)")
ax2.set_title("How long until everyone is back", fontsize=11, color=INK)
ax2.grid(alpha=0.25)
ax2.legend(fontsize=8.5, loc="center right", bbox_to_anchor=(1.0, 0.6))

fig.suptitle(f"A reconnect storm: {N:,} clients, one front door admitting {C} per second",
             fontsize=13, color=INK, y=0.99)
fig.tight_layout(rect=(0, 0, 1, 0.95))
out = os.path.join(HERE, "02-running-a-real-time-system-fig1.svg")
fig.savefig(out, format="svg", bbox_inches="tight")
print("wrote", out)
for p in runs:
    c = results[p][1]
    t90 = t[np.argmax(c >= 0.9 * N)] if (c >= 0.9 * N).any() else None
    print(p, "peak offered/s", int(results[p][0].max()), "t90", t90, "final %", round(c[-1] / N * 100, 1))

# =============================================================================
# fig2 — backpressure policies
# =============================================================================
DT2 = 0.05
T2 = np.arange(0, 70, DT2)
PROD, DRAIN, CAPQ = 20.0, 40.0, 200
stalled = (T2 >= 10) & (T2 < 40)


def queue(policy, dead=False):
    q, qs, lost = 0.0, [], 0.0
    disconnected = False
    for i, tt in enumerate(T2):
        drain = 0.0 if (stalled[i] or dead) else DRAIN
        if policy == "disconnect" and disconnected:
            if not stalled[i]:
                disconnected = False          # client reconnects, replays from the LOG
            qs.append(0.0)
            continue
        if policy == "coalesce":
            q = 1.0 if (stalled[i] or dead) else min(1.0, q + PROD * DT2)
            qs.append(q)
            continue
        q = max(0.0, q + (PROD - drain) * DT2)
        if policy == "drop" and q > CAPQ:
            lost += q - CAPQ
            q = CAPQ
        if policy == "disconnect" and q >= CAPQ:
            disconnected, q = True, 0.0
        qs.append(q)
    return np.array(qs), lost


fig, ax = plt.subplots(figsize=(12.0, 5.2))
ax.axvspan(10, 40, color=GREY, alpha=0.18)
ax.text(25, 1370, "client's network stalls\n(drains 0 msg/s)", ha="center", va="top",
        fontsize=9, color=INK)

q_dead, _ = queue("unbounded", dead=True)
ax.plot(T2, q_dead, color=ACC1, lw=1.6, ls=":",
        label="unbounded buffer, client dead-but-open (never drains, never closed)")
q_unb, _ = queue("unbounded")
ax.plot(T2, q_unb, color=ACC1, lw=2.6, label="unbounded buffer (the default if you never choose)")
q_drop, lost = queue("drop")
ax.plot(T2, q_drop, color=ACC2, lw=2.4, label=f"drop oldest, cap {CAPQ}  (loses {lost:.0f} messages, silently)")
q_dis, _ = queue("disconnect")
ax.plot(T2, q_dis, color=ACC3, lw=2.4,
        label=f"bounded {CAPQ} + disconnect  (client resumes from the log)")
q_co, _ = queue("coalesce")
ax.plot(T2, q_co, color=INK, lw=2.0, ls="--", label="coalesce to latest value (state, not events)")

ax.annotate("grows without limit:\n20 msg/s x forever", xy=(62, q_dead[int(62 / DT2)]),
            xytext=(45, 1250), fontsize=8.5, color=ACC1,
            arrowprops=dict(arrowstyle="->", color=ACC1, lw=0.9))
ax.annotate("600 queued, then 30 s to drain", xy=(40, 600), xytext=(44, 700), fontsize=8.5,
            color=ACC1, arrowprops=dict(arrowstyle="->", color=ACC1, lw=0.9))
ax.annotate("disconnect at the cap:\nserver memory freed", xy=(20, 0), xytext=(13, 330),
            fontsize=8.5, color=ACC3, arrowprops=dict(arrowstyle="->", color=ACC3, lw=0.9))
ax.set_xlim(0, 70)
ax.set_ylim(-20, 1400)
ax.set_xlabel("seconds")
ax.set_ylabel("messages queued for this one client")
ax.set_title("One slow client, four backpressure policies — producer 20 msg/s, client drains up to 40 msg/s",
             fontsize=11.5, color=INK)
ax.grid(alpha=0.25)
fig.legend(*ax.get_legend_handles_labels(), fontsize=9, loc="lower center", ncol=2,
           bbox_to_anchor=(0.5, -0.02), frameon=False)
fig.tight_layout(rect=(0, 0.13, 1, 1))
out = os.path.join(HERE, "02-running-a-real-time-system-fig2.svg")
fig.savefig(out, format="svg", bbox_inches="tight")
print("wrote", out, "drop lost", round(lost))
