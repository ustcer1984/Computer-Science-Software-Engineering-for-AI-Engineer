#!/usr/bin/env python3
"""Figure 3 — the RuO2 measurement disagreement, on one axis and one unit.

Every value is an ordered magnetic moment per Ru atom, in Bohr magnetons. The point of the
figure is that the techniques do not disagree at the edge of their error bars — they
disagree by roughly two orders of magnitude, which is what a *category* disagreement looks
like rather than a precision one.

Sources (as compiled in the 2026 review "Exploring altermagnetism in RuO2: from conflicting
experiments to emerging consensus", Nano Convergence, https://doi.org/10.1186/s40580-026-00532-6):
  * Berlijn et al., PRL 118, 077201 (2017)   — polarised neutron diffraction, bulk : ~0.05 mu_B
  * Hiraishi et al., PRL 132, 166702 (2024)  — muon spin rotation, bulk            : 4.8e-4 mu_B
  * muon spin rotation on a 12 nm film        (same review, film measurement)      : ~7.5e-4 mu_B
Iron metal (2.2 mu_B/atom) is the textbook scale bar for "an actual ferromagnet".
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROWS = [
    ("Iron metal — for scale\n(an ordinary ferromagnet)", 2.2, "#7F8C8D", "textbook value"),
    ("Polarised neutron diffraction, bulk\nBerlijn et al., PRL 2017", 0.05, "#2E86AB",
     "read as: RuO$_2$ is magnetically ordered"),
    ("Muon spin rotation, 12 nm film\n(compiled in the 2026 review)", 7.5e-4, "#C0392B",
     "read as: essentially no ordered moment"),
    ("Muon spin rotation, bulk\nHiraishi et al., PRL 2024", 4.8e-4, "#C0392B",
     "read as: essentially no ordered moment"),
]

labels = [r[0] for r in ROWS]
vals = np.array([r[1] for r in ROWS])
colors = [r[2] for r in ROWS]
notes = [r[3] for r in ROWS]

y = np.arange(len(ROWS))
fig, ax = plt.subplots(figsize=(11.4, 5.4))
ax.barh(y, vals, height=0.55, color=colors, alpha=0.9)

ax.set_xscale("log")
ax.set_xlim(1e-4, 4e3)
ax.set_yticks(y)
ax.set_yticklabels(labels, fontsize=10)
ax.invert_yaxis()

for i, (v, note) in enumerate(zip(vals, notes)):
    txt = f"{v:.3g} " + r"$\mu_{B}$/Ru" if i > 0 else f"{v:.2g} " + r"$\mu_{B}$/Fe"
    ax.text(v * 1.35, i, txt + "   ·   " + note, va="center", ha="left", fontsize=9.6)

ax.set_xlabel(r"Ordered magnetic moment per atom ($\mu_{B}$) — logarithmic axis", fontsize=11)
ax.set_title("Is RuO$_2$ magnetic at all? Two techniques, two orders of magnitude\n"
             "The flagship candidate altermagnet, measured by neutrons and by muons",
             fontsize=12.5, fontweight="bold", pad=14)

# annotate the gap
ax.annotate("", xy=(0.05, 1.42), xytext=(4.8e-4, 1.42),
            arrowprops=dict(arrowstyle="<->", color="#444444", linewidth=1.4))
ax.text(np.sqrt(0.05 * 4.8e-4), 1.66, "about 100x apart", fontsize=10.5,
        style="italic", color="#333333", ha="center")

ax.spines[["top", "right"]].set_visible(False)
ax.grid(axis="x", which="both", alpha=0.22, linewidth=0.7)
ax.set_axisbelow(True)

fig.text(0.005, 0.008,
         "Values compiled in: 'Exploring altermagnetism in RuO2: from conflicting experiments "
         "to emerging consensus', Nano Convergence (2026).",
         fontsize=8.2, color="#555555")

fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig("11-the-unpatchable-bug-and-the-third-magnet-4-plot.png", dpi=170)
print("wrote 11-the-unpatchable-bug-and-the-third-magnet-4-plot.png")
