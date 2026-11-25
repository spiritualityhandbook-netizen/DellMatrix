# CORE I UNSUPPORTED-ARGUMENT CONTRACT REVIEW — Director Report

**Circuit:** Core I unsupported-argument contract review (Director
execution sequence item 3 — PR #252 ruling Q-D3 deferred Core I to
this review; PR #253 certification Q3 confirmed the sequence).
**Mode:** INVESTIGATION / REVIEW. No production code changed, no
test or pin edited. The deliverable is re-verified evidence, a
harm classification, an options analysis, and a recommendation
for the Director to rule on.
**Base:** main `7e3dcdde1cb74e90bcccf8766b4e11df419b8e71`
(post-PR #254), tree `117402446fddeee128584c050e78902a60fdf469`.
**Branch / PR:** `uni/core-i-contract-review` — docs-only,
UNMERGED by design (the PR #252 pattern: investigation PRs merge
only after the Director accepts them).
**Claim ceiling:** PUBLIC_ENTRY_PATH (`form.mandell.executor.
execute_seed`) for the census and chain probes; REAL_USER_PATH
(literal `python3 -m form.repl` subprocess transcripts) for the
REPL exhibits. All behavioral evidence is Uni-executed; the
evidence bundle is in-PR with a SHA-256 manifest so every digest
can be independently recomputed.

## 0. PR #255 grounding (required preliminary)

PR #255 (Studio security, `uni/studio-security`, head `9008be21`,
OPEN, unmerged) touches `gui/`, `director-reports/`, and three
`form/` files: `form/regress.py` (+2 lines — one suite
registration, registry only), `form/gui_api_test.py` (+17,
Studio API suite), `form/studio_security_test.py` (new). It
touches NO Core I execution path (`executor_leaf.py`,
`core_i_ops.py`, `chain_exec.py`, `signatures.py`, `executor.py`,
`seed.py`, `live_identity.py` — none). This review is based on
main `7e3dcdd` and is unaffected by PR #255.

## 1. Verdict summary — the PR #252 Q3 findings, re-verified at this base

Every load-bearing claim from the PR #252 investigation was
re-tested from scratch at base `7e3dcdd`. All confirmed; two
refinements and one adjacent observation were added (§5, §6).

| # | Claim | Verdict at 7e3dcdd |
|---|-------|--------------------|
| 1 | Core I atoms parse typed args under the shared grammar | CONFIRMED — all 51 Dells, `parse_seed` yields `args={'bogus':'zzprobe'}`; duplicates refuse at parse (`duplicate role 'name'`) |
| 2 | Args are then ignored for every Core I Dell except Dell 8 | CONFIRMED — single-atom differential census 51/51: 50 IGNORED, 1 VALIDATED (§2) |
| 3 | The ignore holds on all three surfaces | CONFIRMED — leaf (41 Dells), `core_i_ops` intercept (8), `live_identity` (2), plus the chain path for all 51 (§2, §3) |
| 4 | Dell 8 is the sole exception and validates fully | CONFIRMED — battery §2.2: UNKNOWN_ROLE / INVALID_VALUE / MISSING_REQUIRED / ARGUMENT_CONFLICT, precedence MISSING_REQUIRED > UNKNOWN_ROLE > INVALID_VALUE |
| 5 | Chained Core I atoms behave identically to single atoms (AF-1 parity) | CONFIRMED and GENERALIZED — parity sweep 51/51, zero breaks (§3) |
| 6 | The ignore holds at the real user surface | CONFIRMED — REPL transcripts (§4), incl. an in-session state witness for 37[Nurture] |

## 2. Census — single-atom path (PUBLIC_ENTRY_PATH)

Method: for each Dell 00–50, a bare call and a typed call
`(bogus="zzprobe")` on identical fresh baselines (throwaway
owner, seeded baseline asserted differentially, never absolutely).
Verdict compares ok, error, business-state witness (plane units,
store, groups, nursery pending, `last_*` receipts, history length)
and non-echo messages, with volatile fields (timestamps,
generation ids) scrubbed.

**Result: 50 of 51 Dells IGNORED — bare and typed executions are
identical in every compared dimension. Dell 8 VALIDATED.**

By surface (dispatch order in `executor.py`: intercept →
live_identity → chain → leaf):

- **Leaf (`executor_leaf.py`), 41 Dells** — 00–20, 23–26, 29–33,
  36, 38, 39, 41–43, 45, 46, 48–50: 40 ignored; Dell 8
  validated.
- **Intercept (`core_i_ops.apply_core_i`), 8 Dells** — HANDLED =
  {27, 28, 34, 35, 37, 40, 44, 47} re-verified from code
  (`core_i_ops.py:8`). `apply_core_i` reads `seed.label` only.
  All 8 ignored, including plausible roles (§5 exhibits).
- **live_identity, 2 Dells** — 21[Merge], 22[Split] ignored on
  error paths and on the positive path (21 merging two resolved
  sources: bare == typed, child created identically).

Code census (mechanism, not just behavior): across
`executor_leaf.py`, `core_i_ops.py`, `live_identity.py`, and
`executor.py` there is exactly ONE read of atom args —
`executor_leaf.py:60`, inside the block gated on `primary == 8`.
Registered signatures at this base: 17 Dells, of which exactly
one is Core I (Dell 8: `name` string required, `skin` enum
optional). No other Core I args consumer exists.

### 2.2 Dell 8 battery (single-atom, this base)

| Case | Result |
|------|--------|
| `name="Wish One", skin="SPHERE"` | ok; unit created with SPHERE skin |
| unknown role `bogus` | refuse `UNKNOWN_ROLE: bogus`, zero units created |
| `skin="TRIANGLE"` | refuse `INVALID_VALUE: skin=TRIANGLE not in [...]` — the only wrong-value refusal surface in Core I |
| `skin` only (name missing) | refuse `MISSING_REQUIRED: name` |
| missing + unknown together | `MISSING_REQUIRED` surfaces first |
| unknown + invalid together | `UNKNOWN_ROLE` surfaces first |
| typed name vs differing legacy label | refuse `ARGUMENT_CONFLICT` |
| typed name == label slug | ok (no false conflict) |
| duplicate role in one atom | refused at parse |

## 3. Chain path and the parity sweep

`chain_exec._run_atom` re-emits a Core I atom's args verbatim
into a rebuilt leaf seed (the AF-1 mechanism) and calls
`execute_seed(..., _leaf=True)`. Two precision points the ground
file did not state: (a) the `_leaf=True` re-entry still passes
the HANDLED intercept and the 21/22 branch — both sit before the
`_leaf` check in `executor.py` — so in chains the intercept
Dells are served by `apply_core_i`, not by the leaf; (b) the
certified Core II gate structurally cannot see Core I atoms —
its condition is `atom_args and 51 <= n <= 99`
(`chain_exec.py:75`).

Parity sweep: for all 51 Dells, the typed single-atom outcome
(ok, error class) vs the typed chained outcome
(`atom > 70[Count]`, receipt `atom_results[0]`): **51/51 parity,
zero breaks.** Dell 8's chain battery (valid / invalid /
unknown / missing) matches its single-atom battery
refusal-for-refusal, with zero mutation on refusals. Chain
witnesses: 34 in a chain stamps the default mark; 27 in a chain
checkpoints with the typed stamp ignored; 37 in a chain still
fails `add idea requires a label` despite `(label="typedidea")`.

**Consequence for the ground file's central trap:** the fear was
that a chain-only gate would create a new single-vs-chain
divergence. That fear is well-founded for a chain-only gate —
but §7 shows a shared funnel exists, so the trap is avoidable.

## 4. REPL exhibits (REAL_USER_PATH)

Literal subprocess transcripts (`python3 -m form.repl --owner
CoreIRepl`, piped stdin; full transcripts in the evidence
bundle):

- `05[Tone](bogus="x") :: joy` → `tone=joy`. The label drove;
  the arg was ignored; no refusal, no signal.
- `05[Tone](expression="calm") :: joy` → `tone=joy`. The
  plausible role — the very name the English Intent layer uses
  for this Dell — did not drive.
- `34[Stamp](mark="typedmark")` → `Stamp: stamp @ <ts>`. The
  default mark was used; `typedmark` appears only in the seed
  echo.
- `37[Nurture](label="typedidea")` → nothing added. In-session
  witness (40[TokenCount] in the same session): pending stays 0
  after the typed call, rises to 1 after `37[Nurture] ::
  realidea`.
- `08[Create](name="Repl Wish", skin="SPHERE")` → created;
  `skin="TRIANGLE"` → visible `INVALID_VALUE` refusal.
- **The asymmetry at the user's own surface:** in the same
  session, `82[Group](bogus="x")` → visible refusal: *"Dell
  82[Group] has no registered typed signature; typed arguments
  refused before execution (roles: bogus)"*. Core II refuses
  loudly; Core I (except Dell 8) executes silently. A user — or
  a docked AI — sees one grammar with two contradictory
  contracts.

## 5. Adjacent observation — a failure the REPL never prints

For `37[Nurture](label="typedidea")` the REPL printed NOTHING
after the echo lines: no success, no error. Mechanism, verified
in code: `apply_core_i`'s 37 add-arm returns
`{"ok": False, "error": "add idea requires a label"}` WITHOUT
appending the error to `messages`, and the REPL renders
messages. Neighboring intercept branches do append (27's
checkpoint failure, 28's rollback denial both append message
text). So on surface (b), at least one ordinary failure is
invisible at the real user surface while present in the result
dict. This is not an argument-contract defect per se; it is
recorded because it compounds §6 class (i): on this surface the
ignore is not merely silent about the arg — the accompanying
failure can be silent too. (Narrow claim: the 37 add-arm, this
base, transcript + code. Other intercept arms were not audited
for message discipline.)

## 6. Harm classification

**(iii) Parity breaks — NONE.** The AF-1 defect shape does not
exist for Core I typed args today: single, chain, intercept,
and REPL behaviors agree everywhere probed (51/51 parity). The
ignore is perfectly uniform. This is the strongest mitigating
fact, and it distinguishes Core I from the pre-AF-1 world.

**(ii) Meaningless-by-design — the majority.** For most Core I
Dells no role vocabulary exists at all: no signature, and
`CORE_I.md` documents label-driven behavior (it states NO
argument contract today — the ignore is undocumented, neither
promised nor disclaimed). A `(bogus="x")` on 12[Test] violates
no published per-Dell contract; its only offense is against the
grammar's implication that parentheses mean something.

**(i) Looks-effective-but-isn't — real, and concentrated where
the system itself teaches the role name.** Exhibits, all
returning ok (or the identical bare failure) with the label or
a default driving instead:

| Exhibit | Why the role is plausible | Observed |
|---------|---------------------------|----------|
| `05[Tone](expression="calm") :: joy` | Intent layer's own arg name for Tone | `tone=joy` |
| `04[Transform](direction="left")` | Intent layer's own arg name for Transform | "Transform ready." (no turn); `:: left` turns |
| `06[Cycle](cycles="3")` | the Intent layer's grow/expand actions carry a `cycles` arg | `Cycle x1`; `:: 3` gives `Cycle x3` — same shape, different count, no signal |
| `34[Stamp](mark="typedmark")` | Intent arg name `mark`; receipt field `last_stamp.mark` | mark = `stamp` (default) |
| `37[Nurture](label="typedidea")` | the arm's own error says "requires a label" | fails the label requirement; REPL prints nothing (§5) |
| `44[Bridge](capability="typedcap")` | receipt field `last_core_i.capability` | capability = `external`; the seed label drives it |
| `27[Checkpoint](stamp="typedstamp")` | `checkpoint()`'s own parameter is `stamp` | checkpoint written; the typed stamp leaves no trace in any persisted owner file |
| `28[Rollback](generation="gen-x")` | the operation's whole subject is a generation | identical denial to bare |
| `40[TokenCount](unit="tokens")` | receipt field `last_measure.unit` | unit stays `approx_units` |

Severity calibration, honestly: there is NO state corruption
and NO half-application — an ignored arg never partially
applies; execution is exactly the bare/label behavior,
deterministically. The harm class is the same one the Director
certified as a defect in Core II (silent drop under an ok
receipt), reduced in degree by two mitigations Core II lacked —
perfect parity, and no published per-Dell role contracts to
violate — and aggravated by one factor Core II did not have:
the system's own English/Intent layer teaches role names
(mark, direction, cycles) that the seed layer then silently
ignores, and the primary intended caller of typed args is the
docked AI, which writes them fluently for Core II and Dell 8
and cannot see the Core I ignore.

## 7. The AF-1 pin — precise statement

`form/af1_chain_args_test.py` (13/13 at this base; untouched by
this circuit). Items 1–6 pin Dell 8 and Core II chain/chainlink
behavior. **Check 7, "untyped args parity",** executes
`43[Fallback](note="hi")` single-atom and chained and asserts
`r1.ok == r2.ok AND r2.ok` — i.e. it pins TWO things:

1. **Parity** — single and chain outcomes are equal for an
   untyped Core I atom carrying args (the AF-1 contract proper);
2. **The current outcome value** — ok=True, i.e. silent-ignore
   success, for that Dell/role.

Consequences per option: a UNIFORM contract change to refusal
preserves (1) exactly but violates (2) — check 7 must be
AMENDED by Director ruling (rewritten to assert refusal
parity), never quietly edited. A chain-only or single-only
change violates (1) itself — the pin fails on its own terms,
and the change recreates the AF-1 defect shape in reverse. O2
preserves the pin verbatim. O3 preserves it only if
43[Fallback]'s `note` is not in the collision inventory — which
cannot be proven until that inventory exists.

## 8. Options analysis

**The funnel fact that prices all three options:** every Core I
execution — single-atom front door, HANDLED intercept, 21/22
live_identity, and chain re-entry — passes through
`executor.execute_seed` after `parse_seed`. No production
caller invokes `executor_leaf.execute_seed` directly (only
`executor.py:121` does; remaining references are comments and a
source-inspection helper). A gate placed in `executor.
execute_seed` therefore covers all three surfaces and both
entry shapes at ONE site. The ground file's first technical
question — find the shared pre-dispatch point or prove none
exists — is resolved: **it exists.**

### O1 — EXTEND THE GATE (uniform refusal)
Mechanism: in `executor.execute_seed`, after parse: if the
primary Dell is 00–50, is not Dell 8, and any atom carries
nonempty args → refuse `UNSUPPORTED_ARGS` with sorted role
NAMES only (the certified Core II diagnostic discipline),
before any dispatch; zero business-state mutation. Dell 8
falls through to its existing leaf validation untouched.
Surfaces: all three + REPL + Studio (all ride the funnel).
Pin: amendment required (§7) — refusal-parity rewrite of
check 7, authorized in the same ruling. English layer:
unaffected — a 19-phrase sweep plus source inspection shows
`translate()` emits typed args ONLY on registered Dells (Dell
8's `name` is the sole Core I emission; §9). flow_executor:
out (unchanged; it already refuses arg-shaped text at its
tokenizer — re-verified with a composable control pair).
Legacy risk: calls whose Core I typed args are decorative
today flip ok=True → refusal. Those args do nothing today, so
no working behavior is lost; the break is confined to the
receipt. Scope: one gate site (~15 lines mirroring the Core II
gate) + behavioral suite (this census, made permanent) + pin
amendment + CORE_I.md wording. The smallest change option,
because the funnel exists.

### O2 — DOCUMENTED LEGACY (ratify the ignore)
Mechanism: no behavior change. Make this review's census a
permanent parity/ignore suite; publish the contract in
`CORE_I.md` and the proof cards: Core I is label-driven; typed
arguments are not part of the Core I contract; only
08[Create] accepts typed roles. Pin: preserved verbatim.
Cost: lowest (docs + one suite). Consequence: class (i) harm
becomes PERMANENT and documented — the misleading-success
shapes of §6 remain live for exactly the caller (the docked
AI) least able to detect them, and the REPL asymmetry (82
refuses, 05 silently complies) becomes a stated, user-visible
permanent contract rather than an accident.

### O3 — HYBRID (refuse only on name collision)
Mechanism: the O1 funnel gate + a per-Dell inventory of
"documented legacy role names"; refuse only when an arg name
collides. The inventory does not exist: building it means
per-Dell rulings over label grammars, receipt field names, and
Intent arg names (this review's exhibits suggest ~9 Dells have
plausible vocabularies). Pin: probably preserved (43's `note`
is not a documented role) but unprovable pre-inventory.
Consequence: a two-tier contract — on the same Dell, some role
names refuse while others silently ignore — which is harder to
state, teach, and keep drift-free than either pure contract;
every future Dell or role rename reopens the inventory. Cost:
highest (inventory + per-Dell rulings + gate + suite), for the
least coherent contract.

## 9. Scoping evidence (for Q-C3)

- **REPL:** in scope and probed (§4) — REAL_USER_PATH.
- **English layer:** probed. `translate()` emits seed typed
  args only on registered Dells — in the 19-phrase sweep,
  emissions landed on 8, 56, 84, 85, 86, 87 (all registered,
  zero unregistered emissions), and source inspection concurs:
  the only paren-emitting templates in `translate.py` target
  8, 51, 56, 58, 84–88, every one registered. Separately,
  `Intent.args` is a parallel argument
  channel (`mark`, `direction`, `cycles`, …) that never becomes
  `atom.args` — its role names are precisely the plausible
  names of §6 class (i). Whether that channel needs its own
  contract review is Q-C3.
- **flow_executor:** re-verified at this base — the composable
  control `10[Keep] > 12[Test]` parses; the arg-shaped variant
  is refused at tokenize time (`expected flow at 8`). It never
  silently consumes typed args. Recommended: OUT of any Core I
  repair, as in Q-D4.

## 10. Recommendation (Uni's, for the Director to rule on)

**O1 — extend the gate at the executor funnel.** The defect
class is the one already ruled unacceptable in Core II —
silent drop under an ok receipt — and Core I's mitigations
(parity, undocumented roles) reduce its degree, not its kind,
while its aggravator (the Intent layer teaching the very role
names being ignored, to the docked-AI caller Ace intends as
primary) is structural. The funnel makes O1 the cheapest
honest contract: one site, all surfaces, parity preserved by
construction, English paths untouched. O2 is the defensible
fallback if the Director weighs receipt-compatibility over
honesty; O3 is not recommended — it buys the worst contract
shape at the highest price. The check-7 pin amendment
(refusal-parity form) should be authorized inside the O1
ruling itself, so the pin is amended by ruling, never by an
implementation quietly fitting itself.

## 11. Anticipated probes

- *"Is the census differential confounded by the seeded
  baseline?"* Baselines are identical-by-construction (fresh
  throwaway owner per arm, cleanup before construction); the
  welcome unit appears in both arms and cancels. Volatile
  fields were scrubbed; the one raw difference found (Dell 27's
  random generation id inside a message) is documented in
  probe A's log and resolved by addendum A2 with the normalized
  comparison plus a persisted-file search (no trace of the
  typed stamp anywhere).
- *"Did any probe touch real state?"* The campaign ran in a
  disposable worktree whose `form/state` began empty; before/
  after snapshots of non-probe owners are both empty and
  identical, and probe owners left zero files after cleanup
  (baseline_before.json / baseline_after.json in the bundle).
- *"Is the funnel claim complete?"* Caller census by grep over
  `form/` + `gui/`: `executor_leaf.execute_seed` has exactly
  one production caller (`executor.py`). `core_ii_smoke.py`
  inspects its source but never executes it.
- *"Does the REPL evidence overclaim?"* Transcripts are
  literal subprocess output, saved verbatim. One method error
  is on the record: an early readback check loaded a fresh
  Program instead of the REPL session's unsaved state and was
  discarded; the 37 verdict rests on the in-session TokenCount
  witness (probe C3), not on that readback.
- *"What about chainlink (2v2) Core I atoms?"* AF-1 items 3–4
  pin chainlink arg carriage for Dell 8; chainlink expansion
  builds member atoms from the same parsed args, and members
  re-enter through the same funnel — the O1 gate site covers
  them identically. Not separately re-probed in this review;
  stated as a mechanism derivation, not an executed census.

## 12. Questions for the Director

**Q-C1.** Is this review's decision the CONTRACT (O1 / O2 /
O3), with implementation as a follow-on authorized circuit —
Uni's recommendation, mirroring the honesty-investigation →
gate sequence that worked for Core II? (If O1 is chosen, the
same ruling should authorize the AF-1 check-7 amendment to
refusal-parity form, per §7.)

**Q-C2.** Does the seed-echo boundary from the gate
certificate carry over unchanged to any Core I refusal —
sorted role NAMES only in new diagnostics, the preexisting
universal seed echo explicitly not a secrecy guarantee,
broader redaction reserved to a separate security review?

**Q-C3.** The English layer's `Intent.args` channel (role
names such as `mark`, `direction`, `cycles` that never become
`atom.args`) taught the vocabulary that §6 shows being
silently ignored at the seed layer. Should that channel get
its own contract review as a follow-on, or is it explicitly
out of scope for the argument-honesty program?

## 13. Evidence

Bundle: `director-reports/evidence/core-i-contract-review/`
with `MANIFEST.sha256` — 27 files, manifest digest
`5ee06567c9ff53f0ea2d28f2bd2c8b4e7ba8861c73994dbac25256754d50f8ce`
(verify: `sha256sum -c MANIFEST.sha256`).
Contents: probe sources (`probe_lib.py`, `probe_a_census.py`,
`probe_a2_addendum.py`, `probe_b_chain.py`, `probe_c_repl.py`,
`probe_c2_repl.py`, `probe_c3_repl.py`, `probe_d_misc.py`,
`probe_d2_misc.py`), their logs, the two REPL transcripts,
census JSONs (`census_single.json`, `census_chain.json`,
`dell8_battery.json`, `intercept_deep.json`,
`plausible_roles.json`), baseline snapshots, and `SWAT.md`
(the Director's-eye pre-mortem written before probing).
Supersession notes: probe C was superseded by C2/C3 (two
assertion-string errors and one invalid readback method —
corrected on the record, §11); probe D was superseded by D2
(its flow control used a non-composable Dell; D2 re-ran with a
composable pair). Nothing was removed.

**Boundaries:** no production code, test, or pin changed; no
signatures registered; PR #255 untouched and uninvolved;
DAF-09 untouched; this review certifies nothing and does not
speak for whole-program behavior.
