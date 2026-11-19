"""§7 — what happens to keys after their TTL runs out, when nobody reads them.

1,000,000 keys are written with a TTL of 10 s (SET … EX 10), plus 100,000 keys with no TTL. Nobody reads them. Every
100 ms for 30 s, counted from the first write, we record DBSIZE (keys the server still holds, expired or not), the `expired_keys` counter from
INFO stats, and used_memory. At t = 25 s (every key at least 10 s past its expiry) one client GETs 1,000 of them: they must all come
back nil, whether or not the server has reclaimed them yet.

Run once with the default `hz 10` and once with `hz 100` (how often the background expiry cycle runs per second).

Usage:  python ttl_bench.py <redis-port>  > ttl-bench.csv
"""
import sys, time
import redis

r = redis.Redis(port=int(sys.argv[1]))
print("hz,t_s,dbsize,expired_keys,used_memory_mb,note", flush=True)
for hz in (10, 100):
    r.flushall(); r.config_set("hz", hz); r.config_resetstat()
    t0 = time.perf_counter()
    p = r.pipeline(transaction=False)
    for i in range(100_000):
        p.set(f"keep:{i}", "v" * 50)
    for i in range(1_000_000):
        p.set(f"tmp:{i}", "v" * 50, ex=10)
        if i % 10000 == 9999:
            p.execute()
    p.execute()
    print(f"{hz},{time.perf_counter() - t0:.1f},{r.dbsize()},,,load finished", flush=True)
    probed = False
    while (t := time.perf_counter() - t0) < 30:
        note = ""
        if t >= 25 and not probed:
            pp = r.pipeline(transaction=False)
            for i in range(0, 1_000_000, 1000):
                pp.get(f"tmp:{i}")
            got = pp.execute()
            note = f"GET of 1000 expired keys: {sum(x is not None for x in got)} returned a value"
            probed = True
        st = r.info("stats"); mem = r.info("memory")["used_memory"] / 2**20
        print(f"{hz},{t:.1f},{r.dbsize()},{st['expired_keys']},{mem:.1f},{note}", flush=True)
        time.sleep(0.1)
