"""§4, Table 8: embed or reference? 50,000 orders x 10 line items, four layouts, two questions.

Layouts
  MongoDB embedded     orders_emb  {_id, customer, status, items: [{product, qty, price} x 10]}
  MongoDB referenced   orders_ref + order_items {order, product, qty, price}, index on order_items.order
  PostgreSQL tables    orders + order_items, index on order_items(order_id)       (Ch1's normalized design)
  PostgreSQL jsonb     orders_j (id, doc jsonb) with the items array inside the document
Questions
  A  one order with its items                  (the question the document was shaped for)
  B  total quantity sold of one product        (a question across all orders)
One client; p50 over the stated number of runs with random parameters; 3 runs of each, median of the p50s.
"""
import json
import random
import statistics

import psycopg
from pymongo import ASCENDING, MongoClient

from common import MONGO_URI, PG_DSN, timed

N_ORDERS, ITEMS, N_PRODUCTS = 50_000, 10, 2_000
rng = random.Random(11)
orders = [{"_id": o, "customer": rng.randrange(5_000), "status": rng.choice(["new", "paid", "shipped"]),
           "items": [{"product": rng.randrange(N_PRODUCTS), "qty": rng.randint(1, 5),
                      "price": round(rng.uniform(1, 200), 2)} for _ in range(ITEMS)]} for o in range(N_ORDERS)]

mc = MongoClient(MONGO_URI)
db = mc.bench
for c in ("orders_emb", "orders_ref", "order_items"):
    db[c].drop()
db.orders_emb.insert_many(orders)
db.orders_ref.insert_many([{k: v for k, v in o.items() if k != "items"} for o in orders])
db.order_items.insert_many([{"order": o["_id"], **it} for o in orders for it in o["items"]])
db.order_items.create_index([("order", ASCENDING)])
db.order_items.create_index([("product", ASCENDING)])
db.orders_emb.create_index([("items.product", ASCENDING)])

pg = psycopg.connect(PG_DSN, autocommit=True)
cur = pg.cursor()
cur.execute("DROP TABLE IF EXISTS order_items, orders, orders_j")
cur.execute("CREATE TABLE orders (id int PRIMARY KEY, customer int, status text)")
cur.execute("CREATE TABLE order_items (order_id int REFERENCES orders, product int, qty int, price numeric(8,2))")
cur.execute("CREATE TABLE orders_j (id int PRIMARY KEY, doc jsonb)")
with cur.copy("COPY orders FROM STDIN") as cp:
    for o in orders:
        cp.write_row((o["_id"], o["customer"], o["status"]))
with cur.copy("COPY order_items FROM STDIN") as cp:
    for o in orders:
        for it in o["items"]:
            cp.write_row((o["_id"], it["product"], it["qty"], it["price"]))
with cur.copy("COPY orders_j FROM STDIN") as cp:
    for o in orders:
        cp.write_row((o["_id"], json.dumps(o)))
cur.execute("CREATE INDEX ON order_items (order_id)")
cur.execute("CREATE INDEX ON order_items (product)")
cur.execute("CREATE INDEX ON orders_j USING gin ((doc->'items') jsonb_path_ops)")
for t in ("orders", "order_items", "orders_j"):
    cur.execute(f"VACUUM ANALYZE {t}")

O = lambda: rng.randrange(N_ORDERS)
P = lambda: rng.randrange(N_PRODUCTS)


def pg_q(sql, argf):
    def f(k):
        cur.execute(sql, argf())
        cur.fetchall()
    return f


cases = [
    ("A", "MongoDB embedded: find_one", lambda k: db.orders_emb.find_one({"_id": O()}), 2000),
    ("A", "MongoDB referenced: 2 queries", lambda k: (lambda o: (db.orders_ref.find_one({"_id": o}),
                                                                 list(db.order_items.find({"order": o}))))(O()), 2000),
    ("A", "MongoDB referenced: $lookup", lambda k: list(db.orders_ref.aggregate([
        {"$match": {"_id": O()}},
        {"$lookup": {"from": "order_items", "localField": "_id", "foreignField": "order", "as": "items"}}])), 2000),
    ("A", "PostgreSQL tables: JOIN", pg_q("SELECT o.*, i.product, i.qty, i.price FROM orders o "
                                          "JOIN order_items i ON i.order_id = o.id WHERE o.id = %s",
                                          lambda: (O(),)), 2000),
    ("A", "PostgreSQL jsonb: one row", pg_q("SELECT doc FROM orders_j WHERE id = %s", lambda: (O(),)), 2000),
    ("B", "MongoDB embedded: $unwind", lambda k: (lambda p: list(db.orders_emb.aggregate([
        {"$match": {"items.product": p}}, {"$unwind": "$items"}, {"$match": {"items.product": p}},
        {"$group": {"_id": None, "q": {"$sum": "$items.qty"}}}])))(P()), 300),
    ("B", "MongoDB referenced: $group", lambda k: list(db.order_items.aggregate([
        {"$match": {"product": P()}}, {"$group": {"_id": None, "q": {"$sum": "$qty"}}}])), 300),
    ("B", "PostgreSQL tables: SUM", pg_q("SELECT sum(qty) FROM order_items WHERE product = %s", lambda: (P(),)), 300),
    ("B", "PostgreSQL jsonb: unnest", pg_q(
        "SELECT sum((it->>'qty')::int) FROM orders_j, jsonb_array_elements(doc->'items') it "
        "WHERE doc->'items' @> jsonb_build_array(jsonb_build_object('product', %s::int)) "
        "AND (it->>'product')::int = %s", lambda: (lambda p: (p, p))(P())), 300),
]
print(f"{'Q':<2} {'layout':<32} {'p50 ms':>8} {'p99 ms':>8}")
with open("embed-bench.csv", "w") as f:
    f.write("question,layout,p50_ms,p99_ms\n")
    for q, name, fn, runs in cases:
        res = [timed(fn, runs) for _ in range(3)]
        p50 = statistics.median(r[0] for r in res) / 1000
        p99 = statistics.median(r[1] for r in res) / 1000
        print(f"{q:<2} {name:<32} {p50:>8.3f} {p99:>8.3f}")
        f.write(f"{q},{name},{p50:.3f},{p99:.3f}\n")

st_emb = db.command("collStats", "orders_emb")
st_ref = db.command("collStats", "orders_ref")
st_it = db.command("collStats", "order_items")
print(f"\nMongoDB embedded:   {st_emb['avgObjSize']:.0f} B per order document; storage "
      f"{(st_emb['storageSize'] + st_emb['totalIndexSize']) / 2**20:.1f} MB incl. indexes")
print(f"MongoDB referenced: {st_ref['avgObjSize']:.0f} B per order + {st_it['avgObjSize']:.0f} B per item; storage "
      f"{(st_ref['storageSize'] + st_ref['totalIndexSize'] + st_it['storageSize'] + st_it['totalIndexSize']) / 2**20:.1f}"
      f" MB incl. indexes")
cur.execute("SELECT pg_total_relation_size('orders') + pg_total_relation_size('order_items'), "
            "pg_total_relation_size('orders_j')")
a, b = cur.fetchone()
print(f"PostgreSQL tables:  {a / 2**20:.1f} MB incl. indexes;  PostgreSQL jsonb: {b / 2**20:.1f} MB incl. indexes")
