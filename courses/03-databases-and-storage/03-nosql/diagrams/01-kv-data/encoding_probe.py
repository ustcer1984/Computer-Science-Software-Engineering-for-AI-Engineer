"""§2 — the data structure under each Redis value type: OBJECT ENCODING for a small and a large value of each type.

Small = 3 elements of a few bytes; large = 1,000 elements, above the default compact-encoding thresholds, which are
printed at the end from CONFIG GET.

Usage:  python encoding_probe.py <redis-port>  > encoding-out.txt
"""
import sys, redis

r = redis.Redis(port=int(sys.argv[1]), decode_responses=True)
r.flushall()
r.set("s:int", 12345); r.set("s:short", "hello"); r.set("s:long", "x" * 100)
r.rpush("l:small", *"abc"); r.rpush("l:large", *range(1000))
r.hset("h:small", mapping={"a": 1, "b": 2, "c": 3}); r.hset("h:large", mapping={f"f{i}": i for i in range(1000)})
r.sadd("set:ints", 1, 2, 3); r.sadd("set:small", "a", "b", "c"); r.sadd("set:large", *[f"m{i}" for i in range(1000)])
r.zadd("z:small", {"a": 1, "b": 2, "c": 3}); r.zadd("z:large", {f"m{i}": i for i in range(1000)})
for k in ["s:int", "s:short", "s:long", "l:small", "l:large", "h:small", "h:large", "set:ints", "set:small",
          "set:large", "z:small", "z:large"]:
    print(f"{k:<10} type={r.type(k):<6} encoding={r.object('encoding', k)}")
for p in ("hash-max-listpack-entries", "hash-max-listpack-value", "set-max-intset-entries", "set-max-listpack-entries",
          "zset-max-listpack-entries", "list-max-listpack-size"):
    print(p, r.config_get(p)[p])
r.flushall()
