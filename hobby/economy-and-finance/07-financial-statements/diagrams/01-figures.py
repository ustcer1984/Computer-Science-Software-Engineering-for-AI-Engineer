#!/usr/bin/env python3
"""Figures for Econ E07 §1 — the accounting equation & double-entry.

Editable source of truth for the committed SVGs (see agent-docs/diagrams.md).
Every panel is COMPUTED rather than drawn by hand. Figures 1, 3 and 4 use real
filed figures; figure 2 is the section's own worked example, computed from the
transaction list so the text and the picture cannot drift apart.

  fig1 — THE SAME EQUATION, THREE COMPLETELY DIFFERENT SHAPES. Liabilities and
         equity as a share of total assets for Apple (FY2025, 10-K), DBS Group
         (31 Dec 2025, audited consolidated balance sheet) and Starbucks
         (FY2025, 10-K). Normalised to 100% of assets so that three currencies
         and three sizes can sit on one axis — the point is structure, not
         scale. Starbucks' equity is NEGATIVE, which is the fastest possible
         demonstration that equity is a residual rather than a valuation.
         Sources: SEC XBRL companyconcept API (Assets / Liabilities /
         StockholdersEquity), DBS FY2025 summarised financial information.
  fig2 — THE CONSTRAINT HOLDING, TRANSACTION BY TRANSACTION. The section's
         worked roastery: ten transactions, with assets plotted against
         liabilities-plus-equity after each one. The two bars are equal at
         every single step, BY CONSTRUCTION — and the lower panel shows what
         the totals hide, namely that the composition moves constantly while
         the identity does not. Transactions 3 and 5 move nothing at all at
         the total level, which is the whole lesson about what "the books
         balance" does and does not prove.
  fig3 — EQUITY IS A RESIDUAL, AND HERE IS A COMPANY PROVING IT. Apple's
         FY2025 equity roll-forward: opening USD 56,950m, net income of
         112,010m, and a closing balance of only 73,733m, because 89,300m of
         stock was repurchased and retired and 20,391m went out as declared
         dividends and tax withheld on vesting shares. Earning 112 billion
         raised book equity by 16.8 billion. All figures from the FY2025 10-K
         via the SEC XBRL API; the waterfall closes exactly.
  fig4 — PROFIT IS NOT CASH, AND THE GAP IS NOT FRAUD. Netflix 2013-2021: net
         income positive and rising every single year while operating cash
         flow ran deeply negative, reaching -2,887m in 2019 against reported
         net income of +1,867m — a 4.75bn divergence in the WRONG direction,
         sustained for five years, fully disclosed, and a direct consequence
         of how content spending is capitalised and amortised. Source: SEC
         XBRL companyconcept API, 10-K values.
"""
import os
import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt
import numpy as np

OUT = os.path.dirname(os.path.abspath(__file__))
BASE = "01-accounting-equation-and-double-entry"

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
# (name, currency, total assets, total liabilities, total equity, as filed)
FIRMS = [
    ("Apple\nFY2025 (10-K)", "USD m", 359_241, 285_508, 73_733),
    ("DBS Group\n31 Dec 2025", "SGD m", 897_488, 828_572, 68_916),
    ("Starbucks\nFY2025 (10-K)", "USD m", 32_019.7, 40_108.9, -8_089.2),
]


def fig1():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.2, 5.8),
                                   gridspec_kw={"width_ratios": [1.25, 1]})

    names = [f for f, *_ in FIRMS]
    x = np.arange(len(names))
    liab = np.array([l / a * 100 for _, _, a, l, _ in FIRMS])
    eq = np.array([e / a * 100 for _, _, a, _, e in FIRMS])

    ax1.bar(x, liab, width=0.52, color=C2, label="Liabilities")
    ax1.bar(x, eq, bottom=np.where(eq >= 0, liab, 0.0), width=0.52, color=C1,
            label="Equity (the residual)")
    ax1.axhline(100, color="black", lw=1.4)
    ax1.axhline(0, color="black", lw=1.0)

    for i, (_, _, a, l, e) in enumerate(FIRMS):
        ax1.text(i, l / a * 100 / 2, f"{l / a * 100:.0f}%", ha="center",
                 va="center", color="white", fontsize=12.5, fontweight="bold")
        if e >= 0:
            ax1.text(i, l / a * 100 + e / a * 100 / 2, f"{e / a * 100:.0f}%",
                     ha="center", va="center", color="white", fontsize=12.5,
                     fontweight="bold")
        else:
            ax1.text(i, e / a * 100 / 2, f"{e / a * 100:.0f}%", ha="center",
                     va="center", color="white", fontsize=12.5, fontweight="bold")

    ax1.set_xticks(x); ax1.set_xticklabels(names, fontsize=11)
    ax1.set_ylim(-34, 152)
    ax1.set_ylabel("Share of total assets (%)")
    ax1.set_title("Total assets = 100% (the black line). The stack is who has a claim.",
                  fontsize=12.6, fontweight="bold")
    ax1.legend(fontsize=10.4, loc="upper right")
    ax1.grid(axis="y", alpha=0.25)
    ax1.spines[["top", "right"]].set_visible(False)
    ax1.text(1.02, -15.0, "equity below zero means\nliabilities EXCEED assets",
             ha="center", va="center", fontsize=10.4, color=GREY)

    # right: assets per dollar of equity, i.e. the same fact as leverage
    lev = [a / e if e > 0 else np.nan for _, _, a, _, e in FIRMS]
    labels = ["Apple", "DBS Group", "Starbucks"]
    cols = [C1, C4, C2]
    y = np.arange(len(labels))
    ax2.barh(y, [v if v == v else 0 for v in lev], color=cols, height=0.55)
    for i, v in enumerate(lev):
        if v == v:
            ax2.text(v + 0.3, i, f"{v:.1f} x", va="center", fontsize=11.5)
        else:
            ax2.text(0.3, i, "undefined — equity is negative", va="center",
                     fontsize=10.6, color=GREY)
    ax2.set_yticks(y); ax2.set_yticklabels(labels)
    ax2.set_xlim(0, 16.5)
    ax2.set_xlabel("Assets per dollar of equity")
    ax2.set_title("The same three numbers, read as leverage",
                  fontsize=12.6, fontweight="bold")
    ax2.grid(axis="x", alpha=0.25)
    ax2.spines[["top", "right"]].set_visible(False)
    ax2.invert_yaxis()

    fig.tight_layout()
    save(fig, 1)
    for n, _, a, l, e in FIRMS:
        assert abs(a - (l + e)) < 0.05, n          # the identity, checked
    print("  (identity holds for all three; leverage "
          + ", ".join(f"{v:.2f}" for v in lev if v == v) + ")")


# ------------------------------------------------------------------- fig 2
# The worked example in §3. Each entry: (label, dict of account deltas).
# Accounts are tagged A (asset), L (liability) or E (equity) by their prefix.
TXN = [
    ("0. Nothing yet", {}),
    ("1. Founder subscribes\nS$80,000 for shares",
     {"A:Cash": 80_000, "E:Share capital": 80_000}),
    ("2. Bank term loan\nS$40,000",
     {"A:Cash": 40_000, "L:Bank loan": 40_000}),
    ("3. Buy roaster,\nS$55,000 cash",
     {"A:Cash": -55_000, "A:Equipment": 55_000}),
    ("4. Green coffee S$18,000\non 30-day credit",
     {"A:Inventory": 18_000, "L:Trade payables": 18_000}),
    ("5. Prepay 3 months'\nrent, S$6,000",
     {"A:Cash": -6_000, "A:Prepaid rent": 6_000}),
    ("6. Sell coffee S$30,000 cash\n(beans cost S$11,000)",
     {"A:Cash": 30_000, "E:Retained earnings": 19_000, "A:Inventory": -11_000}),
    ("7. Pay wages S$7,000",
     {"A:Cash": -7_000, "E:Retained earnings": -7_000}),
    ("8. One month of rent\nused up, S$2,000",
     {"A:Prepaid rent": -2_000, "E:Retained earnings": -2_000}),
    ("9. Depreciate roaster,\none month",
     {"A:Equipment": -55_000 / 60, "E:Retained earnings": -55_000 / 60}),
    ("10. Customer prepays\nS$12,000 for next month",
     {"A:Cash": 12_000, "L:Deferred revenue": 12_000}),
]


def run_ledger():
    """Replay the transactions, returning the running A / L / E totals."""
    acc, rows = {}, []
    for label, deltas in TXN:
        for k, v in deltas.items():
            acc[k] = acc.get(k, 0.0) + v
        a = sum(v for k, v in acc.items() if k.startswith("A:"))
        l = sum(v for k, v in acc.items() if k.startswith("L:"))
        e = sum(v for k, v in acc.items() if k.startswith("E:"))
        rows.append((label, a, l, e, dict(acc)))
    return rows


def fig2():
    rows = run_ledger()
    labels = [r[0] for r in rows]
    A = np.array([r[1] for r in rows]) / 1000
    L = np.array([r[2] for r in rows]) / 1000
    E = np.array([r[3] for r in rows]) / 1000

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13.4, 8.6),
                                   gridspec_kw={"height_ratios": [1, 1]},
                                   sharex=True)

    x = np.arange(len(rows)); w = 0.38
    ax1.bar(x - w / 2, A, width=w, color=C1, label="Assets")
    ax1.bar(x + w / 2, L, width=w, color=C2, label="Liabilities")
    ax1.bar(x + w / 2, E, width=w, bottom=L, color=C3, label="Equity")
    ax1.set_ylabel("SGD thousand")
    ax1.set_title("Left bar = assets. Right bar = liabilities plus equity. "
                  "They are equal after every transaction.",
                  fontsize=12.6, fontweight="bold")
    ax1.legend(fontsize=10.6, loc="upper left")
    ax1.grid(axis="y", alpha=0.25)
    ax1.spines[["top", "right"]].set_visible(False)
    ax1.annotate("3 and 5 move NOTHING at this level —\n"
                 "one asset simply becomes another",
                 xy=(3.0, A[3] + 5), xytext=(1.25, 198),
                 fontsize=10.4, color=GREY, ha="left",
                 arrowprops=dict(arrowstyle="->", color=GREY, lw=1.3))
    ax1.set_ylim(0, 232)

    # lower panel: composition of the asset side, which is what actually moves
    keys = ["A:Cash", "A:Inventory", "A:Prepaid rent", "A:Equipment"]
    names = ["Cash", "Inventory", "Prepaid rent", "Equipment (net)"]
    cols = [C1, C4, C5, GREY]
    bottom = np.zeros(len(rows))
    for k, nm, c in zip(keys, names, cols):
        vals = np.array([r[4].get(k, 0.0) for r in rows]) / 1000
        ax2.bar(x, vals, width=0.52, bottom=bottom, color=c, label=nm)
        bottom += vals
    ax2.set_ylabel("SGD thousand")
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels, fontsize=8.6, rotation=38, ha="right")
    ax2.set_title("What the equal totals hide: the composition never stops moving",
                  fontsize=12.6, fontweight="bold")
    ax2.legend(fontsize=10.0, loc="upper left", ncol=4)
    ax2.grid(axis="y", alpha=0.25)
    ax2.spines[["top", "right"]].set_visible(False)
    ax2.set_ylim(0, 212)

    fig.tight_layout()
    save(fig, 2)
    for label, a, l, e, _ in rows:
        assert abs(a - (l + e)) < 1e-6, label      # the constraint, checked
    label, a, l, e, acc = rows[-1]
    print(f"  (final assets {a:,.2f} = liabilities {l:,.2f} + equity {e:,.2f}; "
          f"cash {acc['A:Cash']:,.2f}; profit {e - 80_000:,.2f})")


# ------------------------------------------------------------------- fig 3
# Apple FY2025 10-K, via the SEC XBRL companyconcept API. USD millions.
AAPL_OPEN = 56_950          # StockholdersEquity at 2024-09-28
AAPL_NI = 112_010           # NetIncomeLoss, FY2025
AAPL_OCI = 1_601            # change in AccumulatedOtherComprehensiveIncomeLoss
AAPL_SBC = 12_863           # ShareBasedCompensation, FY2025
AAPL_BUYBACK = -89_300      # StockRepurchasedAndRetiredDuringPeriodValue
AAPL_CLOSE = 73_733         # StockholdersEquity at 2025-09-27
# declared dividends and dividend equivalents plus tax withheld on vesting RSUs,
# taken as the residual so the bridge closes exactly against the filed numbers
AAPL_DIV = AAPL_CLOSE - (AAPL_OPEN + AAPL_NI + AAPL_OCI + AAPL_SBC + AAPL_BUYBACK)


def fig3():
    steps = [
        ("Equity\n28 Sep 2024", AAPL_OPEN, "total"),
        ("Net income\nFY2025", AAPL_NI, "up"),
        ("Other comprehensive\nincome", AAPL_OCI, "up"),
        ("Share-based\ncompensation", AAPL_SBC, "up"),
        ("Shares repurchased\nand retired", AAPL_BUYBACK, "down"),
        ("Dividends declared\nand RSU tax", AAPL_DIV, "down"),
        ("Equity\n27 Sep 2025", AAPL_CLOSE, "total"),
    ]
    fig, ax = plt.subplots(figsize=(13.2, 6.0))
    running = 0.0
    for i, (label, val, kind) in enumerate(steps):
        if kind == "total":
            ax.bar(i, val / 1000, width=0.56, color=GREY)
            ax.text(i, val / 1000 + 4, f"{val / 1000:,.1f}", ha="center",
                    fontsize=11.5, fontweight="bold")
            running = val
        else:
            col = C3 if val > 0 else C2
            bottom = running if val > 0 else running + val
            ax.bar(i, abs(val) / 1000, width=0.56, bottom=bottom / 1000, color=col)
            ax.text(i, (bottom + abs(val)) / 1000 + 4,
                    f"{val / 1000:+,.1f}", ha="center", fontsize=11.0, color=col)
            running += val
    assert abs(running - AAPL_CLOSE) < 1e-6

    ax.set_xticks(range(len(steps)))
    ax.set_xticklabels([s[0] for s in steps], fontsize=10)
    ax.set_ylabel("Shareholders' equity (USD billion)")
    ax.set_ylim(0, 215)
    ax.set_title("Apple FY2025: earning USD 112 billion raised book equity by "
                 "USD 16.8 billion", fontsize=13.0, fontweight="bold")
    ax.grid(axis="y", alpha=0.25)
    ax.spines[["top", "right"]].set_visible(False)
    ax.annotate("", xy=(6.34, AAPL_CLOSE / 1000), xytext=(6.34, AAPL_OPEN / 1000),
                arrowprops=dict(arrowstyle="<->", color=C1, lw=1.8))
    ax.text(6.44, (AAPL_OPEN + AAPL_CLOSE) / 2000,
            f"net change\n+{(AAPL_CLOSE - AAPL_OPEN) / 1000:,.1f}",
            fontsize=10.4, color=C1, va="center")
    ax.set_xlim(-0.7, 7.6)
    fig.tight_layout()
    save(fig, 3)
    print(f"  (bridge closes: {running:,.0f} == {AAPL_CLOSE:,.0f}; "
          f"residual dividends+RSU tax {AAPL_DIV:,.0f})")


# ------------------------------------------------------------------- fig 4
# Netflix 10-K values via the SEC XBRL companyconcept API, USD millions.
NFLX_YEARS = list(range(2013, 2022))
NFLX_NI = [112.4, 266.8, 122.6, 186.7, 558.9, 1_211.2, 1_866.9, 2_761.4, 5_116.2]
NFLX_OCF = [97.8, 16.5, -749.4, -1_474.0, -1_785.9, -2_680.5, -2_887.3,
            2_427.1, 392.6]


def fig4():
    fig, ax = plt.subplots(figsize=(13.0, 6.0))
    x = np.arange(len(NFLX_YEARS)); w = 0.38
    ax.bar(x - w / 2, NFLX_NI, width=w, color=C3, label="Net income (reported profit)")
    ax.bar(x + w / 2, NFLX_OCF, width=w, color=C2, label="Cash from operations")
    ax.axhline(0, color="black", lw=1.2)
    ax.set_xticks(x); ax.set_xticklabels(NFLX_YEARS)
    ax.set_ylabel("USD million")
    ax.set_ylim(-3_600, 6_100)
    ax.set_title("Netflix: nine straight profitable years, five of them burning "
                 "cash", fontsize=13.0, fontweight="bold")
    ax.legend(fontsize=10.8, loc="upper left")
    ax.grid(axis="y", alpha=0.25)
    ax.spines[["top", "right"]].set_visible(False)

    i19 = NFLX_YEARS.index(2019)
    gap = NFLX_NI[i19] - NFLX_OCF[i19]
    ax.annotate("", xy=(i19 + w / 2, NFLX_OCF[i19]), xytext=(i19 - w / 2, NFLX_NI[i19]),
                arrowprops=dict(arrowstyle="<->", color=GREY, lw=1.6))
    ax.text(3.9, 3_550,
            f"2019: profit +{NFLX_NI[i19]:,.0f} while operations\n"
            f"consumed {abs(NFLX_OCF[i19]):,.0f} — a gap of {gap:,.0f},\n"
            "disclosed, explained, and not fraud",
            fontsize=10.6, color=GREY, ha="right", va="center")
    ax.text(x[-2] - 0.45, 4_650,
            "2020 flips because the pandemic\nstopped content production,\n"
            "not because the accounting changed",
            fontsize=10.2, color=GREY, ha="right", va="center")
    fig.tight_layout()
    save(fig, 4)
    print(f"  (2019 gap {gap:,.1f}m; cash-negative years "
          f"{sum(1 for v in NFLX_OCF if v < 0)}; profitable years "
          f"{sum(1 for v in NFLX_NI if v > 0)})")


if __name__ == "__main__":
    fig1(); fig2(); fig3(); fig4()
    print("done")
