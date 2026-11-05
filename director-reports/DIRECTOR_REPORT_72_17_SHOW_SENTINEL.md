# DIRECTOR REPORT — 72-17: Literal Show Placeholder Output (Investigation)

Register item 72-17 (INVESTIGATION, P2/I): "Remove/relabel
literal Show placeholder output" — a bare `09[Show]` was
suspected of emitting a literal placeholder. One-probe
investigation, executed 2026-11-05. Evidence bundle:
`director-reports/evidence/72-17-show-sentinel/` (probe
source, three run logs, SHA-256 manifest). No product code
changed.

## What Show actually does (FACT, code)

Dell 9's default branch (form/mandell/executor_leaf.py:168-180)
appends the literal token `__RENDER__` to the result's
`messages` — a render DIRECTIVE, not rendered content.
Labeled variants produce real output instead: `visual` →
"Visual ready." + path; `avatar` → live avatar status;
`lattice` → the lattice ASCII render. The Dell card
(form/mandell/dell_cards.py, D1 note for Dell 9) documents
the token honestly.

## Probe results (two identical clean runs, exit 0)

Probe `q17_probe.py` — 7 checks, all PASS (run1 was a
calibration run: an over-strict S1 equality and a Studio
401 before the browser-faithful token bootstrap; preserved
and labeled in the bundle):

- **S1 front door** (execute_seed, in-process): bare Show
  messages = `['Mandell: 09[Show]', 'English: Show (Render /
  output)', '__RENDER__']`, ok=True. Controls (lattice,
  avatar) emit real output, no token.
- **S2 REPL** (cross-process, REAL_USER_PATH): piped
  session `08[Create] > 09[Show]` — the token NEVER reaches
  stdout; form/repl.py's `_apply_seed_result` (line 1284)
  intercepts it and prints `Program.render()` (the status
  board; header verified present). **The terminal path is
  clean.**
- **S3 Studio** (cross-process, real server + browser-
  faithful session-token bootstrap): POST /api/execute
  returns result.messages containing `__RENDER__`, and the
  frontend's normal run path dumps that result JSON
  verbatim into the user-visible console
  (gui/static/app.js, `execute()`:
  `logConsole(JSON.stringify(data.result, null, 2))`).
  **The literal placeholder IS user-visible in Studio** —
  inside the raw JSON console dump, on every bare-Show run.
- **S4 chain** (in-process): the token passes through chain
  messages unchanged; the REPL intercepts it at the same
  display boundary, Studio dumps it the same way.

Static-only additional surface (code-evidenced, not
dynamically probed): form/dell_matrix/live_visual.py
(~line 1388) collects result messages raw into its returned
string after also invoking the REPL interceptor — a third
place the token can surface unsubstituted.

## Verdict

1. **No program-wide placeholder fraud.** The token is an
   internal render directive with exactly one intended
   consumer (the REPL display boundary), honestly
   documented; through the terminal the user always sees
   the real render.
2. **Bounded defect CONFIRMED:** the Studio console shows
   the literal `__RENDER__` to the user, because the
   frontend logs the raw result JSON without the
   substitution the REPL performs. The root smell: a
   machine sentinel travels inside the human-readable
   `messages` list, so every present and future display
   surface must know to intercept it — one already doesn't.
3. Register item 72-17: INVESTIGATION COMPLETE. The
   "remove/relabel" remedy is a real, bounded fix awaiting
   the Director's choice (below); no repair is claimed or
   smuggled into this closure.

## Remedy options (for ruling)

- **R-A Display parity (smallest):** the Studio frontend
  substitutes/filters the token wherever it renders result
  data (mirroring repl.py:1284). Kills the visible symptom;
  leaves the mixed-layer smell for the next surface.
- **R-B Structured directive (recommended):** the executor
  stops placing the token in `messages` and instead sets a
  structured render directive on the result; the REPL (its
  only consumer) and any future surface key off the field.
  Removes the placeholder from human text permanently and
  kills the class. Blast radius is small: grep shows
  repl.py is the only sentinel consumer; executor_leaf is
  the only producer; dell_cards documents it (doc update).
- **R-C Relabel:** the leaf emits an honest human sentence
  in messages plus the machine marker moved to a field —
  R-B with extra wording; the sentence risks going stale
  against the actual render.

## Anticipated probes

- "Is the REPL board itself truthful?" — S2 verified the
  board header + owner; board contents are Program.render()
  over live state (the same render certified in earlier
  Studio/REPL work); not re-audited here.
- "Did you probe the English path ('show me')?" — No:
  English composition routes to the same execute_seed
  result and the same two display boundaries; the sentinel
  is produced below the language layer. Bounded claim
  accordingly.
- "Why is run1 in the bundle?" — calibration honesty: it
  records the probe's own two setup defects and their
  fixes, so the clean runs are auditable, not curated.

## Questions for the Director

- Q-17.1: Which remedy — R-A, R-B (recommended), or R-C —
  and as its own bounded circuit?
- Q-17.2: Should the structured-directive pattern (R-B),
  if chosen, be stated as a general law (machine directives
  never travel in human message lists) for future Dells?
