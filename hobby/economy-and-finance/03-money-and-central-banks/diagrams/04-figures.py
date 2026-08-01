#!/usr/bin/env python3
"""Figures for Econ E03 §4 — The MAS model (exchange-rate-based monetary policy).

Editable source of truth for the committed SVGs (see agent-docs/diagrams.md).
Numbers are illustrative but chosen to match the real shape of the pictures:

  fig1 — THE IMPOSSIBLE TRINITY (trilemma): a triangle whose three corners are
         {independent monetary policy, free capital mobility, exchange-rate
         stability}. You can pick any TWO; each side sacrifices the opposite
         corner. Singapore sits on the "free capital + managed FX" side, giving
         up an independent interest rate.
  fig2 — THE BBC POLICY BAND (Basket, Band, Crawl): the SGD NEER managed inside a
         sloping band with three levers — SLOPE (appreciation crawl), WIDTH
         (± band), and LEVEL (a discrete re-centring).
  fig3 — WHY FX, NOT RATES: trade openness (exports + imports as a share of GDP)
         across economies — Singapore trades ~3x its GDP, so import prices
         dominate inflation and the exchange rate is the natural lever.
  fig4 — SAME JOB, DIFFERENT LEVERS (2020-24): the Fed fought the post-COVID
         inflation surge by raising the policy RATE; the MAS fought the same
         surge by steepening the SGD NEER appreciation (a stronger currency).

Run with the project venv:

    .venv/bin/python hobby/economy-and-finance/03-money-and-central-banks/diagrams/04-figures.py

Outputs 04-the-mas-model-figN.svg into this folder.
"""
import os
import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon

OUT = os.path.dirname(os.path.abspath(__file__))
BASE = "04-the-mas-model"

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
# Fig 1 — The impossible trinity (Mundell-Fleming trilemma).
# ---------------------------------------------------------------------------
def fig1():
    fig, ax = plt.subplots(figsize=(9.6, 7.4))
    # Triangle vertices
    A = np.array([0.5, 0.94])    # top: independent monetary policy
    B = np.array([0.06, 0.12])   # bottom-left: free capital mobility
    C = np.array([0.94, 0.12])   # bottom-right: exchange-rate stability
    tri = Polygon([A, B, C], closed=True, fill=False, edgecolor=GREY, lw=2.2)
    ax.add_patch(tri)

    # Vertex labels
    ax.text(A[0], A[1] + 0.03, "Independent\nmonetary policy\n(set your own rate)",
            ha="center", va="bottom", fontsize=11, fontweight="bold")
    ax.text(B[0] - 0.01, B[1] - 0.03, "Free capital\nmobility",
            ha="center", va="top", fontsize=11, fontweight="bold")
    ax.text(C[0] + 0.01, C[1] - 0.03, "Exchange-rate\nstability (managed)",
            ha="center", va="top", fontsize=11, fontweight="bold")

    # Highlight the Singapore side (B-C, the bottom edge)
    ax.plot([B[0], C[0]], [B[1], C[1]], color=C2, lw=5, solid_capstyle="round",
            zorder=3)

    def midlabel(P, Q, txt, color, dy=0.0, dx=0.0, fs=9.6, weight="normal"):
        m = (P + Q) / 2
        ax.text(m[0] + dx, m[1] + dy, txt, ha="center", va="center", color=color,
                fontsize=fs, fontweight=weight,
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=color, lw=1.2))

    # Each SIDE = keep the two corners it joins, SACRIFICE the opposite corner.
    midlabel(A, B, "FLOATING rate\n(USA, Eurozone)\n→ give up FX stability", C1,
             dx=-0.03, weight="bold")
    midlabel(A, C, "CAPITAL CONTROLS\n(China, historically)\n→ give up free capital", C5,
             dx=0.03, weight="bold")
    midlabel(B, C, "MANAGED FX + open capital\n= SINGAPORE / Hong Kong\n→ give up an independent rate",
             C2, dy=-0.055, weight="bold", fs=10)

    ax.text(0.5, 0.36, "THE IMPOSSIBLE TRINITY\npick any TWO sides", ha="center",
            va="center", fontsize=12.5, color=GREY, fontweight="bold", style="italic")

    ax.set_xlim(-0.12, 1.12)
    ax.set_ylim(-0.08, 1.12)
    ax.axis("off")
    ax.set_title("The trilemma: Singapore keeps open capital + a managed currency,\nso it gives up an independent interest rate",
                 fontsize=12.5)
    save(fig, 1)


# ---------------------------------------------------------------------------
# Fig 2 — The BBC policy band: slope, width, level (re-centring).
# ---------------------------------------------------------------------------
def fig2():
    t = np.linspace(0, 48, 400)
    # midpoint: gentle appreciation, then a re-centre up + steeper slope (tighten)
    mid = np.where(t < 20, 100 + 0.10 * t, 100 + 0.10 * 20 + 2.2 + 0.28 * (t - 20))
    width = 1.6
    upper, lower = mid + width, mid - width

    # actual SGD NEER: wiggle inside the band (deterministic pseudo-noise)
    wig = 1.05 * np.sin(t / 2.3) + 0.5 * np.sin(t / 0.7 + 1)
    neer = mid + 0.55 * wig
    neer = np.clip(neer, lower + 0.15, upper - 0.15)

    fig, ax = plt.subplots(figsize=(10.6, 5.8))
    ax.fill_between(t, lower, upper, color=C1, alpha=0.14, label="Policy BAND (± width)")
    ax.plot(t, mid, color=C1, lw=1.6, ls="--", label="Band mid-point")
    ax.plot(t, neer, color=C2, lw=2.2, label="SGD NEER (actual)")

    # Re-centre marker at t=20
    ax.axvline(20, color=GREY, ls=":", lw=1.2)
    ax.annotate("LEVEL: a discrete\nre-centring (shift the\nwhole band up)",
                xy=(20, mid[np.argmin(abs(t - 20))] + 0.2), xytext=(9, 108.6),
                fontsize=8.8, color=GREY, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=GREY, lw=1.3))
    # Slope annotation (steeper after tighten)
    ax.annotate("SLOPE: the appreciation crawl\n(steepen it to TIGHTEN —\nfaster-rising SGD = cheaper imports)",
                xy=(34, mid[np.argmin(abs(t - 34))]), xytext=(24, 101.2),
                fontsize=8.8, color=C1, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=C1, lw=1.3))
    # Width annotation
    ax.annotate("", xy=(6, upper[np.argmin(abs(t - 6))]),
                xytext=(6, lower[np.argmin(abs(t - 6))]),
                arrowprops=dict(arrowstyle="<->", color=C4, lw=1.6))
    ax.text(6.6, lower[np.argmin(abs(t - 6))] + width, "WIDTH:\n± band\n(absorbs\nvolatility)",
            fontsize=8.6, color=C4, va="center", fontweight="bold")

    ax.set_xlabel("Time (months)")
    ax.set_ylabel("SGD NEER index  (higher = stronger SGD = appreciation)")
    ax.set_title("The MAS 'BBC' policy band: Basket · Band · Crawl (slope, width, level)")
    ax.set_xlim(0, 48)
    ax.set_ylim(97.5, 111)
    ax.legend(loc="lower right", fontsize=9)
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, 2)


# ---------------------------------------------------------------------------
# Fig 3 — Why FX, not rates: trade openness = (exports + imports) / GDP.
# ---------------------------------------------------------------------------
def fig3():
    econ = ["Singapore", "Hong Kong", "Netherlands", "Germany", "S. Korea",
            "China", "Japan", "USA"]
    openness = [320, 350, 155, 90, 88, 37, 37, 25]  # approx % of GDP
    colors = [C2 if e == "Singapore" else C1 for e in econ]

    order = np.argsort(openness)[::-1]
    econ = [econ[i] for i in order]
    openness = [openness[i] for i in order]
    colors = [colors[i] for i in order]

    fig, ax = plt.subplots(figsize=(10.2, 5.6))
    bars = ax.bar(econ, openness, color=colors, width=0.66)
    for b, v in zip(bars, openness):
        ax.text(b.get_x() + b.get_width() / 2, v + 5, f"{v}%", ha="center",
                fontsize=9.5, fontweight="bold")
    ax.axhline(100, color=GREY, ls="--", lw=1.0)
    ax.text(7.4, 104, "trade = 100% of GDP", fontsize=8.4, color=GREY, ha="right")

    ax.annotate("Singapore trades ~3x its GDP:\nalmost everything is imported, so the\nIMPORT PRICE (set by the exchange rate)\ndrives inflation → target the currency",
                xy=(0, 320), xytext=(1.4, 250), fontsize=9, color=C2,
                fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=C2, lw=1.4))
    ax.annotate("the US is large & relatively closed\n(trade ~25%): demand is domestic,\nso the INTEREST RATE is the lever",
                xy=(7, 25), xytext=(4.2, 120), fontsize=8.8, color=C1,
                arrowprops=dict(arrowstyle="->", color=C1, lw=1.2))

    ax.set_ylabel("Trade openness: (exports + imports) / GDP  (%)")
    ax.set_title("Why Singapore targets the exchange rate: it is an ultra-open economy")
    ax.set_ylim(0, 380)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.25)
    save(fig, 3)


# ---------------------------------------------------------------------------
# Fig 4 — Same job, different levers (2020-2024): Fed rate vs MAS SGD NEER.
# ---------------------------------------------------------------------------
def fig4():
    yrs = np.array([2020.0, 2020.5, 2021.0, 2021.5, 2022.0, 2022.5, 2023.0,
                    2023.5, 2024.0, 2024.5])
    fed = np.array([0.25, 0.1, 0.1, 0.1, 0.4, 1.7, 4.6, 5.1, 5.3, 4.9])
    # Illustrative SGD NEER index: flat, then steady appreciation as MAS tightens
    neer = np.array([99.0, 99.2, 99.6, 100.2, 101.2, 102.6, 104.2, 105.4,
                     106.0, 106.2])

    fig, ax = plt.subplots(figsize=(10.6, 5.6))
    # inflation surge backdrop
    ax.axvspan(2021.5, 2023.2, color=C4, alpha=0.10)
    ax.text(2022.35, 5.6, "post-COVID inflation surge\n(both are fighting THIS)",
            ha="center", fontsize=8.8, color=C4, fontweight="bold")

    ax.plot(yrs, fed, color=C2, lw=2.8, marker="o", ms=4,
            label="Fed: policy RATE (%)  — left axis")
    ax.set_ylabel("US federal funds rate (%)", color=C2)
    ax.tick_params(axis="y", labelcolor=C2)
    ax.set_ylim(0, 6.4)
    ax.set_xlabel("Year")

    ax2 = ax.twinx()
    ax2.plot(yrs, neer, color=C1, lw=2.8, marker="s", ms=4,
             label="MAS: SGD NEER (stronger SGD)  — right axis")
    ax2.set_ylabel("SGD NEER index (higher = stronger SGD)", color=C1)
    ax2.tick_params(axis="y", labelcolor=C1)
    ax2.set_ylim(98, 108)

    ax.annotate("Fed: RAISE the rate", xy=(2023.0, 4.6), xytext=(2020.7, 4.4),
                fontsize=9, color=C2, arrowprops=dict(arrowstyle="->", color=C2, lw=1.2))
    ax2.annotate("MAS: STEEPEN the SGD\nappreciation (5 tightenings,\n2 off-cycle)",
                 xy=(2023.0, 104.2), xytext=(2021.5, 99.4), fontsize=8.8, color=C1,
                 arrowprops=dict(arrowstyle="->", color=C1, lw=1.2))

    l1, la1 = ax.get_legend_handles_labels()
    l2, la2 = ax2.get_legend_handles_labels()
    ax.legend(l1 + l2, la1 + la2, loc="upper left", fontsize=9,
              frameon=True, framealpha=0.95)
    ax.set_title("Same job, different levers: fighting 2022 inflation (Fed rate vs MAS currency)")
    ax.spines[["top"]].set_visible(False)
    ax2.spines[["top"]].set_visible(False)
    save(fig, 4)


if __name__ == "__main__":
    fig1(); fig2(); fig3(); fig4()
    print("done")
