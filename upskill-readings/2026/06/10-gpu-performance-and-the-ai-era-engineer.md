# Daily Reading — 2026-06-10  🔵 draft (not yet finalized)

**Today's two readings (diversified):**
1. **AI / systems — from first principles** — *Making Deep Learning Go Brrrr From First Principles* (Horace He) *(directly extends yesterday's M01 Ch1 §3 GPU work, and is the conceptual bridge into M01 Ch2 — Memory)*
2. **Software engineering / career** — *The Next Two Years of Software Engineering* (Addy Osmani, Jan 2026) *(keeps you current; speaks straight to your "full-stack dev **and architect**" goal and your vibe-coding reality)*

> Why these: in §3 you pushed the whole session into **GPU memory hierarchy, latency-hiding, FlashAttention, and why LLM inference is memory-bound**. Reading #1 is the canonical first-principles framework that *names* what you were circling — every kernel is **compute-bound, memory-bandwidth-bound, or overhead-bound** — and gives you the back-of-envelope test to tell which. It's the perfect on-ramp to M01 Ch2 (Memory) and to M12. Reading #2 deliberately switches scope: it's the clearest recent map of how the *engineer's role* shifts as agents do more of the typing — i.e. the job you're actually skilling up for.

> **Note (draft):** the two **"What we worked out"** sections that will sit at the bottom get written when you say *finalize* — they're the durable takeaways from our Q&A. For now, read top-down.

---

## 1. Making Deep Learning Go Brrrr From First Principles (Horace He, 2022)

🔗 https://horace.io/brrr_intro.html

**Why it's worth your time even though it's from 2022.** It's the standard reference in ML-systems for *reasoning* about performance instead of cargo-culting tricks. The framework predates and explains the tools you now use by default — `torch.compile`, Triton, XLA. It's short, first-principles, and exactly your style (you re-derive, you don't memorize).

**The one idea.** Any deep-learning workload spends its time in exactly one of **three regimes**, and the optimization that helps depends *entirely* on which one you're in:

- **Compute-bound** — time goes to actual FLOPs. The good place: you're using the expensive silicon. More FLOPs/s (better GPU, lower precision) is the only lever.
- **Memory-bandwidth-bound** — time goes to *moving tensors* between global memory (HBM) and the compute units, not computing on them. Adding FLOPs does nothing; you must move **fewer bytes**. ← *this is the LLM-inference-decode regime you reconstructed in §3.*
- **Overhead-bound** — time goes to *everything else*: Python, the framework, kernel-launch costs. Dominates with **tiny tensors / eager mode**.

**The diagnostic (the back-of-envelope you wanted in §3).** Compare your op's **arithmetic intensity** (FLOPs done per byte moved) against the hardware's ratio of `peak FLOPs ÷ memory bandwidth`. He uses an A100: **~19.5 TFLOP/s** of compute vs **~1.5 TB/s** of bandwidth. If your op does few FLOPs per byte (elementwise ops, activations, the decode step reading weights + KV cache), you're **memory-bound** — the compute units sit idle waiting for data.

```mermaid
flowchart TD
    A["A kernel is too slow.<br/>Which regime?"] --> B{"Achieved FLOPs<br/>near peak (~80%)?"}
    B -- "Yes" --> C["COMPUTE-BOUND<br/>→ lower precision, better GPU,<br/>more FLOPs/s. You're winning."]
    B -- "No" --> D{"Tensors tiny /<br/>eager mode /<br/>many small kernels?"}
    D -- "Yes" --> E["OVERHEAD-BOUND<br/>→ batch, compile (torch.compile),<br/>CUDA graphs, fuse launches"]
    D -- "No" --> F["MEMORY-BANDWIDTH-BOUND<br/>→ move fewer bytes:<br/>OPERATOR FUSION, keep data<br/>on-chip, fewer round-trips"]
    F -.->|"the FlashAttention move"| G["tile + fuse so attention<br/>never materializes the<br/>N×N matrix in HBM"]
```

**The single most impactful technique: operator fusion.** `x.cos().cos()` naively is *read x → write tmp → read tmp → write out* = 4 memory trips. Fused into one kernel it's *read x → write out* = 2 trips → ~2× faster, **for free**, with zero change in FLOPs. Key consequence that surprises people: a fused `x.cos().cos()` costs almost the same as a single `x.cos()` — so for memory-bound chains, *which* cheap elementwise op you pick barely matters; **how many memory round-trips you make is everything.**

**The overhead point that should stick.** GPUs are so much faster than the CPU driving them that "in the time Python performs a *single* FLOP, an A100 could have done ~9.75 million." The only reason eager-mode PyTorch isn't crippled: execution is **asynchronous** — Python races ahead queuing kernels while the GPU chews through earlier ones, *hiding* the overhead — but only while kernels stay big enough to hide behind. Tiny kernels expose it.

**Connect it to your §3 + the next course chapter.**
- This *is* the formal version of "GPU inference is memory-bound" you arrived at. **Decode** = read all the weights + KV cache to produce one token → tiny arithmetic intensity → bandwidth-bound. That's why batching and KV-cache tricks (not faster math) speed up serving.
- **FlashAttention** is literally "memory-bound regime + operator fusion" applied to attention: tile the computation so the N×N attention matrix is *never written to HBM* — it lives in on-chip SRAM. The §3 callback you made (Shared Memory as a software-managed scratchpad) is exactly the mechanism. Paper: [FlashAttention — Dao et al., 2022](https://arxiv.org/abs/2205.14135).
- **Bridge to M01 Ch2 (Memory):** "moving bytes is the bottleneck, not computing on them" is the *same* lesson the CPU cache hierarchy teaches (cache locality, why a cache miss costs ~100× an L1 hit). GPU HBM↔SRAM is the same story one level up. Hold this thought going into Ch2.

**Questions to pressure-test while you read (your usual style):**
- For your arena's LLM serving: is the latency you feel **memory-bound decode** (per-token weight + KV reads) or **overhead-bound** (lots of small calls, framework/Python glue)? The fixes are completely different.
- Operator fusion needs the ops *adjacent and on-device*. Where in a Python pipeline does a `.cpu()` / `.numpy()` / logging call silently break a fusable chain and force a round-trip?
- The A100 ratio is ~13 FLOPs/byte (19.5T ÷ 1.5T). Newer chips push FLOPs up faster than bandwidth. Does that make memory-boundedness **better or worse** over time — and what does that imply for where the industry spends effort (quantization, KV-cache compression, batching)?

---

## 2. The Next Two Years of Software Engineering (Addy Osmani, Jan 5 2026)

🔗 https://addyosmani.com/blog/next-two-years/

**What it covers.** A calm, scenario-based read (not hype) on how the engineer's job changes as coding agents move from autocomplete → autonomous task execution. Osmani frames **five open questions** as "lenses for preparation," giving an optimistic and a pessimistic branch for each rather than firm predictions. This is the macro context for *why* your upskilling plan is shaped the way it is.

- **Junior hiring** — pressure on pure entry-level "typing" work; the bar rises to "immediately useful" (AI-fluent + domain knowledge + communication).
- **Skills & understanding** — the real risk is **atrophy**: leaning on AI so hard you can't judge its output. The counter: humans own the hard 20% — architecture, edge cases, design. His line worth keeping: *"the best engineers won't be the fastest coders, but those who know when to distrust AI."*
- **Developer role** — shift from *author* to **"composer"**: orchestrating agents/services, owning the architecture and the verification, not the keystrokes.
- **Specialist vs generalist** — **T-shaped** wins: one deep area + broad adaptability. Narrow-only niches are the most automatable.
- **Education** — credentials matter less than demonstrated, end-to-end ability (portfolios, real systems).

**Connect it to *you* specifically — this article is almost a mirror of your plan.**
- Your stated method — *"I'll keep vibe coding; what I need is to **read and judge** code with AI help"* — is exactly the "knows when to distrust AI" skill Osmani says becomes the differentiator. Your whole course track (fundamentals → reading code → testing → types → architecture) is the **anti-atrophy** curriculum.
- "Author → composer" *is* the **architect** goal in your profile. The high-leverage move isn't typing faster; it's owning system design + verification — which is why M07 (Architecture) and M06 (Testing) carry so much weight in your plan.
- "T-shaped" reframes your interleaved sequence: your **deep spike** is forming (AI/LLM + the GPU-systems intuition you keep showing); the breadth (CS fundamentals, networking, DB, cloud, security, frontend) is the horizontal bar this plan is deliberately building.

**Questions to pressure-test while you read:**
- Osmani's biggest risk is *skill atrophy from over-trusting AI*. Concretely: where in your current workflow do you **ship AI output you can't fully verify** — and which course module is the direct antidote to that specific blind spot?
- "Composer / orchestrator" sounds like the agent pipelines you already build. Is the future-engineer skill therefore *less* novel for you than for most — i.e. is **agent orchestration** quietly one of your spikes already, per yesterday's "applied context engineering" signal?
- If junior "implementation" work compresses, what's the **fastest-depreciating** skill in your stack, and the **slowest** — and is your study time allocated accordingly?

---

## Sources
- [Making Deep Learning Go Brrrr From First Principles — Horace He (2022)](https://horace.io/brrr_intro.html)
- [FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness — Dao et al. (2022)](https://arxiv.org/abs/2205.14135)
- [The Next Two Years of Software Engineering — Addy Osmani (Jan 2026)](https://addyosmani.com/blog/next-two-years/)

*Study, then Q&A with me. Say "finalize" when done and I'll rewrite this to match how you actually think about it + update your learner profile.*
