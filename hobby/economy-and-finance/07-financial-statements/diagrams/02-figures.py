#!/usr/bin/env python3
"""Figures for Econ E07 §2 — the income statement.

Editable source of truth for the committed SVGs (see agent-docs/diagrams.md).
Every panel is COMPUTED rather than drawn by hand. Figures 1, 2 and 3 use
figures as filed; figure 4 is exact arithmetic on the two presentations of one
set of economics.

All filed values come from the SEC XBRL companyconcept API, 10-K facts only,
with periods filtered to a duration between 330 and 400 days — WITHOUT that
filter the series silently mixes fourth-quarter facts into annual ones, which
is the trap recorded in E07 §1 §10b.

  fig1 — THE SAME ECONOMICS, TWO LEGAL REVENUE FIGURES. A marketplace that
         collects 100 from a customer, pays 85 to a merchant and keeps 15.
         As PRINCIPAL it reports revenue of 100 and cost of 85; as AGENT it
         reports revenue of 15 and no cost of sales. Gross profit, operating
         profit and net income are IDENTICAL in both columns, and the
         reported "revenue" differs by 6.7x. Exact arithmetic, not a data
         series; the real instance cited in the text is Groupon's 2011
         restatement from gross to net.
  fig2 — WHERE A DOLLAR OF REVENUE ACTUALLY GOES. Apple's FY2025 income
         statement as a waterfall, from revenue of USD 416,161m down to net
         income of 112,010m. The point is that the statement is a LADDER OF
         SUBTOTALS, each one answering a different question, and that the
         largest single deduction is the cost of making the thing.
  fig3 — GROSS MARGIN TELLS YOU LESS THAN YOU THINK. The three margins for
         six companies, ordered by gross margin: Costco 12.8% gross through
         to Palantir 82.4%. The teaching pair is Salesforce and NVIDIA —
         near-identical GROSS margins of 77.7% and 71.1%, and operating
         margins of 20.1% versus 60.4%. What separates them is entirely
         below the gross line. The second teaching case is Palantir, whose
         NET margin EXCEEDS its operating margin, because interest income
         and a 1.4% effective tax rate both arrive below the operating line.
  fig4 — THE ADD-BACK THAT DECIDES WHETHER A COMPANY IS PROFITABLE. Share-
         based compensation as a share of net income, for the same six.
         NVIDIA 5.3%, Microsoft 9.3%, Apple 11.5% — and Palantir 42.1%,
         Salesforce 47.1%. Adding SBC back, as every "adjusted" measure
         does, raises Salesforce's profit by almost half.
"""
import os
import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt
import numpy as np

OUT = os.path.dirname(os.path.abspath(__file__))
BASE = "02-the-income-statement"

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
# Apple FY2025 (year ended 27 September 2025), Form 10-K. USD millions.
AAPL = dict(revenue=416_161, cogs=220_960, gross=195_201, rnd=34_550,
            sgna=27_601, operating=133_050, tax=20_719, net=112_010)
AAPL["other"] = AAPL["net"] + AAPL["tax"] - AAPL["operating"]   # non-operating, net


def fig2():
    steps = [
        ("Revenue", AAPL["revenue"], "total"),
        ("Cost of sales", -AAPL["cogs"], "down"),
        ("Gross profit", AAPL["gross"], "total"),
        ("Research and\ndevelopment", -AAPL["rnd"], "down"),
        ("Selling, general\nand admin", -AAPL["sgna"], "down"),
        ("Operating income", AAPL["operating"], "total"),
        ("Non-operating,\nnet", AAPL["other"], "down"),
        ("Income tax", -AAPL["tax"], "down"),
        ("Net income", AAPL["net"], "total"),
    ]
    fig, ax = plt.subplots(figsize=(13.6, 6.2))
    running = 0.0
    for i, (label, val, kind) in enumerate(steps):
        if kind == "total":
            ax.bar(i, val / 1000, width=0.58, color=GREY)
            ax.text(i, val / 1000 + 8, f"{val / 1000:,.1f}", ha="center",
                    fontsize=11.4, fontweight="bold")
            ax.text(i, val / 1000 / 2, f"{val / AAPL['revenue'] * 100:.0f}%",
                    ha="center", va="center", color="white", fontsize=12,
                    fontweight="bold")
            running = val
        else:
            col = C3 if val > 0 else C2
            bottom = running if val > 0 else running + val
            ax.bar(i, abs(val) / 1000, width=0.58, bottom=bottom / 1000, color=col)
            ax.text(i, (bottom + abs(val)) / 1000 + 8, f"{val / 1000:+,.1f}",
                    ha="center", fontsize=10.8, color=col)
            running += val
    assert abs(running - AAPL["net"]) < 1e-6

    ax.set_xticks(range(len(steps)))
    ax.set_xticklabels([s[0] for s in steps], fontsize=9.8)
    ax.set_ylabel("USD billion")
    ax.set_ylim(0, 500)
    ax.set_title("Apple FY2025: the income statement is a ladder of subtotals, "
                 "not a single number", fontsize=13.0, fontweight="bold")
    ax.grid(axis="y", alpha=0.25)
    ax.spines[["top", "right"]].set_visible(False)
    ax.text(1.0, 496, "the largest single deduction is\nthe cost of making the thing",
            fontsize=10.4, color=GREY, ha="center", va="top")
    ax.text(6.5, 300, "everything from here down is\nFINANCING and the TAX CODE,\n"
                      "not the business",
            fontsize=10.4, color=GREY, ha="center", va="top")
    fig.tight_layout()
    save(fig, 2)
    print(f"  (gross {AAPL['gross'] / AAPL['revenue'] * 100:.1f}%, "
          f"operating {AAPL['operating'] / AAPL['revenue'] * 100:.1f}%, "
          f"net {AAPL['net'] / AAPL['revenue'] * 100:.1f}%; "
          f"non-operating {AAPL['other']:+,})")


# ------------------------------------------------------------------- fig 2 & 3
# (name, fiscal year label, revenue, gross profit, operating income,
#  net income, share-based compensation) — USD millions, as filed.
FIRMS = [
    ("Costco",     "FY2026", 303_154, 303_154 - 264_279,  11_685,   9_226,    924),
    ("Apple",      "FY2025", 416_161, 195_201,           133_050, 112_010, 12_863),
    ("Microsoft",  "FY2026", 331_839, 225_465,           155_237, 133_749, 12_405),
    ("NVIDIA",     "FY2026", 215_938, 153_463,           130_387, 120_067,  6_386),
    ("Salesforce", "FY2026",  41_525,  32_255,             8_331,   7_457,  3_509),
    ("Palantir",   "FY2025",   4_475,   3_686,             1_414,   1_625,    684),
]


def fig3():
    order = sorted(FIRMS, key=lambda f: f[3] / f[2])
    names = [f"{f[0]}\n{f[1]}" for f in order]
    gm = [f[3] / f[2] * 100 for f in order]
    om = [f[4] / f[2] * 100 for f in order]
    nm = [f[5] / f[2] * 100 for f in order]

    fig, ax = plt.subplots(figsize=(13.4, 6.2))
    x = np.arange(len(order)); w = 0.26
    ax.bar(x - w, gm, width=w, color=C1, label="Gross margin")
    ax.bar(x,     om, width=w, color=C4, label="Operating margin")
    ax.bar(x + w, nm, width=w, color=C3, label="Net margin")
    for i in range(len(order)):
        for off, v in ((-w, gm[i]), (0, om[i]), (w, nm[i])):
            ax.text(i + off, v + 1.3, f"{v:.1f}", ha="center", fontsize=9.8)
    ax.set_xticks(x); ax.set_xticklabels(names, fontsize=10.6)
    ax.set_ylabel("Per cent of revenue")
    ax.set_ylim(0, 103)
    ax.set_title("Three margins, six companies — and gross margin alone tells you "
                 "very little", fontsize=13.0, fontweight="bold")
    ax.legend(fontsize=10.6, loc="upper left")
    ax.grid(axis="y", alpha=0.25)
    ax.spines[["top", "right"]].set_visible(False)

    i_crm = [f[0] for f in order].index("Salesforce")
    i_nvda = [f[0] for f in order].index("NVIDIA")
    ax.annotate("", xy=(i_crm, om[i_crm] + 0.6), xytext=(i_nvda, om[i_nvda] - 0.6),
                arrowprops=dict(arrowstyle="<->", color=GREY, lw=1.6))
    # the two notes live in the only empty bands: under the legend, and top right
    ax.text(-0.42, 84.0,
            "NVIDIA vs SALESFORCE (arrow):\n"
            "near-identical GROSS margins, operating\n"
            "margins 40 points apart — the whole\n"
            "difference is BELOW the gross line",
            fontsize=10.3, color=GREY, ha="left", va="top")
    ax.text(5.46, 100.0,
            "PALANTIR: net margin EXCEEDS operating margin —\n"
            "interest income on its cash, and a 1.4% effective\n"
            "tax rate, both land below the operating line",
            fontsize=10.3, color=GREY, ha="right", va="top")
    fig.tight_layout()
    save(fig, 3)
    print("  (" + "; ".join(f"{f[0]} {f[3] / f[2] * 100:.1f}/{f[4] / f[2] * 100:.1f}/"
                            f"{f[5] / f[2] * 100:.1f}" for f in order) + ")")


def fig4():
    order = sorted(FIRMS, key=lambda f: f[6] / f[5])
    names = [f"{f[0]}\n{f[1]}" for f in order]
    share = [f[6] / f[5] * 100 for f in order]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.4, 5.8),
                                   gridspec_kw={"width_ratios": [1, 1.05]})

    cols = [C2 if v > 30 else C1 for v in share]
    ax1.bar(np.arange(len(order)), share, width=0.56, color=cols)
    for i, v in enumerate(share):
        ax1.text(i, v + 1.1, f"{v:.1f}%", ha="center", fontsize=11)
    ax1.set_xticks(np.arange(len(order))); ax1.set_xticklabels(names, fontsize=10)
    ax1.set_ylabel("Share-based compensation, % of net income")
    ax1.set_ylim(0, 58)
    ax1.set_title("How big is the add-back?", fontsize=12.6, fontweight="bold")
    ax1.grid(axis="y", alpha=0.25)
    ax1.spines[["top", "right"]].set_visible(False)

    x = np.arange(len(order)); w = 0.38
    rep = [f[5] / 1000 for f in order]
    adj = [(f[5] + f[6]) / 1000 for f in order]
    ax2.bar(x - w / 2, rep, width=w, color=C1, label="Net income, as reported")
    ax2.bar(x + w / 2, adj, width=w, color=C4, label="With SBC added back")
    for i in range(len(order)):
        ax2.text(i + w / 2, adj[i] + 2.6,
                 f"+{(adj[i] / rep[i] - 1) * 100:.0f}%", ha="center",
                 fontsize=10.2, color=C4)
    ax2.set_xticks(x); ax2.set_xticklabels(names, fontsize=10)
    ax2.set_ylabel("USD billion")
    ax2.set_ylim(0, 168)
    ax2.set_title("What the add-back does to the number", fontsize=12.6,
                  fontweight="bold")
    ax2.legend(fontsize=10.2, loc="upper left")
    ax2.grid(axis="y", alpha=0.25)
    ax2.spines[["top", "right"]].set_visible(False)

    fig.tight_layout()
    save(fig, 4)
    print("  (" + "; ".join(f"{f[0]} {f[6] / f[5] * 100:.1f}%" for f in order) + ")")


# ------------------------------------------------------------------- fig 4
# Exact arithmetic. One marketplace, one set of economics, two presentations.
MKT = dict(customer_pays=100.0, merchant_gets=85.0, opex=9.0, tax_rate=0.20)


def market_pnl(gross):
    """Return the P&L under principal (gross) or agent (net) presentation."""
    if gross:
        rev, cos = MKT["customer_pays"], MKT["merchant_gets"]
    else:
        rev, cos = MKT["customer_pays"] - MKT["merchant_gets"], 0.0
    gp = rev - cos
    op = gp - MKT["opex"]
    tax = op * MKT["tax_rate"]
    return dict(revenue=rev, cos=cos, gross=gp, opex=MKT["opex"],
                operating=op, tax=tax, net=op - tax)


def fig1():
    g, n = market_pnl(True), market_pnl(False)
    rows = [("Revenue", "revenue"), ("Cost of sales", "cos"),
            ("Gross profit", "gross"), ("Operating costs", "opex"),
            ("Operating profit", "operating"), ("Tax", "tax"),
            ("Net income", "net")]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.4, 5.8),
                                   gridspec_kw={"width_ratios": [1.15, 1]})
    y = np.arange(len(rows))[::-1]
    w = 0.36
    ax1.barh(y + w / 2, [g[k] for _, k in rows], height=w, color=C2,
             label="As PRINCIPAL (gross)")
    ax1.barh(y - w / 2, [n[k] for _, k in rows], height=w, color=C1,
             label="As AGENT (net)")
    for i, (_, k) in enumerate(rows):
        ax1.text(g[k] + 1.6, y[i] + w / 2, f"{g[k]:,.1f}", va="center", fontsize=10.4)
        ax1.text(n[k] + 1.6, y[i] - w / 2, f"{n[k]:,.1f}", va="center", fontsize=10.4)
    ax1.set_yticks(y); ax1.set_yticklabels([r[0] for r in rows], fontsize=11)
    ax1.set_xlim(0, 124)
    ax1.set_xlabel("Currency units")
    ax1.set_title("One marketplace, one set of economics, two legal presentations",
                  fontsize=12.4, fontweight="bold")
    ax1.legend(fontsize=10.4, loc="lower right")
    ax1.grid(axis="x", alpha=0.25)
    ax1.spines[["top", "right"]].set_visible(False)

    labels = ["Revenue", "Gross profit", "Operating\nprofit", "Net income"]
    keys = ["revenue", "gross", "operating", "net"]
    x = np.arange(len(keys)); w2 = 0.36
    ax2.bar(x - w2 / 2, [g[k] for k in keys], width=w2, color=C2)
    ax2.bar(x + w2 / 2, [n[k] for k in keys], width=w2, color=C1)
    for i, k in enumerate(keys):
        same = abs(g[k] - n[k]) < 1e-9
        ax2.text(i, max(g[k], n[k]) + 3.2,
                 "IDENTICAL" if same else f"{g[k] / n[k]:.1f}x apart",
                 ha="center", fontsize=10.4,
                 color=C3 if same else C2, fontweight="bold")
    ax2.set_xticks(x); ax2.set_xticklabels(labels, fontsize=10.6)
    ax2.set_ylim(0, 124)
    ax2.set_ylabel("Currency units")
    ax2.set_title("Only the top line moves", fontsize=12.4, fontweight="bold")
    ax2.grid(axis="y", alpha=0.25)
    ax2.spines[["top", "right"]].set_visible(False)

    fig.tight_layout()
    save(fig, 1)
    for k in ("gross", "operating", "net"):
        assert abs(g[k] - n[k]) < 1e-9, k      # everything below revenue is equal
    print(f"  (revenue {g['revenue']:.0f} vs {n['revenue']:.0f} = "
          f"{g['revenue'] / n['revenue']:.1f}x; gross profit, operating profit and "
          f"net income identical at {g['gross']:.0f} / {g['operating']:.0f} / "
          f"{g['net']:.1f})")


# ------------------------------------------------------------------- fig 6
# Apple FY2025 (year ended 27 September 2025), Form 10-K, accession
# 0000320193-25-000079. Three different resolutions in one filing.
#
#   revenue   -> five PRODUCT categories   (Note: Revenue, disaggregation,
#                required by ASC 280-10-50-40 / IFRS 8.32)
#   margin    -> two product groupings     (Item 7 MD&A, UNAUDITED commentary)
#   profit    -> five GEOGRAPHIC segments  (Note: Segment Information, the
#                management approach -- these are the units the CODM reviews)
#
# The point of the figure is that the product axis and the profit axis never
# intersect: no filing anywhere states an operating profit for iPhone.
AAPL_PRODUCTS = [("iPhone", 209_586), ("Services", 109_158),
                 ("Wearables, Home\nand Accessories", 35_686),
                 ("Mac", 33_708), ("iPad", 28_023)]
AAPL_GM = [("Products", 112_887, 307_003), ("Services", 82_314, 109_158)]
# segment: (name, net sales, cost of sales, selling & marketing, operating income)
AAPL_SEG = [("Americas", 178_353, 95_699, 10_174, 72_480),
            ("Europe", 111_032, 58_617, 4_676, 47_739),
            ("Greater China", 64_377, 35_141, 2_319, 26_917),
            ("Rest of Asia\nPacific", 33_696, 17_724, 1_386, 14_586),
            ("Japan", 28_703, 13_779, 969, 13_955)]
AAPL_CORP = 42_627          # R&D 34,550 + G&A 8,077, attributed to NO segment


def fig6():
    fig, (ax1, ax2, ax3) = plt.subplots(
        1, 3, figsize=(16.4, 6.0), gridspec_kw=dict(width_ratios=[1.15, 0.75, 1.15]))

    # --- panel 1: revenue, five product categories ------------------------
    names = [n for n, _ in AAPL_PRODUCTS]
    vals = [v / 1000 for _, v in AAPL_PRODUCTS]
    y = np.arange(len(names))[::-1]
    ax1.barh(y, vals, height=0.6, color=C1)
    for yy, v in zip(y, vals):
        ax1.text(v + 4, yy, f"{v:,.1f}", va="center", fontsize=11.2, color=C1,
                 fontweight="bold")
    ax1.set_yticks(y); ax1.set_yticklabels(names, fontsize=10.8)
    ax1.set_xlim(0, 248)
    ax1.set_xlabel("USD billions")
    ax1.set_title("REVENUE — five product categories\n(required, audited note)",
                  fontsize=12.0, fontweight="bold")
    ax1.grid(axis="x", alpha=0.25)
    ax1.spines[["top", "right"]].set_visible(False)

    # --- panel 2: gross margin, two groupings -----------------------------
    gnames = [n for n, _, _ in AAPL_GM]
    gpct = [100 * g / s for _, g, s in AAPL_GM]
    ax2.bar(np.arange(2), gpct, width=0.5, color=[C4, C3])
    for i, p in enumerate(gpct):
        ax2.text(i, p + 1.6, f"{p:.1f}%", ha="center", fontsize=12.4,
                 fontweight="bold", color=[C4, C3][i])
    ax2.axhline(100 * 195_201 / 416_161, color=GREY, lw=1.4, ls="--")
    ax2.text(-0.42, 100 * 195_201 / 416_161 + 1.4, "blended 46.9%", ha="left",
             va="bottom", fontsize=10.2, color=GREY)
    ax2.set_xticks(np.arange(2)); ax2.set_xticklabels(gnames, fontsize=11.2)
    ax2.set_ylim(0, 92)
    ax2.set_ylabel("Gross margin, per cent of that grouping's sales")
    ax2.set_title("MARGIN — two groupings only\n(MD&A commentary, UNAUDITED)",
                  fontsize=12.0, fontweight="bold")
    ax2.grid(axis="y", alpha=0.25)
    ax2.spines[["top", "right"]].set_visible(False)

    # --- panel 3: operating income, five geographic segments --------------
    snames = [s[0] for s in AAPL_SEG] + ["Corporate\n(R&D + G&A)"]
    sop = [s[4] / 1000 for s in AAPL_SEG] + [-AAPL_CORP / 1000]
    y3 = np.arange(len(snames))[::-1]
    cols = [C2] * len(AAPL_SEG) + [GREY]
    ax3.barh(y3, sop, height=0.6, color=cols)
    for yy, v in zip(y3, sop):
        ax3.text(v + (3 if v > 0 else -3), yy, f"{v:,.1f}", va="center",
                 ha="left" if v > 0 else "right", fontsize=11.2,
                 fontweight="bold", color=C2 if v > 0 else GREY)
    ax3.axvline(0, color="black", lw=1.0)
    ax3.set_yticks(y3); ax3.set_yticklabels(snames, fontsize=10.8)
    ax3.set_xlim(-62, 96)
    ax3.set_xlabel("Operating income, USD billions")
    ax3.set_title("PROFIT — five segments, but by GEOGRAPHY\n"
                  "(required, audited note)", fontsize=12.0, fontweight="bold")
    ax3.grid(axis="x", alpha=0.25)
    ax3.spines[["top", "right"]].set_visible(False)

    fig.suptitle("Apple FY2025: revenue splits one way, profit splits another, "
                 "and the two axes never meet",
                 fontsize=13.4, fontweight="bold", y=0.995)
    fig.tight_layout(rect=(0, 0, 1, 0.965))
    save(fig, 6)

    # --- self-checks against the filing -----------------------------------
    assert sum(v for _, v in AAPL_PRODUCTS) == 416_161
    assert sum(s[1] for s in AAPL_SEG) == 416_161
    assert sum(g for _, g, _ in AAPL_GM) == 195_201
    assert AAPL_GM[0][2] + AAPL_GM[1][2] == 416_161          # products + services
    assert sum(s[4] for s in AAPL_SEG) - AAPL_CORP == 133_050
    for _, sales, cogs, sm, op in AAPL_SEG:
        assert sales - cogs - sm == op                        # segment profit is
    serv_rev = 109_158 / 416_161                              # gross profit - S&M
    serv_gp = 82_314 / 195_201
    print(f"  (Services is {100 * serv_rev:.1f}% of revenue but "
          f"{100 * serv_gp:.1f}% of gross profit; "
          f"segment gross margins range "
          f"{min(100 * (s[1] - s[2]) / s[1] for s in AAPL_SEG):.1f}%-"
          f"{max(100 * (s[1] - s[2]) / s[1] for s in AAPL_SEG):.1f}%; "
          f"ALL {AAPL_CORP:,} of R&D and G&A sits outside every segment)")


if __name__ == "__main__":
    fig1(); fig2(); fig3(); fig4(); fig6()
    print("done")
