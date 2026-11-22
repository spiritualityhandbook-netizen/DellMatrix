"""GP-E25 Muse Space suite — snapshot reducer (S1), static exported
view (S2), live revalidation (S3).

GP-E25 (Part 0, Edition 1 circuit): Living Grand Plan Blueprint /
Muse Space. Design of record: director-reports/GRAND_PLAN_DIRECTOR_
EDITION1_2026-11-18/04_MUSE_SPACE_DESIGN.md. Slice definitions of
record: director-reports/MUSE_SPACE_BUILD_RECORD_2026-11-20.md
section 5:

  S1 -- snapshot reducer. Offline, standard-library, pinned
        revision; emits the read model + content identity.
        Acceptance: byte-identical output across two runs on
        identical inputs, in a fresh clone.
  S2 -- static exported view. The seven views of file 04 section 5
        rendered from one snapshot, labeled AS_OF with the exact
        pin. Two Belts keep independent denominators; the canonical
        MWL number displays as its own strict count.
  S3 -- live revalidation. A changed main or PR head marks affected
        evidence STALE until re-read; offline shows the pinned
        snapshot and its age and disables actions that require
        current authority.

Law carried from file 04: missing data yields EVIDENCE_UNAVAILABLE,
never a fabricated count; PROPOSED/INFERRED edges never enter
canonical counts; untrusted source text is escaped in the view;
the Space never writes the register, GitHub, or the Nursery.

The suite runs offline against this checkout's pinned inputs and
synthetic fixtures only -- no network, no gh, no form/state.
Written failing-first (RED while form/muse_space_snapshot.py and
form/muse_space_views.py were absent).
"""
import copy
import importlib
import json
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

RESULTS = []

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MWL_REL = "director-reports/master_work_list_items.json"


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(("PASS " if cond else "FAIL ") + name +
          ((": " + detail) if (detail and not cond) else ""), flush=True)


def load_snapshot_module():
    return importlib.import_module("form.muse_space_snapshot")


def load_views_module():
    return importlib.import_module("form.muse_space_views")


def mwl_rows():
    with open(os.path.join(ROOT, MWL_REL), encoding="utf-8") as fh:
        return json.load(fh)


# ---- synthetic git fixtures -----------------------------------------
# The pin/revalidation checks build their own temp git repos with
# known pins and pinned commit dates instead of leaning on the
# ambient checkout's git state: CI runs in a detached/shallow
# checkout whose HEAD/history the suite may not assume (Form smoke
# 44927573770 failed s1_pin_is_checkout_head, s3_same_pin_all_current
# and s3_offline_disables_authority_actions at 10b1f2a8 for exactly
# that ambient dependence). Assertions keep their full meaning --
# they are evaluated against a repo whose pins are known by
# construction.

FIXTURE_DATE = "2026-11-20T00:00:00+00:00"


def _fx_git(root, *args):
    env = dict(os.environ)
    env["GIT_AUTHOR_DATE"] = FIXTURE_DATE
    env["GIT_COMMITTER_DATE"] = FIXTURE_DATE
    return subprocess.run(["git", "-C", root] + list(args),
                          capture_output=True, text=True, env=env)


def _fx_write(root, rel, data):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as fh:
        fh.write(data)


def _fx_init(root):
    os.makedirs(root)
    _fx_git(root, "init", "-q")
    _fx_git(root, "config", "user.email", "fixture@example.invalid")
    _fx_git(root, "config", "user.name", "Muse Space Fixture")
    return root


def _fx_commit_all(root, msg):
    _fx_git(root, "add", "-A")
    _fx_git(root, "commit", "-q", "-m", msg)
    return _fx_git(root, "rev-parse", "HEAD").stdout.strip()


def make_fixture_repo(snap, td, register_rows=None):
    """Temp git repo holding the canonical inputs copied from this
    checkout (register optionally replaced), committed once with a
    pinned date. Returns (root, head_sha)."""
    root = _fx_init(os.path.join(td, "fx"))
    for rel in snap.INPUTS.values():
        with open(os.path.join(ROOT, rel), "rb") as fh:
            _fx_write(root, rel, fh.read())
    if register_rows is not None:
        _fx_write(root, MWL_REL,
                  json.dumps(register_rows).encode("utf-8"))
    return root, _fx_commit_all(root, "fixture A")


def _fx_git_on(root, date_iso, *args):
    env = dict(os.environ)
    env["GIT_AUTHOR_DATE"] = date_iso
    env["GIT_COMMITTER_DATE"] = date_iso
    return subprocess.run(["git", "-C", root] + list(args),
                          capture_output=True, text=True, env=env)


def _fx_commit_all_on(root, date_iso, msg):
    _fx_git_on(root, date_iso, "add", "-A")
    _fx_git_on(root, date_iso, "commit", "-q", "-m", msg)
    return _fx_git_on(root, date_iso, "rev-parse", "HEAD").stdout.strip()


def make_dated_fixture_repo(snap, td, first_date, second_date=None,
                            second_rows=None):
    """Temp git repo like make_fixture_repo, but its commits carry
    explicit dates, so each pin's AGE is known by construction.
    With second_date, a second commit rewrites the register to
    second_rows at that date. Returns (root, [pin, ...])."""
    root = _fx_init(os.path.join(td, "fxd"))
    for rel in snap.INPUTS.values():
        with open(os.path.join(ROOT, rel), "rb") as fh:
            _fx_write(root, rel, fh.read())
    pins = [_fx_commit_all_on(root, first_date, "dated fixture A")]
    if second_date is not None:
        _fx_write(root, MWL_REL,
                  json.dumps(second_rows).encode("utf-8"))
        pins.append(_fx_commit_all_on(root, second_date,
                                       "dated fixture B"))
    return root, pins


def main():
    try:
        snap = load_snapshot_module()
    except Exception as exc:  # module absent at RED time
        check("snapshot_module_importable", False, repr(exc))
        return finish()
    check("snapshot_module_importable", True)

    model = snap.build_snapshot(ROOT)

    # Fixture repo with known pins for every git-state-dependent
    # check (see the fixture-builder note above).
    fx_td = tempfile.TemporaryDirectory()
    fx_root, fx_head = make_fixture_repo(snap, fx_td.name)
    fx_model = snap.build_snapshot(fx_root)

    # ---- S1: read model shape -------------------------------------
    fields = ("schema_version", "github_snapshot_time", "source_main_sha",
              "source_blob_shas", "retrieval_coverage", "unresolved_sources",
              "nodes", "typed_edges", "belts", "contradictions",
              "perspectives", "derived_metrics", "content_identity")
    check("s1_read_model_fields_present",
          all(f in model for f in fields),
          "file 04 section 2 read model fields + content identity")
    check("s1_pin_is_checkout_head",
          fx_model["source_main_sha"] == fx_head ==
          snap.git_head(fx_root),
          "snapshot is pinned to the fixture checkout's exact HEAD")

    rows = mwl_rows()
    work = [n for n in model["nodes"] if n["type"] == "WORK"]
    check("s1_mwl_nodes_complete_and_unique",
          len(work) == len(rows) and
          len({n["id"] for n in work}) == len(rows) and
          all(n["id"].startswith("mwl:") for n in work),
          "one typed node per register row, namespace-prefixed, unique")

    from collections import Counter
    src_tally = Counter(r["status"] for r in rows)
    check("s1_status_tally_matches_source",
          model["derived_metrics"]["mwl_by_status"] == dict(src_tally),
          "derived tally is computed from the source rows, not typed in")
    active = sum(v for k, v in src_tally.items() if k != "SANDBOXED")
    check("s1_canonical_counts_exclude_proposals",
          model["derived_metrics"]["mwl_rows_total"] == len(rows) and
          model["derived_metrics"]["mwl_active"] == active,
          "crosswalk candidates never inflate the canonical denominator")

    # ---- S1: determinism (the slice acceptance) --------------------
    model2 = snap.build_snapshot(ROOT)
    check("s1_determinism_byte_identical",
          snap.canonical_bytes(model) == snap.canonical_bytes(model2) and
          model["content_identity"] == model2["content_identity"],
          "two runs on identical inputs -> byte-identical output")

    # ---- S1: edge law ----------------------------------------------
    aliases = [e for e in model["typed_edges"] if e["class"] == "ALIAS_OF"]
    check("s1_crosswalk_aliases_proposed_only",
          len(aliases) == 8 and
          all(e["confidence"] == "PROPOSED" for e in aliases),
          "Edition 1 crosswalk candidates ride as PROPOSED-class input")
    deps = [e for e in model["typed_edges"] if e["class"] == "DEPENDS_ON"]
    check("s1_dag_edges_never_verified_class",
          len(deps) > 0 and
          all(e["confidence"] in ("INFERRED", "PROPOSED") for e in deps),
          "DAG source record is pinned at an older main; its edges may "
          "not pose as VERIFIED")
    check("s1_validation_clean_on_real_inputs",
          snap.validate_snapshot(model) == [],
          "no duplicate ids, dangling edges, or missing source SHAs")

    dells = [n for n in model["nodes"] if n["type"] == "DELL"]
    core = [n for n in dells if n.get("address_class") == "CORE"]
    reserved = [n for n in dells if n.get("address_class") == "RESERVED"]
    check("s1_dell_nodes_100_core_plus_reserved_151",
          len(core) == 100 and len(reserved) == 1 and
          reserved[0]["id"] == "dell:151",
          "file 04 M-04: 100 core addresses; 151 marked reserved example")

    # ---- S1: honest absence ----------------------------------------
    with tempfile.TemporaryDirectory() as td:
        os.makedirs(os.path.join(td, "director-reports"))
        with open(os.path.join(td, MWL_REL), "w", encoding="utf-8") as fh:
            json.dump(rows[:3], fh)
        partial = snap.build_snapshot(td)
    check("s1_missing_input_is_evidence_unavailable",
          any("01_SOURCE_CROSSWALK" in u for u in
              partial["unresolved_sources"]) and
          partial["retrieval_coverage"].get(
              "crosswalk_candidates") == "EVIDENCE_UNAVAILABLE",
          "a missing canonical input is named, never silently dropped "
          "or fabricated")

    bad = copy.deepcopy(model)
    bad["typed_edges"] = bad["typed_edges"] + [{
        "class": "DEPENDS_ON", "from": "gp:e01", "to": "mwl:999",
        "confidence": "INFERRED", "provenance": "synthetic fixture"}]
    problems = snap.validate_snapshot(bad)
    check("s1_dangling_edge_named_not_dropped",
          any("mwl:999" in p for p in problems),
          "read-model validation names the dangling ref (file 04 s.7)")
    bad2 = copy.deepcopy(model)
    bad2["nodes"] = bad2["nodes"] + [dict(bad2["nodes"][0])]
    check("s1_duplicate_id_named",
          any("duplicate" in p.lower() for p in snap.validate_snapshot(bad2)),
          "duplicate stable IDs fail validation by name")

    # ---- S2: static exported view ----------------------------------
    try:
        views = load_views_module()
    except Exception as exc:
        check("views_module_importable", False, repr(exc))
        return finish()
    check("views_module_importable", True)
    html = views.render_html(model)
    for marker in ("Blueprint Map", "Two Belts", "Connection Web",
                   "Sequence", "Sync Mirror", "Future View",
                   "Pending Edits"):
        check("s2_view_present_" + marker.lower().replace(" ", "_"),
              marker in html, "file 04 section 5 view: " + marker)
    check("s2_as_of_label_with_exact_pin",
          "AS_OF" in html and model["source_main_sha"] in html,
          "static export carries the exact pin it was rendered from")
    check("s2_future_view_projection_watermark",
          "PROJECTION" in html,
          "unbuilt capability is never presented as live (file 04 s.5F)")
    belts_section = html.split("Two Belts", 1)[1].split("Connection Web", 1)[0]
    check("s2_belts_no_fabricated_split",
          "EVIDENCE_UNAVAILABLE" in belts_section,
          "PLAN/CODE belt split is not derivable from the pinned "
          "register JSON; the view says so instead of inventing one")
    web_section = html.split("Connection Web", 1)[1].split("Sequence", 1)[0]
    check("s2_web_drawn_shown_total_disclosed",
          all(w in web_section for w in ("drawn", "shown", "total")),
          "coverage counts are disclosed, never a silent cut (M-08)")

    evil = copy.deepcopy(model)
    evil["nodes"] = [dict(evil["nodes"][0],
                          label="<script>alert(1)</script>")]
    evil_html = views.render_html(evil)
    check("s2_untrusted_text_escaped",
          "<script>alert(1)</script>" not in evil_html and
          "&lt;script&gt;" in evil_html,
          "source text cannot control scripts (M-14)")

    # ---- S3: live revalidation (fixture repo, known pins) -----------
    rev = snap.revalidate(fx_model, fx_root)
    check("s3_same_pin_all_current",
          rev["overall"] == "CURRENT" and
          all(s["status"] == "CURRENT" for s in rev["sources"].values()),
          "unchanged sources revalidate CURRENT at the same pin")
    stale = copy.deepcopy(fx_model)
    stale["source_main_sha"] = "0" * 40
    rev2 = snap.revalidate(stale, fx_root)
    check("s3_changed_main_marks_stale",
          rev2["overall"] == "STALE",
          "a changed main marks the snapshot STALE until re-read")
    stale2 = copy.deepcopy(fx_model)
    stale2["source_blob_shas"]["master_work_list"] = "0" * 40
    rev3 = snap.revalidate(stale2, fx_root)
    check("s3_changed_blob_marks_that_source_stale",
          rev3["sources"]["master_work_list"]["status"] == "STALE",
          "staleness is per-source and named, not a blanket guess")
    off = snap.offline_status(fx_model, now_iso="2026-11-21T12:00:00+00:00")
    check("s3_offline_disables_authority_actions",
          off["authority_actions_enabled"] is False and
          off["snapshot_age_seconds"] is not None and
          off["mode"] == "OFFLINE",
          "offline shows the pinned snapshot + age; authority actions "
          "disabled (file 04 section 2)")

    # ---- S1: pinned-snapshot provenance (Director 7066270619) -------
    # CORRECTION REQUIRED at 10b1f2a8: build_snapshot read worktree
    # bytes but attached the pin's blob SHA, so checkout B + pin A (or
    # dirty edits at HEAD=A) could publish B's values under AS_OF A.
    # These fixtures are the failing-first proof: every source must be
    # read from the specified Git pin, with the recorded SHA verified
    # against the bytes actually parsed.
    with tempfile.TemporaryDirectory() as td:
        fx, pin_a = make_fixture_repo(snap, td, register_rows=rows[:2])
        _fx_write(fx, MWL_REL, json.dumps(rows[:3]).encode("utf-8"))
        _fx_commit_all(fx, "fixture B")  # checkout now at B
        snap_a = snap.build_snapshot(fx, pin=pin_a)
        a_blob = _fx_git(fx, "rev-parse",
                         pin_a + ":" + MWL_REL).stdout.strip()
    check("s1_pin_a_checkout_b_register_not_misattributed",
          snap_a["source_main_sha"] == pin_a and
          snap_a["derived_metrics"]["mwl_rows_total"] == 2 and
          snap_a["source_blob_shas"]["master_work_list"] == a_blob and
          "mwl:003" not in {n["id"] for n in snap_a["nodes"]},
          "pin A against checkout B reduces A's register: no B row "
          "values, counts, or nodes under AS_OF A / A's blob SHA")

    with tempfile.TemporaryDirectory() as td:
        fx, pin_a = make_fixture_repo(snap, td)
        dirty = rows + [dict(rows[0], n=999, title="DIRTY MARKER",
                             status="OPEN")]
        _fx_write(fx, MWL_REL, json.dumps(dirty).encode("utf-8"))
        m_dirty = snap.build_snapshot(fx)  # pin defaults to HEAD=pin_a
        rev_dirty = snap.revalidate(m_dirty, fx)
    check("s1_dirty_worktree_register_not_published_under_pin",
          m_dirty["source_main_sha"] == pin_a and
          m_dirty["derived_metrics"]["mwl_rows_total"] == len(rows) and
          all("DIRTY MARKER" not in n.get("label", "")
              for n in m_dirty["nodes"]) and
          rev_dirty["overall"] == "CURRENT",
          "uncommitted register edits never enter a pinned snapshot; "
          "revalidate compares pin-vs-pin, so no dirty byte is "
          "certified and no false CURRENT is issued")

    with tempfile.TemporaryDirectory() as td:
        fx = _fx_init(os.path.join(td, "fx3"))
        with open(os.path.join(ROOT, MWL_REL), "rb") as fh:
            _fx_write(fx, MWL_REL, fh.read())
        pin_a = _fx_commit_all(fx, "fixture A (no crosswalk)")
        cw_rel = snap.INPUTS["crosswalk_candidates"]
        _fx_write(fx, cw_rel, json.dumps({
            "grand_plan_addition_candidates": [{
                "candidate_id": "GP-WORKTREE-ONLY",
                "title": "worktree only", "status": "PROPOSED"}],
            "historical_aliases": []}).encode("utf-8"))
        m_wt = snap.build_snapshot(fx, pin=pin_a)
    check("s1_absent_at_pin_worktree_only_input_unavailable",
          m_wt["retrieval_coverage"].get(
              "crosswalk_candidates") == "EVIDENCE_UNAVAILABLE" and
          any("01_SOURCE_CROSSWALK" in u
              for u in m_wt["unresolved_sources"]) and
          "gp:worktree-only" not in {n["id"] for n in m_wt["nodes"]},
          "a path absent at the pin is EVIDENCE_UNAVAILABLE even "
          "when the worktree holds a copy; worktree bytes are never "
          "consumed as pin evidence")

    with tempfile.TemporaryDirectory() as td:
        fx, pin_a = make_fixture_repo(snap, td)
        refused = False
        try:
            snap.build_snapshot(fx, pin="0" * 40)
        except snap.PinUnavailable:
            refused = True
    check("s1_unknown_pin_typed_refusal",
          refused,
          "an unresolvable pin raises the typed PinUnavailable "
          "refusal; no snapshot is fabricated under a false pin")

    # ---- Consumer contract (Director 7075379361) -------------------
    # The seven-day pin freshness gate is WITHDRAWN; the governing
    # contract is: AS_OF/source pin explicit, STALE marking on
    # revalidation, offline age display with authority actions
    # disabled. These checks pin that contract -- including the
    # negative control that NO age refusal exists -- at library
    # level. Consumer wiring (a production caller of revalidate /
    # offline_status; a pin argument on the S2 CLI) is UNIMPLEMENTED
    # and is marked as such in the build addendum; nothing here
    # claims a consumer exists.

    # (a) AS_OF / source pin explicit at a NON-HEAD pin.
    with tempfile.TemporaryDirectory() as td:
        fx, pins = make_dated_fixture_repo(
            snap, td, "2026-11-10T00:00:00+00:00",
            second_date="2026-11-20T00:00:00+00:00",
            second_rows=rows[:3])
        pin_old, pin_new = pins
        m_old = snap.build_snapshot(fx, pin=pin_old)
        html_old = views.render_html(m_old)
        off_old = snap.offline_status(
            m_old, now_iso="2026-11-22T00:00:00+00:00")
    check("contract_as_of_explicit_at_non_head_pin",
          m_old["source_main_sha"] == pin_old and
          pin_old != pin_new and
          "AS_OF" in html_old and pin_old in html_old and
          pin_new not in html_old and
          off_old["as_of"] == pin_old,
          "a snapshot built at an older pin names that pin -- in "
          "the model, in the export's AS_OF label, and in the "
          "offline descriptor -- never the checkout HEAD")

    # (b) Offline age is numeric, grows with pin age, actions off.
    with tempfile.TemporaryDirectory() as td:
        fx, pins = make_dated_fixture_repo(
            snap, td, "2026-11-01T00:00:00+00:00",
            second_date="2026-11-20T00:00:00+00:00",
            second_rows=rows[:3])
        now = "2026-11-22T00:00:00+00:00"
        off_a = snap.offline_status(
            snap.build_snapshot(fx, pin=pins[0]), now_iso=now)
        off_b = snap.offline_status(
            snap.build_snapshot(fx, pin=pins[1]), now_iso=now)
    check("contract_offline_age_grows_with_pin_age",
          isinstance(off_a["snapshot_age_seconds"], int) and
          isinstance(off_b["snapshot_age_seconds"], int) and
          off_a["snapshot_age_seconds"] >
          off_b["snapshot_age_seconds"] > 0 and
          off_a["authority_actions_enabled"] is False and
          off_b["authority_actions_enabled"] is False,
          "offline age is a real number ordered by pin age; "
          "authority actions are disabled at every age (no "
          "threshold)")

    # (c) Real revalidation: a source blob that actually changed on
    # HEAD after the pin marks THAT source STALE; untouched sources
    # stay CURRENT; at HEAD every source is CURRENT.
    with tempfile.TemporaryDirectory() as td:
        fx, pins = make_dated_fixture_repo(
            snap, td, "2026-11-10T00:00:00+00:00",
            second_date="2026-11-20T00:00:00+00:00",
            second_rows=rows[:3])
        m_pin = snap.build_snapshot(fx, pin=pins[0])
        rev_real = snap.revalidate(m_pin, fx)  # HEAD is pins[1]
        m_head = snap.build_snapshot(fx, pin=pins[1])
        rev_head = snap.revalidate(m_head, fx)
    check("contract_revalidate_real_blob_change_marks_source_stale",
          rev_real["sources"]["master_work_list"]["status"] ==
          "STALE" and
          rev_real["sources"]["design"]["status"] == "CURRENT" and
          rev_real["overall"] == "STALE" and
          rev_head["overall"] == "CURRENT" and
          all(s["status"] == "CURRENT"
              for s in rev_head["sources"].values()),
          "a register blob genuinely rewritten after the pin "
          "revalidates STALE by name while untouched sources stay "
          "CURRENT; at HEAD every source is CURRENT")

    # (d) NEGATIVE CONTROL (withdrawn gate): a pin far older than
    # seven days builds and exports successfully -- no age refusal
    # exists anywhere in the path. The pin is a real commit in the
    # fixture repo's own git history, dated 2026-10-01; the suite
    # never leans on the ambient checkout's history (see the
    # fixture-builder note above).
    with tempfile.TemporaryDirectory() as td:
        fx, pins = make_dated_fixture_repo(
            snap, td, "2026-10-01T00:00:00+00:00")
        m_ancient = snap.build_snapshot(fx, pin=pins[0])
        html_ancient = views.render_html(m_ancient)
        off_ancient = snap.offline_status(
            m_ancient, now_iso="2026-11-22T00:00:00+00:00")
    check("contract_no_age_refusal_old_pin_builds",
          m_ancient["source_main_sha"] == pins[0] and
          pins[0] in html_ancient and
          off_ancient["snapshot_age_seconds"] > 7 * 86400,
          "a 52-day-old pin (fixture-dated 2026-10-01 against the "
          "2026-11-22 reference now) builds and renders with no "
          "refusal; if an age gate is ever silently added, this "
          "check turns red")

    # (e) CLI surface of the typed refusal: exit 2, named on stderr,
    # no snapshot on stdout.
    cli = subprocess.run(
        [sys.executable, "-m", "form.muse_space_snapshot",
         "--root", fx_root, "--pin", "0" * 40],
        cwd=ROOT, capture_output=True, text=True)
    check("contract_cli_unresolvable_pin_exit_2",
          cli.returncode == 2 and "PIN UNAVAILABLE" in cli.stderr and
          cli.stdout == "",
          "the S1 CLI refuses an unresolvable pin with exit 2 and "
          "a named stderr refusal; nothing is printed as a snapshot")

    return finish()


def finish():
    n = sum(1 for _, ok in RESULTS if ok)
    print(f"MUSE_SPACE: {n}/{len(RESULTS)}", flush=True)
    return 0 if n == len(RESULTS) else 1


def smoke():
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
