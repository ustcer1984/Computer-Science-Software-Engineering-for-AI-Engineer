#!/usr/bin/env python3
"""Figures for Econ E08 §2 — common-size, trends, and reading a whole annual report.

Editable source of truth for the committed SVGs (see agent-docs/diagrams.md).
Every number is from filed Form 10-K figures, through the SEC XBRL companyfacts
API, 10-K facts only; flows filtered to durations of 330-400 days (E07 §1 §10b),
balances at each fiscal year end. USD millions.

"Latest-filed" means the value as it appears in the most recent 10-K that
reports that year (so restated comparatives win). "First-reported" means the
value in the first 10-K that reported it. Fig 4 is the difference.

  fig1 — COMMON-SIZE INCOME STATEMENTS (§1). Every line per 100 of revenue,
         latest fiscal year: Walmart, Costco, Target, Microsoft.
  fig2 — A SOFTWARE COMPANY BECOMES ASSET-HEAVY (§2). Microsoft FY2016-FY2026:
         (a) index, FY2016 = 100, log scale; (b) three common-size ratios over
         time.
  fig3 — A TREND THAT WARNED (§3). Target FY2018-FY2025: (a) index of revenue,
         inventory and operating income; (b) gross and operating margin.
  fig4 — A TREND THAT BREAKS (§4). Microsoft FY2015-FY2019 revenue and
         operating income, first-reported against restated (ASC 606).
"""
import os

import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt
import numpy as np

OUT = os.path.dirname(os.path.abspath(__file__))
BASE = "02-reading-an-annual-report"
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


# ---------------------------------------------------------------- fig 1
# (label, revenue, [(line, amount)...]) — lines sum to revenue exactly.
# Walmart revenue is TOTAL revenues (net sales 706,413 + membership and other
# income 6,750). Microsoft's selling+general line is the residual of the
# reported lines (sales and marketing + general and administrative).
IS = {
    "Walmart FY2026": (713_163, [("cost of sales", 535_395), ("SG&A", 147_943),
                                  ("operating income", 29_825)]),
    "Costco FY2026": (303_154, [("cost of sales", 264_279), ("SG&A", 27_190),
                                 ("operating income", 11_685)]),
    "Target FY2025": (104_780, [("cost of sales", 75_511), ("SG&A", 21_535),
                                 ("depreciation (own line)", 2_617),
                                 ("operating income", 5_117)]),
    "Microsoft FY2026": (331_839, [("cost of sales", 106_374), ("R&D", 35_562),
                                    ("S&M + G&A", 331_839 - 106_374 - 35_562 - 155_237),
                                    ("operating income", 155_237)]),
}
COL = {"cost of sales": "#9ecae1", "SG&A": "#fdae6b", "depreciation (own line)": "#bcbddc",
       "R&D": "#c7e9c0", "S&M + G&A": "#fdd0a2", "operating income": C2}


def common_size(rev, lines):
    assert sum(a for _, a in lines) == rev, "lines must sum to revenue"
    return [(k, 100 * a / rev) for k, a in lines]


def fig1():
    fig, ax = plt.subplots(figsize=(11.6, 4.9))
    names = list(IS)[::-1]
    seen = set()
    for y, k in enumerate(names):
        rev, lines = IS[k]
        left = 0.0
        for lab, pct in common_size(rev, lines):
            ax.barh(y, pct, left=left, color=COL[lab], edgecolor="white", height=0.62,
                    label=None if lab in seen else lab)
            seen.add(lab)
            if pct >= 3.5:
                ax.text(left + pct / 2, y, f"{pct:.1f}", ha="center", va="center", fontsize=10.5,
                        color="white" if lab == "operating income" else "black")
            else:
                ax.text(left + pct / 2, y + 0.44, f"{pct:.1f}", ha="center", va="bottom", fontsize=9.6,
                        color=GREY)
            left += pct
        assert abs(left - 100) < 1e-9
    ax.set_yticks(range(len(names)), names)
    ax.set_xlim(0, 100)
    ax.set_xlabel("per 100 of revenue")
    ax.set_title("Common-size income statements: where each 100 of revenue went, latest fiscal year",
                 fontsize=13, fontweight="bold")
    ax.legend(ncol=6, fontsize=9.6, loc="upper center", bbox_to_anchor=(0.5, -0.17), frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); save(fig, 1)


# ---------------------------------------------------------------- fig 2
FY = list(range(2016, 2027))
MSFT = {  # latest-filed
    "revenue": [91_154, 96_571, 110_360, 125_843, 143_015, 168_088, 198_270, 211_915, 245_122, 281_724, 331_839],
    "operating income": [26_078, 29_025, 35_058, 42_959, 52_959, 69_916, 83_383, 88_523, 109_433, 128_528, 155_237],
    "net PP&E": [18_356, 23_734, 29_460, 36_477, 44_151, 59_715, 74_398, 95_641, 135_591, 204_966, 313_076],
    "capex": [8_343, 8_129, 11_632, 13_925, 15_441, 20_622, 23_886, 28_107, 44_477, 64_551, 115_948],
    "total assets": [193_468, 250_312, 258_848, 286_556, 301_311, 333_779, 364_840, 411_976, 512_163, 619_003, 758_376],
}


def cagr(a, b, years):
    return (b / a) ** (1 / years) - 1


def fig2():
    m = MSFT
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(13.2, 5.4))
    for k, c in [("revenue", C1), ("operating income", C3), ("net PP&E", C2), ("capex", C4)]:
        idx = [100 * v / m[k][0] for v in m[k]]
        ax.plot(FY, idx, "o-", color=c, lw=2, ms=4)
        g = cagr(m[k][0], m[k][-1], 10)
        ax.annotate(f"{k}\n{idx[-1]:,.0f} ({100*g:.1f}%/yr)", (FY[-1], idx[-1]),
                    textcoords="offset points", xytext=(6, {"capex": -14, "net PP&E": 8}.get(k, 0)),
                    fontsize=9.6, color=c, va="center")
    ax.set_yscale("log")
    ax.set_yticks([100, 200, 500, 1000, 2000], ["100", "200", "500", "1,000", "2,000"])
    ax.set_xlim(2015.6, 2029.4)
    ax.set_title("(a) index, FY2016 = 100 (log scale)", fontsize=12)
    ax.set_xlabel("fiscal year (ends June)")
    ax.grid(alpha=0.2); ax.spines[["top", "right"]].set_visible(False)

    ppe_share = [100 * p / a for p, a in zip(m["net PP&E"], m["total assets"])]
    capex_rev = [100 * c / r for c, r in zip(m["capex"], m["revenue"])]
    om = [100 * o / r for o, r in zip(m["operating income"], m["revenue"])]
    for s, lab, c in [(ppe_share, "net PP&E ÷ total assets", C2), (capex_rev, "capex ÷ revenue", C4),
                      (om, "operating margin", C3)]:
        bx.plot(FY, s, "o-", color=c, lw=2, ms=4)
        bx.annotate(f"{lab}\n{s[0]:.1f}% → {s[-1]:.1f}%", (FY[-1], s[-1]), textcoords="offset points",
                    xytext=(6, 0), fontsize=9.6, color=c, va="center")
    bx.set_xlim(2015.6, 2029.6); bx.set_ylim(0, 52)
    bx.set_title("(b) common-size, over time (%)", fontsize=12)
    bx.set_xlabel("fiscal year (ends June)")
    bx.grid(alpha=0.2); bx.spines[["top", "right"]].set_visible(False)
    fig.suptitle("Microsoft FY2016–FY2026: revenue grew 3.6 times, net property and equipment 17 times",
                 fontsize=13.2, fontweight="bold")
    assert abs(ppe_share[0] - 9.5) < 0.05 and abs(ppe_share[-1] - 41.3) < 0.05
    fig.tight_layout(); save(fig, 2)


# ---------------------------------------------------------------- fig 3
# Target fiscal years: FY2021 ends 29 January 2022, etc.
TGT_FY = list(range(2018, 2026))
TGT = {
    "revenue": [75_356, 78_112, 93_561, 106_005, 109_120, 107_412, 106_566, 104_780],
    "cogs": [53_299, 54_864, 66_177, 74_963, 82_306, 77_828, 76_502, 75_511],
    "operating income": [4_110, 4_658, 6_539, 8_946, 3_848, 5_707, 5_566, 5_117],
    "inventory": [9_497, 8_992, 10_653, 13_902, 13_499, 11_886, 12_740, 12_304],
}


def fig3():
    t = TGT
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(13.2, 5.3))
    for k, c in [("revenue", C1), ("inventory", C4), ("operating income", C3)]:
        idx = [100 * v / t[k][0] for v in t[k]]
        ax.plot(TGT_FY, idx, "o-", color=c, lw=2, ms=4, label=k)
    ax.axvspan(2020.6, 2021.4, color="#fde0c5", alpha=0.6, zorder=0)
    ax.annotate("FY2021: inventory +30.5%,\nrevenue +13.3%", (2021, 100 * 13_902 / 9_497),
                textcoords="offset points", xytext=(-150, 22), fontsize=9.8,
                arrowprops=dict(arrowstyle="->", color=GREY))
    ax.annotate("FY2022: operating\nincome −57%", (2022, 100 * 3_848 / 4_110), textcoords="offset points",
                xytext=(26, 46), fontsize=9.8, arrowprops=dict(arrowstyle="->", color=GREY))
    ax.set_title("(a) index, FY2018 = 100", fontsize=12)
    ax.set_xlabel("fiscal year (FY2021 ends 29 January 2022)")
    ax.legend(fontsize=9.8, frameon=False, loc="upper left")
    ax.grid(alpha=0.2); ax.spines[["top", "right"]].set_visible(False)

    gm = [100 * (r - c) / r for r, c in zip(t["revenue"], t["cogs"])]
    om = [100 * o / r for o, r in zip(t["operating income"], t["revenue"])]
    bx.plot(TGT_FY, gm, "o-", color=C1, lw=2, ms=4, label="gross margin (on total revenue)")
    bx.plot(TGT_FY, om, "o-", color=C3, lw=2, ms=4, label="operating margin")
    for x, g, o in zip(TGT_FY, gm, om):
        bx.text(x, g + 0.8, f"{g:.1f}", ha="center", fontsize=9, color=C1)
        bx.text(x, o + 0.8, f"{o:.1f}", ha="center", fontsize=9, color=C3)
    bx.axvspan(2020.6, 2021.4, color="#fde0c5", alpha=0.6, zorder=0)
    bx.set_ylim(0, 35)
    bx.set_title("(b) margins (%)", fontsize=12)
    bx.set_xlabel("fiscal year")
    bx.legend(fontsize=9.8, frameon=False, loc="lower left")
    bx.grid(alpha=0.2); bx.spines[["top", "right"]].set_visible(False)
    fig.suptitle("Target: inventory ran ahead of sales in FY2021, and the margin paid for it in FY2022",
                 fontsize=13.2, fontweight="bold")
    assert abs(13_902 / 10_653 - 1.305) < 0.001 and abs(106_005 / 93_561 - 1.133) < 0.001
    fig.tight_layout(); save(fig, 3)


# ---------------------------------------------------------------- fig 4
MS_FIRST = {"revenue": {2015: 93_580, 2016: 85_320, 2017: 89_950, 2018: 110_360, 2019: 125_843},
            "operating income": {2015: 18_161, 2016: 20_182, 2017: 22_326, 2018: 35_058, 2019: 42_959}}
MS_LATEST = {"revenue": {2016: 91_154, 2017: 96_571, 2018: 110_360, 2019: 125_843},
             "operating income": {2016: 26_078, 2017: 29_025, 2018: 35_058, 2019: 42_959}}


def fig4():
    fig, axes = plt.subplots(1, 2, figsize=(13.2, 5.0))
    for ax, k in zip(axes, ["revenue", "operating income"]):
        f, l = MS_FIRST[k], MS_LATEST[k]
        ax.plot(list(f), [v / 1000 for v in f.values()], "o--", color=GREY, lw=1.8,
                label="each year as first reported")
        ax.plot(list(l), [v / 1000 for v in l.values()], "o-", color=C1, lw=2.2,
                label="as restated in later 10-Ks (ASC 606)")
        g_first = f[2018] / f[2017] - 1
        g_rest = l[2018] / l[2017] - 1
        ax.annotate(f"FY2018 growth:\n{100*g_first:+.1f}% chaining first-reported\n"
                    f"{100*g_rest:+.1f}% on the restated basis",
                    (2017.5, (f[2017] + l[2018]) / 2000), textcoords="offset points", xytext=(-150, 40),
                    fontsize=9.6, arrowprops=dict(arrowstyle="->", color=GREY))
        ax.set_xticks(list(f), [f"FY{y}" for y in f])
        ax.set_title(f"{k} (USD billions)", fontsize=12)
        ax.legend(fontsize=9.6, frameon=False, loc="upper left")
        ax.grid(alpha=0.2); ax.spines[["top", "right"]].set_visible(False)
    fig.suptitle("Microsoft: the same years, two sets of numbers — a trend built across a restatement breaks",
                 fontsize=13.2, fontweight="bold")
    fig.tight_layout(); save(fig, 4)


if __name__ == "__main__":
    fig1(); fig2(); fig3(); fig4()
    # Numbers quoted in the text, recomputed here so the prose cannot drift.
    m = MSFT
    print("MSFT CAGR rev %.1f%%  PP&E %.1f%%  OI %.1f%%  capex %.1f%%" % tuple(
        100 * cagr(m[k][0], m[k][-1], 10) for k in ["revenue", "net PP&E", "operating income", "capex"]))
    print("MSFT capex/rev FY16 %.1f%% FY26 %.1f%%; OI margin FY16 %.1f%% FY26 %.1f%%" % (
        100 * m["capex"][0] / m["revenue"][0], 100 * m["capex"][-1] / m["revenue"][-1],
        100 * m["operating income"][0] / m["revenue"][0], 100 * m["operating income"][-1] / m["revenue"][-1]))
    t = TGT
    for i in range(1, len(TGT_FY)):
        print("TGT FY%d rev %+.1f%% inv %+.1f%% cogs %+.1f%% OI %+.1f%% GM %.1f%% OM %.1f%% DIO(ye) %.0f" % (
            TGT_FY[i], *(100 * (t[k][i] / t[k][i - 1] - 1) for k in ["revenue", "inventory", "cogs",
                                                                       "operating income"]),
            100 * (t["revenue"][i] - t["cogs"][i]) / t["revenue"][i],
            100 * t["operating income"][i] / t["revenue"][i], 365 * t["inventory"][i] / t["cogs"][i]))
    for k, (rev, lines) in IS.items():
        print(k, [(a, round(p, 2)) for a, p in common_size(rev, lines)])
