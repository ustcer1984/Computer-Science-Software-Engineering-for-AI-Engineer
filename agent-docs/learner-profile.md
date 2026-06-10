# Learner Profile — Zhang Zhou

> **Shared, canonical profile of the learner this repo is teaching.** All AI agents (Claude, Codex,
> Cursor, …) should read this for context and keep it current. Lives in `agent-docs/` per the repo's
> multi-agent rule. Update it when a learning session reveals something new about skills/gaps.

Last updated: 2026-06-10 (v4 — added 2026-06-10 reading session: energy/thermal reframing of GPU
perf + Osmani career-shift mapping). Prior: v3 (2026-06-09) added reading-track progress;
v2 (2026-06-08) corrected after learner feedback; initial calibration from self-description + code
survey of `/home/zhangzhou/Desktop/Projects/aquarium-main` and
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
