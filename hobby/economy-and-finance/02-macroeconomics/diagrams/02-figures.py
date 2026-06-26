#!/usr/bin/env python3
"""Figures for Econ E02 §2 — Inflation & price indices.

Editable source of truth for the committed SVGs (see agent-docs/diagrams.md:
commit the rendered image, keep the source beside it). Numbers are illustrative
but chosen to match the *real shape* of the published data (rounded CPI basket
weights, a stylized inflation series with the 2021-22 spike, a Laspeyres-vs-
chained wedge, and the downward-nominal-wage-rigidity histogram). The point is
the structure a reader should carry, not exact figures. Run with the project
venv:

    .venv/bin/python hobby/economy-and-finance/02-macroeconomics/diagrams/02-figures.py

Outputs 02-inflation-and-price-indices-figN.svg into this folder.
"""
import os
import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt
import numpy as np

OUT = os.path.dirname(os.path.abspath(__file__))
BASE = "02-inflation-and-price-indices"

plt.rcParams.update({
    "font.size": 12,
    "axes.titlesize": 13,
    "axes.labelsize": 12,
    "svg.fonttype": "none",   # keep text as text (smaller, selectable)
    "figure.dpi": 100,
})

C_BLUE  = "#1f77b4"
C_ORANGE = "#ff7f0e"
C_GREEN = "#2ca02c"
C_RED   = "#d62728"
C_PURPLE = "#9467bd"
GREY = "#555555"


def save(fig, n):
    path = os.path.join(OUT, f"{BASE}-fig{n}.svg")
    fig.savefig(path, format="svg", bbox_inches="tight")
    plt.close(fig)
    print("wrote", path)


# ---------------------------------------------------------------------------
# Fig 1 — The CPI basket: inflation is a WEIGHTED average, not one price.
#   Illustrative category weights, rounded to the published shape (housing is
#   the heavyweight in most developed-economy CPIs).
# ---------------------------------------------------------------------------
def fig1():
    fig, ax = plt.subplots(figsize=(9.0, 4.9))
    cats = [
        "Housing\n(rent, utilities)",
        "Transport\n(cars, fuel)",
        "Food &\nbeverages",
        "Health\ncare",
        "Recreation\n& culture",
        "Education",
        "Clothing",
        "Other",
    ]
    weights = np.array([34, 16, 14, 8, 6, 6, 4, 12])  # ~100, illustrative shape
    colors = [C_BLUE, C_ORANGE, C_GREEN, C_RED, C_PURPLE,
              "#8c564b", "#e377c2", "0.7"]

    order = np.argsort(weights)            # ascending → biggest on top
    y = np.arange(len(cats))
    bars = ax.barh(y, weights[order], color=[colors[i] for i in order],
                   height=0.66)
    ax.set_yticks(y)
    ax.set_yticklabels([cats[i] for i in order])
    for b, w in zip(bars, weights[order]):
        ax.text(w + 0.4, b.get_y() + b.get_height()/2, f"{w}%",
                va="center", fontsize=10, fontweight="bold")
    ax.set_xlim(0, 40)
    ax.set_xlabel("Weight in the CPI basket (%)   —   illustrative, rounded to the published shape")
    ax.set_title("Inflation weights what it averages: the CPI basket")
    ax.spines[["top", "right"]].set_visible(False)
    ax.text(39.5, 0.2,
            "A 10% jump in a 34%-weighted\ncategory moves the index 8× more\n"
            "than the same jump in a 4% one",
            ha="right", va="bottom", fontsize=8.5, color=GREY,
            bbox=dict(boxstyle="round,pad=0.4", fc="#f4f4f4", ec="0.8"))
    save(fig, 1)


# ---------------------------------------------------------------------------
# Fig 2 — The level vs the rate: the price level (almost) always rises; the
#   inflation rate is its slope, and THAT is what bounces around. Stylized to
#   the post-2014 shape: low inflation, the 2021-22 spike, disinflation, with a
#   single deflation dip to show what falling prices look like.
# ---------------------------------------------------------------------------
def fig2():
    years = np.arange(2014, 2025)
    infl = np.array([1.6, 0.1, 1.3, 2.1, 2.4, 1.8,
                     1.2, 4.7, 8.0, 4.1, 2.9]) / 100   # note the 2015 dip & 2022 spike
    level = 100 * np.cumprod(1 + infl) / (1 + infl[0])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.0, 4.8))

    # Left: the price level — a near-monotone climb.
    ax1.plot(years, level, color=C_BLUE, lw=2.6, marker="o", ms=4)
    ax1.set_title("The price level (CPI index, 2014 = 100)")
    ax1.set_ylabel("Price level")
    ax1.annotate("prices rarely FALL —\nthey mostly rise faster or slower",
                 xy=(2022, level[8]), xytext=(2014.4, level[-1]-3),
                 fontsize=9, color=GREY,
                 arrowprops=dict(arrowstyle="->", color=GREY))
    ax1.spines[["top", "right"]].set_visible(False)

    # Right: the inflation RATE — the slope of the left panel.
    rate = infl * 100
    colors = [C_RED if r < 0.5 else C_BLUE for r in rate]  # flag near-zero/deflation
    ax2.bar(years, rate, color=C_BLUE, width=0.62)
    ax2.axhline(2.0, color=C_GREEN, ls="--", lw=1.4)
    ax2.text(2014.3, 2.2, "2% target", color=C_GREEN, fontsize=9)
    ax2.axhline(0, color="black", lw=0.8)
    ax2.annotate("2015: near-zero\n(disinflation, not deflation)",
                 xy=(2015, 0.1), xytext=(2015.2, 5.2),
                 fontsize=8.5, color=GREY,
                 arrowprops=dict(arrowstyle="->", color=GREY))
    ax2.annotate("2021-22 spike", xy=(2022, 8.0), xytext=(2018.6, 7.3),
                 fontsize=9, color=C_RED,
                 arrowprops=dict(arrowstyle="->", color=C_RED))
    ax2.set_title("The inflation rate = the slope of the level")
    ax2.set_ylabel("Inflation (% per year)")
    ax2.spines[["top", "right"]].set_visible(False)
    save(fig, 2)


# ---------------------------------------------------------------------------
# Fig 3 — Substitution bias: a FIXED-basket (Laspeyres) index drifts above a
#   chained index that lets buyers substitute toward what got relatively
#   cheaper. The wedge is why a Laspeyres CPI OVERSTATES the cost of living.
# ---------------------------------------------------------------------------
def fig3():
    years = np.arange(2014, 2025)
    # Chained index grows a touch slower each year — the substitution wedge
    # compounds to ~0.3pp/yr, the Boskin-style gap.
    chained = 100 * (1.025) ** (years - 2014)
    laspeyres = 100 * (1.028) ** (years - 2014)

    fig, ax = plt.subplots(figsize=(8.8, 4.9))
    ax.plot(years, laspeyres, color=C_RED, lw=2.6, marker="o", ms=4,
            label="Fixed-basket (Laspeyres) CPI — overstates")
    ax.plot(years, chained, color=C_BLUE, lw=2.6, marker="s", ms=4,
            label="Chained CPI — lets buyers substitute")
    ax.fill_between(years, chained, laspeyres, color="#fde0dd", alpha=0.8)
    ax.annotate("substitution bias\n(the wedge compounds)",
                xy=(2023, (chained[-2] + laspeyres[-2]) / 2),
                xytext=(2014.5, 122), fontsize=9, color="#a63603",
                arrowprops=dict(arrowstyle="->", color=GREY))
    ax.set_title("Why a fixed basket overstates inflation (substitution bias)")
    ax.set_ylabel("Cost-of-living index (2014 = 100)")
    ax.legend(loc="upper left", fontsize=9, frameon=True, framealpha=0.95)
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, 3)


# ---------------------------------------------------------------------------
# Fig 4 — Downward nominal wage rigidity: the histogram of yearly wage CHANGES
#   has a tall spike at exactly 0% and a missing left tail — firms freeze pay
#   rather than cut it. A little inflation lets real wages fall without nominal
#   cuts ("greasing the wheels"). Stylized to the well-known empirical shape.
# ---------------------------------------------------------------------------
def fig4():
    fig, ax = plt.subplots(figsize=(9.0, 4.9))
    # Buckets of nominal wage change (%). Real distributions show a sharp spike
    # at 0 and a truncated left (negative) tail.
    edges = np.arange(-6, 11)            # -6%..+10%
    centers = edges[:-1] + 0.5
    # A roughly bell-shaped mass centred near +3%, but with the negative side
    # "swept up" into a spike at 0.
    base = np.exp(-((centers - 3.0) ** 2) / (2 * 2.6 ** 2))
    base[centers < 0] *= 0.18            # missing left tail (almost no cuts)
    spike_idx = np.where(centers == 0.5)[0][0]  # bucket [0,1) ≈ "froze pay"
    base[spike_idx] += 1.05              # pile-up at zero
    base = base / base.sum() * 100

    colors = [C_RED if c < 0 else (C_GREEN if c == 0.5 else C_BLUE)
              for c in centers]
    ax.bar(centers, base, width=0.92, color=colors, edgecolor="white", lw=0.6)
    ax.axvline(0, color="black", lw=1.0)
    ax.annotate("spike at 0%:\nfirms FREEZE pay\nrather than cut it",
                xy=(0.5, base[spike_idx]), xytext=(2.6, base[spike_idx] - 1),
                fontsize=9, color="#196619",
                arrowprops=dict(arrowstyle="->", color=GREY))
    ax.annotate("missing left tail:\nnominal pay cuts are rare",
                xy=(-2.5, 1.3), xytext=(-5.8, 9.5),
                fontsize=9, color="#a63603",
                arrowprops=dict(arrowstyle="->", color=GREY))
    ax.set_xlabel("Annual change in nominal wage (%)")
    ax.set_ylabel("Share of workers (%)")
    ax.set_title("Downward nominal wage rigidity: why a little inflation greases the wheels")
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, 4)


if __name__ == "__main__":
    fig1(); fig2(); fig3(); fig4()
    print("done")
