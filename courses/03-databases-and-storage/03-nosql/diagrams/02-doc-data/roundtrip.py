"""§3: the empty round trip from Python, to separate client/driver cost from query cost in Table 6 / Figure 3.
MongoDB `ping` command vs PostgreSQL `SELECT 1`; p50 of 5,000 calls, 3 runs."""
import statistics

import psycopg
from pymongo import MongoClient

from common import MONGO_URI, PG_DSN, timed

mc = MongoClient(MONGO_URI)
cur = psycopg.connect(PG_DSN, autocommit=True).cursor()
m = [timed(lambda k: mc.admin.command("ping"), 5000)[0] for _ in range(3)]
p = [timed(lambda k: (cur.execute("SELECT 1"), cur.fetchall()), 5000)[0] for _ in range(3)]
print(f"MongoDB ping        p50 {statistics.median(m):6.1f} us")
print(f"PostgreSQL SELECT 1 p50 {statistics.median(p):6.1f} us")
