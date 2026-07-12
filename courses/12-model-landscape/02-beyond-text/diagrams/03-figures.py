#!/usr/bin/env python3
"""Figures for M12 Ch2 §3 — Audio, Speech & TTS.

Editable source of truth for the committed SVGs (see agent-docs/diagrams.md).
Run with the project venv:

    .venv/bin/python courses/12-model-landscape/02-beyond-text/diagrams/03-figures.py

Outputs 03-audio-speech-and-tts-figN.svg into this folder.

No scipy/librosa in the project venv — STFT and the mel filterbank are implemented
in pure numpy on purpose (they are short and the point is pedagogical clarity).
"""
import os
import numpy as np
import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

OUT = os.path.dirname(os.path.abspath(__file__))
BASE = "03-audio-speech-and-tts"

plt.rcParams.update({
    "font.size": 12,
    "axes.titlesize": 13,
    "axes.labelsize": 12,
    "svg.fonttype": "none",
    "figure.dpi": 100,
})


def save(fig, n):
    path = os.path.join(OUT, f"{BASE}-fig{n}.svg")
    fig.savefig(path, format="svg", bbox_inches="tight")
    plt.close(fig)
    print("wrote", path)


# ---------------------------------------------------------------------------
# DSP helpers (pure numpy) — a short STFT and a mel filterbank.
# ---------------------------------------------------------------------------
def stft_mag(x, n_fft, hop):
    """Return magnitude STFT, shape (n_freq, n_frames)."""
    win = np.hanning(n_fft)
    starts = range(0, len(x) - n_fft, hop)
    cols = []
    for s in starts:
        seg = x[s:s + n_fft] * win
        cols.append(np.abs(np.fft.rfft(seg)))
    return np.array(cols).T  # (n_freq, n_frames)


def hz_to_mel(f):
    return 2595.0 * np.log10(1.0 + f / 700.0)


def mel_to_hz(m):
    return 700.0 * (10.0 ** (m / 2595.0) - 1.0)


def mel_filterbank(n_mels, n_fft, sr, fmin=0.0, fmax=None):
    """Triangular mel filterbank, shape (n_mels, n_fft//2 + 1)."""
    if fmax is None:
        fmax = sr / 2.0
    n_freq = n_fft // 2 + 1
    fft_freqs = np.linspace(0, sr / 2.0, n_freq)
    mel_pts = np.linspace(hz_to_mel(fmin), hz_to_mel(fmax), n_mels + 2)
    hz_pts = mel_to_hz(mel_pts)
    fb = np.zeros((n_mels, n_freq))
    for m in range(1, n_mels + 1):
        lo, ce, hi = hz_pts[m - 1], hz_pts[m], hz_pts[m + 1]
        left = (fft_freqs - lo) / max(ce - lo, 1e-9)
        right = (hi - fft_freqs) / max(hi - ce, 1e-9)
        fb[m - 1] = np.clip(np.minimum(left, right), 0, None)
    return fb, hz_pts[1:-1]


def synth_utterance(sr):
    """A synthetic speech-like signal: three voiced 'syllables' with a pitch
    glide and harmonic + formant structure, plus one broadband fricative burst.
    Recognisable as speech-shaped without needing a real recording."""
    dur = 1.35
    t = np.arange(int(dur * sr)) / sr
    x = np.zeros_like(t)

    def voiced(center, width, f0_start, f0_end, formants):
        env = np.exp(-0.5 * ((t - center) / width) ** 2)
        # instantaneous f0 glide over the syllable
        f0 = f0_start + (f0_end - f0_start) * np.clip((t - (center - width)) / (2 * width), 0, 1)
        phase = 2 * np.pi * np.cumsum(f0) / sr
        seg = np.zeros_like(t)
        for k in range(1, 22):          # harmonics of f0
            fk = k * f0
            # formant emphasis: boost harmonics near each formant frequency
            gain = 1.0 / k
            for Ff, Bw in formants:
                gain += 1.4 * np.exp(-0.5 * ((fk - Ff) / Bw) ** 2)
            seg += gain * np.sin(k * phase)
        return env * seg

    # three syllables with different pitch and formant patterns
    x += voiced(0.22, 0.09, 130, 110, [(650, 120), (1100, 160), (2600, 220)])
    x += voiced(0.72, 0.08, 150, 190, [(400, 100), (1900, 200), (2700, 220)])
    x += voiced(1.12, 0.07, 120, 100, [(550, 120), (900, 150), (2500, 240)])

    # a fricative burst (broadband noise) between syllables 1 and 2 ("s"-like)
    rng = np.random.default_rng(7)
    fric_env = np.exp(-0.5 * ((t - 0.47) / 0.035) ** 2)
    noise = rng.standard_normal(len(t))
    # high-pass-ish: emphasise the derivative to push energy up in frequency
    noise = np.diff(noise, prepend=noise[0])
    x += 0.6 * fric_env * noise

    x /= np.max(np.abs(x)) + 1e-9
    return t, x


# ---------------------------------------------------------------------------
# Fig 1 — one signal, three representations.
#   (a) raw waveform (amplitude vs time) — what a microphone captures
#   (b) linear-frequency spectrogram (STFT magnitude, dB)
#   (c) mel spectrogram — perceptually warped, the standard model input
# ---------------------------------------------------------------------------
def fig1():
    sr = 16000
    t, x = synth_utterance(sr)

    n_fft, hop, n_mels = 512, 128, 64
    S = stft_mag(x, n_fft, hop)            # (n_freq, n_frames)
    power = S ** 2
    fb, mel_hz = mel_filterbank(n_mels, n_fft, sr, fmin=0, fmax=sr / 2)
    mel = fb @ power                        # (n_mels, n_frames)

    S_db = 20 * np.log10(S / (S.max() + 1e-9) + 1e-6)
    mel_db = 10 * np.log10(mel / (mel.max() + 1e-9) + 1e-6)

    n_frames = S.shape[1]
    times = np.linspace(0, t[-1], n_frames)
    freqs = np.linspace(0, sr / 2, S.shape[0])

    fig, axes = plt.subplots(3, 1, figsize=(9.6, 8.4), sharex=True,
                             gridspec_kw={"height_ratios": [1.0, 1.4, 1.4]})
    axw, axs, axm = axes

    # (a) waveform
    axw.plot(t, x, lw=0.5, color="#1f77b4")
    axw.set_ylabel("Amplitude")
    axw.set_title(f"(a) Raw waveform — {sr//1000} kHz × {t[-1]:.2f} s "
                  f"= {len(x):,} samples the model would have to model directly")
    axw.set_xlim(0, t[-1])
    axw.set_yticks([-1, 0, 1])
    axw.spines[["top", "right"]].set_visible(False)

    # (b) linear spectrogram
    im1 = axs.pcolormesh(times, freqs / 1000, S_db, shading="auto",
                         cmap="magma", vmin=-60, vmax=0)
    axs.set_ylabel("Frequency (kHz)")
    axs.set_title("(b) Linear spectrogram — STFT magnitude (dB): "
                  "time × frequency grid; harmonics + a fricative burst visible")
    fig.colorbar(im1, ax=axs, pad=0.01, label="dB")

    # (c) mel spectrogram
    im2 = axm.pcolormesh(times, np.arange(n_mels), mel_db, shading="auto",
                         cmap="magma", vmin=-60, vmax=0)
    axm.set_ylabel("Mel band")
    axm.set_xlabel("Time (s)")
    axm.set_title("(c) Mel spectrogram — frequency axis warped to perception "
                  "(low freqs stretched, highs compressed)")
    # secondary y labels: Hz at a few mel bands
    ticks = [0, 15, 31, 47, 63]
    axm.set_yticks(ticks)
    axm.set_yticklabels([f"{int(mel_hz[i])}" for i in ticks])
    axm.set_ylabel("≈ Hz (mel-spaced)")
    fig.colorbar(im2, ax=axm, pad=0.01, label="dB")

    fig.suptitle("A short utterance, three representations — "
                 "the choice of representation defines the model family",
                 fontsize=13.5, y=0.995)
    fig.tight_layout()
    save(fig, 1)


# ---------------------------------------------------------------------------
# Fig 2 — the sequence-length problem: tokens a transformer must model for
# 10 s of audio, across representations (log scale). This is why neural audio
# codecs (discrete tokens) unlocked the LLM-style approach.
# ---------------------------------------------------------------------------
def fig2():
    secs = 10.0
    # (label, count, colour, note)
    items = [
        ("Raw waveform\n24 kHz PCM", int(24000 * secs), "#7f0000",
         "240,000 samples\n(hopeless for attention)"),
        ("Mel frames\n~86 Hz (hop 256)", int(86 * secs), "#d62728",
         "~860 continuous\nvectors (not tokens)"),
        ("Neural codec RVQ\n75 Hz × 8 books", int(75 * secs * 8), "#1f77b4",
         "6,000 discrete\ntokens (EnCodec-like)"),
        ("Codec, 1 book\n75 Hz", int(75 * secs), "#2ca02c",
         "750 tokens\n(1 RVQ level)"),
        ("Semantic tokens\n~50 Hz (HuBERT)", int(50 * secs), "#9467bd",
         "500 discrete\ntokens"),
    ]
    labels = [it[0] for it in items]
    counts = [it[1] for it in items]
    colors = [it[2] for it in items]
    notes = [it[3] for it in items]

    fig, ax = plt.subplots(figsize=(10.2, 5.6))
    xs = np.arange(len(items))
    bars = ax.bar(xs, counts, color=colors, width=0.62,
                  edgecolor="white", linewidth=0.8, zorder=3)

    ax.set_yscale("log")
    ax.set_ylim(100, 500000)
    ax.set_ylabel("Units to model for 10 s of audio (log scale)")
    ax.set_xticks(xs)
    ax.set_xticklabels(labels, fontsize=9.5)
    ax.set_title("Why raw audio is not a sequence you can attend over — "
                 "and how codecs fix it")
    ax.grid(axis="y", ls=":", lw=0.7, color="0.85", zorder=0)
    ax.spines[["top", "right"]].set_visible(False)

    for x, c, note in zip(xs, counts, notes):
        ax.text(x, c * 1.35, f"{c:,}", ha="center", va="bottom",
                fontsize=9.5, fontweight="bold")
        ax.text(x, c * 0.55, note, ha="center", va="top",
                fontsize=7.6, color="white", zorder=4)

    # annotate the ~300x drop from waveform to codec frames
    ax.annotate("", xy=(3, 750 * 1.05), xytext=(0, 240000 * 0.95),
                arrowprops=dict(arrowstyle="->", color="0.3", lw=1.4,
                                connectionstyle="arc3,rad=-0.25"))
    ax.text(1.55, 30000, "≈ 300× fewer\ntimesteps",
            fontsize=9.5, color="0.25", ha="center",
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="0.7", lw=0.8))

    fig.tight_layout()
    save(fig, 2)


if __name__ == "__main__":
    fig1()
    fig2()
    print("done")
