"""§5, Table 9: schema drift. 10,000 products where a few writers got the price field wrong:
  100 store price as a string ("123.45"), 50 omit it, 50 spell it "Price".
The question "how many products cost more than 100?" is asked in each store; then each store is told to enforce a schema.
"""
import json
import random

import psycopg
from pymongo import MongoClient
from pymongo.errors import OperationFailure, WriteError

from common import MONGO_URI, PG_DSN

rng = random.Random(5)
docs = []
for i in range(10_000):
    price = round(rng.uniform(1, 200), 2)
    d = {"_id": i, "name": f"item {i}"}
    if i < 100:
        d["price"] = f"{price:.2f}"          # string
    elif i < 150:
        pass                                   # missing
    elif i < 200:
        d["Price"] = price                     # wrong field name
    else:
        d["price"] = price
    d["_true_price"] = price
    docs.append(d)
truth = sum(d["_true_price"] > 100 for d in docs)
out = [f"true answer: {truth} products cost more than 100", ""]

mc = MongoClient(MONGO_URI)
db = mc.bench
db.drift.drop()
db.drift.insert_many(docs)
out.append(f"MongoDB  find({{price: {{$gt: 100}}}})                    -> {db.drift.count_documents({'price': {'$gt': 100}})}"
           "   (strings and missing fields silently skipped)")
out.append(f"MongoDB  documents whose price is a string                  -> "
           f"{db.drift.count_documents({'price': {'$type': 'string'}})}")

pg = psycopg.connect(PG_DSN, autocommit=True)
cur = pg.cursor()
cur.execute("DROP TABLE IF EXISTS drift")
cur.execute("CREATE TABLE drift (id int PRIMARY KEY, doc jsonb)")
with cur.copy("COPY drift FROM STDIN") as cp:
    for d in docs:
        cp.write_row((d["_id"], json.dumps(d)))
cur.execute("SELECT count(*) FROM drift WHERE (doc->>'price')::numeric > 100")
out.append(f"PG       (doc->>'price')::numeric > 100                     -> {cur.fetchone()[0]}"
           "   (->> returns text, so the strings cast; missing/misspelt are NULL and skipped)")
try:
    cur.execute("SELECT count(*) FROM drift WHERE (doc->'price')::numeric > 100")
    out.append(f"PG       (doc->'price')::numeric > 100                      -> {cur.fetchone()[0]}")
except psycopg.Error as e:
    out.append(f"PG       (doc->'price')::numeric > 100                      -> ERROR: {e.diag.message_primary}")
cur.execute("SELECT count(*) FROM drift WHERE doc @? '$.price ? (@ > 100)'")
out.append(f"PG       doc @? '$.price ? (@ > 100)'  (jsonpath, lax)      -> {cur.fetchone()[0]}"
           "   (a string is not > 100, so skipped)")

out += ["", "-- now enforce: price must exist and be a number"]
schema = {"$jsonSchema": {"bsonType": "object", "required": ["price"],
                          "properties": {"price": {"bsonType": ["double", "int"], "minimum": 0}}}}
db.command("collMod", "drift", validator=schema, validationLevel="strict", validationAction="error")
try:
    db.drift.insert_one({"_id": 99_999, "name": "new", "price": "9.99"})
    out.append("MongoDB  insert with string price after collMod            -> accepted")
except WriteError as e:
    out.append(f"MongoDB  insert with string price after collMod            -> rejected ({e.details.get('errmsg')})")
out.append(f"MongoDB  existing documents that violate the validator       -> "
           f"{db.drift.count_documents({'$nor': [schema]})} (collMod does not check existing data)")
try:
    db.drift.update_one({"_id": 0}, {"$set": {"name": "renamed"}})
    out.append("MongoDB  update of an existing violator (name only)         -> accepted")
except (WriteError, OperationFailure) as e:
    out.append("MongoDB  update of an existing violator (name only)         -> rejected: strict validates every update")

chk = "CHECK (jsonb_typeof(doc->'price') = 'number' AND (doc->>'price')::numeric >= 0)"
try:
    cur.execute(f"ALTER TABLE drift ADD CONSTRAINT price_is_number {chk}")
    out.append("PG       ADD CONSTRAINT ... CHECK                              -> added")
except psycopg.Error as e:
    out.append(f"PG       ADD CONSTRAINT ... CHECK                              -> ERROR: {e.diag.message_primary}")
cur.execute(f"ALTER TABLE drift ADD CONSTRAINT price_is_number {chk} NOT VALID")
out.append("PG       ADD CONSTRAINT ... CHECK ... NOT VALID                -> added (new rows checked, old ones not)")
try:
    cur.execute("""INSERT INTO drift VALUES (99999, '{"name":"new","price":"9.99"}')""")
    out.append("PG       insert with string price                           -> accepted")
except psycopg.Error as e:
    out.append(f"PG       insert with string price                           -> rejected ({e.diag.message_primary})")
try:
    cur.execute("ALTER TABLE drift VALIDATE CONSTRAINT price_is_number")
    out.append("PG       VALIDATE CONSTRAINT                                -> valid")
except psycopg.Error as e:
    out.append(f"PG       VALIDATE CONSTRAINT                                -> ERROR: {e.diag.message_primary}")
print("\n".join(out))
