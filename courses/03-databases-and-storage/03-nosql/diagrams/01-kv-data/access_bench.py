"""§5 — eight questions asked of a DynamoDB table designed for two of them, and of a PostgreSQL table.

Data: 200 customers × 50 orders = 10,000 orders over 2026, each about 300 bytes, deterministic (seed 7).

DynamoDB (DynamoDB Local 3.3.2, which reproduces the API and the capacity-unit accounting, not the latency):
  table orders   PK = "CUST#<customer>"   SK = "ORDER#<yyyy-mm-dd>#<order id>"
  GSI  by_status PK = status              SK = order_date        (added for question 4b only)
  every call with ReturnConsumedCapacity=TOTAL; "items read" = ScannedCount (what you pay for),
  "items returned" = Count. Pagination is followed to the end.

PostgreSQL 18.6: orders(customer_id, order_date, order_id, status, amount, payload), PRIMARY KEY (customer_id,
order_date, order_id), plus customers(customer_id, name, tier). EXPLAIN (ANALYZE, BUFFERS) for each question:
top plan node, rows returned, shared buffers touched.

Usage:  python access_bench.py <dynamodb-endpoint> <pg-dsn>  > access-out.txt
"""
import sys, random, datetime, json
import boto3, psycopg

EP, DSN = sys.argv[1], sys.argv[2]
d = boto3.client("dynamodb", endpoint_url=EP, region_name="ap-southeast-1",
                 aws_access_key_id="local", aws_secret_access_key="local")
rnd = random.Random(7)
STATUSES = ["DELIVERED"] * 17 + ["SHIPPED"] * 2 + ["OPEN"]
start = datetime.date(2026, 1, 1)
orders = []
for c in range(200):
    for k in range(50):
        day = start + datetime.timedelta(days=rnd.randrange(365))
        orders.append(dict(cust=f"c{c:03d}", date=day.isoformat(), oid=f"o{c:03d}{k:02d}",
                           status=rnd.choice(STATUSES), amount=rnd.randrange(5, 1000), payload="p" * 220))

# ---------- DynamoDB ----------
for t in ("orders",):
    try: d.delete_table(TableName=t)
    except d.exceptions.ResourceNotFoundException: pass
d.create_table(TableName="orders", BillingMode="PAY_PER_REQUEST",
               KeySchema=[{"AttributeName": "PK", "KeyType": "HASH"}, {"AttributeName": "SK", "KeyType": "RANGE"}],
               AttributeDefinitions=[{"AttributeName": a, "AttributeType": "S"} for a in ("PK", "SK", "status", "order_date")],
               GlobalSecondaryIndexes=[{"IndexName": "by_status",
                                        "KeySchema": [{"AttributeName": "status", "KeyType": "HASH"},
                                                      {"AttributeName": "order_date", "KeyType": "RANGE"}],
                                        "Projection": {"ProjectionType": "ALL"}}])
wcu = 0
for i in range(0, len(orders), 25):
    req = [{"PutRequest": {"Item": {"PK": {"S": f"CUST#{o['cust']}"}, "SK": {"S": f"ORDER#{o['date']}#{o['oid']}"},
                                    "order_date": {"S": o["date"]}, "status": {"S": o["status"]},
                                    "amount": {"N": str(o["amount"])}, "payload": {"S": o["payload"]}}}}
           for o in orders[i:i + 25]]
    r = d.batch_write_item(RequestItems={"orders": req}, ReturnConsumedCapacity="TOTAL")
    wcu += sum(x["CapacityUnits"] for x in r["ConsumedCapacity"])
print(f"loaded {len(orders)} items into DynamoDB; write capacity consumed {wcu:.0f} WCU (table + GSI)")


def ddb(op, **kw):
    """Run a Query/Scan to the end; return (calls, items read, items returned, RCU)."""
    calls = read = ret = 0; rcu = 0.0
    while True:
        r = getattr(d, op)(TableName="orders", ReturnConsumedCapacity="TOTAL", **kw)
        calls += 1; read += r["ScannedCount"]; ret += r["Count"]; rcu += r["ConsumedCapacity"]["CapacityUnits"]
        if "LastEvaluatedKey" not in r: return calls, read, ret, rcu
        kw["ExclusiveStartKey"] = r["LastEvaluatedKey"]


one = orders[1234]
res = {}
r = d.get_item(TableName="orders", Key={"PK": {"S": f"CUST#{one['cust']}"}, "SK": {"S": f"ORDER#{one['date']}#{one['oid']}"}},
               ReturnConsumedCapacity="TOTAL")
res["1"] = (1, 1, 1, r["ConsumedCapacity"]["CapacityUnits"])
res["2"] = ddb("query", KeyConditionExpression="PK = :p AND SK BETWEEN :a AND :b",
               ExpressionAttributeValues={":p": {"S": "CUST#c042"}, ":a": {"S": "ORDER#2026-06-01"}, ":b": {"S": "ORDER#2026-06-30~"}})
res["3"] = ddb("query", KeyConditionExpression="PK = :p", FilterExpression="amount > :m",
               ExpressionAttributeValues={":p": {"S": "CUST#c042"}, ":m": {"N": "900"}})
res["4a"] = ddb("scan", FilterExpression="#s = :s", ExpressionAttributeNames={"#s": "status"},
                ExpressionAttributeValues={":s": {"S": "OPEN"}})
res["4b"] = ddb("query", IndexName="by_status", KeyConditionExpression="#s = :s", ExpressionAttributeNames={"#s": "status"},
                ExpressionAttributeValues={":s": {"S": "OPEN"}})
res["5"] = ddb("scan")          # top 10 by amount: no index orders by amount, so read everything and sort in the client
# 6: orders of all "gold" customers in June: no join. Look the gold customers up in the app, then one Query each.
gold = [f"c{c:03d}" for c in range(0, 200, 10)]          # 20 customers; their ids live in a separate store
acc = [0, 0, 0, 0.0]
for c in gold:
    x = ddb("query", KeyConditionExpression="PK = :p AND SK BETWEEN :a AND :b",
            ExpressionAttributeValues={":p": {"S": f"CUST#{c}"}, ":a": {"S": "ORDER#2026-06-01"}, ":b": {"S": "ORDER#2026-06-30~"}})
    acc = [a + b for a, b in zip(acc, x)]
res["6"] = tuple(acc)
res["7"] = ddb("scan", FilterExpression="amount BETWEEN :a AND :b",
               ExpressionAttributeValues={":a": {"N": "500"}, ":b": {"N": "510"}})

# ---------- PostgreSQL ----------
with psycopg.connect(DSN, autocommit=True) as c:
    c.execute("DROP TABLE IF EXISTS orders, customers")
    c.execute("""CREATE TABLE customers (customer_id text PRIMARY KEY, name text, tier text);
                 CREATE TABLE orders (customer_id text, order_date date, order_id text, status text, amount int,
                                      payload text, PRIMARY KEY (customer_id, order_date, order_id))""")
    with c.cursor().copy("COPY customers FROM STDIN") as cp:
        for k in range(200):
            cp.write_row((f"c{k:03d}", f"name {k}", "gold" if k % 10 == 0 else "standard"))
    with c.cursor().copy("COPY orders FROM STDIN") as cp:
        for o in orders:
            cp.write_row((o["cust"], o["date"], o["oid"], o["status"], o["amount"], o["payload"]))
    c.execute("VACUUM ANALYZE orders"); c.execute("VACUUM ANALYZE customers")
    pgq = {
        "1": f"SELECT * FROM orders WHERE customer_id='{one['cust']}' AND order_date='{one['date']}' AND order_id='{one['oid']}'",
        "2": "SELECT * FROM orders WHERE customer_id='c042' AND order_date BETWEEN '2026-06-01' AND '2026-06-30'",
        "3": "SELECT * FROM orders WHERE customer_id='c042' AND amount > 900",
        "4a": "SELECT * FROM orders WHERE status='OPEN'",
        "5": "SELECT * FROM orders ORDER BY amount DESC LIMIT 10",
        "6": """SELECT o.* FROM orders o JOIN customers c USING (customer_id)
                WHERE c.tier='gold' AND o.order_date BETWEEN '2026-06-01' AND '2026-06-30'""",
        "7": "SELECT * FROM orders WHERE amount BETWEEN 500 AND 510",
    }
    pgres = {}
    for k, q in pgq.items():
        plan = c.execute("EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) " + q).fetchone()[0][0]
        top = plan["Plan"]
        def nodes(p):
            yield p
            for ch in p.get("Plans", []): yield from nodes(ch)
        types = " > ".join(dict.fromkeys(n["Node Type"] + (f" on {n['Relation Name']}" if "Relation Name" in n else "") for n in nodes(top)))
        pgres[k] = (top["Actual Rows"], top.get("Shared Hit Blocks", 0) + top.get("Shared Read Blocks", 0),
                    plan["Execution Time"], types)

QUESTIONS = {
    "1": "one order, by its full key",
    "2": "customer c042's orders in June",
    "3": "customer c042's orders over 900",
    "4a": "every OPEN order (no index on status)",
    "4b": "every OPEN order (GSI by_status)",
    "5": "the 10 largest orders",
    "6": "June orders of the 20 gold customers (a join)",
    "7": "orders with amount between 500 and 510",
}
print("\nquestion | DynamoDB requests | items read | items returned | RCU | PostgreSQL rows | PG buffers | PG ms | PG plan")
for k, label in QUESTIONS.items():
    calls, read, ret, rcu = res[k]
    pr = pgres.get(k)
    pgs = f"{pr[0]} | {pr[1]} | {pr[2]:.2f} | {pr[3]}" if pr else "(same SQL as 4a) | | |"
    print(f"{k} {label} | {calls} | {read} | {ret} | {rcu:.1f} | {pgs}")
