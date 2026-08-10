# paper-distill — accumulated lessons

## Read the code as carefully as the paper

The Epona campaign's most valuable teaching material came from the gap between
the two, not from either alone. A subagent sweep of the official clone produced
`code_map.md` in one pass and paid for itself on every page afterwards:

- the released code's time convention is **flipped** relative to the paper's
  equations — and under the paper's own clock, eqs. (1)–(3) are sign-
  inconsistent (the target is −dx/dt). The user pushed on this twice and was
  right both times: the paper needs correcting, not just annotating.
- `models/diffusion/` is dead code; the live rectified-flow math is inline in
  each DiT. A reader who starts in the obviously-named directory reads a file
  that never runs.
- chain-of-forward is intermittent (1 step in 10), fully `.detach()`-ed, and
  takes a separate optimizer step per link — so it is on-policy data
  augmentation, not backprop through a rollout, which the prose implies.
- an entire attention mask is built with a hand-tuned bias and never used;
  a dynamics-reweighted loss is implemented but unreachable.
- one test script hard-codes `is_video=False`, silently bypassing the temporal
  decoder that the paper added to fix flicker.

None of these are in the paper. All of them are worth a paragraph.

## Distillation hygiene

- Read every page including appendices before drafting the concept map; the
  block-level architecture usually lives only in the supplementary figure.
- Record section AND equation numbers as you go — "somewhere in section 3" is
  not a citation and cannot be re-found cheaply later.
- Separate what the paper **claims** from what it **shows**. Epona's
  "learns traffic knowledge" is a qualitative figure; its FVD and PDMS numbers
  are benchmarked. The explainer inherits this framing.
- Note the numbers a reader should remember (FVD 82.8, PDMS 86.2, 78.1→86.2 for
  joint training) — they anchor the campaign hub page.
- Split concepts into *reusable* (flow matching, DiT — they will recur in the
  next campaign) and *paper-specific* (the decoupled TrajDiT/VisDiT design).
  Reusable concepts get folders; paper-specific material stays in the
  distillation and the hub page.

## Deliverable discipline

The .md files are Claude-facing scaffolding. A distillation pass is **not done
for the user** until the concept pages and runnable code exist — the user does
not read markdown. Ship `paper.pdf` committed, `official/` cloned and
gitignored, and move straight on to `concept-code` / `concept-explainer`.
