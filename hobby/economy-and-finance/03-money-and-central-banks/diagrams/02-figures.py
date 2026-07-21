#!/usr/bin/env python3
"""Figures for Econ E03 §2 — Interest rates & the time value of money.

Editable source of truth for the committed SVGs (see agent-docs/diagrams.md:
commit the rendered image, keep the source beside it). Numbers are illustrative
but chosen to match the real shape of the published pictures:

  fig1 — DISCOUNTING: the present value of $1000 received in N years, at a few
         discount rates. The future "melts away" faster the higher the rate —
         this is the master TVM curve, running backwards.
  fig2 — COMPOUNDING: $1000 growing forward at a few rates, with the doubling
         times marked (the Rule of 72). Same formula as fig1, run forwards.
  fig3 — ANATOMY OF A RATE: a stacked waterfall building an interest rate up
         from the real risk-free rate through inflation compensation, term,
         credit and liquidity premia — "there is no single interest rate."
  fig4 — THE YIELD CURVE: three stylised shapes (normal / flat / inverted) of
         yield vs maturity, the term structure the market quotes every day.
  fig5 — THE RECESSION SIGNAL: the 10y-minus-2y Treasury term spread over time;
         it dips below zero (inverts) before most recessions. Illustrative
         reconstruction of the shape of FRED T10Y2Y — see the doc's live-data
         section for the real series.
  fig6 — BOND PRICE vs YIELD: the inverse, convex relationship, and why a long
         (30y) bond's price moves far more than a short (2y) one for the same
         yield change — i.e. duration.

Run with the project venv:

    .venv/bin/python hobby/economy-and-finance/03-money-and-central-banks/diagrams/02-figures.py

Outputs 02-interest-rates-and-time-value-figN.svg into this folder.
"""
import os
import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt
import numpy as np

OUT = os.path.dirname(os.path.abspath(__file__))
BASE = "02-interest-rates-and-time-value"

plt.rcParams.update({
    "font.size": 12,
    "axes.titlesize": 13,
    "axes.labelsize": 12,
    "svg.fonttype": "none",   # keep text as text (smaller, selectable)
    "figure.dpi": 100,
    "text.parse_math": False,  # render literal '$' in labels (don't treat $..$ as mathtext)
})

C1 = "#1f77b4"   # blue
C2 = "#d62728"   # red
C3 = "#2ca02c"   # green
C4 = "#ff7f0e"   # orange
C5 = "#9467bd"   # purple
C6 = "#8c564b"   # brown
GREY = "#555555"


def save(fig, n):
    path = os.path.join(OUT, f"{BASE}-fig{n}.svg")
    fig.savefig(path, format="svg", bbox_inches="tight")
    plt.close(fig)
    print("wrote", path)


# ---------------------------------------------------------------------------
# Fig 1 — Discounting. PV of $1000 received in N years, at r = 2%, 5%, 10%.
#   PV = FV / (1+r)^n. The higher the discount rate, the faster the future
#   value melts away. This is the single most-used curve in finance.
# ---------------------------------------------------------------------------
def fig1():
    fv = 1000.0
    n = np.arange(0, 31)
    fig, ax = plt.subplots(figsize=(9.4, 5.4))
    for r, c in [(0.02, C3), (0.05, C1), (0.10, C2)]:
        pv = fv / (1 + r) ** n
        ax.plot(n, pv, color=c, lw=2.6, label=f"r = {r*100:.0f}%")
        ax.text(30.3, pv[-1], f"${pv[-1]:,.0f}", color=c, fontsize=9.5,
                va="center", fontweight="bold")

    # Highlight the 30-year point for r=10%: a dollar a generation away is worth
    # almost nothing today.
    pv10_30 = fv / 1.10 ** 30
    ax.annotate(f"$1000 in 30 yrs at 10%\nis worth only ${pv10_30:,.0f} today",
                xy=(30, pv10_30), xytext=(18, 430), fontsize=9.2, color=C2,
                arrowprops=dict(arrowstyle="->", color=C2, lw=1.4))

    ax.axhline(fv, color=GREY, ls=":", lw=1.2)
    ax.text(0.3, fv + 12, "face value = $1000 (money today)", fontsize=9,
            color=GREY)
    ax.set_xlabel("Years until you receive the $1000")
    ax.set_ylabel("Present value today ($)")
    ax.set_title("Discounting: what a future $1000 is worth today")
    ax.set_xlim(0, 33)
    ax.set_ylim(0, 1080)
    ax.legend(loc="upper right", fontsize=10, frameon=True, framealpha=0.95,
              title="discount rate")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.25)
    save(fig, 1)


# ---------------------------------------------------------------------------
# Fig 2 — Compounding, forwards. $1000 growing at 3/6/9% with doublings marked
#   (Rule of 72: doubling time ≈ 72/rate%). Same maths as fig1 run the other
#   way — and the reason "start early" is the whole game.
# ---------------------------------------------------------------------------
def fig2():
    pv = 1000.0
    n = np.arange(0, 41)
    fig, ax = plt.subplots(figsize=(9.4, 5.6))
    for r, c in [(0.03, C3), (0.06, C1), (0.09, C2)]:
        fv = pv * (1 + r) ** n
        ax.plot(n, fv, color=c, lw=2.6, label=f"r = {r*100:.0f}%  (doubles ≈ every {72/(r*100):.0f} yrs)")
        ax.text(40.4, fv[-1], f"${fv[-1]:,.0f}", color=c, fontsize=9.5,
                va="center", fontweight="bold")

    # Mark the doublings for the 9% line (Rule of 72 ≈ every 8 years).
    r = 0.09
    for k in range(1, 5):
        t = 72 / 9 * k
        val = pv * (1 + r) ** t
        ax.plot([t], [val], "o", color=C2, ms=5)
        ax.annotate(f"×{2**k}", xy=(t, val), xytext=(t - 1.2, val + 1600),
                    fontsize=8.6, color=C2, ha="center")

    ax.set_xlabel("Years invested")
    ax.set_ylabel("Future value of $1000 ($)")
    ax.set_title("Compounding: the same formula, run forwards (Rule of 72)")
    ax.set_xlim(0, 44)
    ax.set_ylim(0, 34000)
    ax.legend(loc="upper left", fontsize=9, frameon=True, framealpha=0.95)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.25)
    save(fig, 2)


# ---------------------------------------------------------------------------
# Fig 3 — Anatomy of an interest rate. A stacked waterfall building a nominal
#   yield up from the real risk-free rate: + inflation compensation = nominal
#   risk-free (a T-bill); + term premium = a long Treasury; + credit spread =
#   a corporate/EM bond; + liquidity premium. Illustrative percentages.
# ---------------------------------------------------------------------------
def fig3():
    # Components (percentage points), stacked into ONE column so the running
    # total climbs cleanly and milestone labels sit in the right margin.
    comps = [
        ("Real risk-free rate", 1.0, C1),
        ("+ Inflation compensation", 2.2, C4),
        ("+ Term premium", 0.8, C5),
        ("+ Credit / default spread", 2.5, C2),
        ("+ Liquidity premium", 0.6, C6),
    ]
    vals = [c[1] for c in comps]
    cum = np.cumsum(vals)

    fig, ax = plt.subplots(figsize=(9.8, 6.0))
    xbar = 0.0
    w = 0.44
    bottom = 0.0
    for lab, v, c in comps:
        ax.bar(xbar, v, w, bottom=bottom, color=c, label=f"{lab}  (+{v:.1f})")
        ax.text(xbar, bottom + v / 2, f"+{v:.1f}", ha="center", va="center",
                color="white", fontweight="bold", fontsize=10)
        bottom += v

    # Milestone lines + right-margin labels at meaningful cumulative stops.
    stops = {
        1: "3.2%  nominal risk-free  (≈ a T-bill)",
        2: "4.0%  a long-dated Treasury",
        3: "6.5%  an investment-grade corporate bond",
        4: "7.1%  a risky / high-yield bond",
    }
    for i, txt in stops.items():
        y = cum[i]
        ax.plot([xbar - w / 2, 1.15], [y, y], color=GREY, lw=1.0, ls="--",
                alpha=0.7)
        ax.text(1.17, y, "= " + txt, fontsize=9, color="black", va="center")

    ax.set_xticks([xbar])
    ax.set_xticklabels(["one bond's yield,\nbuilt up"], fontsize=10)
    ax.set_ylabel("Interest rate / yield (%)")
    ax.set_title("There is no single interest rate: a yield is built up from premia")
    ax.set_ylim(0, 7.8)
    ax.set_xlim(-0.5, 3.1)
    ax.legend(loc="lower right", bbox_to_anchor=(1.0, 0.02), fontsize=8.8,
              frameon=True, framealpha=0.95, title="component (percentage points)",
              title_fontsize=9)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.25)
    save(fig, 3)


# ---------------------------------------------------------------------------
# Fig 4 — The yield curve: three stylised shapes of yield vs maturity.
#   Normal (upward), flat, and inverted (short > long). Maturities 0.25..30y.
# ---------------------------------------------------------------------------
def fig4():
    mats = np.array([0.25, 0.5, 1, 2, 3, 5, 7, 10, 20, 30])
    x = np.log(mats)  # spread maturities out on a log-ish axis
    normal = 2.0 + 2.3 * (1 - np.exp(-mats / 6.0))
    flat = 3.7 + 0.05 * np.log(mats)
    inverted = 5.2 - 1.3 * (1 - np.exp(-mats / 5.0)) - 0.02 * mats

    fig, ax = plt.subplots(figsize=(9.6, 5.4))
    ax.plot(x, normal, "o-", color=C1, lw=2.6, ms=5, label="Normal (upward-sloping)")
    ax.plot(x, flat, "s-", color=C4, lw=2.6, ms=5, label="Flat")
    ax.plot(x, inverted, "^-", color=C2, lw=2.6, ms=5, label="Inverted (short > long)")

    ax.set_xticks(np.log([0.25, 1, 2, 5, 10, 30]))
    ax.set_xticklabels(["3m", "1y", "2y", "5y", "10y", "30y"])
    ax.set_xlabel("Maturity (log scale)")
    ax.set_ylabel("Yield to maturity (%)")
    ax.set_title("The yield curve: three shapes of the term structure")
    ax.set_ylim(1.4, 5.6)
    ax.legend(loc="center right", fontsize=9.5, frameon=True, framealpha=0.95)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(alpha=0.22)
    ax.annotate("inversion: the market\nexpects rate CUTS\n(→ slowdown ahead)",
                xy=(np.log(10), inverted[7]), xytext=(np.log(1.4), 2.0),
                fontsize=8.8, color=C2,
                arrowprops=dict(arrowstyle="->", color=C2, lw=1.3))
    save(fig, 4)


# ---------------------------------------------------------------------------
# Fig 5 — The recession signal. The 10y-2y Treasury term spread over time. It
#   goes negative (inverts) ahead of most recessions. Illustrative annual
#   reconstruction of the SHAPE of FRED T10Y2Y (values approximate). Recession
#   bands: 1980, 1981-82, 1990-91, 2001, 2008-09, 2020.
# ---------------------------------------------------------------------------
def fig5():
    years = np.arange(1977, 2025)
    # Approximate annual-average 10y-2y spread (percentage points). Chosen to
    # match the well-known shape: inversions before 1980, 1990, 2001, 2008, 2020,
    # and the deep 2022-24 inversion.
    spread = {
        1977: 0.7, 1978: 0.2, 1979: -0.6, 1980: -1.4, 1981: -1.3, 1982: -0.2,
        1983: 1.0, 1984: 1.2, 1985: 1.3, 1986: 1.6, 1987: 1.0, 1988: 0.4,
        1989: -0.2, 1990: 0.2, 1991: 1.4, 1992: 2.2, 1993: 2.4, 1994: 2.0,
        1995: 0.9, 1996: 0.6, 1997: 0.4, 1998: 0.4, 1999: 0.5, 2000: -0.4,
        2001: 0.7, 2002: 2.1, 2003: 2.4, 2004: 1.9, 2005: 0.6, 2006: -0.1,
        2007: 0.1, 2008: 1.4, 2009: 2.6, 2010: 2.6, 2011: 2.2, 2012: 1.5,
        2013: 2.1, 2014: 1.9, 2015: 1.4, 2016: 1.0, 2017: 1.0, 2018: 0.5,
        2019: 0.1, 2020: 0.5, 2021: 1.1, 2022: -0.2, 2023: -0.7, 2024: -0.3,
    }
    y = np.array([spread[t] for t in years])

    fig, ax = plt.subplots(figsize=(11.0, 5.2))
    ax.plot(years, y, color=C1, lw=2.2)
    ax.fill_between(years, y, 0, where=(y >= 0), color=C1, alpha=0.18)
    ax.fill_between(years, y, 0, where=(y < 0), color=C2, alpha=0.30)
    ax.axhline(0, color="black", lw=1.0)

    # Recession bands.
    recessions = [(1980, 1980.6), (1981.5, 1982.9), (1990.5, 1991.2),
                  (2001.2, 2001.9), (2007.9, 2009.5), (2020.1, 2020.5)]
    for a, b in recessions:
        ax.axvspan(a, b, color=GREY, alpha=0.22)
    ax.text(2009.5, 2.75, "grey bands = recessions", fontsize=8.6, color=GREY,
            ha="left")

    ax.annotate("curve INVERTS (spread < 0)\nbefore most recessions",
                xy=(2000, -0.4), xytext=(1994, -1.5), fontsize=9, color=C2,
                fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=C2, lw=1.4))
    ax.annotate("deepest inversion\nsince the early 1980s",
                xy=(2023, -0.7), xytext=(2015.5, -1.6), fontsize=8.8, color=C2,
                arrowprops=dict(arrowstyle="->", color=C2, lw=1.3))

    ax.set_xlabel("Year")
    ax.set_ylabel("10-year minus 2-year Treasury yield (%)")
    ax.set_title("An inverted yield curve is the market's recession signal (illustrative)")
    ax.set_ylim(-2.0, 3.0)
    ax.set_xlim(1977, 2024)
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, 5)


# ---------------------------------------------------------------------------
# Fig 6 — Bond price vs yield. Price of a $1000-face, 5% annual-coupon bond as
#   a function of its yield to maturity, for a 2y and a 30y maturity. Inverse
#   and convex; the long bond's price is far more sensitive to yield (duration).
# ---------------------------------------------------------------------------
def fig6():
    face = 1000.0
    coupon_rate = 0.05
    coupon = coupon_rate * face
    ys = np.linspace(0.01, 0.11, 200)

    def price(n, y):
        t = np.arange(1, n + 1)
        # sum of discounted coupons + discounted face
        pv_coupons = np.sum(coupon / (1 + y) ** t)
        pv_face = face / (1 + y) ** n
        return pv_coupons + pv_face

    p2 = np.array([price(2, y) for y in ys])
    p30 = np.array([price(30, y) for y in ys])

    fig, ax = plt.subplots(figsize=(9.6, 5.6))
    ax.plot(ys * 100, p2, color=C1, lw=2.6, label="2-year bond (short)")
    ax.plot(ys * 100, p30, color=C2, lw=2.6, label="30-year bond (long)")

    # Par point: when yield == coupon rate (5%), price == face (1000).
    ax.plot([5], [face], "ko", ms=6)
    ax.annotate("at par: yield = coupon = 5%\n→ price = face = $1000",
                xy=(5, face), xytext=(5.6, 1330), fontsize=8.8, color="black",
                arrowprops=dict(arrowstyle="->", color="black", lw=1.2))

    # Show the sensitivity gap when yield rises 5% -> 7%.
    p2_7 = price(2, 0.07)
    p30_7 = price(30, 0.07)
    ax.plot([7, 7], [p2_7, p30_7], color=GREY, ls="--", lw=1.2)
    ax.annotate(f"yield 5→7%:\nshort bond −${face - p2_7:,.0f}\nlong bond −${face - p30_7:,.0f}",
                xy=(7, p30_7), xytext=(7.4, 560), fontsize=8.8, color=GREY,
                arrowprops=dict(arrowstyle="->", color=GREY, lw=1.2))

    ax.axhline(face, color=GREY, ls=":", lw=1.0)
    ax.set_xlabel("Yield to maturity (%)")
    ax.set_ylabel("Bond price ($)")
    ax.set_title("Bond price and yield move inversely — and the long bond moves more")
    ax.set_xlim(1, 11)
    ax.set_ylim(400, 1750)
    ax.legend(loc="upper right", fontsize=10, frameon=True, framealpha=0.95)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(alpha=0.22)
    save(fig, 6)


if __name__ == "__main__":
    fig1(); fig2(); fig3(); fig4(); fig5(); fig6()
    print("done")
