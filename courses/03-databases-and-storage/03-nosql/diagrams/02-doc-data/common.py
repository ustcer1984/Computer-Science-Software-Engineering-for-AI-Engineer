"""Shared helpers for the M03 Ch3 §2 benchmarks: connections and a deterministic product catalogue.

Run every script from this folder; see README.md.
"""
import random
import statistics
import time

MONGO_URI = "mongodb://localhost:57017/?directConnection=true"
PG_DSN = "postgresql://postgres:pg@localhost:55433/postgres"

CATEGORIES = [f"cat-{i:02d}" for i in range(20)]
BRANDS = [f"brand-{i:03d}" for i in range(200)]
TAGS = [f"tag-{i:03d}" for i in range(100)]
COLORS = ["black", "white", "red", "blue", "green", "grey", "silver", "gold"]
SIZES = ["XS", "S", "M", "L", "XL"]
MATERIALS = ["steel", "aluminium", "plastic", "wood", "cotton", "glass"]
WORDS = ("light strong compact quiet portable durable classic modern simple premium everyday outdoor travel "
         "kitchen office garden smart wireless rechargeable waterproof").split()


def product(i, rng):
    """One catalogue item: about 700 bytes as JSON text, with a nested object and an array."""
    return {
        "_id": i,
        "sku": f"SKU-{i:07d}",
        "name": " ".join(rng.choice(WORDS) for _ in range(4)).title(),
        "category": rng.choice(CATEGORIES),
        "brand": rng.choice(BRANDS),
        "price": round(rng.uniform(1, 500), 2),
        "stock": rng.randint(0, 1000),
        "tags": sorted(rng.sample(TAGS, rng.randint(3, 6))),
        "attrs": {
            "color": rng.choice(COLORS),
            "size": rng.choice(SIZES),
            "weight_g": rng.randint(50, 5000),
            "material": rng.choice(MATERIALS),
        },
        "rating": {"avg": round(rng.uniform(1, 5), 1), "count": rng.randint(0, 5000)},
        "description": " ".join(rng.choice(WORDS) for _ in range(40)),
    }


def products(n, seed=42):
    rng = random.Random(seed)
    return [product(i, rng) for i in range(n)]


def timed(fn, runs):
    """Call fn(k) for k in range(runs); return (p50_us, p99_us)."""
    lat = []
    for k in range(runs):
        t = time.perf_counter()
        fn(k)
        lat.append((time.perf_counter() - t) * 1e6)
    lat.sort()
    return statistics.median(lat), lat[int(0.99 * (len(lat) - 1))]
