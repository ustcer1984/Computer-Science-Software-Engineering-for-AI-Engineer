# Raw data for M03 Ch2 §2

PostgreSQL 18.6 (`postgres:18`) and MySQL 8.4.13 (`mysql:8.4`, InnoDB) in Docker, default settings, on a laptop,
2026-10-29.

- `schedules.py` — the harness: runs each schedule of the section's Table 1 (plus the fixes of §5) at every isolation
  level, one connection and one thread per session; a statement that has not returned after 1 s is logged as blocked
  and the schedule moves on. Needs `pip install 'psycopg[binary]' pymysql`; usage in its docstring.
- `results-pg.txt`, `results-my.txt` — the full traces: every statement, its result or error, and the final table.
  Figure 1 is transcribed from these.
- `outcomes-pg.csv`, `outcomes-my.csv` — one line per schedule and level: final state, errors, number of blocked steps.
- `counter_mysql.py`, `counter-mysql.csv` — Ch2 §1's counter on InnoDB (Table 4): 8 client threads × 2,000
  increments of one row, three repetitions per method. The SERIALIZABLE version retries deadlocks (`1213`) and
  lock-wait timeouts (`1205`), up to 1,000 times per increment.
- `ssi_bench.sh`, `ssi-bench.csv` — the cost runs of §4 (Figure 3, Table 2), run inside the PostgreSQL container with
  `pgbench -c8 -j8 -T 10 --max-tries=1`, three repetitions, `synchronous_commit = off` so that the drive's flush time
  does not dominate. *committed* and *failed* are pgbench's counts; *failed* splits into *serialization_failures*
  (`40001`) and *deadlocks* (`40P01`). The transfer table has a primary key on `id`; the roster table is run with and
  without a unique index on `(shift, doc)`.
