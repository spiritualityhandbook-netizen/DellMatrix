# SYSTEM-002 / Q-S2.3 — CALLER PRE-CUT REPAIRS (exchange + supersession)

*Build packet, 2026-11-15, Uni (subagent build lane). Base: main `17ae4ce86743d9c5ff848a1b48111119d9bf9a32`. Branch: `uni/sysc29-precuts` (local commit only at lane close; push/PR/campaign/mutants are main-session steps). Authority: the Q-S2.3 investigation (SYSTEM_002_QS22_QS23_INVESTIGATION_2026-11-15.md) classified both sites DEFECT with these fix shapes; the Director's checkpoint mail 1a1df5bdadd2125e authorized the bounded caller-side investigation, and this lane implements the two proven fixes. Scope held: the two `words` pre-cuts only. No MWL credit claimed by this packet.*

## 1. The two defects (proven by the investigation)

1. **exchange.py:768** — `import_packet` landed a foreign packet with `words=seed["keep"][:240]`. keep is contractually admitted to **2,000 chars** (exchange.py:175, bound deliberately raised, rationale at :167-171), and the landed proposal's words become the confirmed unit's body (`confirm_lineage.py:423`). The `[:240]` was present verbatim in the file's creation commit — a mirror of the Nursery store's then-current cut, redundant even then.
2. **supersession.py:651** — `supersede_proposal` created the successor with `words=words[:240]`. The successor text is unbounded free user text (REPL path `core_i_ops.py:467-486`; only non-emptiness is validated, supersession.py:641-643), and the operation's acceptance-policy binding hash is computed over the FULL words (supersession.py:581) — so for any text over 240 chars, **approved content and stored content silently diverged**, with no second copy of the tail anywhere.

**Where supersession stores:** the Nursery. `_supersede_impl` binds `nursery = program.nursery` (supersession.py:557); the successor is created through `nursery.add(...)` (:649), then confirmed/promoted through the legitimate confirm path; the promoted unit's body is minted from `prop.words` (confirm_lineage.py:423). There is no separate supersession store.

## 2. Failing-first (rerunnable probe, captured at the Nursery.add boundary)

Probe method: wrap the receiver program's `nursery.add` to record the `words` argument the caller passes, then delegate to the real `add`. Isolated uuid owners; state cleaned after. Run on the UNMODIFIED base:

```
EXCHANGE import ok=True pid=precut_probe_3576
EXCHANGE caller add() words len = 240
EXCHANGE landed proposal words len = 240
EXCHANGE landed == keep exactly: False
SUPERSESSION receipt ok=True succ=revision_of_predlong_1482
SUPERSESSION caller add() words len = 240
SUPERSESSION stored successor words len = 240
SUPERSESSION stored == approved exactly: False
SUPERSESSION acceptance hash binds FULL text (hash(full) != hash(240-cut)): True
```

Inputs: exchange keep = exactly 1,500 chars (admitted; bound 2,000); supersession successor = exactly 1,000 chars (unbounded path). Both callers handed the store a 240-char prefix of text they had admitted/approved in full.

The new suite reproduces the same failing-first at suite level: on pre-fix code it reports **7/9, smoke False** — exactly the two caller pins fail (X1 captured len=240; S2 captured len=240); every other check passes pre- and post-fix.

## 3. The fixes (two one-line changes; nothing else in product code)

```diff
 form/dell_matrix/exchange.py
-            seed["label"], words=seed["keep"][:240], origin=origin,
+            seed["label"], words=seed["keep"], origin=origin,

 form/mandell/supersession.py
-        words=words[:240],
+        words=words,
```

**Not touched, by design:** the sibling slices at the supersession site — label `[:80]` (supersession.py:648, Q-S2.1 label circuit's field) and reason `[:160]` (:654, Q-S2.2's field) — and `nursery.py` itself (the store cut is SYS-C29's repair, PR #429). The suite pins the label sibling behaviorally (S5: a 100-char explicit label still lands at 80) so the scope boundary is itself under test.

## 4. Test design — and the store-dependency honesty note

New suite `form/precuts_caller_words_test.py` (9 checks, `smoke()`, registered in `form/regress.py` LIST exactly once; LIST 286 → 287 on this base):

- **X1 / S2 — the caller pins.** The `words` argument captured at the `Nursery.add()` boundary equals the admitted keep (1,500) / the approved successor text (1,000) EXACTLY. These fail pre-fix, pass post-fix, and are independent of the store version.
- **X2 / S3 — no cut beyond the store (relational).** The landed/stored words equal the store's own admission of the same text, probed empirically by a direct `nursery.add` of the identical text in the same program. This asserts the caller introduces NO loss of its own, whatever the store's bound is.
- **X3 / S4 — true end-to-end equality where the store admits on any version** (200-char texts): landed/stored words == input exactly.
- **S1 — the authorization fact:** `canonical_hash` over the full successor text differs from the hash over its 240-cut (the divergence the fix removes at the caller).
- **S5 — scope guard** (above). S0 is the setup check (predecessor confirmed through the production confirm path).

**Honesty note (read before quoting any end-to-end number):** on this base (main), the Nursery store itself still cuts words at 240 (`nursery.py:212`). The post-fix probe therefore reads:

```
EXCHANGE caller add() words len = 1500   | landed proposal words len = 240 (store cut)
SUPERSESSION caller add() words len = 1000 | stored successor words len = 240 (store cut)
```

That residual 240 is the STORE's cut — SYS-C29's repair (PR #429: admit words in full to 5,000, explicit refusal beyond), not these callers'. keep ≤ 2,000 sits inside SYS-C29's bound, and the supersession path inherits the same bound, so once SYS-C29 merges, X2/S3 become full end-to-end equality with no change to this suite. **No end-to-end preservation claim is made for >240 texts until both repairs are on main.** This branch does not touch `nursery.py`, so it is independent of PR #429's branch and union-refreshable in either merge order.

## 5. Test results (this lane, at the committed head)

- New suite `form.precuts_caller_words_test`: **9/9 PASS, smoke True** (post-fix); **7/9, smoke False** on pre-fix code (X1/S2 fail — the defect pins).
- Neighbors, each in its own process via `smoke()`, sequential:
  - `form.mandell.p9_exchange_test` — 11/11 PASS
  - `form.step5_exchange_boundary_test` — 20/20 PASS
  - `form.step5b_exchange_durability_test` — 21/21 PASS
  - `form.af34_exchange_counters_test` — 19/19 PASS
  - `form.mandell.supersession_failure_test` — 75/75 PASS
  - `form.supersession_lineage_restart_test` — 11/11 PASS
  - `form.nursery_confirm_race_test` — 57/57 PASS
- Changed paths: `form/dell_matrix/exchange.py` (1 line), `form/mandell/supersession.py` (1 line), `form/precuts_caller_words_test.py` (new), `form/regress.py` (+1 LIST line), this packet. Evidence class: INTEGRATION (production public paths driven in-process; the boundary capture is an observation wrapper, removed after each call).

## 6. Anticipated probes

- *"Did you just move the cut downstream?"* No — the callers now pass text whole; the only remaining cut for words is the store's, owned and being repaired by SYS-C29 (PR #429). §4 states this in the open, with the post-fix probe output.
- *"Why capture at the boundary instead of asserting stored text?"* Because on the unrepaired store a stored-text assertion >240 cannot pass, and writing it as an expectation would fake an end-to-end claim. The boundary pin is the caller's contract; the relational checks (X2/S3) bind stored output to the store's own admission so nothing hides between caller and store.
- *"Could passing keep whole break the exchange journal/detail rendering?"* Detail rendering is independent (`detail_text` built from keep in full already, exchange.py:717); the journal stores seed keep verbatim either way. All four exchange suites pass unmodified, including durability (step5b) and counters (af34).
- *"Supersession with a >5,000 successor after SYS-C29?"* The store will refuse explicitly before mutation (SYS-C29 contract) and supersession's enclosing rollback keeps the predecessor active — a loud refusal replacing today's silent divergence. That composition is SYS-C29's + this circuit's joint behavior once both are on main; it is not re-proven here.

## 7. Questions for the Director

- Q-P1: Merge order vs PR #429 — this branch is independent (no `nursery.py` overlap). Land in either order? Uni's recommendation: #429 first, so the end-to-end statement becomes true the moment this lands.
- Q-P2: Confirm the sibling slices at supersession.py:648/:654 stay with their own circuits (label = Q-S2.1, reason = Q-S2.2) and are not swept into this circuit's certification.
- Q-P3: Any MWL/register placement for the Q-S2.3 fixes is the authorities' call; none is claimed here.
