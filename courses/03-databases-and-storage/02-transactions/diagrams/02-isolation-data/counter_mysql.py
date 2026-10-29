#!/usr/bin/env python3
"""Ch2 §1's lost-update counter, on MySQL 8.4 InnoDB: 8 clients each add 1 to one row 2,000 times.

Methods: read-then-write at READ COMMITTED, at REPEATABLE READ (InnoDB's default) and at
SERIALIZABLE (retrying deadlocks, which is how InnoDB reports a conflict there);
UPDATE … SET n = n + 1; and SELECT … FOR UPDATE then write.

    python counter_mysql.py > counter-mysql.csv      # needs MySQL on localhost:53306
"""
import sys
import threading
import time

import pymysql

CLIENTS, PER_CLIENT, REPS = 8, 2000, 3
LOCK = threading.Lock()


def connect():
    return pymysql.connect(host="127.0.0.1", port=53306, user="root", password="x", database="t", autocommit=True)


def worker(method, level, stats):
    c = connect()
    cur = c.cursor()
    cur.execute(f"SET SESSION TRANSACTION ISOLATION LEVEL {level}")
    for _ in range(PER_CLIENT):
        for attempt in range(1000):
            try:
                cur.execute("START TRANSACTION")
                if method == "atomic":
                    cur.execute("UPDATE counter SET n = n + 1 WHERE id = 1")
                else:
                    lock = " FOR UPDATE" if method == "forupdate" else ""
                    cur.execute("SELECT n FROM counter WHERE id = 1" + lock)
                    n = cur.fetchone()[0]
                    cur.execute("UPDATE counter SET n = %s WHERE id = 1", (n + 1,))
                cur.execute("COMMIT")
                break
            except pymysql.err.OperationalError as e:
                cur.execute("ROLLBACK")
                if e.args[0] in (1213, 1205):      # deadlock, lock wait timeout: retry
                    with LOCK:
                        stats["retries"] += 1
                    continue
                raise
        else:
            with LOCK:
                stats["failed"] += 1
    c.close()


METHODS = [("rmw", "READ COMMITTED"), ("rmw", "REPEATABLE READ"), ("rmw", "SERIALIZABLE"),
           ("atomic", "REPEATABLE READ"), ("forupdate", "REPEATABLE READ")]

if __name__ == "__main__":
    print("method,level,rep,expected,final,retries,failed,seconds")
    admin = connect().cursor()
    admin.execute("DROP TABLE IF EXISTS counter")
    admin.execute("CREATE TABLE counter (id int PRIMARY KEY, n bigint)")
    admin.execute("INSERT INTO counter VALUES (1, 0)")
    for method, level in METHODS:
        for rep in range(1, REPS + 1):
            admin.execute("UPDATE counter SET n = 0 WHERE id = 1")
            stats = {"retries": 0, "failed": 0}
            ts = [threading.Thread(target=worker, args=(method, level, stats)) for _ in range(CLIENTS)]
            t0 = time.monotonic()
            for t in ts:
                t.start()
            for t in ts:
                t.join()
            dt = time.monotonic() - t0
            admin.execute("SELECT n FROM counter WHERE id = 1")
            print(f"{method},{level},{rep},{CLIENTS * PER_CLIENT},{admin.fetchone()[0]},"
                  f"{stats['retries']},{stats['failed']},{dt:.1f}", flush=True)
