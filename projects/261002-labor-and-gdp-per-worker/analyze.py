"""Compute growth rates and draw the four charts. Reads data/raw/, writes data/processed/ and charts/."""
import json, re
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).parent
RAW, OUT, FIG = HERE / "data" / "raw", HERE / "data" / "processed", HERE / "charts"
OUT.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)

plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "Noto Sans CJK JP", "WenQuanYi Zen Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

C = {"CHN": "中国", "TWN": "台湾", "RUS": "俄罗斯", "KOR": "韩国", "JPN": "日本", "IND": "印度", "VNM": "越南",
     "SGP": "新加坡", "CAN": "加拿大", "USA": "美国", "GBR": "英国", "FRA": "法国", "DEU": "德国", "SAU": "沙特"}
ORDER = list(C)

def wb(ind):
    d = json.load(open(RAW / f"wb_{ind}.json"))[1]
    s = pd.DataFrame([(x["countryiso3code"], int(x["date"]), x["value"]) for x in d], columns=["c", "y", "v"])
    return s.pivot(index="y", columns="c", values="v")

wap = wb("SP.POP.1564.TO")
lf = wb("SL.TLF.TOTL.IN")
ur = wb("SL.UEM.TOTL.ZS")
gdp = wb("NY.GDP.MKTP.KD")
emp = lf * (1 - ur / 100)

# Taiwan: IMF WEO (Apr 2026) for employment & real GDP; UN WPP 2024 (via OWID) for 15-64
x = open(RAW / "imf_twn.xml").read()
imf = {}
for s in re.finditer(r"<Series ([^>]*)>(.*?)</Series>", x, re.S):
    ind = re.search(r'INDICATOR="([^"]+)"', s.group(1)).group(1)
    imf[ind] = {int(t): float(v) for t, v in re.findall(r'TIME_PERIOD="(\d+)" OBS_VALUE="([^"]+)"', s.group(2))}
tp = pd.read_csv(RAW / "owid_twn_population_by_age.csv")
tp = tp[tp.Code == "TWN"].set_index("Year")
tot = tp["Total"].fillna(tp["Total (Projected)"])
o65 = tp["Ages 65+"].fillna(tp["Ages 65+ (Projected)"])
u15 = tp["Under-15s"].fillna(tp["Under-15s (Projected)"])
YEARS = range(1999, 2026)
wap["TWN"] = (tot - o65 - u15).reindex(YEARS)
emp["TWN"] = pd.Series(imf["LE"]).reindex(YEARS)
gdp["TWN"] = pd.Series(imf["NGDP_R"]).reindex(YEARS)

for df in (wap, emp, gdp):
    df.sort_index(inplace=True)
levels = {"wap": wap[ORDER].loc[1999:2025], "emp": emp[ORDER].loc[1999:2025], "gdp": gdp[ORDER].loc[1999:2025]}
levels["gdp_wap"] = levels["gdp"] / levels["wap"]
levels["gdp_emp"] = levels["gdp"] / levels["emp"]
growth = {k: v.pct_change().loc[2000:2025] * 100 for k, v in levels.items()}
cagr = {k: ((v.loc[2025] / v.loc[1999]) ** (1 / 26) - 1) * 100 for k, v in levels.items()}

CHARTS = [
    ("wap", "1. 劳动年龄人口（15–64岁）年增长率"),
    ("emp", "2. 实际劳动人口（就业人数 = 劳动力 ×（1 − 失业率））年增长率"),
    ("gdp_wap", "3. 每劳动年龄人口实际GDP 年增长率"),
    ("gdp_emp", "4. 每就业人员实际GDP（劳动生产率）年增长率"),
]
SRC = ("数据：世界银行 WDI（UN WPP 2024 人口；ILO 模型估计劳动力与失业率；GDP 为 2015 年不变价美元），2026-07 更新；"
       "台湾：IMF WEO 2026年4月（就业人数、不变价GDP）与 UN WPP 2024（15–64岁人口）。")

YL = {"wap": (-3, 8), "emp": (-6, 11), "gdp_wap": (-10, 14), "gdp_emp": (-10, 14)}

for key, title in CHARTS:
    g = growth[key]
    order = ORDER  # fixed panel positions across all charts
    ranked = sorted(ORDER, key=lambda c: -cagr[key][c])
    fig, axes = plt.subplots(4, 4, figsize=(16, 13), sharex=True, sharey=True)
    lo, hi = YL[key]
    for ax, c in zip(axes.flat, order):
        for o in ORDER:
            ax.plot(g.index, g[o].clip(lo, hi), color="#d0d0d0", lw=0.7, zorder=1)
        s = g[c]
        ax.axhline(0, color="#555", lw=0.8, zorder=2)
        ax.bar(s.index, s.clip(lo, hi), color=["#2a6fbb" if v >= 0 else "#c8553d" for v in s], width=0.75, zorder=3)
        ax.axhline(cagr[key][c], color="#e0a020", lw=1.6, ls="--", zorder=4)
        for yr, v in s.items():
            if v > hi or v < lo:
                ax.annotate(f"{v:.0f}", (yr, hi if v > hi else lo), ha="center",
                            va="bottom" if v > hi else "top", fontsize=7, color="#900", zorder=5,
                            annotation_clip=False, xytext=(0, 1 if v > hi else -1), textcoords="offset points")
        ax.set_title(f"{C[c]}  年均 {cagr[key][c]:+.2f}%", fontsize=12, loc="left")
        ax.set_ylim(lo, hi)
        ax.grid(axis="y", color="#eee", zorder=0)
        ax.spines[["top", "right"]].set_visible(False)
    for ax in list(axes.flat)[len(order):]:
        ax.axis("off")
    # summary bar in the last empty slots
    sax = fig.add_axes([0.53, 0.06, 0.44, 0.19])
    v = pd.Series({C[c]: cagr[key][c] for c in ranked})
    sax.barh(v.index[::-1], v.values[::-1], color=["#2a6fbb" if a >= 0 else "#c8553d" for a in v.values[::-1]])
    sax.axvline(0, color="#555", lw=0.8)
    sax.set_title("2000–2025 年均复合增长率 (%)", fontsize=11, loc="left")
    sax.tick_params(labelsize=8)
    sax.spines[["top", "right"]].set_visible(False)
    fig.suptitle(title + "，2000–2025（%）", fontsize=17, x=0.02, ha="left", y=0.995)
    fig.text(0.02, 0.965, "柱 = 当年增长率；橙色虚线 = 2000–2025 年均复合增长率；灰线 = 其他国家（对比用）；"
             "超出坐标范围的值以红字标注。各图中国家位置固定；右下角为年均增长率排名。", fontsize=10, color="#444")
    fig.text(0.02, 0.005, SRC, fontsize=8.5, color="#666")
    fig.tight_layout(rect=(0, 0.02, 1, 0.96))
    fig.savefig(FIG / f"chart_{key}.png", dpi=110)
    plt.close(fig)

out = pd.DataFrame({k: v for k, v in cagr.items()}).loc[ORDER].rename(index=C).round(2)
out.to_csv(OUT / "cagr_summary.csv")
print(out.to_string())
for k in growth:
    growth[k].rename(columns=C).round(2).to_csv(OUT / f"growth_{k}.csv")
