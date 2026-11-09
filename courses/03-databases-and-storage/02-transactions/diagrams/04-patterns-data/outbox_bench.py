#!/usr/bin/env python3
"""M03 Ch2 §4 §3 — the dual-write problem and the transactional outbox.

The "broker" is a second database on the same server (`broker`), reached on its own connection, so a write to it is
never in the same transaction as a write to the application database — the situation with SQS, Kafka, Redis, email.

  crash   2,000 orders per design. The application process "crashes" (its connection is dropped, nothing more runs)
          after a randomly chosen order with probability 1% at the dangerous point; 2% of orders also fail a deferred
          constraint at COMMIT (a commit can fail).
            commit-then-publish   INSERT order; COMMIT; <crash?>; publish
            publish-then-commit   INSERT order; publish; <crash?>; COMMIT
            outbox                INSERT order; INSERT outbox row; COMMIT       (one transaction)
                                  relay: BEGIN; SELECT ... FOR UPDATE SKIP LOCKED LIMIT 50; publish each;
                                  <relay crash? 5% per batch>; UPDATE sent_at; COMMIT
          then a consumer applies every delivered message twice over: naively (effect per message) and with an inbox
          (INSERT event_id ON CONFLICT DO NOTHING in the same transaction as the effect).
  hwm     8 writers insert outbox rows in transactions that stay open 0-20 ms after the INSERT, so ids commit out of
          order. Relay A polls `WHERE id > last_seen ORDER BY id` and advances last_seen; relay B polls
          `WHERE sent_at IS NULL ... FOR UPDATE SKIP LOCKED`. Count rows each relay never delivers.
  relay   20,000 pending events (5 per order, numbered 1..5); 1/2/4/8 relay threads x batch 1/10/100; messages per
          second, and how many events reached the broker before an earlier event of the same order.
  cdc     logical decoding with test_decoding: what a slot emits for an order + outbox transaction and for
          pg_logical_emit_message; WAL retained by a slot nobody reads.

Usage:  python outbox_bench.py <dsn-to-postgres-db> crash|hwm|relay|cdc
"""
import random
import sys
import threading
import time
import uuid

import psycopg

DSN, MODE = sys.argv[1], sys.argv[2]
ADMIN = psycopg.connect(DSN, autocommit=True)
for db in ("app", "broker"):
    if not ADMIN.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db,)).fetchone():
        ADMIN.execute(f"CREATE DATABASE {db}")
APP = DSN.rsplit("/", 1)[0] + "/app"
BRK = DSN.rsplit("/", 1)[0] + "/broker"


def setup_app():
    with psycopg.connect(APP, autocommit=True) as c:
        c.execute("DROP TABLE IF EXISTS orders, okref, outbox, inbox, effect")
        # orders.ok must reference okref(true); the check is DEFERRED to COMMIT, so a commit itself can fail
        c.execute("CREATE TABLE okref (ok boolean PRIMARY KEY)")
        c.execute("INSERT INTO okref VALUES (true)")
        c.execute("""CREATE TABLE orders (id int PRIMARY KEY,
                     ok boolean NOT NULL REFERENCES okref DEFERRABLE INITIALLY DEFERRED)""")
        c.execute("""CREATE TABLE outbox (id bigserial PRIMARY KEY, event_id uuid NOT NULL, order_id int NOT NULL,
                     n int NOT NULL DEFAULT 1, created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
                     sent_at timestamptz)""")
        c.execute("CREATE INDEX outbox_pending ON outbox (id) WHERE sent_at IS NULL")
        c.execute("CREATE TABLE inbox (event_id uuid PRIMARY KEY)")
        c.execute("CREATE TABLE effect (order_id int NOT NULL)")


def setup_broker():
    with psycopg.connect(BRK, autocommit=True) as c:
        c.execute("DROP TABLE IF EXISTS msg")
        c.execute("CREATE TABLE msg (seq bigserial PRIMARY KEY, event_id uuid, order_id int, n int)")


def publish(bc, rows):
    with bc.cursor() as cur:
        cur.executemany("INSERT INTO msg (event_id, order_id, n) VALUES (%s, %s, %s)", rows)


class Crash(Exception):
    pass


if MODE == "crash":
    print("design,orders_committed,messages_published,lost,phantom,duplicate_deliveries,"
          "effects_naive,duplicate_effects_naive,effects_inbox,duplicate_effects_inbox,app_crashes,relay_crashes")
    for design in ("commit-then-publish", "publish-then-commit", "outbox"):
        setup_app(); setup_broker()
        rnd = random.Random(7)
        app_crashes = relay_crashes = 0
        app, bc = psycopg.connect(APP), psycopg.connect(BRK, autocommit=True)
        for oid in range(1, 2001):
            ok = rnd.random() >= 0.02             # 2% fail the deferred constraint at COMMIT
            crash = rnd.random() < 0.01
            ev = uuid.uuid4()
            try:
                app.execute("INSERT INTO orders VALUES (%s, %s)", (oid, ok))
                if design == "commit-then-publish":
                    app.commit()
                    if crash: raise Crash
                    publish(bc, [(ev, oid, 1)])
                elif design == "publish-then-commit":
                    publish(bc, [(ev, oid, 1)])
                    if crash: raise Crash
                    app.commit()
                else:
                    app.execute("INSERT INTO outbox (event_id, order_id) VALUES (%s, %s)", (ev, oid))
                    if crash: raise Crash
                    app.commit()
            except Crash:
                app_crashes += 1
                app.close(); app = psycopg.connect(APP)      # process restarted; open transaction is gone
            except psycopg.errors.ForeignKeyViolation:
                app.rollback()                               # the COMMIT failed
        if design == "outbox":
            relay = psycopg.connect(APP)
            while True:
                rows = relay.execute("""SELECT id, event_id, order_id, n FROM outbox WHERE sent_at IS NULL
                                        ORDER BY id LIMIT 50 FOR UPDATE SKIP LOCKED""").fetchall()
                if not rows:
                    relay.commit(); break
                publish(bc, [(r[1], r[2], r[3]) for r in rows])
                if rnd.random() < 0.05:                      # relay dies after publishing, before marking sent
                    relay_crashes += 1
                    relay.close(); relay = psycopg.connect(APP); continue
                relay.execute("UPDATE outbox SET sent_at = now() WHERE id = ANY(%s)", ([r[0] for r in rows],))
                relay.commit()
        app.close()
        committed = {r[0] for r in psycopg.connect(APP).execute("SELECT id FROM orders").fetchall()}
        msgs = bc.execute("SELECT event_id, order_id FROM msg ORDER BY seq").fetchall()
        published_orders = {m[1] for m in msgs}
        lost = len(committed - published_orders)
        phantom = len(published_orders - committed)
        dup_deliv = len(msgs) - len({m[0] for m in msgs})
        # consumer: naive, then with an inbox
        with psycopg.connect(APP, autocommit=True) as cc:
            cc.execute("TRUNCATE effect, inbox")
            for ev, oid in msgs:
                cc.execute("INSERT INTO effect VALUES (%s)", (oid,))
            naive = cc.execute("SELECT count(*), count(*) - count(DISTINCT order_id) FROM effect").fetchone()
            cc.execute("TRUNCATE effect")
            for ev, oid in msgs:
                with cc.transaction():
                    if cc.execute("INSERT INTO inbox VALUES (%s) ON CONFLICT DO NOTHING", (ev,)).rowcount:
                        cc.execute("INSERT INTO effect VALUES (%s)", (oid,))
            inbox = cc.execute("SELECT count(*), count(*) - count(DISTINCT order_id) FROM effect").fetchone()
        print(f"{design},{len(committed)},{len(msgs)},{lost},{phantom},{dup_deliv},{naive[0]},{naive[1]},"
              f"{inbox[0]},{inbox[1]},{app_crashes},{relay_crashes}", flush=True)

elif MODE == "hwm":
    for rep in range(3):
        setup_app()
        stop = threading.Event()
        WRITES = 4000

        def writer(seed, count):
            r = random.Random(seed)
            with psycopg.connect(APP) as c:
                for _ in range(count):
                    c.execute("INSERT INTO outbox (event_id, order_id) VALUES (%s, 0)", (uuid.uuid4(),))
                    time.sleep(r.uniform(0, 0.020))
                    c.commit()

        seen_a, seen_b = set(), set()

        def relay_a():
            last = 0
            with psycopg.connect(APP, autocommit=True) as c:
                while not stop.is_set():
                    for (i,) in c.execute("SELECT id FROM outbox WHERE id > %s ORDER BY id LIMIT 100", (last,)):
                        seen_a.add(i); last = max(last, i)
                    time.sleep(0.005)

        def relay_b():
            with psycopg.connect(APP) as c:
                while True:
                    rows = c.execute("""SELECT id FROM outbox WHERE sent_at IS NULL ORDER BY id LIMIT 100
                                        FOR UPDATE SKIP LOCKED""").fetchall()
                    if rows:
                        seen_b.update(r[0] for r in rows)
                        c.execute("UPDATE outbox SET sent_at = now() WHERE id = ANY(%s)", ([r[0] for r in rows],))
                    c.commit()
                    if not rows:
                        if stop.is_set(): return
                        time.sleep(0.005)

        ws = [threading.Thread(target=writer, args=(rep * 10 + i, WRITES // 8)) for i in range(8)]
        ra, rb = threading.Thread(target=relay_a), threading.Thread(target=relay_b)
        ra.start(); rb.start()
        for t in ws: t.start()
        for t in ws: t.join()
        time.sleep(0.5); stop.set(); ra.join(); rb.join()
        total = WRITES
        print(f"rep {rep}: {total} events committed | relay A (id > last_seen) delivered {len(seen_a)}, "
              f"missed {total - len(seen_a)} | relay B (sent_at IS NULL, SKIP LOCKED) delivered {len(seen_b)}, "
              f"missed {total - len(seen_b)}", flush=True)

elif MODE == "relay":
    print("relays,batch,rep,seconds,msgs_per_s,out_of_order")
    for rep in range(3):
        for relays in (1, 2, 4, 8):
            for batch in (1, 10, 100):
                setup_app(); setup_broker()
                with psycopg.connect(APP, autocommit=True) as c:
                    c.execute("""INSERT INTO outbox (event_id, order_id, n)
                                 SELECT gen_random_uuid(), (g - 1) / 5 + 1, (g - 1) % 5 + 1
                                 FROM generate_series(1, 20000) g""")
                    c.execute("VACUUM ANALYZE outbox")

                def relay():
                    with psycopg.connect(APP) as c, psycopg.connect(BRK) as b:
                        while True:
                            rows = c.execute("""SELECT id, event_id, order_id, n FROM outbox WHERE sent_at IS NULL
                                                ORDER BY id LIMIT %s FOR UPDATE SKIP LOCKED""", (batch,)).fetchall()
                            if not rows:
                                c.commit(); return
                            publish(b, [(r[1], r[2], r[3]) for r in rows]); b.commit()
                            c.execute("UPDATE outbox SET sent_at = now() WHERE id = ANY(%s)", ([r[0] for r in rows],))
                            c.commit()

                ts = [threading.Thread(target=relay) for _ in range(relays)]
                t0 = time.perf_counter()
                for t in ts: t.start()
                for t in ts: t.join()
                secs = time.perf_counter() - t0
                with psycopg.connect(BRK) as b:
                    ooo = b.execute("""SELECT count(*) FROM (SELECT n, lag(n) OVER (PARTITION BY order_id ORDER BY seq) p
                                       FROM msg) s WHERE p IS NOT NULL AND n < p""").fetchone()[0]
                print(f"{relays},{batch},{rep},{secs:.2f},{20000 / secs:.0f},{ooo}", flush=True)

elif MODE == "cdc":
    setup_app()
    a = psycopg.connect(APP, autocommit=True)
    a.execute("SELECT pg_drop_replication_slot(slot_name) FROM pg_replication_slots WHERE slot_name = 'demo'")
    a.execute("SELECT pg_create_logical_replication_slot('demo', 'test_decoding')")
    with a.transaction():
        a.execute("INSERT INTO orders VALUES (1, true)")
        a.execute("INSERT INTO outbox (event_id, order_id) VALUES ('00000000-0000-0000-0000-000000000001', 1)")
    with a.transaction():
        a.execute("INSERT INTO orders VALUES (2, true)")
        a.execute("SELECT pg_logical_emit_message(true, 'order-events', '{\"order\": 2, \"type\": \"created\"}')")
    with a.transaction():
        a.execute("INSERT INTO orders VALUES (3, false)")    # deferred FK fails at COMMIT
        a.execute("INSERT INTO outbox (event_id, order_id) VALUES ('00000000-0000-0000-0000-000000000003', 3)")
        try:
            a.execute("SET CONSTRAINTS ALL IMMEDIATE")
        except psycopg.Error:
            pass
    print("-- what the slot emits (pg_logical_slot_get_changes); the aborted order 3 never appears")
    for lsn, xid, data in a.execute("SELECT lsn, xid, data FROM pg_logical_slot_get_changes('demo', NULL, NULL)"):
        print(f"   xid {xid}: {data[:150]}")
    print("-- an idle slot holds WAL: 100,000 more outbox rows, nobody reading")
    a.execute("""INSERT INTO outbox (event_id, order_id) SELECT gen_random_uuid(), g FROM generate_series(1, 100000) g""")
    a.execute("CHECKPOINT")
    r = a.execute("""SELECT pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)), wal_status
                     FROM pg_replication_slots WHERE slot_name = 'demo'""").fetchone()
    print(f"   WAL retained by slot 'demo': {r[0]} (wal_status {r[1]}); max_slot_wal_keep_size =",
          a.execute("SHOW max_slot_wal_keep_size").fetchone()[0])
    a.execute("SELECT pg_drop_replication_slot('demo')")
