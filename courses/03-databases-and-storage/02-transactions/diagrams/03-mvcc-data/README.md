# Raw data for M03 Ch2 §3

PostgreSQL 18.6 (`postgres:18`, data checksums on, otherwise default settings) in Docker on a laptop, psycopg 3.3.6,
PgBouncer 1.26.1 (`edoburu/pgbouncer`), 2026-11-02. Every script takes the DSN as its first argument.

- `mvcc_trace.py`, `mvcc-trace-out.txt` — §1–§3: row headers read with `pageinspect` after an insert, an update and a
  rollback (hint bits, `xmin`/`xmax`/`ctid`, `pg_xact_status`); a snapshot with in-progress transactions and
  `pg_visible_in_snapshot`; READ COMMITTED vs REPEATABLE READ snapshots; lazy xid assignment; the bits each row-lock
  mode writes and a MultiXact (`pgrowlocks`); WAL written by `FOR SHARE` / `FOR UPDATE` over 100,000 rows; the row-lock
  conflict table (Table 3); foreign-key inserts against each parent lock (Table 5).
- `observe.py`, `observe-hint-out.txt`, `observe-chain-out.txt` — `hint`: two full scans after a 1,000,000-row load and
  a checkpoint, pages dirtied and WAL written (Table 1); `chain`: an idle-in-transaction holder, a row-lock waiter and an
  `ALTER TABLE` behind them, read from `pg_stat_activity` / `pg_locks`, with the `log_lock_waits` server log (§8).
- `table_locks.py` — `matrix`: the 8 × 8 table-lock conflict matrix with `LOCK TABLE … NOWAIT`
  (`table-lock-matrix.csv`, `table-lock-matrix-out.txt`, Figure 2); `stmts`: the table lock each statement takes, read
  from `pg_locks` (in a transaction where possible, otherwise polled every 2 ms while the statement runs on a
  2,000,000-row table; `table-lock-statements-out.txt`, Table 6); `pileup`: 8 clients each running a point `SELECT`
  every 20 ms for 12 s, a report holding `ACCESS SHARE` from t = 1 s to t = 8 s, and an `ALTER TABLE … ADD COLUMN` at
  t = 2 s with no timeout or with `lock_timeout = 200ms` retried every second (`pileup.csv` = every query's start and
  latency; `pileup-waiting.csv` = ungranted locks sampled every 50 ms; `pileup-out.txt`; Figure 4).
- `queue_bench.py`, `queue-bench.csv` — §5: 1,000 jobs, 1–32 worker threads with one connection each, 5 ms of
  `time.sleep` per job, six claim methods (described in the docstring), three repetitions. *executions* counts every
  run of the work; *duplicates* = executions − distinct jobs; *spurious_empty* = times a worker got no job while pending
  jobs remained (for the conditional `UPDATE` these are failed claims). Table 7, Figure 5.
- `deadlock_trace.py`, `deadlock-trace-out.txt` — §6: two sessions locking two rows in opposite orders, at
  `deadlock_timeout` 1 s and 200 ms; which one is the victim and when.
- `deadlock_bench.sh`, `deadlock-bench.csv` — §6, Table 8: pgbench transfers between random account pairs inside the
  container, `-c 8 -j 8 -T 10 --max-tries=1`, `synchronous_commit = off`, 10 and 100 accounts, unordered vs ordered
  locking, `deadlock_timeout` 1 s and 100 ms, three repetitions; the money total is checked after each run.
- `advisory.py`, `advisory-out.txt`, `pgbouncer.ini` — §7: session vs transaction scope, stacking, blocking, key
  spaces, the lock-table limit (binary search with `pg_advisory_xact_lock` over `generate_series`), `hashtext` vs
  `hashtextextended` collisions among 200,000 names, a simulated warm Lambda container that leaks a session lock, and the
  X/Y/Z sequence through PgBouncer in transaction mode (run with
  `docker run -d --network host -v $PWD/pgbouncer.ini:/etc/pgbouncer/pgbouncer.ini …`, plus a `userlist.txt`).

- `applied.py`, `applied-commit-out.txt`, `applied-who-out.txt` — §12 (2026-11-09, same setup): `commit`: one
  transaction inserts 1 … 5,000,000 rows, `COMMIT` timed (median of 5), the table's pages counted in shared buffers at
  that moment with `pg_buffercache`, and row 1's infomask read with `pageinspect` after commit (Table 12, Figure 7);
  `who`: a 1,000,000-row table loaded and checkpointed six times, one setter run first (nothing, a `SELECT`, `VACUUM`,
  `CREATE INDEX`, insert-triggered autovacuum, or a `COPY … FREEZE` load), then a full scan with pages dirtied and WAL
  written (Table 13).

Figures 2, 4 and 5 are drawn from these files by `../03-mvcc-figures.py`; Figure 7 by `../03-mvcc-applied-figures.py`.
