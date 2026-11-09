# Raw data for M03 Ch2 §4

PostgreSQL 18.6 (`postgres:18`, data checksums on, started with `-c wal_level=logical`, otherwise default settings) in
Docker on a laptop, psycopg 3.3.6, 2026-11-09. Every script takes the DSN of the `postgres` database as its first
argument. Timings on a laptop are noisy — another container was running benchmarks on the same machine — so
throughput numbers are medians of 3 runs, and the run-to-run spread is shown where it matters (Figure 1's bands).
Counts (lost updates, duplicates, missed events) are what the section relies on.

- `occ_trace.py`, `occ-trace-out.txt` — §1: two sessions racing the same `UPDATE … WHERE version = 0` at READ COMMITTED
  (0 rows after waiting) and REPEATABLE READ (40001) — Table 1; a 5 s edit held pessimistically vs. optimistically
  while a short request updates the same row — Table 2; which statements change `xmin` — Table 4.
- `occ_bench.py`, `occ-bench.csv` — §1, Table 3, Figure 1: 16 threads × 300 read-then-write increments, 2 ms think time,
  on 1 to 4,096 rows, four methods (no protection, pessimistic, optimistic with version and retry, one-statement
  `UPDATE`), 3 repetitions. *lost* = expected sum − actual sum; *retries* = optimistic `UPDATE`s that matched 0 rows.
- `idem_bench.py`, `idem-bench.csv`, `idem-race-out.txt` — §2: `bench` = 500 payments from 8 client threads through a
  40-thread "server", provider latency exponential (mean 80 ms, cap 600 ms), client timeout 150 ms, up to 5 attempts
  50 ms apart, four server designs (docstring), 3 repetitions — Table 5, Figure 2; `race` = two identical requests
  released through a barrier, 500 pairs per design — Table 6.
- `outbox_bench.py`, `outbox-crash.csv`, `outbox-hwm-out.txt`, `outbox-relay.csv`, `outbox-cdc-out.txt` — §3 and §4. The
  broker is a second database (`broker`) on its own connection. `crash`: 2,000 orders per design, 1% process crashes at
  the dangerous point, 2% of orders failing a deferred foreign key at `COMMIT`, relay crashes 5% per batch of 50, then a
  naive consumer and an inbox consumer over the delivered messages — Table 7, Figure 4. `hwm`: 8 writers keeping
  transactions open 0–20 ms after inserting an outbox row; a high-water-mark relay vs. a `sent_at IS NULL … SKIP LOCKED`
  relay, 3 repetitions — Table 8. `relay`: 20,000 pending events (5 per order), 1/2/4/8 relay threads × batches of
  1/10/100, 3 repetitions; *out_of_order* = events that reached the broker after a later event of the same order —
  Figure 6. `cdc`: a `test_decoding` slot's output for an order + outbox transaction, a `pg_logical_emit_message`, and an
  aborted transaction; WAL retained by the idle slot after 100,000 more inserts.

Figures 1, 2, 4 and 6 are drawn from these files by `../04-patterns-figures.py`.
