#!/usr/bin/env python3
"""C5R.3 ORGANIZE Phase 1 — data foundation (Director 6936275880).

Phase 1 scope ONLY: the additive organization schema on Proposal,
the deterministic creation seed (seed-rule v1), typed bound
refusals, the receipt-identity plumbing, the reserved edit-receipt
section's load/save round-trip, and legacy write-freedom. The edit
door and the SEE view changes are Phase 2 and are NOT built here.

Checks (isolated temp paths throughout; no owner state touched):
- O1: legacy-shaped file (no organization keys) loads with defaults;
  load + SEE browse perform NO writes (file bytes unchanged) and
  assign NO seeds (seed_rule_version stays "").
- O2: seed primary — a validated kind ("new") seeds topic from the
  kind, with exact source fields + rule version + operation ID
  persisted on the record.
- O3: seed fallback — an unvalidated kind with origin "growth:token"
  seeds topic "growth" from the origin family; the EXACT source
  kind/origin values are persisted.
- O4: seed unclassified — unvalidated kind + absent/invalid origin
  family seeds the explicit topic "unclassified".
- O5: seed determinism CROSS_PROCESS — a separate interpreter loads
  the file and reports the same (id, topic, provenance) set and the
  same file digest computed in this process.
- O6: seed atomicity — an injected save failure during add leaves
  no proposal, no seed, no receipt, and unchanged disk bytes.
- O7: the __conflict_dispositions__ section is byte-preserved across
  an organization-carrying save.
- O8: GROW-DUP survivor-no-reseed — a suppressed identical
  growth:token add returns the survivor with NO seed change, NO
  mutation, and NO save (file bytes unchanged).
- O9: duplicate-tag refusal — validate_tags refuses an exact
  duplicate typed (case-distinct tags are NOT duplicates), and a
  persisted record carrying duplicate tags fails load closed.
- O10: bound refusals — topic/cluster/tag bounds refuse typed
  BEFORE mutation; admitted Unicode values pass byte-exact through
  save/load.
- O11: receipt identity — after add, last_organization_receipt
  carries operation ID, actor "system_seed", proposal ID,
  before/after, rule version, predecessor-generation identity, and
  a file_digest equal to the on-disk SHA-256 (also returned by
  save()); the digest appears NOWHERE in the file it describes.
- O12: the __organization_edit_receipts__ section round-trips
  (empty, then with a staged storable receipt); a malformed section
  fails load closed.
- O13: corrupt organization metadata (non-string topic, non-list
  tags) fails load with NurseryLoadError and leaves bytes untouched.
- O14: the 1,000-proposal acceptance fixture shape — 1,000 mixed
  legacy records load and browse with honest totals, bytes
  unchanged, none seeded.

Labels: UNIT_SYNTHETIC / INTEGRATION (direct Nursery authority,
isolated temp files) + CROSS_PROCESS for O5.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from form.dell_matrix.nursery import (
    DISPOSITION_SECTION_KEY,
    EDIT_RECEIPT_SECTION_KEY,
    SEED_RULE_VERSION,
    Nursery,
    NurseryClusterError,
    NurseryLoadError,
    NurseryTagsError,
    NurseryTopicError,
    Proposal,
    build_organization_receipt,
    validate_cluster,
    validate_tags,
    validate_topic,
)

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}"
          + (f" — {detail}" if detail and not cond else ""))


def _sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _write(path, payload):
    with open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps(payload, indent=2))


def _legacy_record(pid, label, status="pending", kind="new"):
    """A pre-C5R.3 record: exactly the fields the old schema wrote."""
    return {
        "id": pid, "label": label, "words": "w", "kind": kind,
        "parents": [], "affinity": 0.0, "reason": "",
        "created": "2026-11-01T00:00:00Z", "status": status,
        "harmony": 0.0, "graph_coherence": 0.0,
        "lifecycle_state": "active", "supersedes_id": None,
        "superseded_by_id": None, "revision_root_id": None,
        "revision_number": None, "origin": "", "detail": "",
        "goals": [],
    }


def _section_fragment(text, key):
    """Extract the raw serialized fragment of a top-level section
    from nursery file text (brace matching, string-aware)."""
    marker = json.dumps(key) + ": "
    start = text.index(marker) + len(marker)
    assert text[start] == "{"
    depth = 0
    in_str = False
    esc = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    raise AssertionError("unterminated section")


def smoke() -> bool:
    tmp = tempfile.mkdtemp(prefix="c5r3_organize_test_")

    # O1: legacy load + browse are write-free and seed-free.
    p1 = os.path.join(tmp, "o1.json")
    _write(p1, {
        "legacy_one_0001": _legacy_record("legacy_one_0001", "Legacy One"),
        "legacy_two_0002": _legacy_record(
            "legacy_two_0002", "Legacy Two", status="confirmed"),
        DISPOSITION_SECTION_KEY: {"c1": {"disposition": "kept"}},
    })
    before = _sha(p1)
    n1 = Nursery.load(p1)
    rec = n1.proposals["legacy_one_0001"]
    check("O1.legacy_defaults", rec.topic == "" and rec.tags == []
          and rec.cluster == "" and rec.seed_topic_source == ""
          and rec.seed_rule_version == "" and rec.seed_operation_id == "")
    res = n1.query(owner="o1", mode="browse")
    check("O1.browse_ok", res.get("ok") is True
          and res.get("total_inventory") == 2)
    check("O1.no_write_no_seed", _sha(p1) == before
          and all(p.seed_rule_version == ""
                  for p in n1.proposals.values()))

    # O2: seed primary from a validated kind.
    p2 = os.path.join(tmp, "o2.json")
    n2 = Nursery(path=p2)
    a = n2.add(label="Seeded By Kind", words="w", kind="design",
               origin="dock:test:model")
    check("O2.seed_primary", a.topic == "design"
          and a.seed_topic_source == "kind"
          and a.seed_source_kind == "design"
          and a.seed_source_origin == "dock:test:model"
          and a.seed_rule_version == SEED_RULE_VERSION
          and a.seed_operation_id == f"seed:{a.id}")
    reloaded = Nursery.load(p2).proposals[a.id]
    check("O2.seed_persisted", reloaded.to_dict() == a.to_dict())

    # O3: seed fallback from the origin family.
    n3 = Nursery(path=os.path.join(tmp, "o3.json"))
    b = n3.add(label="Seeded By Origin", words="w", kind="bespoke",
               origin="growth:token")
    check("O3.seed_fallback", b.topic == "growth"
          and b.seed_topic_source == "origin_family"
          and b.seed_source_kind == "bespoke"
          and b.seed_source_origin == "growth:token")

    # O4: explicit unclassified.
    n4 = Nursery(path=os.path.join(tmp, "o4.json"))
    c1 = n4.add(label="No Source", words="w", kind="bespoke", origin="")
    c2 = n4.add(label="Bad Family", words="w", kind="bespoke",
                origin="Not A Family:x")
    check("O4.seed_unclassified",
          c1.topic == "unclassified"
          and c1.seed_topic_source == "unclassified"
          and c2.topic == "unclassified"
          and c2.seed_topic_source == "unclassified")

    # O5: determinism across a fresh process.
    expected = sorted(
        (p.id, p.topic, p.seed_topic_source, p.seed_source_kind,
         p.seed_source_origin, p.seed_rule_version, p.seed_operation_id)
        for p in n2.proposals.values())
    helper = os.path.join(tmp, "reload_probe.py")
    with open(helper, "w", encoding="utf-8") as f:
        f.write(
            "import hashlib, json, sys\n"
            "sys.path.insert(0, sys.argv[1])\n"
            "from form.dell_matrix.nursery import Nursery\n"
            "n = Nursery.load(sys.argv[2])\n"
            "rows = sorted((p.id, p.topic, p.seed_topic_source,\n"
            "               p.seed_source_kind, p.seed_source_origin,\n"
            "               p.seed_rule_version, p.seed_operation_id)\n"
            "              for p in n.proposals.values())\n"
            "with open(sys.argv[2], 'rb') as fh:\n"
            "    digest = hashlib.sha256(fh.read()).hexdigest()\n"
            "print(json.dumps({'rows': rows, 'digest': digest}))\n")
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    out = subprocess.run(
        [sys.executable, helper, os.path.abspath(root), p2],
        capture_output=True, text=True)
    probe = json.loads(out.stdout) if out.returncode == 0 else {}
    check("O5.cross_process_determinism",
          [list(r) for r in expected] == probe.get("rows")
          and probe.get("digest") == _sha(p2),
          f"rc={out.returncode} err={out.stderr.strip()[:200]}")

    # O6: seed atomicity under an injected save failure.
    p6 = os.path.join(tmp, "o6.json")
    n6 = Nursery(path=p6)
    n6.add(label="Survivor Seed", words="w", kind="new")
    disk_before = _sha(p6)
    receipt_before = n6.last_organization_receipt
    orig_save = n6.save
    n6.save = lambda **kw: orig_save(_fail_at="serialize")
    refused = False
    try:
        n6.add(label="Doomed Seed", words="w", kind="auto")
    except Exception:
        refused = True
    finally:
        n6.save = orig_save
    check("O6.seed_atomicity", refused and len(n6.proposals) == 1
          and _sha(p6) == disk_before
          and n6.last_organization_receipt is receipt_before
          and all(p.label != "Doomed Seed"
                  for p in Nursery.load(p6).proposals.values()))

    # O7: dispositions section byte-preserved across an org save.
    p7 = os.path.join(tmp, "o7.json")
    n7 = Nursery(path=p7)
    n7.conflict_dispositions["conflict-1"] = {
        "disposition": "operator_kept", "note": "Café ☕"}
    n7.save()
    with open(p7, encoding="utf-8") as f:
        frag_before = _section_fragment(f.read(), DISPOSITION_SECTION_KEY)
    n7.add(label="Org Carrying Add", words="w", kind="evolved")
    with open(p7, encoding="utf-8") as f:
        text_after = f.read()
    frag_after = _section_fragment(text_after, DISPOSITION_SECTION_KEY)
    check("O7.dispositions_byte_preserved", frag_before == frag_after)
    check("O7.dispositions_content_kept",
          json.loads(text_after)[DISPOSITION_SECTION_KEY]
          == {"conflict-1": {"disposition": "operator_kept",
                             "note": "Café ☕"}})

    # O8: GROW-DUP survivor gets no reseed, no mutation, no save.
    p8 = os.path.join(tmp, "o8.json")
    n8 = Nursery(path=p8)
    g = dict(label="Twin Cross", words="cross words", kind="new",
             origin="growth:token", affinity=0.5, harmony=0.5)
    s1 = n8.add(**g)
    snap = s1.to_dict()
    disk_before = _sha(p8)
    receipt_before = n8.last_organization_receipt
    s2 = n8.add(**g)
    check("O8.survivor_no_reseed", s2.id == s1.id
          and len(n8.proposals) == 1
          and n8.proposals[s1.id].to_dict() == snap
          and _sha(p8) == disk_before
          and len(n8.suppression_receipts) == 1
          and n8.last_organization_receipt is receipt_before)

    # O9: duplicate-tag refusal (exact duplicates only).
    dup_refused = False
    try:
        validate_tags(["alpha", "beta", "alpha"])
    except NurseryTagsError:
        dup_refused = True
    case_distinct_ok = validate_tags(["Alpha", "alpha"]) == ["Alpha", "alpha"]
    p9 = os.path.join(tmp, "o9.json")
    bad = _legacy_record("dup_tags_0001", "Dup Tags")
    bad["topic"] = ""
    bad["tags"] = ["x", "x"]
    bad["cluster"] = ""
    _write(p9, {"dup_tags_0001": bad})
    load_refused = False
    try:
        Nursery.load(p9)
    except NurseryLoadError:
        load_refused = True
    check("O9.duplicate_tag_refusal",
          dup_refused and case_distinct_ok and load_refused)

    # O10: bound refusals pre-mutation + Unicode byte-exactness.
    refusals = 0
    for fn, val in ((validate_topic, "x" * 201),
                    (validate_cluster, "y" * 201),
                    (validate_tags, ["t"] * 17),
                    (validate_tags, ["z" * 101]),
                    (validate_tags, "notalist")):
        try:
            fn(val)
        except (NurseryTopicError, NurseryClusterError, NurseryTagsError):
            refusals += 1
    check("O10.bound_refusals", refusals == 5, f"refusals={refusals}")
    p10 = os.path.join(tmp, "o10.json")
    n10 = Nursery(path=p10)
    uni = Proposal(id="unicode_0001", label="Unicode", words="w",
                   kind="new", topic="Café ☕",
                   tags=["naïve", "Résumé"], cluster="Groupe Ü")
    n10.proposals[uni.id] = uni
    n10.save()
    back = Nursery.load(p10).proposals[uni.id]
    check("O10.unicode_byte_exact", back.topic == "Café ☕"
          and back.tags == ["naïve", "Résumé"]
          and back.cluster == "Groupe Ü")

    # O11: receipt identity — returned digest, never embedded.
    p11 = os.path.join(tmp, "o11.json")
    n11 = Nursery(path=p11)
    first = n11.add(label="First Receipt", words="w", kind="new")
    r1 = n11.last_organization_receipt
    digest1 = _sha(p11)
    check("O11.receipt_fields", r1 is not None
          and r1["operation_id"] == first.seed_operation_id
          and r1["actor"] == "system_seed"
          and r1["proposal_id"] == first.id
          and r1["before"] == {"topic": "", "tags": [], "cluster": ""}
          and r1["after"]["topic"] == "new"
          and r1["rule_version"] == SEED_RULE_VERSION
          and r1["predecessor_generation"] is None)
    check("O11.returned_digest_is_disk_digest",
          r1["file_digest"] == digest1 == n11._seen)
    second = n11.add(label="Second Receipt", words="w", kind="auto")
    r2 = n11.last_organization_receipt
    with open(p11, encoding="utf-8") as f:
        file_text = f.read()
    check("O11.predecessor_linkage",
          r2["predecessor_generation"] == digest1
          and r2["file_digest"] == _sha(p11) == n11._seen)
    check("O11.digest_never_embedded",
          r2["file_digest"] not in file_text
          and r1["file_digest"] not in file_text
          and all(r2["file_digest"] not in str(v)
                  for v in second.to_dict().values()))
    returned = n11.save()
    check("O11.save_returns_digest", returned == n11._seen == _sha(p11))

    # O12: edit-receipt section round-trip.
    p12 = os.path.join(tmp, "o12.json")
    n12 = Nursery(path=p12)
    n12.save()
    with open(p12, encoding="utf-8") as f:
        raw12 = json.loads(f.read())
    empty_ok = raw12.get(EDIT_RECEIPT_SECTION_KEY) == {}
    staged = build_organization_receipt(
        operation_id="edit:future_0001", actor="human:test",
        proposal_id="future_0001",
        before={"topic": "", "tags": [], "cluster": ""},
        after={"topic": "new", "tags": [], "cluster": ""},
        rule_version=SEED_RULE_VERSION, predecessor_generation=None)
    n12.organization_edit_receipts[staged["operation_id"]] = staged
    n12.save()
    back12 = Nursery.load(p12)
    malformed = os.path.join(tmp, "o12_bad.json")
    _write(malformed, {EDIT_RECEIPT_SECTION_KEY: ["not", "a", "dict"]})
    malformed_refused = False
    try:
        Nursery.load(malformed)
    except NurseryLoadError:
        malformed_refused = True
    check("O12.edit_receipt_section_round_trip", empty_ok
          and back12.organization_edit_receipts
          == {"edit:future_0001": staged}
          and "file_digest" not in staged and malformed_refused)

    # O13: corrupt organization metadata fails load closed.
    corrupt_ok = 0
    for name, mutate in (
            ("topic_type", lambda r: r.update(topic=123)),
            ("tags_type", lambda r: r.update(tags="notalist")),
            ("tags_dup", lambda r: r.update(tags=["a", "a"]))):
        pc = os.path.join(tmp, f"o13_{name}.json")
        record = _legacy_record("corrupt_0001", "Corrupt")
        record.update(topic="", tags=[], cluster="")
        mutate(record)
        _write(pc, {"corrupt_0001": record})
        disk = _sha(pc)
        try:
            Nursery.load(pc)
        except NurseryLoadError:
            if _sha(pc) == disk:
                corrupt_ok += 1
    check("O13.corrupt_org_load_refusal", corrupt_ok == 3,
          f"refused={corrupt_ok}/3")

    # O14: 1,000-proposal fixture shape — load/browse only.
    p14 = os.path.join(tmp, "o14.json")
    payload = {}
    statuses = ["pending", "confirmed", "rejected"]
    for i in range(1000):
        pid = f"fixture_{i:04d}"
        payload[pid] = _legacy_record(
            pid, f"Fixture {i}", status=statuses[i % 3],
            kind=["new", "evolved", "design", "auto"][i % 4])
    _write(p14, payload)
    disk14 = _sha(p14)
    n14 = Nursery.load(p14)
    res14 = n14.query(owner="o14", mode="browse", page_size=200)
    check("O14.fixture_1000", len(n14.proposals) == 1000
          and res14.get("total_inventory") == 1000
          and _sha(p14) == disk14
          and all(p.seed_rule_version == ""
                  for p in n14.proposals.values()))

    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"nursery_c5r3_organize_test: {passed}/{len(RESULTS)} PASS")
    return passed == len(RESULTS)


if __name__ == "__main__":
    raise SystemExit(0 if smoke() else 1)
