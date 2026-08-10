---
name: concept-distill
description: Distill a DL concept or topic (no source paper) into canonical sources and per-concept notes that seed learning mini-projects in src/learning — the topic-driven twin of paper-distill. Use when the user wants to study a concept rather than a paper ("I want to study/learn normalization / optimizers / attention variants", "distill concept X") or wants to extend a topic campaign like fundamentals.
---

# concept-distill

Turn a topic into the raw material for learning mini-projects when there is no
single paper to distill — the building blocks that recur across papers
(normalization, activations, optimizers, initialization, attention variants…).
This skill does the topic-specific work — campaign placement, canonical-source
gathering — then hands off to the shared engine in `distill-core` (a sibling
skill folder of this one) for the concept map, grill round, and `notes.md`
outputs. Downstream skills are the same: `concept-code` / `concept-code-tutor`
and `concept-explainer`.

## How a topic campaign differs from a paper campaign

- No `paper.pdf`, no `official/` clone, no `distillation.md`, no `code_map.md`.
- The campaign groups RELATED topics, not one publication — prefer extending an
  existing topic campaign (e.g. `src/learning/fundamentals/`) over creating a
  new campaign per concept. Create a new one only for a genuinely new area.
- Everything else is identical: same `concepts/<slug>/` layout, same
  notes.md → code → explainer doctrine, same train/analytical flavors.

## Workflow

1. **Place the campaign.** Check `src/learning/` for an existing topic campaign
   the concept belongs to; default to extending it. If a concept already exists
   in ANY earlier campaign (paper- or topic-driven), extend that page instead of
   duplicating — check before creating anything.
2. **Gather the canonical sources.** This replaces the paper read, and it is not
   optional — the math must come from real sources, never from memory:
   - Check `distill-core/references/sources.md` first — the topic may already
     have a curated source list.
   - Otherwise search for the defining paper(s), textbook chapters, and
     authoritative writeups; FETCH and READ the sections that define the math.
     Record exact section/equation numbers as you go — the explainer must cite
     them, same standard as a paper campaign.
   - The topic's variants usually live in different papers (e.g. BatchNorm,
     LayerNorm, GroupNorm, RMSNorm are four papers) — read the defining section
     of each variant you intend to cover.
3. **Run the shared engine.** Read `distill-core/SKILL.md` (sibling folder of
   this skill) and follow its workflow — concept map, grill round, per-concept
   `notes.md`, sources update, CLAUDE.md/journal update — with the fetched
   sources as the source material. Topic-specific grill emphasis: how to SPLIT
   the topic (one concept page vs several siblings), and which variants are in
   scope.

## Rules (on top of distill-core's)

- A topic concept must find its **organizing idea** — the single frame that
  unifies the variants (e.g. "every normalizer = pick reduction axes →
  standardize → affine; only the axes differ"). If the notes are just a list of
  variants, the distillation isn't done.
- **Enumerate the full variant space**, not just the variants the user named in
  the kickoff — the user listing "GroupNorm, adaLN and so on" means "find the
  rest yourself" (the fundamentals campaign was explicitly corrected on this:
  "pull out more of these, not just those").
- Every variant answers **WHY it exists, WHERE it earns its keep (real tasks /
  failure modes it fixes), where it was introduced (paper + year), and the
  math** — that four-part structure is the user's stated template for topic
  pages.
- **Keep the topic generic** — do not inherit a domain bias from whatever
  campaign or paper prompted the study (the normalization page was corrected
  mid-flight for being diffusion-focused; the topic is the subject, not the
  context it came up in).
- Prefer **analytical** flavor when everything the page would claim can be
  derived or measured from the definitions without training; do not force a toy
  training run whose results would misrepresent where the concept actually
  matters. Name the real deployment domains where each variant earns its keep
  instead.
