#!/usr/bin/env python3
"""Why the channel has to stop being silicon: mobility versus body thickness.

THE RELATIONSHIP BEING PLOTTED. To keep electrostatic control of a very short
channel, the conducting body must be made thinner than the channel is long
(roughly t_body < L_g / 3). For silicon that is a trap: below ~4 nm the carriers
are squeezed against two rough interfaces and mobility collapses. The measured
and modelled dependence is brutally steep — Uchida et al. (IEDM 2002 and after)
report an effective mobility falling roughly as

        mu ∝ t_body^6

in the ultrathin-body regime, driven by surface-roughness and thickness-
fluctuation scattering (a 1-atom step in a 3 nm film is a 10% thickness change).

A transition-metal dichalcogenide monolayer escapes the trap by construction,
not by cleverness: the film is a single crystalline layer ~0.65 nm thick with no
dangling bonds and no roughness to fluctuate, so mobility is set by the material
rather than by the thickness.

WHAT IS MODEL AND WHAT IS MEASURED — read this before reading the chart.

  * The silicon curve is a NORMALISED SCALING LAW, not a measurement series:
    mu(t) = mu_thick * min(1, (t / 5 nm)^6), anchored at a nominal thick-body
    mu_thick = 300 cm^2/V/s. The exponent is the reported one; the anchor is
    illustrative. The shape is the point, not the absolute values.

  * The 2D points ARE measurements, each labelled with its source:
      - 123 cm^2/V/s : best FET on 6-inch single-crystal MoS2 grown by
        oxy-MOCVD, Science, 30 Jan 2026 (doi 10.1126/science.aec7259);
        the paper reports average mobility above 100.
      - ~30 cm^2/V/s : typical range for 300 mm fab-grown / transferred
        monolayer MoS2 channels in integration work of this generation.
      - the shaded band is the theoretical phonon-limited ceiling for
        monolayer MoS2 quoted in the literature (~200-400 cm^2/V/s).

Emits a committed PNG next to the reading.
"""
import matplotlib.pyplot as plt
import numpy as np

MU_THICK = 300.0   # cm^2/V/s, illustrative anchor for a thick silicon body
T_KNEE = 5.0       # nm, where the t^6 collapse takes over

t = np.linspace(0.6, 12.0, 600)
mu_si = MU_THICK * np.minimum(1.0, (t / T_KNEE) ** 6)

fig, ax = plt.subplots(figsize=(9.8, 6.0), dpi=150)

ax.plot(t, mu_si, lw=2.6, color="#2c5f8a", zorder=4,
        label=r"silicon body — scaling law $\mu \propto t^{6}$ (model)")

# the phonon-limited ceiling for a monolayer TMD
ax.axhspan(200, 400, color="#5aa469", alpha=0.14, zorder=1)
ax.text(11.8, 470, "green band = theoretical phonon-limited ceiling\nfor a monolayer MoS$_2$ channel", fontsize=9,
        color="#3f7a4d", ha="right", va="center")

# TMD monolayer: thickness-independent, plotted as a horizontal guide
ax.plot([0.6, 12.0], [123, 123], lw=2.2, ls="--", color="#c2451e", zorder=4,
        label="monolayer MoS$_2$ — thickness is fixed at ~0.65 nm (measured)")
ax.plot([0.65], [123], "o", ms=11, color="#c2451e", zorder=6)
ax.annotate("6-inch single-crystal MoS$_2$, oxy-MOCVD\n123 cm$^2$/V/s  (Science, Jan 2026)",
            xy=(0.65, 123), xytext=(1.9, 620), fontsize=9.5, color="#8f2f12",
            arrowprops=dict(arrowstyle="-|>", color="#8f2f12", lw=1.2))
ax.plot([0.65], [30], "o", ms=8, mfc="#ffffff", mec="#c2451e", mew=2.0, zorder=6)
ax.annotate("typical 300 mm integrated\nmonolayer channel, ~30",
            xy=(0.65, 30), xytext=(1.5, 45), fontsize=9, color="#8f2f12",
            arrowprops=dict(arrowstyle="-|>", color="#8f2f12", lw=1.0))

# where silicon dies
for tt in (4.0, 3.0, 2.0):
    mu = MU_THICK * min(1.0, (tt / T_KNEE) ** 6)
    ax.plot([tt], [mu], "s", ms=7, color="#2c5f8a", zorder=6)
    ax.annotate(f"{tt:.0f} nm Si\n{mu:.0f}", xy=(tt, mu), xytext=(tt + 0.35, mu * 0.42),
                fontsize=8.8, color="#1b3d57",
                arrowprops=dict(arrowstyle="-", color="#1b3d57", lw=0.8, alpha=0.6))

ax.axvline(0.65, color="#c2451e", lw=1.0, ls=":", alpha=0.7)
ax.text(0.70, 0.55, "one monolayer\n0.65 nm", fontsize=9, color="#8f2f12", va="bottom")

ax.set_yscale("log")
ax.set_xlim(0.4, 12.0)
ax.set_ylim(0.3, 900)
ax.set_xlabel("channel body thickness  $t$  (nm)", fontsize=11.5)
ax.set_ylabel("effective carrier mobility  (cm$^2$ V$^{-1}$ s$^{-1}$, log scale)", fontsize=11.5)
ax.set_title("The trap silicon cannot get out of, and the way a monolayer sidesteps it\n"
             "thin enough to control a short channel = too thin for silicon to conduct well",
             fontsize=12.5, fontweight="bold", loc="left")
ax.grid(which="major", ls=":", color="#bbbbbb", alpha=0.8)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.legend(loc="lower right", fontsize=9.8, framealpha=0.95)

fig.text(0.005, 0.005,
         "Silicon curve: normalised $t^{6}$ ultrathin-body scaling (Uchida et al.), illustrative anchor of 300 cm$^2$/V/s — "
         "shape, not absolute values. 2D points are measurements (see the script for sources).",
         fontsize=8.0, color="#777777")
fig.tight_layout(rect=(0, 0.03, 1, 1))
out = __file__.replace("-plot.py", "-plot.png")
fig.savefig(out, bbox_inches="tight")
print(out)
