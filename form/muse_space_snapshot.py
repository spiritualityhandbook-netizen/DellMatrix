"""GP-E25 Muse Space -- S1 snapshot reducer + S3 live revalidation.

Design of record: director-reports/GRAND_PLAN_DIRECTOR_EDITION1_
2026-11-18/04_MUSE_SPACE_DESIGN.md. Slice definitions of record:
director-reports/MUSE_SPACE_BUILD_RECORD_2026-11-20.md section 5.

S1: one deterministic, offline, standard-library reducer. It reads
the canonical inputs of file 04 section 2 at one pinned revision of
a local checkout and emits the read model (file 04 section 2 fields)
plus a content identity (sha256 over the canonical serialization).
Same canonical source bytes + same pin -> byte-identical output.

Provenance law (Director 7066270619, CORRECTION REQUIRED at
10b1f2a8): in pinned mode every source is read from the specified
Git pin itself (git show <pin>:<path>) and the recorded blob SHA is
the blob id of the bytes actually parsed, verified against the
pin's recorded blob -- worktree bytes are never reduced under a
pin's AS_OF/SHA attribution. An explicit pin that does not resolve
to a commit is a typed refusal (PinUnavailable), never a silent
fallback. Worktree reads survive only in the unpinned fallback
(no Git HEAD at all), where source_main_sha stays
EVIDENCE_UNAVAILABLE and no pin attribution is claimed.

Honesty law (file 04): a missing input yields EVIDENCE_UNAVAILABLE
and a named unresolved_sources entry -- never a fabricated count.
Crosswalk candidates ride as PROPOSED-class input (Part V owns
reconciliation; this reducer consumes, it never reconciles). The
Edition 1 dependency DAG is pinned at an older main, so its edges
are INFERRED class: inferred/proposed edges never enter canonical
counts or executable gates. The reducer is read-only: it never
writes the register, GitHub, or the Nursery.

S3: revalidate() compares a snapshot's pin and per-source blob SHAs
against a checkout's current state; a changed main or changed
source blob marks the affected evidence STALE until re-read.
STALE requires proof -- both pins real and differing, or a
compared blob that changed; when one side carries no evidence
(unpinned snapshot, checkout without a HEAD) the verdict is
EVIDENCE_UNAVAILABLE, never STALE.
offline_status() reports the pinned snapshot's age and disables
actions that require current authority.

CLI: python3 -m form.muse_space_snapshot [--root PATH] [--pin SHA]
prints the snapshot JSON (canonical bytes) to stdout.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime

SCHEMA_VERSION = "muse-space-read-model-1"
EVIDENCE_UNAVAILABLE = "EVIDENCE_UNAVAILABLE"

_ED1 = "director-reports/GRAND_PLAN_DIRECTOR_EDITION1_2026-11-18"
INPUTS = {
    "master_work_list": "director-reports/master_work_list_items.json",
    "crosswalk_candidates": _ED1 + "/01_SOURCE_CROSSWALK_CANDIDATES.json",
    "dell_baseline": _ED1 + "/05_DELLS_100_ADDRESS_BASELINE.md",
    "dependency_dag": _ED1 + "/08_DEPENDENCY_DAG.json",
    "design": _ED1 + "/04_MUSE_SPACE_DESIGN.md",
    "build_record": "director-reports/MUSE_SPACE_BUILD_RECORD_2026-11-20.md",
}

_DELL_ROW = re.compile(r"^\|\s*(\d{1,3})\s*\|\s*([^|]+?)\s*\|", re.M)


class PinUnavailable(Exception):
    """Typed refusal: an explicit pin does not resolve to a commit
    in this checkout, so no snapshot may be attributed to it."""


def _git(root, *args):
    try:
        out = subprocess.run(["git", "-C", root] + list(args),
                             capture_output=True, text=True, timeout=30)
    except Exception:
        return None
    if out.returncode != 0:
        return None
    return out.stdout.strip()


def _git_bytes(root, *args):
    try:
        out = subprocess.run(["git", "-C", root] + list(args),
                             capture_output=True, timeout=30)
    except Exception:
        return None
    if out.returncode != 0:
        return None
    return out.stdout


def git_head(root):
    return _git(root, "rev-parse", "HEAD")


def _resolve_pin(root, pin):
    """Resolve `pin` to a commit SHA in `root`. An explicit pin that
    does not resolve raises PinUnavailable -- never a silent
    fallback to worktree bytes under a false attribution. Only an
    OMITTED pin (None) defaults to HEAD (None when the checkout has
    no Git HEAD at all: the unpinned fallback); an explicitly
    supplied empty value is an explicit pin, does not resolve, and
    is refused -- it never silently becomes HEAD."""
    if pin is not None:
        resolved = _git(root, "rev-parse", "--verify",
                        "%s^{commit}" % pin)
        if not resolved:
            raise PinUnavailable(
                "pin does not resolve to a commit: %s" % pin)
        return resolved
    return git_head(root)


def _read_at_pin(root, pin, rel):
    """Bytes of `rel` exactly as committed at `pin` (None when the
    path is absent at that revision). Worktree bytes are never read
    in pinned mode."""
    return _git_bytes(root, "show", "%s:%s" % (pin, rel))


def _blob_id(raw):
    """Git blob object id of `raw` (sha1 over the blob header)."""
    return hashlib.sha1(b"blob %d\x00" % len(raw) + raw).hexdigest()


def _blob_sha(root, pin, rel, raw):
    """SHA of the bytes actually parsed. Pinned mode: the git blob
    id of `raw`, verified against the pin's recorded blob; a
    mismatch returns None so unverified bytes are never labeled
    with a pin SHA. Unpinned fallback: content sha256."""
    if pin:
        blob = _blob_id(raw)
        recorded = _git(root, "rev-parse", "%s:%s" % (pin, rel))
        return blob if recorded == blob else None
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _commit_time(root, pin):
    if not pin:
        return EVIDENCE_UNAVAILABLE
    t = _git(root, "log", "-1", "--format=%cI", pin)
    return t if t else EVIDENCE_UNAVAILABLE


def _read(root, rel):
    path = os.path.join(root, rel)
    if not os.path.isfile(path):
        return None
    with open(path, "rb") as fh:
        return fh.read()


def _mwl_node(row, blob):
    title = row.get("title", "")
    label = title.split(" [", 1)[0].strip() or title
    return {
        "id": "mwl:%03d" % int(row["n"]),
        "type": "WORK",
        "label": label,
        "title_full": title,
        "work_ids": row.get("ids", ""),
        "register_status": row.get("status", ""),
        "block": row.get("block", ""),
        "source_refs": [{"file": INPUTS["master_work_list"],
                         "blob_sha": blob}],
    }


def _dell_nodes(text, blob):
    nodes = []
    for num, name in _DELL_ROW.findall(text):
        n = int(num)
        if 0 <= n <= 99:
            nodes.append({
                "id": "dell:%02d" % n,
                "type": "DELL",
                "label": name,
                "address_class": "CORE",
                "evidence_grade": "CONTRACT_ONLY",
                "source_refs": [{"file": INPUTS["dell_baseline"],
                                  "blob_sha": blob}],
            })
    if re.search(r"151 remains a reserved", text):
        nodes.append({
            "id": "dell:151",
            "type": "DELL",
            "label": "Reserved address 151",
            "address_class": "RESERVED",
            "evidence_grade": "CONTRACT_ONLY",
            "source_refs": [{"file": INPUTS["dell_baseline"],
                              "blob_sha": blob}],
        })
    return nodes


def _gp_id(raw):
    return raw.strip().lower().replace("mwl-", "mwl:").replace("gp-", "gp:")


def build_snapshot(root, pin=None):
    """Reduce the canonical inputs under `root` at `pin` (default:
    the checkout's HEAD) into the GP-E25 read model. Never raises on
    a missing input; missing inputs are named in unresolved_sources.
    Raises PinUnavailable when an explicit pin does not resolve to
    a commit. In pinned mode every input is read from the pin
    itself; a path absent at the pin is EVIDENCE_UNAVAILABLE even
    when the worktree holds a copy.
    """
    pin = _resolve_pin(root, pin)
    raw, blob_shas, coverage, unresolved = {}, {}, {}, []
    for key, rel in INPUTS.items():
        data = _read_at_pin(root, pin, rel) if pin else _read(root, rel)
        blob = _blob_sha(root, pin, rel, data) if data is not None else None
        if data is None or (pin and blob is None):
            coverage[key] = EVIDENCE_UNAVAILABLE
            unresolved.append("%s (%s)" % (key, rel))
            blob_shas[key] = None
        else:
            raw[key] = data
            coverage[key] = "RETRIEVED"
            blob_shas[key] = blob

    nodes, edges = [], []

    rows = []
    if "master_work_list" in raw:
        rows = json.loads(raw["master_work_list"].decode("utf-8"))
        nodes.extend(_mwl_node(r, blob_shas["master_work_list"])
                     for r in rows)

    if "dell_baseline" in raw:
        nodes.extend(_dell_nodes(raw["dell_baseline"].decode("utf-8"),
                                 blob_shas["dell_baseline"]))

    crosswalk = None
    if "crosswalk_candidates" in raw:
        crosswalk = json.loads(raw["crosswalk_candidates"].decode("utf-8"))
        known = {n["id"] for n in nodes}
        for cand in crosswalk.get("grand_plan_addition_candidates", []):
            cid = _gp_id(cand.get("candidate_id", ""))
            if cid and cid not in known:
                known.add(cid)
                nodes.append({
                    "id": cid, "type": "CANDIDATE",
                    "label": cand.get("title", ""),
                    "candidate_status": cand.get("status", ""),
                    "equivalence": cand.get(
                        "current_main_equivalence", ""),
                    "source_refs": [{
                        "file": INPUTS["crosswalk_candidates"],
                        "blob_sha": blob_shas["crosswalk_candidates"]}],
                })
        for alias in crosswalk.get("historical_aliases", []):
            src, dst = _gp_id(alias.get("from", "")), _gp_id(alias.get("to", ""))
            for nid in (src, dst):
                if nid and nid not in known:
                    known.add(nid)
                    nodes.append({
                        "id": nid, "type": "CANDIDATE", "label": nid,
                        "candidate_status": "ALIAS_ENDPOINT",
                        "source_refs": [{
                            "file": INPUTS["crosswalk_candidates"],
                            "blob_sha": blob_shas["crosswalk_candidates"]}],
                    })
            if src and dst:
                edges.append({
                    "class": "ALIAS_OF", "from": src, "to": dst,
                    "confidence": "PROPOSED",
                    "provenance": INPUTS["crosswalk_candidates"],
                })

    dag = None
    if "dependency_dag" in raw:
        dag = json.loads(raw["dependency_dag"].decode("utf-8"))
        for dn in dag.get("nodes", []):
            nid = _gp_id(dn.get("id", ""))
            if nid:
                nodes.append({
                    "id": nid, "type": "CIRCUIT",
                    "label": dn.get("title", ""),
                    "phase": dn.get("phase"),
                    "source_refs": [{
                        "file": INPUTS["dependency_dag"],
                        "blob_sha": blob_shas["dependency_dag"]}],
                })
        for dn in dag.get("nodes", []):
            nid = _gp_id(dn.get("id", ""))
            for dep in dn.get("depends_on", []):
                edges.append({
                    "class": "DEPENDS_ON", "from": nid,
                    "to": _gp_id(dep), "confidence": "INFERRED",
                    "provenance": INPUTS["dependency_dag"],
                })

    nodes.sort(key=lambda n: n["id"])
    edges.sort(key=lambda e: (e["class"], e["from"], e["to"]))

    tally = Counter(r.get("status", "") for r in rows)
    active = sum(v for k, v in tally.items() if k != "SANDBOXED")
    belts = {
        "mwl_strict": {
            "definition": "canonical register count from "
                          "master_work_list_items.json at the pin; "
                          "COMPLETE settles only on authority-confirmed "
                          "closure (register law)",
            "rows_total": len(rows),
            "active": active,
            "by_status": dict(sorted(tally.items())),
        },
        "plan": {
            "status": EVIDENCE_UNAVAILABLE,
            "reason": "no canonical per-row PLAN-readiness source in "
                      "the pinned inputs; file 04 section 5B forbids "
                      "substituting historical belt totals",
        },
        "code": {
            "status": EVIDENCE_UNAVAILABLE,
            "reason": "no canonical per-row CODE-certification source "
                      "in the pinned inputs separate from the register "
                      "status; file 04 section 5B forbids substituting "
                      "historical belt totals",
        },
    }
    model = {
        "schema_version": SCHEMA_VERSION,
        "github_snapshot_time": _commit_time(root, pin),
        "source_main_sha": pin if pin else EVIDENCE_UNAVAILABLE,
        "source_blob_shas": blob_shas,
        "retrieval_coverage": coverage,
        "unresolved_sources": unresolved,
        "nodes": nodes,
        "typed_edges": edges,
        "belts": belts,
        "contradictions": [],
        "perspectives": ["map", "belts", "web", "sequence", "mirror",
                         "future", "pending_edits"],
        "derived_metrics": {
            "mwl_rows_total": len(rows),
            "mwl_active": active,
            "mwl_by_status": dict(sorted(tally.items())),
            "node_count": len(nodes),
            "edge_count": len(edges),
            "edges_by_confidence": dict(sorted(Counter(
                e["confidence"] for e in edges).items())),
        },
    }
    problems = validate_snapshot(model)
    contradictions = [{"class": "VALIDATION", "detail": p}
                      for p in problems]
    if crosswalk is not None:
        cw_main = crosswalk.get("verified_current_main")
        if cw_main and pin and cw_main != pin:
            contradictions.append({
                "class": "STALE",
                "detail": "crosswalk candidates were verified against "
                          "main %s, snapshot pin is %s; candidate edges "
                          "remain PROPOSED class" % (cw_main, pin),
            })
    if dag is not None:
        dag_main = dag.get("source_main")
        if dag_main and pin and dag_main != pin:
            contradictions.append({
                "class": "STALE",
                "detail": "dependency DAG source_main is %s, snapshot "
                          "pin is %s; DAG edges remain INFERRED class"
                          % (dag_main, pin),
            })
    model["contradictions"] = contradictions
    model["content_identity"] = hashlib.sha256(
        canonical_bytes(model)).hexdigest()
    return model


def canonical_bytes(model):
    """Deterministic serialization of the read model (identity
    excluded): same model -> same bytes, on any run."""
    body = {k: v for k, v in model.items() if k != "content_identity"}
    return json.dumps(body, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True).encode("utf-8")


def validate_snapshot(model):
    """File 04 section 7 read-model validation. Returns named
    problems; bad rows are named, never quietly discarded."""
    problems = []
    seen = set()
    for node in model.get("nodes", []):
        nid = node.get("id", "")
        if nid in seen:
            problems.append("duplicate node id: %s" % nid)
        seen.add(nid)
        for ref in node.get("source_refs", []):
            if not ref.get("blob_sha"):
                problems.append("node %s missing source SHA" % nid)
    for edge in model.get("typed_edges", []):
        for end in ("from", "to"):
            if edge.get(end) not in seen:
                problems.append("dangling edge %s endpoint: %s"
                                % (end, edge.get(end)))
    return problems


def revalidate(model, root):
    """S3: compare the snapshot's pin and per-source blob SHAs with
    the checkout's current HEAD commit -- pin against pin, never
    worktree bytes against a pin SHA (a dirty worktree is not a
    revision and can neither falsify nor certify a pin). Changed
    main or changed source blob -> that evidence is STALE until
    re-read."""
    head = git_head(root)
    sources = {}
    any_stale = False
    all_current = head is not None
    for key, rel in INPUTS.items():
        recorded = model.get("source_blob_shas", {}).get(key)
        current = (_git(root, "rev-parse", "%s:%s" % (head, rel))
                   if head else None)
        if recorded is None or current is None:
            sources[key] = {"status": EVIDENCE_UNAVAILABLE,
                            "file": rel}
            all_current = False
            continue
        status = "CURRENT" if current == recorded else "STALE"
        if status == "STALE":
            any_stale = True
        sources[key] = {"status": status, "file": rel,
                        "recorded_blob_sha": recorded,
                        "current_blob_sha": current}
    pinned = model.get("source_main_sha")
    if pinned != head:
        all_current = False
        if head is not None and pinned not in (None,
                                               EVIDENCE_UNAVAILABLE):
            # Both sides are real revisions and they differ: the
            # snapshot is provably behind the current main.
            any_stale = True
        # Otherwise one side carries no evidence at all (an
        # unpinned snapshot, or a checkout with no HEAD): a
        # sentinel-vs-absent mismatch proves nothing, so it must
        # not be reported STALE -- the verdict stays
        # EVIDENCE_UNAVAILABLE via the per-source statuses.
    if any_stale:
        overall = "STALE"
    elif all_current:
        overall = "CURRENT"
    else:
        overall = EVIDENCE_UNAVAILABLE
    return {"overall": overall, "current_main_sha": head,
            "pinned_main_sha": model.get("source_main_sha"),
            "sources": sources}


def offline_status(model, now_iso):
    """S3 offline descriptor: pinned snapshot, its age, and
    authority actions disabled (file 04 section 2)."""
    age = None
    stamp = model.get("github_snapshot_time")
    try:
        t0 = datetime.fromisoformat(stamp)
        t1 = datetime.fromisoformat(now_iso)
        age = int((t1 - t0).total_seconds())
    except Exception:
        age = None
    return {"mode": "OFFLINE", "as_of": model.get("source_main_sha"),
            "snapshot_time": stamp, "snapshot_age_seconds": age,
            "authority_actions_enabled": False}


def main(argv=None):
    ap = argparse.ArgumentParser(prog="muse_space_snapshot")
    ap.add_argument("--root", default=".")
    ap.add_argument("--pin", default=None)
    args = ap.parse_args(argv)
    try:
        model = build_snapshot(args.root, args.pin)
    except PinUnavailable as exc:
        sys.stderr.write("PIN UNAVAILABLE: %s\n" % exc)
        return 2
    sys.stdout.write(canonical_bytes(model).decode("utf-8") + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
