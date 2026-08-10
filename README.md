# claude-learning-skills

Claude Code skills for concept learning — turning papers and DL concepts into
mini-projects, explainer pages, and an iterative study loop.

## Skills

| Skill | Role |
|---|---|
| `paper-distill` | Distill a paper (arxiv/PDF) into a concept map + per-concept notes that seed mini-projects |
| `concept-code` | Build the runnable single-file PyTorch mini-project for a concept (Claude implements) |
| `concept-code-tutor` | Same mini-project, but the user writes it — Claude plans milestones, writes skeleton + tests, reviews |
| `concept-explainer` | Self-contained HTML explainer page: KaTeX math, canvas visualizations, code excerpts, real training outputs |
| `study-iterate` | Post-campaign mode — questions, more examples/depth, answers folded back into pages/code |

Workflow: `paper-distill` → `concept-code` **or** `concept-code-tutor` → `concept-explainer` → `study-iterate`.

## Install (global)

Skills are made available to every project by symlinking into `~/.claude/skills/`:

```bash
git clone <remote-url> ~/projects/claude-learning-skills
for s in paper-distill concept-code concept-code-tutor concept-explainer study-iterate; do
  ln -s ~/projects/claude-learning-skills/$s ~/.claude/skills/$s
done
```

## Conventions

The skills write learning artifacts to `src/learning/<campaign>/concepts/<slug>/`
relative to whatever project they run in. `concept-explainer` vendors its own
KaTeX/highlight.js assets, so pages are fully offline.
