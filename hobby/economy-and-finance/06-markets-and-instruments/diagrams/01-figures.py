#!/usr/bin/env python3
"""Figures for Econ E06 §1 — What financial markets are, who's in them, what they're for.

Editable source of truth for the committed SVGs (see agent-docs/diagrams.md).
Numbers are illustrative but chosen to match the real shape of the pictures:

  fig1 — PRIMARY vs SECONDARY, on a log scale. US equity PRIMARY issuance in 2025 was
         roughly 44bn USD of traditional IPOs plus follow-ons/converts (~175bn USD in
         total). US equity SECONDARY trading runs on the order of 100tn USD a year.
         The point of the picture: the market you read about every day is almost
         entirely the SECONDARY one, and it is ~500x larger than the capital-raising
         market it exists to serve.
  fig2 — THE SIZE OF THE POOLS: global equity market capitalisation (~158tn USD, 2025)
         vs global fixed income outstanding (~145tn USD) vs OTC derivatives. The
         derivatives bar is drawn twice on purpose — NOTIONAL (~700tn) next to GROSS
         MARKET VALUE (~20tn) — because the headline number everyone quotes is the one
         that is NOT money at risk.
  fig3 — THE LIMIT ORDER BOOK: resting bids below and asks above, the BID-ASK SPREAD in
         between, and what happens when a large market order 'walks the book'. This is
         what 'liquidity' concretely means and what it concretely costs.
  fig4 — BANK-BASED vs MARKET-BASED FINANCE: how non-financial companies fund themselves
         across economies. Shares are illustrative but the ordering and rough magnitudes
         are the standard picture — the US is the outlier, not the norm.
"""
import os
import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import NullFormatter

OUT = os.path.dirname(os.path.abspath(__file__))
BASE = "01-what-financial-markets-are"

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
    labels = ["PRIMARY\ntraditional IPOs\n(2025)",
              "PRIMARY\nall equity issuance\n(IPOs + follow-ons)",
              "SECONDARY\nequity trading\n(one year)"]
    vals = [44, 175, 100000]          # billion USD
    colors = [C3, C3, C1]

    fig, ax = plt.subplots(figsize=(11.0, 6.2))
    bars = ax.bar(labels, vals, color=colors, width=0.5)
    ax.set_yscale("log")
    ax.set_ylim(10, 1_500_000)
    ax.set_xlim(-0.6, 3.15)

    ax.set_yticks([10, 100, 1000, 10000, 100000, 1000000])
    ax.set_yticklabels(["10", "100", "1,000", "10,000", "100,000", "1,000,000"])
    ax.yaxis.set_minor_formatter(NullFormatter())

    for b, v in zip(bars, vals):
        txt = f"{v:,.0f}bn USD" if v < 1000 else f"{v/1000:,.0f}tn USD"
        ax.text(b.get_x() + b.get_width() / 2, v * 1.4, txt,
                ha="center", fontsize=10.5, fontweight="bold")

    ax.annotate("", xy=(2.6, 100000), xytext=(2.6, 175),
                arrowprops=dict(arrowstyle="<->", color=C2, lw=1.8))
    ax.text(2.72, 4000, "roughly\n500x", fontsize=11, color=C2,
            fontweight="bold", ha="left", va="center")

    ax.text(0.5, 3000, "money that actually reaches\nthe companies", ha="center",
            fontsize=9.4, color=C3, style="italic")
    ax.text(2.0, 600000, "money changing hands between investors\n"
            "— the issuer gets none of it", ha="center",
            fontsize=9.4, color=C1, style="italic")

    ax.set_ylabel("Billion USD (log scale)")
    ax.set_title("Primary vs secondary: almost everything you watch is the resale market")
    ax.grid(axis="y", alpha=0.25, which="major")
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, 1)


def fig2():
    fig, ax = plt.subplots(figsize=(11.0, 6.2))
    labels = ["Global equities\n(market cap)", "Global bonds\n(outstanding)",
              "OTC derivatives\nNOTIONAL", "OTC derivatives\nGROSS MARKET VALUE"]
    vals = [158, 145, 700, 20]
    colors = [C1, C4, GREY, C2]
    bars = ax.bar(labels, vals, color=colors, width=0.58)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 14, f"~{v}tn USD",
                ha="center", fontsize=10.6, fontweight="bold")

    bars[2].set_hatch("//")
    ax.annotate("the number everyone quotes —\nbut notional is the SIZE OF THE BET,\nnot money at risk",
                xy=(1.72, 690), xytext=(0.28, 470), fontsize=9.4, color=GREY, fontweight="bold",
                ha="left", arrowprops=dict(arrowstyle="->", color=GREY, lw=1.4))
    ax.annotate("what is ACTUALLY owed\nif every contract settled today\n— 35x smaller",
                xy=(2.72, 30), xytext=(2.34, 210), fontsize=9.4, color=C2, fontweight="bold",
                ha="left", arrowprops=dict(arrowstyle="->", color=C2, lw=1.4))
    ax.text(0.5, 205, "the two big pools of real claims\nare now roughly the same size",
            ha="center", fontsize=9.6, color=C1, style="italic")

    ax.set_ylabel("Trillion USD")
    ax.set_ylim(0, 830)
    ax.set_title("The size of the pools — and why the derivatives headline misleads")
    ax.grid(axis="y", alpha=0.25)
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, 2)


def fig3():
    bid_px = [99.94, 99.95, 99.96, 99.97, 99.98]
    bid_sz = [900, 700, 500, 400, 300]
    ask_px = [100.02, 100.03, 100.04, 100.05, 100.06]
    ask_sz = [250, 350, 450, 600, 800]

    fig, ax = plt.subplots(figsize=(11.0, 6.2))
    ax.barh(bid_px, bid_sz, height=0.008, color=C3, label="BIDS — buyers waiting")
    ax.barh(ask_px, [-s for s in ask_sz], height=0.008, color=C2, label="ASKS — sellers waiting")

    ax.axhline(99.98, color=C3, lw=1.2, ls="--")
    ax.axhline(100.02, color=C2, lw=1.2, ls="--")
    ax.axhspan(99.98, 100.02, color="#dddddd", alpha=0.55)
    ax.text(0, 100.0, "THE SPREAD  =  100.02 - 99.98  =  0.04\nthe round-trip cost of immediacy",
            ha="center", va="center", fontsize=10.2, fontweight="bold")

    ax.text(430, 99.9855, "best bid 99.98", fontsize=9.3, color=C3, fontweight="bold")
    ax.text(-1120, 100.0165, "best ask 100.02", fontsize=9.3, color=C2, fontweight="bold")
    ax.annotate("a BIG market order 'walks the book':\nit eats 100.02, then 100.03, then 100.04...\n"
                "= MARKET IMPACT, the real cost of size",
                xy=(-140, 100.0455), xytext=(95, 100.0635), fontsize=9.3, color=GREY,
                fontweight="bold", ha="left",
                arrowprops=dict(arrowstyle="->", color=GREY, lw=1.4))
    ax.text(-620, 99.940, "a DEEP book = a tight spread\n= a LIQUID market",
            fontsize=9.3, color=C1, style="italic", ha="center")

    ax.set_yticks([99.94, 99.96, 99.98, 100.00, 100.02, 100.04, 100.06])
    ax.set_yticklabels(["99.94", "99.96", "99.98", "100.00", "100.02", "100.04", "100.06"])
    ax.set_ylim(99.928, 100.075)
    ax.set_xlim(-1150, 1150)
    ax.set_xticks([-800, -400, 0, 400, 800])
    ax.set_xticklabels(["800", "400", "0", "400", "800"])
    ax.legend_ = None
    ax.set_xlabel("Shares resting at each price  (asks on the left, bids on the right)")
    ax.set_ylabel("Price (USD)")
    ax.set_title("What a market actually is: a limit order book, a spread, and depth")
    ax.legend(fontsize=9.5, loc="lower right")
    ax.grid(axis="x", alpha=0.2)
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, 3)


def fig4():
    econ = ["United States", "Japan", "Euro area", "China"]
    bank = [25, 58, 70, 85]
    mkt = [100 - b for b in bank]
    x = np.arange(len(econ))

    fig, ax = plt.subplots(figsize=(10.8, 6.0))
    ax.bar(x, bank, color=C4, width=0.55, label="Bank loans (intermediated)")
    ax.bar(x, mkt, bottom=bank, color=C1, width=0.55, label="Bonds + equity (market-based)")

    for i, (b, m) in enumerate(zip(bank, mkt)):
        ax.text(i, b / 2, f"{b}%", ha="center", va="center", fontsize=11,
                fontweight="bold", color="white")
        ax.text(i, b + m / 2, f"{m}%", ha="center", va="center", fontsize=11,
                fontweight="bold", color="white")

    ax.annotate("the US is the OUTLIER, not the norm —\nwhich is why US finance textbooks\n"
                "over-teach markets and under-teach banks",
xy=(0.05, 101), xytext=(-0.44, 108), fontsize=9.5, color=C1, fontweight="bold",
                ha="left", arrowprops=dict(arrowstyle="->", color=C1, lw=1.4))
    ax.text(2.55, -10, "bank-dominated: a credit squeeze\nhits the whole economy at once",
            ha="center", fontsize=9.2, color=C4, style="italic")

    ax.set_xticks(x); ax.set_xticklabels(econ, fontsize=11)
    ax.set_ylabel("Share of non-financial corporate external funding (%)")
    ax.set_ylim(-16, 138)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_title("Two ways to move savings to borrowers: through a bank, or through a market")
    ax.legend(fontsize=9.8, loc="upper right", ncol=1, framealpha=0.95)
    ax.grid(axis="y", alpha=0.25)
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, 4)


if __name__ == "__main__":
    fig1(); fig2(); fig3(); fig4()
    print("done")
