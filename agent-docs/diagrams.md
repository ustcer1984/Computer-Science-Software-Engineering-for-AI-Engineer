# Diagrams convention

**Diagrams are authored in Mermaid but committed as rendered SVG.** Mermaid is
client-side rendered — it only shows up in viewers that ship a Mermaid JS engine
(Cursor/VS Code with an extension). It does **not** render in most plain markdown
viewers, in many PDF/HTML exports, and is unreliable on GitHub. So we keep the
Mermaid text as the editable source of truth **and** commit a pre-rendered SVG that
displays everywhere.

## What a diagram looks like in a doc

After rendering, each diagram is wrapped like this (managed by the script — don't
hand-edit the markers):

```
<!-- DIAGRAM:START -->
![Diagram 1](diagrams/<doc-basename>-1.svg)

<details>
<summary>Diagram source (Mermaid)</summary>

​```mermaid
flowchart LR
  A --> B
​```

</details>
<!-- DIAGRAM:END -->
```

- The **SVG** is what readers see in any viewer (GitHub, raw markdown, PDF export).
- The **Mermaid source** stays beside it in a collapsed `<details>` — diffable and
  editable. It is the source of truth.
- SVGs live in a `diagrams/` folder next to the doc, named `<doc-basename>-<N>.svg`.

## Workflow for agents

1. **Adding/editing a diagram:** just write or edit a ```` ```mermaid ```` block in
   the doc (a bare block, or the one inside an existing `<details>`). Don't write the
   `![...](.svg)` or the `DIAGRAM:START/END` markers by hand.
2. **Render:** run `npm run diagrams` (renders every doc under `courses/` and
   `upskill-readings/`) or target one file: `node scripts/render-diagrams.mjs <file.md>`.
   This is **idempotent** — it re-renders from the Mermaid source and rewrites the
   wrappers, so it's safe to run repeatedly.
3. **Commit both** the updated `.md` and the generated `.svg` files.
4. **Verify (optional / pre-commit):** `npm run diagrams:check` confirms every block
   is wrapped and every referenced SVG exists, without writing anything.

## Hard constraints (why the config is the way it is)

- **No `<foreignObject>` in output.** GitHub's markdown sanitizer strips it, leaving a
  blank image. `scripts/mermaid.config.json` sets `htmlLabels: false` to avoid it, and
  the render script *fails* if any SVG still contains `<foreignObject>`.
- **Mermaid must actually parse.** Mermaid's strict parser rejects some things lenient
  in-editor previews accept. Known gotchas already hit in this repo:
  - Gantt: `call` is a reserved keyword — don't name a task `call X` (use `fetch X` etc.).
  - quadrantChart: data points need bracketed coords — `"Label": [0.2, 0.8]`, not `0.2 0.8`.
- **Tooling:** `@mermaid-js/mermaid-cli` (`mmdc`) via Puppeteer. The render script reuses
  the system Chrome (`/usr/bin/google-chrome-stable` etc.) so the heavy Chromium download
  is skipped on `npm install`. Set `PUPPETEER_EXECUTABLE_PATH` to override the browser.

## Files

- `scripts/render-diagrams.mjs` — the renderer/rewriter.
- `scripts/mermaid.config.json` — Mermaid config (`htmlLabels: false`).
- `scripts/puppeteer.config.json` — Puppeteer args (`--no-sandbox`).
- `package.json` — `diagrams` and `diagrams:check` npm scripts.
