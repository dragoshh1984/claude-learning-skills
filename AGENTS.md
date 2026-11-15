# AGENTS.md — agent-facing manual for this skill suite

This file is written for AI agents (Claude Code or compatible). If a user
points you at this repo and asks to "install these skills", "explain what they
do", or "use them to study X", this file contains everything you need. The
README is the short human summary; this is the complete reference.

## What this suite is

A pipeline of Claude Code skills for deep, durable studying of deep-learning
material. A study "campaign" turns a paper or a topic into three kinds of
artifacts inside the user's host project, under
`src/learning/<campaign>/concepts/<slug>/`:

- `notes.md` — Claude-facing distilled notes per concept (scaffolding, not a
  user deliverable)
- `<slug>.py` — OPTIONAL: a runnable single-file PyTorch mini-project (a
  controlled experiment, not a demo), built only when the user says yes at the
  mini-project gate
- `index.html` — a self-contained long-form explainer page (real KaTeX math,
  interactive canvas visualizations, verbatim code excerpts, real training
  outputs)

The user-facing deliverables are the HTML pages and the runnable code. The
markdown files are working references for the agent.

## The pipeline

```
paper-distill  (seed: a paper)  ─┐
                                 ├─► distill-core ─► notes.md per concept
concept-distill (seed: a topic) ─┘        │
                                          ▼
                    concept-code  OR  concept-code-tutor   ─► <slug>.py
                                          │
                                          ▼
                    concept-explainer                      ─► index.html
                                          │
                                          ▼
                    study-iterate   (default mode ever after)
                                          │
                                          ▼
                    test-me         (recap tests + grading, any time)
```

## Per-skill reference

### paper-distill — entry point when the seed is a paper
Trigger: user brings a paper (arxiv link/PDF) to study; "distill this paper".
Does the paper-specific work: downloads the PDF (local only, never committed),
reads the FULL paper including appendices, shallow-clones the official
implementation to `<campaign>/official/`, maps every concept to exact
`file:line` in `<campaign>/code_map.md`, and deliberately hunts paper↔code
discrepancies (flipped conventions, dead modules, detached gradients — the
best teaching material). Then delegates to `distill-core` and finally writes
`<campaign>/distillation.md`.

### concept-distill — entry point when the seed is a topic, no single paper
Trigger: "I want to study/learn <concept>" (normalization, optimizers,
attention variants…). Places the work in a topic campaign (prefers extending
an existing one over creating one per concept), gathers and actually reads the
canonical sources (the defining paper of each variant — never from memory),
then delegates to `distill-core`. Topic pages must find the organizing idea
that unifies the variants and answer WHY / WHERE used / where introduced /
the math for each.

### distill-core — shared engine, not invoked directly
Both entry points delegate here. Drafts the concept map (general reusable
concepts vs campaign-specific mechanisms), interviews the user before writing
anything (AskUserQuestion, ONE question at a time: which concepts, priority,
the mini-project gate: none / analytical / train, with a short follow-up only
on a yes), writes `notes.md` per selected concept, and does
the bookkeeping (sources list, host CLAUDE.md concept table, journal).

### concept-code — Claude builds the mini-project (optional)
Runs only when the user opted in at the gate; its first question is "you decide
the details / ask me / I'll write it". Input: a concept's `notes.md`. Output: one file,
`concepts/<slug>/<slug>.py`, production-quality, seeded and reproducible.
Built as a controlled experiment: two or more arms sharing
data/backbone/seed/budget, one flag apart. Two flavors: **train** (small real
training run, MNIST-scale, minutes on a local GPU) or **analytical**
(math/graphs, no gradients). Emits figures to `assets/` and numbers as JSON so
pages quote exact values.

### concept-code-tutor — the USER builds the mini-project
Same target as concept-code, but Claude plans milestones, writes the skeleton
and the tests, then hands over — reviews and diagnoses what the user wrote
without implementing it for them. Resumable state lives in the concept's
`TUTOR.md`. Use when the user says "teach me", "I'll write it", "guide me".

### concept-explainer — the explainer page
Input: `notes.md` + the concept's code. Output: a self-contained
`index.html` (all CSS/JS/fonts inlined from this skill's `assets/`; no CDN).
Authored via a committed `fragment.html`, built with `assets/build_page.py`,
validated with `assets/validate_page.js` (node), excerpt line-refs checked
with `assets/check_excerpts.py`, and verified by headless-Chrome screenshot.
Diagrams are required, with every skip/residual connection drawn.

### study-iterate — the default mode once a campaign exists
Every later question ("why…", "add an example of…", "visualize…", "I don't
get…") is answered in chat AND folded back into the pages/code where durable.
Pages are edited via their `fragment.html` source and rebuilt — never by
editing `index.html` directly.

### test-me — recap tests and grading
Builds a test page in `src/learning/recap/<YYYY-MM-DD>-<slug>/` over any scope
(a concept page, a family, a topic, several paths, the session's questions, or
the learner question log), shaped by `focus` (`only` / `related` / `mixed` /
`none` relative to what the user asked) and `answers` (`mix` = 70% clickable
choices + 30% written by default, `choice`, `text`). Each question has a Submit;
every Submit overwrites `answers.md` in the test folder (File System Access API;
download fallback). "grade test <id>" reads it and corrects wrong answers,
completes partial ones, and updates the learner logs. The answer key stays in
`test.json`, never in the page. Builder: `test-me/assets/build_test.py`.

### grilling / grill-me — interview engine
A relentless one-question-at-a-time interview (AskUserQuestion, recommended
option first) used by the distill grill rounds; `/grill-me` runs one
standalone. From Matt Pocock's collection (see README attribution).

## Install procedure

```bash
git clone <remote-url> ~/projects/claude-learning-skills
for s in paper-distill concept-distill distill-core concept-code concept-code-tutor \
         concept-explainer study-iterate test-me grilling grill-me; do
  ln -s ~/projects/claude-learning-skills/$s ~/.claude/skills/$s
done
```

Notes for the installing agent:
- The clone path is the user's choice; the symlinks must point wherever it is.
- Skip (or ask about) any name that already exists in `~/.claude/skills/`.
- Verify: each skill should appear in the available-skills listing of a new
  session, and `ls -la ~/.claude/skills/` should show the nine links.
- The skills reference each other as sibling folders (paper-distill reads
  `distill-core/SKILL.md`), which resolves both in the repo and through the
  symlink farm — do not install a subset that breaks a delegation pair
  (paper-distill/concept-distill require distill-core).

## What the skills expect from a host project

The skills run inside whatever project the user studies in and create
`src/learning/<campaign>/concepts/<slug>/` there.

- Gitignore these in the host project (heavy or re-pullable; curated small
  PNGs in `concepts/*/assets/` are the committed exception):

  ```gitignore
  src/learning/**/outputs/     # raw run outputs/checkpoints
  src/learning/**/official/    # clones of papers' official code (re-pullable)
  src/learning/**/data/        # dataset downloads (e.g. shared MNIST)
  src/learning/**/.reference/  # tutored builds: reference impls parked out of sight
  src/learning/**/paper.pdf    # papers are linked, never committed
  ```

- Bookkeeping targets, updated when present: `docs/JOURNAL.md` (one entry per
  session) and a concept table in the host project's `CLAUDE.md`.
- Learner memory (used by `test-me`, appended by `study-iterate`):
  `docs/learner/questions.md` (every user question, by topic path → sub-topic,
  with the difficulty it revealed and a status) and `docs/learner/tests.md`
  (grading results). The host `CLAUDE.md` may name other paths.
- Tooling: Python via `uv` (mini-projects, page builds), `node` (page
  validation), headless Chrome (visual verification), a CUDA GPU for `train`
  flavor mini-projects (analytical flavor needs none).

## Self-updating references (local, gitignored)

As the skills work they accumulate personal study data next to themselves.
These files are gitignored — the repo ships concept-free, and each clone grows
its own; create each on first use:

- `<skill>/references/lessons.md` (paper-distill, concept-code,
  concept-explainer) — hard-won rules; read before each run, appended after.
- `distill-core/references/sources.md` — canonical-source bibliography per
  topic, grown with every campaign.
- `concept-code-tutor/references/learner-profile.md` — how this user learns;
  bootstrap from the committed `learner-profile.template.md`.

## Maintaining this repo

Rules for editing the skills themselves are in `CLAUDE.md` (concept-free
content, no project-local paths, sibling-folder references, README/AGENTS
kept in sync).
