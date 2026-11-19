"""§2 — one thread executes every command: what a slow command does to everybody else's GET.

A probe client sends GET every 1 ms for 3 s and records each latency. Halfway through, a second client runs one of:

  KEYS *            over 1,000,000 keys (returns every key name in one reply)
  SCAN loop         the same 1,000,000 names, 1,000 per call (COUNT 1000)
  DEL bighash       a hash with 1,000,000 fields, freed synchronously
  UNLINK bighash    the same hash, freed by a background thread (lazyfree)

Prints the probe's p50, max and the number of probes slower than 10 ms, plus how long the slow command took.
3 repetitions.

Usage:  python block_bench.py <redis-port>  > block-bench-out.txt
"""
import sys, time, threading, statistics
import redis

PORT = int(sys.argv[1])
r = redis.Redis(port=PORT)


def load_keys():
    r.flushall()
    p = r.pipeline(transaction=False)
    for i in range(1_000_000):
        p.set(f"k:{i}", "v")
        if i % 10000 == 9999:
            p.execute()
    p.execute()


def load_hash():
    r.delete("bighash")
    p = r.pipeline(transaction=False)
    for i in range(0, 1_000_000, 1000):
        p.hset("bighash", mapping={f"f{j}": "v" for j in range(i, i + 1000)})
    p.execute()


def probe(out, stop):
    c = redis.Redis(port=PORT)
    while not stop.is_set():
        t = time.perf_counter(); c.get("k:1"); out.append(time.perf_counter() - t)
        time.sleep(0.001)


def run(name, action):
    lat, stop = [], threading.Event()
    th = threading.Thread(target=probe, args=(lat, stop)); th.start()
    time.sleep(1.5)
    c = redis.Redis(port=PORT)
    t = time.perf_counter(); action(c); took = time.perf_counter() - t
    time.sleep(1.5); stop.set(); th.join()
    slow = sum(1 for x in lat if x > 0.010)
    print(f"{name:<16} command {took*1000:8.1f} ms | probe p50 {statistics.median(lat)*1e3:6.3f} ms "
          f"max {max(lat)*1e3:7.1f} ms  probes >10 ms: {slow}", flush=True)


def scan_all(c):
    n = 0
    for _ in c.scan_iter(count=1000):
        n += 1
    assert n >= 1_000_000


load_keys()
print(f"redis {r.info('server')['redis_version']}, dbsize {r.dbsize()}")
for rep in range(3):
    print(f"-- rep {rep}")
    run("KEYS *", lambda c: c.keys("*"))
    run("SCAN loop", scan_all)
    load_hash(); run("DEL bighash", lambda c: c.delete("bighash"))
    load_hash(); run("UNLINK bighash", lambda c: c.unlink("bighash"))
