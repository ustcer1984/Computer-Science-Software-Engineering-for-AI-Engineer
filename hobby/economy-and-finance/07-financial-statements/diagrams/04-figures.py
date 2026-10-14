#!/usr/bin/env python3
"""Figures for Econ E07 §4 — the cash flow statement.

Editable source of truth for the committed SVGs (see agent-docs/diagrams.md).
Every panel is COMPUTED from filed figures, and the identities the text asserts
are asserted here too, so prose and picture cannot drift apart.

Sources: each company's most recent Form 10-K, read off the filing's own
CONSOLIDATED STATEMENTS OF CASH FLOWS, with the multi-year series taken from
the SEC XBRL companyconcept API filtered to 10-K duration facts of 330-400
days (the trap recorded in E07 §1 §10b).

  fig1 — THREE NUMBERS, THREE DIFFERENT STORIES. Net income, operating cash
         flow and free cash flow for six companies, most recent full year.
         Two teaching cases: ORACLE, whose free cash flow is MINUS 23.7bn
         on net income of 17.1bn, and NVIDIA, whose OPERATING CASH FLOW IS
         BELOW NET INCOME despite a 55.6% net margin.
  fig2 — WHERE THE 17bn WENT. NVIDIA FY2026 reconciled from net income
         120,067 to operating cash flow 102,718. The non-cash adjustments
         net to roughly nothing; the whole of the gap is WORKING CAPITAL,
         and almost all of that is receivables and inventory -- which is
         E07 §3 §5.1's cash conversion cycle of +133 days, seen from the
         other side.
  fig3 — THE CAPEX LINE THAT ATE THE FREE CASH FLOW. Capital expenditure as
         a share of operating cash flow, Oracle and Microsoft, FY2020 to
         FY2026. Oracle crosses 100% in FY2025 and reaches 174% in FY2026;
         Microsoft goes from 25% to 63%. Nothing in either income statement
         shows this.
  fig4 — WHERE THE CASH ACTUALLY CAME FROM. Oracle FY2026 sources and uses.
         Operating cash flow of 31,977 against capital expenditure of
         55,663, and a dividend of 5,787 paid anyway -- funded by 46,093 of
         new senior notes and term loans. The filing says so on its face.
"""
import os

import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt
import numpy as np

OUT = os.path.dirname(os.path.abspath(__file__))
BASE = "04-the-cash-flow-statement"

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
# name, fiscal year label, net income, operating cash flow, capital expenditure
TRIPLE = [
    ("Oracle",     "FY2026",  17_087,  31_977,  55_663),
    ("Microsoft",  "FY2026", 133_749, 182_935, 115_948),
    ("NVIDIA",     "FY2026", 120_067, 102_718,   6_042),
    ("Apple",      "FY2025", 112_010, 111_482,  12_715),
    ("Costco",     "FY2026",   9_226,  15_817,   6_435),
    ("Salesforce", "FY2026",   7_457,  14_996,     594),
]


def fig1():
    fig, ax = plt.subplots(figsize=(13.4, 6.4))
    names = [f"{n}\n{fy}" for n, fy, *_ in TRIPLE]
    ni = [r[2] / 1000 for r in TRIPLE]
    ocf = [r[3] / 1000 for r in TRIPLE]
    fcf = [(r[3] - r[4]) / 1000 for r in TRIPLE]
    x = np.arange(len(names)); w = 0.26

    ax.bar(x - w, ni, width=w, color=C1, label="Net income")
    ax.bar(x, ocf, width=w, color=C3, label="Operating cash flow")
    ax.bar(x + w, fcf, width=w, color=C4, label="Free cash flow (operating − capital expenditure)")
    for i in range(len(names)):
        for off, v, col in ((-w, ni[i], C1), (0, ocf[i], C3), (w, fcf[i], C4)):
            ax.text(x[i] + off, v + (4 if v >= 0 else -4), f"{v:,.0f}",
                    ha="center", va="bottom" if v >= 0 else "top",
                    fontsize=9.8, fontweight="bold",
                    color=C2 if v < 0 else col)
    ax.axhline(0, color="black", lw=1.0)
    ax.annotate("free cash flow is NEGATIVE:\ncapex exceeded every dollar\nthe business generated",
                xy=(0 + w, fcf[0]), xytext=(0.52, -70),
                fontsize=10.2, color=C2, ha="left",
                arrowprops=dict(arrowstyle="->", color=C2, lw=1.5))
    ax.annotate("operating cash flow BELOW net income,\nat a 55.6% net margin (see Figure 2)",
                xy=(2, ocf[2]), xytext=(2.45, 148),
                fontsize=10.2, color=GREY, ha="left",
                arrowprops=dict(arrowstyle="->", color=GREY, lw=1.4))

    ax.set_xticks(x); ax.set_xticklabels(names, fontsize=10.8)
    ax.set_ylim(-95, 215)
    ax.set_ylabel("USD billions")
    ax.set_title("Three numbers for the same year, and they do not agree",
                 fontsize=13.2, fontweight="bold")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=3,
              fontsize=10.6, frameon=False)
    ax.grid(axis="y", alpha=0.25)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    save(fig, 1)
    assert fcf[0] < 0 and ocf[2] < ni[2]
    print("  (" + "; ".join(
        f"{r[0]} OCF/NI {r[3] / r[2]:.2f}, FCF/NI {(r[3] - r[4]) / r[2]:+.2f}"
        for r in TRIPLE) + ")")


# ------------------------------------------------------------------- fig 2
# NVIDIA FY2026 (year ended 25 January 2026), Form 10-K, as filed.
NVDA_BRIDGE = [
    ("Net income", 120_067, "start"),
    ("Stock-based\ncompensation", 6_386, "nc"),
    ("Depreciation\n& amortisation", 2_843, "nc"),
    ("Gains on\nsecurities", -8_918, "nc"),
    ("Deferred\nincome taxes", -1_424, "nc"),
    ("Other non-cash", -287, "nc"),
    ("Accounts\nreceivable", -15_399, "wc"),
    ("Inventories", -11_324, "wc"),
    ("Prepaid and\nother assets", 577, "wc"),
    ("Accounts\npayable", 3_096, "wc"),
    ("Accrued\nliabilities", 5_257, "wc"),
    ("Other long-term\nliabilities", 1_844, "wc"),
    ("Operating\ncash flow", 102_718, "end"),
]
COL = {"start": C1, "nc": C5, "wc": C4, "end": C3}


def fig2():
    fig, ax = plt.subplots(figsize=(14.6, 6.6))
    labels = [a for a, _, _ in NVDA_BRIDGE]
    x = np.arange(len(labels))
    run = 0.0
    for i, (lab, val, kind) in enumerate(NVDA_BRIDGE):
        v = val / 1000
        if kind in ("start", "end"):
            ax.bar(i, v, width=0.6, color=COL[kind])
            ax.text(i, v / 2, f"{v:,.1f}", ha="center", va="center",
                    color="white", fontsize=11.0, fontweight="bold")
            run = v
        else:
            ax.bar(i, abs(v), width=0.6, bottom=min(run, run + v),
                   color=COL[kind])
            ax.text(i, max(run, run + v) + 2.0, f"{v:+,.1f}", ha="center",
                    fontsize=9.8, fontweight="bold", color=COL[kind])
            run += v
    assert abs(run - 102.718) < 1e-9, run

    nc = sum(v for _, v, k in NVDA_BRIDGE if k == "nc")
    wc = sum(v for _, v, k in NVDA_BRIDGE if k == "wc")
    ax.text(3.0, 143, f"non-cash adjustments net to {nc / 1000:+,.1f}bn\n"
                      "— they nearly cancel",
            fontsize=10.6, color=C5, ha="center", fontweight="bold")
    ax.text(8.5, 143, f"working capital takes {wc / 1000:,.1f}bn\n"
                      "— and this is the whole of the gap",
            fontsize=10.6, color=C4, ha="center", fontweight="bold")

    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=8.6)
    ax.set_ylim(0, 162)
    ax.set_ylabel("USD billions")
    ax.set_title("NVIDIA FY2026: from net income to operating cash flow, and "
                 "where the 17.3bn went", fontsize=13.2, fontweight="bold")
    ax.grid(axis="y", alpha=0.25)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    save(fig, 2)
    assert abs((120_067 + nc + wc) - 102_718) < 1e-6
    print(f"  (non-cash {nc:+,}; working capital {wc:+,}; "
          f"receivables and inventory alone {-15_399 - 11_324:+,})")


# ------------------------------------------------------------------- fig 3
YEARS = ["FY2020", "FY2021", "FY2022", "FY2023", "FY2024", "FY2025", "FY2026"]
ORCL_OCF = [13_139, 15_887,  9_539, 17_165, 18_673, 20_821, 31_977]
ORCL_CAP = [ 1_564,  2_135,  4_511,  8_695,  6_866, 21_215, 55_663]
MSFT_OCF = [60_675, 76_740, 89_035, 87_582, 118_548, 136_162, 182_935]
MSFT_CAP = [15_441, 20_622, 23_886, 28_107,  44_477,  64_551, 115_948]


def fig3():
    fig, ax = plt.subplots(figsize=(12.4, 6.2))
    o = [100 * c / f for c, f in zip(ORCL_CAP, ORCL_OCF)]
    m = [100 * c / f for c, f in zip(MSFT_CAP, MSFT_OCF)]
    x = np.arange(len(YEARS))
    ax.plot(x, o, marker="o", lw=2.6, color=C2, label="Oracle")
    ax.plot(x, m, marker="s", lw=2.6, color=C1, label="Microsoft")
    for i in (0, len(YEARS) - 1):
        ax.text(x[i], o[i] + 7, f"{o[i]:.0f}%", ha="center", fontsize=11.0,
                fontweight="bold", color=C2)
        ax.text(x[i], m[i] - 11, f"{m[i]:.0f}%", ha="center", fontsize=11.0,
                fontweight="bold", color=C1)
    ax.axhline(100, color=GREY, lw=1.6, ls="--")
    ax.text(0.06, 103, "100% — every dollar the business generated is spent on "
            "capital expenditure", fontsize=10.4, color=GREY, va="bottom")
    ax.fill_between(x, 100, o, where=[v > 100 for v in o], color=C2, alpha=0.13)

    ax.set_xticks(x); ax.set_xticklabels(YEARS, fontsize=11.0)
    ax.set_ylim(0, 196)
    ax.set_ylabel("Capital expenditure as a per cent of operating cash flow")
    ax.set_title("The line that ate the free cash flow",
                 fontsize=13.2, fontweight="bold")
    ax.legend(loc="upper left", fontsize=11.2, frameon=False)
    ax.grid(axis="y", alpha=0.25)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    save(fig, 3)
    assert o[-1] > 100 and o[-2] > 100 and m[-1] < 100
    print(f"  (Oracle {o[0]:.1f}% → {o[-1]:.1f}%, crosses 100% in FY2025 at "
          f"{o[-2]:.1f}%; Microsoft {m[0]:.1f}% → {m[-1]:.1f}%)")


# ------------------------------------------------------------------- fig 4
# Oracle FY2026 (year ended 31 May 2026), Form 10-K, as filed.
ORCL_SOURCES = [("Operating cash flow", 31_977),
                ("Senior notes and term\nloans issued", 46_093),
                ("Mandatory convertible\npreferred stock", 4_954),
                ("Sales and maturities\nof securities", 5_848),
                ("Short-term financing\nfor capital expenditure", 3_345),
                ("Common stock issued", 1_449)]
ORCL_USES = [("Capital expenditure", 55_663),
             ("Debt and commercial\npaper repaid", 9_227),
             ("Dividends paid", 5_787),
             ("Securities purchased\nand acquisitions", 2_039),
             ("Buybacks, tax withholding\nand other", 543)]
ORCL_FX = 96
ORCL_CASH_UP = 20_503


def fig4():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15.6, 6.6))
    for ax, rows, col, title in (
            (ax1, ORCL_SOURCES, C3, "WHERE THE CASH CAME FROM"),
            (ax2, ORCL_USES, C2, "WHERE IT WENT")):
        names = [a for a, _ in rows]
        vals = [v / 1000 for _, v in rows]
        y = np.arange(len(names))[::-1]
        cols = [C4 if ("Operating" in n or "Capital" in n) else col for n in names]
        ax.barh(y, vals, height=0.58, color=cols)
        for yy, v in zip(y, vals):
            ax.text(v + 0.9, yy, f"{v:,.1f}", va="center", fontsize=11.0,
                    fontweight="bold", color=GREY)
        ax.set_yticks(y); ax.set_yticklabels(names, fontsize=10.0)
        ax.set_xlim(0, 66)
        ax.set_xlabel("USD billions")
        ax.set_title(f"{title}\ntotal {sum(vals):,.1f}bn", fontsize=12.4,
                     fontweight="bold")
        ax.grid(axis="x", alpha=0.25)
        ax.spines[["top", "right"]].set_visible(False)

    src = sum(v for _, v in ORCL_SOURCES)
    use = sum(v for _, v in ORCL_USES)
    assert src - use + ORCL_FX == ORCL_CASH_UP, (src, use, src - use + ORCL_FX)
    ocf, capex = ORCL_SOURCES[0][1], ORCL_USES[0][1]
    fig.suptitle("Oracle FY2026: operating cash flow of 32.0bn, capital "
                 f"expenditure of 55.7bn — and a dividend of "
                 f"{ORCL_USES[2][1] / 1000:.1f}bn paid out of new borrowing",
                 fontsize=13.2, fontweight="bold", y=0.995)
    fig.tight_layout(rect=(0, 0, 1, 0.945))
    save(fig, 4)
    print(f"  (sources {src:,} − uses {use:,} + FX {ORCL_FX} = "
          f"{src - use + ORCL_FX:,} increase in cash; "
          f"free cash flow {ocf - capex:+,})")


if __name__ == "__main__":
    fig1(); fig2(); fig3(); fig4()
    print("done")
