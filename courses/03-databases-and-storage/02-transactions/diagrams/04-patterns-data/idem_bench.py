#!/usr/bin/env python3
"""M03 Ch2 §4 §2 — a payment endpoint behind a client that times out and retries; four server designs.

A "server" is a pool of 40 threads, each with its own connection (think: Lambda invocations). One request = one charge
of a payment. The provider call inside it takes an exponentially distributed time (mean 80 ms, capped at 600 ms). The
client waits TIMEOUT_S = 150 ms; on timeout it retries the SAME payment with the SAME idempotency key, up to 5 attempts,
50 ms apart. The server does not know the client gave up and finishes the work anyway — exactly what Lambda,
API Gateway and most HTTP servers do.

  none          no key: BEGIN; provider call; INSERT charge; COMMIT
  check-first   SELECT the key; if absent: charge (commit), then INSERT the key and the response (commit)
  key-in-txn    BEGIN; INSERT key ... ON CONFLICT DO NOTHING; 0 rows -> return the stored response;
                else provider call; INSERT charge; store response; COMMIT
                (a concurrent duplicate WAITS on the uncommitted key, then reads the stored response)
  key-first     txn 1: INSERT key with status 'started' ... ON CONFLICT DO NOTHING, COMMIT
                  conflict: 'finished' -> replay stored response; 'started' -> HTTP 409, the client retries later
                txn 2: provider call; INSERT charge; UPDATE key SET status='finished', response=...; COMMIT
                (Stripe's published design, without its recovery points)

  bench   500 payments from 8 client threads, 3 repetitions -> idem-bench.csv
  race    two identical requests released at the same instant, 500 times per design -> idem-race-out.txt

Usage:  python idem_bench.py <dsn> bench|race
"""
import concurrent.futures as cf
import queue
import random
import sys
import threading
import time
import uuid

import psycopg

DSN, MODE = sys.argv[1], sys.argv[2]
TIMEOUT_S, ATTEMPTS, BACKOFF_S = 0.150, 5, 0.050
POOL = 40


def setup():
    with psycopg.connect(DSN, autocommit=True) as c:
        c.execute("DROP TABLE IF EXISTS charge, idem_key")
        c.execute("CREATE TABLE charge (id bigserial PRIMARY KEY, payment uuid NOT NULL, amount int NOT NULL)")
        c.execute("""CREATE TABLE idem_key (key uuid PRIMARY KEY, status text NOT NULL DEFAULT 'started',
                     response text, created_at timestamptz NOT NULL DEFAULT now())""")


class Conns:
    """One connection per server thread."""
    def __init__(self):
        self.local = threading.local()

    def get(self):
        if not hasattr(self.local, "c"):
            self.local.c = psycopg.connect(DSN, autocommit=True)
        return self.local.c


CONNS = Conns()


def provider(rnd):
    time.sleep(min(rnd.expovariate(1 / 0.080), 0.600))


def handle(design, key, amount, rnd):
    """Returns (http_status, body)."""
    c = CONNS.get()
    if design == "none":
        with c.transaction():
            provider(rnd)
            cid = c.execute("INSERT INTO charge (payment, amount) VALUES (%s, %s) RETURNING id", (key, amount)).fetchone()[0]
        return 200, f"charge {cid}"
    if design == "check-first":
        r = c.execute("SELECT response FROM idem_key WHERE key = %s", (key,)).fetchone()
        if r:
            return 200, r[0] + " (replayed)"
        with c.transaction():
            provider(rnd)
            cid = c.execute("INSERT INTO charge (payment, amount) VALUES (%s, %s) RETURNING id", (key, amount)).fetchone()[0]
        try:
            c.execute("INSERT INTO idem_key (key, status, response) VALUES (%s, 'finished', %s)", (key, f"charge {cid}"))
        except psycopg.errors.UniqueViolation:
            pass
        return 200, f"charge {cid}"
    if design == "key-in-txn":
        with c.transaction():
            n = c.execute("INSERT INTO idem_key (key) VALUES (%s) ON CONFLICT DO NOTHING", (key,)).rowcount
            if n == 0:
                r = c.execute("SELECT response FROM idem_key WHERE key = %s", (key,)).fetchone()
                return 200, r[0] + " (replayed)"
            provider(rnd)
            cid = c.execute("INSERT INTO charge (payment, amount) VALUES (%s, %s) RETURNING id", (key, amount)).fetchone()[0]
            c.execute("UPDATE idem_key SET status = 'finished', response = %s WHERE key = %s", (f"charge {cid}", key))
        return 200, f"charge {cid}"
    if design == "key-first":
        n = c.execute("INSERT INTO idem_key (key) VALUES (%s) ON CONFLICT DO NOTHING", (key,)).rowcount
        if n == 0:
            st, resp = c.execute("SELECT status, response FROM idem_key WHERE key = %s", (key,)).fetchone()
            if st == "finished":
                return 200, resp + " (replayed)"
            return 409, "in progress"
        with c.transaction():
            provider(rnd)
            cid = c.execute("INSERT INTO charge (payment, amount) VALUES (%s, %s) RETURNING id", (key, amount)).fetchone()[0]
            c.execute("UPDATE idem_key SET status = 'finished', response = %s WHERE key = %s", (f"charge {cid}", key))
        return 200, f"charge {cid}"
    raise ValueError(design)


DESIGNS = ["none", "check-first", "key-in-txn", "key-first"]

if MODE == "bench":
    print("design,rep,payments,charges,duplicate_charges,payments_charged_twice_or_more,client_ok,client_ok_replayed,"
          "client_409,client_gave_up,attempts,seconds")
    for rep in range(3):
        for design in DESIGNS:
            setup()
            ex = cf.ThreadPoolExecutor(POOL)
            stats = {"ok": 0, "replayed": 0, "409": 0, "gave_up": 0, "attempts": 0}
            lock = threading.Lock()
            payments = queue.Queue()
            for _ in range(500):
                payments.put(uuid.uuid4())

            def client(seed):
                rnd = random.Random(seed)
                while True:
                    try:
                        key = payments.get_nowait()
                    except queue.Empty:
                        return
                    outcome = "gave_up"
                    for att in range(ATTEMPTS):
                        with lock: stats["attempts"] += 1
                        fut = ex.submit(handle, design, key, 100, random.Random(rnd.random()))
                        try:
                            status, body = fut.result(timeout=TIMEOUT_S)
                        except cf.TimeoutError:
                            time.sleep(BACKOFF_S); continue
                        if status == 409:
                            with lock: stats["409"] += 1
                            time.sleep(BACKOFF_S); continue
                        outcome = "replayed" if "replayed" in body else "ok"
                        break
                    with lock: stats[outcome] += 1

            t0 = time.perf_counter()
            cs = [threading.Thread(target=client, args=(rep * 100 + i,)) for i in range(8)]
            for t in cs: t.start()
            for t in cs: t.join()
            ex.shutdown(wait=True)            # let abandoned requests finish, as a real server would
            secs = time.perf_counter() - t0
            with psycopg.connect(DSN, autocommit=True) as c:
                charges = c.execute("SELECT count(*) FROM charge").fetchone()[0]
                multi = c.execute("SELECT count(*) FROM (SELECT payment FROM charge GROUP BY payment HAVING count(*) > 1) s").fetchone()[0]
                charged = c.execute("SELECT count(DISTINCT payment) FROM charge").fetchone()[0]
            print(f"{design},{rep},500,{charges},{charges - charged},{multi},{stats['ok']},{stats['replayed']},"
                  f"{stats['409']},{stats['gave_up']},{stats['attempts']},{secs:.1f}", flush=True)

elif MODE == "race":
    N = 500
    for design in DESIGNS:
        setup()
        dup, res_kinds, waits = 0, {}, []
        ex = cf.ThreadPoolExecutor(2)
        for i in range(N):
            key = uuid.uuid4()
            bar = threading.Barrier(2)

            def go(j):
                bar.wait()
                t0 = time.perf_counter()
                s, b = handle(design, key, 100, random.Random(i * 2 + j))
                return s, b, time.perf_counter() - t0

            r = [f.result() for f in [ex.submit(go, 0), ex.submit(go, 1)]]
            for s, b, w in r:
                kind = "409" if s == 409 else ("replayed" if "replayed" in b else "charged")
                res_kinds[kind] = res_kinds.get(kind, 0) + 1
            # time the second-finishing request spent when it did not charge
            for s, b, w in r:
                if s == 409 or "replayed" in b:
                    waits.append(w)
        ex.shutdown()
        with psycopg.connect(DSN, autocommit=True) as c:
            charges = c.execute("SELECT count(*) FROM charge").fetchone()[0]
        waits.sort()
        wtxt = (f"median {1000 * waits[len(waits) // 2]:.1f} ms, max {1000 * waits[-1]:.1f} ms" if waits else "-")
        print(f"{design:12s} pairs {N}  charges {charges:5d}  duplicate charges {charges - N:4d}  "
              f"responses {res_kinds}  time taken by the non-charging request: {wtxt}", flush=True)
