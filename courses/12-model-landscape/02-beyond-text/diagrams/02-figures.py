#!/usr/bin/env python3
"""Figures for M12 Ch2 §2 — Video Generation & World Models.

Editable source of truth for the committed SVGs (see agent-docs/diagrams.md).
Run with the project venv:

    .venv/bin/python courses/12-model-landscape/02-beyond-text/diagrams/02-figures.py

Outputs 02-video-and-world-models-figN.svg into this folder.
"""
import os
import numpy as np
import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D

OUT = os.path.dirname(os.path.abspath(__file__))
BASE = "02-video-and-world-models"

plt.rcParams.update({
    "font.size": 12,
    "axes.titlesize": 13,
    "axes.labelsize": 12,
    "svg.fonttype": "none",
    "figure.dpi": 100,
})


def save(fig, n):
    path = os.path.join(OUT, f"{BASE}-fig{n}.svg")
    fig.savefig(path, format="svg", bbox_inches="tight")
    plt.close(fig)
    print("wrote", path)


# ---------------------------------------------------------------------------
# Fig 1 — Flow Matching vs DDPM trajectories in 2D latent space.
#
# Shows N sample paths from noise → data.
#   Left:  DDPM — many small steps, stochastic perturbations → curved paths.
#   Right: Flow Matching — few steps, straight-line interpolant → direct paths.
# ---------------------------------------------------------------------------
def fig1():
    rng = np.random.default_rng(42)
    N = 8

    # Data cluster (top-right) and noise cluster (centered at origin).
    data  = rng.standard_normal((N, 2)) * 0.35 + np.array([2.4, 1.8])
    noise = rng.standard_normal((N, 2)) * 1.1

    T_ddpm = 30   # number of DDPM steps shown
    T_fm   = 5    # number of FM steps shown

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(11.0, 5.0))

    colors = plt.cm.tab10(np.linspace(0, 0.9, N))

    for i in range(N):
        n, d = noise[i], data[i]
        c = colors[i]

        # ---- DDPM (left): straight interpolant + Brownian bridge perturbation ----
        t_d = np.linspace(0, 1, T_ddpm + 1)
        straight_d = np.outer(1 - t_d, n) + np.outer(t_d, d)
        # Brownian bridge noise: zero at endpoints, max std in the middle
        sigma = 0.28 * np.sqrt(t_d * (1 - t_d))
        perturb = rng.standard_normal((T_ddpm + 1, 2)) * sigma[:, None]
        # Pin endpoints to zero perturbation
        perturb[0]  = 0.0
        perturb[-1] = 0.0
        path_ddpm = straight_d + perturb

        axL.plot(path_ddpm[:, 0], path_ddpm[:, 1],
                 "-", lw=1.0, alpha=0.65, color=c)
        axL.plot(path_ddpm[::5, 0], path_ddpm[::5, 1],
                 ".", ms=3.5, alpha=0.65, color=c)
        # Start (noise) and end (data) markers
        axL.plot(*n, "o", ms=6, color=c, markeredgecolor="white", markeredgewidth=0.6)
        axL.plot(*d, "s", ms=6, color=c, markeredgecolor="white", markeredgewidth=0.6)

        # ---- Flow Matching (right): straight-line steps ----
        t_f = np.linspace(0, 1, T_fm + 1)
        path_fm = np.outer(1 - t_f, n) + np.outer(t_f, d)

        axR.plot(path_fm[:, 0], path_fm[:, 1],
                 "-", lw=1.6, alpha=0.75, color=c)
        axR.plot(path_fm[:, 0], path_fm[:, 1],
                 ".", ms=6, alpha=0.75, color=c)
        axR.plot(*n, "o", ms=7, color=c, markeredgecolor="white", markeredgewidth=0.6)
        axR.plot(*d, "s", ms=7, color=c, markeredgecolor="white", markeredgewidth=0.6)

    # Shared formatting
    for ax, title, nfe in [
        (axL, "DDPM  (30 steps shown)", "~30 steps / 100–1000 NFE in practice"),
        (axR, "Flow Matching  (5 steps shown)", "4–8 NFE in practice"),
    ]:
        ax.set_xlim(-3.2, 4.0)
        ax.set_ylim(-3.2, 4.0)
        ax.set_xlabel("Latent $z_1$")
        ax.set_ylabel("Latent $z_2$")
        ax.set_title(title, pad=6)
        ax.text(0.50, 0.03, nfe, transform=ax.transAxes,
                ha="center", va="bottom", fontsize=9.5,
                color="#444444",
                bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="0.7", lw=0.8))
        ax.spines[["top", "right"]].set_visible(False)
        ax.set_xticks([]); ax.set_yticks([])

    # Legend
    noise_patch = Line2D([0], [0], marker="o", color="w", markerfacecolor="#555",
                         markersize=7, label="Noise sample (start)")
    data_patch  = Line2D([0], [0], marker="s", color="w", markerfacecolor="#555",
                         markersize=7, label="Data sample (end)")
    axL.legend(handles=[noise_patch, data_patch], loc="upper left",
               fontsize=9, frameon=True, facecolor="white", edgecolor="0.8")

    fig.suptitle("Sampling trajectories: DDPM vs Flow Matching\n"
                 "Same (noise, data) pairs — same start, same destination",
                 fontsize=13, y=1.02)
    fig.tight_layout()
    save(fig, 1)


# ---------------------------------------------------------------------------
# Fig 2 — Video generation model capability timeline 2022–2025.
#
# Scatter: year (x) vs maximum clip length at release (y, log scale).
# Annotated with model names and colour-coded by architecture era.
# ---------------------------------------------------------------------------
def fig2():
    # (name, year, max_seconds, era)
    # era: 0 = 3D U-Net, 1 = U-Net large-scale, 2 = DiT / FM
    models = [
        ("VDM\n(Ho 2022)",          2022.2,  0.65,  0),   # 16 frames @ ~24fps → ~0.67s
        ("Imagen Video\n(Google)",  2022.9,  5.3,   0),
        ("Gen-1\n(Runway)",         2023.1,  4.0,   0),
        ("AnimateDiff",             2023.4,  1.3,   0),    # 32 frames @ 24fps
        ("SVD\n(Stability)",        2023.11, 1.0,   0),    # 25 frames
        ("Gen-2\n(Runway)",         2023.5,  4.0,   0),
        ("Sora\n(OpenAI)",          2024.2,  60.0,  2),
        ("CogVideoX",               2024.8,  6.0,   2),
        ("HunyuanVideo\n(Tencent)", 2024.11, 5.0,   2),
        ("Veo 2\n(Google)",         2024.12, 60.0,  2),
        ("WAN 2.1\n(Alibaba)",      2025.2,  3.4,   2),    # 81 frames @ 24fps
        ("Kling 2.0\n(Kuaishou)",   2025.5, 180.0,  2),
    ]

    era_colors = {0: "#1f77b4", 2: "#d62728"}
    era_labels = {0: "3D U-Net era", 2: "DiT + Flow Matching era"}

    fig, ax = plt.subplots(figsize=(10.0, 5.5))

    for name, year, secs, era in models:
        c = era_colors[era]
        ax.scatter(year, secs, color=c, s=80, zorder=5,
                   edgecolors="white", linewidths=0.7)
        # offset labels to avoid collisions
        offsets = {
            "VDM\n(Ho 2022)":          (-0.12, -0.5),
            "Imagen Video\n(Google)":  (+0.06, +0.0),
            "Gen-1\n(Runway)":         (+0.06, -0.0),
            "AnimateDiff":             (-0.28, +0.1),
            "SVD\n(Stability)":        (+0.06,  0.0),
            "Gen-2\n(Runway)":         (+0.06, -0.0),
            "Sora\n(OpenAI)":          (+0.06, +0.0),
            "CogVideoX":               (+0.06, +0.0),
            "HunyuanVideo\n(Tencent)": (+0.06, +0.0),
            "Veo 2\n(Google)":         (-0.28, +0.0),
            "WAN 2.1\n(Alibaba)":      (+0.06, +0.0),
            "Kling 2.0\n(Kuaishou)":   (+0.06, +0.0),
        }
        dx, dy = offsets.get(name, (0.06, 0.0))
        ax.annotate(name, (year, secs),
                    xytext=(year + dx, secs * (1.4 if dy >= 0 else 0.7)),
                    fontsize=8.5, color=c,
                    ha="left" if dx >= 0 else "right",
                    arrowprops=dict(arrowstyle="-", color=c, lw=0.7) if abs(dx) > 0.1 else None)

    ax.set_yscale("log")
    ax.set_ylim(0.3, 600)
    ax.set_xlim(2021.8, 2025.9)
    ax.set_xlabel("Year")
    ax.set_ylabel("Maximum clip length at release (seconds, log scale)")
    ax.set_title("Video generation: max clip length at release (2022–2025)")
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(
        lambda x, _: f"{int(x)}s" if x >= 1 else f"{x:.1f}s"
    ))
    ax.grid(axis="y", ls=":", lw=0.7, color="0.85")
    ax.spines[["top", "right"]].set_visible(False)

    legend_handles = [
        mpatches.Patch(color=era_colors[0], label=era_labels[0]),
        mpatches.Patch(color=era_colors[2], label=era_labels[2]),
    ]
    ax.legend(handles=legend_handles, loc="upper left",
              fontsize=10, frameon=True, facecolor="white", edgecolor="0.8")

    fig.tight_layout()
    save(fig, 2)


if __name__ == "__main__":
    fig1()
    fig2()
    print("done")
