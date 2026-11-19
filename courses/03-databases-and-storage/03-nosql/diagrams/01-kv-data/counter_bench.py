"""§6 — Ch2 §4's lost-update test, on a key-value store: 16 threads × 300 increments of ONE counter.

Each thread reads the counter, "thinks" for 2 ms (as in Ch2 §4 Table 3), and writes it back, by one of these methods:

  Redis
    get-set        GET, think, SET value+1                                    (no protection)
    watch-multi    WATCH, GET, think, MULTI / SET / EXEC; retry if EXEC returns nil (optimistic)
    incr           INCR — the server adds 1; no read in the client             (one atomic command)
  DynamoDB (DynamoDB Local)
    get-put        GetItem, think, PutItem n+1                                 (no protection)
    conditional    GetItem, think, PutItem n+1, version+1 with ConditionExpression "version = :v"; retry on
                   ConditionalCheckFailedException                             (optimistic)
    add            UpdateItem "ADD n :one" — the server adds 1                 (one atomic command)

lost = 4,800 − final value; retries = failed conditional writes / failed EXECs per committed increment.
3 repetitions. DynamoDB Local runs on one machine; on AWS each call would take milliseconds, not microseconds, which
widens the read-to-write gap and makes conflicts MORE likely, not less.

Usage:  python counter_bench.py <redis-port> <dynamodb-endpoint>  > counter-bench.csv
"""
import sys, time, threading
import redis, boto3

RPORT, EP = int(sys.argv[1]), sys.argv[2]
THREADS, EACH, THINK = 16, 300, 0.002


def ddb():
    return boto3.client("dynamodb", endpoint_url=EP, region_name="ap-southeast-1",
                        aws_access_key_id="local", aws_secret_access_key="local")


D = ddb()
try: D.delete_table(TableName="counters")
except D.exceptions.ResourceNotFoundException: pass
D.create_table(TableName="counters", BillingMode="PAY_PER_REQUEST",
               KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
               AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}])
KEY = {"pk": {"S": "c"}}


def r_getset(c, stats):
    v = int(c.get("c")); time.sleep(THINK); c.set("c", v + 1)


def r_watch(c, stats):
    while True:
        with c.pipeline() as p:
            try:
                p.watch("c"); v = int(p.get("c")); time.sleep(THINK)
                p.multi(); p.set("c", v + 1); p.execute(); return
            except redis.WatchError:
                stats.append(1)


def r_incr(c, stats):
    c.incr("c")


def d_getput(c, stats):
    v = int(c.get_item(TableName="counters", Key=KEY, ConsistentRead=True)["Item"]["n"]["N"]); time.sleep(THINK)
    c.put_item(TableName="counters", Item={**KEY, "n": {"N": str(v + 1)}, "version": {"N": "0"}})


def d_cond(c, stats):
    while True:
        it = c.get_item(TableName="counters", Key=KEY, ConsistentRead=True)["Item"]
        n, ver = int(it["n"]["N"]), int(it["version"]["N"]); time.sleep(THINK)
        try:
            c.put_item(TableName="counters", Item={**KEY, "n": {"N": str(n + 1)}, "version": {"N": str(ver + 1)}},
                       ConditionExpression="version = :v", ExpressionAttributeValues={":v": {"N": str(ver)}})
            return
        except c.exceptions.ConditionalCheckFailedException:
            stats.append(1)


def d_add(c, stats):
    c.update_item(TableName="counters", Key=KEY, UpdateExpression="ADD n :one",
                  ExpressionAttributeValues={":one": {"N": "1"}})


METHODS = [("redis", "get-set", r_getset), ("redis", "watch-multi", r_watch), ("redis", "incr", r_incr),
           ("dynamodb", "get-put", d_getput), ("dynamodb", "conditional", d_cond), ("dynamodb", "add", d_add)]

print("store,method,rep,expected,final,lost,retries_per_update,seconds", flush=True)
for rep in range(3):
    for store, name, fn in METHODS:
        if store == "redis":
            redis.Redis(port=RPORT).set("c", 0)
            read = lambda: int(redis.Redis(port=RPORT).get("c"))
            mk = lambda: redis.Redis(port=RPORT)
        else:
            D.put_item(TableName="counters", Item={**KEY, "n": {"N": "0"}, "version": {"N": "0"}})
            read = lambda: int(D.get_item(TableName="counters", Key=KEY, ConsistentRead=True)["Item"]["n"]["N"])
            mk = ddb
        stats = []
        def run():
            c = mk()
            for _ in range(EACH):
                fn(c, stats)
        ths = [threading.Thread(target=run) for _ in range(THREADS)]
        t = time.perf_counter()
        for th in ths: th.start()
        for th in ths: th.join()
        s = time.perf_counter() - t
        final = read(); exp = THREADS * EACH
        print(f"{store},{name},{rep},{exp},{final},{exp - final},{len(stats) / exp:.2f},{s:.1f}", flush=True)
