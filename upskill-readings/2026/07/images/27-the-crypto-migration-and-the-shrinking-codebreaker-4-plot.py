#!/usr/bin/env python3
"""The scissors: the codebreaking machine shrinks faster than real machines grow.

TWO CURVES, deliberately plotted together — and deliberately NOT the same unit.

  (a) FALLING — published resource estimates for the number of noisy PHYSICAL
      qubits needed to break RSA-2048 (or, where marked, ECC-256) with Shor's
      algorithm. This curve moved almost entirely because of THEORY: better
      arithmetic, magic-state cultivation instead of distillation factories,
      and quantum LDPC codes instead of the surface code.

        2012  ~1e9        first serious surface-code costings
        2019   2.0e7      Gidney & Ekera, 8 hours
        2025   1.0e6      Gidney, "less than a million noisy qubits", <1 week
        2026.1 1.0e5      Iceberg Quantum, qLDPC — SIMULATION, not hardware
        2026.25 1.0e4     Cain et al., reconfigurable atoms (see runtime caveat)

  (b) RISING — the largest quantum processor / coherent qubit array actually
      announced. RAW qubits, none of them error-corrected.

        2016    5    IBM Quantum Experience
        2017   20    IBM Q
        2018   72    Google Bristlecone
        2021  127    IBM Eagle
        2022  433    IBM Osprey
        2023 1121    IBM Condor
        2025 6100    Caltech tweezer array (Nature, Sept 2025)

THE CAVEAT IS THE POINT. The curves nearly touch, and that is misleading: the
falling curve counts FAULT-TOLERANT qubits (below-threshold two-qubit gates,
mid-circuit measurement, real-time decoding, sustained for the whole run) while
the rising curve counts atoms that merely hold a state. Read the runtime
annotations too — 10,000 qubits buys ECC-256 in ~3 years, not in an afternoon.

Emits a committed PNG next to the reading.
"""
import matplotlib.pyplot as plt

est = [
    (2012.0, 1.0e9, "~$10^9$ qubits\n(2012 surface-code costing)"),
    (2019.0, 2.0e7, "20 million\nGidney–Ekerå, 8 hours"),
    (2025.4, 1.0e6, "<1 million\nGidney, under a week"),
    (2026.1, 1.0e5, "<100,000\nIceberg (simulation)"),
    (2026.25, 1.0e4, "10,000 atoms\nCain et al."),
]

hw = [
    (2016.0, 5, "IBM 5q"),
    (2017.0, 20, None),
    (2018.2, 72, "Google\nBristlecone 72"),
    (2021.9, 127, None),
    (2022.9, 433, "IBM Osprey 433"),
    (2023.9, 1121, "IBM Condor 1121"),
    (2025.73, 6100, "Caltech 6,100-atom\ntweezer array"),
]

fig, ax = plt.subplots(figsize=(9.6, 6.0), dpi=150)

ex = [p[0] for p in est]
ey = [p[1] for p in est]
hx = [p[0] for p in hw]
hy = [p[1] for p in hw]

# The shrinking gap, shaded
ax.fill_between([2016, 2026.25], [1e9, 1e4], [5, 6100], color="#888", alpha=0.07, zorder=0)
ax.text(2017.9, 2e6, "THE GAP\n(shrinking from both ends,\nbut mostly from the top)",
        fontsize=9.5, color="#555", ha="center", va="center", style="italic")

ax.plot(ex, ey, "-o", color="#c1121f", lw=2.6, ms=9, zorder=4,
        label="physical qubits ESTIMATED to break RSA-2048 (falls by theory)")
ax.plot(hx, hy, "-s", color="#0466c8", lw=2.6, ms=8, zorder=4,
        label="largest quantum processor BUILT (raw qubits, not error-corrected)")

est_lab = {
    2012.0: (2012.4, 3.2e9, "left"),
    2019.0: (2019.5, 8.0e7, "left"),
    2025.4: (2025.2, 1.5e7, "center"),
    2026.1: (2024.9, 3.0e5, "right"),
    2026.25: (2026.65, 9.0e3, "left"),
}
for x, y, lab in est:
    lx, ly, ha = est_lab[x]
    ax.annotate(lab, xy=(x, y), xytext=(lx, ly), fontsize=8.4, color="#7a0b16",
                ha=ha, va="center", fontweight="bold")

hw_lab = {
    2016.0: (2015.7, 2.4, "left"),
    2018.2: (2017.3, 220, "left"),
    2022.9: (2023.3, 165, "left"),
    2023.9: (2022.9, 3000, "left"),
    2025.73: (2024.1, 3.0e4, "right"),
}
for x, y, lab in hw:
    if lab is None:
        continue
    lx, ly, ha = hw_lab[x]
    ax.annotate(lab, xy=(x, y), xytext=(lx, ly), fontsize=8.2, color="#023e8a",
                ha=ha, va="center")

# The two honest caveats, parked in a clean right-hand column
ax.annotate("these are DIFFERENT UNITS:\nfault-tolerant qubits above,\nraw atoms below",
            xy=(2026.15, 1.5e5), xytext=(2029.9, 8.0e6), fontsize=9.0,
            color="#c1121f", ha="center", va="center", fontweight="bold",
            arrowprops=dict(arrowstyle="->", color="#c1121f", lw=1.3, alpha=0.75,
                            connectionstyle="arc3,rad=0.25"))

ax.annotate("and read the RUNTIME:\n10,000 qubits → ECC-256 in ~3 years\n"
            "26,000 → ECC-256 in ~10 days\n100,000 → RSA-2048 in ~97 days",
            xy=(2026.55, 6.5e3), xytext=(2029.9, 80), fontsize=8.4,
            color="#444", ha="center", va="center",
            bbox=dict(boxstyle="round,pad=0.45", fc="#fffbe6", ec="#b58900", lw=1.0),
            arrowprops=dict(arrowstyle="->", color="#b58900", lw=1.2, alpha=0.8,
                            connectionstyle="arc3,rad=0.2"))

ax.set_yscale("log")
ax.set_xlim(2011, 2033.2)
ax.set_ylim(1.4, 4e10)
ax.set_xticks([2012, 2014, 2016, 2018, 2020, 2022, 2024, 2026])
ax.set_xlabel("Year", fontsize=11)
ax.set_ylabel("Physical qubits (log scale)", fontsize=11)
ax.set_title("Five orders of magnitude of it came from paper, not silicon",
             fontsize=13.5, fontweight="bold", pad=12)
ax.grid(True, which="both", ls=":", alpha=0.38)
ax.legend(loc="lower left", fontsize=9.3, framealpha=0.94)

fig.text(0.5, 0.005,
         "Published resource estimates vs announced processor sizes. The estimate curve fell about 10^5 in 14 years — roughly a "
         "halving every ten months, faster than Moore's law — driven by better algorithms, magic-state cultivation and qLDPC codes, "
         "not by hardware. The remaining gap is not the factor of ~1.6 the chart appears to show.",
         ha="center", fontsize=7.3, color="#666", style="italic", wrap=True)

fig.tight_layout(rect=(0, 0.045, 1, 1))
out = __file__.rsplit("/", 1)[0] + "/27-the-crypto-migration-and-the-shrinking-codebreaker-4-plot.png"
fig.savefig(out, bbox_inches="tight", facecolor="white")
print("wrote", out)
