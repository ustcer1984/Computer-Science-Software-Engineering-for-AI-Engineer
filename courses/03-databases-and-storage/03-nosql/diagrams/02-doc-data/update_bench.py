"""§2, Figure 2: what changing ONE small field costs as the document grows.

For document sizes 1 KB, 16 KB and 256 KB (text payload, compressible like real prose), 500 documents each:
  MongoDB      $inc counter                                   (journal bytes: wiredTiger "log bytes written")
  PostgreSQL   counter inside the jsonb: jsonb_set(...)        (WAL bytes: pg_wal_lsn_diff)
  PostgreSQL   counter in its own int column beside the jsonb
One client, 1,000 warm-up updates then 2,000 measured, random documents; 3 runs, medians reported.
Two costs per update: log bytes (journal / WAL, written at commit) and data-file bytes (pages written when a checkpoint
is forced right after the 2,000 updates: MongoDB `fsync`, PostgreSQL `CHECKPOINT`). With 500 documents each one is
updated about 4 times per checkpoint here; fewer updates per checkpoint means more data-file bytes per update.
"""
import json
import statistics
import random
import time

import psycopg
from pymongo import MongoClient

from common import MONGO_URI, PG_DSN, WORDS

SIZES = [1_024, 16_384, 262_144]
NDOCS, WARM, MEASURE = 500, 1_000, 2_000
rng = random.Random(3)


def payload(nbytes):
    words, n = [], 0
    while n < nbytes:
        w = rng.choice(WORDS) + f"{rng.randrange(1000)}"
        words.append(w)
        n += len(w) + 1
    return " ".join(words)


mc = MongoClient(MONGO_URI)
db = mc.bench
pg = psycopg.connect(PG_DSN, autocommit=True)
cur = pg.cursor()


def journal_bytes():
    return db.command("serverStatus")["wiredTiger"]["log"]["log bytes written"]


def data_bytes(meter):
    if meter == "mongo":
        return db.command("serverStatus")["wiredTiger"]["block-manager"]["bytes written"]
    cur.execute("SELECT coalesce(sum(write_bytes), 0) FROM pg_stat_io WHERE object = 'relation'")
    return int(cur.fetchone()[0])


def checkpoint(meter):
    if meter == "mongo":
        mc.admin.command("fsync")
    else:
        cur.execute("CHECKPOINT")


def wal_lsn():
    cur.execute("SELECT pg_current_wal_lsn()")
    return cur.fetchone()[0]


def wal_bytes_since(lsn):
    cur.execute("SELECT pg_wal_lsn_diff(pg_current_wal_lsn(), %s)", (lsn,))
    return int(cur.fetchone()[0])


print(f"{'size':>8} {'store':<34} {'updates/s':>10} {'log B/update':>13} {'data-file B/update':>19}")
rows = []
for size in SIZES:
    docs = [{"_id": i, "counter": 0, "body": payload(size)} for i in range(NDOCS)]
    db.blobs.drop()
    db.blobs.insert_many(docs)
    cur.execute("DROP TABLE IF EXISTS b_doc, b_split")
    # autovacuum off on both, so one variant's clean-up does not write pages during the other's measurement
    nav = "WITH (autovacuum_enabled = false, toast.autovacuum_enabled = false)"
    cur.execute(f"CREATE TABLE b_doc (id int PRIMARY KEY, doc jsonb) {nav}")
    cur.execute(f"CREATE TABLE b_split (id int PRIMARY KEY, counter int, doc jsonb) {nav}")
    with cur.copy("COPY b_doc FROM STDIN") as cp:
        for d in docs:
            cp.write_row((d["_id"], json.dumps(d)))
    with cur.copy("COPY b_split FROM STDIN") as cp:
        for d in docs:
            cp.write_row((d["_id"], 0, json.dumps({"_id": d["_id"], "body": d["body"]})))
    cur.execute("VACUUM ANALYZE b_doc")
    cur.execute("VACUUM ANALYZE b_split")
    cur.execute("CHECKPOINT")

    def mongo(k):
        db.blobs.update_one({"_id": rng.randrange(NDOCS)}, {"$inc": {"counter": 1}})

    def pg_doc(k):
        cur.execute("UPDATE b_doc SET doc = jsonb_set(doc, '{counter}', to_jsonb((doc->>'counter')::int + 1)) "
                    "WHERE id = %s", (rng.randrange(NDOCS),))

    def pg_split(k):
        cur.execute("UPDATE b_split SET counter = counter + 1 WHERE id = %s", (rng.randrange(NDOCS),))

    for name, fn, meter in (("MongoDB $inc", mongo, "mongo"),
                            ("PostgreSQL jsonb_set inside doc", pg_doc, "pg"),
                            ("PostgreSQL counter in own column", pg_split, "pg")):
        runs = []
        for run in range(3):
            for k in range(WARM):
                fn(k)
            checkpoint(meter)
            start = journal_bytes() if meter == "mongo" else wal_lsn()
            d0 = data_bytes(meter)
            t = time.perf_counter()
            for k in range(MEASURE):
                fn(k)
            el = time.perf_counter() - t
            used = (journal_bytes() - start) if meter == "mongo" else wal_bytes_since(start)
            checkpoint(meter)
            runs.append((MEASURE / el, used / MEASURE, (data_bytes(meter) - d0) / MEASURE))
        rate, logb, datab = (statistics.median(r[i] for r in runs) for i in range(3))
        rows.append((size, name, rate, logb, datab))
        print(f"{size:>8} {name:<34} {rate:>10,.0f} {logb:>13,.0f} {datab:>19,.0f}")

with open("update-bench.csv", "w") as f:
    f.write("doc_bytes,store,updates_per_s,log_bytes_per_update,data_file_bytes_per_update\n")
    for r in rows:
        f.write(f"{r[0]},{r[1]},{r[2]:.0f},{r[3]:.0f},{r[4]:.0f}\n")
