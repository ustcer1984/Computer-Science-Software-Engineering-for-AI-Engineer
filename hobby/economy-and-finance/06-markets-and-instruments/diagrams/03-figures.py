#!/usr/bin/env python3
"""Figures for Econ E06 §3 — Bonds & fixed income.

Editable source of truth for the committed SVGs (see agent-docs/diagrams.md).
Every panel is COMPUTED from the model in the text rather than drawn by hand,
and figs 3 and 4 use real market data (sources noted below and in the doc).

  fig1 — WHERE THE MONEY IS vs WHERE THE VALUE IS. A 10-year 4% annual-coupon
         bond. Left: the nominal cash flows (ten coupons, then the face value).
         Right: the present value of each of those flows at a 5% yield, with
         MACAULAY DURATION marked as the balance point of the PV bars. Duration
         is not "a maturity" — it is the centre of mass of the discounted cash
         flows, which is why it, and not maturity, predicts the price move.
  fig2 — DURATION IS A TANGENT; CONVEXITY IS THE CURVE. Left: the true
         price-yield curve of a 30-year 4% bond against the straight-line
         duration approximation, with the error shaded — the approximation
         UNDERSTATES gains and OVERSTATES losses, so convexity is a gift.
         Right: a CALLABLE bond, whose price is capped by the call: above the
         call strike the curve bends the wrong way (negative convexity).
  fig3 — WHAT A CREDIT SPREAD HAS TO COVER. The breakeven annual default rate
         implied by a spread, p = s / (1 - R), for three recovery rates. Real
         option-adjusted spreads are marked: US investment grade and high yield
         on 2026-09-15 (0.80% and 2.76%, ICE BofA indices via FRED) and their
         December 2008 records (6.56% and 21.82%).
  fig4 — ONE CURVE, THREE READINGS. The real US Treasury par (constant-maturity)
         curve of 2026-09-15, the zero-coupon SPOT curve bootstrapped from it,
         and the 1-year IMPLIED FORWARD curve. A quoted yield to maturity is a
         blend of the spot curve; the forwards are what the market is actually
         betting on. Source: US Treasury daily yield curve rates.
  fig5 — A BOND IS NOT A BOND FUND — AND BOTH ARE FINE IF YOU WAIT. Yields jump
         permanently from 4% to 6% on day one. Left: cumulative total return of
         a single 10-year bond held to maturity versus the no-shock path.
         Right: the same for a constant-maturity 10-year bond fund, which never
         "pulls to par" but reinvests at the higher yield. Both cross the
         no-shock path at roughly the MACAULAY DURATION — that crossover is
         immunisation, and it is the honest answer to "was the rate rise bad?"
"""
import os
import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt
import numpy as np

OUT = os.path.dirname(os.path.abspath(__file__))
BASE = "03-bonds-and-fixed-income"

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


# ---------------------------------------------------------------- bond maths
def price(coupon_rate, y, n, face=100.0, freq=1):
    """Price of a plain bond: coupons then face, discounted at yield y."""
    c = face * coupon_rate / freq
    per = int(round(n * freq))
    t = np.arange(1, per + 1)
    df = (1 + y / freq) ** (-t)
    return float(c * df.sum() + face * df[-1])


def macaulay(coupon_rate, y, n, face=100.0, freq=1):
    """Macaulay duration in years — the PV-weighted average time to payment."""
    c = face * coupon_rate / freq
    per = int(round(n * freq))
    t = np.arange(1, per + 1)
    cf = np.full(per, c); cf[-1] += face
    pv = cf * (1 + y / freq) ** (-t)
    return float((pv * (t / freq)).sum() / pv.sum())


# ------------------------------------------------------------------- fig 1
def fig1():
    n, cpn, y, face = 10, 0.04, 0.05, 100.0
    t = np.arange(1, n + 1)
    cf = np.full(n, face * cpn); cf[-1] += face
    pv = cf * (1 + y) ** (-t)
    D = macaulay(cpn, y, n)
    P = price(cpn, y, n)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.8, 5.4))

    ax1.bar(t, cf, color=C1, width=0.62)
    for xi, v in zip(t, cf):
        ax1.text(xi, v + 2.5, f"{v:.0f}", ha="center", fontsize=9.6, color=GREY)
    ax1.set_title("What the bond PAYS you (nominal cash flows)")
    ax1.set_xlabel("Year"); ax1.set_ylabel("Dollars per 100 of face value")
    ax1.set_xticks(t); ax1.set_ylim(0, 152)
    ax1.grid(axis="y", alpha=0.25)
    ax1.spines[["top", "right"]].set_visible(False)
    ax1.text(0.55, 146, "ten coupons of 4, then 4 + 100 at maturity\n"
                        f"-> {cf[-1] / cf.sum():.0%} of the money you are owed\n"
                        "   arrives on the very last day",
             fontsize=10.2, color=GREY, va="top",
             bbox=dict(boxstyle="round,pad=0.45", fc="#f2f2f2", ec=GREY, lw=1.0))

    ax2.bar(t, pv, color=C4, width=0.62)
    for xi, v in zip(t, pv):
        ax2.text(xi, v + 1.6, f"{v:.1f}", ha="center", fontsize=9.6, color=GREY)
    ax2.axvline(D, color=C2, lw=2.4, ls="--")
    ax2.plot([D], [-3.4], marker="^", ms=18, color=C2, clip_on=False)
    ax2.annotate(f"Macaulay duration = {D:.2f} years\nthe BALANCE POINT of the PV bars",
                 xy=(D, 26), xytext=(4.4, 44), fontsize=10.6, color=C2,
                 fontweight="bold", ha="center",
                 arrowprops=dict(arrowstyle="->", color=C2, lw=1.4))
    ax2.set_title(f"What it is WORTH TODAY at a {y:.0%} yield (price {P:.2f})")
    ax2.set_xlabel("Year"); ax2.set_ylabel("Present value of that year's payment")
    ax2.set_xticks(t); ax2.set_ylim(0, 96)
    ax2.grid(axis="y", alpha=0.25)
    ax2.spines[["top", "right"]].set_visible(False)
    ax2.text(0.55, 93, "Discounting does not change WHEN the money arrives,\n"
                       "it changes HOW MUCH each arrival is worth now.\n"
                       "Duration is where that weight sits -> it, not the\n"
                       "10-year maturity, is the bond's true time exposure.",
             fontsize=10.2, color=GREY, va="top",
             bbox=dict(boxstyle="round,pad=0.45", fc="#f2f2f2", ec=GREY, lw=1.0))

    fig.suptitle("A bond's maturity tells you when it ENDS; its duration tells you where its VALUE LIVES",
                 fontsize=13.4, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.955])
    save(fig, 1)


# ------------------------------------------------------------------- fig 2
def fig2():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.8, 5.6))

    # --- left: tangent vs curve -------------------------------------------
    n, cpn, y0 = 30, 0.04, 0.04
    ys = np.linspace(0.005, 0.095, 400)
    P = np.array([price(cpn, y, n) for y in ys])
    P0 = price(cpn, y0, n)
    Dmod = macaulay(cpn, y0, n) / (1 + y0)            # modified duration
    lin = P0 * (1 - Dmod * (ys - y0))

    ax1.plot(ys * 100, P, color=C1, lw=2.8, label="True price (the curve)")
    ax1.plot(ys * 100, lin, color=C2, lw=2.2, ls="--",
             label=f"Duration approximation (tangent, D = {Dmod:.1f})")
    ax1.fill_between(ys * 100, lin, P, where=(P > lin), color=C3, alpha=0.20)
    ax1.plot([y0 * 100], [P0], marker="o", ms=9, color="black", zorder=5)
    ax1.annotate("you are here\n(par, 4% yield)", xy=(y0 * 100, P0),
                 xytext=(y0 * 100 + 1.4, P0 + 42), fontsize=10.2, color=GREY,
                 arrowprops=dict(arrowstyle="->", color=GREY))

    p_up = price(cpn, 0.06, n); l_up = P0 * (1 - Dmod * 0.02)
    p_dn = price(cpn, 0.02, n); l_dn = P0 * (1 + Dmod * 0.02)
    ax1.text(5.0, 34, "Yields +2 points:\n"
                      f"duration says {l_up - P0:+.1f}, truth is {p_up - P0:+.1f}\n"
                      f"-> you lose {abs(l_up - p_up):.1f} LESS than predicted\n\n"
                      "Yields -2 points:\n"
                      f"duration says {l_dn - P0:+.1f}, truth is {p_dn - P0:+.1f}\n"
                      f"-> you gain {abs(p_dn - l_dn):.1f} MORE than predicted",
             fontsize=10.0, color=GREY, va="bottom",
             bbox=dict(boxstyle="round,pad=0.5", fc="#eaf5ea", ec=C3, lw=1.2))
    ax1.set_title("Convexity is a GIFT: the curve sits above its own tangent")
    ax1.set_xlabel("Yield to maturity (%)"); ax1.set_ylabel("Price per 100 of face")
    ax1.set_ylim(0, 260); ax1.legend(fontsize=9.8, loc="upper right")
    ax1.grid(alpha=0.25); ax1.spines[["top", "right"]].set_visible(False)

    # --- right: callable bond, negative convexity -------------------------
    n2, cpn2, call = 10, 0.05, 102.0
    ys2 = np.linspace(0.005, 0.095, 400)
    straight = np.array([price(cpn2, y, n2) for y in ys2])
    # the issuer calls when refinancing pays: price is squeezed toward the
    # call price as yields fall. A simple, honest stylisation of the option.
    callable_p = call - 8.0 * np.log1p(np.exp((call - straight) / 8.0))
    callable_p = np.minimum(callable_p, straight)

    ax2.plot(ys2 * 100, straight, color=C1, lw=2.8, label="Straight (non-callable) bond")
    ax2.plot(ys2 * 100, callable_p, color=C5, lw=2.8, label="Callable bond")
    ax2.axhline(call, color=C2, lw=1.8, ls=":")
    ax2.text(8.6, call + 3.5, f"call price {call:.0f}", fontsize=10.2, color=C2, ha="right")
    ax2.fill_between(ys2 * 100, callable_p, straight, color=C2, alpha=0.13)
    ax2.text(1.35, 113, "the issuer's option\n— value taken FROM you",
             fontsize=10.2, color=C2, fontweight="bold", va="center")
    ax2.text(5.0, 144, "NEGATIVE CONVEXITY: when yields fall\n"
                       "you are capped, when they rise you are\n"
                       "not. You get the whole downside and only\n"
                       "part of the upside — which is why a\n"
                       "callable bond must pay MORE.",
             fontsize=10.0, color=GREY, va="top",
             bbox=dict(boxstyle="round,pad=0.5", fc="#fdeeee", ec=C2, lw=1.2))
    ax2.set_title("Negative convexity: a bond whose upside is someone else's option")
    ax2.set_xlabel("Yield to maturity (%)"); ax2.set_ylabel("Price per 100 of face")
    ax2.set_ylim(55, 162); ax2.legend(fontsize=9.8, loc="lower left")
    ax2.grid(alpha=0.25); ax2.spines[["top", "right"]].set_visible(False)

    fig.tight_layout()
    save(fig, 2)


# ------------------------------------------------------------------- fig 3
def fig3():
    s = np.linspace(0, 22, 400)                    # spread in percentage points
    fig, ax = plt.subplots(figsize=(11.4, 6.4))

    for R, c, lab in [(0.20, C2, "Recovery 20% (unsecured, bad outcome)"),
                      (0.40, C1, "Recovery 40% (the long-run average)"),
                      (0.60, C3, "Recovery 60% (secured, good collateral)")]:
        ax.plot(s, s / (1 - R), color=c, lw=2.6, label=lab)

    marks = [(0.80, "IG today  0.80%  (15 Sep 2026)", C1),
             (2.76, "HY today  2.76%  (15 Sep 2026)", C4),
             (6.56, "IG record  6.56%  (Dec 2008)", C5),
             (21.82, "HY record  21.82%  (Dec 2008)", C2)]
    for x, lab, c in marks:
        ax.axvline(x, color=c, lw=1.6, ls="--", alpha=0.8)
        ax.text(x + 0.28, 23.6, lab, fontsize=10.0, color=c, fontweight="bold",
                rotation=90, va="top", ha="left")
    ax.plot([2.76], [2.76 / 0.6], marker="o", ms=9, color=C4, zorder=6)
    ax.text(3.2, 3.0, "4.6% a year", fontsize=10.0, color=C4,
            fontweight="bold")

    ax.text(10.6, 10.2,
            "Read it as a BREAKEVEN, not a forecast:\n"
            "spread ~ (annual default rate) x (1 - recovery)\n\n"
            "At 40% recovery, today's 2.76% high-yield spread\n"
            "is paid for by a 4.6% annual default rate — which is\n"
            "roughly the long-run average. You are being paid the\n"
            "AVERAGE loss, with nothing left over for a bad decade.",
            fontsize=10.6, color=GREY, va="top",
            bbox=dict(boxstyle="round,pad=0.6", fc="#f2f2f2", ec=GREY, lw=1.2))

    ax.set_xlim(0, 22); ax.set_ylim(0, 30)
    ax.set_xlabel("Credit spread over the risk-free curve (percentage points)")
    ax.set_ylabel("Annual default rate the spread just pays for (%)")
    ax.set_title("What a credit spread has to cover — the breakeven default rate it implies")
    ax.legend(fontsize=10.2, loc="upper left")
    ax.grid(alpha=0.25); ax.spines[["top", "right"]].set_visible(False)
    save(fig, 3)


# ------------------------------------------------------------------- fig 4
# Real US Treasury par (constant-maturity) yields, 15 September 2026.
UST = {0.0833: 3.93, 0.25: 4.11, 0.5: 4.17, 1.0: 4.39, 2.0: 4.67, 3.0: 4.76,
       5.0: 4.83, 7.0: 4.91, 10.0: 5.00, 20.0: 5.40, 30.0: 5.36}


def pchip(x, y, xi):
    """Monotone cubic (Fritsch-Carlson) interpolation — no scipy on this box.

    Plain linear interpolation of the par curve puts a KINK at every quoted
    maturity, and the forward curve differentiates that kink into a spurious
    spike. A shape-preserving cubic removes the artefact without inventing
    curvature the data does not support.
    """
    x = np.asarray(x, float); y = np.asarray(y, float)
    h = np.diff(x); d = np.diff(y) / h
    m = np.zeros_like(y)
    m[0], m[-1] = d[0], d[-1]
    for k in range(1, len(y) - 1):
        if d[k - 1] * d[k] <= 0:
            m[k] = 0.0
        else:                                   # weighted harmonic mean
            w1, w2 = 2 * h[k] + h[k - 1], h[k] + 2 * h[k - 1]
            m[k] = (w1 + w2) / (w1 / d[k - 1] + w2 / d[k])
    out = np.empty_like(np.asarray(xi, float))
    idx = np.clip(np.searchsorted(x, xi) - 1, 0, len(x) - 2)
    for j, (xq, i) in enumerate(zip(np.atleast_1d(xi), idx)):
        t = (xq - x[i]) / h[i]
        h00 = 2 * t**3 - 3 * t**2 + 1; h10 = t**3 - 2 * t**2 + t
        h01 = -2 * t**3 + 3 * t**2;    h11 = t**3 - t**2
        out[j] = h00 * y[i] + h10 * h[i] * m[i] + h01 * y[i + 1] + h11 * h[i] * m[i + 1]
    return out


def bootstrap_spots(par_mats, par_yields, horizon=30.0, freq=2):
    """Bootstrap semiannual zero rates from a par curve (yields in percent)."""
    grid = np.arange(1, int(horizon * freq) + 1) / freq
    par = pchip(par_mats, par_yields, grid) / 100.0
    df = np.zeros(len(grid))
    running = 0.0
    for i, (T, c) in enumerate(zip(grid, par)):
        df[i] = (1 - (c / freq) * running) / (1 + c / freq)
        running += df[i]
    spot = freq * (df ** (-1 / (grid * freq)) - 1)
    return grid, par * 100, spot * 100, df


def fig4():
    mats = np.array(sorted(UST)); pars = np.array([UST[m] for m in mats])
    grid, parc, spot, df = bootstrap_spots(mats, pars)

    # 1-year implied forwards from the discount factors
    fw_t, fw = [], []
    for k in range(2, len(grid), 2):                 # every whole year
        if k + 2 <= len(grid):
            fw_t.append(grid[k - 1])
            fw.append((df[k - 1] / df[k + 1] - 1) * 100)
    fw_t = np.array(fw_t); fw = np.array(fw)

    fig, ax = plt.subplots(figsize=(11.6, 6.4))
    ax.plot(grid, parc, color=C1, lw=2.8, label="Par (quoted) curve — what a new bond's coupon would be")
    ax.plot(grid, spot, color=C2, lw=2.8, ls="--", label="Spot (zero-coupon) curve — the true price of time")
    ax.plot(fw_t, fw, color=C3, lw=2.2, ls=":", marker="o", ms=4.2,
            label="1-year implied forwards — what the curve is betting on")
    ax.scatter(mats, pars, color=C1, zorder=5, s=34)

    ax.annotate("3 months 4.11%", xy=(0.25, 4.11), xytext=(1.2, 3.72),
                fontsize=10.0, color=GREY, arrowprops=dict(arrowstyle="->", color=GREY))
    ax.annotate("10 years 5.00%", xy=(10, 5.00), xytext=(9.3, 4.34),
                fontsize=10.0, color=GREY, ha="right",
                arrowprops=dict(arrowstyle="->", color=GREY))
    ax.annotate("20y 5.40% sits ABOVE 30y 5.36%\n— the long end sags, a supply-and-\nconvexity effect, not a forecast",
                xy=(20, 5.40), xytext=(30.6, 7.72), fontsize=10.0, color=GREY,
                ha="right", va="top", arrowprops=dict(arrowstyle="->", color=GREY))
    ax.annotate("the forwards hump to 6.60% for year 16,\nthen fall away — the arithmetic consequence\nof the par curve's sag, not a rate forecast",
                xy=(16, 6.60), xytext=(10.4, 6.42), fontsize=10.0, color=C3,
                ha="right", va="center", arrowprops=dict(arrowstyle="->", color=C3))

    # The explanatory box lives in the empty lower right. It used to sit top
    # left, where it covered the forward curve's entire hump (years 10-19) —
    # which is the one thing this figure exists to show.
    ax.text(30.7, 4.92,
            "One market, three curves. The PAR curve is what you are quoted. The\n"
            "SPOT curve is what each single future dollar actually costs — it sits\n"
            "ABOVE the par curve wherever the curve slopes up, because a coupon\n"
            "bond's early payments are discounted at cheaper short rates. The\n"
            "FORWARDS are the arithmetic consequence: the one-year rates that\n"
            "would make lending long and rolling short break even.",
            fontsize=10.0, color=GREY, va="top", ha="right",
            bbox=dict(boxstyle="round,pad=0.5", fc="#f2f2f2", ec=GREY, lw=1.1))

    ax.set_xlabel("Maturity (years)"); ax.set_ylabel("Yield (% per year)")
    ax.set_title("The US Treasury curve on 15 September 2026, read three ways")
    ax.set_xlim(0, 31); ax.set_ylim(2.9, 7.8)
    ax.legend(fontsize=10.0, loc="upper left")
    ax.grid(alpha=0.25); ax.spines[["top", "right"]].set_visible(False)
    save(fig, 4)


# ------------------------------------------------------------------- fig 5
def fig5():
    n, y0, y1 = 10, 0.04, 0.06
    D = macaulay(y0, y1, n)              # duration measured at the new, higher yield
    k = np.arange(0, n + 1)

    # --- a single bond bought at par, coupons reinvested at the prevailing yield
    def single(y):
        acc = np.array([0.0 if j == 0 else y0 * 100 * (((1 + y) ** j - 1) / y) for j in k])
        mv = np.array([100.0 if j == n else price(y0, y, n - j) for j in k])
        return acc + mv

    base_b, shock_b = single(y0), single(y1)

    # --- a constant-maturity fund: instant mark-down, then compounds at the new yield
    yrs = np.linspace(0, n, 601)
    drop = price(y0, y1, n) / 100.0
    base_f = 100 * (1 + y0) ** yrs
    shock_f = 100 * drop * (1 + y1) ** yrs
    cross = -np.log(drop) / np.log((1 + y1) / (1 + y0))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.8, 6.0), sharey=True)

    for ax, x, base, shock, title in [
            (ax1, k, base_b, shock_b, "A single 10-year bond you hold to maturity"),
            (ax2, yrs, base_f, shock_f, "A constant-maturity 10-year bond FUND")]:
        ax.plot(x, base, color=GREY, lw=2.2, ls="--", label="If yields had stayed at 4%")
        ax.plot(x, shock, color=C1, lw=2.8, marker="o" if len(x) < 30 else None, ms=5,
                label="Yields jump to 6% on day one")
        ax.fill_between(x, shock, base, where=(shock < base), color=C2, alpha=0.16)
        ax.fill_between(x, shock, base, where=(shock >= base), color=C3, alpha=0.16)
        ax.set_xlabel("Years after the rate shock")
        ax.set_title(title)
        ax.grid(alpha=0.25); ax.spines[["top", "right"]].set_visible(False)
        ax.set_xlim(0, n); ax.set_ylim(68, 178)

    ax1.set_ylabel("Value of 100 invested (coupons reinvested)")
    ax1.axvline(D, color=C4, lw=1.8, ls=":")
    ax1.text(D - 0.25, 174, f"duration {D:.1f} yrs", fontsize=10.2, color=C4,
             fontweight="bold", ha="right", va="top")
    ax1.annotate(f"instant paper loss {(price(y0, y1, n) - 100):+.1f} — but you have not\n"
                 "lost anything you were going to spend",
                 xy=(0.08, price(y0, y1, n)), xytext=(1.15, 82), fontsize=9.8, color=C2,
                 va="top", arrowprops=dict(arrowstyle="->", color=C2))
    ax1.text(4.5, 108, f"Ends at {shock_b[-1]:.0f} against {base_b[-1]:.0f}:\n"
                       "the rate rise made you RICHER,\n"
                       "because every coupon reinvests\n"
                       "at 6% instead of 4%",
             fontsize=9.8, color=C3, fontweight="bold", va="top")
    ax1.legend(fontsize=9.6, loc="upper left")

    ax2.axvline(cross, color=C4, lw=1.8, ls=":")
    ax2.text(cross - 0.25, 174, f"crossover {cross:.1f} yrs", fontsize=10.2, color=C4,
             fontweight="bold", ha="right", va="top")
    ax2.text(3.8, 102, "A fund never 'pulls to par' — and it does not\n"
                        "need to. It rolls into the new, higher yield and\n"
                        "catches up at about the DURATION horizon.\n\n"
                        "-> If your horizon is longer than the duration,\n"
                        "   a yield rise is GOOD news in bad clothes.",
             fontsize=9.8, color=GREY, va="top")
    ax2.legend(fontsize=9.6, loc="upper left")

    fig.suptitle("Was the 2022 bond rout a disaster? It depends entirely on your horizon versus your duration",
                 fontsize=13.2, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.945])
    save(fig, 5)
    print(f"  (single bond end {shock_b[-1]:.2f} vs {base_b[-1]:.2f}; "
          f"fund crossover {cross:.2f}y; D={D:.2f}; day-one price {price(y0, y1, n):.2f})")

if __name__ == "__main__":
    fig1(); fig2(); fig3(); fig4(); fig5()
    print("done")
