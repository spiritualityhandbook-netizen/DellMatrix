"""STEP 11 — public-contract wording circuit: B10/B17/B19-B21, C1/C2.

Contracts proven here (wording circuit — mechanisms unchanged):

- B10 Measure (71): the public manor says COUNT / selected-set
  cardinality only; it does NOT say "Quantify a property"; a
  kind/unit label is stated as annotation, and property
  vocabulary is stated as deferred (C2 — no vocabulary invented).
- B17 Commit (95): the public manor says mark/accept of the
  current live state; it does NOT say "Atomically" or "staged";
  it states Revert covers only the Try checkpoint fields.
  Legitimate atomic claims elsewhere (atomic_write mechanism,
  README confirmation-atomicity) are NOT B17's target and stay.
- B19 Route (59): the manor documents the context boundary, and
  the boundary is TESTED on the public chain path: outside a
  Branch, 59 executes as Route (route channel + route cell);
  inside a Branch chain the 59 atom is consumed as the Else
  marker (receipt skipped, reason names the Else marker) and
  never executes as Route (route channel unchanged by it).
- B20 Move/Replace (85/87): the manors carry the deliberate
  contrast — 85 overwrites an existing destination; 87 refuses
  an occupied destination with no mutation — and 87's manor no
  longer says "Atomic". DELL_RUNTIME.md rows carry the same
  contrast.
- B21 (23/28/44/47): manors state what the runtime does —
  23 Lock is the sandbox switch over units (not immutability,
  not a permission grant); 28 Rollback is authority-mediated
  (bare use denied); 44 Bridge and 47 Embed are honest refusals
  (no provider bound), not capability claims.
- Step 7 Q1/Q2 settlement: card 61 (the ONE canonical home)
  states the Join-vs-Any empty-set distinction (an empty
  executed child set is a successful Join under both policies;
  Any(empty)=False is Dell 67's rule) and the partial/ok
  distinction (partial = occurrence-level incompleteness,
  omission OR failure; ok is the separate success verdict).
- Limitation record (step 4 deferral): LEGACY_ONLY_SIGNATURE
  carries an appended dated correction (2026-11-01, step 11);
  the historical 2026-10-27 evidence line is byte-intact and
  the original limitation field is NOT silently rewritten.
  The correction states the verified current count (15 typed /
  85 untyped, executed this suite) and that the original "43"
  figure reconciles with neither 100-14 nor 100-15.

Labels: INTEGRATION / PUBLIC_ENTRY (real Program for B19).
"""
from __future__ import annotations

import glob
import os
import shutil

RESULTS: list = []


def _rec(name: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((name, bool(ok), detail))


def _cleanup(owner: str) -> None:
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "state")
    if not os.path.isdir(base):
        return
    errors = []
    for pat in (f"program_{owner}.json", f"nursery_{owner}.json",
                f"checkpoint_{owner}.json",
                f"confirm_journal_{owner}.json",
                f"confirm_gen_{owner}.json",
                f"confirm_current_{owner}.json",
                f"exchange_journal_{owner}.json"):
        for f in glob.glob(os.path.join(base, pat)):
            try:
                os.remove(f)
            except OSError as e:
                errors.append(f"{f}: {e}")
    d = os.path.join(base, f"ideas_{owner}")
    if os.path.isdir(d):
        try:
            shutil.rmtree(d)
        except OSError as e:
            errors.append(f"{d}: {e}")
    if errors:
        raise RuntimeError(f"cleanup failed for {owner}: {errors}")


def _prog(owner: str):
    _cleanup(owner)
    from form.open import Program
    from form.mandell.core_ii_exec import attach
    p = Program(owner=owner)
    attach(p)
    return p


def _run(prog, seed):
    from form.mandell.executor import execute_seed
    return execute_seed(prog, seed)


def _manor(n: int) -> str:
    from form.mandell.registry import get_dell
    d = get_dell(n) or {}
    return str(d.get("manor") or "")


def _manors() -> None:
    m71 = _manor(71)
    _rec("B10 71 manor says count/cardinality of the selected set",
         "count" in m71.lower() and "cardinality" in m71.lower(), m71)
    _rec("B10 71 manor does NOT claim property quantification",
         "quantify a property" not in m71.lower(), m71)
    _rec("B10/C2 71 manor: label is annotation; property vocab deferred",
         "annotation" in m71.lower() and "deferred" in m71.lower(), m71)

    m95 = _manor(95)
    _rec("B17 95 manor says mark/accept of current live state",
         "mark/accept" in m95.lower() and "live" in m95.lower(), m95)
    _rec("B17 95 manor does NOT say Atomically / staged",
         "atomically" not in m95.lower() and "staged" not in m95.lower(),
         m95)
    _rec("B17 95 manor bounds Revert to the Try checkpoint fields",
         "revert" in m95.lower() and "checkpoint" in m95.lower(), m95)

    m59 = _manor(59)
    _rec("B19 59 manor documents the Branch/Else context boundary",
         "else" in m59.lower() and "branch" in m59.lower(), m59)

    m85, m87 = _manor(85), _manor(87)
    _rec("B20 85 manor states overwrite of an existing destination",
         "overwrite" in m85.lower(), m85)
    _rec("B20 87 manor states occupied-destination refusal",
         "occupied" in m87.lower()
         and ("refus" in m87.lower() or "replace_occupied" in m87), m87)
    _rec("B20 87 manor does NOT say Atomic",
         "atomic" not in m87.lower(), m87)

    m23 = _manor(23)
    _rec("B21 23 manor: sandbox switch over units",
         "sandbox" in m23.lower(), m23)
    _rec("B21 23 manor does NOT claim immutability",
         "immutable" not in m23.lower()
         and "freeze immutable" not in m23.lower(), m23)

    m28 = _manor(28)
    _rec("B21 28 manor: authority-mediated, bare use denied",
         "denied" in m28.lower()
         and ("authority" in m28.lower() or "grant" in m28.lower()), m28)

    m44, m47 = _manor(44), _manor(47)
    _rec("B21 44 manor: honest refusal, no provider bound",
         "refusal" in m44.lower() and "bridge_unavailable" in m44, m44)
    _rec("B21 47 manor: honest refusal, no provider bound",
         "refusal" in m47.lower() and "embed_unavailable" in m47, m47)
    _rec("B21 47 manor does NOT claim Vectorize",
         "vectorize" not in m47.lower(), m47)


def _runtime_rows() -> None:
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "mandell", "DELL_RUNTIME.md")
    text = open(path, encoding="utf-8").read()
    _rec("B20 DELL_RUNTIME 87 row no longer says 'atomic swap'",
         "atomic swap" not in text, "")
    rows = {ln.split("|")[1].strip(): ln for ln in text.splitlines()
            if ln.startswith("|") and len(ln.split("|")) > 2}
    _rec("B20 DELL_RUNTIME 85 row states overwrite",
         "overwrite" in rows.get("85", "").lower(), rows.get("85", ""))
    _rec("B20 DELL_RUNTIME 87 row states occupied refusal",
         "occupied" in rows.get("87", "").lower(), rows.get("87", ""))


def _legit_atomic_intact() -> None:
    here = os.path.dirname(os.path.abspath(__file__))
    aw = os.path.join(here, "dell_matrix", "atomic_write.py")
    _rec("B17 trap: atomic_write mechanism file still present",
         os.path.isfile(aw), aw)
    readme = os.path.join(os.path.dirname(here), "README.md")
    if not os.path.isfile(readme):
        readme = os.path.join(here, "..", "README.md")
    text = open(readme, encoding="utf-8").read() \
        if os.path.isfile(readme) else ""
    _rec("B17 trap: README confirmation-atomicity claim intact",
         "Confirmation atomicity" in text, readme)


def _b19_boundary() -> None:
    p = _prog("Step11B19")
    st = p.core_ii
    r = _run(p, "59[Route] :: alt")
    cell = dict(st.last_result or {})
    _rec("B19 (a) outside Branch: 59 executes as Route "
         "(route channel + route cell)",
         r.get("ok") is True and st.route == "alt"
         and cell.get("source") == "route"
         and cell.get("value") == "alt",
         f"route={st.route} cell={cell}")
    r2 = _run(p, "60[true] > 80[Context] > 59[Route] :: evil > "
                 "70[Count] > 61[Join]")
    atoms = {a.get("dell"): a for a in r2.get("atom_results", [])}
    a59 = atoms.get(59, {})
    _rec("B19 (b) inside Branch: 59 receipt skipped as Else marker",
         a59.get("skipped") is True
         and "else marker" in str(a59.get("reason", "")).lower()
         and "not executed as route"
         in str(a59.get("reason", "")).lower(), str(a59))
    _rec("B19 (b) inside Branch: route channel unchanged by the 59 atom",
         st.route == "alt", f"route={st.route}")
    _cleanup("Step11B19")


def _join_any_card() -> None:
    from form.mandell.dell_cards import DEEP_NOTES
    card61 = DEEP_NOTES.get(61, "")
    low = card61.lower()
    _rec("Q2 card 61 states Join empty-set success vs Any(empty)=False",
         "empty" in low and "join" in low and "any" in low
         and "false" in low, card61[:80])
    _rec("Q1 card 61 states partial vs ok (partial != failure verdict)",
         "partial" in low and "ok" in low
         and ("omission" in low or "incomplete" in low), card61[:80])


def _limitation_correction() -> None:
    from form.mandell.limitation_knowledge import LIMITATIONS
    from form.mandell.signatures import get_signature
    entry = next((e for e in LIMITATIONS
                  if e.get("id") == "LEGACY_ONLY_SIGNATURE"), {})
    _rec("Limitation: historical 2026-10-27 evidence line byte-intact",
         entry.get("evidence", "").startswith(
             "14 Dells have typed signatures (P12 probe 2026-10-27"),
         entry.get("evidence", "")[:60])
    _rec("Limitation: original limitation field not silently rewritten",
         entry.get("limitation") == "43 Dells lack typed signatures",
         entry.get("limitation", ""))
    corr = str(entry.get("dated_correction", ""))
    typed = [n for n in range(100) if get_signature(n)]
    _rec("Limitation: dated step-11 correction appended",
         "2026-11-01" in corr and "step 11" in corr.lower(), corr[:80])
    _rec("Limitation: correction states verified current count 15/85",
         len(typed) == 15 and "15" in corr and "85" in corr,
         f"typed={len(typed)} corr={corr[:80]}")
    _rec("Limitation: correction names '43' as irreconcilable",
         "43" in corr and "reconcil" in corr.lower(), corr[:80])


def main() -> bool:
    _manors()
    _runtime_rows()
    _legit_atomic_intact()
    _b19_boundary()
    _join_any_card()
    _limitation_correction()
    total = len(RESULTS)
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    for name, ok, detail in RESULTS:
        if not ok:
            print(f"FAIL {name} :: {detail}")
    print(f"STEP11_PUBLIC_CONTRACTS: {passed}/{total}")
    return passed == total


def smoke() -> bool:
    return main()


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
