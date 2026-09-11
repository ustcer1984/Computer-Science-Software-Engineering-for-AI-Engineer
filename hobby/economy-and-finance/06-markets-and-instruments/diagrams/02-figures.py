#!/usr/bin/env python3
"""Figures for Econ E06 §2 — Stocks (equity).

Editable source of truth for the committed SVGs (see agent-docs/diagrams.md).
Numbers are illustrative but the SHAPES are the real ones, and figs 2 and 4 are
computed from the models in the text rather than drawn by hand:

  fig1 — THE SHARE COUNT IS NOT CONSTANT: two companies, same starting count.
         The growth company issues stock-based compensation faster than it buys
         back (net DILUTION); the mature company retires stock (net SHRINKAGE).
         A passive holder who never trades sees their ownership share fall in one
         and rise in the other — which is why "the share price went up" is not
         the same question as "did I get richer per share I own".
  fig2 — THE GORDON GROWTH MODEL EXPLODES: price-to-dividend plotted against the
         growth rate for a fixed discount rate. As g approaches r the value goes
         to infinity — the mathematical reason small revisions to growth
         expectations move growth stocks violently.
  fig3 — DIVERSIFICATION, THE ONLY FREE LUNCH: portfolio volatility against the
         number of holdings. Idiosyncratic risk falls away; SYSTEMATIC risk does
         not, no matter how many names you add.
  fig4 — WHERE A STOCK'S VALUE SITS IN TIME (equity duration): the present value
         of each future period, bucketed. For a mature payer most value arrives
         soon; for a growth company most of it sits beyond year 10 — which is
         exactly why a change in the discount rate hits growth stocks hardest.
         Computed from explicit cash-flow models, not drawn.
"""
import os
import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt
import numpy as np

OUT = os.path.dirname(os.path.abspath(__file__))
BASE = "02-stocks-equity"

plt.rcParams.update({
    "font.size": 12, "axes.titlesize": 13, "axes.labelsize": 12,
    "svg.fonttype": "none", "figure.dpi": 100, "text.parse_math": False,
})

C1 = "#1f77b4"; C2 = "#d62728"; C3 = "#2ca02c"; C4 = "#ff7f0e"; C5 = "#9467bd"
GREY = "#555555"


def save(fig, n):
    path = os.path.join(OUT, f"{BASE}-fig{n}.svg")
    fig.savefig(path, format="svg", bbox_inches="tight")
    plt.close(fig)
    print("wrote", path)


def fig1():
    yrs = np.arange(0, 7)
    growth = 1000 * (1.025 ** yrs)            # net issuance ~2.5%/yr
    mature = 1000 * (0.965 ** yrs)            # net buyback ~3.5%/yr
    held = 10.0                               # you own 10m shares and never trade

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.4, 5.6))

    ax1.plot(yrs, growth, color=C2, lw=2.6, marker="o", ms=5,
             label="Growth co. — issues faster than it buys back")
    ax1.plot(yrs, mature, color=C1, lw=2.6, marker="s", ms=5,
             label="Mature co. — retires stock")
    ax1.axhline(1000, color=GREY, lw=1.0, ls=":")
    ax1.set_xlabel("Year")
    ax1.set_ylabel("Shares outstanding (millions)")
    ax1.set_title("The denominator moves")
    ax1.set_ylim(760, 1230)
    ax1.legend(fontsize=8.8, loc="upper left")
    ax1.grid(alpha=0.25)
    ax1.spines[["top", "right"]].set_visible(False)

    own_g = 100 * held / growth
    own_m = 100 * held / mature
    ax2.plot(yrs, own_g, color=C2, lw=2.6, marker="o", ms=5)
    ax2.plot(yrs, own_m, color=C1, lw=2.6, marker="s", ms=5)
    ax2.axhline(1.0, color=GREY, lw=1.0, ls=":")
    ax2.text(0.08, 1.017, "you start owning 1.00%", fontsize=9, color=GREY)
    ax2.annotate(f"DILUTED to {own_g[-1]:.2f}%\nwithout selling a single share",
                 xy=(6, own_g[-1]), xytext=(1.6, 0.875), fontsize=9.4, color=C2,
                 fontweight="bold", arrowprops=dict(arrowstyle="->", color=C2, lw=1.4))
    ax2.annotate(f"CONCENTRATED to {own_m[-1]:.2f}%\nwithout buying a single share",
                 xy=(6, own_m[-1]), xytext=(0.9, 1.175), fontsize=9.4, color=C1,
                 fontweight="bold", arrowprops=dict(arrowstyle="->", color=C1, lw=1.4))
    ax2.set_xlabel("Year")
    ax2.set_ylabel("Your ownership share (%)")
    ax2.set_title("What it does to a holder who never trades")
    ax2.set_ylim(0.82, 1.27)
    ax2.grid(alpha=0.25)
    ax2.spines[["top", "right"]].set_visible(False)

    fig.suptitle("A share is a FRACTION — and companies change the denominator every year",
                 fontsize=13.5, y=1.02)
    save(fig, 1)


def fig2():
    r = 0.08
    g = np.linspace(0.0, 0.074, 400)
    pd_ratio = 1.0 / (r - g)          # P / D1

    fig, ax = plt.subplots(figsize=(11.0, 6.2))
    ax.plot(100 * g, pd_ratio, color=C1, lw=3.0)
    ax.axvline(100 * r, color=C2, lw=2.0, ls="--")
    ax.text(8.12, 60, "g = r\nthe model breaks\n(infinite value)", fontsize=10,
            color=C2, fontweight="bold", va="center")

    for gi, note in [(0.02, "mature payer"), (0.05, "steady grower"), (0.07, "high grower")]:
        v = 1.0 / (r - gi)
        ax.plot([100 * gi], [v], "o", color=C4, ms=9)
        ax.annotate(f"{note}\ng = {100*gi:.0f}%  ->  {v:.0f}x",
                    xy=(100 * gi, v), xytext=(100 * gi - 1.75, v + 14),
                    fontsize=9.4, color=C4, fontweight="bold",
                    arrowprops=dict(arrowstyle="->", color=C4, lw=1.2))

    ax.annotate("from 6% to 7% growth — ONE point —\nthe value DOUBLES (50x to 100x)",
                xy=(6.42, 68), xytext=(0.55, 96), fontsize=10, color=C5, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=C5, lw=1.5))

    ax.set_xlabel("Assumed perpetual growth rate g (%)")
    ax.set_ylabel("Value as a multiple of next year's dividend  (P / D)")
    ax.set_title("Why growth stocks move so violently: the Gordon model at a discount rate of 8%")
    ax.set_xlim(0, 9.2)
    ax.set_ylim(0, 145)
    ax.grid(alpha=0.25)
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, 2)


def fig3():
    n = np.arange(1, 51)
    sys_risk = 15.5
    total = np.sqrt(sys_risk**2 + (39.0**2 - sys_risk**2) / n)

    fig, ax = plt.subplots(figsize=(11.0, 6.2))
    ax.plot(n, total, color=C1, lw=3.0)
    ax.axhline(sys_risk, color=C2, lw=2.0, ls="--")
    ax.fill_between(n, sys_risk, total, color=C3, alpha=0.18)
    ax.fill_between(n, 0, sys_risk, color=C2, alpha=0.10)

    ax.text(26, 9.0, "SYSTEMATIC (market) RISK — you cannot diversify this away.\n"
                     "It is what you are PAID to bear.",
            fontsize=10, color=C2, fontweight="bold", ha="center")
    ax.text(26, 21.5, "IDIOSYNCRATIC RISK — company-specific.\n"
                      "It disappears for free as you add names,\n"
                      "so the market does NOT pay you for it.",
            fontsize=10, color=C3, fontweight="bold", ha="center")

    for k in (1, 10, 30):
        ax.plot([k], [total[k-1]], "o", color=GREY, ms=8)
    ax.annotate(f"1 stock: {total[0]:.0f}%", xy=(1, total[0]), xytext=(3.2, 37),
                fontsize=9.6, color=GREY, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=GREY, lw=1.2))
    ax.annotate(f"~20 names captures most of the benefit\n(10 stocks: {total[9]:.0f}%)",
                xy=(10, total[9]), xytext=(12.5, 30.5), fontsize=9.6, color=GREY,
                fontweight="bold", arrowprops=dict(arrowstyle="->", color=GREY, lw=1.2))

    ax.set_xlabel("Number of stocks held (roughly equally weighted)")
    ax.set_ylabel("Portfolio volatility (annualised standard deviation, %)")
    ax.set_title("Diversification: the only free lunch — and exactly where it stops")
    ax.set_xlim(0, 50)
    ax.set_ylim(0, 42)
    ax.grid(alpha=0.25)
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, 3)


def fig4():
    T = 200
    t = np.arange(1, T + 1)

    # Mature payer: pays a lot now, grows slowly.
    r_m, g_m = 0.08, 0.02
    cf_m = 4.0 * (1 + g_m) ** (t - 1)
    pv_m = cf_m / (1 + r_m) ** t

    # Growth company: pays little now, grows fast for 10 years, then matures.
    r_g = 0.09
    cf_g = np.empty(T)
    c = 1.0
    for i in range(T):
        cf_g[i] = c
        c *= 1.18 if i < 10 else 1.03
    pv_g = cf_g / (1 + r_g) ** t

    buckets = [(1, 5), (6, 10), (11, 20), (21, T)]
    labels = ["Years 1-5", "Years 6-10", "Years 11-20", "Beyond year 20"]
    share_m = [100 * pv_m[a-1:b].sum() / pv_m.sum() for a, b in buckets]
    share_g = [100 * pv_g[a-1:b].sum() / pv_g.sum() for a, b in buckets]

    x = np.arange(len(labels)); w = 0.36
    fig, ax = plt.subplots(figsize=(11.2, 6.2))
    ax.bar(x - w/2, share_m, w, color=C1, label="Mature payer (high payout, 2% growth)")
    ax.bar(x + w/2, share_g, w, color=C2, label="Growth company (low payout, 18% for a decade)")

    for xi, v in zip(x - w/2, share_m):
        ax.text(xi, v + 1.2, f"{v:.0f}%", ha="center", fontsize=10, fontweight="bold", color=C1)
    for xi, v in zip(x + w/2, share_g):
        ax.text(xi, v + 1.2, f"{v:.0f}%", ha="center", fontsize=10, fontweight="bold", color=C2)

    far_m = share_m[2] + share_m[3]
    far_g = share_g[2] + share_g[3]
    ax.text(1.5, 47, f"Value sitting BEYOND year 10:\nmature {far_m:.0f}%   vs   growth {far_g:.0f}%\n"
                     "-> the growth company is a LONG-DURATION asset,\n"
                     "so a rise in the discount rate hurts it far more",
            fontsize=10.2, color=GREY, fontweight="bold", ha="center",
            bbox=dict(boxstyle="round,pad=0.5", fc="#f2f2f2", ec=GREY, lw=1.0))

    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=11)
    ax.set_ylabel("Share of total present value (%)")
    ax.set_title("Where a stock's value actually sits in time — equity duration")
    ax.set_ylim(0, 68)
    ax.legend(fontsize=9.6, loc="upper right")
    ax.grid(axis="y", alpha=0.25)
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, 4)


if __name__ == "__main__":
    fig1(); fig2(); fig3(); fig4()
    print("done")
