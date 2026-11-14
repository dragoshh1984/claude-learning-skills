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
   in the sources (sections/eqs), and a SUGGESTED mini-project choice:
   **none** (explainer page only), **analytical** (math/graphs computed in code,
   no training) or **train** (small model, MNIST-scale). The page is the core
   deliverable; a mini-project is optional and the user decides (see the
   mini-project gate below).
2. **Grill the user** before writing anything to `src/learning/`. Use
   AskUserQuestion, ONE question at a time (the user answers with arrow keys).
   Cover at least: which concepts to create (and priority order), which the user
   already knows well vs wants depth on, **the mini-project gate per concept**
   (below), and anything campaign-specific worth its own page. Recommend an
   answer for each.
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

## The mini-project gate (shared by every skill in this pipeline)

The mini-project is **optional** (user rule, 2026-11-14). The explainer page is
the deliverable; a `<slug>.py` experiment exists only when the user asks for one.

1. **Ask it as its own grill question**, one per concept (or one for a batch of
   concepts, with "decide per concept" as an option), arrow-selectable:
   - *Explainer only — no mini-project*
   - *Explainer + analytical mini-project* (code computes/plots the math, no training)
   - *Explainer + training mini-project* (small real run, minutes on the GPU)
   Recommend one, with a one-line reason (e.g. "explainer only: nothing here is
   worth measuring that the math does not already show"). Do not default to a
   mini-project; recommend one only when it would measure something the page
   cannot derive.
2. **Only if the user picks a mini-project**, run a SHORT follow-up grill — at
   most 3 questions, one at a time. The FIRST question is always how involved
   they want to be:
   - *You decide the details* (recommended default) — Claude picks dataset,
     scale, arms and figures, states the choices in chat, and proceeds;
   - *Ask me the key choices* — then ask at most two more: the question the
     experiment answers / which arms, and scale or runtime budget;
   - *I'll write it myself* — hand off to `concept-code-tutor`.
3. **Record the answer** in `notes.md` (`Mini-project:` line) so later skills
   and fresh sessions do not ask again. `none` means: no `<slug>.py`, no
   `assets/` from our code, no mini-project sections on the page.

## notes.md structure (per concept)

```markdown
# <Concept name>
Status: notes | explainer-drafted | code-done | linked
Mini-project: none | analytical | train   (the user's answer to the gate;
              `ask` if not yet asked; + `details: claude | user | tutor`)
Campaign: <campaign> (paper-driven | topic-driven)
Sources: <paper title + arxiv link + sections/eqs used, or the canonical
          sources for the topic — sync with distill-core references/sources.md>

## What it is (3-6 sentences)
## The math
  - Key equations verbatim with eq numbers, notation defined.
  - DERIVATION GAPS: steps the source skips that the explainer must expand.
## Intuition / mental model
## Mini-project sketch   (only when Mini-project ≠ none)
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
