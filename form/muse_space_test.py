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
import sys

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


def main():
    try:
        snap = load_snapshot_module()
    except Exception as exc:  # module absent at RED time
        check("snapshot_module_importable", False, repr(exc))
        return finish()
    check("snapshot_module_importable", True)

    model = snap.build_snapshot(ROOT)

    # ---- S1: read model shape -------------------------------------
    fields = ("schema_version", "github_snapshot_time", "source_main_sha",
              "source_blob_shas", "retrieval_coverage", "unresolved_sources",
              "nodes", "typed_edges", "belts", "contradictions",
              "perspectives", "derived_metrics", "content_identity")
    check("s1_read_model_fields_present",
          all(f in model for f in fields),
          "file 04 section 2 read model fields + content identity")
    check("s1_pin_is_checkout_head",
          model["source_main_sha"] == snap.git_head(ROOT),
          "snapshot is pinned to this checkout's exact HEAD")

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
    import tempfile
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

    # ---- S3: live revalidation --------------------------------------
    rev = snap.revalidate(model, ROOT)
    check("s3_same_pin_all_current",
          rev["overall"] == "CURRENT" and
          all(s["status"] == "CURRENT" for s in rev["sources"].values()),
          "unchanged sources revalidate CURRENT at the same pin")
    stale = copy.deepcopy(model)
    stale["source_main_sha"] = "0" * 40
    rev2 = snap.revalidate(stale, ROOT)
    check("s3_changed_main_marks_stale",
          rev2["overall"] == "STALE",
          "a changed main marks the snapshot STALE until re-read")
    stale2 = copy.deepcopy(model)
    stale2["source_blob_shas"]["master_work_list"] = "0" * 40
    rev3 = snap.revalidate(stale2, ROOT)
    check("s3_changed_blob_marks_that_source_stale",
          rev3["sources"]["master_work_list"]["status"] == "STALE",
          "staleness is per-source and named, not a blanket guess")
    off = snap.offline_status(model, now_iso="2026-11-21T12:00:00+00:00")
    check("s3_offline_disables_authority_actions",
          off["authority_actions_enabled"] is False and
          off["snapshot_age_seconds"] is not None and
          off["mode"] == "OFFLINE",
          "offline shows the pinned snapshot + age; authority actions "
          "disabled (file 04 section 2)")

    return finish()


def finish():
    n = sum(1 for _, ok in RESULTS if ok)
    print(f"MUSE_SPACE: {n}/{len(RESULTS)}", flush=True)
    return 0 if n == len(RESULTS) else 1


def smoke():
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
