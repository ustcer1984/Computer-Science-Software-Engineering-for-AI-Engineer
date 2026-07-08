# Instructions to AI agents

IMPORTANT: Do NOT edit this section.

* This repository is built with AI agents from multiple providers, e.g. Claude, Codex, Cursor, etc.
* In order to unify repository level rule / skill / memory sharing, all such docs must be created and maintained in `./agent-docs/`.
    * To Claude agents: put your files in `./agent-docs/` instead of `./.claude/`
    * To Cursor agents: put your files in `./agent-docs/` instead of `./.cursor/`
    * To other agents: obey similar rule
* You may add info in this file (AFTER this section) if they are important and all AI agents must always keep in context when working in this reposity.

---

# Important Info (to be created by AI agents)

## What this repo is
A personal **upskilling workspace** for the owner (an AI Engineer) to learn CS, software engineering,
and up-to-date AI. It is not a software product. Three parallel tracks:
- **Course track** — roadmap & progress in [`courses/plan.md`](../courses/plan.md); daily material under
  `courses/{NN}-{module}/{NN}-{chapter}/{NN}-{section}.md`. Rigorous, textbook-depth teaching.
- **Hobby track** — for-interest subjects under `hobby/` (first: Economy & Finance). Same rigorous
  study→Q&A→finalize flow as the course track, lighter sections.
- **Reading track** — daily curated readings under `upskill-readings/{yyyy}/{mm}/{dd}-{topic}.md`.
  **NOT a pre-teach of upcoming course chapters** — see the reading-track rule in
  [`authoring-conventions.md`](authoring-conventions.md) §6 for its "National Geographic / Discovery"
  function and the 1-career + 1-hobby balance rule.

## Rules every agent must keep in context
- **`prompts/` is human-authored and read-only.** Never edit any file in `prompts/`. If something is
  wrong or unclear, raise it in conversation; you may suggest edits but must not make them.
- **Keep the shared learner profile current.** [`learner-profile.md`](learner-profile.md) is the
  canonical record of the owner's skills/gaps/preferences. Read it for context; update it (not a
  private per-agent store) when a session reveals something new. **It is split by access pattern to
  stay readable in one load:** the main file holds *current state* (background, skill map, gaps,
  preferences, per-track progress) plus the latest ~2–3 session notes; the full append-only `vN`
  changelog lives in [`learner-profile-history.md`](learner-profile-history.md). **On each finalize:**
  (1) distil the durable signal into the main file's current-state sections, (2) prepend the new `vN`
  note to the TOP of the history file, (3) keep only the newest ~2–3 notes mirrored in the main file.
  This keeps the hot path roughly constant in size instead of growing every session.
- **Diagrams: author in Mermaid, commit rendered SVG.** Write ```` ```mermaid ```` blocks, then run
  `npm run diagrams` and commit the generated SVGs alongside the doc. Mermaid alone does not render on
  GitHub or most viewers. See [`diagrams.md`](diagrams.md) for the full convention and gotchas.
- **Follow the authoring conventions when writing material.** [`authoring-conventions.md`](authoring-conventions.md)
  records the learner's own rules for all tracks: use analogies (incl. the physics lens) sparingly and only
  where they earn their place; show real charts/plots (prefer a good existing figure, or draw the actual
  thing with dummy values) over prose; and always write math in LaTeX (`$...$`), never code backticks.
- **You may generate illustrations locally (ComfyUI).** Beyond charts/diagrams, this machine can generate
  raster illustrations via the `comfyui-media` skill — use for conceptual/metaphorical/scene-setting visuals
  only, never for quantitative plots or real-specific subjects, always with AI-generated provenance. See
  [`authoring-conventions.md`](authoring-conventions.md) §7 for the full precedence rule and hard limits.
