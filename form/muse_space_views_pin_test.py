"""GP-E25 C1 -- views CLI pin wiring (Director BUILD AUTHORIZATION
7136743763 on PR #510, chat Director).

C1 wires an OPTIONAL explicit pin through the S2 views CLI
(form.muse_space_views). The snapshot library (S1/S3) already
accepts a pin and provides revalidate() / offline_status(); before
C1 the views CLI called build_snapshot(args.root) with no pin and
its export omitted both verdicts, so a reader could not tell which
revision the page describes or whether that revision is still
current.

Contract pinned here, exercised through the USER-FACING CLI
(python3 -m form.muse_space_views), not only library calls:

  * --pin <current HEAD> exports with revalidation verdict CURRENT
    and a numeric offline age.
  * --pin <older commit whose sources changed on HEAD> exports
    with verdict STALE, the changed source named STALE.
  * --pin <unresolvable> is the library's existing typed refusal:
    exit 2, PIN UNAVAILABLE on stderr, no export files written.
  * --pin "" (explicitly supplied empty value) is refused the same
    way: argparse distinguishes it from an omitted --pin, and it
    must never silently resolve to HEAD and export under HEAD's
    attribution.
  * A snapshot with no Git evidence (unpinned fallback) reports
    EVIDENCE_UNAVAILABLE -- provably distinct from STALE -- and
    its offline age is unavailable, never fabricated.
  * The default invocation (no --pin) is preserved, and the
    snapshot's canonical identity is untouched by the wiring: the
    exported snapshot JSON is byte-for-byte the library model.
  * The export surfaces pin + revalidation verdict + offline age
    in a provenance record (muse_space_provenance.json) and in the
    HTML page's Snapshot Provenance section.

Fixtures are synthetic dated git repos (the muse_space_test
pattern): pins and ages are known by construction, never read from
the ambient checkout. Written failing-first: at main the views CLI
has no --pin and writes no provenance, so every check is RED.
"""
import hashlib
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


# ---- synthetic dated git fixtures (muse_space_test pattern) --------

def _fx_git_on(root, date_iso, *args):
    env = dict(os.environ)
    env["GIT_AUTHOR_DATE"] = date_iso
    env["GIT_COMMITTER_DATE"] = date_iso
    return subprocess.run(["git", "-C", root] + list(args),
                          capture_output=True, text=True, env=env)


def _fx_write(root, rel, data):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as fh:
        fh.write(data)


def _fx_commit_all_on(root, date_iso, msg):
    _fx_git_on(root, date_iso, "add", "-A")
    _fx_git_on(root, date_iso, "commit", "-q", "-m", msg)
    return _fx_git_on(root, date_iso, "rev-parse", "HEAD").stdout.strip()


def make_dated_repo(snap, td):
    """Two dated commits: pin_old (2026-11-10, full register),
    pin_new (2026-11-20, register cut to 3 rows) as HEAD.
    Returns (root, pin_old, pin_new, rows)."""
    root = os.path.join(td, "fx")
    os.makedirs(root)
    _fx_git_on(root, "2026-11-10T00:00:00+00:00", "init", "-q")
    _fx_git_on(root, "2026-11-10T00:00:00+00:00",
               "config", "user.email", "fixture@example.invalid")
    _fx_git_on(root, "2026-11-10T00:00:00+00:00",
               "config", "user.name", "Muse Space Fixture")
    with open(os.path.join(ROOT, MWL_REL), encoding="utf-8") as fh:
        rows = json.load(fh)
    for rel in snap.INPUTS.values():
        with open(os.path.join(ROOT, rel), "rb") as fh:
            _fx_write(root, rel, fh.read())
    pin_old = _fx_commit_all_on(root, "2026-11-10T00:00:00+00:00",
                                 "dated fixture A")
    _fx_write(root, MWL_REL, json.dumps(rows[:3]).encode("utf-8"))
    pin_new = _fx_commit_all_on(root, "2026-11-20T00:00:00+00:00",
                                 "dated fixture B")
    return root, pin_old, pin_new, rows


def make_plain_dir(snap, td):
    """The canonical inputs in a plain directory with NO git
    history: the unpinned fallback, where no pin evidence exists."""
    root = os.path.join(td, "plain")
    for rel in snap.INPUTS.values():
        with open(os.path.join(ROOT, rel), "rb") as fh:
            _fx_write(root, rel, fh.read())
    return root


def run_views_cli(root, out, pin=None):
    argv = [sys.executable, "-m", "form.muse_space_views",
            "--root", root, "--out", out]
    if pin is not None:
        argv += ["--pin", pin]
    return subprocess.run(argv, cwd=ROOT, capture_output=True,
                          text=True)


def read_export(out):
    prov = snapj = html = None
    p = os.path.join(out, "muse_space_provenance.json")
    if os.path.isfile(p):
        with open(p, encoding="utf-8") as fh:
            prov = json.load(fh)
    s = os.path.join(out, "muse_space_snapshot.json")
    if os.path.isfile(s):
        with open(s, encoding="utf-8") as fh:
            snapj = json.load(fh)
    h = os.path.join(out, "index.html")
    if os.path.isfile(h):
        with open(h, encoding="utf-8") as fh:
            html = fh.read()
    return prov, snapj, html


def main():
    import importlib
    try:
        snap = importlib.import_module("form.muse_space_snapshot")
    except Exception as exc:
        check("c1_snapshot_module_importable", False, repr(exc))
        return finish()
    check("c1_snapshot_module_importable", True)

    td = tempfile.TemporaryDirectory()
    fx, pin_old, pin_new, rows = make_dated_repo(snap, td.name)

    # ---- current pin ------------------------------------------------
    out = os.path.join(td.name, "out_current")
    cli = run_views_cli(fx, out, pin=pin_new)
    prov, snapj, html = read_export(out)
    check("c1_cli_current_pin_verdict_current",
          cli.returncode == 0 and prov is not None and
          prov.get("pin") == pin_new and
          prov.get("revalidation", {}).get("overall") == "CURRENT" and
          prov.get("revalidation", {}).get("pinned_main_sha") == pin_new and
          prov.get("revalidation", {}).get("current_main_sha") == pin_new and
          html is not None and pin_new in html and "CURRENT" in html,
          "an explicit pin at HEAD exports CURRENT, naming the pin "
          "in the provenance record and on the page")

    # ---- default invocation preserved -------------------------------
    out = os.path.join(td.name, "out_default")
    cli = run_views_cli(fx, out)
    prov, snapj, html = read_export(out)
    check("c1_cli_default_invocation_preserved",
          cli.returncode == 0 and prov is not None and
          prov.get("pin") == pin_new and
          prov.get("revalidation", {}).get("overall") == "CURRENT" and
          snapj is not None and
          snapj.get("source_main_sha") == pin_new,
          "no --pin still pins at HEAD and exports the verdicts; "
          "the ordinary invocation is unchanged in shape")

    # ---- stale pin ----------------------------------------------------
    out = os.path.join(td.name, "out_stale")
    cli = run_views_cli(fx, out, pin=pin_old)
    prov, snapj, html = read_export(out)
    rev = (prov or {}).get("revalidation", {})
    check("c1_cli_stale_pin_verdict_stale",
          cli.returncode == 0 and prov is not None and
          prov.get("pin") == pin_old and
          rev.get("overall") == "STALE" and
          rev.get("pinned_main_sha") == pin_old and
          rev.get("current_main_sha") == pin_new and
          rev.get("sources", {}).get(
              "master_work_list", {}).get("status") == "STALE" and
          html is not None and pin_old in html and "STALE" in html,
          "an older pin whose register changed on HEAD exports "
          "STALE with the changed source named -- provably stale, "
          "not a guess")

    # ---- bad pin: existing typed refusal ------------------------------
    out = os.path.join(td.name, "out_bad")
    cli = run_views_cli(fx, out, pin="0" * 40)
    check("c1_cli_bad_pin_typed_refusal",
          cli.returncode == 2 and "PIN UNAVAILABLE" in cli.stderr and
          not os.path.exists(os.path.join(out, "index.html")) and
          not os.path.exists(os.path.join(
              out, "muse_space_snapshot.json")) and
          not os.path.exists(os.path.join(
              out, "muse_space_provenance.json")),
          "an unresolvable explicit pin is refused by name (exit "
          "2, PIN UNAVAILABLE) and writes no export at all")

    # ---- empty pin: explicit empty value, NOT an omitted --pin -------
    out = os.path.join(td.name, "out_empty")
    cli = run_views_cli(fx, out, pin="")
    check("c1_cli_empty_pin_typed_refusal",
          cli.returncode == 2 and "PIN UNAVAILABLE" in cli.stderr and
          not os.path.exists(os.path.join(out, "index.html")) and
          not os.path.exists(os.path.join(
              out, "muse_space_snapshot.json")) and
          not os.path.exists(os.path.join(
              out, "muse_space_provenance.json")),
          "an explicitly supplied empty --pin is refused by name "
          "(exit 2, PIN UNAVAILABLE) and writes no export at all -- "
          "it never silently resolves to HEAD, unlike an omitted "
          "--pin")

    # ---- stale vs unavailable evidence --------------------------------
    plain = make_plain_dir(snap, td.name)
    out = os.path.join(td.name, "out_plain")
    cli = run_views_cli(plain, out)
    prov, snapj, html = read_export(out)
    check("c1_unavailable_evidence_is_not_stale",
          cli.returncode == 0 and prov is not None and
          prov.get("pin") == "EVIDENCE_UNAVAILABLE" and
          prov.get("revalidation", {}).get("overall") ==
          "EVIDENCE_UNAVAILABLE" and
          prov.get("revalidation", {}).get("overall") != "STALE" and
          prov.get("offline", {}).get("snapshot_age_seconds") is None and
          html is not None and "unavailable" in html,
          "with no Git evidence the export says EVIDENCE_UNAVAILABLE "
          "and shows the age as unavailable -- never STALE, never a "
          "fabricated age")

    # ---- offline snapshot: age surfaced, actions disabled -------------
    out_old = os.path.join(td.name, "out_off_old")
    run_views_cli(fx, out_old, pin=pin_old)
    prov_old, _, html_old = read_export(out_old)
    out_new = os.path.join(td.name, "out_off_new")
    run_views_cli(fx, out_new, pin=pin_new)
    prov_new, _, _ = read_export(out_new)
    off_old = (prov_old or {}).get("offline", {})
    off_new = (prov_new or {}).get("offline", {})
    check("c1_offline_snapshot_age_surfaced",
          off_old.get("mode") == "OFFLINE" and
          off_old.get("authority_actions_enabled") is False and
          isinstance(off_old.get("snapshot_age_seconds"), int) and
          isinstance(off_new.get("snapshot_age_seconds"), int) and
          off_old["snapshot_age_seconds"] >
          off_new["snapshot_age_seconds"] > 0 and
          html_old is not None and "OFFLINE" in html_old,
          "the offline descriptor rides the export: mode OFFLINE, "
          "authority actions disabled, and a real age that grows "
          "with the pin's age")

    # ---- provenance shape on the page and in the record ---------------
    prov, snapj, html = read_export(os.path.join(td.name, "out_stale"))
    check("c1_export_provenance_fields_present",
          prov is not None and
          all(k in prov for k in ("pin", "revalidation", "offline")) and
          all(k in prov["revalidation"] for k in
              ("overall", "current_main_sha", "pinned_main_sha",
               "sources")) and
          all(k in prov["offline"] for k in
              ("mode", "as_of", "snapshot_time",
               "snapshot_age_seconds", "authority_actions_enabled")) and
          html is not None and "Snapshot Provenance" in html and
          prov["pin"] in html and
          str(prov["offline"]["snapshot_age_seconds"]) in html,
          "the export carries pin, revalidation verdict (overall + "
          "per-source), and offline age in the provenance record "
          "and on the rendered page")

    # ---- canonical identity untouched by the wiring -------------------
    # The export file is the canonical body itself (the identity is
    # computed over it, so it is not a field inside it -- the
    # pre-existing export shape). Preservation means: the file is
    # byte-for-byte the library model's canonical body, and the
    # library's content identity verifies against those bytes.
    lib_model = snap.build_snapshot(fx, pin=pin_old)
    _, snapj, _ = read_export(os.path.join(td.name, "out_stale"))
    recomputed = None
    if snapj is not None:
        recomputed = hashlib.sha256(
            snap.canonical_bytes(snapj)).hexdigest()
    check("c1_canonical_identity_preserved",
          snapj is not None and
          snapj.get("source_main_sha") == pin_old and
          snapj == json.loads(snap.canonical_bytes(lib_model)) and
          recomputed == lib_model["content_identity"],
          "the exported snapshot JSON is the library model's "
          "canonical body byte-for-byte, and the model's content "
          "identity still verifies against the exported bytes")

    td.cleanup()
    return finish()


def finish():
    n = sum(1 for _, ok in RESULTS if ok)
    print(f"MUSE_SPACE_VIEWS_PIN: {n}/{len(RESULTS)}", flush=True)
    return 0 if n == len(RESULTS) else 1


def smoke():
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
