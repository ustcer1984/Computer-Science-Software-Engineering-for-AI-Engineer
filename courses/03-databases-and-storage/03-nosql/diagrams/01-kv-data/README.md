# Raw data for M03 Ch3 §1

Redis 8.10.3 (`redis:8`, default settings unless stated), DynamoDB Local 3.3.2 (`amazon/dynamodb-local`, `-inMemory`)
and PostgreSQL 18.6 (`postgres:18`) in Docker on one laptop (22 cores), 2026-11-19. Python clients: redis-py 8.1.0,
boto3 1.44.6, psycopg 3.3.6, run with `python -I`. Timings on a laptop are noisy, so rates are medians of 3 runs;
counts (lost writes, items read, capacity units) are what the section relies on.

**What DynamoDB Local can and cannot show.** It implements the DynamoDB API, condition expressions, transactions and
the capacity-unit accounting (`ReturnConsumedCapacity` returns the same units AWS would bill). It does **not** have
partitions, replication, throttling, adaptive capacity or real latency, so nothing about speed or hot partitions is
measured on it; hot partitions are simulated instead (`partition_sim.py`), and the per-partition limits are taken from
the AWS documentation (checked 2026-11-19).

- `lookup_bench.py`, `lookup-bench.csv` — §2, Figure 2(a): 100,000 keys / rows of 100-byte values; Redis `GET` vs
  PostgreSQL `SELECT v FROM kv WHERE k = %s` (primary key), one client one at a time (latency p50/p99), one client in
  batches of 100 (Redis pipeline / psycopg pipeline mode), and 1/4/16 client processes.
- `server-ceiling-out.txt` — §2, Figure 2(b): the servers' own ceilings with C clients run from separate containers
  sharing the server's network namespace: `redis-benchmark -t get -n 2000000 -c 50 -P 1|16 --threads 4` and `pgbench -S
  -M prepared -c 16|50 -j 8 -T 10` (scale 10). `server_cpu_s` = the server container's cgroup CPU time (user + system)
  during the run, so CPU per lookup = `server_cpu_s` / lookups.
- `footprint.py`, `footprint-out.txt` — §2, Table 3: Redis memory per key (1M keys, 100-byte values, with and without a TTL) vs
  PostgreSQL heap + primary-key index bytes per row for the same pairs.
- `encoding_probe.py`, `encoding-out.txt` — §2, Table 2: `OBJECT ENCODING` of a small and a large value of each type,
  and the default thresholds that switch a compact encoding to the general one.
- `capacity_probe.py`, `capacity-out.txt` — §4, Table 6: the capacity units DynamoDB Local reports for writes and reads
  of different sizes, a missing key, a scan, a 401 KB item, a transaction. One mismatch with AWS: Local reported 2.0
  write units for a 2-item transaction, where the AWS documentation says a transactional write costs 2 units per item
  (4 in total).
- `block_bench.py`, `block-bench-out.txt` — §2, Figure 3: a client `GET`s every 1 ms while another runs `KEYS *` over
  1M keys, a `SCAN … COUNT 1000` loop over the same keys, `DEL` of a 1M-field hash, or `UNLINK` of it.
- `durability_bench.py`, `durability-out.txt` — §3, Table 4: 8 writers, `docker kill -s KILL` after 6 s, restart, count
  acknowledged writes missing, for five persistence settings. Process kill only: the host kernel's page cache
  survives, so a power cut or kernel crash (where `appendfsync everysec` can lose up to about a second and `no` up to
  the kernel's write-back interval) is **not** reproduced. The writers are Python threads, so the throughput column is
  client-bound except for `aof-always`.
- `partition_sim.py`, `partition-sim.csv` — §4, Figure 5: 2,000,000 requests per workload hashed (MD5) onto 1–128
  partitions; busiest partition's share and the table write rate at which it reaches 1,000 write units/s.
- `access_bench.py`, `access-out.txt` — §5, Table 8: 10,000 orders (200 customers × 50), eight questions asked of a
  DynamoDB table keyed `CUST#…` / `ORDER#date#id` with one GSI (global secondary index) on status, and of PostgreSQL
  with `EXPLAIN (ANALYZE, BUFFERS)`.
- `counter_bench.py`, `counter-bench.csv` — §6, Table 9: 16 threads × 300 read-think(2 ms)-write increments of one
  counter: Redis GET/SET, WATCH/MULTI/EXEC, INCR; DynamoDB GetItem/PutItem, conditional PutItem on a version, UpdateItem
  ADD.
- `ttl_bench.py`, `ttl-bench.csv` — §7, Figure 6: 1,000,000 keys with a 10 s TTL and 100,000 without, never read;
  DBSIZE, `expired_keys` and memory every 100 ms, at `hz 10` and `hz 100`.
- `prices.py`, `prices-out.txt` — §8, Table 12: DynamoDB on-demand and ElastiCache node list prices for ap-southeast-1
  from the public AWS Price List API (offer files published 2026-11-11 and 2026-11-18, fetched 2026-11-19).

Figures 2, 3, 5 and 6 are drawn from these files by `../01-kv-figures.py`.
