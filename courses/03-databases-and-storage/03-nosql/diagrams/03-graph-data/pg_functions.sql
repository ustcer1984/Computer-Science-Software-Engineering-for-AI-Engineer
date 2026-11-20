-- Server-side breadth-first search for PostgreSQL, used by reach_bench.py and path_bench.py.
-- A recursive CTE cannot keep a "visited" set that bounds depth at the same time (§3 of the section),
-- so these loop one level at a time and keep the visited set in a temporary table.

-- How many distinct users can `start` reach in at most `k` hops along out-edges?
CREATE OR REPLACE FUNCTION bfs_reach(start bigint, k int) RETURNS bigint
LANGUAGE plpgsql AS $$
DECLARE
  depth int := 0;
  n bigint;
BEGIN
  CREATE TEMP TABLE IF NOT EXISTS bfs_seen (id bigint PRIMARY KEY) ON COMMIT DROP;
  CREATE TEMP TABLE IF NOT EXISTS bfs_frontier (id bigint) ON COMMIT DROP;
  TRUNCATE bfs_seen, bfs_frontier;
  INSERT INTO bfs_seen VALUES (start);
  INSERT INTO bfs_frontier VALUES (start);
  WHILE depth < k LOOP
    depth := depth + 1;
    CREATE TEMP TABLE IF NOT EXISTS bfs_next (id bigint) ON COMMIT DROP;
    TRUNCATE bfs_next;
    -- Expand first, then remove visited users. Written as one join, the planner estimated the anti-join at
    -- 1 row at depth 7 and chose a nested loop over the whole frontier: one call was still running after 49 minutes (README).
    INSERT INTO bfs_next
      WITH x AS MATERIALIZED (SELECT DISTINCT f.dst FROM bfs_frontier fr JOIN follows f ON f.src = fr.id)
      SELECT dst FROM x WHERE NOT EXISTS (SELECT 1 FROM bfs_seen s WHERE s.id = x.dst);
    GET DIAGNOSTICS n = ROW_COUNT;
    EXIT WHEN n = 0;
    INSERT INTO bfs_seen SELECT id FROM bfs_next;
    TRUNCATE bfs_frontier;
    INSERT INTO bfs_frontier SELECT id FROM bfs_next;
    ANALYZE bfs_frontier; ANALYZE bfs_seen;   -- keep statistics current (not enough on its own; see the step above)
  END LOOP;
  SELECT count(*) - 1 INTO n FROM bfs_seen;
  RETURN n;
END $$;

-- Length of the shortest directed path from `a` to `b` (NULL if none within max_depth hops).
-- One-directional: expands from `a` only, level by level, and stops at the level that reaches `b`.
CREATE OR REPLACE FUNCTION bfs_path_len(a bigint, b bigint, max_depth int) RETURNS int
LANGUAGE plpgsql AS $$
DECLARE
  depth int := 0;
  n bigint;
BEGIN
  IF a = b THEN RETURN 0; END IF;
  CREATE TEMP TABLE IF NOT EXISTS bfs_seen (id bigint PRIMARY KEY) ON COMMIT DROP;
  CREATE TEMP TABLE IF NOT EXISTS bfs_frontier (id bigint) ON COMMIT DROP;
  CREATE TEMP TABLE IF NOT EXISTS bfs_next (id bigint) ON COMMIT DROP;
  TRUNCATE bfs_seen, bfs_frontier;
  INSERT INTO bfs_seen VALUES (a);
  INSERT INTO bfs_frontier VALUES (a);
  WHILE depth < max_depth LOOP
    depth := depth + 1;
    TRUNCATE bfs_next;
    -- Expand first, then remove visited users. Written as one join, the planner estimated the anti-join at
    -- 1 row at depth 7 and chose a nested loop over the whole frontier: one call was still running after 49 minutes (README).
    INSERT INTO bfs_next
      WITH x AS MATERIALIZED (SELECT DISTINCT f.dst FROM bfs_frontier fr JOIN follows f ON f.src = fr.id)
      SELECT dst FROM x WHERE NOT EXISTS (SELECT 1 FROM bfs_seen s WHERE s.id = x.dst);
    GET DIAGNOSTICS n = ROW_COUNT;
    IF n = 0 THEN RETURN NULL; END IF;
    IF EXISTS (SELECT 1 FROM bfs_next WHERE id = b) THEN RETURN depth; END IF;
    INSERT INTO bfs_seen SELECT id FROM bfs_next;
    TRUNCATE bfs_frontier;
    INSERT INTO bfs_frontier SELECT id FROM bfs_next;
    ANALYZE bfs_frontier; ANALYZE bfs_seen;   -- keep statistics current (not enough on its own; see the step above)
  END LOOP;
  RETURN NULL;
END $$;

-- Bidirectional version: expand forward from `a` (out-edges) and backward from `b` (in-edges), always the smaller
-- frontier, and stop when the two visited sets meet. This is the algorithm Neo4j's shortest-path operator uses.
CREATE OR REPLACE FUNCTION bibfs_path_len(a bigint, b bigint, max_depth int) RETURNS int
LANGUAGE plpgsql AS $$
DECLARE
  df int := 0;  -- depth reached forward
  db int := 0;  -- depth reached backward
  nf bigint := 1;
  nb bigint := 1;
  meet int;
BEGIN
  IF a = b THEN RETURN 0; END IF;
  CREATE TEMP TABLE IF NOT EXISTS fw_seen (id bigint PRIMARY KEY, d int) ON COMMIT DROP;
  CREATE TEMP TABLE IF NOT EXISTS bw_seen (id bigint PRIMARY KEY, d int) ON COMMIT DROP;
  CREATE TEMP TABLE IF NOT EXISTS step (id bigint) ON COMMIT DROP;
  TRUNCATE fw_seen, bw_seen;
  INSERT INTO fw_seen VALUES (a, 0);
  INSERT INTO bw_seen VALUES (b, 0);
  WHILE df + db < max_depth LOOP
    TRUNCATE step;
    IF nf <= nb THEN
      df := df + 1;
      INSERT INTO step
        WITH c AS MATERIALIZED (SELECT DISTINCT f.dst AS id FROM fw_seen s JOIN follows f ON f.src = s.id
                                WHERE s.d = df - 1)
        SELECT id FROM c WHERE NOT EXISTS (SELECT 1 FROM fw_seen x WHERE x.id = c.id);
      GET DIAGNOSTICS nf = ROW_COUNT;
      IF nf = 0 THEN RETURN NULL; END IF;
      INSERT INTO fw_seen SELECT id, df FROM step;
    ELSE
      db := db + 1;
      INSERT INTO step
        WITH c AS MATERIALIZED (SELECT DISTINCT f.src AS id FROM bw_seen s JOIN follows f ON f.dst = s.id
                                WHERE s.d = db - 1)
        SELECT id FROM c WHERE NOT EXISTS (SELECT 1 FROM bw_seen x WHERE x.id = c.id);
      GET DIAGNOSTICS nb = ROW_COUNT;
      IF nb = 0 THEN RETURN NULL; END IF;
      INSERT INTO bw_seen SELECT id, db FROM step;
    END IF;
    ANALYZE fw_seen; ANALYZE bw_seen;
    SELECT min(f.d + w.d) INTO meet FROM fw_seen f JOIN bw_seen w USING (id);
    IF meet IS NOT NULL THEN RETURN meet; END IF;
  END LOOP;
  RETURN NULL;
END $$;
