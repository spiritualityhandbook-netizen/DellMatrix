# Mandell 00-99 unified runtime

One address space. Two execution bodies. One front door: `execute_seed`.

| Band | Body | Front door |
|------|------|------------|
| 00-50 CORE_I | `executor_leaf.py` | single-atom leaf; multi-atom via `chain_exec` `_leaf=True` |
| 51-99 CORE_II | `query_ops` · `control_runtime` · `spectrum_ops` | `chain_exec` → `execute_core_ii` |

151+ names in `address_space.py` are reserved labels, not 00-99 activation.

## Dispatch

1. `executor.execute_seed` parses the seed.
2. Multi-atom or primary 51-99 → `chain_exec`.
3. Single-atom 00-50 → `executor_leaf`.
4. `chain_exec` sends 00-50 atoms back through the leaf and 51-99 atoms through Core II.

Parser does not care about the 50/51 boundary. Number stays the number even if the bracket word is foreign (`08[Select]` stays 08).

## Persistence

v7 document. Core I units live in the plane snapshot. Core II durable fields live in `core_ii`. Transient Core II fields do not survive save/load.

## Overlap (distinct, not duplicates)

| Pair | Distinct effect |
|------|-----------------|
| 18 Mirror / 57 Compare / 89 Diff | live listing vs typed predicate result vs mutation change-set |
| 12 Test / 91 Assert | Core I validation verb vs Core II predicate fail |
| 20 Alpha / 50 Manifest / 95 Commit | floor close vs bring-into-form vs accept staged tx |
| 28 Rollback / 96 Revert | Core I restore vs Core II tx/snapshot restore |
| 11 Architect / 39 Schema / 97 Define | design note vs shape note vs reusable Core II body |
| 48 Macro / 98 Alias / 99 Compose | Core I shortcut note vs name bind vs executable expansion |
| 36 Inject / 53 Scope | load-into-scope note vs Core II scope field |
| 19 Drive / 85 Move | direction note vs store ownership transfer |
| 40 TokenCount / 70 Count | cost measure note vs selection cardinality |

No pair was collapsed. No number was deleted.

## Maturity (honest)

- **FORMALIZED**: registered 00-99 (100/100).
- **EXECUTABLE**: every 00-99 number has a dispatch arm. Many CORE_I arms are message shells.
- **BEHAVIORALLY_TESTED**: Core II contract suites + this unified suite for named cross-core circuits.
- **INTEGRATED**: cross-core A–E, save/load, `>>` failure, 50>51 flow, compose/control spanning both cores.

FORMALIZED ≠ INTEGRATED. Message-shell Core I Dells are not product features.

## Resonance gaps (not work in this circuit)

1. Core I 27 file checkpoint vs Core II 93-96 transaction store — compatible, not unified storage.
2. ManifestSet expands one Dell number; cross-core composition is chain/flow, not mixed numbers in one bracket.
3. 44 Bridge / 47 Embed / 17 Shadow remain notes, not product subsystems.
4. 100-999 stay reserved.
5. Nursery stays locked.

## Tests

`form/mandell/unified_runtime_test.py` is the integration suite. Unit contracts stay in the existing Core I / Core II files.
