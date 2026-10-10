#!/usr/bin/env python3
"""Figures for Econ E07 §3 — the balance sheet.

Editable source of truth for the committed SVGs (see agent-docs/diagrams.md).
Every panel is COMPUTED from filed figures rather than drawn by hand, and the
identities that the text asserts are asserted here too, so prose and picture
cannot drift apart.

Sources: each company's most recent Form 10-K as filed with the SEC, read off
the filing's own CONSOLIDATED BALANCE SHEETS and the long-term debt note, with
flow figures taken from the XBRL companyconcept API filtered to periods of
330-400 days (the trap recorded in E07 §1 §10b).

  fig1 — "ASSETS" IS NOT ONE KIND OF THING. Five balance sheets normalised to
         a share of total assets. Delta is aeroplanes (56.6% property), Costco
         is shelves and stock, Pfizer is 60.0% goodwill and intangibles --
         things it BOUGHT -- and NVIDIA holds almost no property at all. The
         teaching case is MICROSOFT, whose property share (44.5%) is now
         HIGHER THAN COSTCO'S, because of the data-centre build.
  fig2 — THE LINE THAT IS AN OPINION. Goodwill plus intangibles as a share of
         total assets and as a share of BOOK EQUITY. For five of seven
         companies the second bar exceeds 100%: write those assets to zero and
         equity is negative. Kraft Heinz actually did take a 15.4bn impairment
         in Q4 2018.
  fig3 — THE CURRENT RATIO IS A WEAK INSTRUMENT. Seven current ratios spanning
         0.40 to 3.91, with Apple and Salesforce below the "danger" line of
         1.0 while being trivially solvent. The second panel explains Delta's
         0.40: 43.6% of its current liabilities is DEFERRED REVENUE, settled
         by flying aeroplanes rather than by paying cash.
  fig4 — THE WALL IS IN THE NOTES. Oracle FY2026. The face of the balance
         sheet reports ONE number for non-current liabilities (176,939). The
         debt note reports the year-by-year repayment schedule, and 90,250 of
         130,105 falls beyond year five.
  fig5 — THE CASH CONVERSION CYCLE. Days sales outstanding plus days inventory
         outstanding minus days payable outstanding, for six companies.
         Apple -71 days and Microsoft -52 are financed by their suppliers;
         Pfizer +192 and NVIDIA +133 finance their customers.
"""
import os

import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt
import numpy as np

OUT = os.path.dirname(os.path.abspath(__file__))
BASE = "03-the-balance-sheet"

plt.rcParams.update({
    "font.size": 12, "axes.titlesize": 13, "axes.labelsize": 12,
    "svg.fonttype": "none", "figure.dpi": 100, "text.parse_math": False,
})

C1 = "#1f77b4"; C2 = "#d62728"; C3 = "#2ca02c"; C4 = "#ff7f0e"; C5 = "#9467bd"
C6 = "#8c564b"; GREY = "#555555"


def save(fig, n):
    path = os.path.join(OUT, f"{BASE}-fig{n}.svg")
    fig.savefig(path, format="svg", bbox_inches="tight")
    plt.close(fig)
    print("wrote", path)


# ------------------------------------------------------------------- fig 1
# Each company's most recent 10-K balance sheet, USD millions.
#   cash = cash and equivalents + short-term investments / marketable securities
#   ppe  = property, plant and equipment NET + operating lease right-of-use
#   gwi  = goodwill + identifiable intangibles
#   other is the residual, so each column sums to total assets by construction.
COMPOSITION = [
    # name, as-at, total assets, cash, receivables, inventory, ppe, goodwill+int
    ("Costco\n30 Aug 2026",   89_045,  21_301,  3_959, 19_324,  38_330,     994),
    ("Delta Air Lines\n31 Dec 2025", 81_317, 4_310, 2_850, 1_601, 45_987, 15_719),
    ("Microsoft\n30 Jun 2026", 758_376, 76_843, 80_876, 1_397, 337_253, 138_260),
    ("NVIDIA\n25 Jan 2026",   206_803,  62_556, 38_466, 21_403, 13_250,  24_138),
    ("Pfizer\n31 Dec 2025",   208_160,  13_596, 11_874, 10_654, 21_530, 124_995),
]
COMP_LABELS = ["Cash and investments", "Receivables", "Inventory",
               "Property and leases", "Goodwill and intangibles", "Everything else"]
COMP_COLS = [C3, C1, C4, C2, C5, "#bbbbbb"]


def fig1():
    fig, ax = plt.subplots(figsize=(12.6, 6.4))
    names = [c[0] for c in COMPOSITION]
    x = np.arange(len(names))
    shares = []
    for _, tot, cash, rec, inv, ppe, gwi in COMPOSITION:
        other = tot - cash - rec - inv - ppe - gwi
        assert other > 0
        shares.append([100 * v / tot for v in (cash, rec, inv, ppe, gwi, other)])
    shares = np.array(shares)
    assert np.allclose(shares.sum(axis=1), 100.0)

    bottom = np.zeros(len(names))
    for j, (lab, col) in enumerate(zip(COMP_LABELS, COMP_COLS)):
        ax.bar(x, shares[:, j], width=0.62, bottom=bottom, color=col, label=lab)
        for i, v in enumerate(shares[:, j]):
            if v >= 4.2:
                ax.text(x[i], bottom[i] + v / 2, f"{v:.1f}", ha="center",
                        va="center", fontsize=10.6, color="white",
                        fontweight="bold")
        bottom += shares[:, j]

    ax.set_xticks(x); ax.set_xticklabels(names, fontsize=10.8)
    ax.set_ylim(0, 100); ax.set_ylabel("Per cent of total assets")
    ax.set_title("The same word, five different things: what each company's "
                 "assets actually ARE", fontsize=13.2, fontweight="bold")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.11), ncol=3,
              fontsize=10.6, frameon=False)
    ax.grid(axis="y", alpha=0.25)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    save(fig, 1)
    ms = shares[2][3]; cs = shares[0][3]
    assert ms > cs, "the teaching case is that Microsoft is MORE capital-heavy"
    print(f"  (property share: Delta {shares[1][3]:.1f}%, Microsoft {ms:.1f}%, "
          f"Costco {cs:.1f}%, NVIDIA {shares[3][3]:.1f}%; "
          f"Pfizer goodwill+intangibles {shares[4][4]:.1f}%)")


# ------------------------------------------------------------------- fig 2
# name, goodwill, identifiable intangibles, total assets, TOTAL book equity
GOODWILL = [
    ("Costco",      994,      0,  89_045,  35_803),
    ("NVIDIA",   20_832,  3_306, 206_803, 157_293),
    ("Oracle",   62_261,  3_229, 261_759,  43_056),
    ("Salesforce", 57_941, 6_815, 112_305,  59_142),
    ("Pfizer",   71_264, 53_731, 208_160,  86_476),
    ("Kraft Heinz", 22_179, 37_529, 81_786, 41_664),
    ("Broadcom", 97_801, 32_273, 171_092,  81_292),
]


def fig2():
    fig, ax = plt.subplots(figsize=(12.6, 6.2))
    rows = sorted(GOODWILL, key=lambda r: (r[1] + r[2]) / r[4])
    names = [r[0] for r in rows]
    of_assets = [100 * (r[1] + r[2]) / r[3] for r in rows]
    of_equity = [100 * (r[1] + r[2]) / r[4] for r in rows]
    x = np.arange(len(names)); w = 0.38

    ax.bar(x - w / 2, of_assets, width=w, color=C1,
           label="as a share of TOTAL ASSETS")
    ax.bar(x + w / 2, of_equity, width=w, color=C2,
           label="as a share of BOOK EQUITY")
    for i, (a, e) in enumerate(zip(of_assets, of_equity)):
        ax.text(x[i] - w / 2, a + 3, f"{a:.0f}%", ha="center", fontsize=10.4,
                color=C1, fontweight="bold")
        ax.text(x[i] + w / 2, e + 3, f"{e:.0f}%", ha="center", fontsize=10.4,
                color=C2, fontweight="bold")
    ax.axhline(100, color=GREY, lw=1.5, ls="--")
    ax.text(-0.46, 103, "100% of book equity", fontsize=10.6, color=GREY,
            va="bottom")

    ax.set_xticks(x); ax.set_xticklabels(names, fontsize=11.0)
    ax.set_ylim(0, 186)
    ax.set_ylabel("Goodwill + identifiable intangibles, per cent")
    ax.set_title("The line that is an opinion: how much of the balance sheet, "
                 "and how much of the equity", fontsize=13.0, fontweight="bold")
    ax.legend(loc="upper left", fontsize=10.8, frameon=False)
    ax.grid(axis="y", alpha=0.25)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    save(fig, 2)
    over = [n for n, e in zip(names, of_equity) if e > 100]
    assert len(over) == 5, over
    print(f"  (goodwill+intangibles EXCEED book equity at {len(over)} of "
          f"{len(names)}: {', '.join(over)})")


# ------------------------------------------------------------------- fig 3
CURRENT = [("Delta Air Lines", 10_968, 27_624), ("Salesforce", 28_222, 37_118),
           ("Apple", 147_957, 165_631), ("Costco", 46_582, 43_952),
           ("Pfizer", 42_898, 36_984), ("Microsoft", 207_710, 168_825),
           ("NVIDIA", 125_605, 32_163)]
# Delta's current liabilities, 31 Dec 2025, from the face of the balance sheet
DELTA_CL = [("Air traffic liability\n(tickets already sold)", 7_157),
            ("Loyalty programme\ndeferred revenue", 4_876),
            ("Accounts payable", 5_226),
            ("Accrued salaries\nand benefits", 4_906),
            ("Debt and lease\nmaturities", 2_414),
            ("Fuel card obligation\nand other accruals", 3_045)]


def fig3():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15.4, 6.2),
                                   gridspec_kw=dict(width_ratios=[1.0, 1.0]))
    rows = sorted(CURRENT, key=lambda r: r[1] / r[2])
    names = [r[0] for r in rows]
    ratios = [r[1] / r[2] for r in rows]
    y = np.arange(len(names))[::-1]
    cols = [C2 if r < 1 else C3 for r in ratios]
    ax1.barh(y, ratios, height=0.58, color=cols)
    for yy, r in zip(y, ratios):
        ax1.text(r + 0.07, yy, f"{r:.2f}", va="center", fontsize=11.4,
                 fontweight="bold", color=C2 if r < 1 else C3)
    ax1.axvline(1.0, color=GREY, lw=1.6, ls="--")
    ax1.text(1.06, -0.62, "1.0", fontsize=10.4, color=GREY)
    ax1.axvline(2.0, color=GREY, lw=1.1, ls=":")
    ax1.text(2.06, -0.62, "2.0 — the textbook rule", fontsize=10.4, color=GREY)
    ax1.set_yticks(y); ax1.set_yticklabels(names, fontsize=11.0)
    ax1.set_xlim(0, 4.5)
    ax1.set_xlabel("Current assets ÷ current liabilities")
    nbelow = sum(1 for r in ratios if r < 1)
    assert nbelow == 3, nbelow          # the title's wording depends on this
    ax1.set_title(f"{nbelow} of these are below the “danger” line of 1.0.\n"
                  "All three are solvent.", fontsize=12.4, fontweight="bold")
    ax1.grid(axis="x", alpha=0.25)
    ax1.spines[["top", "right"]].set_visible(False)

    labels = [d[0] for d in DELTA_CL]
    vals = [d[1] for d in DELTA_CL]
    assert sum(vals) == 27_624
    y2 = np.arange(len(labels))[::-1]
    cols2 = [C4, C4] + [C1] * 4
    ax2.barh(y2, [v / 1000 for v in vals], height=0.58, color=cols2)
    for yy, v in zip(y2, vals):
        ax2.text(v / 1000 + 0.12, yy, f"{v / 1000:.1f}", va="center",
                 fontsize=11.0, fontweight="bold", color=GREY)
    ax2.set_yticks(y2); ax2.set_yticklabels(labels, fontsize=10.2)
    ax2.set_xlim(0, 9.6)
    ax2.set_xlabel("USD billions")
    defrev = 100 * (7_157 + 4_876) / 27_624
    ax2.set_title(f"Why Delta lives at 0.40: {defrev:.0f}% of its current\n"
                  "liabilities is settled by FLYING, not by paying",
                  fontsize=12.4, fontweight="bold")
    ax2.grid(axis="x", alpha=0.25)
    ax2.spines[["top", "right"]].set_visible(False)

    fig.tight_layout()
    save(fig, 3)
    print(f"  (current ratios {min(ratios):.2f}-{max(ratios):.2f}; "
          f"Delta deferred revenue {defrev:.1f}% of current liabilities)")


# ------------------------------------------------------------------- fig 4
# Oracle, FY2026 (year ended 31 May 2026), Form 10-K.
ORCL_FACE = [("Current\nliabilities", 41_764), ("Non-current\nliabilities", 176_939),
             ("Total equity\n(incl. NCI)", 43_056)]
ORCL_NOTE = [("Year 1\n(FY2027)", 7_210), ("Year 2", 10_145), ("Year 3", 5_500),
             ("Year 4", 7_250), ("Year 5", 9_750), ("Beyond\nyear 5", 90_250)]


def fig4():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15.0, 6.0),
                                   gridspec_kw=dict(width_ratios=[0.62, 1.38]))
    assert sum(v for _, v in ORCL_FACE) == 261_759        # = total assets

    n1 = [a for a, _ in ORCL_FACE]
    v1 = [v / 1000 for _, v in ORCL_FACE]
    ax1.bar(np.arange(3), v1, width=0.56, color=[C4, C2, C3])
    for i, v in enumerate(v1):
        ax1.text(i, v + 4, f"{v:.1f}", ha="center", fontsize=11.6,
                 fontweight="bold", color=[C4, C2, C3][i])
    ax1.set_xticks(np.arange(3)); ax1.set_xticklabels(n1, fontsize=10.6)
    ax1.set_ylim(0, 215)
    ax1.set_ylabel("USD billions")
    ax1.set_title("What the FACE says\nthree numbers, and one means “later”",
                  fontsize=12.2, fontweight="bold")
    ax1.grid(axis="y", alpha=0.25)
    ax1.spines[["top", "right"]].set_visible(False)

    n2 = [a for a, _ in ORCL_NOTE]
    v2 = [v / 1000 for _, v in ORCL_NOTE]
    cols = [C1] * 5 + [C2]
    ax2.bar(np.arange(len(n2)), v2, width=0.6, color=cols)
    for i, v in enumerate(v2):
        ax2.text(i, v + 1.6, f"{v:.1f}", ha="center", fontsize=11.4,
                 fontweight="bold", color=cols[i])
    ax2.set_xticks(np.arange(len(n2))); ax2.set_xticklabels(n2, fontsize=10.6)
    ax2.set_ylim(0, 103)
    ax2.set_ylabel("Principal repayable, USD billions")
    tot = sum(v for _, v in ORCL_NOTE)
    beyond = 100 * ORCL_NOTE[-1][1] / tot
    ax2.set_title(f"What the NOTE says\n{tot / 1000:.1f}bn of debt, and "
                  f"{beyond:.0f}% of it beyond year five",
                  fontsize=12.2, fontweight="bold")
    ax2.grid(axis="y", alpha=0.25)
    ax2.spines[["top", "right"]].set_visible(False)

    fig.suptitle("Oracle FY2026: the maturity profile is the risk, and it is "
                 "not on the balance sheet", fontsize=13.4, fontweight="bold",
                 y=0.995)
    fig.tight_layout(rect=(0, 0, 1, 0.955))
    save(fig, 4)
    assert tot > 3 * 43_056, "debt is more than 3x book equity"
    print(f"  (debt {tot:,} vs book equity 43,056 = {tot / 43_056:.1f}x; "
          f"{beyond:.1f}% falls beyond year five)")


# ------------------------------------------------------------------- fig 5
# name, revenue, cost of sales, receivables, inventory, payables (same 10-K)
CCC = [("Apple",     416_161, 220_960, 39_777,  5_718, 69_860),
       ("Microsoft", 331_839, 106_374, 80_876,  1_397, 42_416),
       ("Costco",    303_154, 264_279,  3_959, 19_324, 22_591),
       ("NVIDIA",    215_938,  62_475, 38_466, 21_403,  9_812),
       ("Pfizer",     62_579,  16_067, 11_874, 10_654,  5_240)]


def fig5():
    fig, ax = plt.subplots(figsize=(13.0, 6.3))
    rows = []
    for name, rev, cogs, ar, inv, ap in CCC:
        dso = 365 * ar / rev; dio = 365 * inv / cogs; dpo = 365 * ap / cogs
        rows.append((name, dso, dio, dpo, dso + dio - dpo))
    rows.sort(key=lambda r: r[4])
    names = [r[0] for r in rows]
    x = np.arange(len(names)); w = 0.26

    ax.bar(x - w, [r[1] for r in rows], width=w, color=C1,
           label="Days sales outstanding (customers owe you)")
    ax.bar(x, [r[2] for r in rows], width=w, color=C4,
           label="Days inventory outstanding (stock sitting there)")
    ax.bar(x + w, [-r[3] for r in rows], width=w, color=C3,
           label="Days payable outstanding (you owe suppliers)")
    for i, r in enumerate(rows):
        col = C3 if r[4] < 0 else C2
        ax.annotate(f"{r[4]:+.0f}", xy=(x[i], 272), ha="center", fontsize=13.0,
                    fontweight="bold", color=col)
    ax.axhline(0, color="black", lw=1.0)
    ax.set_xticks(x); ax.set_xticklabels(names, fontsize=11.4)
    ax.set_ylim(-170, 302)
    ax.set_ylabel("Days")
    ax.set_title("Who is financing whom: the cash conversion cycle\n"
                 "(the bold figure above each company is its cycle, in days)",
                 fontsize=13.0, fontweight="bold")
    ax.legend(loc="lower left", fontsize=10.4, frameon=False)
    ax.grid(axis="y", alpha=0.25)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    save(fig, 5)
    neg = [r[0] for r in rows if r[4] < 0]
    assert "Apple" in neg and "Microsoft" in neg
    print("  (" + "; ".join(f"{r[0]} {r[4]:+.0f}d" for r in rows) + ")")


if __name__ == "__main__":
    fig1(); fig2(); fig3(); fig4(); fig5()
    print("done")
