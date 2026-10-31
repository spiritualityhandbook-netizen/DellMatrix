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

import json
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
    """A packet or receipt failed validation at the boundary."""


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
    if receipts is None:
        receipts = [
            {k: e[k] for k in RECEIPT_KEYS}
            for e in receipts_for(program, pid)]
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
    prop = program.nursery.add(
        seed["label"], words=seed["keep"][:240], origin=origin,
        reason=reason, detail="\n".join(detail_lines)[:2000],
        goals=[f"replication {lint['receipts']}x/"
               f"{lint['distinct_origins']} origins"])
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
            record_receipt(program, prop.id, r)
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
        record_seed_payload(program, prop.id, packet)
    except Exception as e:
        raise ExchangeError(
            f"import landed proposal {prop.id} but seed payload "
            f"recording failed: {type(e).__name__}") from e
    return {"ok": True, "pid": prop.id, "lint": lint,
            "origin": origin}


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


def record_receipt(program: Any, pid: str, receipt: Dict[str, str]
                   ) -> Dict[str, Any]:
    """Record one run's receipt against a proposal, at the time
    the run happens. Persisted (best-effort save, mirroring dock
    evidence discipline)."""
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
        entries.pop(next(iter(entries)))
        _bump_dropped(program, "exchange_receipts_dropped_total")
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

EXCHANGE_SEEDS_SECTION_VERSION = 1
_MAX_SEED_ENTRIES = 200


def _validate_seed_entry(entry: Any, owner: str
                         ) -> Tuple[bool, str]:
    if not isinstance(entry, dict):
        return False, "entry not an object"
    if set(entry.keys()) != _SEED_ENTRY_KEYS:
        return False, "entry keys mismatch"
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
                        packet: Dict[str, Any]) -> Dict[str, Any]:
    """Preserve an imported packet's original seed + manifest
    under the landed proposal. `packet` must already be
    validated (import_packet validates at the boundary).
    Persisted (best-effort save, the receipts discipline)."""
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
        victim = next(
            (k for k, e in entries.items()
             if e.get("pid") not in live),
            None)
        if victim is None:
            del entries[entry["entry_id"]]
            raise ExchangeError(
                "exchange_seeds is full and every retained "
                "payload belongs to a live proposal; refusing "
                "to evict a live original")
        entries.pop(victim)
        _bump_dropped(program, "exchange_seeds_dropped_total")
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
