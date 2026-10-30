"""D1 circuit 22 (registry pass, spectrum) — Dells
89-99 DEEP CONTRACTS.

The last cluster of the full-registry pass — the
transaction / verification / abstraction arm, all in
spectrum_ops: 89 Diff, 90 Trace, 91 Assert, 92 Guard,
93 Try, 94 Catch, 95 Commit, 96 Revert, 97 Define,
98 Alias, 99 Compose. (Dells 80-88 live in the same
module and were proven in circuits 20/21 and 4-8.)
With this circuit every one of the 100 Dells has a
proven standalone contract. Contracts proven here,
per Dell, through the public seed path:

- 89 Diff: reports the store change-set against a
  baseline chosen by state: an active transaction's
  checkpoint ("transaction"), else the pre-mutation
  checkpoint captured by the last spectrum mutation
  84-88 ("immediate"), else the current state itself
  ("current"). PINNED EXHIBIT: the "current" baseline
  compares the store to itself, so it is vacuous
  (changed=[] by construction), and Dell 55 Set —
  the store's everyday writer — captures no baseline
  at all, so a Set write is invisible to Diff until
  some other baseline exists; against an older
  "immediate" baseline the same Set write DOES show.
- 90 Trace: prints the last <=8 entries of the
  execution trace buffer ("NN[Term]::label" per
  executed Core II atom; Trace's own entry lands
  after its dump) and publishes a cell whose value
  is the WHOLE trace list; empty trace prints
  "(empty)" with count 0.
- 91 Assert: evaluates a condition via the shared
  control runtime (bare = "true"; true-words pass,
  false-words fail, otherwise the predicate engine);
  records last_assert PASS/FAIL; a failure fails the
  atom (assert_fail) and marks an open transaction
  frame "failed".
- 92 Guard: the same evaluation as a gate — ALLOW
  passes, BLOCK fails the atom (guard_block) and
  marks an open frame "failed"; "block"/"deny"
  labels force BLOCK.
- 93 Try: opens a transaction frame with a full
  state checkpoint; ids are monotonic (tx0, tx1,
  ...) over the frame history; depth = the number of
  already-active frames; try_depth tracks the active
  count. PINNED EXHIBIT: only Assert/Guard failures
  mark a frame "failed" — an ordinary atom failure
  (Delete of a missing key) leaves the frame "open";
  the failure is visible only via st.last_error.
- 94 Catch: illegal with no active frame
  (catch_illegal). Otherwise marks the innermost
  active frame "caught" and records the captured
  error. PINNED EXHIBIT: the captured error is
  st.last_error, which is STICKY — it is never
  cleared by success, so Catch can capture an error
  raised before/outside the transaction (even the
  commit_illegal raised by a failed Commit attempt
  on the same frame moments earlier).
- 95 Commit: with no frame ever/at all it fails
  commit_without_try; on a terminal (committed/
  reverted) frame it fails commit_illegal; on a
  "failed" frame it fails commit_illegal ("from
  failed") — the frame must be Caught first. On an
  open/caught frame it marks the frame "committed",
  records accepted = a deepcopy of the CURRENT store
  wholesale, and appends to st.staged. PINNED
  EXHIBIT: there is no staging isolation — mutations
  inside a Try are live immediately, and the
  staged_changes ledger records ONLY spectrum
  mutations (84-88); Dell 55 Set writes inside a
  transaction are never staged. Commit is a
  mark/accept mechanism, not atomic staging.
- 96 Revert: on an active frame it restores the
  frame checkpoint EXACTLY (values rolled back, new
  keys removed, selection/groups/defs restored) and
  marks the frame "reverted". On a committed frame
  it refuses (unrelated_revert); on a reverted frame
  it fails revert_illegal. With no frames it pops
  the snapshot stack (snapshots are captured
  pre-write by Set/Delete/Replace/Patch via shot)
  and restores it; with nothing at all it is an
  ok=True "Revert nothing".
- 97 Define: "name=meaning" stores st.defs[name];
  a label without "=" defines the name as itself;
  bare Define creates defs["def"] = "". Publishes
  NO result cell.
- 98 Alias: "name=target" binds only if the target
  resolves (through alias chains) to a def or a
  composition; a missing/unresolvable target fails
  alias_missing with no mutation; a binding that
  would close a cycle fails alias_cycle with no
  mutation; bare Alias fails alias_missing.
  Publishes NO result cell.
- 99 Compose: "name=body" STORES the composition
  AND EXECUTES IT IMMEDIATELY (define-mode runs);
  ":: name" executes a stored composition (defs and
  aliases resolve as bodies too). Body parts split
  on ">" or ",": a digit part runs that Dell (as
  "NN[ComposeStep]", so the term doubles as its
  label), a named part resolves recursively through
  defs/compositions/aliases, and a body containing
  "[" is executed verbatim as seed text. Errors:
  unknown/empty body malformed_composition,
  self-reference compose_cycle, nesting deeper than
  the bound (st.limit, default 8) compose_depth, and
  a failing body propagates its own error.
  PINNED EXHIBIT: a composition whose define-mode
  run FAILS is still stored, and re-running it
  fails the same way.

Cluster symbiosis: Diff reads Copy's baseline and
Try's checkpoint; Assert's failure is what fails
Try's frame; Catch captures Delete's error; Commit
accepts Set's writes; Revert undoes Set's writes
and Copy's staging; Define and Alias feed Compose's
resolution; Compose runs Set/Count/Select for real.
One literal-REPL leg for REAL_USER_PATH evidence.

House pattern: RESULTS + _rec; loud cleanup
(owner-wide glob; the test owners are unique to
this suite)."""
import os
import subprocess
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from form.mandell.dell_cards import DEEP_NOTES          # noqa: E402

RESULTS = []


def _rec(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))


def _cleanup(owner):
    import glob
    import shutil
    state = os.path.join(_ROOT, "form", "state")
    for f in glob.glob(os.path.join(state, f"*{owner}*")):
        try:
            if os.path.isdir(f):
                shutil.rmtree(f)
            else:
                os.remove(f)
        except FileNotFoundError:
            pass
        except OSError as e:
            raise RuntimeError(f"cleanup failed for {f}: {e}")


def _program(owner):
    from form.open import Program
    _cleanup(owner)
    prog = Program(owner=owner)
    from form.mandell.core_ii_exec import attach
    attach(prog)
    return prog


def _run(prog, seed):
    from form.mandell.executor import execute_seed
    return execute_seed(prog, seed)


def _msgs(r):
    return [m for m in r.get("messages", [])
            if not m.startswith(("Mandell:", "English:",
                                 "Chain atoms=", "-- "))]


def _st(p):
    return p.core_ii


def main():
    owner = "D1RegSpectrum"
    p = _program(owner)
    st = _st(p)

    # -- 89 Diff: vacuous default, Set blindness, Copy baseline
    r = _run(p, "89[Diff]")
    _rec("89 Diff EXHIBIT: with no baseline captured, "
         "Diff compares the store to itself — "
         "baseline=current and changed=[] by "
         "construction (a vacuous diff)",
         r.get("ok") is True
         and _msgs(r) == ["Diff changed=[] baseline=current"]
         and st.last_diff.get("baseline") == "current"
         and st.last_diff.get("changed") == [],
         str(_msgs(r)))
    _run(p, "55[Set] :: a=1")
    r = _run(p, "89[Diff]")
    _rec("89 Diff EXHIBIT: a Set (55) write captures "
         "no baseline — the store changed but Diff "
         "still reports baseline=current, changed=[]",
         _msgs(r) == ["Diff changed=[] baseline=current"]
         and st.store.get("a") == "1", str(_msgs(r)))
    _run(p, "84[Copy] :: a")
    r = _run(p, "89[Diff]")
    _rec("89 Diff: a spectrum mutation (Copy, 84) "
         "captures the pre-mutation checkpoint — Diff "
         "then reports baseline=immediate with the "
         "new key in the change-set",
         _msgs(r) == ["Diff changed=['copy_a'] "
                      "baseline=immediate"]
         and st.last_diff.get("before", {}).get("copy_a")
         is None
         and st.last_diff.get("after", {}).get("copy_a")
         == "1", str(_msgs(r)))

    # -- 90 Trace: dump excludes itself, cell holds all
    r = _run(p, "90[Trace]")
    want = ["89[Diff]::", "55[Set]::a=1", "89[Diff]::",
            "84[Copy]::a", "89[Diff]::"]
    _rec("90 Trace: prints the last <=8 trace entries "
         "(its own entry lands only after the dump) "
         "and publishes a cell holding the WHOLE "
         "trace list with count and matched=True",
         _msgs(r) == ["Trace last 5:"]
         + [f"  · {t}" for t in want]
         and st.last_result.get("source") == "trace"
         and st.last_result.get("value") == want
         and st.last_result.get("count") == 5
         and st.last_result.get("matched") is True
         and st.traces[-1] == "90[Trace]::",
         str(_msgs(r)))

    # -- 91 Assert / 92 Guard
    r = _run(p, "91[Assert]")
    _rec("91 Assert: bare Assert is the condition "
         "'true' and passes; last_assert records PASS",
         r.get("ok") is True
         and _msgs(r) == ["Assert PASS true"]
         and st.last_assert == "PASS", str(_msgs(r)))
    r = _run(p, "91[Assert] :: false")
    _rec("91 Assert: a false condition fails the "
         "atom (assert_fail) and records last_assert "
         "FAIL",
         r.get("ok") is False
         and r.get("error") == "assert_fail"
         and _msgs(r) == ["Assert FAIL false"]
         and st.last_assert == "FAIL", str(_msgs(r)))
    r = _run(p, "91[Assert] :: gte:count 0")
    _rec("91 Assert: non-word conditions go through "
         "the shared predicate engine (gte:count 0 "
         "passes)",
         r.get("ok") is True
         and _msgs(r) == ["Assert PASS gte:count 0"],
         str(_msgs(r)))
    r = _run(p, "92[Guard]")
    _rec("92 Guard: bare Guard allows and records "
         "last_guard ALLOW",
         r.get("ok") is True
         and _msgs(r) == ["Guard ALLOW default"]
         and st.last_guard == "ALLOW", str(_msgs(r)))
    r = _run(p, "92[Guard] :: block")
    r2 = _run(p, "92[Guard] :: gte:count 99")
    _rec("92 Guard: 'block' forces BLOCK, and a "
         "predicate miss also BLOCKs — both fail the "
         "atom guard_block and record last_guard BLOCK",
         r.get("ok") is False
         and r.get("error") == "guard_block"
         and _msgs(r) == ["Guard BLOCK block"]
         and r2.get("ok") is False
         and r2.get("error") == "guard_block"
         and st.last_guard == "BLOCK",
         str((_msgs(r), _msgs(r2))))

    # -- 95/94 with no transaction
    r = _run(p, "95[Commit]")
    _rec("95 Commit: with no transaction at all, "
         "Commit fails honestly (commit_without_try)",
         r.get("ok") is False
         and r.get("error") == "commit_without_try"
         and _msgs(r) == ["Commit illegal"],
         str(_msgs(r)))
    r = _run(p, "94[Catch]")
    _rec("94 Catch: with no active frame, Catch is "
         "illegal (catch_illegal)",
         r.get("ok") is False
         and r.get("error") == "catch_illegal"
         and _msgs(r) == ["Catch illegal"],
         str(_msgs(r)))

    # -- 93/95 happy path + exhibits
    r = _run(p, "93[Try]")
    _rec("93 Try: opens frame tx0 at depth 0 with a "
         "state checkpoint; try_depth tracks the "
         "active count",
         _msgs(r) == ["Try id=tx0 depth=0"]
         and st.try_depth == 1
         and st.tx[-1].get("status") == "open"
         and st.tx[-1].get("checkpoint", {})
         .get("store", {}).get("a") == "1",
         str(_msgs(r)))
    _run(p, "55[Set] :: txkey=tv")
    _rec("95 Commit EXHIBIT: a Set (55) write inside "
         "the transaction is LIVE immediately but is "
         "never added to staged_changes — the staging "
         "ledger records only spectrum mutations",
         st.store.get("txkey") == "tv"
         and st.tx[-1].get("staged_changes") == [],
         str(st.tx[-1].get("staged_changes")))
    r = _run(p, "89[Diff]")
    _rec("89 Diff: inside a transaction the baseline "
         "is the frame checkpoint — the Set write "
         "Diff was blind to outside now shows as "
         "changed=['txkey'] baseline=transaction",
         _msgs(r) == ["Diff changed=['txkey'] "
                      "baseline=transaction"],
         str(_msgs(r)))
    r = _run(p, "95[Commit]")
    _rec("95 Commit: an open frame commits — status "
         "committed, accepted is the whole CURRENT "
         "store (wholesale, incl. the unstaged Set "
         "write), and the commit lands in st.staged",
         _msgs(r) == ["Commit tx0 accepted"]
         and st.tx[-1].get("status") == "committed"
         and st.tx[-1].get("accepted", {})
         .get("txkey") == "tv"
         and st.staged[-1] == {"op": "commit",
                               "id": "tx0",
                               "accepted": True}
         and st.try_depth == 0, str(_msgs(r)))
    r = _run(p, "95[Commit]")
    r2 = _run(p, "96[Revert]")
    _rec("95/96: committing a terminal frame fails "
         "commit_illegal, and Revert refuses a "
         "committed transaction (unrelated_revert) — "
         "a commit cannot be undone by Revert",
         r.get("ok") is False
         and r.get("error") == "commit_illegal"
         and r2.get("ok") is False
         and r2.get("error") == "unrelated_revert"
         and _msgs(r2) == ["Revert refused committed "
                           "transaction"],
         str((_msgs(r), _msgs(r2))))

    # -- ordinary failure does NOT fail the frame; Catch via last_error
    _run(p, "93[Try]")
    r = _run(p, "86[Delete] :: nosuchkey")
    _rec("93 Try EXHIBIT: an ordinary atom failure "
         "(Delete of a missing key) does NOT mark the "
         "frame failed — it stays 'open'; only "
         "st.last_error shows the failure (contrast "
         "Assert/Guard, which fail the frame)",
         r.get("ok") is False
         and st.tx[-1].get("status") == "open"
         and st.tx[-1].get("error") == ""
         and st.last_error == "delete_missing:nosuchkey",
         str(st.tx[-1]))
    r = _run(p, "94[Catch]")
    _rec("94 Catch: Catch marks the frame 'caught' "
         "and captures st.last_error as the frame "
         "error — symbiosis: Catch reads Delete's "
         "failure",
         _msgs(r) == ["Catch delete_missing:nosuchkey"]
         and st.tx[-1].get("status") == "caught"
         and st.tx[-1].get("error")
         == "delete_missing:nosuchkey", str(_msgs(r)))
    r = _run(p, "95[Commit]")
    _rec("95 Commit: a caught frame may commit "
         "(commit is legal from open and caught)",
         _msgs(r) == ["Commit tx1 accepted"]
         and st.tx[-1].get("status") == "committed",
         str(_msgs(r)))

    # -- Assert fails the frame; commit refused; sticky catch; revert
    _run(p, "93[Try]")
    _run(p, "91[Assert] :: false")
    _rec("91/93 symbiosis: an Assert failure inside "
         "a transaction marks the frame 'failed' "
         "(the _fail_open_tx path Delete never takes)",
         st.tx[-1].get("status") == "failed"
         and st.tx[-1].get("error") == "assert_fail",
         str(st.tx[-1]))
    r = _run(p, "95[Commit]")
    _rec("95 Commit: a FAILED frame cannot commit — "
         "commit_illegal 'from failed'; it must be "
         "caught (or reverted) first",
         r.get("ok") is False
         and r.get("error") == "commit_illegal"
         and _msgs(r) == ["Commit illegal from failed"]
         and st.tx[-1].get("status") == "failed",
         str(_msgs(r)))
    r = _run(p, "94[Catch]")
    _rec("94 Catch EXHIBIT: Catch captures the "
         "STICKY last_error — which the failed Commit "
         "attempt just overwrote, so Catch on this "
         "frame captures 'commit_illegal', not the "
         "original assert_fail",
         _msgs(r) == ["Catch commit_illegal"]
         and st.tx[-1].get("status") == "caught"
         and st.tx[-1].get("error") == "commit_illegal",
         str(_msgs(r)))
    r = _run(p, "96[Revert]")
    r2 = _run(p, "96[Revert]")
    _rec("96 Revert: Revert on the (caught) active "
         "frame restores its checkpoint and marks it "
         "reverted; a second Revert on the reverted "
         "frame fails revert_illegal",
         _msgs(r) == ["Revert tx2 exact"]
         and st.tx[-1].get("status") == "reverted"
         and r2.get("ok") is False
         and r2.get("error") == "revert_illegal",
         str((_msgs(r), _msgs(r2))))

    # -- 96 Revert restores Set writes exactly
    _run(p, "55[Set] :: keepme=1")
    _run(p, "93[Try]")
    _run(p, "55[Set] :: keepme=2")
    _run(p, "55[Set] :: newkey=x")
    r = _run(p, "96[Revert]")
    _rec("96 Revert symbiosis: Revert undoes Set's "
         "writes EXACTLY — keepme rolls back to '1' "
         "and the key created inside the transaction "
         "is gone",
         _msgs(r) == ["Revert tx3 exact"]
         and st.store.get("keepme") == "1"
         and "newkey" not in st.store, str(_msgs(r)))
    _cleanup(owner)

    # -- owner B: empty trace, snapshot revert, stale catch, Define/Alias
    owner_b = "D1RegSpectrumB"
    bp = _program(owner_b)
    bst = _st(bp)
    r = _run(bp, "90[Trace]")
    _rec("90 Trace: on a fresh state the trace is "
         "empty — 'Trace last 0:' + '(empty)', cell "
         "value [] count 0 matched=True",
         _msgs(r) == ["Trace last 0:", "  (empty)"]
         and bst.last_result.get("value") == []
         and bst.last_result.get("count") == 0
         and bst.last_result.get("matched") is True,
         str(_msgs(r)))
    r = _run(bp, "96[Revert]")
    _rec("96 Revert: with no frames and no snapshots "
         "Revert is an honest ok=True no-op "
         "('Revert nothing')",
         r.get("ok") is True
         and _msgs(r) == ["Revert nothing"],
         str(_msgs(r)))
    _run(bp, "55[Set] :: s1=v1")
    _run(bp, "88[Patch] :: s1=v2")
    r = _run(bp, "96[Revert]")
    _rec("96 Revert: with no transaction, Revert "
         "pops the snapshot stack — Set/Patch capture "
         "pre-write snapshots via shot, so Revert "
         "undoes the Patch and s1 is 'v1' again",
         _msgs(r) == ["Revert snapshot snapshots=1"]
         and bst.store.get("s1") == "v1"
         and len(bst.snapshots) == 1, str(_msgs(r)))
    _run(bp, "86[Delete] :: ghost")
    _run(bp, "93[Try]")
    r = _run(bp, "94[Catch]")
    _rec("94 Catch EXHIBIT: Catch inside a brand-new "
         "transaction captures a STALE error — the "
         "Delete failure raised before the Try even "
         "opened (last_error is never cleared by "
         "success or by Try)",
         _msgs(r) == ["Catch delete_missing:ghost"]
         and bst.tx[-1].get("error")
         == "delete_missing:ghost", str(_msgs(r)))
    _run(bp, "96[Revert]")
    cell_before = dict(bst.last_result)
    r = _run(bp, "97[Define] :: greet=hello world")
    _rec("97 Define: 'name=meaning' stores the def "
         "and publishes NO result cell (the previous "
         "Dell's cell survives untouched)",
         _msgs(r) == ["Define greet"]
         and bst.defs.get("greet") == "hello world"
         and bst.last_result == cell_before,
         str(_msgs(r)))
    _run(bp, "97[Define] :: lonely")
    _run(bp, "97[Define]")
    _rec("97 Define: a label without '=' defines the "
         "name as itself; a bare Define creates "
         "defs['def'] = ''",
         bst.defs.get("lonely") == "lonely"
         and bst.defs.get("def") == "", str(bst.defs))
    r = _run(bp, "98[Alias] :: g=greet")
    _run(bp, "98[Alias] :: g2=g")
    _rec("98 Alias: an alias binds to a def, and an "
         "alias may chain through another alias "
         "(g2 -> g -> greet)",
         _msgs(r) == ["Alias g->greet"]
         and bst.aliases == {"g": "greet", "g2": "g"},
         str(bst.aliases))
    r = _run(bp, "98[Alias] :: bad=nosuchthing")
    r2 = _run(bp, "98[Alias]")
    _rec("98 Alias: an unresolvable target and a "
         "bare Alias both fail alias_missing with no "
         "mutation",
         r.get("ok") is False
         and r.get("error") == "alias_missing"
         and r2.get("ok") is False
         and r2.get("error") == "alias_missing"
         and bst.aliases == {"g": "greet", "g2": "g"},
         str((_msgs(r), _msgs(r2))))
    r = _run(bp, "98[Alias] :: g=g2")
    _rec("98 Alias: rebinding g to g2 would close a "
         "cycle (g -> g2 -> g) — refused alias_cycle, "
         "existing bindings untouched",
         r.get("ok") is False
         and r.get("error") == "alias_cycle"
         and _msgs(r) == ["Alias cycle g"]
         and bst.aliases == {"g": "greet", "g2": "g"},
         str(_msgs(r)))
    _cleanup(owner_b)

    # -- owner C: Compose + nested Try + in-tx staging
    owner_c = "D1RegSpectrumC"
    cp = _program(owner_c)
    cst = _st(cp)
    r = _run(cp, "99[Compose] :: pair=55,70")
    _rec("99 Compose: define-mode STORES the "
         "composition AND EXECUTES IT IMMEDIATELY — "
         "the composed Set ran during the Define "
         "itself (store has ComposeStep='1' from the "
         "composed atoms' term-as-label)",
         _msgs(r) == ["Compose pair=55,70 ran=[55, 70]"]
         and cst.compositions.get("pair") == "55,70"
         and cst.store.get("ComposeStep") == "1",
         str(_msgs(r)))
    r = _run(cp, "99[Compose] :: pair")
    _rec("99 Compose: run-mode executes a stored "
         "composition by name",
         _msgs(r) == ["Compose exec pair ran=[55, 70]"],
         str(_msgs(r)))
    r = _run(cp, "99[Compose] :: nosuchname")
    r2 = _run(cp, "99[Compose]")
    _rec("99 Compose: an unknown name and a bare "
         "Compose both fail malformed_composition",
         r.get("ok") is False
         and r.get("error") == "malformed_composition"
         and r2.get("ok") is False
         and r2.get("error") == "malformed_composition",
         str((_msgs(r), _msgs(r2))))
    r = _run(cp, "99[Compose] :: loop=loop")
    _rec("99 Compose: a self-referencing body is "
         "refused compose_cycle and nothing is stored",
         r.get("ok") is False
         and r.get("error") == "compose_cycle"
         and "loop" not in cst.compositions,
         str(_msgs(r)))
    _run(cp, "97[Define] :: step=55")
    r = _run(cp, "99[Compose] :: viadef=step")
    _rec("99 Compose symbiosis: a body may name a "
         "Define (97) — the def's meaning resolves "
         "recursively and runs (ran=[55])",
         _msgs(r) == ["Compose viadef=step ran=[55]"],
         str(_msgs(r)))
    r = _run(cp, "99[Compose] :: raw=51[Select]")
    _rec("99 Compose: a body containing '[' is "
         "executed verbatim as seed text — the raw "
         "Select ran and selected the whole plane",
         _msgs(r) == ["Compose raw=51[Select] "
                      "ran=[51]"]
         and cst.selected == ["welcome"], str(_msgs(r)))
    _run(cp, "86[Delete] :: ComposeStep")
    r = _run(cp, "99[Compose] :: bad=86")
    _rec("99 Compose EXHIBIT: define-mode with a "
         "FAILING body propagates the body's own "
         "error (delete_missing:ComposeStep) — yet "
         "the composition is still stored",
         r.get("ok") is False
         and r.get("error")
         == "delete_missing:ComposeStep"
         and _msgs(r) == ["Compose bad=86 ran=[86]"]
         and cst.compositions.get("bad") == "86",
         str(_msgs(r)))
    r = _run(cp, "99[Compose] :: bad")
    _rec("99 Compose: re-running the stored failing "
         "composition fails the same way",
         r.get("ok") is False
         and r.get("error")
         == "delete_missing:ComposeStep"
         and _msgs(r) == ["Compose exec bad ran=[86]"],
         str(_msgs(r)))
    for i in range(9, 0, -1):
        nxt = "55" if i == 9 else f"d{i + 1}"
        _run(cp, f"97[Define] :: d{i}={nxt}")
    r = _run(cp, "99[Compose] :: deep=d1")
    _rec("99 Compose: resolution nesting deeper "
         "than the bound (default 8) is refused "
         "compose_depth",
         r.get("ok") is False
         and r.get("error") == "compose_depth",
         str(_msgs(r)))
    _run(cp, "93[Try]")
    r = _run(cp, "93[Try]")
    _rec("93 Try: nested Try opens tx1 at depth 1 "
         "(ids are monotonic over history, depth "
         "counts active frames); try_depth is 2",
         _msgs(r) == ["Try id=tx1 depth=1"]
         and cst.try_depth == 2, str(_msgs(r)))
    r = _run(cp, "95[Commit]")
    r2 = _run(cp, "96[Revert]")
    _rec("95/96: Commit settles the INNERMOST active "
         "frame (tx1); Revert then reverts the outer "
         "frame (tx0) — the stack unwinds LIFO",
         _msgs(r) == ["Commit tx1 accepted"]
         and _msgs(r2) == ["Revert tx0 exact"]
         and cst.try_depth == 0,
         str((_msgs(r), _msgs(r2))))
    _run(cp, "55[Set] :: base=1")
    _run(cp, "93[Try]")
    _run(cp, "84[Copy] :: base")
    staged = cst.tx[-1].get("staged_changes")
    r = _run(cp, "89[Diff]")
    _rec("93/89 symbiosis: a spectrum mutation "
         "inside a transaction IS staged "
         "({'op': 'copy', 'lab': 'base'} — the "
         "contrast with Set) and Diff reads the "
         "change against the frame checkpoint",
         staged == [{"op": "copy", "lab": "base"}]
         and _msgs(r) == ["Diff changed=['copy_base'] "
                          "baseline=transaction"],
         str(staged))
    r = _run(cp, "96[Revert]")
    _rec("96 Revert: reverting the frame removes "
         "the staged Copy's product — copy_base is "
         "gone, base survives",
         _msgs(r) == ["Revert tx2 exact"]
         and "copy_base" not in cst.store
         and cst.store.get("base") == "1",
         str(_msgs(r)))
    _cleanup(owner_c)

    # -- REAL_USER_PATH: literal REPL seed lines
    owner2 = "D1RegSpectrumRepl"
    _cleanup(owner2)
    proc = subprocess.run(
        [sys.executable, "-m", "form.repl", "--owner",
         owner2],
        input="93[Try]\n55[Set] :: rk=rv\n95[Commit]\n"
              "90[Trace]\n97[Define] :: greet=hi\n"
              "98[Alias] :: g=greet\n",
        capture_output=True, text=True, cwd=_ROOT,
        timeout=120)
    out = proc.stdout or ""
    _rec("REPL: Try, Set, Commit, Trace, Define and "
         "Alias execute on the literal user path",
         proc.returncode == 0
         and "Try id=tx0 depth=0" in out
         and "Commit tx0 accepted" in out
         and "Trace last 3:" in out
         and "Define greet" in out
         and "Alias g->greet" in out, out[-300:])
    _cleanup(owner2)

    # -- docs pins
    _rec("proof cards carry circuit-22 deep notes "
         "(89-99)",
         all(n in DEEP_NOTES and "circuit 22" in DEEP_NOTES[n]
             for n in range(89, 100)),
         str([n for n in range(89, 100)
              if n not in DEEP_NOTES]))

    total = len(RESULTS)
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    for name, ok, detail in RESULTS:
        if not ok:
            print(f"FAIL {name} :: {detail}")
    print(f"D1_REGISTRY_SPECTRUM: {passed}/{total}")
    return passed == total


def smoke():
    return main()


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
