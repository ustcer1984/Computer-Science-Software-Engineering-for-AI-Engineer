"""§3, Table 6: the same five questions asked of MongoDB and of PostgreSQL (jsonb and plain columns).

Run after load_footprint.py. One client, one query at a time; p50 of RUNS executions with random parameters.
Each line prints the plan the database chose (MongoDB winning plan stages; PostgreSQL top plan nodes).
"""
import json
import random

import psycopg
from pymongo import MongoClient

from common import BRANDS, COLORS, MATERIALS, MONGO_URI, PG_DSN, SIZES, TAGS, timed

rng = random.Random(7)
mc = MongoClient(MONGO_URI)
coll = mc.bench.products
pg = psycopg.connect(PG_DSN, autocommit=True)
cur = pg.cursor()


def mongo_plan(flt, count=False):
    ex = mc.bench.command("explain", {"count" if count else "find": "products", "query" if count else "filter": flt},
                          verbosity="executionStats")
    stages, node = [], ex["queryPlanner"]["winningPlan"]
    node = node.get("queryPlan", node)
    while node:
        stages.append(node["stage"] + (f"({node['indexName']})" if "indexName" in node else ""))
        node = node.get("inputStage") or (node.get("inputStages") or [None])[0]
    es = ex["executionStats"]
    return " <- ".join(stages), es["totalDocsExamined"], es["totalKeysExamined"]


def pg_plan(sql, args):
    cur.execute("EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) " + sql, args)
    plan = cur.fetchone()[0][0]["Plan"]
    nodes, n = [], plan
    while n:
        nodes.append(n["Node Type"] + (f"({n['Index Name']})" if "Index Name" in n else ""))
        n = (n.get("Plans") or [None])[0]
    return " <- ".join(nodes), plan["Shared Hit Blocks"] + plan.get("Shared Read Blocks", 0)


def run_pg(label, sql, argf, runs):
    p50, p99 = timed(lambda k: (cur.execute(sql, argf()), cur.fetchall()), runs)
    plan, bufs = pg_plan(sql, argf())
    print(f"  PG    {label:<26} p50 {p50 / 1000:8.2f} ms  p99 {p99 / 1000:8.2f} ms  buffers {bufs:>7,}  {plan}")


def run_mongo(label, fltf, runs, count=False, proj=None):
    if count:
        p50, p99 = timed(lambda k: coll.count_documents(fltf()), runs)
    else:
        p50, p99 = timed(lambda k: list(coll.find(fltf(), proj)), runs)
    plan, docs, keys = mongo_plan(fltf(), count)
    print(f"  Mongo {label:<26} p50 {p50 / 1000:8.2f} ms  p99 {p99 / 1000:8.2f} ms  "
          f"keys {keys:>7,} docs {docs:>7,}  {plan}")


B = lambda: rng.choice(BRANDS)
print("Q1 one item by id, whole document")
run_mongo("_id", lambda: {"_id": rng.randrange(500_000)}, 2000)
run_pg("jsonb, primary key", "SELECT doc FROM p_jsonb WHERE id = %s", lambda: (rng.randrange(500_000),), 2000)
run_pg("columns, primary key", "SELECT * FROM p_cols WHERE id = %s", lambda: (rng.randrange(500_000),), 2000)

print("Q2 brand = ? AND attrs.color = ?  (about 310 items), ids only")
run_mongo("compound index", lambda: {"brand": B(), "attrs.color": rng.choice(COLORS)}, 300, proj={"_id": 1})
run_pg("jsonb, expression index", "SELECT id FROM p_jsonb WHERE doc->>'brand' = %s AND doc#>>'{attrs,color}' = %s",
       lambda: (B(), rng.choice(COLORS)), 300)
run_pg("jsonb, GIN containment @>", "SELECT id FROM p_jsonb WHERE doc @> %s::jsonb",
       lambda: (json.dumps({"brand": B(), "attrs": {"color": rng.choice(COLORS)}}),), 300)
run_pg("columns, B-tree", "SELECT id FROM p_cols WHERE brand = %s AND color = %s",
       lambda: (B(), rng.choice(COLORS)), 300)

print("Q3 has both tags ? and ?  (about 1,000 items), count")
T2 = lambda: rng.sample(TAGS, 2)
run_mongo("multikey index, $all", lambda: {"tags": {"$all": T2()}}, 100, count=True)
run_pg("jsonb, GIN containment @>", "SELECT count(*) FROM p_jsonb WHERE doc @> %s::jsonb",
       lambda: (json.dumps({"tags": T2()}),), 100)
run_pg("columns, GIN on text[] @>", "SELECT count(*) FROM p_cols WHERE tags @> %s", lambda: (T2(),), 100)

print("Q4 price between ? and ?+1  (about 1,000 items), ids only")
P = lambda: round(rng.uniform(1, 499), 2)
def pr():
    p = P()
    return p, p + 1
run_mongo("price index", lambda: (lambda a, b: {"price": {"$gte": a, "$lt": b}})(*pr()), 300, proj={"_id": 1})
run_pg("jsonb, expression index", "SELECT id FROM p_jsonb WHERE (doc->>'price')::numeric >= %s::numeric "
       "AND (doc->>'price')::numeric < %s::numeric", pr, 300)
run_pg("jsonb, same, float param (trap)", "SELECT id FROM p_jsonb WHERE (doc->>'price')::numeric >= %s "
       "AND (doc->>'price')::numeric < %s", pr, 10)
run_pg("jsonb, jsonpath (GIN cannot)", "SELECT id FROM p_jsonb WHERE doc @? %s::jsonpath",
       lambda: ("$.price ? (@ >= %s && @ < %s)" % pr(),), 10)
run_pg("columns, B-tree", "SELECT id FROM p_cols WHERE price >= %s::numeric AND price < %s::numeric", pr, 300)

print("Q5 attrs.material = ? AND attrs.size = ?  (about 16,700 items), count, NO targeted index")
MS = lambda: (rng.choice(MATERIALS), rng.choice(SIZES))
run_mongo("no index -> collection scan", lambda: (lambda m, s: {"attrs.material": m, "attrs.size": s})(*MS()), 10,
          count=True)
run_pg("jsonb, ->> (no index)", "SELECT count(*) FROM p_jsonb WHERE doc#>>'{attrs,material}' = %s "
       "AND doc#>>'{attrs,size}' = %s", MS, 10)
run_pg("jsonb, GIN containment @>", "SELECT count(*) FROM p_jsonb WHERE doc @> %s::jsonb",
       lambda: (json.dumps({"attrs": dict(zip(("material", "size"), MS()))}),), 10)
run_pg("columns (no index)", "SELECT count(*) FROM p_cols WHERE material = %s AND size = %s", MS, 10)
