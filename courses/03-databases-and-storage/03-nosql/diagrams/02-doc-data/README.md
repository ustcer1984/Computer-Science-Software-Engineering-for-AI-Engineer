# Raw data for M03 Ch3 §2

MongoDB 8.2.12 (`mongo:8.2`, started as a single-node replica set `rs0` so that multi-document transactions work,
`--wiredTigerCacheSizeGB 1`) and PostgreSQL 18.6 (`postgres:18`, `shared_buffers=1GB`, `max_wal_size=8GB`) in Docker on
one laptop (22 cores), 2026-11-19. Python clients: pymongo 4.20.0, psycopg 3.3.9. Both servers had the same 1 GB cache
so neither got the whole machine's memory. Defaults otherwise, including the ones that matter here: MongoDB write
concern `majority` (journaled before acknowledging) and PostgreSQL `synchronous_commit = on` (WAL flushed before
acknowledging).

**How to read the timings.** Laptop timings are noisy; latencies are p50s over many calls, and the section relies on
plans, counts and bytes more than on milliseconds. Two caveats apply throughout:

- **The fixed cost per call differs.** An empty round trip from Python is 84.5 µs to MongoDB (`ping`) and 38.1 µs to
  PostgreSQL (`SELECT 1`) (`roundtrip-out.txt`). For one-row reads most of the gap between the two is that, not the
  storage engine.
- **PostgreSQL scans in parallel; MongoDB scans on one thread per query.** A sequential scan in PostgreSQL used a
  `Gather` over worker processes; MongoDB's `COLLSCAN` runs in the one thread serving the query. Scan timings therefore
  partly measure that difference.

Commit-bound rates (updates/s, transfers/s) mostly measure the laptop disk's flush latency and varied up to 5× between
runs; the section uses the byte counts and retry counts from those runs, not the rates, except where stated.

- `common.py` — connection strings and the deterministic catalogue generator (500,000 items, about 640 bytes of JSON
  each: name, brand, price, a `tags` array, a nested `attrs` object, a 40-word description).
- `load_footprint.py`, `footprint-out.txt` — §2 Table 2 and §3 Table 4: loads the catalogue into MongoDB and three
  PostgreSQL tables (`jsonb`, `json`, plain columns), then storage per item before secondary indexes and the size of
  every index after.
- `update_bench.py`, `update-bench.csv`, `update-out.txt` — §2 Figure 2: change one counter in 500 documents of 1 KB,
  16 KB and 256 KB; journal / WAL bytes per update and data-file bytes written at a forced checkpoint (MongoDB `fsync`,
  PostgreSQL `CHECKPOINT`; `pg_stat_io.write_bytes`, WiredTiger `block-manager.bytes written`). Autovacuum is disabled
  on the two PostgreSQL tables so one variant's clean-up does not write pages during the other's measurement; a first
  run without that showed 65 KB per update for the split-column variant that was really autovacuum on the other table.
- `query_bench.py`, `query-out.txt` — §3 Table 5 and Figure 3: five questions, each store's chosen plan and p50. The
  "float param (trap)" row is the same query as the expression-index row with Python floats passed uncast: `numeric`
  compared with `float8` is evaluated as `float8`, so the index on the `numeric` expression is not used.
- `roundtrip.py`, `roundtrip-out.txt` — the empty round trip above.
- `embed_bench.py`, `embed-bench.csv`, `embed-out.txt` — §4 Table 6: 50,000 orders × 10 items in four layouts, two
  questions, median of 3 runs of the p50.
- `schema_drift.py`, `drift-out.txt` — §5 Table 8: 10,000 products of which 100 store price as a string, 50 omit it
  and 50 spell it `Price`; the same question in both stores, then schema enforcement in both.
- `txn_bench.py`, `txn-out.txt` — §6 Table 9: 8 threads × 300 transfers among 10 accounts; MongoDB multi-document
  transactions (`with_transaction`), MongoDB one document holding all balances, PostgreSQL row-locking transactions;
  3 runs.

Figures 2 and 3 are drawn from these files by `../02-doc-figures.py`.
