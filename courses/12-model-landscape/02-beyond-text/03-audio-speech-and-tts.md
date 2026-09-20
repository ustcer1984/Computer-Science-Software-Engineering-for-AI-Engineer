# M12 · Ch2 · §3 — Audio, Speech & TTS

> **Module:** The Model Landscape
> **Chapter:** Beyond text (image/diffusion, video, **audio/speech/TTS**, multimodal)
> **Section:** How machines represent, recognise, and generate sound — the representation
> problem (waveform → spectrogram → discrete tokens), the classic TTS (text-to-speech) cascade, neural audio
> codecs and the LLM-ification of audio, the diffusion/flow-matching branch, ASR (automatic speech recognition) and
> self-supervised speech, and the frontier: native audio-in/audio-out full-duplex models.
> **Plus §9 — an application-side model-selection cheatsheet** (SOTA + open, per use case).
> **Status:** ✅ finalized 2026-07-15. Body pitched high and went untouched (confirmed as a
> reference); the session redirected to *application-side model selection* (→ new §9 cheatsheet,
> merged in) and three real use-case consults (→ §12 Applied). Builds on §1 (diffusion,
> score/energy view, latent diffusion) and §2 (flow matching, tokenisation, DiT). Math in
> LaTeX; real matplotlib plots; key terms glossed in 中文 (大陆/台灣).

**Estimated study time:** 2.5–3 hours (frontier material; budget extra if you read the cited papers).
**Prerequisites:** §1 (DDPM, the score/SDE view, latent diffusion), §2 (flow matching, codec-style
tokenisation, the DiT backbone). Your transformer and quantization knowledge transfers directly — the
modern audio stack is *autoregressive transformers over discrete tokens* and *flow-matching decoders*,
both of which you already understand from the LLM (large language model) and diffusion sides.

---

## Why this section exists (for *you*)

You've now closed the image (§1) and video (§2) gaps. Audio is the third "beyond text" modality, and
it's the one where your **background is the biggest advantage of any section in this chapter** — audio
*is* a signal-processing domain, and Fourier analysis, sampling theory, and the time–frequency
trade-off are tools you own from physics. Where §1 leaned on energy landscapes and §2 on ODE (ordinary differential equation)
trajectories, this section leans on the DSP (digital signal processing) you already have.

The section is built around one organising idea that makes the whole field legible:

> **Every audio model is defined by the representation it chooses.** Raw waveform, spectrogram, or
> discrete token — that single choice determines the architecture, the cost, and the failure modes.

Once you see the representation, you can predict the model. And the punchline connects straight back
to §2: the move that unlocked modern audio generation — **neural audio codecs producing discrete
tokens** — is the audio analogue of spacetime-patch tokenisation, and the technique that made
high-quality TTS fast — **flow matching** — is the exact same one you dissected for video.

---

## 1. The representation problem

<details>
<summary><b>Vocabulary for this section</b> — terms, abbreviations and every symbol in the formulas (click to expand)</summary>

**Abbreviations**

| Short | Stands for | Meaning |
|---|---|---|
| **STFT** | short-time Fourier transform | Fourier transform of successive short windows of the signal — the basis of the spectrogram |
| **PCM** | pulse-code modulation | raw uncompressed audio: amplitude sampled at a fixed rate and quantised to a fixed bit depth |
| **DSP** | digital signal processing | the classical signal-analysis toolkit the section borrows from |
| **Hz / kHz** | hertz / kilohertz | cycles per second, and thousands of cycles per second |
| **ms** | millisecond | thousandth of a second — the unit of STFT window and hop lengths |

**Symbols used in the formulas**

| Symbol | Reads as | Meaning |
|---|---|---|
| $f_{s}$ | "f-sub-s" | the sampling rate; the $s$ subscript means "sampling" |
| $f_{\max}$ | "f-max" | the highest frequency present in the signal |
| $f_{0}$ | "f-zero" | the fundamental frequency (pitch); the zero subscript means the lowest harmonic |
| $f$ | "f" | a frequency in hertz, the input to the mel warp |
| $m$ | "m" | the warped frequency in mels, the output of the mel formula |
| $\mu$-law | "mu-law" | the logarithmic companding curve used to quantise amplitude perceptually |
| $L$ | "capital L" | sequence length in units the model must process |
| $O(L^{2})$ | "big-O of L squared" | self-attention cost growing with the square of the sequence length |
| `2^{16}` | "two to the sixteenth" | the number of amplitude levels 16-bit PCM can represent |
| $\log_{10}$ | "log base ten" | the base-ten logarithm in the mel formula |

**Terms**

| Term | Definition |
|---|---|
| **Sampling rate** | how many amplitude readings per second are taken from the pressure wave |
| **Bit depth** | how many bits encode each amplitude reading |
| **Quantisation** | rounding a continuous amplitude to one of a finite set of levels |
| **Companding** | compressing amplitude non-linearly before quantising, so quiet detail survives |
| **Nyquist–Shannon theorem** | you must sample at least twice the highest frequency you want to represent |
| **Aliasing** | frequencies above half the sampling rate folding down and masquerading as lower ones |
| **Receptive field** | how much of the input one output unit can actually see |
| **Phoneme** | the smallest contrastive sound unit of a language |
| **Spectrogram** | the magnitude of the STFT: a time × frequency image of energy |
| **Window / hop** | the length of each analysed slice, and how far the analysis advances between slices |
| **Time–frequency uncertainty** | the hard trade-off that a window cannot be sharp in both time and frequency |
| **Mel scale** | a perceptually warped frequency axis, roughly logarithmic above a few hundred hertz |
| **Mel-spectrogram** | a spectrogram passed through a mel-spaced triangular filterbank, usually log-scaled |
| **Filterbank** | the set of overlapping band filters that pool STFT bins into mel channels |
| **Harmonic** | an integer multiple of the fundamental frequency, visible as horizontal bands |
| **Formant** | a resonance of the vocal tract; the pattern of formants distinguishes vowels |
| **Fricative** | a turbulent consonant such as "s", broadband in frequency |
| **Phase** | the timing offset of each frequency component — discarded by a magnitude spectrogram |
| **Griffin–Lim** | the classical iterative algorithm for guessing a consistent phase from magnitudes |
| **Vocoder** | the model that renders a waveform from a spectrogram, effectively synthesising the missing phase and fine detail |

</details>

### What sound is, to a computer

Sound is a pressure wave — a continuous 1-D function of time. A microphone samples it into a
sequence of numbers by two discretisations:

- **Sampling rate** $f_{s}$ — how many amplitude readings per second. By the **Nyquist–Shannon**
  theorem, to represent frequencies up to $f_{\max}$ without aliasing you need $f_{s} \geq 2 f_{\max}$.
  Human hearing tops out near 20 kHz, so music uses $f_{s} = 44.1$ or $48$ kHz. Speech energy lives
  below ~8 kHz, so speech systems commonly use **16 kHz** (and telephony historically 8 kHz).
- **Bit depth** — how finely each amplitude is quantised. 16-bit PCM (pulse-code modulation) gives $2^{16} = 65{,}536$ levels;
  the classic $\mu$-law companding used by WaveNet quantises to 256 levels on a logarithmic (loudness-
  perceptual) scale.

You know Nyquist already; the point worth carrying forward is the *consequence*.

### The sequence-length problem — why raw waveform is (almost) hopeless

Ten seconds of 24 kHz audio is $240{,}000$ samples. A transformer's self-attention is $O(L^{2})$ in
sequence length $L$ (Ch1 §3 / your own LLM knowledge), so attending over raw audio is a non-starter —
that's $5.76 \times 10^{10}$ attention entries for a ten-second clip. Even a purely convolutional or
recurrent model must span enormous receptive fields to reach from one phoneme to the next (a single
phoneme is ~1,500 samples).

This is *the* constraint that shapes the whole field. Every successful audio model is, at heart, a
scheme for **shortening the sequence** — compressing 240,000 raw samples into something a neural
network can actually model, while throwing away as little perceptually relevant information as possible.

![Units a model must handle for 10 s of audio, across representations (log scale): raw waveform is ~300× longer than a neural-codec token stream](diagrams/03-audio-speech-and-tts-fig2.svg)

**Figure 2** — units a model must handle for ten seconds of audio, on a log scale: raw waveform is about 300x a codec token stream.

The figure previews the whole section's cast of representations, ranked by how many units the model
must process. Keep it in mind — each representation below is one bar.

### Time domain vs frequency domain: the spectrogram

The alternative to modelling raw samples is to move to the **frequency domain**. The **Short-Time
Fourier Transform (STFT)** slides a window (say 25 ms) across the signal in hops (say 10 ms) and takes
the Fourier transform of each window. The magnitude of the result is a **spectrogram**: a 2-D
time × frequency image where brightness is energy at that time and frequency.

This does two things at once:

1. **It shortens the sequence.** A 10 ms hop turns 24,000 samples/second into ~100 frames/second — a
   ~240× reduction in the temporal axis.
2. **It exposes structure.** Speech and music have clear frequency structure (harmonics, formants,
   notes) that is *implicit* in the waveform but *explicit* in the spectrogram.

> **DSP lens (this one earns its place).** The STFT window length is a genuine
> **time–frequency uncertainty** trade-off — the same Gabor/Heisenberg limit you know. A long window
> gives fine frequency resolution but smears time (you can't localise a transient); a short window
> localises time but blurs frequency. There is no window that is sharp in both. Every spectrogram is a
> point on that trade-off curve, chosen for the signal.

### The mel scale: warp frequency to perception

Human pitch perception is roughly logarithmic — we distinguish 100 Hz from 200 Hz easily but barely
hear 10,000 Hz vs 10,100 Hz. The **mel scale** warps the frequency axis to match:

$$m = 2595 \thinspace \log_{10}\left(1 + \frac{f}{700}\right).$$

A **mel-spectrogram** applies a bank of triangular filters spaced evenly on the mel scale (so densely
packed at low frequency, sparse at high) and usually takes the log of the energy. The result is a
compact ~80-channel × ~frames image that discards perceptually irrelevant detail. **The mel-spectrogram
is the single most important classical representation in speech** — it is the input to almost every
pre-2022 speech model and still ubiquitous today.

![One utterance in three representations: waveform, linear spectrogram, and mel-spectrogram — the mel axis compresses high frequencies to match perception](diagrams/03-audio-speech-and-tts-fig1.svg)

**Figure 1** — one utterance in three representations — waveform, linear spectrogram, and mel-spectrogram.

Panel (a) is the raw waveform — three "syllables" and, at ~0.47 s, a broadband **fricative** burst
(an "s"-like sound). Panel (b) is the linear spectrogram: the horizontal bands are **harmonics** of
the pitch $f_{0}$, and the fricative shows up as a vertical smear of energy across *all* frequencies.
Panel (c) is the mel version — notice the low frequencies (where the harmonics and formants live) are
stretched out, and the highs are squashed. Same information, warped to where the ear cares.

### The phase problem — why you can't just invert a spectrogram

Here is the subtlety that motivates half of this section. The spectrogram keeps only the **magnitude**
of each STFT bin and throws away the **phase**. But the waveform depends on both. To turn a
(mel-)spectrogram back into audio you must **reconstruct the missing phase** — and that is a genuinely
hard inverse problem.

The classical answer, **Griffin–Lim** (1984), iterates between the time and frequency domains guessing
a consistent phase. It works but sounds "robotic"/metallic because the reconstructed phase is only
approximately right. This lossy inverse is exactly why, when neural TTS produces a mel-spectrogram, it
needs a learned **vocoder** to render high-quality audio from it: the vocoder's real job is to
synthesise plausible phase and fine waveform detail that the mel-spectrogram doesn't contain.

> **DSP lens.** Magnitude-only spectrograms are (within a window) invariant to time-shift, which is why
> phase — the thing that encodes *precisely when* each frequency component peaks — is both discarded by
> the transform and essential to reconstruct. Getting phase wrong is audible as roughness, not as a
> pitch or loudness error.

With the representations in hand, the model families fall out naturally.

---

## 2. The classic TTS cascade (2017–2021)

<details>
<summary><b>Vocabulary for this section</b> — terms, abbreviations and every symbol in the formulas (click to expand)</summary>

**Abbreviations**

| Short | Stands for | Meaning |
|---|---|---|
| **TTS** | text-to-speech | synthesising speech audio from written text |
| **GAN** | generative adversarial network | a generator trained against discriminators that judge realism |
| **seq2seq** | sequence-to-sequence | an encoder–decoder model mapping one variable-length sequence to another |
| **AR / non-AR** | autoregressive / non-autoregressive | producing outputs one step at a time versus all at once in parallel |
| **mel** | mel-spectrogram | the perceptually warped spectrogram from §1, used as the pipeline's interface |

**Symbols used in the formulas**

| Symbol | Reads as | Meaning |
|---|---|---|
| $\mathbf{x}$ | "bold x" | the whole waveform, as a vector of samples; bold marks the full sequence |
| $x_{t}$ | "x-sub-t" | the single waveform sample at time index $t$ |
| $x_{<t}$ | "x-less-than-t" | all samples before $t$ — the autoregressive conditioning history |
| $p(\mathbf{x})$ | "p of bold x" | the probability of the whole waveform |
| $\prod_{t}$ | "product over t" | multiply the per-sample conditional probabilities over all time steps |
| $\mid$ | "given" | conditioning: what follows the bar is what is held fixed |

**Terms**

| Term | Definition |
|---|---|
| **Cascade** | a pipeline of separately trained stages, here text → mel → waveform |
| **Acoustic model** | the stage mapping text (or phonemes) to a mel-spectrogram |
| **Alignment** | the correspondence between input symbols and output frames |
| **Monotonic alignment** | an alignment that never goes backwards or skips — enforced structurally by a duration model |
| **Duration predictor** | the module predicting how many frames each phoneme should occupy |
| **Length regulator** | the operation that repeats each phoneme's hidden state for its predicted duration |
| **Variance adaptor** | FastSpeech 2's module predicting pitch and energy alongside duration |
| **Skipping / repeating / babbling** | the characteristic failure modes of soft attention-based alignment |
| **Dilated causal convolution** | a convolution with gaps between kernel taps, giving a large receptive field with few layers, and seeing only the past |
| **Inverse autoregressive flow** | an invertible model that generates all samples in parallel, used as the distilled student of WaveNet |
| **Distillation** | training a fast student to match a slow teacher's distribution |
| **Discriminator** | the adversarial judge; HiFi-GAN uses several, at multiple periods and scales |
| **Transposed convolution** | the upsampling operation that expands frame-rate features up to sample-rate audio |
| **Mel bottleneck** | the hand-designed, phase-free interface between the two stages, and the cascade's main weakness |

</details>

Text-to-speech was, for years, a pipeline of specialised models. Understanding the cascade is worth it:
it names the sub-problems, and every "end-to-end" model since is best understood as *collapsing* one or
more of these stages.

$$\underbrace{\text{text}}_{} \quad \rightarrow \quad \underbrace{\text{acoustic model}}_{\text{text} \to \text{mel}} \quad \rightarrow \quad \underbrace{\text{mel-spectrogram}}_{} \quad \rightarrow \quad \underbrace{\text{vocoder}}_{\text{mel} \to \text{waveform}} \quad \rightarrow \quad \text{audio}.$$

### Stage 1 — the acoustic model (text → mel-spectrogram)

The hard part here is **alignment**: text has (say) 40 phonemes; the mel-spectrogram has 800 frames.
Which frames belong to which phoneme, and for how long? The two generations answer differently.

- **Tacotron 2** (Shen et al., 2018) is **autoregressive with attention** — a seq2seq model that emits
  mel frames one at a time, using an attention mechanism to softly align each frame to the input
  characters. It produced the first genuinely natural neural TTS, but inherited the failure modes of
  soft attention: **skipping** words, **repeating** them, or **babbling** on hard inputs, because
  nothing forces the alignment to be monotonic and complete.
- **FastSpeech / FastSpeech 2** (Ren et al., 2019/2020) is **non-autoregressive**. It predicts an
  explicit **duration** for each phoneme with a duration predictor, then a **length regulator** simply
  copies each phoneme's hidden state that many times to build the frame sequence — no attention, no
  autoregression. This makes it (a) **fast** (all frames in parallel) and (b) **robust** (a phoneme
  can't be skipped or repeated; the alignment is monotonic *by construction*). FastSpeech 2 adds a
  **variance adaptor** predicting pitch and energy, which the mel decoder conditions on.

This autoregressive-vs-parallel split, and the "make the alignment structural instead of learned" move,
is a theme you'll see repeated — it's the same instinct as FastSpeech's descendants in the flow-matching
branch (§5).

### Stage 2 — the vocoder (mel → waveform)

This is the phase-reconstruction problem from §1, solved with a learned model. Its history is a
sprint from "high quality but unusably slow" to "high quality and real-time":

- **WaveNet** (van den Oord et al., 2016) models the waveform **autoregressively, one sample at a
  time**: $p(\mathbf{x}) = \prod_{t} p(x_{t} \mid x_{<t})$, with **dilated causal convolutions**
  stacking to a huge receptive field. Superb quality — and catastrophically slow, because generating
  one second means 24,000 sequential forward passes.
- **Parallel WaveNet** (2017) distils the autoregressive teacher into a parallel student (an inverse
  autoregressive flow), buying real-time synthesis.
- **HiFi-GAN** (Kong et al., 2020) is the workhorse that won: a **GAN (generative adversarial network)** vocoder whose generator is a
  stack of transposed convolutions and whose discriminators judge the waveform at multiple periods and
  scales. It is fast, small, and near-indistinguishable from real audio — and it's still a default
  vocoder in 2025.
- **Flow** (WaveGlow) and **diffusion** (DiffWave, WaveGrad) vocoders also exist; diffusion vocoders
  are highest-quality-per-effort but slower than GANs.

**The cascade's weakness** is the mel-spectrogram bottleneck in the middle: it's a hand-designed
interface, it discards phase, and errors compound across the two independently-trained stages. The rest
of the section is largely the story of **removing that bottleneck**.

---

## 3. Neural audio codecs — turning audio into discrete tokens

<details>
<summary><b>Vocabulary for this section</b> — terms, abbreviations and every symbol in the formulas (click to expand)</summary>

**Abbreviations**

| Short | Stands for | Meaning |
|---|---|---|
| **VQ** | vector quantization | replacing a vector by the index of the nearest codebook entry |
| **VQ-VAE** | vector-quantized variational autoencoder | an autoencoder with a discrete codebook bottleneck |
| **RVQ** | residual vector quantization | a cascade of codebooks, each quantising what the previous one left over |
| **GAN** | generative adversarial network | the adversarial training used for the codec's decoder |
| **DAC** | Descript Audio Codec | a high-fidelity open neural codec |
| **kHz** | kilohertz | thousands of samples per second |

**Symbols used in the formulas**

| Symbol | Reads as | Meaning |
|---|---|---|
| $N$ | "capital N" | the number of codebooks in the RVQ cascade (equivalently, tokens per frame) |
| $K$ | "capital K" | the number of entries in each codebook |
| $K^{N}$ | "K to the N" | the number of distinct combinations the cascade can express |
| $N \log_{2} K$ | "N log-base-two K" | the bits needed to store one frame: $\log_{2} K$ bits per codebook, $N$ of them |

**Terms**

| Term | Definition |
|---|---|
| **Neural audio codec** | a learned encoder–quantiser–decoder that turns waveforms into discrete tokens and back |
| **Encoder** | strided convolutions compressing the waveform to a low-rate sequence of latent vectors |
| **Strided convolution** | a convolution that skips positions, downsampling as it goes |
| **Latent vector** | the continuous per-frame representation before quantisation |
| **Vector quantiser** | the module snapping a latent to its nearest codebook entry |
| **Codebook** | the learned set of representative vectors; its indices are the tokens |
| **Token (audio)** | the integer index of a codebook entry |
| **Frame** | one time step of the encoder's output, costing $N$ tokens under RVQ |
| **Residual** | what a quantiser failed to capture, passed on to the next codebook |
| **Commitment loss** | the VQ term pulling encoder outputs toward the codebook entries they select |
| **Reconstruction loss** | the term penalising difference between input and decoded waveform |
| **Coarse-to-fine** | the first codebook carrying structure, later ones carrying refinement |
| **Bitrate** | bits per second of encoded audio |
| **Flattening vs parallel prediction** | emitting the $N$ codebook streams one after another versus all at once — the RVQ ordering problem |
| **Delay / interleaving pattern** | offsetting the codebook streams in time as a middle ground between the two |

</details>

This is the pivotal idea of modern audio, and the one that connects the field to everything you know
about LLMs. It answers the sequence-length problem from §1 not by moving to the frequency domain, but by
**learning a discrete vocabulary for audio**.

### The VQ-VAE (vector-quantized variational autoencoder) lineage

A neural audio codec is an autoencoder with a **quantiser** in the middle:

- an **encoder** (strided convolutions) compresses the waveform to a low-rate sequence of latent
  vectors (e.g. 75 vectors/second — a ~320× temporal reduction from 24 kHz);
- a **vector quantiser** snaps each latent vector to the nearest entry in a learned **codebook**,
  replacing it with the entry's integer index — a **token**;
- a **decoder** (a GAN, à la HiFi-GAN) reconstructs the waveform from the quantised vectors.

The whole thing is trained with a reconstruction loss + adversarial loss + the VQ commitment loss.
Now audio is a **short sequence of integers from a fixed vocabulary** — exactly the shape a language
model eats.

### Residual Vector Quantization (RVQ): the trick that makes it work

A single codebook can't capture audio at high fidelity — you'd need an astronomically large vocabulary.
**RVQ** (used in SoundStream, EnCodec, DAC) solves this with a *cascade* of codebooks, each quantising
the **residual error** left by the previous one:

<!-- DIAGRAM:START -->
![Diagram 1](diagrams/03-audio-speech-and-tts-1.svg)

<details>
<summary>Diagram source (Mermaid)</summary>

```mermaid
flowchart TB
    x["Encoder output\nframe vector x"] --> c1["Codebook 1\npick nearest e1, emit token 1"]
    c1 --> r1["residual r1 = x minus e1"]
    r1 --> c2["Codebook 2\npick nearest e2, emit token 2"]
    c2 --> r2["residual r2 = r1 minus e2"]
    r2 --> c3["Codebooks 3..N\nquantize each residual"]
    c3 --> sum["Reconstruction\nx_hat = e1 + e2 + ... + eN"]
    sum --> dec["Codec decoder (GAN) then waveform"]
```

</details>
<!-- DIAGRAM:END -->

The first codebook captures the coarse structure; each subsequent one refines what's left. With $N$
codebooks of size $K$ each, you get the expressive power of $K^{N}$ combinations at the storage cost of
$N \log_{2} K$ bits — a **coarse-to-fine** decomposition that should feel familiar from your work with
block quantization on the LLM side (§ your DeepSeek deck), and from §1's coarse-to-fine diffusion.

This is a real, deployed technology twice over: **EnCodec** (Défossez et al., Meta, 2022) is a
neural codec that beats MP3 at the same bitrate, *and* its tokens are the substrate for generative
audio models. **DAC** (Descript Audio Codec, 2023) improved fidelity further.

### The catch RVQ introduces

RVQ multiplies the token count: one *frame* now costs $N$ tokens (one per codebook level). Look back at
the figure in §1 — "codec RVQ, 8 books" is 8× taller than "codec, 1 book". So a generative model over
codec tokens must decide **how to order** the $N$ codebook streams. Flatten them (fully autoregressive,
$N$× longer sequence)? Predict all $N$ in parallel per frame (fast, but they're correlated)? The
**delay/interleaving patterns** used by MusicGen (§4) are engineering answers to exactly this. It is the
audio-specific wrinkle that has no clean analogue in text.

---

## 4. The LLM-ification of audio

<details>
<summary><b>Vocabulary for this section</b> — terms, abbreviations and every symbol in the formulas (click to expand)</summary>

**Abbreviations**

| Short | Stands for | Meaning |
|---|---|---|
| **LM** | language model | a model predicting the next token in a sequence, here over audio tokens |
| **AR / NAR** | autoregressive / non-autoregressive | token-by-token generation versus parallel generation |
| **RVQ** | residual vector quantization | the multi-codebook scheme from §3 producing acoustic tokens |
| **TTS** | text-to-speech | speech synthesis from text |
| **HuBERT / w2v-BERT** | hidden-unit BERT / wav2vec-BERT | self-supervised speech models whose discrete units serve as semantic tokens (§6) |

**Symbols used in the formulas**

| Symbol | Reads as | Meaning |
|---|---|---|
| $N$ | "capital N" | the number of RVQ codebook streams the generative model must order |
| $i$ | "i" | the codebook index (which level of the residual cascade) |
| $i-1$ | "i minus one" | the next-coarser codebook, used as context in MusicGen's delay pattern |
| $t$ | "t" | the frame index along time |

**Terms**

| Term | Definition |
|---|---|
| **Semantic token** | a low-rate discrete unit capturing linguistic content and phonetics, from a self-supervised speech model |
| **Acoustic token** | an RVQ codec token capturing timbre, prosody and recording detail |
| **Timbre** | the voice quality that identifies a speaker or instrument, independent of what is said |
| **Prosody** | rhythm, stress and intonation |
| **Staged generation** | model the semantic stream first, then condition the acoustic stream on it |
| **Prompt (audio)** | a short reference recording, encoded to tokens and prepended so the model continues in that voice |
| **In-context learning** | adapting behaviour from the prompt alone, with no weight update |
| **Zero-shot voice cloning** | reproducing an unseen speaker's voice from a few seconds of reference audio |
| **Codebook delay pattern** | offsetting each RVQ stream by one step so level $i$ at frame $t$ is predicted from level $i-1$ of the same frame |
| **Long-range structure** | song- or discourse-level organisation over minutes, still only partly solved |

</details>

Once audio is discrete tokens, the entire autoregressive-transformer playbook applies. This is the
dominant paradigm of the last three years, and it collapses the §2 cascade into a single language model.

<!-- DIAGRAM:START -->
![Diagram 2](diagrams/03-audio-speech-and-tts-2.svg)

<details>
<summary>Diagram source (Mermaid)</summary>

```mermaid
flowchart TB
    subgraph classic["Classic cascade (2017-2021)"]
        direction TB
        t1["Text"] --> am["Acoustic model\n(Tacotron / FastSpeech)"]
        am --> mel["Mel-spectrogram\n(hand-designed interface)"]
        mel --> voc["Vocoder\n(WaveNet / HiFi-GAN)"]
        voc --> w1["Waveform"]
    end
    subgraph modern["Codec language model (2022-)"]
        direction TB
        t2["Text (+ 3s voice prompt)"] --> lm["Audio LM\nAR transformer over codec tokens"]
        lm --> tok["Discrete audio tokens"]
        tok --> cdec["Codec decoder\n(EnCodec / DAC)"]
        cdec --> w2["Waveform"]
    end
```

</details>
<!-- DIAGRAM:END -->

### Semantic vs acoustic tokens — the two-level insight

**AudioLM** (Borsos et al., Google, 2022) made a key distinction that recurs everywhere:

- **Semantic tokens** — extracted from a self-supervised speech model (w2v-BERT / HuBERT, §6). They
  capture **content and phonetics** (what is said, the linguistic structure) at a low rate, but discard
  speaker identity and fine acoustic detail.
- **Acoustic tokens** — the RVQ codec tokens from §3. They capture **how it sounds** (speaker, prosody,
  recording conditions) in fine detail, but individually carry little linguistic meaning.

AudioLM generates in stages: first model the **semantic** token stream (gets the content and long-range
structure right), then generate **acoustic** tokens *conditioned on* the semantic ones (fills in a
consistent voice and fidelity). This is coarse-to-fine again, now split along a *content vs timbre* axis
— and it's why the field talks about "semantic tokens" as a first-class object.

### VALL-E: TTS as a language-modelling task

**VALL-E** (Wang et al., Microsoft, 2023) reframed TTS itself as codec-language-modelling and delivered
the headline capability of the era: **zero-shot voice cloning from a 3-second sample**. You give it the
text to speak *and* a 3-second recording of a target speaker (encoded to acoustic tokens) as a **prompt**;
it continues the token sequence in that speaker's voice. No fine-tuning — the speaker is adapted purely
by **in-context learning**, exactly the mechanism you know from LLM few-shot prompting.

VALL-E uses a hybrid: an **autoregressive** model for the first (coarse) codebook stream and a
**non-autoregressive** model for the remaining codebooks (conditioned on the first), a pragmatic answer
to the RVQ-ordering problem from §3. The capability — and its obvious misuse potential — is why voice
cloning became a deepfake and consent concern almost overnight.

### MusicGen and music generation

**MusicGen** (Copet et al., Meta, 2023) is a single-stage codec transformer for **music** from text,
and its contribution is largely the **codebook delay pattern**: instead of flattening the $N$ RVQ
streams (too long) or predicting them fully in parallel (ignores their correlation), it offsets each
codebook by one step so the model predicts codebook $i$ of frame $t$ using codebook $i-1$ of the same
frame — a clean middle ground. Music also raises the **long-range structure** problem in its sharpest
form (a song has verse/chorus structure over minutes), which is still only partly solved.

---

## 5. The diffusion / flow-matching branch

<details>
<summary><b>Vocabulary for this section</b> — terms, abbreviations and every symbol in the formulas (click to expand)</summary>

**Abbreviations**

| Short | Stands for | Meaning |
|---|---|---|
| **TTS** | text-to-speech | speech synthesis from text |
| **DiT** | diffusion transformer | the patch-token transformer denoiser from §1 and §2, reused here for speech |
| **FM** | flow matching | training a velocity field along a straight noise-to-data path (§2) |
| **DDPM** | denoising diffusion probabilistic models | the many-step stochastic diffusion sampler used as the speed baseline |
| **NAR** | non-autoregressive | generating the whole output in parallel rather than step by step |
| **AR** | autoregressive | token-by-token generation |

**Terms**

| Term | Definition |
|---|---|
| **Score-based denoising** | generating by following the learned gradient of log-density, as in §1 |
| **Conditional flow matching** | flow matching where the target velocity is defined per noise–data pair |
| **Sampling steps** | the number of solver evaluations needed to go from noise to output |
| **Infilling** | regenerating a masked region of audio so it fits its surrounding context |
| **Speech editing** | replacing words or segments in an existing recording via infilling |
| **Monotonic alignment** | a strictly forward, non-skipping text-to-frame correspondence |
| **Duration predictor** | the module assigning a frame count to each input symbol — dropped entirely by E2/F5-TTS |
| **Filler tokens** | padding added to the character sequence so it matches the audio length, letting alignment be learned implicitly |
| **Latent diffusion (audio)** | diffusion run over codec latents rather than waveforms or mels |
| **Factorised attributes** | modelling content, prosody, timbre and acoustic detail as separate controllable factors |
| **Zero-shot TTS** | synthesising in a voice the model was never fine-tuned on |

</details>

Not everyone went autoregressive. The other major branch generates audio (usually the mel-spectrogram or
a codec latent) with **diffusion or flow matching** — and this is where §2's machinery reappears
verbatim.

- **Grad-TTS** (Popov et al., 2021) put a **diffusion** model on the mel-spectrogram: score-based
  denoising (§1) conditioned on text, then a vocoder. High quality, but many sampling steps.
- **Voicebox** (Le et al., Meta, 2023) used **flow matching** (§2!) for non-autoregressive,
  text-conditioned speech *infilling* — it can edit a region of speech, do zero-shot TTS, denoise, all
  as instances of "fill in the masked audio." Flow matching gives it the few-step sampling that makes it
  practical.
- **Matcha-TTS** (Mehta et al., 2023) is conditional flow matching + a monotonic-alignment acoustic
  model — a compact, fast, high-quality open TTS.
- **E2-TTS / F5-TTS** (2024) push simplicity to the limit: **no phoneme model, no duration predictor,
  no explicit alignment**. F5-TTS pads the character sequence with filler tokens to the audio length and
  lets a flow-matching DiT (§2's backbone!) learn the alignment implicitly. It's a striking convergence:
  the video-generation architecture (DiT + flow matching) applied to speech, dropping decades of
  speech-specific machinery.
- **NaturalSpeech 2/3** (Microsoft, 2023/24) use latent diffusion over codec latents with factorised
  attributes (content, prosody, timbre, acoustic detail modelled separately) for high-fidelity,
  controllable zero-shot TTS.

> **Callback to §2.** Recall the §2 punchline: flow matching wins because straight-line interpolants
> give a nearly-constant target velocity, so 4–8 sampling steps rival 100+ DDPM steps. That's *why* the
> flow-matching TTS models (Voicebox, Matcha, F5) are fast enough to deploy. The optimizer-vs-
> preconditioning distinction you sharpened for video is the *same* distinction here — nothing new to
> learn, just a new modality wearing it.

**AR-over-codec-tokens vs flow-matching-over-latents** is the central architectural fork in audio
generation today, and it mirrors the AR-vs-diffusion tension you saw in image (§1) and video (§2). AR
models are strong on in-context adaptation (voice cloning) and streaming; flow-matching models are
strong on parallel speed and editing/infilling. The frontier (§7) increasingly blends them.

---

## 6. Recognition and representation: ASR and self-supervised speech

<details>
<summary><b>Vocabulary for this section</b> — terms, abbreviations and every symbol in the formulas (click to expand)</summary>

**Abbreviations**

| Short | Stands for | Meaning |
|---|---|---|
| **ASR** | automatic speech recognition | transcribing speech to text |
| **HMM** | hidden Markov model | the classical state-sequence model used for frame-to-phone alignment |
| **GMM** | Gaussian mixture model | the classical acoustic likelihood model paired with HMMs |
| **DNN** | deep neural network | the neural replacement for the GMM in hybrid systems |
| **CTC** | connectionist temporal classification | a loss that sums over all valid alignments of labels to frames, so no frame-level labels are needed |
| **RNN-T** | recurrent neural network transducer | a streaming-friendly end-to-end ASR architecture |
| **seq2seq** | sequence-to-sequence | encoder–decoder with attention |
| **BERT** | bidirectional encoder representations from transformers | the masked-prediction pretraining recipe HuBERT borrows |
| **log-mel** | log mel-spectrogram | the §1 representation used as Whisper's input |
| **language-ID** | language identification | deciding which language is being spoken |

**Terms**

| Term | Definition |
|---|---|
| **Pronunciation lexicon** | the hand-built dictionary mapping words to phone sequences in classical ASR |
| **End-to-end** | one network from audio to text, replacing the separate acoustic, lexicon and language models |
| **Marginalise over alignments** | sum the probability over every way the labels could line up with the frames |
| **Weakly supervised** | trained on noisy, automatically harvested labels rather than curated transcripts |
| **Multitask training** | one model trained on several tasks, selected by special tokens |
| **Robustness** | working across accents, noise and domains without fine-tuning |
| **Self-supervised learning** | learning representations from unlabelled audio by solving a pretext task |
| **Contrastive task** | identifying the true latent among distractors, which forces informative representations |
| **Masked prediction** | predicting the content of hidden spans from their context |
| **Offline k-means** | clustering features into discrete IDs outside the training loop, to create prediction targets |
| **Discrete unit** | a cluster or codebook index treated as a pseudo-phoneme — the source of semantic tokens |
| **Fine-tuning** | further training a pretrained model on a small labelled dataset for a specific task |

</details>

Generation is half the story. The **encoder** side — turning audio into text or into useful
representations — both matters on its own and *feeds* the generative side (semantic tokens come from
here).

### ASR: from HMMs to Whisper

Automatic Speech Recognition went through the same arc as the rest of ML:

- **HMM-GMM → DNN-HMM**: decades of hand-built pipelines (acoustic model + pronunciation lexicon +
  language model), aligned with Hidden Markov Models.
- **End-to-end**: **CTC** (Connectionist Temporal Classification — a loss that marginalises over all
  alignments of a label sequence to a longer frame sequence, so you don't need frame-level labels),
  **RNN-Transducer** (recurrent-neural-network transducer; streaming-friendly), and **seq2seq attention** collapsed the pipeline into one
  network.
- **Whisper** (Radford et al., OpenAI, 2022) is the model worth internalising, and its lesson is
  **not architectural** — it's a fairly standard encoder-decoder transformer over log-mel input. The
  lesson is **scale of weakly-supervised data**: 680,000 hours of audio-transcript pairs scraped from
  the web, trained multitask (transcribe, translate-to-English, language-ID, timestamps) with special
  tokens marking the task. The result is **robustness** — Whisper works across accents, noise, and
  domains without fine-tuning — bought by data scale and weak labels, not clever inductive bias. It's
  the audio instance of the same "just scale (weakly-labelled) data" story you know from LLMs, and it
  connects to your reading-track thesis about training methodology.

### Self-supervised speech representations — where "semantic tokens" come from

The unlabelled-audio pretraining models are the ones that produce the semantic tokens of §4:

- **wav2vec 2.0** (Baevski et al., Meta, 2020) — mask spans of a latent audio sequence and solve a
  **contrastive** task (identify the true quantised latent among distractors). Fine-tuned with CTC (Connectionist Temporal Classification) on a
  *tiny* amount of labelled data, it reached strong ASR — the "BERT moment" for speech.
- **HuBERT** (Hsu et al., 2021) — instead of contrastive learning, run **offline k-means** on features
  to get discrete cluster IDs, then train the model to **predict the cluster ID of masked frames**
  (masked prediction, like BERT), iterating (re-cluster on better features, repeat). HuBERT's discrete
  units *are* a common source of semantic tokens.
- **w2v-BERT** combines contrastive + masked-prediction objectives; it's what AudioLM used.

The elegant loop to notice: **self-supervised speech models both recognise (fine-tune → ASR) and
generate (their discrete units seed generative audio LMs).** The semantic token is the shared currency
between understanding and generation.

---

## 7. The convergence: native audio LLMs and full-duplex speech

<details>
<summary><b>Vocabulary for this section</b> — terms, abbreviations and every symbol in the formulas (click to expand)</summary>

**Abbreviations**

| Short | Stands for | Meaning |
|---|---|---|
| **ASR** | automatic speech recognition | the speech-to-text stage of a cascade |
| **TTS** | text-to-speech | the text-to-speech stage of a cascade |
| **LLM** | large language model | the text reasoning model in the middle of the cascade |
| **ms** | millisecond | the unit conversational latency is measured in |

**Terms**

| Term | Definition |
|---|---|
| **Cascade (voice assistant)** | ASR then LLM then TTS, three models in series |
| **Native audio model** | one model consuming and producing audio tokens directly, with no text round-trip |
| **Latency** | the delay between the user finishing (or not) and the system's audio starting |
| **Turn-taking** | the strict alternation of speaker and listener assumed by cascades |
| **Full-duplex** | modelling both participants' audio streams at once, so listening and speaking overlap |
| **Backchannel** | the short listener noises ("mm-hm") that overlap the speaker's turn |
| **Interruption (barge-in)** | the user speaking over the system, which requires full-duplex handling |
| **Paralinguistics** | everything carried by speech beyond the words: emotion, tone, emphasis, laughter, speaker identity, background sound |
| **Text bottleneck** | the loss of paralinguistics when audio is forced through a text representation |
| **Inner monologue** | Moshi's jointly predicted, time-aligned text stream that guides the audio tokens and yields a transcript |
| **Mimi** | the low-latency neural codec Moshi generates over |
| **Speech-to-speech translation** | producing spoken output in another language directly from spoken input |

</details>

The obvious way to give an LLM a voice is a **cascade**: ASR (speech → text) → LLM (text → text) → TTS
(text → speech). It works, and it's how most "talk to your assistant" systems were built. But it has two
deep flaws:

1. **Latency.** Three models in series, and the LLM can't start until ASR finishes a full utterance —
   easily 1–2 seconds of turn-taking lag, which breaks the feel of conversation.
2. **Lost paralinguistics.** Text is a lossy bottleneck between the ears and the mouth. Emotion, tone,
   sarcasm, emphasis, laughter, who's-speaking, background sound — all of it is destroyed by the
   ASR→text step and cannot be recovered by TTS. The model literally cannot hear *how* you said
   something, only *what*.

The frontier removes the text bottleneck: **native audio-in, audio-out models** that consume and
produce audio tokens directly, with a text stream alongside for reasoning rather than as the interface.

- **GPT-4o** (OpenAI, 2024) — "omni" — is trained end-to-end across text, vision, and audio, so speech
  goes in and comes out without a text round-trip; average voice latency ~320 ms, in the range of human
  conversational turn-taking, and it can convey and perceive tone and emotion.
- **Moshi** (Défossez et al., Kyutai, 2024) is the open, architecturally explicit version and the one
  to study. It is **full-duplex**: rather than push-to-talk turn-taking, it models **two audio streams
  simultaneously** — the user's and its own — so it can listen and speak at the same time, handle
  interruptions and backchannels ("mm-hm"), and overlap naturally. Its **"inner monologue"** trick
  predicts a time-aligned text token stream jointly with the audio tokens, which both improves content
  quality and gives you a transcript for free. It runs on a neural codec (Mimi) at low latency (~160–200
  ms theoretical).
- Related: **SpiRit-LM** (Meta, 2024) interleaves text and speech tokens in one LM to preserve
  expressivity; **SeamlessM4T** (Meta, 2023) does massively-multilingual speech-to-speech translation.

**Full-duplex is the genuinely new capability** — every prior system, cascade or not, assumed strict
turns. Modelling the conversation as two concurrent token streams is the audio analogue of the shift
from request/response to a persistent bidirectional channel (M01 Ch3 §2's async world, if you want the
systems parallel), and it's where the field is heading.

---

## 8. The current landscape (mid-2025)

<details>
<summary><b>Vocabulary for this section</b> — terms, abbreviations and every symbol in the formulas (click to expand)</summary>

**Abbreviations**

| Short | Stands for | Meaning |
|---|---|---|
| **TTS** | text-to-speech | synthesis of speech from text |
| **ASR** | automatic speech recognition | transcription of speech to text |
| **GAN** | generative adversarial network | the vocoder training scheme behind HiFi-GAN |
| **RVQ** | residual vector quantization | the multi-codebook tokenizer behind EnCodec and DAC |
| **LM** | language model | here, an autoregressive model over audio tokens |
| **NAR** | non-autoregressive | parallel rather than step-by-step generation |
| **SFX** | sound effects | non-speech, non-music audio |
| **omni** | omni-modal | a single model handling text, vision and audio together |

**Terms**

| Term | Definition |
|---|---|
| **Vocoder** | mel-spectrogram to waveform renderer |
| **Neural codec** | learned waveform-to-token-and-back compressor |
| **Codec LM** | a language model trained over codec tokens |
| **Latent diffusion (audio)** | diffusion over a compressed audio latent rather than the waveform |
| **Self-supervised model** | pretrained on unlabelled audio; yields ASR features and semantic units |
| **Factorised codec** | a codec whose latent separates content, prosody, timbre and acoustic detail |
| **Full-duplex** | simultaneous listening and speaking over two modelled streams |
| **Open-weight** | weights published for self-hosting (which is not the same as an open commercial licence) |
| **Consumer hardware** | a single desktop GPU rather than a datacentre accelerator |

</details>

**Table 1** — the mid-2025 audio landscape: representation and purpose, model by model.

| Model | Org | Type | Representation | What it's for |
|---|---|---|---|---|
| HiFi-GAN | Kakao | GAN vocoder | mel → waveform | fast, high-quality vocoding (still a default) |
| FastSpeech 2 | Microsoft | non-AR acoustic model | text → mel | fast, robust classic TTS |
| EnCodec / DAC | Meta / Descript | neural codec (RVQ) | waveform ↔ tokens | the token substrate for generative audio |
| Whisper | OpenAI | seq2seq ASR | log-mel → text | robust multilingual transcription/translation |
| wav2vec 2.0 / HuBERT | Meta | self-supervised | waveform → units | ASR fine-tuning + semantic tokens |
| VALL-E (2) | Microsoft | codec LM | text + prompt → tokens | zero-shot voice cloning |
| AudioLM | Google | codec LM | semantic + acoustic | continuation, foundation for the paradigm |
| MusicGen | Meta | codec LM | text → tokens | open text-to-music |
| Stable Audio | Stability | latent diffusion | text → latent | text-to-music/SFX with timing control |
| Voicebox / F5-TTS | Meta / open | flow matching | text → mel/latent | fast NAR TTS, infilling, editing |
| NaturalSpeech 3 | Microsoft | latent diffusion | factorised codec | high-fidelity controllable TTS |
| GPT-4o | OpenAI | native omni | audio ↔ audio | low-latency spoken assistant |
| Moshi | Kyutai | native full-duplex | audio ↔ audio | open full-duplex speech dialogue |

**The open axis is real here too:** EnCodec/DAC, Whisper, HuBERT, MusicGen, F5-TTS, and Moshi are all
open-weight and run on consumer hardware — you could run most of this stack on your RTX 4070. As with
image (2022) and video (2024), the open/proprietary gap in audio narrowed sharply through 2024–25.

---

## 9. Choosing a model — an application cheatsheet

<details>
<summary><b>Vocabulary for this section</b> — terms, abbreviations and every symbol in the formulas (click to expand)</summary>

**Abbreviations**

| Short | Stands for | Meaning |
|---|---|---|
| **TTS** | text-to-speech | synthesising speech from text |
| **STT / ASR** | speech-to-text / automatic speech recognition | transcribing speech |
| **S2S** | speech-to-speech | one model taking audio in and emitting audio out |
| **S2TT** | speech-to-text translation | spoken input, translated text output |
| **S2ST** | speech-to-speech translation | spoken input, spoken output in another language |
| **VC** | voice conversion | changing speaker identity while keeping the words and prosody |
| **SFX** | sound effects | non-speech, non-music audio generation |
| **TTFA / TTFB** | time to first audio / time to first byte | how long before the first audio chunk arrives — the metric for streaming |
| **e2e** | end-to-end | the whole pipeline's latency, not one stage's |
| **WER** | word error rate | ASR accuracy: insertions plus deletions plus substitutions, over reference length |
| **RTFx** | real-time factor (speed multiple) | how many seconds of audio are processed per second of compute |
| **DER** | diarization error rate | the error metric for "who spoke when" |
| **SSM** | state-space model | a non-attention sequence architecture, used by Cartesia for low latency |
| **SALM** | speech-augmented language model | an LLM decoder conditioned on speech encoder output |
| **MMAU** | massive multi-task audio understanding | an audio-reasoning benchmark |
| **SDR** | signal-to-distortion ratio | the quality metric for source separation, in decibels |
| **GPU / VRAM / CPU** | graphics processing unit / video RAM / central processing unit | the hardware, its memory, and the fallback processor |
| **GGUF / AWQ** | GPT-generated unified format / activation-aware weight quantization | a quantized weight file format, and a quantization method |
| **HF** | Hugging Face | the model hosting hub referenced throughout |
| **GA** | general availability | a product released beyond preview |
| **ctx** | context | the model's context-window length |
| **MIT / Apache-2.0** | permissive open-source licences | commercial use allowed |
| **CC-BY / CC-BY-NC** | Creative Commons attribution / attribution-non-commercial | the second forbids commercial use |
| **CPML** | Coqui Public Model License | XTTS-v2's non-commercial licence |
| **SOTA** | state of the art | the current best published result |
| **LADSPA** | Linux audio developer's simple plugin API | the plugin format for the live-microphone denoiser |
| **UVR** | Ultimate Vocal Remover | the community toolchain for music stem separation |
| **NeMo** | NVIDIA's speech/LLM toolkit | the framework NVIDIA's ASR and diarization models ship in |
| **EU / EN / ZH** | European Union / English / Chinese | language-coverage shorthand |
| **QA** | question answering | answering questions about the audio |

**Terms**

| Term | Definition |
|---|---|
| **Dominant axis** | the one constraint (quality, latency, cost, privacy, licence, languages) that actually decides the choice |
| **Hosted** | run by a vendor behind an API; you pay per unit and your audio leaves your infrastructure |
| **Self-host** | you run the weights on your own hardware; no per-call cost, full privacy |
| **Open-weight** | weights are downloadable — which says nothing on its own about commercial rights |
| **Non-commercial weights** | permissive code but weights you may not ship in a product |
| **Streaming TTS** | emitting audio chunks as they are synthesised rather than after the whole utterance |
| **Speaker diarization** | segmenting audio by who is speaking |
| **Voice conversion** | keeping the words and delivery, replacing the speaker identity |
| **Source separation** | splitting a mixture into its constituent sources |
| **Stem separation** | the music case: vocals, drums, bass and other |
| **Speech enhancement** | suppressing noise, echo or distortion in a recording |
| **Bandwidth extension** | reconstructing missing high frequencies to restore fidelity |
| **Quantization** | storing weights at lower precision so a model fits a smaller GPU |
| **Watermarking** | an inaudible marker embedded in generated audio to identify it as synthetic |
| **Code-switching** | changing language mid-utterance while keeping the same voice |
| **End-of-turn detection** | deciding when the user has finished speaking so the agent may respond |
| **Inpainting (music)** | regenerating a section inside an existing track |
| **Foley** | synthesised everyday sound effects for picture |
| **Leaderboard** | a public benchmark ranking — to be filtered by your task and language, not read as an overall score |
| **Consent gating** | requiring verified permission before cloning a voice |

</details>

Sections 1–8 explain *how* these models work. This section is the practical companion you asked for
— *which* one to reach for per use case (hosted/SOTA **and** best open-weight), and the trade-off that
decides it. It's written for the application side, not the internals.

> **⚠ Currency & health warning.** Snapshot as of **2026-07**, cross-checked against vendor pages,
> GitHub/HuggingFace, and public leaderboards. Audio moves fast — versions bump monthly, latency
> numbers shift, leaderboards churn. Treat version numbers and latency figures as "true when written,"
> and re-check the linked leaderboards before committing. Latency figures marked *(vendor)* are
> vendor-stated, not independent benchmarks. §9.15 lists what changed since a Jan-2026 view.
>
> **Self-host note.** "Consumer GPU" = a single 8–24 GB card; your **RTX 4070 (8 GB)** is at the low
> end — most *speech* models fit, but several *omni*/speech-to-speech/music models (Qwen3-Omni,
> Step-Audio-2, Moshi, YuE) want 16–24 GB (quantize or rent). CPU-only is flagged where viable.

### 9.1 How to choose — the six axes

Model selection is almost always a projection onto **one dominant axis**. Name yours first, then the
table picks itself.

**Table 2** — the six axes that decide an audio model choice, and who tends to win on each.

| Axis | The question | Who tends to win |
|---|---|---|
| **Quality** | Human/studio-grade output? | hosted (ElevenLabs, Suno) still edge open |
| **Latency** | Is a human waiting on the first audio chunk? | streaming specialist (Cartesia) or native speech-to-speech |
| **Cost** | High volume, thin margins? | self-hosted open weights amortize; hosted is per-second/char |
| **Privacy / control** | Can the audio leave your infra? (health, legal, on-device) | open weights, self-hosted |
| **Licensing** | Will you *sell* the output? | **check the license** — several strong open models are non-commercial |
| **Languages** | Which, and how many? | Whisper / Canary / Seamless / Gemini for breadth |

**The licensing trap (read this).** For a product that ships output commercially, license is a
*gating* filter, not a footnote. Commercial-safe (Apache/MIT): **Kokoro, Chatterbox, ACE-Step, YuE,
OpenVoice V2, Parakeet/Canary (CC-BY), Whisper (MIT)**. Non-commercial / restricted (prototypes &
internal only): **XTTS-v2 (CPML), Fish OpenAudio/S2-Pro, F5-TTS weights (CC-BY-NC via Emilia),
MusicGen/AudioGen weights (CC-BY-NC), SeamlessM4T v2 (CC-BY-NC), TangoFlux (research-only),
Audio-Flamingo/Audex (NVIDIA non-commercial), Suno/Udio lower tiers**. Always confirm on the model's
own page — several of the strongest open audio models are *code*-permissive but *weights*-non-commercial.

<!-- DIAGRAM:START -->
![Diagram 3](diagrams/03-audio-speech-and-tts-3.svg)

<details>
<summary>Diagram source (Mermaid)</summary>

```mermaid
flowchart TD
    start["What are you building?"] --> q1{"Human waiting\nin real time?"}
    q1 -- "Yes, conversational" --> s2s["Speech-to-speech\nGPT-Realtime / Gemini Live\n(open: Moshi, Step-Audio 2)"]
    q1 -- "Yes, just narration" --> stream["Streaming TTS\nCartesia Sonic / ElevenLabs Flash\n(open: Kokoro, Orpheus)"]
    q1 -- "No, batch/offline" --> q2{"Speech in or out?"}
    q2 -- "Out (synthesize)" --> q3{"Need a specific\ncloned voice?"}
    q3 -- "Yes" --> clone["Voice cloning\nElevenLabs / (open: Chatterbox, F5-TTS)"]
    q3 -- "No" --> tts["General TTS\nElevenLabs v3 / (open: Kokoro, VibeVoice)"]
    q2 -- "In (understand)" --> q4{"Just transcript,\nor reason over audio?"}
    q4 -- "Transcript" --> asr["ASR\nWhisper-v3-turbo / Parakeet / (hosted: Deepgram, AssemblyAI)"]
    q4 -- "Reasoning" --> allm["Audio LLM\nGemini / (open: Qwen3-Omni, Kimi-Audio)"]
    start --> q5{"Music or SFX?"}
    q5 -- "Music" --> music["Suno / (open: ACE-Step, YuE)"]
    q5 -- "Sound effects" --> sfx["ElevenLabs SFX / (open: Stable Audio Open)"]
```

</details>
<!-- DIAGRAM:END -->

### 9.2 Text-to-speech (narration, audiobooks, UI voice)

**Default hosted:** ElevenLabs v3 (quality). **Default open:** Kokoro-82M (tiny/fast/permissive);
VibeVoice for long-form multi-speaker.

**Table 3** — text-to-speech for narration, audiobooks and UI voice.

| Model | Type | Consumer GPU? | When to reach for it |
|---|---|---|---|
| **[ElevenLabs v3](https://elevenlabs.io/v3)** | hosted | — | Most expressive hosted TTS (inline emotion "audio tags"), 70+ langs; GA ~Feb 2026 (⚡ supersedes Multilingual v2). *Not* the realtime model — use Flash for that |
| **[Google Gemini 3.1 Flash TTS](https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-1-flash-tts/)** | hosted | — | Newest Google TTS, native multi-speaker dialogue, SynthID watermark (⚡ supersedes 2.5 TTS); [Chirp 3 HD](https://docs.cloud.google.com/text-to-speech/docs/chirp3-hd) for classic per-voice |
| **[OpenAI gpt-4o-mini-tts](https://developers.openai.com/api/docs/models/gpt-4o-mini-tts)** | hosted | — | Cheap, steerable ("instruct how to say it"), ~USD 0.015/min; already-on-OpenAI convenience |
| **[Azure Neural HD V3](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/high-definition-voices)** | hosted | — | Enterprise scale, 700+ voices |
| **[Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M)** | open (Apache-2.0) | ✅ (even CPU) | The open default — 82M, faster-than-real-time, 8 langs/54 voices; zero per-char cost |
| **[Microsoft VibeVoice-1.5B](https://github.com/microsoft/VibeVoice)** | open | ✅ | **Best open long-form multi-speaker** — up to ~90 min, 4 speakers; podcasts/dialogue audiobooks (Realtime-0.5B variant for streaming) |
| **[Chatterbox](https://github.com/resemble-ai/chatterbox)** | open (MIT) | ✅ | Quality + permissive license + cloning; Multilingual V3 = 23+ langs, watermark |
| **[Piper](https://github.com/rhasspy/piper)** | open (MIT) | ✅ (CPU/Pi) | Edge/offline; tiny, robotic-but-clear, many languages |
| **[Fish OpenAudio S1-mini / S2-Pro](https://huggingface.co/fishaudio/openaudio-s1-mini)** | open (⚠ non-commercial) | ✅ | Strong multilingual + emotion control (S2-Pro open-sourced Mar 2026); prototypes only |
| **[XTTS-v2](https://github.com/idiap/coqui-ai-TTS)** | open (⚠ non-commercial) | ✅ | Legacy 17-lang cloning (Coqui defunct; `idiap` community fork). Superseded for new work by Kokoro/Chatterbox/F5 |

### 9.3 Zero-shot voice cloning (mimic a voice from seconds of reference)

**Table 4** — zero-shot voice cloning from seconds of reference audio.

| Model | Type | When to reach for it |
|---|---|---|
| **[ElevenLabs](https://elevenlabs.io/v3)** (Instant / Professional) | hosted | Best fidelity **with consent/verification guardrails** — the responsible product default |
| **[Chatterbox Multilingual V3](https://github.com/resemble-ai/chatterbox)** | open (MIT) | Top open zero-shot clone **with a commercial license** + emotion-exaggeration control; watermarked |
| **[F5-TTS](https://github.com/SWivid/F5-TTS)** | open (⚠ weights CC-BY-NC) | Very realistic clone from 5–15 s (flow-matching DiT); code MIT but check weight license |
| **[OpenVoice V2](https://github.com/myshell-ai/OpenVoice)** | open (MIT) | Instant cross-lingual cloning with separate tone/style control; **commercial OK** |
| **[Hume EVI 3 / Octave](https://www.hume.ai/octave)** | hosted | Zero-shot voice capture (~30 s) with explicit prosodic/emotion steering |

> **Ethics/legal:** cloning is consent-gated and deepfake-adjacent. For any product, prefer a hosted
> API with identity verification, or enforce consent yourself. Compliance issue, not just a model
> choice. ("VALL-E" is research-only — no open production model; Microsoft's public work moved to
> VibeVoice + Azure HD voices.)

### 9.4 Real-time / streaming TTS (voice agents — latency is king)

Metric is **TTFA/TTFB** (time-to-first-audio), not total render time. Voice-agent budget ≈ 800 ms
end-to-end (STT + LLM + TTS); TTS should eat ≤ ~200 ms.

**Table 5** — real-time and streaming TTS for voice agents, with time-to-first-byte.

| Model | Type | TTFB *(vendor / bench)* | When to reach for it |
|---|---|---|---|
| **[Cartesia Sonic-3.5](https://www.cartesia.ai/sonic)** | hosted | ~40 ms Turbo / ~90 ms *(vendor)* | Latency leader (SSM [state-space model] architecture); default for interruptible agents (⚡ supersedes Sonic-3) |
| **[ElevenLabs Flash v2.5](https://elevenlabs.io/docs/overview/models)** | hosted | ~135 ms e2e *(vendor)* | ElevenLabs quality at near-real-time (English strong); use Flash/Turbo — **not v3** — for agents |
| **[Deepgram Aura-2](https://deepgram.com/learn/introducing-aura-2-enterprise-text-to-speech)** | hosted | sub-200 ms *(vendor)* | Tightest STT↔TTS loop if you're already on Deepgram Nova |
| **[Rime Arcana v3](https://rime.ai/resources/arcana-v3)** | hosted | ~120 ms on-prem *(vendor)* | Conversational (phone-agent) voices, code-switching keeps identity |
| **[Orpheus 3B](https://github.com/canopyai/Orpheus-TTS)** | open (Apache-2.0 base) | ~100–200 ms | **Best open low-latency streaming** — emotion tags + zero-shot cloning; needs ~12 GB |
| **[Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M)** | open | faster-than-real-time | Simplest self-hosted low-latency when you don't need cloning; fits 8 GB / CPU |

### 9.5 ASR / transcription (batch + streaming, multilingual)

> **"There is no catch-all model"** — the [Open ASR Leaderboard](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard)'s own conclusion. Pick by *accuracy vs speed vs languages*.

**Table 6** — ASR and transcription, batch and streaming, multilingual.

| Model | Type | Consumer GPU? | When to reach for it |
|---|---|---|---|
| **[Whisper large-v3-turbo](https://huggingface.co/openai/whisper-large-v3-turbo)** | open (MIT) | ✅ (8 GB) | **Multilingual default** — 99 langs, ~6× faster than large-v3; the safe general pick (no successor as of 2026-07) |
| **[NVIDIA Canary-Qwen-2.5B](https://huggingface.co/nvidia/canary-qwen-2.5b)** | open (CC-BY) | ✅ | **Top English accuracy** on the leaderboard (~5.6% WER [word error rate]); SALM decoder, higher latency |
| **[NVIDIA Parakeet-tdt-0.6b-v3](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3)** | open (CC-BY) | ✅ (~2 GB) | **Speed king** (RTFx in the thousands), now 25 EU languages; batch/long-form at scale |
| **[NVIDIA Canary-1b-v2](https://huggingface.co/nvidia/canary-1b-v2)** | open (CC-BY) | ✅ | Best multilingual-European open model (25 langs + EN↔ translation) |
| **[Deepgram Nova-3 + Flux](https://developers.deepgram.com/docs/models-languages-overview)** | hosted | — | Lowest-latency agent STT with built-in end-of-turn detection (Flux Multilingual GA Apr 2026) |
| **[AssemblyAI Universal-2 / Streaming / Slam-1](https://www.assemblyai.com/universal-2)** | hosted | — | Transcript intelligence + fine-tunable speech LLM; managed |
| **[ElevenLabs Scribe v2 / Realtime](https://elevenlabs.io/blog/introducing-scribe-v2)** | hosted | — | High-accuracy multilingual STT with diarization + word timestamps (~150 ms first partial) |

### 9.6 Speaker diarization ("who spoke when")

**Table 7** — speaker diarization — "who spoke when".

| Model | Type | When to reach for it |
|---|---|---|
| **[pyannote community-1](https://huggingface.co/pyannote/speaker-diarization-community-1)** | open (gated) | The open default (⚡ released Jul 2026 w/ pyannote.audio 4.0; beats 3.1 across metrics); free HF token |
| **[NVIDIA Sortformer (streaming v2.1)](https://huggingface.co/nvidia/diar_streaming_sortformer_4spk-v2.1)** | open | End-to-end, overlap-aware, real-time-capable (≤4 speakers); integrates with NeMo ASR |
| **[WhisperX](https://github.com/m-bain/whisperX)** | open | Transcript **+** speaker labels **+** word alignment in one pipeline — most popular self-host combo |
| **[pyannoteAI](https://www.pyannote.ai/) / AssemblyAI / Deepgram** | hosted | Managed diarization (best-DER hosted ~11% on VoxConverse); or bundled into their STT |

### 9.7 Conversational / speech-to-speech / full-duplex voice AI

Two architectures: **cascade** (STT → LLM → TTS) vs **native speech-to-speech** (one model, audio
in/out — lower latency, keeps tone/emotion). See §7.

**Table 8** — conversational, speech-to-speech and full-duplex models.

| Model | Type | Notes (2026-07) | When to reach for it |
|---|---|---|---|
| **[OpenAI GPT-Realtime-2.1](https://developers.openai.com/api/docs/models)** | hosted (S2S) | ~300–500 ms; tools, reasoning, 128k ctx; +Realtime-Translate & -Whisper siblings | Default production voice agent (⚡ supersedes gpt-4o-realtime) |
| **[Google Gemini Flash Native Audio](https://blog.google/products-and-platforms/products/gemini/gemini-audio-model-updates/)** | hosted (S2S) | ~380 ms, 90+ langs; strong function-calling | Broad language coverage / on GCP |
| **[Amazon Nova 2 Sonic](https://aws.amazon.com/bedrock/nova/)** | hosted (S2S) | On Bedrock; ~USD 0.27/hr input *(vendor)* | If you're on AWS |
| **[Moshi](https://github.com/kyutai-labs/moshi)** | open (S2S) | Full-duplex, ~200 ms, "inner monologue"; ~7B, wants 16–24 GB | The open full-duplex option; self-host/on-prem |
| **[Step-Audio 2 mini](https://github.com/stepfun-ai/Step-Audio2)** | open (Apache-2.0) | 8B, ~24 GB; #1 open on MMAU, beats GPT-4o-Audio on several | Self-hosted GPT-4o-class voice chat, no per-min fee |
| **[GLM-4-Voice](https://github.com/zai-org/GLM-4-Voice)** | open | ~9B, EN/ZH, low latency | Bilingual EN/ZH self-hosted voice |

> **Cascade still wins** when you need a *specific* LLM (your fine-tune), per-stage control, or cheaper
> components. **S2S wins** when latency + paralinguistics (emotion, interruption, backchannel) matter
> more than swappability.

### 9.8 Speech translation (S2T and S2S, many languages)

**Table 9** — speech translation, both speech-to-text and speech-to-speech.

| Model | Type | When to reach for it |
|---|---|---|
| **[Meta SeamlessM4T v2](https://huggingface.co/facebook/seamless-m4t-v2-large)** | open (⚠ CC-BY-NC) | Unified ASR + S2TT + S2ST, ~100 langs in / ~36 out; **Streaming** & **Expressive** variants. Still Meta's latest (no v3) — but **non-commercial** |
| **[NVIDIA Canary-1b-v2](https://huggingface.co/nvidia/canary-1b-v2)** | open (CC-BY) | **Commercial-safe** bidirectional S2TT across 25 EU languages (X↔En); the open pick if you're shipping |
| **[ElevenLabs Dubbing v2](https://elevenlabs.io/blog/introducing-dubbing-v2)** | hosted | S2ST **dubbing** — 90+ langs, clones + preserves the original speaker's voice/emotion/timing (May 2026) |
| **[Google Gemini 3.5 Live Translate](https://deepmind.google/models/model-cards/gemini-3-5-audio/)** | hosted | Real-time streaming S2ST inside a conversational agent (Jun 2026, 70+ langs) |
| **[Whisper](https://huggingface.co/openai/whisper-large-v3-turbo)** (translate mode) | open (MIT) | Quick any-language → **English-only** transcription-translation (S2TT, no S2ST) |

### 9.9 Audio understanding / audio LLMs (captioning, Q&A, classification, reasoning over sound)

**Table 10** — audio understanding and audio LLMs — captioning and question answering.

| Model | Type | Consumer GPU? | When to reach for it |
|---|---|---|---|
| **[Qwen3-Omni-30B-A3B](https://github.com/QwenLM/Qwen3-Omni)** | open (Apache-2.0) | needs 24 GB (quantized) | **Open SOTA** omni (audio+image+video in, text/speech out); confirmed official. (A "Qwen3.5-Omni" is *reported* Mar 2026 but the official repo is **unverified** — treat as rumor) |
| **[Qwen2.5-Omni-7B](https://huggingface.co/Qwen/Qwen2.5-Omni-7B)** | open | ✅ (4-bit) | The **consumer-GPU** omni pick — ASR, audio QA, captioning, real-time speech; GGUF/AWQ fit 8–16 GB |
| **[Kimi-Audio-7B](https://github.com/MoonshotAI/Kimi-Audio)** | open | ✅ | Unified audio foundation (ASR, QA, captioning, emotion, scene class., speech chat); 13M+ hrs |
| **[Audio Flamingo Next](https://huggingface.co/nvidia/audio-flamingo-next-hf)** | open (⚠ non-commercial) | 24 GB | Strongest open **long-audio reasoning** (30-min, temporal chain-of-thought); research only |
| **[Gemini 2.5/3.x audio](https://deepmind.google/models/gemini-audio/)** | hosted | — | Best hosted long-audio understanding (hour-long inputs) |

### 9.10 Text-to-music

> Post-lawsuit landscape: many teams self-host for **commercial rights + pipeline control**. Licenses
> bite hardest here — check carefully.

**Table 11** — text-to-music.

| Model | Type | Consumer GPU? | When to reach for it |
|---|---|---|---|
| **[Suno v5.5](https://suno.com/blog/v5-5)** | hosted | — | Best overall vocals + song structure; "sing in your own voice" (⚠ commercial by tier; label litigation ongoing) |
| **[ElevenLabs Music v2](https://elevenlabs.io/blog/introducing-music-v2)** | hosted | — | **Commercially cleared** (licensed training data) — the safe hosted pick if you sell output; long-form, section control, inpainting |
| **[Google Lyria 3 / RealTime](https://deepmind.google/models/lyria/)** | hosted | — | On Vertex/Gemini + Flow Music; ~3 min, multilingual vocals, SynthID; RealTime for interactive/streaming |
| **[Udio](https://www.udio.com)** | hosted | — | Realistic vocals — but ⚠ **downloads disabled since Oct 2025** (UMG settlement); verify before building on it |
| **[ACE-Step 1.5 / XL](https://github.com/ace-step/ACE-Step)** | open (MIT) | ✅ (6 GB turbo → 20 GB XL) | Open standout — MIT (commercial OK), competitive with Suno on SongEval; the self-host default |
| **[YuE 7B](https://github.com/multimodal-art-projection/YuE)** | open (Apache-2.0) | 24 GB (16 tight) | Full-length songs **with lyrics/vocals**, commercial-friendly |
| **[Stable Audio 3.0 (open variants)](https://stability.ai/news-updates/meet-stable-audio-3-the-model-family-built-for-artistic-experimentation-with-open-weight-models)** | open (Community ≤USD 1M) | ✅ | 3 of 4 variants open-weight; instrumental/sound-design, duration control. (⚠ **there is no "Stable Audio Open 2.0"** — this is the successor) |
| **[MusicGen (stereo)](https://github.com/facebookresearch/audiocraft)** | open (⚠ weights CC-BY-NC) | ✅ | Mature instrumental baseline — but **weights non-commercial** |

### 9.11 Text-to-sound-effects / general audio generation (foley, SFX, ambience)

**Table 12** — text-to-sound-effects and general audio generation — foley, SFX and ambience.

| Model | Type | When to reach for it |
|---|---|---|
| **[ElevenLabs Sound Effects v2](https://elevenlabs.io/docs/overview/capabilities/sound-effects)** | hosted | Quick 48 kHz SFX from a prompt, seamless looping, video-to-SFX; commercial on paid tiers |
| **[Stable Audio Open / 3.0 Small SFX](https://huggingface.co/stabilityai/stable-audio-open-1.0)** | open (Community ≤USD 1M) | **Commercial-friendly** self-hosted SFX/foley/loops with duration control; on-device variants |
| **[TangoFlux](https://huggingface.co/declare-lab/TangoFlux)** | open (⚠ non-commercial) | Fast research-grade text-to-audio (up to 30 s @ 44 kHz, ~6 GB); prototypes only |
| **[AudioGen (AudioCraft)](https://github.com/facebookresearch/audiocraft)** | open (⚠ weights CC-BY-NC) | Environmental audio / foley baseline — **weights non-commercial** |

### 9.12 Voice conversion (change *identity*, keep words/prosody)

Input is *audio*, not text (dubbing, singing, live voice-changing).

**Table 13** — voice conversion: change the identity, keep the words and prosody.

| Model | Type | When to reach for it |
|---|---|---|
| **[Seed-VC](https://github.com/Plachtaa/seed-vc)** | open | **Zero-shot** VC + singing, real-time (~300 ms) from a short reference; no per-voice training |
| **[RVC v2 / Applio](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI)** | open | Highest fidelity **if you train** (~10–20 min target audio); huge community, real-time; streamer standard |
| **[so-vits-svc](https://github.com/svc-develop-team/so-vits-svc)** | open | Long-standing **singing** voice conversion; per-voice training |

### 9.13 Speech enhancement / denoising / source separation

**Table 14** — speech enhancement, denoising and source separation.

| Task | Model | Type | When to reach for it |
|---|---|---|---|
| **Real-time voice denoise** | **[DeepFilterNet3](https://github.com/Rikorose/DeepFilterNet)** | open | Low-latency full-band (48 kHz) noise suppression; runs on CPU/edge; live-mic LADSPA plugin |
| | [Krisp](https://krisp.ai) / [NVIDIA Broadcast/Maxine](https://www.nvidia.com/en-us/geforce/broadcasting/broadcast-app/) | hosted | Turnkey real-time noise/echo suppression during live calls |
| **Speech restoration** | **[Resemble Enhance](https://github.com/resemble-ai/resemble-enhance)** | open | Denoise **+** restore distortion + bandwidth-extend to 44 kHz |
| | [Adobe Enhance Speech](https://podcast.adobe.com/enhance) / [ElevenLabs Voice Isolator](https://elevenlabs.io/docs/creative-platform/audio-tools/voice-isolator) | hosted | One-click cleanup of podcast/interview audio |
| **Enhance + separate (toolkit)** | **[ClearerVoice-Studio / MossFormer2](https://github.com/modelscope/ClearerVoice-Studio)** | open | One-stop: enhancement, speaker separation, super-res, target-speaker extraction |
| **Music stem separation** | **[Mel-Band / BS-RoFormer](https://arxiv.org/abs/2310.01809)** | open | Current best-quality stems (beats Demucs; ~12 dB SDR); used in UVR pipelines |
| | **[Demucs (htdemucs_ft)](https://github.com/facebookresearch/demucs)** | open | The standard, well-documented stem splitter (~9 dB SDR); easy to run (~3 GB) |

### 9.14 Rules of thumb (the cheatsheet in eight lines)

1. **Quality axis, won't self-host?** → ElevenLabs v3 (speech), Suno/ElevenLabs Music (music), Gemini (understanding).
2. **Latency axis (agents)?** → Cartesia Sonic (TTS) or GPT-Realtime/Gemini Live (speech-to-speech).
3. **Cost/privacy, will self-host?** → Kokoro (TTS), Whisper-turbo/Parakeet (ASR), Qwen2.5-Omni-7B (understanding), ACE-Step (music).
4. **Multilingual breadth?** → Whisper / Canary / Seamless / Gemini.
5. **Voice cloning in a product?** → hosted with consent guardrails; open = Chatterbox (commercial) / F5-TTS (non-commercial).
6. **Transcript + who-spoke-when, self-hosted?** → WhisperX (Whisper + pyannote in one).
7. **On an 8 GB RTX 4070?** → Kokoro, Whisper-turbo, Parakeet, ACE-Step, DeepFilterNet, Seed-VC, VibeVoice-1.5B fit; Qwen3-Omni-30B / Moshi / Step-Audio-2 / YuE want 16–24 GB (quantize or rent).
8. **Selling the output?** → resolve **license first**, model second. Apache/MIT (Kokoro, Chatterbox, ACE-Step, YuE, OpenVoice V2) are safe; XTTS-v2, Fish, F5 weights, MusicGen/AudioGen, SeamlessM4T, and Suno's lower tiers are not.

### 9.15 Successor flags — what changed since a Jan-2026 view

Useful if you have an older mental model. Verified this pass (2026-07):

- ElevenLabs → **v3** flagship (GA ~Feb 2026); realtime stays **Flash/Turbo v2.5**.
- Cartesia Sonic-3 → **Sonic-3.5** (GA May 2026). Google → **Gemini 3.1 Flash TTS** (Apr 2026) + native-audio Live API.
- OpenAI realtime → **GPT-Realtime-2.1 / -mini** (Jul 2026) + Translate/Whisper siblings. Amazon Nova Sonic → **Nova 2 Sonic** (Jun 2026).
- Deepgram Nova-3 → **Flux / Flux Multilingual** (GA Apr 2026); **no Nova-4**.
- NVIDIA ASR → **Canary-Qwen-2.5B** (English top) + **Parakeet-tdt-0.6b-v3** (25 EU langs). pyannote 3.1 → **community-1** (Jul 2026, v4.0); Sortformer → **streaming v2.1**. ElevenLabs STT (speech-to-text) → **Scribe v2 / v2 Realtime**.
- Music: **Suno v5.5** (Mar 2026); **ElevenLabs Music v2** (May 2026, commercial-cleared); **Google Lyria 3** + Flow Music; **ACE-Step 1.5/XL**; **Stable Audio 3.0** (⚠ *there is no "Stable Audio Open 2.0"*).
- Translation: **Gemini 3.5 Live Translate** (Jun 2026) + **ElevenLabs Dubbing v2**; **SeamlessM4T v2 has no successor** and is **non-commercial**.
- **Whisper**: still **large-v3-turbo** — no v4. **DeepFilterNet**: still **DFN3** — no v4.
- **Dead/legacy:** PlayHT (shut Dec 2025, acquired by Meta); Coqui/XTTS-v2 (company gone, `idiap` fork only); Parler-TTS & MetaVoice (stale); Udio downloads disabled (Oct 2025).
- **Unverified (treat as rumor):** Qwen3.5-Omni official audio model; AssemblyAI "Universal-3.5 Pro"; "HeartMuLa" music model; Microsoft "MAI-Transcribe-1"; any "Whisper v4."

### 9.16 Sources & leaderboards (2026-07)

Living references — re-check before committing:
[Open ASR Leaderboard](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard) ·
TTS: [Local AI Master](https://localaimaster.com/blog/best-local-tts-models), [DigitalOcean](https://www.digitalocean.com/community/tutorials/best-text-to-speech-models) ·
Streaming latency: [Gradium 2026](https://gradium.ai/content/tts-latency-benchmark-2026), [Cartesia vs ElevenLabs](https://burki.dev/blog/41-cartesia-vs-elevenlabs-tts) ·
ASR: [Northflank](https://northflank.com/blog/best-open-source-speech-to-text-stt-model-in-2026-benchmarks), [Gladia](https://www.gladia.io/blog/best-open-source-speech-to-text-models) ·
S2S: [OpenAI Realtime docs](https://developers.openai.com/api/docs/guides/realtime) ·
Diarization: [pyannote community-1](https://www.pyannote.ai/blog/community-1) ·
Music: [Spheron open-music 2026](https://www.spheron.network/blog/deploy-open-source-ai-music-generation-gpu-cloud-2026/) ·
Audio LLMs: [Qwen3-Omni](https://github.com/QwenLM/Qwen3-Omni) ·
Separation: [ClearerVoice-Studio](https://github.com/modelscope/ClearerVoice-Studio) ·
Translation/VC: [Meta Seamless](https://github.com/facebookresearch/seamless_communication), [Seed-VC](https://github.com/Plachtaa/seed-vc)

---

## 10. What to hold in your head

The conceptual arc, compressed:

1. **Representation is destiny.** Raw waveform (240k units / 10 s) is too long to model directly; the
   whole field is schemes to shorten it — spectrogram, mel-spectrogram, or (the modern winner) discrete
   codec tokens.
2. **The classic cascade** (text → acoustic model → mel → vocoder) names the sub-problems: **alignment**
   (Tacotron's soft attention → FastSpeech's structural durations) and **phase reconstruction** (why a
   learned vocoder exists; HiFi-GAN is the workhorse).
3. **Neural codecs + RVQ** turn audio into a short discrete sequence, which is the hinge of the field:
   it makes audio an LLM problem. RVQ's coarse-to-fine residual codebooks are the mechanism (and their
   $N$-streams-per-frame is the new wrinkle).
4. **The LLM-ification**: AudioLM's semantic-vs-acoustic split; VALL-E's zero-shot voice cloning as pure
   in-context learning; MusicGen's codebook-delay pattern.
5. **The flow-matching branch** (Voicebox, Matcha, F5-TTS) is §2's technique applied to speech —
   straight trajectories → few-step, deployable NAR (non-autoregressive) TTS; F5-TTS even reuses the DiT backbone.
6. **Recognition feeds generation**: Whisper's lesson is *scale of weak supervision, not architecture*;
   self-supervised models (wav2vec 2.0, HuBERT) both do ASR and emit the semantic tokens the generative
   side consumes.
7. **The frontier is native, full-duplex audio** (GPT-4o, Moshi): drop the ASR→text→TTS bottleneck to
   kill latency and preserve paralinguistics; model conversation as two concurrent token streams.

The open research questions that will drive the next 2–3 years:
> **Can a single model be a great listener *and* a great speaker *and* a great reasoner at once** —
> without the text bottleneck, at conversational latency, with long-range musical/narrative structure —
> and can the AR-token and flow-matching branches be unified the way image/video generation is
> converging on DiT + flow matching?

---

## 11. Key terms 中文对照 / 中文對照

| English | 大陆 (简体) | 台灣 (繁體) | Notes |
|---|---|---|---|
| Speech synthesis / TTS | 语音合成 | 語音合成 | script difference only |
| Speech recognition (ASR) | 语音识别 | 語音辨識 | ⚠ **识别** vs **辨識** — genuine word difference |
| Waveform | 波形 | 波形 | identical |
| Sampling rate | 采样率 | 取樣率 | ⚠ **采样** vs **取樣** — common split |
| Spectrogram | 声谱图 / 频谱图 | 聲譜圖 / 頻譜圖 | script difference; both 声/频 used |
| Mel-spectrogram | 梅尔频谱 | 梅爾頻譜 | transliteration 梅尔/梅爾 |
| Fourier transform | 傅里叶变换 | 傅立葉變換 | ⚠ **傅里叶** vs **傅立葉** (name) + 变换/變換 |
| Phase | 相位 | 相位 | identical |
| Vocoder | 声码器 | 聲碼器 | script difference only |
| Codec | 编解码器 | 編解碼器 | script difference only |
| Vector quantization | 矢量量化 / 向量量化 | 向量量化 | 大陆 also uses 矢量; 台灣 uses 向量 |
| Codebook | 码本 | 碼本 | script difference only |
| Token | 词元 / 标记 | 詞元 / 標記 | as in text; 令牌 also seen |
| Autoregressive | 自回归 | 自迴歸 | ⚠ **回归** vs **迴歸** — genuine difference |
| Voice cloning | 声音克隆 | 聲音複製 / 語音克隆 | ⚠ **克隆** vs **複製** — 台灣 often 複製 |
| Prosody | 韵律 | 韻律 | script difference only |
| Phoneme | 音素 | 音素 / 音位 | mostly identical |
| Full-duplex | 全双工 | 全雙工 | script difference only |
| Diffusion / flow matching | 扩散 / 流匹配 | 擴散 / 流匹配 | see §2 |
| Noise reduction / denoising | 降噪 / 噪声抑制 | 降噪 / 雜訊抑制 | ⚠ **噪声** vs **雜訊** (noise) — genuine difference |
| Reverberation | 混响 | 殘響 / 迴響 | ⚠ **混响** vs **殘響** — genuine difference |
| Source separation | 声源分离 | 音源分離 | ⚠ **声源** vs **音源** + 分离/分離 |
| Speaker diarization | 说话人分离 / 说话人日志 | 語者分段 / 語者分離 | ⚠ **说话人** vs **語者** — genuine difference |
| Beamforming | 波束成形 | 波束成形 / 波束賦形 | mostly identical |
| Target speaker extraction | 目标说话人提取 | 目標語者提取 | inherits 说话人 vs 語者 |

---

## 12. Applied (Q&A log)

*(Q&A session: 2026-07-15.)* No questions on the §1–§8 body — he confirmed it works **as a
high-level reference** ("I cannot remember them all, but it's a good doc for reference when needed"),
so the body went **untouched** (same signal as prior sections: the pitch was right). Instead he made
the load-bearing move of the session: **"for audio I'm more likely to work on the application side,"**
and redirected to **model *selection*** — asking for a SOTA-plus-open cheatsheet by use case (now
**§9**, web-researched to 2026-07 and merged in at his request, not kept standalone). He then brought
**three real use cases** and had me suggest toolkits. The threads:

**(12a) "Clean up a talk I recorded on my phone at a conference."** The teaching move was to **refuse
the one-tool framing and decompose the degradation into three** — (1) background noise, (2)
**reverberation** (the phone is metres from the speaker), (3) muffled/low-bandwidth (phone mic) — each
needing a *different* tool, and to flag that **the reverb is the ceiling** (plain denoisers don't touch
it). Toolkit: hosted one-click (**Adobe Enhance Speech**, **ElevenLabs Voice Isolator**) vs local on
the 4070 (**Resemble Enhance** = denoise + restore + bandwidth-extend; **DeepFilterNet3** = faithful
denoise with no resynthesis; **ClearerVoice-Studio** for super-res). Habits: pipeline order
(denoise/dereverb → bandwidth → normalize), **keep the original & A/B** (resynthesis models
hallucinate), and feed the *cleaned* audio to Whisper if a transcript is wanted.

**(12b) The cocktail-party problem** — real-time "focus on my circle" **and** offline "split the
circles into a document." Two keepers: **(i) competing speech ≠ noise** — the interfering circles have
*identical statistics* to the target, so denoisers are useless; this is a **separation/spatial**
problem. **(ii) A mono phone mic is near worst-case**, so **the dominant lever is spatial capture
(directionality / beamforming / get closer), not an algorithm** — humans solve this with two ears +
attention + lip-reading, all discarded by one omni mic. *Real-time:* hardware/positioning >
multichannel beamforming > **target-speaker extraction** (needs enrollment → impractical for a
multi-speaker circle) → streaming ASR; honest verdict = **no magic**, a conversation-boost earbud /
hearing-aid mode likely beats any phone pipeline; frontier = **target-speech-hearing earbuds** (UW
*Look Once to Hear*). *Offline:* (spatial) → **separation** (MossFormer2_SS / SepFormer) →
**diarization** (pyannote community-1 / Sortformer) → **ASR** (Whisper) → **an LLM groups speakers into
conversations by turn-taking + topic coherence** → document; verdict = 2–3 circles plausible, a packed
room **beyond reliable capability today**. Takeaway he took: **upgrade the capture (go multichannel);
don't lean on the algorithm.**

**(12c) "Generate mood/scene-matching music for a travel V-log."** The reusable pattern: **a two-step
pipeline — a VLM (Gemini) watches the footage and writes the *music brief* (genre / BPM /
instrumentation / mood), then a music model consumes it** (or you write the brief yourself). Generator
routes: hosted commercial-safe (**ElevenLabs Music v2**, licensed/cleared; **Suno v5.5** for quality,
w/ a Content-ID caveat; **Lyria 3**) vs free/local/you-own-it (**ACE-Step** MIT on the 4070; **Stable
Audio Open** for instrumental beds); **avoid MusicGen (non-commercial weights) & Udio (downloads
disabled)**. All-in-one editors (**CapCut / DaVinci Resolve**) bundle AI music + auto-beat-sync; the
pragmatic alternative is a royalty-free library. Tips: instrumental for BGM, section-match to scenes,
duck under narration, and resolve **publishing rights** since it'll be posted.

**Calibration (NEW durable signal — audio is an *application* domain for him, unlike LLMs).** Where he
is a peer-level paper-critiquing *builder* on LLM internals (v-series), on **audio he is an
application consumer/integrator**: he brings **concrete real-world use cases** and wants **ranked,
honest, *current* toolkits** — dominant-lever-first, with **explicit limits, licensing gates, and
self-host (RTX 4070) feasibility** — not mechanism internals. This fits his confirmed
practitioner/ops strength ([[arena-cold-start-concern]], LLM serving): he engages hardest when
abstract material meets a system he actually wants to build or use. **Teach-forward:** for the
non-text-model tracks aimed at *use*, lead with **(a) the dominant lever, (b) the honest ceiling, (c)
the license/rights gate**, and pair **SOTA (state of the art) hosted with best open**; flag currency because these churn
monthly. The value he acknowledged was exactly the *reframes* — noise-vs-competing-speech, spatial
capture as the lever, and the VLM (vision-language model)→brief→generate pattern — over enumerating models.
