"""§3 — acknowledged writes lost when the Redis process is killed (SIGKILL), by persistence setting.

For each setting a fresh redis:8 container is started. 8 client threads each write w:<thread>:<i> for i = 1, 2, 3, …
(one SET at a time, each waiting for its reply) and record the highest i acknowledged. After 6 s the container's
process is killed with `docker kill -s KILL` while the writers are running, then the container is started again and
reloads from whatever is on disk. lost = acknowledged − present.

Also reported: write throughput before the kill (acknowledged SETs per second, 8 clients), so the cost of each
setting is visible next to what it protects.

This kills the PROCESS, not the machine: the host kernel and its page cache survive, so data that Redis had passed to
write() but not fsync()ed still reaches disk. A power cut or kernel crash is not reproduced here (see README).

Settings:
  none            --save "" --appendonly no                   (a pure cache)
  rdb-default     the image's defaults: snapshots only, `save 3600 1 300 100 60 10000`
  aof-no          --appendonly yes --appendfsync no           (write() each event-loop pass, the OS flushes when it likes)
  aof-everysec    --appendonly yes --appendfsync everysec     (the default once AOF is on)
  aof-always      --appendonly yes --appendfsync always       (fsync before replying)

Usage:  python durability_bench.py  > durability-out.txt      (needs docker; uses host port 56390)
"""
import subprocess, threading, time, sys
import redis

PORT = 56390
SETTINGS = {
    "none":         ["--save", "", "--appendonly", "no"],
    "rdb-default":  [],
    "aof-no":       ["--appendonly", "yes", "--appendfsync", "no"],
    "aof-everysec": ["--appendonly", "yes", "--appendfsync", "everysec"],
    "aof-always":   ["--appendonly", "yes", "--appendfsync", "always"],
}


def sh(*a):
    return subprocess.run(a, capture_output=True, text=True)


def wait_up():
    for _ in range(200):
        try:
            r = redis.Redis(port=PORT); r.ping()
            while r.info("persistence").get("loading"):
                time.sleep(0.05)
            return r
        except Exception:
            time.sleep(0.05)
    raise RuntimeError("redis did not come back")


def writer(t, acked, stop):
    c = redis.Redis(port=PORT, socket_timeout=2)
    i = 0
    try:
        while not stop.is_set():
            c.set(f"w:{t}:{i + 1}", "x" * 100)
            i += 1; acked[t] = i
    except Exception:
        pass


print("setting,rep,acked,present,lost,extra,writes_per_s", flush=True)
for name, args in SETTINGS.items():
    for rep in range(3):
        sh("docker", "rm", "-f", "kv-dur")
        sh("docker", "run", "-d", "--name", "kv-dur", "-p", f"{PORT}:6379", "redis:8", "redis-server", *args)
        wait_up()
        acked, stop = [0] * 8, threading.Event()
        ths = [threading.Thread(target=writer, args=(t, acked, stop)) for t in range(8)]
        t0 = time.perf_counter()
        for th in ths: th.start()
        time.sleep(6)
        snap = sum(acked); el = time.perf_counter() - t0
        sh("docker", "kill", "-s", "KILL", "kv-dur")
        stop.set()
        for th in ths: th.join()
        sh("docker", "start", "kv-dur")
        r = wait_up()
        a = p = lost = extra = 0
        for t in range(8):
            # keys are written in order per thread, so count the contiguous prefix that survived
            pres = sum(1 for _ in r.scan_iter(match=f"w:{t}:*", count=10000))
            a += acked[t]; p += pres
            lost += max(0, acked[t] - pres); extra += max(0, pres - acked[t])
        print(f"{name},{rep},{a},{p},{lost},{extra},{snap/el:.0f}", flush=True)
sh("docker", "rm", "-f", "kv-dur")
