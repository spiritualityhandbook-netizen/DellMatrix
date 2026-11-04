# DIRECTOR REPORT — STUDIO SECURITY + BROWSER ACCEPTANCE

**Circuit:** STUDIO-SECURITY (Director priority item 2 from the ruling
on PR #252, 2026-11-03; finding from the Director's wake review of the
sleep-run tracks: gui/server.py had no authentication, no origin
protection, no request-size limits; owner isolation is state
separation, not access control; Studio held LOCAL-ONLY until a
dedicated security circuit).
**Status:** SUBMITTED — awaiting Director certification. PR UNMERGED
by design (certification gate). **One item remains open by
environment, not by omission: real-browser acceptance (see §4).**
**Base:** `0f6dcb8d4d701c6fd6b47d60da709520a6289404` (main, PR #252
merge; tree `292a77ac709c6eb1f0f7ead0a84e29d9a34af738`)
**Verified head:** `66050cf83fbef3a9b7aa0763beb08d0be734e53a` (branch
`uni/studio-security`; tree
`66c14bbb34d076a3d08362f69e21c17e4c106ab3`). Exact-head CI and the
fresh-clone run below are at this head. The submission head (this
report + evidence bundle on top) differs only in documentation and
evidence files; its CI is recorded in the Submission Verification
addendum.

## 1. Surface inventory (verified at base, gui/server.py 332 lines)

| Surface | Kind | Base posture |
|---|---|---|
| GET /, /index.html, /app.js, /style.css | static, fixed filename map | confined — no traversal surface (map lookup only) |
| GET /api/dells | registry read | no owner state |
| GET /api/state?owner= | reads any owner's state | caller-supplied owner, no caller check |
| GET /api/growth?owner= | reads any owner's growth | same |
| POST /api/parse | stateless parse | no caller check |
| POST /api/execute | **mutates** program state (seed execution) | no caller check of any kind |
| POST /api/owner | **mutates** the global active owner | no caller check |

Base defects, each reproduced behaviorally by the failing-first
suite (25 RED / 35 on the unchanged base, `red_run.log`):

- **D-S1 Cross-origin execution (the concrete browser vector).**
  Content-Type was never inspected and bodies were JSON-parsed
  regardless, so a malicious web page in the user's browser could
  fire a cross-origin *simple request* (text/plain, no preflight) at
  /api/execute and the seed executed. The loopback bind does not
  close this — the browser is inside the loopback boundary. On base,
  the suite's cross-origin execute **landed in the store** (mutation
  assertions failed alongside the status assertions).
- **D-S2 DNS rebinding.** No Host validation: a rebound attacker
  origin is indistinguishable from the user. Foreign Host, suffix
  Host (localhost.evil.com), wrong-port Host, and missing Host were
  all served on base.
- **D-S3 Unbounded body read.** `rfile.read(Content-Length)` with no
  cap; a non-numeric Content-Length raised inside int() and surfaced
  as a 500, not a 400.
- **D-S4 Unauthenticated owner control.** /api/owner set the global
  active owner from any caller's body (suite: tokenless switch
  succeeded on base and moved the global).
- **D-S5 Accidental exposure.** --host was passed straight to the
  server; nothing refused or even warned on a non-loopback bind.

Already-safe surfaces (findings, not repairs): static confinement
(traversal-shaped paths 404 on base too — kept as regression
guards), malformed JSON → 400, unknown path → 404, handler
exceptions → 500 JSON without crashing the server.

## 2. The hardening (gui/server.py + gui/static; no other production files)

Every POST /api/* passes header discipline **before the body is
read**, in this order: Host → Content-Length shape/cap →
Content-Type → token → Origin.

- **A. Host allowlist (anti-rebinding).** Host hostname must be
  127.0.0.1, localhost, or ::1, and a present port must equal the
  bound port; missing Host → 403. Applies to GET and POST, so
  rebound *reads* of owner state are refused too.
- **B. Origin discipline (POST).** A present Origin must be http,
  loopback-hosted, and on the bound port — foreign origin, foreign
  port, and `Origin: null` → 403. An absent Origin (curl, local
  tooling) is allowed; the token is the gate there.
- **C. Content-Type discipline (POST /api/*).** Must be
  application/json (charset suffix allowed) → 415 otherwise. This
  kills the text/plain simple-request class outright.
- **D. Size cap + length honesty.** Measured largest legitimate
  body: 113 bytes (longest shipped example seed, 56 chars, wrapped
  as JSON). Cap 65536 bytes (~580× headroom). Over-cap → **413
  before any body read** (suite proves it by declaring 200 KB,
  sending 1 KB, and receiving the refusal without the server
  waiting). Malformed/negative Content-Length → 400 (was 500).
  Connections carry a 30 s socket timeout (slow-drip bound; suite
  verifies closure with the constant patched to 1 s).
- **E. Per-launch session token.** `secrets.token_urlsafe(32)`
  minted per server process; served **only** inside the index HTML
  (meta tag, `Cache-Control: no-store`); required as the
  `X-Studio-Token` header (constant-time compare) on every
  POST /api/* → 401 otherwise. app.js's single `api()` wrapper
  injects it on POSTs, so the legitimate UI flow is unchanged.
  Suite asserts the token never appears in /app.js or error bodies.
- **F. Bind guard.** --host outside loopback refuses to start
  (exit 2) unless --allow-remote is given; with it, startup prints a
  plain-words warning (network-reachable; Host allowlist off;
  rebinding protection does not apply; NOT certified safe) and the
  token still gates POSTs. Default bind remains 127.0.0.1.

**What this does NOT claim.** The claim ceiling is LOCALHOST-
HARDENED against web-borne callers: malicious web content and
rebinding origins are refused, with tests. It is not "safe for
network deployment." A local process able to fetch the index page
can obtain the token, so untrusted-local-process exclusion is NOT
achieved — that needs OS-level authentication and is Question 3.
GET endpoints deliberately require no token (they never mutate;
Host check defeats rebound reads; same-origin policy defeats
cross-origin reads) — local-process *read* access to owner state
remains, the same boundary, also Question 3.

**Compatibility.** `form/gui_api_test.py`: all 26 checks and
assertions unchanged and green; only its transport was adapted to
speak the legitimate client's protocol (fetch the token from the
served page, send it on POSTs, JSON Content-Type on the raw-body
probe) — the same shape the browser uses. Zero-friction launch
(`python3 -m gui.server --owner Ace --port 8765`) is preserved.

## 3. Tests & mutants

New suite `form/studio_security_test.py` (35 checks), registered in
`form/regress.py` beside gui_api_test. Every adversarial check
asserts the refusal **and** store-snapshot equality, so a refusal
that still executes fails. Failing-first on the unchanged base:
**25 RED / 35** (the 10 passes are the happy paths and the
already-safe guards). After the fix: **35/35 GREEN**. Adjacent:
gui_api_test 26/26.

Mutants — all killed, each reverted by inverse edit with empty
`git diff` verified: M1 Host check dropped → 4 RED; M2 token check
dropped → 5 RED; M3 size cap dropped → exactly 1 RED (the
413-before-read check); M4 Origin check dropped → 8 RED; M5
Content-Type check dropped → 4 RED.

## 4. Browser acceptance — REMAINS OUTSTANDING (environment)

The only browser engine on this VM is the harness's managed
Chromium (`/opt/meta-chromium/chrome`, "Muse Browser"
155.0.8059.91). It refuses direct launch: *"Hatch WebGL domain
policy is required for browser startup"* — its policy file is
minted per browser task by the harness daemon
(`--hatch-webgl-allowed-domains-file` + `-sha256` switches);
no other engine exists on the VM (searched). Fabricating a policy
to satisfy a safeguard was not attempted, and this agent cannot
operate the managed browser. **Real-browser acceptance therefore
remains outstanding; it requires a browser-task session through
the parent agent.** The CDP driver written for it
(`evidence/studio-security/browser_acceptance.py` — stdlib-only
DevTools-protocol client: loads the page, counts the rack, types
into the real editor, clicks the real RUN button, reads canvas
outcome classes, collects console errors) is preserved and runs
against any launchable Chromium unchanged.

Executed instead, labeled honestly as **INTEGRATION (API-level),
not browser acceptance**: the exact API sequence the UI performs,
replayed against the hardened server on its real launch path —
page + token meta, /app.js, /api/dells (100), /api/state, /api/parse
(2 atoms), /api/execute (ok, 2 receipts, state shows the stored
value), /api/growth — **8/8 PASS** (`browser_acceptance.log`), plus
static contract verification that app.js calls exactly the five API
paths and injects the token header.

**Addendum (2026-11-03, post-submission, parent-run attempt 2):**
the parent agent ran the managed-browser session this section
called for, against the hardened server at this PR's final head
(c3d3254, VM loopback :8791, reachability verified from the VM:
`GET /` 200, `/api/dells` returned the registry). The managed
browser rejected direct loopback navigation before any network
access, and loopback-resolving public hostnames returned
ERR_CONNECTION_REFUSED from the browser's own network environment
(a public site loaded normally in the same session). Mechanism:
the managed browser does not share this VM's loopback. Acceptance
steps 2–6 were not performed and remain UNVERIFIED; real-browser
acceptance stays OUTSTANDING after two mechanistically distinct
blocked routes. Full record:
`evidence/studio-security/browser_acceptance_attempt2.log`.
Remaining routes: a human opening the Studio in their own browser
(a genuine REAL_USER_PATH check), or a future environment with a
launchable Chromium for the preserved CDP driver.

## 5. Regression evidence — read this section carefully

Local full-list runs (private copies, sequential):

| Run | Tree | Verdict |
|---|---|---|
| fwd #1 | candidate | **225/225 GREEN** |
| --twice (contended*) | candidate | RED — daf09 only, both passes |
| --twice (clean) | candidate | RED pass 1 — daf09 only (pass 2 not completed; leg already red) |
| --twice | **base 0f6dcb8** | RED pass 1 — daf09 only, identical signature |
| rev | candidate | 224/225 RED — daf09 only |
| fwd #2 | candidate | 224/225 RED — daf09 only |
| fresh clone fwd | candidate @66050cf | 224/225 RED — daf09 only |

*contended = the parent agent's PR #253 post-merge regression ran
concurrently in a separate worktree; included for completeness —
the clean rerun reproduced the red without contention.

The sole red entry in every case is
`form.daf09_timeout_tree_test:smoke`, always `rc=1 last=28/31
NOT_RETURNED_TRUE`, always the only failure. Isolated, the same
suite is **31/31 GREEN ×3 (passk) on the candidate, ×3 (passk) on
the base, and ×3 run directly in a private copy**. The first
full-list run of the day (fwd #1) was green; every later full-list
run reds identically on both trees. **Mechanism: UNKNOWN.** Per
AGENTS §31.3 this discrepancy is reported, not resolved: it
pre-exists this change (pristine base reproduces it), shares no
code path with this change, and concerns the suite whose
certification the Director already holds WITHHELD for environment
sensitivity. One further data point: GitHub exact-head CI at
66050cf ran the canonical regression in **both** --twice and rev
modes (form-smoke workflow) in the CI environment — **SUCCESS**
(§6). No claim is made from any of this beyond the table.

## 6. Verification

- Exact-head CI at verified head `66050cf` (direct `gh run view`,
  terminal state): package run 41696455101 SUCCESS (3.10 + 3.11);
  smoke run 41696455244 SUCCESS (15m5s; runs `form.regress --twice`
  and `--order rev`).
- Fresh clone from GitHub at `66050cf`: studio_security 35/35,
  gui_api 26/26; full regress per §5 table.
- Evidence bundle in-PR at `evidence/studio-security/` (20 files,
  MANIFEST.md with SHA-256 digests). Logs are Uni-produced
  execution records, not independently inspected by the Director.

## Anticipated probes

- *"The token is page-readable — local processes aren't stopped."*
  Conceded in §2 by design; the claim is scoped to web-borne
  callers; Question 3 asks whether local-process exclusion is in
  his threat model (it requires OS-level auth — a different
  circuit).
- *"413-before-read is a code-path claim."* It is behaviorally
  tested: the probe declares 200 KB, sends 1 KB, and the refusal
  arrives without the server waiting for the rest (suite check +
  M3 mutant kills exactly that check).
- *"Why does GET /api/state need no token while POSTs do?"*
  GETs never mutate; rebound reads die at the Host check;
  cross-origin reads die at same-origin policy. The residual
  (local-process reads) is the same boundary as the token's —
  named, not hidden.
- *"Did the DAF-09 reds come from your change?"* The base tree
  reproduces them identically in the same contexts, the candidate
  shares no code path with that suite, isolated runs are green on
  both trees, and CI is green at the head in both affected modes.
  Mechanism unknown; reported under §31.3, not explained away.
- *"Does --allow-remote make Studio network-safe?"* No — it makes
  exposure deliberate and loudly labeled; the packet claims
  nothing for that posture (Question 2).

## Questions for the Director

1. Does the token model (per-launch, page-served, POST-gating)
   plus the loopback-only posture satisfy you for local use — or
   is the ground file's leaner A+B+C+D set (no token) your
   preference, with the token deferred to an exposure circuit?
2. What additional proof would you require before any
   non-loopback exposure could be considered? (This circuit
   claims none.)
3. Is untrusted-local-process access (iii) in the threat model?
   If so, the honest mechanism is OS-level (unix socket / peer
   credentials), not another header — a separate circuit.
4. Browser acceptance: will you accept the CDP driver's output
   from a parent-run browser session as the acceptance evidence
   when a launchable browser is available, or do you require a
   human-driven session?

## Submission Verification (addendum)

Verified head `66050cf83fbef3a9b7aa0763beb08d0be734e53a`, tree
`66c14bbb34d076a3d08362f69e21c17e4c106ab3`: CI SUCCESS (package
41696455101, smoke 41696455244); fresh clone at this head (Studio
suites 35/35 + 26/26; full regress per §5). This report and the
evidence bundle were committed on top; production code is
identical between the verified head and the submission head.

## Correction (Director Mode C, 2026-11-03)

**Disposition received: CONDITIONAL ACCEPTANCE — design accepted
for a trusted, single-user localhost environment; two corrections
required before merge.** The four design questions are resolved
(token retained; network-deployment claims prohibited; untrusted
local processes out of scope; automated Chromium/CDP counts as
valid browser evidence when it genuinely runs the interface).
Browser acceptance itself remains OPEN. Both corrections are
executed below; nothing else was changed.

**Finding 1 (Director's words):** "*_origin_ok() permits an
Origin without an explicit port even when the server runs on a
non-default port. That does not bypass the separate session-token
check, but it contradicts the stated same-port security rule.*"

Fix (`gui/server.py::_origin_ok`, the only production-code
change): an omitted Origin port now resolves to the HTTP default
**80**, and the *effective* port is compared with the bound
server port — a no-port Origin is accepted only when the server
is itself bound to port 80. Host-header handling, the token
model, and GET posture are untouched.

Failing-first, on the Director's exact case (probe preserved in
the bundle: `correction_origin_probe.py`, real server bound to
port **8765**, valid session token, `Origin: http://127.0.0.1`
with no port, POST `/api/execute`):

- RED (pre-fix): **HTTP 200, store mutated** (`corrprobe` key
  landed) — `correction_probe_RED.log`.
- GREEN (post-fix): **HTTP 403, store snapshot unchanged** —
  `correction_probe_GREEN.log`.

The case is also added to `form/studio_security_test.py` (suite
35 → **36**; suite-level RED captured pre-fix in
`correction_suite_RED.log`). Post-fix: **studio_security 36/36**
(`correction_suite_GREEN.log`); **gui_api 26/26** with unchanged
assertions (`correction_gui_api.log`); legitimate same-origin
behavior (explicit matching port + token) preserved — the
suite's browser-shaped happy paths all pass.

**Finding 2 (Director's words):** "*The additional MANIFEST.md
self-reference is invalid and should be removed. It does not
indicate corruption of the other files.*"

Fix: the `MANIFEST.md` self-hash line is removed. The manifest
now lists **27 evidence files** (the original 21 plus the
correction probe script and its five run logs), every one of the
**21 previously verified digests preserved verbatim** (asserted
by recompute during regeneration), MANIFEST.md itself excluded,
and `sha256sum -c MANIFEST.md` run from the bundle directory
verifies **27/27 OK, exit 0**.

**Corrected code head:** `20ebbcb16466d37c78b415743ef93e46e3979a2e`,
tree `da785fda6b8d6d926c891aea122bda7150a980be`. This addendum and
the INDEX status update are documentation-only on top of it; the
final submission head's exact-head CI (all three checks) is
verified by direct `gh` query and recorded in the circuit
envelope. PR remains UNMERGED — merge authorization follows the
Director's verification of the corrected head.
