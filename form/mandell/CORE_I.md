# Core I 00-50 — maturity from runtime

Dispatch lives in `executor_leaf.py`. Closable recovery/measure/external arms run through `core_i_ops.py`. Front door stays `execute_seed`.

Message output is not implementation. A `primary == N` arm is not maturity.

## Closed this circuit (local state already existed)

| Dell | Level | State |
|------|-------|--------|
| 27 Checkpoint | INTEGRATED | durable program snapshot (plane + Core II durable) |
| 28 Rollback | INTEGRATED | restore that snapshot; missing file fails `rollback_missing` |
| 23 Lock / 24 Unlock | EXECUTABLE + TESTED | sandbox on/off |
| 32 Pause / 33 Resume | EXECUTABLE + TESTED | locomotion idle/walk |
| 18 Mirror | EXECUTABLE + TESTED | read-only unit listing |
| 34 Stamp | EXECUTABLE + TESTED | `{mark, ts}` |
| 35 Discover | EXECUTABLE + TESTED | `{ids, count}` |
| 40 TokenCount | EXECUTABLE + TESTED | numeric `last_measure` |
| 44 Bridge / 47 Embed | CONTRACT | explicit `*_unavailable` — no fake provider |

27 ≠ 93. 28 ≠ 96. Transaction revert does not consume the Core I checkpoint file.

## Partial (stateful but not product-complete)

| Dell | Honest status |
|------|----------------|
| 08 Create / 10 Keep | create unit / save session |
| 16 Decay | resonance score decay — not unit deletion |
| 21 Merge / 22 Split | add units; parents are not destroyed; no typed lineage graph yet |
| 29 Compress / 30 Expand / 38 Distill | derive new units; not a lossless codec |
| 41 Sanitize | redacts label text; does not rewrite live units |
| 06 Cycle / 13 Loop | `grow_ideas` proposals only |
| 45 Translate | existing bridge path |

## Message shells (registered + dispatch only)

00 Nova, 01 Initiate, 02 Persona, 03 Logic, 05 Tone, 11 Architect, 12 Test, 17 Shadow, 20 Alpha, 31 Simulate, 36 Inject, 37 Nurture, 39 Schema, 42 Retry, 43 Fallback, 48 Macro, 49 Profile, 50 Manifest.

These are not product features.

## External blockers

- 44 Bridge needs a bound provider
- 47 Embed needs a vector model
- 17 Shadow is not parallel compute
- 37 Nurture is nursery lifecycle (confirm/reject/use/supersede), not a network stream
- Nursery stays locked for live matrix writes

## Next 3 localities

1. typed unit lineage for 21/22/14/07/15
2. lossless 29/30 only after a codec is chosen
3. 12/03/39 machine-readable result cells without a second predicate engine
