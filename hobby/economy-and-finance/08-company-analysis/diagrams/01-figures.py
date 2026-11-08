#!/usr/bin/env python3
"""Figures for Econ E08 §1 — ratio analysis.

Editable source of truth for the committed SVGs (see agent-docs/diagrams.md).
Every number is COMPUTED from filed Form 10-K figures, and the identities the
text asserts (ROA = margin x turnover, ROE = ROA x leverage, CCC = DSO + DIO
- DPO) are asserted here too.

Source: SEC XBRL companyfacts API, 10-K facts only; flows filtered to
durations of 330-400 days (the trap recorded in E07 §1 §10b), balances taken
at each fiscal year end. Ratios that put a flow over a balance use the
AVERAGE of the opening and closing balance (§1 rule 1). USD millions.

  fig1 — SAME RETURN, OPPOSITE BUSINESSES (§3). Net margin against asset
         turnover, latest fiscal year, eight companies, on iso-ROA curves.
  fig2 — A RETURN YOU CAN MANUFACTURE (§3). (a) Apple FY2017-FY2026: ROA
         and ROE. (b) Home Depot FY2016-FY2025: ROA stays 14-25% while
         year-end equity swings through zero, so ROE is meaningless.
  fig3 — THE CASH CONVERSION CYCLE (§4). DSO + DIO - DPO, latest year.
"""
import os

import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt
import numpy as np

OUT = os.path.dirname(os.path.abspath(__file__))
BASE = "01-ratio-analysis"
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


# Latest fiscal year. (label, revenue, COGS, net income, assets open, assets
# close, equity open, equity close, AR open, AR close, inventory open,
# inventory close, AP open, AP close). Target reports no receivables line.
LATEST = {
    "Apple FY2026":      (478_834, 245_232, 132_175, 359_241, 404_548, 73_733, 112_093, 39_777, 43_817, 5_718, 14_541, 69_860, 82_252),
    "Microsoft FY2026":  (331_839, 106_374, 133_749, 619_003, 758_376, 343_479, 442_387, 69_905, 80_876, 938, 1_397, 27_724, 42_416),
    "NVIDIA FY2026":     (215_938, 62_475, 120_067, 111_601, 206_803, 79_327, 157_293, 23_065, 38_466, 10_080, 21_403, 6_310, 9_812),
    "Amazon 2025":       (716_924, 356_414, 77_670, 624_894, 818_042, 285_970, 411_065, 55_451, 67_729, 34_214, 38_325, 94_363, 121_909),
    "Walmart FY2026":    (706_413, 535_395, 21_893, 260_823, 284_668, 91_013, 99_617, 9_975, 11_172, 56_435, 58_851, 58_666, 63_061),
    "Costco FY2026":     (303_154, 264_279, 9_226, 77_099, 89_045, 29_164, 35_803, 3_203, 3_959, 18_116, 19_324, 19_783, 22_591),
    "Target FY2025":     (104_780, 75_511, 3_705, 57_769, 59_490, 14_666, 16_165, 0, 0, 12_740, 12_304, 13_053, 12_622),
    "Home Depot FY2025": (164_683, 109_818, 14_156, 96_119, 105_095, 6_640, 12_813, 4_903, 5_597, 23_451, 25_817, 11_938, 11_491),
}


def dupont(r):
    rev, cogs, ni, a0, a1, e0, e1 = r[:7]
    A, E = (a0 + a1) / 2, (e0 + e1) / 2
    nm, to, lev = ni / rev, rev / A, A / E
    roa, roe = ni / A, ni / E
    assert abs(nm * to - roa) < 1e-12 and abs(roa * lev - roe) < 1e-12
    return nm, to, roa, lev, roe


def ccc(r):
    rev, cogs = r[0], r[1]
    ar, inv, ap = (r[7] + r[8]) / 2, (r[9] + r[10]) / 2, (r[11] + r[12]) / 2
    dso, dio, dpo = 365 * ar / rev, 365 * inv / cogs, 365 * ap / cogs
    return dso, dio, dpo, dso + dio - dpo


def fig1():
    fig, ax = plt.subplots(figsize=(11.2, 6.6))
    t = np.linspace(0.2, 4.2, 400)
    for roa, ls in [(0.05, ":"), (0.10, "--"), (0.20, "-."), (0.40, "-")]:
        ax.plot(t, 100 * roa / t, color="#bbbbbb", ls=ls, lw=1.2, zorder=1)
        x = {0.05: 0.36, 0.10: 0.47, 0.20: 0.62, 0.40: 2.4}[roa]
        ax.text(x + 0.03, 100 * roa / x, f"ROA {roa:.0%}", color=GREY, fontsize=9.6, ha="left",
                va="bottom")
    off = {"Apple FY2026": (8, 6), "Microsoft FY2026": (8, 4), "NVIDIA FY2026": (8, -4),
           "Amazon 2025": (8, 4), "Walmart FY2026": (6, 7), "Costco FY2026": (-4, 24),
           "Target FY2025": (8, -12), "Home Depot FY2025": (8, 4)}
    for k, r in LATEST.items():
        nm, to, roa, lev, roe = dupont(r)
        ax.scatter(to, 100 * nm, s=70, color=C2 if roa >= 0.2 else C1, zorder=3)
        ax.annotate(f"{k}\n{100*nm:.1f}% × {to:.2f} = {100*roa:.1f}%", (to, 100 * nm),
                    textcoords="offset points", xytext=off[k], fontsize=9.4,
                    ha="right" if off[k][0] < 0 else "left")
    ax.set_xlim(0.2, 4.3); ax.set_ylim(0, 62)
    ax.set_xlabel("asset turnover = revenue ÷ average total assets (times a year)")
    ax.set_ylabel("net margin = net income ÷ revenue (%)")
    ax.set_title("Two routes to the same return: margin × turnover = return on assets",
                 fontsize=13.2, fontweight="bold")
    ax.grid(alpha=0.2); ax.spines[["top", "right"]].set_visible(False)
    c = dupont(LATEST["Costco FY2026"]); w = dupont(LATEST["Amazon 2025"])
    assert abs(c[2] - 0.111) < 0.001 and abs(w[2] - 0.108) < 0.001
    fig.tight_layout(); save(fig, 1)


# (fiscal year end label, revenue, net income, assets open, assets close,
#  equity open, equity close)
APPLE = [
    ("FY17", 229_234, 48_351, 321_686, 375_319, 128_249, 134_047),
    ("FY18", 265_595, 59_531, 375_319, 365_725, 134_047, 107_147),
    ("FY19", 260_174, 55_256, 365_725, 338_516, 107_147, 90_488),
    ("FY20", 274_515, 57_411, 338_516, 323_888, 90_488, 65_339),
    ("FY21", 365_817, 94_680, 323_888, 351_002, 65_339, 63_090),
    ("FY22", 394_328, 99_803, 351_002, 352_755, 63_090, 50_672),
    ("FY23", 383_285, 96_995, 352_755, 352_583, 50_672, 62_146),
    ("FY24", 391_035, 93_736, 352_583, 364_980, 62_146, 56_950),
    ("FY25", 416_161, 112_010, 364_980, 359_241, 56_950, 73_733),
    ("FY26", 478_834, 132_175, 359_241, 404_548, 73_733, 112_093),
]
HD = [
    ("FY16", 94_595, 7_957, 41_973, 42_966, 6_316, 4_333),
    ("FY17", 100_904, 8_630, 42_966, 44_529, 4_333, 1_454),
    ("FY18", 108_203, 11_121, 44_529, 44_003, 1_454, -1_878),
    ("FY19", 110_225, 11_242, 44_003, 51_236, -1_878, -3_116),
    ("FY20", 132_110, 12_866, 51_236, 70_581, -3_116, 3_299),
    ("FY21", 151_157, 16_433, 70_581, 71_876, 3_299, -1_696),
    ("FY22", 157_403, 17_105, 71_876, 76_445, -1_696, 1_562),
    ("FY23", 152_669, 15_143, 76_445, 76_530, 1_562, 1_044),
    ("FY24", 159_514, 14_806, 76_530, 96_119, 1_044, 6_640),
    ("FY25", 164_683, 14_156, 96_119, 105_095, 6_640, 12_813),
]


def fig2():
    fig, (a, b) = plt.subplots(1, 2, figsize=(13.4, 5.8))
    yrs = [r[0] for r in APPLE]
    roa = [100 * r[2] / ((r[3] + r[4]) / 2) for r in APPLE]
    roe = [100 * r[2] / ((r[5] + r[6]) / 2) for r in APPLE]
    assert round(roa[0]) == 14 and round(roe[0]) == 37 and round(roe[-1]) == 142
    a.plot(yrs, roe, "o-", color=C2, lw=2.2, label="ROE = net income ÷ average equity")
    a.plot(yrs, roa, "s-", color=C1, lw=2.2, label="ROA = net income ÷ average assets")
    for i in (0, 5, 9):
        a.annotate(f"{roe[i]:.0f}%", (i, roe[i]), textcoords="offset points", xytext=(0, 8),
                   ha="center", color=C2, fontsize=10, fontweight="bold")
        a.annotate(f"{roa[i]:.0f}%", (i, roa[i]), textcoords="offset points", xytext=(0, -16),
                   ha="center", color=C1, fontsize=10, fontweight="bold")
    a.set_ylim(0, 200); a.set_ylabel("%")
    a.set_title("(a) Apple: ROA 14% → 35%, ROE 37% → 142%", fontweight="bold")
    a.legend(loc="center left", fontsize=9.6, frameon=False)
    a.grid(alpha=0.2); a.spines[["top", "right"]].set_visible(False)

    yrs = [r[0] for r in HD]
    roa = [100 * r[2] / ((r[3] + r[4]) / 2) for r in HD]
    roe = [100 * r[2] / ((r[5] + r[6]) / 2) for r in HD]
    eq = [r[6] / 1000 for r in HD]
    assert 14 <= min(roa) and max(roa) <= 25.2
    b2 = b.twinx()
    b2.bar(yrs, eq, color=["#c7d9ea" if e > 0 else "#f2c4c4" for e in eq], width=0.6, zorder=1)
    b2.axhline(0, color=GREY, lw=0.8)
    b2.set_ylabel("year-end shareholders' equity, USD bn (bars)")
    b2.set_ylim(-6, 14)
    b.set_zorder(b2.get_zorder() + 1); b.patch.set_visible(False)
    b.plot(yrs, roa, "s-", color=C1, lw=2.2, label="ROA")
    b.set_ylim(0, 40); b.set_ylabel("ROA, % (line)")
    for i, r in enumerate(roe):
        b.text(i, 36.5 if i % 2 == 0 else 33.5, f"{r:+,.0f}%", ha="center", fontsize=8.6,
               color=C2, fontweight="bold")
    b.text(-0.5, 39, "ROE that year (red numbers):", fontsize=9, color=C2)
    b.set_title("(b) Home Depot: ROA 14–25%; ROE meaningless", fontweight="bold")
    b.spines[["top"]].set_visible(False); b2.spines[["top"]].set_visible(False)
    fig.tight_layout(); save(fig, 2)


def fig3():
    order = ["NVIDIA FY2026", "Home Depot FY2025", "Walmart FY2026", "Costco FY2026",
             "Target FY2025", "Microsoft FY2026", "Amazon 2025", "Apple FY2026"]
    fig, ax = plt.subplots(figsize=(11.6, 5.8))
    y = np.arange(len(order))[::-1]
    for yi, k in zip(y, order):
        dso, dio, dpo, c = ccc(LATEST[k])
        assert abs(dso + dio - dpo - c) < 1e-9
        ax.barh(yi, dso, color=C1, height=0.55, label="DSO (receivables)" if yi == y[0] else None)
        ax.barh(yi, dio, left=dso, color=C4, height=0.55, label="DIO (inventory)" if yi == y[0] else None)
        ax.barh(yi, -dpo, color=C5, height=0.55, alpha=0.75, label="− DPO (payables)" if yi == y[0] else None)
        ax.plot([c], [yi], marker="D", color="black", ms=7, zorder=4)
        ax.text(max(dso + dio, 0) + 4, yi, f"CCC {c:+.0f} days", va="center", fontsize=10.2,
                fontweight="bold", color=C2 if c < 0 else "black")
    ax.axvline(0, color=GREY, lw=1)
    ax.set_yticks(y); ax.set_yticklabels(order)
    ax.set_xlabel("days (average balances over the year)")
    ax.set_title("Cash conversion cycle = DSO + DIO − DPO  (black diamond)", fontsize=13.2,
                 fontweight="bold")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.13), fontsize=9.6, frameon=False, ncol=3)
    ax.set_xlim(-135, 185)
    ax.grid(axis="x", alpha=0.2); ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); save(fig, 3)


if __name__ == "__main__":
    for k, r in LATEST.items():
        nm, to, roa, lev, roe = dupont(r); d = ccc(r)
        print(f"{k:18s} NM {100*nm:5.1f}% TO {to:4.2f} ROA {100*roa:5.1f}% lev {lev:5.2f} "
              f"ROE {100*roe:6.1f}%  DSO {d[0]:4.0f} DIO {d[1]:4.0f} DPO {d[2]:4.0f} CCC {d[3]:+4.0f}")
    for name, s in (("Apple", APPLE), ("HD", HD)):
        for r in s:
            print(name, r[0], f"ROA {100*r[2]/((r[3]+r[4])/2):.1f} ROE {100*r[2]/((r[5]+r[6])/2):,.0f}")
    fig1(); fig2(); fig3()
