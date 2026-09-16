# M01 · Ch2 · §2 — Garbage Collection: Who Frees the Heap, and How It Knows When

> **Module:** How Computers & Operating Systems Work
> **Chapter:** Memory
> **Section:** Automatic memory management — CPython's reference counting, the cycle collector it needs, and why
> all of it is the deep reason the GIL (Global Interpreter Lock) exists.
> **Status:** ✅ **finalized 2026-06-13.** The body held up; the session was you pressure-testing the §7.2 rule
> ("use `with`, never the GC") against concrete code and a real fab-era image-processing leak — your signature mode,
> now aimed at the GC (garbage collection). §10 captures the two threads: **(10a)** resource-lifetime-vs-object-lifetime — `with` vs
> manual `close()` vs GC *from the GC's point of view* (answer: no GC difference; closing ≠ freeing); and **(10b)**
> the war story — why your `gc.collect()` fix was *also a diagnosis* (the leak must be cyclic), the count-vs-bytes
> threshold blindness that explains the "~10 images" crash, and **process isolation** as the robust "outlive the leak
> instead of cleaning it up" alternative.

**Estimated study time:** 2–3 hours including reflection.
**Prerequisites:** §1 of this chapter (stack vs heap; **a Python name is a pointer to a heap object**; assignment
copies the pointer; mutability; aliasing) and Ch1 §2 (the GIL kicker — "one thread, one instruction stream").
This section pays off the explicit IOU §1 left: *if heap objects must be freed by someone, and Python never makes
you call `free`, then **who frees them, and how does it know when?***

---

## Why this section exists (for *you*)

§1 ended on a cliffhanger. You now know the heap is where every Python object lives, and that — unlike the stack,
which frees itself on `ret` — heap memory **lives until something explicitly frees it**. In C that "something" is
you (`free(p)`), and getting it wrong gives the two classic disasters: free too early → use-after-free; never free
→ leak. Python makes neither mistake *for you*. So there is a mechanism, running constantly, invisibly, that you've
relied on every day without seeing. This section makes it visible.

Here's why it's worth your time specifically — three things it will change:

1. **You'll know when memory is actually freed**, which is not "when I'm done with it" and not "at `del`." This is
   the difference between a pipeline that holds 8 GB of intermediate tensors longer than you think and one that
   doesn't. For someone shipping LLM (large language model) data pipelines, *when the last reference drops* is a latency-and-cost question,
   not trivia.
2. **You'll see the one bug class GC can't save you from — reference cycles — and where your own code makes them.**
   Your graph-pipeline design from §10 is directly relevant here, and the answer is a satisfying callback.
3. **You'll finally see the bottom of the GIL.** You already understand *what* the GIL does (serializes threads).
   This section shows *why CPython has one at all* — and the answer is **reference counting**, not "Python is old."
   That connection is the keystone, and it's why free-threaded Python (PEP 703, your frontier-level material) is so
   hard and so interesting. This is the layer past where most explanations stop.

A framing to carry, since the physics one served §1: garbage collection is a **conservation law with a bookkeeping
problem.** The invariant the runtime must preserve is *"memory reachable from your program stays alive; memory
unreachable from your program gets reclaimed."* "Reachable" is the conserved quantity. The whole design question is
just: **how do you cheaply detect when reachability drops to zero?** CPython answers it two ways at once — a fast
local approximation (reference counting) and a slower global correction (the cycle collector) for the case the
approximation gets wrong. Effective theory plus the correction term at the boundary where it breaks down — the same
shape as §1.

---

## 1. Two families of answer: counting vs. tracing

<details>
<summary><b>Vocabulary for this section</b> — the two GC families and the trade-off table's vocabulary (click to expand)</summary>

**Abbreviations**

| Short | Stands for | Meaning |
|---|---|---|
| **GC** | garbage collection / garbage collector | automatically reclaiming heap memory the program can no longer reach |
| **GIL** | Global Interpreter Lock | **a CPython construct, not an OS one** — one lock a thread must hold to touch any Python object; the kernel knows nothing about it |
| **CPython** | — | the standard C implementation of Python, the one from python.org |
| **PyPy** | — | an alternative Python implementation with a JIT compiler and a pure tracing GC |
| **V8** | — | Google's JavaScript engine, used in Chrome and Node.js |
| **GB** | gigabyte | one thousand megabytes |
| **`INCREF` / `DECREF`** | increment / decrement reference | the two operations that raise and lower an object's reference count |

**Terms**

| Term | Definition |
|---|---|
| **Heap** | the memory region where every Python object lives (§1) |
| **Reference** | a pointer to an object; a name, a list slot, an attribute or a function argument each is one |
| **Reference counting** | giving every object a count of how many references point at it, and freeing it the moment the count reaches zero |
| **Reference count (refcount)** | that integer stored inside the object |
| **Synchronously** | right now, as part of the operation that caused it, rather than later |
| **Scope exit** | leaving the function or block whose frame held the names, which drops those references |
| **Tracing garbage collection** | periodically walking the object graph from the roots and freeing everything not reached |
| **Object graph** | objects as nodes and their references as edges |
| **Roots** | the starting points of a trace: globals, names on the stack, CPU registers — the places the program itself can reach directly |
| **Reachable** | findable by following references from a root; the property that defines "still alive" |
| **Mark-and-sweep** | the classic tracing algorithm: mark everything reachable, then sweep away everything unmarked |
| **Stop-the-world pause** | halting the whole program so the collector can see a consistent heap |
| **Deterministic destruction** | an object being freed at a predictable moment — in CPython, at the last `DECREF` to zero |
| **Reference cycle** | a group of objects referring to each other, so their counts never reach zero even when nothing outside can reach them |
| **Atomics** | hardware instructions that perform a read-modify-write indivisibly, so two threads cannot interleave inside it |
| **Shared mutable state** | data more than one thread can change, which is what makes a lock necessary |
| **Steady-state overhead** | the ongoing cost paid by every operation, as opposed to occasional batched cost |
| **Portability trap** | code that works on CPython because of its timing and breaks on another implementation |
| **File handle** | the OS-level resource behind an open file; leaked if nothing closes it |
| **`with`** | Python's context-manager statement, which releases a resource on block exit no matter what the refcounts do |

</details>

Across all garbage-collected languages there are really only two strategies, and CPython is unusual in using
**both at once**. Get the two archetypes straight first; everything else is detail.

**Reference counting (CPython's primary mechanism).** Every object carries a small integer: *how many references
point at it right now.* Bind a new name to it → increment. Drop a name → decrement. The instant the count hits
**zero**, nobody can reach the object, so it is freed **immediately**, right there, synchronously. No separate
"collector" runs; reclamation is woven into every assignment and every scope exit.

**Tracing garbage collection (Java, Go, JavaScript/V8, C#, PyPy).** Objects carry no count. Periodically a
collector *stops* and walks the object graph outward from a set of **roots** (globals, the stack, registers) —
marking everything it can reach. Anything it didn't reach is, by definition, unreachable → swept and freed in bulk.
This is **mark-and-sweep**, and it runs *later*, in batches, not at the moment of last use.

<!-- DIAGRAM:START -->
![Diagram 1](diagrams/02-garbage-collection-1.svg)

<details>
<summary>Diagram source (Mermaid)</summary>

```mermaid
flowchart TB
    subgraph RC["Reference counting — local, eager, continuous"]
        direction TB
        R1["each object stores a refcount"]
        R2["bind a name / append to list / pass as arg → INCREF"]
        R3["rebind / del / scope exit / pop from list → DECREF"]
        R4["count hits 0 → freed IMMEDIATELY (synchronous)"]
        R1 --> R2 --> R3 --> R4
    end
    subgraph TR["Tracing GC — global, lazy, periodic"]
        direction TB
        T1["objects store NO count"]
        T2["periodically STOP the program"]
        T3["walk graph from roots, MARK reachable"]
        T4["SWEEP everything unmarked → freed in BULK (later)"]
        T1 --> T2 --> T3 --> T4
    end
```

</details>
<!-- DIAGRAM:END -->

The trade-off is sharp and worth memorizing, because it explains a lot of Python's behavior:

| | **Reference counting** (CPython) | **Tracing GC** (Java/Go/V8/PyPy) |
|---|---|---|
| **When is memory freed?** | Immediately, at the last `DECREF` to 0 — **deterministic** | Eventually, at the next collection — **non-deterministic timing** |
| **Pause behavior** | No big stop-the-world pause; cost is *smeared* across every operation | Periodic pauses (modern collectors make them tiny/concurrent, but they exist) |
| **Steady-state overhead** | High & constant — *every* refcount touch is work, even on hot loops | Low per-operation; you "pay" in batched collections |
| **Reference cycles** | **Cannot reclaim them** — needs a helper | Handled for free (a cycle simply isn't reached from roots) |
| **Thread safety of the counter** | Counter is shared mutable state → **needs a lock (the GIL)** or atomics | No per-object counter to race on |

That last row is the whole back half of this section. But first, the immediate consequence of "freed at the last
DECREF to 0":

> **In CPython, destruction is deterministic.** When the last reference to an object goes away, it is freed *then* —
> not "sometime soon." This is why so much Python code quietly relies on it (a file gets flushed when the last
> reference to it drops, a connection closes, a temporary 4 GB array is gone the instant the function returns). It
> is also a **portability trap**: PyPy and Jython use pure tracing GC, so that same code leaks file handles until
> the next collection. *Never* rely on refcount timing for resource cleanup — that's what `with` is for (§6).

---

## 2. Reference counting, concretely — watch the count move

<details>
<summary><b>Vocabulary for this section</b> — the refcount machinery, the `getrefcount` gotcha and the free cascade (click to expand)</summary>

**Abbreviations**

| Short | Stands for | Meaning |
|---|---|---|
| **GC** | garbage collection | automatic reclaiming of unreachable heap memory |
| **CPython** | — | the standard C implementation of Python |
| **`INCREF` / `DECREF`** | increment / decrement reference | raise or lower an object's reference count by one |

**Terms**

| Term | Definition |
|---|---|
| **Reference count (refcount)** | how many references currently point at an object |
| **`ob_refcnt`** | the actual field at the start of every CPython object's C struct that holds that count |
| **C struct** | a record type in C: several fields laid out together in memory — the form every Python object really takes |
| **Macro** | a C construct expanded by the compiler's preprocessor into inline code, so it costs no function call |
| **`Py_INCREF` / `Py_DECREF`** | those macros: add one, or subtract one and deallocate if the result is zero |
| **Deallocate** | release the object's memory back to the allocator |
| **Reference** | anything that points at an object: a name, a list or dict slot, an attribute, a parameter, a closure capture |
| **Name tag** | §1's image for a Python name — a label pointing at a heap object, not a box holding it |
| **`del`** | removes a *name*, which is one `DECREF`; it frees the object only if that was the last reference |
| **Closure** | a nested function that captures variables from the enclosing scope, holding references to them |
| **Attribute** | a value stored on an object, as in `self.x = obj` — another reference |
| **`sys.getrefcount()`** | reports an object's refcount, always one higher than expected because the call itself binds a temporary reference |
| **Immortal object** | since Python 3.12, an object such as `None` or a small int whose refcount is pinned so it is never freed and never needs updating |
| **Cascade** | freeing an object `DECREF`s everything it referenced, which may free those too, recursively |
| **Trashcan mechanism** | CPython's guard that spreads a very deep free cascade over several passes so it cannot overflow the C stack |
| **C stack** | the real machine stack the interpreter runs on, the bounded region of §1 |
| **Smeared cost** | refcounting's overhead spread thinly across every operation instead of concentrated in pauses |

</details>

The mechanism is almost embarrassingly simple. In CPython every object's C struct starts with a field
`ob_refcnt`. Two macros mutate it: `Py_INCREF` (count++) and `Py_DECREF` (count--; if it hit 0, deallocate). That's
it. The art is knowing *which Python operations* trigger them.

```python
import sys

a = [10, 20, 30]          # new list object; one reference ("a") → refcount 1
b = a                     # §1: a SECOND name tag on the SAME object → INCREF → refcount 2
container = [a]           # the list now holds a third reference → INCREF → refcount 3

print(sys.getrefcount(a)) # prints 4, not 3  ← see the gotcha below

del b                     # remove the name "b" → DECREF → refcount 2
container.pop()           # remove it from the list → DECREF → refcount 1
del a                     # remove the last name → DECREF → refcount 0 → FREED right here
```

References are created by **far more than `=`**: passing an object to a function (the parameter is a new
reference), inserting it into a list/dict/set, making it an attribute (`self.x = obj`), capturing it in a closure.
Each of those is an `INCREF`; the matching teardown (function returns, item removed, attribute reassigned, closure
dies) is a `DECREF`. You never write them — the interpreter does, on every single one of these events. *That* is the
"smeared cost" from the table: a tight Python loop touching objects is also a tight loop of integer
increment/decrement on refcounts.

> **The `getrefcount` gotcha (you'll hit this the moment you test it):** `sys.getrefcount(x)` reports **one higher**
> than you expect, because *calling it* binds `x` to its parameter — a temporary extra reference that exists for the
> duration of the call. So a freshly-made object with one name reports `2`. It's not a bug; it's the reference model
> being perfectly consistent (a function argument is a reference, §1). Newer Python (3.12+) also marks some objects
> **immortal** — see §6 — for which `getrefcount` returns a huge constant and never changes.

**The cascade.** When an object is freed, the interpreter `DECREF`s everything *it* referenced — which may drop
*those* to zero, freeing them too, recursively. So `del big_pipeline_state` can tear down a whole tree of objects in
one synchronous burst. (CPython uses a "trashcan" mechanism to keep that cascade from overflowing the *C* stack on
very deep structures — a direct callback to §1's stack-overflow cliff.) This is the elegant part of refcounting:
reclamation is precise, immediate, and proportional to what actually died.

---

## 3. The flaw refcounting can't fix: reference cycles

<details>
<summary><b>Vocabulary for this section</b> — cycles, and every ordinary structure that builds one (click to expand)</summary>

**Abbreviations**

| Short | Stands for | Meaning |
|---|---|---|
| **GC** | garbage collection | automatic reclaiming of unreachable heap memory |
| **`gc`** | the `gc` module | Python's standard-library interface to the cycle collector |

**Terms**

| Term | Definition |
|---|---|
| **Reference count (refcount)** | how many references point at an object right now |
| **Reference cycle** | objects that refer to each other in a closed loop, so each keeps the other's count above zero |
| **Unreachable** | not findable by following references from anything the program itself holds — the definition of garbage |
| **Roots** | the program's own entry points into the heap: names on the stack, globals, registers |
| **Garbage** | objects the program can no longer reach and which should therefore be freed |
| **Leak** | memory never reclaimed, so it accumulates for the life of the process |
| **`del`** | removes one name, that is one `DECREF`; it does not by itself free anything |
| **Local count** | what refcounting sees — the number on one object, with no view of the shape of the graph around it |
| **Back-reference** | a child pointing at its parent, closing the loop the parent opened |
| **Doubly-linked list** | a chain where each node points both to the next node and back to the previous one — inherently cyclic |
| **Observer registry** | a list of objects to be notified of events; if they also hold the registry, that is a cycle |
| **Closure** | a nested function holding on to variables from its enclosing scope |
| **Traceback** | the object recording where an exception was raised; it holds the frames, which hold their locals |
| **Frame** | one function call's block of locals and bookkeeping (§1) |
| **`except ... as e`** | the exception-catching clause; Python deletes `e` at the end of the block precisely to break the traceback cycle |
| **Cycle collector** | the second CPython mechanism whose only job is finding and breaking unreachable cycles — what people mean by "Python's garbage collector" |
| **Container object** | an object that can hold references to others (list, dict, set, instance) — the only kind that can be in a cycle |

</details>

Reference counting has one fatal blind spot, and it's a logical one, not an implementation bug. Consider two
objects that point at **each other**:

```python
a = {}
b = {}
a["partner"] = b      # b's refcount: 2 (the name "b" + a's entry)
b["partner"] = a      # a's refcount: 2 (the name "a" + b's entry)

del a                 # a's refcount: 2 → 1   (b still points to it!)
del b                 # b's refcount: 2 → 1   (a still points to it!)
```

After both `del`s, **you** cannot reach either dict — there's no name pointing in from your program. They are
garbage. But each one's refcount is stuck at **1**, because they hold each other up. Refcounting only sees *local*
counts; it cannot tell that the two surviving references form a closed loop that nothing outside can enter. Pure
refcounting would **leak this forever.**

<!-- DIAGRAM:START -->
![Diagram 2](diagrams/02-garbage-collection-2.svg)

<details>
<summary>Diagram source (Mermaid)</summary>

```mermaid
flowchart LR
    subgraph roots["Your program (roots)"]
        direction TB
        note["after del a, del b:<br/>NO name points in"]
    end
    subgraph heap["Heap — an unreachable cycle"]
        A["dict A<br/>refcount = 1"]
        B["dict B<br/>refcount = 1"]
        A -- "'partner'" --> B
        B -- "'partner'" --> A
    end
    roots -. "nothing reaches in" .-> heap
```

</details>
<!-- DIAGRAM:END -->

This is not exotic. Cycles appear all the time in ordinary structures:

- **Parent ↔ child back-references**: a tree node holding `self.children` *and* each child holding `self.parent`.
- **Doubly-linked lists**: every node points to `prev` and `next`.
- **Caches / observer registries** that hold objects which hold the cache back.
- **A closure that captures a variable referring to the closure**, or an object whose method is stored as its own
  attribute.
- **Exception tracebacks**: a caught exception's traceback holds the frame, the frame holds local variables, and a
  local variable may be the exception — a cycle that pins an entire stack frame's worth of objects. (This is why
  `except ... as e:` deletes `e` at the end of the block, and why holding onto exceptions can leak surprisingly
  large graphs.)

So CPython needs a second mechanism whose *only job* is to find and break unreachable cycles. That's the cycle
collector — the thing people actually mean when they say "Python's garbage collector" (the `gc` module).

---

## 4. The cycle collector: a generational tracing GC bolted on

<details>
<summary><b>Vocabulary for this section</b> — the generational collector, its algorithm and its tuning knobs (click to expand)</summary>

**Abbreviations**

| Short | Stands for | Meaning |
|---|---|---|
| **GC** | garbage collection / garbage collector | automatic reclaiming of unreachable memory; here specifically CPython's cycle collector |
| **`gc`** | the `gc` module | the standard-library interface to that collector |
| **gen 0 / gen 1 / gen 2** | generation zero, one, two | the collector's three age buckets, scanned from most to least often |
| **CPU** | central processing unit | the processor whose time the scans consume |

**Terms**

| Term | Definition |
|---|---|
| **Cycle collector** | CPython's tracing collector, which exists only to reclaim the reference cycles refcounting cannot |
| **Tracing collector** | one that finds live objects by walking references rather than by counting them |
| **Tracked object** | a container the collector keeps in its lists; plain `int`, `str` and `float` are untracked because they cannot form cycles |
| **Container object** | an object able to hold references to other objects — list, dict, set, class instance, a tuple containing containers |
| **Reference count (refcount)** | the per-object count maintained by `INCREF` and `DECREF` |
| **Scratch copy** | the collector's private duplicate of each refcount, which it may decrement freely without touching the real one |
| **Internal reference** | a reference from one tracked object to another; subtracted from the scratch copy |
| **External reference** | a reference from outside the tracked set — a name on your stack, a global — which proves the object is alive |
| **Candidate for collection** | an object whose scratch count fell to zero, meaning nothing outside the set reaches it |
| **Mark-and-sweep** | the tracing family this algorithm belongs to: identify what is reachable, free the rest |
| **Finalize** | run an object's cleanup (`__del__`, weakref callbacks) before its memory is released |
| **Generational collection** | scanning young objects often and old ones rarely, since survivors tend to keep surviving |
| **Weak generational hypothesis** | the empirical observation that most objects die very young |
| **Promotion** | moving an object to an older generation because it survived a collection |
| **Allocation pressure** | the running count of allocations minus deallocations — what triggers a collection, rather than elapsed time |
| **Threshold** | the trigger values, `(700, 10, 10)` by default: 700 net allocations trigger gen 0, 10 gen-0 passes trigger gen 1, 10 of those trigger gen 2 |
| **`gc.get_count()` / `gc.get_threshold()` / `gc.set_threshold()`** | read the current counters, read the thresholds, change the thresholds |
| **`gc.collect()`** | force a collection pass immediately |
| **`gc.disable()`** | switch off the cycle collector; refcounting keeps running and cannot be switched off |
| **Batch job** | a long-running one-shot workload, the case where disabling the collector can pay off |

</details>

The `gc` module is a **tracing collector**, but a specialized one: it doesn't manage all memory (refcounting already
does that). It runs only to **catch the cycles refcounting misses**, and it only tracks *container* objects — things
that can hold references to other objects (lists, dicts, sets, instances, tuples-containing-containers). Objects that
*can't* form cycles — a plain `int`, a `str`, a `float` — are never tracked, because they can't be part of the
problem. That's already a big optimization.

**How it finds an unreachable cycle without roots-walking the whole heap.** The clever trick: for the set of tracked
objects, the collector makes a scratch copy of each refcount and then, for every reference *between tracked objects*,
**decrements the copy.** After this pass, an object's scratch count tells you how many references it has from
*outside* the tracked set. If an object's scratch count is **> 0**, something external (a name on your stack, a
global) still reaches it → it's alive, and so is everything reachable from it. If it's **0**, its only references
were internal — a candidate for collection. Anything left over with no external anchor is an unreachable cycle, and
it gets finalized and freed. (This is a mark-and-sweep variant; the full algorithm is in the reference below.)

**Generational, because most objects die young.** Running that scan over *all* container objects on every collection
would be expensive. So the collector exploits the **weak generational hypothesis** — empirically, *most objects die
very young* (the temporary you made two lines ago) and the few that survive a while tend to live long. It keeps three
**generations**:

<!-- DIAGRAM:START -->
![Diagram 3](diagrams/02-garbage-collection-3.svg)

<details>
<summary>Diagram source (Mermaid)</summary>

```mermaid
flowchart LR
    NEW["new container objects<br/>land in gen 0"] --> G0["Gen 0<br/>scanned OFTEN"]
    G0 -- "survives a collection" --> G1["Gen 1<br/>scanned less often"]
    G1 -- "survives again" --> G2["Gen 2<br/>scanned rarely<br/>(long-lived objects)"]
    G0 -. "freed if unreachable" .-> X0["reclaimed"]
    G1 -. "freed if unreachable" .-> X1["reclaimed"]
    G2 -. "freed if unreachable" .-> X2["reclaimed"]
```

</details>
<!-- DIAGRAM:END -->

- New objects start in **gen 0**, scanned frequently and cheaply (it's small).
- Survive a gen-0 collection → promoted to **gen 1**; survive that → **gen 2**.
- Higher generations are scanned progressively less often, so the rare long-lived objects aren't re-examined
  constantly. You pay the most attention to the youngest objects, which is where almost all the garbage is.

**It's triggered by allocation pressure, not a clock.** The default thresholds are `(700, 10, 10)`: a gen-0
collection runs roughly after *allocations minus deallocations* exceeds 700 since the last one; gen 1 runs after 10
gen-0 collections; gen 2 after 10 of those. You can watch and tune this with `gc.get_count()`, `gc.get_threshold()`,
`gc.set_threshold()`, force a pass with `gc.collect()`, or switch it off with `gc.disable()`.

> **The "turn off the GC" trick you may have seen:** the cycle collector is the *only* part you can disable — refcounting is
> not optional and always runs. Some workloads (a big batch job that allocates a huge, long-lived structure once and
> never makes cycles) call `gc.disable()` to avoid pointless scans of objects that will never be collected anyway —
> Instagram famously did this to cut CPU. The risk: if your code *does* make cycles, disabling the collector turns
> them into leaks. It's a sharp tool, not a default.

---

## 5. The combined picture — and a callback to your graph pipeline

<details>
<summary><b>Vocabulary for this section</b> — how the two mechanisms combine, plus the DAG argument about your own designs (click to expand)</summary>

**Abbreviations**

| Short | Stands for | Meaning |
|---|---|---|
| **GC** | garbage collection / garbage collector | automatic reclaiming of unreachable memory |
| **DAG** | directed acyclic graph | a graph whose edges all point one way and which therefore contains no cycle |
| **`INCREF` / `DECREF`** | increment / decrement reference | the two refcount operations |

**Terms**

| Term | Definition |
|---|---|
| **Reference counting** | freeing an object the instant its count of references reaches zero |
| **Cycle collector** | the periodic tracing pass that reclaims unreachable cycles refcounting cannot see |
| **Correction term** | the borrowed physics phrase for the cycle collector: the small fix applied where the cheap approximation is wrong |
| **Cascade** | the chain of frees triggered when a freed object drops its own references |
| **Reference cycle** | a closed loop of references that props its own members up |
| **Immutable** | with no in-place modification, so an existing object can never be made to point at a newer one |
| **Append-only** | only ever adding entries, never rewriting existing ones |
| **Functional update** | producing a new value rather than mutating the old one — the `state -> new state` flow |
| **Frozen** | not reassignable after construction, as with `@dataclass(frozen=True)` |
| **Node** | one step of the graph pipeline, taking a state and returning a new one |
| **Acyclic** | containing no loop; new nodes may point at old ones, but never the reverse |
| **Bidirectional structure** | links that point both ways (parent and child, observer and subject, previous and next) — the usual source of cycles |
| **Aliasing** | §1's bug class: two names on one object, so a mutation through one is seen through the other |

</details>

Put the two together and you have CPython's actual memory manager:

<!-- DIAGRAM:START -->
![Diagram 4](diagrams/02-garbage-collection-4.svg)

<details>
<summary>Diagram source (Mermaid)</summary>

```mermaid
flowchart TD
    OP["any operation that changes a reference<br/>(bind, pass, store, del, scope exit)"] --> RC["adjust refcount (INCREF / DECREF)"]
    RC --> Z{"refcount == 0?"}
    Z -- "yes" --> FREE["free NOW, synchronously<br/>+ DECREF everything it referenced (cascade)"]
    Z -- "no, still > 0" --> LIVE["object stays alive"]
    LIVE --> CYC{"but is it stuck in an<br/>unreachable CYCLE?"}
    ALLOC["allocations since last GC<br/>cross a threshold"] --> GCRUN["cycle collector runs<br/>(generational mark-and-sweep<br/>over tracked containers)"]
    GCRUN --> CYC
    CYC -- "yes, found by collector" --> FREE2["finalize + free the cycle"]
    CYC -- "no" --> LIVE2["lives until refcount hits 0 normally"]
```

</details>
<!-- DIAGRAM:END -->

Refcounting does ~99% of the work, instantly and precisely. The cycle collector is the periodic correction term that
mops up the one case refcounting provably can't.

**Now the callback you'll appreciate.** Remember your two-part graph-state design from §10d — frozen `Core` + an
append-only, immutable `Artifacts` store, state flowing `state -> new state` through nodes? Ask: *does that design
create reference cycles?* It (almost) **can't**. Immutable, functionally-updated, append-only structures form a
**DAG** (a directed *acyclic* graph): a new state points back at old artifacts, but old artifacts never point
forward at the new state — there's no way to close a loop when you can only build new nodes that reference existing
ones. So your immutable-dataflow discipline doesn't just kill the §1 aliasing bugs — it also keeps the cycle
collector nearly idle, because *you never manufacture the cycles it exists to clean up.* Cycles are a hallmark of
**mutable, bidirectional** structure (parent↔child, observer↔subject, node.prev↔node.next). The same design choice
that made your state honest also made it GC-cheap. Worth holding onto for M14/M07.

---

## 6. The keystone: why this *is* the GIL — and what free-threading changes

<details>
<summary><b>Vocabulary for this section</b> — the race the GIL prevents, and every technique PEP 703 uses to avoid needing it (click to expand)</summary>

**Abbreviations**

| Short | Stands for | Meaning |
|---|---|---|
| **GIL** | Global Interpreter Lock | **a CPython-level lock, not an OS or kernel facility** — a thread must hold it to touch any Python object; CPython itself releases it around blocking calls via `Py_BEGIN_ALLOW_THREADS` |
| **PEP** | Python Enhancement Proposal | the numbered design documents of the Python project |
| **PEP 703** | — | the proposal that makes the GIL optional: free-threaded CPython |
| **PEP 683** | — | the proposal that introduced immortal objects |
| **GC** | garbage collection / garbage collector | automatic reclaiming of unreachable memory |
| **CPython** | — | the standard C implementation of Python |
| **`INCREF` / `DECREF`** | increment / decrement reference | raise or lower an object's reference count |

**Terms**

| Term | Definition |
|---|---|
| **Thread** | one independent stream of execution inside a process, sharing the process's memory with the others |
| **Reference count (refcount)** | the per-object integer that reference counting maintains |
| **`ob_refcnt`** | the field in the object's C struct that holds it |
| **Read-modify-write** | load a value, change it, store it back — three steps, and therefore interruptible |
| **Atomic** | indivisible: no other thread can observe or interleave with a half-finished operation |
| **Race (data race)** | two threads touching the same data at once with at least one writing, so the result depends on timing |
| **Lost update** | the classic race outcome: two increments happen but only one is recorded |
| **Interleaving** | two threads' steps being mixed together by the scheduler |
| **Serialize** | force operations to happen one at a time, in some order |
| **Lock** | a thing exactly one thread can hold at a time, used to serialize access |
| **Interned string** | a string CPython keeps a single shared copy of, so every thread references the same object |
| **Singleton** | an object existing exactly once — `None`, `True`, `False` — and therefore referenced by every thread |
| **Use-after-free** | touching memory that has already been released; here the crash a lost `INCREF` eventually causes |
| **Hot path** | the code executed most often, where any added cost is multiplied enormously |
| **Free-threaded CPython** | the build with no GIL — experimental in 3.13, supported from 3.14 |
| **Immortal object** | one whose refcount is pinned at a sentinel maximum, making `INCREF` and `DECREF` on it no-ops needing no synchronization |
| **No-op** | an operation that does nothing |
| **Sentinel value** | a reserved value used as a marker rather than as a real count |
| **Biased reference counting** | giving each object an owning thread that updates a cheap local count, while other threads use a separate atomic shared count, reconciled when needed |
| **Owning thread** | the thread that created an object and, in the common case, is the only one to touch it |
| **Contended** | being fought over by several threads, which is what makes an atomic operation expensive |
| **Deferred reference counting** | skipping refcount updates on some references and resolving them later at a collection point |
| **mimalloc** | a thread-safe allocator adopted by the free-threaded build so allocation needs no global lock |
| **Reconciliation protocol** | the rules for merging an object's local and shared counts into one true value |
| **Stop-the-world pause** | halting all threads so the collector sees a consistent heap — what the no-GIL cycle collector needs, since it can no longer rely on the GIL for quiet |

</details>

This is the section to push on, because it's where reference counting stops being a Python-trivia topic and becomes
**the** explanation for the single most-discussed fact about CPython. You already know *what* the GIL does. Here's
*why it must exist.*

**The argument, in three steps.**

1. `Py_INCREF` / `Py_DECREF` compile down to roughly `obj->ob_refcnt++` and `obj->ob_refcnt--`. That is a
   **read-modify-write** on a memory location, and it is **not atomic** — it's three operations (load, add, store).
2. `None`, `True`, small ints, interned strings, common type objects — these are referenced by *every* thread,
   constantly. So multiple threads are doing `ob_refcnt++` / `--` on the *same* counter all the time.
3. Two threads interleaving a non-atomic increment lose an update (classic lost-update race). A refcount that should
   be 5 becomes 4. One DECREF too many later → the object is **freed while still in use** → use-after-free → the
   interpreter crashes or corrupts memory. This isn't a rare race; with shared singletons it would be constant.

So CPython needs every refcount mutation to be serialized. The brute-force way to guarantee that is **one global
lock that a thread must hold to touch *any* Python object** — the Global Interpreter Lock. The GIL is not primarily
about your data structures; **it's the lock that makes reference counting thread-safe.** That's the bottom of it.

<!-- DIAGRAM:START -->
![Diagram 5](diagrams/02-garbage-collection-5.svg)

<details>
<summary>Diagram source (Mermaid)</summary>

```mermaid
flowchart TB
    subgraph problem["The race the GIL prevents"]
        direction TB
        T1["Thread 1: load refcnt (5)"] --> T1b["add 1 → 6"] --> T1c["store 6"]
        T2["Thread 2: load refcnt (5)"] --> T2b["sub 1 → 4"] --> T2c["store 4"]
        LOST["interleaved → final value 4 or 6, not 5<br/>→ premature free or leak → CRASH"]
        T1c --> LOST
        T2c --> LOST
    end
```

</details>
<!-- DIAGRAM:END -->

This is why the GIL is so stubborn to remove: refcounting is woven into *every object access*, so the naive fix —
make every refcount a hardware atomic — would put an atomic operation on the hottest path in the interpreter and
slow down *single*-threaded code by tens of percent. For decades that tax was judged not worth it.

**What free-threaded CPython actually does (PEP 703 — your frontier layer).** The no-GIL build, experimental in 3.13
and supported from 3.14, doesn't wave the problem away — it attacks the refcounting cost directly with a stack of
techniques, all of which are "make most refcount operations *not* a contended atomic":

- **Immortal objects (PEP 683):** give `None`, `True`, `False`, small ints, interned strings a refcount pinned at a
  sentinel maximum. `INCREF`/`DECREF` on them become **no-ops** — they're never freed, so they never need a
  consistent count, so threads can touch them with zero synchronization. (This is also why, in 3.12+, `getrefcount`
  on `None` returns an enormous constant — you've seen the effect, now you know the cause.)
- **Biased reference counting:** each object has an **owning thread** that mutates a *local, non-atomic* count
  cheaply (the common case — most objects are only ever touched by their creator); *other* threads use a separate
  *shared, atomic* count. The two are reconciled when needed. You pay the atomic cost only for genuinely
  cross-thread-shared objects, not for everything.
- **Deferred reference counting** for some objects, and **mimalloc** for thread-safe allocation without a global
  allocator lock.

The conceptual payoff is the part to keep: **free-threading is fundamentally a *garbage-collection* engineering
problem, not a "remove a lock" problem.** The lock was a *symptom*; the disease is "refcounting needs a consistent
counter and threads make consistency expensive." Every trick in PEP 703 is a way to make the count consistent
without a global lock. That's the layer most discussions miss, and it's exactly the kind of thing your hardware/
systems instinct will enjoy interrogating (e.g. what does biased refcounting cost when an object's access pattern
*changes* owner? what is the reconciliation protocol? — good questions for our chat).

**The practical knock-on:** in a free-threaded build the cycle collector also has to change (it can't rely on the
GIL to give it a quiet, consistent snapshot of the heap), which is why the no-GIL GC uses a stop-the-world pause
instead. The reference doc covers both builds side by side.

---

## 7. Where this bites *you* — the practitioner's takeaways

<details>
<summary><b>Vocabulary for this section</b> — the practitioner vocabulary: `del`, `with`, arenas, RSS, weak references (click to expand)</summary>

**Abbreviations**

| Short | Stands for | Meaning |
|---|---|---|
| **GC** | garbage collection / garbage collector | automatic reclaiming of unreachable memory |
| **OS** | operating system | the kernel and its services; the layer CPython asks for and returns memory to |
| **RSS** | resident set size | how much of a process's memory is actually in physical RAM right now — the number `top` shows |
| **DB** | database | as in a database connection, a resource needing explicit release |
| **GB** | gigabyte | one thousand megabytes |
| **PEP 442** | Python Enhancement Proposal 442 | the change that made objects with `__del__` collectable inside cycles |
| **PyPy** | — | the alternative Python implementation with a pure tracing GC and therefore no deterministic destruction |
| **CPython** | — | the standard C implementation of Python |

**Terms**

| Term | Definition |
|---|---|
| **`del`** | removes a name, that is one `DECREF`; the object dies only if that was the last reference |
| **Reference count (refcount)** | how many references point at an object |
| **Closure** | a nested function holding references to variables from its enclosing scope — a common accidental retainer |
| **Context manager** | an object usable with `with`, which releases its resource on block exit whatever the refcounts do |
| **`with`** | the statement that drives a context manager; the correct tool for resource cleanup |
| **Resource** | something scarce held outside Python's heap — a file handle, a socket, a DB connection, a lock |
| **Finalizer (`__del__`)** | a method called when an object is destroyed; unreliable for cleanup because its timing is not guaranteed |
| **Resurrect** | a finalizer storing `self` somewhere, making a supposedly dead object live again |
| **Portability trap** | relying on CPython's refcount timing, which other implementations do not provide |
| **pymalloc** | CPython's own small-object allocator, layered over the system `malloc` |
| **Pool / arena** | the blocks pymalloc obtains from the OS once and then carves objects out of; freed objects usually stay in them rather than going back to the kernel |
| **Kernel** | the core of the operating system, which actually owns the physical memory |
| **Resident memory** | the part of a process's memory currently held in RAM — what RSS measures |
| **Leak** | in Python's sense, live objects that keep accumulating, as opposed to merely high RSS |
| **`tracemalloc`** | the standard-library tool that records where objects were allocated, so a real leak can be located |
| **Tensor** | a multi-dimensional numeric array, the large intermediate value in an ML pipeline |
| **Accidental retention** | keeping a big object alive by a reference you forgot about — an earlier state object, a log call, a module-level cache |
| **Module-level cache** | a dict or similar living for the whole process, so anything inside it never dies |
| **Strong reference** | an ordinary reference, which counts and therefore keeps its object alive |
| **Weak reference** | a reference that does **not** raise the refcount, so its target can still die; the entry then disappears |
| **`weakref` / `WeakValueDictionary`** | the module and the dict type that hold their values weakly |
| **Memoization** | caching a function's results by its arguments |
| **Back-edge** | the reference pointing from child back to parent; making it weak keeps the structure acyclic |
| **Acyclic** | containing no reference loop, so refcounting alone can reclaim it immediately |
| **Determinism** | freeing happening at a known moment, which cycles destroy because they wait for a collector pass |

</details>

Not trivia. Concrete consequences for the pipelines you ship:

**1. `del` does not (necessarily) free.** `del x` removes the *name* `x` — one `DECREF`. The object is freed only if
that was the *last* reference. If it's also in a list, captured in a closure, or held by another name, `del` frees
nothing. The reframe from §1: `del` un-sticks one name tag; the object dies only when the *last* tag is gone.

**2. For resource cleanup, use `with`, never the garbage collector.** Because CPython frees deterministically, it's
tempting to lean on "the file closes when the object dies." Don't — it's a portability trap (§1's note: PyPy won't),
and even on CPython a stray reference (a cycle, a logged exception holding a frame) can delay it indefinitely. Files,
sockets, DB (database) connections, locks → context managers (`with open(...) as f:`), which release on block exit regardless of
refcounts. `__del__` finalizers are **not** reliable cleanup hooks (uncertain timing; historically didn't run on
cycles at all before PEP 442; can resurrect objects). Treat `__del__` as a last-resort safety net, not a plan.

**3. Memory freed by Python is not always returned to the OS.** When objects die, CPython's allocator (pymalloc)
often keeps the freed memory in internal pools/arenas to satisfy *future* allocations fast, rather than handing it
back to the kernel. So your process's RSS (resident memory, what `top` shows) can stay high even after a big
structure is freed — the memory is free *to Python*, just not *to the OS*. This is normal, and it's why "I deleted
the data but the process is still huge" is usually not a leak. (A real leak is when *Python's own* live-object count
keeps climbing — see `tracemalloc` in §9.)

**4. The big-tensor / pipeline-state lesson.** A 4 GB intermediate array is freed the instant its last reference
drops — which is great, *if* you actually drop it. The usual accidental-retention culprits: it's still referenced by
an earlier pipeline-state object you kept around, captured in a closure or a logging call, or held by a module-level
cache. If you want a large object gone *now*, ensure no live reference remains (let the holding scope exit; don't
stash it in a long-lived dict). This is where your immutable `state -> new state` flow helps *and* hurts: it avoids
cycles, but if you keep every intermediate `state` in a list "for tracing," you keep every big field those states
reference alive too. Trace with summaries, not with the whole object.

**5. Caches should hold weak references.** A cache that holds normal (strong) references keeps its entries alive
forever — by definition the cache *is* a reference, so refcount never hits zero. If you want "cache it *if* it's
alive elsewhere, but don't keep it alive *just* for the cache," use `weakref` / `WeakValueDictionary`: a weak
reference doesn't increment the refcount, so the object can still die when all *strong* references drop, and the
cache entry quietly disappears. This is the right tool for big-object memoization and observer registries (and it
sidesteps a common cycle source, too).

**6. Cycles aren't a *bug*, but they delay reclamation.** A cycle is freed only on the next cycle-collector pass, not
immediately — so cyclic structures live longer than acyclic ones, and break determinism. If you have a hot,
short-lived structure that forms cycles (e.g. a parser building a tree with parent pointers), either break the cycle
explicitly when done (`node.parent = None`) or use `weakref` for the back-edge so the structure stays acyclic for the
refcounter. The general principle, straight from §5: **prefer acyclic, one-directional structure; make back-edges
weak.**

---

## 8. Check your understanding

Jot a one-line answer to each before our Q&A — we'll dig into whichever are fuzzy.

1. In CPython, *when exactly* is a heap object's memory reclaimed under reference counting? Name three different
   Python operations that cause an `INCREF` and three that cause a `DECREF`.
2. Why can't reference counting alone ever reclaim `a = {}; b = {}; a['x'] = b; b['x'] = a; del a; del b`? Draw what
   the refcounts are after the two `del`s, and say in one sentence what's true about reachability that the counts
   can't see.
3. What problem does the *cycle collector* solve that refcounting can't, and what does "generational" buy it? Why
   does it track lists/dicts/instances but not plain ints and strings?
4. State the causal chain from "reference counts are not atomic" to "CPython has a GIL." Then: name two distinct
   techniques PEP 703 uses to keep refcounting correct *without* a single global lock, and what each one optimizes.
5. Your colleague says "I call `del big_array` and `gc.collect()` but `top` still shows the process using 6 GB —
   it's a leak." Give two *non-leak* explanations consistent with everything above.
6. Why is `with open(path) as f:` the right way to manage a file, and "let the file object get garbage-collected"
   the wrong way — even though on CPython the latter *usually* works? What does "usually" depend on?
7. (Stretch / your wheelhouse) Connect this section to your §10d graph-state design: argue from first principles
   whether a frozen-dataclass + append-only-`Artifacts` pipeline can create reference cycles, and what that implies
   about how hard the cycle collector has to work on your code.

<details>
<summary>Answers</summary>

1. **At the `DECREF` that takes `ob_refcnt` to zero — immediately, synchronously, right there** (§1, §2), plus a
   cascade that `DECREF`s everything the dying object referenced. No collector has to run. **INCREF:** binding a
   second name (`b = a`), passing the object as a function argument, inserting it into a list/dict/set, setting it
   as an attribute (`self.x = obj`), capturing it in a closure. **DECREF:** `del` on a name, rebinding a name to
   something else, a function returning (its frame's locals die), removing it from a container (`container.pop()`).
   That per-operation bookkeeping is the "smeared cost" in §1's table.
2. **Because each dict's count is stuck at 1, held up by the other** — after `del a; del b` the names are gone but
   `a`'s entry still references `b` and `b`'s still references `a`, so both sit at refcount **1**, never 0, never
   freed (§3). The reachability fact the counts can't see: **nothing outside the pair can reach either object — the
   two surviving references form a closed loop with no entry point.** Refcounting is a purely *local* measurement;
   "is there a path from a root?" is a *global* property, which is exactly what a tracing collector computes.
3. **It reclaims unreachable reference cycles — the one case refcounting provably can't** (§3, §4). **Generational**
   buys it cheapness: by the **weak generational hypothesis** most objects die very young, so gen 0 is scanned
   often and is small, while survivors are promoted to gen 1 and gen 2 and re-examined progressively less — you
   spend attention where the garbage actually is instead of rescanning long-lived structures. It tracks only
   **container** objects because a plain `int`, `float` or `str` **holds no references to other objects**, so it
   can't be a link in a cycle — excluding them is free correctness, not a heuristic.
4. **The chain:** `Py_INCREF`/`Py_DECREF` are `ob_refcnt++`/`--`, a **non-atomic read-modify-write** (load, add,
   store); shared objects like `None`, `True`, small ints and interned strings are touched by every thread
   constantly; two threads interleaving lose an update, so a count reads 4 when it should be 5, one `DECREF` too
   many frees a live object → **use-after-free** and a corrupt interpreter. Serializing every refcount mutation
   with **one global lock** is the brute-force cure — that is the GIL (§6). **PEP 703's two:** **immortal objects**
   (PEP 683) pin the count of `None`/`True`/small ints/interned strings at a sentinel so `INCREF`/`DECREF` become
   **no-ops** — it removes synchronization entirely from the hottest, most-shared objects; **biased reference
   counting** gives each object an **owning thread** that mutates a cheap local non-atomic count, with a separate
   shared atomic count for other threads — it optimizes the common case where an object is only ever touched by its
   creator, so you pay the atomic only for genuinely cross-thread objects.
5. **(a) Freed by Python is not returned to the OS** — pymalloc keeps the memory in its own pools and arenas to
   serve future allocations fast, so RSS stays high while the memory is free *to Python* (§7.3). **(b) `del` freed
   nothing, because that wasn't the last reference** — the array is still in a list, a closure, a module-level
   cache, or a held traceback, so the `DECREF` just un-stuck one name tag (§7.1, §7.4). Neither is a leak. The
   discriminator is `tracemalloc` snapshot diffs (§9): a **real** leak is Python's *live-object* count climbing
   without bound, not RSS being high once.
6. **Because `with` desugars to `try/finally`, so `close()` runs on every exit path — exception, `return`, `break`
   — and releases the OS file descriptor deterministically, regardless of refcounts** (§7.2, §10a). Leaning on
   collection is the third approach §10a names: **no `close()` at all**, hoping `file.__del__` runs. "Usually
   works" depends on **CPython's refcounting timing being both deterministic and prompt** — which fails if you run
   on PyPy or Jython (pure tracing GC: the descriptor stays open until the next collection), or if any lingering
   reference delays the drop (a cycle, a logged traceback pinning the frame). Keep the two lifetimes apart:
   **closing is a resource operation, freeing is a memory operation** (§10a).
7. **It (almost) can't create cycles — the structure is a DAG by construction** (§5). A cycle needs some object to
   eventually point *back* at an object that points at it; with `frozen=True` you can never rebind a field after
   construction, and `Artifacts.add` returns a *new* store, so a new state can reference old artifacts but an old
   artifact can never be made to reference the new state. You only ever build new nodes that point at existing
   ones — edges always run backwards in time, which forbids a loop. **Implication: the cycle collector stays nearly
   idle on your code**, every object dies promptly at its last `DECREF`, and reclamation stays deterministic. The
   caveat is the §10c "frozen is shallow" hole — a mutable `extra` dict you poke in place could still close a loop.
   Cycles are a hallmark of **mutable, bidirectional** structure (parent↔child, observer↔subject), which this
   design refuses to build.

</details>

---

## 9. Optional: get your hands dirty (15–20 min)

Python can *show* you every claim in this section.

```python
import sys, gc, weakref

# (a) Watch the refcount move. Remember getrefcount adds 1 for its own argument.
obj = [1, 2, 3]
print("after creation:", sys.getrefcount(obj))   # 2  (name "obj" + the arg)
alias = obj
print("after alias:   ", sys.getrefcount(obj))    # 3
container = [obj]
print("after container:", sys.getrefcount(obj))   # 4
del alias; container.pop()
print("back to:        ", sys.getrefcount(obj))    # 2

# (b) Make an unreachable cycle and prove the cycle collector reclaims it.
class Node:
    def __del__(self): print("  freed:", self.name)
    def __init__(self, name): self.name = name; self.partner = None

gc.disable()                       # turn OFF the cycle collector to see the leak
a = Node("A"); b = Node("B")
a.partner = b; b.partner = a       # cycle
del a, b                           # no __del__ fires — they're leaked (refcount stuck at 1)
print("after del (gc off): nothing freed yet")
gc.enable()
print("collected:", gc.collect())  # forces a pass → 'freed: A' / 'freed: B' print here

# (c) Compare: a NON-cyclic object dies immediately on last del, no collector needed.
c = Node("C"); del c               # 'freed: C' prints INSTANTLY, before any gc pass

# (d) See the generational machinery.
print("counts:    ", gc.get_count())       # (gen0, gen1, gen2) since last collections
print("thresholds:", gc.get_threshold())   # (700, 10, 10) by default

# (e) Weak references: a cache that does NOT keep its value alive.
cache = weakref.WeakValueDictionary()
big = Node("BIG"); cache["k"] = big
print("in cache:", "k" in cache)            # True — but it's a WEAK ref
del big                                      # last STRONG ref gone → 'freed: BIG' prints
print("still cached?", "k" in cache)        # False — entry vanished with the object

# (f) Immortality (Python 3.12+): None's refcount is a pinned sentinel, not a real count.
print("None refcount:", sys.getrefcount(None))   # a huge constant — None is immortal
```

For real diagnosis, the two tools to know:
- **`tracemalloc`** (stdlib) — snapshots of *Python-level* allocations; diff two snapshots to find what's actually
  growing. This distinguishes a true leak (live objects climbing) from "RSS (resident set size) high but Python memory flat" (§7.3).
- **`gc.get_objects()` / `objgraph`** — when you suspect a cycle or a surprise reference keeping something alive,
  these let you find *what* still points at an object you expected to die.

Bring anything surprising to our chat — especially whatever (b) vs (c) does, and the `None` refcount in (f).

---

## 10. Applied — captured from our 2026-06-13 session

The body held; the session was you doing what you do — taking the section's prescriptions into contact with
**concrete code** and a **real production leak**, and pressure-testing them until the precise distinction fell out.
Two threads, distilled so you can re-derive them.

### 10a. `with` vs manual `close()` vs the GC — resource lifetime is *not* object lifetime

You started by stress-testing a snippet (appending the open file object to a list *inside* its `with` block), then
sharpened to the real question: **from the GC's point of view, what is the difference between `with open(path) as f:`
and `f = open(path); ...; f.close()`?**

The keeper: **from the GC's point of view there is none.** Both create exactly one heap file object; both leave the
name `f` *still bound* after the block (`with` is not `del`, and it introduces no new scope — `f` leaks into the
enclosing function scope either way); and in both the *object* is freed at the identical moment — when `f`'s last
reference drops, by reference counting (§2). **Neither `with` nor `close()` frees the object.**

The reframe you pulled out of that — the sentence to keep:

> **Closing is a *resource* operation; freeing is a *memory* operation — and the GC only ever does the second.**

Two orthogonal lifetimes, which the single name `f` made it tempting to conflate:

| | governed by | ends when |
|---|---|---|
| **resource** (open ↔ closed) | `with` / `close()` | block exit — deterministic, scope-bound |
| **object** (alive ↔ freed) | reference counting | last reference drops |

So after the close runs (implicitly in approach 1, explicitly in 2) you are left — in *both* — with a live, **closed**
file object on the heap until `f` is collected. That's exactly the `my_list.append(f)` trap restated: a *live
reference to a dead resource*. The trap isn't a GC bug; it's the two lifetimes diverging.

Where the two approaches *do* differ is **not GC at all** — it's **exception safety**: `with` desugars to
`try/finally`, so `close()` runs on *every* exit path (exception, `return`, `break`); the manual `close()` is skipped
if the logic raises. Pure resource-land. The garbage collector is not involved in the difference.

And that resolved why the section says *"use `with`, **never** the garbage collector"* — the rule targets a **third**
approach that *neither* of yours is: `f = open(path)` with **no close at all**, leaning on the finalizer
(`file.__del__`) to close the fd whenever the object eventually gets collected. *That* is "using the GC for cleanup":
non-deterministic timing, broken on PyPy/tracing GC, delayed indefinitely by any lingering reference (a cycle, a
logged traceback). Approaches 1 and 2 both *avoid* it; the choice between them is exception safety. So the rule isn't
"1 vs 2" — it's **"1-or-2, never 3."**

### 10b. The fab image-processing leak — your `gc.collect()` fix was also a *diagnosis*

You brought a real one: years ago in the fab, a colleague's custom image-processing script crashed after ~10 images
(a memory leak); you fixed it with a per-iteration `gc.collect()` and asked whether there's a better way **without
touching the leaking function.**

The first insight is that **your fix doubled as a diagnosis.** `gc.collect()` reclaims *only* cyclic garbage (§3). Had
the leak been a growing strong reference — a module-level cache, an unclosed fd, a C-level `malloc` — `gc.collect()`
would have done **nothing**. It *worked*, therefore the leak is **reference cycles created inside `process()`**, each
small cycle pinning a **huge** image buffer (§7.6: a tiny cycle holds a giant array hostage).

Why it crashed at ~10 images and not 10,000 — the §4 detail: the automatic collector triggers on object **count**
(the `700` gen-0 threshold), **not bytes**. Image work allocates a *handful* of *enormous* objects per image, so the
count threshold never trips before you exhaust *memory*. Your per-iteration `gc.collect()` is the brute-force
correction for that count-vs-bytes blindness.

Alternatives without touching `process()`, ranked by robustness:

1. **Tune, don't force** — `gc.set_threshold(50, 5, 5)` makes automatic collection fire sooner. **Weaker than what
   you already did**: still count-based, so it's guessing at the wrong variable and can still OOM (out of memory) on few-but-huge
   objects. Your explicit per-loop collect is the *more reliable* form of the same idea, not a worse one.
2. **Process isolation — the robust answer.** Run `process(image)` in a **child process**
   (`ProcessPoolExecutor(max_tasks_per_child=1)`, or `multiprocessing.Pool(maxtasksperchild=1)`); when the child
   exits, the OS reclaims **all** of its memory — *regardless of what kind of leak it is.* This is **strictly stronger
   than `gc.collect()`**, which only worked *because* the leak happened to be cyclic; process isolation survives a
   non-cyclic or C-level leak too. It's the standard production pattern for an un-fixable leaky worker (gunicorn
   `max_requests`, Celery `worker_max_tasks_per_child`). The one knob — `maxtasksperchild` — trades a memory ceiling
   against process-respawn + pickle overhead.

The principle you landed on:

> **`gc.collect()` *cleans up* a leak; process isolation *outlives* it.** When you can't touch the leaking code,
> don't reclaim the garbage — contain the leak in something the OS will reap.

A nice closing symmetry between the two threads: 10a is *"the GC won't free what you still reference"* (a reference
keeps an object alive longer than you meant); 10b is *"the GC can't free what refcounting can't reach"* (a cycle
keeps an object alive that nothing references). Both are the same lesson from opposite sides — **reclamation is
governed by reachability, and your job is to control what's reachable**, whether by dropping references (10a) or by
not building cycles / containing the blast radius (10b).

---

## References (optional, for depth)

*(All links verified live 2026-06-13.)*

- **[CPython `InternalDocs` — "Garbage collector design"](https://github.com/python/cpython/blob/main/InternalDocs/garbage_collector.md)**
  — the authoritative source, straight from the source tree. Covers reference counting, the cycle-detection
  algorithm (the scratch-refcount trick in §4), the generational scheme and thresholds, *and* the differences
  between the default and free-threaded builds. This is the one to read if you read one.
- **[Python docs — `gc` module](https://docs.python.org/3/library/gc.html)** — the practical interface: `collect()`,
  `disable()`, `get_count()`, `get_threshold()`, generations, debug flags. Pairs with §4 and the §9 exercises.
- **[Python docs — `weakref` module](https://docs.python.org/3/library/weakref.html)** — weak references,
  `WeakValueDictionary`/`WeakKeyDictionary`; the §7.5 cache lesson. Short and worth skimming.
- **[PEP 703 — Making the Global Interpreter Lock Optional in CPython](https://peps.python.org/pep-0703/)** — the
  free-threading design (accepted Oct 2023; experimental in 3.13, supported in 3.14). Biased reference counting,
  deferred RC, per-object locking, the cycle collector in a no-GIL world. The frontier layer for §6 — pitched right
  at your level.
- **[PEP 683 — Immortal Objects, Using a Fixed Refcount](https://peps.python.org/pep-0683/)** — the prerequisite
  trick behind §6's "immortal objects": why pinning `None`/`True`/small-ints' refcount makes their INCREF/DECREF
  free and unlocks no-GIL. Explains the `getrefcount(None)` mystery from §9(f).
- **[Computer Systems: A Programmer's Perspective (Bryant & O'Hallaron)](https://csapp.cs.cmu.edu/)** — for the
  language-agnostic GC chapter (mark-and-sweep, reachability, the dynamic-allocation picture under all of this).
  The C-side deep version, continuous with §1's heap material.

---

### What's next
✅ **Finalized 2026-06-13.** Marked done in `courses/plan.md`; §10 captures the `with`-vs-`close()`-vs-GC distinction
(10a) and the fab image-leak war story + process-isolation fix (10b). With §1 (the map + the pointer model) and §2
(who frees the heap) done, the last IOU in Chapter 2 is:
- **§3 — "Out of memory" for real:** what physically happens when the heap can't grow; the difference between a
  *leak* and *legitimately too much*; virtual memory, paging, and the **OOM killer**; and the concrete one you feel —
  *why a 16 GB model won't load on a 12 GB GPU*, and what "CUDA (Compute Unified Device Architecture) out of memory" is actually telling you. That section
  ties §1's address space + this section's allocator picture to the hardware limits you already reason about well.

Per the Phase-1 interleave, the parallel threads remain **M04 Ch1 §2 (tracing data flow)** on the SWE (software engineering) side and
**M12 Ch2 §2 (video — DiT/Sora)** on the AI side — say the word if you'd rather advance one of those instead of
finishing M01 Ch2 with §3.
