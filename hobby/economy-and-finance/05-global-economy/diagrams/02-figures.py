#!/usr/bin/env python3
"""Figures for Econ E05 §2 — Exchange rates & the balance of payments.

Editable source of truth for the committed SVGs (see agent-docs/diagrams.md).
Numbers are illustrative but chosen to match the real shape of the pictures:

  fig1 — PPP ANCHORS THE LONG RUN, NOT THE SHORT RUN: the US real effective exchange
         rate swings widely for years around its long-run average — the market rate
         can deviate far from "fair value" for a decade, so purchasing-power parity
         explains trends over decades, not months.
  fig2 — THE BALANCE OF PAYMENTS SUMS TO ZERO: for each country the current account
         (CA) and the capital/financial account (KA) are equal and opposite — a
         current-account DEFICIT is exactly financed by a capital-account SURPLUS
         (the "capital inflow IS the trade deficit" identity from E04 §3).
  fig3 — THE J-CURVE: after a currency depreciates, the trade balance first WORSENS
         (import prices jump before volumes adjust) and only later IMPROVES — so the
         exchange rate fixes the trade balance slowly, and only if it changes S − I.
  fig4 — MUNDELL-FLEMING: which policy lever works depends on the regime. Under mobile
         capital, a FLOATING rate makes monetary policy powerful and fiscal policy weak
         (crowded out through the exchange rate); a FIXED rate reverses it.

Run with the project venv:

    .venv/bin/python hobby/economy-and-finance/05-global-economy/diagrams/02-figures.py

Outputs 02-exchange-rates-and-balance-of-payments-figN.svg into this folder.
"""
import os
import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt
import numpy as np

OUT = os.path.dirname(os.path.abspath(__file__))
BASE = "02-exchange-rates-and-balance-of-payments"

plt.rcParams.update({
    "font.size": 12,
    "axes.titlesize": 13,
    "axes.labelsize": 12,
    "svg.fonttype": "none",
    "figure.dpi": 100,
    "text.parse_math": False,
})

C1 = "#1f77b4"; C2 = "#d62728"; C3 = "#2ca02c"; C4 = "#ff7f0e"; C5 = "#9467bd"
GREY = "#555555"


def save(fig, n):
    path = os.path.join(OUT, f"{BASE}-fig{n}.svg")
    fig.savefig(path, format="svg", bbox_inches="tight")
    plt.close(fig)
    print("wrote", path)


# ---------------------------------------------------------------------------
# Fig 1 — PPP anchors the long run, not the short run (US real eff. exch. rate).
# ---------------------------------------------------------------------------
def fig1():
    yrs = [1980, 1982, 1985, 1988, 1990, 1995, 2000, 2002, 2005, 2008, 2011,
           2014, 2016, 2019, 2020, 2022, 2024]
    reer = [95, 118, 143, 100, 92, 90, 115, 129, 108, 96, 96,
            103, 118, 116, 113, 128, 121]
    anchor = 108  # long-run average ~ the slow PPP-style anchor

    fig, ax = plt.subplots(figsize=(11.0, 6.0))
    ax.plot(yrs, reer, color=C1, lw=2.6, marker="o", ms=3.5,
            label="US real effective exchange rate (index)")
    ax.axhline(anchor, color=GREY, lw=1.8, ls="--",
               label="long-run average (~ PPP 'fair value' anchor)")
    ax.fill_between(yrs, reer, anchor, where=[r >= anchor for r in reer],
                    color=C2, alpha=0.10, interpolate=True)
    ax.fill_between(yrs, reer, anchor, where=[r <= anchor for r in reer],
                    color=C3, alpha=0.10, interpolate=True)

    ax.annotate("1985 Plaza peak\n(strong dollar)", xy=(1985, 143), xytext=(1987, 138),
                fontsize=8.6, color=C2, arrowprops=dict(arrowstyle="->", color=C2, lw=1.1))
    ax.annotate("2002 peak", xy=(2002, 129), xytext=(2003.5, 137),
                fontsize=8.6, color=C2, arrowprops=dict(arrowstyle="->", color=C2, lw=1.1))
    ax.text(1996, 82, "deviations of ±30% can last a DECADE\n→ PPP anchors the long run, not the short run",
            fontsize=9, color=GREY, fontweight="bold", ha="center")

    ax.set_xlabel("Year")
    ax.set_ylabel("Real effective exchange rate (index, ~108 = average)")
    ax.set_title("What moves a currency (1): PPP is a weak short-run anchor, a strong long-run one")
    ax.set_ylim(78, 150)
    ax.legend(fontsize=9.5, loc="upper right")
    ax.grid(alpha=0.25)
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, 1)


# ---------------------------------------------------------------------------
# Fig 2 — The balance of payments sums to zero (CA + KA = 0).
# ---------------------------------------------------------------------------
def fig2():
    countries = ["USA", "United Kingdom", "China", "Germany"]
    ca = [-3.0, -3.5, 2.2, 6.5]        # current account, % of GDP
    ka = [-x for x in ca]              # capital/financial account = mirror image

    y = np.arange(len(countries))
    fig, ax = plt.subplots(figsize=(10.6, 6.0))
    ax.barh(y - 0.2, ca, height=0.38, color=C1, label="Current account (trade + income), % of GDP")
    ax.barh(y + 0.2, ka, height=0.38, color=C4, label="Capital / financial account, % of GDP")
    ax.axvline(0, color="black", lw=1.1)

    for yi, (c, k) in enumerate(zip(ca, ka)):
        ax.text(c + (0.25 if c >= 0 else -0.25), yi - 0.2, f"{c:+.1f}", va="center",
                ha="left" if c >= 0 else "right", fontsize=9, fontweight="bold", color=C1)
        ax.text(k + (0.25 if k >= 0 else -0.25), yi + 0.2, f"{k:+.1f}", va="center",
                ha="left" if k >= 0 else "right", fontsize=9, fontweight="bold", color=C4)

    ax.set_yticks(y); ax.set_yticklabels(countries, fontsize=10.5)
    ax.set_xlabel("% of GDP")
    ax.set_title("The balance of payments sums to zero: a trade deficit IS a capital-account surplus")
    ax.set_xlim(-8, 8)
    ax.legend(fontsize=9, loc="lower right")
    ax.grid(axis="x", alpha=0.25)
    ax.spines[["top", "right"]].set_visible(False)
    ax.text(-7.8, 1.5, "CA + KA = 0 for every country:\nthe deficit countries (US/UK) IMPORT capital;\n"
            "the surplus countries (China/Germany) EXPORT it",
            fontsize=8.6, color=GREY, va="center", ha="left",
            bbox=dict(boxstyle="round,pad=0.35", fc="white", ec=GREY, lw=1.0))
    save(fig, 2)


# ---------------------------------------------------------------------------
# Fig 3 — The J-curve.
# ---------------------------------------------------------------------------
def fig3():
    t = np.linspace(0, 12, 400)          # quarters after the depreciation
    # a stylized J: quick dip, slow recovery above zero
    tb = -1.6 * np.exp(-t / 1.6) * (1 - np.exp(-t / 0.4)) + 0.9 * (1 - np.exp(-t / 3.2))
    tb = tb - tb[0]

    fig, ax = plt.subplots(figsize=(10.4, 6.0))
    ax.plot(t, tb, color=C1, lw=2.8)
    ax.axhline(0, color="black", lw=1.0)
    ax.axvline(0, color=GREY, lw=1.4, ls=":")
    ax.text(0.15, ax.get_ylim()[1] if False else 0.78, "depreciation\nhappens here", fontsize=8.6,
            color=GREY, va="top")

    # shade the worse-then-better phases
    ax.fill_between(t, tb, 0, where=(tb < 0), color=C2, alpha=0.12)
    ax.fill_between(t, tb, 0, where=(tb >= 0), color=C3, alpha=0.12)

    ax.annotate("PHASE 1: WORSENS\nimport prices jump now,\nbut volumes are still stuck\n(contracts, habits, supply chains)",
                xy=(1.4, -0.95), xytext=(2.2, -0.75), fontsize=8.5, color=C2, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=C2, lw=1.1))
    ax.annotate("PHASE 2: IMPROVES\nexports cheaper + imports dearer\n→ volumes finally adjust",
                xy=(8.5, 0.62), xytext=(5.6, 0.15), fontsize=8.5, color=C3, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=C3, lw=1.1))

    ax.set_xlabel("Time after the depreciation (quarters)")
    ax.set_ylabel("Trade balance (change from before)")
    ax.set_title("The J-curve: a weaker currency worsens the trade balance BEFORE it improves it")
    ax.set_xlim(-0.4, 12)
    ax.set_ylim(-1.3, 1.05)
    ax.grid(alpha=0.22)
    ax.spines[["top", "right"]].set_visible(False)
    ax.text(11.8, -1.18, "…and only lastingly if it shifts S − I (E04 §3)", fontsize=8.2,
            color=GREY, ha="right", style="italic")
    save(fig, 3)


# ---------------------------------------------------------------------------
# Fig 4 — Mundell-Fleming: which lever works, by regime (mobile capital).
# ---------------------------------------------------------------------------
def fig4():
    fig, ax = plt.subplots(figsize=(10.4, 6.4))
    ax.set_xlim(0, 2); ax.set_ylim(0, 2)

    cells = {
        # (col, row): (text, effective?)
        (0, 1): ("MONETARY policy\nPOWERFUL\ncut → capital out → currency\ndepreciates → net exports up\n(reinforces)", True),
        (1, 1): ("FISCAL policy\nWEAK\nspend → rates up → capital in →\ncurrency up → net exports down\n(crowded out via the exch. rate)", False),
        (0, 0): ("MONETARY policy\nIMPOTENT\nrates are pinned to defend\nthe peg — no autonomy left", False),
        (1, 0): ("FISCAL policy\nPOWERFUL\nspend → rates up → CB prints to\nhold the peg → no crowding-out", True),
    }
    for (cx, ry), (txt, ok) in cells.items():
        ax.add_patch(plt.Rectangle((cx, ry), 1, 1, facecolor=(C3 if ok else C2),
                                   alpha=0.13, edgecolor="black", lw=1.2))
        ax.text(cx + 0.5, ry + 0.5, txt, ha="center", va="center", fontsize=8.7,
                color=(C3 if ok else C2), fontweight="bold")

    ax.set_xticks([0.5, 1.5]); ax.set_xticklabels(["MONETARY policy", "FISCAL policy"], fontsize=11)
    ax.set_yticks([0.5, 1.5]); ax.set_yticklabels(["FIXED\nrate", "FLOATING\nrate"], fontsize=11)
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_title("Mundell–Fleming (mobile capital): the regime decides which lever works",
                 fontsize=12.5)
    ax.text(1.0, -0.22, "the FLOATING row is the engine behind E04 §3 §10's US: fiscal expansion → strong dollar → "
            "wider trade deficit",
            ha="center", fontsize=8.5, color=GREY)
    save(fig, 4)


if __name__ == "__main__":
    fig1(); fig2(); fig3(); fig4()
    print("done")
