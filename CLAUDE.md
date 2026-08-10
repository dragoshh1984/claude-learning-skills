# CLAUDE.md — claude-learning-skills

Skill suite for concept learning (see README). The skills are symlinked into
`~/.claude/skills/` and run inside whatever host project the user is studying
in — this repo is only edited when maintaining the skills themselves.

## Rules for editing this repo

- **The repo ships concept-free.** No campaign-, paper-, or topic-specific
  content gets committed. Accumulated study data (each skill's
  `references/lessons.md`, distill-core's `references/sources.md`,
  concept-code-tutor's `references/learner-profile.md`) is gitignored and
  local-only. When a SKILL.md needs an example, keep it generic enough to
  teach the pattern, not the studied subject.
- **No project-local paths.** Skills run globally; reference their own tooling
  via `~/.claude/skills/<skill>/...`, never `.claude/skills/...`, and write
  outputs relative to the host project (`src/learning/...`).
- **Cross-skill references are by sibling folder** (e.g. paper-distill →
  `distill-core/SKILL.md`); both the repo layout and the symlink farm keep
  siblings adjacent, so the reference resolves either way.
- **When adding/renaming a skill**: update the README's table, workflow line,
  and the install symlink loop, and symlink it into `~/.claude/skills/`.
- **Structural lessons** about how a skill should work go into its SKILL.md;
  study-specific lessons go into the local `references/lessons.md`. If a rule
  mentions a paper or campaign by name, it is probably the latter.
- **Never commit — the user decides.**
