# Learner Profile — Zhang Zhou

> **Shared, canonical profile of the learner this repo is teaching.** All AI agents (Claude, Codex,
> Cursor, …) should read this for context and keep it current. Lives in `agent-docs/` per the repo's
> multi-agent rule. Update it when a learning session reveals something new about skills/gaps.

Last updated: 2026-06-12 (v7 — M01 Ch2 §1 memory session that turned into a software-DESIGN session:
he drove it into pipeline state-management and proposed two class-based designs; strong instincts,
real decomposition gaps surfaced. Caught a genuine bug in my small-int-cache example. Flagged
`dataclass` as unfamiliar → reading queued.).
Prior: v6 (2026-06-11) reading #3: git-archaeology + software-design; he reframed git
delegation into a sharp agent-trust principle, and made a well-calibrated skim-not-study call.
v5 (2026-06-10) M04 Ch1 §1 session (code-reading mostly owned; git confirmed as gap); v4 (2026-06-10) reading session;
v3 (2026-06-09) added reading-track progress; v2 (2026-06-08) corrected after learner feedback;
initial calibration from self-description + code survey of
`/home/zhangzhou/Desktop/Projects/aquarium-main` and
`/home/zhangzhou/Desktop/Projects/arena-concept-experiment`).

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

## Learning progress (course track)
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

## Learning progress (reading track)
- **Queued readings (pick up on an upcoming reading day):**
  - **Python `dataclass` + `typing.Protocol`** *(queued 2026-06-12 from M01 Ch2 §1)* — he flagged both as
    unfamiliar when I used them in the best-practice pipeline skeleton. Cover: `@dataclass` (auto
    `__init__`/`__repr__`/`__eq__`), `frozen=True` (immutability → kills aliasing bugs), `slots=True`,
    `dataclasses.replace`, and structural typing via `Protocol`; compare dataclass vs Pydantic vs NamedTuple.
    Ties to M05 Ch2 (now in scope there too) and directly supports his decomposition work. Ref:
    <https://docs.python.org/3/library/dataclasses.html>.
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
- Course roadmap & progress: [`courses/plan.md`](../courses/plan.md)
- Daily reading track: `upskill-readings/{yyyy}/{mm}/`
- Project setup brief (read-only, human-authored): `prompts/000-project-setup.md`
