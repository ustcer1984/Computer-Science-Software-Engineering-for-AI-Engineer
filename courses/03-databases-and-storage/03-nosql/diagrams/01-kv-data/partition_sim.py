"""§4 — hot partitions: a simulation of hash partitioning, because DynamoDB Local has no partitions to measure.

2,000,000 write requests are drawn from each workload; each request's partition key is hashed with MD5 (as Dynamo-style
systems do) and assigned to one of P partitions (hash mod P, an idealisation of DynamoDB's hash ranges). For each P
we record the share of requests landing on the busiest partition, and from it the highest table-wide write rate the
table can take before that partition reaches the per-partition limit of 1,000 write units per second (1 KB items):

    R_max = 1000 / share_of_busiest_partition

Workloads (keys are the partition-key values):
  uniform         1,000,000 customer ids, each equally likely
  zipf-1.1        1,000,000 customer ids, popularity ∝ 1 / rank^1.1 (a few customers are very busy)
  one-key         every write uses today's date as the key ("2026-11-19") — the classic time-series mistake
  sharded-10      today's date plus a random suffix 0–9 ("2026-11-19#7") — write sharding
  sharded-100     the same with 100 suffixes

Usage:  python partition_sim.py  > partition-sim.csv
"""
import hashlib, random, bisect, itertools
from collections import Counter

N_REQ, N_KEYS = 2_000_000, 1_000_000
rnd = random.Random(11)


def h(key):
    return int.from_bytes(hashlib.md5(key.encode()).digest()[:8], "big")


def zipf_sampler(n, s):
    w = [1 / (i ** s) for i in range(1, n + 1)]
    cum = list(itertools.accumulate(w)); tot = cum[-1]
    return lambda: bisect.bisect_left(cum, rnd.random() * tot)


z = zipf_sampler(N_KEYS, 1.1)
workloads = {
    "uniform": [f"cust{rnd.randrange(N_KEYS)}" for _ in range(N_REQ)],
    "zipf-1.1": [f"cust{z()}" for _ in range(N_REQ)],
    "one-key": ["2026-11-19"] * N_REQ,
    "sharded-10": [f"2026-11-19#{rnd.randrange(10)}" for _ in range(N_REQ)],
    "sharded-100": [f"2026-11-19#{rnd.randrange(100)}" for _ in range(N_REQ)],
}
print("workload,partitions,busiest_share,max_table_wcu_per_s,top_key_share", flush=True)
for name, keys in workloads.items():
    kc = Counter(keys)
    hashes = {k: h(k) for k in kc}
    top_key = kc.most_common(1)[0][1] / N_REQ
    for P in (1, 2, 4, 8, 16, 32, 64, 128):
        load = Counter()
        for k, c in kc.items():
            load[hashes[k] % P] += c
        share = max(load.values()) / N_REQ
        print(f"{name},{P},{share:.4f},{1000 / share:.0f},{top_key:.4f}", flush=True)
