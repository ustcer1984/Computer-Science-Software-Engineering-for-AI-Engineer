#!/usr/bin/env python3
"""M03 Ch2 §3 §1-§3 — row versions, snapshots and row locks, traced on PostgreSQL 18.

Every session is its own autocommit connection; transactions are opened with explicit BEGIN so the
order of statements across sessions is exactly the order written here. Output is plain text.

Usage:  python mvcc_trace.py postgresql://postgres:pw@localhost:55433/postgres > mvcc-trace-out.txt
"""
import sys
import threading
import time

import psycopg

DSN = sys.argv[1]


def conn():
    return psycopg.connect(DSN, autocommit=True)


def show(c, sql, label=None):
    cur = c.execute(sql)
    rows = cur.fetchall() if cur.description else []
    print(f"-- {label or sql}")
    if cur.description:
        print("   " + " | ".join(d.name for d in cur.description))
    for r in rows:
        print("   " + " | ".join("NULL" if v is None else str(v) for v in r))
    return rows


PAGE = """SELECT lp, t_xmin, t_xmax, t_ctid,
       array_to_string(raw_flags, ' ') AS flags
FROM heap_page_items(get_raw_page('acct', 0)) h,
     LATERAL heap_tuple_infomask_flags(h.t_infomask, h.t_infomask2) f
WHERE t_xmin IS NOT NULL ORDER BY lp"""
SYS = "SELECT ctid, xmin, xmax, id, bal FROM acct ORDER BY id, ctid"

a, b, c, d = conn(), conn(), conn(), conn()
a.execute("CREATE EXTENSION IF NOT EXISTS pageinspect")
a.execute("CREATE EXTENSION IF NOT EXISTS pgrowlocks")
a.execute("DROP TABLE IF EXISTS child, parent, acct")
a.execute("CREATE TABLE acct (id int PRIMARY KEY, bal int) WITH (autovacuum_enabled = off)")

print("=" * 100)
print("1. Three rows inserted by one transaction; the header before anyone has read them")
print("=" * 100)
a.execute("BEGIN")
show(a, "SELECT pg_current_xact_id() AS my_xid")
a.execute("INSERT INTO acct VALUES (1, 100), (2, 200), (3, 300)")
a.execute("COMMIT")
show(b, PAGE, "page 0, straight after the commit (no reader yet) — note: no XMIN_COMMITTED hint")
show(b, SYS, "a reader's view with system columns")
show(b, PAGE, "page 0 after that first read — the reader set the hint bit HEAP_XMIN_COMMITTED")

print()
print("=" * 100)
print("2. An UPDATE writes a new version; the old one gets xmax. Another session sees the old one until COMMIT")
print("=" * 100)
a.execute("BEGIN")
a.execute("UPDATE acct SET bal = 150 WHERE id = 1")
show(a, "SELECT pg_current_xact_id() AS updater_xid")
xid_u = a.execute("SELECT pg_current_xact_id()").fetchone()[0]
show(b, PAGE, "page 0 while the UPDATE is uncommitted")
show(a, SYS, "the updater's own view")
show(b, SYS, "another session's view")
show(b, f"SELECT pg_xact_status('{xid_u}') AS status", "pg_xact_status(updater) — what pg_xact (the commit log) says")
a.execute("COMMIT")
show(b, f"SELECT pg_xact_status('{xid_u}') AS status", "pg_xact_status(updater) after COMMIT")
show(b, SYS, "another session's view after COMMIT")
show(b, PAGE, "page 0 after COMMIT and a read: old version now XMAX_COMMITTED, i.e. dead to new snapshots")

print()
print("=" * 100)
print("3. An aborted UPDATE: nothing is undone; the new version simply belongs to an aborted xid")
print("=" * 100)
a.execute("BEGIN")
a.execute("UPDATE acct SET bal = 999 WHERE id = 2")
xid_r = a.execute("SELECT pg_current_xact_id()").fetchone()[0]
a.execute("ROLLBACK")
show(b, f"SELECT pg_xact_status('{xid_r}') AS status", f"pg_xact_status({xid_r}) after ROLLBACK")
show(b, SYS, "reader's view")
show(b, PAGE, "page 0 after the reader passed: new version XMIN_INVALID (aborted), old one XMAX_INVALID")

print()
print("=" * 100)
print("4. A snapshot: pg_current_snapshot() = xmin:xmax:in-progress list")
print("=" * 100)
c.execute("BEGIN"); c.execute("INSERT INTO acct VALUES (10, 0)")       # stays in progress
xc = c.execute("SELECT pg_current_xact_id()").fetchone()[0]
d.execute("BEGIN"); d.execute("INSERT INTO acct VALUES (11, 0)")
xd = d.execute("SELECT pg_current_xact_id()").fetchone()[0]
a.execute("BEGIN"); a.execute("INSERT INTO acct VALUES (12, 0)")
xa = a.execute("SELECT pg_current_xact_id()").fetchone()[0]
d.execute("COMMIT")                                                      # commits, but after c and a started
print(f"   in progress: C = {xc}, A = {xa};  committed: D = {xd}")
b.execute("BEGIN ISOLATION LEVEL REPEATABLE READ")
show(b, "SELECT pg_current_snapshot() AS snap, pg_current_xact_id_if_assigned() AS my_xid",
     "B (read-only so far) takes a snapshot")
show(b, "SELECT id, xmin FROM acct WHERE id >= 10 ORDER BY id", "rows 10-12 as B sees them")
show(b, f"SELECT pg_visible_in_snapshot('{xc}', pg_current_snapshot()) AS c_visible,"
        f" pg_visible_in_snapshot('{xd}', pg_current_snapshot()) AS d_visible,"
        f" pg_visible_in_snapshot('{xa}', pg_current_snapshot()) AS a_visible", "visibility of each writer to B")
c.execute("COMMIT"); a.execute("COMMIT")
show(b, "SELECT pg_current_snapshot() AS snap", "B's snapshot after C and A commit (REPEATABLE READ: unchanged)")
show(b, "SELECT id, xmin FROM acct WHERE id >= 10 ORDER BY id", "rows 10-12 as B still sees them")
b.execute("COMMIT")

print()
print("=" * 100)
print("5. READ COMMITTED vs REPEATABLE READ differ only in WHEN the snapshot is taken")
print("=" * 100)
for level in ("READ COMMITTED", "REPEATABLE READ"):
    b.execute(f"BEGIN ISOLATION LEVEL {level}")
    s1 = b.execute("SELECT pg_current_snapshot()::text, (SELECT bal FROM acct WHERE id = 3)").fetchone()
    a.execute("UPDATE acct SET bal = bal + 1 WHERE id = 3")                # autocommit: commits now
    s2 = b.execute("SELECT pg_current_snapshot()::text, (SELECT bal FROM acct WHERE id = 3)").fetchone()
    b.execute("COMMIT")
    print(f"   {level:16s} statement 1: snapshot {s1[0]:<14s} bal={s1[1]}   statement 2: snapshot {s2[0]:<14s} bal={s2[1]}")

print()
print("=" * 100)
print("6. Transaction IDs are assigned lazily: a read-only transaction never gets one")
print("=" * 100)
b.execute("BEGIN")
show(b, "SELECT count(*) AS n, pg_current_xact_id_if_assigned() AS xid FROM acct", "after a SELECT")
b.execute("SELECT * FROM acct WHERE id = 1 FOR SHARE")
show(b, "SELECT pg_current_xact_id_if_assigned() AS xid", "after SELECT ... FOR SHARE (a row lock writes to the page)")
b.execute("COMMIT")

print()
print("=" * 100)
print("7. Row locks live in the tuple header: xmax + infomask bits; two sharers => a MultiXact")
print("=" * 100)
a.execute("VACUUM acct")
for mode in ("FOR KEY SHARE", "FOR SHARE", "FOR NO KEY UPDATE", "FOR UPDATE"):
    a.execute("BEGIN")
    a.execute(f"SELECT * FROM acct WHERE id = 3 {mode}")
    xid = a.execute("SELECT pg_current_xact_id()").fetchone()[0]
    r = b.execute("""SELECT t_xmax, array_to_string(raw_flags, ' ')
        FROM heap_page_items(get_raw_page('acct', 0)) h,
             LATERAL heap_tuple_infomask_flags(h.t_infomask, h.t_infomask2) f
        WHERE t_ctid = (SELECT ctid FROM acct WHERE id = 3) AND t_xmax <> '0'""").fetchall()
    print(f"   {mode:18s} locker xid {xid}:  xmax={r[0][0] if r else None}  flags: {r[0][1] if r else None}")
    a.execute("ROLLBACK")
a.execute("BEGIN"); a.execute("SELECT * FROM acct WHERE id = 3 FOR SHARE")
b.execute("BEGIN"); b.execute("SELECT * FROM acct WHERE id = 3 FOR SHARE")
show(c, """SELECT t_xmax, array_to_string(raw_flags, ' ') AS flags
        FROM heap_page_items(get_raw_page('acct', 0)) h,
             LATERAL heap_tuple_infomask_flags(h.t_infomask, h.t_infomask2) f
        WHERE t_ctid = (SELECT ctid FROM acct WHERE id = 3)""", "two sessions FOR SHARE on row 3: xmax is now a MultiXact ID")
show(c, "SELECT locked_row, locker, multi, xids, modes FROM pgrowlocks('acct')", "pgrowlocks('acct')")
show(c, "SELECT locktype, mode, granted FROM pg_locks WHERE locktype IN ('tuple','transactionid') ORDER BY 1",
     "pg_locks holds no per-row entry for those locks (only each transaction's own xid lock)")
a.execute("ROLLBACK"); b.execute("ROLLBACK")

print()
print("=" * 100)
print("8. Locking rows writes: WAL generated by reading 100,000 rows, plain vs FOR UPDATE / FOR SHARE")
print("=" * 100)
a.execute("DROP TABLE IF EXISTS big")
a.execute("CREATE TABLE big AS SELECT g AS id, 0 AS v FROM generate_series(1, 100000) g")
a.execute("VACUUM FREEZE big")
for q in ("SELECT count(*) FROM big",
          "SELECT count(*) FROM (SELECT * FROM big FOR SHARE) s",
          "SELECT count(*) FROM (SELECT * FROM big FOR UPDATE) s"):
    l0 = a.execute("SELECT pg_current_wal_insert_lsn()").fetchone()[0]
    a.execute("BEGIN"); t0 = time.perf_counter(); a.execute(q); dt = time.perf_counter() - t0; a.execute("COMMIT")
    wal = a.execute(f"SELECT pg_current_wal_insert_lsn() - '{l0}'::pg_lsn").fetchone()[0]
    print(f"   {q:58s} WAL {int(wal):>10,d} bytes   {dt*1000:7.1f} ms")
a.execute("DROP TABLE big")

print()
print("=" * 100)
print("9. Row-lock conflict table, measured: holder takes mode X on row 1, requester tries mode Y NOWAIT")
print("=" * 100)
MODES = ["FOR KEY SHARE", "FOR SHARE", "FOR NO KEY UPDATE", "FOR UPDATE"]
print("   holder \\ requester    " + "  ".join(f"{m:>17s}" for m in MODES))
for h in MODES:
    cells = []
    for r in MODES:
        a.execute("BEGIN"); a.execute(f"SELECT * FROM acct WHERE id = 1 {h}")
        b.execute("BEGIN")
        try:
            b.execute(f"SELECT * FROM acct WHERE id = 1 {r} NOWAIT"); cells.append("ok")
        except psycopg.errors.LockNotAvailable:
            cells.append("CONFLICT")
        b.execute("ROLLBACK"); a.execute("ROLLBACK")
    print(f"   {h:22s}" + "  ".join(f"{x:>17s}" for x in cells))
print("   and the row-lock mode each write statement takes (holder) vs FOR KEY SHARE (requester):")
for h, sql in (("UPDATE non-key column", "UPDATE acct SET bal = bal WHERE id = 1"),
               ("UPDATE key column", "UPDATE acct SET id = 1001 WHERE id = 1"),
               ("DELETE", "DELETE FROM acct WHERE id = 1")):
    res = []
    for r in MODES:
        a.execute("BEGIN"); a.execute(sql); b.execute("BEGIN")
        try:
            b.execute(f"SELECT * FROM acct WHERE id = 1 {r} NOWAIT"); res.append("ok")
        except psycopg.errors.LockNotAvailable:
            res.append("CONFLICT")
        b.execute("ROLLBACK"); a.execute("ROLLBACK")
    print(f"   {h:22s}" + "  ".join(f"{x:>17s}" for x in res))

print()
print("=" * 100)
print("10. Foreign keys: a child INSERT takes FOR KEY SHARE on the parent row")
print("=" * 100)
a.execute("CREATE TABLE parent (id int PRIMARY KEY, name text, credits int)")
a.execute("CREATE TABLE child (id int PRIMARY KEY, parent_id int REFERENCES parent)")
a.execute("INSERT INTO parent VALUES (1, 'p1', 0)")
b.execute("BEGIN"); b.execute("INSERT INTO child VALUES (1, 1)")
show(c, "SELECT locked_row, multi, modes FROM pgrowlocks('parent')", "parent row locks while the child INSERT is open")
b.execute("ROLLBACK")


def try_with_timeout(conn_, sql, timeout=1.0):
    """Run sql in conn_ in a thread; return ('ok', secs) or ('blocked>1s', None)."""
    out = {}

    def run():
        t0 = time.perf_counter()
        try:
            conn_.execute(sql); out["r"] = ("ok", time.perf_counter() - t0)
        except Exception as e:  # noqa
            out["r"] = (type(e).__name__, time.perf_counter() - t0)
    th = threading.Thread(target=run); th.start(); th.join(timeout)
    return th, out


for holder_desc, holder_sql in (
        ("UPDATE parent SET credits = credits + 1 (non-key)", "UPDATE parent SET credits = credits + 1 WHERE id = 1"),
        ("SELECT ... FOR NO KEY UPDATE", "SELECT * FROM parent WHERE id = 1 FOR NO KEY UPDATE"),
        ("SELECT ... FOR UPDATE", "SELECT * FROM parent WHERE id = 1 FOR UPDATE"),
        ("UPDATE parent SET id = 2 (key column)", "UPDATE parent SET id = 2 WHERE id = 1")):
    a.execute("BEGIN"); a.execute(holder_sql)
    b.execute("BEGIN")
    th, out = try_with_timeout(b, "INSERT INTO child VALUES (2, 1)")
    status = out.get("r", ("BLOCKED (still waiting after 1 s)", None))[0]
    a.execute("ROLLBACK"); th.join(); b.execute("ROLLBACK")
    print(f"   parent holder: {holder_desc:52s} -> child INSERT: {status}")

a.execute("DROP TABLE child, parent")
for x in (a, b, c, d):
    x.close()
