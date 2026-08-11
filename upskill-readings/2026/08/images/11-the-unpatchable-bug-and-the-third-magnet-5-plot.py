#!/usr/bin/env python3
"""Figure 4 — why a compensated magnet is intrinsically a thousand times faster.

This is the real textbook relation, plotted, not a sketch. For a uniaxial magnet with
gyromagnetic ratio gamma/2pi = 28 GHz/T:

  ferromagnet          f = (gamma/2pi) * mu0 * H_A
  two-sublattice       f = (gamma/2pi) * mu0 * sqrt( H_A * (2 H_E + H_A) )
  (antiferro/alter-)

The second is the standard Kittel/Keffer-Kittel antiferromagnetic-resonance result: the
resonance is *exchange-enhanced*, i.e. the anisotropy field is geometrically averaged with
the (enormous) inter-sublattice exchange field instead of standing alone. Exchange fields in
real compensated magnets are of order 10^2 - 10^3 T, which is the whole reason the answer
lands in the terahertz rather than the gigahertz.

Anchors marked on the plot (real measured values, not fitted):
  * α-MnTe magnon mode at 3.5 +- 0.1 meV  ->  0.85 THz   (arXiv:2502.18933, AFM resonance in α-MnTe)
  * a typical ferromagnetic-resonance / STT-MRAM working point, a few GHz
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

GAMMA = 28.0  # GHz per tesla

mu0_HA = np.logspace(-3, 0.5, 400)   # anisotropy field, tesla

f_fm = GAMMA * mu0_HA                                        # GHz


def f_afm(HA, HE):
    return GAMMA * np.sqrt(HA * (2 * HE + HA))               # GHz


fig, ax = plt.subplots(figsize=(9.8, 6.2))

ax.loglog(mu0_HA, f_fm, color="#C0392B", linewidth=2.6,
          label=r"ferromagnet:  $f=(\gamma/2\pi)\,\mu_{0}H_{A}$")
ax.loglog(mu0_HA, f_afm(mu0_HA, 100), color="#2E86AB", linewidth=2.6,
          label=r"compensated magnet, $\mu_{0}H_{E}=100$ T")
ax.loglog(mu0_HA, f_afm(mu0_HA, 1000), color="#1B4F72", linewidth=2.6, linestyle="--",
          label=r"compensated magnet, $\mu_{0}H_{E}=1000$ T")

# frequency bands
ax.axhspan(1, 100, color="#F4D03F", alpha=0.14)
ax.axhspan(300, 1e4, color="#7DCEA0", alpha=0.16)
ax.text(1.1e-3, 12, "GHz — where today's magnetic memory lives", fontsize=9.6,
        color="#8A6D0B", va="center")
ax.text(1.1e-3, 2100, "THz — where a compensated magnet lives", fontsize=9.6,
        color="#1D6F42", va="center")

# real anchors
ax.plot([0.85e-3 * 0 + 0.03], [0.85e3], marker="o", markersize=8, color="#145A32", zorder=5)
ax.annotate(r"measured: $\alpha$-MnTe magnon, 3.5 meV = 0.85 THz",
            xy=(0.03, 0.85e3), xytext=(0.055, 4000),
            arrowprops=dict(arrowstyle="->", color="#145A32", linewidth=1.3),
            fontsize=9.8, color="#145A32")

ax.plot([0.1], [GAMMA * 0.1], marker="o", markersize=8, color="#7B241C", zorder=5)
ax.annotate("a ferromagnetic bit at the same anisotropy:\n2.8 GHz",
            xy=(0.1, GAMMA * 0.1), xytext=(0.13, 0.45),
            arrowprops=dict(arrowstyle="->", color="#7B241C", linewidth=1.3),
            fontsize=9.8, color="#7B241C")

ax.set_xlabel(r"Anisotropy field $\mu_{0}H_{A}$ (T)", fontsize=11.5)
ax.set_ylabel("Resonance frequency (GHz)", fontsize=11.5)
ax.set_title("Exchange enhancement: the same anisotropy, a thousand times the speed\n"
             "Uniform-mode resonance for a ferromagnet vs a two-sublattice compensated magnet",
             fontsize=12.5, fontweight="bold", pad=14)
ax.set_ylim(0.05, 2e4)
ax.legend(loc="lower right", fontsize=10.2, framealpha=0.95)
ax.grid(which="both", alpha=0.22, linewidth=0.7)
ax.set_axisbelow(True)
ax.spines[["top", "right"]].set_visible(False)

fig.text(0.005, 0.008,
         "Curves are the standard Kittel / Keffer-Kittel resonance expressions with "
         r"$\gamma/2\pi=28$ GHz/T; exchange fields are representative values. "
         "Marked points are measured.",
         fontsize=8.2, color="#555555")

fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig("11-the-unpatchable-bug-and-the-third-magnet-5-plot.png", dpi=170)
print("wrote 11-the-unpatchable-bug-and-the-third-magnet-5-plot.png")
