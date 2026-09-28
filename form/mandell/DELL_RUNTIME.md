# Dell runtime coverage

Authoritative namespaces on Form:

- CORE_I `00-50` — locked action spine. Executor leaf path.
- CORE_II `51-99` — instruction architecture. `core_ii_exec.py` + `chain_exec.py`.
- ADDRESS `100-999` — reserved. Not production-active.

Multi-atom seeds execute every atom in order. CORE_I atoms use the existing leaf executor. CORE_II atoms use `execute_core_ii`. Registering a number is not completion.

## CORE_I 00-50

Behavior table unchanged. Single-atom CORE_I seeds take the original `execute_seed` leaf path (`_leaf=True` or one atom `<51`).

## CORE_II 51-99 — FORMALIZED runtime

| Dell | Name | Runtime |
|------|------|---------|
| 51 | Select | scope selection set |
| 52 | Filter | reduce selected |
| 53 | Scope | set execution boundary |
| 54 | Query | read selected/store |
| 55 | Set | assign store key |
| 56 | Get | read store key |
| 57 | Compare | structured compare |
| 58 | Match | pattern filter |
| 59 | Route | set route |
| 60 | Branch | record conditional |
| 61 | Join | rejoin marker |
| 62 | Parallel | declare concurrent set |
| 63 | Sequence | declare order |
| 64 | Until | condition marker |
| 65 | While | condition marker |
| 66 | ForEach | iterate selected |
| 67 | Any | existential |
| 68 | All | universal |
| 69 | None | absence |
| 70 | Count | cardinality |
| 71 | Measure | quantify selected |
| 72 | Limit | bound |
| 73 | Threshold | boundary marker |
| 74 | Weight | relative influence |
| 75 | Normalize | scale weights |
| 76 | Resolve | manifest resolver |
| 77 | Infer | labeled PROJECTED_NOT_FACT |
| 78 | Cause | causal edge |
| 79 | Depend | dependency edge |
| 80 | Context | semantic frame |
| 81 | Reference | address without copy |
| 82 | Group | collect |
| 83 | Ungroup | inverse of group |
| 84 | Copy | duplicate, original intact |
| 85 | Move | relocate, identity preserved |
| 86 | Delete | controlled remove |
| 87 | Replace | atomic swap |
| 88 | Patch | partial update |
| 89 | Diff | change-set snapshot |
| 90 | Trace | provenance log |
| 91 | Assert | invariant |
| 92 | Guard | block/allow |
| 93 | Try | snapshot + depth |
| 94 | Catch | consume last_error |
| 95 | Commit | stage snap |
| 96 | Revert | restore snapshot |
| 97 | Define | reusable definition |
| 98 | Alias | name bind |
| 99 | Compose | reusable chain body |

Status: FORMALIZED executable state on `program.core_ii`.
Not a 15-layer full-operator claim. Persistence/UI/hardware still open.

## ADDRESS 100-999

Reserved. See `address_space.py`. Do not execute as active operators.
