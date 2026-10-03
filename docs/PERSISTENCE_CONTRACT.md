# DellMatrix Persistence Contract (GDP-001 Phase 0, R1)

Authoritative statement of what the persistence layer guarantees, what it
does not guarantee, and what every later phase (Idea history, provenance,
Nursery/growth, AI observations) may rely on.

Code authorities (extend these; do not build competing ones):

- `form/dell_matrix/atomic_write.py` — Persistence V2 crash-safe file replacement.
- `form/persist.py` / `form/persist_rest.py` — program save/load/checkpoint
  (serialization envelope v7; staged load).
- `form/dell_matrix/nursery.py` — per-owner nursery file, optimistic
  concurrency, staged validation.
- `form/mandell/checkpoint_generation.py` — Checkpoint Generation V1
  (immutable sealed members + atomic manifest pointer).
- `form/mandell/core_i_recovery.py` — Dell 27 (checkpoint) / Dell 28
  (rollback) operations.

Executable coverage: `form/mandell/p0r1_persist_test.py` (19 checks,
2026-10-03). The contract below is what those tests pin down.

## 1. What is persisted (per owner)

| File | Writer | Content |
|---|---|---|
| `program_<safe>.json` | `persist.save` | Live working program state (envelope v7). |
| `nursery_<safe>.json` | `Nursery.save` | Live working proposals + conflict dispositions. |
| `program_<safe>_cp_<stamp>.json` | `persist.checkpoint` | Legacy timestamped checkpoint (explicit-rollback artifact). |
| `current_<ns>.json` | Generation V1 commit | CURRENT pointer: the committed generation id. |
| `gen_<ns>_<gid>.json` | Generation V1 commit | Generation manifest (member fingerprints). |
| `<kind>_<ns>.g_<gid>.json` | Generation V1 commit | Sealed member copies (`kind` in {nursery, program}). |

`<safe>` is `_safe_owner(owner)`; `<ns>` additionally binds the sha256 of the
exact owner bytes, so colliding safe names can never overwrite each other.

The program file's embedded `nursery` field is back-compat only and is
**never restored**; the nursery's live file is the authority for proposals.

## 2. Atomicity guarantees

**Persistence V2 (single file).** After any interruption, a canonical file
holds either the previous complete generation or the new complete
generation — never a partially serialized generation. Mechanism: serialize
fully before touching the target; sibling temp file (`.dmtmp.` infix, same
directory/filesystem); flush + fsync; atomic `os.replace`; best-effort
directory fsync (degradation is explicit, never silent). No backup
generation is kept (a backup would be a second writer path).

**Generation V1 (logical state = nursery + program).** Commit order:
save live files → copy byte-exact immutable member copies → verify
fingerprints → write manifest → atomically swap the CURRENT pointer (the
commit boundary). A crash before the pointer swap leaves the previous
committed generation authoritative; a crash after exposes the new complete
generation. Member files are never overwritten after sealing. Retention
keeps the current + previous committed generations; older ones are pruned.

## 3. Ownership: committed vs working state (non-aliased)

- **Committed/sealed state**: generation member files. Immutable. Owned by
  the manifest's sha256 fingerprints. No `Nursery` or `Program` instance
  obtained from `load_checkpoint` / `rollback` writes to them — ever.
- **Mutable working state**: the live per-owner files
  (`program_<safe>.json`, `nursery_<safe>.json`). Owned by exactly one
  binding each: `persist.save` always targets `_path(program.owner)`;
  `Nursery.save` targets the instance's bound path.

**Rollback (Dell 28) ownership repair (P0R1 fix).** A generation load
stages the nursery from the sealed member for *reading* the committed
content, then immediately re-points the instance to the live owner file
(`Nursery.repoint_to_live`, wired in `persist_rest._load_impl`). The
in-memory rolled-back proposals are untouched; the sealed member is
unreachable for writing from the moment rollback returns, and the
manifest fingerprint stays valid.

**Eager rollback convergence (Director Decision 2, gate R1; Finding 1, gate R2).**
`core_i_recovery.rollback` eagerly converges live working state with
pair-atomicity: after the generation is validated and the program built,
the live program/nursery pair reflects the target generation's state
*before rollback returns*. A fresh `persist_rest.load(owner)` observes
the rolled-back state with no subsequent save required.

Transactional model (journaled two-file transaction):
PREPARE (serialize both payloads, write journal {phase: prepared} with
old/new fingerprints) > STAGE (write both payloads to staging files;
journal -> {staged}; live files untouched) > COMMIT (atomic rename
staging -> live for both files; the commit boundary; journal ->
{committed}) > CLEANUP (journal removed) > VERIFY (fresh reload matches)
> RETURN.

Crash recovery: `recover_rollback_transaction` runs inside every
`persist_rest.load` before state is exposed. FAIL-CLOSED (Gate R3): recovery
must establish a proven-coherent pair or raise RollbackRecoveryError; it
never suppresses exceptions and never exposes potentially hybrid state.
A 'prepared' journal means nothing was staged -> live files verified
against recorded old fingerprints -> old pair authoritative. A
'staged'/'committed' journal means the commit is deterministically
completed -> canonical files verified against recorded target
fingerprints (actual staged bytes) -> target pair authoritative. After
recovery, a reader sees EITHER the complete old pair OR the complete
target pair. NEVER a hybrid program/nursery pair. Corrupt journal,
unknown phase, missing fields, missing staging files, or fingerprint
mismatch -> explicit failure, no live state exposed.

Failure atomicity: all validation and serialization precede all writes.
A failure before staging leaves live files byte-identical — zero partial
mutation. A failure at/after the staging boundary leaves a journal that
recovery deterministically completes. Sealed members are never written.

## 4. Sealing invariants (executable)

1. No code path writes to a `*.g_<gid>.json` member after sealing except
   the sealer itself (`_seal_members`, before the manifest exists).
2. Every retained member's bytes equal its manifest sha256 at all times
   (asserted across rollback/mutate/save/commit batteries).
3. `load_checkpoint` validates pointer → manifest → every member
   fingerprint → staged parse, and never mixes generations.
4. After `rollback`, `program.nursery.path` is the live owner file, never
   a member path.

## 5. Failure semantics (honest, never silent)

| Situation | Behavior |
|---|---|
| `kill -9` mid-save | Canonical file keeps the previous complete generation; temp files are never mistaken for state. |
| Crash before pointer swap | Previous committed generation authoritative. |
| Crash after pointer swap | New complete generation loadable. |
| Commit failure before boundary | `CheckpointCommitError`; previous generation authoritative. |
| Corrupt sealed member | `CheckpointLoadError` (fingerprint mismatch) — explicit. |
| Missing sealed member | `CheckpointLoadError` (absent member) — explicit. |
| Corrupt manifest/pointer | `CheckpointLoadError` — explicit, never guessed. |
| Committed generation invalid, previous valid | Deterministic recovery via `previous_generation_id`; receipt records `recovered_from`. |
| No committed generation | `CheckpointNotEstablished` → legacy load path; `rollback` → `FileNotFoundError("rollback_missing")`. |
| Nursery file changed under an instance | `NurseryConflictError` — lost update refused, never silently overwritten. |
| Corrupt nursery file | `NurseryLoadError` — never silently replaced with an empty nursery. |
| Serialization failure | Target untouched (`AtomicWriteError`). |

`load()` / `load_checkpoint()` never write any file. A failed load never
leaves a partially mutated in-memory program behind (staged validation).

## 6. MUST NOT

- Never write to a sealed generation member through any `Nursery`/`Program`
  instance or helper. Members are written once, by the sealer.
- Never treat absence of a disqualifier as proof of state (e.g. "file
  exists" ≠ "generation committed" — only the CURRENT pointer decides).
- Never invent recovery generations: valid canonical → load; else explicit
  failure. The only sanctioned fallback is the manifest's
  `previous_generation_id` link.
- Never load a generation member with `Nursery.load(member_path)` +
  `save()` directly; members are only consumed through
  `load_checkpoint`/`rollback`, which establish the live-file binding.
- Never convert an unavailable security evaluation into PASS
  (EVALUATION_UNAVAILABLE_QUOTA stays as-is).

## 7. What later phases may rely on

- Save/load/checkpoint/rollback are coherent across fresh OS processes
  (proven, not assumed).
- One logical state = one committed generation (nursery + program joined
  by manifest, never mixed).
- Optimistic concurrency on the nursery file; atomic replacement on the
  program file.
- Every mutation path (`add`/`confirm`/`reject`/`clear_rejected`) is
  all-or-nothing against the canonical file.
- Outcome records (`outcome_ledger`) ride the program member into sealed
  generations as immutable evidence.

## 8. Performance baseline (Phase-0 §21; 200-unit program, 2026-10-03)

save 0.032–0.040s · load 0.005–0.027s · commit 0.135–0.168s ·
rollback 0.009–0.014s. Full regression suite duration is recorded by the
R1 return packet / CI, not here.
