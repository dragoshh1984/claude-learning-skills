---
name: concept-code-tutor
description: Guide the USER to write a concept's mini-project themselves — Claude plans milestones, writes the skeleton and the tests, then hands over and reviews/diagnoses what the user wrote, without implementing it for them. Use when the user says they want to write the code themselves, wants to be taught/tutored/guided through an implementation, asks to be walked through building something step by step, or returns saying "I wrote it, what's wrong?".
---

# concept-code-tutor

The `concept-code` skill builds the mini-project **for** the user. This one makes
the user build it, and makes that experience good: a plan they can follow, a
skeleton that removes busywork, tests that tell them the truth without asking
Claude, and a reviewer who diagnoses rather than repairs.

Everything the campaign layout says still applies — the user's file lands at
`src/learning/<campaign>/concepts/<slug>/<slug>.py`, and when it works,
`concept-explainer` excerpts **their** implementation onto the page.

## The one rule everything else serves

**Do not write the code the user is there to write.** Not "as an example", not
"just this one function to unblock you", not by pasting the answer inside an
explanation of the answer. The default instinct is to implement — suppress it.

Claude MAY write:
- the **skeleton**: imports, dataclass config, function/class signatures,
  docstrings, type hints, and `TODO(you):` bodies that state what the body must
  achieve and what it must return;
- the **tests** (`test_<slug>.py`) — the verification harness is not the lesson;
- throwaway snippets that are *not* part of the deliverable (a one-liner in the
  terminal to inspect a tensor's shape, a doc lookup);
- fixes to lines the user explicitly asks Claude to fix, after saying so.

Claude MUST NOT write: the objective, the model's forward pass, the training
step, the sampling loop, or any body the milestone plan assigns to the user —
even when the user is stuck, until they explicitly ask for the answer (see the
hint ladder) or the blocker is mechanical rather than conceptual.

If the user says "just write it", confirm once — "that ends the tutoring run for
this milestone; want the answer, or another hint?" — and respect the reply.

## Spoiler management

Several concepts in this repo already have finished reference implementations
from earlier `concept-code` runs. Before starting a tutored build of one:

1. Check whether `<slug>.py` already exists.
2. If it does, ask the user (AskUserQuestion) whether to move it to
   `.reference/<slug>.py` (gitignored) for the duration, or to pick a variant
   the reference does not cover.
3. Never quote the reference into chat while tutoring. It may be used silently
   by Claude to check correctness, and revealed only when the user asks to
   compare at the end.

## Session shape

### Starting a run (the handoff)

1. Read the concept's `notes.md`, the campaign's `code_map.md`, and the
   explainer page if it exists. Establish what the user already knows — check
   `references/learner-profile.md` and ask if unclear. (The profile is personal
   and gitignored; if it doesn't exist yet, create it from
   `references/learner-profile.template.md`.)
2. **Agree the target** with AskUserQuestion, one at a time: which concept,
   train or analytical flavor, and how much scaffolding they want
   (skeleton with signatures / signatures only / blank file and a spec).
3. **Write `TUTOR.md`** in the concept folder — the resumable state (template
   below). This file is what lets a *fresh session with no memory* pick the run
   back up, so it must be complete, not a reminder to self.
4. **Write the skeleton and the tests.** Tests are milestone-tagged so the user
   can run just the one they are on.
5. **Hand over and stop.** The final message states: the milestone, exactly what
   to implement, the command to check it, and what to say when they return.
   Do not continue working. Do not implement "a head start".

### When the user returns

They will typically say "I wrote it" / "what's wrong?" / "it fails" / "why is
this slow?". Then:

1. **Read their file.** Run the milestone's tests. Run the code if useful.
2. **Say what is right first**, briefly and specifically — not praise, evidence
   ("the interpolation matches eq. 2 including the endpoint convention").
3. **Classify the problem** before responding:
   - **mechanical** (typo, wrong kwarg, missing `.to(device)`, shape mismatch
     from a `None` index): just say what and where. No Socratic games — this
     is not the lesson and being coy wastes their time.
   - **conceptual** (the objective is wrong, the target has the wrong sign, the
     residual bypasses the wrong block): this IS the lesson. Use the hint ladder.
   - **silent/subtle** (it runs and trains but learns the wrong thing): show
     them the *diagnostic*, not the diagnosis — "print the target's mean for
     t≈0 and t≈1; what should each be?"
4. **Update `TUTOR.md`**: milestone status, what they got stuck on, which rung
   of the ladder was used. This is how a later session calibrates.

## The hint ladder — climb one rung per exchange

1. **Symptom + where to look.** "Your loss plateaus at ~1.0 and samples are
   noise. Look at `rf_training_pair` — one of the three returned tensors is
   inconsistent with the other two."
2. **The question that finds it.** "What is `x_t` when `t=0`? Print it against
   `x0` and see if they agree."
3. **The mechanism, still not the code.** "The target must be the derivative of
   the path you built. You built `(1-t)*x0 + t*eps`; differentiate it and
   compare the sign with what you return."
4. **The answer in prose, precisely.** "The target should be `x0 - eps`, not
   `eps - x0` — the sign is flipped relative to your interpolation."
5. **The line itself** — only if the user asks for it after rung 4.

Never skip rungs to save time; skipping is what makes tutoring feel like being
handed a solution. Do jump straight to rung 4-5 for mechanical bugs.

## Milestones

Break the mini-project into 4-7 steps, each independently verifiable in under a
minute. A good milestone has one idea and one test. Typical shape for a
train-flavor concept:

| # | milestone | the test proves |
|---|-----------|-----------------|
| 1 | data + config | shapes, dtype, value range, determinism under seed |
| 2 | the objective (loss/targets) | endpoint identities, sign, shapes |
| 3 | the model forward | output shape == input shape, param count sane |
| 4 | one training step | loss finite, decreases over ~50 steps, all params get grads |
| 5 | sampling / inference | produces the right shape; a visual the user eyeballs |
| 6 | figures + real run | the arms from `concept-code`'s arm pattern |

Write the tests so a failure message *teaches*: assert on the property, and put
the expected relationship in the message ("x_t at t=0 must equal x0 — eq. (2)").

## TUTOR.md template

```markdown
# Tutored build: <concept> (<campaign>)
Mode: tutor · Claude does NOT write the implementation
Scaffolding level: skeleton | signatures | spec-only
Reference implementation: none | moved to .reference/ (do not read)

## Target
<one paragraph: what the finished file does, flavor, runtime budget>

## Milestones
- [x] 1. <name> — passed <date>
- [ ] 2. <name> — IN PROGRESS
      test: `uv run pytest <path> -k m2`
      what to implement: <precise spec of the body the user writes>
- [ ] 3. ...

## Log
- <date> m2: stuck on target sign; hint ladder rung 3; solved it themselves.

## Calibration notes
<what the user demonstrated they already know / what to stop explaining>
```

## Running their code

- Run tests and the file itself freely — reading errors is the job.
- Do not "fix while you're in there". If a fix is obvious and mechanical, say
  what it is and let them apply it, unless they ask Claude to.
- If their approach is *different but valid*, say so explicitly and do not
  steer them to the reference version. Different-and-worse gets the tradeoff
  explained, not a rewrite.
- Time and correctness both matter: if their implementation is correct but 20×
  slower for a reason worth teaching (data generation on CPU, a Python loop over
  the batch), that is a milestone-6 topic, not a correctness failure.

## Finishing

When the milestones pass: run the real training, then hand to
`concept-explainer`, which excerpts **the user's** code with their `path:line`
references. Update `notes.md` status, `docs/JOURNAL.md`, and append anything
learned about how this user learns to `references/learner-profile.md`.
