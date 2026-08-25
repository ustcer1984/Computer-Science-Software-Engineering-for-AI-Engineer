#!/usr/bin/env python3
"""Figures for Econ E05 §1 — Trade & comparative advantage.

Editable source of truth for the committed SVGs (see agent-docs/diagrams.md).
Numbers are illustrative but chosen to match the real shape / the textbook logic:

  fig1 — COMPARATIVE ADVANTAGE GROWS THE PIE: a symmetric two-country, two-good
         example. Left: the opportunity costs that DRIVE trade (each country is the
         cheaper producer of one good). Right: world output of BOTH goods rises when
         each country specializes and they trade.
  fig2 — CONSUMING BEYOND THE PPF: even the country that is worse at everything gains.
         Its production frontier is a straight line; trading at a world price lets it
         consume at a point OUTSIDE its own frontier — the gains-from-trade wedge.
  fig3 — WINNERS AND LOSERS (the China shock): total gains, concentrated losses. US
         manufacturing employment falls as China's share of US imports rises after its
         2001 WTO entry — the distributional cost trade theory used to gloss over.
  fig4 — THE TARIFF'S DEADWEIGHT LOSS: a tariff raises the domestic price, helping
         producers (a) and raising revenue (c) but costing consumers more — the two
         triangles (b + d) are pure deadweight loss (ties to E01 §3).

Run with the project venv:

    .venv/bin/python hobby/economy-and-finance/05-global-economy/diagrams/01-figures.py

Outputs 01-trade-and-comparative-advantage-figN.svg into this folder.
"""
import os
import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt
import numpy as np

OUT = os.path.dirname(os.path.abspath(__file__))
BASE = "01-trade-and-comparative-advantage"

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
# Fig 1 — Comparative advantage grows the pie (symmetric 2x2 example).
# Home: all-in 100 computers OR 50 wheat  (opp cost 1 computer = 0.5 wheat)
# Foreign: all-in 50 computers OR 100 wheat (opp cost 1 computer = 2 wheat)
# ---------------------------------------------------------------------------
def fig1():
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(12.4, 5.8))

    # --- Left: opportunity costs (the driver) ---
    groups = ["Opp. cost of\n1 COMPUTER\n(wheat given up)", "Opp. cost of\n1 WHEAT\n(computers given up)"]
    home = [0.5, 2.0]
    frgn = [2.0, 0.5]
    x = np.arange(2); w = 0.34
    axL.bar(x - w/2, home, w, color=C1, label="Home")
    axL.bar(x + w/2, frgn, w, color=C4, label="Foreign")
    for xi, (h, f) in enumerate(zip(home, frgn)):
        axL.text(xi - w/2, h + 0.05, f"{h}", ha="center", fontsize=9.5, fontweight="bold", color=C1)
        axL.text(xi + w/2, f + 0.05, f"{f}", ha="center", fontsize=9.5, fontweight="bold", color=C4)
    axL.set_xticks(x); axL.set_xticklabels(groups, fontsize=9)
    axL.set_ylabel("Opportunity cost (units of the other good)")
    axL.set_title("What DRIVES trade: opportunity cost, not who's 'better'")
    axL.set_ylim(0, 2.5)
    axL.legend(fontsize=10, loc="upper center")
    axL.grid(axis="y", alpha=0.25)
    axL.spines[["top", "right"]].set_visible(False)
    axL.text(0, -0.9, "Home is the cheaper COMPUTER maker · Foreign the cheaper WHEAT maker\n"
             "→ each specializes where its opportunity cost is LOWEST",
             fontsize=8.7, color=GREY, ha="left")

    # --- Right: world output rises with specialization ---
    labels = ["Computers", "Wheat"]
    autarky = [75, 75]     # Home 50+ Foreign 25 = 75 ; Home 25 + Foreign 50 = 75
    trade = [100, 100]     # Home all computers (100) ; Foreign all wheat (100)
    x2 = np.arange(2)
    axR.bar(x2 - w/2, autarky, w, color=GREY, alpha=0.6, label="No trade (each splits its labour)")
    axR.bar(x2 + w/2, trade, w, color=C3, label="Specialize + trade")
    for xi, (a, tr) in enumerate(zip(autarky, trade)):
        axR.text(xi - w/2, a + 1.5, f"{a}", ha="center", fontsize=9.5, fontweight="bold", color=GREY)
        axR.text(xi + w/2, tr + 1.5, f"{tr}", ha="center", fontsize=9.5, fontweight="bold", color=C3)
    axR.annotate("+33%", xy=(0 + w/2, 100), xytext=(0 + w/2, 112), ha="center",
                 fontsize=10, color=C3, fontweight="bold")
    axR.annotate("+33%", xy=(1 + w/2, 100), xytext=(1 + w/2, 112), ha="center",
                 fontsize=10, color=C3, fontweight="bold")
    axR.set_xticks(x2); axR.set_xticklabels(labels, fontsize=10)
    axR.set_ylabel("Total WORLD output (units)")
    axR.set_title("The pie grows: same labour, more of BOTH goods")
    axR.set_ylim(0, 125)
    axR.legend(fontsize=9, loc="lower center")
    axR.grid(axis="y", alpha=0.25)
    axR.spines[["top", "right"]].set_visible(False)

    fig.suptitle("Comparative advantage: specialization by opportunity cost makes both sides richer",
                 fontsize=13, y=1.02)
    save(fig, 1)


# ---------------------------------------------------------------------------
# Fig 2 — Consuming beyond the PPF (the country worse at everything still gains).
# Foreign PPF: 50 computers OR 100 wheat (straight line, opp cost 1 comp = 2 wheat).
# World price 1 computer = 1 wheat. Foreign specializes in wheat (0,100), trades.
# ---------------------------------------------------------------------------
def fig2():
    fig, ax = plt.subplots(figsize=(9.6, 7.0))

    # PPF: from (comp=50, wheat=0) to (comp=0, wheat=100)
    ax.plot([50, 0], [0, 100], color=C1, lw=2.6, label="Production frontier (what it can MAKE alone)")
    # autarky consumption point on PPF
    ax.plot(25, 50, "o", color=C1, ms=9)
    ax.annotate("A: no-trade\n(make & consume 25 computers, 50 wheat)",
                xy=(25, 50), xytext=(27, 62), fontsize=8.8, color=C1,
                arrowprops=dict(arrowstyle="->", color=C1, lw=1.1))
    # production under trade: full specialization in wheat (0, 100)
    ax.plot(0, 100, "s", color=C3, ms=9)
    ax.annotate("P: specialize\n(make 100 wheat, 0 computers)",
                xy=(0, 100), xytext=(6, 104), fontsize=8.8, color=C3,
                arrowprops=dict(arrowstyle="->", color=C3, lw=1.1))
    # trade line: from (0,100) slope -1 (world price 1 comp = 1 wheat)
    ax.plot([0, 60], [100, 40], color=C3, lw=2.4, ls="--",
            label="Trade line (world price: 1 computer = 1 wheat)")
    # consumption under trade beyond PPF
    ax.plot(40, 60, "*", color=C2, ms=17)
    ax.annotate("C: consume 40 computers + 60 wheat\n— BEYOND the frontier!",
                xy=(40, 60), xytext=(24, 24), fontsize=9.2, color=C2, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=C2, lw=1.3))

    # gains-from-trade wedge (between PPF and trade line)
    ax.fill([0, 50, 60, 0], [100, 0, 40, 100], color=C3, alpha=0.08)
    ax.text(30, 82, "gains from\ntrade", fontsize=10, color=C3, fontweight="bold", ha="center")

    ax.set_xlabel("Computers")
    ax.set_ylabel("Wheat")
    ax.set_title("Even a country that's worse at everything gains: trade lets it consume OUTSIDE its frontier")
    ax.set_xlim(0, 66)
    ax.set_ylim(0, 115)
    ax.legend(fontsize=9, loc="upper right")
    ax.grid(alpha=0.22)
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, 2)


# ---------------------------------------------------------------------------
# Fig 3 — Winners and losers: the China shock.
# ---------------------------------------------------------------------------
def fig3():
    yrs = [1970, 1980, 1990, 1995, 2000, 2001, 2005, 2010, 2015, 2018, 2020]
    mfg = [17.8, 19.4, 17.7, 17.2, 17.3, 16.4, 14.2, 11.5, 12.3, 12.8, 12.2]     # US mfg employment, millions
    chn = [1, 2, 3, 6, 8, 9, 15, 19, 21, 21, 19]                                  # China % of US goods imports

    fig, ax = plt.subplots(figsize=(11.0, 6.1))
    ax.plot(yrs, mfg, color=C2, lw=2.7, marker="o", ms=4, label="US manufacturing employment (millions)")
    ax.set_ylabel("US manufacturing employment (millions)", color=C2)
    ax.tick_params(axis="y", labelcolor=C2)
    ax.set_ylim(8, 21)

    ax2 = ax.twinx()
    ax2.plot(yrs, chn, color=C1, lw=2.4, marker="s", ms=4, ls="--",
             label="China's share of US goods imports (%)")
    ax2.set_ylabel("China's share of US goods imports (%)", color=C1)
    ax2.tick_params(axis="y", labelcolor=C1)
    ax2.set_ylim(0, 26)

    ax.axvline(2001, color=GREY, ls=":", lw=1.2)
    ax.annotate("China joins\nthe WTO (2001)", xy=(2001, 10.0), xytext=(1984, 13.4),
                fontsize=8.8, color=GREY, ha="center",
                arrowprops=dict(arrowstyle="->", color=GREY, lw=1.1))
    ax.annotate("the 'China shock': ~1–2M mfg jobs lost,\nconcentrated in specific towns\n(Autor–Dorn–Hanson)",
                xy=(2009, 11.5), xytext=(2004.5, 15.6), fontsize=8.6, color=C2, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=C2, lw=1.2))

    ax.set_xlabel("Year")
    ax.set_title("Winners and losers: aggregate gains from trade, but concentrated local losses")
    ax.spines[["top"]].set_visible(False)
    ax2.spines[["top"]].set_visible(False)
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, fontsize=9, loc="upper left")
    save(fig, 3)


# ---------------------------------------------------------------------------
# Fig 4 — The tariff's deadweight loss (ties to E01 §3).
# Demand P = 100 - Q ; Supply P = 20 + Q ; world price Pw = 40 ; tariff t = 15.
# ---------------------------------------------------------------------------
def fig4():
    Q = np.linspace(0, 80, 200)
    D = 100 - Q
    S = 20 + Q
    Pw, t = 40, 15
    Pt = Pw + t
    Qs1, Qd1 = Pw - 20, 100 - Pw          # 20, 60
    Qs2, Qd2 = Pt - 20, 100 - Pt          # 35, 45

    fig, ax = plt.subplots(figsize=(10.4, 6.6))
    ax.plot(Q, D, color=C1, lw=2.4, label="Domestic demand")
    ax.plot(Q, S, color=C3, lw=2.4, label="Domestic supply")
    ax.axhline(Pw, color=GREY, lw=1.6, ls="--")
    ax.axhline(Pt, color=C2, lw=1.6, ls="--")
    ax.text(78, Pw - 3, "world price Pw", color=GREY, fontsize=9, ha="right")
    ax.text(78, Pt + 1.5, "price with tariff  Pw + t", color=C2, fontsize=9, ha="right")

    # area a — producer surplus gain (between Pw and Pt, left of supply)
    ax.fill([0, Qs1, Qs2, 0], [Pw, Pw, Pt, Pt], color=C3, alpha=0.25)
    ax.text(9, 48, "a", fontsize=12, fontweight="bold", color=C3)
    # area b — production DWL triangle
    ax.fill([Qs1, Qs2, Qs1], [Pw, Pt, Pt], color=C2, alpha=0.35)
    ax.text(26.5, 52.5, "b", fontsize=11, fontweight="bold", color=C2)
    # area c — government tariff revenue
    ax.fill([Qs2, Qd2, Qd2, Qs2], [Pw, Pw, Pt, Pt], color=GREY, alpha=0.30)
    ax.text(40, 47.5, "c", fontsize=12, fontweight="bold", color="black")
    # area d — consumption DWL triangle
    ax.fill([Qd2, Qd1, Qd2], [Pt, Pw, Pw], color=C2, alpha=0.35)
    ax.text(46.5, 47, "d", fontsize=11, fontweight="bold", color=C2)

    for qx, py in [(Qs1, Pw), (Qs2, Pt), (Qd2, Pt), (Qd1, Pw)]:
        ax.plot([qx, qx], [0, py], color="grey", lw=0.7, ls=":")

    ax.set_xlabel("Quantity")
    ax.set_ylabel("Price")
    ax.set_title("A tariff's deadweight loss: producers gain (a) + revenue (c),\nbut consumers lose a+b+c+d → b + d is burned")
    ax.set_xlim(0, 80)
    ax.set_ylim(20, 100)
    ax.legend(fontsize=9.5, loc="upper right")
    ax.spines[["top", "right"]].set_visible(False)
    ax.text(1.5, 24,
            "a = producer gain   ·   c = govt revenue   ·   b + d = DEADWEIGHT LOSS (pure waste)\n"
            "consumers lose a + b + c + d — more than everyone else gains",
            fontsize=8.7, color=GREY,
            bbox=dict(boxstyle="round,pad=0.35", fc="white", ec=GREY, lw=1.0))
    save(fig, 4)


if __name__ == "__main__":
    fig1(); fig2(); fig3(); fig4()
    print("done")
