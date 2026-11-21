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
SOURCE_DISAGREEMENT, MERGE_TREE_CONFLICT, GITHUB_UNCHECKED,
AUTHORITY_HOLD, AUTHORITY_NOT_AFFIRMATIVE, CHECKS_MISSING,
CHECK_MISSING, CHECK_HEAD_MISMATCH, POST_MERGE_MISMATCH, FRESH_CLONE_MISSING,
FRESH_CLONE_FAILED, FRESH_CLONE_REVISION, BUNDLE_INCOMPLETE.

Freshness doctrine (Workflow v2; Director correction 7052971505,
2026-11-20): the operative freshness leg is the section-32 GitHub
scan (``authority_freshness``) — exact PR, head, scan timestamp,
latest comment/review ids, and both authorities' dispositions.
Email is exception-only transport (AGENTS.md section 44); a legacy
``mail_freshness`` block may ride in a bundle as a historical
receipt alias when material, but it is never mandatory, never
satisfies the GitHub leg, and never overrides a newer GitHub
ruling. Historical bundles recorded MAIL_UNCHECKED / MAIL_HOLD;
those codes are legacy aliases of GITHUB_UNCHECKED /
AUTHORITY_HOLD.

Written failing-first at plan stage (0/28 while the reconciler was
absent); the reconciler landed at code stage and the suite now
judges it. The suite plants synthetic bundles only — no network,
no gh, no form/state.
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
             "conclusion": "success", "run_id": 111, "head": HEAD,
             "sources": {"ci": "success", "pr_view": "success"}},
            {"name": "smoke", "status": "completed",
             "conclusion": "success", "run_id": 222, "head": HEAD,
             "sources": {"ci": "success", "pr_view": "success"}},
        ],
        "expected_checks": ["build", "smoke"],
        "merge_tree": {"clean": True, "conflicts": []},
        "authority_freshness": {
            "source": "github",
            "pr": 999,
            "head_checked": HEAD,
            "scan_timestamp": "2026-11-20T00:00:00Z",
            "latest_comment_id": "7000000002",
            "latest_review_id": "6000000001",
            "director_disposition": "CONFIRM",
            "keeper_disposition": "CONFIRM",
            "newest_ruling_id": "7000000002",
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
             "conclusion": "success", "run_id": 333, "head": MERGE},
            {"name": "smoke", "status": "completed",
             "conclusion": "success", "run_id": 444, "head": MERGE},
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
    del b["authority_freshness"]
    check("github_unchecked_refused",
          refused_with(b, "GITHUB_UNCHECKED"),
          "no merge outruns an unread ruling about its own PR; "
          "the operative scan is the GitHub record (section 32), "
          "not mail")

    b = clean_pre()
    b["authority_freshness"]["newest_ruling_disposition"] = "HOLD"
    check("authority_hold_refused",
          refused_with(b, "AUTHORITY_HOLD"),
          "a HOLD on the GitHub record stops the gate")

    b = clean_pre()
    b["authority_freshness"]["newest_ruling_disposition"] = \
        "CORRECTION_REQUIRED"
    check("authority_correction_required_refused",
          refused_with(b, "AUTHORITY_HOLD"),
          "CORRECTION_REQUIRED is not a confirmation")

    b = clean_pre()
    v = verdict_of(b)
    check("nc_github_checked_no_mail_reconciled",
          "mail_freshness" not in b
          and v is not None and v.get("verdict") == "RECONCILED",
          "negative control (a): a complete GitHub scan with no "
          "mail leg at all reconciles when every other leg is "
          "valid — mail is not a mandatory leg (Workflow v2)")

    b = clean_pre()
    b["authority_freshness"]["newest_ruling_disposition"] = "HOLD"
    b["mail_freshness"] = {
        "watermark_checked": "1a1example",
        "newest_ruling_id": "7000000001",
        "newest_ruling_disposition": "CONFIRM",
    }
    check("nc_github_hold_overrides_stale_mail_confirm_refused",
          refused_with(b, "AUTHORITY_HOLD"),
          "negative control (b): a newer GitHub HOLD refuses the "
          "gate even when an older mail receipt says CONFIRM — "
          "stale mail never overshadows the GitHub record")

    b = clean_pre()
    del b["authority_freshness"]
    b["mail_freshness"] = {
        "watermark_checked": "1a1example",
        "newest_ruling_id": "7000000001",
        "newest_ruling_disposition": "CONFIRM",
    }
    check("nc_cached_email_only_refused",
          refused_with(b, "GITHUB_UNCHECKED"),
          "negative control (c): cached email alone, with no "
          "GitHub scan, refuses — an unreachable GitHub scan "
          "fails closed and never falls back to stale mail")

    b = clean_pre()
    b["authority_freshness"] = {"source": "email_exception"}
    check("email_exception_without_receipt_refused",
          refused_with(b, "GITHUB_UNCHECKED"),
          "an email-exception transport is accepted only with a "
          "named GitHub outage/rollback authority receipt and "
          "later reconciliation to GitHub; without them it "
          "refuses like any missing scan")

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


    # --- Director 7056433688 correction (2026-11-20): fail-open paths
    # in the checks and authority legs. A bundle with NO CI executions
    # or with non-affirmative authority dispositions must never reach
    # RECONCILED.
    b = clean_pre()
    b["checks"] = []
    check("empty_checks_refused",
          refused_with(b, "CHECKS_MISSING"),
          "a bundle with zero CI executions is not evidence; the "
          "checks leg must refuse, not skip")

    b = clean_pre()
    b["checks"] = [{"name": "lint", "status": "completed",
                    "conclusion": "success", "run_id": 999,
                    "head": HEAD}]
    check("arbitrary_check_set_refused",
          refused_with(b, "CHECK_MISSING"),
          "a nonempty arbitrary list does not satisfy the gate; the "
          "applicable expected check set must be present")

    b = clean_pre()
    del b["expected_checks"]
    check("expected_checks_undeclared_refused",
          refused_with(b, "BUNDLE_INCOMPLETE"),
          "the bundle must declare its applicable expected check set")

    b = clean_pre()
    b["checks"][0]["head"] = "d" * 40
    check("check_head_mismatch_refused",
          refused_with(b, "CHECK_HEAD_MISMATCH"),
          "every check run must be bound to the frozen head")

    b = clean_pre()
    b["authority_freshness"]["director_disposition"] = "PENDING"
    check("pending_director_disposition_refused",
          refused_with(b, "AUTHORITY_NOT_AFFIRMATIVE"),
          "PENDING is not an affirmative Director disposition")

    b = clean_pre()
    b["authority_freshness"]["keeper_disposition"] = "NO_STAMP"
    check("no_stamp_keeper_disposition_refused",
          refused_with(b, "AUTHORITY_NOT_AFFIRMATIVE"),
          "NO_STAMP is not an affirmative Keeper disposition")

    b = clean_pre()
    b["authority_freshness"]["newest_ruling_disposition"] = "PENDING"
    check("pending_newest_ruling_refused",
          refused_with(b, "AUTHORITY_NOT_AFFIRMATIVE"),
          "latest-ruling precedence: a PENDING newest ruling cannot "
          "ride under older affirmative dispositions")

    b = clean_pre()
    b["authority_freshness"]["director_disposition"] = "WHATEVER"
    check("unknown_disposition_refused",
          refused_with(b, "AUTHORITY_NOT_AFFIRMATIVE"),
          "an unknown disposition string must refuse, never pass")

    b = clean_pre()
    b["gate_scope"] = "CODE"
    for k in ("director_disposition", "keeper_disposition",
              "newest_ruling_disposition"):
        b["authority_freshness"][k] = "PLAN_CONFIRM"
    check("plan_scope_disposition_for_code_gate_refused",
          refused_with(b, "AUTHORITY_NOT_AFFIRMATIVE"),
          "a PLAN-scope confirmation does not authorize a CODE gate")

    b = clean_pre()
    b["gate_scope"] = "CODE"
    for k in ("director_disposition", "keeper_disposition",
              "newest_ruling_disposition"):
        b["authority_freshness"][k] = "CODE_CONFIRM"
    v = verdict_of(b)
    check("code_scope_dispositions_reconciled",
          v is not None and v.get("verdict") == "RECONCILED",
          "scope-matching affirmative CODE dispositions reconcile")

    b = clean_pre()
    b["authority_freshness"]["source"] = "email_exception"
    b["authority_freshness"]["exception_receipt"] = "outage-2026"
    check("email_exception_truthy_string_receipt_refused",
          refused_with(b, "GITHUB_UNCHECKED"),
          "a bare truthy receipt value cannot manufacture "
          "authorization; the receipt must be a named record")

    b = clean_pre()
    b["authority_freshness"]["source"] = "email_exception"
    b["authority_freshness"]["exception_receipt"] = {
        "authority": "Director", "receipt_id": "OUTAGE-1"}
    b["authority_freshness"]["director_disposition"] = "PENDING"
    check("email_exception_receipt_cannot_manufacture_authorization",
          refused_with(b, "AUTHORITY_NOT_AFFIRMATIVE"),
          "even a named exception receipt never substitutes for "
          "affirmative authority dispositions")

    b = clean_post()
    b["post_merge"]["post_checks"][0]["head"] = HEAD
    check("post_check_head_mismatch_refused",
          refused_with(b, "POST_MERGE_MISMATCH"),
          "post-merge checks must be bound to the merge commit")

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
