# DIRECTOR REPORT — Track D TD-1 Binding Foundation

Circuit: DIR-SUS-WAKE-2026-11-04 Priority 3 · Authority: Director
ruling on PR #261 (2026-11-04) — S1 approved, TD-1 authorized as a
bounded circuit; TD-2..TD-5 NOT authorized and NOT implemented.
Base: `24099af` · Frozen head: see PR.

## What was built (binding only — zero containment)

- **Schema (S1 recorded mapping):** `Unit.idea_id` (optional,
  default None), carried end to end: `Plane.place(idea_id=...)`,
  `BlankCube.place_idea`, Program persist serialization
  (`form/persist.py`), restore (`form/persist_rest.py`), legacy
  checkpoint files (they ride `serialize()`), and BlankCube pack
  export/restore. Legacy state without the field loads unbound.
- **Operation:** `Program.bind_unit_to_idea(unit_id, *, subject)`
  and `Program.binding_census()`, implemented in
  `form/mandell/unit_binding.py`. REPL-visible read-only via the
  existing `runtime` command (runtime_observe gains a binding
  summary; the REPL prints one line). No other surface changed.

## The three Director amendments — how each is discharged

1. **Validated target, not file existence.** Any set pointer is
   checked through `load_idea` (exists + parses + id matches).
   Missing → refusal `target_missing`; corrupt/mismatched →
   `target_invalid`; an Idea owned by another owner is missing for
   this owner. H1 is refused and reported, never silently rebound.
2. **No false in-memory success.** Order is: mint shell →
   `save_idea` → set pointer → `persist_rest.save`. If the Program
   save fails, the pointer is rolled back to None in memory and
   `BindingFailed` reports the orphaned shell id; the shell stays
   as census-visible canonical history (never auto-deleted, per
   the plan's H2 treatment). Cross-file atomicity is NOT claimed —
   the ordering guarantees the narrower fact that a persisted
   pointer never precedes its Idea.
3. **Competing instances.** Before minting, bind re-reads the
   persisted program state; a persisted pointer this instance does
   not hold → refusal `conflict` naming the persisted Idea id. The
   stale instance's pointer is untouched; no overwrite, no mint.

## Shell contract (TD3)

Fresh UUID; title = the unit's label; NO properties and no copied
Plane content (words/detail/goals stay in the Plane). Provenance is
exactly one `bridge_bind` change event on the shell — the Idea
model's idea-level provenance boundary (the same one archive/delete
use) — with `source=human`, `activity=bridge_bind`, and
`agent=<the real invoking subject>` (subject is required; an empty
subject refuses before any mutation).

Disclosed design point: the mint records its event through the
Idea's `_on_information_change` boundary from within the same
package, because the model exposes no public idea-level event API.
Flagged as Question 1 below rather than silently normalized.

## Evidence

- **Failing-first:** suite aborts on pristine code at import
  (`unit_binding` does not exist).
- **Targeted:** `form/track_d_td1_test.py` **24/24 GREEN** —
  schema carriage ×5 paths (place, persist, legacy-no-field,
  checkpoint, blank-cube pack out and back); bind happy path;
  shell purity (title only, zero active properties, exactly one
  event, subject provenance); durability across fresh load;
  idempotent re-bind (no second mint); **zero SemanticGraph
  writes** (graph + journal file hashes identical across a bind);
  refusals: unknown unit, H1 missing, H1 corrupt, foreign-owner;
  save-failure rollback + orphan census + recovery re-bind minting
  a fresh shell with the orphan retained; competing-instance
  conflict refusal; census exactness; runtime-state visibility;
  load-never-binds.
- **Mutants killed:** M1 existence-check instead of validated load
  (H1 corrupt goes red); M3 conflict rule removed (conflict check
  red); M4 rollback removed (rollback check red). A pointer-before-
  Idea ordering mutant is not suite-distinguishable without a
  crash-injection point between the two saves; the ordering is
  code-reviewed and stated, not test-claimed.
- **Regression:** `form.regress` ×3 sequential at the code head —
  forward GREEN 232/232, `--twice` GREEN (464), `--order rev`
  GREEN 232/232. Suite registered (canonical count 231 → 232) with
  the required `smoke()` entrypoint.
- **Fresh clone:** suite 24/24 in a clean clone of the branch.

## Anticipated probes

- *Generation rollback / confirm compensation carrying the field:*
  both ride the same `serialize()`/restore pair proven here
  (checkpoint round-trip is executed; generation files are
  program-state serializations). A dedicated generation-rollback
  round-trip was not separately executed — stated plainly.
- *Studio:* TD8 sequences Studio after TD-1's REPL-first surface;
  Studio does not display binding state in TD-1 (nodes_payload is
  untouched). No Studio claim is made.
- *Census orphan definition:* `unreferenced_idea_ids` includes
  pre-existing unbound Ideas; the suite distinguishes orphans only
  against a pre-bind baseline, and the census docstring says so.

## Questions for the Director

1. Is recording the shell's origin through the Idea model's
   internal change-event boundary acceptable, or should TD-1 also
   add a small public Idea API for idea-level origin events?
2. TD-1 is submitted for independent review. TD-2 (containment
   ops) remains unimplemented pending that review, per the ruling.
