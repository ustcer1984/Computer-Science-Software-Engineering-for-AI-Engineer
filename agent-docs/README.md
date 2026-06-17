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
and up-to-date AI. It is not a software product. Two parallel tracks:
- **Course track** — roadmap & progress in [`courses/plan.md`](../courses/plan.md); daily material under
  `courses/{NN}-{module}/{NN}-{chapter}/{NN}-{section}.md`.
- **Reading track** — daily curated readings under `upskill-readings/{yyyy}/{mm}/{dd}-{topic}.md`.

## Rules every agent must keep in context
- **`prompts/` is human-authored and read-only.** Never edit any file in `prompts/`. If something is
  wrong or unclear, raise it in conversation; you may suggest edits but must not make them.
- **Keep the shared learner profile current.** [`learner-profile.md`](learner-profile.md) is the
  canonical record of the owner's skills/gaps/preferences. Read it for context; update it (not a
  private per-agent store) when a session reveals something new.
- **Diagrams: author in Mermaid, commit rendered SVG.** Write ```` ```mermaid ```` blocks, then run
  `npm run diagrams` and commit the generated SVGs alongside the doc. Mermaid alone does not render on
  GitHub or most viewers. See [`diagrams.md`](diagrams.md) for the full convention and gotchas.
- **Follow the authoring conventions when writing material.** [`authoring-conventions.md`](authoring-conventions.md)
  records the learner's own rules for all tracks: use analogies (incl. the physics lens) sparingly and only
  where they earn their place; show real charts/plots (prefer a good existing figure, or draw the actual
  thing with dummy values) over prose; and always write math in LaTeX (`$...$`), never code backticks.
