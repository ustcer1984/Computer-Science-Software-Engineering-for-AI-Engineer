"""§9 Applied — one order through "outbox + relay", step by step, with one relay crash.

Same setup as outbox_bench.py: the "broker" is a second database (`broker`) reached on its own connection.
Prints, after every step, the order row, the outbox row (sent_at), the broker's messages and the consumers' effects:

  1. the application inserts the order and its outbox row in ONE transaction, and commits
  2. relay attempt 1 claims the row (FOR UPDATE SKIP LOCKED), publishes it, then "crashes" before UPDATE sent_at
  3. relay attempt 2 finds the row still unsent, publishes it again, marks it sent, commits
  4. a naive consumer applies every delivery; an inbox consumer records event_id with the effect and skips repeats
  5. a rolled-back order: the application's transaction aborts — no order, no outbox row, nothing ever published

Usage:  python outbox_trace.py <dsn-to-postgres-db>
"""
import sys, psycopg

DSN = sys.argv[1]
ADMIN = psycopg.connect(DSN, autocommit=True)
for db in ("app", "broker"):
    ADMIN.execute(f"DROP DATABASE IF EXISTS {db} WITH (FORCE)")
    ADMIN.execute(f"CREATE DATABASE {db}")
APP = DSN.rsplit("/", 1)[0] + "/app"
BRK = DSN.rsplit("/", 1)[0] + "/broker"

with psycopg.connect(APP, autocommit=True) as c:
    c.execute("""CREATE TABLE orders (id bigint PRIMARY KEY, item text NOT NULL);
                 CREATE TABLE outbox (id bigserial PRIMARY KEY, event_id uuid NOT NULL DEFAULT gen_random_uuid(),
                                      aggregate_id bigint NOT NULL, type text NOT NULL, payload jsonb NOT NULL,
                                      sent_at timestamptz);
                 CREATE TABLE effects_naive (n bigserial, event_id uuid, order_id bigint);
                 CREATE TABLE inbox (event_id uuid PRIMARY KEY);
                 CREATE TABLE effects_inbox (n bigserial, event_id uuid, order_id bigint);""")
with psycopg.connect(BRK, autocommit=True) as c:
    c.execute("CREATE TABLE messages (seq bigserial, event_id uuid, body jsonb)")

app = psycopg.connect(APP, autocommit=True)
brk = psycopg.connect(BRK, autocommit=True)


def state(step):
    orders = app.execute("SELECT count(*) FROM orders").fetchone()[0]
    ob = app.execute("SELECT count(*), count(*) FILTER (WHERE sent_at IS NULL) FROM outbox").fetchone()
    msgs = brk.execute("SELECT count(*), count(DISTINCT event_id) FROM messages").fetchone()
    naive = app.execute("SELECT count(*) FROM effects_naive").fetchone()[0]
    inbox = app.execute("SELECT count(*) FROM effects_inbox").fetchone()[0]
    print(f"| {step} | {orders} | {ob[0]} ({ob[1]} unsent) | {msgs[0]} ({msgs[1]} distinct event_id) "
          f"| {naive} | {inbox} |", flush=True)


print("| Step | Orders | Outbox rows | Broker messages | Naive consumer effects | Inbox consumer effects |")
print("|---|---|---|---|---|---|")
state("0. start")

# 1. the application: one transaction, two inserts
with psycopg.connect(APP) as a:
    a.execute("INSERT INTO orders VALUES (42, 'book')")
    a.execute("""INSERT INTO outbox (aggregate_id, type, payload)
                 VALUES (42, 'order_created', '{"order_id": 42}')""")
    state("1a. app inserted both rows, not committed (seen from outside)")
    a.commit()
state("1b. app committed")


def relay(crash_before_mark):
    r = psycopg.connect(APP)
    rows = r.execute("""SELECT id, event_id, payload FROM outbox WHERE sent_at IS NULL
                        ORDER BY id LIMIT 50 FOR UPDATE SKIP LOCKED""").fetchall()
    for _, eid, body in rows:
        brk.execute("INSERT INTO messages (event_id, body) VALUES (%s, %s)", (eid, psycopg.types.json.Jsonb(body)))
    if crash_before_mark:
        r.close()                       # process dies: its transaction (and row locks) vanish, sent_at never set
        return len(rows)
    r.execute("UPDATE outbox SET sent_at = now() WHERE id = ANY(%s)", ([x[0] for x in rows],))
    r.commit(); r.close()
    return len(rows)


n = relay(crash_before_mark=True)
state(f"2. relay attempt 1: claimed {n}, published, crashed before marking sent")
n = relay(crash_before_mark=False)
state(f"3. relay attempt 2: claimed {n} (still unsent), published again, marked sent")
n = relay(crash_before_mark=False)
state(f"3b. relay attempt 3: claimed {n}, nothing to do")

# 4. consumers read every delivered message
for eid, body in brk.execute("SELECT event_id, body FROM messages ORDER BY seq").fetchall():
    app.execute("INSERT INTO effects_naive (event_id, order_id) VALUES (%s, %s)", (eid, body["order_id"]))
    with app.transaction():
        if app.execute("INSERT INTO inbox VALUES (%s) ON CONFLICT DO NOTHING", (eid,)).rowcount == 1:
            app.execute("INSERT INTO effects_inbox (event_id, order_id) VALUES (%s, %s)", (eid, body["order_id"]))
state("4. both consumers read the 2 deliveries")

# 5. an order whose transaction fails: nothing to publish
try:
    with psycopg.connect(APP) as a:
        a.execute("INSERT INTO orders VALUES (43, 'pen')")
        a.execute("""INSERT INTO outbox (aggregate_id, type, payload)
                     VALUES (43, 'order_created', '{"order_id": 43}')""")
        a.execute("INSERT INTO orders VALUES (43, 'pen again')")    # duplicate key: the transaction aborts
except psycopg.errors.UniqueViolation:
    pass
relay(crash_before_mark=False)
state("5. order 43's transaction failed; relay ran")
