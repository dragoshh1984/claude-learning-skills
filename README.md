# claude-learning-skills

Claude Code skills for concept learning — turning papers and DL concepts into
mini-projects, explainer pages, and an iterative study loop.

## Quick start

Two entry points, depending on what seeds the study:

**A paper** → `paper-distill`:

```
/paper-distill https://arxiv.org/abs/2406.XXXXX
```

or just say it naturally: *"I want to study this paper: \<link\>, distill it"*.
It downloads the PDF, reads it fully, clones the official code, maps concepts to
exact `file:line`, then grills you one question at a time about which concepts
you want, priority, and whether each should be a **train** mini-project
(MNIST-scale run) or **analytical** (math/plots, no training). Only then does it
write `distillation.md` + one `notes.md` per selected concept.

**A concept/topic with no single paper** → `concept-distill`:

```
/concept-distill normalization layers
```

or *"I want to study optimizers, distill the concept"*. Instead of one paper it
gathers and reads the canonical sources (the defining papers of each variant,
textbook chapters), places the work in a topic campaign (e.g. `fundamentals/`),
then runs the same grill round and writes the same `notes.md`.

Both delegate their shared back half — concept map → grill → notes →
bookkeeping — to `distill-core`.

## Skills

| Skill | Role |
|---|---|
| `paper-distill` | Entry point for a paper: acquisition, full read, official-code map, paper↔code discrepancy hunt → `distill-core` |
| `concept-distill` | Entry point for a topic with no paper: canonical-source gathering, topic-campaign placement → `distill-core` |
| `distill-core` | Shared engine (not invoked directly): concept map → grill round → per-concept `notes.md` → bookkeeping |
| `concept-code` | Build the runnable single-file PyTorch mini-project for a concept (Claude implements) |
| `concept-code-tutor` | Same mini-project, but the user writes it — Claude plans milestones, writes skeleton + tests, reviews |
| `concept-explainer` | Self-contained HTML explainer page: KaTeX math, canvas visualizations, code excerpts, real training outputs |
| `study-iterate` | Post-campaign mode — questions, more examples/depth, answers folded back into pages/code |
| `grilling` | Relentless one-question-at-a-time interview engine (used by the distill grill rounds) |
| `grill-me` | `/grill-me` launcher for a `grilling` session |

Workflow: `paper-distill` **or** `concept-distill` → `concept-code` **or**
`concept-code-tutor` → `concept-explainer` → `study-iterate`.

## Attribution

`grilling` and `grill-me` are taken from Matt Pocock's skills collection:
<https://github.com/mattpocock/skills/tree/main>.

## Install (global)

Skills are made available to every project by symlinking into `~/.claude/skills/`:

```bash
git clone <remote-url> ~/projects/claude-learning-skills
for s in paper-distill concept-distill distill-core concept-code concept-code-tutor \
         concept-explainer study-iterate grilling grill-me; do
  ln -s ~/projects/claude-learning-skills/$s ~/.claude/skills/$s
done
```

## Conventions

The skills write learning artifacts to `src/learning/<campaign>/concepts/<slug>/`
relative to whatever project they run in. `concept-explainer` vendors its own
KaTeX/highlight.js assets, so pages are fully offline.

## What the skills expect from a host project

- A `src/learning/` directory (the skills create campaign/concept folders
  inside it).
- These gitignore entries — heavy or re-pullable artifacts never get committed
  (curated small PNGs in `concepts/*/assets/` are the committed exception):

  ```gitignore
  src/learning/**/outputs/     # raw run outputs/checkpoints
  src/learning/**/official/    # clones of papers' official code (re-pullable)
  src/learning/**/data/        # dataset downloads (e.g. shared MNIST)
  src/learning/**/.reference/  # tutored builds: reference impls parked out of sight
  src/learning/**/paper.pdf    # papers are linked, never committed
  ```

- Bookkeeping targets, updated when present: `docs/JOURNAL.md` (one entry per
  session) and a concept table in the project's `CLAUDE.md`.
- Tooling: Python via `uv` (mini-projects, page builds), `node` (page
  validation), headless Chrome (visual verification).

**Self-updating references (local, gitignored).** As the skills work they
accumulate personal study data next to themselves — `references/lessons.md`
(hard-won rules, read before each run and appended to after), distill-core's
`references/sources.md` (canonical-source bibliography per topic), and
concept-code-tutor's `references/learner-profile.md` (how you learn;
bootstrapped from the committed `learner-profile.template.md`). All of these
are gitignored: the repo ships concept-free, and each clone grows its own.
