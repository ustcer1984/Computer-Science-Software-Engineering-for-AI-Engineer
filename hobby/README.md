# Hobby Courses

A side track for subjects studied **for interest**, separate from the career-development
course and reading tracks. Set up per [`prompts/001-hobby-setup.md`](../prompts/001-hobby-setup.md).

## How it works

- **One subject per subfolder.** Each subject keeps its own plan and material under
  `hobby/{subject}/`. (One plan per subject, not one master plan — the subjects are unrelated.)
- **A plan first.** When you name a new subject, a `plan.md` for it is created here; you steer it
  the same way as the main course plan (redirect any time).
- **Material on request, in small bites.** When you have time, you ask for the next hobby section.
  Material is generated as `hobby/{subject}/{NN}-{module}/{NN}-{section}.md`, sized for **1–2 hours**
  of study (lighter than a main-track section).
  - **Wording note (from the setup prompt):** the bare phrase *"prepare course material"* always
    means the **main track**. For this track, ask for *"hobby material"* (or name the subject).
- **Same session flow as the main track:** you study first → Q&A with the assistant → say
  *"finalize"*, at which point the section is rewritten to fit how you actually think and the
  subject's progress tracker is updated.
- **Readings:** hobby topics may also appear in the daily reading track
  (`upskill-readings/`), kept to roughly **25%** of readings (real-world case studies, latest-news
  analysis, or new concepts/theories).
- **Diagrams:** same repo convention — author in Mermaid, then `npm run diagrams` to commit rendered
  SVGs (the renderer now scans `hobby/` too). See [`agent-docs/diagrams.md`](../agent-docs/diagrams.md).

## Subjects

| Subject | Plan | Status |
|---|---|---|
| Economy & Finance | [`economy-and-finance/plan.md`](economy-and-finance/plan.md) | 🔵 E01 §1–§2 ✅ finalized; §3 🔵 prepared (study/finalize next) |
| Game Theory & Strategic Interaction | [`game-theory/plan.md`](game-theory/plan.md) | 🔵 plan ready, no sections yet |
