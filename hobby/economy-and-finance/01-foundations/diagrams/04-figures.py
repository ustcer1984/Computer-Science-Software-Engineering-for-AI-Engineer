#!/usr/bin/env python3
"""Figures for Econ E01 §4 — Firms, costs & competition.

Editable source of truth for the committed SVGs (see agent-docs/diagrams.md:
commit the rendered image, keep the source beside it). All curves use dummy but
internally consistent values — the point is the *shape and the regions*, not the
numbers. Run with the project venv:

    .venv/bin/python hobby/economy-and-finance/01-foundations/diagrams/04-figures.py

Outputs 04-firms-costs-and-competition-figN.svg into this folder.
"""
import os
import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt
import numpy as np

OUT = os.path.dirname(os.path.abspath(__file__))
BASE = "04-firms-costs-and-competition"

plt.rcParams.update({
    "font.size": 12,
    "axes.titlesize": 13,
    "axes.labelsize": 12,
    "svg.fonttype": "none",   # keep text as text (smaller, selectable)
    "figure.dpi": 100,
})

C_MC = "#d62728"   # marginal cost / red
C_ATC = "#1f77b4"  # average total cost / blue
C_AVC = "#2ca02c"  # average variable cost / green
C_AFC = "#9467bd"  # average fixed cost / purple
C_P = "#ff7f0e"    # price / orange
C_D = "#1f77b4"    # demand / blue (figs 3,5)
C_MR = "#9467bd"   # marginal revenue / purple
C_PROF = "#c7e9c0" # profit fill (green)
C_LOSS = "#fcbba1" # loss fill (red)
GREY = "#555555"


def style(ax, xmax, ymax, xlabel="Quantity  $q$", ylabel="Cost / Price  ($\\$$)"):
    ax.set_xlim(0, xmax)
    ax.set_ylim(0, ymax)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.plot(1, 0, ">k", transform=ax.get_yaxis_transform(), clip_on=False, ms=6)
    ax.plot(0, 1, "^k", transform=ax.get_xaxis_transform(), clip_on=False, ms=6)


def legend(ax, loc="upper center", fontsize=9):
    ax.legend(loc=loc, frameon=True, facecolor="white", framealpha=0.92,
              edgecolor="0.8", fontsize=fontsize)


def save(fig, n):
    path = os.path.join(OUT, f"{BASE}-fig{n}.svg")
    fig.savefig(path, format="svg", bbox_inches="tight")
    plt.close(fig)
    print("wrote", path)


# --- the firm's cost structure (shared by figs 1, 2, 3) ---------------------
# VC(q) = 10q - 0.8 q^2 + 0.05 q^3 ; FC = 100
FC = 100.0
def VC(q):  return 10*q - 0.8*q**2 + 0.05*q**3
def TC(q):  return FC + VC(q)
def MC(q):  return 10 - 1.6*q + 0.15*q**2
def AVC(q): return VC(q)/q
def ATC(q): return TC(q)/q
def AFC(q): return FC/q

def _min_on(f, lo, hi):
    q = np.linspace(lo, hi, 20000)
    y = f(q)
    i = int(np.argmin(y))
    return q[i], y[i]


# ---------------------------------------------------------------------------
# Fig 1 — The family of cost curves: MC cuts AVC and ATC at their minima.
# ---------------------------------------------------------------------------
def fig1():
    fig, ax = plt.subplots(figsize=(7.0, 5.4))
    q = np.linspace(2.0, 18.0, 400)
    ax.plot(q, MC(q),  color=C_MC,  lw=2.6, label="Marginal cost (MC)")
    ax.plot(q, ATC(q), color=C_ATC, lw=2.4, label="Average total cost (ATC)")
    ax.plot(q, AVC(q), color=C_AVC, lw=2.2, label="Average variable cost (AVC)")
    ax.plot(q, AFC(q), color=C_AFC, lw=1.8, ls="--", label="Average fixed cost (AFC)")

    qa, va = _min_on(AVC, 3, 15)      # min AVC
    qt, vt = _min_on(ATC, 5, 17)      # min ATC
    for (qx, vy, txt) in [(qa, va, "min AVC\n(shutdown point)"),
                          (qt, vt, "min ATC\n(break-even point)")]:
        ax.plot([qx], [vy], "ko", ms=5)
        ax.vlines(qx, 0, vy, color=GREY, ls=":", lw=0.8)
    ax.annotate("MC cuts AVC\nat its minimum", xy=(qa, va), xytext=(qa-3.4, va+6),
                fontsize=9, arrowprops=dict(arrowstyle="->", color="black"))
    ax.annotate("MC cuts ATC\nat its minimum", xy=(qt, vt), xytext=(qt+0.4, vt+9),
                fontsize=9, arrowprops=dict(arrowstyle="->", color="black"))

    style(ax, xmax=18, ymax=40, ylabel="Cost per unit  ($\\$$)")
    ax.set_title("The cost curves: marginal pulls the average")
    legend(ax, loc="upper center")
    save(fig, 1)


# ---------------------------------------------------------------------------
# Fig 2 — The output decision: profit, loss-but-operate, and the shutdown rule.
# ---------------------------------------------------------------------------
def fig2():
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(12.0, 5.2), sharey=True)
    q = np.linspace(2.0, 18.0, 400)
    qa, va = _min_on(AVC, 3, 15)
    qt, vt = _min_on(ATC, 5, 17)

    def base(ax):
        ax.plot(q, MC(q),  color=C_MC,  lw=2.6, label="MC")
        ax.plot(q, ATC(q), color=C_ATC, lw=2.2, label="ATC")
        ax.plot(q, AVC(q), color=C_AVC, lw=2.0, label="AVC")
        ax.plot([qa],[va],"ko",ms=4); ax.plot([qt],[vt],"ko",ms=4)

    # --- Left: P above ATC -> economic profit -------------------------------
    P1 = 26.0
    # q* where MC = P1 (upper branch)
    qs = np.linspace(qt, 18, 20000); q1 = qs[int(np.argmin(np.abs(MC(qs)-P1)))]
    base(axL)
    axL.axhline(P1, color=C_P, lw=2.2, label="Price $P = MR$")
    axL.fill_between([0, q1], ATC(q1), P1, color=C_PROF, alpha=0.95)
    axL.text(q1/2, (ATC(q1)+P1)/2, "economic\nPROFIT", ha="center", va="center", fontsize=10)
    axL.vlines(q1, 0, P1, color=GREY, ls=":", lw=0.9)
    axL.text(q1, -1.4, "$q^\\ast$", ha="center", va="top", fontsize=12)
    axL.plot([q1],[P1],"ko",ms=5)
    style(axL, xmax=18, ymax=40, ylabel="Cost per unit  ($\\$$)")
    axL.set_title("$P > $ ATC : produce, earn economic profit")
    legend(axL, loc="upper center")

    # --- Right: AVC < P < ATC -> operate at a loss; below AVC -> shut down ---
    P2 = 13.0
    qs2 = np.linspace(qa, 16, 20000); q2 = qs2[int(np.argmin(np.abs(MC(qs2)-P2)))]
    base(axR)
    axR.axhline(P2, color=C_P, lw=2.2, label="Price $P = MR$")
    axR.fill_between([0, q2], P2, ATC(q2), color=C_LOSS, alpha=0.95)
    axR.text(q2/2, (P2+ATC(q2))/2, "LOSS\n(but $<$ fixed cost)", ha="center", va="center", fontsize=9)
    axR.vlines(q2, 0, P2, color=GREY, ls=":", lw=0.9)
    axR.text(q2, -1.4, "$q^\\ast$", ha="center", va="top", fontsize=12)
    axR.plot([q2],[P2],"ko",ms=5)
    axR.annotate("below min AVC\n$\\Rightarrow$ SHUT DOWN", xy=(qa, va), xytext=(qa-0.2, va-5.2),
                 fontsize=9, ha="center", arrowprops=dict(arrowstyle="->", color="black"))
    style(axR, xmax=18, ymax=40, ylabel="")
    axR.set_title("AVC $< P <$ ATC : keep operating, but at a loss")
    legend(axR, loc="upper center")
    save(fig, 2)


# ---------------------------------------------------------------------------
# Fig 3 — Perfect competition: price-taker, and the long-run zero-profit pull.
# ---------------------------------------------------------------------------
def fig3():
    fig, ax = plt.subplots(figsize=(7.2, 5.4))
    q = np.linspace(2.0, 18.0, 400)
    qt, vt = _min_on(ATC, 5, 17)     # min ATC = long-run price
    ax.plot(q, MC(q),  color=C_MC,  lw=2.6, label="MC = the firm's supply")
    ax.plot(q, ATC(q), color=C_ATC, lw=2.2, label="ATC")

    # short-run: high price, profit
    Psr = 26.0
    qs = np.linspace(qt, 18, 20000); qsr = qs[int(np.argmin(np.abs(MC(qs)-Psr)))]
    ax.axhline(Psr, color=C_P, lw=2.2, ls="-", label="Short-run price (profit)")
    ax.fill_between([0, qsr], ATC(qsr), Psr, color=C_PROF, alpha=0.9)
    ax.text(qsr/2, (ATC(qsr)+Psr)/2, "profit\nattracts entry", ha="center", va="center", fontsize=9)
    ax.plot([qsr],[Psr],"ko",ms=5)

    # long-run: price competed down to min ATC, zero economic profit
    ax.axhline(vt, color="#8c564b", lw=2.0, ls="--", label="Long-run price = min ATC")
    ax.plot([qt],[vt],"ko",ms=5)
    ax.annotate("long-run eq.:\nzero profit,\n$P=MC=$ min ATC",
                xy=(qt, vt), xytext=(qt+0.3, vt-8.5), fontsize=9,
                arrowprops=dict(arrowstyle="->", color="black"))
    ax.annotate("", xy=(11.5, vt+0.6), xytext=(11.5, Psr-0.6),
                arrowprops=dict(arrowstyle="->", color=GREY, lw=1.6))
    ax.text(11.7, (vt+Psr)/2, "entry\n$\\Rightarrow P\\downarrow$", color=GREY,
            fontsize=8.5, va="center")

    style(ax, xmax=18, ymax=40, ylabel="Price / Cost  ($\\$$)")
    ax.set_title("Perfect competition: free entry competes profit to zero")
    legend(ax, loc="upper center")
    save(fig, 3)


# ---------------------------------------------------------------------------
# Fig 4 — Economies of scale: the long-run average cost envelope.
# ---------------------------------------------------------------------------
def fig4():
    fig, ax = plt.subplots(figsize=(7.4, 5.2))
    Q = np.linspace(0.5, 12, 500)
    # A few short-run ATC curves (different plant sizes), LRAC = lower envelope.
    plants = [(2.0, 8.0), (4.0, 6.2), (6.0, 5.6), (8.0, 6.2), (10.0, 8.0)]
    for i, (q0, c0) in enumerate(plants):
        SR = c0 + 0.45*(Q - q0)**2
        ax.plot(Q, SR, color="0.78", lw=1.2, zorder=1)
    # LRAC: smooth U through the plant minima
    LRAC = 5.6 + 0.09*(Q - 6.0)**2
    ax.plot(Q, LRAC, color=C_ATC, lw=3.0, label="Long-run average cost (LRAC)", zorder=3)

    mes = 6.0  # minimum efficient scale (bottom of LRAC)
    ax.axvline(mes, color=GREY, ls=":", lw=1)
    ax.plot([mes],[5.6],"ko",ms=5,zorder=4)
    ax.text(mes, -0.7, "MES", ha="center", va="top", fontsize=11)
    ax.annotate("minimum\nefficient scale", xy=(mes, 5.6), xytext=(mes+0.3, 4.0),
                fontsize=9, arrowprops=dict(arrowstyle="->", color="black"))

    ax.text(2.4, 9.4, "ECONOMIES\nof scale\n(LRAC $\\downarrow$)", color="#08519c",
            fontsize=9.5, ha="center")
    ax.text(9.6, 9.4, "DISECONOMIES\nof scale\n(LRAC $\\uparrow$)", color="#a63603",
            fontsize=9.5, ha="center")

    style(ax, xmax=12, ymax=12, xlabel="Output / firm size  $Q$", ylabel="Average cost  ($\\$$)")
    ax.set_title("Economies of scale: the LRAC envelope of plant choices")
    legend(ax, loc="upper center")
    save(fig, 4)


# ---------------------------------------------------------------------------
# Fig 5 — Monopolistic competition long run: tangency, excess capacity.
#   ATC(q) = 0.1 q^2 - 2q + 20  (min at q=10, ATC=10)
#   D: P = 16.4 - 0.8 q  (tangent to ATC at q=6) ; MR = 16.4 - 1.6 q
#   MC = 0.3 q^2 - 4q + 20 ; MR=MC at q=6 (=6.8); P=ATC=11.6 at q=6.
# ---------------------------------------------------------------------------
def fig5():
    fig, ax = plt.subplots(figsize=(7.2, 5.6))
    q = np.linspace(0.5, 14, 400)
    ATCm = 0.1*q**2 - 2*q + 20
    MCm = 0.3*q**2 - 4*q + 20
    D = 16.4 - 0.8*q
    MR = 16.4 - 1.6*q
    qt, Pt = 6.0, 11.6
    qmin = 10.0  # min ATC

    ax.plot(q, D,    color="#1f77b4", lw=2.4, label="Demand (the firm's own brand)")
    ax.plot(q, MR,   color=C_MR,      lw=2.0, ls="--", label="Marginal revenue")
    ax.plot(q, ATCm, color="#ff7f0e", lw=2.4, label="ATC")
    ax.plot(q, MCm,  color=C_MC,      lw=2.2, label="MC")

    ax.plot([qt],[Pt],"ko",ms=6)
    ax.annotate("tangency:\n$P = $ ATC\n(zero profit)", xy=(qt, Pt), xytext=(qt+1.2, Pt+3.0),
                fontsize=9, arrowprops=dict(arrowstyle="->", color="black"))
    ax.plot([qt],[6.8],"ko",ms=5)
    ax.annotate("$MR = MC$", xy=(qt, 6.8), xytext=(qt-3.6, 6.8-2.6),
                fontsize=9, arrowprops=dict(arrowstyle="->", color="black"))
    ax.vlines(qt, 0, Pt, color=GREY, ls=":", lw=0.9)
    ax.vlines(qmin, 0, 0.1*qmin**2-2*qmin+20, color=GREY, ls=":", lw=0.9)
    ax.text(qt, -0.8, "$q^\\ast$", ha="center", va="top", fontsize=12)
    ax.text(qmin, -0.8, "min-ATC\nscale", ha="center", va="top", fontsize=9)
    # excess-capacity bracket
    ax.annotate("", xy=(qt, 2.0), xytext=(qmin, 2.0),
                arrowprops=dict(arrowstyle="<->", color="#7f3b08", lw=1.4))
    ax.text((qt+qmin)/2, 1.2, "excess capacity", ha="center", va="top",
            color="#7f3b08", fontsize=9)

    style(ax, xmax=14, ymax=22, xlabel="Quantity  $q$  (the firm)", ylabel="Price / Cost  ($\\$$)")
    ax.xaxis.set_label_coords(0.5, -0.13)
    ax.set_title("Monopolistic competition (long run): zero profit, but $P>MC$")
    legend(ax, loc="upper right")
    save(fig, 5)


if __name__ == "__main__":
    fig1(); fig2(); fig3(); fig4(); fig5()
    print("done")
