# M12 · Ch2 · §1 — Diffusion & Image Generation: The Other Generative Paradigm

> **Module:** The Model Landscape
> **Chapter:** Beyond text (image/diffusion, audio, video, TTS, multimodal)
> **Section:** How image (and, by extension, video) generation actually works — the diffusion paradigm,
> from the thermodynamic intuition through the score/SDE view to latent diffusion, guidance, and the
> DiT/flow-matching frontier.
> **Status:** ✅ finalized 2026-06-10. You'd already read the DDPM paper and built a strong
> physics-grounded mental model (signal/noise, SNR, the model as a noise filter). The session was a
> high-level Q&A that *confirmed* the parts you had right (SNR as the native axis; non-sequential
> training; coarse→fine) and corrected two mechanisms (sampling is **not** resonance/amplification →
> it's **annealed Langevin descent on a learned energy landscape**; multi-step is **not** noise adding
> detail → it's **integrating a curved trajectory**). Your editing analysis independently re-derived
> production techniques. All captured in §13.

**Estimated study time:** 3 hours (paper-grounded; budget extra if you follow the citations).
**Prerequisites:** none new — your LLM/transformer knowledge transfers more than you'd expect (the modern
backbone is a transformer). Your physics is the *real* prerequisite, and you already have it.

---

## Why this section exists (for *you*)

Your two decks make it clear: on the autoregressive-LLM axis you're at frontier level — attention math,
the linear-attention↔RNN↔Titans lineage, MoE/MLA/FP8, the R1 data critique. So we skip all of that.

But you flagged the real gap honestly: **you haven't read the papers on image, video, audio, or TTS.**
This section attacks the biggest and most foundational of those — **diffusion** — because image generation
*is* diffusion, video is diffusion-with-time, and even modern TTS borrows the machinery.

Here's the hook that should make this efficient for you: **diffusion is not an ML trick, it's
physics you already own.** The forward process is literally a diffusion / Ornstein–Uhlenbeck process; the
training target is a **score function** `∇ₓ log p(x)`; sampling is **Langevin dynamics**; the whole thing
has a clean **stochastic-differential-equation** formulation with a deterministic **probability-flow ODE**
twin. Where an ML engineer memorizes the DDPM loss, you can *derive why it has that form* from
non-equilibrium statistical mechanics. We'll lean on that the whole way.

The one conceptual pivot to internalize up front:

> **An LLM generates by autoregression** — one discrete token at a time, left to right, each conditioned
> on the past. **A diffusion model generates by iterative denoising** — it starts from pure Gaussian noise
> and refines the *entire* image in parallel over many steps. Sequential-and-discrete vs
> parallel-and-continuous. Almost everything that's different downstream follows from this.

---

## 1. The two generative paradigms, side by side

<!-- DIAGRAM:START -->
![Diagram 1](diagrams/01-diffusion-and-image-generation-1.svg)

<details>
<summary>Diagram source (Mermaid)</summary>

```mermaid
flowchart LR
    subgraph AR["Autoregressive (LLM, PixelCNN, early DALL·E)"]
        direction LR
        a1["token₁"] --> a2["token₂"] --> a3["token₃"] --> a4["… (sequential)"]
    end
    subgraph DIF["Diffusion (Stable Diffusion, Imagen, Sora)"]
        direction LR
        d0["pure noise<br/>x_T"] --> d1["denoise"] --> d2["denoise"] --> d3["…"] --> d4["clean image<br/>x₀"]
    end
```

</details>
<!-- DIAGRAM:END -->

| | Autoregressive | Diffusion |
|---|---|---|
| Unit | discrete tokens | continuous values (pixels / latents) |
| Order | sequential, causal | whole canvas refined in parallel |
| Steps | `n` = sequence length | `T` = denoising steps (decoupled from output size) |
| Likelihood | exact, tractable | variational bound / score-based |
| Sampling control | temperature / top-p | guidance scale (CFG) |
| Native strength | language, code, anything serializable | images, audio, video, continuous signals |

Note the resurgence caveat: **autoregressive image models are back** (token-based: VQ-GAN + transformer,
and 2024-era models). The paradigms are converging on a shared transformer backbone — but diffusion is
where the field's center of mass for images/video sits, so we start there.

---

## 2. The forward process — destroy structure with noise (your home turf)

Take a real image `x₀`. Define a **Markov chain** that adds a little Gaussian noise at each step `t = 1…T`:

```
q(xₜ | xₜ₋₁) = N(xₜ ; √(1−βₜ)·xₜ₋₁ , βₜ·I)
```

`βₜ` is the **noise schedule** (small → large). After enough steps, `x_T` is indistinguishable from pure
Gaussian noise — all structure destroyed. This is exactly a **variance-preserving diffusion process**;
the `√(1−βₜ)` keeps the variance bounded (a discretized Ornstein–Uhlenbeck process).

The property that makes it tractable (and that you can verify by composing Gaussians): you can jump to
*any* noise level in closed form, no iteration:

```
q(xₜ | x₀) = N(xₜ ; √(ᾱₜ)·x₀ , (1−ᾱₜ)·I)      where  ᾱₜ = Πₛ(1−βₛ)
```

So `xₜ = √(ᾱₜ)·x₀ + √(1−ᾱₜ)·ε`, with `ε ~ N(0, I)`. **This is the single most important equation in the
whole section** — it says any noisy version of an image is just a known blend of the clean image and a
known Gaussian noise sample. Training will exploit exactly this.

<!-- DIAGRAM:START -->
![Diagram 2](diagrams/01-diffusion-and-image-generation-2.svg)

<details>
<summary>Diagram source (Mermaid)</summary>

```mermaid
flowchart LR
    x0["x₀ (clean)"] -->|"+ noise β₁"| x1["x₁"] -->|"β₂"| x2["x₂"] -->|"…"| xT["x_T ≈ N(0,I)<br/>(pure noise)"]
    xT -.->|"learned reverse: this is the hard part"| x0
```

</details>
<!-- DIAGRAM:END -->

The forward process has **no learned parameters** — it's a fixed physics simulation. All the learning is
in reversing it.

---

## 3. The reverse process — and what the network actually predicts

We want `p(xₜ₋₁ | xₜ)`: given a noisier image, produce a slightly cleaner one. For small `βₜ`, this reverse
conditional is also approximately Gaussian (a result from the diffusion literature / Feller) — so a
network only needs to predict its **mean** (the variance is often fixed or a small learned correction).

The clean trick (Ho et al., **DDPM**, 2020): instead of predicting the cleaned image directly,
**predict the noise `ε` that was added.** Because `xₜ = √(ᾱₜ)x₀ + √(1−ᾱₜ)ε`, knowing `ε` is equivalent to
knowing `x₀` — but the noise-prediction target makes the loss beautifully simple:

```
L = E_{x₀, ε, t}  ‖ ε − ε_θ(xₜ, t) ‖²
```

That's it — a plain **MSE between true and predicted noise**. Training:

<!-- DIAGRAM:START -->
![Diagram 3](diagrams/01-diffusion-and-image-generation-3.svg)

<details>
<summary>Diagram source (Mermaid)</summary>

```mermaid
flowchart TD
    A["Sample clean image x₀ from data"] --> B["Sample random t ∈ {1…T} and noise ε~N(0,I)"]
    B --> C["Form xₜ = √(ᾱₜ)x₀ + √(1−ᾱₜ)ε  (closed form, §2)"]
    C --> D["Network ε_θ(xₜ, t) predicts the noise"]
    D --> E["Loss = ‖ε − ε_θ‖²  → backprop"]
    E -.->|"repeat over millions of (image, t)"| A
```

</details>
<!-- DIAGRAM:END -->

The model is trained to be a **denoiser at every noise level simultaneously** (`t` is fed in as a
conditioning input, usually via a sinusoidal/time embedding — yes, the same positional-encoding idea you
know). Sampling then runs the denoiser `T` times from pure noise down to a clean image.

---

## 4. The score view — where your physics pays off

Here's the reframing that, from your background, is probably *more* natural than the noise-prediction
story. Predicting the noise is — up to a known scale factor — equivalent to estimating the **score
function** of the noisy data distribution:

```
score:  s_θ(xₜ, t) ≈ ∇_{xₜ} log p_t(xₜ)        and     ε_θ ≈ −√(1−ᾱₜ) · s_θ
```

The score is the gradient of log-density — it points "toward higher-probability (more image-like)
regions." Once you have it, you can sample by **Langevin dynamics**: repeatedly step along the score and
add a little noise, exactly the overdamped Langevin equation you'd write in stat-mech:

```
x ← x + (η/2)·∇ log p(x) + √η · z ,   z ~ N(0,I)
```

Song & Ermon (**NCSN**, 2019) and Song et al. (**Score-SDE**, 2021) unify everything into a single
continuous picture. The forward noising is a **stochastic differential equation**:

```
forward SDE:   dx = f(x,t) dt + g(t) dw          (drift + Brownian motion)
reverse SDE:   dx = [f − g²·∇log p_t(x)] dt + g(t) dw̄   ← run this backward to generate
```

and — the result you'll appreciate most — there's a **deterministic probability-flow ODE** with the *same
marginals* as the SDE:

```
probability-flow ODE:   dx/dt = f(x,t) − ½ g(t)²·∇log p_t(x)
```

This ODE is why deterministic, few-step samplers exist (you're solving an ODE, so you can use a good
numerical integrator and take big steps). DDPM ≈ a particular SDE discretization; **DDIM** ≈ the ODE.
The "many steps because it's an SDE / few steps because it's an ODE" distinction maps directly onto
stochastic-vs-deterministic integration — a thing you already understand.

### The frame to hold: annealed descent on a learned energy landscape

Since the score is `−∇(energy)`, **sampling is noisy gradient descent down a learned energy surface,
with the noise level acting as temperature, cooled from hot to cold** — i.e. simulated annealing /
annealed Langevin dynamics, which you already own from stat-mech. Start hot → the (smoothed) landscape
`p_t` is flat and every state is reachable; cool slowly → you settle into one of many **basins**
(image modes). *Which* basin you land in is set by the trajectory — and under the deterministic ODE,
entirely by the **initial seed**. This is the rigorous replacement for "pure noise contains all
signals and the filter amplifies a subset": the seed *selects* a basin, but the image content is
**synthesized** by the learned dynamics, not linearly amplified out of frequency components sitting in
the noise. The noise schedule literally *is* the temperature schedule.

Two precise hooks worth carrying:
- **Tweedie's formula:** the optimal one-shot denoiser output is the *posterior mean* `E[x₀ | xₜ]`. At
  high noise that mean is a blurry average over all plausible images (hence "few steps → looks like a
  house but no texture"); as noise drops it collapses to one specific, detailed sample. This is the
  rigorous version of "extract the signal."
- **Coarse→fine = low-freq→high-freq.** Natural images have ~1/f spectra; high-noise steps fix
  low-frequency layout, low-noise steps paint high-frequency detail. The spectral reading of
  "structure first, detail later" is correct.

---

## 5. Sampling — the latency story (the part that bites in production)

Naive DDPM uses `T ≈ 1000` denoising steps → 1000 forward passes per image. That's the diffusion
analogue of the LLM **decode** problem you know: generation is an iterative loop, and each step is a full
network evaluation. The progression of fixes:

- **DDIM (2021)** — use the deterministic ODE; 20–50 steps with little quality loss.
- **DPM-Solver / higher-order ODE solvers (2022)** — exploit the ODE's structure; ~10–20 steps.
- **Distillation → consistency models (Song et al., 2023) / progressive distillation** — train a student
  to jump many steps at once → **1–4 steps**. This is the frontier of "real-time" image/video gen.

### *Why* multiple steps — the correct reason (a Q&A correction worth pinning)

It is **not** that each step re-injects noise to "add new detail." The clean disproof: the deterministic
ODE samplers (DDIM, probability-flow ODE) add **zero** noise after the seed and still produce fully
detailed images. The real reason is **numerical-integration accuracy**: the noise→data trajectory is
**curved** (the score/velocity field is nonlinear in `x` *and* the target landscape sharpens as it
cools), so one big linear step overshoots → blur/artifacts; many small steps track the curve. The
"precision" that forces many steps is **step-size / truncation error**, not floating-point bit-width
(FP16-vs-FP32 is a minor, separate effect).

The proof that *curvature* is the cause: **consistency/distillation models reach 1–4 steps by learning
the curved map directly** — if the bottleneck were noise re-injection or float precision, that couldn't
work. And the stochastic samplers that *do* re-add noise (DDPM/SDE) use it only as **error-correction**
("churn" that scrubs accumulated integration error — Karras et al.'s *EDM* analyzes exactly this); it is
optional and never a detail-source.

> **The mental model to carry:** diffusion trades a *single hard problem* (model `p(x)` directly, as a
> GAN or autoregressive model must) for *many easy problems* (denoise a little, `T` times). The price is
> the iterative sampling loop — and the last five years of diffusion research is largely about **paying
> down that loop** (fewer, bigger steps), exactly as LLM serving is about paying down the decode loop.
> The number of *inference* steps is decoupled from the "1000" training framing — you choose the
> discretization of a continuous trajectory.

---

## 6. Latent diffusion — why Stable Diffusion is affordable

Running diffusion in **pixel space** (512×512×3) is brutally expensive — every one of `T` steps is a
full-resolution network pass. Rombach et al. (**Latent Diffusion / Stable Diffusion**, 2022) made it
practical with one move:

1. Train a **VAE** (autoencoder) to compress an image into a small **latent** (e.g. 512×512×3 → 64×64×4).
2. Run the *entire* diffusion process in that compact latent space.
3. Decode the final latent back to pixels once, at the end.

<!-- DIAGRAM:START -->
![Diagram 4](diagrams/01-diffusion-and-image-generation-4.svg)

<details>
<summary>Diagram source (Mermaid)</summary>

```mermaid
flowchart LR
    IMG["image 512×512×3"] -->|"VAE encoder"| Z["latent 64×64×4<br/>(~48× smaller)"]
    Z --> DIFF["diffusion happens HERE<br/>(T denoising steps, cheap)"]
    DIFF --> Zc["clean latent"]
    Zc -->|"VAE decoder"| OUT["image 512×512×3"]
```

</details>
<!-- DIAGRAM:END -->

The compute saving is roughly the compression ratio — the difference between "needs a datacenter" and
"runs on your GPU." Conceptually it's the same instinct as DeepSeek's MLA you analyzed: **do the expensive
operation in a compressed space.** You already have the intuition; this is the image-domain instance.

---

## 7. Conditioning & guidance — how you actually control the output

Everything so far generates *some* plausible image. Text-to-image needs **conditioning**. Two pieces:

**(a) How the text gets in.** The prompt is encoded by a text encoder (**CLIP** text encoder, or **T5**)
into embeddings, which the denoiser attends to via **cross-attention** layers — the Query comes from the
image features, the Keys/Values from the text embeddings. This is *literally the attention mechanism you
already know*, used to let each image region "look at" the prompt. (When SD generates a "red cube on a
blue table," cross-attention is what binds "red" to the cube region.)

**(b) Classifier-free guidance (CFG)** — Ho & Salimans, 2021 — the single most important sampling knob,
and a genuinely clever trick. Train the model *both* conditioned and unconditioned (randomly drop the text
~10% of the time). At sampling, extrapolate away from the unconditioned prediction:

```
ε̂ = ε_uncond + w · (ε_cond − ε_uncond)
```

`w` is the **guidance scale**. `w=1` → normal conditional sampling; `w>1` (typically 5–15) → push harder
toward the prompt: more prompt-faithful and sharper, but too high → oversaturated, less diverse. This is
the diffusion analogue of an LLM's temperature/top-p — the **fidelity ↔ diversity** dial — and you should
file it next to those.

---

## 8. The backbone — and why your transformer knowledge transfers

What network *is* `ε_θ`? Two eras:

- **U-Net era (2020–2022):** a convolutional encoder–decoder with skip connections and a few
  self/cross-attention layers. Good inductive bias for images (locality, multi-scale).
- **Transformer era — DiT (Peebles & Xie, 2023):** replace the U-Net with a **Diffusion Transformer**.
  **Patchify** the latent into a sequence of patch tokens (exactly like ViT), add positional embeddings,
  run standard transformer blocks, condition on `t` and text via adaptive layernorm / cross-attention.
  **This is the bridge to everything you already know** — the denoiser is now a transformer, scaling laws
  return, and the same engineering (FlashAttention, etc.) applies. SD3, PixArt, and Sora are DiT-based.

So your hard-won attention/transformer expertise is *not* stranded on the LLM side — the image/video
frontier is built on the same block. The novelty is the *training objective* (denoising/score), not the
architecture.

**The current frontier — flow matching / rectified flow** (Lipman et al. 2022; Liu et al. 2022; powering
SD3 and Flux): reframe generation as learning a **velocity field** that transports noise to data along the
*straightest possible* probability path. It generalizes diffusion (recall the probability-flow ODE in §4),
and straighter paths mean fewer integration steps → faster sampling. If you read one set of papers past
this section, read these — they're where image/video generation is heading, and the ODE framing from §4 is
the prerequisite you'll already have.

### How an LLM produces images — decoupled vs unified

Two regimes, and the distinction matters:
- **Decoupled (the common production setup):** the LLM writes a rich text prompt; a *separate* diffusion
  model renders it. **DALL·E 3** works this way — GPT and the image generator are different models with
  no shared weights. The LLM is a prompt author, nothing more.
- **Unified (the frontier):** one transformer carries both an autoregressive text objective *and* a
  diffusion image objective. **Transfusion** (Zhou et al., 2024) and **Chameleon** are the reference
  points; native image generation in GPT-4o / Gemini is the productized version. This is close to the
  "one shared backbone, different generative heads" intuition — but it's the *frontier*, not how most
  shipped systems work today.

---

## 9. The bridge to video (preview of §2)

Video = add a **time axis**. Modern video models (Sora, and the open ones) are **DiT over spacetime
patches**: cut the video into patches across height, width, *and* time; run a transformer with attention
spanning frames so motion is coherent; diffuse the whole clip. The "world model" claims you've seen in the
news come from the fact that to denoise video well, the model must implicitly learn object permanence,
physics, and 3D consistency. We'll do this properly in §2 — but notice the pattern: **same diffusion
machinery, one more dimension, transformer backbone.** Your physics lens on "does it actually obey
conservation laws / is the motion physically plausible" will be exactly the right critical angle there,
just as it was for the H800 analysis.

---

## 10. The one-page mental model

<!-- DIAGRAM:START -->
![Diagram 5](diagrams/01-diffusion-and-image-generation-5.svg)

<details>
<summary>Diagram source (Mermaid)</summary>

```mermaid
flowchart TD
    A["Two paradigms: autoregressive (sequential, discrete)<br/>vs DIFFUSION (parallel denoising, continuous)"]
    A --> B["FORWARD: fixed physics — add Gaussian noise to data<br/>xₜ = √ᾱₜ·x₀ + √(1−ᾱₜ)·ε (closed form)"]
    B --> C["LEARN the REVERSE: predict the noise ε_θ(xₜ,t)<br/>≡ estimate the score ∇log p ≡ Langevin / reverse-SDE"]
    C --> D["SAMPLE: denoise from pure noise, T steps<br/>SDE(DDPM) vs ODE(DDIM) → distill to 1–4 steps"]
    D --> E["LATENT diffusion: do it all in a compressed VAE space (cheap)"]
    E --> F["CONDITION: text via cross-attention; control via CFG guidance scale"]
    F --> G["BACKBONE: U-Net → DiT (transformer) → flow matching (frontier)"]
```

</details>
<!-- DIAGRAM:END -->

**The seven things to carry:**
1. Diffusion = **learn to reverse a noising process**; train a denoiser at all noise levels with a plain
   MSE-on-noise loss.
2. The closed-form `xₜ = √ᾱₜ·x₀ + √(1−ᾱₜ)·ε` is the keystone — it makes training a one-step sampling job.
3. **Noise prediction ≡ score estimation ≡ Langevin/SDE** — your stat-mech reading of it is the correct one.
4. **SDE (stochastic, many steps) vs probability-flow ODE (deterministic, few steps)** explains DDPM vs
   DDIM and the whole fast-sampler line; **distillation/consistency** gets to 1–4 steps.
5. **Latent diffusion** (compress, then diffuse) is what made it affordable — same instinct as MLA.
6. **Cross-attention** injects the prompt; **classifier-free guidance (`w`)** is the fidelity↔diversity dial
   (the temperature/top-p of image gen).
7. The backbone went **U-Net → DiT (a transformer) → flow matching** — so your transformer knowledge
   transfers directly; the *only* genuinely new idea is the denoising/score objective.

---

## 11. Check your understanding (frontier-level)

1. Why does predicting the *noise* `ε` (rather than the clean image `x₀` directly) give such a simple
   training loss? Use the closed-form forward equation in your answer.
2. You described DeepSeek's MLA as "low-rank compression to save VRAM." What is the *exact* structural
   analogue in latent diffusion, and why does it buy a roughly proportional compute saving?
3. From the SDE/ODE picture: explain — physically, not by citing the paper — why DDIM can use ~20 steps
   where DDPM wants ~1000. What are you trading away?
4. Classifier-free guidance with a high `w` makes images more prompt-faithful but oversaturated and less
   diverse. Relate this precisely to the LLM sampling knob you already use, and say what "oversaturated"
   corresponds to there.
5. A DiT and a GPT are both transformers. Name two concrete differences in *how* they're used (input,
   attention pattern, training objective, or output) that follow from autoregressive-vs-diffusion.
6. (Stretch / your edge) Sora is pitched as a "world model." From your physics background, design one
   *critical test* — in the spirit of your DeepSeek teardown — that would reveal whether a video diffusion
   model has actually learned physics versus merely memorized plausible-looking motion.

---

## 12. Optional: paper trail (you read papers — here's the efficient path)

In dependency order, skim the abstract + figures of each:
1. **DDPM** (Ho et al., 2020) — the simple-loss formulation. [arXiv:2006.11239](https://arxiv.org/abs/2006.11239)
2. **Score-SDE** (Song et al., 2021) — the unifying SDE/ODE view. [arXiv:2011.13456](https://arxiv.org/abs/2011.13456)
3. **Classifier-Free Guidance** (Ho & Salimans, 2021). [arXiv:2207.12598](https://arxiv.org/abs/2207.12598)
4. **Latent Diffusion / Stable Diffusion** (Rombach et al., 2022). [arXiv:2112.10752](https://arxiv.org/abs/2112.10752)
5. **DiT** (Peebles & Xie, 2023) — diffusion on a transformer. [arXiv:2212.09748](https://arxiv.org/abs/2212.09748)
6. **Flow Matching** (Lipman et al., 2022) + **Rectified Flow** (Liu et al., 2022) — the frontier.
   [arXiv:2210.02747](https://arxiv.org/abs/2210.02747) · [arXiv:2209.03003](https://arxiv.org/abs/2209.03003)

Bring me the one that surprised you or that you want to push past — that's how these sessions work best
for you.

---

## 13. Applied — your own mental model (from the session)

You came in having read the DDPM paper and built a physics-grounded model of diffusion. The session was
a peer-level Q&A. Recording it because the *shape* of what you got right vs wrong is the real lesson.

### What you had right (and sharper than most published explainers)

1. **"It's all about SNR; the model is a noise filter that raises SNR."** Correct, and the SNR axis is
   the *native* coordinate system of the rigorous theory — Kingma et al.'s **Variational Diffusion
   Models** parameterizes the whole loss as an integral over log-SNR. Most blogs never say this.
2. **"Step-by-step noising is just a way to generate samples at different SNR; training needn't be
   sequential — i.i.d. {noisy, clean} pairs at well-distributed SNR would train the same model."**
   Correct, *and that is literally how DDPM trains* (§3): sample a random `t`, jump to that noise level
   via the closed form, one loss, backprop — no per-image chain. The Markov chain is a derivation
   device, not a training procedure. You saw through a misconception many people hold.
3. **"Few steps → looks like the category but lacks detail."** Correct — that's the posterior-mean blur
   (Tweedie) and the low-freq-first / high-freq-later spectral order. Your spectral intuition holds.

### The two mechanisms you had wrong — and the corrected versions

1. **Not "resonance / amplification of signals present in the noise" → annealed Langevin descent on a
   learned energy landscape (§4).** The denoiser is a nonlinear learned map; image content is
   *synthesized*, not linearly amplified out of the seed's frequency components. What the seed *does*
   set is which **basin** you fall into. Keep "the seed selects the sample"; drop "the filter amplifies
   pre-existing signal."
2. **Not "multi-step keeps adding noise to pick up new detail" → integrating a curved trajectory (§5).**
   You corrected this yourself mid-session: the deterministic sampler adds *no* noise; multiple steps
   are needed because the noise→data path is **curved** (nonlinear score field + an annealing target),
   so one big linear step overshoots. The forcing "precision" is step-size/truncation error, not float
   bit-width. Proof: distillation learns the curved map directly → 1–4 steps.

### Where your engineering instinct re-derived real, shipping techniques

- **"The encoder is a reusable image embedder; freeze it, repurpose it."** Real — diffusion features are
  used for discriminative tasks (**DIFT** / "Emergent Correspondence"; diffusion features for
  segmentation). Caveat: it's a *noise-conditioned* encoder, so which `t` you query matters. Correction:
  a **U-Net ≠ YOLO** architecturally (YOLO = backbone + FPN/PAN neck + detection heads, not a symmetric
  encoder–decoder); the true shared idea is "a multi-scale feature backbone is reusable across tasks."
- **"Align image embeddings with text embeddings so the LLM can consume them."** That principle *is*
  **CLIP** (contrastive image-text alignment), and it's how VLMs ingest images — though via a CLIP ViT,
  not the diffusion encoder.
- **Image-editing drift ("remove the glasses, but the hair changes too").** Your diagnosis was right:
  standard diffusion editing (**SDEdit**: noise partway, regenerate) re-samples the *whole* image with
  nothing pinning the untouched regions. And both your proposed fixes are production reality:
  - **Proposal 1 (agentic loop with deterministic editors):** a real, growing product direction; plays
    to your agent-orchestration strength.
  - **Proposal 2 (instruction → mask which features to freeze → apply as mask):** you independently
    re-derived **masked inpainting + grounded segmentation** — the dominant localized-edit pipeline.
    The "draw the boundary from the instruction" model exists: **GroundingDINO / SAM / Grounded-SAM**
    turn "the glasses" into a mask; inpainting regenerates only inside it. The attention-space cousin
    (no explicit mask, edit the cross-attention maps from §7) is **Prompt-to-Prompt**; the
    instruction-trained editor is **InstructPix2Pix** (which still drifts — *why* mask methods win).

**Signal for future sessions:** teach him non-text models **through the physics he owns** (energy
landscapes, annealing, SDE/ODE, spectra) and let him **stress-test the model until it breaks, then give
the precise why** — that's where the real learning happened here. His instinct for *system architecture*
(reusable embedders, mask-based control, agentic edit loops) runs ahead of the literature he's read.

---

## References

*(All links verified 2026-06-10. The OpenAI Sora report bot-blocks automated fetchers but resolves
normally in a browser.)*

**The spine — diffusion theory & architecture (dependency order):**
- **[Ho et al. — Denoising Diffusion Probabilistic Models (DDPM)](https://arxiv.org/abs/2006.11239)** —
  the simple noise-prediction loss.
- **[Song et al. — Score-Based Generative Modeling through SDEs](https://arxiv.org/abs/2011.13456)** —
  the unifying score / forward-SDE / reverse-SDE / probability-flow-ODE picture (§4).
- **[Ho & Salimans — Classifier-Free Diffusion Guidance](https://arxiv.org/abs/2207.12598)** — the
  guidance-scale knob (§7).
- **[Rombach et al. — High-Resolution Image Synthesis with Latent Diffusion Models](https://arxiv.org/abs/2112.10752)** —
  Stable Diffusion; diffuse in a compressed latent (§6).
- **[Peebles & Xie — Scalable Diffusion Models with Transformers (DiT)](https://arxiv.org/abs/2212.09748)** —
  the transformer backbone (§8).
- **[Lipman et al. — Flow Matching for Generative Modeling](https://arxiv.org/abs/2210.02747)** +
  **[Liu et al. — Rectified Flow](https://arxiv.org/abs/2209.03003)** — the current frontier (§8).

**The session corrections:**
- **[Kingma et al. — Variational Diffusion Models](https://arxiv.org/abs/2107.00630)** — the **SNR**
  parameterization that confirms your axis.
- **[Karras et al. — Elucidating the Design Space of Diffusion Models (EDM)](https://arxiv.org/abs/2206.00364)** —
  separates the deterministic ODE path from optional **stochastic churn** (error-correction), the precise
  version of "noise's real role" (§5).
- **[Song et al. — Consistency Models](https://arxiv.org/abs/2303.01469)** — learn the curved map directly
  → 1–4 steps; the proof that step-count is about *curvature*, not noise (§5).

**Representation reuse & multimodal (your architecture instincts):**
- **[Radford et al. — CLIP: Learning Transferable Visual Models from NL Supervision](https://arxiv.org/abs/2103.00020)** —
  image-text embedding alignment; how VLMs ingest images.
- **[Tang et al. — Emergent Correspondence from Image Diffusion (DIFT)](https://arxiv.org/abs/2306.03881)** —
  diffusion encoder features used for discriminative tasks.
- **[Zhou et al. — Transfusion: one multimodal transformer (AR text + diffusion images)](https://arxiv.org/abs/2408.11039)** —
  the "unified" generation frontier (§8).

**Editing — your two proposals, as shipping techniques:**
- **[Meng et al. — SDEdit](https://arxiv.org/abs/2108.01073)** — the noise-then-regenerate editing that
  causes the drift you diagnosed.
- **[Kirillov et al. — Segment Anything (SAM)](https://arxiv.org/abs/2304.02643)** +
  **[Liu et al. — Grounding DINO](https://arxiv.org/abs/2303.05499)** — instruction/text → mask, for
  masked inpainting (your Proposal 2).
- **[Hertz et al. — Prompt-to-Prompt (cross-attention editing)](https://arxiv.org/abs/2208.01626)** — the
  mask-free, attention-space cousin.
- **[Brooks et al. — InstructPix2Pix](https://arxiv.org/abs/2211.09800)** — the instruction-trained editor.

**Explainers / video:**
- **[Lilian Weng — "What are Diffusion Models?"](https://lilianweng.github.io/posts/2021-07-11-diffusion-models/)** —
  the best single math-complete blog explainer.
- **[Sora technical report — "Video generation models as world simulators" (OpenAI)](https://openai.com/index/video-generation-models-as-world-simulators/)** —
  the spacetime-patch DiT video story, for §9 and your critical-test exercise.

---

### What's next

After we Q&A and finalize this, the AI thread (M12 Ch2) continues:
- **§2 — Video generation** (spacetime DiT, Sora, temporal coherence, the "world model" debate — your
  critical-thinking + physics edge applies directly).
- **§3 — Audio, speech & TTS** (neural codecs, discrete audio tokens, autoregressive vs diffusion TTS).
- **§4 — Multimodal & representation models** (CLIP, VLMs, embedding models — how modalities get fused).

Interleaved with your real-gap tracks (M01 Ch2 memory · M04 Ch1 §2 data-flow / Ch2 decomposition).
