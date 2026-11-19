"""§2 — one key, one value: Redis GET vs PostgreSQL primary-key SELECT, from the same Python client.

100,000 keys of 100-byte values are loaded into Redis (SET) and into a PostgreSQL table
kv(k text PRIMARY KEY, v text). Then, for each store:

  seq      one client, 20,000 random lookups one after another; per-lookup latency -> p50 / p99, lookups/s
  batch    one client, 20,000 random lookups in batches of 100 (Redis pipeline; PostgreSQL pipeline mode)
  procs    1 / 4 / 16 client processes, each doing 5,000 sequential lookups after a warm-up; total lookups / slowest
           process's time

3 repetitions; the CSV holds every run. Python client overhead is included on both sides on purpose: it is what an
application sees. The server-only ceilings are measured separately with redis-benchmark and pgbench (README).

Usage:  python lookup_bench.py <redis-port> <pg-dsn>  > lookup-bench.csv
"""
import sys, time, random, statistics, multiprocessing as mp
import redis, psycopg

RPORT, DSN = int(sys.argv[1]), sys.argv[2]
N, VAL = 100_000, "x" * 100


def load():
    r = redis.Redis(port=RPORT)
    r.flushall()
    p = r.pipeline(transaction=False)
    for i in range(N):
        p.set(f"k:{i}", VAL)
        if i % 5000 == 4999:
            p.execute()
    p.execute()
    with psycopg.connect(DSN, autocommit=True) as c:
        c.execute("DROP TABLE IF EXISTS kv")
        c.execute("CREATE TABLE kv (k text PRIMARY KEY, v text NOT NULL)")
        with c.cursor().copy("COPY kv (k, v) FROM STDIN") as cp:
            for i in range(N):
                cp.write_row((f"k:{i}", VAL))
        c.execute("VACUUM ANALYZE kv")
        c.execute("SELECT count(*) FROM kv").fetchone()      # warm the cache


def redis_seq(n, rnd):
    r = redis.Redis(port=RPORT)
    lat = []
    for _ in range(n):
        k = f"k:{rnd.randrange(N)}"
        t = time.perf_counter(); v = r.get(k); lat.append(time.perf_counter() - t)
        assert v is not None
    return lat


def pg_seq(n, rnd):
    lat = []
    with psycopg.connect(DSN, autocommit=True, prepare_threshold=0) as c:
        cur = c.cursor()
        for _ in range(n):
            k = f"k:{rnd.randrange(N)}"
            t = time.perf_counter(); cur.execute("SELECT v FROM kv WHERE k = %s", (k,)); v = cur.fetchone()
            lat.append(time.perf_counter() - t)
            assert v is not None
    return lat


def redis_batch(n, rnd, b=100):
    r = redis.Redis(port=RPORT)
    t = time.perf_counter()
    for _ in range(n // b):
        p = r.pipeline(transaction=False)
        for _ in range(b):
            p.get(f"k:{rnd.randrange(N)}")
        assert all(x is not None for x in p.execute())
    return time.perf_counter() - t


def pg_batch(n, rnd, b=100):
    with psycopg.connect(DSN, autocommit=True, prepare_threshold=0) as c:
        t = time.perf_counter()
        for _ in range(n // b):
            with c.pipeline():
                curs = []
                for _ in range(b):
                    cur = c.cursor(); cur.execute("SELECT v FROM kv WHERE k = %s", (f"k:{rnd.randrange(N)}",))
                    curs.append(cur)
            assert all(cu.fetchone() is not None for cu in curs)
        return time.perf_counter() - t


def worker(args):
    store, n, seed = args
    rnd = random.Random(seed)
    (redis_seq if store == "redis" else pg_seq)(200, rnd)          # warm-up
    t = time.perf_counter()
    (redis_seq if store == "redis" else pg_seq)(n, rnd)
    return time.perf_counter() - t


if __name__ == "__main__":
    load()
    print("store,mode,rep,clients,lookups,seconds,lookups_per_s,p50_us,p99_us", flush=True)
    for rep in range(3):
        for store, seq, batch in (("redis", redis_seq, redis_batch), ("postgres", pg_seq, pg_batch)):
            rnd = random.Random(rep)
            seq(500, rnd)
            lat = seq(20_000, rnd)
            q = statistics.quantiles(lat, n=100)
            print(f"{store},seq,{rep},1,20000,{sum(lat):.3f},{20000/sum(lat):.0f},{q[49]*1e6:.0f},{q[98]*1e6:.0f}", flush=True)
            s = batch(20_000, rnd)
            print(f"{store},batch100,{rep},1,20000,{s:.3f},{20000/s:.0f},,", flush=True)
            for procs in (1, 4, 16):
                with mp.Pool(procs) as pool:
                    s = max(pool.map(worker, [(store, 5000, 1000 * rep + i) for i in range(procs)]))
                print(f"{store},procs,{rep},{procs},{5000*procs},{s:.3f},{5000*procs/s:.0f},,", flush=True)
