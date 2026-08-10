---
name: distill-core
description: Shared distillation engine — concept map → grill round → per-concept notes.md → bookkeeping. Not invoked directly; paper-distill (paper-seeded) and concept-distill (topic-seeded) both delegate here after preparing their source material.
---

# distill-core

The shared back half of every distillation: turn prepared source material into a
concept map, let the user select, and write the `notes.md` files that seed
`concept-code` / `concept-code-tutor` / `concept-explainer`.

The caller (paper-distill or concept-distill) arrives with:
- a campaign dir `src/learning/<campaign>/`
- read source material — a fully-read paper + `code_map.md`, or fetched
  canonical sources for a topic
- a candidate concept list

## Workflow

1. **Draft the concept map.** Split into:
   - **General reusable concepts** — things that recur across papers/topics
     (e.g. flow matching, DiT blocks, CFG, normalization). These become
     `src/learning/<campaign>/concepts/<slug>/`.
   - **Campaign-specific mechanisms** — the paper's own contributions, or the
     topic's niche variants. These live in the campaign's material, referencing
     the general concepts.
   For each candidate concept, sketch: one-line definition, where it is defined
   in the sources (sections/eqs), and whether its mini-project flavor is
   **train** (small model, MNIST-scale) or **analytical** (math/graphs, no
   training).
2. **Grill the user** before writing anything to `src/learning/`. Use
   AskUserQuestion, ONE question at a time (the user answers with arrow keys).
   Cover at least: which concepts to create (and priority order), which the user
   already knows well vs wants depth on, train vs analytical flavor per concept,
   and anything campaign-specific worth its own page. Recommend an answer for
   each.
3. **Write outputs** (only for concepts the user selected):
   `src/learning/<campaign>/concepts/<slug>/notes.md` per concept — see below.
   The campaign's `index.html` hub is built only AFTER its concepts exist.
   REMEMBER: .md files are Claude-facing references. The user-facing
   deliverables are the concept `index.html` pages and `<slug>.py` files —
   a distillation pass is not "done for the user" until those follow.
4. **Update the canonical-source list** in `references/sources.md` (this skill's
   folder): for each topic, the papers/textbooks/guides an explainer must cite.
   The file is local and gitignored (personal study data); create it on first
   use.
5. **Update repo `CLAUDE.md`** (concept table) and `docs/JOURNAL.md` (one entry:
   what was distilled, what was selected, why).

## notes.md structure (per concept)

```markdown
# <Concept name>
Status: notes | explainer-drafted | code-done | linked
Flavor: train | analytical
Campaign: <campaign> (paper-driven | topic-driven)
Sources: <paper title + arxiv link + sections/eqs used, or the canonical
          sources for the topic — sync with distill-core references/sources.md>

## What it is (3-6 sentences)
## The math
  - Key equations verbatim with eq numbers, notation defined.
  - DERIVATION GAPS: steps the source skips that the explainer must expand.
## Intuition / mental model
## Mini-project sketch
  - train: dataset, architecture size, what success looks like, runtime budget
  - analytical: what to compute/plot, over what ranges
## Visualization ideas (interactive canvas candidates)
## Decisions to ASK the user (never parked on a page — see study-iterate)
```

## Rules

- Never present a concept map built from an abstract or from memory alone —
  read the sources first (the caller is responsible for having done this).
- Equation numbers and section references are mandatory; "somewhere in
  section 3" is not a citation.
- Distinguish clearly what the source *claims* vs what it *shows* — the
  explainer will inherit this framing.
- If a concept already exists in an earlier campaign, extend that page/notes
  with the new perspective and link to it instead of duplicating.
