"""LM-1 EXTERNAL IMPORT — design tests T1-T10 (Director GO mail
1a1cd7d53c3ec395; design director-reports/
LM1_IMPORT_EXECUTION_DESIGN_2026-11-11.md SS4, as corrected).

Contracts proven here, against the shipped artifact
(form/mandell/lm_table_v2.json) and against synthetic fixture
builds driven through form/lm1_import.py's pure build path:

- T1 PROVENANCE COMPLETE: every external row carries source_page,
  source_revid, license, changed_fields; every manifest revid
  equals the boundary pin for its page.
- T2 EXAMPLES STRUCTURALLY EXCLUDED: fixture pages whose etymology
  and examples cells carry UNIQUE SENTINELS (inline, cross-column,
  multiline-continuation, and vertical-format fixtures) emit
  artifacts containing none of them in any field, while the
  root/meaning/origin content is carried.
- T3 ZERO ADAPTED: adapted is False on every imported row;
  changed_fields entries name only ALLOWED_OPS; a marked-up
  fixture gloss cleans to exactly the expected text.
- T4 PRECEDENCE: external_wikipedia is the lowest stratum; for
  every piece present in both external and in-repo strata,
  lookup() ranks every external row below every in-repo row.
- T5 QUARANTINE: the standing quarantined pieces (dell / man /
  re / alpha / delta / omega) are position_unresolved on every
  row; a synthetic new position collision (fixture) joins the
  quarantine.
- T6 LINEAGE / EXPORT: a complete-lineage set classifies and
  carries notices; a set with one provenance field stripped is
  REFUSED; an adapted row forces derived_adaptation; in-repo
  rows alone classify independent.
- T7 V1 INTEGRITY + LOADER PATHS: lm_table_v1.json sha256 is the
  pre-import pin; the loader's single read path returns v2 when
  present and falls back to v1 behavior when v2 is absent.
- T8 CARDINALITY: the shipped artifact validates; a copy with
  one external row silently dropped FAILS validation; fixture
  ledger identities balance per page and in total.
- T9 PARTIAL COVERAGE: a fixture with one license-excluded page
  emits coverage PARTIAL naming the page and no rows from it;
  claiming COMPLETE over exclusions fails validation.
- T10 NO-WRITE-ON-FAILURE: a build failed at a gate leaves a
  pre-existing artifact byte-identical and creates no artifact
  where none existed.

Repair tests (Director CORRECTION_REQUIRED / MERGE HOLD, mail
1a1cdca2f4dd89fe -- the original two-replace publish was not
pair-atomic, and the v1 hash was rechecked only after publish):

- T-A INJECTED FAILURE BETWEEN REPLACES: a fault raising after
  the collisions replace and before the table replace leaves a
  mixed pair on disk; the reader fails closed
  (PairInconsistentError) and never serves it; the previous pair
  is retained as build-area .prev copies.
- T-B PROCESS INTERRUPTION: the importer as a subprocess, killed
  (SIGKILL) while parked at the same publish point via the
  env-gated fault hook, leaves the same guarantee.
- T-C V1 CONCURRENT MUTATION BEFORE COMMIT: a v1 change landing
  after staging aborts the build BEFORE publish -- the previous
  pair (or its absence) is byte-identical, nothing staged leaks.
- T-D READER CONSISTENCY: a hand-flipped binding hash, a
  byte-appended collisions file, and a flipped generation id are
  each detected by the reader, which fails closed.
- T-E RETRY / RECOVERY: after a mid-publish crash (in-process and
  via the killed subprocess), re-running the build converges the
  pair to one consistent new generation that the reader serves.
"""

from __future__ import annotations

import copy
import glob
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

V1_SHA256 = "59c63a40f8d274254a7589b9a2e6ef49dba712eb880ca5ac144b005bb8da8849"
QUARANTINED = ("dell", "man", "re", "alpha", "delta", "omega")

RIGHTS = {"text": "Creative Commons Attribution-Share Alike 4.0",
          "url": "https://creativecommons.org/licenses/by-sa/4.0/"
                 "deed.en",
          "confirmed": True,
          "verified_via": "fixture rightsinfo"}

PAGE_A_WIKITEXT = """{| class="wikitable sortable"
|-
! Root !! Meaning in English !! Origin language !! Etymology !! English examples
|-
| '''zzalpha-'''<ref>{{testref}}</ref> || alpha meaning || Latin || SENTINEL_ETYM_X1 || SENTINEL_EX_X2, zzalphaic
|-
| '''zzbeta-''' || beta meaning || Greek || etym || first example
continuation line SENTINEL_MULTI_X3
|-
| '''zzroot-''' || root meaning || Latin || etym || example
|-
| '''zzgamma-'''
| gamma meaning
| Greek
| SENTINEL_ETYM_X4
| SENTINEL_EX_X5
|-
| '''zzdelta-''' || '''bold''' [[word|linked]] meaning || Latin || etym || example
|}"""

PAGE_B_WIKITEXT = """{| class="wikitable sortable"
|-
! Root !! Meaning in English !! Origin language !! Etymology !! English examples
|-
| '''zzeta-''' || eta meaning || Latin || etym || example
|}"""

SENTINELS = ("SENTINEL_ETYM_X1", "SENTINEL_EX_X2",
             "SENTINEL_MULTI_X3", "SENTINEL_ETYM_X4",
             "SENTINEL_EX_X5")

# Subprocess driver for T-B/T-E: builds a pair from a JSON spec
# ({v1_doc, payloads: [{letter, wikitext}]}) at argv paths. The
# env-gated fault hook in form/lm1_import.py parks it mid-publish.
_DRIVER_SRC = """
import hashlib, json, sys
sys.path.insert(0, sys.argv[1])
from form import lm1_import as imp

RIGHTS = {"text": "Creative Commons Attribution-Share Alike 4.0",
          "url": "https://creativecommons.org/licenses/by-sa/4.0/",
          "confirmed": True, "verified_via": "driver rightsinfo"}

spec = json.load(open(sys.argv[2]))
payloads = []
for entry in spec["payloads"]:
    wikitext = entry["wikitext"]
    payloads.append({
        "title": imp.page_title(entry["letter"]),
        "revid": imp.LETTER_PINS[entry["letter"]],
        "revision_timestamp": "2026-11-11T00:00:00Z",
        "wikitext": wikitext,
        "sha256": hashlib.sha256(
            wikitext.encode("utf-8")).hexdigest(),
        "license_verified": True})
imp.run_build(payloads, RIGHTS, "2026-11-11T00:00:00Z",
              spec["v1_doc"], table_path=sys.argv[3],
              collisions_path=sys.argv[4])
print("DRIVER DONE")
"""


def _fixture_v1_doc():
    def row(piece, sense):
        return {"piece": piece, "authored_form": piece,
                "position_class": "root",
                "authored_position_class": "root",
                "language": "project", "sense": sense,
                "dell_ref": None, "la": None, "split": None,
                "stratum": "inrepo",
                "provenance": {"source_file": "fixture",
                               "source_symbol": "FIXTURE"},
                "conflict_status": "clean", "notes": ""}
    return {"header": {"table": "lm_table", "version": 1},
            "rows": [row("zzalpha", "fixture in-repo alpha"),
                     row("zzroot", "fixture in-repo root")]}


def _payload(letter, wikitext, verified=True, revid=None):
    from form import lm1_import as imp
    return {"title": imp.page_title(letter),
            "revid": imp.LETTER_PINS[letter] if revid is None
            else revid,
            "revision_timestamp": "2026-11-11T00:00:00Z",
            "wikitext": wikitext,
            "sha256": hashlib.sha256(
                wikitext.encode("utf-8")).hexdigest(),
            "license_verified": verified}


def _fixture_build(verified_b=True):
    from form import lm1_import as imp
    payloads = [_payload("A", PAGE_A_WIKITEXT),
                _payload("B", PAGE_B_WIKITEXT,
                         verified=verified_b)]
    return imp.build_table(_fixture_v1_doc(), payloads, RIGHTS,
                           "2026-11-11T00:00:00Z")


def smoke() -> bool:
    print("=== LM-1 IMPORT SMOKE ===")
    r = []

    def rec(name, ok, detail=""):
        print(f"[{'PASS' if ok else 'FAIL'}] {name}"
              + (f" -- {detail}" if detail and not ok else ""))
        r.append(bool(ok))

    from form import lm1_import as imp
    from form.mandell import lm_table

    v2 = lm_table.load_table()
    rows = v2["rows"]
    header = v2["header"]
    ext = [row for row in rows
           if row.get("stratum") == "external_wikipedia"]

    # ---- T1: provenance completeness + manifest pins
    rec("T1 table header is version 2 (import artifact)",
        header.get("version") == 2)
    prov_ok = all(
        row.get("source_page") and row.get("source_revid")
        and row.get("license") and "changed_fields" in row
        and row["source_revid"] == imp.pin_for_title(
            row["source_page"])
        for row in ext)
    rec("T1 every external row carries complete provenance "
        "with pinned revids", prov_ok and len(ext) > 0,
        f"external rows: {len(ext)}")
    manifest = header.get("manifest", {})
    rec("T1 manifest pins all 24 letter pages",
        len(manifest.get("pages", [])) == 24 and all(
            p["revid"] == imp.pin_for_title(p["title"])
            for p in manifest["pages"]))

    # ---- T2: sentinel fixtures -- examples/etymology unreachable
    built = _fixture_build()
    fixture_ext = [row for row in built["table"]["rows"]
                   if row.get("stratum") == "external_wikipedia"]
    blob = json.dumps(fixture_ext, ensure_ascii=False)
    rec("T2 no sentinel (etymology/examples, inline, multiline, "
        "vertical) appears in any emitted field",
        not any(s in blob for s in SENTINELS))
    rec("T2 root/meaning/origin content IS carried",
        all(tok in blob for tok in
            ("alpha meaning", "beta meaning", "gamma meaning",
             "zzalpha", "zzbeta", "zzgamma")))

    # ---- T3: zero adapted + closed normalization list
    rec("T3 adapted is False on every imported row (real + "
        "fixture)",
        all(row.get("adapted") is False for row in ext)
        and all(row.get("adapted") is False
                for row in fixture_ext))
    ops_ok = all(
        op in imp.ALLOWED_OPS
        for row in ext + fixture_ext
        for ops in (row.get("changed_fields") or {}).values()
        for op in ops)
    rec("T3 changed_fields name only ALLOWED_OPS", ops_ok)
    delta = [row for row in fixture_ext
             if row["piece"] == "zzdelta"]
    rec("T3 marked-up gloss cleans to exactly the carried text",
        len(delta) == 1
        and delta[0]["sense"] == "bold linked meaning",
        f"{[d['sense'] for d in delta]}")

    # ---- T4: precedence -- external never wins
    rec("T4 loader precedence ends at external_wikipedia",
        lm_table.PRECEDENCE[-1] == "external_wikipedia")
    by_piece = {}
    for row in rows:
        by_piece.setdefault(row["piece"], []).append(row)
    overlap = [p for p, grows in by_piece.items()
               if any(g["stratum"] == "external_wikipedia"
                      for g in grows)
               and any(g["stratum"] != "external_wikipedia"
                       for g in grows)]
    rank_of = {s: i for i, s in enumerate(lm_table.PRECEDENCE)}
    order_ok = bool(overlap)
    for piece in overlap:
        got = lm_table.lookup(piece, table=v2)
        ranks = [(g["stratum"] == "external_wikipedia",
                  g["precedence_rank"]) for g in got]
        ext_ranks = [rk for is_ext, rk in ranks if is_ext]
        other_ranks = [rk for is_ext, rk in ranks if not is_ext]
        if not (max(other_ranks) < min(ext_ranks)):
            order_ok = False
    rec("T4 for every overlapping piece, external rows rank "
        "below all in-repo rows", order_ok,
        f"overlapping pieces: {len(overlap)}")
    fz = lm_table.lookup("zzalpha", table=built["table"])
    rec("T4 fixture lookup returns in-repo first, external last",
        len(fz) == 2 and fz[0]["stratum"] == "inrepo"
        and fz[-1]["stratum"] == "external_wikipedia")

    # ---- T5: quarantine
    quar_ok = True
    for piece in QUARANTINED:
        for row in by_piece.get(piece, []):
            if row["position_class"] != "position_unresolved":
                quar_ok = False
    rec("T5 quarantined pieces are position_unresolved on every "
        "row (incl. external)", quar_ok)
    rec("T5 external rows exist for a quarantined piece (man/re) "
        "and are quarantined",
        any(row["piece"] in QUARANTINED for row in ext))
    zzroot = [row for row in fixture_ext
              if row["piece"] == "zzroot"]
    rec("T5 synthetic new position collision joins quarantine",
        len(zzroot) == 1
        and zzroot[0]["position_class"] == "position_unresolved"
        and zzroot[0]["authored_position_class"] == "prefix")
    zzbeta = [row for row in fixture_ext
              if row["piece"] == "zzbeta"]
    rec("T5 non-colliding external row keeps its mapped position",
        len(zzbeta) == 1
        and zzbeta[0]["position_class"] == "prefix")

    # ---- T6: lineage / export classification
    one_ext = [dict(ext[0])]
    cls = imp.classify_export(one_ext)
    rec("T6 complete-lineage external set classifies "
        "unchanged_quote with license notice",
        cls["classification"] == "unchanged_quote"
        and any("CC BY-SA" in n for n in cls["notices"]))
    stripped = [dict(ext[0])]
    del stripped[0]["source_revid"]
    try:
        imp.classify_export(stripped)
        refused = False
    except imp.ExportRefused:
        refused = True
    rec("T6 set with stripped provenance is REFUSED", refused)
    adapted = [dict(ext[0], adapted=True)]
    rec("T6 adapted row forces derived_adaptation",
        imp.classify_export(adapted)["classification"]
        == "derived_adaptation")
    inrepo_only = [row for row in rows
                   if row["stratum"] == "ace_seed"][:2]
    rec("T6 in-repo rows alone classify independent",
        imp.classify_export(inrepo_only)["classification"]
        == "independent")

    # ---- T7: v1 integrity + loader paths
    v1_path = os.path.join(_HERE, "mandell", "lm_table_v1.json")
    v1_hash = hashlib.sha256(open(v1_path, "rb").read()).hexdigest()
    rec("T7 lm_table_v1.json sha256 == pre-import pin",
        v1_hash == V1_SHA256, v1_hash)
    rec("T7 default load returns v2; explicit v1 path returns v1",
        header.get("version") == 2
        and lm_table.load_table(path=v1_path)["header"]
        .get("version") == 1)
    tmp = tempfile.mkdtemp(prefix="lm1_import_t7_")
    try:
        mod_dir = os.path.join(tmp, "mandell")
        os.makedirs(mod_dir)
        shutil.copy(os.path.join(_HERE, "mandell", "lm_table.py"),
                    os.path.join(mod_dir, "lm_table.py"))
        shutil.copy(v1_path, os.path.join(mod_dir,
                                          "lm_table_v1.json"))
        shutil.copy(os.path.join(_HERE, "mandell",
                                 "lm_table_v1.collisions.json"),
                    os.path.join(mod_dir,
                                 "lm_table_v1.collisions.json"))
        spec = importlib.util.spec_from_file_location(
            "lm_table_v1_only", os.path.join(mod_dir,
                                             "lm_table.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        t = mod.load_table()
        rec("T7 v2-absent fallback returns v1 exactly (158 rows, "
            "no external stratum)",
            t["header"]["version"] == 1 and len(t["rows"]) == 158
            and not any(row["stratum"] == "external_wikipedia"
                        for row in t["rows"]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    rec("T7 absent table still loads empty without raising",
        lm_table.load_table(path=os.path.join(
            _HERE, "mandell", "lm_table_v2.MISSING.json"))
        == {"header": None, "rows": []})

    # ---- T8: cardinality reconciliation
    try:
        imp.validate_table(v2)
        valid = True
    except imp.ImportAbort:
        valid = False
    rec("T8 shipped artifact validates against its ledger",
        valid)
    tampered = copy.deepcopy(v2)
    tampered["rows"] = [row for row in tampered["rows"]
                        if row.get("stratum")
                        != "external_wikipedia"] + \
        [row for row in tampered["rows"]
         if row.get("stratum") == "external_wikipedia"][1:]
    try:
        imp.validate_table(tampered)
        tamper_caught = False
    except imp.ImportAbort:
        tamper_caught = True
    rec("T8 silently dropped external row fails validation",
        tamper_caught)
    tot = built["ledger"]["totals"]
    rec("T8 fixture ledger balances (source = parsed + invalid "
        "+ excluded; totals 6/6/0/0)",
        tot["source_rows"] == tot["parsed_rows"]
        + tot["invalid_rows"] + tot["license_excluded_rows"]
        and tot["source_rows"] == 6
        and tot["emitted_pieces"] == 6)

    # ---- T9: partial coverage honesty
    built_partial = _fixture_build(verified_b=False)
    cov = built_partial["table"]["header"]["coverage"]
    b_rows = [row for row in built_partial["table"]["rows"]
              if row.get("source_page")
              == imp.page_title("B")]
    rec("T9 license-excluded page -> coverage PARTIAL naming it, "
        "no rows from it",
        cov["status"] == "PARTIAL"
        and cov["excluded_pages"] == [imp.page_title("B")]
        and b_rows == [])
    rec("T9 fixture ledger counts the excluded page's rows",
        built_partial["ledger"]["totals"]
        ["license_excluded_rows"] == 1)
    lying = copy.deepcopy(built_partial["table"])
    lying["header"]["coverage"]["status"] = "COMPLETE"
    try:
        imp.validate_table(lying)
        lie_caught = False
    except imp.ImportAbort:
        lie_caught = True
    rec("T9 COMPLETE claim over exclusions fails validation",
        lie_caught)

    # ---- T10: no-write-on-failure
    tmp = tempfile.mkdtemp(prefix="lm1_import_t10_")
    try:
        tpath = os.path.join(tmp, "lm_table_v2.json")
        cpath = os.path.join(tmp, "lm_table_v2.collisions.json")
        with open(tpath, "wb") as f:
            f.write(b"PREVIOUS-ARTIFACT")
        bad = [_payload("A", PAGE_A_WIKITEXT, revid=999999999)]
        try:
            imp.run_build(bad, RIGHTS, "2026-11-11T00:00:00Z",
                          _fixture_v1_doc(), table_path=tpath,
                          collisions_path=cpath)
            aborted = False
        except imp.ImportAbort:
            aborted = True
        rec("T10 gate failure aborts and leaves the previous "
            "artifact byte-identical, no partial artifact",
            aborted
            and open(tpath, "rb").read() == b"PREVIOUS-ARTIFACT"
            and not os.path.exists(cpath))
        os.unlink(tpath)
        try:
            imp.run_build(bad, RIGHTS, "2026-11-11T00:00:00Z",
                          _fixture_v1_doc(), table_path=tpath,
                          collisions_path=cpath)
            aborted2 = False
        except imp.ImportAbort:
            aborted2 = True
        rec("T10 failed build creates no artifact where none "
            "existed", aborted2 and not os.path.exists(tpath))
        good = [_payload("A", PAGE_A_WIKITEXT),
                _payload("B", PAGE_B_WIKITEXT)]
        imp.run_build(good, RIGHTS, "2026-11-11T00:00:00Z",
                      _fixture_v1_doc(), table_path=tpath,
                      collisions_path=cpath)
        rec("T10 successful build writes both artifacts "
            "atomically",
            os.path.exists(tpath) and os.path.exists(cpath)
            and json.load(open(tpath))["header"]["version"] == 2)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # ---- T-A..T-E: pair-atomic publish (Director HOLD repair)
    def _mk_pair_dir(tag):
        ptmp = tempfile.mkdtemp(prefix=f"lm1_import_{tag}_")
        mod_dir = os.path.join(ptmp, "mandell")
        os.makedirs(mod_dir)
        for name in ("lm_table.py", "lm_table_v1.json",
                     "lm_table_v1.collisions.json"):
            shutil.copy(os.path.join(_HERE, "mandell", name),
                        os.path.join(mod_dir, name))
        return ptmp, mod_dir

    def _load_pair_mod(mod_dir, tag):
        spec = importlib.util.spec_from_file_location(
            f"lm_table_pair_{tag}",
            os.path.join(mod_dir, "lm_table.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def _gen_payloads(tag):
        # The tag must move BOTH members of the pair: "eta
        # meaning" (zzeta, external-only) changes the table,
        # while "alpha meaning" (zzalpha, colliding with the
        # in-repo fixture row) changes the collisions log.
        return [_payload("A", PAGE_A_WIKITEXT.replace(
                    "alpha meaning", "alpha meaning" + tag)),
                _payload("B", PAGE_B_WIKITEXT.replace(
                    "eta meaning", "eta meaning" + tag))]

    def _pair_paths(mod_dir):
        return (os.path.join(mod_dir, "lm_table_v2.json"),
                os.path.join(mod_dir,
                             "lm_table_v2.collisions.json"))

    def _served_sense(mod):
        t = mod.load_table()
        got = [row["sense"] for row in t["rows"]
               if row["piece"] == "zzeta"
               and row["stratum"] == "external_wikipedia"]
        return got[0] if got else None

    def _refused(mod, fn):
        try:
            fn()
            return False
        except mod.PairInconsistentError:
            return True

    # ---- T-A: injected failure between the two replaces
    tmp, mod_dir = _mk_pair_dir("ta")
    try:
        tpath, cpath = _pair_paths(mod_dir)
        imp.run_build(_gen_payloads(""), RIGHTS,
                      "2026-11-11T00:00:00Z", _fixture_v1_doc(),
                      table_path=tpath, collisions_path=cpath)
        mod = _load_pair_mod(mod_dir, "ta")
        gen1_table = open(tpath, "rb").read()
        gen1_coll = open(cpath, "rb").read()
        rec("T-A setup: generation 1 pair serves consistently",
            _served_sense(mod) == "eta meaning")

        def _crash(point):
            if point == "after_collisions_replace":
                raise RuntimeError("injected mid-publish crash")

        try:
            imp.run_build(_gen_payloads(" v2"), RIGHTS,
                          "2026-11-11T00:00:00Z",
                          _fixture_v1_doc(), table_path=tpath,
                          collisions_path=cpath, fault=_crash)
            crashed = False
        except RuntimeError:
            crashed = True
        rec("T-A crash lands between replaces (collisions new, "
            "table still generation 1)",
            crashed
            and open(cpath, "rb").read() != gen1_coll
            and open(tpath, "rb").read() == gen1_table)
        rec("T-A reader fails closed on the mixed pair -- it is "
            "never served",
            _refused(mod, mod.load_table)
            and _refused(mod, mod.load_collisions))
        rec("T-A previous pair retained as build-area .prev "
            "recovery copies",
            open(tpath + ".prev", "rb").read() == gen1_table
            and open(cpath + ".prev", "rb").read() == gen1_coll)

        # ---- T-E (in-process): re-run converges the pair
        imp.run_build(_gen_payloads(" v2"), RIGHTS,
                      "2026-11-11T00:00:00Z", _fixture_v1_doc(),
                      table_path=tpath, collisions_path=cpath)
        rec("T-E re-run after the crash converges; reader serves "
            "generation 2 with its collisions",
            _served_sense(mod) == "eta meaning v2"
            and isinstance(mod.load_collisions(), list))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # ---- T-B: process interruption (SIGKILL mid-publish)
    tmp, mod_dir = _mk_pair_dir("tb")
    try:
        tpath, cpath = _pair_paths(mod_dir)
        imp.run_build(_gen_payloads(""), RIGHTS,
                      "2026-11-11T00:00:00Z", _fixture_v1_doc(),
                      table_path=tpath, collisions_path=cpath)
        gen1_table = open(tpath, "rb").read()
        gen1_coll = open(cpath, "rb").read()
        spec_path = os.path.join(tmp, "spec.json")
        with open(spec_path, "w", encoding="utf-8") as f:
            json.dump({"v1_doc": _fixture_v1_doc(),
                       "payloads": [
                           {"letter": "A",
                            "wikitext": PAGE_A_WIKITEXT.replace(
                                "alpha meaning",
                                "alpha meaning v2")},
                           {"letter": "B",
                            "wikitext": PAGE_B_WIKITEXT.replace(
                                "eta meaning", "eta meaning v2")}]},
                      f)
        driver = os.path.join(tmp, "driver.py")
        with open(driver, "w", encoding="utf-8") as f:
            f.write(_DRIVER_SRC)
        marker = os.path.join(tmp, "marker")
        env = dict(os.environ)
        env["LM1_IMPORT_FAULT"] = "sleep:after_collisions_replace"
        env["LM1_IMPORT_FAULT_MARKER"] = marker
        proc = subprocess.Popen(
            [sys.executable, driver, _ROOT, spec_path, tpath,
             cpath],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, env=env)
        deadline = time.time() + 30
        while not os.path.exists(marker) \
                and proc.poll() is None and time.time() < deadline:
            time.sleep(0.05)
        parked = os.path.exists(marker)
        mid_mixed = parked \
            and open(cpath, "rb").read() != gen1_coll \
            and open(tpath, "rb").read() == gen1_table
        proc.kill()
        proc.communicate(timeout=15)
        rec("T-B importer killed mid-publish: collisions new, "
            "table still generation 1", parked and mid_mixed)
        mod = _load_pair_mod(mod_dir, "tb")
        rec("T-B reader fails closed after the kill -- the mixed "
            "pair is never served",
            _refused(mod, mod.load_table)
            and _refused(mod, mod.load_collisions))

        # ---- T-E (subprocess): a clean re-run converges
        env2 = dict(os.environ)
        env2.pop("LM1_IMPORT_FAULT", None)
        env2.pop("LM1_IMPORT_FAULT_MARKER", None)
        done = subprocess.run(
            [sys.executable, driver, _ROOT, spec_path, tpath,
             cpath],
            capture_output=True, text=True, timeout=120, env=env2)
        rec("T-E clean re-run in a new process converges; reader "
            "serves generation 2",
            done.returncode == 0
            and "DRIVER DONE" in done.stdout
            and _served_sense(mod) == "eta meaning v2")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # ---- T-C: v1 concurrent mutation before commit
    tmp, mod_dir = _mk_pair_dir("tc")
    try:
        tpath, cpath = _pair_paths(mod_dir)
        imp.run_build(_gen_payloads(""), RIGHTS,
                      "2026-11-11T00:00:00Z", _fixture_v1_doc(),
                      table_path=tpath, collisions_path=cpath)
        gen1_table = open(tpath, "rb").read()
        gen1_coll = open(cpath, "rb").read()
        v1p = os.path.join(mod_dir, "lm_table_v1.json")
        expected = hashlib.sha256(
            open(v1p, "rb").read()).hexdigest()

        def _mutate(point):
            if point == "staged":
                with open(v1p, "ab") as f:
                    f.write(b" ")

        try:
            imp.run_build(_gen_payloads(" v2"), RIGHTS,
                          "2026-11-11T00:00:00Z",
                          _fixture_v1_doc(), table_path=tpath,
                          collisions_path=cpath, v1_path=v1p,
                          expected_v1_sha256=expected,
                          fault=_mutate)
            aborted = False
        except imp.ImportAbort:
            aborted = True
        rec("T-C v1 mutation after staging aborts the build "
            "before publish", aborted)
        rec("T-C abort publishes NOTHING: pair byte-identical, "
            "no .prev written, no staged temp left behind",
            open(tpath, "rb").read() == gen1_table
            and open(cpath, "rb").read() == gen1_coll
            and not os.path.exists(tpath + ".prev")
            and not glob.glob(os.path.join(mod_dir, "*.tmp-*")))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    tmp, mod_dir = _mk_pair_dir("tc2")
    try:
        tpath, cpath = _pair_paths(mod_dir)
        v1p = os.path.join(mod_dir, "lm_table_v1.json")
        expected = hashlib.sha256(
            open(v1p, "rb").read()).hexdigest()

        def _mutate2(point):
            if point == "staged":
                with open(v1p, "ab") as f:
                    f.write(b" ")

        try:
            imp.run_build(_gen_payloads(""), RIGHTS,
                          "2026-11-11T00:00:00Z",
                          _fixture_v1_doc(), table_path=tpath,
                          collisions_path=cpath, v1_path=v1p,
                          expected_v1_sha256=expected,
                          fault=_mutate2)
            aborted2 = False
        except imp.ImportAbort:
            aborted2 = True
        rec("T-C aborted first build creates no artifact where "
            "none existed",
            aborted2 and not os.path.exists(tpath)
            and not os.path.exists(cpath))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # ---- T-D: reader consistency under hand corruption
    tmp, mod_dir = _mk_pair_dir("td")
    try:
        tpath, cpath = _pair_paths(mod_dir)
        imp.run_build(_gen_payloads(""), RIGHTS,
                      "2026-11-11T00:00:00Z", _fixture_v1_doc(),
                      table_path=tpath, collisions_path=cpath)
        mod = _load_pair_mod(mod_dir, "td")
        good_table = open(tpath, "rb").read()
        good_coll = open(cpath, "rb").read()
        doc = json.loads(good_table)
        doc["header"]["pair"]["collisions_sha256"] = "0" * 64
        with open(tpath, "wb") as f:
            f.write(imp._serialize(doc))
        rec("T-D flipped binding hash in the table is detected",
            _refused(mod, mod.load_table))
        with open(tpath, "wb") as f:
            f.write(good_table)
        with open(cpath, "ab") as f:
            f.write(b" ")
        rec("T-D byte-appended collisions file is detected by "
            "both readers",
            _refused(mod, mod.load_table)
            and _refused(mod, mod.load_collisions))
        with open(cpath, "wb") as f:
            f.write(good_coll)
        doc = json.loads(good_table)
        doc["header"]["pair"]["generation"] = "f" * 64
        with open(tpath, "wb") as f:
            f.write(imp._serialize(doc))
        rec("T-D flipped generation id is detected",
            _refused(mod, mod.load_table))
        with open(tpath, "wb") as f:
            f.write(good_table)
        rec("T-D restored pair verifies and serves again",
            _served_sense(mod) == "eta meaning")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"    coverage: {header['coverage']['status']}; "
          f"external rows {len(ext)}; totals "
          f"{manifest['ledger_totals']}")
    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
