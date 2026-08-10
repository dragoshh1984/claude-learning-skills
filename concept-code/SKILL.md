---
name: concept-code
description: Build the runnable single-file PyTorch mini-project for a DL concept in src/learning/<campaign>/concepts/<slug>/ — either a small training run (MNIST-scale, minutes on the local GPU) or an analytical/math study (graphs and cost models, no gradients). Use after paper-distill produced notes.md with a mini-project sketch, or when the user asks for a minimal working example of a concept.
---

# concept-code

Produce `src/learning/<campaign>/concepts/<slug>/<slug>.py`: one file, minimal
but production-quality, that demonstrates the concept **for real** — it trains,
it produces figures, and the explainer quotes it verbatim. Write it to be read.

**Before starting, read `references/lessons.md` (this skill's folder)** — the
accumulated hard-won rules from previous mini-projects apply before any new
code is written. The file is local and gitignored (personal study data); if it
doesn't exist yet, skip and create it with the first lesson.

> If the user wants to write the code themselves — "teach me", "I'll implement
> it", "guide me through it" — use **`concept-code-tutor`** instead. That skill
> forbids Claude from writing the implementation; this one requires it.

## The arm pattern — the single most important rule

A mini-project is not a demo, it is a **controlled experiment**. Build it as
two or more arms that share *everything* except the one thing being taught:

    --cond {adaln, concat}     conditioning mechanism      (dit)
    --head {l2, flow}          objective                   (ar_world_models)
    --arm {tf, cof-detach, cof-grad}   training procedure  (exposure_bias)
    --space {pixel, latent}    where generation happens    (latent_generation)

Same data, same backbone, same seed, same step budget, same optimizer. One flag
apart. That is what makes the resulting number a *finding* rather than an
anecdote — and it is what lets the page state a conclusion honestly.

**State any confound you could not remove.** adaLN's modulation MLPs added 0.96M
parameters, so that arm was not capacity-matched; the page says so and cites the
paper's properly-controlled version. An unstated confound is a lie of omission.

## Two flavors

- **train** — a real (small) training run: MNIST-scale data, an architecture
  just big enough to show the concept, minutes not hours.
- **analytical** — no gradients: compute and plot the math itself (cost models,
  masks, activation curves, schedules). Do not force a training loop onto a
  concept that does not need one; a measured benchmark can be the deliverable.

## File shape

- Single file, argparse subcommands: `train` (per arm), `sample`/`eval`, and
  **`figures`** (exports curated PNGs into `assets/` for the explainer).
- Config as a dataclass at the top; every hyperparameter named, none buried.
- Seeded and reproducible: one `--seed`, set torch/numpy/random.
- Device auto-detect, dtype explicit. Plain PyTorch loops — no Lightning: the
  loop mechanics ARE the lesson.
- Section banner comments `# ── <name> ──────` dividing the file into the units
  the explainer will excerpt; each readable in isolation.
- Type hints, explicit names, early failure. Comments only where the math↔code
  mapping isn't obvious — then cite the paper's equation number.

## Output contract (the explainer depends on this)

```
outputs/<arm>/config.json        the exact dataclass, so a run is rerunnable
outputs/<arm>/train_log.jsonl    appended + flushed every log_every steps
outputs/<arm>/model.pt
outputs/<arm>/summary.json       {params, wall_s, ms_per_step, ...}
assets/*.png                     curated, committed, small
assets/*.json                    the numbers behind each figure
```

`outputs/` and the shared `data/` dir are gitignored; `assets/` is committed.
Emit **summary.json and a numbers JSON next to every figure** — the page quotes
exact values ("0.136 vs 0.144", "2.65 ms/step") and must never re-derive them by
eye from a plot.

## Smoke test before any full run

Not optional, and not just "does it run":

1. shapes out == shapes in, for every arm;
2. loss is finite, and one optimizer step succeeds;
3. **every parameter receives a gradient** — `assert all(p.grad is not None ...)`.
   This caught a real bug: the L2 head carried an unused timestep MLP. The fix
   was to delete the dead module, not to loosen the assertion;
4. one sample / one figure is produced;
5. for analytical work, assert the property you are claiming (causality leak
   == 0.0, shapes after the reshape choreography, etc.).

## Running the work

- Assume the box may be busy with the user's own jobs; check before launching.
- Launch arms **in parallel in the background**, then write the explainer prose
  while they train. Do not idle waiting on a run.
- Generate toy data **on the GPU** (`affine_grid`/`grid_sample` for moving
  sprites) so data generation never becomes the bottleneck.
- Share one dataset download per campaign (`src/learning/<campaign>/data/`).

## Cross-concept reuse

Concepts build on each other. Prefer importing the previous concept's world and
backbone over copying them when the point is a *controlled comparison* — an A/B
is only meaningful if both arms share exactly the same dynamics and architecture
(`exposure_bias.py` imports `ar_world_models.py` for precisely this reason).
Copy instead when the file must read standalone as a lesson.

## Workflow

1. Read `notes.md` (mini-project sketch), the campaign's `code_map.md`, and the
   explainer page if it exists.
2. **Survey tooling** — check whether a better library exists and PROPOSE
   additions before adding. Keep deps minimal, justify each.
3. **Bring design decisions to the user** (AskUserQuestion, ONE question at a
   time, arrow-selectable, with a recommendation): flavor, dataset/architecture
   scale, which arms to run, what the figures should show. Never park these
   questions in a file — ask, then build the chosen answer.
4. Write the file. Smoke-test. Launch arms. Export figures.
5. **Design for a surprise.** The best pages came from measured results that
   contradict intuition (L2 winning MSE while producing unusable blur; VQ
   costing 2.2× at equal compression; 28× predicted vs 4× measured speedup).
   Set the experiment up so it *can* surprise you, then report what happened.
6. Update `notes.md` status, `docs/JOURNAL.md`, and tell `concept-explainer`
   that excerpts and `path:line` references need re-syncing.
7. Reusable lessons → `references/lessons.md`; structural changes amend this file.

Learning code is EXEMPT from the research-campaign evaluation contract (no
folds, cohorts, or leaderboards). Required instead: seeded, reproducible, a loss
curve for anything that trains, and honest reporting of negative results.
