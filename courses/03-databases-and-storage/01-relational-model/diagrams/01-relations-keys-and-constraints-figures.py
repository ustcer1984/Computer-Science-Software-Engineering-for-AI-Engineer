#!/usr/bin/env python3
"""Figures for M03 Ch1 §1 — the relational model: relations, keys and constraints.

fig1: how dominant is the relational model, 56 years after Codd? Real data from
      the DB-Engines Ranking, September 2026 (https://db-engines.com/en/ranking and
      https://db-engines.com/en/ranking_categories, read 2026-09-28).

      Left : the top 15 systems by popularity score, coloured by primary model.
      Right: the share of total popularity score held by each database model.

      Caveat drawn onto the figure: DB-Engines measures POPULARITY (web mentions,
      search interest, job offers, Q&A activity, social media), not installations
      or data volume.

Run:  .venv/bin/python 01-relations-keys-and-constraints-figures.py
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
INK = "#1b2430"
COL = {"Relational": "#1d4ed8", "Document": "#c2410c", "Key-value": "#047857",
       "Wide column": "#7c3aed", "Search": "#eab308", "Multi-model": "#64748b", "Graph": "#be185d"}

# (system, primary model, score) — DB-Engines, September 2026
top = [
    ("Oracle", "Relational", 1122.27), ("MySQL", "Relational", 844.82),
    ("Microsoft SQL Server", "Relational", 698.69), ("PostgreSQL", "Relational", 683.26),
    ("MongoDB", "Document", 381.31), ("Snowflake", "Relational", 211.61),
    ("Databricks", "Multi-model", 168.34), ("Redis", "Key-value", 158.06),
    ("IBM Db2", "Relational", 110.57), ("SQLite", "Relational", 97.05),
    ("Elasticsearch", "Search", 95.50), ("Apache Cassandra", "Wide column", 93.96),
    ("MariaDB", "Relational", 74.42), ("Splunk", "Search", 71.68),
    ("Azure SQL Database", "Relational", 70.84),
]
# share of total ranking score per model, September 2026
share = [("Relational", 71.0), ("Document", 10.9), ("Key-value", 4.8), ("Search", 3.9),
         ("Vector", 2.8), ("Wide column", 2.3), ("Graph", 1.6), ("Time series", 1.2),
         ("Spatial", 0.5), ("RDF", 0.3)]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.0, 5.6), gridspec_kw={"width_ratios": [1.35, 1]})

names = [t[0] for t in top][::-1]
scores = [t[2] for t in top][::-1]
colors = [COL[t[1]] for t in top][::-1]
ax1.barh(names, scores, color=colors)
for y, s in enumerate(scores):
    ax1.text(s + 12, y, f"{s:.0f}", va="center", fontsize=8, color=INK)
ax1.set_xlabel("DB-Engines popularity score (September 2026)")
ax1.set_title("Top 15 database systems — coloured by primary model", fontsize=11, color=INK)
ax1.set_xlim(0, 1260)
ax1.grid(axis="x", alpha=0.25)
seen = []
handles = []
for _, m, _s in top:
    if m not in seen:
        seen.append(m)
        handles.append(plt.Rectangle((0, 0), 1, 1, color=COL[m], label=m))
ax1.legend(handles=handles, fontsize=8.5, loc="lower right")

labs = [s[0] for s in share][::-1]
vals = [s[1] for s in share][::-1]
cols = [COL.get(l, "#94a3b8") for l in labs]
ax2.barh(labs, vals, color=cols)
for y, v in enumerate(vals):
    ax2.text(v + 1, y, f"{v:.1f}%", va="center", fontsize=8.5, color=INK)
ax2.set_xlim(0, 85)
ax2.set_xlabel("share of total popularity score (%)")
ax2.set_title("Share of popularity by database model", fontsize=11, color=INK)
ax2.grid(axis="x", alpha=0.25)

fig.suptitle("Fifty-six years after Codd, the relational model still holds about 71% of database mindshare",
             fontsize=12.5, color=INK, y=0.99)
fig.text(0.5, 0.005, "Source: DB-Engines Ranking, September 2026. Popularity = web mentions, search interest, "
         "jobs, Q&A and social activity — not installations or data volume.",
         ha="center", fontsize=8.5, color="#475569")
fig.tight_layout(rect=(0, 0.03, 1, 0.95))
out = os.path.join(HERE, "01-relations-keys-and-constraints-fig1.svg")
fig.savefig(out, format="svg", bbox_inches="tight")
print("wrote", out)
