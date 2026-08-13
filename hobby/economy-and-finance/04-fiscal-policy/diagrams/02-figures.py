#!/usr/bin/env python3
"""Figures for Econ E04 §2 — Deficits, public debt & sustainability.

Editable source of truth for the committed SVGs (see agent-docs/diagrams.md).
Numbers are illustrative but chosen to match the real shape of the pictures
(representative values for well-known public series):

  fig1 — DEBT/GDP IS NOT A STRAIGHT LINE: gross general-government debt as a share
         of GDP for the UK, USA and Japan across the last century — WWII spikes,
         the postwar "melt", and the post-2008 / COVID climbs, with Japan's
         relentless rise to ~250%.
  fig2 — THE SNOWBALL: simulated debt/GDP paths from the master equation
         Δb = (r − g)·b − p, showing how the (r − g) differential and the primary
         balance decide whether debt melts, holds, or snowballs.
  fig3 — THE KEY VARIABLE (r − g): the real interest rate on government debt minus
         real GDP growth, by decade (US). Negative for most of the postwar era
         (debt melts even with deficits); positive and dangerous in the 1980s and
         turning up again in the 2020s.
  fig4 — DENOMINATION BEATS THE RATIO: debt/GDP across countries, coloured by
         whether the debt is in the country's OWN currency or a foreign/■euro one,
         with default/crisis episodes marked — Japan is fine at ~255% (own
         currency) while Argentina defaulted near 60% and Greece imploded at ~180%.

Run with the project venv:

    .venv/bin/python hobby/economy-and-finance/04-fiscal-policy/diagrams/02-figures.py

Outputs 02-deficits-debt-and-sustainability-figN.svg into this folder.
"""
import os
import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt
import numpy as np

OUT = os.path.dirname(os.path.abspath(__file__))
BASE = "02-deficits-debt-and-sustainability"

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
# Fig 1 — Debt/GDP is not a straight line: UK, USA, Japan across a century.
# ---------------------------------------------------------------------------
def fig1():
    uk_y = [1900, 1918, 1933, 1946, 1955, 1970, 1990, 2000, 2008, 2012, 2020, 2024]
    uk_d = [30, 130, 180, 250, 140, 70, 32, 38, 50, 82, 105, 100]
    us_y = [1900, 1919, 1933, 1946, 1960, 1975, 1990, 2000, 2008, 2012, 2020, 2024]
    us_d = [8, 33, 40, 106, 53, 33, 60, 55, 68, 99, 132, 122]
    jp_y = [1970, 1980, 1990, 2000, 2005, 2010, 2015, 2020, 2024]
    jp_d = [12, 50, 63, 138, 176, 207, 231, 255, 250]

    fig, ax = plt.subplots(figsize=(11.2, 6.0))
    ax.plot(uk_y, uk_d, color=C1, lw=2.3, marker="o", ms=3.5, label="UK")
    ax.plot(us_y, us_d, color=C2, lw=2.3, marker="s", ms=3.5, label="USA")
    ax.plot(jp_y, jp_d, color=C5, lw=2.3, marker="^", ms=4, label="Japan")

    ax.axvspan(1939, 1945, color=GREY, alpha=0.10)
    ax.text(1942, 265, "WWII", ha="center", fontsize=8.6, color=GREY, fontweight="bold")
    ax.annotate("WWII peaks:\nUK ~250%, US ~106%", xy=(1946, 250), xytext=(1949, 205),
                fontsize=8.4, color=GREY, arrowprops=dict(arrowstyle="->", color=GREY, lw=1.1))
    ax.annotate("the postwar MELT\n(g > r + financial repression →\ndebt/GDP falls without repayment)",
                xy=(1970, 70), xytext=(1955, 120), fontsize=8.4, color=C3, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=C3, lw=1.2))
    ax.annotate("Japan: relentless climb\nto ~250% after 1990",
                xy=(2015, 231), xytext=(1978, 200), fontsize=8.4, color=C5, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=C5, lw=1.2))
    ax.annotate("2008 + COVID\nclimbs", xy=(2020, 132), xytext=(2006, 150),
                fontsize=8.4, color=C2, arrowprops=dict(arrowstyle="->", color=C2, lw=1.1))

    ax.set_xlabel("Year")
    ax.set_ylabel("Gross government debt (% of GDP)")
    ax.set_title("Debt/GDP is not a straight line: wars and crises drive it up, growth melts it down")
    ax.set_xlim(1898, 2027)
    ax.set_ylim(0, 285)
    ax.legend(fontsize=10, loc="upper left")
    ax.grid(alpha=0.25)
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, 1)


# ---------------------------------------------------------------------------
# Fig 2 — The snowball: Δb = (r − g)·b − p.
# ---------------------------------------------------------------------------
def fig2():
    T = 30
    t = np.arange(T + 1)
    b0 = 100.0

    def path(rg, p):
        b = [b0]
        for _ in range(T):
            b.append(b[-1] + (rg / 100.0) * b[-1] - p)
        return np.array(b)

    melt = path(-2.0, 0.0)     # g>r by 2pp, primary balanced
    stable = path(0.0, 0.0)    # r=g
    snow = path(+2.0, 0.0)     # r>g by 2pp, primary balanced
    tamed = path(+2.0, 2.5)    # r>g but a primary surplus of 2.5% GDP

    fig, ax = plt.subplots(figsize=(10.8, 6.0))
    ax.plot(t, snow, color=C2, lw=2.6, label="r − g = +2%, primary balance 0  → SNOWBALL")
    ax.plot(t, tamed, color=C4, lw=2.6, label="r − g = +2%, primary SURPLUS 2.5%  → tamed")
    ax.plot(t, stable, color=GREY, lw=2.0, ls="--", label="r − g = 0, primary balance 0  → flat")
    ax.plot(t, melt, color=C3, lw=2.6, label="r − g = −2%, primary balance 0  → MELTS")

    ax.text(30.3, snow[-1], "snowball", color=C2, fontsize=9, va="center", fontweight="bold")
    ax.text(30.3, melt[-1], "melts", color=C3, fontsize=9, va="center", fontweight="bold")

    ax.set_xlabel("Years")
    ax.set_ylabel("Debt / GDP (%), starting at 100%")
    ax.set_title("The snowball: the (r − g) gap and the primary balance decide debt's fate")
    ax.set_xlim(0, 34)
    ax.set_ylim(30, 210)
    ax.legend(fontsize=9, loc="upper left")
    ax.grid(alpha=0.25)
    ax.spines[["top", "right"]].set_visible(False)
    ax.text(1, 55, "master equation:  Δb = (r − g)·b − p\n(b = debt/GDP, p = primary surplus/GDP)",
            fontsize=9, color=GREY, style="italic",
            bbox=dict(boxstyle="round,pad=0.35", fc="white", ec=GREY, lw=1.0))
    save(fig, 2)


# ---------------------------------------------------------------------------
# Fig 3 — The key variable (r − g), by decade (US).
# ---------------------------------------------------------------------------
def fig3():
    decades = ["1950s", "1960s", "1970s", "1980s", "1990s", "2000s", "2010s", "2020s*"]
    rg = [-1.5, -1.0, -2.6, 2.6, 1.1, -0.6, -1.6, 0.6]
    colors = [C3 if v < 0 else C2 for v in rg]

    fig, ax = plt.subplots(figsize=(10.6, 5.9))
    bars = ax.bar(decades, rg, color=colors, width=0.62)
    ax.axhline(0, color="black", lw=1.0)
    for b, v in zip(bars, rg):
        ax.text(b.get_x() + b.get_width() / 2, v + (0.12 if v >= 0 else -0.22),
                f"{v:+.1f}", ha="center", fontsize=9, fontweight="bold",
                color=(C2 if v >= 0 else C3))

    ax.text(3.1, -1.7, "r < g  →  debt MELTS even while\nrunning deficits (the favorable\nregime — most of the postwar era)",
            fontsize=8.6, color=C3, fontweight="bold")
    ax.text(4.5, 2.45, "r > g  →  debt SNOWBALLS\nunless you run a primary surplus",
            fontsize=8.6, color=C2, fontweight="bold")

    ax.set_ylabel("Real interest rate on debt  −  real GDP growth  (percentage points)")
    ax.set_title("The one number that matters: the (r − g) differential, US by decade")
    ax.set_ylim(-3.2, 3.4)
    ax.grid(axis="y", alpha=0.25)
    ax.spines[["top", "right"]].set_visible(False)
    ax.text(7.0, -3.05, "*2020s: partial", fontsize=7.5, color=GREY, ha="center")
    save(fig, 3)


# ---------------------------------------------------------------------------
# Fig 4 — Denomination beats the ratio.
# ---------------------------------------------------------------------------
def fig4():
    # (country, debt/GDP, own-currency?, crisis/default?)
    rows = [
        ("Japan", 255, True, False),
        ("Greece (2011)", 180, False, True),
        ("Italy", 135, False, False),
        ("USA", 122, True, False),
        ("UK", 100, True, False),
        ("Sri Lanka (2022)", 100, False, True),
        ("Argentina (2001)", 62, False, True),
    ]
    rows.sort(key=lambda r: r[1])
    names = [r[0] for r in rows]
    vals = [r[1] for r in rows]
    colors = [C1 if r[2] else C2 for r in rows]

    fig, ax = plt.subplots(figsize=(10.8, 5.9))
    y = np.arange(len(names))
    bars = ax.barh(y, vals, color=colors, height=0.62)
    ax.set_yticks(y); ax.set_yticklabels(names, fontsize=10)

    for r, b, v in zip(rows, bars, vals):
        ax.text(v + 3, b.get_y() + b.get_height() / 2, f"{v}%", va="center",
                fontsize=9, fontweight="bold")
        if r[3]:
            ax.text(v - 6, b.get_y() + b.get_height() / 2, "✗ default/crisis", va="center",
                    ha="right", fontsize=8.4, color="white", fontweight="bold")

    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=C1, label="Own-currency debt (can always print → risk is inflation, not default)"),
                       Patch(color=C2, label="Foreign-currency / euro debt (can genuinely run out → default)")],
              fontsize=9, loc="lower right")
    ax.set_xlabel("Gross debt (% of GDP)")
    ax.set_title("Denomination beats the ratio: Japan is fine at 255%, Argentina defaulted at 62%")
    ax.set_xlim(0, 290)
    ax.grid(axis="x", alpha=0.25)
    ax.spines[["top", "right"]].set_visible(False)
    ax.annotate("same ratio (~100%),\nopposite fate — the difference\nis the CURRENCY, not the number",
                xy=(100, 1), xytext=(150, 1.7), fontsize=8.4, color=GREY,
                arrowprops=dict(arrowstyle="->", color=GREY, lw=1.1))
    save(fig, 4)


if __name__ == "__main__":
    fig1(); fig2(); fig3(); fig4()
    print("done")
