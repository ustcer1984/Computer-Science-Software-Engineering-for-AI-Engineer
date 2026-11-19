"""§6, Table 10: a two-document transfer under contention. 10 accounts, 8 threads x 300 transfers between random pairs.

MongoDB   session.with_transaction(): two $inc updates in one multi-document transaction (single-node replica set).
          A conflicting write aborts the transaction at once (WriteConflict, labelled TransientTransactionError);
          with_transaction re-runs the callback. Retries = callback calls - 1.
MongoDB   one document holding all balances: both $inc in ONE update_one (single-document atomicity, no transaction).
PostgreSQL READ COMMITTED: two UPDATE ... SET balance = balance +/- x, rows locked in id order. A conflicting
          writer WAITS for the row lock instead of aborting (Ch2 §3).
After each run the total of all balances must still be 10 x 1,000.
"""
import random
import threading
import time

import psycopg
from pymongo import MongoClient

from common import MONGO_URI, PG_DSN

ACCOUNTS, THREADS, PER_THREAD = 10, 8, 300
mc = MongoClient(MONGO_URI)
db = mc.bench


def run(worker):
    calls = [0] * THREADS
    ths = [threading.Thread(target=worker, args=(t, calls)) for t in range(THREADS)]
    t0 = time.perf_counter()
    for th in ths:
        th.start()
    for th in ths:
        th.join()
    return time.perf_counter() - t0, sum(calls)


def pairs(seed):
    rng = random.Random(seed)
    for _ in range(PER_THREAD):
        a, b = rng.sample(range(ACCOUNTS), 2)
        yield a, b, rng.randint(1, 10)


# MongoDB multi-document transaction
db.acct.drop()
db.acct.insert_many([{"_id": i, "balance": 1000} for i in range(ACCOUNTS)])


def mongo_txn(t, calls):
    client = MongoClient(MONGO_URI)
    acct = client.bench.acct
    with client.start_session() as s:
        for a, b, x in pairs(t):
            def cb(session):
                calls[t] += 1
                acct.update_one({"_id": a}, {"$inc": {"balance": -x}}, session=session)
                acct.update_one({"_id": b}, {"$inc": {"balance": x}}, session=session)
            s.with_transaction(cb)


el, calls = run(mongo_txn)
total = sum(d["balance"] for d in db.acct.find())
n = THREADS * PER_THREAD
print(f"MongoDB multi-document transaction   {n / el:>7,.0f} transfers/s   retries per transfer "
      f"{(calls - n) / n:5.2f}   total balance {total}")

# MongoDB single document
db.acct1.drop()
db.acct1.insert_one({"_id": 0, **{f"b{i}": 1000 for i in range(ACCOUNTS)}})


def mongo_one(t, calls):
    acct = MongoClient(MONGO_URI).bench.acct1
    for a, b, x in pairs(t):
        calls[t] += 1
        acct.update_one({"_id": 0}, {"$inc": {f"b{a}": -x, f"b{b}": x}})


el, calls = run(mongo_one)
doc = db.acct1.find_one({"_id": 0})
total = sum(doc[f"b{i}"] for i in range(ACCOUNTS))
print(f"MongoDB one document, one update     {n / el:>7,.0f} transfers/s   retries per transfer "
      f"{(calls - n) / n:5.2f}   total balance {total}")

# PostgreSQL
pg = psycopg.connect(PG_DSN, autocommit=True)
pg.execute("DROP TABLE IF EXISTS acct")
pg.execute("CREATE TABLE acct (id int PRIMARY KEY, balance int)")
pg.execute("INSERT INTO acct SELECT g, 1000 FROM generate_series(0, %s) g", (ACCOUNTS - 1,))


def pg_txn(t, calls):
    with psycopg.connect(PG_DSN) as conn:
        for a, b, x in pairs(t):
            calls[t] += 1
            with conn.transaction():
                for acc, delta in sorted(((a, -x), (b, x))):      # lock in id order: no deadlock
                    conn.execute("UPDATE acct SET balance = balance + %s WHERE id = %s", (delta, acc))


el, calls = run(pg_txn)
total = pg.execute("SELECT sum(balance) FROM acct").fetchone()[0]
print(f"PostgreSQL transaction, row locks    {n / el:>7,.0f} transfers/s   retries per transfer "
      f"{(calls - n) / n:5.2f}   total balance {total}")
