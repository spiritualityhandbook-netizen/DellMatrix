"""SM-07 failing-first suite — the unified merge-gate reconciler.

Register row #91 (SM-07): exact-head / merge-tree / post-merge /
fresh-clone gate reconciliation. Today those four legs are four
separate rituals held together by prose and operator discipline
(AGENTS.md section 32, the verify-merge-gate skill, the merge
record). The PR #340 section-32 receipt disclosure (INDEX, recorded
2026-11-09) is the standing proof of the defect class: a freshness
check that WAS performed left no independently retrievable receipt,
so the gate could not be reconciled after the fact.

Contract under test (Part 0 plan, director-reports/PART_0_PLAN_2026-11-20.md):
``certification_runner.reconcile_gate(bundle)`` is a pure, offline,
standard-library function. It consumes ONE evidence bundle for ONE
frozen candidate and returns ONE verdict:

    {"verdict": "RECONCILED" | "REFUSED",
     "refusals": [<refusal code>, ...],
     "legs": {leg name -> state}}

It never raises on malformed input — a malformed bundle is a
REFUSED bundle (fail-closed). Refusal codes include:
HEAD_DRIFT, TREE_DRIFT, CHECK_NOT_TERMINAL, CHECK_FAILED_UNCLASSIFIED,
CHECK_FAILED_CANDIDATE, CHECK_FAILED_PREEXISTING_UNAUTHORIZED,
SOURCE_DISAGREEMENT, MERGE_TREE_CONFLICT, MAIL_UNCHECKED, MAIL_HOLD,
POST_MERGE_MISMATCH, FRESH_CLONE_MISSING, FRESH_CLONE_FAILED,
FRESH_CLONE_REVISION, BUNDLE_INCOMPLETE.

This suite is failing-first: at plan stage the reconciler does not
exist, so every check fails with the absence recorded. The suite
plants synthetic bundles only — no network, no gh, no form/state.
"""
import copy
import importlib.util
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(("PASS " if cond else "FAIL ") + name +
          ((": " + detail) if (detail and not cond) else ""), flush=True)


def _load_reconciler():
    path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "director-reports", "certification_runner.py")
    try:
        spec = importlib.util.spec_from_file_location(
            "certification_runner", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return getattr(mod, "reconcile_gate", None)
    except Exception:
        return None


RECONCILE = _load_reconciler()

HEAD = "a" * 40
TREE = "b" * 40
MERGE = "c" * 40


def clean_pre():
    return {
        "phase": "pre",
        "pr": 999,
        "head": HEAD,
        "tree": TREE,
        "frozen_head": HEAD,
        "frozen_tree": TREE,
        "checks": [
            {"name": "build", "status": "completed",
             "conclusion": "success", "run_id": 111,
             "sources": {"ci": "success", "pr_view": "success"}},
            {"name": "smoke", "status": "completed",
             "conclusion": "success", "run_id": 222,
             "sources": {"ci": "success", "pr_view": "success"}},
        ],
        "merge_tree": {"clean": True, "conflicts": []},
        "mail_freshness": {
            "watermark_checked": "1a1example",
            "newest_ruling_id": "7000000001",
            "newest_ruling_disposition": "CONFIRM",
        },
        "red_classifications": {},
        "allow_preexisting": False,
    }


def clean_post():
    b = clean_pre()
    b["phase"] = "post"
    b["post_merge"] = {
        "merged": True,
        "merge_commit": MERGE,
        "expected_merge_commit": MERGE,
        "main_head_after": MERGE,
        "post_checks": [
            {"name": "build", "status": "completed",
             "conclusion": "success", "run_id": 333},
            {"name": "smoke", "status": "completed",
             "conclusion": "success", "run_id": 444},
        ],
    }
    b["fresh_clone"] = {"ran": True, "revision": MERGE,
                        "result": "success"}
    return b


def verdict_of(bundle):
    """Return the verdict dict, or None when the reconciler is
    absent or raises (both are contract failures at this stage)."""
    if RECONCILE is None:
        return None
    try:
        return RECONCILE(bundle)
    except Exception:
        return None


def refused_with(bundle, code):
    v = verdict_of(bundle)
    return (v is not None and v.get("verdict") == "REFUSED"
            and code in v.get("refusals", []))


def main():
    if RECONCILE is None:
        check("reconciler_present", False,
              "certification_runner.reconcile_gate does not exist yet "
              "(SM-07 unbuilt — expected at plan stage)")
    else:
        check("reconciler_present", True)

    v = verdict_of(clean_pre())
    check("clean_pre_bundle_reconciled",
          v is not None and v.get("verdict") == "RECONCILED",
          "a fully-evidenced pre-merge bundle must reconcile")

    b = clean_pre()
    b["checks"][1]["status"] = "in_progress"
    b["checks"][1]["conclusion"] = None
    check("running_check_refused",
          refused_with(b, "CHECK_NOT_TERMINAL"),
          "a non-terminal check is not a passed check")

    b = clean_pre()
    b["checks"][1]["conclusion"] = "failure"
    check("unclassified_red_refused",
          refused_with(b, "CHECK_FAILED_UNCLASSIFIED"),
          "every red check must be classified before the gate")

    b = clean_pre()
    b["checks"][1]["conclusion"] = "failure"
    b["red_classifications"] = {"smoke": "candidate-caused"}
    check("candidate_caused_red_refused",
          refused_with(b, "CHECK_FAILED_CANDIDATE"),
          "a candidate-caused failure refuses the gate")

    b = clean_pre()
    b["checks"][1]["conclusion"] = "failure"
    b["red_classifications"] = {"smoke": "pre-existing"}
    check("preexisting_red_without_authorization_refused",
          refused_with(b, "CHECK_FAILED_PREEXISTING_UNAUTHORIZED"),
          "pre-existing red still needs the governing authorization")

    b = clean_pre()
    b["checks"][1]["conclusion"] = "failure"
    b["red_classifications"] = {"smoke": "pre-existing"}
    b["allow_preexisting"] = True
    v = verdict_of(b)
    check("preexisting_red_with_authorization_reconciled_and_carried",
          v is not None and v.get("verdict") == "RECONCILED"
          and v.get("legs", {}).get("checks", {}).get(
              "classifications", {}).get("smoke") == "pre-existing",
          "an authorized pre-existing red reconciles, with the "
          "classification carried into the verdict record")

    b = clean_pre()
    b["head"] = "d" * 40
    check("head_drift_refused", refused_with(b, "HEAD_DRIFT"),
          "any new commit is a new candidate; the gate re-runs")

    b = clean_pre()
    b["tree"] = "e" * 40
    check("tree_drift_refused", refused_with(b, "TREE_DRIFT"),
          "the frozen tree is part of the candidate identity")

    b = clean_pre()
    b["checks"][0]["sources"] = {"ci": "success", "pr_view": "failure"}
    check("source_disagreement_refused",
          refused_with(b, "SOURCE_DISAGREEMENT"),
          "two sources disagreeing stops the gate until resolved "
          "from the authoritative source")

    b = clean_pre()
    b["merge_tree"] = {"clean": False, "conflicts": ["form/open.py"]}
    check("merge_tree_conflict_refused",
          refused_with(b, "MERGE_TREE_CONFLICT"),
          "a non-clean merge-tree refuses the gate")

    b = clean_pre()
    del b["mail_freshness"]
    check("mail_unchecked_refused",
          refused_with(b, "MAIL_UNCHECKED"),
          "no merge outruns an unread ruling about its own PR")

    b = clean_pre()
    b["mail_freshness"]["newest_ruling_disposition"] = "HOLD"
    check("mail_hold_refused", refused_with(b, "MAIL_HOLD"),
          "a HOLD newer than the watermark stops the gate")

    b = clean_pre()
    b["mail_freshness"]["newest_ruling_disposition"] = \
        "CORRECTION_REQUIRED"
    check("mail_correction_required_refused",
          refused_with(b, "MAIL_HOLD"),
          "CORRECTION_REQUIRED is not a confirmation")

    v = verdict_of(clean_post())
    check("clean_post_bundle_reconciled",
          v is not None and v.get("verdict") == "RECONCILED",
          "a fully-evidenced post-merge bundle must reconcile")

    b = clean_post()
    b["post_merge"]["merge_commit"] = "f" * 40
    check("post_merge_mismatch_refused",
          refused_with(b, "POST_MERGE_MISMATCH"),
          "the recorded merge commit must match the authority")

    b = clean_post()
    b["post_merge"]["post_checks"][1]["conclusion"] = "failure"
    check("post_merge_red_refused",
          refused_with(b, "POST_MERGE_MISMATCH"),
          "post-merge checks are part of the reconciled verdict")

    b = clean_post()
    b["fresh_clone"] = {"ran": False, "revision": None, "result": None}
    check("fresh_clone_missing_refused",
          refused_with(b, "FRESH_CLONE_MISSING"),
          "fresh-clone verification is a leg, not an option")

    b = clean_post()
    b["fresh_clone"]["result"] = "failure"
    check("fresh_clone_failure_refused",
          refused_with(b, "FRESH_CLONE_FAILED"),
          "a failing fresh-clone run refuses the post-merge leg")

    b = clean_post()
    b["fresh_clone"]["revision"] = HEAD
    check("fresh_clone_wrong_revision_refused",
          refused_with(b, "FRESH_CLONE_REVISION"),
          "fresh-clone proof must be at the merged revision")

    for idx, bad in enumerate(
            (None, {}, {"phase": "pre"}, {"phase": "sideways"})):
        v = verdict_of(bad)
        check("malformed_bundle_refused_%d" % idx,
              v is not None and v.get("verdict") == "REFUSED",
              "malformed input refuses; it never raises and never "
              "reconciles")

    n = sum(1 for _, okk in RESULTS if okk)
    print(f"GATE_RECONCILIATION: {n}/{len(RESULTS)}", flush=True)
    return 0 if n == len(RESULTS) else 1


def smoke():
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
