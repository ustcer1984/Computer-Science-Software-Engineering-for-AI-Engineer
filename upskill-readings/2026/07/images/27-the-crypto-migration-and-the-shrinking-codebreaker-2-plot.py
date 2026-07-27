#!/usr/bin/env python3
"""The quietest protocol transition in internet history.

Share of human-initiated HTTPS request traffic reaching Cloudflare that is
protected by POST-QUANTUM (hybrid X25519 + ML-KEM-768) key agreement.

Points are figures Cloudflare has published:
  * early 2024  —  1.8%   ("The state of the post-quantum Internet", 2024)
  * Jan 2025    —  29%    (Radar 2025 Year in Review: "29% at the start of the year")
  * late Oct 25 —  >50%   ("majority of human traffic", pq-2025 blog)
  * early Dec 25 - 52%    (Radar 2025 Year in Review)
  * June 2026   —  ~67%   ("over two-thirds of browser traffic", post-quantum EO blog)

The connecting line is interpolation between reported figures, not a continuous
measurement series. The point of the chart is the SHAPE: a core internet
primitive was replaced under everybody's feet in about two years, with no user
-visible event of any kind.

Emits a committed PNG next to the reading.
"""
import matplotlib.pyplot as plt

# (decimal year, percent, is_reported)
pts = [
    (2024.12, 1.8, "1.8%\n(early 2024)"),
    (2025.00, 29.0, "29%\n(Jan 2025)"),
    (2025.82, 50.0, "crosses 50%\n(late Oct 2025)"),
    (2025.93, 52.0, None),
    (2026.47, 67.0, "over two-thirds\n(June 2026)"),
]

fig, ax = plt.subplots(figsize=(9.0, 5.2), dpi=150)

xs = [p[0] for p in pts]
ys = [p[1] for p in pts]

ax.fill_between(xs, ys, color="#0466c8", alpha=0.10, zorder=1)
ax.plot(xs, ys, "-o", color="#0466c8", lw=2.4, ms=8, zorder=3,
        label="hybrid post-quantum key agreement (X25519MLKEM768)")

# The half-way line — the "majority" milestone
ax.axhline(50, color="#555", ls="--", lw=1.0, alpha=0.55, zorder=2)
ax.text(2023.98, 51.4, "majority of human web traffic", fontsize=8.2,
        color="#555", style="italic", va="bottom")

# Reported-value labels
for x, y, lab in pts:
    if lab is None:
        continue
    dy = 6.5 if y < 55 else -9.5
    ax.annotate(lab, xy=(x, y), xytext=(x, y + dy), fontsize=8.6,
                color="#023e8a", ha="center", va="center", fontweight="bold")

# Event annotations along the bottom  (tx = text anchor, may differ from the rule line)
events = [
    (2025.05, 2025.05, "center", "Cloudflare makes hybrid PQ\nthe default for all sites"),
    (2025.73, 2025.73, "center", "iOS 26 ships PQ TLS\n(iOS PQ share: 2% → 11%\nin four days)"),
    (2026.47, 2026.86, "right", "Executive Order 14412\nfederal deadlines:\n2030 encryption / 2031 auth"),
]
for x, tx, ha, txt in events:
    ax.annotate(txt, xy=(tx, 3), xytext=(tx, 3), fontsize=7.6, color="#7a0b16",
                ha=ha, va="bottom",
                bbox=dict(boxstyle="round,pad=0.32", fc="#fff0f0", ec="#c1121f",
                          lw=0.8, alpha=0.9))
    ax.axvline(x, color="#c1121f", ls=":", lw=1.0, alpha=0.45, zorder=0)

ax.set_ylim(0, 82)
ax.set_xlim(2023.9, 2026.9)
ax.set_xticks([2024.0, 2024.5, 2025.0, 2025.5, 2026.0, 2026.5])
ax.set_xticklabels(["2024", "", "2025", "", "2026", ""])
ax.set_ylabel("Share of human HTTPS requests using\npost-quantum key agreement (%)", fontsize=10.5)
ax.set_xlabel("Year", fontsize=11)
ax.set_title("The migration nobody announced: post-quantum HTTPS, 2024–2026",
             fontsize=13, fontweight="bold", pad=12)
ax.grid(True, axis="y", ls=":", alpha=0.4)
ax.legend(loc="upper left", fontsize=9.2, framealpha=0.93)

fig.text(0.5, 0.005,
         "Reported Cloudflare figures; the connecting line is interpolation, not a continuous measurement series. "
         "Hybrid means classical X25519 AND post-quantum ML-KEM-768 together — an attacker must break both.",
         ha="center", fontsize=7.3, color="#666", style="italic", wrap=True)

fig.tight_layout(rect=(0, 0.035, 1, 1))
out = __file__.rsplit("/", 1)[0] + "/27-the-crypto-migration-and-the-shrinking-codebreaker-2-plot.png"
fig.savefig(out, bbox_inches="tight", facecolor="white")
print("wrote", out)
