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

**A concept/topic with no single paper** → `concept-distill`:

```
/concept-distill normalization layers
```

or *"I want to study optimizers, distill the concept"*.

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

## More details

Everything else lives in [AGENTS.md](AGENTS.md) — written for AI agents, not
humans. Point your agent at this repo and say *"install these skills"* or
*"tell me what these skills do"*: AGENTS.md contains the full pipeline, a
per-skill reference, the install/verify procedure, and what the skills expect
from a host project.
