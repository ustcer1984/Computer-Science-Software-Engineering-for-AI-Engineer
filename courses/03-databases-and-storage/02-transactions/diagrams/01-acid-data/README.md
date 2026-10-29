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

Added 2026-10-29 for the §11 Applied answer (same image, PostgreSQL 18.6, container data on the overlay filesystem
rather than a named volume; the `rr` script of `lost-update.csv` — `BEGIN ISOLATION LEVEL REPEATABLE READ`, read,
write `:cur + 1`, `COMMIT`):

- `rr-max-tries.csv` — 8 clients × 2,000 transactions with `--max-tries` = 1, 2, 3, 5, 10 and 1000, three
  repetitions each. *final* = counter value; *failed*, *transactions_retried* and *total_retries* are pgbench's
  `number of failed transactions`, `number of transactions retried` and `total number of retries` lines. In every
  run final + failed = 16,000.
- `rr-retry-distribution.csv` — one further `--max-tries=1000` run with per-transaction logging (`-l`): how many of
  the 16,000 increments needed each number of retries (the log's last column). Final value 16,000, 0 failed,
  2,206 transactions retried, 100,410 retries in total; median 0, 90th percentile 8, 99th percentile 140,
  maximum 938 (one increment that took 1.77 s).
