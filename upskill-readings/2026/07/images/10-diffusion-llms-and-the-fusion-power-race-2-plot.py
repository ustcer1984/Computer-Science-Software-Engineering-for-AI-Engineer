#!/usr/bin/env python3
"""Fusion power density vs on-axis magnetic field: the B^4 law.

Why compact fusion suddenly looks plausible. In a tokamak the fusion power
density scales like the FOURTH power of the on-axis toroidal field, P ∝ B^4.
Low-temperature superconductors (ITER) cap the on-axis field near ~5 T; the
REBCO high-temperature-superconductor tape CFS/MIT ran to a record 20 T magnet
(Sept 2021) lets SPARC reach ~12 T on-axis. Normalizing ITER = 1, that is
(12.2/5.3)^4 ≈ 28x the power density in the same volume — the whole reason a
SPARC-sized machine can chase ITER-class physics.

Emits a committed PNG next to the reading. Real curve, illustrative points.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager

B_ITER = 5.3    # ITER on-axis toroidal field (T)
B_SPARC = 12.2  # SPARC on-axis toroidal field (T)

# P ∝ B^4, normalized so ITER = 1
B = np.linspace(3.0, 14.0, 400)
P = (B / B_ITER) ** 4

fig, ax = plt.subplots(figsize=(8.4, 5.2), dpi=150)

ax.plot(B, P, color="#c1121f", lw=2.6, zorder=3,
        label=r"$P \propto B^{4}$  (fusion power density)")

# Reference machines
for Bx, name, py, color, dx in [
    (B_ITER, "ITER\n~5.3 T on-axis\n(low-temp superconductor)", (B_ITER/B_ITER)**4, "#0466c8", 0.25),
    (B_SPARC, "SPARC\n~12.2 T on-axis\n(HTS REBCO tape)", (B_SPARC/B_ITER)**4, "#023e8a", -0.15),
]:
    py = (Bx / B_ITER) ** 4
    ax.scatter([Bx], [py], s=90, color=color, zorder=5, edgecolor="white", lw=1.2)
    ax.annotate(name, xy=(Bx, py), xytext=(Bx + dx, py * (2.2 if Bx == B_ITER else 0.42)),
                fontsize=9.5, color=color, fontweight="bold",
                ha="left" if Bx == B_ITER else "right",
                arrowprops=dict(arrowstyle="-", color=color, lw=1.0, alpha=0.6))

ratio = (B_SPARC / B_ITER) ** 4
ax.annotate(f"≈ {ratio:.0f}× the power density\nof ITER, in the same volume",
            xy=(B_SPARC, ratio), xytext=(9.6, 0.55),
            fontsize=10.5, color="#c1121f", ha="center", va="center",
            fontweight="bold",
            arrowprops=dict(arrowstyle="->", color="#c1121f", lw=1.3, alpha=0.75,
                            connectionstyle="arc3,rad=0.25"))

ax.set_yscale("log")
ax.set_xlabel("On-axis magnetic field  B  (tesla)", fontsize=11)
ax.set_ylabel("Relative fusion power density  (ITER = 1, log scale)", fontsize=11)
ax.set_title("Why a ribbon of tape shrank the reactor: the $B^{4}$ law",
             fontsize=13, fontweight="bold", pad=12)
ax.grid(True, which="both", ls=":", alpha=0.4)
ax.set_xlim(3, 14)
ax.set_ylim(0.05, 60)
ax.legend(loc="upper left", fontsize=10, framealpha=0.9)

fig.text(0.5, 0.005,
         "Curve is the textbook P ∝ B⁴ scaling; machine points are illustrative on-axis fields. "
         "Higher field → dramatically more power in the same volume, so a higher-field magnet means a smaller reactor.",
         ha="center", fontsize=7.5, color="#666", style="italic")

fig.tight_layout(rect=(0, 0.03, 1, 1))
out = __file__.rsplit("/", 1)[0] + "/10-diffusion-llms-and-the-fusion-power-race-2-plot.png"
fig.savefig(out, bbox_inches="tight", facecolor="white")
print("wrote", out)
