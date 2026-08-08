#!/usr/bin/env python3
"""Figures for Econ E04 §1 — Taxes, spending & the government budget.

Editable source of truth for the committed SVGs (see agent-docs/diagrams.md).
Numbers are illustrative but chosen to match the real shape of the pictures
(representative recent shares/values for well-known public series):

  fig1 — WHERE THE MONEY COMES FROM: government revenue by source, as a share of
         total revenue, for three very different systems — the USA (income +
         payroll heavy), a high-tax European system (consumption/VAT + social
         contributions heavy), and Singapore (corporate + GST + a large non-tax
         investment-income contribution).
  fig2 — WHERE THE MONEY GOES: US federal outlays by category, sorted, coloured by
         mandatory vs discretionary vs net interest — mandatory + interest now
         dominate.
  fig3 — THE BUDGET BALANCE: US federal surplus/deficit as a share of GDP,
         1960–2024, with the late-1990s surpluses, the GFC trough, and the COVID
         spike marked. Deficits widen automatically in every recession
         (the automatic stabilizers, E02 §4).
  fig4 — THE STABILIZATION LEVER: illustrative fiscal-multiplier ranges by
         instrument (spending/investment vs tax cut) and by state of the economy
         (deep slack vs near full employment). Spending beats tax cuts, and both
         are bigger when there is slack.

Run with the project venv:

    .venv/bin/python hobby/economy-and-finance/04-fiscal-policy/diagrams/01-figures.py

Outputs 01-taxes-spending-and-the-budget-figN.svg into this folder.
"""
import os
import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt
import numpy as np

OUT = os.path.dirname(os.path.abspath(__file__))
BASE = "01-taxes-spending-and-the-budget"

plt.rcParams.update({
    "font.size": 12,
    "axes.titlesize": 13,
    "axes.labelsize": 12,
    "svg.fonttype": "none",
    "figure.dpi": 100,
    "text.parse_math": False,
})

C1 = "#1f77b4"; C2 = "#d62728"; C3 = "#2ca02c"; C4 = "#ff7f0e"; C5 = "#9467bd"
C6 = "#8c564b"; GREY = "#555555"


def save(fig, n):
    path = os.path.join(OUT, f"{BASE}-fig{n}.svg")
    fig.savefig(path, format="svg", bbox_inches="tight")
    plt.close(fig)
    print("wrote", path)


# ---------------------------------------------------------------------------
# Fig 1 — Where the money comes from: revenue composition (share of total).
# ---------------------------------------------------------------------------
def fig1():
    cats = ["Personal\nincome", "Payroll /\nsocial contrib.", "Consumption\n(VAT/GST)",
            "Corporate\nincome", "Other tax\n(property, etc.)", "Non-tax\n(e.g. invest. income)"]
    # Illustrative shares of total revenue (%), rows sum ~100.
    usa    = [49, 35, 0, 9, 5, 2]
    europe = [23, 33, 25, 6, 9, 4]     # high-tax European system (VAT + social)
    sing   = [15, 0, 20, 22, 20, 23]   # SG: corporate + GST + NIRC-type non-tax
    X = np.arange(len(cats)); w = 0.26

    fig, ax = plt.subplots(figsize=(11.2, 5.9))
    ax.bar(X - w, usa, w, label="USA (federal)", color=C1)
    ax.bar(X, europe, w, label="High-tax Europe", color=C4)
    ax.bar(X + w, sing, w, label="Singapore", color=C2)

    ax.set_xticks(X); ax.set_xticklabels(cats, fontsize=9)
    ax.set_ylabel("Share of total government revenue (%)")
    ax.set_title("Where the money comes from: three very different revenue mixes (illustrative)")
    ax.legend(fontsize=9.5)
    ax.set_ylim(0, 55)
    ax.grid(axis="y", alpha=0.25)
    ax.spines[["top", "right"]].set_visible(False)
    ax.annotate("US leans on income\n+ payroll; no federal VAT",
                xy=(0 - w, 49), xytext=(0.2, 52), fontsize=8.4, color=C1,
                arrowprops=dict(arrowstyle="->", color=C1, lw=1.1))
    ax.annotate("Europe leans on\nVAT + social contributions",
                xy=(2, 25), xytext=(2.3, 40), fontsize=8.4, color=C4,
                arrowprops=dict(arrowstyle="->", color=C4, lw=1.1))
    ax.annotate("Singapore: corporate + GST +\na big NON-TAX slice (NIRC,\ninvestment returns — §4 §10b)",
                xy=(5 + w, 23), xytext=(3.5, 44), fontsize=8.4, color=C2,
                arrowprops=dict(arrowstyle="->", color=C2, lw=1.1))
    save(fig, 1)


# ---------------------------------------------------------------------------
# Fig 2 — Where the money goes: US federal outlays by category.
# ---------------------------------------------------------------------------
def fig2():
    cats = ["Health\n(Medicare/\nMedicaid)", "Social\nSecurity", "Other\nmandatory",
            "Non-defense\ndiscretionary", "Defense\ndiscretionary", "Net\ninterest"]
    share = [24, 21, 17, 14, 13, 11]
    # colour by type: mandatory (green), discretionary (blue), interest (red)
    kind = ["M", "M", "M", "D", "D", "I"]
    cmap = {"M": C3, "D": C1, "I": C2}
    colors = [cmap[k] for k in kind]

    fig, ax = plt.subplots(figsize=(11.0, 5.8))
    bars = ax.bar(cats, share, color=colors, width=0.66)
    for b, v in zip(bars, share):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.5, f"{v}%", ha="center",
                fontsize=9.5, fontweight="bold")

    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=C3, label="Mandatory / entitlements"),
                       Patch(color=C1, label="Discretionary (annual appropriations)"),
                       Patch(color=C2, label="Net interest on the debt")],
              fontsize=9.5, loc="upper right")
    ax.set_ylabel("Share of total federal outlays (%)")
    ax.set_title("Where the money goes (US federal): mandatory + interest now dominate (illustrative)")
    ax.set_ylim(0, 30)
    ax.grid(axis="y", alpha=0.25)
    ax.spines[["top", "right"]].set_visible(False)
    ax.text(4.0, 22.0, "Mandatory + interest ≈ 73% → only ~27% is the\n'discretionary' budget Congress votes on each year",
            ha="center", fontsize=9, color=GREY, fontweight="bold")
    save(fig, 2)


# ---------------------------------------------------------------------------
# Fig 3 — The budget balance: US federal surplus/deficit as % of GDP.
# ---------------------------------------------------------------------------
def fig3():
    yrs = np.array([1960, 1965, 1968, 1970, 1975, 1980, 1983, 1986, 1990, 1993,
                    1998, 1999, 2000, 2001, 2004, 2007, 2009, 2012, 2015, 2018,
                    2019, 2020, 2021, 2022, 2023, 2024])
    bal = np.array([0.1, -0.2, -2.8, -0.3, -3.3, -2.6, -5.9, -4.9, -3.7, -3.7,
                    0.8, 1.3, 2.3, 1.2, -3.4, -1.1, -9.8, -6.7, -2.4, -3.8,
                    -4.6, -14.7, -11.9, -5.4, -6.2, -6.3])

    fig, ax = plt.subplots(figsize=(11.2, 5.8))
    ax.fill_between(yrs, 0, bal, where=(bal >= 0), color=C3, alpha=0.5, interpolate=True)
    ax.fill_between(yrs, 0, bal, where=(bal < 0), color=C2, alpha=0.35, interpolate=True)
    ax.plot(yrs, bal, color=GREY, lw=1.8)
    ax.axhline(0, color="black", lw=1.0)

    ax.annotate("Clinton-era\nSURPLUSES\n(1998–2001)", xy=(1999.5, 1.6), xytext=(1988.5, 3.5),
                fontsize=8.6, color=C3, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=C3, lw=1.2))
    ax.annotate("GFC\n−9.8% (2009)", xy=(2009, -9.8), xytext=(2003.2, -12.5),
                fontsize=8.6, color=C2, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=C2, lw=1.2))
    ax.annotate("COVID\n−14.7% (2020)", xy=(2020, -14.7), xytext=(2013.5, -13.2),
                fontsize=8.6, color=C2, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=C2, lw=1.2))
    ax.text(1960.5, -14.2, "deficits widen automatically in EVERY recession\n(the automatic stabilizers, E02 §4 §10a)",
            fontsize=8.8, color=GREY, style="italic")

    ax.set_xlabel("Year")
    ax.set_ylabel("Federal surplus (+) / deficit (−), % of GDP")
    ax.set_title("The budget balance: the US has run deficits in almost every year since 1970")
    ax.set_ylim(-16, 5.5)
    ax.set_xlim(1959, 2025)
    ax.grid(axis="y", alpha=0.25)
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, 3)


# ---------------------------------------------------------------------------
# Fig 4 — The stabilization lever: fiscal-multiplier ranges.
# ---------------------------------------------------------------------------
def fig4():
    labels = ["Public\ninvestment", "Gov't\nspending", "Transfers to\nliquidity-\nconstrained",
              "Broad\ntax cut"]
    slump  = [1.6, 1.4, 1.2, 0.8]      # deep slack / at the ZLB
    normal = [0.8, 0.7, 0.5, 0.4]      # near full employment
    X = np.arange(len(labels)); w = 0.36

    fig, ax = plt.subplots(figsize=(10.8, 5.8))
    ax.bar(X - w/2, slump, w, label="In a slump (slack / ZLB)", color=C2)
    ax.bar(X + w/2, normal, w, label="Near full employment", color=C1)
    ax.axhline(1.0, color=GREY, ls="--", lw=1.0)
    ax.text(3.35, 1.03, "multiplier = 1\n(a dollar spent →\na dollar of GDP)", fontsize=8.2,
            color=GREY, va="bottom", ha="right")

    for x, v in zip(X - w/2, slump):
        ax.text(x, v + 0.03, f"{v}", ha="center", fontsize=8.6, color=C2, fontweight="bold")
    for x, v in zip(X + w/2, normal):
        ax.text(x, v + 0.03, f"{v}", ha="center", fontsize=8.6, color=C1, fontweight="bold")

    ax.set_xticks(X); ax.set_xticklabels(labels, fontsize=9.2)
    ax.set_ylabel("Fiscal multiplier (extra GDP per $1 of stimulus)")
    ax.set_title("The stabilization lever: spending beats tax cuts, and slack makes both bigger (illustrative ranges)")
    ax.legend(fontsize=9.5, loc="upper right")
    ax.set_ylim(0, 1.9)
    ax.grid(axis="y", alpha=0.25)
    ax.spines[["top", "right"]].set_visible(False)
    ax.annotate("tax cuts are partly SAVED\n(MPC < 1) → smaller bang\nthan direct spending",
                xy=(3 - w/2, 0.8), xytext=(1.35, 1.55), fontsize=8.4, color=GREY,
                arrowprops=dict(arrowstyle="->", color=GREY, lw=1.1))
    save(fig, 4)


if __name__ == "__main__":
    fig1(); fig2(); fig3(); fig4()
    print("done")
