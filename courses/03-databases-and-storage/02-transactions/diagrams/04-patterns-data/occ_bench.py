#!/usr/bin/env python3
"""M03 Ch2 §4 §1 — read-then-write under contention: no protection, pessimistic, optimistic, and one atomic UPDATE.

Every operation adds 1 to a randomly chosen row's balance. Between reading the row and writing it the client "thinks"
for THINK_S seconds (application work). 16 client threads, OPS operations each, autocommit connections, READ COMMITTED.
The number of rows sets the contention: 1 row = every client wants the same row.

  naive        SELECT balance; think; UPDATE SET balance = <read + 1>                   (lost updates expected)
  pessimistic  BEGIN; SELECT ... FOR UPDATE; think; UPDATE; COMMIT
  optimistic   SELECT balance, version; think; UPDATE ... SET version = version + 1
               WHERE id = %s AND version = <read>; 0 rows -> read again and retry
  atomic       think; UPDATE SET balance = balance + 1                                  (no read needed; reference)

Output CSV columns: method, rows, rep, seconds, ops_per_s, lost, retries, p50_ms, p99_ms
Usage:  python occ_bench.py <dsn> > occ-bench.csv
"""
import random
import statistics
import sys
import threading
import time

import psycopg

DSN = sys.argv[1]
THREADS, OPS, THINK_S = 16, 300, 0.002
ROWS = [1, 4, 16, 64, 256, 4096]
REPS = 3


def setup(n):
    with psycopg.connect(DSN, autocommit=True) as c:
        c.execute("DROP TABLE IF EXISTS acct")
        c.execute("CREATE TABLE acct (id int PRIMARY KEY, balance bigint NOT NULL, version int NOT NULL)")
        c.execute("INSERT INTO acct SELECT g, 0, 0 FROM generate_series(1, %s) g", (n,))


def op(conn, method, rid, stats):
    if method == "naive":
        b = conn.execute("SELECT balance FROM acct WHERE id = %s", (rid,)).fetchone()[0]
        time.sleep(THINK_S)
        conn.execute("UPDATE acct SET balance = %s WHERE id = %s", (b + 1, rid))
    elif method == "pessimistic":
        with conn.transaction():
            b = conn.execute("SELECT balance FROM acct WHERE id = %s FOR UPDATE", (rid,)).fetchone()[0]
            time.sleep(THINK_S)
            conn.execute("UPDATE acct SET balance = %s WHERE id = %s", (b + 1, rid))
    elif method == "optimistic":
        while True:
            b, v = conn.execute("SELECT balance, version FROM acct WHERE id = %s", (rid,)).fetchone()
            time.sleep(THINK_S)
            cur = conn.execute("UPDATE acct SET balance = %s, version = version + 1 WHERE id = %s AND version = %s",
                               (b + 1, rid, v))
            if cur.rowcount == 1:
                break
            stats["retries"] += 1
    elif method == "atomic":
        time.sleep(THINK_S)
        conn.execute("UPDATE acct SET balance = balance + 1 WHERE id = %s", (rid,))


def run(method, n, rep):
    setup(n)
    lat, lock = [], threading.Lock()
    stats = {"retries": 0}

    def worker(seed):
        rnd = random.Random(seed)
        local = {"retries": 0}
        with psycopg.connect(DSN, autocommit=True) as conn:
            mine = []
            for _ in range(OPS):
                t0 = time.perf_counter()
                op(conn, method, rnd.randint(1, n), local)
                mine.append(time.perf_counter() - t0)
        with lock:
            lat.extend(mine)
            stats["retries"] += local["retries"]

    ts = [threading.Thread(target=worker, args=(rep * 1000 + i,)) for i in range(THREADS)]
    t0 = time.perf_counter()
    for t in ts: t.start()
    for t in ts: t.join()
    secs = time.perf_counter() - t0
    with psycopg.connect(DSN, autocommit=True) as c:
        total = c.execute("SELECT sum(balance) FROM acct").fetchone()[0]
    lat.sort()
    expected = THREADS * OPS
    print(f"{method},{n},{rep},{secs:.3f},{expected / secs:.1f},{expected - total},{stats['retries']},"
          f"{1000 * lat[len(lat) // 2]:.2f},{1000 * lat[int(len(lat) * 0.99)]:.2f}", flush=True)


print("method,rows,rep,seconds,ops_per_s,lost,retries,p50_ms,p99_ms")
for rep in range(REPS):
    for n in ROWS:
        for m in ("naive", "pessimistic", "optimistic", "atomic"):
            run(m, n, rep)
