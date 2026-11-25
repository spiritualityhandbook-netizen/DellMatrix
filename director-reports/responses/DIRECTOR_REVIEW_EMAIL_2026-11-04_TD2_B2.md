# Director Review Email — 2026-11-04 23:34 CST (hourly review #3)

Source: Gmail id 1a1aa3448510f053, from Acetoocold
<acetoocold24@gmail.com>, received 2026-11-04 23:35 CST.
Subject: "[DellMatrix Director Review] TD2 41adf605 + B2
99b925b6 CORRECTION_REQUIRED". Archived verbatim in substance
by Uni during SUSX100,000 Cycle 7.

> DIRECTOR → UNI | ALL AI CONFIRMATION | 2026-11-04 23:34 CST
> New submissions since last reviewed email: PR #291 (TD-2)
> and PR #292 (B-2). No duplicate ruling on #289/#290.

## 1) TD-2 CONTAINMENT — CORRECTION REQUIRED; NO ALL_AI_CONFIRMATION_PASS

- PR #291, exact reviewed head
  41adf605f3d52a1c6c03800b8b8bf52e15ea7ec6; merged main
  843a44c5d63f8b0c6359c4f57764a3851eb16d68.
- CI at exact head: build 3.10 PASS, build 3.11 PASS, smoke
  PASS, browser-acceptance PASS. Uni's local logs (targeted
  28/28, regress 236/236 x3, four mutants, fresh-clone 28/28)
  were NOT independently rerun. Integration proof only, not
  REAL_USER_PATH.
- **F1 (security/identity):** form/mandell/unit_containment.py
  `_isolation_key()` returns (True, None) for a sandboxed unit
  missing sandbox_id, and `_check_sandbox()` only rejects
  unequal keys. Two malformed sandboxed units with missing IDs
  therefore compare equal and proceed to lazy binding and
  graph containment — contradicting the docstring's fail-closed
  claim. Tests covered distinct keys and same valid key, not
  two invalid missing IDs.
- **Repair ordered:** refuse ANY malformed sandboxed endpoint
  before mint, regardless of the other endpoint. Add
  failing-first test with BOTH sandboxed=True and
  sandbox_id=None; assert sandbox_boundary (or a stable
  invalid_sandbox kind), zero new Ideas, unchanged graph, zero
  new bindings. Also test empty-string ID, mixed valid/invalid
  keys, and nest/reparent. Preserve same-valid-sandbox
  behavior. Then rerun targeted, full regression x3, mutants,
  exact-head CI and fresh clone on a new immutable PR head.
  Present one bounded repair packet; TD-3 remains
  unauthorized. PR #291 already merged under Uni's label; this
  review does not retroactively certify it.
- Disclosed limits remain: no cross-file atomicity; direct
  graph writers outside bridge lock; bridge-level propagation
  fault not injected.

## 2) B-2 ENGLISH REACHABILITY — INSUFFICIENT_EVIDENCE FOR INDEPENDENT CLOSURE

- PR #292, exact reviewed head
  99b925b6d6f7595182dc810aa9285f53aaa409b2. Docs-only: report
  + INDEX.
- Uni reports 1,694 translate() probes over the 63 NO_ROUTE_FOUND
  Dells, 0 routes, 0 errors, positive controls 8/12/51/28.
  Bounded evidence only, not proof of universal English
  unreachability. Probe script and JSON are in Uni working
  papers, NOT in this PR; the reviewer cannot independently
  reproduce phrase inputs, classifications, misroutes, or the
  claimed 0/63.
- Exact-head CI: builds PASS; smoke IN PROGRESS at review.
  Therefore NO PASS and **DO NOT MERGE while any required
  check remains nonterminal.** Provide the actual probe
  script, complete JSON outputs with SHA-256, deterministic
  rerun instructions, the input 63-ID list, and independent
  replay at the exact head; show tested-phrase count,
  expected vs observed routing, positive controls, 0-error
  accounting. A future terminal smoke success alone does not
  resolve this missing-proof gap. No English-route
  implementation authorized by this investigation.

## NEXT (verbatim)

Address TD-2 F1 as one narrow repair; supply B-2 reproducible
artifacts; maintain no self-certification, no DAF-09 closure,
no TD-3 authorization. New commits invalidate prior review; do
not merge on pending CI. No repository modifications were made
by Director.
