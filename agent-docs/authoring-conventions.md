# Authoring conventions for course material

> **Scope:** project-level — applies to **all tracks** (course, reading, hobby, and any future track).
> These are the learner's own instructions on how material should be written. Keep them in context
> whenever you prepare or finalize a section/reading. Established 2026-06-17 from learner feedback on
> Econ E01 §2; extended 2026-06-18 (rule 3) from feedback on M04 Ch2 §1.

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
    silently eats the rest of the expression (this is how a whole `$$…$$` fraction vanished). Use the
    **letter-named** equivalents, which survive because the backslash is followed by a letter:
    `\thinspace` / `\medspace` / `\thickspace` / `\quad` for spacing; and **avoid `\%` entirely** —
    reword to a fractional-change ratio like `\frac{\Delta Q / Q}{\Delta P / P}` (which *is* the
    percentage-change ratio) instead of writing `\%\Delta Q`.
  - **Never put a literal `*` inside math** (`$P^*$`, `$Q^*$`). GitHub runs Markdown `*emphasis*` parsing
    *over* the `$...$` content, so the `*` is eaten (you get `$P^$`) and — worse — it pairs with the next
    real `*emphasis*` asterisk in the paragraph, turning text italic and corrupting *every other* `$...$`
    span between them (one stray `*` silently broke `$MB$`, `$MC$`, … on the same line). Write the
    superscript star as `\ast`: `$P^\ast$`, `$Q^\ast$`. Same risk with `_` (subscript-underscore vs
    `_emphasis_`) — keep `_` only inside `{}` like `Q_{d}` and you're safe.
  - **Never put a literal `|` inside math in a table cell.** The table parser reads every `|` as a column
    separator, so `$|\varepsilon|$` in a cell *silently shreds the whole table* into inline text. Write
    absolute value as `$\lvert\varepsilon\rvert$` (or `$\lVert\cdot\rVert$` for norms). Inline `$|\cdot|$`
    *outside* a table is fine.
  - **Don't place two inline-math spans adjacent with no spaces** (`$MB$/$MC$`, `$x$$y$`). GitHub parses
    the first and leaves the second literal (`MB/$MC$`). Merge into one span (`$MB/MC$`) or put text/space
    between them.
  - Prefer plain `(...)` or `\left(...\right)` over `\big(`/`\!` micro-spacing in inline math — fewer
    macros, fewer surprises across renderers.
- **Verify on GitHub, not just in the editor.** This repo is **public**, so after pushing you can open the
  blob URL and check the math actually rendered — e.g. drive a headless browser (Playwright) to
  `https://github.com/<owner>/<repo>/blob/main/<path>` and screenshot it. Cursor's preview is *not*
  authoritative for math.

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
