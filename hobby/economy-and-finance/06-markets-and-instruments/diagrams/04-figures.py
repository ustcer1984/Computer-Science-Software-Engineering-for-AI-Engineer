#!/usr/bin/env python3
"""Figures for Econ E06 §4 — FX, commodities & derivatives.

Editable source of truth for the committed SVGs (see agent-docs/diagrams.md).
Every panel is COMPUTED rather than drawn by hand. Figures 1, 2 and 5 use real
data; figures 3 and 4 are exact arithmetic from the models in the text, with
their real-market anchors noted.

  fig1 — THE FX MARKET IS MOSTLY NOT A CURRENCY MARKET. Left: global FX
         turnover by instrument, BIS Triennial Central Bank Survey, April 2025
         (USD 9.6tn/day net-net). SPOT is only 31% of it; FX SWAPS are 42% —
         i.e. the largest single use of the world's largest market is
         short-term FUNDING, not taking a view on a currency. Right: turnover
         by trading location, where Singapore is third at 11.8%.
         Source: BIS Triennial Central Bank Survey 2025.
  fig2 — A FORWARD RATE IS ARITHMETIC, NOT A FORECAST. Covered interest
         parity on real USD/SGD data of 18 September 2026: spot 1.2775, USD
         6-month 4.24% (constant-maturity Treasury, FRED DGS6MO), SGD 6-month
         T-bill cut-off 1.70% (MAS auction of 10 September 2026, the figure
         E06 §3 §8 uses). Left: the two routes for USD 1,000,000 over six
         months — stay in dollars, or swap into SGD and contract now to come
         back — end at the IDENTICAL amount, which is what pins the forward.
         Right: the implied 6-month forward as a function of the SGD rate,
         holding the USD rate fixed; today's point marked. The line is the
         whole content of "the market expects the SGD to strengthen": it does
         not.
  fig3 — THE CURVE, AND WHY AN INDEX IS NOT THE COMMODITY. Left: the futures
         curve from cost of carry, F = S exp((r + u - y)T), anchored on real
         WTI spot of USD 107.02 (2026-09-15, FRED DCOILWTICO) with r = 4.24%
         and storage u = 3%: a low convenience yield gives CONTANGO, a high
         one gives BACKWARDATION. Right: what rolling that curve does to a
         front-month index when SPOT NEVER MOVES — the whole return is the
         roll, and over five years it is -26.8% in contango and +26.9% in
         backwardation. Exact arithmetic, not a data series.
  fig4 — WHAT AN OPTION ACTUALLY PAYS. Left: payoff at expiry, net of premium,
         for a long call, a long put and a covered call on a 100 strike.
         Right: the call's value BEFORE expiry against its value AT expiry —
         the gap is time value, and it is the part that decays. Premiums from
         Black-Scholes at S = K = 100, r = 4%, sigma = 25%, T = 1.
  fig5 — THE NUMBER IN THE HEADLINE IS THE WRONG NUMBER. OTC derivatives at
         end-June 2025: notional USD 846tn, gross market value USD 21.8tn
         (2.6% of notional), gross credit exposure after legally enforceable
         netting USD 3.0tn (0.4% of notional). Log scale, because the point is
         the two orders of magnitude. Source: BIS OTC derivatives statistics;
         netting and gross credit exposure per ISDA's summary of the same data.
"""
import os
import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt
import numpy as np

OUT = os.path.dirname(os.path.abspath(__file__))
BASE = "04-fx-commodities-and-derivatives"

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


# ------------------------------------------------------------------- fig 1
# BIS Triennial Central Bank Survey, April 2025. Daily averages, net-net.
FX_TOTAL = 9.6                                   # USD trillion per day
FX_INSTR = [("FX swaps", 4.0, C2), ("Spot", 3.0, C1), ("Outright forwards", 1.8, C4),
            ("FX options", 0.7, C5), ("Currency swaps", 0.2, C3)]
FX_LOC = [("United Kingdom", 38.0), ("United States", 19.0), ("Singapore", 11.8),
          ("Hong Kong SAR", 7.0)]


def fig1():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.0, 5.8),
                                   gridspec_kw={"width_ratios": [1.35, 1]})

    names = [n for n, _, _ in FX_INSTR][::-1]
    vals = [v for _, v, _ in FX_INSTR][::-1]
    cols = [c for _, _, c in FX_INSTR][::-1]
    y = np.arange(len(names))
    ax1.barh(y, vals, color=cols, height=0.62)
    for i, v in enumerate(vals):
        ax1.text(v + 0.09, i, f"{v:.1f}tn  ({v / FX_TOTAL * 100:.0f}%)",
                 va="center", fontsize=11)
    ax1.set_yticks(y); ax1.set_yticklabels(names)
    ax1.set_xlim(0, 5.5)
    ax1.set_xlabel("Daily average turnover (USD trillion)")
    ax1.set_title(f"By instrument — total USD {FX_TOTAL}tn every day")
    ax1.grid(axis="x", alpha=0.25)
    ax1.spines[["top", "right"]].set_visible(False)
    ax1.text(2.05, 0.62,
             "Taking a VIEW on a currency\nis the 31% slice.\n"
             "The 42% slice is short-term\nFUNDING: borrow one currency,\n"
             "lend another, unwind on a\nfixed date at a fixed rate.",
             fontsize=10.6, color=GREY, va="center",
             bbox=dict(boxstyle="round,pad=0.5", fc="#f2f2f2", ec=GREY, lw=1.1))

    lnames = [n for n, _ in FX_LOC][::-1]
    lvals = [v for _, v in FX_LOC][::-1]
    lcols = [C3 if n == "Singapore" else "#9ecae1" for n in lnames]
    y2 = np.arange(len(lnames))
    ax2.barh(y2, lvals, color=lcols, height=0.6)
    for i, v in enumerate(lvals):
        ax2.text(v + 0.7, i, f"{v}%", va="center", fontsize=11)
    ax2.set_yticks(y2); ax2.set_yticklabels(lnames)
    ax2.set_xlim(0, 46)
    ax2.set_xlabel("Share of global turnover (%)")
    ax2.set_title("By trading location — where the desks sit")
    ax2.grid(axis="x", alpha=0.25)
    ax2.spines[["top", "right"]].set_visible(False)
    ax2.annotate("third in the world,\nand ahead of Hong Kong",
                 xy=(11.8, 1), xytext=(31, 0.28), fontsize=10.4, color=C3,
                 ha="center", arrowprops=dict(arrowstyle="->", color=C3))

    fig.suptitle("The world's largest market, and what it is actually doing "
                 "(BIS Triennial Survey, April 2025)",
                 fontsize=13.2, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    save(fig, 1)
    print(f"  (instrument shares sum to {sum(v for _, v, _ in FX_INSTR):.1f}tn)")


# ------------------------------------------------------------------- fig 2
S_SGD = 1.2775          # USD/SGD spot, 18 September 2026 (FRED DEXSIUS)
R_USD = 0.0424          # US 6-month constant-maturity Treasury, same day
R_SGD = 0.0170          # SGD 6-month T-bill cut-off, MAS auction 10 Sep 2026
TENOR = 0.5
NOTIONAL = 1_000_000.0


def fwd(r_sgd, r_usd=R_USD, s=S_SGD, t=TENOR):
    """Covered interest parity, simple interest: the forward that makes the two
    routes pay exactly the same. Quoted USD/SGD, i.e. SGD per one USD."""
    return s * (1 + r_sgd * t) / (1 + r_usd * t)


def fig2():
    f0 = fwd(R_SGD)
    usd_leg = NOTIONAL * (1 + R_USD * TENOR)
    sgd_start = NOTIONAL * S_SGD
    sgd_end = sgd_start * (1 + R_SGD * TENOR)
    back = sgd_end / f0                 # hedged: come back at the forward
    unhedged = sgd_end / S_SGD          # if the spot rate simply did not move

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.4, 6.2))

    # --- left: three end-states for the same USD 1,000,000 over six months
    labels = ["Route A\nstay in USD\nat 4.24%",
              "Route B\nSGD at 1.70%, come\nback at the FORWARD",
              "Route B unhedged\nif spot simply does\nnot move"]
    vals = [usd_leg, back, unhedged]
    cols = [C1, C2, "#bbbbbb"]
    bars = ax1.bar(labels, vals, color=cols, width=0.56)
    for b, v in zip(bars, vals):
        ax1.text(b.get_x() + b.get_width() / 2, v + 1100, f"USD {v:,.0f}",
                 ha="center", fontsize=12, fontweight="bold")
    ax1.axhline(usd_leg, color=GREY, ls=":", lw=1.4)
    ax1.set_ylim(NOTIONAL - 2000, usd_leg + 9500)
    ax1.set_ylabel("US dollars in six months")
    ax1.grid(axis="y", alpha=0.25); ax1.spines[["top", "right"]].set_visible(False)
    ax1.annotate("", xy=(2, unhedged + 400), xytext=(2, usd_leg - 400),
                 arrowprops=dict(arrowstyle="<->", color=GREY, lw=1.5))
    ax1.text(1.66, (usd_leg + unhedged) / 2, f"USD {usd_leg - unhedged:,.0f} short",
             ha="right", fontsize=10.6, color=GREY)
    ax1.set_title("The same million dollars, three ways\n"
                  f"spot 1.2775 -> SGD {sgd_start:,.0f}; six months at 1.70% -> "
                  f"SGD {sgd_end:,.0f}; back at {f0:.4f}", fontsize=11.6)
    ax1.yaxis.set_major_formatter(
        matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))

    # --- right: the forward as a function of the SGD rate
    rs = np.linspace(0.0, 0.06, 400)
    ax2.plot(rs * 100, [fwd(r) for r in rs], color=C1, lw=2.8)
    ax2.axhline(S_SGD, color=GREY, ls=":", lw=1.6)
    ax2.text(0.15, S_SGD + 0.0011, "spot 1.2775", fontsize=10.4, color=GREY)
    ax2.scatter([R_SGD * 100], [f0], color=C2, zorder=5, s=75)
    ax2.annotate(f"today: SGD 6m at 1.70%\n->  forward {f0:.4f}\n"
                 f"= {(f0 - S_SGD) * 10000:.0f} pips, SGD at a PREMIUM",
                 xy=(R_SGD * 100, f0), xytext=(2.45, 1.2570), fontsize=10.6, color=C2,
                 arrowprops=dict(arrowstyle="->", color=C2))
    ax2.scatter([R_USD * 100], [S_SGD], color=C3, zorder=5, s=75)
    ax2.annotate("equal rates -> forward = spot.\nThe forward premium IS the\n"
                 "interest differential, nothing else.",
                 xy=(R_USD * 100, S_SGD), xytext=(1.05, 1.2845), fontsize=10.4, color=C3,
                 arrowprops=dict(arrowstyle="->", color=C3))
    ax2.set_xlabel("SGD 6-month interest rate (%)")
    ax2.set_ylabel("Implied 6-month forward (SGD per USD)")
    ax2.set_title("Move the rate, move the forward — one for one")
    ax2.set_ylim(1.2485, 1.2925)
    ax2.grid(alpha=0.25); ax2.spines[["top", "right"]].set_visible(False)

    fig.suptitle("Covered interest parity on real USD/SGD data, 18 September 2026 — "
                 "the forward is the rate gap, not a view",
                 fontsize=13.2, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.945])
    save(fig, 2)
    print(f"  (forward {f0:.5f}; route A {usd_leg:,.2f} vs hedged B {back:,.2f} vs "
          f"unhedged {unhedged:,.2f}; points {(f0 - S_SGD) * 10000:.1f})")


# ------------------------------------------------------------------- fig 3
S_OIL = 107.02          # WTI spot, 2026-09-15 (FRED DCOILWTICO)
R_OIL = 0.0424          # financing, 6-month Treasury same week
U_STORE = 0.03          # storage and insurance, per year
Y_CONT, Y_BACK = 0.01, 0.12     # convenience yield: plentiful vs scarce


def fig3():
    T = np.linspace(0, 2, 200)
    c_cont = R_OIL + U_STORE - Y_CONT
    c_back = R_OIL + U_STORE - Y_BACK
    f_cont = S_OIL * np.exp(c_cont * T)
    f_back = S_OIL * np.exp(c_back * T)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.2, 6.0))

    ax1.plot(T * 12, f_cont, color=C2, lw=2.8,
             label=f"CONTANGO — convenience yield {Y_CONT * 100:.0f}%, carry +{c_cont * 100:.2f}%/yr")
    ax1.plot(T * 12, f_back, color=C3, lw=2.8, ls="--",
             label=f"BACKWARDATION — convenience yield {Y_BACK * 100:.0f}%, carry {c_back * 100:.2f}%/yr")
    ax1.axhline(S_OIL, color=GREY, ls=":", lw=1.6)
    ax1.text(0.4, S_OIL + 0.7, f"spot {S_OIL:.2f}", fontsize=10.4, color=GREY)
    ax1.set_xlabel("Months to delivery"); ax1.set_ylabel("Futures price (USD per barrel)")
    ax1.set_title("The curve is the carry:  F = S x exp((r + u - y) x T)")
    ax1.legend(fontsize=9.8, loc="upper left")
    ax1.grid(alpha=0.25); ax1.spines[["top", "right"]].set_visible(False)

    yrs = np.linspace(0, 5, 300)
    ax2.plot(yrs, 100 * np.exp(-c_cont * yrs), color=C2, lw=2.8,
             label="Front-month index, curve in contango")
    ax2.plot(yrs, 100 * np.exp(-c_back * yrs), color=C3, lw=2.8, ls="--",
             label="Front-month index, curve in backwardation")
    ax2.axhline(100, color=C1, lw=2.6, ls=":")
    ax2.text(2.45, 101.4, "the commodity itself — spot NEVER moves",
             fontsize=10.6, color=C1)
    e_c = 100 * np.exp(-c_cont * 5); e_b = 100 * np.exp(-c_back * 5)
    ax2.annotate(f"{e_c - 100:+.1f}% after 5 years", xy=(5, e_c), xytext=(0.72, 77.0),
                 fontsize=11, color=C2, fontweight="bold",
                 arrowprops=dict(arrowstyle="->", color=C2))
    ax2.annotate(f"{e_b - 100:+.1f}% after 5 years", xy=(5, e_b), xytext=(2.85, 110.5),
                 fontsize=11, color=C3, fontweight="bold",
                 arrowprops=dict(arrowstyle="->", color=C3))
    ax2.set_xlabel("Years"); ax2.set_ylabel("Index level (spot = 100 throughout)")
    ax2.set_title("Roll yield: the whole return, with no price move at all")
    ax2.legend(fontsize=9.8, loc="upper left")
    ax2.set_ylim(65, 145)
    ax2.grid(alpha=0.25); ax2.spines[["top", "right"]].set_visible(False)

    fig.suptitle("A commodity index is not the commodity — the shape of the curve "
                 "is a return in its own right",
                 fontsize=13.2, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.945])
    save(fig, 3)
    print(f"  (contango 12m {S_OIL * np.exp(c_cont):.2f}, backwardation 12m "
          f"{S_OIL * np.exp(c_back):.2f}; 5y roll {e_c - 100:+.1f}% / {e_b - 100:+.1f}%)")


# ------------------------------------------------------------------- fig 4
def norm_cdf(x):
    """Standard normal CDF via the error function — no scipy on this box."""
    from math import erf, sqrt
    return 0.5 * (1.0 + erf(x / sqrt(2.0)))


def bs(S, K, r, sig, T, call=True):
    from math import log, sqrt, exp
    if T <= 0:
        return max(S - K, 0.0) if call else max(K - S, 0.0)
    d1 = (log(S / K) + (r + 0.5 * sig * sig) * T) / (sig * sqrt(T))
    d2 = d1 - sig * sqrt(T)
    if call:
        return S * norm_cdf(d1) - K * exp(-r * T) * norm_cdf(d2)
    return K * exp(-r * T) * norm_cdf(-d2) - S * norm_cdf(-d1)


K_OPT, R_OPT, SIG, T_OPT = 100.0, 0.04, 0.25, 1.0


def fig4():
    c0 = bs(100.0, K_OPT, R_OPT, SIG, T_OPT, True)
    p0 = bs(100.0, K_OPT, R_OPT, SIG, T_OPT, False)
    S = np.linspace(60, 145, 400)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.2, 6.0))

    ax1.plot(S, np.maximum(S - K_OPT, 0) - c0, color=C1, lw=2.8,
             label=f"Long call, premium {c0:.2f} — loss capped, upside open")
    ax1.plot(S, np.maximum(K_OPT - S, 0) - p0, color=C2, lw=2.8, ls="--",
             label=f"Long put, premium {p0:.2f} — the insurance leg")
    ax1.plot(S, (S - 100.0) + c0 - np.maximum(S - K_OPT, 0), color=C3, lw=2.6, ls="-.",
             label=f"Covered call — you sold the upside for {c0:.2f}")
    ax1.axhline(0, color=GREY, lw=1.0)
    ax1.axvline(K_OPT, color=GREY, ls=":", lw=1.4)
    ax1.text(K_OPT + 0.8, -21.5, "strike 100", fontsize=10.4, color=GREY)
    ax1.annotate(f"call breaks even at {K_OPT + c0:.2f},\nnot at the strike",
                 xy=(K_OPT + c0, 0), xytext=(116, -15.5), fontsize=10.4, color=C1,
                 arrowprops=dict(arrowstyle="->", color=C1))
    ax1.set_xlabel("Price of the underlying at expiry")
    ax1.set_ylabel("Profit or loss per unit")
    ax1.set_title("Payoff at expiry, net of the premium")
    ax1.legend(fontsize=9.6, loc="upper left")
    ax1.set_ylim(-25, 46)
    ax1.grid(alpha=0.25); ax1.spines[["top", "right"]].set_visible(False)

    ax2.plot(S, np.maximum(S - K_OPT, 0), color=GREY, lw=2.2, ls="--",
             label="Value AT expiry — intrinsic value only")
    for T, col, lab in [(1.0, C1, "1 year left"), (0.5, C4, "6 months left"),
                        (0.08333, C2, "1 month left")]:
        ax2.plot(S, [bs(s, K_OPT, R_OPT, SIG, T, True) for s in S], color=col, lw=2.6,
                 label=f"Value with {lab}")
    ax2.axvline(K_OPT, color=GREY, ls=":", lw=1.4)
    ax2.annotate("this gap is TIME VALUE —\nit is what you pay for, and\n"
                 "it goes to zero at expiry\nwhatever the price does",
                 xy=(100, c0 / 2), xytext=(61, 21.5), fontsize=10.4, color=GREY,
                 arrowprops=dict(arrowstyle="->", color=GREY))
    ax2.set_xlabel("Price of the underlying now")
    ax2.set_ylabel("Call value per unit")
    ax2.set_title("Before expiry the option is worth more than it would pay")
    ax2.legend(fontsize=9.6, loc="upper left")
    ax2.set_ylim(-1, 50)
    ax2.grid(alpha=0.25); ax2.spines[["top", "right"]].set_visible(False)

    fig.suptitle(f"An option is an ASYMMETRY you buy — Black-Scholes at "
                 f"S = K = 100, r = 4%, sigma = 25%, T = 1",
                 fontsize=13.2, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.945])
    save(fig, 4)
    print(f"  (call {c0:.4f}, put {p0:.4f}, put-call parity check "
          f"{c0 - p0:.4f} vs {100 - K_OPT * np.exp(-R_OPT * T_OPT):.4f})")


# ------------------------------------------------------------------- fig 5
# BIS OTC derivatives statistics, end-June 2025.
NOTIONAL_TN, GMV_TN, GCE_TN = 846.0, 21.8, 3.0


def fig5():
    labels = ["Notional\namounts\noutstanding",
              "Gross\nmarket\nvalue",
              "Gross credit\nexposure\n(after netting)"]
    vals = [NOTIONAL_TN, GMV_TN, GCE_TN]
    cols = [C2, C4, C3]

    fig, ax = plt.subplots(figsize=(11.4, 6.3))
    bars = ax.bar(labels, vals, color=cols, width=0.55)
    ax.set_yscale("log")
    ax.set_ylim(1, 3000)
    ax.set_ylabel("USD trillion (log scale)")
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v * 1.13, f"USD {v:,.1f}tn",
                ha="center", fontsize=12.5, fontweight="bold")
    ax.text(1, GMV_TN * 0.42, f"{GMV_TN / NOTIONAL_TN * 100:.1f}% of notional",
            ha="center", fontsize=11, color="white", fontweight="bold")
    ax.text(2, GCE_TN * 0.42, f"{GCE_TN / NOTIONAL_TN * 100:.1f}% of notional",
            ha="center", fontsize=11, color="white", fontweight="bold")

    ax.set_yticks([1, 10, 100, 1000])
    ax.set_yticklabels(["1", "10", "100", "1,000"])
    ax.annotate("", xy=(0.74, 30), xytext=(0.30, 620),
                arrowprops=dict(arrowstyle="->", color=GREY, lw=1.6))
    ax.text(0.80, 165, "divide by 39 —\nalmost nobody ever\nowes the notional",
            fontsize=10.6, color=GREY, va="center")
    ax.annotate("", xy=(1.74, 4.2), xytext=(1.30, 16),
                arrowprops=dict(arrowstyle="->", color=GREY, lw=1.6))
    ax.text(1.80, 11.5, "divide by 7 again —\nclose-out netting removes\nabout 86% of it",
            fontsize=10.6, color=GREY, va="center")

    ax.set_title("OTC derivatives at end-June 2025: three numbers, two orders of "
                 "magnitude apart", fontsize=13.2, fontweight="bold")
    ax.grid(axis="y", alpha=0.25)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    save(fig, 5)
    print(f"  (GMV {GMV_TN / NOTIONAL_TN * 100:.2f}% of notional; "
          f"GCE {GCE_TN / NOTIONAL_TN * 100:.2f}%; netting removes "
          f"{(1 - GCE_TN / GMV_TN) * 100:.1f}% of GMV)")


if __name__ == "__main__":
    fig1(); fig2(); fig3(); fig4(); fig5()
    print("done")
