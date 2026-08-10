---
name: concept-explainer
description: Author or iterate on a self-contained HTML explainer page for a DL concept in src/learning/<campaign>/concepts/<slug>/ — real LaTeX math (KaTeX), interactive canvas visualizations, inline excerpts of the concept's PyTorch code, embedded real training outputs. Use after paper-distill produced notes.md, whenever the user asks to explain/visualize/diagram a concept, or to refine an existing page.
---

# concept-explainer

Produce `src/learning/<campaign>/concepts/<slug>/index.html`: a long-form,
self-contained explainer calibrated to a strong-ML-background reader. Input is
the concept's `notes.md` (from `paper-distill`), its code file (from
`concept-code`) when it exists, and the paper's official implementation cloned
at `src/learning/<campaign>/official/`.

**Before starting, read `references/lessons.md` (this skill's folder)** — the
accumulated page-building rules apply before any HTML is written.

## Non-negotiables (learned from user corrections)

- **Ship finished pages, never roadmaps.** No "Planned for the full page",
  no "skeleton draft", no status banners. If a concept is worth a page, build
  the page: derivations, interactives, trained code, real figures. A page that
  describes what it would contain is not a deliverable.
- **Never park open questions on a page.** Design decisions go to the user
  HERE, interview style — AskUserQuestion, one question at a time, arrow-
  selectable options, with a recommendation. Then build the chosen answer.
- **Name every parallel stream explicitly**, even when the code is identical
  (Epona: img/VisDiT vs traj/TrajDiT) — never leave the reader guessing whether
  a statement covers both.
- **Report negative and counterintuitive results in full.** A measured null
  (chain-of-forward not helping) with candidate explanations and what would
  falsify it is more valuable than a tuned-until-it-agrees result. Never
  declare a direction dead — that verdict is the user's.
- **State confounds you did not remove** (e.g. adaLN's extra parameters).
- **When the paper is wrong, say so ONCE and then be correct everywhere.**
  Flag the error prominently at the top of the owning page — what the paper
  says, why it is wrong, what the correct form is — and from then on write
  every equation, caption, figure and line of code in the correct convention,
  with no further asides. Do not annotate each equation with a correction, and
  do not keep a comparison table: repetition makes the reader carry the error
  around instead of dropping it. (This replaces an earlier per-equation
  correction style that the user rejected as noise.)
  Consequences to follow through on: the **code** must adopt the correct
  convention too (pages quote it verbatim, so a mismatch is a contradiction),
  models must be **retrained** if the change alters what an input means, and
  **figures must be regenerated** — a strip rendered noise→data reads backwards
  under the corrected clock even if its caption is fixed.

## Page doctrine

- **Self-contained single file.** All CSS/JS/fonts inlined; megabyte-size pages
  are accepted. Start from `assets/template.html` in this skill's folder — it has
  KaTeX (JS + CSS + fonts) inlined and the base layout. Never use CDN links.
- **Source-of-truth rule.** The page's editable SOURCE is a committed
  `fragment.html` sitting next to `index.html` (h1 + `<section id>` blocks +
  inline `<script>` for interactives). `index.html` is BUILT from it with
  `assets/build_page.py` (inlines images as data URIs via `--images-root`) and
  is never edited directly. Validate every build with `assets/validate_page.js`
  (node) — one bad KaTeX expression silently kills all math on the page.
- **Long-form scrolling with a sticky TOC.** One section = one idea, slide-ish
  pacing. Keyboard j/k or prev/next jumps between sections.
- **Notation table near the top** — every symbol used later, defined once.
- **Section anatomy** (not every section needs all parts, but this is the order):
  1. Motivation — why this idea exists, what breaks without it.
  2. The math — KaTeX-rendered equations. Cite the source paper with section +
     equation numbers AND the canonical sources (see `distill-core`
     `references/sources.md`). Key equations get a visual box.
  3. Expanded derivation — the steps the paper skips, worked explicitly. This is
     the core value of the page; do not compress it away.
  4. Intuition — mental model, limiting cases, what the equation "does".
  5. Interactive visualization — see below.
  6. Code — inline excerpt of OUR mini-project code (see linking rules), AND
     the corresponding excerpt of the paper's ACTUAL implementation from
     `official/` with its file:line — side by side or stacked, so the reader
     sees both the pedagogical minimum and the production reality.
  7. Real outputs — figures the code actually produced, from `assets/`
     (trial basis: keep curated small PNGs, raw outputs stay gitignored).

## Diagrams (required, not optional)

Every concept page carries at least a **high-level overview diagram** and an
**expanded block diagram**. Architecture is the thing prose is worst at.

- **Draw every skip and residual connection explicitly.** They are the load-
  bearing structure of modern nets and the reader's main question. The template
  reserves the accent hue (`.dg-skip`, `.dg-op`) for exactly this: everything
  else is `currentColor`. Label each one with what it carries
  ("concat 96ch @32×32", "residual 2 · around the MLP").
- **Say what is NOT a skip** when it could be mistaken for one (encoder→mid is
  ordinary flow; an autoencoder has no encoder→decoder bridge, and that absence
  is the lesson).
- Verify structure against the real code before drawing — read the block's
  `forward` in `official/` rather than assuming the usual pattern.
- Hand-authored inline `<svg>` with `viewBox`, `role="img"`, `aria-label`,
  wrapped in `<figure class="diagram">` with a `<figcaption>` stating the claim.
  Classes: `.dg-node`/`.dg-node-2` boxes, `.dg-flow` arrows, `.dg-skip` skips,
  `.dg-cut` severed/training-only paths, `.dg-ghost` broadcast buses,
  `.dg-t`/`.dg-b`/`.dg-s`/`.dg-k` text. Unique marker ids per diagram.
- **Check for text overflow programmatically** (x + estimated width vs viewBox
  width, accounting for `text-anchor`) and render every diagram in a headless
  browser before shipping. Both were needed to catch real breakage.

## Interactive visualizations

- Vanilla JS + `<canvas>` (or inline SVG). No external libraries.
- Each interactive teaches exactly ONE relationship — typically sliders for the
  1-3 parameters that matter, driving an immediate redraw. If you need more
  controls than that, split into two interactives.
- Always render the initial state without interaction — the page must teach even
  if the reader never touches a slider.
- Label axes and show current parameter values numerically.

## Code linking rules

- Excerpts are copied VERBATIM from the concept's `.py` file at authoring time,
  syntax-highlighted, headed by the repo-relative path with line numbers, e.g.
  `src/learning/<campaign>/concepts/<slug>/<slug>.py:42-73`.
- **After ANY edit to a `.py` — including a docstring or comment — re-verify
  every excerpt AND every inline `path:line` on every page that quotes it.**
  A one-line docstring change shifts every reference below it, and a wrong
  line number is a lie the reader cannot detect. Do not do this by eye:
  ```
  uv run python .claude/skills/concept-explainer/assets/check_excerpts.py --all
  ```
  It verifies that each excerpt's first line sits exactly at the stated start
  line and that every quoted line really appears in the stated range (ignoring
  indentation, which pages de-indent, and `...` elisions). Exit code 1 if stale.
  Run it before every rebuild; treat a STALE line like a failing test.
- Excerpt the sections marked with `# ── <name> ──` banners (the `concept-code`
  skill mandates those); never paraphrase code.

## Workflow

1. Read `notes.md`, the code file (if any), and the canonical sources list.
2. **Grill the user** (AskUserQuestion, ONE question at a time, arrow-selectable,
   with a recommended answer): section list for this page, which derivations to
   expand vs summarize, which interactives to build, depth calibration for THIS
   topic (what they already know).
3. Build the page from the template. Verify: opens locally, math renders,
   interactives run, excerpts match the real file.
4. Iterate: the user reviews in a browser and gives feedback in rounds — expect
   multiple iterations, treat each as normal, not as rework.
5. Update `notes.md` status, repo `CLAUDE.md` concept table, `docs/JOURNAL.md`.
6. **Refine this skill**: if the iteration taught a reusable lesson (a layout
   that worked, a viz pattern, a KaTeX gotcha), append it to
   `references/lessons.md` and, when structural, amend this file.

## Template maintenance

`assets/template.html` (committed) is built by `assets/build_template.py` from
the committed `assets/vendor/` dir (KaTeX + highlight.js) — no network, ever.
The layout, palette and all page CSS live in that script's `LAYOUT` string:
**edit the script, never `template.html`**, then:

```
uv run python .claude/skills/concept-explainer/assets/build_template.py   # -> template.html
# then rebuild EVERY page — each embeds a copy of the template
```

Palette rules learned the hard way: define colors for `main a` (links),
`a:visited`, and `accent-color` on range/checkbox inputs, plus explicit button
styling. Anything left unstyled falls back to the browser's default blue, which
looks broken next to the page palette. Current palette: warm paper light /
deep slate dark, deep-teal accent (`--accent`/`--link`), muted plum for visited.
