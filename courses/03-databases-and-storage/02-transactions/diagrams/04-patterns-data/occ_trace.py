#!/usr/bin/env python3
"""M03 Ch2 §4 §1 — what an optimistic version check actually does inside PostgreSQL, traced with two sessions.

  1. READ COMMITTED: A and B both read version 0. A updates WHERE version = 0 and has not committed; B's identical
     UPDATE waits on A's row lock; A commits; B re-checks the row's NEW version and updates 0 rows.
  2. The same at REPEATABLE READ: B gets SQLSTATE 40001 instead of 0 rows.
  3. "The user thinks for minutes": a 5 s edit held with SELECT ... FOR UPDATE vs. done optimistically, while a second
     request changes the same row.
  4. xmin as a free version number: which statements change it.

Usage:  python occ_trace.py <dsn>
"""
import sys
import threading
import time

import psycopg

DSN = sys.argv[1]
m = psycopg.connect(DSN, autocommit=True)


def reset():
    m.execute("DROP TABLE IF EXISTS doc")
    m.execute("CREATE TABLE doc (id int PRIMARY KEY, body text, stock int, version int NOT NULL DEFAULT 0)")
    m.execute("INSERT INTO doc VALUES (1, 'draft', 10, 0)")


def race(level):
    reset()
    a, b = psycopg.connect(DSN), psycopg.connect(DSN)
    for s in (a, b):
        s.execute(f"SET TRANSACTION ISOLATION LEVEL {level}")
    va = a.execute("SELECT version FROM doc WHERE id = 1").fetchone()[0]
    vb = b.execute("SELECT version FROM doc WHERE id = 1").fetchone()[0]
    print(f"   A read version {va}; B read version {vb}")
    r = a.execute("UPDATE doc SET body = 'A', version = version + 1 WHERE id = 1 AND version = %s", (va,)).rowcount
    print(f"   A: UPDATE ... WHERE version = {va} -> {r} row (not committed yet)")
    out = {}

    def bgo():
        t0 = time.perf_counter()
        try:
            out["rows"] = b.execute("UPDATE doc SET body = 'B', version = version + 1 WHERE id = 1 AND version = %s",
                                    (vb,)).rowcount
        except psycopg.Error as e:
            out["err"] = f"{e.sqlstate} {str(e).splitlines()[0]}"
        out["wait"] = time.perf_counter() - t0

    t = threading.Thread(target=bgo); t.start()
    time.sleep(1.0)
    print(f"   B: same UPDATE issued; after 1.0 s it is still waiting: {t.is_alive()}")
    a.commit(); t.join()
    if "err" in out:
        print(f"   A commits -> B returns after {out['wait']:.2f} s with ERROR {out['err']}")
        b.rollback()
    else:
        print(f"   A commits -> B returns after {out['wait']:.2f} s, rows updated = {out['rows']}")
        b.commit()
    print("   final row:", m.execute("SELECT body, version FROM doc WHERE id = 1").fetchone())
    a.close(); b.close()


print("== 1. optimistic check at READ COMMITTED")
race("READ COMMITTED")
print("== 2. optimistic check at REPEATABLE READ")
race("REPEATABLE READ")

print("== 3. a 5 s edit while another request changes stock on the same row")
for style in ("pessimistic", "optimistic"):
    reset()
    editor, other = psycopg.connect(DSN), psycopg.connect(DSN, autocommit=True)
    res = {}

    def edit():
        if style == "pessimistic":
            editor.execute("SELECT body FROM doc WHERE id = 1 FOR UPDATE")
            time.sleep(5)
            editor.execute("UPDATE doc SET body = 'edited' WHERE id = 1")
            editor.commit(); res["edit"] = "saved"
        else:
            v = editor.execute("SELECT version FROM doc WHERE id = 1").fetchone()[0]
            editor.commit()                     # nothing held while the user thinks
            time.sleep(5)
            n = editor.execute("UPDATE doc SET body = 'edited', version = version + 1 WHERE id = 1 AND version = %s",
                               (v,)).rowcount
            editor.commit(); res["edit"] = "saved" if n else "conflict: 0 rows, show the user the new version"

    te = threading.Thread(target=edit); te.start(); time.sleep(0.2)
    t0 = time.perf_counter()
    other.execute("UPDATE doc SET stock = stock - 1, version = version + 1 WHERE id = 1")
    w = time.perf_counter() - t0
    te.join()
    print(f"   {style:11s}: the stock update waited {w:6.3f} s; the editor's save: {res['edit']}")
    editor.close(); other.close()

print("== 4. xmin as a version number")
reset()
x = lambda: m.execute("SELECT xmin::text FROM doc WHERE id = 1").fetchone()[0]
print("   after INSERT                       xmin =", x())
m.execute("UPDATE doc SET body = body WHERE id = 1")
print("   after a no-op UPDATE (body = body) xmin =", x())
m.execute("BEGIN"); m.execute("SELECT * FROM doc WHERE id = 1 FOR UPDATE"); m.execute("COMMIT")
print("   after SELECT ... FOR UPDATE        xmin =", x())
m.execute("BEGIN"); m.execute("UPDATE doc SET stock = 9 WHERE id = 1"); m.execute("UPDATE doc SET stock = 8 WHERE id = 1")
m.execute("COMMIT")
print("   after two UPDATEs in one txn       xmin =", x(), "(one transaction = one xmin)")
m.execute("CREATE TABLE doc2 AS SELECT * FROM doc")
print("   the same row copied to a new table xmin =",
      m.execute("SELECT xmin::text FROM doc2").fetchone()[0], "(a dump/restore or logical copy renumbers it)")
m.execute("DROP TABLE doc2"); m.execute("DROP TABLE doc")
