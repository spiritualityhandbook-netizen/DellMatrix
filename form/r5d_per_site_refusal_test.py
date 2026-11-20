#!/usr/bin/env python3
"""R5-D per-site executable failing-first refusal tests.

Answers Director 7031447110: "prepare per-site executable
failing-first refusal tests ... for the proposed first bounded A/B
subset". The subset is the 60 buildable sites from
r5d_path_proofs.jsonl (A=24 + B=36) at aeb862f, cross-referenced with
the side-effect inventory at this commit.

Two executable layers, per site:
  DOOR  - history is set to the exact R5-C cap (10,000 entries) by
          direct state setup (setup, not capture), then ONE capture
          is attempted through the site's own door (note / note_seed)
          with the site's own literal arguments where parseable.
          Contract: typed pre-mutation refusal AND history +
          serialized state byte-identical after the attempt.
  CALLER- (open.py Program methods with no required arguments only)
          the real caller method is invoked with history at cap.
          Contract: the refusal propagates (typed exception or
          ok=False receipt) AND serialized state is unchanged --
          i.e. NONE of the caller's own mutations happened. Sites
          whose callers need arguments or non-Program fixtures are
          reported SKIP with the reason, never PASS.

STATUS: FAILING-FIRST on current main (7027419): note() evicts to
history_max=24 and note_seed truncates; no typed refusal exists.
Every DOOR/CALLER check is expected FAIL today for that reason; the
R5-D build for a site turns its checks green. CONTROL checks pass
today. NO product code is changed by this file.

Labels: INTEGRATION (Program + persist serialize, in-process).
Hygiene: uuid owner, exact-pattern cleanup; cleanup errors fail.
"""
from __future__ import annotations

import ast
import inspect
import json
import sys
import uuid
from pathlib import Path

REPO = str(Path(__file__).resolve().parents[1])
sys.path.insert(0, REPO)
EVID = Path(REPO) / "director-reports" / "r5d-evidence"

RESULTS = []
_CLEANUP_ERRORS = []
RUN = uuid.uuid4().hex[:8]
OWNER = f"R5PS{RUN}"
CAP_ENTRIES = 10_000


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def _refusal_seen(fn):
    try:
        ret = fn()
    except Exception as exc:  # noqa: BLE001
        name, msg = type(exc).__name__, str(exc)
        if any(k in name for k in ("Refus", "History", "Cap",
                                   "Budget")) or "refus" in msg.lower() \
                or "LEGACY_OVER_BUDGET" in msg:
            return True, exc
        return False, exc
    if isinstance(ret, dict) and ret.get("ok") is False:
        return True, ret
    return False, ret


def _seed_args(site):
    try:
        vals = [ast.literal_eval(a) for a in site["args"]]
        dell, term = int(vals[0]), str(vals[1])
        label = str(vals[2]) if len(vals) > 2 else ""
        return dell, term, label
    except Exception:  # noqa: BLE001
        return 9, "Show", "r5d-site"


def main():
    from form.open import open_program
    from form.persist import serialize

    proofs = [json.loads(l) for l in
              (EVID / "r5d_path_proofs.jsonl").read_text().splitlines()
              if l.strip()]
    inv = {f"{o['file']}:{o['line']}": o["site_verdict"]
           for o in (json.loads(l) for l in
                     (EVID / "r5d_side_effect_inventory.jsonl")
                     .read_text().splitlines() if l.strip())}
    build = [r for r in proofs if r["verdict"] in
             ("A-PROVEN-DIRECT", "B-PROVEN-CANDIDATE",
              "A-DOWNGRADED-B-LOOP")]
    check("control_buildable_sites_60", len(build) == 60,
          f"n={len(build)}")
    check("control_inventory_covers_all_60",
          len(inv) == 60 and all(
              f"{r['file']}:{r['line']}" in inv for r in build),
          f"inv={len(inv)}")

    p = open_program(OWNER)
    cap_hist = [f"cap-{i:05d}" for i in range(CAP_ENTRIES)]

    # ── DOOR layer: every buildable site ──
    for site in sorted(build, key=lambda x: (x["file"], x["line"])):
        tag = f"{site['file'].split('/')[-1]}:{site['line']}"
        p.history = list(cap_hist)
        before = serialize(p)
        if site["door"] == "note":
            text = (site["args"][0] if site["args"] else "site-note")
            text = f"r5d-site {tag}"  # refusal is cap-driven, not text
            refused, how = _refusal_seen(lambda: p.note(text))
        else:
            dell, term, label = _seed_args(site)
            refused, how = _refusal_seen(
                lambda: p.note_seed(dell, term, label))
        unchanged = list(p.history) == cap_hist \
            and serialize(p) == before
        check(f"door_{tag}_{site['function']}",
              refused and unchanged,
              f"inv={inv.get(f'{site['file']}:{site['line']}')} "
              f"refused={refused} unchanged={unchanged} how={how!r}"[:160])

    # ── CALLER layer: no-required-arg Program methods in open.py ──
    caller_sites = [s for s in build if s["file"] == "form/open.py"]
    for site in sorted(caller_sites, key=lambda x: x["line"]):
        fn = getattr(p, site["function"], None)
        tag = f"open.py:{site['line']}"
        if fn is None or not callable(fn):
            print(f"SKIP  caller_{tag}_{site['function']}  no method")
            continue
        req = [pr for pr in inspect.signature(fn).parameters.values()
               if pr.default is inspect.Parameter.empty
               and pr.kind in (pr.POSITIONAL_ONLY,
                               pr.POSITIONAL_OR_KEYWORD)]
        if req:
            print(f"SKIP  caller_{tag}_{site['function']}  "
                  f"needs args {[r.name for r in req]}")
            continue
        p.history = list(cap_hist)
        before = serialize(p)
        refused, how = _refusal_seen(fn)
        unchanged = serialize(p) == before
        check(f"caller_{tag}_{site['function']}",
              refused and unchanged,
              f"refused={refused} unchanged={unchanged} "
              f"how={how!r}"[:160])

    _cleanup()
    check("cleanup_clean", not _CLEANUP_ERRORS,
          "; ".join(_CLEANUP_ERRORS))
    ok_n = sum(1 for _, ok in RESULTS if ok)
    print(f"R5PS {ok_n}/{len(RESULTS)} PASS")
    return 0 if ok_n == len(RESULTS) else 1


def _cleanup():
    from form.persist import _STATE_DIR, _safe_owner
    from form.dell_matrix.nursery import owner_nursery_path
    state = Path(_STATE_DIR)
    safe = _safe_owner(OWNER)
    cands = [state / f"program_{safe}.json",
             Path(owner_nursery_path(OWNER))]
    cands += list(state.glob(f"*{safe}*"))
    for pth in set(cands):
        try:
            if pth.is_dir():
                import shutil
                shutil.rmtree(pth)
            elif pth.exists():
                pth.unlink()
        except OSError as exc:
            _CLEANUP_ERRORS.append(f"{pth}: {exc}")


def smoke():
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
