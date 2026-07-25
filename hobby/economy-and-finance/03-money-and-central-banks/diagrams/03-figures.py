#!/usr/bin/env python3
"""Figures for Econ E03 §3 — Central banks & monetary policy (the Fed model).

Editable source of truth for the committed SVGs (see agent-docs/diagrams.md:
commit the rendered image, keep the source beside it). Numbers are illustrative
but chosen to match the real shape of the published pictures:

  fig1 — HOW THE FED SETS THE RATE: the market for reserves, two regimes.
         (a) scarce reserves (pre-2008): a vertical reserve supply meets a
         downward-sloping demand ON ITS SLOPE, so the Fed moves the rate by
         moving supply (open-market operations). (b) ample reserves (post-2008):
         supply sits far out on the FLAT floor, so the overnight rate = the
         administered floor (IORB) and barely moves when supply shifts — "price,
         not quantity" (§1).
  fig2 — THE TAYLOR RULE (conceptual): the prescribed policy rate as a function
         of inflation, with slope > 1 (the Taylor principle: the real rate rises
         when inflation rises), the neutral point at target, and the zero floor.
  fig3 — THE TWO TOOLS OVER TIME: the policy rate (conventional) and the Fed's
         balance sheet (unconventional / QE-QT), 2007-2026 — ZLB episodes,
         QE expansions, the 2022 hiking cycle, and QT.
  fig4 — LONG AND VARIABLE LAGS: a stylised impulse response to a one-off rate
         hike — the output gap troughs after ~4-6 quarters, inflation after
         ~8-12, so policy acts on the economy of a year-plus from now.

Run with the project venv:

    .venv/bin/python hobby/economy-and-finance/03-money-and-central-banks/diagrams/03-figures.py

Outputs 03-monetary-policy-the-fed-model-figN.svg into this folder.
"""
import os
import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt
import numpy as np

OUT = os.path.dirname(os.path.abspath(__file__))
BASE = "03-monetary-policy-the-fed-model"

plt.rcParams.update({
    "font.size": 12,
    "axes.titlesize": 13,
    "axes.labelsize": 12,
    "svg.fonttype": "none",
    "figure.dpi": 100,
    "text.parse_math": False,   # render literal '$' in labels
})

C1 = "#1f77b4"   # blue
C2 = "#d62728"   # red
C3 = "#2ca02c"   # green
C4 = "#ff7f0e"   # orange
C5 = "#9467bd"   # purple
GREY = "#555555"


def save(fig, n):
    path = os.path.join(OUT, f"{BASE}-fig{n}.svg")
    fig.savefig(path, format="svg", bbox_inches="tight")
    plt.close(fig)
    print("wrote", path)


# ---------------------------------------------------------------------------
# Fig 1 — The market for reserves, two regimes.
# ---------------------------------------------------------------------------
def fig1():
    fig, (axA, axB) = plt.subplots(1, 2, figsize=(12.2, 5.6), sharey=True)
    R = np.linspace(0, 10, 400)

    def demand(floor, ceiling, mid, k):
        # reverse-S: high (toward ceiling) when reserves scarce, flattening to
        # the floor when reserves are ample.
        return floor + (ceiling - floor) / (1 + np.exp(k * (R - mid)))

    # --- Panel A: scarce reserves (pre-2008) ---
    ceilingA, floorA = 5.0, 0.25
    dA = demand(floorA, ceilingA, mid=4.2, k=1.1)
    axA.plot(R, dA, color=C1, lw=2.6, label="Reserve demand")
    axA.axhline(ceilingA, color=C2, ls="--", lw=1.4)
    axA.text(0.2, ceilingA + 0.12, "ceiling = discount rate", color=C2, fontsize=9)
    axA.axhline(floorA, color=C3, ls="--", lw=1.4)
    axA.text(6.4, floorA + 0.12, "floor (≈0 pre-IOR)", color=C3, fontsize=9)
    # vertical supply on the sloped part; a second (shifted) supply shows OMO
    Rs1 = 4.2
    axA.axvline(Rs1, color=GREY, lw=2.4)
    axA.plot([Rs1], [demand(floorA, ceilingA, 4.2, 1.1)[np.argmin(abs(R - Rs1))]],
             "o", color="black", ms=7, zorder=5)
    tgt = floorA + (ceilingA - floorA) / (1 + np.exp(1.1 * (Rs1 - 4.2)))
    axA.annotate("target rate\n(set here)", xy=(Rs1, tgt), xytext=(1.2, 1.5),
                 fontsize=9, fontweight="bold",
                 arrowprops=dict(arrowstyle="->", color="black", lw=1.3))
    Rs2 = 5.6
    axA.axvline(Rs2, color=GREY, lw=1.6, ls=":")
    axA.annotate("Fed shifts SUPPLY\n(open-market ops)\n→ moves the rate",
                 xy=(Rs2, 1.4), xytext=(6.0, 3.2), fontsize=8.6, color=GREY,
                 arrowprops=dict(arrowstyle="->", color=GREY, lw=1.2))
    axA.set_title("(a) Scarce reserves (pre-2008)", fontsize=11.5)
    axA.set_xlabel("Quantity of reserves")
    axA.set_ylabel("Overnight interest rate (%)")
    axA.set_ylim(-0.4, 6.0)
    axA.legend(loc="upper right", fontsize=9)
    axA.spines[["top", "right"]].set_visible(False)

    # --- Panel B: ample reserves (post-2008) ---
    ceilingB, floorB = 5.0, 2.0
    dB = demand(floorB, ceilingB, mid=2.6, k=1.4)
    axB.plot(R, dB, color=C1, lw=2.6, label="Reserve demand")
    axB.axhline(ceilingB, color=C2, ls="--", lw=1.4)
    axB.text(0.2, ceilingB + 0.12, "ceiling = discount rate", color=C2, fontsize=9)
    axB.axhline(floorB, color=C3, ls="-", lw=1.8)
    axB.text(5.0, floorB + 0.14, "administered floor = IORB", color=C3, fontsize=9.2,
             fontweight="bold")
    Rs1b, Rs2b = 6.5, 8.5
    axB.axvline(Rs1b, color=GREY, lw=2.4)
    axB.axvline(Rs2b, color=GREY, lw=1.6, ls=":")
    axB.plot([Rs1b], [floorB], "o", color="black", ms=7, zorder=5)
    axB.annotate("rate pinned at the floor —\nSUPPLY can shift a lot (QE/QT)\nand the rate barely moves",
                 xy=(Rs2b, floorB), xytext=(2.6, 3.4), fontsize=8.8, color="black",
                 arrowprops=dict(arrowstyle="->", color=GREY, lw=1.2))
    axB.annotate("", xy=(Rs2b, floorB + 0.02), xytext=(Rs1b, floorB + 0.02),
                 arrowprops=dict(arrowstyle="<->", color=C4, lw=1.6))
    axB.set_title("(b) Ample reserves (post-2008): the floor system", fontsize=11.5)
    axB.set_xlabel("Quantity of reserves")
    axB.set_ylim(-0.4, 6.0)
    axB.legend(loc="upper right", fontsize=9)
    axB.spines[["top", "right"]].set_visible(False)

    fig.suptitle("How the Fed sets the rate: the market for reserves (price, not quantity)",
                 fontsize=13)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    save(fig, 1)


# ---------------------------------------------------------------------------
# Fig 2 — The Taylor rule (conceptual). Prescribed nominal policy rate vs
#   inflation, slope 1.5 (Taylor principle), neutral at (target=2, r*+2),
#   clipped at the zero lower bound.
# ---------------------------------------------------------------------------
def fig2():
    pi = np.linspace(-1, 8, 300)
    rstar, target = 0.5, 2.0
    # Taylor (output gap = 0): i = r* + pi + 0.5(pi - target)  -> slope 1.5
    i = rstar + pi + 0.5 * (pi - target)
    i_clip = np.maximum(i, 0.0)

    fig, ax = plt.subplots(figsize=(9.4, 5.8))
    ax.plot(pi, i_clip, color=C1, lw=2.8, label="Taylor-rule policy rate")
    # 45-degree line (nominal rate == inflation => real rate constant)
    ax.plot(pi, pi, color=GREY, lw=1.4, ls="--", label="45° line (nominal = inflation)")

    # neutral point
    inrt = rstar + target
    ax.plot([target], [inrt], "o", color="black", ms=7, zorder=5)
    ax.annotate("neutral: inflation at 2% target\n→ rate = r* + target = 2.5%",
                xy=(target, inrt), xytext=(2.5, 1.0), fontsize=9,
                arrowprops=dict(arrowstyle="->", color="black", lw=1.2))

    # ZLB region
    ax.axhspan(-1.5, 0, color=C2, alpha=0.08)
    ax.axhline(0, color=C2, lw=1.2)
    ax.annotate("zero lower bound:\nrule wants a NEGATIVE rate\nbut can't cut below ~0\n→ QE / forward guidance",
                xy=(-0.3, 0), xytext=(-0.9, 2.6), fontsize=8.6, color=C2,
                arrowprops=dict(arrowstyle="->", color=C2, lw=1.2))

    ax.annotate("slope > 1 (the Taylor principle):\nraise the NOMINAL rate more than\n1-for-1 with inflation, so the REAL\nrate rises and actually tightens",
                xy=(6, rstar + 6 + 0.5 * (6 - target)),
                xytext=(3.1, 8.6), fontsize=8.8, color=C1, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=C1, lw=1.3))

    ax.set_xlabel("Inflation rate (%)")
    ax.set_ylabel("Prescribed policy rate (%)")
    ax.set_title("The Taylor rule: how the Fed's reaction function sets the rate")
    ax.set_xlim(-1, 8)
    ax.set_ylim(-1.5, 12)
    ax.legend(loc="upper left", fontsize=9)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(alpha=0.2)
    save(fig, 2)


# ---------------------------------------------------------------------------
# Fig 3 — The two tools over time: policy rate + Fed balance sheet, 2007-2026.
# ---------------------------------------------------------------------------
def fig3():
    yrs = np.array([2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016,
                    2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026])
    # Effective fed funds rate (approx annual avg, %).
    effr = np.array([5.0, 1.9, 0.16, 0.17, 0.10, 0.14, 0.11, 0.09, 0.13, 0.40,
                     1.00, 1.83, 2.16, 0.38, 0.08, 1.68, 5.03, 5.13, 4.30, 3.60])
    # Fed balance sheet (WALCL, approx, $ trillions).
    bs = np.array([0.9, 2.2, 2.2, 2.4, 2.9, 2.9, 4.0, 4.5, 4.5, 4.5,
                   4.4, 4.1, 3.8, 7.4, 8.8, 8.9, 7.7, 7.0, 6.6, 6.3])

    fig, ax = plt.subplots(figsize=(11.0, 5.6))
    ax.plot(yrs, effr, color=C2, lw=2.8, marker="o", ms=4,
            label="Policy rate (conventional tool)")
    ax.set_xlabel("Year")
    ax.set_ylabel("Effective fed funds rate (%)", color=C2)
    ax.tick_params(axis="y", labelcolor=C2)
    ax.set_ylim(0, 6.2)

    ax2 = ax.twinx()
    ax2.fill_between(yrs, bs, color=C1, alpha=0.15)
    ax2.plot(yrs, bs, color=C1, lw=2.4, ls="--",
             label="Fed balance sheet (unconventional tool)")
    ax2.set_ylabel("Fed balance sheet ($ trillions)", color=C1)
    ax2.tick_params(axis="y", labelcolor=C1)
    ax2.set_ylim(0, 10)

    # annotate episodes
    ax.axvspan(2008.7, 2015.5, color=GREY, alpha=0.08)
    ax.text(2011.6, 5.6, "ZLB: rate stuck at ~0\n→ QE does the work", fontsize=8.6,
            color=GREY, ha="center")
    ax.axvspan(2020.0, 2021.6, color=GREY, alpha=0.08)
    ax.annotate("2022–23: fastest\nhiking cycle in 40 yrs\n+ QT (balance sheet ↓)",
                xy=(2023, 5.03), xytext=(2019.4, 3.6), fontsize=8.6, color=C2,
                arrowprops=dict(arrowstyle="->", color=C2, lw=1.2))

    l1, la1 = ax.get_legend_handles_labels()
    l2, la2 = ax2.get_legend_handles_labels()
    ax.legend(l1 + l2, la1 + la2, loc="center left", fontsize=9,
              frameon=True, framealpha=0.95)
    ax.set_title("Two tools: the policy rate and the balance sheet (2007–2026)")
    ax.spines[["top"]].set_visible(False)
    ax2.spines[["top"]].set_visible(False)
    save(fig, 3)


# ---------------------------------------------------------------------------
# Fig 4 — Long and variable lags: stylised impulse response to a one-off hike.
# ---------------------------------------------------------------------------
def fig4():
    q = np.linspace(0, 16, 300)
    # output gap: dips, troughs ~q5, recovers (damped)
    outgap = -1.0 * np.exp(-((q - 5) ** 2) / 12) * (q > 0)
    # inflation: later, shallower, troughs ~q10
    infl = -0.6 * np.exp(-((q - 10) ** 2) / 20) * (q > 0)

    fig, ax = plt.subplots(figsize=(9.8, 5.4))
    ax.axhline(0, color="black", lw=1.0)
    ax.axvline(0, color=C2, lw=2.2)
    ax.text(0.2, 0.28, "rate hike\nat t = 0", color=C2, fontsize=9, fontweight="bold")

    ax.plot(q, outgap, color=C1, lw=2.8, label="Output gap (real activity)")
    ax.plot(q, infl, color=C4, lw=2.8, label="Inflation")

    ax.annotate("output responds first\n(trough ≈ 4–6 quarters)",
                xy=(5, outgap[np.argmin(abs(q - 5))]), xytext=(6.5, -0.55),
                fontsize=8.8, color=C1,
                arrowprops=dict(arrowstyle="->", color=C1, lw=1.2))
    ax.annotate("inflation responds later\n(trough ≈ 8–12 quarters)",
                xy=(10, infl[np.argmin(abs(q - 10))]), xytext=(10.6, -0.25),
                fontsize=8.8, color=C4,
                arrowprops=dict(arrowstyle="->", color=C4, lw=1.2))

    ax.set_xlabel("Quarters after the rate change")
    ax.set_ylabel("Response (deviation from baseline)")
    ax.set_title("'Long and variable lags': policy acts on next year's economy")
    ax.set_xlim(0, 16)
    ax.set_ylim(-1.2, 0.5)
    ax.legend(loc="lower right", fontsize=9.5)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(alpha=0.2)
    save(fig, 4)


if __name__ == "__main__":
    fig1(); fig2(); fig3(); fig4()
    print("done")
