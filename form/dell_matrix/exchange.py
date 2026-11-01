"""Exchange v1 (master plan P9) — seed packets with receipts.

The Fourth Piece (adopted 2026-10-26; grounding packet
~/workspace/FOURTH_PIECE_EXCHANGE_GROUNDING_PACKET.md): seeds
and Keeps travel between minds CARRYING THEIR RECEIPTS — the
guess recorded before the test, the test method, the measured
result, the mirror, the outcome — so a receiver inherits a
warrant, not a claim, and their own gate still decides.

Reception law (non-negotiable): an imported packet lands as a
PENDING Nursery proposal under the receiver's own gate —
STORED, never ELIGIBLE-by-default, never auto-learned.
Replication is counted, never scored: the system shows how
many receipts from how many distinct origins stand behind a
Keep; humans judge. Chain lint labels missing links precisely
("method absent") — absence of evidence is labeled, never
silently upgraded (Positive Evidence Law).

Deliberately NOT built (grounding packet section 7): no
central registry/server, no global trust scores, no
auto-learning, no identity beyond origin stamps, no
marketplace. Transport is a file.

Receipts are recorded when a run happens (record_receipt,
persisted per proposal in the ``exchange_receipts`` section),
assembled into the packet at export (build_packet), validated
strictly at the boundary (validate_packet — closed shape,
bounded, JSON data only, never evaluated), screened against
the receiver's protected values at import, and displayed by
lint at the gate.

Director completion order (2026-10-28) residual repair: the
imported seed's ORIGINAL payload — label, chain, Keep and the
manifest's declared requirements — is preserved as validated
durable data in the ``exchange_seeds`` section, associated
with the imported proposal. The Nursery proposal's detail is
a human review RENDERING derived from that payload, never its
source: export reads the stored original, so a packet survives
A→B→C with its seed and requirements byte-identical. (The
defect this repairs: export sourced the Keep from the
formatted, bounded detail — prefix added, tail clipped — and
chain/requirements were never stored at all.)
"""

from __future__ import annotations

import hashlib
import json
import os
import time
import uuid
from typing import Any, Dict, List, Tuple

from form.dell_matrix.session_section import (
    MISSING,
    serialize_records_section,
    validate_records_section,
)

PACKET_VERSION = 1
REGISTRY_STAMP = "core1:00-50,core2:51-99"

MAX_RECEIPTS = 50
_MAX_RECEIPT_ENTRIES = 200

_PACKET_KEYS = frozenset({"version", "seed", "manifest", "receipts"})
_SEED_KEYS = frozenset({"label", "chain", "keep"})
_MANIFEST_KEYS = frozenset(
    {"author_origin", "created", "registry", "requirements"})
# AF-3: provenance is an OPTIONAL manifest field (back-compat:
# legacy packets without it still validate). It states how the
# seed in THIS packet was sourced at export: "original" = the
# stored imported payload, byte-identical; "reconstructed" =
# the native/rendered fallback. Absence is never upgraded to a
# claim — an unflagged packet's provenance is unknown.
_PROVENANCE_VALUES = frozenset({"original", "reconstructed"})


def _oldest_key(entries: Dict[str, Any]) -> str:
    """DAF-05: the shared explicit eviction policy (oldest by ts,
    ties by insertion order) — see session_section.oldest_key.
    The shared loader returns records newest-first, so raw dict
    order must never choose the victim."""
    from form.dell_matrix.session_section import oldest_key
    return oldest_key(entries)


def _receipts_digest(receipts: List[Dict[str, str]]) -> str:
    """DAF-04: order-insensitive digest of a receipt multiset —
    the durable provenance witness stamped on the seed record at
    import, checked again at export."""
    canon = sorted(
        json.dumps({k: r[k] for k in sorted(RECEIPT_KEYS)},
                   sort_keys=True, ensure_ascii=False)
        for r in receipts)
    return hashlib.sha256("\n".join(canon).encode("utf-8")).hexdigest()


def _bump_dropped(program: Any, attr: str, n: int = 1) -> None:
    """AF-4: count a writer-side eviction at the moment and
    place of loss (PP2b B2). The serialize boundary in
    persist.py remains a backstop for populations trimmed
    elsewhere; writers that trim to the cap before save would
    otherwise make that backstop unreachable."""
    total = getattr(program, attr, 0)
    if not isinstance(total, int) or isinstance(total, bool) \
            or total < 0:
        total = 0
    setattr(program, attr, total + n)
RECEIPT_KEYS = frozenset(
    {"origin", "guess", "test_method", "result", "mirror", "outcome"})

_RECEIPT_ENTRY_KEYS = frozenset({
    "entry_id", "owner", "ts", "pid", "origin", "guess",
    "test_method", "result", "mirror", "outcome"})

EXCHANGE_RECEIPTS_SECTION_VERSION = 1


class ExchangeError(Exception):
    """A packet or receipt failed validation at the boundary.

    `details` (DAF-06 follow-up, step 5b): optional structured
    evidence for failures whose compensation state matters —
    stage, compensation status, journal retention. The string
    message remains the human-readable summary; details never
    replace it."""

    def __init__(self, message: str = "", *,
                 details: Dict[str, Any] = None):
        super().__init__(message)
        self.details: Dict[str, Any] = dict(details) if details else {}


def _str(v: Any, limit: int, field: str) -> str:
    if not isinstance(v, str) or len(v) > limit:
        raise ExchangeError(f"{field} must be a string of "
                            f"at most {limit} chars")
    return v


def _validate_receipt(r: Any) -> Dict[str, str]:
    if not isinstance(r, dict) or set(r.keys()) != RECEIPT_KEYS:
        raise ExchangeError("receipt keys mismatch")
    out = {}
    for k, limit in (("origin", 200), ("guess", 500),
                     ("test_method", 1000), ("result", 1000),
                     ("mirror", 1000), ("outcome", 500)):
        out[k] = _str(r[k], limit, f"receipt.{k}")
    if not out["origin"]:
        raise ExchangeError("receipt.origin must be non-empty")
    return out


def validate_packet(data: Any) -> Dict[str, Any]:
    """Strictly validate a seed packet. Raises ExchangeError.
    Returns a normalized copy (only known keys, bounded)."""
    if not isinstance(data, dict) or set(data.keys()) != _PACKET_KEYS:
        raise ExchangeError("packet keys mismatch")
    if data["version"] != PACKET_VERSION:
        raise ExchangeError("unsupported packet version")
    seed = data["seed"]
    if not isinstance(seed, dict) or set(seed.keys()) != _SEED_KEYS:
        raise ExchangeError("seed keys mismatch")
    seed = {
        "label": _str(seed["label"], 120, "seed.label"),
        "chain": _str(seed["chain"], 4000, "seed.chain"),
        # Director review repair (2026-10-28): the keep bound is
        # 2000, aligned with the Nursery detail bound, so a 1000
        # bound made re-export of legitimately-kept ideas fail.
        # Imported Keeps are additionally preserved verbatim in
        # the exchange_seeds payload store (completion-order
        # residual repair) — export never re-derives them from
        # the rendered detail.
        "keep": _str(seed["keep"], 2000, "seed.keep"),
    }
    if not seed["label"]:
        raise ExchangeError("seed.label must be non-empty")
    man = data["manifest"]
    if not isinstance(man, dict) \
            or not _MANIFEST_KEYS <= set(man.keys()) \
            <= _MANIFEST_KEYS | {"provenance"}:
        raise ExchangeError("manifest keys mismatch")
    reqs = man["requirements"]
    if not isinstance(reqs, list) or len(reqs) > 8 or any(
            not isinstance(x, str) or len(x) > 120 for x in reqs):
        raise ExchangeError("manifest.requirements out of bounds")
    man = {
        "author_origin": _str(man["author_origin"], 200,
                              "manifest.author_origin"),
        "created": _str(man["created"], 32, "manifest.created"),
        "registry": _str(man["registry"], 40, "manifest.registry"),
        "requirements": list(reqs),
    }
    if "provenance" in data["manifest"]:
        prov = data["manifest"]["provenance"]
        if prov not in _PROVENANCE_VALUES:
            raise ExchangeError("manifest.provenance invalid")
        man["provenance"] = prov
    if not man["author_origin"]:
        raise ExchangeError("manifest.author_origin must be non-empty")
    receipts = data["receipts"]
    if not isinstance(receipts, list) or len(receipts) > MAX_RECEIPTS:
        raise ExchangeError("receipts out of bounds")
    receipts = [_validate_receipt(r) for r in receipts]
    return {"version": PACKET_VERSION, "seed": seed,
            "manifest": man, "receipts": receipts}


def lint_packet(packet: Dict[str, Any]) -> Dict[str, Any]:
    """Chain lint: precise labels for missing links, plus the
    replication count. Never a bare pass/fail, never a score."""
    labels: List[str] = []
    receipts = packet["receipts"]
    if not receipts:
        labels.append("no receipts")
    field_absent = {"guess": "guess absent",
                    "test_method": "method absent",
                    "result": "result absent",
                    "mirror": "mirror absent",
                    "outcome": "outcome absent"}
    for i, r in enumerate(receipts, 1):
        for field, label in field_absent.items():
            if not r[field].strip():
                labels.append(f"receipt {i}: {label}")
    distinct = len({r["origin"] for r in receipts})
    return {
        "labels": labels,
        "complete": not labels,
        "receipts": len(receipts),
        "distinct_origins": distinct,
    }


def build_packet(program: Any, pid: str, *, chain=None,
                 receipts=None,
                 requirements=None) -> Dict[str, Any]:
    """Assemble a packet for one of the program's proposals.

    For an IMPORTED proposal the seed and manifest come from
    the stored original payload (record_seed_payload) — never
    from the proposal's rendered detail — so re-export is
    byte-identical to what was imported. For a native proposal
    the seed is the proposal itself (keep = detail or words).

    Overrides are explicit: passing chain / receipts /
    requirements replaces the corresponding field deliberately;
    leaving one as None inherits the stored original (imported)
    or the native default. There is no silent default that
    erases an import."""
    prop = program.nursery.proposals.get(pid)
    if prop is None:
        raise ExchangeError(f"unknown proposal {pid}")
    stored = seed_payload_for(program, pid)
    if stored is None and (prop.origin or "").startswith("exchange:"):
        # DAF-06: an exchange import without its original seed
        # record is a damaged/partial import, not a native
        # proposal — never let it export as a reconstruction.
        raise ExchangeError(
            f"proposal {pid} is an exchange import without its "
            "original seed record (incomplete import); export refused")
    if receipts is None:
        current = receipts_for(program, pid)
        if stored is not None and "receipts_expected" in stored:
            # DAF-04: the import stamped its receipt provenance
            # on the seed record; an export whose inherited
            # receipts no longer match it is incomplete and must
            # refuse rather than present a truncated chain as
            # complete. (An explicit receipts override is a
            # deliberate caller act and is not checked.)
            cur = [{k: e[k] for k in RECEIPT_KEYS} for e in current]
            if len(cur) != stored["receipts_expected"] \
                    or _receipts_digest(cur) != stored["receipts_hash"]:
                raise ExchangeError(
                    f"receipt provenance incomplete for {pid}: "
                    f"expected {stored['receipts_expected']} "
                    f"receipt(s), present {len(cur)}; export refused")
        receipts = [
            {k: e[k] for k in RECEIPT_KEYS}
            for e in current]
    if stored is not None:
        seed = {
            "label": stored["label"],
            "chain": stored["chain"] if chain is None else chain,
            "keep": stored["keep"],
        }
        manifest = {
            "author_origin": stored["author_origin"],
            "created": stored["created"],
            "registry": stored["registry"],
            "requirements": (list(stored["requirements"])
                             if requirements is None
                             else list(requirements)),
            # AF-3: the seed came from the stored original
            # payload — say so on the packet itself.
            "provenance": "original",
        }
    else:
        seed = {
            "label": prop.label,
            "chain": "" if chain is None else chain,
            "keep": prop.detail or prop.words,
        }
        manifest = {
            "author_origin": prop.origin or f"host:{program.owner}",
            "created": time.strftime(
                "%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "registry": REGISTRY_STAMP,
            "requirements": (list(requirements)
                             if requirements is not None else []),
            # AF-3: no stored original exists for this proposal;
            # the seed is the native/rendered source. Label it
            # reconstructed — never let it pass as an original.
            "provenance": "reconstructed",
        }
    packet = {
        "version": PACKET_VERSION,
        "seed": seed,
        "manifest": manifest,
        "receipts": list(receipts),
    }
    return validate_packet(packet)


def write_packet(packet: Dict[str, Any], path: str) -> None:
    packet = validate_packet(packet)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(packet, f, indent=2, ensure_ascii=False)


def read_packet(path: str) -> Dict[str, Any]:
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        raise ExchangeError(f"packet unreadable: {type(e).__name__}")
    return validate_packet(data)


def _preflight_import(program: Any, packet: Dict[str, Any]) -> None:
    """DAF-04/DAF-06: refuse an import BEFORE any mutation when
    landing it would break a live proposal's provenance.

    Seeds: the landing always records one seed payload; at cap
    with no non-live victim, record_seed_payload would fail
    closed AFTER the proposal landed (the DAF-06 partial
    import) — refuse here instead, with the same error.
    Receipts: bounded admission/backpressure — if the incoming
    receipts would force eviction (oldest-first) of any receipt
    belonging to a live Nursery proposal, refuse here. Evicting
    only non-live proposals' receipts stays permitted and
    counted, exactly as the direct writers behave."""
    live = getattr(program.nursery, "proposals", {}) or {}
    seeds = getattr(program, "exchange_seeds", None) or {}
    if len(seeds) >= _MAX_SEED_ENTRIES and not any(
            isinstance(e, dict) and e.get("pid") not in live
            for e in seeds.values()):
        raise ExchangeError(
            "exchange_seeds is full and every retained "
            "payload belongs to a live proposal; refusing "
            "to evict a live original")
    need = len(packet["receipts"])
    entries = getattr(program, "exchange_receipts", None) or {}
    overflow = len(entries) + need - _MAX_RECEIPT_ENTRIES
    if overflow > 0:
        # Would-be victims under the shared oldest-first policy
        # (ts, then insertion order — session_section.oldest_key).
        indexed = list(enumerate(entries.values()))
        indexed.sort(key=lambda iv: (str(iv[1].get("ts", "")), iv[0]))
        victims = [e for _, e in indexed[:overflow]]
        if any(e.get("pid") in live for e in victims):
            raise ExchangeError(
                "exchange_receipts capacity: importing "
                f"{need} receipt(s) would evict receipt(s) of a "
                "live proposal; import refused before mutation "
                "(bounded admission)")


# ----------------------- import transaction journal (DAF-06, step 5b)
# An import spans TWO durable files (the nursery file, written by
# nursery.add at landing, and the program file, written by the one
# final save) with no shared atomicity. The bridge is recorded
# intent: a journal written BEFORE landing, retained until the
# transaction is proven complete or proven compensated, and
# resolved at load by recover_exchange_import — never by inferred
# visibility (the GDP_R3 recovery law). One journal per owner: an
# unresolved journal refuses the next import (fail closed).

_IMPORT_JOURNAL_VERSION = 1


def _import_journal_path(owner: str) -> str:
    from form.persist import _safe_owner
    state = os.path.join(os.path.dirname(__file__), "..", "state")
    return os.path.join(
        state, f"exchange_import_{_safe_owner(owner)}.journal.json")


def _write_import_journal(owner: str, journal: Dict[str, Any]) -> None:
    from form.dell_matrix.atomic_write import atomic_write_json
    atomic_write_json(_import_journal_path(owner), journal)


def _read_import_journal(owner: str) -> Any:
    """The retained import journal for owner, or None. A present
    but unreadable/malformed journal raises ExchangeError — the
    evidence is preserved, never silently dropped."""
    path = _import_journal_path(owner)
    if not os.path.isfile(path):
        return None
    try:
        with open(path, encoding="utf-8") as f:
            journal = json.load(f)
    except Exception as e:
        raise ExchangeError(
            f"exchange import journal for {owner} is unreadable "
            f"({type(e).__name__}); recovery evidence preserved",
            details={"stage": "journal_read", "journal_retained": True}
        ) from e
    if not isinstance(journal, dict) \
            or journal.get("kind") != "exchange_import" \
            or journal.get("version") != _IMPORT_JOURNAL_VERSION \
            or journal.get("owner") != owner:
        raise ExchangeError(
            f"exchange import journal for {owner} is malformed; "
            "recovery evidence preserved",
            details={"stage": "journal_read", "journal_retained": True})
    return journal


def _clear_import_journal(owner: str) -> bool:
    try:
        os.remove(_import_journal_path(owner))
        return True
    except OSError:
        return False


def _mark_journal_incomplete(owner: str, journal: Dict[str, Any],
                             stage: str, cause: BaseException,
                             compensation_errors: List[str]) -> None:
    """Retain the journal as compensation_incomplete evidence.
    Best-effort: if even this write fails, the in-progress journal
    already on disk still identifies the transaction."""
    journal["status"] = "compensation_incomplete"
    journal["failure"] = {
        "stage": stage,
        "error": f"{type(cause).__name__}: {cause}"[:300],
        "compensation_errors": list(compensation_errors)[:6],
    }
    try:
        _write_import_journal(owner, journal)
    except Exception:
        pass


def _raw_state_files(owner: str) -> Tuple[Any, Any]:
    """(nursery_raw, program_raw) parsed from the canonical files;
    a missing file reads as {} and a malformed one raises — a
    durability verdict is never taken from unreadable state."""
    from form.persist import _path
    from form.dell_matrix.nursery import owner_nursery_path
    raws = []
    for path in (owner_nursery_path(owner), _path(owner)):
        if not os.path.isfile(path):
            raws.append({})
            continue
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ExchangeError(f"durable state file {path} is not "
                                "an object; cannot verify import state")
        raws.append(data)
    return raws[0], raws[1]


def _section_entries(program_raw: Any, section: str) -> Dict[str, Any]:
    raw = program_raw.get(section)
    if not isinstance(raw, dict):
        return {}
    entries = raw.get("entries")
    return entries if isinstance(entries, dict) else {}


def _durable_import_state(owner: str, pid: str) -> Dict[str, Any]:
    """What the canonical files actually hold for one import:
    proposal presence (nursery file) and seed/receipt entries
    (program file). This — not a save call returning — is the
    durability evidence compensation is judged by."""
    nursery_raw, program_raw = _raw_state_files(owner)
    from form.dell_matrix.nursery import DISPOSITION_SECTION_KEY
    proposals = {k: v for k, v in nursery_raw.items()
                 if k != DISPOSITION_SECTION_KEY
                 and isinstance(v, dict)}
    seeds = [e for e in _section_entries(program_raw,
                                         "exchange_seeds").values()
             if isinstance(e, dict) and e.get("pid") == pid]
    receipts = [e for e in _section_entries(
        program_raw, "exchange_receipts").values()
        if isinstance(e, dict) and e.get("pid") == pid]
    return {"proposal_present": pid in proposals,
            "seed_present": bool(seeds),
            "receipts_count": len(receipts)}


def _compensate_import(program: Any, pid: str) -> Tuple[bool, List[str]]:
    """Roll a landed import back and PROVE the rollback durable.

    Removes the proposal and this import's receipt/seed entries
    in memory, persists through BOTH save boundaries, then judges
    completeness by re-reading the canonical files: complete only
    when the durable state holds no trace of the import. Save
    errors are collected, never suppressed. (Evictions of
    non-live records performed during recording remain real,
    counted losses — the step 5 contract.)"""
    errors: List[str] = []
    for attr in ("exchange_receipts", "exchange_seeds"):
        entries = getattr(program, attr, None)
        if isinstance(entries, dict):
            for k in [k for k, e in entries.items()
                      if isinstance(e, dict) and e.get("pid") == pid]:
                del entries[k]
    program.nursery.proposals.pop(pid, None)
    try:
        program.nursery.save()
    except Exception as e:
        errors.append(f"nursery.save: {type(e).__name__}")
    try:
        program.save()
    except Exception as e:
        errors.append(f"program.save: {type(e).__name__}")
    try:
        st = _durable_import_state(program.owner, pid)
        complete = not st["proposal_present"] \
            and not st["seed_present"] and st["receipts_count"] == 0
    except Exception as e:
        errors.append(f"verify: {type(e).__name__}")
        complete = False
    return complete, errors


def _dispose_import_journal(owner: str, outcome: str) -> None:
    """Dispose of the import journal after a recovery outcome, or
    raise: disposal is a SEPARATE fact from the outcome itself
    (DIR-F12). A failed unlink never reads as successful disposal
    — the journal is recovery evidence, retained on disk, and the
    caller fails closed so a later load can retry disposal."""
    if _clear_import_journal(owner):
        return
    raise ExchangeError(
        "exchange import recovery established "
        f"'{outcome}' but the import journal could not be "
        "cleared; recovery evidence retained for retry",
        details={"stage": "recovery", "journal_retained": True,
                 "recovery_outcome": outcome})


def _fail_import(program: Any, journal: Dict[str, Any], pid: str,
                 stage: str, cause: BaseException) -> ExchangeError:
    """Compensate a failed import and build the honest error:
    compensation status and journal retention are part of the
    result, never swallowed. Compensation completeness and
    journal disposal are SEPARATE facts (DIR-F12): verified
    compensation stays "complete" when true, and journal_retained
    reports the actual outcome of the disposal attempt."""
    complete, errors = _compensate_import(program, pid)
    if complete:
        cleared = _clear_import_journal(program.owner)
    else:
        cleared = False
        _mark_journal_incomplete(program.owner, journal, stage,
                                 cause, errors)
    retained = not cleared
    details = {"stage": stage,
               "compensation": "complete" if complete else "incomplete",
               "journal_retained": retained,
               "journal_disposal": "cleared" if cleared else "retained",
               "compensation_errors": errors}
    return ExchangeError(
        f"exchange import failed at {stage}: "
        f"{type(cause).__name__}: {cause} "
        f"(compensation {details['compensation']}"
        f"{'; journal retained' if retained else ''})",
        details=details)


def recover_exchange_import(owner: str) -> str:
    """Load-boundary recovery for a retained import journal.

    Called by persist_rest.load before the loaded state is
    exposed (with the other recorded-intent recoveries). No
    journal -> "none". A journal whose import is durably COMPLETE
    (proposal + seed payload + receipt provenance all present and
    matching the journal) had committed before the interruption:
    clear the journal, change nothing ("completed"). Any other
    journaled import is partial or aborted: remove its proposal
    and exchange entries from the canonical files, verify by
    re-reading, then clear the journal ("removed" /
    "already_absent"). Malformed evidence, an ambiguous target,
    or a failed write/verify raises — state is not exposed over
    unresolved recovery evidence. Unjournaled state is never
    touched (recorded-intent law)."""
    journal = _read_import_journal(owner)
    if journal is None:
        return "none"
    from form.persist import _path
    from form.dell_matrix.nursery import (
        DISPOSITION_SECTION_KEY, owner_nursery_path)
    from form.dell_matrix.atomic_write import atomic_write_json

    nursery_raw, program_raw = _raw_state_files(owner)
    proposals = {k: v for k, v in nursery_raw.items()
                 if k != DISPOSITION_SECTION_KEY
                 and isinstance(v, dict)}
    pid = journal.get("pid")
    if pid is None:
        cands = [k for k, v in proposals.items()
                 if v.get("label") == journal.get("label")
                 and v.get("origin") == journal.get("origin")
                 and hashlib.sha256(
                     str(v.get("detail", "")).encode("utf-8")
                 ).hexdigest() == journal.get("detail_sha256")]
        if len(cands) > 1:
            raise ExchangeError(
                "exchange import recovery: multiple proposals match "
                "the journaled intent; refusing to guess",
                details={"stage": "recovery", "journal_retained": True})
        pid = cands[0] if cands else None

    if pid is not None \
            and journal.get("status") != "compensation_incomplete":
        seed = next((e for e in _section_entries(
            program_raw, "exchange_seeds").values()
            if isinstance(e, dict) and e.get("pid") == pid), None)
        receipts = [{k: e[k] for k in RECEIPT_KEYS}
                    for e in _section_entries(
                        program_raw, "exchange_receipts").values()
                    if isinstance(e, dict) and e.get("pid") == pid
                    and all(k in e for k in RECEIPT_KEYS)]
        js, jm = journal["seed"], journal["manifest"]
        complete = pid in proposals and seed is not None \
            and all(seed.get(k) == js[k]
                    for k in ("label", "chain", "keep")) \
            and all(seed.get(k) == jm[k] for k in
                    ("author_origin", "created", "registry")) \
            and list(seed.get("requirements") or []) \
            == list(jm["requirements"]) \
            and seed.get("receipts_expected") \
            == journal["receipts_expected"] \
            and seed.get("receipts_hash") == journal["receipts_hash"] \
            and len(receipts) == journal["receipts_expected"] \
            and _receipts_digest(receipts) == journal["receipts_hash"]
        if complete:
            _dispose_import_journal(owner, "completed")
            return "completed"

    if pid is None:
        _dispose_import_journal(owner, "no_target")
        return "no_target"
    st = _durable_import_state(owner, pid)
    if not st["proposal_present"] and not st["seed_present"] \
            and st["receipts_count"] == 0:
        _dispose_import_journal(owner, "already_absent")
        return "already_absent"
    if pid in nursery_raw:
        del nursery_raw[pid]
        atomic_write_json(owner_nursery_path(owner), nursery_raw)
    touched = False
    for section in ("exchange_receipts", "exchange_seeds"):
        entries = _section_entries(program_raw, section)
        for k in [k for k, e in entries.items()
                  if isinstance(e, dict) and e.get("pid") == pid]:
            del entries[k]
            touched = True
    if touched:
        atomic_write_json(_path(owner), program_raw)
    st = _durable_import_state(owner, pid)
    if st["proposal_present"] or st["seed_present"] \
            or st["receipts_count"]:
        raise ExchangeError(
            "exchange import recovery could not establish removal "
            f"of partial import {pid}; evidence retained",
            details={"stage": "recovery", "journal_retained": True})
    _dispose_import_journal(owner, "removed")
    return "removed"


def import_packet(program: Any, packet: Dict[str, Any]) -> Dict[str, Any]:
    """Land a foreign packet as a PENDING proposal in the
    receiver's nursery. Never confirms, never makes eligible.
    Packet text is screened against the receiver's protected
    values first (the dock's import discipline)."""
    packet = validate_packet(packet)
    from form.dell_matrix import inference_dock as _dock
    protected = _dock.protected_values(program)
    if protected:
        blob = json.dumps(packet, ensure_ascii=False)
        for val in protected:
            if val and val in blob:
                return {"ok": False, "reason": "protected_material",
                        "detail": "Packet text carries receiver-"
                                  "protected material; refused."}
    # DAF-04/DAF-06 preflight: capacity and provenance capacity
    # across every owner the landing will touch, BEFORE the
    # durable nursery landing. A refusal here mutates nothing.
    _preflight_import(program, packet)
    lint = lint_packet(packet)
    seed, man = packet["seed"], packet["manifest"]
    origin = f"exchange:{man['author_origin']}"[:120]
    lint_text = "; ".join(lint["labels"]) if lint["labels"] \
        else "chain complete"
    reason = (
        f"exchange import from {man['author_origin']} · "
        f"replication: {lint['receipts']} receipt(s), "
        f"{lint['distinct_origins']} distinct origin(s) · "
        f"lint: {lint_text}")[:160]
    detail_lines = [f"KEEP: {seed['keep']}"]
    if seed["chain"]:
        detail_lines.append(f"SEED CHAIN: {seed['chain']}")
    for i, r in enumerate(packet["receipts"], 1):
        detail_lines.append(
            f"RECEIPT {i} ({r['origin']}): guess: {r['guess']} · "
            f"method: {r['test_method']} · result: {r['result']} · "
            f"mirror: {r['mirror']} · outcome: {r['outcome']}")
    # DAF-06 (step 5b): the landing below is a transaction across
    # two durable files. Record intent in the import journal
    # BEFORE landing; an unresolved journal from an earlier import
    # refuses this one (fail closed until a load/restart recovery
    # resolves the evidence).
    detail_text = "\n".join(detail_lines)[:2000]
    owner = program.owner
    if _read_import_journal(owner) is not None:
        raise ExchangeError(
            "unresolved exchange import recovery evidence for "
            f"{owner}; load/restart recovery must resolve it "
            "before another import",
            details={"stage": "journal", "journal_retained": True})
    journal: Dict[str, Any] = {
        "version": _IMPORT_JOURNAL_VERSION,
        "kind": "exchange_import",
        "owner": owner,
        "import_id": uuid.uuid4().hex,
        "phase": "intent",
        "status": "in_progress",
        "pid": None,
        "label": seed["label"],
        "origin": origin,
        "detail_sha256": hashlib.sha256(
            detail_text.encode("utf-8")).hexdigest(),
        "seed": {"label": seed["label"], "chain": seed["chain"],
                 "keep": seed["keep"]},
        "manifest": {"author_origin": man["author_origin"],
                     "created": man["created"],
                     "registry": man["registry"],
                     "requirements": list(man["requirements"])},
        "receipts_expected": len(packet["receipts"]),
        "receipts_hash": _receipts_digest(packet["receipts"]),
    }
    try:
        _write_import_journal(owner, journal)
    except Exception as e:
        raise ExchangeError(
            f"exchange import journal could not be written: "
            f"{type(e).__name__}; import refused before landing",
            details={"stage": "journal"}) from e
    try:
        prop = program.nursery.add(
            seed["label"], words=seed["keep"][:240], origin=origin,
            reason=reason, detail=detail_text,
            goals=[f"replication {lint['receipts']}x/"
                   f"{lint['distinct_origins']} origins"])
    except Exception as e:
        # DIR-F12: disposal is a separate fact — if the journal
        # cannot be cleared, its retention must surface, not hide
        # behind the landing failure.
        if not _clear_import_journal(owner):
            raise ExchangeError(
                "exchange import landing failed and the import "
                "journal could not be cleared; recovery evidence "
                f"retained ({type(e).__name__}: {e})",
                details={"stage": "journal_clear",
                         "journal_retained": True}) from e
        raise
    journal["pid"] = prop.id
    journal["phase"] = "landed"
    try:
        _write_import_journal(owner, journal)
    except Exception as e:
        raise _fail_import(program, journal, prop.id,
                           "journal_update", e) from e
    try:
        # Director review repair (2026-10-28): PRESERVE the packet's
        # receipts as first-class records in the receiver's receipts
        # section, under the imported proposal. Before this, receipts
        # existed only as text inside the bounded detail rendering —
        # silently truncated there, absent from receipts_for, and
        # missing from any re-export. Recording uses the canonical
        # record_receipt path (each receipt keeps its own origin —
        # provenance is never rewritten to the receiver).
        try:
            for r in packet["receipts"]:
                record_receipt(program, prop.id, r, _defer_save=True)
        except Exception as e:
            raise ExchangeError(
                f"import landed proposal {prop.id} but receipt "
                f"recording failed: {type(e).__name__}") from e
        # Director completion order residual repair (2026-10-28):
        # preserve the packet's ORIGINAL seed payload + declared
        # requirements as durable data under the imported proposal.
        # The detail above is only a rendering of it; export reads
        # this record, so the seed survives re-export byte-exact.
        try:
            record_seed_payload(program, prop.id, packet,
                                _defer_save=True)
        except Exception as e:
            raise ExchangeError(
                f"import landed proposal {prop.id} but seed payload "
                f"recording failed: {type(e).__name__}") from e
    except Exception as e:
        # DAF-06 (step 5b): a post-landing failure must not leave a
        # durable partial import, and the rollback itself must be
        # proven, not assumed — compensate across every owner this
        # import touched and report the compensation state in the
        # error's details; incomplete compensation retains the
        # journal for load-boundary recovery.
        raise _fail_import(program, journal, prop.id,
                           "record", e) from e
    # AF-6: the writers above deferred their per-record saves;
    # this boundary save carries the whole import's durability
    # (one full save per import). Step 5b: a failure here is an
    # import failure — never ordinary success.
    try:
        program.save()
    except Exception as e:
        raise _fail_import(program, journal, prop.id,
                           "final_save", e) from e
    # DIR-F12: the landing is durably complete at this point, so
    # a failed journal disposal must NOT convert success into a
    # failure (or trigger compensation of a complete import) —
    # but it is a separate fact and is reported as such; the
    # retained journal is resolved by load-boundary recovery.
    cleared = _clear_import_journal(owner)
    return {"ok": True, "pid": prop.id, "lint": lint,
            "origin": origin, "journal_retained": not cleared}


# --------------------------------------- recorded receipts section

def _validate_receipt_entry(entry: Any, owner: str
                            ) -> Tuple[bool, str]:
    if not isinstance(entry, dict):
        return False, "entry not an object"
    if set(entry.keys()) != _RECEIPT_ENTRY_KEYS:
        return False, "entry keys mismatch"
    if entry["owner"] != owner:
        return False, "entry owner mismatch"
    for k, limit in (("entry_id", 64), ("ts", 32), ("pid", 120),
                     ("origin", 200), ("guess", 500),
                     ("test_method", 1000), ("result", 1000),
                     ("mirror", 1000), ("outcome", 500)):
        v = entry[k]
        if not isinstance(v, str) or len(v) > limit:
            return False, f"{k} invalid"
    if not entry["entry_id"] or not entry["pid"] \
            or not entry["origin"]:
        return False, "entry identity fields must be non-empty"
    return True, ""


def validate_receipts_section(raw: Any, owner: str):
    """Validate a persisted exchange_receipts section. Never
    raises."""
    return validate_records_section(
        raw, version=EXCHANGE_RECEIPTS_SECTION_VERSION,
        kind="entries",
        validate_rec=lambda rec: _validate_receipt_entry(rec, owner),
        id_field="entry_id", max_keep=_MAX_RECEIPT_ENTRIES,
        sort_field="ts", key_not_string="entry key not a string",
        mismatch="entry key/ID mismatch")


def serialize_receipts_section(entries: Any, malformed: Any,
                               owner: str,
                               extra: Any = None) -> Dict[str, Any]:
    """Serialize recorded receipts with the strict schema. Never
    raises."""
    return serialize_records_section(
        entries, malformed,
        version=EXCHANGE_RECEIPTS_SECTION_VERSION, kind="entries",
        validate_rec=lambda rec: _validate_receipt_entry(rec, owner),
        id_field="entry_id", max_keep=_MAX_RECEIPT_ENTRIES,
        sort_field="ts", key_not_string="entry key not a string",
        mismatch="not serialized as valid: key/ID mismatch",
        extra=extra)


_MISSING = MISSING


def record_receipt(program: Any, pid: str, receipt: Dict[str, str],
                   _defer_save: bool = False) -> Dict[str, Any]:
    """Record one run's receipt against a proposal, at the time
    the run happens. Persisted (best-effort save, mirroring dock
    evidence discipline). `_defer_save` is private: only a host
    that owns the save boundary (import_packet) may defer, and
    that host saves once at its end (AF-6)."""
    if pid not in program.nursery.proposals:
        raise ExchangeError(f"unknown proposal {pid}")
    r = _validate_receipt(receipt)
    entry = {
        "entry_id": uuid.uuid4().hex,
        "owner": program.owner,
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "pid": pid,
        **r,
    }
    entries = getattr(program, "exchange_receipts", None)
    if entries is None:
        entries = {}
        program.exchange_receipts = entries
    entries[entry["entry_id"]] = entry
    while len(entries) > _MAX_RECEIPT_ENTRIES:
        entries.pop(_oldest_key(entries))
        _bump_dropped(program, "exchange_receipts_dropped_total")
    if not _defer_save:
        try:
            program.save()
        except Exception:
            pass
    return entry


def receipts_for(program: Any, pid: str) -> List[Dict[str, Any]]:
    out = [e for e in (getattr(program, "exchange_receipts", None)
                       or {}).values() if e.get("pid") == pid]
    out.sort(key=lambda e: e.get("ts", ""))
    return out


# --------------------------------- imported seed payload section
# The original seed + manifest of an imported packet, preserved
# verbatim as durable data (Director completion order residual
# repair). One record per imported proposal. The Nursery detail
# is a rendering OF this record, never its source.

_SEED_ENTRY_KEYS = frozenset({
    "entry_id", "owner", "ts", "pid", "label", "chain", "keep",
    "author_origin", "created", "registry", "requirements"})
# DAF-04: receipt provenance (expected count + multiset digest)
# is an OPTIONAL pair on the seed entry — legacy entries without
# it stay valid and simply carry no provenance claim.
_SEED_PROVENANCE_KEYS = frozenset({"receipts_expected", "receipts_hash"})

EXCHANGE_SEEDS_SECTION_VERSION = 1
_MAX_SEED_ENTRIES = 200


def _validate_seed_entry(entry: Any, owner: str
                         ) -> Tuple[bool, str]:
    if not isinstance(entry, dict):
        return False, "entry not an object"
    if not _SEED_ENTRY_KEYS <= set(entry.keys()) \
            <= _SEED_ENTRY_KEYS | _SEED_PROVENANCE_KEYS:
        return False, "entry keys mismatch"
    if ("receipts_expected" in entry) != ("receipts_hash" in entry):
        return False, "receipt provenance keys must appear as a pair"
    if "receipts_expected" in entry:
        exp = entry["receipts_expected"]
        if not isinstance(exp, int) or isinstance(exp, bool) \
                or not 0 <= exp <= MAX_RECEIPTS:
            return False, "receipts_expected invalid"
        h = entry["receipts_hash"]
        if not isinstance(h, str) or len(h) != 64:
            return False, "receipts_hash invalid"
    if entry["owner"] != owner:
        return False, "entry owner mismatch"
    for k, limit in (("entry_id", 64), ("ts", 32), ("pid", 120),
                     ("label", 120), ("chain", 4000),
                     ("keep", 2000), ("author_origin", 200),
                     ("created", 32), ("registry", 40)):
        v = entry[k]
        if not isinstance(v, str) or len(v) > limit:
            return False, f"{k} invalid"
    if not entry["entry_id"] or not entry["pid"] \
            or not entry["label"] or not entry["author_origin"]:
        return False, "entry identity fields must be non-empty"
    reqs = entry["requirements"]
    if not isinstance(reqs, list) or len(reqs) > 8 or any(
            not isinstance(x, str) or len(x) > 120 for x in reqs):
        return False, "requirements invalid"
    return True, ""


def validate_seeds_section(raw: Any, owner: str):
    """Validate a persisted exchange_seeds section. Never
    raises."""
    return validate_records_section(
        raw, version=EXCHANGE_SEEDS_SECTION_VERSION,
        kind="entries",
        validate_rec=lambda rec: _validate_seed_entry(rec, owner),
        id_field="entry_id", max_keep=_MAX_SEED_ENTRIES,
        sort_field="ts", key_not_string="entry key not a string",
        mismatch="entry key/ID mismatch")


def serialize_seeds_section(entries: Any, malformed: Any,
                            owner: str,
                            extra: Any = None) -> Dict[str, Any]:
    """Serialize imported seed payloads with the strict schema.
    Never raises."""
    return serialize_records_section(
        entries, malformed,
        version=EXCHANGE_SEEDS_SECTION_VERSION, kind="entries",
        validate_rec=lambda rec: _validate_seed_entry(rec, owner),
        id_field="entry_id", max_keep=_MAX_SEED_ENTRIES,
        sort_field="ts", key_not_string="entry key not a string",
        mismatch="not serialized as valid: key/ID mismatch",
        extra=extra)


def record_seed_payload(program: Any, pid: str,
                        packet: Dict[str, Any],
                        _defer_save: bool = False) -> Dict[str, Any]:
    """Preserve an imported packet's original seed + manifest
    under the landed proposal. `packet` must already be
    validated (import_packet validates at the boundary).
    Persisted (best-effort save, the receipts discipline).
    `_defer_save`: same private boundary rule as
    record_receipt (AF-6)."""
    if pid not in program.nursery.proposals:
        raise ExchangeError(f"unknown proposal {pid}")
    seed, man = packet["seed"], packet["manifest"]
    entry = {
        "entry_id": uuid.uuid4().hex,
        "owner": program.owner,
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "pid": pid,
        "label": seed["label"],
        "chain": seed["chain"],
        "keep": seed["keep"],
        "author_origin": man["author_origin"],
        "created": man["created"],
        "registry": man["registry"],
        "requirements": list(man["requirements"]),
        # DAF-04: stamp the packet's receipt provenance on the
        # durable seed record, so a later export can substantiate
        # (or refuse) the proposal's receipt completeness.
        "receipts_expected": len(packet["receipts"]),
        "receipts_hash": _receipts_digest(packet["receipts"]),
    }
    ok, why = _validate_seed_entry(entry, program.owner)
    if not ok:
        raise ExchangeError(f"seed payload invalid: {why}")
    entries = getattr(program, "exchange_seeds", None)
    if entries is None:
        entries = {}
        program.exchange_seeds = entries
    entries[entry["entry_id"]] = entry
    while len(entries) > _MAX_SEED_ENTRIES:
        # AF-3: a payload whose proposal is still live in the
        # Nursery is the ONLY original that proposal's export
        # can reproduce — evicting it silently degraded every
        # later re-export. Evict only payloads whose proposal
        # has left the Nursery (oldest first); if every retained
        # payload is live, fail closed and store nothing new.
        live = getattr(program.nursery, "proposals", {}) or {}
        # DAF-05: the victim is the OLDEST non-live payload under
        # the shared policy (oldest ts; ties by insertion order)
        # — never the raw dict-first entry, whose identity flips
        # with load order.
        cands = [(k, e) for k, e in entries.items()
                 if e.get("pid") not in live]
        if cands:
            min_ts = min(str(e.get("ts", "")) for _, e in cands)
            victim = next(k for k, e in cands
                          if str(e.get("ts", "")) == min_ts)
        else:
            victim = None
        if victim is None:
            del entries[entry["entry_id"]]
            raise ExchangeError(
                "exchange_seeds is full and every retained "
                "payload belongs to a live proposal; refusing "
                "to evict a live original")
        entries.pop(victim)
        _bump_dropped(program, "exchange_seeds_dropped_total")
    if not _defer_save:
        try:
            program.save()
        except Exception:
            pass
    return entry


def seed_payload_for(program: Any, pid: str
                     ) -> Any:
    """The stored original payload for an imported proposal,
    or None for a native proposal (or a pre-repair import,
    whose original payload no longer exists — export then
    falls back to the legacy detail rendering, as before)."""
    best = None
    for e in (getattr(program, "exchange_seeds", None)
              or {}).values():
        if e.get("pid") == pid:
            if best is None or (e.get("ts") or "") >= \
                    (best.get("ts") or ""):
                best = e
    return best
