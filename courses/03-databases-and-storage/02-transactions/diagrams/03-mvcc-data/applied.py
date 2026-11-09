#!/usr/bin/env python3
"""M03 Ch2 §3 §12 — two questions about hint bits, measured.

  commit   why hint bits are not set at commit: COMMIT time (median of 5) against the number of rows the transaction wrote,
           and how much of the table is still in shared_buffers when COMMIT runs (pg_buffercache)
  who      who sets the hint bits first: after a load and a checkpoint, run one "setter" (a SELECT, VACUUM,
           autovacuum, CREATE INDEX, or nothing because the rows were loaded with COPY … FREEZE), then a full
           scan, and count the pages and WAL each step dirtied / wrote

Usage:  python applied.py <dsn> commit|who
"""
import io
import sys
import time

import psycopg

DSN, WHAT = sys.argv[1], sys.argv[2]
m = psycopg.connect(DSN, autocommit=True)
m.execute("CREATE EXTENSION IF NOT EXISTS pageinspect")
m.execute("CREATE EXTENSION IF NOT EXISTS pg_buffercache")


def lsn():
    return m.execute("SELECT pg_current_wal_insert_lsn()").fetchone()[0]


def wal_since(l0):
    return int(m.execute(f"SELECT pg_current_wal_insert_lsn() - '{l0}'::pg_lsn").fetchone()[0])


def scan(table):
    """One full scan; returns (pages read, pages dirtied, WAL bytes, ms)."""
    l0 = lsn()
    plan = [r[0] for r in m.execute(f"EXPLAIN (ANALYZE, BUFFERS, TIMING OFF) SELECT count(*) FROM {table}")]
    wal = wal_since(l0)
    b = [p for p in plan if "Buffers:" in p][0]
    hit = int(b.split("hit=")[1].split()[0]) if "hit=" in b else 0
    read = int(b.split("read=")[1].split()[0]) if "read=" in b else 0
    dirt = int(b.split("dirtied=")[1].split()[0]) if "dirtied=" in b else 0
    ms = float([p for p in plan if "Execution Time" in p][0].split(":")[1].split()[0])
    return hit + read, dirt, wal, ms


def bits(table, n=3):
    """Infomask flags of the first n rows of page 0."""
    out = []
    for (flags,) in m.execute(
            f"SELECT (heap_tuple_infomask_flags(t_infomask, t_infomask2)).raw_flags "
            f"FROM heap_page_items(get_raw_page('{table}', 0)) LIMIT {n}"):
        out.append(",".join(f.replace("HEAP_", "") for f in flags if "XMIN" in f or "XMAX_INVALID" in f) or "-")
    return out


if WHAT == "commit":
    print("shared_buffers =", m.execute("SHOW shared_buffers").fetchone()[0],
          "| data_checksums =", m.execute("SHOW data_checksums").fetchone()[0])
    print(f"{'rows':>10} {'insert_s':>9} {'commit_ms':>9} {'table_MB':>9} {'pages':>8} {'in_buffers_at_commit':>21} "
          f"  row-1 flags after COMMIT")
    import statistics
    for n in (1, 10_000, 100_000, 1_000_000, 5_000_000):
      commits = []
      for rep in range(5):
          m.execute("DROP TABLE IF EXISTS c; CREATE TABLE c (id int, v int, pad text) WITH (autovacuum_enabled = off)")
          m.execute("CHECKPOINT")
          s = psycopg.connect(DSN)            # one explicit transaction
          t0 = time.perf_counter()
          s.execute(f"INSERT INTO c SELECT g, g, 'x' FROM generate_series(1, {n}) g")
          t1 = time.perf_counter()
          pages = m.execute("SELECT pg_relation_size('c') / 8192").fetchone()[0]
          inbuf = m.execute("""SELECT count(*) FROM pg_buffercache
                               WHERE relfilenode = pg_relation_filenode('c') AND relforknumber = 0""").fetchone()[0]
          t2 = time.perf_counter()
          s.commit()
          t3 = time.perf_counter()
          s.close()
          commits.append((t3 - t2) * 1000)
      hinted = bits("c", 1)[0]
      mb = pages * 8192 / 1e6
      print(f"{n:>10,} {t1 - t0:>9.2f} {statistics.median(commits):>9.2f} {mb:>9.1f} {pages:>8,} "
            f"{inbuf:>8,} ({100 * inbuf / max(pages, 1):5.1f}%)        {hinted}")
    m.execute("DROP TABLE c")

elif WHAT == "who":
    N = 1_000_000
    print(f"{N:,} rows per table; data_checksums =", m.execute("SHOW data_checksums").fetchone()[0])

    def load(table, freeze=False):
        m.execute(f"DROP TABLE IF EXISTS {table}")
        if freeze:
            buf = io.StringIO("".join(f"{i}\t{i}\n" for i in range(1, N + 1)))
            with m.transaction():
                m.execute(f"CREATE TABLE {table} (id int, v int) WITH (autovacuum_enabled = off)")
                with m.cursor().copy(f"COPY {table} FROM STDIN WITH (FREEZE)") as cp:
                    cp.write(buf.getvalue())
        else:
            m.execute(f"CREATE TABLE {table} (id int, v int) WITH (autovacuum_enabled = off)")
            m.execute(f"INSERT INTO {table} SELECT g, g FROM generate_series(1, {N}) g")
        m.execute("CHECKPOINT")

    def run(label, table, setter):
        before = bits(table)[0]
        l0 = lsn(); t0 = time.perf_counter()
        setter()
        setter_wal, setter_s = wal_since(l0), time.perf_counter() - t0
        after = bits(table)[0]
        pages, dirt, wal, ms = scan(table)
        print(f"  {label:<34} bits before: {before:<28} after setter: {after:<28} "
              f"setter WAL {setter_wal / 1e6:6.1f} MB {setter_s:6.2f} s | then SELECT: dirtied {dirt:>5,}/{pages:,} "
              f"WAL {wal / 1e6:5.1f} MB {ms:6.1f} ms")

    load("w1"); run("nothing (first SELECT pays)", "w1", lambda: None)
    load("w2"); run("SELECT count(*)", "w2", lambda: scan("w2"))
    load("w3"); run("VACUUM", "w3", lambda: m.execute("VACUUM w3"))
    load("w4"); run("CREATE INDEX", "w4", lambda: m.execute("CREATE INDEX ON w4 (id)"))

    def autovac():
        m.execute("ALTER TABLE w5 SET (autovacuum_enabled = on, autovacuum_vacuum_insert_threshold = 1000)")
        t0 = time.time()
        while time.time() - t0 < 180:
            if m.execute("SELECT autovacuum_count FROM pg_stat_user_tables WHERE relname = 'w5'").fetchone()[0]:
                break
            time.sleep(0.5)
        m.execute("ALTER TABLE w5 SET (autovacuum_enabled = off)")
        print("    (autovacuum ran after %.0f s)" % (time.time() - t0))
    load("w5"); run("autovacuum (insert threshold)", "w5", autovac)
    load("w6", freeze=True); run("nothing — loaded with COPY FREEZE", "w6", lambda: None)
    for t in ("w1", "w2", "w3", "w4", "w5", "w6"):
        m.execute(f"DROP TABLE {t}")
