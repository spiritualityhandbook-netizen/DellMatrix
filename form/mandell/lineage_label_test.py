"""Phase H — `lineage` by label (README completion program).

The lineage command historically accepted only an exact proposal or
unit ID, while users think in labels (the README §2 row was PARTIAL:
"label lookup not implemented"). Resolution now lives in
runtime_observe.resolve_lineage_ref beside the outcome/interaction
resolvers, under the same never-ambiguous rule:

- exact ID first (byte-identical historical behavior);
- exact-case label matches, else case-insensitive label matches,
  across nursery proposals AND plane units;
- a confirmed proposal and its plane unit share an ID and count as
  one entity (proposal record wins, as on the ID path);
- exactly one distinct ID resolves; more is an honest ambiguity
  listing; zero is an honest miss. Resolution mutates nothing.

Evidence: INTEGRATION at the resolver + REAL_USER_PATH through the
real REPL subprocess (create / lineage by label / ambiguity / ID
regression / unit by label / miss).
"""

from __future__ import annotations

import glob
import os
import shutil
import subprocess
import sys
import uuid

CHECKS: list = []


def check(name: str, cond: bool, detail: str = "") -> None:
    CHECKS.append((name, bool(cond)))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}"
          + (f" — {detail}" if detail and not cond else ""))


def unique_owner(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def _cleanup(owner: str) -> None:
    from form.dell_matrix.nursery import owner_nursery_path
    paths = [owner_nursery_path(owner),
             f"form/state/program_{owner}.json"]
    try:
        from form.persist import _path, _cp_path
        paths += [_path(owner), _cp_path(owner)]
    except Exception:
        pass
    for path in paths:
        try:
            os.remove(path)
        except OSError:
            pass
    for pat in glob.glob(f"form/state/checkpoint_{owner}_*"):
        try:
            os.remove(pat)
        except OSError:
            pass
    shutil.rmtree(f"form/state/ideas_{owner}", ignore_errors=True)


def _repl(commands: list, owner: str, timeout: int = 120):
    cwd = os.path.abspath(".")
    args = [sys.executable, "-m", "form.repl", "--owner", owner, "--load"]
    env = {**os.environ, "PYTHONPATH": cwd}
    result = subprocess.run(
        args, cwd=cwd, env=env, input="\n".join(commands) + "\n",
        capture_output=True, text=True, timeout=timeout)
    return result.returncode, result.stdout


def smoke() -> bool:
    from form.open import open_program
    from form.mandell import runtime_observe as ro

    owner = unique_owner("lineageh")
    try:
        p = open_program(owner)
        a = p.nursery.add("Unique Label", words="u")
        t1 = p.nursery.add("Twin", words="one")
        t2 = p.nursery.add("Twin", words="two")
        n0 = len(p.nursery.proposals)

        r = ro.resolve_lineage_ref(p, a.id)
        check("fn: id resolves as before",
              r.get("ok") and r.get("via") == "id"
              and r.get("proposal") is a)
        r = ro.resolve_lineage_ref(p, "Unique Label")
        check("fn: exact label resolves",
              r.get("ok") and r.get("via") == "label"
              and r.get("proposal") is a)
        r = ro.resolve_lineage_ref(p, "unique label")
        check("fn: case-insensitive label resolves",
              r.get("ok") and r.get("via") == "label"
              and r.get("proposal") is a)
        r = ro.resolve_lineage_ref(p, "Twin")
        check("fn: shared label is honestly ambiguous",
              r.get("status") == "ambiguous"
              and [m["id"] for m in r.get("matches", [])]
              == sorted([t1.id, t2.id]),
              str(r))
        r = ro.resolve_lineage_ref(p, "No Such Thing")
        check("fn: unknown label is an honest miss",
              r.get("status") == "not_recorded")
        r = ro.resolve_lineage_ref(p, "  ")
        check("fn: empty ref rejected", r.get("status") == "unknown_ref")

        ctx = p.make_review_context(a.id, owner)
        conf = p.confirm_proposal(a.id, _producer=owner,
                                  _review_context=ctx)
        check("fn: fixture confirm works", conf.get("ok") is True,
              str(conf))
        r = ro.resolve_lineage_ref(p, "Unique Label")
        check("fn: confirmed label dedupes proposal+unit to one entity",
              r.get("ok") and r.get("via") == "label"
              and r.get("proposal") is a)
        check("fn: resolution is read-only",
              len(p.nursery.proposals) == n0
              and p.nursery.proposals[a.id].status == "confirmed")

        from form import persist_rest
        persist_rest.save(p)

        rc, out = _repl([
            "lineage Unique Label",
            "lineage Twin",
            f"lineage {t1.id}",
            "create an idea called Solo Thing",
            "lineage Solo Thing",
            "lineage Nonexistent",
            "quit",
        ], owner)
        check("repl: exits clean", rc == 0)
        check("repl: label shows proposal with via-label marker",
              f"Proposal {a.id}" in out and "(via label)" in out,
              out[-500:])
        check("repl: ambiguous label lists both candidate ids",
              "matches 2 records" in out
              and t1.id in out and t2.id in out, out[-500:])
        check("repl: id path unchanged (no via-label marker on id line)",
              f"Proposal {t1.id} [new] Twin" in out
              and f"Proposal {t1.id} [new] Twin (via label)" not in out)
        check("repl: unit resolves by label",
              "Live idea solo_thing: Solo Thing (via label)" in out,
              out[-500:])
        check("repl: unknown label is an honest miss",
              "No proposal or idea for id or label: Nonexistent" in out)
    finally:
        _cleanup(owner)

    passed = sum(1 for _, ok in CHECKS if ok)
    print(f"=== Lineage by label: {passed}/{len(CHECKS)} ===")
    return passed == len(CHECKS)


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
