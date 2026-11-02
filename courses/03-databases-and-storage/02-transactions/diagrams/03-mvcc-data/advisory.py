#!/usr/bin/env python3
"""M03 Ch2 §3 §7 — advisory locks on PostgreSQL 18: scopes, stacking, key spaces, the lock-table limit, hash
collisions, a transaction-mode pooler (real PgBouncer), and a session lock that outlives a "Lambda" request.

Usage:  python advisory.py <dsn> [<pgbouncer-dsn>]
The PgBouncer part runs only if the second DSN is given (pool_mode = transaction, default_pool_size = 2).
"""
import sys
import threading
import time

import psycopg

DSN = sys.argv[1]
BOUNCER = sys.argv[2] if len(sys.argv) > 2 else None
notices = []


def conn(dsn=DSN):
    c = psycopg.connect(dsn, autocommit=True, prepare_threshold=None)
    c.add_notice_handler(lambda d: notices.append(f"{d.severity}: {d.message_primary}"))
    return c


def one(c, sql, args=None):
    return c.execute(sql, args).fetchone()[0]


a, b, m = conn(), conn(), conn()
print("1. Scope ----------------------------------------------------------------------------------")
print("   A: pg_advisory_lock(1) outside a transaction  ->", one(a, "SELECT pg_advisory_lock(1)::text"))
print("   B: pg_try_advisory_lock(1)                    ->", one(b, "SELECT pg_try_advisory_lock(1)"))
a.execute("BEGIN"); one(a, "SELECT pg_advisory_lock(2)::text"); a.execute("ROLLBACK")
print("   A: BEGIN; pg_advisory_lock(2); ROLLBACK;  B: pg_try_advisory_lock(2) ->",
      one(b, "SELECT pg_try_advisory_lock(2)"), "  (the session lock survived the rollback)")
a.execute("BEGIN"); one(a, "SELECT pg_advisory_xact_lock(3)::text")
print("   A: BEGIN; pg_advisory_xact_lock(3);       B: pg_try_advisory_lock(3) ->", one(b, "SELECT pg_try_advisory_lock(3)"))
a.execute("COMMIT")
print("   A: COMMIT;                                B: pg_try_advisory_lock(3) ->", one(b, "SELECT pg_try_advisory_lock(3)"))
one(b, "SELECT pg_advisory_unlock(3)")
print("   A: pg_advisory_unlock_all();", one(a, "SELECT pg_advisory_unlock_all()::text"))

print("2. Stacking (re-entrant, counted) ---------------------------------------------------------")
one(a, "SELECT pg_advisory_lock(9)::text"); one(a, "SELECT pg_advisory_lock(9)::text")
print("   A: lock(9) twice; unlock(9) once ->", one(a, "SELECT pg_advisory_unlock(9)"),
      "; B: try(9) ->", one(b, "SELECT pg_try_advisory_lock(9)"))
print("   A: unlock(9) again ->", one(a, "SELECT pg_advisory_unlock(9)"), "; B: try(9) ->", one(b, "SELECT pg_try_advisory_lock(9)"))
one(b, "SELECT pg_advisory_unlock(9)")
notices.clear()
print("   A: unlock(10), never taken ->", one(a, "SELECT pg_advisory_unlock(10)"), "  notice:", notices)

print("3. Blocking vs try, shared vs exclusive, and what pg_locks shows ----------------------------")
one(a, "SELECT pg_advisory_lock(42)::text")
t0 = time.perf_counter(); res = {}
th = threading.Thread(target=lambda: res.setdefault("r", (one(b, "SELECT pg_advisory_lock(42)::text"),
                                                           time.perf_counter() - t0)))
th.start(); time.sleep(0.5)
for r in m.execute("""SELECT l.pid, l.locktype, l.classid, l.objid, l.objsubid, l.mode, l.granted,
                             a.wait_event_type, a.wait_event
                      FROM pg_locks l JOIN pg_stat_activity a USING (pid)
                      WHERE l.locktype = 'advisory' ORDER BY l.granted DESC""").fetchall():
    print("  ", r)
waiter = one(m, "SELECT pid FROM pg_locks WHERE locktype = 'advisory' AND NOT granted")
print(f"   pg_blocking_pids({waiter}) =", one(m, "SELECT pg_blocking_pids(%s)", (waiter,)),
      " A's pid =", one(a, "SELECT pg_backend_pid()"))
time.sleep(0.5); one(a, "SELECT pg_advisory_unlock(42)"); th.join()
print(f"   B's blocking pg_advisory_lock(42) returned after {res['r'][1]:.2f} s, when A unlocked")
one(b, "SELECT pg_advisory_unlock(42)")
one(a, "SELECT pg_advisory_lock_shared(43)::text")
print("   A holds shared(43): B try shared ->", one(b, "SELECT pg_try_advisory_lock_shared(43)"),
      "; B try exclusive ->", one(m, "SELECT pg_try_advisory_lock(43)"))
a.execute("SELECT pg_advisory_unlock_all()"); b.execute("SELECT pg_advisory_unlock_all()")
print("   key spaces: A lock(bigint 1) ->", one(a, "SELECT pg_try_advisory_lock(1::bigint)"),
      "; B lock(int 0, int 1) ->", one(b, "SELECT pg_try_advisory_lock(0, 1)"))
for r in m.execute("""SELECT classid, objid, objsubid FROM pg_locks WHERE locktype = 'advisory'
                      ORDER BY objsubid""").fetchall():
    print("     pg_locks row: classid, objid, objsubid =", r)
a.execute("SELECT pg_advisory_unlock_all()"); b.execute("SELECT pg_advisory_unlock_all()")

print("4. Advisory locks live in the shared lock table: how many fit in one transaction ------------")
print("   max_locks_per_transaction =", one(m, "SHOW max_locks_per_transaction"),
      ", max_connections =", one(m, "SHOW max_connections"),
      ", max_prepared_transactions =", one(m, "SHOW max_prepared_transactions"))
lo, hi = 1, 400000
while lo < hi:
    mid = (lo + hi + 1) // 2
    a.execute("BEGIN")
    try:
        a.execute(f"SELECT count(pg_advisory_xact_lock(g)) FROM generate_series(1, {mid}) g"); ok = True
    except psycopg.errors.OutOfMemory as e:
        ok = False; err = e
    a.execute("ROLLBACK")
    lo, hi = (mid, hi) if ok else (lo, mid - 1)
print(f"   largest number of advisory locks one transaction could take: {lo:,d}; one more ->")
print("   ERROR:", err.diag.message_primary, "| HINT:", err.diag.message_hint)
a.execute("BEGIN")
a.execute("SELECT id FROM generate_series(1, 1000) id WHERE pg_try_advisory_xact_lock(id) ORDER BY random() LIMIT 1")
print("   a claim query with ORDER BY random() (sort, so the filter runs on every row) holds",
      one(m, "SELECT count(*) FROM pg_locks WHERE locktype = 'advisory'"), "advisory locks for 1 row returned")
a.execute("ROLLBACK")

print("5. Hashing names to keys: collisions among 200,000 distinct names -------------------------")
n = 200000
d32 = one(m, f"SELECT count(DISTINCT hashtext('job:' || g)) FROM generate_series(1, {n}) g")
d64 = one(m, f"SELECT count(DISTINCT hashtextextended('job:' || g, 0)) FROM generate_series(1, {n}) g")
print(f"   hashtext (32-bit):          {n - d32} collisions   (birthday estimate n^2/2^33 = {n * (n - 1) / 2 / 2 ** 32:.2f})")
print(f"   hashtextextended (64-bit):  {n - d64} collisions   (estimate {n * (n - 1) / 2 / 2 ** 64:.1e})")
ex = m.execute(f"""SELECT h, array_agg(s ORDER BY s) FROM (SELECT 'job:' || g AS s, hashtext('job:' || g) AS h
                   FROM generate_series(1, {n}) g) x GROUP BY h HAVING count(*) > 1 LIMIT 2""").fetchall()
for h, names in ex:
    print(f"     e.g. hashtext({names[0]!r}) = hashtext({names[1]!r}) = {h}")

print("6. A session lock that outlives a request (a warm Lambda container) ------------------------")
container_a, container_b = conn(), conn()       # module-level connections, one per container


def handler(c, job):                            # takes a session lock; the work fails before the unlock
    if not one(c, "SELECT pg_try_advisory_lock(hashtextextended(%s, 0))", (job,)):
        return "skipped: locked"
    raise TimeoutError("downstream call timed out")      # pg_advisory_unlock is never reached


for i, (name, c) in enumerate((("A", container_a), ("B", container_b), ("A", container_a), ("B", container_b))):
    try:
        out = handler(c, "nightly-report")
    except TimeoutError as e:
        out = f"raised {e!r}"
    print(f"   invocation {i + 1} on container {name}: {out}")
held = one(m, "SELECT count(*) FROM pg_locks WHERE locktype = 'advisory' AND granted")
print("   advisory locks still held (container A's connection is idle, the request is long over):", held)
print("   container A's connection, idle:", m.execute("""SELECT state, now() - state_change FROM pg_stat_activity
       WHERE pid = %s""", (one(container_a, "SELECT pg_backend_pid()"),)).fetchone())
container_a.execute("SET idle_session_timeout = '3s'")
t0 = time.perf_counter()
while one(m, "SELECT count(*) FROM pg_locks WHERE locktype = 'advisory'") > 0:
    time.sleep(0.05)
print(f"   with idle_session_timeout = 3s on that session, the server closed it and the lock went after "
      f"{time.perf_counter() - t0:.1f} s")
print("   invocation 5 on container B:", handler.__name__, "->", end=" ")
try:
    print(handler(container_b, "nightly-report"))
except TimeoutError as e:
    print("acquired the lock, then raised", repr(e))
container_b.close()


def handler_xact(c, job):                       # the same handler with a transaction-scoped lock
    with c.transaction():
        if not one(c, "SELECT pg_try_advisory_xact_lock(hashtextextended(%s, 0))", (job,)):
            return "skipped: locked"
        raise TimeoutError("downstream call timed out")


container_c = conn()
for i in range(2):
    try:
        out = handler_xact(container_c, "nightly-report")
    except TimeoutError as e:
        out = f"raised {e!r}"
    print(f"   xact-scoped version, invocation {i + 1}: {out}; locks held afterwards:",
          one(m, "SELECT count(*) FROM pg_locks WHERE locktype = 'advisory'"))

if BOUNCER:
    print("7. Through PgBouncer in transaction mode (default_pool_size = 2) -------------------------")
    x, y, z = conn(BOUNCER), conn(BOUNCER), conn(BOUNCER)
    q = "SELECT pg_backend_pid(), pg_try_advisory_lock(42)"
    pid, ok = x.execute(q).fetchone(); print(f"   client X: try_lock(42) -> {ok}   (ran on server backend {pid})")
    pid, ok = y.execute(q).fetchone(); print(f"   client Y: try_lock(42) -> {ok}   (ran on server backend {pid})")
    y.execute("BEGIN"); pid_y = one(y, "SELECT pg_backend_pid()")
    print(f"   client Y: BEGIN ... (holds server backend {pid_y} for its transaction)")
    notices.clear()
    pid, ok = x.execute("SELECT pg_backend_pid(), pg_advisory_unlock(42)").fetchone()
    print(f"   client X: unlock(42) -> {ok}   (ran on server backend {pid})  notice: {notices}")
    pid, ok = z.execute(q).fetchone(); print(f"   client Z: try_lock(42) -> {ok}   (ran on server backend {pid})")
    y.execute("COMMIT")
    for r in m.execute("""SELECT pid, objid, granted FROM pg_locks WHERE locktype = 'advisory'""").fetchall():
        print("   pg_locks on the server: advisory lock 42 held by backend", r[0])
    x.close(); y.close(); z.close()
