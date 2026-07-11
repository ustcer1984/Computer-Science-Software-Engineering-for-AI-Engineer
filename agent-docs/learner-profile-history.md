# Learner Profile — Change History (archive)

> **Append-only changelog for [`learner-profile.md`](learner-profile.md). Newest first.**
> The CURRENT, canonical state of the learner lives in `learner-profile.md` — read that for
> calibration. This file is the *cold* audit trail: the per-session `vN` notes kept verbatim for the
> "how we learned that" history. **On each finalize:** distil the durable signal into `learner-profile.md`,
> append the new `vN` note to the TOP here, and keep only the latest ~2–3 notes mirrored in the main file.
> (Maintenance rule recorded in [`README.md`](README.md).)

---

v27 (2026-07-12 — **course: M01 Ch4 §3 (why I/O dominates latency) finalized → core of Ch4 COMPLETE** (optional §4 zero-copy remains).
Body (prepared 07-07: the round-trip as the unit of latency; latency ≠ throughput bridged by **Little's Law** $L = \lambda W$; the critical path;
the **four levers** fewer/overlap/closer/hide; **tail-at-scale** Dean & Barroso $1 - p^{N}$; latency- vs bandwidth-bound + the bandwidth-delay
product; 2 matplotlib figs + 1 Mermaid) went **untouched**. **§9 Applied was driven by a real production latency investigation he had run** on a
low-traffic serverless service (AWS Lambda + always-on RDS) and brought to Q&A — I used it as a field test of the whole section, captured as four
threads: **(9.1)** *the latency is the round-trips* — a new matplotlib **fig3** breaks a ~3.6 s cold request into container-init +
init_db-bootstrap + first-DB-connect + Firebase-cert-fetch vs a **42 ms query = ~1%**, making §1/§7 visceral (the DB was never the bottleneck; the
seconds were cold-start setup + network round-trips). **(9.2) Little's Law inverted** — the usual worry is *too much* $\lambda$; a cold start is
the **low-$\lambda$ corner** ($\lambda$ so low the platform reclaims idle containers), so a "warmer" (timed pings) is best understood as
**injecting synthetic $\lambda$**; and Little's Law *sizes* the fix — $N_{\text{warm}} \approx \lambda_{\text{peak}} \times W$, so a page that
fans out briefly needs concurrency $> 1$ and a one-container warmer under-serves it. **(9.3) the four levers in prod** — persistent-connection
reuse & module-cached certs = Lever 1 (pay the handshake once, amortize), **static file in object storage = Lever 3 taken to its limit** (the
read path touches no Lambda/DB — the trip you don't make costs zero), background prefetch of a rare tab = Lever 4 (hide), and Lever 2 was already
there but **fan-out over cold containers amplifies the tail** (§5, each concurrent call may cold-start its own container). **(9.4) latency ≠
throughput decides the architecture** — cold-start latency is a **low-traffic pathology that self-heals as $\lambda$ rises**, so "we got popular"
is the *wrong* trigger to leave serverless *for latency*; the real trigger is **cost at high utilization**, a point on the throughput/cost axis.
**NEW durable signal — he does serious production ops/latency investigations:** log-only CloudWatch diagnosis with a confirmed zero-activity
baseline, careful before/after validation, and an **honest revert of a fix that proved net-negative** (a cert-prewarm that made public endpoints
fetch certs they never had). He **independently arrived at the right fixes** — warmer, static-S3, persistent connection, memory right-sizing —
before this session. **His applied distributed-systems / cloud-ops is a confirmed STRENGTH, not a gap** (consistent with the "pragmatic
distributed-systems patterns" skill-map entry, now with a concrete, well-executed exhibit). **Calibration — reinforces the standing v20–v26 rule
on the applied-systems axis (well-calibrated & generative; value = naming/locating, not re-ranking):** here on a real ops problem he was
generative and correct; my contribution was **(a)** mapping his ad-hoc fixes onto the **four-lever checklist** so they read as one discipline, and
**(b)** naming two gaps he had not framed — the warmer's **single-container / fan-out-concurrency limit** (a low-$\lambda$ tool does not cover a
concurrency spike; measure concurrent cold starts, not aggregate; use $N_{\text{warm}} = \lambda_{\text{peak}} \times W$), and the
**latency-vs-cost axis confusion** in his "if we get popular, move Lambda→EC2" plan (latency self-heals with traffic → the trigger is cost; and
**Fargate > raw EC2** for a lean non-profit team, **connection pooling (RDS Proxy/PgBouncer) > a bigger RDS instance** as the first DB lever, since
his queries are tiny but persistent-connection-per-container multiplies connection count). **Teach-forward: bring his real production systems and
investigations into the material as applied cases** — that is where he engages hardest and where his strength lives; steelman then *locate/name*,
do not correct. **Process:** folded the session's opening question — **why it is called "Little's Law"** (the MIT operations researcher **John
D. C. Little**, whose 1961 paper gave the first general proof) — into §2 as a short aside. Added **cold start / serverless** to the bilingual
key-terms table. Introduced two GitHub math-render traps of my own in the new §9 prose (`$\lambda$` inside `**bold**`, and a hyphen-glued opening
`$`) and caught/fixed both with the conventions rule-4 pre-push greps before commit. **Next:** optional Ch4 §4 (zero-copy / `sendfile` / page
cache) to fully close Ch4; or open **M02 Networking** (Ch4 §3 leaned on RTTs/TCP windows/BDP — the natural continuation); or rotate to M04 Ch2 §2
/ M12 Ch2 §3.).

v26 (2026-07-10 — **reading 07-07 finalized (mechanistic interpretability · Vera C. Rubin Observatory).** Two
Discovery-register feature stories; Story 2 (Rubin — 3.2-gigapixel camera, 20 TB/night firehose, dark-matter link)
was a read with no discussion, **Story 1 (interpretability) he drove into a full training-methodology thesis.**
**NEW durable signal — he has model-eval-team background** (mechanistic interp was on their roadmap but never
prioritized; the *training* team didn't know how to convert it into a usable signal) **and holds strong, original
views on how models *should* be trained.** His thesis, in its final sharpened form after I mis-framed it twice: **train
an LLM the way you teach a kid — make the phase transitions CLOSED-LOOP, gated on a readiness exam (evals +
interpretability), rather than the OPEN-LOOP predetermined token budgets used today.** Crucially **NOT** a proposal to
replace the loss (he was explicit: loss stays as the dense pretraining signal); it's a **control-theory reframe** of
*what triggers a phase change* — open-loop schedule → closed-loop feedback on a readiness signal, "like a year-end exam
promoting a student." Side-observations he raised: human learning has **no clean pre/post split** (a child learns to
speak and to follow instructions at once) and uses **prepared curricula, not a library dump**.
**Calibration — a textbook confirmation of the standing v20–v25 rule (systems/conceptual → well-calibrated &
generative, value = naming/locating not re-ranking):** he **produced the thesis himself** and **corrected me twice**
(I first over-read it as "replace loss with evals," then as "you just mean data scheduling"), each time sharpening it
back to the precise claim. My contribution was to *locate* it in the literature: **(1) the premise fix** — post-training
*already* grades by outcome not loss (RLHF/DPO/**RLVR** = grading-by-test, his own 06-16 reading), so the field is
half-way there; **(2) his exact closed-loop gate is already real in RL post-training** — automatic/adaptive curricula
that sample tasks at the frontier of ability and promote on pass-rate = **Vygotsky's zone of proximal development**
formalized; **(3) the three blockers that keep it out of *pretraining*, all plumbing not principle** — the LR schedule
is welded to a fixed horizon (→ **WSD / Warmup-Stable-Decay** loosens it, MiniCPM), the mid-run exam is noisy/expensive
(→ the strongest case *for* interp in the gate: a developmental signal like the **Local Learning Coefficient** flags the
induction-head/ICL phase transition *earlier & smoother* than the benchmark it produces, and — key — a promote/hold
**gate is Goodhart-milder than a differentiable target**, so his framing survives the gaming objection a naive
interp-loss wouldn't), and labs need **predictable compute** (adaptive-length runs are an ops/economics gamble);
**(4) failure modes he hadn't met** — fine-grained curriculum learning mostly **fails to beat a shuffled mix at scale**
(IID batches are a brutal baseline; "difficulty" ill-defined for text), and the ~10,000× **sample-efficiency gap** (a
child is fluent on ~100M words) says the lever is the **learner** (priors/embodiment/active learning — **BabyLM**), not
the **syllabus**; and **(5) the open question his analogy surfaced** — a gate is only half a policy, the unexplored half
is the **remediation rule on a *failed* exam** (feed more of the same? switch data? back up the mixture? = teacher who
*resequences* vs one who merely holds back), which is where a pedagogy-shaped loop would earn its efficiency. Landed
synthesis: **his closed-loop reframe is correct and under-exploited** — already real where the exam is cheap
(RL post-training), absent from pretraining for LR-coupling + eval-noise + compute-predictability reasons *now partially
solved*; the frontier version = **an adaptive controller that gates phase transitions on interp-confirmed readiness and
carries a remediation policy for holds.** Full record in the reading's **"What we worked out"** section, with verified
follow-up links (devinterp review, induction-heads, LLC, Mechanistic Data Attribution, Textbooks-Are-All-You-Need,
BabyLM, emergent-abilities-mirage). **Teach-forward: he is a peer-level sparring partner on AI training/methodology —
steelman then locate in the live literature, bring 2026 research, don't "correct."** His **eval-team background** and
**control-theory framing** are live anchors; **hands-dirty follow-up = reproduce a developmental-interpretability
phase-transition detection (devinterp/LLC) on a small model** on his RTX 4070.
**Process/tooling — ComfyUI image generation entered the workflow (2026-07-08 authorized, 2026-07-09 applied):** the
local `comfyui-media` skill (Z-Image Turbo) is now used for **path-4** illustrations under a strict precedence rule
(real figure → matplotlib data plot → Mermaid diagram → generated image) and two hard limits (no real-*specific*
subjects = fabrication; no baked-in text = generate-then-annotate). Reviewed the whole reading track and added **4
illustrations** to the two Discovery-register readings (07-02: undersea cable + inflation-chainsaw; 07-07: AI-mind
metaphor + generic observatory dome), **deliberately skipping the 7 technical 06-xx readings** (well-served by their
diagrams/code — an image would be filler). Rule recorded in `authoring-conventions.md` §7. **Next:** continue the
reading rotation, or the devinterp mini-repro.)

v25 (2026-07-07 — **hobby econ E02 §4 (the business cycle) finalized → Module E02 (Macroeconomics) COMPLETE
(§§1–4).** Body (drafted 07-02; 4 matplotlib figs + mermaid one-pager + bilingual glossary): anatomy & NBER
dating ("not a clock"; the wrong "two-quarters" rule); the **output gap** as the cycle's one state variable
(its sign predicts unemployment via Okun and inflation via Phillips — the three headlines as read-outs of one
state); **demand-vs-supply shocks** via AD–AS (demand moves P & Y together = the normal/fixable cycle; supply
moves them apart = stagflation); **propagation** (multiplier $1/(1-c)$ = §2 paradox-of-thrift named, accelerator,
confidence/coordination, **financial/balance-sheet/debt-deflation/Minsky**, inventories) + a **Frisch–Slutsky
rocking-horse** lens (cycle = impulse response of a shocked damped system); the **expectations-augmented Phillips
curve** — $\pi = \pi^{e} - \beta(u - u^{\ast})$, a short-run trade-off with a **vertical long-run** at
$u^{\ast}$, the §3 cliffhanger paid off (the E03 bridge); and **leading/coincident/lagging** indicators (yield-curve inversion,
Sahm rule).

**§10 = a three-thread live session the learner drove**, and it is the headline signal — it advances the
standing v20–v24 calibration one notch: **beyond being *well-calibrated* in conceptual/systems/social-science,
he now *generates his own correct extensions and counter-arguments and initiates the deep arc*.** My value-add
in these domains is **naming / locating / decoupling**, not dominant-cause re-ranking (that mode is reserved for
*physical-magnitude* questions, per v21/v23/v24).

- **(10a) "What acts as a damper in the economy?"** — he took the §4 Frisch–Slutsky framing and asked the
  mechanical/electrical engineer's question (a shock is damped by a dashpot / an RC network — what is the
  economy's $c\dot{x}$ term?). Mapped $m\ddot{x} + c\dot{x} + kx = F(t)$ (multiplier–accelerator = mass+spring;
  shocks §3 = forcing): **automatic stabilizers** = the passive dashpot (they *shrink the multiplier* $1/(1-c)$
  by cutting the effective MPC); **buffers + consumption-smoothing** = the more genuinely velocity-proportional
  damping (SG reserves = a national dashpot, local lens); **discretionary monetary/fiscal policy** = an *active*
  damper with a **destabilizing lag** (Friedman's long-and-variable; rules-vs-discretion; Taylor rule = the
  feedback law → E03); the twist — **leverage/finance = negative damping (Minsky anti-damper)** → macroprudential
  policy = engineering damping back in; and price-flexibility = the *spring* ($kx$), not a damper (weak/sticky §2,
  can go negative = debt-deflation).
- **(10b) AI boom or AI bubble?** (live case, I web-researched mid-2026 data). He framed it in the section's own
  language — **both supply and demand curves shifting rapidly** (E01 §2 indeterminacy) and the **hardware
  price-hike (GPU/HBM) pulling in heavy investment → oversupply worry** — fusing his **AI-engineer domain with
  econ**, and his **E01 §2 §10b semiconductor-cobweb intuition resurfaced**. Keystone: *not boom-XOR-bubble →
  separate three questions* (demand real & supply-constrained now / financial bubble in circular-financing +
  debt + GPU-depreciation-mismatch / hardware overshoot). The oversupply worry = **the cobweb model** + the **§4
  accelerator** (AI demand can keep growing yet capex crash — only takes deceleration) + the **§4 bullwhip**;
  circular financing = the 10a **negative damping**. Ranked by layer (memory/HBM most cyclical; labs most
  financially fragile; Nvidia margins normalize via custom silicon = E01 §4 §9 moat race; datacenters durable;
  apps = the ROI crux). Bottom line: **real, durable transition financed partly by a speculative capital cycle
  with a near-inevitable overinvestment correction = telecom-fiber-2000, not tulips**; watch §6 leading
  indicators. *(Sources retrieved 2026-07-07: IEEE ComSoc/Introl on capex & AI-debt; IEEE Spectrum/IDC/TrendForce
  on DRAM/HBM shortage & glut risk; Bloomberg/Noah Smith on circular financing; INSEAD on the bubble debate.)*
- **(10c) Is capitalism *doomed* by the cycle? — Marxist crisis theory vs Keynes.** He brought his **中国
  pre-graduate 马克思主义政治经济学**, rejected 剩余价值=剥削 (sharpened: the labour theory of value was abandoned
  at the marginal revolution → each factor paid its marginal product, E01 §4; the steelman survives as
  **monopsony**, §3), but found the *crisis* argument hard to refute. Keystone #1 — **split the mechanism from
  the conclusion**: the underconsumption/MPC demand-gap mechanism is **right** (it is *his own §2 §9b model*,
  and = Keynes's effective demand / Piketty $r>g$ / secular stagnation — mainstream absorbed it), but the
  **inevitability is wrong** (5 rebuttals: the investment channel makes it a contingent $S>I$ condition;
  offset-able by the 10a dampers/redistribution; the failed immiseration+collapse prediction; crises are
  multi-causal incl. supply-shock stagflation = the *opposite* of overproduction; it needs sticky prices to
  bite → a fixable coordination failure) → the **Keynesian synthesis** (same mechanism, opposite conclusion;
  capitalism absorbed the critique by building the dampers). **The learner then supplied two original, correct
  counter-arguments** to the concentration premise — **wealth dissipation (富不过三代, bankruptcy, creative
  destruction)** and **human-capital mobility (Musk)** — and keystone #2 was **splitting Marx into Pillar A
  (economic: capital-*share* concentration → crisis) vs Pillar B (sociological: a permanent hereditary
  capitalist class → revolution)**: his arguments **kill Pillar B** (which *is* wrong) but **not Pillar A**
  (individual churn ≠ structural concentration — Piketty shows concentration rising *despite* churn; dissipation
  historically needed war/policy to beat $r>g$; downturns re-concentrate on the QE recovery; Musk =
  skill→convert-to-capital→compound + survivorship bias + winner-take-all is *more* concentrating; the Great
  Gatsby curve). **Landing (his, and I agreed): a real concentration concern, but no destiny in either
  direction — concentration-vs-dissipation is a policy choice variable, not a law of history.**

**Teach-forward (durable):** in econ/social-science, **peer-level intellectual sparring** — steelman his idea,
then add value by *locating which pillar/mechanism it hits* and *naming*, not correcting; he **initiates**
history-of-thought and political-economy depth and drives multi-thread arcs. **Bilingual Western↔Marxist
economic vocabulary bridging is load-bearing** for this learner (he was schooled in the Marxist tradition and
reads across both). **Lead econ sections toward a live current case + real-time web research** (confirmed a
third time: E01 §3 sugar policy, E02 §3 the 2026 Fed, now the AI capex cycle). He **fluently connects econ to
his AI-engineer domain** (GPU/memory cycles, the semiconductor cobweb). **Process:** found & fixed **two new
GitHub math-render traps** — (i) an escaped `\$` (literal dollar, e.g. `\$1`) on the same line as an inline
`$…$` span is read as an opening math delimiter and jams the prose into an italic run while dumping the real
formula as literal LaTeX (fix: spell the money out); (ii) a re-confirmed indented-`$$`-in-list leak (fix: inline
math) — both added to `authoring-conventions.md` rule 4. Playwright-on-the-GitHub-blob verification is now the
routine final check. **Next: E03 §1 (money & how banks create it)** — the endogenous/credit-money thread the
learner began reinventing in §2 §9b.)

---

v24 (2026-07-07 — **course: M01 Ch4 §2 (blocking/non-blocking I/O & multiplexing) finalized.** Body (five I/O
models · thread-per-connection vs event loop · C10k · `select`→`poll`→`epoll` scaling · `io_uring`/IOCP completion model)
pitched high, went **untouched**; the whole session was one deep thread into the **io_uring completion model**, built from
his **factory + two-warehouse analogy** (SQ = inbox/raw-materials, CQ = outbox/finished-goods; + a work-order ticket that
travels with the item and returns stamped on it = io_uring's `user_data`, echoed verbatim SQE→CQE). **Two predictions, both
well-ranked:** (a) *"SQ→CQ probably not FIFO"* → correct — completions arrive in **completion order**, not submission order
(and execution order isn't guaranteed either without `IOSQE_IO_LINK`). (b) *"user needs an orchestrator to sort & deliver to
the target client"* → correct once we aligned on the word: he meant **sortation** (a parcel-hub scanner reading a barcode and
diverting each package to its chute), i.e. a **demultiplex** — read the echoed `user_data` tag → wake the right waiter, an
**$O(1)$** pointer-deref/lookup, not a search, and order-of-arrival-irrelevant. Named precisely = a hardware demux / a network
switch. **One genuine refinement (a decoupling, not a dominant-cause re-rank):** the completion **dispatcher (the "sorters")
is intrinsic to the completion model** — every completion-model runtime runs a reap-and-route loop, even IOCP, even with a
blocking syscall — and it is **orthogonal to the zero-syscall knob**: zero-syscall is bought by **`SQPOLL`** (a kernel thread
that watches the SQ ring so no `io_uring_enter` "doorbell" is needed; completions are read straight from the shared CQ ring),
which trades **a busy CPU core for eliminated boundary crossings** — his semiconductor *derating* framing. **Callbacks:** the
tag-routing pattern is cross-OS — **Windows IOCP's `OVERLAPPED` pointer + completion key ARE `user_data`**, `GetQueuedCompletionStatus`
= `io_uring_wait_cqe` (§9a from §1); it's also how **hardware already talks to the kernel** — **NVMe/NIC submission+completion
descriptor rings with a Command Identifier echoed on completion** (io_uring deliberately mirrors the hardware queue design;
his hardware/semiconductor lens); and the dispatcher already exists in **asyncio** (`user_data` ≈ the `Task`/`Future`) and at
his **application layer** (matching 2,000 fan-out responses back to requests by `request_id` = the same correlation-tag
pattern). **IMPORTANT calibration refinement (updates the v21/v23 split):** the long-standing "captures a real *secondary*
effect but **mis-ranks it vs the dominant cause**" tendency is specific to ranking **competing PHYSICAL MAGNITUDES**
(fragmentation vs bandwidth, external vs internal waste, GPU internals) — it does **NOT** extend to **mechanism reasoned
through a systems/logistics analogy**, which is a genuine **strength**. Here, on a *mechanistic* io_uring detail, he was
**well-calibrated**: both predictions held, the residual work was *naming* (sortation = demux) and *decoupling* (dispatcher ⟂
zero-syscall), and — logged for honest pattern-reading — part of my own first-pass "re-rank" was **fighting his word "sort"
rather than his idea.** **Teach-forward:** for mechanism questions, hand him an analogy and let him run it; add value by
precise naming + separating bundled concepts, not by correcting. **Next:** Ch4 §3 (why I/O dominates latency — last core
piece of Ch4); or Ch4 §4 (zero-copy / `sendfile` / page cache, if added); or rotate to M04 Ch2 §2 / M12 Ch2 §3.).

v23 (2026-07-06 — **course: M01 Ch4 §1 (the kernel boundary & the system call) finalized → opens Ch4 (I/O,
syscalls & the kernel boundary).** First section of Ch4; the bottom-up finale of M01. Cashes Ch3 §2's IOUs:
`epoll_wait`/`selector.select` are *syscalls*; a blocking `read` parks the thread *in the kernel* (why the GIL is free
across I/O); "the loop's one blocking call." **Body (pitched high) went untouched:** user vs kernel mode (rings;
mode-switch ≠ context-switch; kernel = privileged library in every address space, not a process); the syscall as a
guarded trap at the instruction level (`rax`/`rdi`… ABI, the one fixed `LSTAR` entry, `sys_call_table` dispatch,
argument validation, `sysret`, `errno`) vs a function call; the cost ladder (fn ≪ syscall ≪ context switch) with a real
log-scale latency figure + the two rules (batch crossings · park don't spin); Meltdown→KPTI (Ch1 §3 callback; `pti`
active on this box); libc wrappers + the vDSO; a real captured `strace` walkthrough; `mmap`/`llama.cpp`; interrupts vs
faults vs syscalls. 1 matplotlib fig + 1 Mermaid diagram (both visually verified); refs verified live; bilingual 中文
key-terms table. **§9 Applied — he asked nothing about the body and drove two comparative *portability* threads past the
material** (his signature "one layer past the text," both comparative = his stated preference): **(9a) "Are syscalls
the same on Windows/Linux?"** → keeper *separate the hardware from the contract* — the two rings, the `syscall`/`sysret`
trap, the cost ladder, even Meltdown/KPTI (Windows = KVA Shadow) are **hardware-universal**; per-OS is the **vocabulary**
+ the **stable-ABI location**: Linux freezes it *at the syscall* (num 0 = `read` forever; raw syscalls fine), **Windows
one layer up in `ntdll`/`kernel32`** (numbers/SSDT private, shift per build); plus the **I/O model** — `epoll`
readiness/reactor vs Windows **IOCP** completion/proactor (asyncio `Selector`- vs `Proactor`-EventLoop; `io_uring` =
Linux converging). **(9b) "x86 vs ARM; why won't x86 Windows apps run on ARM Windows?"** → keeper *the ISA is the
binary's mother tongue*: different ISA = different bytes → **native impossible**; CISC/RISC nuance (micro-ops,
ISA-as-contract; fixed-4B vs 1–15B decode → power efficiency; 31 vs 16 registers); the sleeper = **strong x86-TSO vs
weak-ARM memory ordering** → latent data races that "worked" on x86 break on Graviton (**Ch3 §3 hardware-floor
callback**); emulation (Prism/Rosetta) bridges **user-mode only** and breaks at (a) ring-0 drivers, (b) perf, (c) mixing
ISAs in one process; tied to his **Lambda/Graviton/Docker multi-arch** + **Python arch-neutral bytecode** (Ch1 §1
callback). **Calibration (reinforces v21/v22):** conceptual/systems → **well-calibrated, not mis-ranked**; these were
*open exploratory questions*, so value added = **structure + naming + wiring to owned material**, NOT dominant-cause
re-ranking. **NEW durable signal — he reflexively tests a mechanism's *generality* ("is this Linux-only? does it hold on
Windows/ARM?").** Feed it: **teach the universal principle first, then explicitly flag what's platform/arch-specific**;
when material is written for one platform, mark hardware-universal vs OS/ISA-specific (acted on: added a §1 portability
callout, and named the pattern in the status/why blocks). His **AWS cross-arch experience (Graviton/Lambda/Docker) is a
live anchor** — the x86/ARM material landed on lived practice. **This session = a Ch1 §3 / Ch1 §5 trailer**; reopen the
x86/ARM weak-memory hazard at M01 Ch5. **Next:** Ch4 §2 (blocking/non-blocking, `epoll`/`io_uring`, C10k) — direct
continuation; or Ch4 §3 (I/O dominates latency); or rotate to M04 Ch2 §2 / M12 Ch2 §3.).

v22 (2026-07-02 — **reading-track redefined (`prompts/002`) + reading #8 finalized: undersea cables (career) ·
Milei's Argentina (hobby).** Process: the **reading track is now National-Geographic/Discovery genre, NOT a course
brought forward** (wonder/currency/case-studies/debates), and each day pairs **1 career + 1 hobby topic** that need
**not** map to a course chapter (career = any positive-career-effect topic; hobby = anything genuinely interesting,
agent's judgment). Rule → `authoring-conventions.md` §6; README updated; memory `reading-track-is-discovery-not-preteach`
added. Standing instruction confirmed: **always commit & push material (drafts included)** — he reads on GitHub
(memory `commit-directly-to-main` updated). **Calibration — one clean instance of each half of the v21 split in a
single session.** *Story 1 — Starlink vs undersea cables (physical/systems):* his thesis "scale satellite count →
satellites beat cables" was **well-calibrated on the systems/economics axis** (cheap launch via Starship = the real
lever; distributed graceful degradation, 1-of-7000 ≪ 1-of-3-cables; seabed sabotage is uniquely easy — all credited)
but **mis-ranked the physics**: his "phased array + laser comms → everyone shares the same bandwidth without
interference → capacity scales freely" → re-ranked to (i) satellite↔ground RF = **spatial reuse of a shared, finite,
ITU-regulated spectrum**, beam count capped by diffraction $\theta \approx \lambda/D$ + orbital geometry, so capacity
scales **sub-linearly** vs fiber's **linear** private-waveguide scaling (lay another interference-free ~10 THz strand),
and laser inter-satellite links add zero *ground-facing* capacity; (ii) the **demand-geometry crux** — satellite
capacity is spread over geography by construction while demand + cables are concentrated (~450 Tbps whole constellation
vs 250 Tbps one cable into one metro), so **dense areas are satellites' hardest case**, inverting his "grow into dense
markets later" claim. Landed conclusion: **not replacement but a tiered system — fiber core + LEO edge & low-latency
overlay** (latency is the one axis LEO wins: c-in-vacuum + straight laser mesh beats bent ⅔-c fiber); boundary slides
satellite-ward as launch cheapens, ocean trunk stays glass. Corrected too: a cable **landing station ≠ a datacenter**
(light infra), so his proposed "small centralized receiver site" is just a landing station/teleport and concedes fiber
backhaul. Integrated instantly on naming — the signature pattern. *Story 2 — Milei's Argentina (social-science):*
**well-calibrated**, as v20/v21 predict. His read ("mostly a success") rests on strong moves that **largely hold**:
(1) the **malinvestment / flight-from-cash** framing (hyperinflation pumps forward-buying → some pre-Milei manufacturing
demand was distortion, and its unwind is the cure working); (2) the **attribution correction** (Argentina's
manufacturing was structurally uncompetitive behind ~70 yrs of import-substitution tariffs *before* Milei — blaming its
fall on him confuses trigger with disease); (3) the **poverty rebound 53%→~32%** as evidence the pain is front-loaded,
which the op-ed under-weights. Needed **naming/nuance, not a dominant-cause re-rank**: (a) the **real-exchange-rate
anchor** — the tool that crushed inflation left the peso overvalued, which *fights* the export pivot he's counting on
(**confidence ≠ competitiveness**; Convertibility 1991→2001 rhyme); (b) **trade is USD-invoiced**, so hyperinflation
did *not* stop trade (Argentina kept exporting commodities, ran surpluses) — the **`cepo`** (capital controls + multiple
FX rates) strangled it, and **Milei lifting the `cepo` (Apr 2025) is the genuine pro-trade win** his intuition pointed
at; the real "confidence" channel is **trade finance / investment**, not willingness-to-hold-pesos; (c) the synthesis
that reconciled it — **two export sectors on two clocks**: commodities (never stopped, dollar-priced, rate-exposed *now*,
financing the whole stabilization) vs manufactured/new exports (need the stability precondition — his sequencing
argument is right *there*). He **refined his own argument mid-thread** (the trade-under-hyperinflation sequencing point)
— peer-level. Only over-rank: "the lost demand was all fake" — some was genuine immiseration (real-wage collapse), not
only distortion unwinding. **Meta:** he now **drives readings with a thesis** (sparring, not passive intake) — the
"expand my view" reading track is working. **Teach-forward re-confirmed:** physical/mechanistic → hypothesize-then-
re-rank to the dominant mechanism; systems/social-science → full depth, lead with naming/nuance. **Process nit:** he
caught a mis-cited link — a generic **BBC topics feed** labeled "Argentina — BBC News" showing irrelevant stories — →
a citation must resolve to *fixed, on-topic content*, not a rolling feed (HTTP 200 ≠ valid citation); swapped to a
dated Semafor article. **Next:** two fresh topics next reading day (1 career, 1 hobby), keep diversifying.).

v21 (2026-07-02 — **course-track backfill: M01 Ch3 §2 (async, 06-25) + §3 (synchronization &
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

v20 (2026-07-02 — **hobby econ Module E02 macro §§1–3 finalized: GDP (§1, 06-26), inflation (§2, 06-29),
unemployment (§3, 07-02).** These postdated v18/v19 and had only been logged in `hobby/economy-and-finance/
plan.md`; now distilled into the main file's hobby-track section. **Durable calibration:** the standing
"captures a real *secondary* effect but **mis-ranks it vs the dominant cause**" pattern is **specific to
physical/mechanistic detail** — in **conceptual / systems / social-science reasoning he is well-calibrated,
not mis-ranked.** E02 §2 (§9): rebuilt *endogenous/credit money* and a *steady-state* model from scratch and
relocated his own "inflation punishes thrift" moral unease onto the right target (idle-cash vs saving;
distributional defect; externalities/growth-dependence/discount-rate); needed only naming + two corrections
(Minsky debt-deferral; MPC demand-gap), not a dominant-cause re-rank. E02 §3 (§11, the 07-02 session): pulled
**one** buried mechanics question outward through the whole monetary-policy chain — *how is potential growth
$g^{\ast}$ estimated?* (unobservable; production-function/filters; real-time-revision failure modes, Orphanides)
→ the **Fed's reaction function** (one lever/two targets; Taylor rule; corrected his "both-high → raise" —
high unemployment argues for *cutting*; stagflation is a genuine conflict) → **central-bank independence**
(time-inconsistency/inflation-bias, fiscal dominance, credibility paradox, Burns/Nixon 1972) → **a live 2026
case he asked me to web-research** (Powell's chair term ended 15 May; **Kevin Warsh**, Trump's own pick, held
rates 12–0 and flipped the dot plot to a hike bias with inflation past 4%; the "capture-test" caveat). **How
to teach forward (systems/social-science):** teach at full depth, expect substantive push-back, don't lead
with re-ranking; ground the abstraction in a **live current case** and offer **real-time research** — he
explicitly wanted it here. **Process/tooling:** two more GitHub-math render traps found via the live-Playwright
check & documented in `authoring-conventions.md` rule 4 — `($…(…)…$)` (literal parens wrapping math that
itself contains parens) and inline math inside `*emphasis*` (`*… $x$ …*`) both leak the raw `$…$`. **Next:**
E02 §4 (business cycle) closes the macro module; the inflation-unemployment trade-off bridges to E03
(monetary policy).).

v19 (2026-06-28 — **reading #7: databases — storage engines & isolation ✅ finalized.**
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
Prior: v17 (2026-06-24 — **Econ E01 §4 "firms, costs & competition" ✅ finalized; Module E01 done.**
He studied the body, then in Q&A drove it straight to a live case he cares about — **frontier AI labs
(OpenAI/Anthropic) serving below AVC yet not shutting down** — and largely *self-derived* the resolution:
huge FC+VC, price < per-token cost, kept alive by investors betting on future pricing power + falling
hardware cost. Same confirmed pattern as every prior session: **he proposes a structurally-correct model and
integrates the re-rank instantly when the dominant principle is named.** The thread (now §9 Applied of the
file): the keystone re-rank is **static single-period shutdown rule → dynamic multi-period NPV** (capital
markets relax the self-financing assumption); then (b) most of the "loss" is **training-FC/investment**, not
below-AVC *serving*, and committed compute is fixed not variable (he'd fused them); (c) his "tech advance +
scaling lowers cost" instinct = the **learning/experience curve = a *moving* LRAC**, named precisely vs §4's
*static* economies of scale — a distinction he lacked the vocab for but had the intuition for; (d) it's a
**race to build barriers to entry** (penetration pricing/blitzscaling, Amazon comp) to manufacture a §3
monopoly. He explicitly asked for **failure modes** (his standing want): gave him commoditization →
open-weight → §4 *airline* outcome, cost-declines-competed-away, and the Red-Queen FC race. **Signals:**
(i) **strong dynamic/systems reasoning** — he intuitively reframed a static rule as a multi-period optimization
under endogenous curves *before* being told, his physics/systems strength showing again (cf. v16's self-as-
system move); (ii) he reasons natively about **AI-industry economics** — the examples that land hardest are
AI/compute ones; (iii) gap surfaced & filled: he conflated *fixed vs variable* with *training vs serving*, and
lacked the static-scale vs dynamic-learning-curve distinction — both now taught. No process/authoring feedback
this session; the §3/§8-style "read material → Q&A → capture thread → finalize" loop is working well and he
likes it ("finalize here"). Module E01 (micro foundations) complete; next is E02 macro (GDP) or a
reports-first jump to E07.).
Prior: v16 (2026-06-21 — **reading #6: RL, verifiable rewards & environments ✅ finalized.** A
**metacognitive** session, new in kind: he left the readings' content alone and instead **mapped the training
course itself onto the RL-environment formalism** — he = trainee (≈ policy), me = task-generator + LLM-as-judge —
and asked whether it holds. It does, and the session became about *where it breaks.* The durable threads (now in
the reading's "What we worked out"): **(1)** the `E=(T,H,V,S,C)` map onto his setup, with the keystone he'd missed
named — **`S` (state) = this very profile + the progress tracker**, the thing that makes the course an
*adaptive curriculum* (T aimed at his frontier/ZPD) rather than a one-shot eval; his cold-start = the RL
*exploration* phase. **(2)** disentangled his fused "scope/constitution/task" → the two keys are **T (task
distribution)** and **V's rubric (the constitution / how it's graded)**. **(3)** three seams where the analogy
breaks, all high-value: *(a)* his feedback channel is **natural-language explanation, not a scalar reward** → he's
closer to **Reflexion / verbal-RL** than GRPO, so one good correction outweighs 1,000 binary rewards (his learning
bottleneck is feedback *bandwidth/quality*, not throughput); *(b)* **he controls his own verifier → self-reward-
hacking risk** ("performing understanding" = fluent jargon-correct restatement that passes my judgment without the
model forming), compounded by my **task-setter+judge role-fusion** (an RL bias anti-pattern) — fix is *verifiable
beats judgeable* turned on himself (predict-then-run, apply-to-real-repo, teach/build-break); *(c)* adaptive
curriculum vs fixed env. **Signals:** (i) **strong metacognition / abstraction-transfer** — he spontaneously
lifted a just-learned formalism and applied it reflexively to his own learning process; the self-as-system move,
consistent with his physics/systems strength. (ii) **A concrete teaching lever falls out:** he himself flagged the
"performing understanding" failure mode, so going forward **don't rely only on Q&A-judged understanding — give him
verifiable checks** (predict-then-run, apply to Arena/aquarium, reconstruct-from-scratch) where reality grades, not
me. (iii) Confirms the AI-thread rotation note: do swing out of AI next (databases / networking). Left him one
**open exercise** (carried in the reading): design a verifiable, un-gameable self-check for this material by
applying the T/V decomposition to his own Arena judge rubric / eval pipeline — doubles as a shippable improvement.
Clean track-economy ("we can finalize here").).
Prior: v15 (2026-06-18 — **M04 Ch2 §1 "cohesion, coupling & module depth" ✅ finalized + a major,
durable authoring calibration about how to pitch the whole course.** The section (his clearest gap,
decomposition) was prepared, then he steered it with a real design problem and three pieces of
process feedback. **The design thread (now §11 Applied of the file):** he described the actual origin of
a pipeline-organization smell — a linear pipeline of independent steps split into two files **by technical
kind** (I/O-bound `process_waiting.py` vs CPU-only `process_no_waiting.py`), with new step functions
"casually" dropped into whichever matched. He asked whether one-file-per-function is better and felt it
"isn't much." **Correct instinct, exactly the §1 lesson:** grouping by technical kind is *logical
cohesion* (= package-by-layer), and one-file-per-function only changes *granularity*, not the *organizing
principle* (slides right on the U-curve). The re-rank he took: the file layout was conflating two axes —
*what a step does* (the org axis for source) vs *whether it waits on I/O* (a runtime property that belongs
in the **interface + runner**, not the directory). He then proposed his own fix (a `process_interface.py`
of all signatures + a `process_logic/` folder); I pressure-tested it — the C-header `.h/.c` split is a
Python anti-pattern (duplicated signatures that drift; separates interface from body = shallow boundary).
Landed: **"an interface file is not a list of signatures"** — what earns a shared file is the *one shared
contract* (`Step` Protocol) + the *catalog that wires the steps* (`PIPELINE` registry), bodies grouped by
cohesion in `steps/`; and once I/O-ness lives in the type, the runner can **fan out the independent I/O
steps** (the M01 Ch3 §1 sequential-await→gather audit item, surfacing on its own). He agreed the refined
layout was "much better." Same confirmed teaching pattern: he proposes a plausible design, integrates the
re-rank instantly when the dominant principle is named. **THE BIG CALIBRATION — three durable rules for
ALL future material (now `agent-docs/authoring-conventions.md` rule 3):** (1) **the two reference repos
were shared once to calibrate his level, NOT as the course's purpose** — teach the subjects
*comprehensively*, like a real course, don't frame sections as "fix file X"; (2) **stop over-citing the
repos** (`process_no_waiting.py`/`ArenaPage.jsx`/line counts were sprinkled everywhere — cut it); (3) **a
code snippet he shows in Q&A is a question, not an endorsement** — don't assume it's his production code or
call it "your bad code"; and (4, his strongest want) **prefer real-world canonical good/bad examples and
teach failure modes he hasn't encountered** ("Let me know the failure mode I have not encountered
before"). I finalized §1 by re-anchoring every example to real systems — Unix file API / Go `io.Reader` /
`requests` (deep), Java stream wrappers / Java `Date` (shallow/leaky), ORM N+1 + TCP-over-IP (Spolsky
leaks), Y2K (change amplification), Segment + Amazon Prime Video monolith reversals + Spring's
`AbstractSingletonProxyFactoryBean` + FizzBuzzEnterpriseEdition (over-decomposition far-wall). **This
recalibrates a standing bias in this profile and the plan:** many earlier notes lean hard on "his clearest
gap is the 2,434/3,270-LoC files" and "use his pipeline code" — that framing was useful for *pitch level*
but he does NOT want it as the course's organizing goal. Teach-forward: comprehensive coverage, real-world
exemplars, repo references sparing and only when they truly illuminate, his snippets treated as
discussion not confession.).
Prior: v14 (2026-06-17 — **Economy & Finance E01 §2 "supply, demand & how prices coordinate a market"**
✅ finalized + **durable authoring-style feedback that applies to ALL tracks**. He'd seen supply–demand before,
found the body easy, and (signature move) went after the model's **foundational assumptions** rather than its
content: he argued the whole apparatus rests on two pre-assumptions that "don't always hold" — **(1) a free
market** and **(2) that the equilibrium actually forms** (everyone knows the price; info takes time). Both real;
both **mis-ranked as "regimes where the model is falsified."** The re-rank he took (now §10 of the file):
**(1)** separate the *forces* (scarcity, diminishing MB / rising MC — universal) from the *solver* (the price
mechanism is one solver; central planning is another on the same problem). A planned economy doesn't repeal
S/D — it overrides the price signal while scarcity remains = **§6 price-controls scaled up**, and its
shortages/gluts are S/D reasserting through a non-price channel (USSR = confirming experiment, not
counterexample). Why planning fails = the **socialist calculation / Hayek knowledge problem**, which is the §5
"price = dual variable / distributed computation" point sharpened. Genuine residual where he's right =
**market failure** (the *competitive* assumptions: no market power/externalities, exogenous preferences). **(2)**
equilibrium is the optimality **condition** ($Z(P^\ast)=0$), not the search **dynamics** — *his own §1-era
condition-vs-dynamics distinction returning*; info lag is about the *path*, leaves the fixed point intact;
modelled as a friction it **predicts price dispersion** (search theory, Stigler 1961), and at the extreme
(production lag + adaptive expectations) gives genuine **non-convergence** — the **cobweb / hog cycle**, which
he immediately mapped to the **semiconductor cycle he lived through**. Same confirmed pattern: plausible
premise capturing a real effect, needs the dominant frame named; integrates instantly. **NEW & IMPORTANT —
he set three authoring rules for all future material** (now `agent-docs/authoring-conventions.md`): **(a) use
the physics/analogy lens *sparingly*, only where it earns its place — deriving everyday results via heavy
formalism (his example: full Lagrange for S/D) is overkill, and "not every physics PhD still remembers
Lagrange after the classroom"; don't make the basics *depend* on advanced tools. (b) Show real charts/plots —
prefer a good existing public figure, or if self-made draw the actual thing with dummy values (e.g. matplotlib
curves), not just conceptual box-flowcharts; he explicitly asked "why explain the demand/supply curves in text
only?" (c) Always write math in LaTeX (`$...$`), never code backticks.** This is a real calibration: the
physics-lens lever (logged since v3) is genuine but I had been **over-applying** it. Teach-forward: keep the
hypothesis→re-rank method and the lens for *genuinely hard* ideas, but dial back lens density, add real plots,
and LaTeX all math. He scoped the §2 revision tightly ("just LaTeX the math, don't rewrite the rest, finalize")
— good track-economy again. Also fixed a stale Wheelan/Norton ref link (404) in both §1 and §2 while verifying.).
Prior: v13 (2026-06-16 — **first HOBBY-track session: Economy & Finance E01 §1 "how economists think"**
✅ finalized. He left the body untouched and instead stress-tested the section's *core analogy* ("economics =
constrained optimization") with two methodological objections imported straight from his ML/optimization world —
exactly the predicted mode, and strong evidence the **physics/ML-analogy teaching lever works for non-CS subjects
too.** Two threads (now §11 of the file): **(1) "the cost surface isn't fixed"** — he argued the econ value
surface is heterogeneous, unobservable, and non-stationary (unlike a supervised loss `L(w)`), hence prediction is
hard. All real; re-ranked to the **dominant** frame — the surface is **endogenous/coupled** (each agent's
landscape is produced by the others' optimization) → solution concept is a **fixed point/equilibrium, not a
minimum**. He'd *already* reached, unprompted, for **multi-agent RL / GANs** as the right analogy (vs supervised
SGD) — confirms his LLM/ML-architecture strength generalizes to *systems/strategic* reasoning; I only added the
names (reflexivity/Lucas; "the map rewrites the territory"). **(2) opportunity cost / rationality vs local
minima — his signature hypothesis pattern again** (real effect, mis-ranked, integrates instantly on naming): he
analogized "don't follow the first-order gradient → local min" to "an agent who flouts opportunity cost can still
be rational." Re-rank that landed: first-order **optimality *condition*** (`MB=MC`, the intertemporal **Euler
equation** — holds *at the global optimum too*) vs first-order **search *dynamics*** (greedy descent, what gets
stuck). His short-vs-long example is **inside** the model (intertemporal optimization/NPV; **opportunity cost ≠
short-termism**; myopia is a property of the *objective*, not of marginalism). Where his local-min point genuinely
bites: **non-convexity** (lock-in, poverty traps, coordination failures) + **bounded rationality** (Simon's
satisficing = limited-lookahead local search). The synthesis he was circling, in his own vocabulary: apparent
irrationality (exploration/noise) = the **annealing temperature / ε-greedy term** that escapes local optima →
*higher-order* rationality (explore/exploit). Closed with the falsifiability caveat (revealed-preference
tautology). Clean track-economy: "we can finalize here." **NEW ACTION — he asked for "game theory + its math";**
I judged it a **separate hobby subject** (`hobby/game-theory/plan.md`), not an econ add-on, because it
**double-serves econ AND his AI career** (he himself bridged equilibria↔GANs/MARL; plus mechanism design,
Shapley/SHAP). Offered to promote it to the main `courses/` track if he wants rigor/demonstrables. **Teach-forward
(now confirmed across CS *and* a brand-new humanities-ish subject): let him state the plausible hypothesis, then
re-rank against the dominant mechanism with the precise machinery, reaching for physics/ML analogies — he
integrates instantly.**).
Prior: v12 (2026-06-16 — M01 Ch3 §1 concurrency vs parallelism & the GIL → **§1 finalized**. The body
(two axes, the three models, the GIL scope, free-threading) was written to *cash in* his existing async/GIL keystones rather than re-teach,
and it went **untouched** — he absorbed it and drove the entire session **applying** it to a concrete **LLM-eval pipeline** (batch-generate →
parse → batch-judge → parse → aggregate). Three threads, all in his signature mode (sharp hypothesis → re-rank against the dominant mechanism):
**(1)** "the `openai` library does batch inference — what's the mechanism?" → untangled **"batch" = three layers** (client async fan-out / the
Batch API / server-side continuous batching); identified his case as §1–§4 client fan-out, and took the re-rank that the ceiling is the **rate
limit, not the GIL/CPU**. **(2)** the `asyncio.gather` failure mode — his **scheduler** model was correct (ready-FIFO, await-yields, completion
re-enqueued), but his **failure** model **fused two opposite hangs**: he said "the thread hangs" for a task parked-on-I/O-forever, when in fact
the loop and the other 999 are fine and only `gather`'s **join barrier** waits (results recoverable) — vs the genuinely loop-freezing case of a
*blocking* call (§4 footgun). Landed the keeper that **`return_exceptions` handles errors but only a timeout handles silence.** **(3)** parse/calc
CPU steps — strategic instinct right (negligible vs I/O), but his split "math→C-lib, parse→multiprocessing" was inconsistent; re-ranked to **one
lever: push the loop into C, not thread-vs-process**, plus the nuance **"C library" ≠ "GIL released"** (numpy releases → parallel; json/orjson/
pydantic hold → fast single-thread). Same confirmed pattern as v10/v11 — plausible premise capturing a real effect, needs the dominant mechanism
named and the failure re-ranked; integrates instantly. **New signal: he reasons about applied concurrency/async at a strong-practitioner level**
(arena asyncio + distributed-systems retries/idempotency) and naturally reaches for the right robustness primitives (semaphore-bounded fan-out,
idempotent retry, partial-harvest) once the mechanism is named. Minor knowledge gap closed: thought `json` was pure-Python (it's C-accelerated) —
but with correct meta-instinct ("never cared, it's never my bottleneck"). Clean track-economy: finalized at the natural stop.).
Prior: v11 (2026-06-15 — reading #5: LLM inference serving (continuous batching + prefill/decode).
The **scheduling** companion to v10's **memory** session — he again drove the entire Q&A from his own vLLM
ops priors, in his signature sharp-hypothesis mode, and twice **corrected his own wording** mid-stream
(precision-on-mechanics maturing). Same confirmed pattern: a plausible premise capturing a real effect but
needing a re-frame — "decode is bandwidth-bound → use more bandwidth" flipped to *tokens-per-byte, bandwidth
already saturated*; "PagedAttention oversubscribes VRAM" corrected to *ends over-reservation, no overcommit*.
The headline he reached himself, unprompted: **disaggregation vs Sarathi is a TRADE-OFF (utilization vs
goodput), not a strict improvement** — he saw colocation's higher HW utilization and only needed the hidden
premise named (efficiency ≠ keeping units busy; the objective is goodput-under-SLO). Confirms: LLM-serving
internals are now a genuine strength on *both* axes (memory + scheduling); he reasons fluently about
roofline/arithmetic-intensity, PCIe-vs-HBM bandwidth, and statistical-multiplexing/thrashing analogies.
Continue teaching by letting him state the hypothesis then re-ranking against the dominant mechanism.).
Prior: v10 (2026-06-14 — M01 Ch2 §3 out of memory → **Ch2 COMPLETE**. Body untouched in session;
he drove the *entire* Q&A into **LLM-serving memory** from his own ops experience (vLLM, llama.cpp).
**New signal: hands-on LLM inference-serving/deployment experience** (vLLM `gpu_memory_utilization` tuning,
llama.cpp `-ngl` offloading) — a practitioner strength on the *serving/optimization* side, beyond the
integration side already logged. His hypotheses followed a now-consistent pattern: plausible, capturing a
real *secondary* effect, but **mis-ranking it against the dominant cause** (external- vs internal-fragmentation;
paging-cost vs derating-margin) — both corrected cleanly. The semiconductor **derating** framing landed hard;
hardware/bandwidth reasoning (PCIe, RAM-vs-VRAM bandwidth) is fluent. He probes for the *mechanism behind a
rule-of-thumb* ("just experience" → "but why"). The session's payoff was a unifying systems principle he can
now reuse — *don't move/duplicate/over-reserve the big thing.*).
Prior: v9 (2026-06-13 — M01 Ch2 §2 garbage collection. Body at/above level; session was his
signature pressure-test mode aimed at the GC, anchored to concrete code + a real fab production leak.
Surfaced a strong new orthogonality model — resource-lifetime ⊥ object-lifetime, "closing ≠ freeing" —
and a war story (image-processing leak fixed with per-loop gc.collect()) that he used to probe for a
better fix; landed "gc.collect() proves the leak is cyclic" + process-isolation as the robust pattern.
Brings real production memory-debugging experience.).
Prior: v8 (2026-06-12 — reading #4: dataclasses + typing.Protocol, the pair queued same-day
from M01 Ch2 §1. Pure mechanics pressure-test in his signature mode; closed the flagged gap. Landed
the orthogonality model frozen=semantics vs slots=storage, and Protocol=static-contract vs
Pydantic=runtime-validator. Two of his hypotheses were half-wrong and got corrected cleanly.).
Prior: v7 (2026-06-12) — M01 Ch2 §1 memory session that turned into a software-DESIGN session:
he drove it into pipeline state-management and proposed two class-based designs; strong instincts,
real decomposition gaps surfaced. Caught a genuine bug in my small-int-cache example. Flagged
`dataclass` as unfamiliar → reading queued (now done in v8).
v6 (2026-06-11) reading #3: git-archaeology + software-design; he reframed git
delegation into a sharp agent-trust principle, and made a well-calibrated skim-not-study call.
v5 (2026-06-10) M04 Ch1 §1 session (code-reading mostly owned; git confirmed as gap); v4 (2026-06-10) reading session;
v3 (2026-06-09) added reading-track progress; v2 (2026-06-08) corrected after learner feedback;
initial calibration from self-description + code survey of
`/home/zhangzhou/Desktop/Projects/aquarium-main` and
`/home/zhangzhou/Desktop/Projects/arena-concept-experiment`).
