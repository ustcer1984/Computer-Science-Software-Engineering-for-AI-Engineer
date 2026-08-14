#!/usr/bin/env python3
"""Figures for Econ E04 §3 — The policy mix (fiscal + monetary together).

Editable source of truth for the committed SVGs (see agent-docs/diagrams.md).
Numbers are illustrative but chosen to match the real shape of the pictures
(representative values for well-known episodes / literature ranges):

  fig1 — THE POLICY-MIX MATRIX: the two levers span a 2x2 (fiscal stance x
         monetary stance). Each quadrant is a real historical regime — loose+loose
         (COVID 2020-21), loose fiscal + tight money (Reagan-Volcker 1980s), tight
         fiscal + loose money (Eurozone/UK austerity 2010s), tight+tight (the 1937
         mistake). The point: the MIX, not either lever alone, sets demand.
  fig2 — THE MULTIPLIER DEPENDS ON THE OTHER LEVER: the fiscal multiplier is near
         zero when the central bank offsets (normal times, full employment), around
         one when it accommodates, and large at the zero lower bound — the "monetary
         offset" story that decides whether fiscal stimulus works.
  fig3 — THE 1980s FIGHTING MIX (US, real data shape): a loose fiscal stance
         (widening Reagan deficits) run straight into a tight monetary stance
         (Volcker's high real rates) — the textbook case of the two levers pulling
         against each other, producing record real interest rates.
  fig4 — FISCAL DOMINANCE: as debt/GDP rises, the extra interest bill from a +1pp
         rate rise (≈ Δr x debt) grows, until the rate hike needed to fight
         inflation becomes fiscally intolerable — the channel by which high debt can
         subordinate monetary policy to the budget (Sargent-Wallace).

Run with the project venv:

    .venv/bin/python hobby/economy-and-finance/04-fiscal-policy/diagrams/03-figures.py

Outputs 03-the-policy-mix-figN.svg into this folder.
"""
import os
import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt
import numpy as np

OUT = os.path.dirname(os.path.abspath(__file__))
BASE = "03-the-policy-mix"

plt.rcParams.update({
    "font.size": 12,
    "axes.titlesize": 13,
    "axes.labelsize": 12,
    "svg.fonttype": "none",
    "figure.dpi": 100,
    "text.parse_math": False,
})

C1 = "#1f77b4"; C2 = "#d62728"; C3 = "#2ca02c"; C4 = "#ff7f0e"; C5 = "#9467bd"
GREY = "#555555"


def save(fig, n):
    path = os.path.join(OUT, f"{BASE}-fig{n}.svg")
    fig.savefig(path, format="svg", bbox_inches="tight")
    plt.close(fig)
    print("wrote", path)


# ---------------------------------------------------------------------------
# Fig 1 — The policy-mix matrix: fiscal stance x monetary stance.
# ---------------------------------------------------------------------------
def fig1():
    fig, ax = plt.subplots(figsize=(10.6, 7.4))

    # quadrant background tints
    ax.axhspan(0, 1, xmin=0.5, xmax=1.0, color=C2, alpha=0.06)   # loose+loose
    ax.axhspan(0, 1, xmin=0.0, xmax=0.5, color=C1, alpha=0.05)   # tight fiscal + loose money
    ax.axhspan(-1, 0, xmin=0.5, xmax=1.0, color=C4, alpha=0.06)  # loose fiscal + tight money
    ax.axhspan(-1, 0, xmin=0.0, xmax=0.5, color=GREY, alpha=0.08)  # tight+tight

    ax.axhline(0, color="black", lw=1.4)
    ax.axvline(0, color="black", lw=1.4)

    # quadrant labels (episode + effect), placed at quadrant centres
    ax.text(0.5, 0.72, "LOOSE fiscal  +  LOOSE monetary",
            ha="center", fontsize=10.5, fontweight="bold", color=C2)
    ax.text(0.5, 0.52, "both levers push demand the SAME way\n→ maximum stimulus (and overheating risk)\n"
            "COVID 2020–21 (transfers + QE) · 1970s Great Inflation",
            ha="center", fontsize=8.8, color=GREY)

    ax.text(0.5, -0.30, "LOOSE fiscal  +  TIGHT monetary",
            ha="center", fontsize=10.5, fontweight="bold", color=C4)
    ax.text(0.5, -0.52, "the levers FIGHT → high real rates,\nstrong currency, crowding out\n"
            "Reagan tax cuts + Volcker rate hikes (early 1980s)",
            ha="center", fontsize=8.8, color=GREY)

    ax.text(-0.5, 0.72, "TIGHT fiscal  +  LOOSE monetary",
            ha="center", fontsize=10.5, fontweight="bold", color=C1)
    ax.text(-0.5, 0.52, "austerity, with the central bank trying\nto offset it → often a weak recovery\n"
            "Eurozone / UK austerity + QE (2010–2015)",
            ha="center", fontsize=8.8, color=GREY)

    ax.text(-0.5, -0.30, "TIGHT fiscal  +  TIGHT monetary",
            ha="center", fontsize=10.5, fontweight="bold", color=GREY)
    ax.text(-0.5, -0.52, "both levers pull demand DOWN\n→ deep contraction (usually a mistake)\n"
            "the 1937 'Roosevelt recession' · disinflation",
            ha="center", fontsize=8.8, color=GREY)

    # axis arrows / labels
    ax.annotate("", xy=(1.02, 0), xytext=(-1.02, 0),
                arrowprops=dict(arrowstyle="->", color="black", lw=1.4))
    ax.annotate("", xy=(0, 1.02), xytext=(0, -1.02),
                arrowprops=dict(arrowstyle="->", color="black", lw=1.4))
    ax.text(1.05, -0.06, "FISCAL:\nloose →", fontsize=9, fontweight="bold", va="top")
    ax.text(-1.05, -0.06, "← tight", fontsize=9, fontweight="bold", va="top", ha="left")
    ax.text(0.03, 1.05, "MONETARY: loose ↑", fontsize=9, fontweight="bold")
    ax.text(0.03, -1.08, "tight ↓", fontsize=9, fontweight="bold")

    ax.set_xlim(-1.15, 1.2)
    ax.set_ylim(-1.18, 1.18)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_title("The policy-mix matrix: it's the COMBINATION of the two levers that sets demand",
                 fontsize=12.5)
    save(fig, 1)


# ---------------------------------------------------------------------------
# Fig 2 — The fiscal multiplier depends on the monetary regime.
# ---------------------------------------------------------------------------
def fig2():
    labels = ["CB actively\nOFFSETS\n(tightens to hold\ninflation at target,\nfull employment)",
              "CB NEUTRAL /\naccommodates\n(holds rates,\nlets stimulus\npass through)",
              "ZERO LOWER BOUND\n(rates stuck at 0,\nCB cannot offset —\ndeep slump)"]
    lo = [0.0, 0.6, 1.4]
    hi = [0.5, 1.0, 2.1]
    mid = [(a + b) / 2 for a, b in zip(lo, hi)]
    colors = [C2, C4, C3]

    fig, ax = plt.subplots(figsize=(10.4, 6.2))
    x = np.arange(3)
    for i in range(3):
        ax.bar(x[i], hi[i] - lo[i], bottom=lo[i], width=0.5, color=colors[i], alpha=0.85)
        ax.text(x[i], hi[i] + 0.06, f"{lo[i]:.1f}–{hi[i]:.1f}", ha="center",
                fontsize=10, fontweight="bold", color=colors[i])

    ax.axhline(1.0, color=GREY, ls="--", lw=1.1)
    ax.text(2.46, 1.03, "multiplier = 1\n(a dollar of spending →\na dollar of output)",
            fontsize=8.2, color=GREY, va="bottom", ha="right")

    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=8.8)
    ax.set_ylabel("Fiscal multiplier  (Δ output per $1 of fiscal stimulus)")
    ax.set_title("Does fiscal stimulus work? It depends on what the OTHER lever does")
    ax.set_ylim(0, 2.4)
    ax.grid(axis="y", alpha=0.25)
    ax.spines[["top", "right"]].set_visible(False)
    ax.annotate("'monetary offset':\nthe multiplier collapses when the\ncentral bank leans against the stimulus",
                xy=(0, 0.25), xytext=(0.35, 1.55), fontsize=8.6, color=C2, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=C2, lw=1.2))
    save(fig, 2)


# ---------------------------------------------------------------------------
# Fig 3 — The 1980s fighting mix (US, representative annual data shape).
# ---------------------------------------------------------------------------
def fig3():
    yrs = list(range(1977, 1993))
    # representative real fed funds rate (nominal minus CPI inflation), % — Volcker tightening
    real_ffr = [-1.5, -0.6, 0.3, 1.4, 6.2, 5.6, 4.8, 6.6, 4.6, 3.9, 3.4, 3.6, 4.6, 3.0, 1.4, 0.4]
    # federal budget deficit as % of GDP (positive = deficit) — Reagan fiscal expansion
    deficit = [2.6, 2.5, 1.6, 2.6, 2.5, 3.9, 5.9, 4.7, 5.0, 4.9, 3.1, 3.0, 2.7, 3.7, 4.4, 4.5]

    fig, ax = plt.subplots(figsize=(11.0, 6.1))
    ax.bar([y + 0.0 for y in yrs], deficit, width=0.6, color=C1, alpha=0.35,
           label="Federal budget deficit (% of GDP) — LOOSE fiscal")
    ax.set_ylabel("Budget deficit (% of GDP)", color=C1)
    ax.tick_params(axis="y", labelcolor=C1)
    ax.set_ylim(0, 7.5)

    ax2 = ax.twinx()
    ax2.plot(yrs, real_ffr, color=C2, lw=2.6, marker="o", ms=4,
             label="Real fed funds rate (%) — TIGHT monetary")
    ax2.set_ylabel("Real policy interest rate (%)", color=C2)
    ax2.tick_params(axis="y", labelcolor=C2)
    ax2.set_ylim(-3, 8)
    ax2.axhline(0, color=C2, lw=0.8, ls=":", alpha=0.6)

    ax2.annotate("Volcker shock:\nreal rates to ~6%\nto break inflation",
                 xy=(1981, 6.2), xytext=(1978.7, 7.1), ha="left", fontsize=8.6, color=C2,
                 fontweight="bold", arrowprops=dict(arrowstyle="->", color=C2, lw=1.2))
    ax.annotate("Reagan deficits\nwiden at the same time",
                xy=(1985, 5.0), xytext=(1986.6, 6.9), ha="left", fontsize=8.6, color=C1,
                fontweight="bold", arrowprops=dict(arrowstyle="->", color=C1, lw=1.2))

    ax.set_xlabel("Year")
    ax.set_title("The 1980s 'fighting mix' (US): loose fiscal + tight monetary → record real rates")
    ax.spines[["top"]].set_visible(False)
    ax2.spines[["top"]].set_visible(False)
    # merge legends
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, fontsize=9, loc="lower center")
    save(fig, 3)


# ---------------------------------------------------------------------------
# Fig 4 — Fiscal dominance: monetary room shrinks as debt rises.
# ---------------------------------------------------------------------------
def fig4():
    debt = np.linspace(0, 260, 400)          # debt/GDP, %
    hit = debt / 100.0 * 1.0                  # extra interest bill from +1pp, % of GDP ≈ Δr × debt

    fig, ax = plt.subplots(figsize=(10.6, 6.1))
    ax.plot(debt, hit, color=C2, lw=2.8)
    ax.fill_between(debt, 0, hit, where=(debt >= 150), color=C2, alpha=0.10)

    # reference debt levels
    for x0, name, yo in [(35, "low-debt EM", 0.0), (100, "USA / UK", 0.0),
                         (135, "Italy", 0.0), (255, "Japan", 0.0)]:
        ax.plot([x0, x0], [0, x0 / 100.0], color=GREY, ls=":", lw=1.0)
        ax.plot(x0, x0 / 100.0, "o", color=GREY, ms=5)
        ax.text(x0, x0 / 100.0 + 0.08, name, ha="center", fontsize=8.4, color=GREY)

    ax.axhspan(1.5, 2.8, color=C2, alpha=0.07)
    ax.text(20, 2.35, "FISCAL-DOMINANCE ZONE\na +1pp hike now costs >1.5% of GDP a year in interest —\n"
            "raising rates to fight inflation starts to threaten solvency,\n"
            "so the budget begins to CONSTRAIN monetary policy",
            fontsize=8.6, color=C2, fontweight="bold", va="center")

    ax.set_xlabel("Government debt (% of GDP)")
    ax.set_ylabel("Extra interest bill from a +1pp rate rise (% of GDP)")
    ax.set_title("Fiscal dominance: the more debt, the less room the central bank has to hike")
    ax.set_xlim(0, 265)
    ax.set_ylim(0, 2.8)
    ax.grid(alpha=0.22)
    ax.spines[["top", "right"]].set_visible(False)
    ax.text(150, 0.35, "extra interest  ≈  Δr × debt\n(so the slope IS the debt ratio)",
            fontsize=8.6, color=GREY, style="italic",
            bbox=dict(boxstyle="round,pad=0.35", fc="white", ec=GREY, lw=1.0))
    save(fig, 4)


if __name__ == "__main__":
    fig1(); fig2(); fig3(); fig4()
    print("done")
