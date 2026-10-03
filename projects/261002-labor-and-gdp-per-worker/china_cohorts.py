"""Why China's 15-64 population ticks up in 2024-26: compare the cohort turning 15 with the one turning 65."""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "Noto Sans CJK JP", "WenQuanYi Zen Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
HERE = Path(__file__).parent

b = pd.read_csv(HERE / "data" / "raw" / "owid_chn_births.csv").dropna(subset=["Number of births"])
births = b.set_index("Year")["Number of births"] / 1e6
NBS = {2024: 9.54, 2025: 7.92}  # NBS releases (not yet in UN WPP estimates)

years = range(2000, 2041)
enter = pd.Series({t: births.get(t - 15) for t in years})
leave = pd.Series({t: births.get(t - 65) for t in years})

fig, (a1, a2) = plt.subplots(1, 2, figsize=(16, 6.2), gridspec_kw={"width_ratios": [1.15, 1]})

# left: births by year, famine trough and boom highlighted
a1.bar(births.index, births.values, color="#9bb7d4", width=0.85)
a1.bar(list(NBS), list(NBS.values()), color="#c8553d", width=0.85, label="国家统计局 2024–2025")
a1.axvspan(1958.5, 1961.5, color="#e0a020", alpha=0.25)
a1.axvspan(1961.5, 1975.5, color="#2a6fbb", alpha=0.08)
a1.text(1958, 36, "1959–61\n出生低谷", ha="right", va="top", fontsize=10, color="#8a5a00")
a1.text(1968.5, 36.5, "1962–75 婴儿潮", ha="center", va="top", fontsize=10, color="#1d4f86")
a1.axvspan(2008.5, 2011.5, color="#888", alpha=0.12)
a1.text(2010, 36.5, "2009–11\n（2024–26 年满15岁）", ha="center", va="top", fontsize=9, color="#444")
a1.set_ylim(0, 38)
a1.set_title("中国每年出生人数（百万）", loc="left", fontsize=13)
a1.legend(loc="lower left", fontsize=9, frameon=False)
a1.grid(axis="y", color="#eee"); a1.spines[["top", "right"]].set_visible(False)

# right: entering vs exiting cohorts by calendar year
a2.plot(enter.index, enter.values, color="#2a6fbb", lw=2.2, marker="o", ms=3, label="满 15 岁的一代（进入）= t−15 年出生数")
a2.plot(leave.index, leave.values, color="#c8553d", lw=2.2, marker="o", ms=3, label="满 65 岁的一代（退出）= t−65 年出生数")
a2.plot(leave.index, leave.values * 0.75, color="#c8553d", lw=1.2, ls="--", label="退出一代 × 0.75（约略扣除活到 64 岁前的死亡）")
a2.axvspan(2023.5, 2026.5, color="#e0a020", alpha=0.25)
a2.text(2025, 6.5, "进入 > 退出\n→ 暂时回升", ha="center", fontsize=10, color="#8a5a00")
a2.text(2034, 6.5, "婴儿潮退休\n→ 加速下降", ha="center", fontsize=10, color="#1d4f86")
a2.set_ylim(5, 36)
a2.set_title("按日历年：进入 vs 退出 15–64 岁的出生队列（百万）", loc="left", fontsize=13)
a2.legend(loc="upper left", fontsize=9, frameon=False)
a2.grid(axis="y", color="#eee"); a2.spines[["top", "right"]].set_visible(False)

fig.text(0.01, 0.01, "数据：UN WPP 2024（经 Our World in Data）出生人数；国家统计局 2024 年 954 万、2025 年 792 万。"
         "右图为出生数近似，未计入移民与精确死亡率。", fontsize=8.5, color="#666")
fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig(HERE / "charts" / "china_cohorts.png", dpi=110)
