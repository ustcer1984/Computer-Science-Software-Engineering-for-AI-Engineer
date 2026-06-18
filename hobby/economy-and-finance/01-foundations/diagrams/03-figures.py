#!/usr/bin/env python3
"""Figures for Econ E01 §3 — Elasticity, surplus & market failure.

Editable source of truth for the committed SVGs (see agent-docs/diagrams.md:
commit the rendered image, keep the source beside it). All curves use dummy but
internally consistent values — the point is the *shape and the regions*, not the
numbers. Run with the project venv:

    .venv/bin/python hobby/economy-and-finance/01-foundations/diagrams/03-figures.py

Outputs 03-elasticity-surplus-and-market-failure-figN.svg into this folder.
"""
import os
import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt
import numpy as np

OUT = os.path.dirname(os.path.abspath(__file__))
BASE = "03-elasticity-surplus-and-market-failure"

plt.rcParams.update({
    "font.size": 12,
    "axes.titlesize": 13,
    "axes.labelsize": 12,
    "svg.fonttype": "none",   # keep text as text (smaller, selectable)
    "figure.dpi": 100,
})

C_D = "#1f77b4"   # demand / blue
C_S = "#d62728"   # supply / red
C_3 = "#2ca02c"   # third curve / green
C_CS = "#9ecae1"  # consumer-surplus fill
C_PS = "#fdae6b"  # producer-surplus fill
C_DW = "#bdbdbd"  # deadweight fill
GREY = "#555555"


def style(ax, xmax=10, ymax=10, xlabel="Quantity  $Q$", ylabel="Price  $P$"):
    ax.set_xlim(0, xmax)
    ax.set_ylim(0, ymax)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])
    # arrowheads on the axes
    ax.plot(1, 0, ">k", transform=ax.get_yaxis_transform(), clip_on=False, ms=6)
    ax.plot(0, 1, "^k", transform=ax.get_xaxis_transform(), clip_on=False, ms=6)


def legend(ax, loc="upper right", fontsize=9):
    # white-backed frame so curves crossing behind the legend don't show through
    ax.legend(loc=loc, frameon=True, facecolor="white", framealpha=0.92,
              edgecolor="0.8", fontsize=fontsize)


def save(fig, n):
    path = os.path.join(OUT, f"{BASE}-fig{n}.svg")
    fig.savefig(path, format="svg", bbox_inches="tight")
    plt.close(fig)
    print("wrote", path)


# ---------------------------------------------------------------------------
# Fig 1 — Elastic vs inelastic demand: same price rise, very different ΔQ.
# ---------------------------------------------------------------------------
def fig1():
    fig, ax = plt.subplots(figsize=(6.6, 5.0))
    Q0, P0 = 5.0, 5.0           # common starting point
    P1 = 7.0                    # both face the SAME price rise
    # inelastic = steep: small slope dQ/dP. elastic = flat: large dQ/dP.
    # line through (Q0,P0): Q = Q0 + b*(P-P0) with b<0.
    b_inel, b_elas = -0.30, -2.0
    Pgrid = np.linspace(1.2, 9.0, 50)
    Qi = Q0 + b_inel * (Pgrid - P0)
    Qe = Q0 + b_elas * (Pgrid - P0)
    ax.plot(Qi, Pgrid, color=C_D, lw=2.4, label="Inelastic demand (steep)")
    ax.plot(Qe, Pgrid, color=C_3, lw=2.4, label="Elastic demand (flat)")

    Qi1 = Q0 + b_inel * (P1 - P0)
    Qe1 = Q0 + b_elas * (P1 - P0)
    # price-rise guide lines
    ax.hlines([P0, P1], 0, Q0 + 0.2, color=GREY, ls=":", lw=1)
    ax.annotate("", xy=(0.6, P1), xytext=(0.6, P0),
                arrowprops=dict(arrowstyle="->", color="black", lw=1.6))
    ax.text(0.85, (P0 + P1) / 2, "price\nrise", va="center", fontsize=10)

    for Q1, c, lab in [(Qi1, C_D, "small $\\Delta Q$"), (Qe1, C_3, "large $\\Delta Q$")]:
        ax.vlines(Q1, 0, P1, color=c, ls=":", lw=1)
        ax.annotate("", xy=(Q1, 0.5), xytext=(Q0, 0.5),
                    arrowprops=dict(arrowstyle="->", color=c, lw=1.8))
    ax.plot([Q0], [P0], "ko", ms=5)
    ax.text(Qi1 - 0.1, 0.9, "inelastic:\n" + "small $\\Delta Q$", color=C_D, fontsize=9, ha="right")
    ax.text(Qe1 + 0.15, 0.9, "elastic:\nlarge $\\Delta Q$", color=C_3, fontsize=9, ha="left")

    style(ax)
    ax.set_title("Same price rise, very different quantity response")
    legend(ax, fontsize=10)
    save(fig, 1)


# ---------------------------------------------------------------------------
# Fig 2 — Elasticity along a linear demand curve, and the total-revenue test.
# ---------------------------------------------------------------------------
def fig2():
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(11.0, 4.6))
    # Linear demand P = a - m Q, a=10, m=1 over Q in [0,10]
    a, m = 10.0, 1.0
    Q = np.linspace(0, 10, 200)
    P = a - m * Q
    mid = 5.0  # midpoint Q where elasticity = 1 (for linear demand)

    axL.plot(Q, P, color=C_D, lw=2.4)
    axL.axvline(mid, color=GREY, ls=":", lw=1)
    axL.fill_between(Q[Q <= mid], P[Q <= mid], color=C_3, alpha=0.12)
    axL.fill_between(Q[Q >= mid], P[Q >= mid], color=C_S, alpha=0.12)
    axL.text(2.0, 7.2, "ELASTIC\n$|\\epsilon|>1$\nupper half", color=C_3, fontsize=10, ha="center")
    axL.text(8.0, 2.2, "INELASTIC\n$|\\epsilon|<1$\nlower half", color=C_S, fontsize=10, ha="center")
    axL.plot([mid], [a - m * mid], "ko", ms=5)
    axL.annotate("unit elastic\n$|\\epsilon|=1$", xy=(mid, a - m * mid), xytext=(mid + 0.5, 6.5),
                 fontsize=10, arrowprops=dict(arrowstyle="->", color="black"))
    style(axL)
    axL.set_title("Elasticity is NOT slope: it slides along a straight line")

    # Total revenue TR = P*Q = (a - mQ) Q -> parabola, peak at Q = a/(2m) = 5
    TR = P * Q
    axR.plot(Q, TR, color="#6a3d9a", lw=2.4)
    axR.axvline(mid, color=GREY, ls=":", lw=1)
    axR.plot([mid], [(a - m * mid) * mid], "ko", ms=5)
    axR.annotate("TR peaks where\n$|\\epsilon|=1$", xy=(mid, (a - m * mid) * mid),
                 xytext=(mid + 0.4, 17), fontsize=10,
                 arrowprops=dict(arrowstyle="->", color="black"))
    axR.annotate("raise price\n$\\Rightarrow$ TR $\\uparrow$", xy=(2.5, (a - m * 2.5) * 2.5),
                 xytext=(0.6, 8), color=C_3, fontsize=9.5,
                 arrowprops=dict(arrowstyle="->", color=C_3))
    axR.annotate("raise price\n$\\Rightarrow$ TR $\\downarrow$", xy=(7.5, (a - m * 7.5) * 7.5),
                 xytext=(7.4, 8), color=C_S, fontsize=9.5,
                 arrowprops=dict(arrowstyle="->", color=C_S))
    axR.set_xlim(0, 10)
    axR.set_ylim(0, 28)
    axR.set_xlabel("Quantity  $Q$")
    axR.set_ylabel("Total revenue  $TR = P\\cdot Q$")
    axR.spines[["top", "right"]].set_visible(False)
    axR.set_xticks([]); axR.set_yticks([])
    axR.set_title("The total-revenue test")
    save(fig, 2)


# ---------------------------------------------------------------------------
# Fig 3 — Consumer & producer surplus at the competitive equilibrium.
# ---------------------------------------------------------------------------
def fig3():
    fig, ax = plt.subplots(figsize=(6.6, 5.2))
    # Demand P = 10 - Q ; Supply P = 2 + Q ; intersect at Q*=4, P*=6
    Q = np.linspace(0, 10, 200)
    PD = 10 - Q
    PS = 2 + Q
    Qstar, Pstar = 4.0, 6.0
    ax.plot(Q, PD, color=C_D, lw=2.4, label="Demand (marginal benefit)")
    ax.plot(Q, PS, color=C_S, lw=2.4, label="Supply (marginal cost)")

    # CS triangle: between demand and P* for Q in [0,Q*]
    qfill = np.linspace(0, Qstar, 50)
    ax.fill_between(qfill, Pstar, 10 - qfill, color=C_CS, alpha=0.85, label="Consumer surplus")
    # PS triangle: between P* and supply
    ax.fill_between(qfill, 2 + qfill, Pstar, color=C_PS, alpha=0.85, label="Producer surplus")

    ax.hlines(Pstar, 0, Qstar, color=GREY, ls=":", lw=1)
    ax.vlines(Qstar, 0, Pstar, color=GREY, ls=":", lw=1)
    ax.plot([Qstar], [Pstar], "ko", ms=5)
    ax.text(-0.15, Pstar, "$P^*$", ha="right", va="center", fontsize=12)
    ax.text(Qstar, -0.3, "$Q^*$", ha="center", va="top", fontsize=12)
    ax.text(1.3, 7.6, "CS", fontsize=12, fontweight="bold", color="#08519c")
    ax.text(1.3, 4.4, "PS", fontsize=12, fontweight="bold", color="#a63603")

    style(ax)
    ax.set_title("Total surplus = CS + PS, maximised at $Q^*$")
    legend(ax)
    save(fig, 3)


# ---------------------------------------------------------------------------
# Fig 4 — Deadweight loss & incidence from a per-unit tax.
# ---------------------------------------------------------------------------
def fig4():
    fig, ax = plt.subplots(figsize=(6.8, 5.4))
    # D: P = 10 - Q ; S: P = 2 + Q ; free-market Q*=4, P*=6
    Q = np.linspace(0, 10, 200)
    PD = 10 - Q
    PS = 2 + Q
    tax = 3.0
    PSt = 2 + Q + tax           # supply shifted up by the tax
    # new traded quantity: 10 - Q = 2 + Q + tax -> Q = (8 - tax)/2
    Qt = (8 - tax) / 2.0        # = 2.5
    Pb = 10 - Qt                # price buyers pay = 7.5
    Ps = 2 + Qt                 # price sellers keep = 4.5
    Qstar, Pstar = 4.0, 6.0

    ax.plot(Q, PD, color=C_D, lw=2.4, label="Demand")
    ax.plot(Q, PS, color=C_S, lw=2.4, label="Supply (pre-tax)")
    ax.plot(Q, PSt, color=C_S, lw=1.8, ls="--", label="Supply + tax")

    # tax-revenue rectangle: width Qt, height tax, between Ps and Pb
    ax.fill_between([0, Qt], Ps, Pb, color="#c7e9c0", alpha=0.9)
    ax.text(Qt / 2, (Ps + Pb) / 2, "tax\nrevenue", ha="center", va="center", fontsize=9.5)

    # deadweight-loss triangle: vertices (Qt,Pb)->(Qstar,Pstar)->(Qt,Ps)
    ax.fill([Qt, Qstar, Qt], [Pb, Pstar, Ps], color=C_DW, alpha=0.9)
    ax.annotate("deadweight\nloss", xy=(Qt + 0.45, Pstar), xytext=(5.4, 6.6),
                fontsize=10, arrowprops=dict(arrowstyle="->", color="black"))

    for y, lab in [(Pb, "$P_b$ (buyers pay)"), (Pstar, "$P^*$"), (Ps, "$P_s$ (sellers keep)")]:
        ax.hlines(y, 0, Qt if y != Pstar else Qstar, color=GREY, ls=":", lw=0.9)
        ax.text(-0.2, y, lab, ha="right", va="center", fontsize=9.5)
    ax.vlines(Qt, 0, Pb, color=GREY, ls=":", lw=0.9)
    ax.vlines(Qstar, 0, Pstar, color=GREY, ls=":", lw=0.9)
    ax.text(Qt, -0.3, "$Q_{tax}$", ha="center", va="top", fontsize=10)
    ax.text(Qstar, -0.3, "$Q^*$", ha="center", va="top", fontsize=10)
    ax.plot([Qstar], [Pstar], "ko", ms=4)

    # y-axis label dropped: the P_b / P* / P_s labels already mark the axis as price,
    # and a rotated "Price" label collides with them.
    style(ax, ylabel="")
    ax.set_title("A tax drives a wedge: $Q\\downarrow$, and a deadweight-loss triangle opens")
    legend(ax)
    save(fig, 4)


# ---------------------------------------------------------------------------
# Fig 5 — Negative externality: market over-produces vs the social optimum.
# ---------------------------------------------------------------------------
def fig5():
    fig, ax = plt.subplots(figsize=(6.8, 5.2))
    Q = np.linspace(0, 10, 200)
    D = 10 - Q              # demand = marginal social benefit
    MPC = 2 + Q            # private marginal cost (the market supply)
    ext = 2.0
    MSC = 2 + Q + ext      # social marginal cost = MPC + external cost
    Qm, Pm = 4.0, 6.0      # market eq: D = MPC -> Q=4
    Qe = (8 - ext) / 2.0   # efficient: D = MSC -> Q=3
    Pe = 10 - Qe           # = 7

    ax.plot(Q, D, color=C_D, lw=2.4, label="Demand = MSB")
    ax.plot(Q, MPC, color=C_S, lw=2.4, label="MPC = supply (private cost)")
    ax.plot(Q, MSC, color="#7f3b08", lw=2.2, ls="--", label="MSC = social cost")

    # external-cost wedge between MPC and MSC, drawn at Qw=5 (both within frame)
    Qw = 5.0
    ax.annotate("", xy=(Qw, 2 + Qw + ext), xytext=(Qw, 2 + Qw),
                arrowprops=dict(arrowstyle="<->", color="#7f3b08", lw=1.4))
    ax.text(Qw + 0.15, 2 + Qw - 0.25, "external\ncost", color="#7f3b08",
            fontsize=9, va="top")

    # DWL triangle: vertices (Qe,Pe)->(Qm,Pm)->(Qe, MSC at Qe)
    MSC_Qe = 2 + Qe + ext  # = Pe here (Pe = MSC at Qe by construction)
    ax.fill([Qe, Qm, Qe], [Pe, Pm, MSC_Qe], color=C_DW, alpha=0.9)
    ax.annotate("deadweight loss\n(over-production)", xy=(Qe + 0.35, Pe - 0.4),
                xytext=(0.6, 7.6), fontsize=9.5,
                arrowprops=dict(arrowstyle="->", color="black"))

    for Qx, lab in [(Qm, "$Q_{mkt}$"), (Qe, "$Q^*$")]:
        ax.vlines(Qx, 0, 10 - Qx, color=GREY, ls=":", lw=0.9)
        ax.text(Qx, -0.3, lab, ha="center", va="top", fontsize=10)
    ax.plot([Qm, Qe], [Pm, Pe], "ko", ms=4)

    style(ax)
    ax.set_title("Negative externality: private optimum over-produces")
    legend(ax)
    save(fig, 5)


# ---------------------------------------------------------------------------
# Fig 6 — Monopoly: MR<P, restricted output, deadweight loss.
# ---------------------------------------------------------------------------
def fig6():
    fig, ax = plt.subplots(figsize=(6.8, 5.4))
    Q = np.linspace(0, 10, 200)
    a, m = 10.0, 1.0
    D = a - m * Q          # demand / price
    MR = a - 2 * m * Q     # marginal revenue: twice the slope
    mc = 2.0
    MC = mc + 0 * Q        # constant marginal cost for clarity
    # monopoly: MR = MC -> a - 2mQ = mc -> Qm = (a-mc)/(2m) = 4
    Qm = (a - mc) / (2 * m)
    Pm = a - m * Qm        # = 6
    # competitive: P = MC -> Qc = a - mc = 8, Pc = mc = 2
    Qc = a - mc
    Pc = mc

    ax.plot(Q, D, color=C_D, lw=2.4, label="Demand (price)")
    ax.plot(Q[MR >= 0], MR[MR >= 0], color="#9467bd", lw=2.0, ls="--", label="Marginal revenue")
    ax.plot(Q, MC, color=C_S, lw=2.2, label="Marginal cost")

    # DWL triangle between Qm and Qc: (Qm,Pm)->(Qm,MC)->(Qc,Pc)
    ax.fill([Qm, Qm, Qc], [Pm, mc, Pc], color=C_DW, alpha=0.9)
    ax.annotate("deadweight loss\n(under-production)", xy=(Qm + 0.5, 3.2),
                xytext=(5.4, 5.0), fontsize=9.5,
                arrowprops=dict(arrowstyle="->", color="black"))
    # monopoly profit (markup) rectangle: width Qm, height Pm-mc
    ax.fill_between([0, Qm], mc, Pm, color="#fee391", alpha=0.6)
    ax.text(Qm / 2, (mc + Pm) / 2, "monopoly\nmark-up", ha="center", va="center", fontsize=9)

    ax.hlines(Pm, 0, Qm, color=GREY, ls=":", lw=0.9)
    ax.vlines(Qm, 0, Pm, color=GREY, ls=":", lw=0.9)
    ax.vlines(Qc, 0, Pc, color=GREY, ls=":", lw=0.9)
    ax.text(-0.15, Pm, "$P_m$", ha="right", va="center", fontsize=11)
    ax.text(-0.15, mc, "MC", ha="right", va="center", fontsize=10)
    ax.text(Qm, -0.3, "$Q_m$", ha="center", va="top", fontsize=10)
    ax.text(Qc, -0.3, "$Q_{comp}$", ha="center", va="top", fontsize=10)
    ax.plot([Qm], [Pm], "ko", ms=4)

    style(ax)
    ax.set_title("Monopoly sets $MR=MC$, charges $P_m>MC$, and restricts output")
    legend(ax)
    save(fig, 6)


if __name__ == "__main__":
    fig1(); fig2(); fig3(); fig4(); fig5(); fig6()
    print("done")
