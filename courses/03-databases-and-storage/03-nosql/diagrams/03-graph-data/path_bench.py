"""§3 Table 5: shortest directed path between two random users.

  neo4j_shortest  Cypher  MATCH p = SHORTEST 1 (a)-[:FOLLOWS]->+(b) RETURN length(p)
  pg_uni          PL/pgSQL BFS from a only, stopping at the level that reaches b      (bfs_path_len)
  pg_bi           PL/pgSQL BFS from both ends, expanding the smaller frontier          (bibfs_path_len)
  pg_cte          recursive CTE: cannot stop early, so it expands to the depth limit and then takes min(depth)

30 random pairs; all methods must agree on every length. Output: path-out.txt.
"""
import random
import statistics

import psycopg
from neo4j import GraphDatabase

from common import NEO4J_URI, PG_DSN, N_USERS, timed

rng = random.Random(23)
PAIRS = [(rng.randrange(N_USERS), rng.randrange(N_USERS)) for _ in range(30)]
MAX_DEPTH = 12

Q_NEO = "MATCH p = SHORTEST 1 (a:User {id:$a})-[:FOLLOWS]->+(b:User {id:$b}) RETURN length(p) AS n"
Q_CTE = """
WITH RECURSIVE r(id, d) AS (
  SELECT %(a)s::bigint, 0
  UNION
  SELECT f.dst, r.d + 1 FROM r JOIN follows f ON f.src = r.id WHERE r.d < %(k)s
) SELECT min(d) FROM r WHERE id = %(b)s"""


def main():
    d = GraphDatabase.driver(NEO4J_URI)
    ns = d.session(database="neo4j")
    pg = psycopg.connect(PG_DSN, autocommit=True)
    pg.execute("SET statement_timeout = '300s'")

    def neo(a, b):
        r = ns.run(Q_NEO, a=a, b=b).single()
        return r["n"] if r else None

    methods = {
        "neo4j_shortest": neo,
        "pg_bi": lambda a, b: pg.execute("SELECT bibfs_path_len(%s,%s,%s)", (a, b, MAX_DEPTH)).fetchone()[0],
        "pg_uni": lambda a, b: pg.execute("SELECT bfs_path_len(%s,%s,%s)", (a, b, MAX_DEPTH)).fetchone()[0],
    }
    truth = [neo(a, b) for a, b in PAIRS]
    lens = [x for x in truth if x is not None]
    print(f"path lengths over {len(PAIRS)} pairs: {sorted(truth, key=lambda x: (x is None, x))}")
    print(f"median length {statistics.median(lens)}; unreachable {truth.count(None)}")
    for name, fn in methods.items():
        got = [fn(a, b) for a, b in PAIRS]
        assert got == truth, (name, got, truth)
        runs = len(PAIRS) if name == "pg_uni" else 3 * len(PAIRS)   # pg_uni takes seconds per call
        p50, p99 = timed(lambda i: fn(*PAIRS[i % len(PAIRS)]), runs)
        print(f"{name:<15} p50 {p50:9.2f} ms  p99 {p99:9.2f} ms", flush=True)

    # the recursive CTE has no way to stop at the first hit: time it on a few pairs only, at the needed depth
    sub = [(a, b, n) for (a, b), n in zip(PAIRS, truth) if n is not None][:5]
    ts = []
    for a, b, n in sub:
        p50, _ = timed(lambda i: pg.execute(Q_CTE, {"a": a, "b": b, "k": n}).fetchone(), 1)
        got = pg.execute(Q_CTE, {"a": a, "b": b, "k": n}).fetchone()[0]
        assert got == n
        ts.append(p50)
        print(f"pg_cte  pair ({a},{b}) length {n}: {p50:.1f} ms (depth limit set to the known answer)", flush=True)
    print(f"pg_cte  median of {len(ts)} pairs {statistics.median(ts):.1f} ms")

    # how much each method touched, for one pair
    a, b = PAIRS[0]
    _, s, _ = d.execute_query("PROFILE " + Q_NEO, a=a, b=b)

    def walk(p, ind=0):
        print("   " + " " * ind + f"{p['operatorType'].split('@')[0]} rows={p.get('rows')} dbHits={p.get('dbHits')}")
        for c in p.get("children", []):
            walk(c, ind + 2)
    print(f"\nNeo4j PROFILE pair {PAIRS[0]}:")
    walk(s.profile)


if __name__ == "__main__":
    main()
