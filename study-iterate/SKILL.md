---
name: study-iterate
description: The default post-campaign mode for src/learning — the user asks questions, requests more examples/visualizations/depth about a studied paper or concept, and every answer both lands in chat AND is folded back into the campaign's HTML pages / code where durable. Use whenever the user asks anything about an existing learning campaign (a "why/how/what-if" question, "add an example of X", "visualize Y", "I don't get section Z", "go deeper on W").
---

# study-iterate

After `paper-distill` → `concept-code` → `concept-explainer` produce a campaign,
the campaign is never "done" — it enters this mode. The user probes; the
artifacts grow. The failure mode to avoid: great answers in chat that evaporate,
while the pages stay frozen.

## The contract

1. **Answer in chat FIRST.** The user asked a question; give the direct answer
   immediately — math, numbers, file:line from `third_party/`, whatever it takes.
   Do not make them wait for a page rebuild to learn the answer.
2. **Then fold it back.** Decide where the answer's durable form belongs and
   update it in the same turn:

| the request was… | it lands in… |
|---|---|
| conceptual question the page should have answered | patch that page section (the gap IS the finding) |
| question about the paper's claims/details | answer from `paper.pdf` + cite; add to page if it closes a real gap |
| question about the real implementation | answer from `code_map.md` / `third_party/` with file:line; extend `code_map.md` if it required new digging |
| "add an example / visualization / interactive" | `concept-explainer` doctrine: extend the fragment, rebuild, validate |
| "make the code show X" / new variant | `concept-code` doctrine: extend the `.py`, rerun figures, re-sync excerpts |
| a question that reveals a MISSING concept | propose a new concept folder (one AskUserQuestion, then build it) |
| "I want to write this one myself" / "teach me to build X" | hand off to `concept-code-tutor` — Claude stops implementing and starts tutoring |
| the user returns mid-tutored-build ("I wrote it, what's wrong?") | `concept-code-tutor` review mode; read `TUTOR.md` first, never patch silently |
| pure curiosity, no durable value | chat only — not everything needs to land; say so |

3. **Small asks get action, not grilling.** The grill rounds belong to the big
   skills. Here, act on the obvious interpretation and state what you assumed;
   reserve AskUserQuestion for genuine scope forks (e.g. "new page or new
   section?").

## Mechanics (the source-of-truth rule)

- Each page's SOURCE is the committed `fragment.html` next to it
  (`concepts/<slug>/fragment.html`, campaign hub `<campaign>/fragment.html`).
  **Never edit `index.html` directly** — edit the fragment, then rebuild:
  `uv run python ~/.claude/skills/concept-explainer/assets/build_page.py
  --content <dir>/fragment.html --title "<title>" --out <dir>/index.html
  [--images-root <dir>]`
- Validate after every rebuild: `node ~/.claude/skills/concept-explainer/assets/validate_page.js <page>`
  (KaTeX dist copy required next to it — see lessons.md).
- If the `.py` changed: rerun its `figures`, re-check every excerpt + line
  reference on the page against the new file before rebuilding.
- Batch: if one session touches a page several times, rebuild/validate once at
  the end, not per edit.

## Bookkeeping (cheap, but every time something durable changed)

- `notes.md` status line if a concept's state advanced.
- Repo `CLAUDE.md` concept table on status changes only.
- `docs/JOURNAL.md` one line per session of iteration (what was asked, what landed).
- **Every user question → the learner question log** (host `CLAUDE.md` says
  where; default `docs/learner/questions.md`), under its topic path and
  sub-topic: date, the question, the difficulty it revealed, where it was
  answered, status `open`. `test-me` builds tests from this log.
- A reusable lesson → the relevant skill's `references/lessons.md`.

## User corrections are permanent

When the user corrects the *way* work is done — not the content — that
correction is a rule, not a one-off fix. Write it into the owning skill in the
same turn, phrased as a non-negotiable. Corrections banked this way so far:

- questions go to the user interview-style (AskUserQuestion, one at a time,
  arrow-selectable, with a recommendation) — never a wall of prose questions,
  and never parked in a file;
- ship finished pages, never roadmaps or "planned" sections;
- .md files are Claude-facing scaffolding; the deliverables are HTML and code;
- name every parallel stream explicitly, even when the code is identical;
- diagrams are required, with every skip connection drawn;
- pull the paper's official repo and link explanations to the real implementation;
- survey the best available tool for a job and propose it rather than defaulting;
- **general explanations use the deployed system**, at the paper's real sizes
  and with its real measurements; hand-built toys live only in a separate toy
  section after the whole explanation, each saying what it changes (full rule
  in `concept-explainer` SKILL.md). Iterating must not add a toy to a concept
  section;
- **every page has a closed jargon glossary** after the notation (aliases +
  code names for the terms the page uses, kept short; `concept-explainer`
  SKILL.md). When iterating on a page that lacks one, add it;
- **the mini-project is optional** — a page may have none (`Mini-project: none`
  in `notes.md`); never add one while iterating unless the user asks, and then
  run the gate's short follow-up (`distill-core`). When a page has one,
  **it lives at the END of the page, whole and uninterleaved** —
  concept explanation (math, diagrams, interactives, `third_party/` code) first,
  then ONE contiguous experiment block (our `.py` excerpts, our figures, our
  result tables, running it, extensions). Iterating on a page must never
  reintroduce a measurement, one of our figures, or a snippet of our code into
  the concept half; cite it forward as "measured in §N" instead. Full statement
  in `concept-explainer` SKILL.md, first non-negotiable.

The test for whether a lesson is banked: a fresh session with no memory of this
conversation would do the right thing by reading the skill alone.

## Verify before claiming

Anything shipped to the user gets checked by the strongest cheap method
available, in this order: build → `validate_page.js` → headless-browser render →
read the numbers back out of the JSON. Syntax checks do not catch an interactive
whose readout contradicts its own output, and a diff does not catch a slider
still painted browser-blue. Both happened; both were caught by rendering.

## Tone of the loop

- Treat repeated iteration as the NORMAL state, not rework; never present a
  page as final.
- If the user's question exposes an error on a page (wrong equation, stale
  excerpt, misleading figure) — fix it in the same turn and say so explicitly;
  errors found by the user outrank new features.
- Track open threads: if an iteration ends with "we should also…", record it in
  the concept's notes.md `## Open questions` so the next session picks it up.
