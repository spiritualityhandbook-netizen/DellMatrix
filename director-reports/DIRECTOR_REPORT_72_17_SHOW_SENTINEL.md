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

---

## Addendum 1 — Targeted correction (2026-11-05, answering the Director's 13:47 CST review, INSUFFICIENT_EVIDENCE on head 41e2b94)

The review's central finding is correct and is owned
without qualification: **the original PR's MANIFEST.sha256
listed three probe logs that were not in the PR.** Cause:
the repository's `.gitignore` carries `*.log`; the bundle
commit used a plain `git add -A`, which silently skipped
them, and the PR tree was never inspected for their
presence before submission. The logs existed locally the
whole time. This is the same failure class the 72-28 cycle
had already banked ("force-add evidence files") — the rule
was known and not applied. Correction, per required point:

**1. Raw logs committed; manifest verifiable.** All three
original logs are now committed (force-added past the
ignore rule), calibration run labeled as such in the
bundle. The on-disk originals hash-verify against the
originally committed manifest — the manifest was accurate;
its files were missing. Verification command, run in
`director-reports/evidence/72-17-show-sentinel/`:

```
sha256sum -c MANIFEST.sha256   # exit 0, every entry OK
```

The bundle also gains: `q17_probe_run4.log` (the bounded
probe re-run at this correction, exit 0, classification
unchanged) and the manifest is regenerated over the full
bundle at the frozen correction head. The verify-72-17 CI
workflow re-runs this same `sha256sum -c` at the exact head
and prints its exit code.

**2. Real browser/UI assertion.** Supplied as
`q17_browser_probe.py` + `.github/workflows/verify-72-17.yml`,
following the repository's own ruled-valid pattern
(studio-browser-acceptance): an externally started real
Chromium drives the actual Studio UI over CDP — genuine DOM,
real input events, zero driver-issued API calls; the page's
own app.js carries the per-launch session token, so the
authenticated path is the user's path. Flow: control seed
(55[Set]>>56[Get]) first — assertion B1: its user-visible
`#console-log` text contains NO `__RENDER__`; then bare
`09[Show]` — assertion B2: the console text DOES contain
`__RENDER__`; B3: the served token is a real per-launch
token. Raw outputs (full console text, screenshot,
assertions JSON with browser product + pinned SHA) are
uploaded as the run's artifacts and archived into this
bundle by a supplement records PR referencing the frozen
head, without amending it. Environment honesty: the probe
could NOT be executed on Uni's local VM — the only local
Chromium is the harness build, which refuses direct launch
("Hatch WebGL domain policy is required"), and the runtime
browser cannot reach this VM's loopback. Both local attempts
are preserved, labeled, as `browser_probe_run1.log` (probe
path defect, fixed) and `browser_probe_run2.log`
(SETUP_FAILED, no CDP targets). The CI execution at the
frozen head is therefore the browser evidence of record —
AUTOMATED BROWSER (CDP), not a human session, not
REAL_USER_PATH. The REPL-absence control remains q17_probe
S2 (cross-process, re-run as run4).

**3. Call sites verified at the pinned head (41e2b94).**
Frontend: `gui/static/app.js` line 661, inside `execute()`:
`logConsole(JSON.stringify(data.result, null, 2));` —
`logConsole` (line 65) appends a text node to `#console-log`
and scrolls it into view: user-visible by construction.
REPL interceptor: `form/repl.py` line 1284, inside
`_apply_seed_result`: `if msg == "__RENDER__": print();
print(p.render())`. Additional surfaces census (unchanged
from the report): live_visual.py raw collection remains
STATIC-ONLY; all other consumers are listed under point 4.

**4. R-B compatibility with all known consumers.**
Sentinel touchpoints at the pinned head — producer:
`executor_leaf.py:180` (only); runtime consumer of the
token's VALUE: `repl.py:1284` (only); documentation:
`dell_cards.py:464`; pinned test expectation:
`d1_registry_leaf2_test.py:143` (asserts the current
contract; an R-B circuit updates it deliberately).
`messages` consumers and their R-B posture: chain_exec
(aggregates atom messages — opaque passthrough, unaffected);
execution_observer / operator_bridge / semantic_router /
runtime_observe (copy or truncate messages as records —
opaque, unaffected); live_visual (collects messages for
display — loses only a non-human token; its render still
prints via the same `_apply_seed_result` it already calls);
flow_executor (own result shape, opaque); gui/server.py
(JSON passthrough, no inspection); app.js (display only —
under R-B its dump simply stops containing the token; no
frontend change required). **Answer: R-B is compatible with
every known consumer.** The only deliberate migrations are
the producer, the REPL's check (keyed to the new structured
field), the dell card's note, and the one pinned test. No
consumer parses `messages` for the token besides the REPL.
Consistent with the Director's design guidance, R-B is the
candidate architecture; per his order, NOTHING is
implemented here — the Studio defect remains OPEN and this
PR remains HELD for re-review.
