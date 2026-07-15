#!/usr/bin/env python3
"""Figures for M12 Ch2 §4 — Multimodal & Representation (embeddings, CLIP, VLMs).

Editable source of truth for the committed SVGs (see agent-docs/diagrams.md).
Run with the project venv:

    .venv/bin/python courses/12-model-landscape/02-beyond-text/diagrams/04-figures.py

Outputs 04-multimodal-and-representation-figN.svg into this folder.

All data is synthetic/dummy but drawn to show the *real* shape of each phenomenon
(the CLIP similarity matrix, the modality gap, the quadratic visual-token cost).
"""
import os
import numpy as np
import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

OUT = os.path.dirname(os.path.abspath(__file__))
BASE = "04-multimodal-and-representation"

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
# Fig 1 — CLIP's contrastive objective as a similarity matrix.
#   A batch of N (image, text) pairs. Cell (i, j) = cosine similarity between
#   image i and text j (after L2-normalisation, scaled by 1/temperature).
#   Training pushes the DIAGONAL (the N true pairs) up and every OFF-diagonal
#   (the N^2 - N mismatched pairs) down. This is the canonical CLIP figure.
# ---------------------------------------------------------------------------
def fig1():
    rng = np.random.default_rng(3)
    N = 8
    captions = [
        "a dog on a beach", "a red sports car", "a slice of pizza",
        "a snowy mountain", "an astronaut", "a cup of coffee",
        "a city at night", "a field of tulips",
    ]
    imgs = [f"img {i+1}" for i in range(N)]

    # Build a similarity matrix with a strong diagonal (trained model) and a
    # little realistic off-diagonal structure (some pairs are semantically closer).
    sim = rng.uniform(0.02, 0.18, size=(N, N))
    # a couple of plausible confusions (coffee<->pizza food; city<->car urban)
    sim[2, 5] = sim[5, 2] = 0.34
    sim[1, 6] = sim[6, 1] = 0.30
    np.fill_diagonal(sim, rng.uniform(0.82, 0.97, size=N))

    fig, ax = plt.subplots(figsize=(8.4, 7.0))
    im = ax.imshow(sim, cmap="magma", vmin=0, vmax=1.0, aspect="equal")

    ax.set_xticks(range(N))
    ax.set_yticks(range(N))
    ax.set_xticklabels(captions, rotation=40, ha="right", fontsize=9)
    ax.set_yticklabels(imgs, fontsize=9.5)
    ax.set_xlabel("Text encoder  →  $T_1 \\ldots T_N$")
    ax.set_ylabel("$I_1 \\ldots I_N$  ←  Image encoder")
    ax.set_title("CLIP's objective: a batch of N pairs → an N×N similarity matrix\n"
                 "maximise the N diagonal (true) pairs, minimise the N²−N off-diagonal",
                 fontsize=12.5)

    # outline the diagonal cells (the positives)
    for i in range(N):
        ax.add_patch(mpatches.Rectangle((i - 0.5, i - 0.5), 1, 1, fill=False,
                                        edgecolor="#39d353", lw=2.2, zorder=5))
        ax.text(i, i, f"{sim[i, i]:.2f}", ha="center", va="center",
                color="black", fontsize=8.5, fontweight="bold", zorder=6)

    fig.colorbar(im, ax=ax, pad=0.02, fraction=0.046,
                 label="cosine similarity  $\\langle I_i, T_j\\rangle$")
    # legend for the diagonal
    ax.plot([], [], color="#39d353", lw=2.2, label="positives (matched pair) — pushed ↑")
    ax.legend(loc="upper left", bbox_to_anchor=(0.0, -0.28), fontsize=9.5,
              frameon=False)
    fig.tight_layout()
    save(fig, 1)


# ---------------------------------------------------------------------------
# Fig 2 — the modality gap. Even after CLIP aligns image and text, the two
# encoders' outputs live in two SEPARATE cones on the unit hypersphere; a
# matched pair is *closer to each other than to random* but the whole image
# cloud and the whole text cloud are offset. (Liang et al. 2022, "Mind the Gap".)
# Shown as a 2D projection: two clusters, matched pairs connected by thin lines.
# ---------------------------------------------------------------------------
def fig2():
    rng = np.random.default_rng(11)
    N = 14
    # underlying "semantic" 2D coordinate shared by a matched pair
    theta = rng.uniform(0, 2 * np.pi, size=N)
    r = rng.uniform(0.4, 1.0, size=N)
    base = np.stack([r * np.cos(theta), r * np.sin(theta)], axis=1)

    # image and text embeddings = shared semantics + a modality-specific OFFSET
    # (the gap) + small noise. The offset is what the modality gap is.
    img_offset = np.array([1.9, 1.4])
    txt_offset = np.array([-1.9, -1.4])
    img = base + img_offset + rng.normal(0, 0.14, size=(N, 2))
    txt = base + txt_offset + rng.normal(0, 0.14, size=(N, 2))

    fig, ax = plt.subplots(figsize=(8.6, 6.6))

    # connecting lines for matched pairs
    for i in range(N):
        ax.plot([img[i, 0], txt[i, 0]], [img[i, 1], txt[i, 1]],
                color="0.75", lw=0.7, zorder=1)

    ax.scatter(img[:, 0], img[:, 1], s=90, color="#1f77b4", edgecolor="white",
               lw=0.8, zorder=3, label="image embeddings")
    ax.scatter(txt[:, 0], txt[:, 1], s=90, marker="s", color="#d62728",
               edgecolor="white", lw=0.8, zorder=3, label="text embeddings")

    # draw the two cloud centroids and the gap vector between them
    ci, ct = img.mean(0), txt.mean(0)
    ax.annotate("", xy=ci, xytext=ct,
                arrowprops=dict(arrowstyle="<->", color="#333", lw=2.0))
    mid = (ci + ct) / 2
    ax.text(mid[0] + 0.15, mid[1] + 0.35, "the modality gap\n(a constant offset\nbetween the two cones)",
            fontsize=10.5, color="#333", ha="left",
            bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="0.7", lw=0.8))

    ax.text(ci[0], ci[1] + 1.4, "image cone", ha="center", color="#1f77b4",
            fontsize=11, fontweight="bold")
    ax.text(ct[0], ct[1] - 1.5, "text cone", ha="center", color="#d62728",
            fontsize=11, fontweight="bold")

    ax.set_title("The modality gap: aligning ≠ merging.\n"
                 "Matched pairs are nearest neighbours, but image and text clouds "
                 "stay in separate regions", fontsize=12.5)
    ax.set_xlabel("embedding dim 1 (2D projection)")
    ax.set_ylabel("embedding dim 2 (2D projection)")
    ax.set_aspect("equal")
    ax.legend(loc="lower right", fontsize=10, frameon=True)
    ax.grid(ls=":", lw=0.6, color="0.9")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    save(fig, 2)


# ---------------------------------------------------------------------------
# Fig 3 — why high resolution is expensive for a VLM. An image becomes a grid
# of patches → visual tokens; token count grows with (resolution / patch)^2,
# and self-attention over the LLM's context is O(L^2) in those tokens. Two
# curves: #visual tokens vs resolution, and the relative attention cost.
# ---------------------------------------------------------------------------
def fig3():
    patch = 14  # ViT-L/14 patch size in pixels
    res = np.array([224, 336, 448, 672, 896, 1344])
    tokens = (res // patch) ** 2  # visual tokens (one per patch)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.2, 5.0))

    # (a) visual tokens vs resolution
    ax1.plot(res, tokens, "o-", color="#1f77b4", lw=2, ms=7, zorder=3)
    for x, y in zip(res, tokens):
        ax1.annotate(f"{y:,}", (x, y), textcoords="offset points",
                     xytext=(0, 9), ha="center", fontsize=9, fontweight="bold")
    ax1.set_xlabel("Input resolution (px, square)")
    ax1.set_ylabel("Visual tokens  (one per 14×14 patch)")
    ax1.set_title("(a) Tokens grow with resolution²")
    ax1.grid(ls=":", lw=0.7, color="0.85")
    ax1.spines[["top", "right"]].set_visible(False)
    ax1.annotate("common CLIP\ninput (224/336)", xy=(336, 576),
                 xytext=(250, 3600), fontsize=9, color="0.3",
                 arrowprops=dict(arrowstyle="->", color="0.5", lw=1.1))

    # (b) attention cost ~ L^2 where L = text_ctx + visual_tokens
    text_ctx = 512
    L = text_ctx + tokens
    cost = (L / L[0]) ** 2  # normalised to the smallest case
    ax2.plot(res, cost, "s-", color="#d62728", lw=2, ms=7, zorder=3)
    for x, y in zip(res, cost):
        ax2.annotate(f"{y:.0f}×", (x, y), textcoords="offset points",
                     xytext=(0, 9), ha="center", fontsize=9, fontweight="bold")
    ax2.set_xlabel("Input resolution (px, square)")
    ax2.set_ylabel("Relative self-attention cost  $O(L^2)$")
    ax2.set_title("(b) …and attention cost grows with tokens²")
    ax2.grid(ls=":", lw=0.7, color="0.85")
    ax2.spines[["top", "right"]].set_visible(False)
    ax2.text(0.5, 0.92, f"$L = {text_ctx}$ text tokens + visual tokens",
             transform=ax2.transAxes, fontsize=9.5, color="0.3", ha="center")

    fig.suptitle("Why a VLM's resolution is a compute knob: an image is patches → tokens, "
                 "and tokens cost O(L²) attention", fontsize=12.5, y=1.02)
    fig.tight_layout()
    save(fig, 3)


if __name__ == "__main__":
    fig1()
    fig2()
    fig3()
    print("done")
