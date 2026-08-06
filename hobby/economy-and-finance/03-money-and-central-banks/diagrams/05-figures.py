#!/usr/bin/env python3
"""Figures for Econ E03 §5 — The PBoC model (China: managed FX, capital controls, 强制结汇).

Editable source of truth for the committed SVGs (see agent-docs/diagrams.md).
Numbers are illustrative but chosen to match the real shape of the pictures
(annual/representative values for well-known public series):

  fig1 — THE COMPLETED TRILEMMA: the same triangle as §4, now with all three
         corners' regimes labelled and CHINA's side (independent rate + managed
         FX → give up free capital = capital controls) highlighted.
  fig2 — RMB / USD, 1994–2025 (plotted so LOWER = STRONGER yuan): the 8.28 hard
         peg, the 2005 managed-appreciation reform to a ~6.05 peak in 2014, the
         Aug-2015 8·11 devaluation, and the managed 6.3–7.3 range since.
  fig3 — CHINA'S FX RESERVES, 1994–2025 (USD tn): the compulsory-surrender-driven
         climb to a ~4tn peak in 2014, the ~1tn drawdown of 2014–16 defending the
         yuan, then a ~3.0–3.3tn plateau.
  fig4 — THE RRR (large banks, %), 2003–2025: up to a 21.5% peak in 2011 to
         sterilize the yuan created buying surrendered dollars, then cut steadily
         to ~9% as the machine runs in reverse.

Run with the project venv:

    .venv/bin/python hobby/economy-and-finance/03-money-and-central-banks/diagrams/05-figures.py

Outputs 05-the-pboc-model-figN.svg into this folder.
"""
import os
import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon

OUT = os.path.dirname(os.path.abspath(__file__))
BASE = "05-the-pboc-model"

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
# Fig 1 — The completed trilemma: China's corner highlighted.
# ---------------------------------------------------------------------------
def fig1():
    fig, ax = plt.subplots(figsize=(9.8, 7.6))
    A = np.array([0.5, 0.94])    # top: independent monetary policy
    B = np.array([0.06, 0.12])   # bottom-left: free capital mobility
    C = np.array([0.94, 0.12])   # bottom-right: exchange-rate stability
    tri = Polygon([A, B, C], closed=True, fill=False, edgecolor=GREY, lw=2.2)
    ax.add_patch(tri)

    ax.text(A[0], A[1] + 0.03, "Independent\nmonetary policy\n(set your own rate)",
            ha="center", va="bottom", fontsize=11, fontweight="bold")
    ax.text(B[0] - 0.01, B[1] - 0.03, "Free capital\nmobility",
            ha="center", va="top", fontsize=11, fontweight="bold")
    ax.text(C[0] + 0.01, C[1] - 0.03, "Exchange-rate\nstability (managed)",
            ha="center", va="top", fontsize=11, fontweight="bold")

    # Highlight CHINA's side = the RIGHT edge (A-C): independent rate + managed FX.
    ax.plot([A[0], C[0]], [A[1], C[1]], color=C2, lw=5.5, solid_capstyle="round",
            zorder=3)

    def midlabel(P, Q, txt, color, dy=0.0, dx=0.0, fs=9.6, weight="normal"):
        m = (P + Q) / 2
        ax.text(m[0] + dx, m[1] + dy, txt, ha="center", va="center", color=color,
                fontsize=fs, fontweight=weight,
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=color, lw=1.2))

    # Each SIDE keeps the two corners it joins, sacrifices the opposite corner.
    midlabel(A, B, "FLOAT (§3)\nFed · USA · Eurozone\n→ give up FX stability", C1,
             dx=-0.05, weight="bold")
    midlabel(B, C, "MANAGED FX + open capital (§4)\nMAS · Singapore / Hong Kong\n→ give up an independent rate",
             C3, dy=-0.055, weight="bold", fs=9.4)
    midlabel(A, C, "CAPITAL CONTROLS (§5)\nPBoC · CHINA\n→ give up free capital",
             C2, dx=0.055, weight="bold")

    ax.text(0.42, 0.40, "THE IMPOSSIBLE TRINITY\npick any TWO corners", ha="center",
            va="center", fontsize=12, color=GREY, fontweight="bold", style="italic")

    ax.set_xlim(-0.14, 1.16)
    ax.set_ylim(-0.08, 1.14)
    ax.axis("off")
    ax.set_title("The completed trilemma: Fed and MAS take two corners;\nChina (PBoC) takes the third — keep the rate + managed FX, give up free capital",
                 fontsize=12)
    save(fig, 1)


# ---------------------------------------------------------------------------
# Fig 2 — RMB/USD 1994-2025 (lower = stronger yuan).
# ---------------------------------------------------------------------------
def fig2():
    yrs = np.array([1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003,
                    2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013,
                    2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023,
                    2024, 2025])
    rate = np.array([8.62, 8.35, 8.31, 8.29, 8.28, 8.28, 8.28, 8.28, 8.28, 8.28,
                     8.28, 8.19, 7.97, 7.61, 6.95, 6.83, 6.77, 6.46, 6.31, 6.15,
                     6.14, 6.28, 6.64, 6.76, 6.62, 6.91, 6.90, 6.45, 6.73, 7.08,
                     7.19, 7.25])

    fig, ax = plt.subplots(figsize=(10.8, 5.8))
    ax.plot(yrs, rate, color=C2, lw=2.4, marker="o", ms=3.2)

    # Peg era shading
    ax.axvspan(1994, 2005.5, color=GREY, alpha=0.08)
    ax.text(1999.7, 6.6, "HARD PEG ~8.28\n(held through the\n1997 Asian crisis)",
            ha="center", fontsize=9, color=GREY, fontweight="bold")

    ax.annotate("2005: managed-appreciation\nreform begins",
                xy=(2005.5, 8.19), xytext=(2005.9, 7.55), fontsize=8.8, color=C1,
                fontweight="bold", arrowprops=dict(arrowstyle="->", color=C1, lw=1.2))
    ax.annotate("strongest ≈ 6.05 (2014)",
                xy=(2014, 6.14), xytext=(2007.4, 6.35), fontsize=8.8, color=C3,
                fontweight="bold", arrowprops=dict(arrowstyle="->", color=C3, lw=1.2))
    ax.annotate("Aug 2015: 8·11\ndevaluation",
                xy=(2015, 6.28), xytext=(2017.6, 6.15), fontsize=8.8, color=C4,
                fontweight="bold", arrowprops=dict(arrowstyle="->", color=C4, lw=1.3))
    ax.text(2021.6, 7.55, "managed range\n~6.3 – 7.3", ha="center", fontsize=8.8,
            color=C2, fontweight="bold")

    ax.set_xlabel("Year")
    ax.set_ylabel("RMB per USD   (LOWER = STRONGER yuan)")
    ax.set_title("The yuan, 1994–2025: hard peg → managed appreciation → 8·11 → managed float",
                 pad=12)
    ax.set_ylim(8.95, 5.7)  # inverted (stronger yuan UP) with headroom below the title
    ax.set_xlim(1993.5, 2025.5)
    ax.spines[["top"]].set_visible(False)
    ax.grid(alpha=0.25)
    save(fig, 2)


# ---------------------------------------------------------------------------
# Fig 3 — China FX reserves 1994-2025 (USD trillion).
# ---------------------------------------------------------------------------
def fig3():
    yrs = np.array([1994, 1996, 1998, 2000, 2002, 2004, 2005, 2006, 2007, 2008,
                    2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018,
                    2019, 2020, 2021, 2022, 2023, 2024, 2025])
    res = np.array([0.05, 0.11, 0.15, 0.17, 0.29, 0.61, 0.82, 1.07, 1.53, 1.95,
                    2.40, 2.85, 3.18, 3.31, 3.82, 3.84, 3.33, 3.01, 3.14, 3.07,
                    3.10, 3.22, 3.25, 3.13, 3.24, 3.20, 3.29])

    fig, ax = plt.subplots(figsize=(10.8, 5.8))
    ax.fill_between(yrs, 0, res, color=C1, alpha=0.16)
    ax.plot(yrs, res, color=C1, lw=2.4, marker="o", ms=3.2)

    ax.annotate("compulsory surrender funnels\nevery export USD to the PBoC\n→ reserves explode",
                xy=(2009, 2.40), xytext=(2000.4, 2.95), fontsize=8.8, color=C3,
                fontweight="bold", arrowprops=dict(arrowstyle="->", color=C3, lw=1.3))
    ax.annotate("peak ≈ 3.99tn (mid-2014)",
                xy=(2014, 3.84), xytext=(2011.2, 4.15), fontsize=9, color=C2,
                fontweight="bold", arrowprops=dict(arrowstyle="->", color=C2, lw=1.3))
    ax.annotate("~1tn drawdown, 2014–16:\nselling USD to DEFEND the yuan\nafter 8·11 (the finite-ammo side)",
                xy=(2016, 3.01), xytext=(2016.6, 1.7), fontsize=8.8, color=C4,
                fontweight="bold", arrowprops=dict(arrowstyle="->", color=C4, lw=1.3))

    ax.set_xlabel("Year")
    ax.set_ylabel("China official FX reserves (USD trillion)")
    ax.set_title("China's reserve pile: built by compulsory surrender, dented defending the yuan")
    ax.set_xlim(1993.5, 2025.5)
    ax.set_ylim(0, 4.5)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.25)
    save(fig, 3)


# ---------------------------------------------------------------------------
# Fig 4 — RRR (large banks, %) 2003-2025.
# ---------------------------------------------------------------------------
def fig4():
    yrs = np.array([2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012,
                    2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022,
                    2023, 2024, 2025])
    rrr = np.array([7.0, 7.5, 7.5, 9.0, 14.5, 15.5, 15.5, 18.5, 21.5, 20.0,
                    20.0, 20.0, 17.5, 17.0, 17.0, 14.5, 13.0, 12.5, 11.5, 11.0,
                    10.5, 9.5, 9.0])

    fig, ax = plt.subplots(figsize=(10.8, 5.6))
    ax.plot(yrs, rrr, color=C5, lw=2.6, marker="o", ms=3.4)
    ax.fill_between(yrs, 0, rrr, color=C5, alpha=0.10)

    ax.annotate("peak 21.5% (2011):\nlocking up the yuan created\nby buying surrendered USD\n= the STERILIZATION brake",
                xy=(2011, 21.5), xytext=(2004.4, 16.0), fontsize=8.8, color=C2,
                fontweight="bold", arrowprops=dict(arrowstyle="->", color=C2, lw=1.3))
    ax.annotate("the machine in reverse:\ninflows slow → cut the RRR\n= EASING (to ~9% by 2025)",
                xy=(2022, 11.0), xytext=(2016.4, 6.0), fontsize=8.8, color=C3,
                fontweight="bold", arrowprops=dict(arrowstyle="->", color=C3, lw=1.3))

    ax.set_xlabel("Year")
    ax.set_ylabel("Reserve requirement ratio, large banks (%)")
    ax.set_title("The RRR: China's sterilization brake (up to 2011), then its easing lever")
    ax.set_xlim(2002.5, 2025.5)
    ax.set_ylim(0, 24)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.25)
    save(fig, 4)


if __name__ == "__main__":
    fig1(); fig2(); fig3(); fig4()
    print("done")
