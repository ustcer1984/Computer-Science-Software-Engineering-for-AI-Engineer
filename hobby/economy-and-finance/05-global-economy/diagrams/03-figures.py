#!/usr/bin/env python3
"""Figures for Econ E05 §3 — Capital flows, crises & globalization.

Editable source of truth for the committed SVGs (see agent-docs/diagrams.md).
Numbers are illustrative but chosen to match the real shape of the pictures:

  fig1 — THE SUDDEN STOP: net private capital flows to the Asia-5 (Thailand, Indonesia,
         Korea, Malaysia, Philippines) surge through the mid-1990s and then REVERSE
         violently in 1997-98 — a swing of over 100bn USD, roughly a tenth of their
         combined GDP. Because CA + KA = 0 (§2), the current account had to adjust just
         as violently.
  fig2 — THE DAMAGE, AND THE OUTLIER: currencies against the USD, indexed to 100 in
         June 1997. The rupiah loses ~85%, the baht and won roughly half — while the
         Singapore dollar gives up only ~15%, the control case for §6.
  fig3 — THE 'NEVER AGAIN' REACTION: emerging-Asia FX reserves explode after 1997 as
         self-insurance — which is also the counterpart of the US deficit (E04 §3).
  fig4 — THREE GENERATIONS OF CRISIS MODELS: first (bad fundamentals, a deserved
         attack), second (self-fulfilling, multiple equilibria), third (balance sheets
         and contractionary devaluation) — the analytical spine of §3.
"""
import os
import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt
import numpy as np

OUT = os.path.dirname(os.path.abspath(__file__))
BASE = "03-capital-flows-and-crises"

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


def fig1():
    yrs = [1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000]
    flows = [25, 30, 30, 33, 36, 74, 93, -12, -45, -25, -20]
    colors = [C1 if v >= 0 else C2 for v in flows]

    fig, ax = plt.subplots(figsize=(11.0, 6.0))
    ax.bar(yrs, flows, color=colors, width=0.62)
    ax.axhline(0, color="black", lw=1.1)
    for y, v in zip(yrs, flows):
        ax.text(y, v + (3 if v >= 0 else -6), f"{v:+d}", ha="center", fontsize=8.6,
                fontweight="bold", color=(C1 if v >= 0 else C2))

    ax.annotate("THE SUDDEN STOP\n1996 → 1997: a swing of over 105bn USD\n"
                "(about a tenth of their combined GDP) in ONE year",
                xy=(1997, -12), xytext=(1991.4, -33), fontsize=9, color=C2, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=C2, lw=1.3))
    ax.text(1992.2, 88, "the 'bonanza': capital floods IN\nduring the boom (and makes it bigger)",
            fontsize=8.6, color=C1, ha="center")

    ax.set_xlabel("Year")
    ax.set_ylabel("Net private capital flows (billion USD)")
    ax.set_title("The sudden stop: capital to the Asia-5 reversed violently in 1997")
    ax.set_ylim(-60, 105)
    ax.grid(axis="y", alpha=0.25)
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, 1)


def fig2():
    q = ["Jun 97", "Sep 97", "Dec 97", "Mar 98", "Jun 98", "Sep 98", "Dec 98"]
    x = np.arange(len(q))
    series = {
        "Indonesia (rupiah)": ([100, 72, 45, 22, 15, 20, 24], C2),
        "Thailand (baht)":    ([100, 72, 55, 52, 58, 60, 62], C4),
        "Korea (won)":        ([100, 90, 52, 60, 65, 68, 70], C5),
        "Malaysia (ringgit)": ([100, 80, 68, 63, 62, 65, 66], GREY),
        "Singapore (SGD)":    ([100, 93, 85, 83, 82, 84, 85], C3),
    }
    fig, ax = plt.subplots(figsize=(11.0, 6.2))
    for name, (vals, c) in series.items():
        lw = 3.0 if "Singapore" in name else 2.2
        ax.plot(x, vals, color=c, lw=lw, marker="o", ms=4, label=name)

    ax.axhline(100, color="black", lw=1.0, ls=":")
    ax.annotate("the rupiah loses ~85%\n(balance sheets destroyed:\nUSD debt, rupiah income)",
                xy=(4, 15), xytext=(0.12, 31), fontsize=8.5, color=C2, fontweight="bold", ha="left",
                arrowprops=dict(arrowstyle="->", color=C2, lw=1.2))
    ax.annotate("Singapore gives up only ~15%\n— the CONTROL CASE (§6)",
                xy=(6, 85), xytext=(4.15, 97), fontsize=8.8, color=C3, fontweight="bold", ha="left",
                arrowprops=dict(arrowstyle="->", color=C3, lw=1.3))

    ax.set_xticks(x); ax.set_xticklabels(q, fontsize=9.5)
    ax.set_ylabel("Currency vs USD (index, June 1997 = 100)")
    ax.set_title("The damage, and the outlier: Asian currencies in the 1997–98 crisis")
    ax.set_ylim(0, 112)
    ax.legend(fontsize=9, loc="lower right")
    ax.grid(alpha=0.25)
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, 2)


def fig3():
    yrs = [1995, 2000, 2005, 2010, 2015, 2020, 2025]
    res = [0.25, 0.5, 1.5, 3.2, 4.5, 5.2, 5.8]
    fig, ax = plt.subplots(figsize=(10.6, 6.0))
    ax.fill_between(yrs, res, color=C1, alpha=0.20)
    ax.plot(yrs, res, color=C1, lw=2.8, marker="o", ms=5)
    for y, v in zip(yrs, res):
        ax.text(y, v + 0.16, f"{v:.1f}", ha="center", fontsize=9, fontweight="bold", color=C1)

    ax.axvline(1997.5, color=C2, ls="--", lw=1.4)
    ax.text(1998.0, 6.05, "1997 crisis", color=C2, fontsize=9, fontweight="bold")
    ax.annotate("the 'NEVER AGAIN' reaction:\nself-insurance by hoarding reserves\n"
                "(costly — low-yielding + sterilization, E03 §5)",
                xy=(2010, 3.2), xytext=(1999.0, 4.25), fontsize=8.8, color=GREY, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=GREY, lw=1.2))
    ax.text(2016.5, 1.0, "…and the counterpart of the\nUS deficit (E04 §3 §10c)",
            fontsize=8.5, color=GREY, style="italic", ha="center")

    ax.set_xlabel("Year")
    ax.set_ylabel("Emerging-Asia FX reserves (trillion USD)")
    ax.set_title("The aftermath: reserve accumulation as self-insurance against the next sudden stop")
    ax.set_ylim(0, 6.6)
    ax.grid(alpha=0.25)
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, 3)


def fig4():
    fig, ax = plt.subplots(figsize=(12.0, 4.6))
    ax.set_xlim(0, 3); ax.set_ylim(0, 1)
    panels = [
        (0, "FIRST GENERATION\n(Krugman 1979)", C1,
         "TRIGGER: bad fundamentals\nfixed peg + unsustainable deficits\n→ reserves drain predictably\n"
         "→ speculators attack when\nreserves hit the threshold\n\nThe crisis is DESERVED.\nLatin America, 1980s"),
        (1, "SECOND GENERATION\n(Obstfeld)", C4,
         "TRIGGER: expectations\nthe government CHOOSES: defend\n(high rates = recession) or exit\nif markets expect exit, defending\n"
         "costs more → exit becomes optimal\n\nSELF-FULFILLING; multiple\nequilibria. The crisis need NOT\nbe deserved. ERM 1992"),
        (2, "THIRD GENERATION\n(post-1997)", C2,
         "TRIGGER: balance sheets\ncurrency + maturity MISMATCH\n(borrow short in USD, earn local)\n→ devaluation DESTROYS balance\n"
         "sheets → contractionary\ndevaluation, twin banking crisis\n\nThe ER is an AMPLIFIER.\nAsia 1997"),
    ]
    for cx, title, colr, body in panels:
        ax.add_patch(plt.Rectangle((cx + 0.03, 0.03), 0.94, 0.94, facecolor=colr,
                                   alpha=0.10, edgecolor=colr, lw=1.6))
        ax.text(cx + 0.5, 0.90, title, ha="center", va="top", fontsize=10.5,
                fontweight="bold", color=colr)
        ax.text(cx + 0.5, 0.70, body, ha="center", va="top", fontsize=8.4, color=GREY)

    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_title("Three generations of currency-crisis models — modern crises usually mix all three",
                 fontsize=12.5)
    save(fig, 4)


if __name__ == "__main__":
    fig1(); fig2(); fig3(); fig4()
    print("done")
