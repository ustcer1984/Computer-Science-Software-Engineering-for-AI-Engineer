#!/usr/bin/env python3
"""Figures for Econ E07 §5 — the notes and the red flags.

Editable source of truth for the committed SVGs (see agent-docs/diagrams.md).
Every panel is COMPUTED from filed figures or from a cited primary source,
and the identities the text asserts are asserted here too.

Sources: each company's Form 10-K. Multi-year series come from the SEC XBRL
companyfacts API, filtered to 10-K duration facts of 330-400 days (the trap
recorded in E07 §1 §10b). The useful-life effects are quoted from the
"change in accounting estimate" sentences in each filing's notes or MD&A.
The detection shares are Figure 13 of the ACFE's *Occupational Fraud 2024:
A Report to the Nations* (1,921 cases investigated Jan 2022 - Sep 2023).

  Figures are numbered in DOCUMENT order.

  fig1 — WHAT FINDS FRAUD (§2). How occupational fraud was initially
         detected: tips 43%, external audit 3%.
  fig2 — ONE SENTENCE IN A NOTE (§3). The disclosed effect of each server
         useful-life change on operating income, as a share of that year's
         operating income. Four of the largest companies in the world added
         3.5-4.6% to operating income with one sentence; Amazon went the
         other way in 2025, citing AI.
  fig3 — WHO DEFINES "PROFIT" (§4). (a) Share-based compensation as a
         share of revenue, latest fiscal year, nine companies. (b) Snowflake
         FY2019-FY2026: GAAP operating income has never been positive;
         adding back SBC alone has turned it positive every year since FY2023.
  fig4 — AN OPEN CASE (§5). Super Micro Computer FY2022-FY2026: net income
         against operating cash flow, and the FY2026 bridge in which
         inventory and receivables consume 12.8bn.

  (Function names are by topic, not by figure number.)
"""
import os

import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt
import numpy as np

OUT = os.path.dirname(os.path.abspath(__file__))
BASE = "05-notes-and-red-flags"

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
# (label, disclosed effect on operating income USD m, that year's operating
#  income USD m). Signs: + raises operating income.
LIVES = [
    ("Alphabet 2023\nservers and network → 6 yrs", 3_900, 84_293),
    ("Amazon 2024\nservers 5 → 6 yrs", 3_100, 68_593),
    ("Microsoft FY2023\nservers and network 4 → 6 yrs", 3_700, 88_523),
    ("Oracle FY2025\nservers and network 5 → 6 yrs", 733, 17_678),
    ("Meta 2025\nmost servers and network → 5.5 yrs", 2_920, 83_276),
    ("Amazon 2025\na subset of servers 6 → 5 yrs", -1_400, 79_975),
]


def fig1():
    fig, ax = plt.subplots(figsize=(11.6, 5.8))
    labels = [a for a, _, _ in LIVES]
    pct = [100 * e / oi for _, e, oi in LIVES]
    y = np.arange(len(LIVES))[::-1]
    cols = [C1 if p > 0 else C2 for p in pct]
    ax.barh(y, pct, color=cols, height=0.6)
    for yi, p, (_, e, _) in zip(y, pct, LIVES):
        ax.text(p + (0.12 if p > 0 else -0.12), yi,
                f"{p:+.1f}%  ({e / 1000:+.1f}bn)", va="center",
                ha="left" if p > 0 else "right", fontsize=10.8,
                fontweight="bold", color=C1 if p > 0 else C2)
    assert abs(pct[0] - 4.63) < 0.01 and abs(pct[-1] + 1.75) < 0.01
    ax.set_yticks(y); ax.set_yticklabels(labels, fontsize=10.2)
    ax.axvline(0, color=GREY, lw=1)
    ax.set_xlim(-4.2, 6.6)
    ax.set_xlabel("disclosed effect on that year's operating income, % of operating income")
    ax.set_title("One sentence in a note: changing how long a server is assumed to last",
                 fontsize=13.2, fontweight="bold")
    ax.text(-4.0, -0.95, "Amazon, 2025: \"due to the increased pace of technology development,\n"
                         "particularly in the area of artificial intelligence and machine learning\"",
            fontsize=9.6, color=C2, style="italic")
    ax.set_ylim(-1.3, len(LIVES) - 0.4)
    ax.grid(axis="x", alpha=0.25)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    save(fig, 2)


# ------------------------------------------------------------------- fig 2
# Latest fiscal year: (company, revenue, GAAP operating income, SBC), USD m.
SBC = [
    ("Snowflake FY2026", 4_684, -1_435, 1_600),
    ("Palantir 2025", 4_475, 1_414, 684),
    ("Meta 2025", 200_966, 83_276, 20_427),
    ("Salesforce FY2026", 41_525, 8_331, 3_509),
    ("Alphabet 2025", 402_836, 129_039, 24_953),
    ("Microsoft FY2026", 331_839, 155_237, 12_405),
    ("Apple FY2025", 416_161, 133_050, 12_863),
    ("NVIDIA FY2026", 215_938, 130_387, 6_386),
    ("Amazon 2025", 716_924, 79_975, 19_467),
]
SNOW_YEARS = ["FY19", "FY20", "FY21", "FY22", "FY23", "FY24", "FY25", "FY26"]
SNOW_OI = [-185, -358, -544, -715, -842, -1_095, -1_456, -1_435]
SNOW_SBC = [22, 78, 301, 605, 862, 1_168, 1_479, 1_600]


def fig2():
    fig, (a, b) = plt.subplots(1, 2, figsize=(15.0, 6.2),
                               gridspec_kw={"width_ratios": [1.0, 1.15]})
    names = [n for n, *_ in SBC]
    share = [100 * s / r for _, r, _, s in SBC]
    y = np.arange(len(SBC))[::-1]
    a.barh(y, share, color=[C2 if s > 10 else C5 for s in share], height=0.62)
    for yi, s in zip(y, share):
        a.text(s + 0.6, yi, f"{s:.1f}%", va="center", fontsize=10.6, fontweight="bold")
    assert abs(share[0] - 34.16) < 0.01
    a.set_yticks(y); a.set_yticklabels(names, fontsize=10.4)
    a.set_xlim(0, 40)
    a.set_xlabel("share-based compensation, % of revenue")
    a.set_title("(a) How big the adjustment is", fontsize=12.6, fontweight="bold")
    a.grid(axis="x", alpha=0.25)
    a.spines[["top", "right"]].set_visible(False)

    x = np.arange(len(SNOW_YEARS))
    adj = [o + s for o, s in zip(SNOW_OI, SNOW_SBC)]
    assert adj == [-163, -280, -243, -110, 20, 73, 23, 165], adj
    b.bar(x - 0.2, [v / 1000 for v in SNOW_OI], width=0.4, color=C2,
          label="GAAP operating income (audited)")
    b.bar(x + 0.2, [v / 1000 for v in adj], width=0.4, color=C4,
          label="operating income + SBC (the largest add-back)")
    b.text(x[-1] + 0.2, adj[-1] / 1000 + 0.05, "+0.17", ha="center",
           fontsize=10.4, fontweight="bold", color=C4)
    b.text(x[-1] - 0.2, SNOW_OI[-1] / 1000 - 0.12, "−1.44", ha="center",
           fontsize=10.4, fontweight="bold", color=C2)
    b.axhline(0, color=GREY, lw=1)
    b.set_xticks(x); b.set_xticklabels(SNOW_YEARS)
    b.set_ylim(-1.75, 0.45)
    b.set_ylabel("USD billions")
    b.set_title("(b) Snowflake: the same business, two answers", fontsize=12.6,
                fontweight="bold")
    b.legend(loc="lower left", fontsize=10, frameon=False)
    b.grid(axis="y", alpha=0.25)
    b.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    save(fig, 3)


# ------------------------------------------------------------------- fig 3
SMCI_YEARS = ["FY2022", "FY2023", "FY2024", "FY2025", "FY2026"]
SMCI_REV = [5_196, 7_123, 14_989, 21_972, 39_063]
SMCI_NI = [285, 640, 1_153, 1_049, 2_230]
SMCI_OCF = [-441, 664, -2_486, 1_660, -6_810]
# FY2026 bridge: increases in inventory and receivables as filed (cash outflows).
SMCI_INV = 8_877
SMCI_AR = 3_922


def fig3():
    fig, (a, b) = plt.subplots(1, 2, figsize=(15.0, 6.2),
                               gridspec_kw={"width_ratios": [1.25, 1.0]})
    x = np.arange(len(SMCI_YEARS))
    a.bar(x - 0.2, [v / 1000 for v in SMCI_NI], width=0.4, color=C1, label="net income")
    a.bar(x + 0.2, [v / 1000 for v in SMCI_OCF], width=0.4, color=C3,
          label="operating cash flow")
    for xi, r in zip(x, SMCI_REV):
        a.text(xi, 3.05, f"revenue\n{r / 1000:.1f}bn", ha="center", fontsize=9.6, color=GREY)
    cni, cocf = sum(SMCI_NI), sum(SMCI_OCF)
    assert (cni, cocf) == (5_357, -7_413)
    a.text(0.0, -6.2, f"five years cumulative:\nnet income {cni / 1000:+.1f}bn\n"
                      f"operating cash flow {cocf / 1000:+.1f}bn",
           fontsize=10.6, fontweight="bold", color=C2)
    a.axhline(0, color=GREY, lw=1)
    a.set_xticks(x); a.set_xticklabels(SMCI_YEARS)
    a.set_ylim(-7.6, 3.9)
    a.set_ylabel("USD billions")
    a.set_title("(a) Super Micro: profit and cash, five years", fontsize=12.6,
                fontweight="bold")
    a.legend(loc="upper left", bbox_to_anchor=(0.0, 0.86), fontsize=10, frameon=False)
    a.grid(axis="y", alpha=0.25)
    a.spines[["top", "right"]].set_visible(False)

    other = SMCI_OCF[-1] - SMCI_NI[-1] + SMCI_INV + SMCI_AR
    steps = [("Net income", SMCI_NI[-1], C1), ("Inventories", -SMCI_INV, C4),
             ("Receivables", -SMCI_AR, C4), ("Everything\nelse", other, C5)]
    run = 0.0
    for i, (lab, v, c) in enumerate(steps):
        v /= 1000
        if i == 0:
            b.bar(i, v, color=c, width=0.6); run = v
        else:
            b.bar(i, abs(v), bottom=min(run, run + v), color=c, width=0.6); run += v
        b.text(i, max(run, run - v if i else v) + 0.35, f"{v:+.1f}", ha="center",
               fontsize=10.8, fontweight="bold", color=c)
    b.bar(4, SMCI_OCF[-1] / 1000, color=C3, width=0.6)
    b.text(4, SMCI_OCF[-1] / 1000 - 0.8, f"{SMCI_OCF[-1] / 1000:+.1f}", ha="center",
           fontsize=10.8, fontweight="bold", color=C3)
    assert abs(run - SMCI_OCF[-1] / 1000) < 1e-9
    b.axhline(0, color=GREY, lw=1)
    b.set_xticks(range(5))
    b.set_xticklabels([s[0] for s in steps] + ["Operating\ncash flow"], fontsize=10)
    b.set_ylim(-11.5, 4.2)
    b.set_title("(b) FY2026: where the 9.0bn gap went", fontsize=12.6, fontweight="bold")
    b.grid(axis="y", alpha=0.25)
    b.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    save(fig, 4)


# ------------------------------------------------------------------- fig 4
DETECT = [("Tip", 43), ("Internal audit", 14), ("Management review", 13),
          ("Document examination", 6), ("Account reconciliation", 5),
          ("By accident", 5), ("External audit", 3),
          ("Automated transaction/data monitoring", 3),
          ("Surveillance/monitoring", 2), ("Notification by law enforcement", 2),
          ("Other", 2), ("Confession", 1)]


def fig4():
    fig, ax = plt.subplots(figsize=(11.0, 6.0))
    y = np.arange(len(DETECT))[::-1]
    vals = [v for _, v in DETECT]
    cols = [C2 if n == "External audit" else (C1 if n == "Tip" else C5) for n, _ in DETECT]
    ax.barh(y, vals, color=cols, height=0.62)
    for yi, v in zip(y, vals):
        ax.text(v + 0.5, yi, f"{v}%", va="center", fontsize=10.6, fontweight="bold")
    ax.set_yticks(y); ax.set_yticklabels([n for n, _ in DETECT], fontsize=10.4)
    ax.set_xlim(0, 50)
    ax.set_xlabel("% of 1,921 cases, by how the fraud was first detected")
    ax.set_title("What actually finds fraud — and how rarely it is the external auditor",
                 fontsize=13.0, fontweight="bold")
    ax.grid(axis="x", alpha=0.25)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    save(fig, 1)


if __name__ == "__main__":
    fig1(); fig2(); fig3(); fig4()
