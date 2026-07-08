# Authoring conventions for course material

> **Scope:** project-level — applies to **all tracks** (course, reading, hobby, and any future track).
> These are the learner's own instructions on how material should be written. Keep them in context
> whenever you prepare or finalize a section/reading. Established 2026-06-17 from learner feedback on
> Econ E01 §2; extended 2026-06-18 (rule 3) from feedback on M04 Ch2 §1; extended 2026-06-29 (rule 4: bare
> sub/superscripts, `$$`-in-lists, emphasis-in-`\text{}` traps, and the two-level Playwright verification)
> from GitHub math-render bugs in Econ E02 §2 and §3; extended 2026-07-02 (rule 4: the `($…$)` open-paren
> trap and the math-inside-`*emphasis*` trap) from two more Econ E02 §3/§11 render bugs; extended 2026-07-08
> (rule 7: locally-generated ComfyUI illustrations); extended 2026-07-09 (rule 4: the opening-`$`-glued-to-a-
> quote-or-hyphen trap) from three shipped Econ render bugs found during a track-wide illustration pass.

## 1. Use analogies (incl. the "physics lens") sparingly — only where they earn their place

The learner has a physics/ML background, and tying a hard concept to something he already owns is a
genuine teaching lever. **But do not reach for it everywhere.** Over-applying it is noise, not signal.

- Use an analogy when it makes a *genuinely difficult* idea click. Skip it when the plain explanation
  is already clear — a dedicated "Physics lens" callout on an easy point is filler.
- **Do not assume deep, classroom-specific machinery is still fresh.** His words: "not every physics PhD
  can still remember Lagrange analysis after leaving the classroom for long." Deriving an everyday result
  (e.g. supply/demand) through heavy formalism (full Lagrangian/KKT) is **overkill**. Name the connection
  if it illuminates ("the price is a shadow price"), but don't make understanding the basics *depend* on
  recalling advanced tools.
- Rule of thumb: the analogy is a *bridge for the hard parts*, not a *lens bolted onto every paragraph*.

## 2. Show charts/plots — and prefer a real figure over prose

If a concept has a standard visual (a curve, a plot, a labelled diagram), **show it** rather than
describing it in words. "Why explain demand and supply curves in text only when you can show the plot?"

- **Prefer a good existing figure.** A well-received public image/figure usually beats one built from
  scratch. Embed or adapt it (commit a local copy + keep the source URL for provenance — see
  [`diagrams.md`](diagrams.md)).
- **If you build it yourself, draw the actual thing.** For a quantitative relationship, assign dummy
  values and plot the real curves (e.g. matplotlib → committed PNG/SVG), not just a conceptual box-and-
  arrow flowchart. A schematic flowchart is fine for *structure*; a plot is better for *a function or a
  relationship*.
- All the [`diagrams.md`](diagrams.md) rules still apply: commit a rendered image (never source-only), and
  **look at the rendered image** before committing.

## 3. Teach comprehensively; ground examples in the real world, not the learner's repos

*(Established 2026-06-18 from learner feedback on M04 Ch2 §1.)* Two reference repos
(`aquarium-main`, `arena-concept-experiment`) were shared **once, to calibrate his level** so material
isn't pitched too low. They are **not the goal of the course.** Do not write as if the point of a
section is to improve those repos.

- **Be comprehensive.** The CS/SWE/AI tracks should cover their subjects properly and durably, the way
  a good course or textbook would — not as a thin wrapper around "fix file X." Cover the concept fully
  even where it doesn't touch his code.
- **Don't over-cite the repos.** A repo reference is fine occasionally when it genuinely illuminates,
  but stop sprinkling `process_no_waiting.py` / `ArenaPage.jsx` / line counts through every section.
- **A code snippet he shows in Q&A is usually a question, not an endorsement.** He often pastes code to
  *ask your opinion*; it does **not** mean he wrote it, uses it, or thinks it's good. Never assume his
  examples are his production code or label them "your bad code." Critique the design on its merits.
- **Prefer real-world canonical good/bad examples, and teach failure modes he hasn't met.** His words:
  "Let me know the failure mode I have not encountered before." Reach for well-known industry
  exemplars — deep modules (Unix file API, Go `io.Reader`, `requests`), shallow/leaky ones (Java stream
  wrappers, ORM N+1, TCP-over-IP), over-decomposition casualties (Segment, Prime Video monolith
  reversals, `FizzBuzzEnterpriseEdition`) — over invented or repo-specific ones. They generalize and
  they stretch him.

## 4. Always write math in LaTeX

Every mathematical expression, formula, equation, variable, sub/superscript, or operator goes in
**LaTeX math** so it renders correctly and reads cleanly — **not** in inline code backticks or plain text.

- Inline: `$Q_d(P)$`, `$P^*$`, `$MB = MC$`, `$Z'(P^*) < 0$`.
- Display (for anything you want set off): `$$dP/dt \propto Z(P) = Q_d(P) - Q_s(P)$$`.
- Use proper symbols: `\propto \approx \geq \leq \neq \partial \alpha \leftarrow \cdot`, subscripts
  `Q_d`, superscripts `P^*`. Don't leave `>=`, `P*`, `Q_d` in code font or raw text.
- GitHub-flavoured markdown renders `$...$` and `$$...$$`, **but its math parser is more fragile than
  Cursor's** — math that looks perfect in the editor can break on github.com. These traps have actually
  bitten us; verify the *rendered GitHub page* (see below), don't trust the editor preview:
  - **Never use a backslash followed by ASCII punctuation inside math** — `\,` `\;` `\:` `\!` `\%`.
    CommonMark strips the backslash *before* the math reaches the renderer, so `\;`→`;`, `\,`→`,` (stray
    semicolons/commas appear in the output), and `\%`→`%`, which MathJax treats as a **comment** that
    silently eats the rest of the expression (this is how a whole `$$…$$` fraction vanished). Use a
    **letter-named** equivalent, which survives because the backslash is followed by a letter — **but
    only the ones GitHub's MathJax actually ships.** Verified on github.com (2026-06-21, M12 Ch2 §2):
    **`\thinspace` and `\quad`/`\qquad` work** (they are base-TeX primitives); **`\thickspace` and
    `\medspace` do NOT** — they are amsmath macros GitHub's MathJax build doesn't load, so they render
    as the *literal text* `\thickspace` in the equation. So: use **`\thinspace`** for a small gap and
    **`\quad`** for a larger separator; do **not** use `\thickspace`/`\medspace`. And **avoid `\%`
    entirely** — reword to a fractional-change ratio like `\frac{\Delta Q / Q}{\Delta P / P}` (which
    *is* the percentage-change ratio) instead of writing `\%\Delta Q`.
  - **Never put a literal `*` inside math** (`$P^*$`, `$Q^*$`). GitHub runs Markdown `*emphasis*` parsing
    *over* the `$...$` content, so the `*` is eaten (you get `$P^$`) and — worse — it pairs with the next
    real `*emphasis*` asterisk in the paragraph, turning text italic and corrupting *every other* `$...$`
    span between them (one stray `*` silently broke `$MB$`, `$MC$`, … on the same line). Write the
    superscript star as `\ast`: `$P^\ast$`, `$Q^\ast$`.
  - **Always brace subscripts/superscripts — never a *bare* `_` or `^` in math** (`$P_t$`, `$x_i$`,
    `$\pi_t$`). Same mechanism as the `*` trap: GitHub runs `_emphasis_` parsing over `$...$`, so a bare `_t`
    is read as an underscore-emphasis marker — it pairs with the next `_` in the expression (or paragraph),
    *italicizes the LaTeX as literal text, and the math never renders at all* (this actually shipped: `$$\text{rate}_t = \frac{\text{index}_t - \text{index}_{t-1}}{\dots}$$` rendered as raw italic `$$…$$` on
    github.com, E02 §2 2026-06-26). Always wrap the script in `{}`: `$P_{t}$`, `$x_{i}$`, `$\pi_{t}$`,
    `$Q_{d}$`. A one-line pre-push grep catches every bare subscript: `grep -nE '_[^{]' <file>` (and
    `grep -nE '\^[^{\\]' <file>` for superscripts) — both should return nothing inside math.
  - **Never put markdown emphasis (`*word*` / `_word_`) inside math — especially inside `\text{}`.** To
    italicize a word that sits inside a formula, you can't use `*…*`: GitHub's emphasis parser (and many
    markdown linters, which *auto-normalize* `*emphasis*` to `_emphasis_` on save) turn `\text{the job-*seeking*
    population}` into `\text{the job-_seeking_ population}`, and a **bare `_` in MathJax *text* mode is illegal**
    — the whole display equation dies with the red error **`'_' allowed only in math mode`** (this shipped in
    E02 §3 2026-06-29; a linter flipped the `*` to `_` *after* the trap-grep passed). Fix: **drop the emphasis
    inside math** (keep the word plain in `\text{}`), or move the emphasized prose *outside* the `$…$`. Catch
    it pre-push with `grep -nE '\$[^$]*[_*][^$]*\$' <file>` (ignore the known-safe `^{\ast}`, `_{...}` hits).
  - **Don't wrap inline math in markdown emphasis either — `*… $x$ …*` / `**… $x$ …**` leaks the raw `$x$`.**
    The flip side of the rule above: an italic or bold *run* that *contains* a `$…$` span stops GitHub's
    math extension from opening the delimiter, so the raw LaTeX shows through — even though the *identical*
    math renders fine when it isn't inside emphasis (shipped in E02 §11 2026-07-02: an italicized aside
    `*…you need potential growth $g^{\ast}$…*` leaked while the same `$g^{\ast}$` in plain prose rendered).
    Fix: **take the emphasis off the clause that holds the math** (emphasize the surrounding words instead),
    or split so the `$…$` sits outside the `*…*`. Especially bite-y when the emphasis run also spans a soft
    line-break. Eyeball-only review misses it; Playwright-verify.
  - **Don't wrap inline math in literal parens when the math itself contains parentheses** — the nested
    `(…$…(…)…$)` confuses GitHub's cmark-gfm delimiter matching and the whole `$…$` leaks as raw text. A
    parenthetical aside like `**Okun's law** ($\Delta u \approx -0.5 (g - g^{\ast})$)` fails, but the *same*
    math with no outer parens (`… $…-0.5 (g - g^{\ast})$, …`) renders fine, and outer parens around math with
    *no* inner parens (`($\text{employed} / \text{pop}$)`) also render fine — you need **both** layers to trip
    it. Because every other math span on the page renders, eyeball-only review misses it (shipped in E02 §3
    2026-07-02: 1 leak out of 11 spans). Fix: drop the outer parens — use em-dashes (`— $…$ —`) or commas
    (`, $…$,`) for the aside. Catch the risky pattern pre-push with `grep -nE '\(\$[^$]*\(' <file>` (open-paren,
    then inline math that contains another open-paren); Playwright-verify to be sure.
  - **Don't put a `$$…$$` display block on an indented list-continuation line.** GitHub renders display math
    only as a *standalone block* (its own paragraph, column 0, blank line on each side). A `$$…$$` indented
    under a `-`/`1.` list item is left as literal text. Either lift the equation out to a standalone block
    after the list, or use **inline** `$…$` (which *does* work inside list items) — both fixes were needed in
    E02 §2. Standalone `$$…$$` in ordinary body prose (as in E02 §1) is fine.
  - **Never put a literal `|` inside math in a table cell.** The table parser reads every `|` as a column
    separator, so `$|\varepsilon|$` in a cell *silently shreds the whole table* into inline text. Write
    absolute value as `$\lvert\varepsilon\rvert$` (or `$\lVert\cdot\rVert$` for norms). Inline `$|\cdot|$`
    *outside* a table is fine.
  - **Don't place two inline-math spans adjacent with no spaces** (`$MB$/$MC$`, `$x$$y$`). GitHub parses
    the first and leaves the second literal (`MB/$MC$`). Merge into one span (`$MB/MC$`) or put text/space
    between them.
  - **Never use an escaped `\$` (a literal dollar sign, e.g. `\$1`, `\$100 billion`) on a line/paragraph that
    also contains an inline `$…$` math span.** GitHub's math extension scans for `$` delimiters and treats
    the *escaped* `\$` as an **opening** delimiter, so it pairs with the next real `$` — swallowing the prose
    in between as a run-together italic math span and leaving your *actual* formula dumped as literal LaTeX
    source with a stray trailing `$`. Shipped in E02 §4 2026-07-02: `a \$1 shock … moves output by
    $\Delta Y = \frac{…}{1-c}$` rendered as the jammed italic `1shocktodemandultimatelymovesoutputby` followed
    by literal `\Delta Y = \frac{…}` — the money sign, not the math, was the culprit. **Fix: spell the money
    out** ("a one-dollar shock", "100 billion dollars") so there's no `$` sign on that line at all. Catch it
    pre-push with `grep -nE '\\\$' <file>` and check each hit shares no line/paragraph with `$…$` math.
    Eyeball-only review of the editor preview misses it (Cursor renders the escape correctly); Playwright the
    GitHub blob — the `.js-display-math`/`.js-inline-math` span count coming up *short* of your `$…$` count is
    the tell.
  - **Give an inline `$…$`'s *opening* `$` a clean left boundary — a space or an opening bracket `([{`, never
    a glued `"` or a hyphen.** GitHub only opens an inline-math span when the opening `$` is flanked on the
    left by whitespace or opening-bracket punctuation; a `$` glued directly to a **double-quote** (`"$P < AVC$"`)
    or sitting inside a **hyphenated word** (`hire-to-$MRP$`, `efficient-$P^\ast$`) fails to open, so the whole
    span renders as **literal LaTeX** (dollar signs visible). Found shipped in three econ sections 2026-07-09
    (E01 §2 `efficient-$P^\ast$`, E01 §4 `"$P < AVC \Rightarrow$…`, E02 §4 `hire-to-$MRP$`) — every *other* span
    on those pages rendered, so eyeball review of "the math works" misses it. Note the **closing** `$` glued to
    a following `"` is *fine* (`$g^{\ast}$"` renders), and an opening `$` after `(` is fine — it's specifically
    the *opening* `$` after a quote or hyphen that breaks. **Fix: reword so the opening `$` follows a space** —
    `(efficient-price $P^\ast$)`, `"hire to $MRP$"`, `shut down when $P < AVC$`. Catch pre-push with
    `grep -nE '"\$[A-Za-z\\]|[A-Za-z]-\$[A-Za-z\\]' <file>` (opening `$` glued to a quote or a hyphen-word).
    Playwright-confirm: the raw `$…$` appears in the rendered `.markdown-body` innerText.
  - Prefer plain `(...)` or `\left(...\right)` over `\big(`/`\!` micro-spacing in inline math — fewer
    macros, fewer surprises across renderers.
- **Verify on GitHub, not just in the editor.** This repo is **public**, so after pushing, check the blob URL
  `https://github.com/<owner>/<repo>/blob/<sha>/<path>`. Cursor's preview is *not* authoritative for math.
  There are **two levels of check, and you need both** — the cheap one has a real blind spot:
  - **(1) Recognition check — `curl` + grep (cheap, but only proves GitHub *parsed* it as math).** `curl -sL`
    the blob URL and grep the HTML: GitHub wraps every *recognized* expression in `<math-renderer>` /
    `js-inline-math` / `js-display-math`. `grep -oE 'js-(inline|display)-math' blob.html | sort | uniq -c`
    should roughly match your `$…$` / `$$…$$` counts (each display block ≈ 2 markers), and the formula should
    sit *inside* `<math-renderer …>$…$</math-renderer>`, not leak into prose. **Do not** use the `POST
    /markdown` REST API — it doesn't enable the math extension (zero spans even for valid input → false
    negative). **Blind spot:** this only checks *recognition*. A formula can be correctly wrapped in a
    `<math-renderer>` (so the grep passes) and **still fail to typeset** — e.g. the `_`-in-`\text{}` trap
    above was counted as math yet rendered a red `'_' allowed only in math mode` error. The grep said "fine";
    the page was broken.
  - **(2) Typesetting check — Playwright (authoritative; catches what grep can't).** Playwright is installed
    **globally** (v1.58.2), so any project on this machine can use it: the CLI is on `PATH` (`playwright
    --version`), import the library via the global root — `import { chromium } from
    '<npm root -g>/playwright/index.mjs'` (resolve `<npm root -g>` with `npm root -g`; currently
    `/home/zhangzhou/.nvm/versions/node/v24.14.1/lib/node_modules`), and the browsers are cached under
    `~/.cache/ms-playwright`. Load the blob URL (`waitUntil: 'networkidle'`, then a ~2.5 s pause
    so MathJax runs), then **(a)** screenshot the formula region and *look at it*, and **(b)** assert
    `body.innerText` contains none of MathJax's error strings — `'allowed only in math mode'`,
    `'Undefined control sequence'`, `'Misplaced'`, `'Math input error'`. Note GitHub does **not** reliably
    emit classic `mjx-container` nodes (count came back 0 even when math rendered fine), so don't gate on that
    selector — trust the screenshot and the error-string scan. This is the only check that would have caught
    the E02 §3 bug (2026-06-29).

## 5. Gloss key terms in Chinese (中文), with 大陆/台灣 both where they differ

*(Established 2026-06-20 from learner feedback on Econ E01 §3.)* The learner reads economy/business **news
and reports in Chinese as well as English**. Material stays **in English**, but **give the Chinese
translation for key concepts and terms** so the vocabulary transfers to Chinese-language sources.

- **Provide both Mainland China (大陆, 简体) and Taiwan (台灣, 繁體) terms.** They differ in two ways: usually
  just **simplified vs traditional script**, but sometimes a **genuinely different word** — flag those
  (the learner trips over them when reading across both). Recurring real splits seen so far: **信息↔資訊**
  (information), **物品↔財** (goods), **垄断↔獨占** (monopoly), **寡头垄断↔寡占** (oligopoly), **收入↔所得**
  (income), **税↔租稅** (tax), **价格歧视↔差別取價**, and transliterated names (**科斯↔寇斯** Coase,
  **庇古↔皮古** Pigou). Don't assume a term is identical across the strait — check.
- **How to gloss:** a **bilingual "Key terms" table** near the end of the section (English · 大陆 · 台灣,
  with a note column marking ⚠ genuine differences) works well as a reference; optionally also gloss the
  single most central term inline at first mention. Keep glosses to *key* concepts, not every word.
- Applies to **all tracks**, but is most load-bearing for subjects whose payoff is *reading real-world
  sources* (the Econ/Finance hobby track especially).

## 6. The reading track is "National Geographic / Discovery," NOT a course brought forward

*(Established 2026-07-02 from `prompts/002-reading-track-clarification.md`.)* The **reading track**
(`upskill-readings/`) is a **different genre** from the course and hobby tracks. Its job is to make the
learner go *"huh, I didn't know that / I want to know more"* — the way a good National Geographic or
Discovery feature does — **not** to pre-teach, textbook-style, the chapters coming up in the course. The
earlier readings erred by being "future courses brought forward" (rigorous RTT/handshake mechanics, etc.);
that is explicitly **not wanted**.

- **Function:** wonder, breadth, and currency — the surrounding world, not the syllabus. Lead with **latest
  technologies, real case studies, current popular topics and live debates**, recent news and events. Think
  *Quanta / The Economist / a great Nat-Geo feature for a smart adult*, not a lecture. Story- and
  example-driven.
- **Pitch:** the *genre* is Discovery-channel-accessible, but the *intellect* is still his (PhD, frontier
  practitioner). Accessible and vivid ≠ dumbed down. Go deep on the interesting parts.
- **NOT this:** derivations, problem-set rigor, "here is the mechanism one layer down, ahead of M0x." If it
  reads like a course section, it's wrong for this track. (Course/hobby tracks are where rigor lives.)
- **Balance rule (new 2026-07-02):** each day's reading carries **two topics — one "career" and one
  "hobby"** (replaces the old "one theme, two altitudes"; the two need not share a theme). **Neither has to
  map to a course chapter or even the course subjects** (clarified 2026-07-02): the **career** topic is
  anything with a plausible **positive effect on his career** (CS/SWE/AI, but also adjacent tech, industry,
  tools, ways of working, science that feeds his work…); the **hobby** topic is anything **genuinely
  interesting** — *use your judgment* on what he'd find fascinating (his known interests: economics/finance,
  physics/semiconductors, AI frontier, geopolitics-of-tech, systems). Breadth is the point; don't cage it to
  the syllabus.
- **Keep the good production values** (they still apply): a "why this / why now" framing, real committed
  figures/diagrams (rule 2), verified hyperlinks ([[references-need-valid-links]]), any math in LaTeX
  (rule 4), and the bilingual 中文 glossary (rule 5). Just in service of a feature story, not a lecture.

## 7. Generated illustrations — you may create images locally (ComfyUI), but only where they earn their place

*(Established 2026-07-08 from learner instruction.)* Beyond charts and diagrams, this machine can
**generate/edit raster images locally** via the `comfyui-media` skill (installed ComfyUI + Z-Image
Turbo on an RTX 4070; fast text-to-image, ~14 s per 832²/1024² image, no cloud API). You are cleared
to use it to make **illustrations for any track's material.** But images are a garnish, not the meat —
the rule-2 precedence still governs *what kind* of visual a given need calls for.

- **Precedence — pick the right tool for the visual, in this order:**
  1. **A real, canonical figure** (a published plot, a real photograph of a real thing, an official
     diagram) — still the first choice per rule 2. Commit a local copy + keep the source URL.
  2. **A drawn-from-data figure** (matplotlib/plotly → committed PNG/SVG) for any *quantitative*
     relationship — a curve, distribution, trend. **Never** generate these as AI images; a model
     paints a plausible-looking plot with wrong/meaningless numbers.
  3. **A structural diagram** (Mermaid etc. per [`diagrams.md`](diagrams.md)) for architecture, flow,
     state, hierarchy — boxes, arrows, pipelines.
  4. **A generated illustration** (ComfyUI) — the right tool *only* for the remaining case: a
     **conceptual, metaphorical, atmospheric, or scene-setting** visual where a picture aids
     comprehension or engagement and **no real figure exists and the content isn't quantitative or
     structural.** Examples that fit: a metaphor made concrete (a "shadow price" as a literal shadow),
     a section/mascot header, a vivid scene for a reading-track feature (rule 6 — this genre benefits
     most), an analogy illustration.
- **Two hard limits — do not cross them (this is educational material; honesty of depiction matters):**
  - **Never generate a picture of a *real, specific* thing and present it as that thing.** A generated
    "photo of the Vera Rubin Observatory," a named person, a specific chip die shot, a real UI
    screenshot — these are **fabrications**. For real specific subjects use a real licensed/public
    image with provenance (path 1). Generate only *generic/illustrative* subjects ("a large telescope
    dome at dusk," "a stylized data-center hall").
  - **Never bake text into the pixels — add it as an overlay layer instead.** Z-Image Turbo is weak at
    rendering precise words/labels, so generate the picture **text-free** and then, *when the illustration
    needs labels/arrows/highlight boxes/callouts*, draw them on top with **matplotlib or PIL** — a
    deterministic, crisp overlay (the "generate, then annotate" two-layer workflow). This is how you put
    trustworthy text on a generated image, and it lets a generated backdrop carry a precise labeled layer
    (an *annotated scene*) when a plain Mermaid/matplotlib diagram would be too sterile. Recipe:
    `comfyui-media` skill → `references/annotate.md`. (Text that only lives in the markdown caption around
    the image is fine too — but a caption is not a substitute for an on-image label pointing at a feature.)
- **Provenance is mandatory.** Every generated image gets a caption (or adjacent note) marking it
  AI-generated locally, e.g. *"Illustration — generated locally (ComfyUI + Z-Image Turbo)."* Readers
  must never mistake a generated illustration for a real figure/photo.
- **Where they live & how to commit** — mirror the diagrams convention: put the PNG in an `images/`
  folder next to the doc (`images/<doc-basename>-<N>.png`), embed with `![alt](images/…)`, and record
  the **prompt** used in an HTML comment or a collapsed `<details>` beside the embed so the image is
  regenerable/diffable (the prompt is the "source of truth," like Mermaid source for diagrams). **If the
  image was annotated** (the two-layer workflow above), also commit the **annotation script**
  (`images/<doc-basename>-<N>-annotate.py`) beside it — the overlay's source of truth, exactly like a
  matplotlib figure's `.py`. The committed PNG is the *annotated* result; provenance still marks the base
  picture AI-generated (e.g. *"…generated locally (ComfyUI); labels added in matplotlib."*).
- **ALWAYS look at the rendered image before committing** — same mandate as diagrams.md: `Read` the
  PNG and check it actually shows what you intended, with no garbled anatomy/text/artifacts. Generators
  routinely produce plausible-but-wrong output. Do not commit an image you haven't looked at. Regenerate
  (tweak the prompt/seed) until it's right.
- **How to run it:** invoke the `comfyui-media` skill, or call its CLI directly —
  `python3 ~/.claude/skills/comfyui-media/scripts/comfy_media.py txt2img --prompt "…" --out <name>
  --width 1024 --height 1024`. It starts the server, generates, and prints the output PNG path (lands
  in `ComfyUI/output/`); copy that into the doc's `images/` folder. The skill can also download
  fitting open models for image *editing* or *video* when Z-Image can't do the task.
