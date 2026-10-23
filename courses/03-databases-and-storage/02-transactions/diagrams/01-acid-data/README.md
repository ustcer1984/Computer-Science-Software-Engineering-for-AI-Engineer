# Raw data for M03 Ch2 §1

PostgreSQL 18.6 in Docker (`postgres:18`, default settings, data on a named volume) on a laptop with a consumer
NVMe SSD, 2026-10-24. `pg_test_fsync` on the same volume: `fdatasync` of one 8 kB write ≈ 1.6 ms (≈ 620 per second);
a non-synced 8 kB write ≈ 0.26 µs.

- `commit-cost.csv` — `pgbench -T 10`, three repetitions. `one.sql` = one `INSERT` per transaction; `hundred.sql` =
  `BEGIN`, 100 `INSERT`s, `COMMIT`. tps for `100 rows per commit` counts transactions, so rows per second = 100 × tps.
  The 128-client runs failed (above `max_connections = 100`) and are blank.
- `crash-loss.csv` — `pgbench` in a second container, 4 clients doing one-row inserts with per-transaction logging
  (`-l`); the server container was `docker kill -s KILL`ed after about 6 s. *acknowledged* = log lines (commits the
  client was told succeeded); *survived* = rows present after restart and crash recovery. A process kill, not a power
  cut: the host's page cache survived.
- `lost-update.csv` — 8 clients × 2,000 transactions incrementing one counter row; `--max-tries=1000` so pgbench retries
  serialization failures. Scripts are listed in the section's §5.
