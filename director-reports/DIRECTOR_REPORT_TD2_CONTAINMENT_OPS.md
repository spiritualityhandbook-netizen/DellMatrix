# DIRECTOR REPORT — TD-2: Canonical Idea Containment Operations

**Circuit:** Track D TD-2 (containment operations), authorized by the Director's Mode D review 2026-11-04 (Q2) under the nine Track D decisions of 2026-11-04. Executed in SUSX100,000 Cycle 1 (build) + main-session regression repair + Cycle 4 (fresh clone), 2026-11-04.
**Branch:** `uni/td2-containment-ops`. **Code head:** `eb038d4728392306cc0a5e00335b4214d0f143ec` (TD-2 commit `9a3cf88` + merge of main `289fcdc`); this report rides in the same PR, so the PR head will be the report commit — CI evidence is read at the PR's final head.
**Status:** SUBMITTED — one frozen candidate for Director review. The TD-2 line STOPS here per the circuit contract; no TD-3 or further Track D circuit is auto-authorized. Uni label on merge: MERGED_VERIFIED_BY_UNI (not a certification).

## What DellMatrix can do now that it could not before

A user at the REPL (or any caller of the public Program API) can **nest** one Plane unit inside another, **promote** a nested unit back to top level, and **reparent** a unit to a different parent — with the containment living in canonical Ideas inside the SemanticGraph, the sole containment authority. Units are addressed by id or unique label; nobody handles canonical Idea ids. Both endpoints are lazy-bound through TD-1 (title+provenance-only shells, real invoking subject, source HUMAN) before any graph append. The REPL commands print every refusal with its kind — no invisible errors.

## Implementation (diff: 6 files, +1039/−4 at the code head)

- `form/mandell/unit_containment.py` (NEW, 479 lines): the bridge. `nest_units`, `promote_unit`, `reparent_unit`, `containment_view` (derived read: binding + graph queries composed with unit existence and Idea lifecycle), plus `ContainmentRefused` / `ContainmentFailed` mirroring the TD-1 error discipline. Every op runs inside the TD-1-R2 `owner_state_lock` (re-entrant; inner binds join); lock-busy past the bounded wait refuses `state_locked` — no unlocked fallback (§31.2).
- `form/open.py`: four thin Program wrappers (`nest_units`, `promote_unit`, `reparent_unit`, `containment_view`); TD-1 comment updated to point at TD-2.
- `form/repl.py` (+158): REPL-first surface — `nest`, `promote`, `reparent`, `containment` commands resolving unit ids/labels (exact id first, else unique label; ambiguity is a printed refusal listing candidate ids).
- `form/mandell/unit_binding.py`: docstring-only pointer to the new module (no behavior change).
- `form/track_d_td2_test.py` (NEW, 369 lines, 28 checks) + registration in `form/regress.py` (canonical count 235 → **236**).

## Contract enforcement (per the nine decisions + amendments)

- **Sole authority:** no Plane containment field, no cache, no second store; every read resolves through a freshly loaded SemanticGraph; the bridge discards its graph instance per op. `Unit.parents` (lineage) is never read or written as containment.
- **Prevalidation before append:** lifecycle gate (TD4 — both endpoint Ideas must load validly AND be `LifecycleState.ACTIVE`; non-ACTIVE refuses `idea_not_active`; missing refuses `target_missing`; corrupt/id-mismatch refuses `target_invalid` — validated load, never file existence); sandbox gate (TD7 — endpoint isolation key `(sandboxed, sandbox_id)` must match, refused BEFORE any mint; an inconsistent unit keys fail-closed); single-parent (a different active parent refuses `second_parent`, demanding explicit reparent; same parent is an idempotent no-op); self/cycle refused pre-append with `GraphInvariantError` as translated backstop, never leaked raw.
- **Ordering & honesty:** bind child → bind parent → graph append (each bind TD-1-ordered). A graph failure after bindings raises `ContainmentFailed` whose detail **discloses the partial bindings**; the persisted graph is unchanged (graph `_append` rollback + fresh reload per op). Bound-but-unnested is a normal, disclosed state. Retry converges (binds and graph ops are idempotent).
- **Identity:** promote/reparent never change unit id or idea id; promote supersedes the CONTAINS edge and reparent is the graph's atomic append pair — historical edges preserved (asserted from the persisted graph JSON).
- **No scope creep:** no bulk bind/migration, no unbind/rebind, no cross-sandbox or cross-owner containment, no Exchange containment transfer, no Dell verb, no Studio work, no TD-3.

## Evidence

- **Failing-first:** the suite fails at import on the pristine base (`form.mandell.unit_containment` absent) — log retained in the run record.
- **Targeted suite:** `form/track_d_td2_test.py` **28/28 GREEN** — three-level ancestry root-first, breadcrumb agreement with the graph, idempotent same-parent nest, second-parent refusal, reparent identity + superseded-history, promote identity + subtree untouched, promote-of-unbound mints nothing, self/cycle refusals, cross-sandbox refusal before mint, same-sandbox allowed, archived-child refusal, graph-save-failure injection (ContainmentFailed + partial-binding disclosure + persisted graph unchanged), stale-instance conflict via TD-1 reconciliation, REPL breadcrumb-by-label, REPL visible refusals, REPL promote. Test realism: **INTEGRATION** (public Program API + REPL handler path), not REAL_USER_PATH.
- **Mutants (4, each killed by its target check, inverse-edit reverts):** sandbox gate dropped → killed by "cross-sandbox nest refuses"; lifecycle gate dropped → killed by "archived child refuses"; ancestry resolution broken → killed by "three-level ancestry resolves to units root-first"; partial-binding disclosure removed → killed by "graph failure discloses the partial bindings and leaves the persisted graph unchanged."
- **Full regression ×3 (sequential, main session, terminal logs):** fwd **236/236 GREEN**; `--twice` **236/236 GREEN**; `--order rev` **236/236 GREEN** at code head eb038d4. (The first chain attempt was cron-launched and died with its session/VM; it was recorded as NO RESULT and re-run from the main session per standing law — no pass was ever claimed from interim output.)
- **Fresh clone:** targeted suite at eb038d4 in a clean clone: **28/28 GREEN, rc=0**.
- **Exact-head CI:** this PR's checks at its final head (reported in the PR; merge only on all terminal PASS per the hard gate).

## Boundaries and exceptions (stated, not buried)

1. **No cross-file atomicity is claimed.** Bridge ops hold the owner-state lock across binds + graph load/mutate/save, so bridge-vs-bridge and bridge-vs-canonical-save contention is serialized; writers that bypass both the lock and the bridge (e.g. a direct SemanticGraph user in another process) are NOT fenced by TD-2 — disclosed in the SWAT pre-mortem (probe 4).
2. **Propagation failure** (`_propagate_structure`) is not separately fault-injected at the bridge level in v1; the graph's own suites cover `_append` rollback, and bridge-level graph *save* failure IS injected and green.
3. The containment view is derived per call; there is no persisted view to audit — by design (no second authority), at the cost of a graph load per view.
4. DAF-09 and whole-program certification remain WITHHELD; nothing in this circuit touches them.

## Anticipated probes

- *"Show me the second containment store."* — There is none: grep the diff; containment bytes exist only in `graph_<owner>.json`; `containment_view` composes binding + graph queries at call time.
- *"Kill it between the second bind and the append."* — Both shells + pointers persist (valid TD-1 bindings, census-visible); no edge exists; the next op discloses/uses the existing bindings idempotently. The injected save-failure check proves the failure-side shape of this.
- *"Two processes nest the same child."* — Both serialize on the owner lock; the second sees the first's committed parent and refuses `second_parent` unless it explicitly reparents.

## Questions for the Director

1. TD-2 disposition: certify within the stated boundaries, or are additional probes required (e.g. a bridge-level propagation fault-injection check) before certification?
2. The disclosed unfenced path (direct SemanticGraph writers outside the bridge) — acceptable as a stated boundary for v1, or should a follow-up circuit fence graph persistence itself?
