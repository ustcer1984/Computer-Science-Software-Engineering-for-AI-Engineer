#!/bin/sh
# M03 Ch2 §2: what each isolation level costs, run inside the postgres:18 container:
#   docker cp ssi_bench.sh iso-pg:/tmp/ && docker exec iso-pg sh /tmp/ssi_bench.sh > ssi-bench.csv
# (1) transfer: read the source balance, then move 1 between two random accounts out of N.
#     --max-tries=1, so every serialization failure is counted, not hidden by a retry.
# (2) roster: the doctors-on-call check per shift (100 shifts x 10 doctors), SERIALIZABLE, with
#     and without an index the check can use — SSI's predicate locks follow the access path.
set -e
P="psql -U postgres -qtA"
# The point is the cost of isolation, not of durability: without this, each commit waits for
# the laptop SSD's flush and throughput swings 2-5x between identical runs (Ch2 §1 §4).
$P -c "ALTER DATABASE postgres SET synchronous_commit = off"
cat > /tmp/transfer.sql <<'SQL'
\set a random(1, :n)
\set b random(1, :n)
BEGIN;
SELECT bal FROM acct WHERE id = :a;
UPDATE acct SET bal = bal - 1 WHERE id = :a;
UPDATE acct SET bal = bal + 1 WHERE id = :b;
COMMIT;
SQL
cat > /tmp/roster.sql <<'SQL'
\set s random(1, 100)
\set d random(1, 10)
BEGIN;
SELECT count(*) FROM duty WHERE shift = :s AND on_call;
UPDATE duty SET on_call = NOT on_call WHERE shift = :s AND doc = :d;
COMMIT;
SQL
run() {  # level script n -> committed, failed, serialization failures, deadlocks, tps
  $P -c "ALTER DATABASE postgres SET default_transaction_isolation = '$1'"
  out=$(pgbench -U postgres -n -c8 -j8 -T 10 --max-tries=1 --failures-detailed -D n=$3 -f /tmp/$2.sql postgres 2>&1)
  tx=$(echo "$out" | sed -n 's/^number of transactions actually processed: \([0-9]*\).*/\1/p')
  fl=$(echo "$out" | sed -n 's/^number of failed transactions: \([0-9]*\).*/\1/p')
  se=$(echo "$out" | sed -n 's/^number of serialization failures: \([0-9]*\).*/\1/p')
  dl=$(echo "$out" | sed -n 's/^number of deadlock failures: \([0-9]*\).*/\1/p')
  tps=$(echo "$out" | sed -n 's/^tps = \([0-9.]*\).*/\1/p' | head -1)
  echo "$tx,${fl:-0},${se:-0},${dl:-0},$tps"
}
echo "workload,variant,level,accounts,rep,committed,failed,serialization_failures,deadlocks,tps"
for n in 10 100 1000 10000 100000; do
  $P -c "DROP TABLE IF EXISTS acct; CREATE TABLE acct (id int PRIMARY KEY, bal int);
         INSERT INTO acct SELECT g, 1000000 FROM generate_series(1, $n) g;"
  $P -c "VACUUM ANALYZE acct;"
  for lvl in "read committed" "repeatable read" "serializable"; do
    for rep in 1 2 3; do echo "transfer,pk,$lvl,$n,$rep,$(run "$lvl" transfer $n)"; done
  done
done
for variant in index noindex; do
  $P -c "DROP TABLE IF EXISTS duty; CREATE TABLE duty (shift int, doc int, on_call boolean);
         INSERT INTO duty SELECT s, d, true FROM generate_series(1,100) s, generate_series(1,10) d;"
  if [ $variant = index ]; then $P -c "CREATE UNIQUE INDEX ON duty (shift, doc);"; fi
  $P -c "VACUUM ANALYZE duty;"
  for lvl in "repeatable read" "serializable"; do
    for rep in 1 2 3; do echo "roster,$variant,$lvl,1000,$rep,$(run "$lvl" roster 1000)"; done
  done
done
$P -c "ALTER DATABASE postgres RESET ALL"
