# Authoring conventions for course material

> **Scope:** project-level — applies to **all tracks** (course, reading, hobby, and any future track).
> These are the learner's own instructions on how material should be written. Keep them in context
> whenever you prepare or finalize a section/reading. Established 2026-06-17 from learner feedback on
> Econ E01 §2.

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

## 3. Always write math in LaTeX

Every mathematical expression, formula, equation, variable, sub/superscript, or operator goes in
**LaTeX math** so it renders correctly and reads cleanly — **not** in inline code backticks or plain text.

- Inline: `$Q_d(P)$`, `$P^*$`, `$MB = MC$`, `$Z'(P^*) < 0$`.
- Display (for anything you want set off): `$$dP/dt \propto Z(P) = Q_d(P) - Q_s(P)$$`.
- Use proper symbols: `\propto \approx \geq \leq \neq \partial \alpha \leftarrow \cdot`, subscripts
  `Q_d`, superscripts `P^*`. Don't leave `>=`, `P*`, `Q_d` in code font or raw text.
- GitHub-flavoured markdown renders `$...$` and `$$...$$`; verify long expressions read cleanly.
