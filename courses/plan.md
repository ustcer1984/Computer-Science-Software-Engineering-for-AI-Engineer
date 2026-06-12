# Upskilling Plan — Course Track

> **Status: v2 DRAFT.** Revised per your kickoff feedback (deeper foundations, cloud-from-zero,
> full cyber-security track). Per `prompts/000-project-setup.md` this is still yours to revise —
> edit freely or tell me in chat. You've asked me to set the sequence; you'll steer mid-way.

Author of plan: Claude (calibrated against your self-description + a survey of `aquarium-main` and
`arena-concept-experiment`).
Last updated: 2026-06-10

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
- **Ch2 — Python typing in practice:** type hints, `mypy`/`pyright`, Pydantic as runtime validation.
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
| M01 | Ch2 Memory | 🔵 | §1 `02-memory/01-stack-heap-and-variables.md` 🔵 draft (2026-06-12) | §1 (address space; stack vs heap; names-are-pointers): pays off Ch1 §3's "a list is a million pointers" IOU. Process address-space map; stack = bump-pointer/automatic/bounded (→ RecursionError as railing before native-stack cliff, TCO callback to §2); heap = allocator search/GC-freed/fragments/cache-cold. The pivot: Python name = pointer to heap object, assignment copies the pointer; everything-is-an-object incl. ints. Mutability as the only built-in protection; aliasing; `==` vs `is` + small-int cache. His-world bugs: mutable default arg, shared-state aliasing (= M04 env-leakage shape), shallow vs deep copy. Awaiting Q&A → finalize. Next §2 GC (refcount + cycle collector + GIL re-entry), §3 OOM. |
| M01 | Ch3 Concurrency | ⬜ | | |
| M01 | Ch4 I/O & kernel | ⬜ | | |
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
| M04 | Ch2 Decomposition | ⬜ | | |
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
| M12 | Ch2 Beyond text | 🔵 | §1 `02-beyond-text/01-diffusion-and-image-generation.md` ✅ (2026-06-10) | **AI thread (his stated gap + goal "understand all model types").** §1 (diffusion/image) **finalized**: he'd read DDPM and had a strong physics model. Session *confirmed* SNR-as-native-axis (=VDM), non-sequential training, coarse→fine; *corrected* two mechanisms — sampling = **annealed Langevin descent on a learned energy landscape** (not resonance/amplification); multi-step = **integrating a curved trajectory** (not noise adding detail; proof = distillation→1–4 steps). His editing analysis independently re-derived **masked inpainting + grounded segmentation** (SAM/GroundingDINO) and the agentic-editor loop; §13 captures it. Refs verified. Next: §2 video (DiT/Sora — fold in annealing + decoupled-vs-unified/Transfusion) · §3 audio/speech/TTS · §4 multimodal & representation (CLIP/VLMs, embeddings). |
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
