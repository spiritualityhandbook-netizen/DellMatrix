# RUNTIME TRUTH INVARIANTS

**Authority:** GDP-001 Phase 0, Requirement 5 (Runtime Truth).
**Scope:** all DellMatrix view, report, perspective, and display surfaces —
any code that turns Program state into something a human or AI reads.
**Status:** binding for all subsequent GDP phases.

---

## R5-1. No confident empty over unverified state

A view MUST NOT report a confident inventory (e.g. "0 nodes", "empty",
"nothing found") when it has not verified the state it claims to describe.
Blindness is not emptiness.

* Origin: MPC-012 found `perspective_views.py` blind to the real Program path
  (`program.cube.session.plane.units`), confidently reporting `count: 0`
  while real ideas existed. Fixed in `form/dell_matrix/perspective_views.py`
  via `_probe_nodes()` (canonical-path rewire) + honest UNKNOWN reporting.
* Enforcement: a `count` field may appear ONLY when the inventory was read
  from a verified source. When the source cannot be verified the field is
  omitted entirely, never zero-filled.

## R5-2. Every reported view carries its epistemic status

Every view/report dict MUST include:

* `epistemic_status` — one of the exhaustive labels below
* `data_source` — the concrete path the data was read from
  (e.g. `"program.cube.session.plane.units"`)

A status-bearing surface must never silently drop the status when it
summarizes or re-wraps another view's output
(see `DynamicViewSwitch.switch_to` sight summary).

## R5-3. Status labels are exhaustive

The ONLY permitted values of `epistemic_status`:

| Label         | Meaning                                                        |
|---------------|----------------------------------------------------------------|
| `REAL`        | read from the verified canonical Program state path           |
| `PARTIAL`     | read from a legacy/non-canonical adapter path (may be stale)   |
| `UNAVAILABLE` | a state source exists but could not be read                    |
| `UNKNOWN`     | no verifiable state source                                     |
| `UNSUPPORTED` | the requested operation is not supported                       |

No other label may be invented ad hoc. If none fits, the surface is
mis-designed — fix the surface, not the label set.

## R5-4. Every computed display value traces to a read of real state

No-theater law applied to display: if something is shown, a real read
produced it. Specifically:

* vision/cone computations run ONLY over verified node lists; a blind
  program gets an honest "cannot verify" report, never a fabricated vision
  over invented data;
* skin/position/label strings are normalized from the read objects
  (`_normalize_node`); Enum rendering uses `.value`, never `str()` of the
  Enum member;
* aggregate reports (`by_skin`, counts) are computed from the same verified
  list the view returns — never from a parallel or cached copy.

## R5-5. Canonical paths win over adapters

When several node-source paths exist, the verified canonical path is
authoritative. Legacy adapters (`program.plane.all_nodes()` /
`program.plane.nodes`) are retained for compatibility but their output is
always labeled `PARTIAL` with `data_source` naming the adapter. The
canonical inventory path for Program nodes is:

```
program.cube.session.plane.units   (Plane.units: id -> Unit)
```

If the canonical path moves, this document and `_probe_nodes()` move with it
— adapters must not silently become the truth.

## R5-6. Pose and body defaults are labeled, not silent

`_pose_from_program()` falls back to `((0.0, 0.0), "N")` when no avatar body
is readable. That fallback is a default pose, not a measured one, and must
not be presented as the body's actual position. (Full pose-status plumbing
is deferred to Phase 7 perspectives work; the fallback itself is honest as
long as it is not claimed as measured.)

## R5-7. Rewraps preserve honesty

Any code that summarizes, truncates, or re-wraps a view (switchers,
transactions, audio/prediction consumers) MUST propagate
`epistemic_status` and `data_source`, and MUST NOT synthesize a `count`
from a status-less summary. A summary of an UNKNOWN view is UNKNOWN.

---

## Verification

* `python3 -m form.dell_matrix.perspective_views` — module smoke (13 checks)
* `python3 -m form.dell_matrix.perspective_runtime_truth_checks` — 26 checks,
  including the real-`Program` integration proof and the blind-program
  negative paths. (Named `*_checks.py`, not `*_test.py`, so `form.regress`
  auto-discovery does not require a `LIST` edit on this branch — wire it into
  `form/regress.py` LIST at integration time.)
* Canonical regression: `python -m form.regress` (full suite) must stay green.

## Open / deferred

* Full pose-source status plumbing (R5-6) → Phase 7.
* `spatial_audio` / `world_predict` consume `_nodes_from_program()` (list
  only, status discarded) and have no live callers in `form/open.py` or the
  REPL → Phase 7 perspectives wiring, recorded in the GDP ledger.
* Volumetric/spatial honesty (all real ideas at `(0,0)`) → Phase 4; this
  requirement fixes *visibility* of state, not *meaningfulness* of position.
