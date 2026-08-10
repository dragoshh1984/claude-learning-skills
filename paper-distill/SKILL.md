---
name: paper-distill
description: Distill a DL paper (arxiv link/PDF) into a concept map and per-concept notes that seed learning mini-projects in src/learning. Use when the user brings a paper to study, says "distill/extract/break down this paper", or starts a new learning topic from a publication.
---

# paper-distill

Turn a paper into the raw material for learning mini-projects: a paper-level
distillation plus one `notes.md` per selected concept. Downstream skills:
`concept-explainer` (HTML page) and `concept-code` (runnable PyTorch).

## Workflow

1. **Obtain the paper + code.** A campaign dir `src/learning/<campaign>/` is the
   home for one studied paper. Download the PDF to `<campaign>/paper.pdf` — the
   original paper IS committed as the campaign's doc. If an official
   implementation exists, shallow-clone it to `<campaign>/official/` (gitignored
   — `src/learning/**/official/` — re-pullable; record the clone command in
   `distillation.md`). Note the arxiv id, version, and date.
2. **Read the FULL paper** — every page, including appendices; that is where the
   derivations live. If a concept's math is defined in a *referenced* paper
   (e.g. the method builds on flow matching defined elsewhere), fetch and read the
   relevant sections of that reference too. Record exact section and equation
   numbers as you go — the explainer must cite them.
   Then **map the official code into `<campaign>/code_map.md`** — dispatch a
   subagent over the clone and demand exact `file:line` for every concept, plus
   short verbatim quotes of the load-bearing lines (the loss, the target, the
   detach, the mask). This file is the single most reused artifact of a
   campaign: every explainer quotes from it, and it prevents citing code from
   memory.

   **Hunt paper↔code discrepancies deliberately** — they are the best teaching
   material in the whole campaign, and no paper lists them. Ask specifically:
   - Does the code's time/index convention match the paper's equations?
     (Epona's code runs t=1 as clean data while the paper writes t=0 — and the
     paper's own equations are sign-inconsistent as a result.)
   - Which modules are DEAD? (`models/diffusion/` was never imported; the live
     math sat inline in each DiT. A reader starting there reads the wrong file.)
   - Are gradients cut where the prose implies they flow? (chain-of-forward is
     fully detached with a per-link optimizer step — data augmentation, not
     backprop through a rollout.)
   - What is built and never used, or configured off? (an unused attention mask
     with a hand-tuned bias; a reweighted loss that is unreachable.)
   - Do training and inference disagree? (uniform t in training vs a shifted
     schedule at inference; `is_video=False` bypassing the temporal decoder.)
   - Units and conventions that will bite (yaw in degrees, not radians).
3. **Draft the concept map.** Split into:
   - **General reusable concepts** — things that will recur across papers
     (e.g. flow matching, DiT blocks, CFG). These become `src/learning/<campaign>/concepts/<slug>/`.
   - **Paper-specific mechanisms** — the paper's own contributions/combinations.
     These live in the paper's material, referencing the general concepts.
   For each candidate concept, sketch: one-line definition, where in the paper
   (sections/eqs), and whether its mini-project flavor is **train** (small model,
   MNIST-scale) or **analytical** (math/graphs, no training).
4. **Grill the user** before writing anything to `src/learning/`. Use
   AskUserQuestion, ONE question at a time (the user answers with arrow keys).
   Cover at least: which concepts to create (and priority order), which the user
   already knows well vs wants depth on, train vs analytical flavor per concept,
   and anything paper-specific worth its own page. Recommend an answer for each.
5. **Write outputs** (only for concepts the user selected):
   - `src/learning/<campaign>/distillation.md` — paper summary, architecture
     walkthrough, the concept map (with links to concept folders), the
     concept→official-code map, what is paper-specific, key results/claims.
     The campaign's `index.html` hub is built only AFTER its concepts exist.
   - `src/learning/<campaign>/concepts/<slug>/notes.md` per concept — see below.
   REMEMBER: .md files are Claude-facing references. The user-facing
   deliverables are the concept `index.html` pages and `<slug>.py` files —
   a distillation pass is not "done for the user" until those follow.
6. **Update the canonical-source list** in `references/sources.md` (this skill's
   folder): for each topic, the papers/textbooks/guides an explainer must cite.
7. **Update repo `CLAUDE.md`** (concept table) and `docs/JOURNAL.md` (one entry:
   what was distilled, what was selected, why).

## notes.md structure (per concept)

```markdown
# <Concept name>
Status: notes | explainer-drafted | code-done | linked
Flavor: train | analytical
Source paper: <title, arxiv link, sections/eqs used>
Canonical sources: <list with links; sync with paper-distill references/sources.md>

## What it is (3-6 sentences)
## The math
  - Key equations verbatim with eq numbers, notation defined.
  - DERIVATION GAPS: steps the paper skips that the explainer must expand.
## Intuition / mental model
## Mini-project sketch
  - train: dataset, architecture size, what success looks like, runtime budget
  - analytical: what to compute/plot, over what ranges
## Visualization ideas (interactive canvas candidates)
## Decisions to ASK the user (never parked on a page — see study-iterate)
```

## Rules

- Never present a concept map built from the abstract alone — read the paper first.
- Equation numbers and section references are mandatory; "somewhere in section 3"
  is not a citation.
- Distinguish clearly what the paper *claims* vs what it *shows* — the explainer
  will inherit this framing.
- If a concept already exists in an earlier campaign, extend that page/notes
  with the new paper's perspective and link to it instead of duplicating.
