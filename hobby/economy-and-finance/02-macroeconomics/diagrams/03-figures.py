#!/usr/bin/env python3
"""Figures for Econ E02 §3 — Unemployment & the labour market.

Editable source of truth for the committed SVGs (see agent-docs/diagrams.md:
commit the rendered image, keep the source beside it). Numbers are illustrative
but chosen to match the *real shape* of the published data (the labour-force
partition, a stylized unemployment+participation series through 2008-09 and
2020, the Okun's-law scatter, and the U-3-vs-U-6 slack gap). The point is the
structure a reader should carry, not exact figures. Run with the project venv:

    .venv/bin/python hobby/economy-and-finance/02-macroeconomics/diagrams/03-figures.py

Outputs 03-unemployment-and-labour-market-figN.svg into this folder.
"""
import os
import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt
import numpy as np

OUT = os.path.dirname(os.path.abspath(__file__))
BASE = "03-unemployment-and-labour-market"

plt.rcParams.update({
    "font.size": 12,
    "axes.titlesize": 13,
    "axes.labelsize": 12,
    "svg.fonttype": "none",   # keep text as text (smaller, selectable)
    "figure.dpi": 100,
})

C_EMP = "#2ca02c"    # employed / green
C_UNE = "#d62728"    # unemployed / red
C_NILF = "#9aa0a6"   # not in labour force / grey
C_BLUE = "#1f77b4"
C_ORANGE = "#ff7f0e"
GREY = "#555555"


def save(fig, n):
    path = os.path.join(OUT, f"{BASE}-fig{n}.svg")
    fig.savefig(path, format="svg", bbox_inches="tight")
    plt.close(fig)
    print("wrote", path)


# ---------------------------------------------------------------------------
# Fig 1 — The labour-force accounting: how the working-age population splits,
#   and which slices the two headline ratios are built from.
# ---------------------------------------------------------------------------
def fig1():
    fig, ax = plt.subplots(figsize=(10.0, 3.6))
    # Shares of the working-age (15+) population — illustrative, realistic.
    emp, une, nilf = 62.0, 3.3, 34.7          # sum = 100
    lf = emp + une                             # labour force = 65.3
    u_rate = une / lf * 100                     # ~5.05%
    part = lf                                   # participation = LF / pop = 65.3%

    ax.barh(0, emp, color=C_EMP, height=0.5)
    ax.barh(0, une, left=emp, color=C_UNE, height=0.5)
    ax.barh(0, nilf, left=emp + une, color=C_NILF, height=0.5)

    ax.text(emp/2, 0, f"Employed\n{emp:.0f}%", ha="center", va="center",
            color="white", fontsize=10, fontweight="bold")
    ax.text(emp + une/2, 0.55, f"Unemployed {une:.1f}%", ha="center", va="bottom",
            color=C_UNE, fontsize=9, fontweight="bold")
    ax.annotate("", xy=(emp, 0.30), xytext=(emp + une, 0.30),
                arrowprops=dict(arrowstyle="-", color=C_UNE, lw=0.8))
    ax.text(emp + une + nilf/2, 0, f"Not in the labour force\n{nilf:.0f}%",
            ha="center", va="center", color="white", fontsize=10, fontweight="bold")

    # Bracket the labour force (employed + unemployed).
    ax.plot([0, lf], [-0.45, -0.45], color="black", lw=1.0)
    ax.plot([0, 0], [-0.40, -0.45], color="black", lw=1.0)
    ax.plot([lf, lf], [-0.40, -0.45], color="black", lw=1.0)
    ax.text(lf/2, -0.62, f"LABOUR FORCE = employed + unemployed = {lf:.1f}%  of working-age pop",
            ha="center", va="top", fontsize=9.5, color="black")

    ax.set_xlim(0, 100)
    ax.set_ylim(-1.05, 1.0)
    ax.set_yticks([])
    ax.set_xlabel("Share of the working-age (15+) population (%)   —   illustrative")
    ax.set_title("The labour-force accounting — and the two ratios it feeds", pad=52)
    ax.spines[["top", "right", "left"]].set_visible(False)

    ax.text(0.5, 1.04,
            f"Unemployment rate = unemployed / LABOUR FORCE = {une:.1f}/{lf:.1f} = {u_rate:.1f}%\n"
            f"Participation rate = LABOUR FORCE / working-age pop = {part:.1f}%",
            transform=ax.transAxes, ha="center", va="bottom", fontsize=9.5,
            color="#08519c", linespacing=1.5,
            bbox=dict(boxstyle="round,pad=0.4", fc="#eaf2fb", ec="#9ec3e6"))
    save(fig, 1)


# ---------------------------------------------------------------------------
# Fig 2 — Why you must watch participation too. The unemployment rate (left
#   axis) spikes in recessions; the participation rate (right axis) drifts and
#   dips — and a falling rate can flatter the headline (discouraged workers
#   leave the labour force, so they stop being counted as "unemployed").
# ---------------------------------------------------------------------------
def fig2():
    years = np.arange(2005, 2025)
    # Stylized US-shaped series (illustrative): GFC spike, long recovery, COVID.
    unemp = np.array([5.1, 4.6, 4.6, 5.8, 9.3, 9.6, 8.9, 8.1, 7.4, 6.2,
                      5.3, 4.9, 4.4, 3.9, 3.7, 8.1, 5.4, 3.6, 3.6, 4.0])
    part = np.array([66.0, 66.2, 66.0, 65.8, 65.4, 64.7, 64.1, 63.7, 63.2, 62.9,
                     62.7, 62.8, 62.9, 62.9, 63.1, 61.8, 61.7, 62.2, 62.6, 62.7])

    fig, ax1 = plt.subplots(figsize=(10.2, 4.9))
    ax1.bar(years, unemp, color=C_UNE, width=0.6, alpha=0.85,
            label="Unemployment rate (left)")
    ax1.axhline(4.5, color=GREY, ls="--", lw=1.2)
    ax1.text(2005.2, 4.65, "≈ natural rate (~4.5%)", color=GREY, fontsize=8.5)
    ax1.set_ylabel("Unemployment rate (%)", color=C_UNE)
    ax1.tick_params(axis="y", labelcolor=C_UNE)
    ax1.set_ylim(0, 11)
    ax1.spines[["top"]].set_visible(False)

    ax2 = ax1.twinx()
    ax2.plot(years, part, color=C_BLUE, lw=2.6, marker="o", ms=3.5,
             label="Participation rate (right)")
    ax2.set_ylabel("Labour-force participation rate (%)", color=C_BLUE)
    ax2.tick_params(axis="y", labelcolor=C_BLUE)
    ax2.set_ylim(60, 67)
    ax2.spines[["top"]].set_visible(False)

    ax1.annotate("GFC", xy=(2010, 9.6), xytext=(2010, 10.4),
                 ha="center", fontsize=9, color=C_UNE)
    ax1.annotate("COVID", xy=(2020, 8.1), xytext=(2020, 9.6),
                 ha="center", fontsize=9, color=C_UNE)
    ax2.annotate("participation slides as boomers retire\n& discouraged workers exit",
                 xy=(2015, 62.7), xytext=(2012.0, 61.0),
                 fontsize=8.5, color=C_BLUE,
                 arrowprops=dict(arrowstyle="->", color=C_BLUE))
    ax1.set_title("Two gauges, not one: unemployment rate vs participation")
    save(fig, 2)


# ---------------------------------------------------------------------------
# Fig 4 (defined here, saved as fig4) — Okun's law: faster real GDP growth ⇒
#   falling unemployment. The link back to E02 §1 §9d (output gap ↔ unemployment
#   gap). Scatter + fitted line. Appears LAST in the doc as the GDP bridge.
# ---------------------------------------------------------------------------
def fig3():
    # Generate points along Okun's relation with noise (deterministic — no RNG).
    g = np.array([-2.5, -0.2, 1.0, 1.6, 2.0, 2.2, 2.5, 2.9, 3.0, 3.3,
                  3.6, 4.0, 4.2, -3.5, 5.8, 2.7, 1.4, 3.1, 2.4, 0.6])
    # Okun: Δu ≈ -0.5 (g - g_potential), g_potential ≈ 2.0; add small wobble.
    wobble = np.array([0.3, -0.2, 0.1, -0.3, 0.2, -0.1, 0.0, 0.2, -0.2, 0.1,
                       -0.1, 0.2, -0.2, 0.4, -0.3, 0.1, -0.2, 0.0, 0.1, -0.1])
    du = -0.5 * (g - 2.0) + wobble

    fig, ax = plt.subplots(figsize=(8.6, 5.0))
    ax.scatter(g, du, s=46, color=C_BLUE, zorder=3, edgecolor="white", lw=0.5)
    xs = np.linspace(g.min() - 0.4, g.max() + 0.4, 50)
    ax.plot(xs, -0.5 * (xs - 2.0), color=C_UNE, lw=2.2,
            label="Okun's law:  Δu ≈ −0.5 (g − 2%)")
    ax.axhline(0, color="black", lw=0.8)
    ax.axvline(2.0, color=GREY, ls=":", lw=1.2)
    ax.text(2.08, ax.get_ylim()[1]*0.78, "potential\ngrowth ≈ 2%",
            fontsize=8.5, color=GREY)

    ax.annotate("growth above potential\n→ unemployment FALLS",
                xy=(4.0, -1.0), xytext=(3.1, -1.9),
                fontsize=8.8, color="#196619",
                arrowprops=dict(arrowstyle="->", color=GREY))
    ax.annotate("recession\n→ unemployment RISES",
                xy=(-2.5, 2.25), xytext=(-2.2, 1.0),
                fontsize=8.8, color="#a63603",
                arrowprops=dict(arrowstyle="->", color=GREY))
    ax.set_xlabel("Real GDP growth, g (% per year)")
    ax.set_ylabel("Change in unemployment rate, Δu (pp)")
    ax.set_title("Okun's law: the bridge from GDP (§1) to jobs")
    ax.legend(loc="upper right", fontsize=9, frameon=True, framealpha=0.95)
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, 4)


# ---------------------------------------------------------------------------
# Fig 3 (defined here, saved as fig3) — Headline understates slack: U-3
#   (official) vs U-6 (adds discouraged, marginally attached, and involuntary
#   part-timers). The gap is the hidden slack, and it widens in downturns.
# ---------------------------------------------------------------------------
def fig4():
    years = np.arange(2005, 2025)
    u3 = np.array([5.1, 4.6, 4.6, 5.8, 9.3, 9.6, 8.9, 8.1, 7.4, 6.2,
                   5.3, 4.9, 4.4, 3.9, 3.7, 8.1, 5.4, 3.6, 3.6, 4.0])
    # U-6 runs well above U-3, gap widest in slumps (involuntary part-time spikes).
    gap = np.array([3.9, 3.7, 3.7, 4.6, 7.0, 7.4, 6.9, 6.4, 6.0, 5.4,
                    4.9, 4.7, 4.3, 3.9, 3.3, 5.9, 4.4, 3.2, 3.3, 3.5])
    u6 = u3 + gap

    fig, ax = plt.subplots(figsize=(10.2, 4.9))
    ax.plot(years, u6, color=C_ORANGE, lw=2.6, marker="s", ms=3.5,
            label="U-6 (broad: + discouraged, marginally attached, part-time-for-economic-reasons)")
    ax.plot(years, u3, color=C_UNE, lw=2.6, marker="o", ms=3.5,
            label="U-3 (official headline rate)")
    ax.fill_between(years, u3, u6, color="#fde3c8", alpha=0.7)
    ax.annotate("the gap = hidden slack\n(widest in downturns)",
                xy=(2010, (u3[5] + u6[5]) / 2), xytext=(2013.2, 14.0),
                fontsize=9, color="#a63603",
                arrowprops=dict(arrowstyle="->", color=GREY))
    ax.set_ylabel("Rate (%)")
    ax.set_ylim(0, 18)
    ax.set_title("The headline understates slack: U-3 vs U-6")
    ax.legend(loc="upper right", fontsize=8.2, frameon=True, framealpha=0.95)
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, 3)


if __name__ == "__main__":
    fig1(); fig2(); fig3(); fig4()
    print("done")
