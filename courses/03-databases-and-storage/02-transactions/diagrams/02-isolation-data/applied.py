"""M03 Ch2 §2 §12 experiments on PostgreSQL 18. Usage: python applied.py DSN"""
import sys, threading, time, psycopg
DSN = sys.argv[1]
def conn(ac=False): return psycopg.connect(DSN, autocommit=ac)
def setup():
    with conn(True) as c:
        c.execute("DROP TABLE IF EXISTS cat, meta, board")
        c.execute("CREATE TABLE cat(id int primary key, wave int)")
        c.execute("INSERT INTO cat SELECT g, 1 FROM generate_series(1,100) g")
        c.execute("CREATE TABLE meta(k text primary key, v int)"); c.execute("INSERT INTO meta VALUES ('snapshot',1)")
        c.execute("CREATE TABLE board(model int primary key, score float)")
        c.execute("INSERT INTO board SELECT g, g FROM generate_series(1,50) g")

def e1(level, reload_sql):
    setup(); r = conn(); w = conn()
    r.execute(f"BEGIN ISOLATION LEVEL {level}")
    snap = r.execute("SELECT v FROM meta").fetchone()[0]        # snapshot taken here (RR)
    w.execute("BEGIN"); w.execute(reload_sql); w.execute("INSERT INTO cat SELECT g, 2 FROM generate_series(1,120) g"); w.execute("COMMIT")
    rows = r.execute("SELECT count(*), min(wave), max(wave) FROM cat").fetchone()
    r.execute("COMMIT"); r.close(); w.close()
    return snap, rows

print("E1  reader snapshot taken, then a reload (old 100 rows wave 1 -> new 120 rows wave 2) commits, then reader reads cat")
for level in ("READ COMMITTED", "REPEATABLE READ"):
    for name, sql in (("TRUNCATE", "TRUNCATE cat"), ("DELETE", "DELETE FROM cat")):
        print(f"    {level:16} {name:9} -> count, min wave, max wave = {e1(level, sql)[1]}")

print("E2  error swallowed inside `with conn.transaction()`")
for variant in ("plain", "savepoint"):
    setup(); c = conn(True); raised = None
    try:
        with c.transaction():
            c.execute("UPDATE cat SET wave = 9 WHERE id = 1")
            try:
                if variant == "savepoint":
                    with c.transaction():
                        c.execute("SELECT 1/0")
                else:
                    c.execute("SELECT 1/0")
            except psycopg.errors.DivisionByZero:
                pass
            c.execute("SELECT 1") if variant == "savepoint" else None
    except Exception as e:
        raised = repr(e)
    wave = conn(True).execute("SELECT wave FROM cat WHERE id = 1").fetchone()[0]
    print(f"    {variant:9}: exception at block exit = {raised}; row 1 wave after = {wave}")
# plain, but with no further statement: does the block exit raise?
setup(); c = conn(True); raised=None
try:
    with c.transaction():
        c.execute("UPDATE cat SET wave = 9 WHERE id = 1")
        try: c.execute("SELECT 1/0")
        except psycopg.errors.DivisionByZero: pass
except Exception as e: raised = repr(e)
print(f"    plain, nothing after the error: exception = {raised}; wave = {conn(True).execute('SELECT wave FROM cat WHERE id=1').fetchone()[0]}")
# what does the server answer to COMMIT in an aborted transaction?
c = conn(True); c.execute("BEGIN"); 
try: c.execute("SELECT 1/0")
except Exception: pass
cur = c.execute("COMMIT"); print(f"    raw COMMIT in aborted txn -> server status message: {cur.statusmessage!r}")

print("E3  autocommit refresh: DELETE, then insert 50 rows in 5 batches 0.2 s apart; a reader polls count(*)")
setup(); seen = []
def refresher():
    w = conn(True); w.execute("DELETE FROM board")
    for b in range(5):
        time.sleep(0.2); w.execute("INSERT INTO board SELECT g, g FROM generate_series(%s::int,%s::int) g", (b*10+1, b*10+10))
t = threading.Thread(target=refresher); r = conn(True); t.start()
while t.is_alive():
    seen.append(r.execute("SELECT count(*) FROM board").fetchone()[0]); time.sleep(0.05)
seen.append(r.execute("SELECT count(*) FROM board").fetchone()[0]); t.join()
print(f"    distinct counts seen by the reader: {sorted(set(seen))}")
setup(); seen=[]
def refresher_tx():
    w = conn(True)
    with w.transaction():
        w.execute("DELETE FROM board")
        for b in range(5):
            time.sleep(0.2); w.execute("INSERT INTO board SELECT g, g FROM generate_series(%s::int,%s::int) g", (b*10+1, b*10+10))
t = threading.Thread(target=refresher_tx); t.start()
while t.is_alive():
    seen.append(r.execute("SELECT count(*) FROM board").fetchone()[0]); time.sleep(0.05)
t.join(); print(f"    same refresh in one transaction: distinct counts seen = {sorted(set(seen))}")

print("E4  two overlapping refreshes in autocommit (DELETE, sleep, INSERT all)")
setup(); errs = []
def run(delay):
    w = conn(True); time.sleep(delay)
    try:
        w.execute("DELETE FROM board"); time.sleep(0.3); w.execute("INSERT INTO board SELECT g, g FROM generate_series(1,50) g")
    except Exception as e: errs.append(type(e).__name__)
ts=[threading.Thread(target=run,args=(d,)) for d in (0,0.1)]; [x.start() for x in ts]; [x.join() for x in ts]
print(f"    errors: {errs}; rows after: {r.execute('SELECT count(*) FROM board').fetchone()[0]}")
a, b = conn(True), conn(True)
print(f"    guard: pg_try_advisory_lock(42) -> first {a.execute('SELECT pg_try_advisory_lock(42)').fetchone()[0]}, second {b.execute('SELECT pg_try_advisory_lock(42)').fetchone()[0]}")
