# Diagrams convention

> **Scope:** project-level — applies to **all tracks** (course, reading, hobby, and any future track).

## The principle (this is the part that matters)

**A diagram must display correctly in any plain viewer — GitHub, raw markdown, PDF/HTML
export — so always commit a rendered image (SVG/PNG), not just source that needs a live
engine to render.** That's the only hard requirement. *How* you produce the image is open.

## You choose the tool — Mermaid is allowed, not mandatory

- **Mermaid is fine** (and there's ready-made tooling for it below), but you are **not
  obliged to use Mermaid only.**
- **Other tools are welcome** — e.g. **draw.io / diagrams.net**, Excalidraw, Graphviz,
  PlantUML, matplotlib, a hand-built SVG, etc. Pick whatever renders the idea clearest.
- **You may also use an existing online diagram or image directly** — link or embed a
  suitable public image/diagram instead of authoring one, when that's the best fit.
  (For images that live remotely, prefer committing a local copy so the doc still renders
  if the source disappears; keep the original URL in a caption or comment for provenance.)
- **For non-diagram *illustrations* (conceptual/metaphorical/scene-setting art), you can also
  generate images locally** via the `comfyui-media` skill — but that's governed by its own rule:
  see [`authoring-conventions.md`](authoring-conventions.md) §7 (precedence, hard limits, provenance).
  This `diagrams.md` doc stays about *structural* diagrams and *data* figures.

Whatever the source, keep an **editable source of truth** beside the rendered image where
practical (the Mermaid/PlantUML/draw.io source in a collapsed `<details>` or a sibling
file), so the diagram stays diffable and editable.

## ALWAYS verify the rendered image visually

**After generating any diagram — Mermaid or otherwise — open the produced image and look
at it.** Render tools regularly emit images that *parse* fine but *look* wrong. Check for:

- **overlap** — nodes/edges/labels colliding or sitting on top of each other;
- **incorrect position / layout** — arrows crossing badly, clusters in the wrong place,
  truncated or cut-off content;
- **font too small / unreadable** — text that won't be legible at normal viewing size;
- **missing or blank elements** — e.g. a stripped `<foreignObject>` leaving a blank box.

Use the Read tool on the SVG/PNG (it renders images visually) to inspect it; if it looks
wrong, fix the source (simplify the graph, shorten labels, bump font size, switch tools)
and re-render until it's clean. **Do not commit a diagram you haven't looked at.**

---

## Mermaid path (one recommended option, with tooling)

**When you choose Mermaid: author in Mermaid but commit the rendered SVG.** Mermaid is
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
3. **Look at the rendered SVG** (Read tool) and confirm it's clean — see "ALWAYS verify
   the rendered image visually" above. This step is **required**, not optional.
4. **Commit both** the updated `.md` and the generated `.svg` files.
5. **Structural check (optional / pre-commit):** `npm run diagrams:check` confirms every
   block is wrapped and every referenced SVG exists, without writing anything. Note this
   is only a *structural* check — it does **not** catch overlap/layout/font problems, which
   is why step 3 (looking at the image) is mandatory.

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
