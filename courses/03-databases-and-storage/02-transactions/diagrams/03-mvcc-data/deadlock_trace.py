#!/usr/bin/env python3
"""M03 Ch2 §3 §6 — a deadlock reproduced on PostgreSQL 18: who waits, who is chosen, how long detection takes.

Two sessions update rows 1 and 2 in opposite orders. A blocks first (t = 0), B closes the cycle 0.3 s later.
Run once per deadlock_timeout value. Usage:  python deadlock_trace.py <dsn>
"""
import sys
import threading
import time

import psycopg

DSN = sys.argv[1]
setup = psycopg.connect(DSN, autocommit=True)
for dt in ("1s", "200ms"):
    setup.execute("DROP TABLE IF EXISTS acct; CREATE TABLE acct (id int PRIMARY KEY, bal int)")
    setup.execute("INSERT INTO acct VALUES (1, 100), (2, 100)")
    a = psycopg.connect(DSN, autocommit=True); b = psycopg.connect(DSN, autocommit=True)
    for s in (a, b):
        s.execute(f"SET deadlock_timeout = '{dt}'")
    pa, pb = (s.execute("SELECT pg_backend_pid()").fetchone()[0] for s in (a, b))
    a.execute("BEGIN"); b.execute("BEGIN")
    a.execute("UPDATE acct SET bal = bal - 10 WHERE id = 1")
    b.execute("UPDATE acct SET bal = bal - 10 WHERE id = 2")
    res = {}
    t0 = time.perf_counter()

    def step(name, s, sql):
        t = time.perf_counter()
        try:
            s.execute(sql); res[name] = ("ok", t - t0, time.perf_counter() - t0, None)
        except psycopg.errors.DeadlockDetected as e:
            res[name] = ("40P01", t - t0, time.perf_counter() - t0, e)

    ta = threading.Thread(target=step, args=("A", a, "UPDATE acct SET bal = bal + 10 WHERE id = 2")); ta.start()
    time.sleep(0.3)
    tb = threading.Thread(target=step, args=("B", b, "UPDATE acct SET bal = bal + 10 WHERE id = 1")); tb.start()
    time.sleep(0.1)
    print(f"deadlock_timeout = {dt}   (A = pid {pa}, B = pid {pb})")
    for r in setup.execute("""SELECT pid, pg_blocking_pids(pid), wait_event_type, wait_event, left(query, 45)
                              FROM pg_stat_activity WHERE pid IN (%s, %s) ORDER BY pid""", (pa, pb)).fetchall():
        print("   while both wait:", r)
    ta.join(); tb.join()
    for name, s in (("A", a), ("B", b)):
        st, start, end, e = res[name]
        print(f"   {name}: started waiting at {start:5.2f} s, statement returned at {end:5.2f} s -> {st}")
        if e:
            print("      ERROR: ", e.diag.message_primary)
            print("      DETAIL:", (e.diag.message_detail or "").replace("\n", "\n              "))
            print("      HINT:  ", e.diag.message_hint)
        s.execute("ROLLBACK" if st != "ok" else "COMMIT")
    print("   final:", setup.execute("SELECT * FROM acct ORDER BY id").fetchall())
    a.close(); b.close()
setup.execute("DROP TABLE acct")
