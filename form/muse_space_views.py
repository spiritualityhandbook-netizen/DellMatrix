"""GP-E25 Muse Space -- S2 static exported view.

Renders the seven views of Edition 1 file 04 section 5 (Blueprint
Map, Two Belts, Connection Web, Sequence, Sync Mirror, Future View,
Pending Edits) from ONE S1 snapshot (form.muse_space_snapshot) as a
single self-contained static HTML export, labeled AS_OF with the
exact pin it was rendered from.

Law carried from file 04: every source string is HTML-escaped
(untrusted text cannot control scripts, M-14); the Two Belts keep
independent denominators and the canonical MWL number displays as
its own strict count -- a belt split that the pinned inputs cannot
derive is shown as EVIDENCE_UNAVAILABLE, never fabricated (s.5B);
the Connection Web discloses drawn/shown/total (M-08); the Future
View carries a persistent PROJECTION watermark and never presents
unbuilt capability as live functionality (s.5F); Pending Edits
drafts stay local -- submission is out of scope until an
authenticated, reviewed connector pathway is independently
validated (build record section 5). The export is read-only: it
writes nothing to the register, GitHub, or the Nursery.

CLI: python3 -m form.muse_space_views [--root PATH] [--out DIR]
     [--pin SHA]
writes <out>/muse_space_snapshot.json, <out>/index.html and
<out>/muse_space_provenance.json.

GP-E25 C1 (Director BUILD AUTHORIZATION 7136743763): an optional
explicit --pin is wired through to the snapshot library, and the
export surfaces the library's existing S3 verdicts -- the pin, the
revalidation verdict (CURRENT / STALE / EVIDENCE_UNAVAILABLE, with
per-source detail), and the offline snapshot age (or unavailable)
-- in the provenance record and on the page, so a reader can tell
which revision the page describes and whether it is still
current. A bad explicit pin is refused by the library's typed
PinUnavailable (exit 2, no export written). The snapshot model
itself is never modified by the wiring: its canonical identity is
preserved byte-for-byte.
"""
import argparse
import html
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from form.muse_space_snapshot import (PinUnavailable, build_snapshot,
                                      canonical_bytes, offline_status,
                                      revalidate)


def esc(value):
    return html.escape(str(value), quote=True)


def _section(title, body):
    return '<section><h2>%s</h2>%s</section>' % (esc(title), body)


def _belts_section(model):
    belts = model["belts"]
    strict = belts["mwl_strict"]
    rows = "".join(
        "<tr><td>%s</td><td>%d</td></tr>" % (esc(k), v)
        for k, v in strict["by_status"].items())
    body = ("<p>Canonical MWL strict count (its own number, not an "
            "average of belts): <strong>%d rows, %d active</strong>.</p>"
            "<table><tr><th>Register status</th><th>Rows</th></tr>%s"
            "</table>" % (strict["rows_total"], strict["active"], rows))
    for name in ("plan", "code"):
        belt = belts[name]
        body += ("<h3>%s belt</h3><p>%s -- %s</p>"
                 % (esc(name.upper()), esc(belt["status"]),
                    esc(belt["reason"])))
    return _section("Two Belts", body)


def _web_section(model):
    edges = model["typed_edges"]
    total = len(edges)
    items = "".join(
        "<li>%s: %s -&gt; %s [%s]</li>"
        % (esc(e["class"]), esc(e["from"]), esc(e["to"]),
           esc(e["confidence"]))
        for e in edges)
    body = ("<p>Edges drawn %d / shown %d / total %d. INFERRED and "
            "PROPOSED edges are labeled and never enter canonical "
            "counts or executable gates.</p><ul>%s</ul>"
            % (total, total, total, items))
    return _section("Connection Web", body)


def export_provenance(model, root, now_iso=None):
    """C1 provenance for one exported snapshot: the pin it was
    rendered from, the S3 revalidation verdict against the
    checkout's current HEAD, and the S3 offline descriptor (mode,
    snapshot age in seconds or None when the snapshot time is not
    evidence, authority actions disabled). The model is read-only
    here -- provenance rides beside it, never inside it, so the
    snapshot's canonical identity is untouched."""
    if now_iso is None:
        now_iso = datetime.now(timezone.utc).isoformat()
    return {
        "pin": model.get("source_main_sha"),
        "revalidation": revalidate(model, root),
        "offline": offline_status(model, now_iso),
    }


def _provenance_section(provenance):
    if provenance is None:
        body = ("<p>Revalidation verdict "
                "<strong>EVIDENCE_UNAVAILABLE</strong> (not performed "
                "for this render); offline snapshot age "
                "unavailable.</p>")
        return _section("Snapshot Provenance", body)
    rev = provenance["revalidation"]
    off = provenance["offline"]
    age = off.get("snapshot_age_seconds")
    age_text = ("%d seconds" % age) if age is not None else "unavailable"
    sources = "".join(
        "<li>%s: %s</li>" % (esc(key), esc(src.get("status", "")))
        for key, src in sorted(rev.get("sources", {}).items()))
    body = (
        "<p>Pin <code>%s</code>. Revalidation verdict "
        "<strong>%s</strong> (pinned main <code>%s</code>, current "
        "main <code>%s</code>). Offline descriptor: mode "
        "<strong>%s</strong>, snapshot age %s, authority actions "
        "enabled: %s.</p><ul>%s</ul>"
        % (esc(provenance.get("pin")), esc(rev.get("overall")),
           esc(rev.get("pinned_main_sha")),
           esc(rev.get("current_main_sha")), esc(off.get("mode")),
           esc(age_text), esc(off.get("authority_actions_enabled")),
           sources))
    return _section("Snapshot Provenance", body)


def render_html(model, provenance=None):
    pin = model["source_main_sha"]
    nodes = model["nodes"]
    by_type = {}
    for node in nodes:
        by_type.setdefault(node["type"], []).append(node)
    map_body = "<p>Nodes drawn %d / shown %d / total %d.</p>" % (
        len(nodes), len(nodes), len(nodes))
    for ntype in sorted(by_type):
        items = "".join(
            "<li><strong>%s</strong> %s</li>"
            % (esc(n["id"]), esc(n.get("label", "")))
            for n in by_type[ntype])
        map_body += "<h3>%s</h3><ul>%s</ul>" % (esc(ntype), items)

    blocks = {}
    for node in nodes:
        if node["type"] == "WORK":
            blocks.setdefault(node.get("block", ""), []).append(node)
    seq_body = "".join(
        "<h3>%s</h3><p>%d work objects</p>"
        % (esc(block or "(unblocked)"), len(items))
        for block, items in blocks.items())

    contradictions = model["contradictions"]
    if contradictions:
        mirror_body = "<ul>%s</ul>" % "".join(
            "<li>[%s] %s</li>" % (esc(c["class"]), esc(c["detail"]))
            for c in contradictions)
    else:
        mirror_body = ("<p>AGREES -- no contradictions detected in "
                       "the pinned inputs at this pin.</p>")

    tally = model["derived_metrics"]["mwl_by_status"]
    open_n = tally.get("OPEN", 0) + tally.get("PARTIAL", 0)
    future_body = (
        '<div class="watermark">PROJECTION</div>'
        "<p>PROJECTION: this view projects intended capability when "
        "plan families close. It is not live functionality and makes "
        "no semantic claims about the current program. Projection "
        "basis at the pin: %d work objects OPEN or PARTIAL in the "
        "canonical register.</p>" % open_n)

    pending_body = (
        "<p>Local drafts only. Drafts never modify canonical truth "
        "and grant no completion. Submission stays disabled: it is "
        "out of scope until an authenticated, reviewed connector "
        "pathway is independently validated (build record "
        "section 5).</p>")

    return (
        "<!DOCTYPE html>\n<html lang=\"en\"><head><meta charset="
        "\"utf-8\"><title>Muse Space -- Living Grand Plan Blueprint"
        "</title><style>.watermark{position:fixed;top:40%%;left:30%%;"
        "font-size:4em;opacity:0.15;transform:rotate(-20deg);"
        "pointer-events:none}</style></head><body>"
        "<h1>Muse Space -- Living Grand Plan Blueprint</h1>"
        "<p>Static export labeled <strong>AS_OF</strong> pin "
        "<code>%s</code>; snapshot time %s; content identity "
        "<code>%s</code>. Read-only witness surface: never a source "
        "of truth.</p>%s%s%s%s%s%s%s%s</body></html>\n"
        % (esc(pin), esc(model["github_snapshot_time"]),
           esc(model["content_identity"]),
           _provenance_section(provenance),
           _section("Blueprint Map", map_body),
           _belts_section(model),
           _web_section(model),
           _section("Sequence", seq_body),
           _section("Sync Mirror", mirror_body),
           _section("Future View", future_body),
           _section("Pending Edits", pending_body)))


def main(argv=None):
    ap = argparse.ArgumentParser(prog="muse_space_views")
    ap.add_argument("--root", default=".")
    ap.add_argument("--out", default="muse_space_export")
    ap.add_argument("--pin", default=None,
                    help="optional explicit snapshot pin (commit "
                         "SHA); an unresolvable pin is refused by "
                         "name and no export is written")
    args = ap.parse_args(argv)
    try:
        model = build_snapshot(args.root, args.pin)
    except PinUnavailable as exc:
        sys.stderr.write("PIN UNAVAILABLE: %s\n" % exc)
        return 2
    provenance = export_provenance(model, args.root)
    os.makedirs(args.out, exist_ok=True)
    snap_path = os.path.join(args.out, "muse_space_snapshot.json")
    with open(snap_path, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(json.loads(canonical_bytes(model)),
                            indent=1, sort_keys=True) + "\n")
    prov_path = os.path.join(args.out, "muse_space_provenance.json")
    with open(prov_path, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(provenance, indent=1, sort_keys=True) + "\n")
    html_path = os.path.join(args.out, "index.html")
    with open(html_path, "w", encoding="utf-8") as fh:
        fh.write(render_html(model, provenance))
    age = provenance["offline"]["snapshot_age_seconds"]
    print("wrote %s, %s and %s (pin %s, identity %s, revalidation "
          "%s, offline age %s)"
          % (snap_path, html_path, prov_path,
             model["source_main_sha"], model["content_identity"],
             provenance["revalidation"]["overall"],
             ("%ds" % age) if age is not None else "unavailable"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
