# Core II runtime

Status: **FORMALIZED**. Not full maturity. Certified only against the closed 51-99 contracts.

## Persistence

Durable: scope selected store groups defs aliases compositions weights context route refs causes deps last_assert last_guard

Transient: last_result frames last_frame last_control flow_taken flow_blocked tx snapshots staged try_depth traces limit

Limit is a session bound for loops. It is not world state.

Snapshots and staged lists are transaction runtime only.

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

## Transaction law

93 opens a checkpointed frame. 95 accepts in-place mutations. 96 restores an open frame only. A committed frame rejects unrelated revert.

## Nursery

Generic store mutation does not define future idea destruction. Nursery is not implemented here.
