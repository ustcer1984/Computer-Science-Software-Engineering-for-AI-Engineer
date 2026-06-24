#!/usr/bin/env python3
"""Figures for Econ E02 §1 — GDP & measuring output.

Editable source of truth for the committed SVGs (see agent-docs/diagrams.md:
commit the rendered image, keep the source beside it). Numbers are illustrative
but chosen to match the *real shape* of the published data (rounded composition
shares, a stylized nominal-vs-real series). The point is the structure a reader
should carry, not exact figures — release values move and get revised. Run with
the project venv:

    .venv/bin/python hobby/economy-and-finance/02-macroeconomics/diagrams/01-figures.py

Outputs 01-gdp-and-measuring-output-figN.svg into this folder.
"""
import os
import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt
import numpy as np

OUT = os.path.dirname(os.path.abspath(__file__))
BASE = "01-gdp-and-measuring-output"

plt.rcParams.update({
    "font.size": 12,
    "axes.titlesize": 13,
    "axes.labelsize": 12,
    "svg.fonttype": "none",   # keep text as text (smaller, selectable)
    "figure.dpi": 100,
})

# A shared palette for the four expenditure components, reused across figures.
C_C  = "#1f77b4"   # consumption / blue
C_I  = "#ff7f0e"   # investment / orange
C_G  = "#2ca02c"   # government / green
C_NX = "#d62728"   # net exports / red
GREY = "#555555"


def save(fig, n):
    path = os.path.join(OUT, f"{BASE}-fig{n}.svg")
    fig.savefig(path, format="svg", bbox_inches="tight")
    plt.close(fig)
    print("wrote", path)


# ---------------------------------------------------------------------------
# Fig 1 — Value added: why we count only the final price (no double counting).
#   A loaf of bread's $2.50 retail price = the SUM of value added at each stage.
# ---------------------------------------------------------------------------
def fig1():
    fig, ax = plt.subplots(figsize=(8.4, 5.0))
    stages = ["Farmer\n(wheat)", "Miller\n(flour)", "Baker\n(loaf)", "Shop\n(retail)"]
    sale   = np.array([0.60, 1.10, 2.00, 2.50])      # price each stage sells at
    bought = np.array([0.00, 0.60, 1.10, 2.00])      # price of inputs bought in
    value_added = sale - bought                       # 0.60, 0.50, 0.90, 0.50

    x = np.arange(len(stages))
    # The intermediate (bought-in) part, stacked under the value added.
    ax.bar(x, bought, color="0.82", width=0.62, label="Cost of intermediate inputs")
    ax.bar(x, value_added, bottom=bought, color=C_C, width=0.62,
           label="Value added at this stage")

    for xi, (b, va, s) in enumerate(zip(bought, value_added, sale)):
        ax.text(xi, b + va/2, f"+${va:.2f}", ha="center", va="center",
                color="white", fontsize=10, fontweight="bold")
        ax.text(xi, s + 0.06, f"sells for\n${s:.2f}", ha="center", va="bottom",
                fontsize=8.5, color=GREY)

    ax.set_xticks(x)
    ax.set_xticklabels(stages)
    ax.set_ylim(0, 3.5)
    ax.set_ylabel("Dollars per loaf")
    ax.set_title("Value added sums to the final price — count it once, not four times")
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(loc="upper left", bbox_to_anchor=(0.012, 0.82),
              frameon=True, framealpha=0.95, fontsize=9.5)

    # Annotate the punchline: sum of value added = final sale price.
    ax.text(1.5, 3.28,
            "Σ value added  =  $0.60+$0.50+$0.90+$0.50  =  $2.50  =  final price",
            ha="center", fontsize=9.5, color="#08519c",
            bbox=dict(boxstyle="round,pad=0.4", fc="#eaf2fb", ec="#9ec3e6"))
    save(fig, 1)


# ---------------------------------------------------------------------------
# Fig 2 — The expenditure approach across economies: GDP = C + I + G + NX.
#   Illustrative shares of GDP (rounded to the published shape). NX can be
#   strongly negative (US deficit) or strongly positive (Singapore surplus).
# ---------------------------------------------------------------------------
def fig2():
    fig, ax = plt.subplots(figsize=(9.2, 4.8))
    # (C, I, G, NX) as % of GDP — illustrative, rounded to real shape.
    data = {
        "United States": (68, 18, 17, -3),
        "China":         (38, 42, 16,  4),
        "Singapore":     (32, 24, 11, 33),
    }
    names = list(data.keys())
    y = np.arange(len(names))[::-1]   # top-to-bottom in listed order
    comps = ["C  (consumption)", "I  (investment)", "G  (gov't spending)", "NX (net exports)"]
    colors = [C_C, C_I, C_G, C_NX]

    for yi, name in zip(y, names):
        C, I, G, NX = data[name]
        # Every bar totals GDP = 100%. NX is a COMPONENT of GDP, not an add-on.
        left = 0
        for val, col in zip((C, I, G), colors[:3]):
            ax.barh(yi, val, left=left, color=col, height=0.55)
            ax.text(left + val/2, yi, f"{val}", ha="center", va="center",
                    color="white", fontsize=9.5, fontweight="bold")
            left += val
        # left now = C+I+G = 100 - NX.
        if NX >= 0:
            # Surplus: the final segment carries the stack up to exactly 100.
            ax.barh(yi, NX, left=left, color=C_NX, height=0.55)
            ax.text(left + NX/2, yi, f"+{NX}", ha="center", va="center",
                    color="white", fontsize=9.5, fontweight="bold")
        else:
            # Deficit: C+I+G overshoot 100 (spending leaks to imports); the red
            # tail from 100 to C+I+G is the import drag that NX subtracts back.
            ax.barh(yi, -NX, left=100, color=C_NX, height=0.55)
            ax.text(100 + (-NX)/2, yi, f"{NX}", ha="center", va="center",
                    color="white", fontsize=8.5, fontweight="bold")

    ax.axvline(100, color=GREY, ls="--", lw=1.2)
    ax.text(100, len(names)-0.28, "GDP = 100%", ha="center", va="bottom",
            fontsize=9, color=GREY)
    ax.set_yticks(y)
    ax.set_yticklabels(names)
    ax.set_xlim(0, 118)
    ax.set_xlabel("Share of GDP (%)   —   illustrative, rounded to the published shape")
    ax.set_title("Same identity, different shape: GDP = C + I + G + NX")
    ax.spines[["top", "right", "left"]].set_visible(False)
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in colors]
    ax.legend(handles, comps, loc="lower right", ncol=1, frameon=True,
              framealpha=0.95, fontsize=8.5)
    save(fig, 2)


# ---------------------------------------------------------------------------
# Fig 3 — Nominal vs real GDP, and the GDP deflator. "Grew 2%" = REAL growth.
# ---------------------------------------------------------------------------
def fig3():
    years = np.arange(2014, 2025)
    base = 2014
    real_growth = 0.025                       # ~2.5%/yr real
    # Inflation varies: low early, a spike in 2021-2022, back down.
    infl = np.array([0.018, 0.016, 0.014, 0.021, 0.024, 0.018,
                     0.012, 0.047, 0.080, 0.041, 0.029])
    real = 100 * (1 + real_growth) ** (years - base)
    deflator = 100 * np.cumprod(1 + infl) / (1 + infl[0])  # index, 2014≈100
    nominal = real * deflator / 100

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.0, 4.8))

    # Left: levels — nominal pulls away from real as prices rise.
    ax1.plot(years, nominal, color=C_NX, lw=2.6, marker="o", ms=4,
             label="Nominal GDP (current prices)")
    ax1.plot(years, real, color=C_C, lw=2.6, marker="s", ms=4,
             label="Real GDP (constant 2014 prices)")
    ax1.fill_between(years, real, nominal, color="#fdd", alpha=0.6)
    ax1.annotate("the gap is pure\nprice change (inflation)",
                 xy=(2023, (real[-2]+nominal[-2])/2), xytext=(2016.3, 138),
                 fontsize=9, arrowprops=dict(arrowstyle="->", color=GREY))
    ax1.set_title("Nominal vs real GDP (index, 2014 = 100)")
    ax1.set_ylabel("GDP index")
    ax1.legend(loc="upper left", fontsize=9, frameon=True, framealpha=0.95)
    ax1.spines[["top", "right"]].set_visible(False)

    # Right: growth rates — nominal growth = real growth + inflation (≈).
    nom_g = 100 * (nominal[1:]/nominal[:-1] - 1)
    real_g = 100 * (real[1:]/real[:-1] - 1)
    yr = years[1:]
    w = 0.4
    ax2.bar(yr - w/2, nom_g, w, color=C_NX, label="Nominal growth")
    ax2.bar(yr + w/2, real_g, w, color=C_C, label="Real growth (the headline)")
    ax2.axhline(2.5, color=GREY, ls=":", lw=1)
    ax2.text(2014.6, 2.7, "real ≈ 2.5%/yr", fontsize=8.5, color=GREY)
    ax2.set_title("Growth rates: nominal ≈ real + inflation")
    ax2.set_ylabel("Annual growth (%)")
    ax2.legend(loc="upper right", fontsize=9, frameon=True, framealpha=0.95)
    ax2.spines[["top", "right"]].set_visible(False)
    save(fig, 3)


# ---------------------------------------------------------------------------
# Fig 4 — GDP vs GNI: where production happens vs whose income it is.
#   GNI as % of GDP. <100: income flows OUT to foreign owners (Ireland, SG).
#   >100: net income flows IN (remittances — Philippines).
# ---------------------------------------------------------------------------
def fig4():
    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    # Illustrative GNI-to-GDP ratios, rounded to the well-known shape.
    countries = ["Ireland", "Singapore", "United States", "Philippines"]
    gni = [65, 90, 101, 108]
    colors = ["#d62728" if v < 100 else "#2ca02c" for v in gni]

    bars = ax.barh(countries[::-1], gni[::-1], color=colors[::-1], height=0.6)
    ax.set_ylim(-0.7, 3.6)
    ax.axvline(100, color=GREY, ls="--", lw=1.4)
    ax.text(100, 3.62, "100%: GNI = GDP", ha="center", va="bottom",
            fontsize=8.5, color=GREY)

    for b, v in zip(bars, gni[::-1]):
        ax.text(v + 0.8, b.get_y() + b.get_height()/2,
                f"{v}%", va="center", fontsize=10, fontweight="bold")

    # Two explanatory notes in the empty right-hand column (x > all bar ends).
    ax.text(116, 2.5, "< 100%:\nincome flows\nOUT to foreign\nowners",
            fontsize=8.5, color="#a63603", ha="center", va="center")
    ax.text(116, 0.5, "> 100%:\nnet income\nflows IN\n(remittances)",
            fontsize=8.5, color="#196619", ha="center", va="center")
    ax.set_xlim(0, 132)
    ax.set_xlabel("Gross National Income as % of GDP   (illustrative)")
    ax.set_title("GDP vs GNI: produced-here vs earned-by-residents", pad=14)
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, 4)


if __name__ == "__main__":
    fig1(); fig2(); fig3(); fig4()
    print("done")
