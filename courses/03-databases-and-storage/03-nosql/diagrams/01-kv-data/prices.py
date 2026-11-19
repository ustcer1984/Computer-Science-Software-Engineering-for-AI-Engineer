"""§8 — list prices used in Table 12, from the public AWS Price List API (no credentials needed), Singapore region.

Prints the DynamoDB on-demand request and storage prices and the ElastiCache on-demand node prices for a few node
types, with each offer file's publication date.

Usage:  python prices.py  > prices-out.txt
"""
import json, urllib.request

BASE = "https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/{}/current/ap-southeast-1/index.json"


def offer(svc):
    with urllib.request.urlopen(BASE.format(svc)) as f:
        return json.load(f)


def prices(d, sku):
    for t in d["terms"]["OnDemand"].get(sku, {}).values():
        for pd in t["priceDimensions"].values():
            yield pd["pricePerUnit"]["USD"], pd["unit"], pd["description"]


d = offer("AmazonDynamoDB")
print("AmazonDynamoDB ap-southeast-1, offer published", d["publicationDate"])
for sku, p in d["products"].items():
    u = p["attributes"].get("usagetype", "")
    if u in ("APS1-ReadRequestUnits", "APS1-WriteRequestUnits", "APS1-TimedStorage-ByteHrs"):
        for usd, unit, desc in prices(d, sku):
            print(f"  {u:<28} {usd:>14} per {unit:<18} {desc}")

e = offer("AmazonElastiCache")
print("AmazonElastiCache ap-southeast-1, offer published", e["publicationDate"])
for sku, p in e["products"].items():
    a = p["attributes"]
    if p.get("productFamily") == "Cache Instance" and a.get("instanceType") in ("cache.t4g.micro", "cache.t4g.small", "cache.r7g.large") \
            and a.get("cacheEngine") in ("Redis", "Valkey") and a.get("memory"):
        for usd, unit, desc in prices(e, sku):
            print(f"  {a['instanceType']:<16} {a['cacheEngine']:<7} {a['memory']:>10} {usd:>8} per {unit}  {desc}")
