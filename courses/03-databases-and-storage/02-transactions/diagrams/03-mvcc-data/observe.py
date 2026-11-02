#!/usr/bin/env python3
"""M03 Ch2 §3 §1 and §8 — hint bits cost the first reader; and observing a chain of lock waits.

  hint     a 1,000,000-row table loaded and checkpointed; the first two full scans, with buffers dirtied and WAL
  chain    A holds a row lock, B waits on A, C waits on B (via the lock queue); print the blocking tree;
           log_lock_waits is switched on for the run so the server log records the waits

Usage:  python observe.py <dsn> hint|chain
"""
import sys
import threading
import time

import psycopg

DSN, WHAT = sys.argv[1], sys.argv[2]
m = psycopg.connect(DSN, autocommit=True)

if WHAT == "hint":
    print("data_checksums =", m.execute("SHOW data_checksums").fetchone()[0],
          "| wal_log_hints =", m.execute("SHOW wal_log_hints").fetchone()[0])
    m.execute("DROP TABLE IF EXISTS hb")
    m.execute("CREATE TABLE hb (id int, v int) WITH (autovacuum_enabled = off)")
    m.execute("INSERT INTO hb SELECT g, g FROM generate_series(1, 1000000) g")
    m.execute("CHECKPOINT")
    for i in (1, 2):
        l0 = m.execute("SELECT pg_current_wal_insert_lsn()").fetchone()[0]
        plan = [r[0] for r in m.execute("EXPLAIN (ANALYZE, BUFFERS, TIMING OFF) SELECT count(*) FROM hb")]
        wal = m.execute(f"SELECT pg_current_wal_insert_lsn() - '{l0}'::pg_lsn").fetchone()[0]
        bufs = [p.strip() for p in plan if "Buffers" in p][0]
        ex = [p.strip() for p in plan if "Execution Time" in p][0]
        print(f"   scan {i}: {bufs:55s} WAL written {int(wal):>12,d} bytes   {ex}")
    m.execute("VACUUM hb")
    l0 = m.execute("SELECT pg_current_wal_insert_lsn()").fetchone()[0]
    plan = [r[0] for r in m.execute("EXPLAIN (ANALYZE, BUFFERS, TIMING OFF) SELECT count(*) FROM hb")]
    print("   after VACUUM:", [p.strip() for p in plan if "Buffers" in p][0])
    print("   table size:", m.execute("SELECT pg_size_pretty(pg_relation_size('hb'))").fetchone()[0])
    m.execute("DROP TABLE hb")

elif WHAT == "chain":
    m.execute("ALTER SYSTEM SET log_lock_waits = on"); m.execute("SELECT pg_reload_conf()")
    time.sleep(0.5)
    m.execute("DROP TABLE IF EXISTS orders; CREATE TABLE orders (id int PRIMARY KEY, status text)")
    m.execute("INSERT INTO orders VALUES (1, 'new'), (2, 'new')")
    a, b, c = (psycopg.connect(DSN, autocommit=True) for _ in range(3))
    for s, n in ((a, "worker-a"), (b, "worker-b"), (c, "migration")):
        s.execute(f"SET application_name = '{n}'")
    a.execute("BEGIN"); a.execute("UPDATE orders SET status = 'paid' WHERE id = 1")
    b.execute("BEGIN")
    tb = threading.Thread(target=lambda: b.execute("UPDATE orders SET status = 'void' WHERE id = 1")); tb.start()
    time.sleep(0.3)
    tc = threading.Thread(target=lambda: c.execute("ALTER TABLE orders ADD COLUMN note text")); tc.start()
    time.sleep(1.5)
    print("-- who is blocked by whom (pg_stat_activity + pg_blocking_pids)")
    for r in m.execute("""
        SELECT pid, application_name AS app, pg_blocking_pids(pid) AS blocked_by,
               wait_event_type || ':' || wait_event AS waiting_on, state,
               round(extract(epoch FROM now() - xact_start)::numeric, 1) AS xact_s, left(query, 50) AS query
        FROM pg_stat_activity
        WHERE backend_type = 'client backend' AND pid <> pg_backend_pid() AND datname = current_database()
        ORDER BY xact_start""").fetchall():
        print("  ", r)
    print("-- the same, from pg_locks: what each one holds or wants")
    for r in m.execute("""
        SELECT a.application_name, l.locktype, coalesce(l.relation::regclass::text, l.transactionid::text, '') AS what,
               l.mode, l.granted
        FROM pg_locks l JOIN pg_stat_activity a USING (pid)
        WHERE a.application_name IN ('worker-a','worker-b','migration') AND l.locktype IN ('relation','transactionid','tuple')
          AND (l.relation IS NULL OR l.relation = 'orders'::regclass)
        ORDER BY a.application_name, l.granted DESC, l.locktype""").fetchall():
        print("  ", r)
    a.execute("COMMIT"); tb.join(); b.execute("COMMIT"); tc.join()
    m.execute("ALTER SYSTEM RESET log_lock_waits"); m.execute("SELECT pg_reload_conf()")
    m.execute("DROP TABLE orders")
