# concept-explainer — accumulated lessons

- **Always validate before delivering**: run `assets/validate_page.js <page>` with
  node — it syntax-checks every inline script and KaTeX-renders every `$`/`$$`
  expression with `throwOnError:true` (the page uses that flag, so ONE bad
  expression kills all math rendering silently). It resolves KaTeX from the
  committed `assets/vendor/`, so it works from a clean checkout.
- **Never leave anything to browser defaults.** The user's first aesthetic
  complaint was "ugly blue links": plain `<a>` inside `main` had no color rule at
  all and fell back to `#0000EE`; the same bug hit range sliders and checkboxes
  (`accent-color` unset) and unstyled `<button>`s. Style links, `:visited`,
  `:focus-visible`, form controls and buttons in the template — a default-styled
  control next to a designed page reads as a bug.
- **Verify visually, don't assume.** `google-chrome --headless --screenshot`
  with `--blink-settings=preferredColorScheme=1` (light) / `=2` (dark) renders
  the real page; screenshots caught the slider-blue that the CSS diff didn't.
  Gotcha: URL `#anchor` screenshots come out blank on these big pages — instead
  extract the section of interest into a temp fragment, build it with
  `build_page.py`, and screenshot that at the top of the page.
- **A palette change means rebuilding EVERY page** (each embeds its own copy of
  the template), then re-validating all of them.
- **Build pages with `assets/build_page.py`** — replaces {{TITLE}}/{{CONTENT}} in
  the template and inlines `<img src>` as data URIs (pass `--images-root`).
  Author content as a fragment (h1 + `<section id>` blocks); the TOC builds
  itself from `section[id] > h2` at load.
- **Analytic interactives beat trained ones**: for flow matching, the 2D mixture
  marginal velocity field is closed-form (Gaussian posterior algebra) — the
  interactive needs zero training artifacts and stays exact. Prefer a toy with a
  closed form over shipping model weights to JS.
- **A wrong convention gets corrected once, then obeyed silently.** Epona's
  paper declares t=0 data while its own code (and the whole FM literature) uses
  t=0 noise — and under the paper's declaration its eqs. (1)-(3) are
  sign-inconsistent. Evolution of how this page handled it, ending where the
  user wanted it: (1) a convention table comparing all four sources — too much
  bookkeeping; (2) a per-equation correction note — the user asked for this,
  then rejected it as repetitive noise; (3) **one prominent statement at the
  top, everything thereafter simply written correctly** — final. The table and
  every correction block were deleted.
  Doing (3) properly is a whole-campaign change, not a text edit: our code
  switched convention, five models were retrained (checkpoints encode what t
  means), and the figures were regenerated because a noise→data strip reads
  backwards otherwise. Budget for that before promising it.
- **Official-code excerpts next to ours**: quote the paper's real implementation
  (with `official/...:line`) directly under our pedagogical version — the
  differences (mean_flat reduction, the shifted inference schedule, dead
  modules) are
  themselves teaching material. Source the file:line refs from the campaign's
  `code_map.md`, never from memory.
- **Real failure figures teach best**: the 1-Euler-step MNIST grid (mean-digit
  collapse) turned a discretization-error paragraph into something visible; pair
  it with the matching interactive (Euler step-count on the 2D toy).
- **Name every parallel stream explicitly** when a paper has more than one
  (Epona: img/VisDiT vs traj/TrajDiT), even where the code is line-identical —
  never let the reader wonder whether a statement covers the other one. (This
  is what survives of an earlier "repeat the correction everywhere" rule; the
  correction itself is now stated once — see above.)
- **Docstring/comment edits shift line numbers too** — any .py touch, however
  cosmetic, requires re-syncing every `path:line` reference on the page.
- **Validate interactives by SCREENSHOT, not by syntax check.** `validate_page.js`
  catches parse errors and bad KaTeX; it cannot catch an interactive whose
  readout contradicts its own numbers. A drift-fan-out demo shipped claiming
  "outruns linear growth" while displaying 1.1× over 4× the horizon — the toy
  was contractive, so error shrank. Fix was to model the real mechanism
  (off-distribution states produce larger errors) and to COMPUTE the verdict
  from the measurement instead of asserting it in prose.
- **Design interactives so the text cannot go stale**: derive every claim in the
  readout from the live simulation (measured ratio vs √T vs linear), so the
  words are always true for whatever the sliders are set to.
- **Extract-and-screenshot workflow**: pull the `div.interactive` blocks plus
  the trailing `<script>` into a temp fragment, build with `build_page.py`,
  screenshot at the top of the page. URL `#anchor` screenshots come out blank.
- **The best teaching results are the counterintuitive measured ones**: L2 head
  scoring better on MSE while producing unusable blur; VQ costing 2.2× recon
  error at equal compression; a 28× FLOPs ratio delivering 4× wall-clock. Design
  each mini-project so it can produce a surprise, then report the surprise.

- **Never write "it is obvious that" / "it is simply" / assert a result in
  passing.** The flow-matching page stated the marginal field "is an expectation
  over every (data, noise) pair whose path passes through x" as if self-evident;
  the user asked why, and it is in fact a theorem (the marginalization trick)
  that needs the continuity equation to derive. Any sentence of the form "X is
  Y" about a non-definitional fact is a derivation the page owes the reader.
- **Name-collisions deserve a table, not prose.** Three objects in flow matching
  share one shape — conditional velocity u_t(x|x_1), marginal velocity u_t(x),
  and the network v_Θ — and readers reasonably ask which is which and whether
  the network is scalar. A 3-row table (object | what it is | known?) killed the
  confusion faster than any paragraph.
- **Say why a word was chosen when a vaguer one exists.** "Velocity field" vs
  "vector field" is not decoration: both are vector fields, but the score
  ∇log p_t is a vector field that is NOT a velocity. Spelling that out turns
  jargon into information.

- **Unpack the load-bearing adjective.** A table column reading "known in
  closed form" prompted the next question; the phrase was doing real work and
  had never been defined. When a page leans on a term of art (closed form,
  tractable, exact, well-posed), spend the two sentences: what it means, why
  this object has it, and what the object that lacks it would require instead.

- **Excerpt references rot silently, so check them mechanically.** After the
  time-convention rewrite, 5 of 13 excerpts pointed at the wrong lines and 2
  quoted paraphrased code (an elided argument list, an added comment) in
  violation of the verbatim rule — none of it visible while reading the page.
  `assets/check_excerpts.py --all` catches both classes in one second. The user
  had to ask for this; it is now mandated in the SKILL, not optional.
- **Verbatim means verbatim.** If a line is too long, quote it anyway or widen
  the elision to a whole `...` line — never rewrite the inside of a line, and
  never add an explanatory comment that is not in the file. Put the explanation
  in the code-path label or the prose instead.

- **Say where a technique is used, not just what it computes.** Emphasising
  the one-step estimate x̂₁ = x_t + (1-t)v led the user to conclude Epona skips
  the ODE solver entirely and "picks a random t near 1". It does not: the
  one-step form is a training-only device, and inference runs 100 Euler steps.
  Whenever a page teaches a shortcut, state in the same breath which phase uses
  it (train / sample / both) and what the other phase does instead.
- **Answer the questions the equations imply but never state.** For a sampler:
  what is random (only the initial noise), what is deterministic (everything
  else — same ε gives a bit-identical sample), whether you start from data (no),
  whether the sampled path is straight (no — conditional paths are straight, the
  marginal one curves), and how to get/choose among multiple samples (draw more
  ε; the model ranks nothing, ranking needs an external criterion). These are the
  first questions a careful reader asks and they are almost never written down.

- **A box in a diagram is a promise the prose has to keep.** The U-Net diagram
  showed a `t → sin emb` bus feeding every block, and the page never said what
  the embedding was, whether that t was the same t the objective sampled (it is,
  the identical tensor), or why a raw scalar would not do. If a diagram names a
  component, some section must explain it — otherwise the picture generates
  questions the text cannot answer.
- **Anticipate the "then why is it an input?" question.** Rectified flow's
  conditional target is constant in t, which makes conditioning on t look
  redundant until you remember the network fits the MARGINAL field, which varies
  strongly with t. Whenever a quantity is constant in one view and not in
  another, say so explicitly at the point where the reader will notice.

- **A broadcast bus must actually touch every target.** Three diagrams drew a
  conditioning bus ("t → sin emb" feeding every block) with connectors that
  floated: the bus sat at y=366 while several risers started at y=348, so they
  connected to nothing, and the risers that did reach the top block ran straight
  THROUGH the two boxes below it. The reader sees "not connected to all blocks"
  immediately even when the caption claims otherwise. Draw a bus as an explicit
  trunk with short arrowheaded taps, route the trunk in a column that crosses no
  box, and give every branch an arrowhead so contact is unambiguous. Verify by
  rendering — coordinate arithmetic is exactly the kind of thing that looks fine
  in the source and wrong on screen.

- **Use `<details class="fold">` for depth the main thread doesn't need.** Long
  provenance walkthroughs (why the ResBlock is shaped the way it is, which paper
  each line came from) would bury the argument if inlined, and would be lost if
  cut. A collapsible fold keeps the page's spine readable and the depth one
  click away. Styled in the template: accent summary, ▸/▾ marker, page-bg code
  blocks so nested `pre` stays legible against the fold's tinted background.
- **CSS escapes inside build_template.py's LAYOUT get eaten twice.** `content:
  "\25B8"` in the source becomes a Python OCTAL escape (`\25` → 0x15) before it
  ever reaches CSS, and the page renders literal garbage ("B8␀a0") in place of
  the disclosure triangle. Use the literal glyph (▸) in the CSS rather than a
  numeric escape — or double every backslash and verify by rendering.

- **Explain broadcasting with a tiny RUN tensor, not prose.** "The time
  embedding is added per channel" is invisible; a 2x3x2x2 example printing the
  shape at each step, plus the before/after of one channel showing the same
  +0.4683 at all four pixels, is immediate. Run it and paste the real numbers —
  invented ones drift from what the code does.
- **Show the silent failure, not just the correct call.** `[:, :, None, None]`
  looks like noise until you see that omitting it crashes loudly when C != W but
  broadcasts SILENTLY when C == W — painting the bias across space instead of
  channels and giving every sample every other sample's bias. The unsqueeze is
  the interesting part of the line precisely because of what it prevents.

- **Show all variants at once; a selector hides the comparison.** The
  normalization axes visual first shipped as a dropdown ("pick a normalizer") —
  the user immediately asked for them side by side, and was right: the entire
  point is that BatchNorm's highlight is the ONLY one spanning multiple samples,
  which you cannot see if you only ever view one at a time. Reserve selectors
  for parameters (G, the reference channel), never for the things being compared.
- **Draw a 4-D tensor as N separate 3-D volumes.** (B,C,H,W) has no honest 3-D
  projection, and flattening H·W into one axis (the GroupNorm paper's figure)
  loses the thing beginners are trying to see. Rendering each sample as its own
  isometric stack of C channel-cards, each card an H×W grid, keeps all four axes
  legible AND makes "crosses the batch" a visual property rather than a claim.
- **Prefer an animated canvas over a GIF for pages.** Same motion, a fraction of
  the bytes (a GIF must be inlined as a data URI), sharp at any DPI, pausable,
  and parameterizable. Say so when the user asks for a GIF — the request is for
  the animation, not the file format.

- **Interactive parameters must respect the concept's own constraints.** The
  GroupNorm slider let G range 1..4 with C=4, so G=3 produced C/G=1.333 and the
  page printed a channel called "c1.3333333333333333". PyTorch itself refuses
  that (`num_channels must be divisible by num_groups`). Fix: compute the legal
  set (divisors of C) and snap the slider to it, then SAY the constraint in the
  readout — an illegal state a user can reach is a claim that it is legal.
- **Sync control labels from state on load**, never trust the hardcoded HTML
  value; a slider whose displayed number disagrees with the value driving the
  drawing is indistinguishable from a logic bug.
- **Label a visual by what it PRODUCES, not by what it consumes.** "avg over
  B,H,W" was read by the user as "average across the channels", the exact
  opposite. "one (μ,σ) per channel · pools 27 values" cannot be misread. State
  the rule too: the axes you average over disappear; what remains is what you
  get one statistic per.

- **Audit for redundancy after adding a visual.** A good interactive can make
  earlier prose, tables and figures obsolete, and nobody notices because each
  was correct when written. The normalization page ended up asserting "only
  BatchNorm crosses samples" in FOUR places — the interactive, a summary table,
  a five-row results table, and a bar chart — until the user called it out.
  When a visual lands, re-read the sections around it and delete what it now
  says better. Keep the measured number (magnitude is evidence the picture
  cannot give); drop the restatements.

## Page anatomy that worked (six pages in, this sequence held up)

1. **Motivation** — what breaks without this idea; name the alternatives it
   replaced and what each one cost.
2. **The math**, quoted with the paper's equation numbers, in a boxed eq with a
   citation line underneath.
3. **The derivation the paper skipped**, worked in full. This is the reason the
   page exists; never compress it to save room.
4. **One correction block near the top where the paper is wrong**, stating the
   error and the correct form — then every later equation, caption and figure
   simply uses the correct form, with no further mention.
5. **Architecture diagrams**: high-level overview + expanded blocks, all skips
   drawn (see SKILL.md).
6. **An interactive** whose readout is computed from the simulation.
7. **The experiment**: arms table, real figures, and the honest caveat.
8. **Ours ↔ theirs code**, our excerpt followed by the official implementation
   with `file:line`, including the places they differ.
9. **Running it** — the exact commands and the wall-clock on this machine.
10. **References** with links.

## Voice

- Cross-link concepts by name and let pages depend on each other's results
  ("measured at 2.2× worse on the latent generation page") — the campaign should
  read as one body of work, not six leaflets.
- State the confound you could not remove, in the same paragraph as the result.
- When a result contradicts the paper or common sense, explain the mechanism
  before drawing any conclusion, and list what would falsify your reading.
- Numbers in prose come from the code's JSON outputs, never from reading a plot.
