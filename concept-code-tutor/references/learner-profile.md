# Learner profile

Calibration for tutored builds: what the user has already demonstrated, so hints
start at the right rung and explanations skip what they own. Append after every
tutored milestone; keep it factual (what they did, not a grade).

## Established from the Epona campaign (2026-08-08)

Working style — these are strong signals, treat them as defaults:

- **Wants the real thing, not scaffolding.** Rejected roadmaps and skeleton
  pages outright ("do the actual full page wtf"). In tutoring terms: do not
  pad a milestone with ceremony; give the spec and get out of the way.
- **Reads critically and pushes back with a hypothesis.** Challenged the
  paper-vs-code convention flip by proposing a specific alternative explanation
  ("are you sure you're not mixing trajectory with image generation?"), and was
  right to push a second time. Expect and welcome disagreement; bring evidence,
  not authority.
- **Wants the underlying reason, not the fix.** Repeatedly asked for deeper
  explanation rather than a patch. Start hints at rung 2-3, not rung 1.
- **Cares about visual/structural clarity** — asked for diagrams with every skip
  connection drawn. Diagram-first explanations will land well for architecture
  bugs (draw the wrong wiring next to the right wiring).
- **Prefers being asked over being guessed at**, one question at a time with
  options and a recommendation.

Technical ground already covered (do not re-explain from scratch; reference it):

- rectified flow / flow matching: the objective, the clock conventions and why
  they differ between the Epona paper, its code, and Lipman.
- adaLN-Zero, QK-Norm, 2D RoPE, dual- vs single-stream DiT blocks.
- latent generation, VQ vs continuous latents, the LDM scale factor.
- AR world models, the conditional-mean/blur argument, exposure bias and
  chain-of-forward including the detach question.
- factorized spatiotemporal attention, causal masks, KV-cache accounting.

Unknown / not yet observed:

- how they write PyTorch when unassisted — idioms, error patterns, where they
  slow down. **Fill this in after the first tutored milestone.**
