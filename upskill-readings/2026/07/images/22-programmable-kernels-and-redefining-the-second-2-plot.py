#!/usr/bin/env python3
"""The march of clock accuracy: why the second is being redefined.

Fractional frequency uncertainty (lower = more accurate) versus year, for two
families of atomic clock:

  * MICROWAVE caesium clocks — the basis of the SI second since 1967 (the Cs-133
    hyperfine transition at 9,192,631,770 Hz). Their best realizations (caesium
    fountains) have plateaued near a few parts in 10^16: that is now the FLOOR
    of the definition itself, not a technology limit.
  * OPTICAL clocks — probing an electronic transition hundreds of THz instead of
    ~9 GHz, so a far finer "ruler." They have blown past caesium by ~two orders
    of magnitude and now reach the 10^-18 / 10^-19 regime.

The gap is the whole argument for redefinition: measurement accuracy is now
limited by the *definition* (caesium), not by the technology (optical). Points
are real published milestones; values are representative headline figures.

Emits a committed PNG next to the reading.
"""
import matplotlib.pyplot as plt

# (year, fractional uncertainty, label)  — microwave caesium family
cs = [
    (1955, 1.0e-10, "First Cs clock\n(Essen & Parry)"),
    (1993, 1.0e-14, "NIST-7"),
    (1999, 1.0e-15, "NIST-F1 fountain"),
    (2014, 1.0e-16, "NIST-F2"),
]
# (year, fractional uncertainty, label) — optical family
opt = [
    (2006, 1.0e-16, "early optical (Hg+)"),
    (2010, 8.6e-18, "Al+ quantum logic"),
    (2015, 2.1e-18, "JILA Sr lattice"),
    (2019, 9.4e-19, "NIST Al+ (2019)"),
    (2025, 5.5e-19, "NIST Al+ 2025\nworld record"),
]

fig, ax = plt.subplots(figsize=(8.6, 5.4), dpi=150)

# Caesium floor band (the "definition floor")
ax.axhspan(7e-17, 3e-16, color="#0466c8", alpha=0.08, zorder=0)
ax.text(1990, 2.4e-16, "caesium floor — a few parts in $10^{16}$\n(the limit of the *definition*, not the technology)",
        fontsize=8.2, color="#0466c8", va="center", ha="center", style="italic")

# Redefinition target band
ax.axhspan(1e-19, 1e-18, color="#c1121f", alpha=0.07, zorder=0)
ax.text(2028, 3e-19, "optical regime\n$10^{-18}$–$10^{-19}$", fontsize=8.6,
        color="#c1121f", ha="right", va="center", fontweight="bold")

# Series
cx, cy, _ = zip(*cs)
ox, oy, _ = zip(*opt)
ax.plot(cx, cy, "-o", color="#0466c8", lw=2.2, ms=7, zorder=3,
        label="microwave caesium (basis of the SI second)")
ax.plot(ox, oy, "-s", color="#c1121f", lw=2.2, ms=7, zorder=3,
        label="optical clocks (the challenger)")

# Point labels — caesium below-right of each point (downward = larger y on inverted axis)
for x, y, name in cs:
    ax.annotate(name, xy=(x, y), xytext=(x + 1.2, y * 3.0), fontsize=7.6,
                color="#023e8a", ha="left")

# Point labels — optical, each placed below its marker with a manual offset to avoid collisions
opt_lab = {
    2006: (2003.5, 2.4e-17, "right", "early optical (Hg+)"),
    2010: (2010.6, 4.5e-17, "left", "Al+ quantum logic"),
    2015: (2015.6, 1.1e-17, "left", "JILA Sr lattice"),
    2019: (2018.4, 3.4e-18, "right", "NIST Al+ (2019)"),
    2025: (2024.4, 2.0e-18, "right", "NIST Al+ 2025\nworld record"),
}
for x, y, name in opt:
    lx, ly, ha, txt = opt_lab[x]
    ax.annotate(txt, xy=(x, y), xytext=(lx, ly), fontsize=7.7,
                color="#7a0b16", ha=ha, va="center",
                fontweight="bold" if "record" in txt else "normal")

# Callout: the 2025 record in human terms — parked in the empty upper-middle
ax.annotate("wouldn't gain or lose a second\nin ~40 billion years\n(≈ 3× the age of the universe)",
            xy=(2025, 5.5e-19), xytext=(1980, 7e-18), fontsize=8.8,
            color="#c1121f", ha="center", va="center", fontweight="bold",
            arrowprops=dict(arrowstyle="->", color="#c1121f", lw=1.2, alpha=0.7,
                            connectionstyle="arc3,rad=-0.28"))

ax.legend(loc="lower right", fontsize=9.5, framealpha=0.92)

ax.set_yscale("log")
ax.invert_yaxis()  # better (smaller) uncertainty toward the top
ax.set_xlabel("Year", fontsize=11)
ax.set_ylabel("Fractional frequency uncertainty  (smaller = better; log, inverted)", fontsize=10.5)
ax.set_title("Two orders of magnitude of headroom: why the SI second is being redefined",
             fontsize=12.5, fontweight="bold", pad=12)
ax.grid(True, which="both", ls=":", alpha=0.4)
ax.set_xlim(1953, 2030)

fig.text(0.5, 0.005,
         "Real published milestones; values are representative headline figures. Optical clocks (probing ~hundreds of THz "
         "instead of caesium's ~9 GHz) now beat the caesium definition by ~100×, so the definition itself has become the bottleneck.",
         ha="center", fontsize=7.3, color="#666", style="italic", wrap=True)

fig.tight_layout(rect=(0, 0.035, 1, 1))
out = __file__.rsplit("/", 1)[0] + "/22-programmable-kernels-and-redefining-the-second-2-plot.png"
fig.savefig(out, bbox_inches="tight", facecolor="white")
print("wrote", out)
