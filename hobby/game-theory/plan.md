# Hobby Plan — Game Theory & Strategic Interaction

> **Status: v1 plan ready, no sections written yet.** Yours to steer — edit freely or redirect in chat at
> any module boundary (same as the other plans).
>
> Author of plan: Claude. Created: 2026-06-16 (spun off from the Economy & Finance §1 Q&A, where you reached
> for the multi-agent-RL / GAN analogy for economic equilibria and asked for "game theory + related math").

The study of **decision-making when your payoff depends on what other optimizing agents do.** Single-agent
optimization (what most of physics and supervised ML is) descends a *fixed, exogenous* surface. Game theory
is what happens when the surface is **endogenous and coupled** — every agent reshapes everyone else's
landscape — so the solution concept stops being a *minimum* and becomes a **fixed point / equilibrium.**

## Why this is its own subject (and why it's worth your time twice over)

You raised it inside the economics track, but game theory **double-serves two of your tracks**, which is why
it gets its own plan rather than a couple of econ sections:

- **It deepens the economics hobby** — oligopoly, auctions, public goods, insurance/lemons, the
  principal–agent problem, bargaining. The strategic half of microeconomics *is* game theory.
- **It directly feeds your AI career** — and this is the part that would be wasted if it were buried in econ.
  You already connected economic equilibria to **multi-agent RL** and **GANs** (a GAN is a two-player
  zero-sum game; its training is *learning in games*). The same machinery underlies **mechanism design**
  (ad/spectrum auctions, matching markets), **adversarial robustness**, **RLHF-as-a-game**, **LLM-agent
  negotiation/markets**, and **Shapley values** (the cooperative-game object behind SHAP feature attribution).

> **Want this promoted to the main career track instead?** It's pitched here as a hobby, but it's rigorous
> and demonstrably career-relevant. Say the word and I'll re-home it under `courses/` with exercises and a
> heavier proof/derivation load. Default for now: hobby, concept-first, math woven in at your level.

## How this plan is pitched (for *you*)

- **Foundational and dependency-ordered** (form → equilibrium → dynamics → information → design), like the
  econ and main tracks. Each module earns the next.
- **Concept-first, math woven in — not dumbed down.** You're a physicist; you have the math maturity, so the
  relevant tools appear inline at full strength rather than in a remedial appendix. The recurring toolkit:
  **fixed-point theorems** (Brouwer/Kakutani — why Nash equilibria *exist*), **convexity & LP/minimax
  duality** (zero-sum games), **probability & Bayesian updating** (games of incomplete information),
  **dynamical systems on the simplex** (evolutionary & learning dynamics — where your GAN-convergence
  question lives), and a little **social-choice/impossibility** (Arrow). Each module names which tool it uses.
- **Physics/ML lens throughout** — equilibrium = fixed point (not optimum); existence = topology;
  minimax = duality; replicator dynamics = a dynamical system; learning-in-games = the convergence/cycling
  behaviour you already know from GANs and multi-agent RL.
- **Real, grounded examples** — with a Singapore/Asia lens where natural (COE *is* an auction; spectrum
  auctions; HDB/school **matching markets** = Gale–Shapley; ERP as mechanism design).
- **Bite-sized.** Each **§ section = 1–2 hours**. A "module" is a themed group of sections.

---

## Modules

### G01 — What a Game Is (normal form & dominance) · `01-foundations/`
*The objects: players, strategies, payoffs — and the first solution concept.*
- §1 — Strategic (normal) form; the prisoner's dilemma; why individually rational ⇒ collectively bad.
- §2 — Dominance & iterated elimination; best response; **pure-strategy Nash equilibrium** as a fixed point
  of the best-response map. *(Lens: equilibrium ≠ optimum — the §11a econ thread, made rigorous.)*

### G02 — Mixed Strategies & Why Equilibria Exist · `02-mixed-and-existence/`
*Randomization, and the theorem that makes the whole field well-posed.*
- §1 — Mixed strategies & expected payoff; matching pennies / rock–paper–scissors (no pure equilibrium).
- §2 — **Nash's existence theorem** via **Brouwer/Kakutani fixed points** *(your topology will make this
  feel inevitable rather than magical)*.
- §3 — Zero-sum games, the **minimax theorem** (von Neumann), and the **LP-duality** equivalence.

### G03 — Sequential Games (extensive form) · `03-dynamic-games/`
*Order, information, and credible commitment.*
- §1 — Game trees, information sets, backward induction.
- §2 — **Subgame-perfect equilibrium**; credible vs empty threats; commitment as strategic advantage
  (why burning a bridge can help you). Bargaining (Rubinstein) & the centipede game.

### G04 — Repeated Games & the Emergence of Cooperation · `04-repeated-games/`
*How self-interested agents cooperate without being told to.*
- §1 — Finitely vs infinitely repeated games; discounting; the **folk theorem**.
- §2 — Tit-for-tat, Axelrod's tournaments, reputation. *(Lens: cooperation as an equilibrium, not altruism.)*

### G05 — Games of Incomplete Information · `05-information/`
*When you don't know the others' payoffs — the bridge to economics.*
- §1 — Bayesian games, types, **Bayes–Nash equilibrium**.
- §2 — **Signalling & screening** (Spence), **adverse selection** (Akerlof's lemons), **moral hazard**, the
  **principal–agent** problem. *(Huge econ payoff: insurance, credit, contracts, executive pay.)*

### G06 — Mechanism Design & Auctions ("reverse game theory") · `06-mechanism-design/`
*Design the rules so that self-interested play yields the outcome you want.*
- §1 — The **revelation principle**, **incentive compatibility**, the **VCG** mechanism.
- §2 — Auction formats (first-/second-price, English, Dutch); **revenue equivalence**; the winner's curse.
  *(SG/AI examples: spectrum & COE auctions, online ad auctions.)*
- §3 — **Matching markets** without money: **Gale–Shapley** stable matching (school choice, HDB, kidney
  exchange, residency match).
- §4 — **Social choice & Arrow's impossibility** (a taste): why "fair aggregation of preferences" is
  formally impossible, and what voting rules trade off.

### G07 — Evolutionary & Learning Dynamics · `07-dynamics/`
*What happens when agents don't compute the equilibrium but grope toward it — your GAN thread, properly.*
- §1 — **Evolutionarily stable strategies** & **replicator dynamics** (a dynamical system on the simplex);
  hawk–dove, the evolution of cooperation.
- §2 — **Learning in games**: fictitious play, **no-regret / multiplicative weights**, and when play
  **converges vs cycles** — the direct formal account of GAN / multi-agent-RL (non-)convergence.

### G08 — Cooperative Game Theory (coalitions) · `08-cooperative/`
*Value creation and fair division when binding agreements are possible.*
- §1 — Characteristic-function games, the **core**, the **Shapley value** (axioms + formula).
- §2 — Applications: cost/surplus allocation, and **SHAP** — the Shapley value as ML feature attribution
  *(direct career tie-in)*.

### G09 — Synthesis: Strategy in Economics, AI & the Wild · `09-applications/`
*Pulling the threads together across your tracks.*
- §1 — **Economics:** oligopoly (Cournot / Bertrand / Stackelberg), tragedy of the commons, public goods —
  closing the loop with E01 §4 and the externalities thread.
- §2 — **AI/ML:** GANs as zero-sum games, multi-agent RL & self-play (AlphaZero), adversarial robustness,
  RLHF-as-a-game, mechanism design for LLM-agent markets/negotiation.
- §3 — **Strategic reasoning as a habit:** Schelling points, commitment, signalling, and the limits of
  game-theoretic rationality (behavioural game theory; people don't backward-induct).

---

## Track → module (where each of your two interests is served)

| Your interest | Primary modules |
|---|---|
| Strategic **economics** (oligopoly, auctions, contracts, insurance) | G01, **G05**, **G06**, G09 §1 |
| **AI/ML** (GANs, multi-agent RL, mechanism design, SHAP) | G02 §3, **G07**, **G08**, **G09 §2** |
| The **math** itself (fixed points, duality, dynamics, social choice) | **G02**, G06 §4, **G07** |
| Everyday **strategic reasoning** | G03, G04, G09 §3 |

## Suggested sequence

Default is **linear** (G01 → G09) — built in dependency order. But if the **AI** angle is what's pulling you,
a fast path is **G01 → G02 → G07 → G08 → G09 §2** (form → equilibrium/existence → learning dynamics →
Shapley → AI synthesis), deferring the econ-heavy information/mechanism modules. Tell me your priority and
I'll re-sequence.

---

## Progress tracker

**Legend:** ⬜ not started · 🔵 in progress · ✅ finalized · ⏭️ skipped (you already know it)

| Module | Section | Status | File | Notes |
|---|---|---|---|---|
| G01 Foundations | §1 Normal form & the prisoner's dilemma | ⬜ | | |
| G01 | §2 Dominance, best response & pure Nash | ⬜ | | |
| G02 Mixed & existence | §1 Mixed strategies | ⬜ | | |
| G02 | §2 Nash existence (fixed-point theorems) | ⬜ | | |
| G02 | §3 Zero-sum, minimax & LP duality | ⬜ | | |
| G03 Dynamic games | §1 Game trees & backward induction | ⬜ | | |
| G03 | §2 Subgame perfection, commitment, bargaining | ⬜ | | |
| G04 Repeated games | §1 Repetition, discounting & the folk theorem | ⬜ | | |
| G04 | §2 Tit-for-tat, reputation, cooperation | ⬜ | | |
| G05 Information | §1 Bayesian games & Bayes–Nash | ⬜ | | |
| G05 | §2 Signalling, lemons, moral hazard, principal–agent | ⬜ | | |
| G06 Mechanism design | §1 Revelation principle, IC, VCG | ⬜ | | |
| G06 | §2 Auctions & revenue equivalence | ⬜ | | |
| G06 | §3 Matching markets (Gale–Shapley) | ⬜ | | |
| G06 | §4 Social choice & Arrow's impossibility | ⬜ | | |
| G07 Dynamics | §1 ESS & replicator dynamics | ⬜ | | |
| G07 | §2 Learning in games; convergence vs cycling (GANs/MARL) | ⬜ | | |
| G08 Cooperative | §1 The core & the Shapley value | ⬜ | | |
| G08 | §2 Applications + SHAP | ⬜ | | |
| G09 Synthesis | §1 Economics: oligopoly & commons | ⬜ | | |
| G09 | §2 AI/ML: GANs, MARL, mechanism design | ⬜ | | |
| G09 | §3 Strategic reasoning & its limits | ⬜ | | |
