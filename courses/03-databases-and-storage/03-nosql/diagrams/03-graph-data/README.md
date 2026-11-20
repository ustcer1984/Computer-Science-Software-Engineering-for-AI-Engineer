# Raw data for M03 Ch3 §3

Neo4j 2026.10.2 Community (`neo4j:community`, page cache 1 GB, heap 1 GB, store format `record-aligned-1.1`, no
authentication) and PostgreSQL 18.6 (`postgres:18`, `shared_buffers=1GB`, `max_wal_size=8GB`) in Docker on one laptop
(22 cores), 2026-11-20. Python clients: neo4j 6.4.1, psycopg 3.3.9, numpy, matplotlib 3.11.2. Both servers had a 1 GB
cache. The Neo4j store (514 MB) fits its page cache; PostgreSQL's 1,085 MiB slightly exceeds shared buffers but stayed
in the operating system's file cache, so all timings are warm.

**How to read the timings.** Laptop timings are noisy; latencies are p50s over many calls, and the section relies on
work counters (db hits, buffers, rows) and the shape of the curves more than on single milliseconds.

- **The fixed cost per call differs.** An empty query from Python took 0.34 ms in Neo4j (`RETURN 1` in a reused
  session, auto-commit) and 0.041 ms in PostgreSQL (`SELECT 1`) (`reach-out.txt`). The driver's `execute_query` helper
  costs more (about 0.6 ms) because it runs a managed transaction per call; the benchmarks use a session.
- **PostgreSQL scans in parallel; a Cypher query runs on one thread.** This matters for the whole-graph questions
  (`shape-out.txt` part C), not for traversals.

Files:

- `common.py`, `graph-out.txt` — the deterministic graph (1,000,000 users, 9,973,434 follows; degree statistics) and
  the CSV writer. Run `GRAPH_DATA_DIR=/tmp/graph-csv python common.py`. Neo4j is loaded with
  `neo4j-admin database import full neo4j --id-type=integer --nodes=User=users.csv --relationships=FOLLOWS=follows.csv`
  into an empty volume (§10 of the section has the exact commands). **`--id-type=integer` matters:** without it the
  `id` property is stored as a string, every `{id: 12345}` lookup with an integer parameter matches nothing, and the
  first run returned 0 for every query.
- `load_footprint.py`, `footprint-out.txt`, `neo4j-store-out.txt` — §2 Table 2: PostgreSQL `COPY`, the two edge
  indexes, sizes; Neo4j's lookup index on `:User(id)` and its store file sizes. Neo4j store files are allocated in
  chunks, so the relationship store's 402.7 MB is about 40 bytes per edge as allocated.
- `pg_functions.sql` — PL/pgSQL `bfs_reach`, `bfs_path_len` (one direction) and `bibfs_path_len` (both directions).
  Each expansion step is written as a `MATERIALIZED` CTE followed by the visited filter. **The first version wrote it
  as one join with `NOT EXISTS`**; at depth 7 the planner estimated the anti-join at 1 row and chose a nested loop
  that rescanned the 288,987-row frontier per row. A `bfs_path_len` call in that version was still running after 49
  minutes when it was terminated; `ANALYZE` on the temporary tables did not change the estimate. With the rewrite, 7
  hops take 4.5 s and 8 hops 7.4 s (`bfs_reach(12345, k)`, measured by hand).
- `reach_bench.py`, `reach-bench.csv`, `reach-out.txt` — §3 Figure 2 and Table 3: k-hop reach for 20 random users,
  k = 1..6, six methods, all checked to return identical counts; then Neo4j `PROFILE` and PostgreSQL
  `EXPLAIN (ANALYZE, BUFFERS)` for one user at 3 and 5 hops. The Cypher query needs `WHERE b <> a`: without it, a cycle
  back to the start user makes Neo4j count the start, and the first run disagreed with PostgreSQL by 1 for one user at
  5 hops. Path counts differ by a few between Neo4j (trails: no relationship repeated) and the `UNION ALL` CTE
  (walks).
- `path_bench.py`, `path-out.txt` — §4 Table 4: shortest path for 30 random pairs (all connected, lengths 5–8), four
  methods, all checked to agree on every length. The recursive CTE was timed on 5 pairs with the depth limit set to
  the known answer.
- `shape_bench.py`, `shape-out.txt` — §5 Table 5 and §6 Table 6: co-followers for users who follow only small accounts
  against users who follow the most-followed account; reach ignoring direction (single runs, so the Neo4j times there
  include query compilation); three whole-graph questions.

Figure 2 is drawn from `reach-bench.csv` by `../03-graph-figures.py`.
