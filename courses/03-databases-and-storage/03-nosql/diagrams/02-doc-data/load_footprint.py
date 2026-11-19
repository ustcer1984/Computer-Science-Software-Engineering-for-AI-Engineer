"""§2, Table 3 and Table 5: load 500,000 catalogue items four ways and measure storage and index sizes.

MongoDB: collection `products` (BSON, WiredTiger, default snappy block compression).
PostgreSQL: `p_jsonb` (id + jsonb), `p_json` (id + json text), `p_cols` (one column per field, tags as text[]).
"""
import json
import sys

import psycopg
from pymongo import ASCENDING, MongoClient

from common import MONGO_URI, PG_DSN, products

N = int(sys.argv[1]) if len(sys.argv) > 1 else 500_000
docs = products(N)
json_bytes = sum(len(json.dumps(d, separators=(",", ":"))) for d in docs)

mc = MongoClient(MONGO_URI)
db = mc.bench
db.products.drop()
for i in range(0, N, 10_000):
    db.products.insert_many(docs[i:i + 10_000], ordered=False)

pg = psycopg.connect(PG_DSN, autocommit=True)
cur = pg.cursor()
cur.execute("""
DROP TABLE IF EXISTS p_jsonb, p_json, p_cols;
CREATE TABLE p_jsonb (id int PRIMARY KEY, doc jsonb NOT NULL);
CREATE TABLE p_json  (id int PRIMARY KEY, doc json  NOT NULL);
CREATE TABLE p_cols  (id int PRIMARY KEY, sku text, name text, category text, brand text, price numeric(8,2),
                      stock int, tags text[], color text, size text, weight_g int, material text,
                      rating_avg numeric(2,1), rating_count int, description text);
""")
for table in ("p_jsonb", "p_json"):
    with cur.copy(f"COPY {table} (id, doc) FROM STDIN") as cp:
        for d in docs:
            cp.write_row((d["_id"], json.dumps(d, separators=(",", ":"))))
with cur.copy("COPY p_cols FROM STDIN") as cp:
    for d in docs:
        a, r = d["attrs"], d["rating"]
        cp.write_row((d["_id"], d["sku"], d["name"], d["category"], d["brand"], d["price"], d["stock"], d["tags"],
                      a["color"], a["size"], a["weight_g"], a["material"], r["avg"], r["count"], d["description"]))
for stmt in ("VACUUM ANALYZE p_jsonb", "VACUUM ANALYZE p_json", "VACUUM ANALYZE p_cols", "CHECKPOINT"):
    cur.execute(stmt)
mc.admin.command("fsync")

out = [f"items: {N:,}   JSON text, compact: {json_bytes / N:.0f} bytes per item on average", "",
       "== Table 3: storage per item, before secondary indexes =="]
st = db.command("collStats", "products")
out.append(f"MongoDB BSON (uncompressed, avgObjSize)   {st['avgObjSize']:>6.0f} B/item")
out.append(f"MongoDB on disk (storageSize, snappy)     {st['storageSize'] / N:>6.0f} B/item   "
           f"_id index {st['indexSizes']['_id_'] / N:.0f} B/item")
for t in ("p_jsonb", "p_json", "p_cols"):
    cur.execute(f"SELECT pg_table_size('{t}'), pg_indexes_size('{t}'), "
                f"(SELECT avg(pg_column_size(t.*)) FROM {t} t)")
    tbl, idx, row = cur.fetchone()
    out.append(f"PostgreSQL {t:<8} heap+TOAST               {tbl / N:>6.0f} B/item   "
               f"primary key {idx / N:.0f} B/item   avg row {float(row):.0f} B")
cur.execute("SELECT avg(pg_column_size(doc)) FROM p_jsonb")
jb = float(cur.fetchone()[0])
cur.execute("SELECT avg(pg_column_size(doc)) FROM p_json")
js = float(cur.fetchone()[0])
out.append(f"avg stored value: jsonb {jb:.0f} B, json {js:.0f} B")

# ---- secondary indexes -------------------------------------------------------------------------------
db.products.create_index([("brand", ASCENDING)], name="brand")
db.products.create_index([("tags", ASCENDING)], name="tags_multikey")
db.products.create_index([("price", ASCENDING)], name="price")
db.products.create_index([("brand", ASCENDING), ("attrs.color", ASCENDING)], name="brand_color")
cur.execute("""
CREATE INDEX j_brand       ON p_jsonb ((doc->>'brand'));
CREATE INDEX j_price       ON p_jsonb (((doc->>'price')::numeric));
CREATE INDEX j_brand_color ON p_jsonb ((doc->>'brand'), (doc#>>'{attrs,color}'));
CREATE INDEX j_gin_ops     ON p_jsonb USING gin (doc);
CREATE INDEX j_gin_path    ON p_jsonb USING gin (doc jsonb_path_ops);
CREATE INDEX c_brand       ON p_cols (brand);
CREATE INDEX c_price       ON p_cols (price);
CREATE INDEX c_brand_color ON p_cols (brand, color);
CREATE INDEX c_tags_gin    ON p_cols USING gin (tags);
ANALYZE p_jsonb; ANALYZE p_cols;
""")
mc.admin.command("fsync")
st = db.command("collStats", "products")
out += ["", "== Table 5: secondary index sizes (MB) =="]
for name, size in st["indexSizes"].items():
    out.append(f"MongoDB    {name:<16} {size / 2**20:>7.1f}")
cur.execute("""SELECT c.relname, pg_relation_size(c.oid) FROM pg_class c JOIN pg_index i ON i.indexrelid = c.oid
               WHERE i.indrelid IN ('p_jsonb'::regclass, 'p_cols'::regclass) ORDER BY 1""")
for name, size in cur.fetchall():
    out.append(f"PostgreSQL {name:<16} {size / 2**20:>7.1f}")
print("\n".join(out))
