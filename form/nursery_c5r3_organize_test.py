#!/usr/bin/env python3
"""C5R.3 ORGANIZE — data foundation + edit door + SEE views
(Director 6936275880).

Phase 1: the additive organization schema on Proposal, the
deterministic creation seed (seed-rule v1), typed bound refusals,
the receipt-identity plumbing, the reserved edit-receipt section's
load/save round-trip, and legacy write-freedom.
Phase 2: the trusted edit operation (Nursery.organize_proposal +
Program.organize_proposal + the REPL `proposals organize` door)
and the SEE organization views (searchable topic/tags/cluster,
cursor-bound filters, overlap-aware grouping).

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
- O15: edit happy path — only topic/tags/cluster change (every
  other record field byte-identical), seed provenance retained,
  the receipt persists in the reserved section WITHOUT a digest
  while the returned form's file_digest equals the post-save disk
  SHA and appears nowhere in the file.
- O16: edit refusals — unknown ID and no-changes return typed
  refusals whose refusal receipts are never persisted; caller
  bugs raise instead (missing/empty actor ValueError, typed
  bound violations, a non-organization field TypeError); an edit
  WITHOUT expected_generation is lawful (the binding is opt-in
  at this layer; save()'s lost-update guard still applies), and
  after refused/raised attempts the record is byte-identical.
- O17: expected-generation binding — a wrong or externally-moved
  generation refuses STALE_GENERATION; a stale instance whose
  save guard fires restores its in-memory values.
- O18: an injected save failure during edit propagates, with the
  in-memory record, the disk bytes, and the receipt state all
  restored.
- O19: crash controls (subprocess) — crash_before_replace leaves
  the old generation byte-intact with no receipt;
  crash_after_replace lawfully exposes the complete new
  generation: new topic AND its receipt together.
- O20: SEE organization views — topic grouping partitions with
  the unclassified group holding legacy records; tag grouping
  discloses overlap (memberships > distinct); cluster grouping
  includes the unclustered group; topic/tag/cluster filters
  narrow exactly; search finds stored topic/tag/cluster values;
  an unknown grouping refuses GROUP_INVALID.
- O21: cursor binding — continuing a cursor with a changed topic
  filter or changed grouping refuses CURSOR_FILTER_MISMATCH; an
  edit between pages refuses STALE_CURSOR.
- O22: the REPL organize door — values parsed from the ORIGINAL
  line are stored byte-exact (case/accents), the actor is the
  host-bound repl:<owner>, an `actor:` token refuses
  ARGUMENT_INVALID with no mutation, a confirmed proposal stays
  confirmed after organizing, and grouped browse prints groups.
- O23: model-origin refusal — a connect-session line naming the
  organize door is not a connect command and changes nothing.
- O24: a legacy record's first edit succeeds while its seed
  fields stay empty (an edit never seeds).
- O25: 1,000 organized records round-trip byte-exact, topic
  grouping totals are exact over the full set, and one edit
  leaves the other 999 records untouched.
- O26: the dispositions section is byte-preserved across an
  EDIT save (not only an add save).

Labels: UNIT_SYNTHETIC / INTEGRATION (direct Nursery authority,
isolated temp files) + CROSS_PROCESS for O5 and O19.
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
    NurseryConflictError,
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

    # ── Phase 2: trusted edit operation ────────────────────────

    # O15: edit happy path — org fields only, receipt persisted.
    p15 = os.path.join(tmp, "o15.json")
    n15 = Nursery(path=p15)
    e15 = n15.add(label="Edit Me", words="w", kind="design", origin="")
    before15 = n15.proposals[e15.id].to_dict()
    pre15 = _sha(p15)
    resp15 = n15.organize_proposal(
        e15.id, actor="human:Tester", topic="Roadmap",
        tags=["alpha", "beta"], expected_generation=pre15)
    after15 = n15.proposals[e15.id].to_dict()
    changed15 = {k for k in before15 if before15[k] != after15[k]}
    check("O15.edit_succeeds", resp15.get("ok") is True)
    check("O15.only_org_fields_changed", changed15 == {"topic", "tags"},
          f"changed={sorted(changed15)}")
    check("O15.seed_provenance_retained",
          after15["seed_topic_source"] == "kind"
          and after15["seed_rule_version"] == SEED_RULE_VERSION
          and after15["topic"] == "Roadmap")
    r15 = resp15.get("receipt", {})
    check("O15.receipt_identity",
          r15.get("operation_id") == f"edit:{e15.id}:1"
          and r15.get("actor") == "human:Tester"
          and r15.get("kind") == "human_organization_edit"
          and r15.get("topic_source") == "human"
          and r15.get("predecessor_generation") == pre15)
    check("O15.returned_digest_is_post_save_disk",
          r15.get("file_digest") == _sha(p15) == n15._seen
          and resp15.get("generation") == _sha(p15))
    check("O15.undo_labeled_unavailable",
          "unavailable" in resp15.get("undo", ""))
    with open(p15, encoding="utf-8") as f:
        text15 = f.read()
    stored15 = Nursery.load(p15).organization_edit_receipts.get(
        r15.get("operation_id"), {})
    check("O15.receipt_persisted_without_digest",
          stored15.get("after", {}).get("topic") == "Roadmap"
          and "file_digest" not in stored15
          and r15.get("file_digest") not in text15)

    # O16: edit refusals change nothing. Returned refusals carry a
    # refusal receipt that is NEVER persisted; caller bugs (missing
    # actor, typed bound violations, a non-organization field) raise.
    p16 = os.path.join(tmp, "o16.json")
    n16 = Nursery(path=p16)
    e16 = n16.add(label="Refuse Me", words="w", kind="new", origin="")
    snap16 = _sha(p16)
    before16 = n16.proposals[e16.id].to_dict()
    gen16 = _sha(p16)
    r16a = n16.organize_proposal(
        "nope_0000", actor="human:T", expected_generation=gen16,
        topic="X")
    check("O16.refusal_unknown_id",
          r16a.get("ok") is False
          and r16a.get("error") == "PROPOSAL_NOT_FOUND")
    r16b = n16.organize_proposal(
        e16.id, actor="human:T", expected_generation=gen16)
    check("O16.refusal_no_changes",
          r16b.get("ok") is False and r16b.get("error") == "NO_CHANGES")
    check("O16.refusal_receipts_not_persisted",
          n16.organization_edit_receipts == {}
          and "receipt" in r16a)
    raised16 = 0
    for kwargs16, exc16 in (
            (dict(actor=None, topic="X"), ValueError),
            (dict(actor="", topic="X"), ValueError),
            (dict(actor="human:T", topic="t" * 201), NurseryTopicError),
            (dict(actor="human:T", tags=["a", "a"]), NurseryTagsError),
            (dict(actor="human:T",
                  tags=[f"t{i}" for i in range(17)]), NurseryTagsError),
            (dict(actor="human:T", cluster="c" * 201),
             NurseryClusterError),
            (dict(actor="human:T", topic="X", status="confirmed"),
             TypeError)):
        try:
            n16.organize_proposal(e16.id, **kwargs16)
        except exc16:
            raised16 += 1
    check("O16.caller_bugs_raise", raised16 == 7,
          f"raised={raised16}/7")
    check("O16.status_not_editable",
          n16.proposals[e16.id].status == "pending")
    resp16 = n16.organize_proposal(e16.id, actor="human:T", topic="Free")
    check("O16.unbound_edit_allowed",
          resp16.get("ok") is True
          and n16.proposals[e16.id].topic == "Free")
    n16.organize_proposal(e16.id, actor="human:T", topic="new")
    check("O16.nothing_else_changed",
          n16.proposals[e16.id].to_dict() == before16)

    # O17: expected-generation binding.
    p17 = os.path.join(tmp, "o17.json")
    n17 = Nursery(path=p17)
    e17 = n17.add(label="Gen Bind", words="w", kind="new", origin="")
    r17a = n17.organize_proposal(
        e17.id, actor="human:T", expected_generation="0" * 64,
        topic="X")
    check("O17.wrong_generation_refuses",
          r17a.get("error") == "STALE_GENERATION")
    other17 = Nursery.load(p17)
    other17.add(label="External", words="w", kind="new", origin="")
    r17b = n17.organize_proposal(
        e17.id, actor="human:T", expected_generation=n17._seen,
        topic="X")
    check("O17.moved_generation_refuses",
          r17b.get("error") == "STALE_GENERATION")
    raised17 = False
    try:
        n17.organize_proposal(
            e17.id, actor="human:T", expected_generation=_sha(p17),
            topic="X")
    except NurseryConflictError:
        raised17 = True
    check("O17.stale_instance_guard_restores",
          raised17 and n17.proposals[e17.id].topic == "new"
          and n17.organization_edit_receipts == {})

    # O18: injected save failure restores everything.
    p18 = os.path.join(tmp, "o18.json")
    n18 = Nursery(path=p18)
    e18 = n18.add(label="Fail Save", words="w", kind="design", origin="")
    snap18 = _sha(p18)
    receipt18_before = n18.last_organization_receipt
    orig18 = n18.save
    n18.save = lambda **kw: orig18(_fail_at="replace")
    raised18 = False
    try:
        n18.organize_proposal(
            e18.id, actor="human:T", expected_generation=_sha(p18),
            topic="Nope")
    except Exception:
        raised18 = True
    finally:
        n18.save = orig18
    check("O18.failure_restores_all",
          raised18 and n18.proposals[e18.id].topic == "design"
          and _sha(p18) == snap18
          and n18.organization_edit_receipts == {}
          and n18.last_organization_receipt is receipt18_before)

    # O19: crash controls in a subprocess (Persistence V2).
    helper19 = os.path.join(tmp, "edit_crash_worker.py")
    with open(helper19, "w", encoding="utf-8") as f:
        f.write(
            "import hashlib, sys\n"
            "sys.path.insert(0, sys.argv[1])\n"
            "from form.dell_matrix.nursery import Nursery\n"
            "path, mode = sys.argv[2], sys.argv[3]\n"
            "n = Nursery.load(path)\n"
            "pid = next(iter(n.proposals))\n"
            "with open(path, 'rb') as fh:\n"
            "    gen = hashlib.sha256(fh.read()).hexdigest()\n"
            "n.organize_proposal(pid, actor='human:Crash',\n"
            "                    topic='AfterCrash',\n"
            "                    expected_generation=gen, _fail_at=mode)\n"
            "print('EDIT RETURNED (crash hook did not fire)')\n")
    root19 = os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    for mode19, want_topic19, want_receipts19 in (
            ("crash_before_replace", "design", 0),
            ("crash_after_replace", "AfterCrash", 1)):
        p19 = os.path.join(tmp, f"o19_{mode19}.json")
        n19 = Nursery(path=p19)
        e19 = n19.add(label="Crash Edit", words="w", kind="design",
                      origin="")
        pre19 = _sha(p19)
        proc19 = subprocess.run(
            [sys.executable, helper19, root19, p19, mode19],
            capture_output=True, text=True)
        fresh19 = Nursery.load(p19)
        check(f"O19.{mode19}",
              proc19.returncode == 42
              and fresh19.proposals[e19.id].topic == want_topic19
              and len(fresh19.organization_edit_receipts)
              == want_receipts19,
              f"rc={proc19.returncode} "
              f"err={proc19.stderr.strip()[:200]}")
        if mode19 == "crash_before_replace":
            check("O19.before_replace_bytes_intact",
                  _sha(p19) == pre19)

    # ── Phase 2: SEE organization views ────────────────────────

    # O20: filters + grouping over stored organization.
    p20 = os.path.join(tmp, "o20.json")
    n20 = Nursery(path=p20)

    def mk20(pid, topic, tags, cluster, seeded=True):
        n20.proposals[pid] = Proposal(
            id=pid, label=pid, words="w", kind="new", origin="",
            topic=topic, tags=tags, cluster=cluster,
            seed_topic_source="kind" if seeded else "",
            seed_source_kind="new" if seeded else "",
            seed_rule_version=SEED_RULE_VERSION if seeded else "",
            seed_operation_id=f"seed:{pid}" if seeded else "")

    mk20("r1", "alpha", ["red", "blue"], "c1")
    mk20("r2", "beta", ["red"], "c1")
    mk20("r3", "", [], "", seeded=False)
    mk20("r4", "alpha", ["blue"], "")
    n20.save()
    base20 = n20.query(owner="o20", mode="browse")
    check("O20.ungrouped_shape",
          base20.get("ok") is True and base20.get("groups") is None
          and base20.get("unseeded_in_scope") == 1
          and base20.get("total_matches") == 4)
    gt20 = n20.query(owner="o20", mode="browse", group_by="topic")
    by_topic20 = {g["key"]: g["count"] for g in gt20["groups"]}
    check("O20.topic_partition",
          by_topic20 == {"alpha": 2, "beta": 1, "unclassified": 1}
          and gt20["group_membership_total"] == 4
          and gt20["group_distinct_total"] == 4,
          f"groups={gt20.get('groups')}")
    gtag20 = n20.query(owner="o20", mode="browse", group_by="tag")
    by_tag20 = {g["key"]: g["count"] for g in gtag20["groups"]}
    check("O20.tag_overlap_disclosed",
          by_tag20.get("red") == 2 and by_tag20.get("blue") == 2
          and by_tag20.get(None) == 1
          and gtag20["group_membership_total"] == 5
          and gtag20["group_distinct_total"] == 4,
          f"groups={gtag20.get('groups')}")
    gcl20 = n20.query(owner="o20", mode="browse", group_by="cluster")
    by_cl20 = {g["key"]: g["count"] for g in gcl20["groups"]}
    check("O20.cluster_groups", by_cl20 == {"c1": 2, "": 2},
          f"groups={gcl20.get('groups')}")
    check("O20.topic_filter",
          n20.query(owner="o20", mode="browse",
                    topic="ALPHA")["total_matches"] == 2)
    f20 = n20.query(owner="o20", mode="browse", topic="unclassified")
    check("O20.unclassified_filter_finds_legacy",
          f20["total_matches"] == 1
          and f20["items"][0]["id"] == "r3")
    check("O20.tag_filter",
          n20.query(owner="o20", mode="browse",
                    tag="RED")["total_matches"] == 2)
    check("O20.cluster_empty_filter",
          n20.query(owner="o20", mode="browse",
                    cluster="")["total_matches"] == 2)
    s20a = n20.query(owner="o20", mode="search", term="beta")
    check("O20.search_finds_topic",
          s20a["total_matches"] == 1
          and s20a["items"][0]["id"] == "r2")
    check("O20.search_finds_tags",
          n20.query(owner="o20", mode="search",
                    term="red")["total_matches"] == 2)
    check("O20.search_finds_cluster",
          n20.query(owner="o20", mode="search",
                    term="c1")["total_matches"] == 2)
    bad20 = n20.query(owner="o20", mode="browse", group_by="status")
    check("O20.bad_grouping_refused",
          bad20.get("ok") is False
          and bad20.get("error") == "GROUP_INVALID")

    # O21: cursor binding for the new parameters.
    p21 = os.path.join(tmp, "o21.json")
    n21 = Nursery(path=p21)
    for i21 in range(3):
        pid21 = f"c{i21}"
        n21.proposals[pid21] = Proposal(
            id=pid21, label=pid21, words="w", kind="new", origin="",
            topic="alpha", seed_topic_source="kind",
            seed_source_kind="new",
            seed_rule_version=SEED_RULE_VERSION,
            seed_operation_id=f"seed:{pid21}")
    n21.save()
    page21 = n21.query(owner="o21", mode="browse", topic="alpha",
                       page_size=1)
    cur21 = page21.get("next_cursor")
    check("O21.page_one_cursor", page21.get("ok") is True
          and bool(cur21))
    bad21a = n21.query(owner="o21", mode="browse", topic="beta",
                       cursor=cur21)
    check("O21.changed_topic_filter_refuses",
          bad21a.get("error") == "CURSOR_FILTER_MISMATCH")
    bad21b = n21.query(owner="o21", mode="browse", topic="alpha",
                       group_by="topic", cursor=cur21)
    check("O21.changed_grouping_refuses",
          bad21b.get("error") == "CURSOR_FILTER_MISMATCH")
    page21b = n21.query(owner="o21", mode="browse", topic="alpha",
                        page_size=1, cursor=cur21)
    check("O21.continuation_works",
          page21b.get("ok") is True
          and len(page21b.get("items", [])) == 1)
    first21 = n21.query(owner="o21", mode="browse", page_size=1)
    n21.organize_proposal(
        "c0", actor="human:T", expected_generation=_sha(p21),
        topic="moved")
    stale21 = n21.query(owner="o21", mode="browse", page_size=1,
                        cursor=first21.get("next_cursor"))
    check("O21.edit_between_pages_refuses",
          stale21.get("error") == "STALE_CURSOR",
          f"got {stale21.get('error')}")

    # ── Phase 2: doors ─────────────────────────────────────────

    # O22: the REPL organize door (real owner store, cleaned up).
    import uuid as _uuid
    from form.dell_matrix.nursery import owner_nursery_path
    from form.open import open_program
    from form.repl import _dispatch_public_line, capture_output
    owner22 = "C5R3O22" + _uuid.uuid4().hex[:8].upper()
    path22 = owner_nursery_path(owner22)
    try:
        p22 = open_program(owner22)
        e22 = p22.nursery.add(label="Door Case", words="w",
                              kind="design", origin="")
        _, out22 = capture_output(lambda: _dispatch_public_line(
            p22, f"proposals organize {e22.id} topic:MixedCase "
                 f"tag:Straße tag:News", "o22"))
        stored22 = p22.nursery.proposals[e22.id]
        check("O22.door_stores_byte_exact",
              stored22.topic == "MixedCase"
              and stored22.tags == ["Straße", "News"],
              f"got {stored22.topic!r} {stored22.tags}")
        check("O22.door_prints_undo_unavailable",
              "organization undo is unavailable" in out22)
        check("O22.door_actor_host_bound",
              p22.nursery.last_organization_receipt["actor"]
              == f"repl:{owner22}")
        _, out22b = capture_output(lambda: _dispatch_public_line(
            p22, f"proposals organize {e22.id} actor:evil topic:X",
            "o22"))
        check("O22.actor_token_refused",
              "ARGUMENT_INVALID" in out22b
              and p22.nursery.proposals[e22.id].topic == "MixedCase")
        p22.nursery.confirm(e22.id)
        capture_output(lambda: _dispatch_public_line(
            p22, f"proposals organize {e22.id} cluster:PostConfirm",
            "o22"))
        check("O22.confirmed_stays_confirmed",
              p22.nursery.proposals[e22.id].cluster == "PostConfirm"
              and p22.nursery.proposals[e22.id].status == "confirmed")
        _, out22c = capture_output(lambda: _dispatch_public_line(
            p22, "proposals browse group:topic", "o22"))
        check("O22.grouped_browse_prints_groups",
              "groups by topic" in out22c and "MixedCase" in out22c)
        _, out22d = capture_output(lambda: _dispatch_public_line(
            p22, "proposals search Straße", "o22"))
        check("O22.search_finds_tag_value", e22.id in out22d)
    finally:
        if os.path.exists(path22):
            os.unlink(path22)

    # O23: a connect-session line cannot reach the edit door.
    from form.dell_matrix.connection_session import ConnectionSession
    from form.repl import _handle_connect_line
    owner23 = "C5R3O23" + _uuid.uuid4().hex[:8].upper()
    path23 = owner_nursery_path(owner23)
    try:
        p23 = open_program(owner23)
        e23 = p23.nursery.add(label="Dock Target", words="w",
                              kind="design", origin="")
        session23 = ConnectionSession.open(owner23)
        _, out23 = capture_output(lambda: _handle_connect_line(
            p23, f"proposals organize {e23.id} topic:Hacked",
            session23))
        check("O23.connect_line_cannot_edit",
              "not a connect command" in out23
              and p23.nursery.proposals[e23.id].topic == "design",
              f"out={out23.strip()[:160]!r}")
    finally:
        if os.path.exists(path23):
            os.unlink(path23)

    # O24: a legacy record's first edit never seeds it.
    p24 = os.path.join(tmp, "o24.json")
    _write(p24, {"legacy1": _legacy_record("legacy1", "Legacy")})
    n24 = Nursery.load(p24)
    resp24 = n24.organize_proposal(
        "legacy1", actor="human:T", expected_generation=_sha(p24),
        topic="Filed")
    after24 = n24.proposals["legacy1"]
    check("O24.legacy_first_edit",
          resp24.get("ok") is True and after24.topic == "Filed"
          and after24.seed_topic_source == ""
          and after24.seed_rule_version == ""
          and after24.seed_operation_id == ""
          and resp24["receipt"]["before"]["topic"] == "")

    # O25: 1,000 organized records — round-trip + exact grouping.
    p25 = os.path.join(tmp, "o25.json")
    n25 = Nursery(path=p25)
    for i25 in range(1000):
        pid25 = f"m{i25:04d}"
        n25.proposals[pid25] = Proposal(
            id=pid25, label=f"Mass {i25}", words="w", kind="new",
            origin="", topic=f"t{i25 % 10}",
            tags=[f"g{i25 % 7}", "common"], cluster=f"c{i25 % 5}",
            seed_topic_source="kind", seed_source_kind="new",
            seed_rule_version=SEED_RULE_VERSION,
            seed_operation_id=f"seed:{pid25}")
    n25.save()
    fresh25 = Nursery.load(p25)
    check("O25.thousand_round_trip",
          len(fresh25.proposals) == 1000
          and all(fresh25.proposals[pid].to_dict()
                  == n25.proposals[pid].to_dict()
                  for pid in n25.proposals))
    g25 = fresh25.query(owner="o25", mode="browse", group_by="topic")
    by25 = {gr["key"]: gr["count"] for gr in g25["groups"]}
    check("O25.grouping_totals_exact",
          g25["group_membership_total"] == 1000
          and g25["group_distinct_total"] == 1000
          and len(by25) == 11
          and all(by25[f"t{i}"] == 100 for i in range(10))
          and by25["unclassified"] == 0,
          f"groups={len(g25.get('groups', []))}")
    snap25 = {pid: rec.to_dict()
              for pid, rec in fresh25.proposals.items()}
    resp25 = fresh25.organize_proposal(
        "m0500", actor="human:T", expected_generation=_sha(p25),
        cluster="moved")
    check("O25.one_edit_one_record",
          resp25.get("ok") is True
          and all(fresh25.proposals[pid].to_dict() == snap25[pid]
                  for pid in snap25 if pid != "m0500")
          and len(fresh25.organization_edit_receipts) == 1)

    # O26: dispositions byte-preserved across an EDIT save.
    p26 = os.path.join(tmp, "o26.json")
    n26 = Nursery(path=p26)
    e26 = n26.add(label="Disp Guard", words="w", kind="new", origin="")
    n26.conflict_dispositions["c1"] = {
        "disposition": "operator_kept", "note": "Café ☕"}
    n26.save()
    with open(p26, encoding="utf-8") as f:
        frag26_before = _section_fragment(
            f.read(), DISPOSITION_SECTION_KEY)
    resp26 = n26.organize_proposal(
        e26.id, actor="human:T", expected_generation=_sha(p26),
        topic="Filed")
    with open(p26, encoding="utf-8") as f:
        frag26_after = _section_fragment(
            f.read(), DISPOSITION_SECTION_KEY)
    check("O26.dispositions_preserved_across_edit",
          resp26.get("ok") is True
          and frag26_before == frag26_after and frag26_before != "")

    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"nursery_c5r3_organize_test: {passed}/{len(RESULTS)} PASS")
    return passed == len(RESULTS)


if __name__ == "__main__":
    raise SystemExit(0 if smoke() else 1)
