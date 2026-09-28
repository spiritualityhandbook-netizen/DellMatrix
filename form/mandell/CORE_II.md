# Core II runtime

Status: **FORMALIZED**. Certification is the passing 51-99 contract suite on the same HEAD.

## Persistence

Durable: scope selected store groups defs aliases compositions weights context route refs causes deps last_assert last_guard

Transient: last_result last_diff frames last_frame last_control flow_taken flow_blocked tx snapshots staged try_depth traces limit

Limit is a session bound for loops and composition expansion. It is not world state.

`last_result` is never written into store. `73[Threshold]` does not write `_threshold`. Durable threshold values require explicit `55[Set]`.

## Diff baseline

- Inside an active transaction: checkpoint of that transaction
- Otherwise: prestate of the last successful 84-88 mutation
- Unrelated older snapshots are not used

## Transaction model

States: OPEN · FAILED · CAUGHT · COMMITTED · REVERTED

Legal transitions:
- OPEN → COMMITTED
- OPEN → FAILED → CAUGHT
- OPEN → REVERTED
- FAILED → CAUGHT
- FAILED → REVERTED
- CAUGHT → COMMITTED
- CAUGHT → REVERTED

COMMITTED and REVERTED are immutable. `try_depth` counts only active frames. Terminal frames stay in history for trace and do not change execution.

Catch next action is explicit: revert restores the checkpoint; commit accepts current durable state.

## Composition bound

Expansion bound is `72[Limit]` when valid, else 8. Direct, indirect, and alias cycles fail with `compose_cycle` before execution. Depth overflow fails with `compose_depth` and does not run the body.

## Semantic boundaries

| Core II | Core I cousin | Boundary |
|---------|---------------|----------|
| 57 Compare | 18 Mirror | typed relation vs reflection |
| 89 Diff | 18 Mirror | before/after/changed vs likeness |
| 91 Assert | 12 Test | runtime predicate vs CORE_I test verb |
| 95 Commit | 20 Alpha / 50 Manifest | accept staged mutation vs begin/manifest |
| 96 Revert | 28 Rollback | tx/snapshot restore vs CORE_I rollback |
| 97 Define | 11 Architect / 39 Schema | named semantic body vs design/schema |
| 98 Alias | 48 Macro | name reference vs macro expand |
| 99 Compose | 48 Macro | executable Dell sequence vs macro |
| 53 Scope | 36 Inject | semantic frame vs injection |
| 85 Move | 19 Drive | ownership transfer vs drive |
| 70 Count | 40 TokenCount | selection cardinality vs token count |

## Nursery

Generic store mutation does not define future idea destruction. Nursery is not implemented here.
