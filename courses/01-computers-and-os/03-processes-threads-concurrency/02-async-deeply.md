# M01 · Ch3 · §2 — Async, Deeply: The Event Loop, Tasks vs Coroutines vs Futures, Structured Concurrency, and Cancellation

> **Module:** How Computers & Operating Systems Work
> **Chapter:** Processes, Threads & Concurrency
> **Section:** One level under §1. §1 told you *which* model to pick (async for I/O-bound high fan-out) and *why* (the GIL is free
> while you wait). This section opens the async box and shows the machinery: **what the event loop actually does on each tick**, the
> **three things people lump together as "a coroutine"** (coroutine vs Future vs Task) and how a Task *drives* a coroutine, the
> **spawning primitives** (`await` vs `create_task` vs `gather` vs `as_completed` vs `TaskGroup`) and when each is right, **structured
> concurrency** (why `TaskGroup` exists and what the unstructured `go`-statement world cost us), and — the centrepiece, and the direct
> cash-in of your 06-16 session — **cancellation**: how it's an *exception injected into a parked coroutine*, why it only lands at an
> `await`, why `CancelledError` is a `BaseException` you must re-raise, and how `asyncio.timeout` is built entirely on top of it.
> **Status:** ✅ **finalized 2026-06-25.** The body held at your level and went untouched — you drove a single, sharp Q&A thread into the
> §5 cancellation mechanism via check-question 8.5 (a timeout wrapped around a non-yielding CPU loop). This time the hypothesis wasn't
> mis-ranked — you named the **dominant** reason correctly ("the timeout will never fire"), and we made it precise into the **two
> independent reasons** it can't work. §10 captures it.

**Estimated study time:** 2–3 hours including reflection.

**Prerequisites — this section is built on three things you already own:**
- **Ch1 §2 (the call stack):** your own derivation that async is **one live native stack + N parked heap continuations the event loop
  swaps** (green threads); that a coroutine is a *single-use frame* and a Task is a *reusable result box*; and that **`await` is not
  concurrency** — two sequential `await`s are blocking calls in disguise. This section makes the "swap" mechanical.
- **Ch3 §1 (concurrency vs parallelism, the GIL):** async lives in §1's **bottom-left cell** — massive concurrency, *zero* parallelism,
  one thread, one core. The event loop never escapes the GIL (Global Interpreter Lock) because it never needs to: it's the scheduler *for one thread*.
- **The 06-16 Applied session (§1 §9b):** you drove the `asyncio.gather` failure model and landed the keeper *"`return_exceptions`
  handles errors; only a **timeout** handles silence."* §6 here is the mechanism under that keeper — *why* a timeout can break into a
  coroutine that a missing response left hanging forever.

---

## Why this section exists (for *you*)

You ship `asyncio` in production and reason about it fluently at the §1 level — CPU vs I/O, where the GIL is free, the bottom-left cell.
But three things you currently hold as *intuitions* are exactly the ones that produce the subtle async bugs, and they all live one layer
below where §1 stopped:

1. **You picture the event loop as "a thing that runs my coroutines," but not as a concrete loop with a `deque`, a heap, and exactly
   one blocking syscall per tick.** Once you can narrate one tick, every "why didn't this run / why did *that* starve / why is my p99
   spiking" question becomes mechanical instead of mysterious — you already started this in 9b ("a task parked on I/O doesn't hang the
   loop") and this section finishes it.
2. **You use `await`, `gather`, and `create_task` by feel.** This section pins down the *category difference*: `await` runs work
   **inside** the current task (sequential); `create_task`/`gather`/`TaskGroup` **spawn new tasks** (concurrent) — and the three spawners
   differ in exactly one axis that matters in production: **what happens to the siblings when one fails.**
3. **Cancellation is the part nearly everyone — including very good engineers — gets wrong, and it's the direct continuation of your 9b
   timeout insight.** You correctly concluded "only a timeout handles silence." The *why* is that a timeout is not a passive watchdog —
   it reaches **into** your stuck coroutine and *throws an exception at the suspended `await`*. Understanding that one mechanism explains
   why timeouts work, why they sometimes *don't* (a coroutine with no `await` to land on), why `except Exception` is safe but
   `except BaseException` is a bug, and why a `finally` that does cleanup during cancellation is a minefield.

**The one mechanism the whole section turns on.** Hold this and everything below is a corollary. A running coroutine makes progress until
it hits an `await` on something **not yet ready**; at that instant it **suspends** (saves its frame on the heap — Ch1 §2) and **yields
control back to the event loop**. The loop is now free to run other ready work. Later, when the awaited thing becomes ready, the loop
**resumes** the coroutine — and it resumes it in one of exactly two ways: by **sending in a value** (`coro.send(result)` — the normal
case, "your I/O returned this") or by **throwing in an exception** (`coro.throw(exc)` — the cancellation/timeout case, "stop waiting,
here's a `CancelledError` instead"). *Normal completion and cancellation are the same resume machinery with a different payload.* That
symmetry — **resume-with-a-value vs resume-with-an-exception** — is the spine of this section.

---

## 1. The event loop, one tick at a time

<details>
<summary><b>Vocabulary for this section</b> — the loop's three structures and every step of a tick (click to expand)</summary>

**Abbreviations**

| Short | Stands for | Meaning |
|---|---|---|
| **I/O** | input/output | network, disk or database traffic — anything the program waits on rather than computes |
| **FD** | file descriptor | the small integer the kernel uses to name an open socket or file; the selector watches FDs |
| **IOCP** | I/O completion ports | Windows' kernel readiness/completion mechanism, the counterpart of `epoll` and `kqueue` |
| **CPU** | central processing unit | the processor; a loop asleep in the kernel consumes none of it |
| **ms** | millisecond | one thousandth of a second |
| **OS** | operating system | the software that owns the hardware and does the actual waiting for you |

**Terms**

| Term | Definition |
|---|---|
| **Event loop** | the in-process scheduler that repeatedly waits for events and runs the callbacks they unblock |
| **Tick** | one iteration of the loop — compute a timeout, select, schedule ready callbacks, move due timers, drain the run queue |
| **`_run_once`** | CPython's internal method that performs exactly one tick |
| **`_ready`** | the loop's run queue: a `deque` of callbacks that can run right now |
| **`deque`** | double-ended queue — a list you can push and pop efficiently at both ends |
| **Callback** | a plain function the loop will call later; resuming a parked task is one of these |
| **`Handle`** | the loop's wrapper object around a scheduled callback |
| **`_scheduled`** | the loop's timer queue: a min-heap of `TimerHandle`s ordered by when they should fire |
| **Min-heap** | a structure that always gives you the smallest element (here, the earliest deadline) cheaply |
| **`TimerHandle`** | a callback plus the time at which it is due |
| **`call_later` / `call_at`** | schedule a callback after a delay, or at an absolute loop time |
| **`asyncio.sleep`** | suspend a coroutine for a duration by putting a timer in `_scheduled` — it does **not** block the thread |
| **`time.sleep`** | the synchronous sleep: it parks the whole *thread*, so the loop never reaches `select` and nothing else runs |
| **Deadline** | the absolute time at which a timer or timeout is due |
| **Selector** | the object wrapping the kernel's readiness mechanism — `epoll` on Linux, `kqueue` on macOS, IOCP on Windows |
| **`epoll` / `epoll_wait`** | the Linux syscall family for "tell me which of these many FDs are ready"; `epoll_wait` is where the loop sleeps |
| **Syscall** | a call into the kernel; the one blocking call per tick is a syscall |
| **Readiness** | the kernel's report that a socket now has data to read, or room to write |
| **Select timeout** | how long the loop is willing to sleep in the kernel — zero if work is ready, otherwise the time to the nearest timer |
| **Busy-wait** | spinning in a loop checking a condition, burning CPU; what `asyncio.sleep` deliberately is not |
| **Park** | to suspend a coroutine at an `await` so the loop can run something else |
| **Resume** | to continue a parked coroutine from exactly where it suspended |
| **Run queue** | the list of things ready to run — the loop's `_ready`, analogous to an OS scheduler's queue |
| **`ntodo` snapshot** | counting the ready callbacks before draining and running only that many, so callbacks scheduled mid-drain wait for the next tick |
| **Starvation** | a runnable task never getting a turn because others keep monopolizing the scheduler |
| **Fairness** | the guarantee that every ready callback gets its turn within a bounded number of ticks |
| **Cooperative scheduling** | the loop can only switch *between* callbacks, never inside one — so a callback that never yields freezes everything |
| **Preemption** | involuntary interruption by a scheduler; the OS does this to threads, the event loop cannot do it to a coroutine |

</details>

In §1 you said the loop is "the scheduler running inside your own process." True, but vague. Here is what it concretely *is* and what
one iteration (a **tick**) actually does. CPython's loop (`asyncio.base_events.BaseEventLoop`) holds three structures:

- **`_ready`** — a `collections.deque` of **callbacks ready to run right now** (each wrapped in a `Handle`). This is the run queue. A task
  that just became unblocked has its "resume me" callback sitting here.
- **`_scheduled`** — a **min-heap** of `TimerHandle`s ordered by *when* they should fire. Everything time-based lives here: `call_later`,
  `loop.call_at`, **`asyncio.sleep`**, and — the one that matters most for §6 — **every timeout's deadline**.
- **the selector** — `selectors.DefaultSelector`, which is `epoll` on Linux, `kqueue` on macOS, IOCP (I/O completion ports) on Windows. This is the kernel's
  readiness oracle: you register "tell me when *this* socket is readable/writable," and the kernel watches the file descriptors for you.

One tick of `_run_once` is five steps, and the shape of it is the whole story:

<!-- DIAGRAM:START -->
![Diagram 1](diagrams/02-async-deeply-1.svg)

<details>
<summary>Diagram source (Mermaid)</summary>

```mermaid
flowchart TB
    START(["tick begins"]) --> T1{"compute the select timeout"}
    T1 -- "_ready not empty" --> TZERO["timeout = 0<br/>(don't sleep — work is waiting)"]
    T1 -- "_ready empty,<br/>timers pending" --> TNEAR["timeout = time until<br/>the nearest timer fires"]
    T1 -- "_ready empty,<br/>no timers" --> TINF["timeout = None<br/>(sleep until an FD wakes us)"]
    TZERO --> SEL
    TNEAR --> SEL
    TINF --> SEL["event_list = selector.select(timeout)<br/>★ THE one blocking call in the whole loop ★<br/>— sleeps in the kernel (epoll_wait) here"]
    SEL --> IO["for each ready FD:<br/>schedule its callback onto _ready<br/>(I/O completion wakes the parked task)"]
    IO --> TIMERS["move every now-due timer<br/>from _scheduled → _ready<br/>(sleeps elapsed, timeouts fired)"]
    TIMERS --> DRAIN["ntodo = len(_ready)  ← snapshot!<br/>run exactly ntodo callbacks<br/>(work scheduled *now* waits for next tick<br/>→ no starvation)"]
    DRAIN --> START
```

</details>
<!-- DIAGRAM:END -->

Four facts to read off this, because they answer real questions you've hit:

1. **There is exactly one blocking call per tick: `selector.select(timeout)`.** This is the *physical location* of "the loop is waiting on
   I/O." When 999 of your eval tasks are parked on network reads, the loop is sitting inside `epoll_wait` in the kernel, asleep,
   consuming **zero CPU** — and it wakes the instant *any* of those sockets has data. This is why one thread serves thousands of
   connections (§1 bottom-left): waiting is centralised into one kernel sleep, not one-thread-per-wait.
2. **The select timeout is computed from the timers.** If the nearest thing scheduled is an `asyncio.sleep(0.2)` or a timeout deadline
   200 ms out, the loop tells the kernel "wake me in at most 200 ms." So `asyncio.sleep` isn't a busy-wait — it's a timer in `_scheduled`
   that sets the kernel sleep length. (And `time.sleep` is a catastrophe here precisely because it sleeps the *thread*, not via the
   selector — the loop never reaches `select`, so nothing else runs. §1's footgun, now located exactly.)
3. **I/O completion and timer firing both do the same thing: push a callback onto `_ready`.** A socket becoming readable and a timeout
   deadline arriving are, to the loop, identical events — "schedule this resume." That unification is why a timeout can compete fairly
   with I/O: both are just entries in the run queue.
4. **The `ntodo` snapshot is a fairness guarantee.** The drain step records how many callbacks are ready *at the start* of the drain and
   runs only that many. Callbacks scheduled *during* the drain wait for the next tick. Without this, a task that re-schedules itself every
   time it runs could starve everything else forever. (This is the asyncio analog of the run-queue fairness an OS scheduler enforces —
   Ch1 §3's preemption, except here it's *cooperative*, so the loop can only be fair *between* callbacks, never *within* one. Which is the
   whole reason a single un-yielding callback freezes everyone — §6, §7.)

> **The keeper for §1:** "the loop waits on I/O" is literally "the loop is asleep inside `epoll_wait`, woken by the kernel when an FD (file descriptor) is
> ready or the nearest timer is due." Concurrency without parallelism is *one thread alternating between sleeping in the kernel and
> draining a run queue.* There is no magic — there is a `deque`, a heap, and one syscall.

---

## 2. Coroutine vs Future vs Task — the three things people call "a coroutine"

<details>
<summary><b>Vocabulary for this section</b> — the three objects and the await/park/wake cycle (click to expand)</summary>

**Abbreviations**

| Short | Stands for | Meaning |
|---|---|---|
| **I/O** | input/output | network, disk or database traffic — the thing an `await` usually waits on |

**Terms**

| Term | Definition |
|---|---|
| **Coroutine** | the object you get by *calling* an `async def` function: a paused frame, inert until awaited or wrapped in a Task |
| **`async def`** | the syntax that defines a coroutine function; calling it builds a coroutine object instead of running the body |
| **Frame** | the per-call state of a function (its locals and its position in the code); a coroutine's frame lives on the heap so it can be paused |
| **Inert** | does nothing on its own — a recipe, not a running job |
| **Single-use** | a coroutine object can be awaited exactly once; a Task, being a handle, can be inspected and awaited repeatedly |
| **Future** | a low-level "result box": a state plus a result-or-exception plus a list of done-callbacks fired on resolution |
| **`PENDING` / `FINISHED` / `CANCELLED`** | the three Future states — not done yet, done with a result or exception, and cancelled |
| **Done-callback** | a function registered to run when a Future resolves; how a parked Task gets woken |
| **`add_done_callback`** | the method that registers one |
| **Task** | a Future subclass that also *drives* a coroutine; creating one schedules it on the loop immediately |
| **`asyncio.create_task`** | the modern way to make a Task from a coroutine and start it running |
| **`ensure_future`** | the older, more permissive wrapper that returns a Task for a coroutine or passes a Future through |
| **`loop.create_future()`** | how library code makes a bare Future |
| **`Task.__step`** | the internal driver that resumes the coroutine once and re-parks it |
| **`coro.send(value)`** | resume the coroutine, delivering `value` as the result of the `await` it was parked on |
| **`coro.throw(exc)`** | resume the coroutine by raising `exc` at that same `await` — the mirror image, used for cancellation |
| **`await`** | suspend here until the awaited thing resolves; the only point at which the loop can switch |
| **Park / wake** | suspend at an `await`, then be rescheduled when the awaited Future resolves |
| **`set_result`** | what the I/O machinery calls on a Future when the answer arrives, which resolves it and schedules its done-callbacks |
| **Transport** | asyncio's low-level connection object that moves bytes and resolves the Futures your coroutine is waiting on |
| **Synchronization primitive** | a building block for coordinating flows; the Future is the one everything else here is built from |
| **Chaining frames** | `await coro` runs the inner coroutine *inside the current Task*, so the two never overlap — concurrency needs more Tasks |
| **`asyncio.gather`** | run several awaitables concurrently and collect their results |
| **`TaskGroup`** | the 3.11+ scoped way to spawn several tasks that must all finish before the block exits |
| **"coroutine was never awaited"** | the warning you get for building a coroutine object and discarding it without running it |

</details>

You used these words interchangeably in 9b and mostly got away with it. They are three distinct objects, and the distinction is the
difference between *code that does nothing* and *code that's actually running*.

**Table 1** — coroutine against future against task — the three objects people conflate.

| | **Coroutine** | **Future** | **Task** |
|---|---|---|---|
| **What it is** | the object returned by calling an `async def` fn | a low-level "result box" with a state + done-callbacks | a `Future` subclass that **wraps and drives** a coroutine |
| **Created by** | calling `foo()` where `foo` is `async def` | libraries, rarely you (`loop.create_future()`) | `asyncio.create_task(coro)` / `ensure_future` |
| **Does it run on its own?** | **No** — inert until awaited or wrapped | N/A — it's a value holder, not code | **Yes** — scheduled on the loop the moment it's created |
| **Single-use?** | **Yes** — one frame, one `await` consumes it | — | reusable as a handle (await it, cancel it, query it) |
| **Mental model** | a *recipe* | a *mailbox* (will hold a result later) | a *running job* + the mailbox for its result |

The load-bearing facts:

- **A coroutine object is inert.** `foo()` for `async def foo` runs *nothing* — it builds a coroutine object (a paused frame) and hands it
  to you. This is why `foo()` without `await` is the classic "coroutine was never awaited" warning: you made the recipe and threw it away.
  (Contrast a normal function: `bar()` runs `bar`. `foo()` for a coroutine does *not* run `foo`.)
- **A Future is a result that isn't here yet** — `PENDING` → `FINISHED` (has a result or an exception) or `CANCELLED`, plus a list of
  done-callbacks to fire on resolution. You rarely make one; the machinery does (a network transport sets a Future's result when bytes
  arrive). It's the synchronisation primitive the whole system is built from.
- **A Task is the only one of the three that *runs your coroutine*.** A Task is a Future (so it *has* a result, you can `await` it, cancel
  it, ask if it's done) **plus** a driver loop that pumps the coroutine. Creating a Task **schedules it immediately** — it's the act of
  saying "loop, please start making this coroutine make progress."

**How a Task drives a coroutine — the await→park→wake cycle, mechanically.** This is the Ch1 §2 "swap" made concrete, and it's worth
seeing once at the `send`/`throw` level because §6 (cancellation) is just this picture with a different arrow:

<!-- DIAGRAM:START -->
![Diagram 2](diagrams/02-async-deeply-2.svg)

<details>
<summary>Diagram source (Mermaid)</summary>

```mermaid
sequenceDiagram
    participant L as Event loop
    participant T as Task.__step
    participant C as coroutine frame
    participant F as Future (awaited thing)
    L->>T: run the Task's step callback
    T->>C: coro.send(None)  (resume / start)
    C->>C: run until the next `await` on a PENDING future
    C-->>T: yield that Future
    T->>F: future.add_done_callback(Task.__wakeup)
    Note over T,L: Task parks. Control returns to the loop.<br/>The loop runs OTHER ready callbacks.
    Note over F: ...later: I/O completes (or timer fires).<br/>Something calls future.set_result(x).
    F->>L: schedule the done-callbacks onto _ready
    L->>T: Task.__wakeup runs (next tick)
    T->>C: coro.send(x)   ← resume WITH THE VALUE
    Note over C: coroutine continues right after the `await`,<br/>as if the call had just returned x
```

</details>
<!-- DIAGRAM:END -->

The single most useful thing to extract: **`await coro` does *not* create a Task.** It runs the awaited coroutine *inside the current
Task*, chaining frames — the current task simply doesn't proceed past the `await` until the inner thing is done. So two `await`s in a row
run **sequentially in one task**. To get *concurrency* you must create *more tasks* (`create_task`/`gather`/`TaskGroup`), which give the
loop more independently-resumable jobs to interleave. This is the precise, mechanical statement of your Ch1 §2 realisation — and it's the
#1 async performance bug in the wild: people `await` a list of coroutines in a loop and wonder why it's serial.

```python
# SERIAL — one task, two awaits back to back. Total ≈ a + b.
x = await fetch(url_a)
y = await fetch(url_b)

# CONCURRENT — two tasks, the loop interleaves them. Total ≈ max(a, b).
x, y = await asyncio.gather(fetch(url_a), fetch(url_b))
```

---

## 3. The spawning primitives — `gather`, `as_completed`, `wait`, `TaskGroup`

<details>
<summary><b>Vocabulary for this section</b> — the spawn/collect primitives and their error policies (click to expand)</summary>

**Terms**

| Term | Definition |
|---|---|
| **Awaitable** | anything you can `await` — a coroutine, a Future or a Task |
| **`await coro`** | run the awaited thing inside the current task; nothing else of yours overlaps with it |
| **`create_task(coro)`** | schedule a coroutine as an independent Task right now and hand you the handle |
| **`gather(*aws)`** | run several awaitables concurrently and return their results in **input** order |
| **`return_exceptions=True`** | `gather`'s harvest mode: a child's exception comes back as an object in the result list instead of propagating, and the batch always completes |
| **`as_completed(aws)`** | yields the awaitables in **completion** order, so you can persist each result the moment it lands |
| **`wait(aws, return_when=…)`** | the low-level primitive: returns `(done, pending)` sets and never raises — you decide what to do with the stragglers |
| **`TaskGroup()`** | the 3.11+ scoped spawner: `async with` block, cancels siblings on a failure, raises an `ExceptionGroup` |
| **`ExceptionGroup`** | a single exception carrying several underlying exceptions at once |
| **Propagate** | for an exception to travel outward to the caller rather than being stored or ignored |
| **Sibling** | another task spawned by the same call; the key question is whether a failure cancels them |
| **Orphan** | a task nobody is waiting on any more — still running, still consuming connections and quota, its result discarded |
| **Fail-fast** | stop the whole batch as soon as one part fails |
| **Harvest mode** | the opposite policy: let everything finish and sort successes from failures afterwards |
| **Fan-out** | issuing many concurrent operations from one place |
| **Rate-limit budget** | the allowance of requests per interval a remote API grants you; orphans keep spending it |
| **Straggler** | the one slow or hung item holding up a collection point |
| **Join barrier** | a single point that waits for *all* children — `gather`'s shape, and why one straggler withholds every finished result |
| **Index-aligned** | position `i` of the result list corresponds to input `i`, so failures can be mapped back to their inputs |
| **Eval harvest** | the pipeline pattern of running many independent evaluations and keeping every outcome, success or failure |

</details>

Once you accept "concurrency needs more than one task," the question is *how you spawn and collect them*, and asyncio gives you several
tools that look interchangeable but differ on the axes that bite in production: **ordering, error policy, and what happens to siblings
when one fails.**

**Table 2** — the spawning primitives: what each returns, its ordering, and its error behaviour.

| Primitive | Returns | Result order | On a child error | Siblings on error | Use it when |
|---|---|---|---|---|---|
| `await coro` | the value | — | propagates | — (no siblings) | the next step *depends on* this result |
| `create_task(coro)` | a `Task` (now) | — | stored on the Task until awaited | independent | fire-and-(carefully)-forget; you hold the handle |
| `gather(*aws)` | list, **input order** | input order | **first exception propagates to caller** | **keep running, orphaned** ⚠ | you want all results, order matters, all-or-nothing-ish |
| `gather(..., return_exceptions=True)` | list incl. exception objects | input order | captured as a result | all run to completion | **eval-harvest** — collect everything, inspect failures after (your 9b) |
| `as_completed(aws)` | iterator of futures | **completion order** | raised when you `await` that one | independent | stream/persist results as they finish (your 9b "don't lose 997") |
| `wait(aws, return_when=…)` | `(done, pending)` sets | — | **never raises** — you inspect | your choice (you cancel `pending`) | low-level control; "first to finish wins" races |
| `TaskGroup()` (3.11+) | — (`async with`) | — | **cancels all siblings**, raises `ExceptionGroup` | **cancelled** | all tasks must succeed together; fail-fast |

Three traps hide in that table:

- **`gather`'s default error policy is the surprising one.** When one child raises, `gather` propagates that exception to your `await`
  *immediately* — but it does **not cancel the other children**. They keep running as orphans, consuming connections and rate-limit
  budget, their results (or further exceptions) silently dropped. For a fan-out where a failure should stop the work, `gather` leaks; for
  an eval where you want *every* result regardless, you need `return_exceptions=True`. Neither default is "cancel siblings cleanly" —
  that's what `TaskGroup` added.
- **`return_exceptions=True` turns `gather` into "harvest mode"** — exactly the 9b policy. Every coroutine that raises comes back as an
  *exception object in the result list, index-aligned*, and the batch always completes. You then filter results from failures yourself.
  This is the right tool for an eval pass; `TaskGroup` (fail-fast) is the *wrong* one there.
- **`as_completed` is how you stop a straggler from holding 999 finished results hostage** (the 9b "join barrier" problem). Instead of one
  collection point that waits for *all* (`gather`), you consume results *as each finishes* and persist immediately — so a crash or a hang
  at item 998 costs you nothing already harvested.

---

## 4. Structured concurrency — why `TaskGroup` exists

<details>
<summary><b>Vocabulary for this section</b> — nurseries, scopes, and aggregated errors (click to expand)</summary>

**Abbreviations**

| Short | Stands for | Meaning |
|---|---|---|
| **PEP** | Python enhancement proposal | the numbered design documents; PEP 654 added `ExceptionGroup` and `except*` |
| **GC** | garbage collection | automatic reclamation of unreachable objects — when an abandoned Task is collected is when its lost exception is finally logged |

**Terms**

| Term | Definition |
|---|---|
| **Structured concurrency** | the discipline that every spawned task lives inside a lexical block which cannot exit until all its children finish |
| **`TaskGroup`** | asyncio's 3.11+ implementation of that discipline, used as an `async with` block |
| **Nursery** | Trio's name for the same scope — the vocabulary the idea was first published in |
| **Trio** | the third-party async library where structured concurrency was worked out before asyncio adopted it |
| **`create_task`** | the unstructured spawn: the task's lifetime is unbounded and its errors have nowhere to go |
| **Lifetime (of a task)** | how long it may keep running; unstructured tasks can outlive the function that spawned them |
| **Lexical scope** | the block of source text something belongs to — here, the hard boundary a child task cannot escape |
| **`async with`** | the asynchronous context manager syntax; its exit is where `TaskGroup` waits for children |
| **Call graph** | which function calls which; `goto`-like spawning breaks the guarantee that a call returns to its caller |
| **`go` statement / `goto`** | the analogy: a jump that abandons the caller-returns-to-caller discipline, which is why unowned background tasks are hard to reason about |
| **Swallowed exception** | one that is raised, stored on an un-awaited Task, and never surfaced — visible only as a late "Task exception was never retrieved" log line |
| **`ExceptionGroup` (PEP 654)** | the container that lets more than one simultaneous failure be reported without losing any |
| **`except*`** | the syntax for handling one exception type across every member of an `ExceptionGroup` |
| **Fail-fast** | cancel the remaining children as soon as one fails — `TaskGroup`'s policy, and the wrong one for a harvest |
| **Cancellation** | asking a task to stop by raising `CancelledError` in it at its next `await` (the mechanism is §5) |

</details>

`create_task` has a quiet design flaw that the industry took ~a decade to name. When you write `asyncio.create_task(work())` and move on,
you've created a job whose **lifetime is unbounded** (it can outlive the function that spawned it) and whose **errors have nowhere to go**
(if `work()` raises and nobody ever `await`s the task, the exception is *swallowed* — surfaced only as a "Task exception was never
retrieved" log line when the task is eventually garbage-collected, if you're watching logs at all). Nathaniel Smith's essay *"Notes on
structured concurrency, or: `go` statement considered harmful"* (the Trio project) made the analogy precise: **an unowned background task
is a `goto` across the call graph** — it breaks the discipline that makes ordinary code tractable, namely that a function call *returns to
its caller* and *propagates its errors upward*.

**Structured concurrency** restores that discipline. The rule: **every spawned task lives inside a lexical scope, and the scope does not
exit until all its children finish.** Tasks cannot outlive the block that created them; an error in any child propagates to the parent
block like a normal exception. Trio called the scope a *nursery*; asyncio adopted it in 3.11 as **`TaskGroup`**:

```python
# Unstructured (the "go statement"): lifetimes unbounded, errors can vanish.
t1 = asyncio.create_task(fetch(a))
t2 = asyncio.create_task(fetch(b))
# ... if fetch(b) raises and we never await t2, the error is swallowed.

# Structured: the `async with` block is a hard boundary.
async with asyncio.TaskGroup() as tg:
    tg.create_task(fetch(a))
    tg.create_task(fetch(b))
# Control does NOT pass this line until BOTH finish.
# If either raises: the other is CANCELLED, and an ExceptionGroup is raised here.
```

Two consequences worth holding:

- **Errors aggregate into an `ExceptionGroup` (PEP 654), caught with `except*`.** If two children fail, you don't lose one — `TaskGroup`
  raises an `ExceptionGroup` containing *both*, and the new `except* ValueError:` syntax lets you handle each type across the group. This
  is why `ExceptionGroup` was added to the language in 3.11: structured concurrency *needs* "more than one thing failed at once" to be a
  first-class idea.
- **`TaskGroup` is fail-fast by design**, which makes it the *wrong* tool for your eval harvest (9b) and the *right* tool for "fetch the
  user, their org, and their permissions — if any of the three fails the whole request is meaningless, cancel the rest." Match the policy
  to the job: **all-must-succeed → `TaskGroup`; collect-everything → `gather(return_exceptions=True)` or `as_completed`.**

---

## 5. Cancellation — the part everyone gets wrong (and the cash-in of 9b)

<details>
<summary><b>Vocabulary for this section</b> — cancellation, timeouts, and the re-raise rule (click to expand)</summary>

**Abbreviations**

| Short | Stands for | Meaning |
|---|---|---|
| **I/O** | input/output | network, disk or database traffic — what a parked-forever coroutine is usually waiting on |
| **CPU** | central processing unit | the processor; CPU-bound code never yields, so cancellation cannot reach it |

**Terms**

| Term | Definition |
|---|---|
| **Cancellation** | asking a task to stop by *injecting an exception* into it — it does not kill a thread or interrupt a running line |
| **`task.cancel()`** | sets the cancel flag so the task is next resumed with an exception instead of a value |
| **`CancelledError`** | the exception that is thrown in; it inherits from `BaseException`, **not** `Exception` |
| **`BaseException` vs `Exception`** | `except Exception:` deliberately does not catch `CancelledError`, so ordinary error handling cannot silently eat a shutdown |
| **`coro.throw(CancelledError)`** | the actual delivery: the exception is raised *at* the `await` where the coroutine is suspended |
| **Suspension point / await point** | a place where the coroutine can be paused and resumed — the only place an injected exception can land |
| **Parked** | suspended at an `await` and therefore cancellable; a coroutine spinning in Python or stuck in a blocking C call is not |
| **Unwind** | the exception travelling outward through the coroutine's frames, running `try/finally` blocks on the way |
| **`try/finally`** | cleanup that runs even when the exception is a cancellation — how locks and connections get released |
| **Re-raise** | the mandatory `raise` after catching `CancelledError`; without it the task swallows its own cancellation and shutdown hangs |
| **`asyncio.timeout()`** | the 3.11+ context manager that schedules a deadline, cancels the work inside on expiry, and converts the `CancelledError` into `TimeoutError`; it nests correctly |
| **`asyncio.wait_for()`** | the older wrapper doing the same job around a single awaitable |
| **`TimeoutError`** | what a timeout re-raises at its block boundary, so callers see a timeout rather than a cancellation |
| **Watchdog** | a passive observer that checks a clock; a timeout is explicitly *not* this — it actively reaches in and throws |
| **Timer / `_scheduled`** | the loop's deadline queue; a timeout is an entry in it and fires as an ordinary tick event |
| **`asyncio.shield()`** | protects an inner awaitable from an outer cancellation — the outer `await` still raises, and the shielded work continues detached |
| **Detached** | still running with nobody awaiting it |
| **`Task.uncancel()`** | decrements the 3.11+ cancellation counter, which is what lets nested timeouts tell each other's cancellations apart |
| **Cancellation count** | the per-task tally of pending cancellations that makes nested `asyncio.timeout()` blocks correct |
| **`return_exceptions=True`** | `gather`'s harvest flag; it can only capture an exception the coroutine raises itself, so it is powerless against silence |
| **Silence** | a response that simply never arrives — nothing raises, so only an externally injected cancellation can end the wait |
| **Blocking the loop** | running without yielding, so no `await` is ever reached — the same root cause as uncancellable code |

</details>

This is the section. Your 06-16 keeper was *"only a timeout handles silence."* Correct — and the mechanism behind it is the single most
misunderstood thing in asyncio. Get this and you can reason about every timeout, shutdown, and "task won't die" bug you'll ever hit.

**Cancellation is an exception injected into a parked coroutine — nothing more.** `task.cancel()` does **not** kill the task, stop a
thread, or interrupt a running line of code. It sets a flag so that the **next time the coroutine resumes from an `await`**, the loop
resumes it not with `coro.send(value)` but with **`coro.throw(CancelledError)`** — i.e. it *raises `CancelledError` at the exact `await`
where the coroutine is suspended.* From the coroutine's point of view, the `await` it was sitting on "returns" by raising. This is the
same resume machinery as §2's wake cycle, with the exception arrow instead of the value arrow:

<!-- DIAGRAM:START -->
![Diagram 3](diagrams/02-async-deeply-3.svg)

<details>
<summary>Diagram source (Mermaid)</summary>

```mermaid
sequenceDiagram
    participant Timer as Timeout timer (in _scheduled)
    participant L as Event loop
    participant T as Task
    participant C as coroutine (parked at `await resp`)
    Note over C: stuck — the response never comes,<br/>so `resp` future stays PENDING forever
    Note over Timer: deadline arrives → timer fires (a normal tick event)
    Timer->>L: scheduled callback runs
    L->>T: task.cancel()  (sets the cancel flag)
    L->>T: Task.__step resumes the task
    T->>C: coro.throw(CancelledError)  ← resume WITH AN EXCEPTION
    Note over C: CancelledError raised AT the `await resp`.<br/>`try/finally` cleanup runs as it unwinds.
    C-->>T: CancelledError propagates out
    Note over T,L: asyncio.timeout() catches it at the block<br/>boundary → converts to TimeoutError
```

</details>
<!-- DIAGRAM:END -->

Now every property of cancellation falls out of "it's an injected exception":

- **Cancellation only lands at an `await`.** The exception is delivered *when the coroutine next resumes*. A coroutine spinning in a tight
  pure-Python loop, or stuck in a blocking C call, **never resumes** (it never yielded), so the `CancelledError` is queued but *cannot be
  delivered* — `task.cancel()` appears to do nothing until the code reaches a suspension point. **This is the same root cause as "blocking
  the loop" (§1, §7): no `await`, no yield, no cooperation, no cancellation.** A timeout on a CPU-bound coroutine is a timeout that never
  fires in time.
- **This is *why* a timeout breaks the 9b "silence" hang but `return_exceptions` can't.** When a response never comes, the coroutine is
  *parked at an `await`* (the well-behaved case from 9b — the loop is fine, only this one task is stuck). A timer in `_scheduled` is still
  scheduled; when its deadline arrives the loop fires it (§1 — timers compete fairly with I/O), it calls `task.cancel()`, and because the
  task **is** parked at an `await`, the `CancelledError` lands cleanly and unwinds the wait. `return_exceptions=True` can only catch an
  exception the coroutine *raises on its own*; silence raises nothing, so only an *externally injected* exception — a cancellation from a
  timeout — can end it. That's the mechanism your keeper was standing on.
- **`asyncio.timeout()` and `asyncio.wait_for()` are *built on* cancellation.** They schedule a timer; on expiry they `cancel()` the task
  running inside the block; they catch the resulting `CancelledError` at the boundary and re-raise it as `TimeoutError`. A timeout is not
  a passive watchdog that checks a clock — it is an active *"reach in and throw."* (3.11's `asyncio.timeout()` context manager is the
  modern form; `wait_for` is the older wrapper. Prefer `timeout` — it composes and nests correctly.)

**The rule that makes cancellation safe — and the bug that makes it the worst kind of unsafe:**

- **`CancelledError` inherits from `BaseException`, not `Exception`** (since Python 3.8 — deliberately). So a blanket `except Exception:`
  — your normal "catch errors, log, continue" — **does not** catch cancellation, which is correct: your error handling shouldn't
  accidentally suppress a shutdown. Good.
- **But if you *do* catch it** — in a `try/except CancelledError:` or a bare `except:` or `except BaseException:` for cleanup — **you must
  re-raise it.** Catch-and-don't-re-raise means the task *swallows its own cancellation*: the timeout fired, the exception was thrown in,
  and your code ate it and kept running. Now `asyncio.timeout` thinks it cancelled the task but the task is still going; shutdown hangs;
  "this task won't die" tickets get filed. The idiom:

  ```python
  try:
      await do_work()
  except asyncio.CancelledError:
      await cleanup()          # fine to clean up...
      raise                    # ...but you MUST re-raise, or cancellation is broken
  ```

- **`try/finally` runs during cancellation** — that's how you release locks/connections on the way out. But **awaiting inside a `finally`
  during cancellation is a minefield**: that `await` is *itself* a suspension point, so it can be cancelled too (a second timeout, a
  shutdown), cutting your cleanup short. For cleanup that absolutely must complete, wrap it in `asyncio.shield()` (which protects an inner
  awaitable from cancellation propagating in) — but know that `shield` only protects the *inner* task; the outer `await` still raises, and
  the shielded work keeps running detached. (3.11 added `Task.uncancel()` and a cancellation *count* so that nested timeouts don't confuse
  each other — an inner timeout firing no longer looks like the outer one to the outer block. You rarely call `uncancel` yourself; it's
  what makes nested `asyncio.timeout()` blocks correct.)

> **The keeper (the spine of the section, stated for cancellation):** *normal completion resumes a coroutine with a value; cancellation
> resumes it with an exception.* Both need the coroutine to be **parked at an `await`** to take effect — which is why cancellation and
> timeouts are powerless against un-yielding code, exactly as throughput is (the §1 footgun, now seen from the other side). Catch
> `CancelledError` only to clean up, and **always re-raise**, or you turn a cooperative shutdown into a hang.

---

## 6. The footgun gallery — real failure modes, ranked

<details>
<summary><b>Vocabulary for this section</b> — each failure mode's machinery in one place (click to expand)</summary>

**Abbreviations**

| Short | Stands for | Meaning |
|---|---|---|
| **GC** | garbage collection | automatic reclamation of unreachable objects; it is what destroys an unreferenced pending Task and what finally logs a lost exception |
| **DB** | database | a data store reached over a connection; a synchronous driver blocks the calling thread |
| **p99** | 99th-percentile latency | the response time 99% of requests beat — the first metric a stalled loop wrecks |
| **CPU** | central processing unit | the processor; CPU-heavy steps belong off the loop |
| **I/O** | input/output | network, disk or database traffic |

**Terms**

| Term | Definition |
|---|---|
| **Fire-and-forget** | spawning a task and not keeping the handle — the shape behind failure modes 1 and 5 |
| **Weak reference** | a reference that does not keep an object alive; the loop holds only these to tasks, which is why you must hold a strong one |
| **Strong reference** | an ordinary reference that keeps the object alive |
| **`add_done_callback`** | used here to drop the strong reference once the task completes, so the set does not grow forever |
| **"Task was destroyed but it is pending!"** | the warning for a task collected mid-flight — the work silently never finished |
| **"Task exception was never retrieved"** | the late log line for an exception stored on a task nobody awaited |
| **Orphan / sibling** | a task still running after the call that spawned it has given up on it; `gather` leaves siblings running on the first error |
| **`gather` / `return_exceptions=True` / `TaskGroup`** | the three error policies: propagate-but-leak, capture-everything, and cancel-siblings |
| **`CancelledError`** | the exception cancellation injects; catching it without re-raising breaks timeouts and shutdown |
| **Bare `except:` / `except BaseException:`** | over-broad handlers that do catch `CancelledError`, which is how it gets swallowed |
| **Blocking the loop** | a call that never yields — a sync DB driver, `requests`, `time.sleep`, a heavy pure-Python parse, a `boto3` call — so `selector.select` is never reached and every task starves |
| **`selector.select`** | the loop's single blocking call per tick; not reaching it is the precise definition of blocking the loop |
| **`requests` / `boto3`** | popular synchronous libraries; they must not be called directly from a coroutine |
| **`httpx` / `aiohttp`** | async-native HTTP clients that cooperate with the loop |
| **`loop.run_in_executor`** | hand a blocking or CPU-heavy function to a thread or process pool so the loop stays free |
| **Process pool** | worker processes with their own interpreters — the right home for CPU-bound Python work |
| **`asyncio.run()`** | creates a fresh loop, runs a coroutine to completion, then closes the loop — it cannot be called from inside a running loop |
| **`RuntimeError`** | what you get for that nesting mistake |
| **Jupyter** | the notebook environment, which already runs a loop — so top-level `await` works there but `asyncio.run` does not |
| **`nest_asyncio`** | the shim that patches the loop to allow re-entrant `asyncio.run` in environments like Jupyter |
| **One loop per thread** | the invariant behind all of the above: a thread runs at most one event loop at a time |
| **Structured concurrency** | scoping tasks to a block so their errors cannot vanish — the root fix for modes 1, 2 and 5 |

</details>

Canonical async bugs, each one a corollary of §1–§5. The first three are the ones that bite even experienced people.

1. **Fire-and-forget tasks get garbage-collected mid-flight.** `asyncio.create_task(bg_work())` *without keeping a reference* is a live
   bug: **the event loop holds only a *weak* reference to tasks**, so if you don't keep a strong one, the garbage collector can destroy
   the task while it's still pending — `Task was destroyed but it is pending!` and the work silently never finishes. The documented idiom
   is to stash a strong ref and clear it on completion:
   ```python
   _background = set()
   def spawn(coro):
       t = asyncio.create_task(coro)
       _background.add(t)
       t.add_done_callback(_background.discard)   # keep a strong ref until it's done
   ```
2. **`gather` leaves siblings running on the first error (§3).** The exception reaches you, but the other coroutines keep consuming
   connections/budget as orphans. If a failure should stop the fan-out, use `TaskGroup` (cancels siblings); if it shouldn't, use
   `return_exceptions=True` (everyone finishes). The default is neither.
3. **Swallowing `CancelledError` (§5).** Catching it (often via an over-broad `except BaseException` or a bare `except:`) and not
   re-raising breaks cancellation and timeouts. Symptom: shutdown hangs, `asyncio.timeout` doesn't actually stop the work.
4. **Blocking the loop (§1, located in §1's tick).** A sync DB (database) driver, `requests`, `time.sleep`, a heavy pure-Python parse, or a blocking
   `boto3` call sitting directly in a coroutine **never reaches `selector.select`** — so *every* other task starves until it returns,
   spiking p99 for all users (your 9b Hang #2). Fix: an async client (`httpx`/`aiohttp`/an async DB driver), `asyncio.sleep` not
   `time.sleep`, or push the CPU step to `loop.run_in_executor(process_pool, …)` (§1 §4 hybrid).
5. **Unretrieved task exceptions.** A backgrounded task that raises, with no one to `await` its result, logs *"Task exception was never
   retrieved"* only when it's GC (garbage collection)'d — easy to miss entirely. Structured concurrency (`TaskGroup`) fixes this at the root: errors propagate
   to the block.
6. **`asyncio.run()` nesting / multiple loops.** `asyncio.run` creates *and closes* a fresh loop; you cannot call it from inside a running
   loop (`RuntimeError: asyncio.run() cannot be called from a running event loop`). Notably **Jupyter already runs a loop**, so `await` works
   at top level there but `asyncio.run(...)` does not — the `nest_asyncio` shim exists for exactly this. One loop per thread.

---

## 7. Where this bites *you* — the practitioner's playbook

<details>
<summary><b>Vocabulary for this section</b> — the harness recipe and the audit checklist (click to expand)</summary>

**Abbreviations**

| Short | Stands for | Meaning |
|---|---|---|
| **GC** | garbage collection | automatic reclamation of unreachable objects; it is what makes a dropped task handle vanish mid-flight |
| **p99** | 99th-percentile latency | the response time 99% of requests beat |
| **CPU** | central processing unit | the processor; CPU-heavy steps must leave the event loop |

**Terms**

| Term | Definition |
|---|---|
| **`Semaphore`** | a counting permit holder: at most N coroutines inside the guarded region at once — how you cap concurrency to a rate limit |
| **Rate limit** | the cap a remote API puts on requests per interval |
| **`asyncio.timeout`** | per-request deadline; the only construct that can end a coroutine parked forever on silence |
| **`gather(return_exceptions=True)`** | capture every child's outcome, exceptions included, instead of propagating the first one |
| **`as_completed`** | consume results in completion order so a hang late in the batch does not withhold what already finished |
| **Persist** | write each result out as it arrives, rather than at one collection point at the end |
| **Idempotent retry** | re-running a failed item safely, because doing it twice has the same effect as doing it once |
| **`TaskGroup`** | scoped spawning with fail-fast cancellation — right for "all must succeed", wrong for a harvest |
| **Fail-fast** | cancel the rest as soon as one fails |
| **`create_task`** | unstructured spawn; dropping its handle risks the task being garbage-collected while pending |
| **Blocking call** | a call that never yields to the loop, stalling every other task and spiking p99 |
| **Executor** | a thread or process pool that runs blocking or CPU-bound work off the loop |
| **`CancelledError`** | the cancellation exception; catching it without `raise` turns a cooperative shutdown into a hang |
| **Serial `await`s** | awaiting items one after another in a loop — correct but with no concurrency at all |
| **Straggler / upstream** | the slow item, and the remote service behind it; a dead upstream parks a task indefinitely without a timeout |
| **`loop.set_debug(True)` / `PYTHONASYNCIODEBUG=1`** | asyncio's debug mode, which warns on slow callbacks, un-awaited coroutines and tasks destroyed while pending |
| **Slow callback** | a single callback that held the loop too long — debug mode's name for blocking the loop |

</details>

Ranked, concrete, mapped to the sections — and aimed at the eval pipeline and the arena from §1's session.

1. **For the eval harness, the shape is now fully specified (§3, §5).** `Semaphore` (rate limit, 9a) + **per-request `asyncio.timeout`**
   (the only thing that ends silence, §5) + **capture-don't-propagate** (`gather(return_exceptions=True)` or `as_completed`, §3) +
   **persist via `as_completed`** so a hang at item 998 doesn't cost the first 997 + idempotent retry on failed indices. Do **not** use
   `TaskGroup` here — its fail-fast cancellation is the opposite of harvest.
2. **For the arena, audit for the three structural bugs (§5, §6).** (a) Any `create_task` whose handle you drop → potential GC-vanish; add
   the set+discard idiom. (b) Any blocking call on the loop → p99 killer; move to async client or executor. (c) Any
   `except CancelledError` / broad `except` without a `raise` → shutdown/timeout hang.
3. **Reach for `TaskGroup` as the default for "do N things, all must succeed" (§4).** It cancels stragglers on failure, aggregates errors,
   and bounds task lifetime to the block — three bugs designed out at once. Drop to raw `gather`/`create_task` only when you specifically
   need the unstructured behaviour (harvest mode, or a genuinely long-lived background task you own explicitly).
4. **Never `await` a network call without a timeout (§5).** This is the 9b keeper as a hard rule. A timeout is the only construct that can
   reach into a parked-forever coroutine and end it; without one, a single dead upstream connection parks a task for the lifetime of the
   process.
5. **When debugging "why is async slow / not concurrent," check for serial `await`s first (§2).** A loop of `await foo()` is sequential;
   the fix is `gather`/`TaskGroup`/`as_completed`. This is the most common async non-bug-bug — code that's *correct* but accidentally
   serial.
6. **Turn on `loop.set_debug(True)` / `PYTHONASYNCIODEBUG=1` in dev (§1, §6).** It warns on slow callbacks (a callback blocking the loop
   too long — your footgun #4 made visible), coroutines never awaited, and tasks destroyed while pending. Cheap early warning for exactly
   the bugs above.

---

## 8. Check your understanding

Jot a one-line answer to each before our Q&A — and where I ask for a hypothesis, *commit to one*; we'll re-rank it against the dominant
mechanism together (your signature mode).

1. Narrate **one tick** of the event loop in order, and answer: where, physically, is "the loop waiting on I/O"? What sets how long that
   wait lasts? Why does `time.sleep(1)` inside a coroutine break the whole loop, but `await asyncio.sleep(1)` doesn't?
2. Define **coroutine**, **Future**, and **Task** in one sentence each. Then: why does calling `foo()` (an `async def`) run *none* of
   `foo`'s body? And why do two `await`s in a row run *sequentially* even though async is "concurrent"?
3. You have 200 coroutines. Give the right collection primitive and justify it for: (a) you need every result and want failures reported
   per-item, not a crash; (b) all 200 must succeed or the whole job is meaningless; (c) you want to persist each result the instant it
   finishes so a late crash loses nothing. Name what `gather` (default) does to the *other 199* when #50 raises.
4. **(The core one.)** Explain what `task.cancel()` actually does — at the level of `send`/`throw`. Then explain *why* a timeout can end a
   coroutine that's hung waiting for a response that never comes, but `return_exceptions=True` cannot. Use the word "parked."
5. A coroutine is stuck in `while True: x += 1` (no `await`). You wrap it in `asyncio.timeout(5)`. Predict what happens at t=5s and explain
   the mechanism. (Hypothesis: does the timeout fire? does the task stop? when?)
6. A teammate writes `try: await work() except Exception: log(); return`. They say "this is safe, it won't swallow cancellation." Are they
   right? Now they change it to `except BaseException:`. What breaks, and what's the symptom in production?
7. (Synthesis) Why was `ExceptionGroup` / `except*` added to the language *at the same time* as `TaskGroup`? What problem in structured
   concurrency requires "more than one error at once" to be a first-class concept?

<details>
<summary>Answers</summary>

1. **One tick: (1) compute the select timeout, (2) `selector.select(timeout)`, (3) push a callback onto `_ready` for every ready file
   descriptor, (4) move every now-due timer from `_scheduled` into `_ready`, (5) snapshot `ntodo = len(_ready)` and run exactly that many
   callbacks** (§1). Physically, "the loop waiting on I/O" is the thread **asleep inside `epoll_wait`, in `selector.select`** — the one
   blocking call in the whole loop, burning zero CPU. Its length is set by the run queue and the timer heap: 0 if `_ready` is non-empty,
   otherwise the time until the nearest `_scheduled` timer, otherwise `None`. `await asyncio.sleep(1)` is just a timer in `_scheduled`
   that caps that kernel sleep, so the loop keeps draining everything else; `time.sleep(1)` sleeps the **thread**, so the tick never
   reaches `select` at all and all 999 other tasks starve.
2. **Coroutine = the inert object you get from calling an `async def` function — a paused frame, a *recipe*. Future = a result box with a
   state (`PENDING`/`FINISHED`/`CANCELLED`) plus done-callbacks — a *mailbox*. Task = a Future subclass that wraps and *drives* a
   coroutine, scheduled on the loop the instant it is created — a *running job* plus its mailbox** (§2). `foo()` runs none of the body
   because calling an `async def` **builds** the frame rather than executing it — hence the "coroutine was never awaited" warning: you
   made the recipe and threw it away. Two `await`s run sequentially because **`await` does not create a Task** — it runs the awaited
   coroutine *inside the current task*, chaining frames, so the task cannot proceed past the first `await` until it resolves. Concurrency
   needs *more tasks* for the loop to interleave (`create_task`/`gather`/`TaskGroup`).
3. (a) **`gather(..., return_exceptions=True)`** — harvest mode: every raising coroutine comes back as an exception object, index-aligned,
   and the batch always completes, so failures are reported per item instead of crashing the call (§3). (b) **`TaskGroup`** — fail-fast by
   design: the first error cancels all siblings and raises an `ExceptionGroup` at the block, which is exactly the policy when partial
   success is meaningless (§3, §4). (c) **`as_completed`** — it yields futures in *completion* order, so you persist each result the
   instant it lands and a crash at item 198 costs nothing already harvested (§3). What default `gather` does to the other 199 when #50
   raises: **nothing — it does not cancel them.** The exception propagates to your `await` immediately while the siblings keep running as
   **orphans**, consuming connections and rate-limit budget with their results silently dropped (§6, footgun 2).
4. **`task.cancel()` sets a flag; it kills nothing and interrupts no running line.** The next time the loop would resume that task, it
   resumes it with **`coro.throw(CancelledError)`** instead of `coro.send(value)` — the exception is raised *at the exact `await` where
   the coroutine is suspended* (§5). Normal completion and cancellation are the same resume machinery with a different payload. A timeout
   ends a silent hang because the coroutine is **parked** at an `await` on a Future that stays `PENDING` forever: the loop itself is
   healthy, the timeout's deadline sits in `_scheduled`, the tick fires it (§1 — timers and I/O are the same kind of event), it calls
   `cancel()`, and the injected exception has a suspension point to land on. `return_exceptions=True` can only capture an exception the
   coroutine **raises on its own**; silence raises nothing, so only an *externally injected* exception can end it.
5. **The timeout never fires and the program hangs forever — only `Ctrl-C` breaks it** (§10a). Two independent reasons, and the dominant
   one is not the obvious one. **Dominant:** `asyncio.timeout` is not a watchdog thread — it is a timer scheduled **on the same loop**,
   and your `while True` runs inside the Task's `__step` callback, so `coro.send(None)` never returns, `__step` never returns, `_run_once`
   never finishes its tick (§1), the due timer is never moved to `_ready`, and **`task.cancel()` is never even called**. **Independent
   second reason:** even granting that `cancel()` somehow fired, cancellation is delivered only at a resume-from-`await`, and this
   coroutine has no suspension point anywhere — the exception has nowhere to land. The fix is therefore not a timeout at all: get the work
   off the loop with `run_in_executor` onto a process pool (Ch3 §1 §4).
6. **They are right the first time and wrong the second.** `CancelledError` inherits from `BaseException`, not `Exception` (deliberately,
   since 3.8), so a blanket `except Exception:` cannot catch it — their "log and continue" genuinely cannot suppress a cancellation (§5).
   Switching to `except BaseException:` **does** catch it, and because they `return` instead of re-raising, the task **swallows its own
   cancellation**: the timeout fired, the exception was thrown in, and the code ate it and kept going. Production symptom:
   `asyncio.timeout` appears not to stop the work, shutdown hangs, "this task won't die" (§6, footgun 3). The idiom is catch, clean up,
   **and `raise`**.
7. **Because structured concurrency makes "several children failed at once" a routine, first-class event, and the pre-3.11 exception model
   could only carry one exception** (§4). A `TaskGroup` child failure *cancels its siblings*, and those siblings can raise on their way
   out too, so the block has to deliver a *set* of errors to a single point — pick one and you are back to the silently-swallowed error
   that structured concurrency exists to abolish. `ExceptionGroup` (PEP 654) is that multi-error value and `except*` is the syntax that
   handles one type across the group without discarding the rest. Hence the two features shipped together in 3.11.

</details>

---

## 9. Optional: get your hands dirty (15–20 min)

Make the abstractions concrete. Watch the wall-clock and the order of prints — the surprises are the point.

```python
import asyncio, time

# (a) Serial awaits vs gather — the §2 lesson, timed.
async def work(name, secs):
    await asyncio.sleep(secs)          # stands in for an I/O wait; releases to the loop
    return f"{name} done"

async def serial():
    t = time.perf_counter()
    await work("A", 1); await work("B", 1)            # two awaits, one task
    print(f"serial:  {time.perf_counter()-t:.2f}s")   # ~2s

async def concurrent():
    t = time.perf_counter()
    await asyncio.gather(work("A", 1), work("B", 1))  # two tasks
    print(f"gather:  {time.perf_counter()-t:.2f}s")   # ~1s

asyncio.run(serial()); asyncio.run(concurrent())
```

```python
# (b) Cancellation is an injected exception. Watch it land AT the await, and watch finally run.
async def victim():
    try:
        print("victim: parking on a 10s wait")
        await asyncio.sleep(10)
    except asyncio.CancelledError:
        print("victim: CancelledError landed AT the await")
        raise                              # <-- comment this out and see the warning/hang behaviour change
    finally:
        print("victim: finally ran (cleanup happens during cancellation)")

async def main_cancel():
    t = asyncio.create_task(victim())
    await asyncio.sleep(0.5)
    t.cancel()                             # inject the exception
    try:
        await t
    except asyncio.CancelledError:
        print("main: task was cancelled")

asyncio.run(main_cancel())
```

```python
# (c) The §5 punchline: a timeout CANNOT cancel un-yielding code. (Ctrl-C it after a few seconds.)
async def cpu_stuck():
    x = 0
    while True:               # no await — never resumes — cancellation has nowhere to land
        x += 1

async def main_timeout():
    try:
        async with asyncio.timeout(2):
            await cpu_stuck()
    except TimeoutError:
        print("this line will NOT print in 2s — the timeout can't break in")

# asyncio.run(main_timeout())   # uncomment to feel the footgun; it hangs past 2s
```

```python
# (d) TaskGroup fail-fast vs gather harvest — same two coroutines, opposite outcomes.
async def ok():   await asyncio.sleep(0.2); return "ok"
async def boom(): await asyncio.sleep(0.1); raise ValueError("boom")

async def harvest():
    res = await asyncio.gather(ok(), boom(), return_exceptions=True)
    print("gather harvest:", res)          # ['ok' arrives, ValueError captured] — both finish

async def failfast():
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(ok()); tg.create_task(boom())
    except* ValueError as eg:
        print("TaskGroup failfast: ok() was cancelled, got", eg.exceptions)

asyncio.run(harvest()); asyncio.run(failfast())
```

Bring the numbers and the print-orders to our chat — especially (b) with and without the `raise` (the swallowed-cancellation bug made
visible), and (c) (the timeout that can't fire).

---

## 10. Applied — captured from our 2026-06-25 session

A short, clean session: the body held at your level and you took the whole exchange into **one question — check-question 8.5** — *a
coroutine stuck in `while True: x += 1` (no `await`), wrapped in `asyncio.timeout(5)`: does the timeout fire?* You committed to a
hypothesis — **"this timeout will never fire"** — and, notably, this time it wasn't your usual sharp-but-mis-ranked guess: you'd named the
**dominant** mechanism correctly. The value was in sharpening *why* into two layers.

### 10a. The confirmation, and the two independent reasons (the §5 mechanism, made precise)

Your conclusion is right: **the timeout never fires; the program hangs forever** (only `Ctrl-C` breaks it). What we pinned down is that
**two separate things** each independently doom it — and you'd zeroed in on the first, which is the one that actually decides the outcome:

- **Reason 1 — the dominant one: the loop itself is wedged, so the timer can never run.** The crux you spotted: `asyncio.timeout(5)` is
  **not a separate watchdog thread** — it's a timer scheduled *on the same event loop* (`loop.call_at(deadline, …)`, whose callback calls
  `task.cancel()`). Your `while True` runs *inside* the Task's `__step` callback; `coro.send(None)` enters the loop and **never returns**,
  so `__step` never returns, so `_run_once` never completes its tick (§1), so the loop never reaches the step where it would fire the
  due timer. The deadline passes unnoticed in the `_scheduled` heap and **`task.cancel()` is never even called.** The timeout machinery is
  frozen *on the very loop it's trying to interrupt* — this is the §1/§6 "blocking the loop" footgun in its purest form.
- **Reason 2 — independent, would bite even if Reason 1 didn't: cancellation needs an `await` to land.** Granting Reason 1 away (say
  `cancel()` were somehow called from another thread), cancellation is an exception **injected at the next resume-from-`await`**
  (`coro.throw(CancelledError)`, §5). With no suspension point anywhere in the coroutine, there's nowhere to deliver it — the CPU loop is
  *intrinsically* uncancellable. So the work is doubly unreachable: the cancel is never **sent** (R1) and would have nowhere to **land**
  (R2).

The `Ctrl-C` exception to the rule is the tell that it's specifically the *Python/loop* level that's stuck: `SIGINT` is delivered at the C
level and raises `KeyboardInterrupt` into the running bytecode without the loop's cooperation, which is exactly why it works when the
timeout can't.

> **The keeper:** *a timeout protects against an `await` that hangs (silence on I/O — your 9b case), never against CPU-bound code that
> refuses to yield.* The two failure modes look identical from outside ("it's stuck") but have opposite fixes: silence → wrap the `await`
> in `asyncio.timeout`; a non-yielding hot loop → there's nothing for a timeout to grab, so the fix is to get the work **off the loop**
> (`run_in_executor` → a process pool, §1 §4). Diagnosing "stuck" therefore starts with one question — *is it parked at an `await`, or
> burning CPU with no `await`?* — and only the first is a timeout's job.

*(Closing note: this is the same boundary as your 06-16 9b re-rank, seen from the other side. There you separated "a task parked on I/O"
(recoverable, the loop is fine) from "a blocking call freezing the loop" (everyone starves). 8.5 is the second case taken to its limit —
the thing freezing the loop is also the thing the timeout would need the loop to interrupt, so the timeout joins the victims.)*

---

## 11. References (optional, for depth)

*(All links verified live 2026-06-25.)*

- **[Python docs — `asyncio` Tasks & coroutines](https://docs.python.org/3/library/asyncio-task.html)** — the authoritative reference for
  `create_task`, `gather`, `as_completed`, `wait`, `TaskGroup`, `timeout`, `wait_for`, `shield`, and the cancellation contract. Read the
  "Task Cancellation" and "Timeouts" subsections alongside §5.
- **[Python docs — Event Loop](https://docs.python.org/3/library/asyncio-eventloop.html)** — the loop API (`call_later`, `call_at`,
  `run_in_executor`, `set_debug`) behind §1's tick. The selector/`run_forever` machinery lives here.
- **[Python docs — Developing with asyncio](https://docs.python.org/3/library/asyncio-dev.html)** — the official footgun list (§6):
  blocking the loop (the "Running Blocking Code" section → `run_in_executor`), debug mode (`loop.set_debug`, `PYTHONASYNCIODEBUG`, slow-callback
  logging), and the "never retrieved" warning. The strong-reference idiom for `create_task` (keep a set so the GC can't collect a pending task)
  is documented on the **[`create_task` reference](https://docs.python.org/3/library/asyncio-task.html#asyncio.create_task)** itself.
- **[Nathaniel J. Smith — "Notes on structured concurrency, or: `go` statement considered harmful"](https://vorpus.org/blog/notes-on-structured-concurrency-or-go-statement-considered-harmful/)**
  — the essay that named the §4 idea. The `go`-statement-as-`goto` argument and the nursery design that became `TaskGroup`. Essential
  background, not just trivia.
- **[Trio documentation](https://trio.readthedocs.io/en/stable/)** — the library that pioneered nurseries and the "cancellation scope"
  model asyncio later adopted; reading Trio's cancellation docs is the cleanest way to see §5's ideas in their native form.
- **[PEP 654 — Exception Groups and `except*`](https://peps.python.org/pep-0654/)** — *why* the language grew `ExceptionGroup` and `except*`
  (§4): structured concurrency needs "several tasks failed at once" as a first-class value.
- **[PEP 3156 — Asynchronous IO Support (the `asyncio` design)](https://peps.python.org/pep-3156/)** and
  **[PEP 492 — `async`/`await` syntax](https://peps.python.org/pep-0492/)** — the origin documents: PEP 3156 specifies the event-loop/Future
  model of §1–§2; PEP 492 is where coroutines became their own thing (§2's "inert recipe").

---

### What's next
✅ **Finalized 2026-06-25.** This section dropped one level below §1 into the loop, the task model, and cancellation — and cashed the 9b
timeout keeper into its mechanism (§5). §10 captures the 8.5 thread: the timeout-on-a-CPU-loop, your correct "never fires," and the
two-independent-reasons sharpening (loop wedged · cancellation needs an await). Diagrams verified, links live; `courses/plan.md` Ch3 row
flips §2 to ✅. Natural follow-ons, your call at the boundary:
- **Ch3 §3 — Synchronization & races** (locks, `queue.Queue`/`asyncio.Queue`, deadlock, the data races free-threading exposes — §1 §5's
  "now it's your job"). The third leg of the chapter; pairs with the shared-mutable-state warning.
- **Ch3 §4 — *(if we add it)* the producer/consumer & backpressure patterns** that the queue primitives enable — straight into M07 scaling
  territory.
- Or **rotate scope** per the interleave (this would be a fifth M01 day if taken now): **M04 Ch2 §2** (refactoring in moves, SWE — software engineering) or
  **M12 Ch2 §3** (audio/speech/text-to-speech, AI — your "all model types" goal).
