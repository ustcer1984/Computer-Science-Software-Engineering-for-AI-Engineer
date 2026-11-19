"""§2 — what one key costs: Redis memory per key vs PostgreSQL bytes per row, for the same 1,000,000 pairs.

Key "k:<i>" (up to 9 bytes), value 100 bytes. Redis: used_memory before and after loading (no TTL, then again with a
TTL on every key). PostgreSQL: heap + primary-key index size of kv(k text PRIMARY KEY, v text) after VACUUM.

Usage:  python footprint.py <redis-port> <pg-dsn>  > footprint-out.txt
"""
import sys, redis, psycopg

r = redis.Redis(port=int(sys.argv[1])); DSN = sys.argv[2]; N = 1_000_000; V = "x" * 100
for ttl in (None, 3600):
    r.flushall(); base = r.info("memory")["used_memory"]
    p = r.pipeline(transaction=False)
    for i in range(N):
        p.set(f"k:{i}", V, ex=ttl)
        if i % 10000 == 9999: p.execute()
    p.execute()
    used = r.info("memory")["used_memory"] - base
    print(f"redis {'with TTL' if ttl else 'no TTL  '}: {used/2**20:7.1f} MiB for {N:,} keys = {used/N:5.0f} bytes per key "
          f"(payload {9+100} bytes)")
r.flushall()
with psycopg.connect(DSN, autocommit=True) as c:
    c.execute("DROP TABLE IF EXISTS kvf"); c.execute("CREATE TABLE kvf (k text PRIMARY KEY, v text NOT NULL)")
    with c.cursor().copy("COPY kvf FROM STDIN") as cp:
        for i in range(N): cp.write_row((f"k:{i}", V))
    c.execute("VACUUM ANALYZE kvf")
    heap, idx = c.execute("SELECT pg_table_size('kvf'), pg_indexes_size('kvf')").fetchone()
    print(f"postgres: heap {heap/2**20:.1f} MiB + index {idx/2**20:.1f} MiB = {(heap+idx)/N:.0f} bytes per row on disk "
          f"(cached in RAM only as far as shared_buffers / page cache allow)")
    c.execute("DROP TABLE kvf")
