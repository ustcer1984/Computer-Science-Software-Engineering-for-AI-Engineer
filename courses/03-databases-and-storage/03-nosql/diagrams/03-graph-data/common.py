"""Shared helpers for the M03 Ch3 §3 benchmarks: connections and a deterministic "follows" graph.

The graph: N users, each following about 10 others. Half of a user's follows go to a popular account chosen with
Zipf-like weights (so a few accounts have very many followers), half to a random user in the same city (so there is
local structure). Generated with a fixed seed, so every run builds the same graph.

Run every script from this folder; see README.md.
"""
import os
import statistics
import time

import numpy as np

NEO4J_URI = "bolt://localhost:57687"
PG_DSN = "postgresql://postgres:pg@localhost:55434/postgres"

N_USERS = 1_000_000
MEAN_OUT = 10          # follows per user, on average
P_POPULAR = 0.5        # share of follows that go to a popular account
ZIPF_S = 0.9           # popularity exponent
N_CITIES = 50
SEED = 7

DATA_DIR = os.environ.get("GRAPH_DATA_DIR", "/tmp/graph-csv")


def build_graph(n=N_USERS, seed=SEED):
    """Return (city, age, src, dst) as numpy arrays. Edges are unique and contain no self-loops."""
    rng = np.random.default_rng(seed)
    # cities with Zipf-like sizes
    cw = 1.0 / np.arange(1, N_CITIES + 1) ** 1.0
    city = rng.choice(N_CITIES, size=n, p=cw / cw.sum()).astype(np.int32)
    age = rng.integers(16, 80, size=n).astype(np.int32)

    out_deg = 1 + rng.poisson(MEAN_OUT - 1, size=n)
    src = np.repeat(np.arange(n, dtype=np.int64), out_deg)
    m = len(src)

    # popularity: Zipf weights over a random permutation of user ids, so popular users are spread out
    rank_w = 1.0 / np.arange(1, n + 1) ** ZIPF_S
    perm = rng.permutation(n)
    pop_p = np.empty(n)
    pop_p[perm] = rank_w / rank_w.sum()

    popular = rng.random(m) < P_POPULAR
    dst = np.empty(m, dtype=np.int64)
    dst[popular] = rng.choice(n, size=popular.sum(), p=pop_p)

    # local: a random user from the same city
    order = np.argsort(city, kind="stable")
    counts = np.bincount(city, minlength=N_CITIES)
    starts = np.concatenate([[0], np.cumsum(counts)[:-1]])
    loc = ~popular
    c = city[src[loc]]
    pick = starts[c] + (rng.random(loc.sum()) * counts[c]).astype(np.int64)
    dst[loc] = order[pick]

    keep = src != dst
    src, dst = src[keep], dst[keep]
    key = np.unique(src * n + dst)          # drop duplicate edges
    return city, age, (key // n).astype(np.int64), (key % n).astype(np.int64)


def write_csv(city, age, src, dst, out=DATA_DIR):
    """Write the graph as CSV for neo4j-admin import and PostgreSQL COPY."""
    os.makedirs(out, exist_ok=True)
    ids = np.arange(len(city))
    with open(f"{out}/users.csv", "w") as f:
        f.write("id:ID(User),city:int,age:int\n")
        np.savetxt(f, np.column_stack([ids, city, age]), fmt="%d", delimiter=",")
    with open(f"{out}/follows.csv", "w") as f:
        f.write(":START_ID(User),:END_ID(User)\n")
        np.savetxt(f, np.column_stack([src, dst]), fmt="%d", delimiter=",")


def timed(fn, runs):
    """Call fn(k) for k in range(runs); return (p50_ms, p99_ms)."""
    lat = []
    for k in range(runs):
        t = time.perf_counter()
        fn(k)
        lat.append((time.perf_counter() - t) * 1e3)
    lat.sort()
    return statistics.median(lat), lat[int(0.99 * (len(lat) - 1))]


if __name__ == "__main__":
    t = time.time()
    city, age, src, dst = build_graph()
    indeg = np.bincount(dst, minlength=N_USERS)
    outdeg = np.bincount(src, minlength=N_USERS)
    print(f"users {N_USERS:,}  edges {len(src):,}  built in {time.time() - t:.1f}s")
    print(f"out-degree mean {outdeg.mean():.2f} max {outdeg.max()}")
    q = np.percentile(indeg, [50, 90, 99, 99.9])
    print(f"in-degree  p50 {q[0]:.0f} p90 {q[1]:.0f} p99 {q[2]:.0f} p99.9 {q[3]:.0f} max {indeg.max():,} "
          f"(user {indeg.argmax()})")
    print(f"top-10 in-degrees: {sorted(indeg)[-10:][::-1]}")
    write_csv(city, age, src, dst)
    print(f"CSV written to {DATA_DIR} in {time.time() - t:.1f}s total")
