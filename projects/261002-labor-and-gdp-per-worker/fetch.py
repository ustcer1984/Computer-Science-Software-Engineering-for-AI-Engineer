"""Download the raw data into data/raw/ (re-run to refresh with newer releases)."""
import urllib.request
from pathlib import Path

RAW = Path(__file__).parent / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)

WB_COUNTRIES = "CHN;RUS;KOR;JPN;IND;VNM;SGP;CAN;USA;GBR;FRA;DEU;SAU"  # Taiwan is not in WDI
WB_INDICATORS = [
    "SP.POP.1564.TO",  # population ages 15-64
    "SL.TLF.TOTL.IN",  # labor force, total (ILO modelled)
    "SL.UEM.TOTL.ZS",  # unemployment, % of labor force (ILO modelled)
    "NY.GDP.MKTP.KD",  # GDP, constant 2015 US$
]


def get(url, out):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as r:
        (RAW / out).write_bytes(r.read())
    print("saved", out)


for ind in WB_INDICATORS:
    get(f"https://api.worldbank.org/v2/country/{WB_COUNTRIES}/indicator/{ind}"
        f"?format=json&date=1999:2026&per_page=2000", f"wb_{ind}.json")

# Taiwan: IMF WEO — employed persons (LE), unemployment (LUR), real GDP (NGDP_R), population (LP)
get("https://api.imf.org/external/sdmx/2.1/data/IMF.RES,WEO/TWN.LE+LUR+NGDP_R+LP.A", "imf_twn.xml")

# Taiwan: UN WPP 2024 population by age (estimates to 2023, medium-variant projections after)
get("https://ourworldindata.org/grapher/population-by-age-group-with-projections.csv"
    "?country=TWN&csvType=filtered", "owid_twn_population_by_age.csv")
