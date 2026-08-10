---
name: grilling
description: Grill the user relentlessly about a plan, decision, or idea. Use when the user wants to stress-test their thinking, or uses any 'grill' trigger phrases.
---

Interview the user relentlessly until you reach a shared understanding. Map this as a **design tree**: every decision branches into the decisions that hang off it.

Work the tree **one question at a time**. The **frontier** is every decision whose prerequisites are already settled — the questions you could ask _now_ without guessing at answers you haven't heard yet. From the frontier, pick the single most load-bearing question — the one whose answer reshapes the most of the tree — and **wait for the user's answer before asking the next**. Never batch multiple questions into one message, even when several are independently askable.

**Ask every question through the `AskUserQuestion` tool** (one call, one question) so the user picks an answer with arrow keys instead of typing. Rules for each call:

- Put your recommended option **first**, with `(Recommended)` appended to its label.
- Give 2–4 concrete, mutually exclusive options; each option's `description` carries the tradeoff in a sentence or two. The user can always type a custom answer via "Other", so never add a catch-all option yourself.
- Any context, evidence, or reasoning too long for option descriptions goes in normal prose **before** the tool call — keep the question itself short.
- Use `multiSelect: true` when choices genuinely compose.

Each answer reshapes the tree — settled decisions push the frontier outward and unblock questions that depended on them. Recompute the frontier after every answer and pick the next single question. A question whose answer depends on a still-open question waits until that one is settled.

Finding _facts_ is your job, never the user's. When a frontier question needs a fact from the environment (filesystem, tools, etc.), dispatch a sub-agent to find it — don't ask the user for anything you could look up yourself. Don't block on it: a running exploration is an unsettled prerequisite, so only the questions downstream of it wait for the sub-agent to report — ask the rest of the frontier now. The _decisions_ are the user's — put each to them and wait.

The session is done when the frontier is empty: every branch of the design tree visited, nothing left silently assumed. Do not act on it until the user confirms you have reached a shared understanding.
