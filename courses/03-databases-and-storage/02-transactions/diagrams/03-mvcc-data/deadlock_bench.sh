#!/bin/sh
# M03 Ch2 §3 §6 — lock ordering vs deadlocks: transfers between random pairs of accounts, 8 clients, 10 s,
# no retries, synchronous_commit = off; accounts 10 and 100; unordered vs ordered (lower id locked first);
# deadlock_timeout 1 s (default) and 100 ms. Runs pgbench inside the container. Output: deadlock-bench.csv
#   usage: sh deadlock_bench.sh pg18-ch2 > deadlock-bench.csv
C=${1:-pg18-ch2}
docker exec -i $C sh -c 'cat > /tmp/unordered.sql' <<'SQL'
\set a random(1, :n)
\set b random(1, :n)
BEGIN;
UPDATE acct SET bal = bal - 1 WHERE id = :a;
UPDATE acct SET bal = bal + 1 WHERE id = :b;
END;
SQL
docker exec -i $C sh -c 'cat > /tmp/ordered.sql' <<'SQL'
\set a random(1, :n)
\set b random(1, :n)
\set lo least(:a, :b)
\set hi greatest(:a, :b)
BEGIN;
UPDATE acct SET bal = bal + CASE WHEN id = :a THEN -1 ELSE 0 END + CASE WHEN id = :b THEN 1 ELSE 0 END WHERE id = :lo;
UPDATE acct SET bal = bal + CASE WHEN id = :a THEN -1 ELSE 0 END + CASE WHEN id = :b THEN 1 ELSE 0 END WHERE id = :hi AND :hi <> :lo;
END;
SQL
echo "accounts,order,deadlock_timeout,rep,committed,failed,deadlocks,tps"
for n in 10 100; do
 for order in unordered ordered; do
  for dt in 1s 100ms; do
   for rep in 1 2 3; do
    docker exec $C psql -U postgres -q -c "DROP TABLE IF EXISTS acct" -c "CREATE TABLE acct (id int PRIMARY KEY, bal int)" \
       -c "INSERT INTO acct SELECT g, 1000 FROM generate_series(1, $n) g" >/dev/null
    out=$(docker exec -e PGOPTIONS="-c synchronous_commit=off -c deadlock_timeout=$dt" $C \
          pgbench -U postgres -n -c 8 -j 8 -T 10 --max-tries=1 --failures-detailed -D n=$n -f /tmp/$order.sql postgres 2>&1)
    committed=$(echo "$out" | sed -n 's/^number of transactions actually processed: \([0-9]*\).*/\1/p')
    failed=$(echo "$out" | sed -n 's/^number of failed transactions: \([0-9]*\).*/\1/p')
    dl=$(echo "$out" | sed -n 's/^number of deadlock failures: \([0-9]*\).*/\1/p')
    tps=$(echo "$out" | sed -n 's/^tps = \([0-9.]*\).*/\1/p')
    sum=$(docker exec $C psql -U postgres -Atc "SELECT sum(bal) FROM acct")
    echo "$n,$order,$dt,$rep,$committed,$failed,$dl,$tps"
    [ "$sum" = "$((n*1000))" ] || echo "SUM MISMATCH $sum" >&2
   done
  done
 done
done
