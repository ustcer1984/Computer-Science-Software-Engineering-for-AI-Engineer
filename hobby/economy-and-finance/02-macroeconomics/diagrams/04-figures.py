#!/usr/bin/env python3
"""Figures for Econ E02 §4 — The business cycle.

Editable source of truth for the committed SVGs (see agent-docs/diagrams.md:
commit the rendered image, keep the source beside it). Numbers are illustrative
but chosen to match the *real shape* of the textbook / published pictures (real
GDP wobbling around a rising potential trend; the AD-AS response to a demand vs
a supply shock; the expectations-augmented Phillips curve with a vertical
long-run leg at the natural rate; and the lead/coincident/lag timing of the
headline indicators around a recession). The point is the structure a reader
should carry, not exact figures. Run with the project venv:

    .venv/bin/python hobby/economy-and-finance/02-macroeconomics/diagrams/04-figures.py

Outputs 04-the-business-cycle-figN.svg into this folder.
"""
import os
import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt
import numpy as np

OUT = os.path.dirname(os.path.abspath(__file__))
BASE = "04-the-business-cycle"

plt.rcParams.update({
    "font.size": 12,
    "axes.titlesize": 13,
    "axes.labelsize": 12,
    "svg.fonttype": "none",   # keep text as text (smaller, selectable)
    "figure.dpi": 100,
})

C_ACT = "#1f77b4"    # actual output / blue
C_POT = "#555555"    # potential (trend) / grey
C_UNE = "#d62728"    # red (unemployment / contraction)
C_GRN = "#2ca02c"    # green (expansion / good)
C_ORA = "#ff7f0e"    # orange
C_HOT = "#f4a582"    # overheating shade
C_SLK = "#92c5de"    # slack shade
GREY = "#555555"


def save(fig, n):
    path = os.path.join(OUT, f"{BASE}-fig{n}.svg")
    fig.savefig(path, format="svg", bbox_inches="tight")
    plt.close(fig)
    print("wrote", path)


# ---------------------------------------------------------------------------
# Fig 1 — The anatomy of a cycle. Real GDP (blue) wobbles around a rising
#   POTENTIAL-output trend (grey). The gap between them is the OUTPUT GAP:
#   above trend = overheating (positive gap, shaded warm); below = slack
#   (negative gap, shaded cool). Phases labelled; one recession band shaded.
# ---------------------------------------------------------------------------
def fig1():
    t = np.linspace(0, 12, 600)
    potential = 100.0 + 3.0 * t                     # rising trend
    # A deliberately IRREGULAR cyclical component (two frequencies) so it does
    # not look like a clean sine wave — cycles vary in length and depth.
    cycle = 5.2 * np.sin(2 * np.pi * t / 6.2) + 1.7 * np.sin(2 * np.pi * t / 3.1 + 0.7)
    actual = potential + cycle

    fig, ax = plt.subplots(figsize=(10.4, 5.2))
    ax.plot(t, potential, color=C_POT, lw=2.0, ls="--", label="Potential output (trend)")
    ax.plot(t, actual, color=C_ACT, lw=2.6, label="Actual real GDP")

    # Shade the output gap: warm where actual>potential, cool where below.
    ax.fill_between(t, potential, actual, where=(actual >= potential),
                    color=C_HOT, alpha=0.7, interpolate=True,
                    label="Positive gap (overheating)")
    ax.fill_between(t, potential, actual, where=(actual < potential),
                    color=C_SLK, alpha=0.7, interpolate=True,
                    label="Negative gap (slack)")

    # Mark a peak and the following trough (from the first big hump).
    i_peak = np.argmax(actual[t < 4])
    i_trough = np.argmin(actual[(t > 4) & (t < 9)]) + np.searchsorted(t, 4)
    ax.plot(t[i_peak], actual[i_peak], "o", color="black", ms=6, zorder=5)
    ax.plot(t[i_trough], actual[i_trough], "o", color="black", ms=6, zorder=5)
    ax.annotate("PEAK", xy=(t[i_peak], actual[i_peak]),
                xytext=(t[i_peak] - 0.2, actual[i_peak] + 3.2),
                ha="center", fontsize=9.5, fontweight="bold")
    ax.annotate("TROUGH", xy=(t[i_trough], actual[i_trough]),
                xytext=(t[i_trough], actual[i_trough] - 4.4),
                ha="center", fontsize=9.5, fontweight="bold")

    # Shade the recession (peak -> trough) as a vertical band.
    ax.axvspan(t[i_peak], t[i_trough], color=C_UNE, alpha=0.08)
    ax.text((t[i_peak] + t[i_trough]) / 2, 108, "RECESSION\n(peak→trough)",
            ha="center", va="bottom", fontsize=8.8, color=C_UNE)

    # Phase labels along the bottom.
    ax.annotate("expansion", xy=(1.4, 101), fontsize=9, color=C_GRN, ha="center")
    ax.annotate("contraction", xy=(4.7, 101), fontsize=9, color=C_UNE, ha="center")
    ax.annotate("recovery →\nexpansion", xy=(9.4, 101), fontsize=9, color=C_GRN, ha="center")

    ax.set_xlabel("Time  →")
    ax.set_ylabel("Real output (index)")
    ax.set_title("The anatomy of a business cycle — actual GDP around potential")
    ax.set_xticks([]); ax.set_ylim(96, 150)
    ax.legend(loc="upper left", fontsize=8.6, frameon=True, framealpha=0.95, ncol=2)
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, 1)


# ---------------------------------------------------------------------------
# Fig 2 — Why supply shocks are the nasty ones. Two AD-AS panels.
#   LEFT: a DEMAND shock (AD shifts left) — price level AND output fall together
#         → a "normal" recession policy can lean against.
#   RIGHT: a SUPPLY shock (SRAS shifts up/left) — prices RISE while output FALLS
#         → STAGFLATION; one policy lever cannot fix both.
# ---------------------------------------------------------------------------
def fig2():
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(11.0, 4.9))

    def frame(ax, title):
        ax.set_xlim(0, 10); ax.set_ylim(0, 10)
        ax.set_xlabel("Real output  Y →")
        ax.set_ylabel("Price level  P →")
        ax.set_title(title, fontsize=11.5)
        ax.set_xticks([]); ax.set_yticks([])
        ax.spines[["top", "right"]].set_visible(False)

    Y = np.linspace(1, 9, 50)

    # ---- LEFT: demand shock ----
    frame(axL, "Demand shock  (e.g. spending / confidence collapse)")
    sras = 1.2 + 0.9 * Y                       # upward-sloping short-run AS
    ad0 = 12.5 - 0.9 * Y                        # downward AD
    ad1 = 9.5 - 0.9 * Y                         # AD shifted LEFT
    axL.plot(Y, sras, color=GREY, lw=2.4)
    axL.plot(Y, ad0, color=C_ACT, lw=2.4)
    axL.plot(Y, ad1, color=C_ACT, lw=2.4, ls="--")
    axL.text(8.6, sras[-1], "SRAS", color=GREY, fontsize=10, va="center")
    axL.text(8.7, ad0[-6], "AD₀", color=C_ACT, fontsize=10)
    axL.text(2.3, 8.0, "AD₁", color=C_ACT, fontsize=10)
    # Equilibria: SRAS = AD.  1.2+0.9Y = c - 0.9Y  ->  Y=(c-1.2)/1.8
    for c, mark, lab, off in [(12.5, "o", "E₀", (8, 6)), (9.5, "s", "E₁", (-20, 6))]:
        y = (c - 1.2) / 1.8; p = 1.2 + 0.9 * y
        axL.plot(y, p, mark, color=C_UNE, ms=8, zorder=5)
        axL.annotate(lab, (y, p), textcoords="offset points", xytext=off,
                     fontsize=10, fontweight="bold")
    axL.annotate("", xy=(4.6, 1.0), xytext=(6.3, 1.0),
                 arrowprops=dict(arrowstyle="->", color=C_UNE, lw=1.6))
    axL.text(3.0, 8.7, "P ↓  and  Y ↓\n(same direction)", color=C_UNE,
             fontsize=9.5, fontweight="bold")

    # ---- RIGHT: supply shock ----
    frame(axR, "Supply shock  (e.g. oil / tariff spike)")
    sras0 = 1.2 + 0.9 * Y
    sras1 = 3.6 + 0.9 * Y                        # SRAS shifted UP/left
    ad = 12.5 - 0.9 * Y
    axR.plot(Y, ad, color=C_ACT, lw=2.4)
    axR.plot(Y, sras0, color=GREY, lw=2.4)
    axR.plot(Y, sras1, color=GREY, lw=2.4, ls="--")
    axR.text(8.7, ad[-6], "AD", color=C_ACT, fontsize=10)
    axR.text(6.6, sras0[8] + 0.3, "SRAS₀", color=GREY, fontsize=10)
    axR.text(2.6, sras1[12] + 0.3, "SRAS₁", color=GREY, fontsize=10)
    for b, mark, lab, off in [(1.2, "o", "E₀", (8, 6)), (3.6, "s", "E₁", (10, 4))]:
        y = (12.5 - b) / 1.8; p = b + 0.9 * y
        axR.plot(y, p, mark, color=C_UNE, ms=8, zorder=5)
        axR.annotate(lab, (y, p), textcoords="offset points", xytext=off,
                     fontsize=10, fontweight="bold")
    axR.annotate("", xy=(4.6, 1.0), xytext=(6.3, 1.0),
                 arrowprops=dict(arrowstyle="->", color=C_UNE, lw=1.6))
    axR.text(0.6, 9.3, "P ↑  but  Y ↓\n= STAGFLATION", color=C_UNE,
             fontsize=9.5, fontweight="bold")

    fig.suptitle("What drives the cycle: a demand shock vs a supply shock", fontsize=13)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    save(fig, 2)


# ---------------------------------------------------------------------------
# Fig 3 — The expectations-augmented Phillips curve. Short-run curves slope
#   down (the inflation-unemployment trade-off), but each is drawn for a given
#   EXPECTED inflation; raise expectations and the whole curve shifts UP. In the
#   long run there is NO trade-off — the curve is VERTICAL at the natural rate
#   u*. The 1970s "stagflation drift" is the economy hopping to higher curves.
# ---------------------------------------------------------------------------
def fig3():
    u = np.linspace(2.0, 9.0, 50)
    u_star = 5.0
    # SRPC: pi = pi_e + a (u* - u).  Three expected-inflation regimes.
    a = 1.1
    fig, ax = plt.subplots(figsize=(9.2, 5.4))
    for pi_e, col, lab in [(2.0, C_ACT, "SRPC (expected π ≈ 2%)"),
                           (5.0, C_ORA, "SRPC (expected π ≈ 5%)"),
                           (8.0, C_UNE, "SRPC (expected π ≈ 8%)")]:
        ax.plot(u, pi_e + a * (u_star - u), color=col, lw=2.3, label=lab)

    # Vertical long-run Phillips curve at u*.
    ax.axvline(u_star, color="black", lw=2.4, ls="-")
    ax.text(u_star + 0.12, 0.7, "LRPC\n(vertical at u*\n— no long-run\ntrade-off)",
            fontsize=8.4, va="bottom", ha="left")
    ax.text(u_star, 12.55, "u* = natural rate / NAIRU", ha="center", va="bottom",
            fontsize=8.8, fontweight="bold")

    # Short-run trade-off arrow along the lowest curve.
    ax.annotate("move ALONG a curve\n= short-run trade-off\n(lower u ↔ higher π)",
                xy=(3.3, 2.0 + a * (u_star - 3.3)), xytext=(2.15, 8.6),
                fontsize=8.6, color=C_ACT,
                arrowprops=dict(arrowstyle="->", color=C_ACT))
    # The 1970s drift: hopping to higher curves as expectations un-anchor.
    ax.annotate("expectations un-anchor\n→ whole curve shifts UP\n(1970s stagflation)",
                xy=(7.3, 8.0 + a * (u_star - 7.3)), xytext=(5.9, 11.7),
                fontsize=8.6, color=C_UNE, ha="left",
                arrowprops=dict(arrowstyle="->", color=C_UNE))

    ax.set_xlabel("Unemployment rate  u  (%)")
    ax.set_ylabel("Inflation rate  π  (%)")
    ax.set_title("The Phillips curve: short-run trade-off, no long-run one")
    ax.set_xlim(2, 9); ax.set_ylim(0, 13)
    ax.legend(loc="lower left", fontsize=8.6, frameon=True, framealpha=0.95)
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, 3)


# ---------------------------------------------------------------------------
# Fig 4 — Timing: leading, coincident, and lagging indicators around a
#   recession. A LEADING index (blue) turns down before the peak; GDP
#   (coincident, black) turns at the peak; UNEMPLOYMENT (lagging, red, right
#   axis) keeps rising past the trough. This is why the news watches the yield
#   curve/PMIs to see a recession coming and why unemployment confirms it late.
# ---------------------------------------------------------------------------
def fig4():
    t = np.linspace(0, 12, 700)
    T = 8.0
    # One clean cycle in-window. Period-8 sines with phases chosen so the
    # relevant turning points fall INSIDE [0,12]:
    #   GDP (coincident) peaks at t=5 (recession start), troughs at t=9.
    #   Leading peaks ~1.2 earlier, at t=3.8.
    #   Unemployment (lagging, countercyclical) troughs at t=6.5 and peaks
    #     at t=10.5 — i.e. AFTER the GDP trough. Turning points are hard-coded
    #     into the phase, not found by argmax (which would pick the wrong
    #     periodic copy at the left edge).
    LEAD_PEAK, GDP_PEAK, UNEMP_PEAK = 3.8, 5.0, 10.5
    rec_start, rec_end = 5.0, 9.0                 # GDP peak -> trough
    gdp = 100 + 6.0 * np.sin(2 * np.pi * (t - (GDP_PEAK - T / 4)) / T)
    lead = 100 + 5.0 * np.sin(2 * np.pi * (t - (LEAD_PEAK - T / 4)) / T)
    unemp = 5.0 - 1.6 * np.sin(2 * np.pi * (t - (UNEMP_PEAK + T / 4)) / T)

    fig, ax1 = plt.subplots(figsize=(10.6, 5.2))
    ax1.axvspan(rec_start, rec_end, color=C_UNE, alpha=0.10)
    ax1.text((rec_start + rec_end) / 2, 108.6, "RECESSION", ha="center",
             fontsize=9.5, color=C_UNE, fontweight="bold")

    ax1.plot(t, lead, color=C_ACT, lw=2.5, label="Leading (e.g. yield curve, PMIs, permits)")
    ax1.plot(t, gdp, color="black", lw=2.5, label="Coincident (GDP, industrial production)")
    ax1.set_ylabel("Activity index (leading & coincident)")
    ax1.set_ylim(92, 110)
    ax1.set_xlabel("Time  →")
    ax1.set_xlim(0, 12)
    ax1.set_xticks([])

    ax2 = ax1.twinx()
    ax2.plot(t, unemp, color=C_UNE, lw=2.5, ls="-", label="Lagging: unemployment rate (right)")
    ax2.set_ylabel("Unemployment rate (%)", color=C_UNE)
    ax2.tick_params(axis="y", labelcolor=C_UNE)
    ax2.set_ylim(3.0, 7.5)

    # Turning-point markers at the hard-coded times.
    ax1.axvline(LEAD_PEAK, color=C_ACT, ls=":", lw=1.3)
    ax1.text(LEAD_PEAK - 0.1, 92.6, "leading\npeaks FIRST", color=C_ACT,
             fontsize=8.2, ha="center", va="bottom")
    ax1.axvline(GDP_PEAK, color="black", ls=":", lw=1.3)
    ax1.text(GDP_PEAK + 0.12, 92.6, "GDP peaks\n(recession starts)", color="black",
             fontsize=8.2, ha="left", va="bottom")
    ax2.axvline(UNEMP_PEAK, color=C_UNE, ls=":", lw=1.3)
    ax2.text(UNEMP_PEAK, 3.55, "unemployment\npeaks LAST", color=C_UNE,
             fontsize=8.2, ha="center", va="bottom")

    lines1, labs1 = ax1.get_legend_handles_labels()
    lines2, labs2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labs1 + labs2, loc="upper left", fontsize=8.2,
               frameon=True, framealpha=0.95)
    ax1.set_title("Reading the cycle in real time: leading, coincident, lagging")
    ax1.spines[["top"]].set_visible(False)
    ax2.spines[["top"]].set_visible(False)
    save(fig, 4)


if __name__ == "__main__":
    fig1(); fig2(); fig3(); fig4()
    print("done")
