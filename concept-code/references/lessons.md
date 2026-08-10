# concept-code — accumulated lessons

Concrete things that went right or wrong while building the Epona campaign's six
mini-projects. Each is a rule earned, not a preference.

## Experiment design

- **One flag apart, or it proves nothing.** Every mini-project that produced a
  quotable result was built as arms sharing data/backbone/seed/budget with a
  single differing flag. Every arm's number went into the page.
- **The metric can be the trap.** On Moving-MNIST the L2 head beat the flow head
  on MSE at *every* rollout depth while producing visually unusable smears —
  because MSE is minimized by the conditional mean. Always look at the samples
  next to the metric, and when they disagree, that disagreement is the lesson.
- **Make the world genuinely stochastic when teaching multimodality.** Two
  bouncing digits are nearly deterministic given a few frames; adding a random
  velocity re-kick (p=0.1/frame) is what made the blur theorem observable at all.
- **Negative results are deliverables.** Chain-of-forward did not help on our
  toy. Reported as-is with four candidate explanations and the falsifiers,
  rather than tuned until it agreed with the paper. The most useful explanation
  was structural: our rollouts never collapsed, so there was no disease to cure.
- **Theory over-promises; measure it.** The factorized-attention FLOPs ratio
  predicted 28.4× at T=32 and the GPU delivered 4.0× — the factorized path was
  launch/bandwidth-bound (constant ~0.48 ms across a 32× workload range). A
  FLOPs ratio is an upper bound; say so and show the gap.

## Mechanics

- **Assert every parameter gets a gradient** in the smoke test. It caught a dead
  `t_mlp` in the L2-head arm (the head has no notion of a noise level). Right
  fix: don't build the module for that arm. Wrong fix: relax the assertion.
- **Emit numbers as JSON beside every figure.** Pages quote exact values; nobody
  should read "0.136" off a plot. `summary.json` with params/wall_s/ms_per_step
  makes the page's tables trivial and auditable.
- **JSONL logs flushed as you go** mean a crashed run is still analyzable.
- **Render toy data on the GPU.** Moving-MNIST via `affine_grid` + `grid_sample`
  keeps data generation off the critical path and supports subpixel motion for
  free; a Python paste loop would have dominated the step time.
- **Latent spaces are not unit-variance.** Ours measured σ = 4.98, which would
  wreck a diffusion noise schedule — hence LDM's scale factor. Measure it, log
  it, divide by it, multiply back before decoding.
- **Watch what a comparison actually includes.** Latent-space flow trained 5.4×
  faster per step, but that excludes the autoencoder's own training. Fair only
  because the AE is trained once and reused — say that explicitly.

- **Never publish a wall-clock benchmark measured under contention.** The
  latent-vs-pixel speedup was first taken with four other jobs on the GPU and
  read 5.4×; re-measured on an idle GPU the small job reproduced exactly
  (2.65 → 2.63 ms/step) while the big one dropped 14.28 → 10.32, because the
  larger job suffers more from sharing. True figure: 3.9×. Parallel arms are
  fine for *training*; they are not fine for *timing*. Re-run timed arms alone,
  or report only ratios you have measured in isolation.

## Process

- **Never chain jobs with `until ! pgrep -f "<pattern>"`.** `pgrep -f` matches
  full command lines, and the waiting shell's own command line contains the
  pattern — so it matches itself and the loop never exits. This silently stalled
  a whole retraining batch: the GPU sat at 0% for many minutes while the logs
  looked merely "slow", and it was the USER who noticed the idle hardware, not
  me. Sequence jobs by launching the next batch after the previous one's
  completion notification arrives, or match on something that cannot appear in
  the waiter (a pidfile, `pgrep -x python`, a sentinel file the job touches).
- **Idle hardware is a symptom, check it early.** When a background run looks
  slow, `nvidia-smi` + `pgrep -c` distinguishes "training" from "hung" in one
  command. A log stuck on its first line for minutes is usually not buffering.


- **Launch arms in the background and write prose while they train.** Six
  concepts trained in the time it took to author the pages; serializing them
  would have doubled the session.
- **Check the GPU is free first** — the box may be running the user's jobs.
- **Cross-concept imports are the honest choice for an A/B**: `exposure_bias.py`
  imports the world and backbone from `ar_world_models.py`, guaranteeing the
  arms cannot silently diverge. Duplicate only when standalone readability wins.
- **Docstring edits shift line numbers**, which invalidates every `path:line`
  reference on the explainer page. Re-grep after any edit, however cosmetic.
