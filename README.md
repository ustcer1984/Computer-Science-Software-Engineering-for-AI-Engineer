# Computer-Science-Software-Engineering-for-AI-Engineer

An AI Engineer's structured, AI-assisted learning journey into computer science, software
engineering, and up-to-date AI — going from just-in-time, vibe-coded knowledge to durable
first-principles understanding.

## Goals

- Work as a full-stack developer **and architect**.
- Understand all kinds of models (LLM, image, multimodal, audio) and apply them in agentic frameworks.
- Build deep CS, software-engineering, cloud, and security foundations.
- Stay current on the latest technologies and tool stacks.

## How it works — two parallel tracks

Worked through with an AI assistant, ~2–3 hrs/day.

### 1. Course track (`courses/`)
A systematic, foundations-first curriculum.
- The roadmap, module/chapter breakdown, and progress tracker live in
  [`courses/plan.md`](courses/plan.md).
- Daily material is generated on request and saved as
  `courses/{NN}-{module}/{NN}-{chapter}/{NN}-{section}.md`.
- Each session: request material → study & Q&A → "finalize", at which point the assistant rewrites
  the section to fit the learner and updates progress.

### 2. Reading track (`upskill-readings/`)
Daily curated articles/papers/videos to stay current and broaden exposure.
- Saved as `upskill-readings/{yyyy}/{mm}/{dd}-{topic}.md` (link + short summary per item).
- Up to ~25% of readings may cover hobby subjects (see below).

### Hobby track (`hobby/`)
A side track for subjects studied purely for interest, one subfolder per subject, each with its own
plan. Same study → Q&A → finalize flow as the course track, but material is sized for 1–2 hours.
See [`hobby/README.md`](hobby/README.md). First subject: **Economy & Finance**.

## Repository layout

| Path | Purpose |
|---|---|
| [`courses/`](courses/) | Course track — `plan.md` plus generated material. |
| [`upskill-readings/`](upskill-readings/) | Daily reading track, organised by date. |
| [`hobby/`](hobby/) | Hobby track — for-interest subjects, one subfolder & plan per subject. |
| [`prompts/`](prompts/) | Human-authored instructions to AI agents. **Read-only — agents must not edit.** |
| [`agent-docs/`](agent-docs/) | Shared, cross-agent docs (rules + the canonical learner profile). |
| `CLAUDE.md` | Entry-point guidance for Claude. |

## Working with AI agents

This repo is worked on by AI agents from multiple providers (Claude, Codex, Cursor, …). To keep
rules, memory, and the learner profile shared across them, all such docs live in
[`agent-docs/`](agent-docs/) rather than provider-specific folders — start with
[`agent-docs/README.md`](agent-docs/README.md).
