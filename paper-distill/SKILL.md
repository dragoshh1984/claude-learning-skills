---
name: paper-distill
description: Distill a DL paper (arxiv link/PDF) into a concept map and per-concept notes that seed learning mini-projects in src/learning. Use when the user brings a paper to study, says "distill/extract/break down this paper", or starts a new learning topic from a publication.
---

# paper-distill

Turn a paper into the raw material for learning mini-projects. This skill does
the paper-specific work — acquisition, full read, code mapping, discrepancy
hunting — then hands off to the shared engine in `distill-core` (a sibling
skill folder of this one) for the concept map, grill round, and `notes.md`
outputs. Downstream skills: `concept-explainer` (HTML page) and `concept-code`
(runnable PyTorch).

**Before starting, read `references/lessons.md` (this skill's folder)** — the
accumulated distillation lessons apply before any reading plan is made. New
reusable lessons from a distillation pass land there too.

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
3. **Run the shared engine.** Read `distill-core/SKILL.md` (sibling folder of
   this skill) and follow its workflow — concept map, grill round, per-concept
   `notes.md`, sources update, CLAUDE.md/journal update — with the paper +
   `code_map.md` as the source material.
4. **Write `src/learning/<campaign>/distillation.md`** (paper campaigns only) —
   paper summary, architecture walkthrough, the concept map (with links to
   concept folders), the concept→official-code map, what is paper-specific,
   key results/claims.

## Rules (on top of distill-core's)

- Never present a concept map built from the abstract alone — read the paper first.
- The paper↔code discrepancy hunt is not optional; an empty discrepancy section
  means it wasn't done, not that there are none.
