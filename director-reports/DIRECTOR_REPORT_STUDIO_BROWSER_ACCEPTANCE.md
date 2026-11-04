# DIRECTOR REPORT — STUDIO REAL-BROWSER ACCEPTANCE (GitHub Actions)

Circuit: STUDIO-BROWSER-ACCEPTANCE — Director-specified in the
Studio security certification directive (PR #255, step 6,
2026-11-03): *execute real-browser acceptance on a GitHub Actions
runner with Chromium and Studio on the same loopback host; capture
DOM assertions, console errors, and a genuine screenshot; do not
label API-only replay as browser acceptance.*

Status: **SUBMITTED** — PR #258 held UNMERGED for Director review.
Base: db61de0a1a1391c83237a0fab016d814f0c10af0 (main; PR #255 +
PR #256 merged). Browser evidence executed at code head
5d889e3be058c395b3928095488cc0aed46b91c3; every commit above it on
the PR branch is documentation/evidence only.

Realism label (fixed): **AUTOMATED BROWSER (CDP) on CI runner** —
genuine Chromium, real DOM, real input-pipeline events, ruled
valid technical browser evidence by the Director when it genuinely
runs the interface. NOT a human session; NOT REAL_USER_PATH.

## 1. What was built

- `.github/workflows/studio-browser-acceptance.yml` — triggers:
  `workflow_dispatch` (usable once on the default branch) +
  `pull_request` on paths `gui/**` and the workflow file itself.
  It does NOT run on ordinary pushes to main. On ubuntu-latest it
  sets up Python 3.11, discovers a Chromium binary on the runner
  (falls back to installing google-chrome-stable), starts
  `python3 -m gui.server --owner BrowserCI --port 8765` (loopback
  default bind; `--allow-remote` is never passed), starts headless
  Chromium with remote debugging bound to 127.0.0.1:9333, runs the
  driver, and uploads the evidence directory as an artifact with
  `if: always()`. The driver's exit code gates the job.
- `gui/browser_acceptance.py` — the repo-owned driver. Placement
  justification: it accepts the `gui/` product surface, so it
  lives beside `gui/server.py`; the security circuit's original
  remains untouched at
  `director-reports/evidence/studio-security/browser_acceptance.py`
  as the historical artifact. Adaptations: bounded-wait polling
  (no fixed-sleep assertions), RUN pressed via
  `Input.dispatchMouseEvent` at the button's real coordinates
  (input pipeline, not `el.click()`), a token-meta assertion,
  structured `assertions.json` output, raw console capture
  (`console_events.json`), and in-driver screenshot byte
  verification (PNG magic + IHDR dimensions + size floor).
- **No product files changed.** `gui/server.py` and `gui/static/`
  are byte-identical to the certified merged tree; the workflow
  weakens nothing to make the test pass.

Genuineness contract: the driver sends **zero** HTTP requests to
the app API. Its only HTTP is the CDP `/json/list` control plane.
Every app request (dells, state, parse, execute) is issued by the
page's own `app.js`, which is also what carries the per-launch
session token — a broken token flow would fail this drive exactly
as it would fail a user. The seed enters through the page's own
example `<select>` and its real `change` handler (the app's code
path for that control; disclosed rather than dressed up), and RUN
is a genuine mouse press through the browser input pipeline.

## 2. The drive — assertions (run 41750912673, attempt 1)

Engine: Chrome/156.0.8078.47 (HeadlessChrome, ubuntu-latest).
Server and browser on the same runner loopback.

| # | Assertion | Observed |
|---|---|---|
| 1 | Page title is the Studio | 'DellMatrix Studio' |
| 2 | Transport, rack panel, editor, canvas, receipts, RUN, examples all in the DOM | missing=[] |
| 3 | Served page carries the per-launch session token (not the placeholder) | token length 43 |
| 4 | Frontend init completed (status reaches "engine ready") | 'engine ready · owner BrowserCI · store 0 · plants 0 · history 0' |
| 5 | Dell Rack renders exactly 100 Dells | count=100 |
| 6 | Both rack groups render | 'CORE I — ACTION SPINE · 00–50 \| CORE II — INSTRUCTION ARCHITECTURE · 51–99' |
| 7 | Example select loads its seed into the editor | '55[Set] :: tempo=120 >> 56[Get] :: tempo' |
| 8 | Canvas renders the canonical parse (2 atoms) | count=2 |
| 9 | No outcome painted before the run | painted=0 |
| 10 | Chain verdict shows CHAIN OK from the run's receipts | '✓ CHAIN OK — 2 atoms' |
| 11 | Both atoms painted atom-ok from real receipts | ok=2 |
| 12 | Per-atom verdicts read 'ran' | ['✓ ran', '✓ ran'] |
| 13 | Store panel shows the executed value | 'tempo' + '120' present |
| 14 | Receipts panel records the run as OK | rows=1, verdict OK |
| 15 | Zero console errors / page exceptions (favicon excluded) | app_errors=[] |
| 16 | Screenshot is a real PNG of the page | 159,387 bytes, 1440×857 |

**BROWSER-ACCEPT: 16/16.** Console detail: the entire session
produced exactly **one** raw error candidate — the favicon.ico
404 network log entry — excluded by the driver's narrow,
disclosed favicon-only rule; the raw capture is preserved in
`console_events.json` for audit.

## 3. Runs

- **Attempt 1** — run 41750912673, job 126315503183, SUCCESS,
  16/16. Artifacts downloaded with `gh run download` and bundled
  byte-identical (see §5).
- **Attempt 2** — rerun of the same run ID, job 126315960018,
  SUCCESS, **16/16** (screenshot 159,571 bytes, same dimensions;
  the byte difference is the run's receipt timestamp). Two
  consecutive full green runs of the same head: the acceptance is
  repeatable, not a single lucky pass. Attempt 2's driver log is
  preserved in the workspace evidence dir; attempt 1 is the
  bundled canonical attempt.
- **Local validation (API-LEVEL ONLY, not browser evidence):**
  before the first CI run, the driver's assertion expectations
  were checked against a locally launched server (token
  substitution present; /api/dells = 100; the example seed parses
  to atoms [55, 56]; execute returns ok with both atom_results ok
  and store {tempo: 120}) — the same values the browser then
  verified through the DOM. The driver also fails closed locally
  with no CDP listener (FAIL + exit 1). Recorded in
  `local_validation.log`.

## 4. The screenshot

`studio_browser.png` (in the bundle) was captured in-session,
after the assertions passed, and inspected directly. It shows the
dark Studio UI after the driven run: transport reading
"done · ok" with owner BrowserCI; the Dell Rack with the Core I
list; the Flow Canvas holding the 55[Set] and 56[Get] cards
painted with green atom-ok borders and "✓ ran" verdicts under a
"✓ CHAIN OK — 2 atoms" pill; the syntax-tinted seed in the
editor; the Inspector showing "Last result — OK" with the run's
full result JSON (atom_results for Dells 55 and 56, ok true);
the Store panel reporting 1 key; and the Receipts footer row for
the run marked OK. It is a screenshot of the working application
mid-task, not of a load screen or an error page.

## 5. Evidence bundle

`director-reports/evidence/studio-browser-acceptance/` —
assertions.json, chrome.log, chrome_version.json,
console_events.json, driver.log, local_validation.log,
run_record.md, server.log, studio_browser.png, MANIFEST.sha256
(9 files; the manifest excludes itself — no self-hash entry —
and `sha256sum -c` verifies cleanly).

## 6. Boundaries — what this does NOT prove

- No human session: keyboard/mouse came from CDP input events.
  REAL_USER_PATH for Studio remains unclaimed (Ace's own
  two-minute browser check would still be a distinct evidence
  class).
- One engine (Chrome 156 headless), one viewport (1440×1000),
  one happy-path seed. The Growth and Console views were not
  driven; no failing-seed / PARTIAL / skipped verdict path was
  exercised in the browser; no cross-browser claim.
- The certificate sought is for the acceptance EVIDENCE, not a
  re-review of Studio security (already certified, PR #255) and
  not network deployment (prohibited claim, unchanged).

## Anticipated probes

- *"Did the driver bypass the token?"* No driver-issued app
  requests exist to bypass it with; §1's genuineness contract is
  checkable by reading the driver — its only `urllib` call is the
  CDP target list.
- *"Could the assertions pass on a blank page?"* No: they are
  positive-content (exact counts, exact strings, a store value
  that only exists if the run executed). The local failure-path
  run shows the driver failing closed when the browser is absent.
- *"Why is the favicon 404 not an app error?"* It is a network
  log entry for a resource the page never references explicitly;
  the exclusion rule is one substring, disclosed in code and in
  `console_events.json`, where the raw entry remains auditable.
- *"The workflow installs Chrome — supply-chain surface?"* The
  install path is a fallback only (the runner image's Chrome was
  used in both recorded runs); it fetches the vendor's stable
  .deb over HTTPS from dl.google.com inside a disposable runner.

## Questions for the Director

1. Does this evidence close the browser-acceptance item as
   **AUTOMATED BROWSER (CDP)** for the Studio security
   certificate's scope (localhost, single-user)?
2. Should the workflow's PR-paths trigger stand as the permanent
   acceptance gate for future `gui/**` changes, or should it be
   dispatch-only after merge?
3. Is the single happy-path drive sufficient for this
   certificate, or should a follow-up circuit add the
   Growth/Console views and a PARTIAL/failing verdict path
   before this item is called complete?

---

## Addendum — merge resolution against advanced main (2026-11-03)

After submission, main advanced (PR #257 archival merge, 8426334) and
this branch went CONFLICTING on director-reports/INDEX.md only (the
archival status updates and this report's row occupy adjacent lines).
Resolved by merge commit 8e33690: the INDEX now carries both the
archived ruling rows/status updates and this report's row, verbatim.
Verified: `git diff b60a368..8e33690 -- gui/ .github/ form/` is EMPTY
— no product, workflow, or test content changed; the browser evidence
executed at b60a368 covers byte-identical product code at the
resolved head. The browser-acceptance workflow was additionally
re-dispatched at the resolved head for an exact-head run (see PR
checks).
