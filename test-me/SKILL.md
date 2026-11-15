---
name: test-me
description: Generate a recap test (an HTML page the user answers in the browser, saved to answers.md) over any part of src/learning — one concept page, a family, a topic, several of them, or the questions the user asked in this conversation / the learner question log — and later grade the submitted answers in chat, correcting wrong ones and completing partial ones. Use when the user says "test me", "quiz me", "give me a recap test on X", "check what I remember", or comes back with "grade my test" / "I did the test".
---

# test-me

Two modes, same skill:

- **create** — build a test page in `src/learning/recap/<test-id>/` from the
  chosen scope, shaped by what the user has struggled with.
- **grade** — read the answers the page saved, then correct the user
  question by question in chat, and update the learner memory.

The deliverable is the **test page** (answered in the browser) and the
**grading in chat**. `test.json` and the learner logs are Claude-facing.

## Inputs and knobs (create)

| knob | values | default |
|---|---|---|
| `scope` | a path under `src/learning/` (concept dir or its `index.html`, a family dir, a topic dir), several paths, `session` (questions asked in this conversation), `log` or `log:<topic-path>` (difficulties recorded in the learner question log) | ask |
| `focus` | `only` = ONLY about what the user asked · `related` = mostly what was asked plus its neighbours · `mixed` = coverage of the scope, ~⅓ aimed at logged difficulties · `none` = pure coverage, ignore the question history | `related` for `session`/`log`, `mixed` for paths |
| `answers` | `mix` · `choice` (every question has clickable answers) · `text` (every question is written) | `mix` |
| `mix` | share of choice questions when `answers=mix` | `0.7` (70% choice + submit, 30% written + submit) |
| `n` | number of questions | 10 |

Parse what the user already said. If scope or focus is genuinely unclear, ask
— **one AskUserQuestion at a time**, arrow-selectable, recommended option
first, at most two questions (scope, then focus). Everything else takes its
default; state the defaults in one line and go.

## The learner memory (read first, write after)

The host project keeps a learner question log (its `CLAUDE.md` says where;
default `docs/learner/questions.md`), organized by **topic path → sub-topic**,
one entry per user question with the date, the question, what it revealed
(the difficulty), where it was answered, and a status. Grading results go to
`docs/learner/tests.md`. Before creating a test, read both (if present) plus
the current conversation: the session's questions count even if not yet
logged. If the log is missing, create it with the header format below.

```
# Learner question log
## <topic path, e.g. transformers/concepts/vit_detr_def_detr>
### <sub-topic, e.g. decoder / tgt>
- 2026-11-15 · "how is tgt being filled in" · difficulty: could not map the code to the data flow · answered: chat + page #tgt-fill · status: open
```

Status moves `open` → `tested-ok` / `tested-wrong` (after a test) → `resolved`
(two correct answers on different tests, or the user says so).

## Create — workflow

1. **Resolve the scope** to concrete pages: read their `fragment.html`
   (the source; skip the built `index.html`), the concept `notes.md`, and for
   `session`/`log` the questions themselves. Read the paper's code excerpts
   the pages quote when a question targets the implementation.
2. **Plan the questions** (do not show the plan; build it):
   - weight by `focus`: `only` → every question traces to a logged or session
     question (`from` filled); `related` → ≥ 60%; `mixed` → ~⅓; `none` → 0.
     Open and `tested-wrong` difficulties first; skip `resolved` ones unless
     the scope is exactly that topic.
   - spread across the scope's sub-topics; no two questions testing the same
     fact.
   - question types, mixed: why-does-this-exist, predict-a-shape-or-number at
     the **deployed** sizes, what-breaks-if, compare-two-methods, paper-vs-code
     gap, trace-the-data-flow, explain-in-your-own-words. Prefer understanding
     over recall; never quiz trivia (a table's third decimal).
   - **choice questions**: 3–5 options, one or several correct (`multi`,
     labelled "choose all that apply"). Distractors are real misconceptions —
     the user's own logged confusions are the best ones. Each still has a "why?"
     box; a right pick with wrong reasoning is graded partial.
   - **text questions**: answerable in 2–5 sentences; write `key_points` (what a
     full answer must contain) and `explain` (the model answer).
   - every question gets `ref`: the page link + `#anchor` where the answer
     lives (used when grading, never shown on the test page).
   - math in prompts/choices as `$…$` (KaTeX renders it on the page).
3. **Write** `src/learning/recap/<YYYY-MM-DD>-<slug>/test.json` (schema in
   `assets/build_test.py`'s docstring; the folder name is the id).
4. **Build**: `python ~/.claude/skills/test-me/assets/build_test.py build
   src/learning/recap/<id>`. It checks the spec, prints the choice/text mix
   (must match the knob: with `mix=0.7`, n=10 → 7 choice, 3 text), writes the
   page without the answer key, rebuilds `src/learning/recap/index.html` (the
   list of tests with status) and the site nav. Validate with
   `node ~/.claude/skills/concept-explainer/assets/validate_page.js`.
5. **Tell the user** the page path, the knobs used, and how saving works: the
   first Submit asks where to save — choose `answers.md` in the test folder —
   then every Submit overwrites it with the whole test (Chrome/Edge; other
   browsers download `answers-<id>.md` instead). Do not open the browser
   unless the user's setup says to.

## Grade — workflow

Triggered by "grade test <id>", "I did the test", "check my answers".

1. Find `src/learning/recap/<id>/answers.md` (fallback: newest
   `~/Downloads/answers-<id>*.md`; if neither exists, say so and stop). Read
   it with `test.json`. Grade only **submitted** answers; list unsubmitted
   ones as skipped (mention a draft if one exists).
2. Per question, a verdict — **correct**, **partial**, **wrong**, **skipped** —
   then, in chat:
   - wrong → what the right answer is, why, and which misconception the pick or
     sentence shows; link the page section (`ref`).
   - partial → what was right, then exactly what was missing or imprecise
     ("complete me"), against `key_points`.
   - correct → one line; add the nuance only if the reasoning box missed it.
   Plain first, then precise. No LaTeX in chat (plain text / unicode math).
   Start with the score and the two or three weak spots, then the questions in
   order; keep correct ones short.
3. **Write back**:
   - `test.json` → `grading: {date, score, items: [{q, verdict, note}]}`; rebuild
     with `build_test.py build` so the recap overview shows "graded".
   - `docs/learner/tests.md` → one entry: date, test id, scope, score, per
     sub-topic verdicts, the misconceptions seen.
   - `docs/learner/questions.md` → update the status of each difficulty a
     question targeted (`from`); add a new entry for a misconception the test
     revealed that was not logged.
4. If a wrong answer shows the PAGE is unclear or wrong, say so and offer to
   fix it (via `study-iterate`); do not silently edit pages during grading.
5. Offer a follow-up test on the weak spots (`scope=log:<topic>`,
   `focus=only`), never start one unasked.

## Rules

- Questions are about the material as deployed and as measured (real sizes,
  real code), consistent with the pages — never about a toy's numbers unless
  the question says it is the toy.
- The answer key never goes into the page (`build_test.py` strips `key`,
  `key_points`, `explain`, `ref`, `from`).
- One test = one folder; never overwrite a graded test — make a new one.
- Don't grade generously: a vague answer that would not let the user rebuild
  the idea is partial, and say what is missing.
