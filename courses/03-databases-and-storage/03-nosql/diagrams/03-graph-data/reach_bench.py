"""§3 Figure 2 and Table 4: "how many users can X reach in k hops?", k = 1..6, by five methods.

Methods (all count distinct users reached along out-edges, excluding the start):
  neo4j_bfs   Cypher  MATCH (a)-[:FOLLOWS*1..k]->(b) WHERE b <> a RETURN count(DISTINCT b)   (planner picks a pruning BFS)
  neo4j_paths Cypher  the same pattern with count(b), no DISTINCT: one row per path, so every path is walked
  pg_bfs      PL/pgSQL level-by-level BFS with a visited table (pg_functions.sql)
  pg_cte      recursive CTE, UNION over (id, depth): dedupes per level only
  pg_paths    recursive CTE, UNION ALL: every path, deduplicated at the end
  csr         the graph as two numpy arrays in this process (compressed sparse row), BFS with numpy

Path-enumerating methods are only run while their row count stays below PATH_LIMIT.
Writes reach-bench.csv and prints plans/work counters to stdout (reach-out.txt).
"""
import csv
import random
import time

import numpy as np
import psycopg
from neo4j import GraphDatabase

from common import NEO4J_URI, PG_DSN, N_USERS, build_graph, timed

STARTS = random.Random(11).sample(range(N_USERS), 20)
DEPTHS = range(1, 7)
PATH_LIMIT_DEPTH = 6

CTE_SET = """
WITH RECURSIVE r(id, d) AS (
  SELECT %(s)s::bigint, 0
  UNION
  SELECT f.dst, r.d + 1 FROM r JOIN follows f ON f.src = r.id WHERE r.d < %(k)s
) SELECT count(DISTINCT id) - 1 FROM r"""

CTE_ALL = """
WITH RECURSIVE r(id, d) AS (
  SELECT %(s)s::bigint, 0
  UNION ALL
  SELECT f.dst, r.d + 1 FROM r JOIN follows f ON f.src = r.id WHERE r.d < %(k)s
) SELECT count(DISTINCT id) - 1, count(*) - 1 FROM r"""


def csr_arrays():
    _, _, src, dst = build_graph()
    order = np.argsort(src, kind="stable")
    col = dst[order].astype(np.int32)
    indptr = np.zeros(N_USERS + 1, dtype=np.int64)
    np.cumsum(np.bincount(src, minlength=N_USERS), out=indptr[1:])
    return indptr, col


def csr_reach(indptr, col, start, k):
    seen = np.zeros(N_USERS, dtype=bool)
    seen[start] = True
    frontier = np.array([start])
    for _ in range(k):
        lo, hi = indptr[frontier], indptr[frontier + 1]
        idx = np.concatenate([np.arange(a, b) for a, b in zip(lo, hi)]) if len(frontier) < 2000 else \
            np.repeat(lo - np.concatenate([[0], np.cumsum(hi - lo)[:-1]]), hi - lo) + np.arange((hi - lo).sum())
        nxt = np.unique(col[idx])
        nxt = nxt[~seen[nxt]]
        if len(nxt) == 0:
            break
        seen[nxt] = True
        frontier = nxt
    return int(seen.sum()) - 1


def main():
    d = GraphDatabase.driver(NEO4J_URI)
    ns = d.session(database="neo4j")   # one session, auto-commit queries: the cheapest call path
    pg = psycopg.connect(PG_DSN, autocommit=True)
    t = time.time()
    indptr, col = csr_arrays()
    print(f"CSR built in {time.time() - t:.1f}s: indptr {indptr.nbytes / 2**20:.1f} MiB + col {col.nbytes / 2**20:.1f} MiB")

    # fixed cost per call
    p50, _ = timed(lambda i: ns.run("RETURN 1").consume(), 300)
    print(f"empty round trip: Neo4j RETURN 1 p50 {p50:.3f} ms", end="; ")
    p50, _ = timed(lambda i: pg.execute("SELECT 1").fetchone(), 300)
    print(f"PostgreSQL SELECT 1 p50 {p50:.3f} ms")

    # warm both caches with a full pass over the edges
    d.execute_query("MATCH (:User)-[r:FOLLOWS]->() RETURN count(r)")
    pg.execute("SELECT count(*) FROM follows").fetchone()
    pg.execute("SELECT count(*) FROM (SELECT src FROM follows ORDER BY src, dst) x").fetchone()

    rows = []
    for k in DEPTHS:
        q_bfs = f"MATCH (a:User {{id:$id}})-[:FOLLOWS*1..{k}]->(b) WHERE b <> a RETURN count(DISTINCT b) AS n"
        q_paths = (f"MATCH (a:User {{id:$id}})-[:FOLLOWS*1..{k}]->(b) "
                   f"WHERE b <> a RETURN count(b) AS paths")
        d.execute_query(q_bfs, id=STARTS[0])  # compile once
        methods = {
            "neo4j_bfs": lambda s: ns.run(q_bfs, id=s).single()["n"],
            "pg_bfs": lambda s: pg.execute("SELECT bfs_reach(%s, %s)", (s, k)).fetchone()[0],
            "pg_cte": lambda s: pg.execute(CTE_SET, {"s": s, "k": k}).fetchone()[0],
            "csr": lambda s: csr_reach(indptr, col, s, k),
        }
        if k <= PATH_LIMIT_DEPTH:
            d.execute_query(q_paths, id=STARTS[0])
            methods["neo4j_paths"] = lambda s: ns.run(q_paths, id=s).single()["paths"]
            methods["pg_paths"] = lambda s: pg.execute(CTE_ALL, {"s": s, "k": k}).fetchone()[1]
        reached = [methods["neo4j_bfs"](s) for s in STARTS]
        for name, fn in methods.items():
            out = [fn(s) for s in STARTS]  # warm, and check the answers
            if name not in ("neo4j_paths", "pg_paths"):
                assert out == reached, (name, k, out[:3], reached[:3])
            p50, p99 = timed(lambda i: fn(STARTS[i % len(STARTS)]), 3 * len(STARTS))
            extra = int(np.median(out)) if name.endswith("paths") else ""
            rows.append([k, name, round(p50, 3), round(p99, 3), int(np.median(reached)), extra])
            print(f"k={k} {name:<12} p50 {p50:9.2f} ms  p99 {p99:9.2f} ms  reached(median) {int(np.median(reached)):>7}"
                  + (f"  paths(median) {extra}" if extra != "" else ""), flush=True)

    with open("reach-bench.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["depth", "method", "p50_ms", "p99_ms", "reached_median", "paths_median"])
        w.writerows(rows)

    # work counters for one start at depth 3 and 5
    s = STARTS[0]
    for k in (3, 5):
        _, summ, _ = d.execute_query(f"PROFILE MATCH (a:User {{id:$id}})-[:FOLLOWS*1..{k}]->(b) "
                                     f"WHERE b <> a RETURN count(DISTINCT b) AS n", id=s)

        def hits(p):
            return p.get("dbHits", 0) + sum(hits(c) for c in p.get("children", []))

        def ops(p):
            return [p["operatorType"].split("@")[0]] + [o for c in p.get("children", []) for o in ops(c)]
        print(f"\nNeo4j PROFILE k={k}: {' <- '.join(ops(summ.profile))}; total db hits {hits(summ.profile):,}")
        for name, sql, args in (("pg_cte", CTE_SET, {"s": s, "k": k}),):
            plan = pg.execute("EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) " + sql, args).fetchall()
            print(f"PostgreSQL {name} k={k}:")
            for (line,) in plan:
                if any(w in line for w in ("Recursive Union", "Buffers", "Execution Time", "Index Only Scan",
                                           "Nested Loop", "Hash Join", "WorkTable", "rows=")):
                    print("   ", line.strip()[:150])


if __name__ == "__main__":
    main()
