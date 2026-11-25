"""Phase I — `resonance` / `harmony` user commands (README program).

README §2 listed resonance/harmony as PARTIAL: "Scoring machinery
real (resonance_rank, affinity); no direct user command." The
machinery is now reachable from the REPL:

- `resonance` ranks the canonically active plane units from the
  avatar's center with production resonance_rank over
  nodes_payload + scores + live forces (read-only — it does not
  snap/move the avatar the way first_person_view does).
- `resonance <id or label>` ranks the OTHER active units from the
  focus unit — candidate connections, suggestions only; nothing is
  linked or mutated. Focus resolution reuses resolve_lineage_ref
  (never ambiguous; a pending proposal is honestly "not live").
- `harmony` prints Program.harmony_of over the active unit IDs.

Non-vacuity note: resonance_rank falls back to the score embedded
in each node payload, so dropping the explicit scores argument is
NOT a discriminating mutant. The discriminating controls here are
(1) the no-score control — with no score set, the center unit leads;
setting a real score reorders the ranking — and (2) the lifecycle
filter: a superseded unit remains in plane.units but must never be
ranked; deleting the is_active filter makes it appear.

Evidence: INTEGRATION at runtime_observe.resonance_candidates +
REAL_USER_PATH through the real REPL subprocess.
"""

from __future__ import annotations

import glob
import os
import re
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
    from form.dell_matrix import canonical_lifecycle as cl

    owner = unique_owner("resonancei")
    try:
        p = open_program(owner)
        ids = {}
        for label, words in [
                ("Tidal Gates", "tidal gates need daily inspection"),
                ("Harbor Lights", "harbor lights guide ships"),
                ("Tidal Pools", "tidal pools fill and empty daily")]:
            pr = p.nursery.add(label, words=words)
            ctx = p.make_review_context(pr.id, owner)
            conf = p.confirm_proposal(pr.id, _producer=owner,
                                      _review_context=ctx)
            assert conf.get("ok"), conf
            ids[label] = pr.id
        pend = p.nursery.add("Pending Thought", words="not confirmed")
        p.nursery.add("Twin", words="pending one")
        p.nursery.add("Twin", words="pending two")

        avatar0 = tuple(p.avatar.body.pos)

        # Control: with no scores anywhere, the unit at the center
        # (welcome, dist 0) leads the ranking.
        res = ro.resonance_candidates(p)
        check("fn: no-score control — center unit leads",
              res.get("ok") and res["rows"]
              and res["rows"][0]["id"] == "welcome",
              str(res.get("rows", [])[:1]))
        # A real score reorders: Tidal Gates (equal distance, seed
        # skin) must overtake the center unit once scored.
        p.enhance.state.scores[ids["Tidal Gates"]] = 0.9
        res = ro.resonance_candidates(p)
        rows = res.get("rows", [])
        check("fn: scored unit outranks unscored at equal distance",
              rows and rows[0]["id"] == ids["Tidal Gates"],
              str(rows[:2]))
        check("fn: rows sorted by resonance desc",
              all(rows[i]["resonance"] >= rows[i + 1]["resonance"]
                  for i in range(len(rows) - 1)))
        check("fn: pending proposals never ranked",
              all(r["id"] != pend.id for r in rows))

        res = ro.resonance_candidates(p, "Tidal Gates")
        check("fn: focus mode resolves by label and excludes itself",
              res.get("ok") and res.get("focus", {}).get("id")
              == ids["Tidal Gates"]
              and all(r["id"] != ids["Tidal Gates"]
                      for r in res.get("rows", [])),
              str(res)[:200])
        res = ro.resonance_candidates(p, ids["Harbor Lights"])
        check("fn: focus mode resolves by id",
              res.get("ok") and res.get("focus", {}).get("id")
              == ids["Harbor Lights"])
        res = ro.resonance_candidates(p, "Pending Thought")
        check("fn: pending focus is honestly not_live",
              res.get("status") == "not_live", str(res))
        res = ro.resonance_candidates(p, "Twin")
        check("fn: ambiguous focus reported, never guessed",
              res.get("status") == "ambiguous", str(res))
        res = ro.resonance_candidates(p, "Missing Thing")
        check("fn: unknown focus is an honest miss",
              res.get("status") == "not_recorded", str(res))

        # Lifecycle filter: a superseded unit stays in plane.units
        # but is not active and must never be ranked; its revision is.
        from form.mandell.supersession import supersede_proposal
        old = p.nursery.add("Old Draft", words="original river wording")
        ctx = p.make_review_context(old.id, owner)
        p.confirm_proposal(old.id, _producer=owner, _review_context=ctx)
        p.acceptance_policy.grant_opt_in(owner, scope="supersede")
        rec = supersede_proposal(p, old.id,
                                 words="revised river wording",
                                 _producer=owner)
        assert rec.get("ok"), rec
        res = ro.resonance_candidates(p)
        ranked_ids = [r["id"] for r in res.get("rows", [])]
        active_n = sum(1 for u in p.cube.session.plane.units
                       if cl.is_active(p, u))
        check("fn: superseded unit excluded, revision ranked",
              old.id not in ranked_ids
              and rec["new_id"] in ranked_ids
              and res.get("considered") == active_n,
              str(ranked_ids))
        check("fn: read-only (avatar and scores unchanged)",
              tuple(p.avatar.body.pos) == avatar0
              and p.scores().get(ids["Tidal Gates"]) == 0.9)

        active_ids = [u for u in p.cube.session.plane.units
                      if cl.is_active(p, u)]
        expected_harmony = p.harmony_of(active_ids)

        from form import persist_rest
        persist_rest.save(p)
        rc, out = _repl([
            "resonance",
            "resonance Tidal Gates",
            "harmony",
            "resonance Pending Thought",
            "resonance Missing Thing",
            "quit",
        ], owner)
        check("repl: exits clean", rc == 0)
        check("repl: center mode header + rows",
              "Resonance from where you stand" in out
              and "Tidal Gates" in out and "Harbor Lights" in out)
        check("repl: focus mode is labeled as suggestions only",
              "Candidate connections for Tidal Gates" in out
              and "suggestions only" in out)
        m = re.search(r"Harmony of (\d+) live idea\(s\): ([0-9.]+)", out)
        check("repl: harmony prints the production metric",
              m is not None
              and int(m.group(1)) == len(active_ids)
              and abs(float(m.group(2)) - round(expected_harmony, 3)) < 0.0011,
              out[-400:])
        check("repl: pending focus honestly not live",
              "is not a live idea yet" in out)
        check("repl: unknown focus honestly missed",
              "No proposal or idea for id or label: Missing Thing" in out)
    finally:
        _cleanup(owner)

    passed = sum(1 for _, ok in CHECKS if ok)
    print(f"=== Resonance command: {passed}/{len(CHECKS)} ===")
    return passed == len(CHECKS)


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
