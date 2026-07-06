# Upskilling Plan — Course Track

> **Status: v2 DRAFT.** Revised per your kickoff feedback (deeper foundations, cloud-from-zero,
> full cyber-security track). Per `prompts/000-project-setup.md` this is still yours to revise —
> edit freely or tell me in chat. You've asked me to set the sequence; you'll steer mid-way.

Author of plan: Claude (calibrated against your self-description + a survey of `aquarium-main` and
`arena-concept-experiment`).
Last updated: 2026-06-13

---

## How to use this file

- This file is the **course track** roadmap and progress tracker. The **reading track** lives in
  `upskill-readings/` and runs in parallel; it is not scheduled here.
- Daily flow (from the project setup): you say *"Prepare today's course material"*, I generate a
  section as `courses/{NN}-{module}/{NN}-{chapter}/{NN}-{section}.md`, we Q&A, then you say
  *"finalize"* and I rewrite that section to fit how you actually think + update the status below.
- **Decisions baked in** (kickoff): **balanced interleave** across the three scopes ·
  **concept-first, light coding** · **deep, low-level foundations** (you like to understand how
  things work underneath) · examples drawn from your repos *but not limited to them*.

**Status legend:** ⬜ not started · 🔵 in progress · ✅ finalized · ⏭️ skipped (you already know it)

---

## Your snapshot (the version this plan is tuned to)

Full detail lives in [`agent-docs/learner-profile.md`](../agent-docs/learner-profile.md). In short:

- **Background:** PhD applied physics, 10 yrs semiconductor failure analysis → ~1 yr AI Engineer.
  Strong analyst, fast learner who wants to understand things from first principles.
- **Real strengths:** Python; LLM integration (practitioner); pragmatic distributed-systems patterns.
- **Cloud — corrected:** *not* a prior strength. Zero cloud before this job; learned AWS/GCP
  just-in-time for projects. Solid on the components you've used, blank beyond them. Want the
  fundamentals + AWS vs GCP vs Azure.
- **Behind:** code decomposition, testing, type safety, frontend/JS fundamentals, LLM eval, and the
  deep CS/security fundamentals this plan is built to supply.
- **Style:** mostly vibe-codes; goal is to **read & understand** code with AI help, not hand-write it.

> **On the reference repos:** `aquarium-main` and `arena-concept-experiment` are used for grounded
> examples, but material is **not limited to them**. They are **actively maintained and may be heavily
> refactored** — so I'll treat their current code as illustrative, not fixed, and won't build lessons
> that break when they change. Where a lesson surfaces a genuine improvement, you may implement it
> directly in those repos.

---

## Guiding principles

1. **Foundations first, and deep.** You learn best from the low level up — how the machine, OS,
   network, and database actually work — so the early phases prioritise durable fundamentals over
   tools-of-the-month.
2. **Concept-first.** Each section builds a mental model and teaches you to *read/judge* code and
   trade-offs. Coding exercises are optional and grounded in real code.
3. **Interleaved.** Every phase still touches CS + software-engineering + AI so motivation stays high
   and ideas reinforce each other — but the centre of gravity early on is fundamentals.
4. **Comparative.** Where there are competing technologies (Linux/macOS/Windows, SQL/graph/NoSQL,
   AWS/GCP/Azure, framework vs framework-less), the goal is to understand the *differences and
   trade-offs*, not memorise one.
5. **Spaced recall.** Periodic lightweight review checkpoints, because retention > coverage.

---

## Modules

Coherent topic units, numbered by area. The **interleaved study sequence** further down sets the
actual order. Folder paths follow your numbering convention.

### M01 — How Computers & Operating Systems Work  ·  `courses/01-computers-and-os/`
*Why for you: you orchestrate code across machines but the layer underneath is implicit. Make it explicit, bottom-up.*
- **Ch1 — The execution model:** compilation vs interpretation; what Python actually does; the call stack; machine code & the CPU at a glance.
- **Ch2 — Memory:** stack vs heap; references vs values; what "out of memory" really means; garbage collection.
- **Ch3 — Processes, threads & concurrency:** processes vs threads vs async; the GIL; parallelism vs concurrency; your `asyncio` usage explained.
- **Ch4 — I/O, syscalls & the kernel boundary:** blocking vs non-blocking I/O; what a syscall is; why I/O dominates latency.
- **Ch5 — OS landscape — Linux vs macOS vs Windows:** kernels, filesystems, process & permission models; why Linux runs the servers; how containers relate to the kernel.

### M02 — Networking & The Web  ·  `courses/02-networking-and-web/`
*Why for you: you ship API Gateway + WebSockets but largely on intuition. Solidify the protocols, bottom-up.*
- **Ch1 — How a request travels:** DNS, IP/TCP, the OSI mental model (just enough), latency budgets.
- **Ch2 — HTTP deeply:** methods, status codes, headers, idempotency, caching, content negotiation.
- **Ch3 — TLS & secure transport:** what HTTPS guarantees, certificates, the handshake (conceptually).
- **Ch4 — Real-time:** REST vs WebSockets vs SSE vs long-polling — and which your arena turns should use.

### M03 — Databases & Storage (from first principles)  ·  `courses/03-databases-and-storage/`
*Why for you: you want the fundamental design of relational vs graph DBs, and how they handle efficiency and security.*
- **Ch1 — The relational model from the ground up:** relations, keys, normalization, how a query is planned & executed, B-tree indexes.
- **Ch2 — Transactions, concurrency & consistency:** ACID, isolation levels, locking, MVCC; your advisory-lock pattern explained.
- **Ch3 — Graph, document & key-value databases:** their data models and internal design; when each beats relational; graph-DB internals; the CAP trade-off.
- **Ch4 — Efficiency:** indexing strategies, reading a query plan, partitioning/sharding, replication, caching, hot keys.
- **Ch5 — Database security:** access control & least privilege, encryption at rest/in transit, injection, auditing.

### M04 — Writing Code That Lasts  ·  `courses/04-code-that-lasts/`
*Why for you: your clearest gap. Directly attacks the 2,400-line and 3,270-line files.*
- **Ch1 — Reading code well:** navigating an unfamiliar codebase; tracing data flow.
- **Ch2 — Decomposition:** functions, modules, boundaries, cohesion & coupling; refactoring a monolith.
- **Ch3 — Design patterns you'll actually meet:** strategy, factory, adapter, dependency injection — spotted in real code.
- **Ch4 — Naming, comments & code smells:** what to keep, what to delete, when AI-generated code is lying to you.

### M05 — Types & Correctness  ·  `courses/05-types-and-correctness/`
*Why for you: loose `Dict[str, Any]` everywhere; zero TypeScript. Types are free bug-catching.*
- **Ch1 — What a type system buys you:** static vs dynamic; the value of contracts.
- **Ch2 — Python typing in practice:** type hints, `mypy`/`pyright`, **`dataclass` (incl. `frozen`/`slots`/`replace`) & `typing.Protocol`** *(queued from M01 Ch2 §1 2026-06-12 — he flagged dataclass as unfamiliar; also slated as a near-term reading)*, Pydantic as runtime validation; dataclass vs Pydantic vs NamedTuple.
- **Ch3 — TypeScript fundamentals:** just enough to read & trust your frontend; migrating JS → TS.

### M06 — Testing & Quality  ·  `courses/06-testing-and-quality/`
*Why for you: tests are sparse/absent in solo work. Build the habit and the judgment.*
- **Ch1 — Why & what to test:** the testing pyramid; what's worth testing; cost vs confidence.
- **Ch2 — Unit testing:** structure, fixtures, mocking external services (LLMs, AWS, DBs).
- **Ch3 — Integration & end-to-end:** when, how, and the trap of testing too much.
- **Ch4 — Quality gates:** coverage (and its lies), linting/formatting, pre-commit, CI checks.

### M07 — Software Architecture & System Design  ·  `courses/07-architecture-and-system-design/`
*Why for you: your stated "architect" goal. The high-leverage module.*
- **Ch1 — Architectural styles:** monolith vs microservices vs serverless vs event-driven — trade-offs.
- **Ch2 — Designing for scale:** load, statelessness, horizontal scaling, queues, back-pressure.
- **Ch3 — The system-design method:** requirements → estimates → components → bottlenecks (interview-style, applied to your apps).
- **Ch4 — Cost & efficiency:** choosing libraries/services for cost and latency.

### M08 — Cloud Computing from Zero  ·  `courses/08-cloud-from-zero/`
*Why for you: corrected priority — built assuming no cloud foundation, ending in a real AWS/GCP/Azure comparison.*
- **Ch1 — What "the cloud" actually is:** virtualization, VMs vs containers, multi-tenancy, regions & availability zones.
- **Ch2 — The core service categories:** compute, storage, networking, identity, managed data — the mental model that maps across all providers.
- **Ch3 — Service models:** IaaS vs PaaS vs SaaS; where serverless fits; the shared-responsibility model.
- **Ch4 — AWS vs GCP vs Azure:** how their services map to each other, naming, relative strengths, lock-in, and how to ramp on a new provider fast.
- **Ch5 — Cloud cost & efficiency:** pricing models, reading a bill, cost-aware architecture.

### M09 — DevOps & Delivery  ·  `courses/09-devops-and-delivery/`
*Why for you: explicitly named pain. You already do IaC — fill in the delivery discipline.*
- **Ch1 — Containers & images:** the Docker mental model, the kernel link, registries, dev/stg/prod parity.
- **Ch2 — Infrastructure as Code:** what your CDK is really doing; declarative infra; drift; Terraform vs CDK.
- **Ch3 — CI/CD pipelines:** build → test → deploy; staging gates; rollbacks; blue-green/canary.
- **Ch4 — Observability:** structured logging, metrics, distributed tracing (you have Langfuse — generalize it).

### M10 — Cyber Security  ·  `courses/10-cyber-security/`
*Why for you: explicitly requested as its own track. Broad and defensive, deploy-focused.*
- **Ch1 — The security mindset & threat modeling:** the CIA triad, attacker thinking, attack surface, trust boundaries.
- **Ch2 — Cryptography you must know:** hashing vs encryption, symmetric vs asymmetric, signing, certificates (deepens M02 Ch3).
- **Ch3 — Authentication & authorization:** sessions, JWT (your Firebase flow explained), OAuth/OIDC, API keys, RBAC.
- **Ch4 — Web application security — OWASP Top 10:** injection, XSS, CSRF, SSRF, secrets handling, the vulns that actually bite.
- **Ch5 — Network & infrastructure security:** firewalls, VPC/network isolation, least privilege in the cloud, zero-trust ideas.
- **Ch6 — Supply chain & secure SDLC:** dependency risk, secrets scanning, SAST/DAST (your `bandit` step), shifting security left.

### M11 — Frontend Foundations  ·  `courses/11-frontend-foundations/`
*Why for you: weakest area. Built specifically because you have no JS/frontend background.*
- **Ch1 — How the browser works:** DOM, the render pipeline, events, the JS runtime/event loop.
- **Ch2 — JavaScript you must own:** closures, async/promises, modules, `this` — the parts that bite.
- **Ch3 — The React mental model:** components, state, props, hooks, re-render rules (decoding your ArenaPage).
- **Ch4 — Frontend architecture:** state management, data fetching (why React Query), component decomposition.

### M12 — The Model Landscape  ·  `courses/12-model-landscape/`
*Why for you: goal is to understand all model types, not just LLMs.*
- **Ch1 — How modern models work (conceptually):** transformers, tokens, embeddings, training vs inference.
- **Ch2 — Beyond text:** image/diffusion, multimodal, audio/speech, embedding models — what each is for.
- **Ch3 — Choosing a model:** the current frontier (incl. Claude 4.x family), capability vs cost vs latency, open vs hosted.

### M13 — Building with LLMs  ·  `courses/13-building-with-llms/`
*Why for you: your daily work. Level up from "wiring it" to "engineering it".*
- **Ch1 — Prompting & structured output:** reliable JSON, schemas, where your pipeline can be hardened.
- **Ch2 — Context & retrieval (RAG):** chunking, embeddings, retrieval, when RAG is the wrong tool.
- **Ch3 — Tool use & function calling:** the modern pattern your graph-lite pipeline approximates.
- **Ch4 — Reliability & cost:** retries, validation, prompt caching, latency/cost engineering.

### M14 — Agentic Systems  ·  `courses/14-agentic-systems/`
*Why for you: you built a framework-less agent pipeline — understand the design space you chose within.*
- **Ch1 — What an "agent" really is:** the loop, planning, memory, when agents beat plain pipelines.
- **Ch2 — Frameworks vs framework-less:** LangGraph et al. vs your graph-lite — the real trade-offs.
- **Ch3 — Multi-agent & orchestration:** patterns, hand-offs, and their failure modes.
- **Ch4 — MCP & tool ecosystems:** how agents connect to the outside world.

### M15 — Evaluation & Observability for AI  ·  `courses/15-ai-eval-and-observability/`
*Why for you: a gap in both repos. The discipline that makes AI systems trustworthy.*
- **Ch1 — Why eval is hard:** non-determinism, what "correct" means for generative output.
- **Ch2 — Building evals:** datasets, metrics, LLM-as-judge (and its pitfalls).
- **Ch3 — Guardrails & tracing in production:** generalizing your SEA-Guard + Langfuse setup; A/B testing.

---

## Interleaved study sequence

Six phases, foundations-first. Within a phase, study the listed module-chapters **in parallel** (a
little of each per week) rather than strictly top-to-bottom. Durations assume ~2–3 hrs/day on the
course track and are estimates, not deadlines. **You can redirect at any phase boundary — or mid-phase.**

### Phase 1 — Bedrock & momentum  *(~4 weeks)*
Start at the bottom of the stack, land one immediately-useful SWE skill, and open the AI thread.
- **M01 Ch1–4** — how computers & OS work (execution, memory, concurrency, I/O)
- **M04 Ch1–2** — reading code & decomposition *(your clearest gap; instantly useful)*
- **M12 Ch2** — beyond text: image/diffusion, audio, video, TTS *(AI thread — recalibrated 2026-06-10:
  M12 Ch1 LLM-fundamentals skipped as known; non-text models are the genuine AI gap. Pitched at frontier
  level.)*

### Phase 2 — Systems, web & data foundations  *(~5 weeks)*
- **M01 Ch5** — Linux vs macOS vs Windows
- **M02** — networking & the web
- **M03 Ch1–2** — relational model, transactions
- **M13 Ch1–2** — building with LLMs (prompting/output, RAG)

### Phase 3 — Data depth & engineering discipline  *(~5 weeks)*
- **M03 Ch3–5** — graph/NoSQL design, efficiency, database security
- **M05** — types & correctness
- **M06** — testing & quality
- **M04 Ch3–4** — design patterns & smells *(carry-over)*

### Phase 4 — Architecture & the cloud  *(~5 weeks)*
- **M07** — software architecture & system design *(your architect goal)*
- **M08** — cloud from zero (incl. AWS vs GCP vs Azure)
- **M14 Ch1–2** — agentic systems

### Phase 5 — Delivery, security & frontend  *(~6 weeks)*
- **M09** — DevOps & delivery
- **M10** — cyber security *(full track)*
- **M11** — frontend foundations *(your weakest area — paced gently)*
- **M15** — AI evaluation & observability

### Phase 6 — Integration & capstone  *(ongoing)*
Apply everything to real code (remembering the repos may have moved on — re-survey before diving in):
- Refactor a monolith using M04/M05/M06, or implement a real improvement the course surfaced.
- Run a full system-design exercise on one of your apps (M07).
- Remaining chapters: **M12 Ch2–3, M13 Ch3–4, M14 Ch3–4.**

---

## Progress tracker

| Module | Chapter | Status | Finalized section files | Notes |
|---|---|---|---|---|
| M01 Computers & OS | Ch1 Execution model | ✅ | §1 `01-execution-model/01-source-to-running.md` ✅ (2026-06-08); §2 `01-execution-model/02-the-call-stack.md` ✅ (2026-06-09); §3 `01-execution-model/03-machine-code-and-cpu.md` ✅ (2026-06-09) | **Ch1 complete.** §3 (machine code & CPU): ISA, datapath, `call`/`ret` as PC save/restore, memory hierarchy & cache locality, pipelining/branch-prediction/speculation (+Spectre→M10), clock wall→multicore→concurrency mandate (→Ch3), SIMD/GPU. He knew the body; session ran on *his* questions one layer past it → §11 applied: multi-core private/shared topology + MESI coherence + false-sharing/memory-ordering (→Ch3); GPU hierarchy (SM≈core, latency-hiding via thread oversubscription not caches, software-managed Shared Memory, FlashAttention/memory-bound inference); what CUDA is (software stack not HW, PTX→SASS JIT = §1 callback, CUDA moat, alternatives). Next: M04 Ch1 / M12 Ch1 (Phase 1). |
| M01 | Ch2 Memory | ✅ | §1 `02-memory/01-stack-heap-and-variables.md` ✅ (2026-06-12); §2 `02-memory/02-garbage-collection.md` ✅ (2026-06-13); §3 `02-memory/03-out-of-memory.md` ✅ (2026-06-14) | **Ch2 COMPLETE (2026-06-14).** **§3 (out of memory) — finalized 2026-06-14.** The body went untouched in session; he drove the *entire* Q&A into **LLM-serving memory** from his own ops experience (vLLM, llama.cpp), and the three threads collapsed to one principle — *don't move/duplicate/over-reserve the big thing.* §11 captures: **(11a) PagedAttention** — his "contiguous KV-cache too huge → external frag" hypothesis caught the *smallest* of three wastes; dominant = **internal frag from forced over-reservation** (contiguity + dynamic growth → reserve `max_seq_len` → ~60–80% waste); fixed-size blocks kill external frag *by construction*; missed dimension = CoW block sharing; §1 paging mapping confirmed. **(11b) vLLM `gpu_memory_utilization`** — corrected his "paging isn't free" guess (paging = compute cost inside the pool, wrong axis); it's the **ceiling** sizing the KV pool, and the headroom is a **derating safety margin** against an under-estimated *variable* peak (no GPU swap → exceed = `CUDA OOM` crash); semiconductor *derating* framing landed. **(11c) llama.cpp `-ngl` offload** — purely-CPU blocks (compute follows weights); **sequential** (transformer dependency chain → additive latency; decode bandwidth-bound → CPU layer ~10–40× → knee/cliff); traffic tiny because **weights pinned, only ~8 KB activations cross PCIe**; decode-vs-prefill caveat. **Body:** Last IOU of Ch2. Body: virtual vs physical address space (the map-vs-territory framing; VIRT/VSZ vs RES/RSS); the capacity hierarchy (RAM→swap, demand paging, minor vs major faults, thrashing, why prod runs little/no swap & k8s disabled it); what `malloc` really does (Linux **overcommit** → alloc succeeds, the *write* faults later → can't return an error → OOM killer); **the four signatures** (in-proc `MemoryError`+traceback · kernel OOM-killer `Killed`/exit 137/`dmesg` · **cgroup** `OOMKilled`/exit 137 = his AWS/Lambda/ECS reality · `CUDA OOM`) with a one-glance diagnostic table; **leak vs legitimately-too-much** (§2 carry-over: shape-over-time + `tracemalloc`; gc.collect→cyclic; fix is *touch less* not *free more*); freed≠returned-to-OS + **fragmentation OOM with free memory**; **§7 the GPU wall** (his headline — VRAM separate/small/no-swap; full budget = weights+grads+optim(Adam 2×)+activations+KV-cache+context+frag; 7B fp16=14GB won't fit 12GB; training ~4× inference; `allocated`/`reserved`/`free` + fragmentation; **vLLM PagedAttention = §1 demand-paging for the KV-cache**). §10 hands-on, §11 Applied=placeholder. Heavy callbacks: §1 address space, §2 pymalloc/RSS/cycles/process-isolation, Ch1 §3 GPU hierarchy/KV-cache/quantization, his fab leak + Lambda cold-start. **On finalize → flips Ch2 to ✅ (chapter complete).** Next options offered: M01 Ch3 concurrency (cashes the GIL keystone), M04 Ch1 §2 data-flow, or M12 Ch2 §2 video. | **§2 (garbage collection):** body = refcounting (eager/deterministic/freed-at-DECREF-to-0) + the cycle it can't reclaim + the generational cycle collector (scratch-refcount trick, 700/10/10 thresholds) + **the keystone — refcounting is *why* the GIL exists** (non-atomic `ob_refcnt++`), and PEP 703/683 free-threading (immortal objects, biased refcounting) framed as *"no-GIL is a GC engineering problem, not a lock-removal one."* Callback to §1 §10d: his immutable append-only graph state forms a **DAG → can't make cycles → keeps the collector idle**. **Session = his signature mode aimed at the GC** (§10): (10a) he stress-tested the §7.2 rule with `my_list.append(f)` inside `with`, then asked **`with` vs manual `close()` from the GC's POV** → landed **no GC difference; closing≠freeing; resource-lifetime ⊥ object-lifetime; `with` wins on exception-safety not memory; "1-or-2-never-3"** (3 = lean on `__del__`). (10b) **fab war story** — colleague's image script crashed ~10 imgs, he fixed with per-loop `gc.collect()`, asked for a better way w/o touching the fn → keepers: **`gc.collect()` working *proves* the leak is cyclic**; the **count-vs-bytes threshold blindness** explains "~10 imgs" (few-but-huge objects never trip the 700 count); **process isolation** (`maxtasksperchild=1`; gunicorn/Celery pattern) is *strictly stronger* — "**`gc.collect()` cleans up a leak; process isolation outlives it.**" Next §3 OOM. | §1 (address space; stack vs heap; names-are-pointers): pays off Ch1 §3's "a list is a million pointers" IOU. Body: process address-space map; stack = bump-pointer/automatic/bounded (→ RecursionError as railing before native-stack cliff, TCO callback to §2); heap = allocator search/GC-freed/fragments/cache-cold. Pivot: Python name = pointer to heap object, assignment copies the pointer; everything-is-an-object incl. ints. Mutability as the only built-in protection; aliasing; `==` vs `is` + small-int cache (he caught a real bug in my example: one-line `a=257;b=257;a is b` is True via compile-time const dedup — fixed). **Session went almost entirely into a SWE-design thread (→M04): pipeline state management.** §10 captures it: frames vary in size (stack Q); and the design arc — class-with-mutable-`self` makes mutation *more* implicit (temporal coupling, monolith risk); his `PipeState` read/update refinement = shallow module (Ousterhout) w/ no invariant; keeper principle = **flow immutable state via explicit signatures, inject set-once deps on `self`, never mutate in place**. §10 captures the whole arc he drove from linear → graph: 10b best-practice linear pipeline **skeleton** (frozen dataclass State + Deps DI + Step Protocol + uniform runner); 10c "can a step add a key?" = no, fixed schema by design (slots/frozen) + frozen-is-shallow gotcha; 10d **two-part state for complex/LangGraph-style graphs** he pushed to — stable `Core` + open-but-typed `Artifacts` (**"open values, closed shapes — fix the grammar not the vocabulary"**; append-only provenance-stamped store = baked-in reducer; loop guard = recursion-limit analog), full graph skeleton, reducer/Pydantic upgrade paths. **This is M14 Ch2 / M07 territory — reuse his pipeline + this skeleton there.** `dataclass`/`Protocol` flagged unfamiliar → reading queued + added to M05 Ch2. Next §2 GC (refcount + cycle collector + GIL re-entry), §3 OOM. |
| M01 | Ch3 Concurrency | ✅ | §1 `03-processes-threads-concurrency/01-concurrency-parallelism-and-the-gil.md` ✅ (2026-06-16); §2 `03-processes-threads-concurrency/02-async-deeply.md` ✅ (2026-06-25); §3 `03-processes-threads-concurrency/03-synchronization-and-races.md` ✅ (2026-06-26) | **Ch3 COMPLETE (2026-06-26).** **§3 (synchronization & races) — finalized 2026-06-26.** No questions on the body — he read it and returned a **design synthesis** instead (captured in §11 Applied): (1) *linear pipeline = no race* (one flow of control — top of the decision tree); (2) *immutable state removes the racing concern even scaling to a concurrent graph* — he reached the section's senior move independently (a data race needs a **write** to shared memory; no mutation → no write → the entire §1–§5 lock apparatus is unnecessary), the concurrency payoff of the append-only store he'd already derived in Ch1 §2 §1; (3) hasn't needed threads (I/O-bound → async is right, threads buy nothing under the GIL) — sound triage. **The one edge I sharpened:** immutability kills races on the *flowing* state; the residual care point is the **fan-in/join** — combine *functionally* (return-and-reduce over immutable results, never $N$ edges appending into one shared mutable sink) and coordinate with **structured concurrency** (`gather`/`TaskGroup`, §2), not a lock; unbounded fan-out → back-pressure (§6), a capacity question not a race. **Keeper: the senior fix for racing isn't a better lock — it's arranging not to have shared mutable state.** **Body (pitched high, went untouched):** The third leg; fuses §1 ("the GIL only hid the cheap races; free-threading makes them yours") + §2 ("the world only changes at an `await`") into one theory: a bug lives wherever a broken **invariant** is observable by another flow; the cure is to make that window mutually exclusive. **(§1)** `x += 1` = 3 bytecodes → lost-update race; **data race vs race condition** (the latter possible with only atomic ops — check-then-act); the GIL makes *bytecodes* atomic only, releases on a ~5ms timer + I/O, PEP 703 widens every window. **(§2)** critical section / lock / `with`-discipline; contention = Amdahl; coarse-vs-fine granularity dial; `Lock` vs `RLock`. **(§3, centrepiece)** the async twist — single-thread async *still* races across an `await`; **the one-question test: lock iff an `await` is inside the broken-invariant region**; `asyncio.Lock` NOT thread-safe, no timeout, non-reentrant. **(§4)** full primitive table (Lock/RLock/Semaphore/BoundedSemaphore/Event/Condition/Barrier) — `BoundedSemaphore` for caps, `Condition` **must** wait in a `while` (spurious wakeup + stolen-condition). **(§5)** deadlock = Coffman's 4 conditions, break any one; **lock-ordering kills circular-wait (the shippable fix)**; dining philosophers; livelock→randomised backoff; starvation→fairness. **(§6)** the escape — "share memory by communicating": `queue.Queue`/`asyncio.Queue` = producer/consumer + **back-pressure** via `maxsize`; actor model; **immutability (Ch1 §2 §1) = no critical section ever**. **(§7)** hardware floor — memory model / barriers / MESI (Ch1 §3 §11), broken double-checked-locking, lock-free is expert-only. 3 diagrams (lost-update sequence · do-I-need-a-lock decision tree · deadlock wait-for cycle) all visually verified; refs verified live; bilingual 中文 key-terms table (thread 线程↔執行緒, process 进程↔行程, semaphore 信号量↔號誌, queue 队列↔佇列, deadlock 死锁↔死結, the 并行 CN/TW false-friend). Next options at boundary: Ch4 I/O & kernel, or rotate to M04 Ch2 §2 / M12 Ch2 §3 (optional Ch3 §4 producer/consumer parked until a concurrent-graph pipeline needs it). | **§2 (async deeply) — finalized 2026-06-25.** One level under §1, cashing the 9b timeout keeper into its mechanism. Body (held at his level, untouched): **(§1)** the event loop one tick at a time — `_ready` deque + `_scheduled` heap + selector; the single blocking `selector.select()`/`epoll_wait`; timer-derived timeout; the `ntodo` fairness snapshot. **(§2)** coroutine vs Future vs Task (table) + await→park→wake at the `send`/`throw` level (Task.__step driving the coroutine); `await coro` ≠ a Task → two awaits serial. **(§3)** spawning-primitives table keyed on *sibling-on-error* behaviour (gather orphans siblings; `return_exceptions=True`=harvest; as_completed=stream/persist). **(§4)** structured concurrency — go-statement-considered-harmful (Smith/Trio nurseries), `TaskGroup`+`ExceptionGroup`/`except*` (PEP 654), fail-fast vs harvest. **(§5, centrepiece)** cancellation = an exception *injected* (`coro.throw(CancelledError)`) at the parked `await`; only lands at an await; timeout beats silence but `return_exceptions` can't; `CancelledError`∈BaseException → must re-raise; shield/finally/uncancel. **(§6)** footgun gallery (fire-and-forget GC + set/discard; gather orphans; swallowed CancelledError; blocking the loop; unretrieved exceptions; `asyncio.run` nesting/Jupyter). 3 Mermaid diagrams visually verified; refs verified live. **§10 Applied (2026-06-25 session):** short clean session — he drove **only check-Q 8.5** (timeout around a non-yielding `while True` CPU loop). Correctly predicted **"never fires"** and — unusually — named the *dominant* reason, not a mis-rank. Sharpened into **two independent reasons**: (R1, dominant) the timeout is *not a watchdog thread* — it's a timer on the *same loop*, and the un-yielding `__step` callback never returns → `_run_once` never ticks → the timer never fires → `task.cancel()` is never even called (the blocking-the-loop footgun in its purest form); (R2, independent) even if cancel ran, `CancelledError` lands only at an `await`, of which there are none → intrinsically uncancellable. `Ctrl-C` works (SIGINT at C level) — the tell that it's the loop that's stuck. Keeper: *timeout protects a hanging `await` (silence/I/O — 9b), never a non-yielding CPU loop; that needs `run_in_executor`→process pool, not a timeout.* Mirror image of the 9b parked-vs-blocking split, taken to its limit. **§1 finalized 2026-06-16.** Body (two orthogonal axes via Pike + a 2×2 *table* — Mermaid couldn't lay out the grid; multiplexing framing · processes/threads/async cost table · the GIL pinned down: what it locks, ~5ms switch interval, releases on I/O + in good C extensions → "threads parallelize only GIL-released work" · CPU-vs-IO decision + `run_in_executor` hybrid · free-threading/PEP 703) held at his level and went **untouched** — he drove the whole session **applying** it to an **LLM-eval pipeline**. §9 (Applied) captures three threads: **(9a)** "batch" = 3 mechanisms (client fan-out / Batch API / continuous batching); the `openai` chat "batch" he uses *is* §1–§4 async fan-out, ceiling = rate limit not GIL (06-09 callback), ties to his 06-15 continuous-batching reading. **(9b)** `asyncio.gather` failure mode — scheduler model right; **mis-ranked the failure** by fusing two opposite hangs: a task *parked on I/O* doesn't hang the thread (only `gather`'s join barrier waits; 999 results recoverable) vs a *blocking call* that freezes the loop (§4 footgun in parse/aggregate). Keeper: `return_exceptions` handles **errors**, only a **timeout** handles **silence** → for "response never comes," timeout is the dominant fix (Ousterhout "define errors out of existence"). **(9c)** parse/calc — lever is *push the loop into C, not thread-vs-process*; **"C library" ≠ "GIL released"** (numpy releases→parallel; json/orjson/pydantic hold→fast single-thread; lxml releases); the ladder (don't bother→C/Rust lib→ProcessPool last). Next inside Ch3: §2 Async-deeply (cancellation — cashes 9b) or §3 sync/races; or rotate scope (4th straight M01 day) to M04/M12. |
| M01 | Ch4 I/O & kernel | 🔵 | §1 `04-io-syscalls-and-the-kernel-boundary/01-the-kernel-boundary-and-syscalls.md` ✅ (2026-07-06) | **§1 (the kernel boundary & the system call) finalized 2026-07-06.** Opens the bottom-up finale of M01 and cashes Ch3 §2's IOUs: `epoll_wait`/`selector.select` are *syscalls*; a blocking `read` parks the thread *in the kernel* (why the GIL is free across I/O); "the loop's one blocking call." **Body (pitched high, went untouched):** user vs kernel mode (rings; mode-switch ≠ context-switch; kernel = privileged library in every address space, not a process); the syscall as a guarded trap at the instruction level (`rax`/`rdi`… ABI, the one fixed `LSTAR` entry, `sys_call_table` dispatch, argument validation, `sysret`, `errno`) contrasted with a function call; the cost ladder (fn call ≪ syscall ≪ context switch) with a **real log-scale latency figure** + the two rules (batch crossings · park don't spin); the **Meltdown→KPTI** callback to Ch1 §3 (`pti` active on this box); libc wrappers + the **vDSO**; a **real captured `strace`** walkthrough (fd-as-handle, buffered read = Rule 1); the frame for §2/§3 + `mmap`/`llama.cpp`; interrupts vs faults vs syscalls. 1 matplotlib fig + 1 Mermaid diagram (both visually verified); refs verified live; bilingual 中文 key-terms table (kernel 内核↔核心, syscall 系统调用↔系統呼叫, memory 内存↔記憶體, …). **§9 Applied (2026-07-06):** no body questions — he drove two **comparative portability** threads past the material (his signature "push one layer past the text"). **(9a) "Are syscalls the same on Windows/Linux?"** → keeper *separate the hardware from the contract*: the two rings, the `syscall`/`sysret` trap, the cost ladder, and even Meltdown/KPTI (Windows = KVA Shadow) are **hardware-universal**; what's per-OS is the **vocabulary** and the **stable-ABI location** — Linux freezes the contract *at the syscall* (num 0 = `read` forever; raw syscalls OK), **Windows freezes it one layer up in `ntdll`/`kernel32`** (syscall numbers/SSDT are private & shift per build). Plus the **I/O-model** split: `epoll` readiness/reactor vs Windows **IOCP** completion/proactor (visible in asyncio's `SelectorEventLoop` vs `ProactorEventLoop`; `io_uring` = Linux converging). **(9b) "x86 vs ARM, why won't x86 Windows apps run on ARM Windows?"** → keeper *the ISA is the binary's mother tongue*: different ISA = different machine-code bytes → **native impossible**; CISC/RISC with nuance (micro-ops, ISA-as-contract; fixed-4B vs 1–15B decode → power efficiency; 31 vs 16 registers); the sleeper = **strong (x86 TSO) vs weak (ARM) memory ordering** → latent data races that "worked" on x86 break on Graviton (**Ch3 §3 hardware-floor callback**); emulation (Prism/Rosetta) bridges **user-mode only** and breaks at (a) ring-0 drivers, (b) perf, (c) mixing ISAs in one process; tie-back to his **Lambda/Graviton/Docker multi-arch** + **Python arch-neutral bytecode** (Ch1 §1 callback). **Calibration:** in conceptual/systems domains he's **well-calibrated, not mis-ranked** — these were open exploratory questions; value added = *structure + naming* + wiring to owned material, not dominant-cause re-ranking (reinforces v21). **Authoring signal:** his first question exposed the material's Linux-centricity → added a §1 portability callout (hardware-universal vs Linux-specific). **This session = a Ch1 §3 / Ch1 §5 trailer** (reopen the x86/ARM memory-model hazard at M01 Ch5). **Next:** Ch4 §2 (blocking/non-blocking & `epoll`/`io_uring`, C10k) — the direct continuation; or Ch4 §3 (why I/O dominates latency); or rotate to M04 Ch2 §2 / M12 Ch2 §3. |
| M01 | Ch5 Linux/macOS/Windows | ⬜ | | |
| M02 Networking & Web | Ch1 Request lifecycle | ⬜ | | |
| M02 | Ch2 HTTP | ⬜ | | |
| M02 | Ch3 TLS | ⬜ | | |
| M02 | Ch4 Real-time | ⬜ | | |
| M03 Databases & Storage | Ch1 Relational model | ⬜ | | |
| M03 | Ch2 Transactions | ⬜ | | |
| M03 | Ch3 Graph/NoSQL design | ⬜ | | |
| M03 | Ch4 Efficiency | ⬜ | | |
| M03 | Ch5 Database security | ⬜ | | |
| M04 Code That Lasts | Ch1 Reading code | 🔵 | §1 `01-reading-code/01-navigating-an-unfamiliar-codebase.md` ✅ (2026-06-10) | §1 finalized. Already using most strategies; git confirmed as gap → reading entry queued. §11 has two real cases: environment leakage in a pipeline; understanding-driven refactoring + copy-paste inheritance in an eval repo. |
| M04 | Ch2 Decomposition | 🔵 | §1 `02-decomposition/01-cohesion-coupling-and-module-depth.md` ✅ (2026-06-18) | **§1 finalized 2026-06-18.** The conceptual core of decomposition. Body: kills "decomposition = smaller files" → complexity (change amplification / cognitive load / unknown-unknowns) → cohesion ladder → coupling ladder + the **decomposition U-curve** (xychart plot: total = within-module ↓ + between-module ↑; valley ≠ line count) → **module depth** as the unifier ($\text{depth}\approx\text{functionality}/\text{interface}$) → info hiding & leaky abstractions → when NOT to decompose (the far-wall failure modes). Two figures (U-curve + ❌shared-bag vs ✅data-flow). **§11 Applied = a full worked design case from the session** — organizing a linear pipeline of independent I/O- vs CPU-bound steps: the *logical-cohesion* trap (group files by technical kind / package-by-layer), why one-file-per-step isn't the fix, the two conflated axes (*what it does* = file layout vs *whether it waits* = interface+runner), the `contract.py`+`pipeline.py`+`runner.py`+`steps/` layout, why "interface file ≠ list of signatures" (his C-header proposal critiqued), and the fan-out bonus once I/O-ness lives in the type. **DURABLE FEEDBACK (now `agent-docs/authoring-conventions.md` rule 3):** teach comprehensively (the repos were level-calibration, NOT the course's goal); stop over-citing his repos; a Q&A snippet is a *question, not an endorsement*; prefer real-world canonical good/bad examples + failure modes he hasn't met. §1 was re-anchored to real systems (Unix I/O, Go `io.Reader`, Java stream wrappers, ORM N+1 / TCP leaks, Segment & Prime Video monolith reversals, FizzBuzzEnterpriseEdition). Next inside Ch2: §2 refactoring-in-moves, or §3 module/file boundaries; or rotate to M12 Ch2 §2 video. |
| M04 | Ch3 Design patterns | ⬜ | | |
| M04 | Ch4 Smells & naming | ⬜ | | |
| M05 Types | Ch1 Type systems | ⬜ | | |
| M05 | Ch2 Python typing | ⬜ | | |
| M05 | Ch3 TypeScript | ⬜ | | |
| M06 Testing | Ch1 Why/what | ⬜ | | |
| M06 | Ch2 Unit testing | ⬜ | | |
| M06 | Ch3 Integration/E2E | ⬜ | | |
| M06 | Ch4 Quality gates | ⬜ | | |
| M07 Architecture | Ch1 Styles | ⬜ | | |
| M07 | Ch2 Scale | ⬜ | | |
| M07 | Ch3 Design method | ⬜ | | |
| M07 | Ch4 Cost | ⬜ | | |
| M08 Cloud from Zero | Ch1 What cloud is | ⬜ | | |
| M08 | Ch2 Service categories | ⬜ | | |
| M08 | Ch3 IaaS/PaaS/SaaS | ⬜ | | |
| M08 | Ch4 AWS vs GCP vs Azure | ⬜ | | |
| M08 | Ch5 Cost & efficiency | ⬜ | | |
| M09 DevOps & Delivery | Ch1 Containers | ⬜ | | |
| M09 | Ch2 IaC | ⬜ | | |
| M09 | Ch3 CI/CD | ⬜ | | |
| M09 | Ch4 Observability | ⬜ | | |
| M10 Cyber Security | Ch1 Mindset/threat model | ⬜ | | |
| M10 | Ch2 Cryptography | ⬜ | | |
| M10 | Ch3 AuthN/AuthZ | ⬜ | | |
| M10 | Ch4 OWASP Top 10 | ⬜ | | |
| M10 | Ch5 Network/infra sec | ⬜ | | |
| M10 | Ch6 Supply chain/SDLC | ⬜ | | |
| M11 Frontend | Ch1 Browser | ⬜ | | |
| M11 | Ch2 JavaScript | ⬜ | | |
| M11 | Ch3 React model | ⬜ | | |
| M11 | Ch4 FE architecture | ⬜ | | |
| M12 Model Landscape | Ch1 How models work | ⏭️ | | **SKIPPED — already known (recalibrated 2026-06-10).** His own decks (`temp/context-window-titans.pdf`, `temp/deepseek-review.pdf`) show LLM theory is a *strength*: transformers/attention math, KV-cache cost, efficient-attention lineage (sparse→linear/kernel-trick→linear-attn-as-RNN/RetNet→Titans), MoE/MLA/MTP/FP8/quantization, RLHF/R1 pipeline; he reads & *critiques* frontier papers. Draft §1 written then deleted (below his level). |
| M12 | Ch2 Beyond text | 🔵 | §1 `02-beyond-text/01-diffusion-and-image-generation.md` ✅ (2026-06-10); §2 `02-beyond-text/02-video-and-world-models.md` ✅ (2026-06-25) | **AI thread (his stated gap + goal "understand all model types").** §1 (diffusion/image) **finalized**: he'd read DDPM and had a strong physics model. Session *confirmed* SNR-as-native-axis (=VDM), non-sequential training, coarse→fine; *corrected* two mechanisms — sampling = **annealed Langevin descent on a learned energy landscape** (not resonance/amplification); multi-step = **integrating a curved trajectory** (not noise adding detail; proof = distillation→1–4 steps). His editing analysis independently re-derived **masked inpainting + grounded segmentation** (SAM/GroundingDINO) and the agentic-editor loop; §13 captures it. Refs verified. §2 (video & world models) **finalized 2026-06-25**: builds on §1's curved-trajectory correction — flow matching (straight-line interpolant, constant velocity target → 4–8 NFE vs 100–1000 for DDPM) is the direct answer to "can we make that trajectory less curved?" Covers: temporal coherence problem → 3D U-Net era (VideoLDM, Imagen Video, AnimateDiff motion-module adapters) → DiT + spacetime patch tokenization (Sora's key move: 3D patches → flat token sequence → variable duration/resolution natively) → flow matching math ($v^\ast = \mathbf{x} - \boldsymbol{\epsilon}$, constant conditional velocity, straightness → fewer NFE) → unified vs decoupled (Transfusion: AR + diffusion in one model, engineering reasons why decoupled dominates today) → world models (Sora as world simulator: emergent 3D consistency, object permanence; failure modes diagnose lack of persistent state; Genie action-conditioned from unlabelled video; GameNGen Doom in a neural network). Two matplotlib figures (FM vs DDPM trajectory comparison; capability timeline 2022–2025) + Mermaid architecture diagram (spacetime patch pipeline). Bilingual 中文 glosses. **§10 Applied Q&A (2026-06-25):** whole session = one analogy refined twice — *"DDPM→FM fewer steps ≈ SGD→Adam faster convergence?"* Re-rank (now a §4 callout "Is this just a better optimizer?"): **shared enemy is real** (both = first-order steps along a path, step size capped by curvature/conditioning → fewer steps ⇐ less curvature), **but two different levers** — Adam = *smarter mover on a fixed path* (≈ better ODE sampler DDIM/DPM-Solver; higher-order ↔ momentum/Newton) vs FM = *straighter path so a dumb Euler solver wins* (≈ preconditioning/natural gradient; OT geodesic ↔ natural gradient is exact). Caveat: optimizer cuts *training* steps free, FM cuts *inference* steps but pays extra *training* (rectification). Earlier fused framing also corrected (training-over-θ vs sampling-over-z; FM *matches* a prescribed route, doesn't *search* it). Also this session: verified GitHub LaTeX with Playwright → fixed `\,`/`\;`/`\!`→`\thinspace`/`\quad`, and learned **`\thickspace`/`\medspace` are NOT in GitHub's MathJax** (render as literal text) — conventions rule 4 corrected. Next: §3 audio/speech/TTS · §4 multimodal & representation (CLIP/VLMs, embeddings). |
| M12 | Ch3 Choosing a model | ⬜ | | Mostly practitioner-known; keep light/fast. |
| M13 Building w/ LLMs | Ch1 Prompting/output | ⬜ | | |
| M13 | Ch2 RAG | ⬜ | | |
| M13 | Ch3 Tool use | ⬜ | | |
| M13 | Ch4 Reliability/cost | ⬜ | | |
| M14 Agentic Systems | Ch1 What's an agent | ⬜ | | |
| M14 | Ch2 Framework(-less) | ⬜ | | |
| M14 | Ch3 Multi-agent | ⬜ | | |
| M14 | Ch4 MCP | ⬜ | | |
| M15 AI Eval/Obs | Ch1 Why eval is hard | ⬜ | | |
| M15 | Ch2 Building evals | ⬜ | | |
| M15 | Ch3 Guardrails/tracing | ⬜ | | |

---

## Adjusting as we go

You set the destination; I picked the route. At any phase boundary — or any day — tell me to slow
down, skip ahead, go deeper on a topic, or insert something new, and I'll re-sequence and update this
file. I'll also keep [`agent-docs/learner-profile.md`](../agent-docs/learner-profile.md) current as
your skills evolve, so any agent (Claude/Codex/Cursor) stays in sync.
