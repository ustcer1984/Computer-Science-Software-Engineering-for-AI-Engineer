"""§5 Table 6 and §6 Table 7: where the shape of the question, not the engine, decides the cost.

Part A, supernodes: "how many other users follow at least one account I follow?" (out one hop, then in one hop)
  for 20 users who follow only small accounts, and 20 users who follow the most-followed account (151,514 followers).
Part B, path explosion: the same start users, k-hop reach ignoring direction, counted as distinct users and as paths.
Part C, whole-graph questions: average age per city; the ten most-followed users.

Output: shape-out.txt.
"""
import random
import time

import numpy as np
import psycopg
from neo4j import GraphDatabase

from common import NEO4J_URI, PG_DSN, build_graph, timed

TIMEOUT_S = 60


def main():
    d = GraphDatabase.driver(NEO4J_URI)
    ns = d.session(database="neo4j")
    pg = psycopg.connect(PG_DSN, autocommit=True)
    pg.execute(f"SET statement_timeout = '{TIMEOUT_S}s'")

    _, _, src, dst = build_graph()
    n = int(max(src.max(), dst.max())) + 1
    indeg = np.bincount(dst, minlength=n)
    top = int(indeg.argmax())
    big = indeg[dst] > 1000                      # edge points at an account with over 1,000 followers
    follows_big = np.zeros(n, dtype=bool)
    follows_big[src[big]] = True
    follows_top = np.zeros(n, dtype=bool)
    follows_top[src[dst == top]] = True
    rng = random.Random(5)
    small = rng.sample(list(np.flatnonzero(~follows_big)), 20)
    celeb = rng.sample(list(np.flatnonzero(follows_top)), 20)
    print(f"most-followed user {top} has {indeg[top]:,} followers; {follows_top.sum():,} users follow it; "
          f"{(~follows_big).sum():,} users follow no account with over 1,000 followers")

    # ---- Part A: co-followers -------------------------------------------------------------------------------
    q_neo = ("MATCH (me:User {id:$id})-[:FOLLOWS]->(:User)<-[:FOLLOWS]-(other) WHERE other <> me "
             "RETURN count(DISTINCT other) AS n")
    q_pg = ("SELECT count(DISTINCT f2.src) FROM follows f1 JOIN follows f2 ON f2.dst = f1.dst "
            "WHERE f1.src = %s AND f2.src <> %s")
    print("\nA. co-followers (distinct users who follow something I follow)")
    for label, group in (("follows only small accounts", small), ("follows the top account", celeb)):
        res = [ns.run(q_neo, id=int(u)).single()["n"] for u in group]
        assert res == [pg.execute(q_pg, (int(u), int(u))).fetchone()[0] for u in group]
        a, _ = timed(lambda i: ns.run(q_neo, id=int(group[i % 20])).consume(), 40)
        b, _ = timed(lambda i: pg.execute(q_pg, (int(group[i % 20]),) * 2).fetchone(), 40)
        print(f"  {label:<30} answer median {int(np.median(res)):>8,}   Neo4j p50 {a:8.2f} ms   PostgreSQL p50 {b:8.2f} ms")
    u = int(celeb[0])
    _, s, _ = d.execute_query("PROFILE " + q_neo, id=u)

    def hits(p):
        return p.get("dbHits", 0) + sum(hits(c) for c in p.get("children", []))
    print(f"  Neo4j PROFILE for one top-account follower: {hits(s.profile):,} db hits")
    for (line,) in pg.execute("EXPLAIN (ANALYZE, BUFFERS) " + q_pg, (u, u)).fetchall():
        if "Buffers" in line or "Execution" in line:
            print("   PG", line.strip())
            break

    # ---- Part B: ignoring direction, distinct users vs paths -----------------------------------------------
    print("\nB. reach ignoring direction (k hops), distinct users vs paths, one ordinary start user")
    s0 = int(small[0])
    for k in (1, 2, 3):
        qd = f"MATCH (a:User {{id:$id}})-[:FOLLOWS*1..{k}]-(b) WHERE b <> a RETURN count(DISTINCT b) AS n"
        qp = f"MATCH (a:User {{id:$id}})-[:FOLLOWS*1..{k}]-(b) WHERE b <> a RETURN count(b) AS n"
        out = []
        for name, q in (("distinct", qd), ("paths", qp)):
            t = time.perf_counter()
            try:
                r = ns.run(q, id=s0, timeout=TIMEOUT_S).single()["n"]
            except Exception as e:  # noqa: BLE001 - report the timeout as data
                r = f"timeout>{TIMEOUT_S}s ({type(e).__name__})"
            out.append(f"{name} {r if isinstance(r, str) else f'{r:,}'} in {(time.perf_counter() - t) * 1e3:,.0f} ms")
        cte = f"""WITH RECURSIVE r(id, d) AS (
            SELECT {s0}::bigint, 0
            UNION ALL
            SELECT x.nb, r.d + 1 FROM r CROSS JOIN LATERAL (
                SELECT dst AS nb FROM follows WHERE src = r.id
                UNION ALL
                SELECT src FROM follows WHERE dst = r.id) x
            WHERE r.d < {k})
          SELECT count(*) FROM r WHERE id <> {s0}"""
        t = time.perf_counter()
        try:
            r = pg.execute(cte).fetchone()[0]
            pgs = f"{r:,} rows in {(time.perf_counter() - t) * 1e3:,.0f} ms"
        except psycopg.errors.QueryCanceled:
            pgs = f"cancelled at {TIMEOUT_S}s"
        except psycopg.Error as e:
            pgs = f"error: {str(e).splitlines()[0]}"
        print(f"  k={k}: Neo4j {out[0]}; Neo4j {out[1]}; PostgreSQL UNION ALL CTE {pgs}", flush=True)

    # ---- Part C: whole-graph questions ---------------------------------------------------------------------
    print("\nC. whole-graph questions")
    qs = [
        ("average age per city",
         "MATCH (u:User) RETURN u.city AS city, avg(u.age) AS a",
         "SELECT city, avg(age) FROM users GROUP BY city"),
        ("ten most-followed users",
         "MATCH (u:User) RETURN u.id AS id, COUNT { (u)<-[:FOLLOWS]-() } AS f ORDER BY f DESC LIMIT 10",
         "SELECT dst, count(*) AS f FROM follows GROUP BY dst ORDER BY f DESC LIMIT 10"),
        ("count all follow edges",
         "MATCH ()-[r:FOLLOWS]->() RETURN count(r) AS n",
         "SELECT count(*) FROM follows"),
    ]
    for label, qn, qp in qs:
        ns.run(qn).consume()
        pg.execute(qp).fetchall()
        a, _ = timed(lambda i: ns.run(qn).consume(), 5)
        b, _ = timed(lambda i: pg.execute(qp).fetchall(), 5)
        print(f"  {label:<26} Neo4j p50 {a:9.1f} ms   PostgreSQL p50 {b:9.1f} ms")
    _, s, _ = d.execute_query("PROFILE " + qs[1][1])

    def ops(p):
        return [f"{p['operatorType'].split('@')[0]}({p.get('dbHits')})"] + [o for c in p.get("children", []) for o in ops(c)]
    print("  Neo4j plan, most-followed:", " <- ".join(ops(s.profile)))


if __name__ == "__main__":
    main()
