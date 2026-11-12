#!/usr/bin/env python3
"""LM-1 EXTERNAL IMPORT — build-time-only importer (Wikipedia roots).

Authority chain (all on record in director-reports/):

  Ace license ruling 2026-11-11 (LM1_LICENSE_RULING_ACE_2026-11-11.md,
  PR #390, merged 49b81dd): the import is approved, with attribution.
  Boundary (LM1_IMPORT_LICENSE_BOUNDARY_2026-11-11.md, PR #391,
  merged 610fb13): provenance pins, four-place attribution,
  collection-vs-adaptation decision, lineage/distribution rules.
  Design (LM1_IMPORT_EXECUTION_DESIGN_2026-11-11.md, PR #392,
  merged 4e556c4; corrected per Director mail 1a1cd5cf024ee08e).
  Director GO: mail 1a1cd7d53c3ec395 (conditional code-circuit GO;
  conditions fulfilled 2026-11-11 when PR #391 merged as 610fb13).

This tool is BUILD-TIME ONLY (same pattern as form/lm1_harvest.py):
no runtime module imports it. It fetches the 24 pinned letter pages
of "List of Greek and Latin roots in English" (English Wikipedia)
via the MediaWiki API and emits:

  form/mandell/lm_table_v2.json             the v2 table
  form/mandell/lm_table_v2.collisions.json  the v2 collision log

lm_table_v1.json is read (its rows are carried over verbatim) and
NEVER written. The v2 table's external rows form ONE new stratum,
external_wikipedia, at the LOWEST precedence:
customs > ace_seed > inrepo > inrepo_force > inrepo_legacy >
candidate > external_wikipedia.

Gates, in order, all fail-closed (design SS2):

  1. Revision pin check: fetched revid must equal the pin; a
     mismatch aborts the whole build, no partial table.
  2. Per-page license check: the site license is re-verified via
     the MediaWiki siteinfo rightsinfo at fetch time. That is a
     SITE-level statement; the per-page exception scan of the
     pinned wikitext is recorded in director-reports/
     LM1_IMPORT_ATTRIBUTION_2026-11-11.md (substantiation
     section). If the site license cannot be confirmed as
     CC BY-SA 4.0, every page is treated as unconfirmed
     (license-excluded) -- never worked around. No GFDL election.
  3. No copied examples (Q-LM1.10): the parser reads ONLY the root,
     meaning, and origin columns of each wikitable row. The
     etymology and examples columns are structurally unreachable:
     no code path reads cells[3] or cells[4].
  4. Zero adapted rows: carried content is unchanged; the only
     transforms are the closed ALLOWED_OPS format normalizations
     (boundary SS3), each recorded per row in changed_fields. Any
     other transform aborts the run (there is no code path that
     performs one; validate_table() refuses artifacts whose rows
     record an unlisted op).
  5. Per-row provenance: every external row carries source_page,
     source_revid, license, changed_fields, adapted=False.
  6. Collision quarantine + lowest precedence: an external row is
     position-quarantined (position_class = position_unresolved)
     when (a) its piece is in the standing QUARANTINED set
     (dell/man/re/alpha/delta/omega), (b) its authored position
     conflicts with the position(s) the in-repo rows attest for
     that piece, or (c) external rows for a piece new to the table
     disagree among themselves on position. Sense-only differences
     are logged collisions (conflict_status = collision_logged),
     mirroring the v1 harvest's treatment. The collisions log is
     recomputed over the final v2 row set.
  7. Cardinality reconciliation: a per-page ledger (source rows,
     parsed rows, invalid rows, license-excluded rows, emitted
     wikitable rows, emitted piece rows) plus totals; identities
     must balance exactly or the build aborts. The ~1,693 figure
     from the proposal is an estimate, never an acceptance number.
  8. Partial-coverage honesty: if any page is license-excluded the
     manifest coverage status is PARTIAL naming the pages, and
     validate_table() refuses any artifact claiming COMPLETE
     coverage in that state.
  9. Pair-atomic publish (REPAIRED 2026-11-11 per Director mail
     1a1cdca2f4dd89fe; the original sequence -- two independent
     _write_atomic calls, collisions then table -- was NOT
     pair-atomic, and main() re-checked the v1 hash only AFTER
     publishing, when a failure could no longer unpublish):
     both artifacts are built and validated in memory, serialized
     once, and staged (temp file + fsync) beside their targets;
     the table header's "pair" block binds the exact collisions
     bytes and the canonical rows bytes to a single generation
     id; the v1 hash is rechecked BEFORE anything is published;
     the previous pair is copied to <path>.prev build-area
     recovery copies; the collisions file is replaced first and
     the table LAST -- the table is the commit point. The loader
     (form/mandell/lm_table.py) verifies the binding on every
     default read and fails closed on a mixed pair, so an
     interruption between the replaces is never served as a
     consistent pair; re-running this build converges the pair
     (tested recovery protocol: T-A/T-B/T-E in
     form/lm1_import_test.py). A failed gate leaves the previous
     artifacts (or their absence) byte-identical.

Export helper (boundary SS4, build-time only): classify_export()
classifies a row set as unchanged_quote / derived_adaptation /
independent and REFUSES (ExportRefused) bulk export of any set
containing a row with incomplete lineage. It makes no runtime or
API guarantee; LM-2/LM-3 composition lineage is a separate circuit.

Run from the repository root:  python3 -m form.lm1_import
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

TOOL_VERSION = "lm1_import/1.0"
API_URL = "https://en.wikipedia.org/w/api.php"
USER_AGENT = ("DellMatrix-LM1-Import/1.0 (build-time importer; "
              "https://github.com/spiritualityhandbook-netizen/"
              "DellMatrix)")

SOURCE_WORK = "List of Greek and Latin roots in English"
SOURCE_URL = "https://en.wikipedia.org/wiki/" + \
    SOURCE_WORK.replace(" ", "_")
ATTRIBUTION_AUTHOR = "Wikipedia contributor community"
LICENSE_NAME = "CC BY-SA 4.0"
LICENSE_URL = "https://creativecommons.org/licenses/by-sa/4.0/"

HUB_TITLE = SOURCE_WORK
HUB_REVID = 1378877227

# Boundary SS1 pins (letter -> revid), verified live at design time
# and re-verified by this build at fetch time (gate 1).
LETTER_PINS = {
    "A": 1377897064, "B": 1275596589, "C": 1360815995,
    "D": 1346448644, "E": 1301146259, "F": 1222950818,
    "G": 1371511202, "H": 1347769344, "I": 1350925285,
    "J": 1369713942, "K": 1299697880, "L": 1320808977,
    "M": 1318218716, "N": 1307355515, "O": 1277566959,
    "P": 1381251622, "Q": 1271579775, "R": 1181415582,
    "S": 1360399905, "T": 1381965170, "U": 1253371142,
    "V": 1320485430, "X": 1106460130, "Z": 1276421824,
}

V1_TABLE_PATH = os.path.join(_HERE, "mandell", "lm_table_v1.json")
V2_TABLE_PATH = os.path.join(_HERE, "mandell", "lm_table_v2.json")
V2_COLLISIONS_PATH = os.path.join(_HERE, "mandell",
                                  "lm_table_v2.collisions.json")

PRECEDENCE_V2 = ["customs", "ace_seed", "inrepo", "inrepo_force",
                 "inrepo_legacy", "candidate", "external_wikipedia"]
EXTERNAL_STRATUM = "external_wikipedia"

# Standing quarantine set (harvest law; Q-LM1.3-Q-LM1.6 unruled).
QUARANTINED = {"dell", "man", "re", "alpha", "delta", "omega"}

# The closed list of allowed format normalizations (boundary SS3,
# Director Q-B1 conditional acceptance). changed_fields entries may
# name ONLY these ops; anything else is an adaptation, and this
# build creates zero adapted rows.
ALLOWED_OPS = ("ref_removed", "comment_removed", "template_removed",
               "link_flattened", "markup_stripped",
               "whitespace_normalized")


class ImportAbort(Exception):
    """A build gate failed; nothing may be written."""


class ExportRefused(Exception):
    """Bulk export refused: incomplete lineage in the row set."""


def page_title(letter: str) -> str:
    return f"{SOURCE_WORK}/{letter}"


def pin_for_title(title: str) -> int:
    if title == HUB_TITLE:
        return HUB_REVID
    letter = title.rsplit("/", 1)[-1]
    return LETTER_PINS[letter]


def _norm(piece: str) -> str:
    return (piece or "").strip().strip("-").lower()


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# ------------------------------------------------------------------
# Fetch layer (network; build-time only, never used by tests)
# ------------------------------------------------------------------

def _api(params: dict) -> dict:
    params = dict(params, format="json")
    url = API_URL + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.load(resp)


def fetch_rightsinfo() -> dict:
    """Site license at fetch time (gate 2 evidence)."""
    data = _api({"action": "query", "meta": "siteinfo",
                 "siprop": "rightsinfo"})
    rights = data.get("query", {}).get("rightsinfo", {})
    url = rights.get("url", "")
    confirmed = "/licenses/by-sa/4.0" in url
    return {"text": rights.get("text", ""), "url": url,
            "confirmed": confirmed,
            "verified_via": "MediaWiki API siteinfo rightsinfo"}


def fetch_page(title: str) -> dict:
    """Fetch one page's current revision (ids + timestamp + text)."""
    data = _api({"action": "query", "prop": "revisions",
                 "rvprop": "ids|timestamp|content",
                 "rvslots": "main", "titles": title})
    pages = data.get("query", {}).get("pages", {})
    if len(pages) != 1:
        raise ImportAbort(f"fetch for {title!r} returned "
                          f"{len(pages)} pages")
    page = next(iter(pages.values()))
    if "revisions" not in page:
        raise ImportAbort(f"page {title!r} has no revision "
                          "(missing page?)")
    rev = page["revisions"][0]
    wikitext = rev["slots"]["main"]["*"]
    return {"title": page["title"], "revid": rev["revid"],
            "revision_timestamp": rev["timestamp"],
            "wikitext": wikitext,
            "sha256": _sha256_bytes(wikitext.encode("utf-8"))}


# ------------------------------------------------------------------
# Field cleaning: the closed ALLOWED_OPS normalization pipeline
# ------------------------------------------------------------------

def _strip_templates(s: str) -> str:
    # Innermost-first iterative removal of {{...}} spans.
    prev = None
    while prev != s:
        prev = s
        s = re.sub(r"\{\{[^{}]*\}\}", "", s)
    return s


def _flatten_links(s: str) -> str:
    # [[target|display]] -> display; [[target]] -> target text
    # (for anchor targets [[#a-]] the fragment names the form).
    s = re.sub(r"\[\[([^\]|]*)\|([^\]]*)\]\]", r"\2", s)
    s = re.sub(r"\[\[([^\]]*)\]\]",
               lambda m: m.group(1).lstrip("#"), s)
    return s


def clean_field(raw: str):
    """Apply ONLY the allowed format normalizations.

    Returns (cleaned_text, ops) where ops lists the ALLOWED_OPS
    that actually changed the text, in application order.
    """
    ops = []
    s = raw
    if "<ref" in s:
        s = re.sub(r"<ref[^>]*>.*?</ref>", "", s, flags=re.S)
        s = re.sub(r"<ref[^>]*/>", "", s)
        ops.append("ref_removed")
    if "<!--" in s:
        s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
        ops.append("comment_removed")
    if "{{" in s:
        s = _strip_templates(s)
        ops.append("template_removed")
    if "[[" in s:
        s = _flatten_links(s)
        ops.append("link_flattened")
    if "''" in s or re.search(r"<[^>]+>", s):
        s = s.replace("'''", "").replace("''", "")
        s = re.sub(r"<[^>]+>", "", s)
        ops.append("markup_stripped")
    collapsed = re.sub(r"\s+", " ", s).strip()
    if collapsed != s:
        ops.append("whitespace_normalized")
    return collapsed, ops


def root_forms(root_raw: str):
    """Extract the variant forms from a root cell.

    Refs/comments are stripped and links flattened (so an anchor
    cross-reference cell '''[[#amm-|amath-]]''' yields its display
    form 'amath-'), then the '''...''' bold spans are the forms.
    Returns (forms, ops).
    """
    ops = []
    s = root_raw
    if "<ref" in s:
        s = re.sub(r"<ref[^>]*>.*?</ref>", "", s, flags=re.S)
        s = re.sub(r"<ref[^>]*/>", "", s)
        ops.append("ref_removed")
    if "<!--" in s:
        s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
        ops.append("comment_removed")
    if "[[" in s:
        s = _flatten_links(s)
        ops.append("link_flattened")
    spans = re.findall(r"'''(.+?)'''", s, flags=re.S)
    if not spans:
        spans = [s]  # fallback: whole cleaned cell (not seen in data)
    forms = []
    for span in spans:
        for part in span.split(","):
            form = re.sub(r"<[^>]+>", "", part)
            form = re.sub(r"\s+", " ", form).strip().strip('"')
            if form and any(ch.isalpha() for ch in form):
                forms.append(form)
    return forms, ops


def position_of(form: str) -> str:
    """Schema mapping from the source's own dash notation:
    trailing dash only -> prefix; leading dash only -> suffix;
    anything else (bare or infix-dashed combining form) -> root."""
    lead = form.startswith("-")
    trail = form.endswith("-")
    if trail and not lead:
        return "prefix"
    if lead and not trail:
        return "suffix"
    return "root"


# ------------------------------------------------------------------
# Wikitext parsing (reads ONLY root / meaning / origin columns)
# ------------------------------------------------------------------

def _table_blocks(wikitext: str):
    return [m.group(1) for m in
            re.finditer(r"\{\|(.*?)\n\|\}", wikitext, re.S)]


def _row_chunks(block: str):
    parts = re.split(r"(?m)^\|-.*$", block)
    return parts[1:]


def _split_cells(chunk: str):
    lines = [l for l in chunk.split("\n") if l.strip()]
    if not lines:
        return []
    if any("||" in l for l in lines):
        joined = "\n".join(lines).lstrip()
        if joined.startswith("|"):
            joined = joined[1:]
        return joined.split("||")
    cells = []
    for line in lines:
        s = line.strip()
        if s.startswith("|") or s.startswith("!"):
            cells.append(s[1:])
        elif cells:
            cells[-1] += "\n" + s
    return cells


def parse_page(wikitext: str) -> dict:
    """Parse one letter page's wikitables.

    Returns {"parsed": [ {forms, sense, language, changed_fields} ],
             "source_rows": n, "invalid_rows": n}.
    A chunk is a data row iff its first non-empty line does not
    start with '!' (header). A data row is INVALID (counted, never
    silently dropped) when it does not yield exactly 5 cells, has
    no extractable root form, or has an empty cleaned gloss.
    cells[3] (etymology) and cells[4] (examples) are never read.
    """
    parsed = []
    source_rows = 0
    invalid_rows = 0
    for block in _table_blocks(wikitext):
        for chunk in _row_chunks(block):
            lines = [l for l in chunk.split("\n") if l.strip()]
            if not lines:
                continue
            if lines[0].strip().startswith("!"):
                continue  # header row: not a data row
            source_rows += 1
            cells = _split_cells(chunk)
            if len(cells) != 5:
                invalid_rows += 1
                continue
            forms, root_ops = root_forms(cells[0])
            sense, gloss_ops = clean_field(cells[1])
            language, origin_ops = clean_field(cells[2])
            if not forms or not sense:
                invalid_rows += 1
                continue
            parsed.append({
                "forms": forms,
                "sense": sense,
                "language": language,
                "changed_fields": {"root": root_ops,
                                   "meaning": gloss_ops,
                                   "origin": origin_ops},
            })
    return {"parsed": parsed, "source_rows": source_rows,
            "invalid_rows": invalid_rows}


# ------------------------------------------------------------------
# Build (pure: payloads in, artifacts out; raises ImportAbort)
# ------------------------------------------------------------------

def _external_row(form, parsed_row, payload):
    pos = position_of(form)
    return {
        "piece": _norm(form),
        "authored_form": form,
        "position_class": pos,
        "authored_position_class": pos,
        "language": parsed_row["language"],
        "sense": parsed_row["sense"],
        "dell_ref": None,
        "la": None,
        "split": None,
        "stratum": EXTERNAL_STRATUM,
        "provenance": {
            "source_file": f"English Wikipedia: {payload['title']}",
            "source_symbol": "roots wikitable"},
        "source_page": payload["title"],
        "source_revid": payload["revid"],
        "license": LICENSE_NAME,
        "changed_fields": parsed_row["changed_fields"],
        "adapted": False,
        "conflict_status": "clean",
        "notes": "External import under CC BY-SA 4.0 (Ace ruling "
                 "2026-11-11; boundary + design on record). Format "
                 "normalization only -- zero adapted rows. Examples "
                 "and etymology columns not copied (Q-LM1.10).",
    }


def _apply_quarantine(v1_rows, ext_rows) -> None:
    attested = {}
    for row in v1_rows:
        attested.setdefault(row["piece"], set()).add(
            row["authored_position_class"])
    by_piece = {}
    for row in ext_rows:
        by_piece.setdefault(row["piece"], []).append(row)
    for piece, erows in by_piece.items():
        quar = False
        if piece in QUARANTINED:
            quar = True
        elif piece in attested:
            if any(r["authored_position_class"] not in attested[piece]
                   for r in erows):
                quar = True
        elif len({r["authored_position_class"] for r in erows}) > 1:
            quar = True
        if quar:
            for r in erows:
                r["position_class"] = "position_unresolved"
                r["conflict_status"] = "position_unresolved"


def compute_collisions(rows) -> list:
    rank = {s: i for i, s in enumerate(PRECEDENCE_V2)}
    groups = {}
    for row in rows:
        groups.setdefault(row["piece"], []).append(row)
    out = []
    for piece in sorted(groups):
        grows = groups[piece]
        if len(grows) < 2:
            continue
        keys = {(g["position_class"], g["sense"]) for g in grows}
        if len(keys) <= 1:
            continue
        best = min(grows, key=lambda g: rank[g["stratum"]])
        out.append({
            "piece": piece,
            "rows": [
                {"stratum": g["stratum"],
                 "authored_position_class":
                     g["authored_position_class"],
                 "position_class": g["position_class"],
                 "sense": g["sense"],
                 "source_file": g["provenance"]["source_file"]}
                for g in sorted(
                    grows, key=lambda g: rank[g["stratum"]])],
            "precedence_outcome":
                "No runtime change: existing module behavior is "
                "untouched by the table. Table annotation only: "
                f"highest-precedence shipped stratum = "
                f"{best['stratum']} (a runtime custom, if bound, "
                "outranks every shipped stratum). "
                "position_unresolved pieces are excluded from "
                "position-dependent consumption until an authority "
                "rules (Q-LM1.3-Q-LM1.6).",
        })
    return out


def build_table(v1_doc: dict, payloads: list, rights: dict,
                fetched_at: str) -> dict:
    """Build the v2 table document from fetched page payloads.

    payloads: [{title, revid, revision_timestamp, wikitext, sha256,
                license_verified}] in pin order.
    Returns {"table": doc, "collisions": [...], "ledger": {...}}.
    Raises ImportAbort on any gate failure; writes nothing.
    """
    ledger_pages = {}
    ext_rows = []
    excluded_pages = []
    totals = {"source_rows": 0, "parsed_rows": 0, "invalid_rows": 0,
              "license_excluded_rows": 0, "emitted_rows": 0,
              "emitted_pieces": 0}

    for payload in payloads:
        title = payload["title"]
        # Gate 1: revision pin (also checked at fetch time).
        if payload["revid"] != pin_for_title(title):
            raise ImportAbort(
                f"gate 1 (pin): {title} revid {payload['revid']} "
                f"!= pin {pin_for_title(title)} -- abort, no "
                "partial table")
        counted = parse_page(payload["wikitext"])
        source_rows = counted["source_rows"]
        if not payload["license_verified"]:
            # Gate 2: page excluded, never worked around.
            entry = {"source_rows": source_rows, "parsed_rows": 0,
                     "invalid_rows": 0,
                     "license_excluded_rows": source_rows,
                     "emitted_rows": 0, "emitted_pieces": 0}
            excluded_pages.append(title)
        else:
            emitted_pieces = 0
            for prow in counted["parsed"]:
                for form in prow["forms"]:
                    ext_rows.append(_external_row(form, prow,
                                                  payload))
                    emitted_pieces += 1
            entry = {"source_rows": source_rows,
                     "parsed_rows": len(counted["parsed"]),
                     "invalid_rows": counted["invalid_rows"],
                     "license_excluded_rows": 0,
                     "emitted_rows": len(counted["parsed"]),
                     "emitted_pieces": emitted_pieces}
        # Gate 7: per-page identity must balance exactly.
        if entry["source_rows"] != entry["parsed_rows"] + \
                entry["invalid_rows"] + \
                entry["license_excluded_rows"]:
            raise ImportAbort(
                f"gate 7 (cardinality): {title} ledger does not "
                f"balance: {entry}")
        if entry["emitted_rows"] != entry["parsed_rows"]:
            raise ImportAbort(
                f"gate 7 (cardinality): {title} emitted != parsed: "
                f"{entry}")
        ledger_pages[title] = entry
        for k in totals:
            totals[k] += entry[k]
    if totals["source_rows"] != totals["parsed_rows"] + \
            totals["invalid_rows"] + totals["license_excluded_rows"]:
        raise ImportAbort("gate 7 (cardinality): totals do not "
                          "balance")

    # Gate 8: coverage status is computed, never asserted.
    coverage_status = "PARTIAL" if excluded_pages else "COMPLETE"

    # v1 rows are carried over byte-faithful: deep-copy them so no
    # build step can mutate the caller's v1 document, and never
    # rewrite a v1 row's fields (a v1 row whose piece newly collides
    # because of an external row keeps the conflict_status it
    # shipped with in v1; the collision is recorded in the v2
    # collisions log, which is derived data).
    v1_rows = copy.deepcopy(v1_doc.get("rows", []))
    _apply_quarantine(v1_rows, ext_rows)
    all_rows = list(v1_rows) + ext_rows
    collisions = compute_collisions(all_rows)
    collided = {c["piece"] for c in collisions}
    for row in ext_rows:
        if row["piece"] in collided and \
                row["conflict_status"] == "clean":
            row["conflict_status"] = "collision_logged"
    rank = {s: i for i, s in enumerate(PRECEDENCE_V2)}
    all_rows.sort(key=lambda r: (r["piece"], rank[r["stratum"]],
                                 r["authored_position_class"],
                                 r.get("source_page", ""),
                                 r["sense"]))

    per_stratum = {}
    for row in all_rows:
        per_stratum[row["stratum"]] = \
            per_stratum.get(row["stratum"], 0) + 1

    manifest_pages = []
    for payload in payloads:
        manifest_pages.append({
            "title": payload["title"],
            "revid": payload["revid"],
            "revision_timestamp": payload["revision_timestamp"],
            "fetched_at": fetched_at,
            "sha256": payload["sha256"],
            "license": {"name": LICENSE_NAME, "url": LICENSE_URL,
                        "verified": payload["license_verified"],
                        "verified_via": rights["verified_via"],
                        "rights_text": rights["text"],
                        "rights_url": rights["url"]},
            "ledger": ledger_pages[payload["title"]],
        })

    header = {
        "table": "lm_table",
        "version": 2,
        "generated_by": TOOL_VERSION,
        "import_date": fetched_at[:10],
        "retrieved_at": fetched_at,
        "authorization": "Ace license ruling 2026-11-11 "
                         "(LM1_LICENSE_RULING_ACE_2026-11-11.md, "
                         "PR #390 merged 49b81dd); Director GO mail "
                         "1a1cd7d53c3ec395, conditions fulfilled "
                         "2026-11-11 (PR #391 merged 610fb13); "
                         "boundary LM1_IMPORT_LICENSE_BOUNDARY_"
                         "2026-11-11.md; design LM1_IMPORT_EXECUTION_"
                         "DESIGN_2026-11-11.md (PR #392 merged "
                         "4e556c4)",
        "precedence": PRECEDENCE_V2,
        "precedence_note": "Customs are runtime state (persist "
                           "v7), never shipped; a bound custom "
                           "outranks every shipped stratum. "
                           "external_wikipedia is the LOWEST "
                           "shipped stratum and never wins a "
                           "lookup. lookup() returns the full row "
                           "set -- never a silent first-match.",
        "attribution": {
            "source_work": SOURCE_WORK,
            "source_url": SOURCE_URL,
            "author": ATTRIBUTION_AUTHOR,
            "hub_title": HUB_TITLE,
            "hub_revid": HUB_REVID,
            "license": LICENSE_NAME,
            "license_url": LICENSE_URL,
            "changes": "Format normalization only (reference / "
                       "comment / template stripping, link "
                       "flattening, markup stripping, whitespace "
                       "normalization), recorded per row in "
                       "changed_fields; root-cell variant forms "
                       "extracted; etymology and examples columns "
                       "not copied (Q-LM1.10); fields mapped to "
                       "the stratum schema. Zero adapted rows.",
        },
        "coverage": {
            "status": coverage_status,
            "excluded_pages": excluded_pages,
            "external_rows": len(ext_rows),
            "total_rows": len(all_rows),
            "per_stratum": per_stratum,
            "collision_pieces": len(collisions),
            "quarantined_pieces": sorted(QUARANTINED),
        },
        "manifest": {
            "rightsinfo": rights,
            "hub": {"title": HUB_TITLE, "revid": HUB_REVID},
            "pages": manifest_pages,
            "ledger_totals": totals,
            "v1_carry": {
                "path": "form/mandell/lm_table_v1.json",
                "rows": len(v1_rows),
                "note": "v1 rows carried over verbatim "
                        "(byte-faithful row content); v1 file "
                        "itself untouched by this build.",
            },
        },
    }
    doc = {"header": header, "rows": all_rows}
    validate_table(doc)
    return {"table": doc, "collisions": collisions,
            "ledger": {"pages": ledger_pages, "totals": totals}}


def validate_table(doc: dict) -> None:
    """Self-check an artifact against the build gates.

    Raises ImportAbort on: incomplete per-row provenance (gate 5),
    an unlisted changed-fields op or an adapted row (gate 4),
    a ledger that does not balance against the rows present
    (gate 7), or a coverage claim inconsistent with the manifest
    (gate 8). Used by the build itself and by the test suite.
    """
    header = doc.get("header") or {}
    rows = doc.get("rows", [])
    manifest = header.get("manifest", {})
    ext = [r for r in rows if r.get("stratum") == EXTERNAL_STRATUM]
    for row in ext:
        if not row.get("source_page") or \
                not row.get("source_revid") or \
                not row.get("license") or \
                "changed_fields" not in row:
            raise ImportAbort(
                f"gate 5 (provenance): external row for piece "
                f"{row.get('piece')!r} is missing provenance")
        if row.get("adapted") is not False:
            raise ImportAbort(
                f"gate 4 (zero adapted): row {row.get('piece')!r} "
                "is not marked adapted=False")
        for ops in (row.get("changed_fields") or {}).values():
            for op in ops:
                if op not in ALLOWED_OPS:
                    raise ImportAbort(
                        f"gate 4 (zero adapted): row "
                        f"{row.get('piece')!r} records unlisted "
                        f"transform {op!r}")
    totals = manifest.get("ledger_totals", {})
    if totals:
        if totals["source_rows"] != totals["parsed_rows"] + \
                totals["invalid_rows"] + \
                totals["license_excluded_rows"]:
            raise ImportAbort("gate 7 (cardinality): manifest "
                              "totals do not balance")
        if totals["emitted_pieces"] != len(ext):
            raise ImportAbort(
                f"gate 7 (cardinality): ledger emitted_pieces "
                f"{totals['emitted_pieces']} != external rows "
                f"present {len(ext)}")
        for entry in manifest.get("pages", []):
            led = entry["ledger"]
            n = sum(1 for r in ext
                    if r.get("source_page") == entry["title"])
            if n != led["emitted_pieces"]:
                raise ImportAbort(
                    f"gate 7 (cardinality): page {entry['title']} "
                    f"ledger emitted_pieces {led['emitted_pieces']} "
                    f"!= rows present {n}")
    coverage = header.get("coverage", {})
    excluded = coverage.get("excluded_pages", [])
    if coverage.get("status") == "COMPLETE" and excluded:
        raise ImportAbort(
            "gate 8 (coverage): artifact claims COMPLETE coverage "
            f"with excluded pages {excluded}")
    if coverage.get("status") == "PARTIAL" and not excluded:
        raise ImportAbort("gate 8 (coverage): PARTIAL claimed "
                          "with no excluded pages named")
    for entry in manifest.get("pages", []):
        if entry["revid"] != pin_for_title(entry["title"]):
            raise ImportAbort(
                f"gate 1 (pin): manifest revid for "
                f"{entry['title']} != pin")


# ------------------------------------------------------------------
# Export helper (build-time only; boundary SS4)
# ------------------------------------------------------------------

def classify_export(rows) -> dict:
    """Classify a row set for bulk export; refuse incomplete
    lineage. Returns {"classification": ..., "notices": [...],
    "external_rows": n}. Raises ExportRefused when any row's
    lineage is incomplete (an external row without source_page /
    source_revid / license, or any row without provenance)."""
    rows = list(rows)
    external = 0
    notices = []
    for row in rows:
        prov = row.get("provenance") or {}
        if row.get("stratum") == EXTERNAL_STRATUM:
            external += 1
            if not row.get("source_page") or \
                    not row.get("source_revid") or \
                    not row.get("license"):
                raise ExportRefused(
                    f"external row for piece {row.get('piece')!r} "
                    "has incomplete lineage (source_page / "
                    "source_revid / license required)")
        elif not prov.get("source_file"):
            raise ExportRefused(
                f"row for piece {row.get('piece')!r} has no "
                "provenance source_file -- lineage incomplete")
    if any(row.get("adapted") for row in rows):
        classification = "derived_adaptation"
        notices.append("Set contains adapted rows: distribute "
                       "under CC BY-SA 4.0 with attribution and "
                       "source availability.")
    elif external:
        classification = "unchanged_quote"
        notices.append(
            f"Set contains {external} row(s) from "
            f"{SOURCE_WORK!r} ({ATTRIBUTION_AUTHOR}), licensed "
            f"{LICENSE_NAME} ({LICENSE_URL}); attribution record: "
            "director-reports/LM1_IMPORT_ATTRIBUTION_2026-11-11.md")
    elif any("stratum" not in row for row in rows):
        # Fail-closed default (boundary SS4): uncertain lineage
        # classifies conservatively as a derived adaptation.
        classification = "derived_adaptation"
        notices.append("Set contains rows of unknown stratum: "
                       "classified conservatively as derived "
                       "adaptation pending case-specific "
                       "assessment.")
    else:
        classification = "independent"
        notices.append("No external-source rows: no obligation "
                       "from the Wikipedia source arises (other "
                       "sources' terms may still apply).")
    return {"classification": classification, "notices": notices,
            "external_rows": external}


# ------------------------------------------------------------------
# Pair-atomic publish + main (gate 9, repaired per Director mail
# 1a1cdca2f4dd89fe -- see the module docstring)
# ------------------------------------------------------------------

def _serialize(doc) -> bytes:
    """The one serialization for both artifacts: the exact bytes
    that are hashed for the pair binding are the exact bytes
    written to disk."""
    return json.dumps(doc, ensure_ascii=False, indent=1,
                      sort_keys=True).encode("utf-8") + b"\n"


def _stage_bytes(path: str, data: bytes) -> str:
    """Write data to a temp file beside its target and fsync it.
    Returns the temp path; nothing is visible at the target yet."""
    tmp = f"{path}.tmp-{os.getpid()}"
    with open(tmp, "wb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    return tmp


def _write_atomic_bytes(path: str, data: bytes) -> None:
    os.replace(_stage_bytes(path, data), path)


def _write_atomic(path: str, doc) -> None:
    _write_atomic_bytes(path, _serialize(doc))


def pair_binding(rows, collisions_bytes: bytes) -> dict:
    """Bind the artifact pair to a single generation.

    The generation id is derived from BOTH members' content: the
    sha256 of the exact collisions-file bytes and the sha256 of
    the canonical rows bytes. The table header carries all three
    values; the loader recomputes them on every default read, so
    any pair that is not exactly one generation -- mixed publish,
    partial publish, tampered member -- is detected.
    """
    collisions_sha = _sha256_bytes(collisions_bytes)
    rows_bytes = json.dumps(rows, ensure_ascii=False,
                            sort_keys=True,
                            separators=(",", ":")).encode("utf-8")
    rows_sha = _sha256_bytes(rows_bytes)
    generation = _sha256_bytes(bytes.fromhex(collisions_sha)
                               + bytes.fromhex(rows_sha))
    return {"binding": "lm1-pair/1", "generation": generation,
            "collisions_sha256": collisions_sha,
            "rows_sha256": rows_sha}


def _effective_fault(fault):
    """Resolve the failure-injection hook for publish tests.

    An explicit callable wins. Otherwise, when the environment
    carries LM1_IMPORT_FAULT=sleep:<point>, the hook sleeps at the
    named publish point (writing LM1_IMPORT_FAULT_MARKER first if
    set) -- used by the process-interruption test (T-B), which
    kills the importer mid-publish. Build-time test use only;
    unset in normal builds.
    """
    if fault is not None:
        return fault
    spec = os.environ.get("LM1_IMPORT_FAULT", "")
    if not spec.startswith("sleep:"):
        return None
    point = spec.split(":", 1)[1]
    marker = os.environ.get("LM1_IMPORT_FAULT_MARKER")

    def hook(hit):
        if hit == point:
            if marker:
                with open(marker, "w", encoding="utf-8") as f:
                    f.write(hit)
            time.sleep(120)

    return hook


def run_build(payloads, rights, fetched_at, v1_doc,
              table_path=V2_TABLE_PATH,
              collisions_path=V2_COLLISIONS_PATH,
              v1_path=None, expected_v1_sha256=None,
              fault=None) -> dict:
    """Build, bind, and publish the artifact pair (gate 9).

    Publish protocol (all steps after build_table, which runs
    every gate in memory and writes nothing):

      1. Serialize both artifacts once; the table header gains
         the "pair" generation binding (pair_binding()).
      2. Stage both payloads to fsynced temp files beside their
         targets. Nothing is visible at the targets yet.
      3. Pre-publish v1 recheck: when expected_v1_sha256 is
         supplied, the v1 file at v1_path must still hash to it;
         a concurrent v1 change aborts the build with NOTHING
         published. (The pre-repair code checked only after
         publishing, when the failure could not unpublish.)
      4. Retain the previous pair as <path>.prev build-area
         recovery copies (never read by the loader, never part of
         the committed artifact set; recovery aids only).
      5. Publish: os.replace the collisions file, then the table
         file LAST. The table is the commit point -- its header
         binds the collisions bytes of the same generation, and
         the loader verifies that binding on every default read
         and fails closed (PairInconsistentError) on a mixed
         pair. A crash between the two replaces therefore leaves
         a state no reader will serve; re-running the build
         converges the pair to one consistent generation
         (recovery protocol, tested by T-A/T-B/T-E).

    fault: optional callable invoked at the publish points
    "staged", "after_collisions_replace", "after_table_replace"
    (failure-injection tests); see _effective_fault for the
    env-gated alternative.
    """
    built = build_table(v1_doc, payloads, rights, fetched_at)
    hook = _effective_fault(fault)
    table_doc = {"header": built["table"]["header"],
                 "rows": built["table"]["rows"]}
    collisions_bytes = _serialize(built["collisions"])
    table_doc["header"]["pair"] = pair_binding(
        table_doc["rows"], collisions_bytes)
    table_bytes = _serialize(table_doc)
    built["table"] = table_doc
    staged = []
    try:
        staged.append((_stage_bytes(collisions_path,
                                     collisions_bytes),
                       collisions_path))
        staged.append((_stage_bytes(table_path, table_bytes),
                       table_path))
        if hook is not None:
            hook("staged")
        if expected_v1_sha256 is not None:
            if v1_path is None:
                raise ImportAbort(
                    "gate 9 (publish): expected_v1_sha256 "
                    "supplied without v1_path -- abort, nothing "
                    "published")
            try:
                with open(v1_path, "rb") as f:
                    actual_v1 = _sha256_bytes(f.read())
            except OSError as exc:
                raise ImportAbort(
                    "gate 9 (publish): v1 table unreadable for "
                    f"the pre-publish recheck ({exc}) -- abort, "
                    "nothing published")
            if actual_v1 != expected_v1_sha256:
                raise ImportAbort(
                    "gate 9 (publish): v1 table changed during "
                    "the build -- aborting BEFORE publish; the "
                    "previous pair (or its absence) is untouched")
        for _tmp, target in staged:
            if os.path.exists(target):
                with open(target, "rb") as f:
                    _write_atomic_bytes(target + ".prev", f.read())
        os.replace(staged[0][0], staged[0][1])
        if hook is not None:
            hook("after_collisions_replace")
        os.replace(staged[1][0], staged[1][1])
        if hook is not None:
            hook("after_table_replace")
    except BaseException:
        for tmp, _target in staged:
            if os.path.exists(tmp):
                os.unlink(tmp)
        raise
    return built


def main() -> int:
    fetched_at = datetime.now(timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ")
    rights = fetch_rightsinfo()
    hub = fetch_page(HUB_TITLE)
    if hub["revid"] != HUB_REVID:
        raise ImportAbort(
            f"gate 1 (pin): hub revid {hub['revid']} != pin "
            f"{HUB_REVID} -- abort")
    payloads = []
    for letter in LETTER_PINS:
        title = page_title(letter)
        page = fetch_page(title)
        if page["revid"] != LETTER_PINS[letter]:
            raise ImportAbort(
                f"gate 1 (pin): {title} revid {page['revid']} "
                f"!= pin {LETTER_PINS[letter]} -- abort, no "
                "partial table")
        page["license_verified"] = rights["confirmed"]
        payloads.append(page)
    if not any(p["license_verified"] for p in payloads):
        raise ImportAbort(
            "gate 2 (license): site license could not be "
            "confirmed as CC BY-SA 4.0 at fetch time; every page "
            "is unconfirmed -- aborting rather than emitting an "
            "empty import")
    # Read the v1 bytes ONCE: the document parsed and the hash
    # rechecked before publish (inside run_build) are the same
    # bytes, so no change can slip between parse and recheck.
    with open(V1_TABLE_PATH, "rb") as f:
        v1_bytes = f.read()
    v1_doc = json.loads(v1_bytes)
    v1_hash = _sha256_bytes(v1_bytes)
    built = run_build(payloads, rights, fetched_at, v1_doc,
                      v1_path=V1_TABLE_PATH,
                      expected_v1_sha256=v1_hash)
    # Post-publish read-back: the pair on disk must verify
    # against its own binding before success is reported.
    with open(V2_COLLISIONS_PATH, "rb") as f:
        published_collisions_sha = _sha256_bytes(f.read())
    with open(V2_TABLE_PATH, encoding="utf-8") as f:
        published_pair = (json.load(f).get("header")
                          or {}).get("pair") or {}
    if published_pair.get("collisions_sha256") != \
            published_collisions_sha:
        raise ImportAbort(
            "gate 9 (publish): post-publish read-back failed -- "
            "the published pair does not verify against its "
            "binding")
    totals = built["ledger"]["totals"]
    cov = built["table"]["header"]["coverage"]
    print(f"lm1_import: coverage {cov['status']}; "
          f"source rows {totals['source_rows']}, parsed "
          f"{totals['parsed_rows']}, invalid "
          f"{totals['invalid_rows']}, license-excluded "
          f"{totals['license_excluded_rows']}, emitted pieces "
          f"{totals['emitted_pieces']} -> {V2_TABLE_PATH}, "
          f"{V2_COLLISIONS_PATH}")
    print(f"lm1_import: v1 sha256 unchanged: {v1_hash}")
    print(f"lm1_import: pair generation "
          f"{published_pair.get('generation')}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ImportAbort as exc:
        print(f"lm1_import: ABORT -- {exc}", file=sys.stderr)
        sys.exit(1)
