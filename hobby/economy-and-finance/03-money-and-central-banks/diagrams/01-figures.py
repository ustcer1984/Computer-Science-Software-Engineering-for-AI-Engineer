#!/usr/bin/env python3
"""Figures for Econ E03 §1 — What money is, and how banks create it.

Editable source of truth for the committed SVGs (see agent-docs/diagrams.md:
commit the rendered image, keep the source beside it). Numbers are illustrative
but chosen to match the real shape of the published pictures:

  fig1 — the US monetary aggregates (~2024), nested: the monetary base M0 is a
         MINORITY of broad money M2; most money is commercial-bank deposits.
  fig2 — the textbook money-multiplier CASCADE as a shrinking geometric series
         (same maths as the E02 §4 spending multiplier), summing to 1/r.
  fig3 — LOANS CREATE DEPOSITS: a bank's balance sheet before/after a new loan;
         both asset and liability sides expand together (new money from nothing).
  fig4 — the money multiplier ratio M2/M0 over time COLLAPSING after 2008 QE —
         the empirical case against the mechanical multiplier / for endogenous
         money.

Run with the project venv:

    .venv/bin/python hobby/economy-and-finance/03-money-and-central-banks/diagrams/01-figures.py

Outputs 01-money-and-bank-credit-figN.svg into this folder.
"""
import os
import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

OUT = os.path.dirname(os.path.abspath(__file__))
BASE = "01-money-and-bank-credit"

plt.rcParams.update({
    "font.size": 12,
    "axes.titlesize": 13,
    "axes.labelsize": 12,
    "svg.fonttype": "none",   # keep text as text (smaller, selectable)
    "figure.dpi": 100,
})

C_BASE = "#d62728"   # central-bank money (base) / red
C_DEP = "#1f77b4"    # commercial-bank deposits / blue
C_CASH = "#ff7f0e"   # physical currency / orange
C_RES = "#9467bd"    # reserves / purple
C_LOAN = "#2ca02c"   # loans (asset) / green
GREY = "#555555"


def save(fig, n):
    path = os.path.join(OUT, f"{BASE}-fig{n}.svg")
    fig.savefig(path, format="svg", bbox_inches="tight")
    plt.close(fig)
    print("wrote", path)


# ---------------------------------------------------------------------------
# Fig 1 — The monetary aggregates (US, approx 2024, trillions of USD).
#   A tall M2 bar built as M1 + (M2-M1); an M1 bar built as currency + deposits;
#   and a separate, much SHORTER monetary-base bar (currency + reserves) to make
#   the point that central-bank money is a MINORITY of the money supply and the
#   bulk of money is commercial-bank deposits.
# ---------------------------------------------------------------------------
def fig1():
    # Approximate US values, trillions USD (illustrative, ~2024).
    currency = 2.3      # physical notes & coins in circulation
    reserves = 3.3      # bank reserves at the Fed
    base = currency + reserves          # M0 ~ 5.6
    m1_deposits = 15.7                  # spendable deposits in M1
    m1 = currency + m1_deposits         # ~18.0
    m2_extra = 3.0                      # M2 minus M1 (time/MMF)
    m2 = m1 + m2_extra                  # ~21.0

    fig, ax = plt.subplots(figsize=(9.2, 5.6))
    x_base, x_m2 = 0.0, 1.3
    w = 0.62

    # --- Monetary base bar (M0): currency + reserves ---
    ax.bar(x_base, currency, w, color=C_CASH, label="Physical currency")
    ax.bar(x_base, reserves, w, bottom=currency, color=C_RES, label="Bank reserves")
    ax.text(x_base, base + 0.35, f"M0 base\n≈ {base:.1f}T", ha="center", fontsize=9.5,
            fontweight="bold")

    # --- Broad money bar (M2): currency + deposits + M2-extra ---
    ax.bar(x_m2, currency, w, color=C_CASH)
    ax.bar(x_m2, m1_deposits, w, bottom=currency, color=C_DEP,
           label="Commercial-bank deposits")
    ax.bar(x_m2, m2_extra, w, bottom=m1, color=C_DEP, alpha=0.55,
           label="M2-only (time/MMF)")
    ax.text(x_m2, m1 + 0.05, "— M1 line", ha="left", va="center", fontsize=8.2,
            color=GREY)
    ax.plot([x_m2 - w / 2, x_m2 + w / 2], [m1, m1], color=GREY, lw=1.2, ls="--")
    ax.text(x_m2, m2 + 0.35, f"M2 broad\n≈ {m2:.1f}T", ha="center", fontsize=9.5,
            fontweight="bold")

    # Annotation: the gap is privately-created money.
    ax.annotate("", xy=(x_m2 + w / 2 + 0.08, base), xytext=(x_m2 + w / 2 + 0.08, m2),
                arrowprops=dict(arrowstyle="<->", color="black", lw=1.4))
    ax.text(x_m2 + w / 2 + 0.16, (base + m2) / 2,
            "the gap = commercial-bank\ndeposits (created by LENDING) —\n>80% of all money is NOT\ncentral-bank money",
            fontsize=8.8, va="center", ha="left")

    ax.set_xticks([x_base, x_m2])
    ax.set_xticklabels(["Central-bank money\n(M0 / base)",
                        "The money supply\n(M2)"])
    ax.set_ylabel("Trillions of USD (approx. 2024)")
    ax.set_title("Most money is private bank deposits, not government cash")
    ax.set_ylim(0, 24)
    ax.set_xlim(-0.6, 2.35)
    ax.legend(loc="upper left", fontsize=8.4, frameon=True, framealpha=0.95)
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, 1)


# ---------------------------------------------------------------------------
# Fig 2 — The textbook money-multiplier cascade. A 1000 injection with a 10%
#   reserve ratio produces lending rounds 900, 810, 729, ... (a geometric
#   series), and cumulative deposits approach 1000/r = 10,000. Same maths as the
#   E02 §4 spending multiplier — shown to be recognised, then dismantled in §4b.
# ---------------------------------------------------------------------------
def fig2():
    r = 0.10
    rounds = 12
    injection = 1000.0
    # New loan created each round: 1000*(1-r)^k for k=0..; deposits added each
    # round = the loan of the previous round. We plot the LOAN created per round.
    loans = injection * (1 - r) ** np.arange(rounds)      # 900? -> actually round0 deposit=1000
    # Round 0: deposit 1000, lends 900. Show deposits created per round:
    deposits = injection * (1 - r) ** np.arange(rounds)   # 1000, 900, 810, ...
    cumulative = np.cumsum(deposits)
    total = injection / r

    fig, ax = plt.subplots(figsize=(10.0, 5.4))
    xs = np.arange(rounds)
    ax.bar(xs, deposits, 0.62, color=C_DEP, label="New deposit each round")
    ax2 = ax.twinx()
    ax2.plot(xs, cumulative, color=C_BASE, lw=2.6, marker="o", ms=4,
             label="Cumulative deposits")
    ax2.axhline(total, color=GREY, ls="--", lw=1.5)
    ax2.text(rounds - 1, total - 700, f"total → 1000/r = {total:,.0f}",
             ha="right", va="top", fontsize=9.5, color=GREY, fontweight="bold")

    ax.set_xlabel("Lending round  (deposit → keep 10% → lend the rest → redeposit)")
    ax.set_ylabel("New deposit created this round", color=C_DEP)
    ax.tick_params(axis="y", labelcolor=C_DEP)
    ax2.set_ylabel("Cumulative deposits", color=C_BASE)
    ax2.tick_params(axis="y", labelcolor=C_BASE)
    ax.set_title("The textbook money multiplier (r = 10%): a geometric cascade")
    ax.set_xticks(xs)
    ax.set_ylim(0, 1100)
    ax2.set_ylim(0, 11000)

    lines1, labs1 = ax.get_legend_handles_labels()
    lines2, labs2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labs1 + labs2, loc="center right", fontsize=9,
              frameon=True, framealpha=0.95)
    ax.spines[["top"]].set_visible(False)
    ax2.spines[["top"]].set_visible(False)
    save(fig, 2)


# ---------------------------------------------------------------------------
# Fig 3 — Loans create deposits. A single bank's balance sheet BEFORE and AFTER
#   making a new loan: both the ASSET side and the LIABILITY side grow by the
#   loan amount SIMULTANEOUSLY. New money (the deposit) is created at the moment
#   the loan is recorded — not transferred from anywhere.
# ---------------------------------------------------------------------------
def fig3():
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(11.0, 5.2), sharey=True)

    reserves = 100.0
    dep0 = 100.0
    loan = 500.0

    def panel(ax, title, dep, loan_amt):
        # Assets column at x=0, Liabilities column at x=1.
        wA = 0.5
        # Assets: reserves (bottom) + loans (on top)
        ax.bar(0, reserves, wA, color=C_RES, label="Reserves (asset)")
        if loan_amt > 0:
            ax.bar(0, loan_amt, wA, bottom=reserves, color=C_LOAN,
                   label="Loan to borrower (asset)")
        # Liabilities: deposits
        ax.bar(1, dep, wA, color=C_DEP, label="Deposits (liability)")
        ax.set_xticks([0, 1])
        ax.set_xticklabels(["Assets", "Liabilities"])
        ax.set_title(title, fontsize=11.5)
        ax.set_xlim(-0.6, 1.6)
        ax.spines[["top", "right"]].set_visible(False)
        # value labels
        ax.text(0, reserves / 2, f"{reserves:.0f}", ha="center", va="center",
                fontsize=9, color="white", fontweight="bold")
        if loan_amt > 0:
            ax.text(0, reserves + loan_amt / 2, f"loan\n{loan_amt:.0f}", ha="center",
                    va="center", fontsize=9, color="white", fontweight="bold")
        ax.text(1, dep / 2, f"deposits\n{dep:.0f}", ha="center", va="center",
                fontsize=9, color="white", fontweight="bold")

    panel(axL, "BEFORE the loan", dep0, 0.0)
    panel(axR, "AFTER a new 500 loan", dep0 + loan, loan)

    # Emphasize simultaneous expansion — placed in the empty central gap
    # between the two bars so it never collides with the legend.
    axR.text(0.5, 330, "both sides\ngrow by 500\ntogether\n→ new money\nCREATED\n(not moved\nfrom anywhere)",
             ha="center", va="center", fontsize=9, fontweight="bold", color=C_BASE)
    axR.annotate("", xy=(0.0, reserves + loan + 15), xytext=(0.0, reserves + 15),
                 arrowprops=dict(arrowstyle="->", color=C_LOAN, lw=2))
    axR.annotate("", xy=(1.0, dep0 + loan + 15), xytext=(1.0, dep0 + 15),
                 arrowprops=dict(arrowstyle="->", color=C_DEP, lw=2))

    axL.set_ylabel("Balance ($)")
    axL.set_ylim(0, 680)
    handles, labels = axR.get_legend_handles_labels()
    axR.legend(handles, labels, loc="upper right", fontsize=8.4, frameon=True,
               framealpha=0.95)
    fig.suptitle("Loans create deposits: a double-entry keystroke, not a transfer",
                 fontsize=13)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    save(fig, 3)


# ---------------------------------------------------------------------------
# Fig 4 — The "money multiplier" ratio M2 / monetary base over time. It drifted
#   around 8-12 for decades, then COLLAPSED after 2008 QE (base ballooned, M2
#   didn't follow) and again in 2020. Illustrative shape matching FRED
#   M2SL / BOGMBASE. This is the empirical case against the mechanical
#   multiplier and for endogenous money (§4b).
# ---------------------------------------------------------------------------
def fig4():
    years = np.array([1985, 1990, 1995, 2000, 2005, 2007, 2008, 2009, 2010,
                      2012, 2014, 2016, 2018, 2019, 2020, 2021, 2022, 2024])
    # Approximate M2/base ratio (illustrative, matches the published shape).
    ratio = np.array([9.5, 10.2, 11.0, 11.6, 9.8, 9.2, 5.2, 4.1, 3.7,
                      3.4, 3.1, 3.3, 3.6, 3.9, 2.9, 2.8, 3.2, 3.7])

    fig, ax = plt.subplots(figsize=(10.2, 5.2))
    ax.plot(years, ratio, color=C_DEP, lw=2.6, marker="o", ms=4)

    # Mark the 2008 QE collapse.
    ax.axvspan(2008, 2009, color=C_BASE, alpha=0.12)
    ax.annotate("2008 QE:\nbase balloons,\nM2 doesn't follow\n→ ratio COLLAPSES",
                xy=(2008.5, 5.0), xytext=(2010.5, 8.5), fontsize=9,
                color=C_BASE, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=C_BASE, lw=1.6))
    ax.axvspan(2020, 2021, color=C_BASE, alpha=0.12)
    ax.annotate("2020 QE", xy=(2020.5, 2.9), xytext=(2016.5, 1.8), fontsize=8.6,
                color=C_BASE, arrowprops=dict(arrowstyle="->", color=C_BASE, lw=1.2))

    ax.text(1993, 12.0, "If the multiplier were a real, stable\nmechanism, this line would be FLAT.",
            fontsize=9, color=GREY, style="italic")

    ax.set_xlabel("Year")
    ax.set_ylabel("Money multiplier ratio  (M2 / monetary base)")
    ax.set_title("The 'money multiplier' is not a constant — it collapsed after 2008")
    ax.set_ylim(0, 13)
    ax.set_xlim(1984, 2025)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.25)
    save(fig, 4)


if __name__ == "__main__":
    fig1(); fig2(); fig3(); fig4()
    print("done")
