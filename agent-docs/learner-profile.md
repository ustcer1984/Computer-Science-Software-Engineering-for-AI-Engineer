# Learner Profile — Zhang Zhou

> **Shared, canonical profile of the learner this repo is teaching.** All AI agents (Claude, Codex,
> Cursor, …) should read this for context and keep it current. Lives in `agent-docs/` per the repo's
> multi-agent rule. Update it when a learning session reveals something new about skills/gaps.

Last updated: 2026-07-02 (v21 — **course-track backfill: M01 Ch3 §2 (async, 06-25) + §3 (synchronization &
races, 06-26) finalized → Ch3 (Concurrency) COMPLETE.** Both were logged in `courses/plan.md` but missed here
while the profile tracked the hobby-econ run (v18→v20); backfilled now (entries below). **Durable calibration
(reinforces & generalizes the v20 read):** the long-standing "captures a real *secondary* effect but **mis-ranks
it vs the dominant cause**" pattern is **specific to physical/mechanistic detail** — in **systems-design /
architecture reasoning he is well-calibrated, not mis-ranked**, now confirmed twice more. §2: on the trap Q
(a timeout around a non-yielding CPU loop) he named the **dominant** reason it never fires — *not* his usual
mis-rank. §3: he read the body, **asked nothing**, and returned the section's **senior conclusion unprompted** —
*immutable state makes a pipeline race-free **by construction**, so it scales from linear to a concurrent graph
without inheriting the lock problem* (a data race needs a **write** to shared memory; no mutation → the whole
§1–§5 lock apparatus is unnecessary) — the concurrency payoff of the append-only pipeline design he'd already
derived in **Ch1 §2 §1**. He needed only *naming* the one residual care point (the fan-in/join: combine
*functionally* + coordinate with structured concurrency, don't append into a shared mutable sink), not a
re-rank. **So in concurrency/systems-design: teach at full depth, expect correct senior conclusions, and
lead with *naming/nuancing* rather than dominant-cause re-ranking** — reserve the hypothesis→re-rank teaching
mode for **physical/mechanistic** detail (fragmentation, bandwidth, GPU internals). Confirms the immutable-graph-
state instinct again → **reuse his pipeline design in M07 / M14 Ch2**. Also, sound triage: he hasn't needed
threads — I/O-bound work → async, threads buy nothing under the GIL. **Next course options:** Ch4 (I/O, syscalls
& the kernel boundary) or rotate to M04 Ch2 §2 / M12 Ch2 §3.).
Prior: v20 (2026-07-02 — **hobby econ Module E02 macro §§1–3 finalized: GDP (§1), inflation (§2),
unemployment (§3).** These postdate the last profile bump and were only logged in `hobby/economy-and-finance/
plan.md` — now mirrored in the hobby-track section below. **The durable calibration this stretch:** the
long-standing "captures a real *secondary* effect but **mis-ranks it vs the dominant cause**" pattern is
**specific to physical/mechanistic detail**. In **conceptual / systems / social-science reasoning he is
well-calibrated, not mis-ranked** — E02 §2 he rebuilt *endogenous money* and a *steady-state* model from
scratch and relocated his own "inflation punishes thrift" unease onto the right target (externalities/growth-
dependence); E02 §3 (07-02 session, now §11) he pulled **one** mechanics question outward through a whole
causal chain — *how is potential growth $g^{\ast}$ estimated?* → the **Fed's reaction function** (one lever,
two targets; Taylor rule) → **central-bank independence** (time-inconsistency, fiscal dominance, the
credibility paradox, Burns/Nixon) → a **live 2026 case he asked me to web-research** (Powell → Warsh, the
17-Jun hold + hike bias, inflation past 4%). **So in systems/social-science domains: teach at full depth,
expect substantive push-back, don't lead with re-ranking; and reach for a live current case + real-time
research** (see [[authoring-rules-material]]). **Process/tooling:** two more GitHub-math render traps found &
fixed via the live-Playwright check and documented in `authoring-conventions.md` rule 4 — the `($…(…)…$)`
parens-wrapping-math-with-inner-parens leak, and inline math inside `*emphasis*` (`*… $x$ …*`) failing to
render. **Next:** E02 §4 (the business cycle) closes the macro module; then the inflation-unemployment
trade-off bridges into E03 (monetary policy).).
Prior: v19 (2026-06-28 — **reading #7: databases — storage engines & isolation ✅ finalized.**
Prepared as the deliberate swing out of AI (storage + concurrency foundations, ahead of M02/M03). He read
both topics but **left §2 (isolation/MVCC/snapshot-vs-serializable/write-skew) for course M03 Ch2 — explicitly
flagging it as hard "without a database-design background."** That confirms the standing CS-fundamentals/DB-design
gap and sets the sequence: **M03 Ch1 (relational model) must precede Ch2 (transactions/isolation)** or the
isolation material won't land. He drove the **entire** session off §1's storage-engine framing, in three hops, into
a **real production architecture decision** — his signature abstract→own-system move. Threads (now the reading's
"What we worked out"): **(1) "what data structure suits a graph DB?"** — keystone re-rank: splits into *storage
engine* (still B-tree/LSM underneath) vs *access method* (the real answer: **index-free adjacency** = embedded
pointer-based adjacency lists; Neo4j = fixed-size records + doubly-linked relationship lists; hop = $O(1)$/$O(\deg)$
local pointer-chase vs relational hop = JOIN = B-tree probe $O(\log n)$ growing with *total* $n$); plus the
**adjacency-matrix/GraphBLAS SpMV** view for whole-graph analytics (landed via his linear-algebra fluency); caveats
he took = still needs a B-tree at the entry point, and pointer-chasing = random access → RAM-bound (his working-set/
OOM point). **(2) "so Postgres can be a graph DB — edge-tables = simulating a graph on relational?"** — his instinct
**correct and well-ranked on the first try** (edge table IS an adjacency list as rows; hop = JOIN = index probe;
recursive CTE = the simulation); keystone he took: **a graph query *language* ≠ a graph *access method*** (Apache AGE
= openCypher on Postgres tables → still JOIN-per-hop, no index-free adjacency); "**has relationships ≠ needs a graph
DB**"; SQL/PGQ (SQL:2023) + GQL (ISO 2024) standardized graph-over-relational. **(3) the payoff — his aquarium
`nexus` Neptune-vs-RDS cost call.** Hypothesis ("use the existing RDS only, to save cost") was **right and stronger
than he framed it.** Repo dive (he asked): **Neptune Serverless** (openCypher) beside a **Postgres 17** RDS; the
`nexus` knowledge graph = ~8 relationship types and **every query a fixed-depth star/chain (1–3 hops)** — only one
variable-length query (`SUPERSEDES*0..`, a short version chain → trivial recursive CTE). Verdict: consolidate —
Neptune Serverless floors at 1 NCU and never scales to zero (~$100+/mo per env) vs ≈$0 marginal on the RDS — but the
**bigger win is removing the RDS↔Neptune dual-write** (a two-store consistency problem = §2's isolation theme
returning *applied*, so §2 wasn't wasted). Steelman/caveats given (roadmap = real knowledge graph / GraphRAG?,
schema churn, migration cost); wrote him a **discussion memo in `temp/`** (gitignored) with the full relational
target schema + recursive-CTE replacement, for the colleague discussion. **Signals:** (i) **confirmed again: he
metabolizes new CS/systems theory by immediately applying it to his own production stack** (here aquarium; before:
the eval pipeline, vLLM ops) — teach DB/systems through his real systems + a real decision, not abstractly.
(ii) **his hypotheses are sharpening** — both the "edge-table = relational simulation" and "just use the RDS" calls
were correctly ranked first-try, needing *naming* (language-vs-access-method; the dual-write as the real prize) not a
dominant-mechanism re-rank. (iii) **new gap named by him: database design / relational modeling** — the genuine next
DB step (M03 Ch1→Ch2). (iv) **strong cost-aware / consolidation reasoning** — he intuited the "just use Postgres"
thesis unprompted; distributed-systems strength generalizing to system-design/cost. (v) clean track-economy
("finalize here"). **Next:** M03 Ch1 (relational model) → Ch2 (transactions/isolation, with him explicitly), or
continue the reading rotation.).
Prior: v18 (2026-06-25 — **M12 Ch2 §2 "video generation & world models" ✅ finalized.** The body
(temporal-coherence problem → 3D-U-Net era → DiT/Sora spacetime patches → flow matching → Transfusion →
world models) was pitched at his frontier level and went mostly untouched; the whole Q&A was **one analogy,
refined twice, in his signature plausible-premise→re-rank mode** (now §10 Applied + a new §4 callout "Is this
just a better optimizer?"). First framing — *"FM optimizes the route from noise to data, like the optimizer
in LLM training?"* — fused **two optimizations on two variables**: training (SGD/Adam over weights $\theta$,
present in DDPM too → not the distinguishing feature) vs sampling (the ODE-integrated *route* over the latent
$\mathbf{z}_t$); and the deeper correction that **FM doesn't *search* the route — the straight interpolant is a
*prescribed* target and training is regression *matching* a known velocity**, the only genuine route-optimization
being rectification→optimal-transport. Second, sharper framing (his real point) — *"the DDPM→FM step reduction
feels like the SGD→Adam speed-up"* — is the **good** version: the **shared enemy is real** (both are first-order
local steps along a path, $\mathbf{z}\leftarrow\mathbf{z}+hv_\theta$ / $\theta\leftarrow\theta-\eta\nabla L$,
whose step size is capped by **curvature/conditioning** — Euler error $\sim h^2\lVert\ddot{\mathbf{z}}\rVert$,
GD steps $\sim\kappa$ — so *fewer steps ⇐ less curvature*), **but they pull different levers**: Adam = a *smarter
mover on a fixed path* (Lever 1; diffusion analogue = a better ODE sampler DDIM/DPM-Solver on the same model;
higher-order solvers ↔ momentum/Newton) whereas FM = a *straighter path that lets a dumb Euler solver win*
(Lever 2; **reconditioning the problem**, true analogue = **preconditioning / natural gradient**, and since
rectification's straight paths are the OT geodesics, *"straighten via OT" ↔ "follow the geodesic via natural
gradient"* is exact). He took the currency caveat (a better optimizer cuts *training* steps free; FM cuts
*inference* steps but pays extra *training* via rectification). **Signals:** (i) the **optimization↔sampling
bridge** (Euler-step ≈ gradient-step; solver-swap ≈ optimizer-swap; FM ≈ preconditioning) lands instantly
because it's stated in the ML vocabulary he owns — keep teaching non-text generative models *through his
optimization/ML lens*, not just the physics lens. (ii) Same confirmed pattern: a hypothesis that captures a
**real structural parallel** but needs the **dominant distinction named** (here: which lever — solver vs problem
geometry); integrates on naming. (iii) Clean track-economy ("finalize here"). **Process/tooling note this
session:** verified the section's math on the **live GitHub blob with Playwright** (the screenshot is
authoritative; a DOM-selector check gave a false all-clear) and caught two real render bugs — `\,`/`\;`/`\!`
leaking literal punctuation (CommonMark strips the backslash) → fixed to `\thinspace`/`\quad`; and the discovery
that **`\thickspace`/`\medspace` are NOT in GitHub's MathJax build** (they render as literal text — only base-TeX
`\thinspace`/`\quad`/`\qquad` survive). `agent-docs/authoring-conventions.md` rule 4 corrected accordingly. Next
in M12 Ch2: §3 audio/speech/TTS · §4 multimodal & representation (CLIP/VLMs, embeddings).).

Earlier entries (**v17 → initial calibration**, 2026-06-08 … 2026-06-24) are archived in
[`learner-profile-history.md`](learner-profile-history.md), the append-only change log. Their durable
signal is already distilled into the sections below (skill map, gaps, preferences, per-track progress);
read the history only for the chronological "how we got here" trail.

## Background
- PhD in applied physics; 10 yrs material/failure analysis in semiconductor manufacturing.
- ~1 year as an AI Engineer (building web apps + data pipelines). Strong analyst, fast learner.
- Works primarily by "vibe coding" with AI agents (Cursor, Claude). **Goal is to read & understand
  code with AI help, not to hand-write it.**
- Time budget: ~2–3 hrs/day on upskilling.

## Goals
- Become a full-stack developer **and architect**.
- Understand all model types (LLM, image, multimodal, audio) and apply them in agentic frameworks.
- Stay current on latest tech / tool stacks.

## Calibrated skill map

**Strengths:**
- Python — comfortable, idiomatic enough (Pydantic, SQLAlchemy, asyncio).
- Pragmatic distributed-systems patterns — event-driven orchestration, advisory locks, idempotency,
  retries — applied successfully in his projects.
- AI/LLM integration (practitioner) — multi-provider (Gemini/Vertex, SEA-LION, OpenAI-compatible/
  OpenRouter), structured JSON output, a deliberately framework-less "graph-lite" pipeline,
  multilingual translation, guardrails (SEA-Guard), Langfuse tracing.
- **LLM inference serving / deployment (hands-on, surfaced 2026-06-14)** — has run models on **vLLM**
  (tuned `gpu_memory_utilization`) and **llama.cpp** (CPU/GPU layer offloading via `-ngl`). Operates these
  but wanted the *mechanisms* behind the rules-of-thumb (got: PagedAttention internal-vs-external
  fragmentation, KV-pool sizing & derating, sequential bandwidth-bound offload). Pair the serving track
  (M07/M08/M13) with this real experience; he learns it fastest anchored to a knob he's actually turned.
- **LLM theory & architecture — a genuine STRENGTH, not a gap (recalibrated 2026-06-10 from two of his
  own technical decks).** He understands transformers, attention math (QKV, the O(n²) quadratic cost,
  the explicit KV-cache VRAM scaling), tokenization, embeddings, and training-vs-inference *cold* — and
  goes far beyond: efficient-attention lineage (prompt/semantic compression → sparse attention/BigBird →
  linear attention via the kernel trick & associativity → linear-attention-as-RNN/RetNet → Titans
  test-time-memory with surprise/forget gates, MAC/MAG variants); and frontier training internals (MLA
  low-rank KV compression, DeepSeekMoE auxiliary-loss-free load balancing with bias-only top-k, MTP,
  FP8 mixed-precision with FP32 master weights, block-wise quantization with power-of-2 scalers, RLHF /
  rule-based-reward RL, R1-Zero/R1 pipeline, distillation). He reads and *critiques frontier papers*
  (DeepSeek V3/R1, Titans, RetNet) and reasons about them at the level of a strong ML engineer. **Do NOT
  teach him LLM fundamentals — pitch the AI-algorithm track at frontier/paper-critique level or skip it.**
  **BUT (his own words, 2026-06-10): the strength is LLM-specific.** Real **gap in other model types —
  image/diffusion, audio, video, TTS** — has not read papers on them. This is the genuine AI gap and
  serves his stated goal ("understand all model types"). → **M12 Ch2 (Beyond text) is the AI thread to
  keep and teach properly**, pitched at his level (frontier, architecture-deep, physics lens welcome).
  M12 Ch1 (how LLMs work) = SKIP/known.
- SQL — basic-solid; parameterized queries.

**Gaps (consistent across BOTH repos = real signal):**
1. **Code decomposition / modularity** — recurring monolithic files (`process_no_waiting.py` 2,434 LoC;
   `ArenaPage.jsx` 3,270 LoC). His clearest, most actionable gap.
2. **Testing discipline** — sparse/absent, especially in solo work; no CI test gates in arena.
3. **Type safety** — loose `Dict[str, Any]` in Python; **zero TypeScript** in frontend.
4. **Frontend / JavaScript fundamentals** — beginner-to-mid; can vibe React hooks/router/context but
   lacks browser/DOM/JS-core mental models; DRY violations (duplicated app code across two SPAs).
5. **LLM reliability & evaluation** — basic JSON-parse fallback; no eval framework; thin prompt-reliability strategy.
6. **Observability depth** — basic logging in solo work.
7. **CS fundamentals depth** — ~50% LeetCode medium; DS&A + C basics; likely gaps in OS/concurrency
   theory, networking internals, deeper storage/consistency theory. He *wants* these from first principles.

**CLOUD — CORRECTED (his own words, overrides the code survey):** cloud is NOT a prior strength.
**Zero cloud experience before this job**; learned AWS/GCP just-in-time as projects required. Has an
average grasp of the *specific components he's used* but no picture beyond them. Explicitly wants
cloud fundamentals from scratch + a real **AWS vs GCP vs Azure** comparison. (The earlier "cloud
strong" read came from project code that was likely heavily AI-assisted.)

**Cyber security** — explicitly requested as its own training track (not just deploy hygiene).

**Important caveat (repos):** `aquarium-main` is a team repo with pre-existing strong CI/conventions,
so its surrounding maturity is NOT all his; `arena-concept-experiment` (mostly solo) is the cleaner
signal of independent capability. Both repos are **actively maintained and may be heavily refactored**
— treat their current code as illustrative, not fixed. He may directly implement improvements the
learning surfaces.

## Learning preferences (kickoff 2026-06-08, incl. follow-up feedback)
- **Deep, low-level foundations matter to him** — likes to understand how things work underneath
  (e.g. OS internals & Linux/macOS/Windows differences; relational vs graph DB design, efficiency,
  security). Front-load fundamentals.
- **Balanced interleave** across CS / software-engineering / AI (not one scope at a time).
- **Concept-first, light coding** — build mental models, learn to read/judge code; hands-on optional.
- **Comparative framing** preferred where technologies compete (OSes, DB types, cloud providers, frameworks).
- He's happy for the agent to set the learning sequence; he'll redirect mid-way as interests shift.
- **Bilingual (English + Chinese).** Reads economy/business news and reports in Chinese as well as English.
  Material stays in English but should **gloss key concepts/terms in Chinese**, giving **both Mainland (大陆,
  简体) and Taiwan (台灣, 繁體)** forms and flagging genuine terminology differences (not just script). Rule
  recorded in [`authoring-conventions.md`](authoring-conventions.md) §5. *(Added 2026-06-20, Econ E01 §3.)*

## Learning progress (course track)
- **2026-06-25 — M12 Ch2 §2 (video generation & world models) ✅ finalized.** Second section of the AI
  thread (non-text models), pitched at his frontier level. Body untouched; the whole Q&A was **one analogy
  refined twice** — *"DDPM→FM fewer sampling steps ≈ SGD→Adam faster convergence?"* The re-rank (now a §4
  callout + §10 Applied): the **shared enemy is real** (both = first-order steps along a path whose step size
  is capped by **curvature/conditioning** → fewer steps ⇐ less curvature) **but two different levers** — Adam
  is a *smarter mover on a fixed path* (≈ a better ODE sampler, DDIM/DPM-Solver; higher-order ↔ momentum/
  Newton), whereas FM is a *straighter path that lets a dumb Euler solver win* (≈ **preconditioning / natural
  gradient**; rectification's straight paths = OT geodesics, so "straighten via OT" ↔ "natural gradient" is
  exact). FM is **not a better optimizer — it reconditions the problem**. Also corrected the earlier fused
  framing (training-over-$\theta$ vs sampling-over-$\mathbf{z}$; FM *matches* a prescribed route, doesn't
  *search* it). **Teach-forward:** non-text generative models land best **through his optimization/ML lens**
  (the Euler-step≈gradient-step, solver-swap≈optimizer-swap, FM≈preconditioning bridge landed instantly),
  not only the physics lens. **Tooling:** verified the math on the live GitHub blob with Playwright and fixed
  two real render bugs (`\,`/`\;`/`\!` → `\thinspace`/`\quad`; discovered `\thickspace`/`\medspace` aren't in
  GitHub's MathJax) — conventions rule 4 corrected. Next in M12 Ch2: §3 audio/speech/TTS · §4 multimodal
  (CLIP/VLMs, embeddings).
- **2026-06-18 — M04 Ch2 §1 (cohesion, coupling & module depth) ✅ finalized.** First decomposition
  section; rotated here off a run of M01 days. Body teaches the *metric* for a good boundary: decomposition
  ≠ smaller files → complexity (change amplification / cognitive load / unknown-unknowns) → cohesion ladder
  → coupling ladder + the **decomposition U-curve** (total = within-module ↓ + between-module ↑; the valley
  is set by cohesion/coupling, not line count) → **module depth** ($\approx$ functionality/interface) as the
  unifier → info hiding & leaky abstractions → far-wall failure modes. **He drove it with a real design
  problem** (now §11 Applied): a pipeline of independent steps split into files **by technical kind**
  (waiting/non-waiting) — he correctly sensed one-file-per-function "isn't much better." Re-rank he took:
  that's **logical cohesion** (= package-by-layer); the layout conflated *what a step does* (→ file
  organization) with *whether it waits* (→ interface + runner). He proposed a `process_interface.py` +
  `process_logic/` split; I pressure-tested it (C-header `.h/.c` split = Python anti-pattern: duplicated
  signatures + interface-severed-from-body = shallow boundary) → keeper **"an interface file is not a list
  of signatures"** (the shared thing is the `Step` contract + the `PIPELINE` catalog; bodies grouped by
  cohesion in `steps/`), and the bonus that once I/O-ness is in the type, the runner can **fan out the
  independent I/O steps** (the long-flagged sequential-await→`gather` audit item, surfacing unprompted). He
  agreed the refined layout was "much better." **Same confirmed pattern as the concept sessions, now on a
  SWE-design axis:** he proposes a plausible design, integrates the re-rank instantly once the dominant
  principle is named — so teach the SWE track by giving him designs to critique and pressure-testing his
  proposals, not by stating rules. **MAJOR process calibration (durable, all tracks — `agent-docs/authoring-
  conventions.md` rule 3):** the two repos were level-calibration, **not** the course's goal → teach
  *comprehensively*; stop over-citing repos / line counts; his Q&A snippets are *questions, not
  endorsements*; and **lead with real-world canonical good/bad examples + failure modes he hasn't met**
  (his explicit ask). Acted on immediately — §1 was re-anchored to Unix I/O, Go `io.Reader`, Java stream
  wrappers, ORM N+1 / TCP leaks, Y2K, and the Segment / Prime Video / Spring / FizzBuzzEnterpriseEdition
  over-decomposition cases. **How to teach forward:** comprehensive coverage at his (already-high) level,
  real-world exemplars over invented ones, repo mentions sparing. Next inside Ch2: §2 refactoring-in-moves
  or §3 module/file boundaries; or rotate to **M12 Ch2 §2 video models** (his strongest critique mode).
- **2026-06-26 — M01 Ch3 §3 (synchronization & races) ✅ finalized → Ch3 (Concurrency) COMPLETE.** The third leg;
  fuses §1 ("the GIL only hid the *cheap* races; free-threading makes them yours") + §2 ("the world only changes at an
  `await`") into one theory: a bug lives wherever a broken **invariant** is observable by another flow → make that window
  mutually exclusive (locks/primitives), break a Coffman condition to kill deadlock, or — the senior move — **remove the
  shared mutable state entirely** (queues/actors/immutability). Body (pitched high: `x+=1`=3 bytecodes; data-race vs
  race-condition; the one-question async test *lock iff an `await` is inside the critical section*; the primitive toolkit
  + the `Condition` `while`-loop; deadlock as Coffman's four + lock-ordering; message-passing/back-pressure; the memory-
  barrier floor) went **untouched**. **No questions — he read it and returned a design synthesis** (now §11 Applied):
  (1) *linear pipeline = no race* (one flow of control); (2) **immutable state makes a concurrent graph race-free by
  construction** — he reached the section's senior conclusion **unprompted** (no write to shared memory → the entire
  §1–§5 lock apparatus is unnecessary), the concurrency payoff of the **Ch1 §2 §1** append-only pipeline he'd already
  designed; (3) hasn't needed threads (I/O-bound → async). The one edge I **named** (not re-ranked): the **fan-in/join**
  is the residual care point — combine *functionally* (return-and-reduce, never $N$ edges appending into one shared
  mutable sink) and coordinate with **structured concurrency** (`gather`/`TaskGroup`), not a lock; unbounded fan-out →
  back-pressure. **Signal:** on systems-design he's **well-calibrated** — needs *naming*, not dominant-cause re-ranking
  (see v21 header); reuse the immutable-graph-pipeline instinct in **M07 / M14 Ch2**. Full body/diagram detail in
  `courses/plan.md`. **Next:** Ch4 (I/O & kernel), or rotate to M04 Ch2 §2 / M12 Ch2 §3 (optional Ch3 §4 producer/
  consumer parked until a concurrent-graph pipeline needs it — his own "revisit if needed").
- **2026-06-25 — M01 Ch3 §2 (async, deeply: event loop · coroutine/Future/Task · structured concurrency · cancellation)
  ✅ finalized.** One level under §1, cashing his 06-16 `gather`-timeout keeper into its mechanism. Body (the event-loop
  tick with `_ready` deque + `_scheduled` heap + one blocking `selector.select`; coroutine ≠ Future ≠ Task; the
  spawning-primitives table keyed on sibling-on-error; `TaskGroup`/`ExceptionGroup`; **cancellation = an exception
  *injected* at the parked `await`, `CancelledError`∈BaseException → must re-raise**) held at his level and went
  untouched. **Session = one sharp thread** (check-Q 8.5: `asyncio.timeout` wrapped around a non-yielding `while True`
  CPU loop): he predicted **"the timeout never fires"** and — **notably, named the *dominant* reason, not his usual
  mis-rank** — which we sharpened into two independent reasons (the loop is wedged so the timer can't run; *and* there's
  no `await` for the cancel to land on). Keeper: *a timeout protects a hanging `await` (silence/I/O), never a non-yielding
  CPU loop — that needs `run_in_executor` → a process pool.* **Signal:** first cleanly *well-ranked-first-try*
  concurrency hypothesis — the systems-calibration trend (v21). Full detail in `courses/plan.md`. (Next inside Ch3 was
  §3 — now done.)
- **2026-06-16 — M01 Ch3 §1 (concurrency vs parallelism, the three models, the GIL) ✅ finalized.** First section of Ch3, written
  deliberately to *build on* his existing keystones (Ch1 §2 async-stack model; Ch2 §2 refcounting→GIL) instead of re-teaching them — the body
  went **untouched**, confirming the pitch was right, and he spent the whole session **applying** §1–§4 to a concrete **LLM-eval pipeline**.
  Three Q&A threads (now §9 Applied in the section file): **(1) "what's the mechanism behind the `openai` library's batch inference?"** →
  untangled **"batch" = three mechanisms at three layers** (client async fan-out / the Batch API job / server-side continuous batching); his case
  is client fan-out = §1–§4 (I/O-bound, high fan-out → asyncio, GIL released on the await), and he took the re-rank that **the ceiling is the
  provider rate limit, not the GIL** (06-09 reading callback) — plus the tie to his 06-15 continuous-batching reading (*client supplies
  concurrency; server converts it to GPU efficiency*). **(2) the `asyncio.gather` failure mode** — his **scheduler** model was spot-on
  (ready-FIFO deque, a task runs until it awaits a pending future then yields, I/O completion re-enqueued FIFO), but his **failure** model
  **fused two opposite hangs**: he asserted "the thread hangs" when a response never comes, but in fact a task **parked on I/O** doesn't block
  the loop or the other 999 tasks — only `gather`'s **join barrier** waits, and the completed results are recoverable inside their Task objects;
  the *genuinely* loop-freezing case is a **blocking call** with no await (§4 footgun, lives in his parse/aggregate steps). The keeper he took:
  **`return_exceptions=True` handles *errors*, but only a *timeout* handles *silence*** — so for "response never comes" the dominant fix is the
  timeout (= his Ousterhout **"define the error out of existence"**), composed with semaphore-bounded fan-out + idempotent retry + `as_completed`
  partial-harvest. **(3) parse/aggregate CPU steps** — strategic instinct correct (negligible vs the network I/O, Amdahl), but his split
  *math→C-library, parsing→multiprocessing* was inconsistent; re-ranked to **one lever — push the hot loop into C, not thread-vs-process** — and
  the nuance that breaks "it's C so no concurrency needed": **"C library" ≠ "GIL released"** (numpy releases → real parallelism; json/orjson/
  pydantic *hold* the GIL because they build Python objects → fast but single-threaded; lxml releases). Decision rule for eval: not "is parse
  CPU-bound?" but "is a single parse long enough to stall the loop?" → inline if fast, ProcessPool (mind the pickle tax) only if heavy.
  **Signals:** (a) **applied concurrency/async is a confirmed strength** — he reasons fluently about the event loop, fan-out, and reaches for the
  right robustness primitives (bounded concurrency, idempotent retry, partial harvest) once the mechanism is named, consistent with his
  distributed-systems patterns. (b) **Same hypothesis pattern as v10/v11, now also on a *failure-model* axis** — the scheduler mechanics he had
  exactly right; the *failure ranking* is where he needed the re-frame ("thread hangs" → "only the join barrier waits"). Teaching value =
  naming the dominant mechanism and re-ranking; he integrates instantly. (c) He **anchors abstract material to a real system he's building** (the
  eval pipeline) — teach concurrency/SWE through his own pipelines. (d) Minor gap closed with correct meta-instinct: thought `json` was pure
  Python (it's C-accelerated) — "never cared, never my bottleneck," which is the right call. (e) Clean track-economy again ("we can finalize
  here"). **How to teach forward:** keep giving him the mechanism then a failure scenario to mis-rank — he converges on the precise distinction
  by attacking it. Ch3 §2 (async deeply: cancellation, TaskGroup) directly cashes thread (2); but it's a *fourth* straight M01 day, so the
  interleave pull to **M04 (SWE decomposition)** or **M12 (video models)** is now strong — offer the rotation at the next boundary.
- **2026-06-14 — M01 Ch2 §3 (out of memory: virtual memory, paging, OOM killer, the GPU/VRAM wall) ✅ finalized
  → Ch2 (Memory) COMPLETE.** The body (address-space-vs-RAM, overcommit, the four OOM signatures, leak-vs-too-much,
  the VRAM budget) went **untouched** — he absorbed it and spent the whole session pulling the *why* out of three
  **LLM-serving** rules-of-thumb from his own ops experience. Three threads (now §11): **(1) PagedAttention** — he
  hypothesized a contiguous KV-cache is bad because it's "too huge → no contiguous VRAM chunk" (**external
  fragmentation**). Corrected: that's the *smallest* of three wastes; the dominant one is **internal fragmentation
  from forced over-reservation** — contiguity + dynamic growth to an unknown length ⇒ you must reserve `max_seq_len`
  up front (prior systems use only ~20–40% of KV memory); fixed-size blocks eliminate external frag *by construction*;
  and he'd missed the **copy-on-write block-sharing** dimension entirely. §1 paging mapping confirmed. **(2) vLLM
  `gpu_memory_utilization`** — he'd been told 0.80–0.85 "just experience" and guessed the reason was "paging isn't
  free." Corrected (an **axis error**): paging cost is compute/latency paid *inside* the pool, not VRAM; the ratio is
  a **ceiling**, and the `(1−ratio)` slice is a **safety margin against an under-estimated, *variable* peak** (batch
  composition, CUDA graphs, fragmentation, NCCL, other tenants) — exceed it and, with **no GPU swap**, you get a
  `CUDA OOM` *crash*. He took the **derating** framing (run below max rating for margin against a variable peak —
  his semiconductor world) immediately. **(3) llama.cpp `-ngl` offload** — he'd observed "low offload ratio ≈
  tolerable" and asked three sharp questions; answers: offloaded blocks are **purely CPU** (compute follows weights);
  GPU/CPU run **sequentially** (transformer dependency chain → additive latency; decode is **bandwidth-bound** so a
  CPU layer is ~10–40× a GPU layer → mild at low ratio, sharp **knee** at high); cross-bus traffic is tiny because
  **weights are pinned per device and only ~8 KB of activations cross PCIe** (move the small thing, not the big
  thing) — with a decode-vs-prefill caveat he logged. **Payoff:** all three collapsed to one principle he can reuse —
  ***don't move, duplicate, or over-reserve the big thing***; PagedAttention / derating / offloading are the OS
  memory playbook (§1–§7) re-skinned for serving. **Signals:** (a) **NEW — real LLM inference-serving/deployment
  experience** (vLLM + llama.cpp ops), a practitioner strength on the *serving/optimization* side; moved into the
  skill map. Anchor M07/M08/M13 serving content to knobs he's actually turned. (b) **Consistent hypothesis pattern,
  now a confirmed teaching lever:** his guesses reliably capture a *real secondary effect* but **mis-rank it against
  the dominant cause** (external-vs-internal frag; paging-cost-vs-margin) — same shape as the macro-strong/micro-needs-
  calibration read from 06-12. The teaching value is *naming the dominant mechanism and re-ranking*; he integrates the
  correction instantly. (c) **Hardware/bandwidth reasoning is fluent** (PCIe vs RAM vs VRAM bandwidth, bandwidth-bound
  decode) — the GPU/AI-hardware strength again. (d) He **probes the mechanism behind a rule-of-thumb** ("just
  experience" is unsatisfying to him) — give him the *why*, not the *what*. (e) Good track-economy: clean "finalize
  here" at the natural stop. **How to teach him going forward:** let him state the plausible hypothesis, then re-rank
  it against the dominant cause with the precise mechanism — and reach for **physics/semiconductor analogies**
  (derating landed instantly) to lock concepts.
- **2026-06-13 — M01 Ch2 §2 (garbage collection: refcounting + cycle collector + the GIL) ✅ finalized.** Body
  (refcounting, cycles, generational collector, refcounting-is-why-the-GIL-exists, PEP 703/683 free-threading) was
  at/above his level — he absorbed it fast; the session was **his signature pressure-test mode now aimed at the GC**,
  and notably **grounded in concrete code and a real production leak** rather than theory. Two threads (now §10):
  **(1) Resource-vs-object lifetime.** He stress-tested the section's "use `with`, never the GC" rule by appending an
  open file object to a list *inside* its `with` block, then asked the sharp version: **from the GC's point of view,
  what's the difference between `with open()` and manual `f = open(); ...; f.close()`?** He drove to the precise
  answer himself: **no GC difference** (both leave `f` bound, both freed identically by refcounting; `with` is not a
  scope and not `del`), the difference is **exception-safety in resource-land, not memory-land**, and the real reframe
  — **"closing is a resource operation, freeing is a memory operation, and the GC only does the second"** (resource
  lifetime ⊥ object lifetime). Resolved the rule as **"1-or-2, never 3"** (3 = lean on `__del__`/GC to close the fd).
  **(2) A fab war story (genuinely new signal — real production memory-debugging experience):** years ago a
  colleague's custom image-processing script crashed after ~10 images (leak); he fixed it with a per-iteration
  `gc.collect()` and asked for a better way *without touching the function.* Keepers he took: **`gc.collect()` working
  is itself a diagnosis — it proves the leak is *cyclic*** (a strong-ref leak wouldn't respond); the **count-vs-bytes
  threshold blindness** explains the "~10 images" crash (few-but-huge objects never trip the 700 object-count
  threshold); and **process isolation** (`maxtasksperchild=1`; gunicorn/Celery `max_requests` pattern) is *strictly
  stronger* than `gc.collect()` because it survives non-cyclic/C-level leaks too — **"`gc.collect()` cleans up a leak;
  process isolation outlives it."** **Signals:** (a) **verify-don't-trust meta-skill again** — he pressure-tested the
  *material's own prescription* ("never the GC") with a counterexample snippet until the precise scope of the rule
  fell out (same instinct as catching the small-int-cache bug on 06-12, and the article-vs-skeleton contradiction).
  (b) **Strong systems/OS intuition confirmed** — he reached for process isolation as the robust containment pattern
  essentially unprompted; the GIL↔refcounting connection landed immediately (consistent with the 06-09 concurrency
  strength). (c) **He brings real production debugging history** (fab image-processing) and learns best when the
  abstraction is brought into contact with a concrete bug he's actually hit — anchor GC/OS/perf material to his
  shipped systems. (d) Good track-economy again: finalized cleanly at the natural stopping point. **How to teach:
  keep giving him the rule, then a snippet that seems to violate it** — he converges on the precise distinction by
  attacking the boundary, faster than from the statement alone.
- **2026-06-12 — M01 Ch2 §1 (address space: stack/heap & the Python object model) ✅ finalized.** Body
  (stack vs heap, names-are-pointers, mutability/aliasing) was at/below his level — he absorbed it fast and
  the session **turned into a software-DESIGN session**, which is the real signal. Arc: (1) sharp stack
  question (do frames vary in size — yes, per-function, compile-time-fixed in C except VLA/`alloca`). (2) He
  asserted, unprompted, that **passing mutable args through pipeline steps hurts readability/traceability** and
  proposed making the pipeline a **class with state on `self`, mutated via methods**. Good instinct (he's
  detecting a real smell) but **mis-attributed the cause** — I pushed back: moving state to `self` makes
  mutation *more* implicit (temporal coupling; "globals with smaller scope"; monolith risk = his own 2.4k-LoC
  gap). (3) He refined to a `PipeState` class with `read_state()`/`update_state(data)` — I named it a **shallow
  module** (Ousterhout, his 06-11 reading: generic `update_state(data)` guards no invariant = wide interface in
  disguise; `read_state()` returning the live object reopens aliasing). (4) Landed the keeper: **the axis is
  explicit-and-returned vs implicit-and-mutated, not arg-vs-self** → flow immutable state through explicit
  signatures, inject set-once deps on `self`, mutate nothing; a class earns mutable `self` only to protect a
  real invariant behind a semantic interface. Gave him a **best-practice pipeline skeleton** (frozen dataclass
  `State` + `Deps` DI + `Step` Protocol + uniform runner for one-place tracing/retry) — he asked to keep it in
  the material (now §10b). (5) **He then pushed the design all the way to a complex GRAPH pipeline (LangGraph-style)**
  and proposed — correctly, unprompted — that graph state needs **two parts**: stable data with a definite schema,
  and **dynamic "artifacts"** (loop steps stashing things; shapes that evolve with features, so a fixed schema keeps
  breaking). A genuinely good, framework-designer-level intuition. Resolving principle we landed (now §10d):
  **"open set of values, closed set of shapes — fix the grammar, not the vocabulary"** → don't pre-declare which
  artifacts exist, but type each one + stamp provenance + give the container a fixed interface (append-only store =
  a baked-in reducer; = LangGraph channels+reducers, but typed). **Signals:** (a) he *proactively* reasons about
  architecture at a high level — engaged, opinionated, iterates fast — and his *systems/architecture* intuition
  (two-part state, dynamic artifacts, graph loops) is a genuine STRENGTH; but the *local* decomposition mechanics
  are the gap (he reached twice for "encapsulate state in a class," the move that tends to *create* his monoliths;
  the explicit-immutable-dataflow alternative was new and landed). Net: strong at macro design, needs calibration
  at micro (module boundaries, interface depth, mutation discipline). Strong pull toward agentic/graph-pipeline
  architecture (his framework-less graph-lite work) → M14 Ch2/M07 will land well and should reuse THIS skeleton.
  (b) **Caught a real correctness bug in my
  example** (one-line `a=257;b=257;a is b` is True via compile-time constant dedup, not False) — his "verify,
  don't trust" instinct applied to *my* material; verified live with Python before fixing. (c) **`dataclass`/
  `typing.Protocol` are unfamiliar** — notable given his Python strength; he vibe-codes and hasn't needed them.
  → reading queued (below) + added to M05 Ch2 scope. (d) Good track-economy call again: "we can finalize here."
  **How to teach the SWE track:** give him designs to critique and *pressure-test his proposals* the way he
  pressure-tests concepts — he learns decomposition by having a plausible-but-flawed design taken apart, not by
  rules. Lean on Ousterhout vocabulary (deep/shallow modules, define-errors-out-of-existence) — it's now shared
  language. **M04 Ch2 (Decomposition) is the high-value next SWE stop** and should use *his* pipeline code.
- **2026-06-10 — M12 Ch2 §1 (diffusion & image generation) ✅ finalized.** First section of the
  recalibrated AI thread (non-text models). He'd already read the DDPM paper and built a physics-grounded
  mental model; the session was a *peer-level* Q&A. **What he had right (sharper than most explainers):**
  (1) "it's all about SNR; the model is a noise filter" — and SNR is literally the VDM parameterization;
  (2) **training needn't be sequential** — i.i.d. {noisy,clean} pairs at distributed SNR train the same
  model, which is exactly how DDPM trains (he saw through a common misconception); (3) few-steps→blur =
  posterior-mean / low-freq-first. **Two mechanisms he had wrong, then corrected:** (a) sampling is NOT
  "resonance amplifying signals present in the noise" → it's **annealed Langevin descent on a learned
  energy landscape** (seed selects the basin; content is *synthesized*, not amplified); (b) multi-step is
  NOT "noise added each step to pick up detail" → it's **integrating a curved trajectory** (he corrected
  this himself mid-session: deterministic ODE adds no noise; forcing factor is step-size/truncation error,
  not float precision; proof = distillation→1–4 steps). **Standout signal — his engineering instinct runs
  ahead of the papers he's read:** he independently re-derived CLIP-style image-text alignment, diffusion-
  feature reuse for discriminative tasks, and (for image editing) **masked inpainting + grounded
  segmentation** (SAM/GroundingDINO) *and* the agentic deterministic-editor loop — all production reality.
  **How to teach him (confirmed):** non-text models **through the physics he owns** (energy landscapes,
  annealing, SDE/ODE, spectra); let him stress-test a model until it breaks, then give the precise why.
  His architecture/systems intuition (reusable embedders, mask-based control, agent loops) is a strength
  to lean on. Next: §2 video (Sora/world-model critique = his strongest mode).
- **2026-06-10 — AI-knowledge recalibration from two of his own decks (`temp/context-window-titans.pdf`
  22 Apr 2025; `temp/deepseek-review.pdf` 18 Feb 2025).** He asked me to assess his LLM knowledge by
  reading them. Verdict: **his LLM theory is far ahead of where the plan assumed.** The draft M12 Ch1 §1
  (tokens/embeddings/attention/training-vs-inference) is *entirely below his level* — he teaches this
  material. **Context-window deck:** a rigorous survey of efficient attention — quadratic-cost VRAM math,
  sparse attention, the linear-attention kernel trick (associativity reorder), linear-attention-as-RNN
  (RetNet), and Titans (test-time neural memory, surprise/forget gates, MAC/MAG) — current to Jan 2025
  papers. **DeepSeek deck:** deep architecture (MLA, aux-loss-free MoE, MTP, FP8 mixed precision, block
  quantization) + a genuinely sharp *critical* analysis ("a mixture of achievements and lies"): separates
  the "low cost" (V3/pretraining) from "best performance" (R1/post-training) claim, identifies the hidden
  variable (high-quality CoT **data**, not the simple RL), spots the language-mixing/"aha-moment" tell,
  and ends with intellectual honesty ("I do NOT know" where he can't prove it). **Signals confirmed/new:**
  (1) LLM architecture/training is a real strength — move it OUT of the gap column. (2) His distinctive
  edge again: **hardware-grounded reasoning** (the H800-vs-H100 FP-throughput/NVLink constraint analysis —
  physics/semiconductor lens) and **skeptical "read between the lines" critical thinking** (the standout
  meta-skill). (3) **How he learns/consolidates: by building critical, frontier-level presentations** —
  so teach him by giving frontier material to *critique*, not fundamentals to absorb. **Action:** recalibrate
  the AI-algorithm track (M12–M14) to frontier/paper level or skip; redirect the freed energy to his real
  gaps (SWE decomposition/testing/types, CS internals, cloud, frontend, eval rigor). His own Osmani-mapping
  read already pointed here.
- **2026-06-10 — M04 Ch1 §1 (navigating an unfamiliar codebase) ✅ finalized.** He came in already
  using most of the strategies (three-altitude model, entry-point first, data-flow tracing, monolith
  navigation). Session added no new concepts — it *confirmed* existing practice and gave it names.
  **Gap confirmed: git as a reading and history tool** (`git log`, `git blame`, `git log -S`) — he
  knows it exists but does not reach for it habitually. Wants a concept + feature survey (not command
  memorization) → **git reading entry queued** for an upcoming reading day.
  Two real-world cases he shared, now in §11: (1) **environment leakage** — a colleague's pipeline
  broke on every machine but his because each step hardcoded its own path assumptions; he traced the
  artifact data-flow to find the divergence. Lesson: config/paths must be managed at one level above
  the steps that use them (twelve-factor principle). (2) **Understanding-driven refactoring** — when
  onboarded to a poorly documented eval repo, his first PR used Cursor to add docstrings/type hints
  as scaffolding *before* reading the code. Then found and fixed **copy-paste inheritance** (class A
  nominally inheriting class B but actually holding a silent copy of it). **New signal:** he uses AI
  agents deliberately as a reading/refactoring tool, not just a writing tool — a more mature
  workflow than most at his experience level. **Confirmed prior signal:** orient → trace similar
  example → fix → build is his natural sequence; disciplined and effective.
- **2026-06-09 — M01 Ch1 §3 (machine code & the CPU) ✅ finalized → Ch1 COMPLETE.** He said up front
  he *already understood most of the material* (machine code, memory hierarchy, pipelining, the clock
  wall, SIMD/GPU), so the session ran almost entirely on **his own questions one layer past the text**,
  all aimed at GPU/AI hardware: (1) on multi-core CPUs, what's private vs shared → got the full topology
  (registers + L1/L2 private, L3 shared) and was given **cache coherence/MESI + false sharing + coherence
  ≠ memory-ordering** as the bridge to Ch3. (2) **GPU memory hierarchy** — confirmed the same
  private→shared→VRAM skeleton and grasped the key inversion (GPU hides latency by *thread
  oversubscription + huge register file*, not caches; Shared Memory = software-managed scratchpad; ties
  to tiling/FlashAttention and memory-bound LLM inference). (3) **What CUDA is** — cleanly separated
  "CUDA core" (HW lane) from CUDA (software platform); took the PTX→SASS JIT as a §1 callback; understood
  the CUDA *software* moat and that alternatives (OpenCL/Vulkan/SYCL/Triton/HIP) run on NVIDIA but funnel
  through the NVIDIA driver/PTX. **Signal:** CPU/GPU hardware fundamentals are a genuine *strength*, not
  a gap — likely from the physics/semiconductor background (device layer is second nature; he wanted the
  *architecture* layer above it). His curiosity pulls consistently toward **AI/GPU hardware** — worth
  weighting M12 (model landscape) and GPU/accelerator content. **Process feedback he gave:** course
  References must carry **real, verified hyperlinks** (saved as a memory) — I now verify links before
  finalizing. **Pattern still holds:** learns by pushing a model one question past where it's been
  explained.
- **2026-06-09 — M01 Ch1 §2 (the call stack) ✅ finalized.** Covered frames, call/return, LIFO,
  reading tracebacks bottom-up, recursion/stack-overflow, CPython frame objects. He drove the session
  almost entirely into **async/await ↔ the stack** and **tail-call optimization** — both via sharp,
  build-up questions. Key things he worked out (and a couple of misconceptions corrected): (1) "one
  thread → one core" is right, but the cause is "a thread is one instruction stream," not the stack;
  GIL kicker landed. (2) Nailed `await` ≠ concurrency — *the* big one: two sequential `await`s are just
  blocking calls, concurrency needs `gather`/`create_task`; he initially expected the async version to
  be 2× faster. (3) Built the correct async-stack model himself ("two stacks" → corrected to *one live
  native stack + N parked heap continuations swapped by the event loop*; green-threads). (4) coroutine =
  single-use frame vs Task = reusable result box. (5) TCO: Python's no-TCO-by-design, Scheme/Erlang as
  the opposite pole, and the multiple-recursion limit (quicksort) → stack-to-heap escape (same move as
  async). **Pattern confirmed:** learns by incrementally pressure-testing a model with "is X valid? does
  Y hold?" code snippets until it breaks, then wants the precise why. Very strong systems reasoning.
  Likely worth auditing his arena turn-handling for sequential `await`s that should fan out concurrently.
- **2026-06-08 — M01 Ch1 §1 (execution model) ✅ finalized.** Covered compile vs interpret, CPython
  bytecode + VM, why Python is "slow" vs native libs, JIT. He grasped it quickly and *drove the session
  by connecting theory to his live AWS work* — ARM cross-arch builds, Lambda being polyglot / when a
  compiled language helps (I/O- vs CPU-bound), and cold-start latency. Strong systems intuition; learns
  best when concepts are anchored to his own production systems. Next: §2 (call stack).
- **How he learns (observed):** asks sharp, practical "why does my system do X" questions; prefers
  re-deriving principles over memorising; appreciates explicit cost/trade-off framing.

## Learning progress (hobby track)
*(The third track — for-interest subjects under `hobby/`, lighter 1–2 hr sections. Same study→Q&A→finalize flow.)*
- **2026-07-02 — Economy & Finance · E02 §3 (unemployment & the labour market) ✅ finalized.** Body (4 real
  matplotlib figs + a mermaid one-pager + bilingual glossary): the rate from its precise definition, the
  labour-force accounting, participation/U-6/duration, the four types & NAIRU, Okun's law as the bridge back
  to §1, wage rigidity from §2. **The session (now §11) is the headline signal:** from one buried mechanics
  question — *how is potential growth $g^{\ast}$ actually estimated?* — he pulled a single thread outward
  through the **entire monetary-policy chain**: $g^{\ast}$ is unobservable (methods + real-time-revision
  failure modes) → the **Fed's reaction function** (one lever, two targets; Taylor rule; his premise "both
  high → raise" corrected — high unemployment argues for *cutting*, and stagflation is a genuine conflict) →
  **central-bank independence** (time-inconsistency/inflation-bias, fiscal dominance, the credibility paradox,
  Burns/Nixon 1972) → **a live 2026 case he asked me to web-research** (Powell's chair term ended, **Kevin
  Warsh** — Trump's own pick — held rates 12–0 and flipped the dot plot to a hike bias with inflation past 4%;
  the "capture test" caveat). **Calibration:** in this conceptual/systems domain he is **well-calibrated, not
  mis-ranked** — the corrections he needed were *naming/nuancing* (which world am I in? which gap dominates?),
  not dominant-cause re-ranks. **He also wanted the abstraction grounded in live current events and explicitly
  asked for real-time research** — lead econ/policy sections toward a current case and offer to look it up.
  Next: **§4 — the business cycle** (closes Module E02; assembles cyclical unemployment + output gap + Okun +
  NAIRU↔Phillips, then bridges to E03 monetary policy).
- **2026-06-29 — Economy & Finance · E02 §2 (inflation & price indices) ✅ finalized.** Body (4 figs + one-
  pager): inflation as the rate-of-change of the price level, CPI/basket/Laspeyres, the index family
  (headline/core/PPI/PCE/deflator), real=nominal/index + Fisher, the upward biases, why ≈2%. **Session (§9)
  was two deep threads, both starting from a *moral* unease** — his strongest mode. (9a) "inflation punishes
  thrift" → he **relocated his own critique onto the right target** himself once the pieces were named (mild
  inflation taxes *idle cash* not saving; the real defects are distributional, plus externalities/growth-
  dependence/the discount rate). (9b) he **rebuilt the money-and-growth loop and a steady-state thought
  experiment from scratch**, effectively reinventing *endogenous/credit money* unprompted; needed only two
  corrections (debt-deferral/Minsky; the MPC demand-gap) + naming (Daly's steady-state, scale/distribution/
  allocation). **Confirms: reconstructs macro theory from first principles; teach at full depth.** Next: §3.
- **2026-06-26 — Economy & Finance · E02 §1 (GDP & measuring output) ✅ finalized — opens Module E02.** Body
  (4 figs + one-pager + bilingual glossary): GDP from its one-sentence definition, the three approaches via
  the circular flow, the $C+I+G+NX$ identity with a real cross-country composition plot, nominal vs real +
  deflator + PPP, the welfare critiques + GDP-vs-GNI. **Session (§9):** the built-then-resold-house edge case
  (only *new* production counts; wealth-stock vs GDP-flow); "GDP can be manipulated" calibrated into three
  tiers (rebasing/noise/fraud) unified by **Goodhart's law** + the reward-hacking ML lens; China's growth
  *target* is real not nominal; and **why "+3% can be a crisis for China yet +1% is fine for Singapore"** —
  the break-even/treadmill growth rate + declining potential (the §3 Okun cliffhanger). Fast integration of
  the re-frames; strong systems instinct. Next: §2 (inflation).
- **2026-06-20 — Economy & Finance · E01 §3 (elasticity, surplus & market failure) ✅ finalized.** Body taught
  with 6 real matplotlib curves (per his rule 2) + a bilingual 中文 (大陆/台灣) glossary (his new rule —
  see [[bilingual-chinese-glosses]] / conventions §5). Q&A was his signature **plausible-premise → re-rank**
  applied to **Singapore's sugar policy** (now §8 of the file): he reached for *externality* → re-ranked to
  **information/internality** (∴ the matched tool is *labelling*, not a *sugar tax*); his standout move was
  the **shift-vs-slope** insight — a label *shifts* the demand curve so it beats a tax that only *slides
  along* it precisely **when demand is price-inelastic** (he derived this himself, just needed the wording
  tightened). Also strong: read the **zero-sugar twin** as strategic firm behaviour (product-line versioning)
  and bubble tea as substitution; needed nudging on regressivity, ceteris-paribus (why prices *rose*), and
  not routing the P\*/Q\* *direction* through elasticity. **Calibration:** he learns best by taking a fresh
  concept straight to a **live real-world policy/market** and pressure-testing it — lead future econ sections
  toward a current case to dissect. Bilingual glossing now standard. Next: **§4 — firms, costs & competition.**
- **2026-06-17 — Economy & Finance · E01 §2 (supply, demand & how prices coordinate a market) ✅ finalized.**
  He'd seen S/D before → body easy, untouched; spent the session attacking the model's **foundational
  assumptions** (free market; equilibrium-actually-forms) in his signature plausible-premise→re-rank mode. The
  re-rank (now §10 of the file): **(10a)** *forces* (scarcity, MB/MC — universal) vs *solver* (price mechanism
  is one solver; central planning another) → a planned economy = §6 price-controls at scale, its shortages are
  S/D via a non-price channel, and *why* planning fails = the Hayek **calculation/knowledge problem** (= the §5
  price-as-dual-variable point); genuine residual = **market failure** (competitive assumptions). **(10b)**
  equilibrium = optimality *condition* not search *dynamics* (his own §1 distinction); info lag → **price
  dispersion** (search theory) or, with production lags, **cobweb non-convergence** — which he mapped instantly
  to the **semiconductor cycle**. **Headline for teaching this learner going forward (the v14 calibration):**
  he gave **three durable authoring rules for all tracks** (`agent-docs/authoring-conventions.md`) — (1) **use
  the physics/analogy lens sparingly**, only for genuinely hard ideas; full-Lagrange-for-S/D is overkill and he
  may not recall deep classroom tools; (2) **show real charts/plots** (prefer existing figures, or draw actual
  curves with dummy values) instead of text-only; (3) **always LaTeX for math**. Net: the lens lever is real but
  I'd been over-using it — dial it back, plot more, LaTeX everything. Tight track-economy ("just LaTeX the math,
  finalize"). Next: **§3 — elasticity, surplus & market failure** (his 10a objection lands right on it).
- **2026-06-16 — Economy & Finance · E01 §1 (how economists think: scarcity, opportunity cost, incentives,
  marginal thinking, trade-offs) ✅ finalized.** First hobby-track section. Body pitched through his
  physics/optimization lens (scarcity=constraint, opportunity cost=shadow price/Lagrange multiplier,
  MB=MC=derivative-to-zero, PPF=Pareto frontier, rational agent=spherical cow) and absorbed without challenge;
  he spent the session **attacking the core analogy** with two ML-import objections (captured in §11 of the
  file, summarized in the v13 header). Key takeaways for teaching this track: (a) the **physics/ML-analogy
  lever transfers cleanly to economics** — he reasons about a social science as a coupled optimization system
  and reached for **multi-agent RL / GANs** to model equilibria *unprompted*; (b) his **hypothesis→re-rank
  pattern is subject-independent** (same shape as the CS/serving sessions); (c) he wants the *mechanism behind
  the rule*, not the rule. **Spun off a new subject from this session — see below.**
- **NEW SUBJECT created 2026-06-16 — Game Theory & Strategic Interaction** (`hobby/game-theory/plan.md`, no
  sections yet). He asked for "game theory + related math." Judged it its own subject (not an econ add-on)
  because it **double-serves the econ hobby AND his AI career** (GANs/MARL = learning-in-games; mechanism
  design; Shapley value = SHAP). Plan is concept-first with the math woven in at his level (fixed-point
  theorems, LP/minimax duality, Bayesian games, replicator/learning dynamics). **Open question for him:**
  offered to **promote it to the main `courses/` track** if he wants rigor + demonstrables instead of hobby
  framing — he hasn't answered; default stays hobby. Watch for his AI-vs-econ priority to pick the sequence
  (an AI-fast path G01→G02→G07→G08→G09§2 is pre-drawn in the plan).

## Learning progress (reading track)
- **Queued readings (pick up on an upcoming reading day):**
  - *(none currently — the dataclass/Protocol queue item was completed as the 2026-06-12 reading; see below.)*
  - **Next reading day: rotate further OUT** — the AI-serving thread has now had two adjacent days (06-14 course +
    06-15 reading). Best swing: **M12 Ch2 §2 video models (Sora/DiT — his strongest critique mode)** per his stated
    "understand all model types" gap, or something current outside serving. Reaffirm the plan is on-track if he asks
    (mild metacognitive watch-item from 06-10).
- **2026-06-15 — fifth reading entry ✅ finalized** (`upskill-readings/2026/06/15-llm-inference-serving.md`):
  LLM inference serving — (1) continuous batching (Anyscale); (2) prefill/decode: chunked prefill (Sarathi-Serve)
  vs disaggregation (DistServe). Deliberately adjacent to the 06-14 course session (LLM-serving **memory**) to add
  the **scheduling** axis while fresh. He engaged it the same way as v10 — re-derived the engine from his own vLLM
  ops priors rather than the text, sharp-hypothesis mode. **Three threads (now the "What we worked out" record in
  the file):** (1) *"decode is bandwidth-bound → optimize by using more bandwidth"* — premise right, conclusion
  flipped: bandwidth is **already saturated**, so the lever is **tokens-per-byte-moved**; split into aggregate
  throughput (batching amortizes the *fixed, shared* weight traffic; KV traffic is per-sequence & unshared → the
  wall) vs per-request TPOT (quantization / GQA / speculative decoding shrink bytes-per-token). (2) *continuous
  batching vs PagedAttention* — his separation instinct was right; two wordings corrected: unit is **sequences in
  one batch** (goal = no idle slots, not constant count), and **PagedAttention ends over-*reservation*, it does NOT
  oversubscribe/overcommit VRAM** (the "avg≪max bet" lives at the scheduler-admission layer, hedged by preemption);
  he then asked the right follow-up — *does the preemption net degrade perf?* → yes: recompute/swap, rare=tax,
  chronic=**thrashing** (= yesterday's OS page-thrash one layer up); preemptions in the vLLM log = over-admitted.
  (3) **the headline he reached himself:** *if disaggregation under-utilizes each GPU, how can it beat Sarathi?* →
  it's a **trade-off, not strictly better** — he correctly saw colocation's higher HW utilization and only needed
  the hidden premise named: **objective is goodput-under-SLO, not unit-utilization**; disaggregation spends
  utilization to buy zero-interference + per-phase-optimal parallelism + independent scaling (cost: KV transfer
  over the interconnect); regime rule = few-GPU/loose-SLO→chunk, many-GPU/tight-SLO→disaggregate. **Signals:**
  (a) **LLM-serving internals confirmed a strength on BOTH axes now** (memory v10 + scheduling v11). (b) Same
  hypothesis-pattern as v10 — real-effect premise, needs the dominant frame named — but **his self-correction of
  wording mid-thread** ("by sequences I mean…", "by oversubscribe I mean…") shows the micro-precision gap closing.
  (c) roofline / arithmetic-intensity / PCIe-vs-HBM reasoning is fluent and reusable. (d) clean track-economy:
  "it is a trade-off, not better, understood. We can finalize here." **Teach forward:** keep letting him state the
  plausible hypothesis, then re-rank against the dominant mechanism; he integrates instantly.
- **2026-06-12 — fourth reading entry ✅ finalized** (`upskill-readings/2026/06/12-dataclasses-and-protocols.md`):
  Python `dataclass` + `typing.Protocol` — the pair he flagged unfamiliar in the same-day M01 Ch2 §1 pipeline-skeleton
  session, picked up immediately to consolidate while fresh. **Closed the gap cleanly.** The session was almost
  entirely a **mechanics pressure-test in his signature mode** — sharp yes/no hypotheses about flag combinations
  until the model broke, then the precise why. Keepers he landed: (1) the article's "a slots class may not have
  default values" is true only for *manual* `__slots__` (class-var vs slot-descriptor name collision); `slots=True`
  (3.10+) was added to kill exactly that footgun — *he caught the apparent contradiction with my skeleton and made
  me resolve it* (verify-don't-trust again, now on Python mechanics). (2) **`frozen` and `slots` are orthogonal —
  semantics vs storage**: `frozen` bans *all* writes (reassign AND add, via `__setattr__`); `slots` removes `__dict__`
  so it blocks *unknown names while still allowing reassignment* — the mutable-but-fixed-schema case frozen can't
  express. (3) once `frozen=True`, **`slots=True` is droppable with no correctness harm** — pure perf/memory knob
  (he reasoned his way to this himself). (4) instance method-attachment is blocked, and instance-assigned functions
  aren't bound methods anyway (descriptor protocol fires only on class-stored functions). (5) **Protocol conformance
  is checked *statically* by default** (mypy/pyright verify signatures+types); `@runtime_checkable`+`isinstance` is a
  shallow escape hatch (name-presence only, no signatures; `issubclass` breaks on data members). Clean split he
  adopted: **Protocol = static contract, Pydantic = runtime validation, opposite ends on purpose.** **Signals:**
  (a) two of his opening hypotheses were *half-wrong* ("frozen lets me add fields, only slots blocks"; "only slots
  catches typos") and corrected without friction — his **macro/systems intuition is strong but local Python-semantics
  precision is the gap** (consistent with the 06-12 course-session read: strong at design altitude, needs calibration
  at micro-mechanics). (b) verify-don't-trust meta-skill showed up again — he flagged the article-vs-skeleton
  contradiction unprompted. (c) good track-economy again: "we can finalize here," "no need to change the plan."
  (d) `dataclass`/`Protocol` now move OUT of the unfamiliar column — he has a precise frozen/slots/defaults/methods
  model and the static-vs-runtime Protocol philosophy. Solid primer for **M05 Ch2** (he declined to pull Pydantic
  forward; it stays a section there + M13 Ch1/Ch4 for the LLM-output angle).
- **2026-06-11 — third reading entry ✅ finalized** (`upskill-readings/2026/06/11-git-archaeology-and-software-design.md`):
  (1) Git as a code-*reading*/history tool (Tekin pickaxe article + Julia Evans *Inside .git*) — the
  entry queued from M04 Ch1 §1; (2) Ousterhout *A Philosophy of Software Design* (deep modules /
  complexity) — his #1 gap. **Reading #1 — the standout thread (he drove it):** he quickly went past
  "git log searches history" to *"can I just delegate `find when & why this code was added, whether
  it's still needed, and is it safe to remove` to an agent?"* — and we worked out the keeper principle:
  **that compound question is four sub-questions on different epistemic ground, and git history only
  covers the past two.** Git records the *past* (when/why = ground truth, agent reads it well); "still
  needed / safe to remove" is a *present-dependency-graph + future-runtime* question git is silent on,
  and the agent answers all four in the **same confident voice**. Two traps he locked in: (a) the
  **fabricated "why"** when commit hygiene is bad — agent invents intent from the diff; *defence: demand
  the quoted commit/PR*; (b) **"safe to remove" = proving a universal negative** — grep/agent can't,
  esp. in Python (dynamic `getattr` dispatch, decorator/framework entry points, external cross-repo
  consumers); absence of evidence ≠ evidence of absence. **Discharge = falsify, not accept:** full test
  suite + type checker for static callers, then **deprecation telemetry / canary in prod** for the
  dynamic/external ones ("zero *observed* calls > zero *greppable* calls" — his physics "run the
  experiment, don't trust the model" instinct again). His refined claim: *rely on agents for archaeology
  (when + recorded why); never accept "safe to remove" without falsifying it* — a clean **composer split**
  (agent owns retrieval, he owns the universal-negative safety judgment). **Signal:** his "know when to
  distrust AI" reasoning is sharp and *specific* — he can name exactly which sub-claim is unverifiable
  and why; this is his strongest meta-skill showing up again, now applied to agent delegation. Lands in
  his real gaps (testing, observability) as the *remedy*. **Reading #2 — a metacognition signal:** he
  recognised mid-read that the Ousterhout material overlaps the course track and asked whether he must
  finish it. **Correct, well-calibrated call — chose to skim-not-master**; logged as a deliberate *primer
  for M04 Ch2 (Decomposition)* + M07. Three keepers he's carrying now: **deep-not-just-small** (the
  monolith fix is *deeper* modules, not merely more files — the bit most get wrong), **strategic-vs-tactical**
  (agent = tactical tornado by default; the strategic ~15% is his job — same shape as the "safe to remove"
  lesson), **"define errors out of existence"** (design the error away > handle it → bridge to M05 types +
  his LLM-reliability gap). **Process note:** he's now comfortable *stopping a reading early* when the course
  will cover it — good track-economy judgment; reading track is exposure/priming, course track is mastery.
- **2026-06-10 — second reading entry ✅ finalized** (`upskill-readings/2026/06/10-gpu-performance-and-the-ai-era-engineer.md`):
  (1) Horace He *Making Deep Learning Go Brrrr From First Principles* (compute/memory/overhead regimes,
  arithmetic intensity, operator fusion); (2) Addy Osmani *The Next Two Years of Software Engineering*.
  **Reading #1 — the standout signal:** he understood the article fast (operator fusion was the one new
  piece) and immediately **reframed the whole time/speed framework onto the energy/power/heat axis** —
  unprompted, his physics + semiconductor-failure-analysis lens. He worked the full picture: data
  movement dominates energy even more than time (~600–1000× DRAM-vs-FLOP), the regimes remap (compute-
  bound = most energy-efficient; memory-bound decode = wasteful; overhead-bound = doubly bad via leakage),
  and — the genuinely sharp insight — **"time is the `max`, energy is the `sum`": overlap hides time but
  not joules, so the roofline can mislead on power.** Took the three energy-only levers (static/leakage +
  race-to-idle; the V²f cubic wall → slow-and-wide → why GPU beats CPU on perf/watt; precision as a
  quadratic compute + linear movement win) and the thermal feedback loop (leakage↑ with T → throttle →
  perf, spatial hotspots in memory/interconnect = his old failure-analysis world). **Confirms & sharpens
  the prior signal:** GPU/AI-hardware is a real strength, and the *distinctive lens he brings* is
  **energy/thermal/device physics** — he learns systems best by re-deriving them through the physics he
  already owns. Flagged follow-ups: on-package HBM as an energy-per-bit (wire-length→capacitance) move;
  energy-per-token back-of-envelope. **Reading #2:** he used it to check whether his **course plan**
  follows the article's advice — it does, almost point-for-point (M07/M08/M09/M10 = Osmani's complementary-
  skills list; M04–M06 = the "know when to distrust AI" verification skill; M14 = composer/orchestrator).
  Two takeaways recorded: the alignment is **convergent not copied** (plan predates his reading it →
  corroboration), and **he's *ahead* on the composer/agent-orchestration shift** (already builds framework-
  less agent pipelines — consistent with the 06-09 applied-context-engineering signal; a real edge to lean
  into). **Honest watch-item surfaced & accepted:** the "distrust AI" skill is a *doing*-skill that cashes
  out in his weakest areas (testing/types/reading diffs); the plan front-loads *understand* and back-loads
  *build/demonstrate* to Phase 6 — lever if it feels too theoretical is to pull real-code (arena/aquarium)
  application forward. **Mild metacognitive note:** he sought some reassurance the path is correct (asked
  twice if the courses match the recommendation) — worth periodically affirming the plan is on-track.
- **2026-06-09 — first reading entry ✅ finalized** (`upskill-readings/2026/06/09-async-concurrency-and-agent-context.md`):
  (1) Python concurrency — async/await vs threading; (2) Anthropic *context engineering for agents*. He
  drove both into strong Q&A. **Async/eval thread:** correctly reasoned that for CPU-bound work threads
  beat async (async freezes the loop) but **initially stopped short of the GIL point** — needed the
  correction that threads don't parallelize CPU either (GIL serializes; fix = processes / native libs
  that drop the GIL / GPU); took the `run_in_executor(process_pool)` hybrid well. Also held a
  **misconception that async clients get server-side optimization** — corrected: server can't tell, wire
  requests identical, throughput ceiling is the rate limit not the client model. **Context-engineering
  thread (his strongest contribution):** independently re-derived the Anthropic framework from his own
  coding-agent practice — plan-first (= system-prompt-at-right-altitude), repo structure/READMEs/`docs/`
  (= retrieval index + JIT retrieval), grep-vs-embeddings retrieval, and compaction strategies. His
  Claude-Code-vs-Cursor observations were accurate; correct intuition that Cursor's faster retrieval is
  architectural (embeddings outside the model loop) and that its instant compaction is amortised/avoided.
  **Signals:** systems reasoning on concurrency/GIL is now strong and confirmed (consistent with §2);
  **emerging real strength in *applied* context engineering / agent-ergonomics** — thinks about how to
  set agents up to succeed (plans, structure, docs). Possible follow-ups he flagged: Cursor-vs-Claude
  retrieval/compaction internals; an arena audit for sequential `await`s that should fan out.
- **Active production concern surfaced:** `arena-concept-experiment` (just launched, low traffic) has
  **Lambda cold-start latency** hurting first-load UX (esp. leaderboard) — improvement plan written to
  his local `temp/arena-cold-start-latency-plan.md` (gitignored). May implement later. Suspected
  secondary cause to verify: dev RDS auto-pause.

## Pointers
- Change history (archived `vN` session notes): [`learner-profile-history.md`](learner-profile-history.md)
- Course roadmap & progress: [`courses/plan.md`](../courses/plan.md)
- Daily reading track: `upskill-readings/{yyyy}/{mm}/`
- Project setup brief (read-only, human-authored): `prompts/000-project-setup.md`
