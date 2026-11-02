#!/usr/bin/env python3
"""M03 Ch2 §3 §5 — a job queue in a PostgreSQL table: N workers claiming jobs six different ways.

Each run loads 1,000 pending jobs; every worker (one thread, one connection) loops: claim a job, "work" for 5 ms
(time.sleep — stands in for the real job), mark it done. Every execution of the work is recorded in memory, so a
job executed twice is counted. A worker that finds no job checks whether pending jobs remain; if they do, that
"empty" answer was spurious and it tries again.

Methods
  naive          SELECT the first pending id (no lock), work, UPDATE ... SET status = 'done'       (autocommit)
  for_update     BEGIN; SELECT ... LIMIT 1 FOR UPDATE; work; UPDATE done; COMMIT
  skip_locked    BEGIN; SELECT ... LIMIT 1 FOR UPDATE SKIP LOCKED; work; UPDATE done; COMMIT
  advisory       BEGIN; SELECT ... WHERE pg_try_advisory_xact_lock(id) LIMIT 1; work; UPDATE done; COMMIT
  claim_update   UPDATE ... SET status = 'running' WHERE id = (SELECT ... LIMIT 1) AND status = 'pending'
                 RETURNING id  (no SKIP LOCKED; autocommit); work; UPDATE done
  claim_skip     UPDATE ... SET status = 'running', claimed_by = w, claimed_at = now()
                 WHERE id = (SELECT ... LIMIT 1 FOR UPDATE SKIP LOCKED) RETURNING id  (autocommit); work; UPDATE done

Usage:  python queue_bench.py <dsn> > queue-bench.csv
"""
import sys
import threading
import time

import psycopg

DSN = sys.argv[1]
NJOBS, WORK_S = 1000, 0.005
PICK = "SELECT id FROM jobs WHERE status = 'pending' ORDER BY id LIMIT 1"


def load(c):
    c.execute("DROP TABLE IF EXISTS jobs")
    c.execute("""CREATE TABLE jobs (id bigint PRIMARY KEY, status text NOT NULL, claimed_by int,
                 claimed_at timestamptz, payload text)""")
    c.execute("CREATE INDEX jobs_pending ON jobs (id) WHERE status = 'pending'")
    c.execute(f"INSERT INTO jobs SELECT g, 'pending', NULL, NULL, 'x' FROM generate_series(1, {NJOBS}) g")
    c.execute("VACUUM ANALYZE jobs")


def pending(c):
    return c.execute("SELECT count(*) FROM jobs WHERE status = 'pending'").fetchone()[0]


def worker(method, w, start, log, stats):
    c = psycopg.connect(DSN, autocommit=True)
    spurious = 0
    start.wait()
    while True:
        jid = None
        if method == "naive":
            r = c.execute(PICK).fetchone()
            if r:
                jid = r[0]; log.append(jid); time.sleep(WORK_S)
                c.execute("UPDATE jobs SET status = 'done', claimed_by = %s WHERE id = %s", (w, jid))
        elif method in ("for_update", "skip_locked", "advisory"):
            q = {"for_update": PICK + " FOR UPDATE",
                 "skip_locked": PICK + " FOR UPDATE SKIP LOCKED",
                 "advisory": "SELECT id FROM jobs WHERE status = 'pending' AND pg_try_advisory_xact_lock(id)"
                             " ORDER BY id LIMIT 1"}[method]
            c.execute("BEGIN")
            r = c.execute(q).fetchone()
            if r:
                jid = r[0]; log.append(jid); time.sleep(WORK_S)
                c.execute("UPDATE jobs SET status = 'done', claimed_by = %s WHERE id = %s", (w, jid))
            c.execute("COMMIT")
        elif method == "claim_update":
            r = c.execute(f"""UPDATE jobs SET status = 'running', claimed_by = %s, claimed_at = now()
                              WHERE id = ({PICK}) AND status = 'pending' RETURNING id""", (w,)).fetchone()
            if r:
                jid = r[0]; log.append(jid); time.sleep(WORK_S)
                c.execute("UPDATE jobs SET status = 'done' WHERE id = %s", (jid,))
        elif method == "claim_skip":
            r = c.execute(f"""UPDATE jobs SET status = 'running', claimed_by = %s, claimed_at = now()
                              WHERE id = ({PICK} FOR UPDATE SKIP LOCKED) RETURNING id""", (w,)).fetchone()
            if r:
                jid = r[0]; log.append(jid); time.sleep(WORK_S)
                c.execute("UPDATE jobs SET status = 'done' WHERE id = %s", (jid,))
        if jid is None:
            if pending(c) == 0:
                break
            spurious += 1
            time.sleep(0.0005)
    stats.append(spurious)
    c.close()


METHODS = ["naive", "for_update", "skip_locked", "advisory", "claim_update", "claim_skip"]
print("method,workers,rep,wall_s,jobs_per_s,executions,distinct_jobs,duplicates,spurious_empty")
setup = psycopg.connect(DSN, autocommit=True)
for rep in (1, 2, 3):
    for method in METHODS:
        for n in (1, 2, 4, 8, 16, 32):
            load(setup)
            start, log, stats = threading.Barrier(n + 1), [], []
            ths = [threading.Thread(target=worker, args=(method, w, start, log, stats)) for w in range(n)]
            for t in ths:
                t.start()
            start.wait(); t0 = time.perf_counter()
            for t in ths:
                t.join()
            wall = time.perf_counter() - t0
            done = setup.execute("SELECT count(*) FROM jobs WHERE status = 'done'").fetchone()[0]
            assert done == NJOBS, (method, n, done)
            print(f"{method},{n},{rep},{wall:.3f},{NJOBS / wall:.1f},{len(log)},{len(set(log))},"
                  f"{len(log) - len(set(log))},{sum(stats)}", flush=True)
setup.execute("DROP TABLE jobs")
