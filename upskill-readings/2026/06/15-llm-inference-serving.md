# Daily Reading — 2026-06-15  🔵 in progress

**Today's two readings (the *other half* of yesterday's course session):**
1. **Continuous batching** — *iteration-level scheduling*: why a naïve batch wastes most of your GPU, and how injecting new requests per-forward-pass buys 8–24× throughput. The **scheduling** layer.
2. **Prefill vs decode** — the two phases have *opposite* bottlenecks (compute-bound vs memory-bound). How modern servers stop them from sabotaging each other: **chunked prefill** (Sarathi-Serve) and **disaggregation** (DistServe). The **frontier** layer.

> **Why these, and why now.** Yesterday (M01 Ch2 §3, *out of memory*) you drove the entire session into LLM-serving **memory** from your own vLLM/llama.cpp ops experience — KV-cache budgeting, `gpu_memory_utilization` as the pool ceiling, PagedAttention killing internal fragmentation. That's the **memory** axis of "why does my LLM server behave the way it does." It is exactly *half* the picture. The other half is **scheduling**: given a fixed pool of KV-cache blocks, *which requests run in this forward pass, and how do you keep the GPU busy?* That's continuous batching. And once you're scheduling, you hit the deeper structural fact your memory work set up: **prefill and decode are different machines** — one saturates compute, one starves on memory bandwidth (your "load 1MB > compute on it" point from Ch1 §3 and yesterday's §7). Today closes the loop: memory (yesterday) + scheduling (today) = the complete mental model of an LLM serving engine. This is also directly **Arena-relevant** — throughput/latency under load is your production reality.

> **Diversification note.** On 06-12 I promised to swing back to the **AI thread** — this is it (after 3 CS/SWE days). I deliberately kept it adjacent to yesterday's course work to *consolidate while the session is one day old* (same rationale as the dataclass/Protocol pairing). It is **additive, not repetitive**: yesterday was where the bytes *live*; today is *which work runs when*. Next reading day I'll rotate further out — likely M12 Ch2 video (DiT/Sora) or something current in the model landscape. Say the word if you'd rather pivot today.

---

## 1. Continuous batching — stop letting the slowest request idle your GPU

🔗 **Primary (the canonical article, your level):** [How continuous batching enables 23x throughput in LLM inference while reducing p50 latency — Anyscale](https://www.anyscale.com/blog/continuous-batching-llm-inference)
🔗 **Deeper companion (mechanism + diagrams):** [LLM Inference: Continuous Batching and PagedAttention — insujang](https://insujang.github.io/2024-01-07/llm-inference-continuous-batching-and-pagedattention/)
🔗 **Tie-back to yesterday (the memory half):** [vLLM: Easy, Fast, and Cheap LLM Serving with PagedAttention — vLLM blog](https://vllm.ai/blog/2023-06-20-vllm)

**The one idea.** A naïve server batches at the **request** level: it gathers N prompts, runs them together until *all N* finish, then takes the next batch. But LLM outputs have wildly different lengths — one request emits 12 tokens, another emits 800. The whole batch is held hostage by the longest generation, and every sequence that finished early leaves its GPU slot **idle** for the rest of the batch. Continuous batching schedules at the **iteration** level instead: after *every* forward pass, finished sequences are evicted and waiting requests are spliced into their freed slots. The batch is never "full of corpses." That's the entire trick — and it's worth up to **23×**.

<!-- DIAGRAM:START -->
![Diagram 1](diagrams/15-llm-inference-serving-1.svg)

<details>
<summary>Diagram source (Mermaid)</summary>

```mermaid
flowchart TB
    subgraph Static["Static / request-level batching"]
        direction TB
        S1["iter→  S1: ████████ (done@2, then IDLE......)"]
        S2["iter→  S2: ██ (done@1, then IDLE.........)"]
        S3["iter→  S3: ████████████████ (longest — everyone waits)"]
        S4["iter→  S4: ████████ (done@2, then IDLE......)"]
        Snote["GPU underutilized until the LAST sequence finishes.<br/>Variable output lengths → most slots idle most of the time."]
    end
    subgraph Cont["Continuous / iteration-level batching"]
        direction TB
        C1["iter→  S1: ████ │ NEW S5 splices in ████████"]
        C2["iter→  S2: ██ │ NEW S6 ███ │ NEW S8 ████"]
        C3["iter→  S3: ████████████████ (still long, but...)"]
        C4["iter→  S4: ████ │ NEW S7 ████████"]
        Cnote["A freed slot is refilled NEXT iteration.<br/>GPU stays saturated → 8–24× throughput."]
    end
    Static --> Cont
```

</details>
<!-- DIAGRAM:END -->

**Why this works — and it's *your* insight from yesterday.** Continuous batching only pays off because **decode is memory-bandwidth-bound, not compute-bound** (your Ch1 §3 + §3-yesterday point: "it takes longer to load 1MB to the compute cores than to compute on it"). Generating one token for one sequence barely touches the GPU's FLOPs — it's dominated by *streaming the weights and KV-cache through memory*. So adding more sequences to the batch is nearly **free on the compute axis**: you reuse the same weight-load across more sequences, amortizing the bandwidth cost. Batching is the lever that turns a memory-bound workload back toward compute-bound (higher arithmetic intensity — the roofline framing). This is why the headline result is *throughput*, and why the ceiling on batch size is **KV-cache memory**, not FLOPs — which is precisely the budget you spent yesterday learning to size.

**The two halves snap together.** This is the payoff for keeping yesterday and today adjacent:
- **PagedAttention (yesterday)** decides *how many* sequences can fit — it kills the internal fragmentation from `max_seq_len` over-reservation, so the KV pool holds far more concurrent sequences.
- **Continuous batching (today)** decides *which* of those sequences run each iteration, keeping the pool's slots full.
- Together: PagedAttention raises the batch-size ceiling, continuous batching keeps you pinned against it. **vLLM's 23× is both mechanisms multiplying** — neither alone gets there. (The 06-12-style keeper: *memory layout and scheduling are orthogonal axes of the same win.*)

**The numbers worth holding** (Anyscale's production benchmark, vs naïve HF Transformers):
| System | Throughput vs HF | What it adds |
|---|---|---|
| HF Transformers (static) | 1× | request-level batching |
| FasterTransformer (optimized static) | ~4× | better kernels, still static |
| HF TGI / Ray (continuous batching) | ~8× | iteration-level scheduling |
| **vLLM (continuous batching + PagedAttention)** | **~23×** | scheduling **+** paged KV memory |

The other reported edge: continuous batching **also lowers median latency** at the same time — counterintuitive, because usually throughput and latency trade off. It works here because a new request doesn't wait for the current batch to drain; it enters at the next iteration. (Hold that thought — reading 2 shows where this *does* still bite latency.)

**Questions to pressure-test while you read (your style):**
- Continuous batching evicts finished sequences each iteration. When a *new* request joins, it must first run its **prefill** (process the whole prompt) before it can decode. What does injecting a fat prefill into a batch of decodes do to the *latency of the sequences already decoding*? (This is the exact seam reading 2 attacks — predict the failure before you read it.)
- The batch-size ceiling is KV-cache memory. Tie it to yesterday's `gpu_memory_utilization`: if you raise that knob, you get a bigger KV pool → bigger max batch → more throughput. What's the cost you accept, and what crashes if your peak estimate was wrong? (You answered this yesterday — confirm it transfers.)
- Throughput went up 23× but **per-token latency for a single lonely request** barely changes (or worsens slightly). Why is continuous batching a *throughput* optimization, not a *single-request-latency* one — and why does that distinction decide whether it helps your Arena workload?

---

## 2. Prefill vs decode — two phases, opposite bottlenecks, one GPU

🔗 **Frontier — disaggregation:** [DistServe: Disaggregating Prefill and Decoding for Goodput-optimized LLM Serving (arXiv 2401.09670)](https://arxiv.org/abs/2401.09670)
🔗 **Frontier — the other answer, chunked prefill:** [Taming Throughput-Latency Tradeoff with Sarathi-Serve (arXiv 2403.02310)](https://arxiv.org/abs/2403.02310)
🔗 **Origin of chunked prefill:** [SARATHI: Piggybacking Decodes with Chunked Prefills (arXiv 2308.16369)](https://arxiv.org/abs/2308.16369)

**The one idea.** An LLM request has two phases that are *physically different workloads*:
- **Prefill** — process the entire prompt in **one** parallel forward pass. Hundreds/thousands of tokens at once → high arithmetic intensity → **compute-bound**. Sets your **TTFT** (time to first token).
- **Decode** — generate output tokens **one at a time**, each pass reading all the weights + the growing KV-cache to emit a single token → **memory-bandwidth-bound**. Sets your **TPOT/TBT** (time per output token).

Same GPU, opposite bottlenecks. When you naïvely mix them in one continuous batch (reading 1), a long prefill **monopolizes the compute** for an iteration and *stalls* every decode sharing that batch — users mid-stream see their token stream hitch. This is the **prefill–decode interference** that reading 1's question pointed at. Two SLOs that pull against each other:

<!-- DIAGRAM:START -->
![Diagram 2](diagrams/15-llm-inference-serving-2.svg)

<details>
<summary>Diagram source (Mermaid)</summary>

```mermaid
flowchart TB
    Req["Request"] --> PF["PREFILL<br/>whole prompt, 1 parallel pass<br/>COMPUTE-bound · sets TTFT"]
    PF --> DEC["DECODE<br/>1 token / pass, KV-cache grows<br/>MEMORY-BW-bound · sets TPOT"]

    DEC --> Problem{"Mix prefill + decode<br/>in ONE batch?"}
    Problem -- "naïve" --> Stall["A fat prefill HOGS compute that iter<br/>→ ongoing decodes STALL (TPOT spikes)<br/>= prefill–decode interference"]

    Stall --> Fix1["CHUNKED PREFILL (Sarathi-Serve)<br/>split prefill into 256/512-tok chunks,<br/>piggyback on decode's spare compute<br/>→ stall-free, ONE GPU pool"]
    Stall --> Fix2["DISAGGREGATION (DistServe)<br/>prefill GPUs ⟂ decode GPUs,<br/>stream KV across → zero interference<br/>→ tune each phase independently"]
```

</details>
<!-- DIAGRAM:END -->

**Goodput, not throughput — the metric shift that matters.** DistServe's framing: raw throughput (tokens/sec) is a vanity number if half those tokens arrived too late to honor their SLO. **Goodput** = requests/sec *that meet both TTFT and TPOT targets*. A server can have great throughput and terrible goodput (it's fast on average but stalls violate latency for a third of users — your tail-latency problem). This is the right lens for Arena: a user staring at a turn cares about *their* TTFT and smooth streaming, not your aggregate tokens/sec.

**Two answers, and the trade-off between them** (this is the keeper):
- **Chunked prefill (Sarathi-Serve)** — *don't separate the phases, tame them.* Split a long prefill into fixed chunks (256/512 tokens) and **piggyback** each chunk onto a batch of decodes, using the *spare compute the memory-bound decodes leave on the table* ("arithmetic intensity slack"). Decodes never stall because each iteration's compute is capped. **One GPU pool, stall-free.** Gains: up to 2.6× (Mistral-7B, 1×A100) / 6.9× (Falcon-180B, 8×A100) within SLO. This is now a **standard vLLM scheduler option** — directly tunable in your stack.
- **Disaggregation (DistServe)** — *separate the phases onto different GPUs.* Prefill runs on one GPU group, decode on another; the KV-cache is streamed across the interconnect at handoff. Each group gets its **own parallelism, batch policy, and even hardware**, tuned for its bottleneck — zero interference *by construction* (the same "design the problem out of existence" instinct as `frozen` from 06-12, applied to hardware). Gains: **7.4× more requests / 12.6× tighter SLO**. Cost: complexity, KV transfer bandwidth, and you need enough GPUs to dedicate. It shines at scale; chunked prefill shines on a single node.

**Connect it to *you*.** You run vLLM. Both of these are levers you can actually pull: chunked prefill is a scheduler flag; disaggregation is an architecture choice (vLLM, SGLang, TensorRT-LLM all now support a P/D-disaggregated mode). The decision rule that falls out: **single-node / cost-bound → chunked prefill; multi-node / SLO-bound at scale → disaggregation.** And the *why* is the same physics you already own — prefill is compute-bound, decode is memory-bound, so the question is always "am I packing the spare capacity of one onto the other, or am I giving each its own box?"

**Questions to pressure-test while you read:**
- Disaggregation has to **physically copy the KV-cache** from the prefill GPU to the decode GPU. Using yesterday's KV-cache sizing (per-token bytes × layers × 2 for K and V): for a 4k-token prompt, roughly how much data crosses the interconnect, and why does DistServe say it places the two phases "according to bandwidth"? When does the transfer cost eat the disaggregation win? (Echoes your llama.cpp `-ngl` analysis — *who pays the PCIe/NVLink toll, and is the thing crossing it small or huge?*)
- Chunked prefill caps per-iteration compute to protect TPOT — but chunking a prefill into N pieces means re-reading the model weights N times for that prompt. What does that cost on the *memory-bandwidth* axis, and why is it still a net win? (Hint: whose spare capacity is it spending?)
- "Goodput under SLO" vs "throughput." Sketch a workload where system A has 2× the throughput of system B but **lower goodput**. Which one would you ship for Arena, and what does that tell you about the metric your dashboards should actually track?

---

## What to take away (read first on review)

- **An LLM serving engine has two orthogonal axes: memory (where the KV-cache lives) and scheduling (which work runs each iteration).** Yesterday was the first; today is the second. vLLM's 23× is *both multiplying*.
- **Continuous batching = iteration-level scheduling.** Refill freed slots every forward pass; never let the slowest sequence idle the GPU. It's a *throughput* win, enabled by decode being memory-bound (batching is near-free on compute).
- **Prefill ≠ decode.** Compute-bound (TTFT) vs memory-bound (TPOT). Mixing them naïvely causes **interference** (prefill stalls decodes). Two fixes: **chunked prefill** (tame, one pool — a vLLM flag) and **disaggregation** (separate, scale — an architecture). Single-node→chunk; at-scale-SLO→disaggregate.
- **Goodput > throughput** for user-facing serving. Track requests-meeting-SLO, not raw tokens/sec — your Arena tail-latency lens.

---

## Sources
- [How continuous batching enables 23x throughput in LLM inference while reducing p50 latency — Anyscale](https://www.anyscale.com/blog/continuous-batching-llm-inference)
- [LLM Inference: Continuous Batching and PagedAttention — insujang](https://insujang.github.io/2024-01-07/llm-inference-continuous-batching-and-pagedattention/)
- [vLLM: Easy, Fast, and Cheap LLM Serving with PagedAttention — vLLM blog](https://vllm.ai/blog/2023-06-20-vllm)
- [DistServe: Disaggregating Prefill and Decoding for Goodput-optimized LLM Serving (arXiv 2401.09670)](https://arxiv.org/abs/2401.09670)
- [Taming Throughput-Latency Tradeoff in LLM Inference with Sarathi-Serve (arXiv 2403.02310)](https://arxiv.org/abs/2403.02310)
- [SARATHI: Efficient LLM Inference by Piggybacking Decodes with Chunked Prefills (arXiv 2308.16369)](https://arxiv.org/abs/2308.16369)

*Drafted 2026-06-15. Pairs with the course track's M01 Ch2 §3 (out of memory, 2026-06-14): that session was the **memory** axis of LLM serving; this reading is the **scheduling** axis. Finalize after our Q&A.*
