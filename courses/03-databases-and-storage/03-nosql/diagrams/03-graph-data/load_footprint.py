"""§2 Table 2: load the graph into PostgreSQL, create the indexes both stores need, and report storage.

Neo4j was loaded beforehand with `neo4j-admin database import full` (see README.md); this script only creates its
lookup index on :User(id) and reads the store sizes. PostgreSQL reads the same CSV files with COPY.
"""
import subprocess
import time

import psycopg
from neo4j import GraphDatabase

from common import NEO4J_URI, PG_DSN


def pg_load():
    with psycopg.connect(PG_DSN, autocommit=True) as c:
        c.execute("DROP TABLE IF EXISTS follows, users")
        c.execute("CREATE TABLE users (id bigint PRIMARY KEY, city int NOT NULL, age int NOT NULL)")
        c.execute("CREATE TABLE follows (src bigint NOT NULL, dst bigint NOT NULL)")
        t = time.time()
        c.execute("COPY users FROM '/import/users.csv' WITH (FORMAT csv, HEADER true)")
        c.execute("COPY follows FROM '/import/follows.csv' WITH (FORMAT csv, HEADER true)")
        t_copy = time.time() - t
        t = time.time()
        # the two indexes an adjacency query needs: out-edges by src, in-edges by dst
        c.execute("ALTER TABLE follows ADD PRIMARY KEY (src, dst)")
        c.execute("CREATE INDEX follows_dst_src ON follows (dst, src)")
        c.execute("VACUUM ANALYZE users")
        c.execute("VACUUM ANALYZE follows")
        t_idx = time.time() - t
        print(f"PostgreSQL: COPY {t_copy:.1f}s, indexes + VACUUM ANALYZE {t_idx:.1f}s")
        rows = c.execute("""
            SELECT relname, pg_relation_size(oid), reltuples::bigint
            FROM pg_class WHERE relname IN ('users','users_pkey','follows','follows_pkey','follows_dst_src')
            ORDER BY relname""").fetchall()
        for name, size, tup in rows:
            print(f"  {name:<16} {size / 2**20:8.1f} MiB  rows {tup:,}")
        return dict((r[0], r[1]) for r in rows)


def neo4j_prepare():
    with GraphDatabase.driver(NEO4J_URI) as d:
        d.execute_query("CREATE INDEX user_id IF NOT EXISTS FOR (u:User) ON (u.id)")
        d.execute_query("CALL db.awaitIndexes(600)")
        rec, _, _ = d.execute_query("SHOW DATABASES YIELD name, store WHERE name = 'neo4j' RETURN store")
        print(f"Neo4j store format: {rec[0]['store']}")
    out = subprocess.run(
        ["docker", "exec", "graph-neo4j", "sh", "-c",
         "cd /data/databases/neo4j && ls -l neostore.nodestore.db neostore.relationshipstore.db "
         "neostore.propertystore.db neostore.relationshipgroupstore.db 2>/dev/null; du -sb . ; du -sb schema"],
        capture_output=True, text=True).stdout
    print(out)


if __name__ == "__main__":
    pg_load()
    neo4j_prepare()
