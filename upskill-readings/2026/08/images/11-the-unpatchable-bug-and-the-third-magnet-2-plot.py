#!/usr/bin/env python3
"""Figure 1 — what an *adaptive* attacker does to a prompt-injection detector.

Source of every number: Zhan, Liang et al., "Adaptive Attacks Break Defenses Against
Indirect Prompt Injection Attacks on LLM Agents", arXiv:2503.00061 (NAACL 2025 Findings),
Table 4 — detection rate on the InjecAgent benchmark, reported as
  DR-o : detection rate against the ORIGINAL (defense-unaware) injection
  DR-a : detection rate against an ADAPTIVE attack optimised in the presence of that defense

One unit throughout: percentage of injected attacks the defense flags. Higher is better
for the defender. Perplexity filtering is included exactly as published (it detects
essentially nothing either way) — it is the honest control, not a typo.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# (label, DR-original %, DR-adaptive %)  -- arXiv:2503.00061 Table 4
ROWS = [
    ("Fine-tuned detector\n(Vicuna-7B agent)", 61, 1),
    ("Fine-tuned detector\n(Llama3-8B agent)", 61, 10),
    ("LLM-based detector\n(Vicuna-7B agent)", 34, 0),
    ("LLM-based detector\n(Llama3-8B agent)", 72, 0),
    ("Perplexity filtering\n(Vicuna-7B agent)", 0, 1),
    ("Perplexity filtering\n(Llama3-8B agent)", 0, 1),
]

labels = [r[0] for r in ROWS]
orig = np.array([r[1] for r in ROWS], dtype=float)
adap = np.array([r[2] for r in ROWS], dtype=float)

y = np.arange(len(ROWS))
h = 0.38

fig, ax = plt.subplots(figsize=(10.2, 6.0))

b1 = ax.barh(y - h / 2, orig, height=h, color="#3B7EA1",
             label="vs the standard injection — the defence looks fine")
b2 = ax.barh(y + h / 2, adap, height=h, color="#C0392B",
             label="vs an adaptive attack that knows the defence is there")

for bars in (b1, b2):
    for rect in bars:
        w = rect.get_width()
        ax.text(w + 1.2, rect.get_y() + rect.get_height() / 2,
                f"{w:.0f}%", va="center", ha="left", fontsize=10.5, fontweight="bold",
                color=rect.get_facecolor())

ax.set_yticks(y)
ax.set_yticklabels(labels, fontsize=10)
ax.invert_yaxis()
ax.set_xlim(0, 92)
ax.set_xlabel("Detection rate — share of injected attacks the defence flags (%)", fontsize=11)
ax.set_title("A prompt-injection detector is only as good as the attacker's ignorance of it\n"
             "InjecAgent benchmark: detection collapses once the attack is defence-aware",
             fontsize=12.5, fontweight="bold", pad=14)

ax.axvline(50, color="#888888", linestyle=":", linewidth=1.1, zorder=0)
ax.text(50.6, -0.62, "coin flip", fontsize=9, color="#666666", style="italic")

ax.legend(loc="lower right", fontsize=9.8, framealpha=0.96)
ax.spines[["top", "right"]].set_visible(False)
ax.grid(axis="x", alpha=0.25, linewidth=0.7)
ax.set_axisbelow(True)

fig.text(0.005, 0.008,
         "Data: Zhan et al., arXiv:2503.00061 (NAACL 2025 Findings), Table 4 — detection rate "
         "on InjecAgent, original vs adaptive attack.",
         fontsize=8.2, color="#555555")

fig.tight_layout(rect=(0, 0.028, 1, 1))
fig.savefig("11-the-unpatchable-bug-and-the-third-magnet-2-plot.png", dpi=170)
print("wrote 11-the-unpatchable-bug-and-the-third-magnet-2-plot.png")
