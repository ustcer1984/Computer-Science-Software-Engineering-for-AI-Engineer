#!/usr/bin/env python3
"""M03 Ch2 §3 §4 — table-level locks on PostgreSQL 18.

  matrix   the 8 x 8 conflict matrix, measured with LOCK TABLE ... NOWAIT     -> table-lock-matrix.csv
  stmts    which table-lock mode each common statement takes (pg_locks)      -> stdout
  pileup   the lock-queue pile-up: a long reader, then an ALTER TABLE, while 8 clients run point SELECTs;
           three scenarios (no DDL / DDL with no timeout / DDL with lock_timeout = 200 ms and retry)
                                                                             -> pileup.csv, pileup-waiting.csv

Usage:  python table_locks.py <dsn> matrix|stmts|pileup
"""
import csv
import random
import sys
import threading
import time

import psycopg

DSN, WHAT = sys.argv[1], sys.argv[2]
MODES = ["ACCESS SHARE", "ROW SHARE", "ROW EXCLUSIVE", "SHARE UPDATE EXCLUSIVE",
         "SHARE", "SHARE ROW EXCLUSIVE", "EXCLUSIVE", "ACCESS EXCLUSIVE"]


def conn():
    return psycopg.connect(DSN, autocommit=True)


if WHAT == "matrix":
    a, b = conn(), conn()
    a.execute("DROP TABLE IF EXISTS lt; CREATE TABLE lt (id int)")
    rows = []
    for h in MODES:
        row = []
        for r in MODES:
            a.execute("BEGIN"); a.execute(f"LOCK TABLE lt IN {h} MODE")
            b.execute("BEGIN")
            try:
                b.execute(f"LOCK TABLE lt IN {r} MODE NOWAIT"); row.append(0)
            except psycopg.errors.LockNotAvailable:
                row.append(1)
            b.execute("ROLLBACK"); a.execute("ROLLBACK")
        rows.append(row)
        print(f"{h:24s}", " ".join("X" if x else "." for x in row))
    with open("table-lock-matrix.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["held \\ requested"] + MODES)
        for h, row in zip(MODES, rows):
            w.writerow([h] + row)
    a.execute("DROP TABLE lt")

elif WHAT == "stmts":
    a, b = conn(), conn()
    a.execute("DROP TABLE IF EXISTS c2, p2, st CASCADE")
    a.execute("CREATE TABLE st (id int PRIMARY KEY, v int, w int)")
    a.execute("INSERT INTO st SELECT g, g, g FROM generate_series(1, 2000000) g")
    a.execute("CREATE TABLE p2 (id int PRIMARY KEY); CREATE TABLE c2 (id int, pid int)")
    a.execute("CREATE MATERIALIZED VIEW IF NOT EXISTS mv AS SELECT 1 AS x")
    a.execute("ANALYZE st")
    LOCKQ = """SELECT c.relname, l.mode FROM pg_locks l JOIN pg_class c ON c.oid = l.relation
               WHERE l.pid = %s AND c.relname IN ('st','p2','c2','mv') ORDER BY 1, 2"""
    in_tx = [
        "SELECT * FROM st WHERE id = 1",
        "SELECT * FROM st WHERE id = 1 FOR UPDATE",
        "SELECT * FROM st WHERE id = 1 FOR SHARE",
        "INSERT INTO st VALUES (0, 0, 0)",
        "UPDATE st SET v = v WHERE id = 1",
        "DELETE FROM st WHERE id = 1",
        "MERGE INTO st USING (SELECT 5 AS id) s ON st.id = s.id WHEN MATCHED THEN UPDATE SET v = 1",
        "ANALYZE st",
        "CREATE INDEX ON st (w)",
        "ALTER TABLE st ADD COLUMN x int",
        "ALTER TABLE st ADD COLUMN y int DEFAULT 7",
        "ALTER TABLE st ALTER COLUMN w SET STATISTICS 500",
        "ALTER TABLE st ADD CONSTRAINT w_pos CHECK (w > 0) NOT VALID",
        "ALTER TABLE st SET (fillfactor = 90)",
        "CREATE TRIGGER t BEFORE UPDATE ON st FOR EACH ROW EXECUTE FUNCTION suppress_redundant_updates_trigger()",
        "ALTER TABLE c2 ADD CONSTRAINT fk FOREIGN KEY (pid) REFERENCES p2 NOT VALID",
        "REFRESH MATERIALIZED VIEW mv",
        "TRUNCATE st",
        "DROP TABLE st",
    ]
    pid_a = a.execute("SELECT pg_backend_pid()").fetchone()[0]
    for s in in_tx:
        a.execute("BEGIN")
        a.execute(s)
        locks = b.execute(LOCKQ, (pid_a,)).fetchall()
        a.execute("ROLLBACK")
        print(f"{s[:70]:72s} {', '.join(f'{r}:{m}' for r, m in locks)}")
    a.execute("ALTER TABLE st ADD CONSTRAINT w_pos CHECK (w > 0) NOT VALID")
    a.execute("CREATE UNIQUE INDEX st_v ON st (v)")
    a.execute("UPDATE st SET w = w + 0 WHERE id <= 600000")          # some dead rows for VACUUM to chew on
    # statements that cannot run in a transaction block: run them in a thread and poll their locks
    outside = [
        "ALTER TABLE st VALIDATE CONSTRAINT w_pos",
        "VACUUM st",
        "VACUUM FULL st",
        "CLUSTER st USING st_pkey",
        "CREATE INDEX CONCURRENTLY st_w ON st (w)",
        "REINDEX INDEX CONCURRENTLY st_w",
        "DROP INDEX CONCURRENTLY st_w",
        "REINDEX TABLE st",
        "ALTER TABLE st ALTER COLUMN w TYPE bigint",
    ]
    c = conn(); pid_c = c.execute("SELECT pg_backend_pid()").fetchone()[0]
    for s in outside:
        seen = set()
        th = threading.Thread(target=lambda: c.execute(s)); th.start()
        while th.is_alive():
            for r, m in b.execute(LOCKQ, (pid_c,)).fetchall():
                seen.add(f"{r}:{m}")
            time.sleep(0.002)
        th.join()
        print(f"{s[:70]:72s} {', '.join(sorted(x for x in seen if x.startswith('st:')))}")
    a.execute("DROP TABLE st, c2, p2; DROP MATERIALIZED VIEW mv")

elif WHAT == "pileup":
    setup = conn()
    out = open("pileup.csv", "w", newline="")
    W = csv.writer(out); W.writerow(["scenario", "client", "start_s", "latency_ms"])
    wout = open("pileup-waiting.csv", "w", newline="")
    WW = csv.writer(wout); WW.writerow(["scenario", "t_s", "waiting_sessions"])
    events = []
    for scenario in ("no DDL", "DDL, no lock_timeout", "DDL, lock_timeout 200 ms + retry"):
        setup.execute("DROP TABLE IF EXISTS items")
        setup.execute("CREATE TABLE items (id int PRIMARY KEY, v int)")
        setup.execute("INSERT INTO items SELECT g, g FROM generate_series(1, 10000) g")
        setup.execute("VACUUM ANALYZE items")
        T0 = time.perf_counter() + 0.5
        STOP = T0 + 12.0
        lock = threading.Lock()

        def reader(k):
            cn = conn(); rnd = random.Random(k)
            while time.perf_counter() < T0:
                time.sleep(0.001)
            while (now := time.perf_counter()) < STOP:
                cn.execute("SELECT v FROM items WHERE id = %s", (rnd.randint(1, 10000),)).fetchone()
                lat = time.perf_counter() - now
                with lock:
                    W.writerow([scenario, k, f"{now - T0:.4f}", f"{lat * 1000:.3f}"])
                time.sleep(0.02)
            cn.close()

        def long_reader():                      # a 7-second report: holds ACCESS SHARE from t=1 to t=8
            cn = conn()
            time.sleep(max(0, T0 + 1.0 - time.perf_counter()))
            cn.execute("BEGIN"); cn.execute("SELECT count(*) FROM items")
            time.sleep(max(0, T0 + 8.0 - time.perf_counter()))
            cn.execute("COMMIT"); cn.close()
            events.append((scenario, "long reader commits", time.perf_counter() - T0))

        def ddl():
            cn = conn()
            time.sleep(max(0, T0 + 2.0 - time.perf_counter()))
            tries = 0
            if scenario == "DDL, no lock_timeout":
                t = time.perf_counter(); cn.execute("ALTER TABLE items ADD COLUMN note text")
                events.append((scenario, "ALTER done", time.perf_counter() - T0, time.perf_counter() - t))
            else:
                cn.execute("SET lock_timeout = '200ms'")
                while True:
                    tries += 1
                    try:
                        cn.execute("ALTER TABLE items ADD COLUMN note text"); break
                    except psycopg.errors.LockNotAvailable:
                        time.sleep(1.0)
                events.append((scenario, f"ALTER done after {tries} tries", time.perf_counter() - T0))
            cn.close()

        def sampler():
            cn = conn()
            while (now := time.perf_counter()) < STOP:
                if now >= T0:
                    n = cn.execute("""SELECT count(*) FROM pg_locks l JOIN pg_class c ON c.oid = l.relation
                                      WHERE c.relname = 'items' AND NOT l.granted""").fetchone()[0]
                    WW.writerow([scenario, f"{now - T0:.3f}", n])
                time.sleep(0.05)
            cn.close()

        ths = [threading.Thread(target=reader, args=(k,)) for k in range(8)] + \
              [threading.Thread(target=long_reader), threading.Thread(target=sampler)]
        if scenario != "no DDL":
            ths.append(threading.Thread(target=ddl))
        for t in ths:
            t.start()
        for t in ths:
            t.join()
        out.flush(); wout.flush()
    for e in events:
        print(e)
    setup.execute("DROP TABLE items")
