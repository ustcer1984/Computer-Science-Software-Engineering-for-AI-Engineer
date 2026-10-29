#!/usr/bin/env python3
"""Run two- and three-session schedules against PostgreSQL and MySQL, step by step.

Used for M03 Ch2 §2. Each session is its own connection in its own thread. Steps run
in the order written; a step that has not finished after BLOCK_S seconds is recorded
as blocked, and the schedule moves on — the step's eventual result is recorded when it
arrives. This is the method of Martin Kleppmann's Hermitage test suite
(https://github.com/ept/hermitage), automated.

    python schedules.py pg   > results-pg.txt     # needs PG on localhost:55432
    python schedules.py my   > results-my.txt     # needs MySQL on localhost:53306

Writes the outcome matrix to outcomes-<engine>.csv beside this file.
"""
import csv
import os
import queue
import sys
import threading
import time

BLOCK_S = 1.0
HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = sys.argv[1] if len(sys.argv) > 1 else "pg"

if ENGINE == "pg":
    import psycopg
    LEVELS = ["READ COMMITTED", "REPEATABLE READ", "SERIALIZABLE"]

    def connect():
        c = psycopg.connect("host=localhost port=55432 user=postgres password=x dbname=postgres", autocommit=True)
        return c

    def begin(level):
        return [f"BEGIN ISOLATION LEVEL {level}"]

    def err(e):
        return f"ERROR {getattr(e, 'sqlstate', '')}: {str(e).splitlines()[0]}"
else:
    import pymysql
    from pymysql.constants import CLIENT
    LEVELS = ["READ UNCOMMITTED", "READ COMMITTED", "REPEATABLE READ", "SERIALIZABLE"]

    def connect():
        # FOUND_ROWS: report rows matched by an UPDATE, as PostgreSQL does, not rows changed
        c = pymysql.connect(host="127.0.0.1", port=53306, user="root", password="x", database="t", autocommit=True,
                            client_flag=CLIENT.FOUND_ROWS)
        c.cursor().execute("SET SESSION innodb_lock_wait_timeout = 5")
        return c

    def begin(level):
        return [f"SET TRANSACTION ISOLATION LEVEL {level}", "START TRANSACTION"]

    def err(e):
        return f"ERROR {e.args[0]}: {e.args[1] if len(e.args) > 1 else ''}"


class Session(threading.Thread):
    def __init__(self, name):
        super().__init__(daemon=True)
        self.name, self.conn, self.q = name, connect(), queue.Queue()
        self.start()

    def run(self):
        while True:
            sql, box, done = self.q.get()
            try:
                cur = self.conn.cursor()
                cur.execute(sql)
                rows = cur.fetchall() if cur.description else None
                status = getattr(cur, "statusmessage", None) or f"{cur.rowcount} row(s)"
                box["out"] = (", ".join("(" + ", ".join(str(v) for v in r) + ")" for r in rows) or "no rows") if rows is not None else status
            except Exception as e:  # noqa: BLE001 — the error IS the observation
                box["out"] = err(e)
            box["t"] = time.monotonic()
            done.set()

    def submit(self, sql):
        box, done = {}, threading.Event()
        self.q.put((sql, box, done))
        return box, done


def run(setup, steps, level, check):
    """steps: list of (session, sql); 'BEGIN' expands to the level's begin statements."""
    admin = connect()
    for s in setup:
        admin.cursor().execute(s)
    # A session's statements queue in its own thread, so a statement issued while an
    # earlier one is blocked runs when that one returns, as it would for a real client.
    sessions, log, pending = {}, [], []

    def drain():
        for p in sorted([p for p in pending if p[1].is_set()], key=lambda p: p[2]["t"]):
            log.append(f"  {p[0]}: ... {p[3]}  ->  {p[2]['out']}  (returned)")
            pending.remove(p)

    for who, sql in steps:
        if who not in sessions:
            sessions[who] = Session(who)
        for st in (begin(level) if sql == "BEGIN" else [sql]):
            busy = any(p[0] == who for p in pending)
            box, done = sessions[who].submit(st)
            if done.wait(BLOCK_S):
                drain()
                log.append(f"  {who}: {st}  ->  {box['out']}")
            else:
                log.append(f"  {who}: {st}  ->  " + ("(queued behind its blocked statement)" if busy else "(blocked)"))
                pending.append((who, done, box, st))
        time.sleep(0.2)  # let a statement this one released finish before we look
        drain()
    for p in list(pending):
        p[1].wait(10)
    drain()
    for p in pending:
        log.append(f"  {p[0]}: ... {p[3]}  ->  still blocked at the end")
    cur = admin.cursor()
    cur.execute(check)
    final = cur.fetchall()
    for s in sessions.values():
        s.conn.close()
    admin.close()
    return log, final


T = "CREATE TABLE test (id int PRIMARY KEY, value int)"
SETUP = ["DROP TABLE IF EXISTS test", T, "INSERT INTO test VALUES (1, 10), (2, 20)"]
ALL = "SELECT id, value FROM test ORDER BY id"

CASES = {
    "dirty write": (SETUP, [
        ("T1", "BEGIN"), ("T2", "BEGIN"),
        ("T1", "UPDATE test SET value = 11 WHERE id = 1"),
        ("T2", "UPDATE test SET value = 12 WHERE id = 1"),
        ("T1", "UPDATE test SET value = 21 WHERE id = 2"),
        ("T1", "COMMIT"),
        ("T2", "UPDATE test SET value = 22 WHERE id = 2"),
        ("T2", "COMMIT")], ALL),
    "dirty read": (SETUP, [
        ("T1", "BEGIN"), ("T2", "BEGIN"),
        ("T1", "UPDATE test SET value = 101 WHERE id = 1"),
        ("T2", "SELECT value FROM test WHERE id = 1"),
        ("T1", "ROLLBACK"),
        ("T2", "COMMIT")], ALL),
    "non-repeatable read": (SETUP, [
        ("T1", "BEGIN"), ("T2", "BEGIN"),
        ("T1", "SELECT value FROM test WHERE id = 1"),
        ("T2", "UPDATE test SET value = 12 WHERE id = 1"),
        ("T2", "COMMIT"),
        ("T1", "SELECT value FROM test WHERE id = 1"),
        ("T1", "COMMIT")], ALL),
    "read skew": (SETUP, [
        ("T1", "BEGIN"), ("T2", "BEGIN"),
        ("T1", "SELECT value FROM test WHERE id = 1"),
        ("T2", "UPDATE test SET value = 12 WHERE id = 1"),
        ("T2", "UPDATE test SET value = 18 WHERE id = 2"),
        ("T2", "COMMIT"),
        ("T1", "SELECT value FROM test WHERE id = 2"),
        ("T1", "COMMIT")], ALL),
    "phantom": (SETUP, [
        ("T1", "BEGIN"), ("T2", "BEGIN"),
        ("T1", "SELECT id, value FROM test WHERE value % 3 = 0"),
        ("T2", "INSERT INTO test VALUES (3, 30)"),
        ("T2", "COMMIT"),
        ("T1", "SELECT id, value FROM test WHERE value % 3 = 0"),
        ("T1", "COMMIT")], ALL),
    "lost update": (SETUP, [
        ("T1", "BEGIN"), ("T2", "BEGIN"),
        ("T1", "SELECT value FROM test WHERE id = 1"),
        ("T2", "SELECT value FROM test WHERE id = 1"),
        ("T1", "UPDATE test SET value = 11 WHERE id = 1"),
        ("T2", "UPDATE test SET value = 11 WHERE id = 1"),
        ("T1", "COMMIT"),
        ("T2", "COMMIT")], ALL),
    # value + 1 in SQL (§1's correct version): does the engine use the newest value?
    "update in SQL": (SETUP, [
        ("T1", "BEGIN"), ("T2", "BEGIN"),
        ("T1", "SELECT value FROM test WHERE id = 1"),
        ("T2", "SELECT value FROM test WHERE id = 1"),
        ("T1", "UPDATE test SET value = value + 1 WHERE id = 1"),
        ("T2", "UPDATE test SET value = value + 1 WHERE id = 1"),
        ("T1", "COMMIT"),
        ("T2", "SELECT value FROM test WHERE id = 1"),
        ("T2", "COMMIT")], ALL),
    "write skew": (SETUP, [
        ("T1", "BEGIN"), ("T2", "BEGIN"),
        ("T1", "SELECT id, value FROM test WHERE id IN (1, 2)"),
        ("T2", "SELECT id, value FROM test WHERE id IN (1, 2)"),
        ("T1", "UPDATE test SET value = 11 WHERE id = 1"),
        ("T2", "UPDATE test SET value = 21 WHERE id = 2"),
        ("T1", "COMMIT"),
        ("T2", "COMMIT")], ALL),
    "write skew on a predicate": (SETUP, [
        ("T1", "BEGIN"), ("T2", "BEGIN"),
        ("T1", "SELECT id, value FROM test WHERE value % 3 = 0"),
        ("T2", "SELECT id, value FROM test WHERE value % 3 = 0"),
        ("T1", "INSERT INTO test VALUES (3, 30)"),
        ("T2", "INSERT INTO test VALUES (4, 42)"),
        ("T1", "COMMIT"),
        ("T2", "COMMIT")], ALL),
}

# Doctors on call: the rule is "at least one doctor on call". Each checks, then leaves.
DOC = ["DROP TABLE IF EXISTS doctors",
       "CREATE TABLE doctors (name varchar(10) PRIMARY KEY, on_call boolean NOT NULL)",
       "INSERT INTO doctors VALUES ('alice', true), ('bob', true)"]
CASES["doctors on call"] = (DOC, [
    ("Alice", "BEGIN"), ("Bob", "BEGIN"),
    ("Alice", "SELECT count(*) FROM doctors WHERE on_call"),
    ("Bob", "SELECT count(*) FROM doctors WHERE on_call"),
    ("Alice", "UPDATE doctors SET on_call = false WHERE name = 'alice'"),
    ("Bob", "UPDATE doctors SET on_call = false WHERE name = 'bob'"),
    ("Alice", "COMMIT"),
    ("Bob", "COMMIT")], "SELECT name, on_call FROM doctors ORDER BY name")

# Fekete, O'Neil and O'Neil 2004: a read-only transaction that sees an impossible state.
# x = checking, y = savings. T1 deposits 20 into savings. T2 withdraws 10 from checking,
# charging a fee of 1 if x + y would go negative. T3 only reads.
FEK = ["DROP TABLE IF EXISTS bank", "CREATE TABLE bank (k char(1) PRIMARY KEY, bal int)",
       "INSERT INTO bank VALUES ('x', 0), ('y', 0)"]
CASES["read-only anomaly"] = (FEK, [
    ("T2", "BEGIN"),
    ("T2", "SELECT k, bal FROM bank ORDER BY k"),                    # sees x = 0, y = 0: x + y - 10 < 0, so fee
    ("T1", "BEGIN"),
    ("T1", "UPDATE bank SET bal = bal + 20 WHERE k = 'y'"),
    ("T1", "COMMIT"),
    ("T3", "BEGIN"),
    ("T3", "SELECT k, bal FROM bank ORDER BY k"),                    # sees x = 0, y = 20
    ("T3", "COMMIT"),
    ("T2", "UPDATE bank SET bal = bal - 11 WHERE k = 'x'"),          # withdraw 10 + fee 1
    ("T2", "COMMIT")], "SELECT k, bal FROM bank ORDER BY k")

# The same two writers without the read-only report: serializable as T2 before T1.
CASES["read-only anomaly, without T3"] = (FEK, [
    ("T2", "BEGIN"),
    ("T2", "SELECT k, bal FROM bank ORDER BY k"),
    ("T1", "BEGIN"),
    ("T1", "UPDATE bank SET bal = bal + 20 WHERE k = 'y'"),
    ("T1", "COMMIT"),
    ("T2", "UPDATE bank SET bal = bal - 11 WHERE k = 'x'"),
    ("T2", "COMMIT")], "SELECT k, bal FROM bank ORDER BY k")

# A write inside a snapshot: does UPDATE see rows the snapshot does not?
CASES["phantom seen by a write"] = (SETUP, [
    ("T1", "BEGIN"),
    ("T1", "SELECT id, value FROM test WHERE value % 3 = 0"),
    ("T2", "BEGIN"),
    ("T2", "INSERT INTO test VALUES (3, 30)"),
    ("T2", "COMMIT"),
    ("T1", "UPDATE test SET value = value + 3 WHERE value % 3 = 0"),
    ("T1", "SELECT id, value FROM test WHERE value % 3 = 0"),
    ("T1", "COMMIT")], ALL)

# Not an isolation anomaly: what an error does to the rest of the transaction.
CASES["error mid-transaction"] = (SETUP, [
    ("T1", "BEGIN"),
    ("T1", "UPDATE test SET value = 11 WHERE id = 1"),
    ("T1", "INSERT INTO test VALUES (2, 99)"),                       # duplicate key
    ("T1", "COMMIT")], ALL)

if ENGINE == "pg":
    # PostgreSQL docs, 13.2.1: the READ COMMITTED re-check of an UPDATE's WHERE clause.
    WEB = ["DROP TABLE IF EXISTS website", "CREATE TABLE website (id int PRIMARY KEY, hits int)",
           "INSERT INTO website VALUES (1, 9), (2, 10)"]
    CASES["re-check surprise"] = (WEB, [
        ("T1", "BEGIN"), ("T2", "BEGIN"),
        ("T1", "UPDATE website SET hits = hits + 1"),
        ("T2", "DELETE FROM website WHERE hits = 10"),
        ("T1", "COMMIT"),
        ("T2", "COMMIT")], "SELECT id, hits FROM website ORDER BY id")

    # Three ways to stop the doctors' write skew without SERIALIZABLE — and one that looks right but is not.
    CASES["doctors, FOR UPDATE"] = (DOC, [
        ("Alice", "BEGIN"), ("Bob", "BEGIN"),
        ("Alice", "SELECT count(*) FROM (SELECT 1 FROM doctors WHERE on_call FOR UPDATE) s"),
        ("Bob", "SELECT count(*) FROM (SELECT 1 FROM doctors WHERE on_call FOR UPDATE) s"),
        # the application leaves only if its check returned 2 or more; the UPDATE re-states that decision
        ("Alice", "UPDATE doctors SET on_call = false WHERE name = 'alice' "
                  "AND (SELECT count(*) FROM doctors WHERE on_call) >= 2"),
        ("Alice", "COMMIT"),
        ("Bob", "UPDATE doctors SET on_call = false WHERE name = 'bob' "
                "AND (SELECT count(*) FROM doctors WHERE on_call) >= 2"),
        ("Bob", "COMMIT")], "SELECT name, on_call FROM doctors ORDER BY name")
    CASES["doctors, one statement"] = (DOC, [
        ("Alice", "BEGIN"), ("Bob", "BEGIN"),
        ("Alice", "UPDATE doctors SET on_call = false WHERE name = 'alice' "
                  "AND (SELECT count(*) FROM doctors WHERE on_call) >= 2"),
        ("Bob", "UPDATE doctors SET on_call = false WHERE name = 'bob' "
                "AND (SELECT count(*) FROM doctors WHERE on_call) >= 2"),
        ("Alice", "COMMIT"),
        ("Bob", "COMMIT")], "SELECT name, on_call FROM doctors ORDER BY name")
    BOOK = ["CREATE EXTENSION IF NOT EXISTS btree_gist", "DROP TABLE IF EXISTS booking",
            "CREATE TABLE booking (room int, during tstzrange, "
            "EXCLUDE USING gist (room WITH =, during WITH &&))"]
    CASES["double booking, exclusion constraint"] = (BOOK, [
        ("T1", "BEGIN"), ("T2", "BEGIN"),
        ("T1", "SELECT count(*) FROM booking WHERE room = 1 AND during && '[2026-11-02 10:00, 2026-11-02 11:00)'"),
        ("T2", "SELECT count(*) FROM booking WHERE room = 1 AND during && '[2026-11-02 10:30, 2026-11-02 11:30)'"),
        ("T1", "INSERT INTO booking VALUES (1, '[2026-11-02 10:00, 2026-11-02 11:00)')"),
        ("T2", "INSERT INTO booking VALUES (1, '[2026-11-02 10:30, 2026-11-02 11:30)')"),
        ("T1", "COMMIT"),
        ("T2", "COMMIT")], "SELECT room, lower(during)::time, upper(during)::time FROM booking ORDER BY 2")

if __name__ == "__main__":
    out = []
    only = sys.argv[2:] or list(CASES)
    for name in only:
        setup, steps, check = CASES[name]
        for level in LEVELS:
            log, final = run(setup, steps, level, check)
            print(f"### {name} — {ENGINE} {level}")
            print("\n".join(log))
            fin = ", ".join("(" + ", ".join(str(v) for v in r) + ")" for r in final)
            print(f"  final: {fin}\n")
            out.append({"case": name, "engine": ENGINE, "level": level, "final": fin,
                        "errors": " | ".join(l.strip() for l in log if "ERROR" in l),
                        "blocked": sum("(blocked)" in l for l in log)})
    if not sys.argv[2:]:
        with open(os.path.join(HERE, f"outcomes-{ENGINE}.csv"), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(out[0]))
            w.writeheader()
            w.writerows(out)
