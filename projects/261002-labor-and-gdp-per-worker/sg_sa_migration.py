"""Singapore & Saudi Arabia: working-age population swings vs foreign-labour policy / business-cycle events."""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "Noto Sans CJK JP", "WenQuanYi Zen Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
HERE = Path(__file__).parent
P = HERE / "data" / "processed"
wap = pd.read_csv(P / "growth_wap.csv", index_col=0)
emp = pd.read_csv(P / "growth_emp.csv", index_col=0)

# (start, end, label, colour): red = contraction (shock / tightening), green = expansion
EVENTS = {
    "新加坡": [
        (2001.5, 2003.5, "科网泡沫后衰退\n+ SARS", "r"),
        (2003.5, 2008.5, "经济繁荣、大型工程\n外劳政策宽松", "g"),
        (2010.5, 2019.5, "2011 大选后收紧外劳：\n提高外劳税、降低配额、2014 公平考量框架", "r"),
        (2019.5, 2021.5, "新冠封关\n非居民 −10.7%", "r"),
        (2021.5, 2023.5, "重开\n劳工回流", "g"),
    ],
    "沙特": [
        (1999.5, 2016.5, "油价高涨、基建扩张：外劳持续大量流入", "g"),
        (2012.5, 2014.5, "清查非法劳工\n+ 沙特化配额", "r"),
        (2016.5, 2019.5, "2017 外籍家属费\n2018 外籍员工税", "r"),
        (2021.5, 2025.5, "2030 愿景大型项目\n外劳回流", "g"),
    ],
}
COL = {"r": "#c8553d", "g": "#3a9a5b"}

fig, axes = plt.subplots(2, 1, figsize=(15, 10.5), sharex=True)
for ax, (c, lo, hi) in zip(axes, [("新加坡", -6.5, 10.5), ("沙特", -6.5, 13.5)]):
    for i, (a, b, lab, k) in enumerate(EVENTS[c]):
        ax.axvspan(a, b, color=COL[k], alpha=0.10 if b - a < 10 else 0.05, zorder=0)
        y = {("沙特", 1): -0.8, ("沙特", 2): hi - 0.4}.get((c, i), hi - 0.4)
        ax.text((a + b) / 2, y, lab, ha="center", va="top", fontsize=9.5, color=COL[k])
    ax.axhline(0, color="#555", lw=0.8)
    ax.plot(wap.index, wap[c], color="#2a6fbb", lw=2.4, marker="o", ms=4, label="劳动年龄人口（15–64 岁）增长率")
    ax.plot(emp.index, emp[c], color="#e0a020", lw=1.6, ls="--", marker="o", ms=3, label="就业人数增长率")
    ax.set_ylim(lo, hi)
    ax.set_title(f"{c}：年增长率（%）", loc="left", fontsize=14)
    ax.grid(axis="y", color="#eee"); ax.spines[["top", "right"]].set_visible(False)
    ax.legend(loc="lower left", fontsize=9.5, frameon=False)
# flag suspect Saudi estimates (census-revision artefacts in UN WPP)
sa = axes[1]
for yr in (2010, 2020, 2021):
    sa.annotate("?", (yr, wap.loc[yr, "沙特"]), xytext=(0, 9), textcoords="offset points",
                ha="center", fontsize=12, color="#900", fontweight="bold")
sa.text(2010, -5.8, "“?” = 可能是 UN WPP 在 2010 / 2022 人口普查间修订、插值的痕迹，而非真实变化", fontsize=9, color="#900")
axes[1].set_xticks(range(2000, 2026, 2))
fig.text(0.01, 0.005, "数据：World Bank WDI（UN WPP 2024 人口；ILO 模型估计就业）。红色底 = 冲击或收紧时期；绿色底 = 扩张时期。",
         fontsize=8.5, color="#666")
fig.tight_layout(rect=(0, 0.02, 1, 1))
fig.savefig(HERE / "charts" / "sg_sa_migration.png", dpi=110)
