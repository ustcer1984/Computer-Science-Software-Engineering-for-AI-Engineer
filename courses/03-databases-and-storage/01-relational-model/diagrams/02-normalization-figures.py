#!/usr/bin/env python3
"""Figures for M03 Ch1 §2 — normalization. (Figure 2 in the doc is a Mermaid diagram,
so the files here are fig1, fig3 and fig4, matching the doc's figure numbers.)

fig1: the vote sheet of §1, drawn as the table it is, with every cell that
      REPEATS a fact already stated elsewhere in the table shaded by the
      dependency that makes it redundant. The same six rows are loaded in the
      hands-on (§11), so the picture and the database agree.

fig3: the normal forms as nested sets. Every relation in an inner form is also
      in every outer one; each ring is labelled with the one kind of dependency
      it forbids.

fig4: what normalizing buys and costs, MEASURED (not estimated) on PostgreSQL 18
      in Docker on a laptop, 2026-10-05. Dataset: 500,000 battles x 2 votes =
      1,000,000 vote rows; 40 models across 8 providers, with popularity skewed
      so the most-used model appears in 332,088 rows; 100,000 voters. The wide
      table had indexes on model_a and model_b, so its UPDATE did not scan.
      Each figure is the median of 5-21 runs inside a rolled-back transaction.

Run:  .venv/bin/python 02-normalization-figures.py
Outputs SVGs next to this script (committed alongside the doc).
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Patch

HERE = os.path.dirname(os.path.abspath(__file__))
INK, GREY = "#1b2430", "#64748b"
C_MODEL, C_BATTLE, C_VOTER = "#fdba74", "#93c5fd", "#86efac"   # orange, blue, green

# =============================================================================
# fig1 — the redundancy in the vote sheet
# =============================================================================
cols = ["battle_id", "voter_email", "voter_country", "model_a", "model_a_provider",
        "model_b", "model_b_provider", "prompt", "winner"]
rows = [
    [1, "ana@x.com", "SG", "orca-7b",   "Northwind", "heron-70b", "Bluefin",   "Translate to Malay", "a"],
    [1, "ben@x.com", "MY", "orca-7b",   "Northwind", "heron-70b", "Bluefin",   "Translate to Malay", "tie"],
    [2, "ana@x.com", "SG", "heron-70b", "Bluefin",   "kite-8b",   "Tern",      "Summarise this memo", "b"],
    [2, "cai@x.com", "ID", "heron-70b", "Bluefin",   "kite-8b",   "Tern",      "Summarise this memo", "b"],
    [3, "ben@x.com", "MY", "kite-8b",   "Tern",      "orca-7b",   "Northwind", "Write a pantun", "a"],
    [3, "dev@x.com", "TH", "kite-8b",   "Tern",      "orca-7b",   "Northwind", "Write a pantun", "b"],
]

# Which cells repeat a fact already stated in an earlier row?
shade = {}
seen_battle, seen_voter, seen_model = set(), set(), set()
for r, row in enumerate(rows):
    b, v = row[0], row[1]
    if b in seen_battle:                       # battle_id -> model_a, model_b, prompt
        for c in (3, 5, 7):
            shade[(r, c)] = C_BATTLE
    seen_battle.add(b)
    if v in seen_voter:                        # voter_email -> voter_country
        shade[(r, 2)] = C_VOTER
    seen_voter.add(v)
    for mc, pc in ((3, 4), (5, 6)):            # model -> provider (across BOTH column pairs)
        if row[mc] in seen_model:
            shade[(r, pc)] = C_MODEL
        seen_model.add(row[mc])

fig, ax = plt.subplots(figsize=(13.2, 3.9))
ax.axis("off")
widths = [0.95, 1.15, 0.85, 0.85, 1.15, 0.85, 1.15, 1.55, 0.55]
tbl = ax.table(cellText=[[str(x) for x in row] for row in rows], colLabels=cols,
               colWidths=[w / sum(widths) for w in widths], loc="center", cellLoc="center")
tbl.auto_set_font_size(False)
tbl.set_fontsize(9.5)
tbl.scale(1, 1.75)
for (r, c), cell in tbl.get_celld().items():
    cell.set_edgecolor("#cbd5e1")
    if r == 0:
        cell.set_facecolor("#1e293b")
        cell.get_text().set_color("white")
        cell.get_text().set_fontweight("bold")
        if c in (0, 1):
            cell.get_text().set_text(cols[c] + " (key)")
    else:
        cell.set_facecolor(shade.get((r - 1, c), "white"))
ax.legend(handles=[
    Patch(facecolor=C_BATTLE, edgecolor="#94a3b8", label="repeats a fact about the BATTLE   (battle_id determines models and prompt)"),
    Patch(facecolor=C_VOTER, edgecolor="#94a3b8", label="repeats a fact about the VOTER   (voter_email determines country)"),
    Patch(facecolor=C_MODEL, edgecolor="#94a3b8", label="repeats a fact about the MODEL   (model determines provider, in either column)"),
], loc="lower center", bbox_to_anchor=(0.5, -0.16), ncol=1, fontsize=9.5, frameon=False)
n_red = len(shade)
n_cells = len(rows) * len(cols)
ax.set_title(f"The vote sheet: {n_red} of its {n_cells} cells restate something the table already says",
             fontsize=12, color=INK, pad=6)
fig.tight_layout()
out = os.path.join(HERE, "02-normalization-fig1.svg")
fig.savefig(out, format="svg", bbox_inches="tight")
print("wrote", out, "redundant cells", n_red, "of", n_cells)

# =============================================================================
# fig3 — the normal forms as nested sets
# =============================================================================
rings = [
    ("1NF", "every cell holds one value of its column's type; no repeating groups", "#e2e8f0"),
    ("2NF", "forbids a non-key column depending on PART of a composite key", "#dbeafe"),
    ("3NF", "forbids a non-key column depending on ANOTHER non-key column", "#bfdbfe"),
    ("BCNF", "forbids ANY determinant that is not a key", "#93c5fd"),
    ("4NF", "forbids two INDEPENDENT multi-valued facts in one table", "#60a5fa"),
    ("5NF", "forbids a table that is the join of three or more smaller ones", "#3b82f6"),
]
fig, ax = plt.subplots(figsize=(11.5, 6.4))
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis("off")
for i, (name, rule, col) in enumerate(rings):
    pad_x, pad_y = i * 4.0, i * 7.4
    box = FancyBboxPatch((2 + pad_x, 6 + pad_y), 96 - 2 * pad_x, 90 - 2 * pad_y,
                         boxstyle="round,pad=0.4,rounding_size=2.0", fc=col, ec="#1e3a8a", lw=1.2)
    ax.add_patch(box)
    txt_col = "white" if i >= 4 else INK
    ax.text(4.0 + pad_x, 93.2 - pad_y, name, fontsize=12.5, fontweight="bold", color=txt_col, va="top")
    ax.text(12.5 + pad_x, 92.8 - pad_y, rule, fontsize=9.8, color=txt_col, va="top")
ax.text(50, 1.5, "An operational (OLTP) schema aims for 3NF or BCNF, then checks for the one 4NF problem; 5NF cases are rare.",
        ha="center", va="bottom", fontsize=9.8, color=GREY, style="italic")
ax.set_title("The normal forms nest: each one forbids one more kind of redundancy",
             fontsize=12.5, color=INK)
fig.tight_layout()
out = os.path.join(HERE, "02-normalization-fig3.svg")
fig.savefig(out, format="svg", bbox_inches="tight")
print("wrote", out)

# =============================================================================
# fig4 — measured trade-off, PostgreSQL 18
# =============================================================================
ops = [
    ("Change one fact\n(rename the provider of the\nmost-used model)", 3176.69, 0.02, "332,088 rows rewritten", "1 row"),
    ("Analytical read\n(wins per provider over\nall 1,000,000 votes)", 75.26, 145.62, "no joins", "2 joins"),
    ("Point read\n(one battle with its\nvotes, models, voters)", 0.02, 0.19, "1 index lookup", "4 joins"),
]
fig, ax = plt.subplots(figsize=(11.8, 5.6))
x = range(len(ops))
w = 0.36
wide = [o[1] for o in ops]
norm = [o[2] for o in ops]
b1 = ax.bar([i - w / 2 for i in x], wide, w, color="#c2410c", label="wide vote sheet (one table)")
b2 = ax.bar([i + w / 2 for i in x], norm, w, color="#1d4ed8", label="normalized (model, voter, battle, vote)")
ax.set_yscale("log")
ax.set_ylim(0.005, 150000)
ax.set_xticks(list(x))
ax.set_xticklabels([o[0] for o in ops], fontsize=10)
ax.set_ylabel("median time, milliseconds (log scale)")
for i, o in enumerate(ops):
    ax.text(i - w / 2, o[1] * 1.35, f"{o[1]:,.2f} ms\n{o[3]}", ha="center", va="bottom", fontsize=8.8, color="#7c2d12")
    ax.text(i + w / 2, o[2] * 1.35, f"{o[2]:,.2f} ms\n{o[4]}", ha="center", va="bottom", fontsize=8.8, color="#1e3a8a")
ax.text(0, 30000, "about 160,000 x", ha="center", fontsize=10.5, fontweight="bold", color=INK)
ax.text(1, 900, "1.9 x the other way", ha="center", fontsize=10.5, fontweight="bold", color=INK)
ax.text(2, 4.0, "both well under\na millisecond", ha="center", fontsize=10, fontweight="bold", color=INK)
ax.grid(axis="y", alpha=0.25, which="both")
ax.legend(loc="upper right", fontsize=9.5)
ax.set_title("Normalizing makes a change of fact cheap and makes some reads pay for joins\n"
             "(PostgreSQL 18, 1,000,000 votes; measured 2026-10-05)", fontsize=11.5, color=INK)
fig.tight_layout()
out = os.path.join(HERE, "02-normalization-fig4.svg")
fig.savefig(out, format="svg", bbox_inches="tight")
print("wrote", out)
