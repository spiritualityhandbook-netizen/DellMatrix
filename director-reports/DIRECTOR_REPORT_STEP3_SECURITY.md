# DIRECTOR REPORT — Director order step 3 (security circuits)
For: Director (held for re-ruling; per Ace's 2026-10-31 cadence,
one report per closed circuit). From: Uni. Date: 2026-10-31.
Status of the work: IMPLEMENTED-VERIFIED by Uni. NOT certified;
certification is the Director's act on re-ruling (order step 14).

## Scope ruled on
DAF-02/B5 (P1, Sanitize disclosure), DAF-03 (P1, InternetGate
redirect/userinfo), DAF-10 (P2, fetch-log bound) — audit §4/§5,
completion order §8.3.

## Before (executed on e4b13ec, the pre-fix main)
Failing-first probe (synthetic canary, presence booleans only;
loopback server with hit counters):
- DAF-02: canary present in the execution result dict, messages,
  outcome-ledger record, and the SAVED program JSON. History clean.
- DAF-03: fetch of an allowed 127.0.0.1 URL redirecting to
  localhost (not allowed) returned ok with content; blocked-target
  hit counter = 1. _host_ok("https://example.com:pass@not-allowed
  .invalid/test") = True under the default allowlist, while
  urlparse hostname = not-allowed.invalid.
- DAF-10: 45 failed fetches -> fetch_log length 45 (cap 40).

## Fix (PR #164; candidate efbad97; tree 123c871)
- One redaction authority, form/mandell/redaction.py. For seeds
  containing Dell 41: executor_leaf and chain_exec build all echoes
  and returned seed/english from a redacted seed copy; the Dell-41
  IN line shows the sanitized representation; the execution
  observer sanitizes the receipt; outcome_ledger sanitizes any
  Dell-41 receipt at the persistence boundary. Sanitized audit
  facts preserved (dell, ok, redacted text, ordinary words). No
  digest substitution. No historical-data migration (per ruling).
- InternetGate: _host_ok uses urlparse — http/https only, userinfo
  rejected, parsed hostname matched against the allowlist (exact
  or subdomain). A gate-bound redirect handler authorizes each hop
  BEFORE connecting; _json_get host-checks and shares the same
  opener. Default OFF unchanged.
- Fetch log: one _append_log append-and-trim (cap 40) for success
  and failure; logged URLs are userinfo/query-free; error strings
  userinfo-stripped.

## Evidence
- Suite form/step3_security_test.py: 23/23 (saved-JSON witness,
  chain witness, blocked-hop ZERO hits, same-host and
  allowed-host redirect positive controls, userinfo refusal with
  no request, _json_get both ways, clean passthrough, non-Sanitize
  echo unchanged). In regress LIST; regress now 206 entries.
- Defect-restoring mutants, each killed, code restored and
  re-verified 23/23: redactor->identity 16/23; redirect
  validation off 21/23 (blocked fetch ok, hits=1); log trim
  removed 21/23 (len 45/50).
- Neighborhoods: d1_registry_leaf4 36/36 (its pinned raw-echo
  exhibit updated to the B5 FIX contract), gate_hardening 19/19,
  pp2_autonomy_charter 20/20, r76_connected 44/44, internet_gate
  smoke 6/6, eoc_i 146/146, symbiosis_ledger 39/39.
- Regress x3 on candidate: fwd 206/206, --twice 206+206,
  --order rev 206/206, all GREEN.
- Exact-head CI verified COMPLETE in a separate step before
  merge: Python package run 41203296037 SUCCESS; Form smoke run
  41203296125 SUCCESS (completed 2026-10-31T13:06:23Z).
- Merge 76a390dd43568c045ff198f0c954d1c0458f2f42 (normal merge
  commit; parents e4b13ec + efbad97); merge tree 123c871 ==
  candidate tree. Fresh-clone regress at merge: 206/206 GREEN.
- SWAT unanimity 4/4 recorded BEFORE implementation
  (goal hidden_files/step3_ground.md). Full packet:
  STEP3_SECURITY_PACKET.md.

## Limits / honest boundaries
- Redaction = Sanitize's canonical patterns (secret-key values,
  12+ digit runs) — the same semantics as the historical OUT
  line, now applied at every surface. No broader claim.
- Pre-fix historical program JSONs are not migrated.
- Port policy remains the documented host allowlist (no separate
  port restriction); scheme and userinfo are restricted and every
  hop's host is authorized.
- Third-party scanning remains EVALUATION_UNAVAILABLE, never PASS.

## Requested ruling
Re-rule DAF-02/B5, DAF-03, DAF-10 at step 14 (or incrementally
on this report): IMPLEMENTED-VERIFIED -> certified bounded scope
or further findings. Uni does not self-certify.
