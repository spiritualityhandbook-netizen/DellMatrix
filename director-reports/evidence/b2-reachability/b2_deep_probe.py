"""B-2 deep per-Dell English reachability probe (G-02) — reproducible.

This is the probe behind DIRECTOR_REPORT_B2_REACHABILITY_VALIDATION.md,
made self-contained for independent replay (Director hourly review
2026-11-04 23:34 CST: INSUFFICIENT_EVIDENCE until the script, complete
JSON + SHA-256, rerun instructions and the 63-ID input list are in the
PR). Changes from the Cycle-6 working-paper original are disclosed in
REPRODUCIBILITY.md: (1) the repo root is resolved relative to this
file (override: B2_REPO env var) instead of a hardcoded worktree path;
(2) the 63-ID input list is embedded below (TARGETS_63, copied from
the SM-14 census NO_ROUTE_FOUND rows) instead of reading an external
census file; (3) the positive controls (8, 12, 51, 28) are run through
the same probe_dell() and recorded in the output JSON, instead of a
separate unrecorded run. The tiers, frames, routing rule and per-Dell
logic are otherwise byte-equivalent to the original.

Tiers (uniform, disclosed, no per-Dell hand-tuning):
  Tier S (static): scan form/mandell/translate.py + phrases.py source
    for the Dell's seed token "N[" and its registry name as a word.
  Tier M (manor verbs): verbs taken mechanically from the Dell's own
    registry "manor" string, plus the Dell name. Frames per verb v:
    "{v} testitem", "{v} the testitem", "please {v} testitem", "{v}".
  Tier N (name forms): "{name} the testitem", "use {name}",
    "use {name} on testitem", "do {name}", "{name} on testitem",
    "{name}s testitem", "{name}ing testitem".

A Dell is ROUTE_FOUND_DEEP when any Tier M/N phrase routes to it
through the real translate() (same routed_dells rule as SM-14).
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.environ.get(
    "B2_REPO",
    os.path.abspath(os.path.join(HERE, "..", "..", "..")))
sys.path.insert(0, REPO)

from form.mandell.phrases import PHRASES  # noqa: F401,E402  (parity import)
from form.mandell.registry import get_dell  # noqa: E402
from form.mandell.translate import translate  # noqa: E402

# The input set: the 63 SM-14 NO_ROUTE_FOUND Dell IDs.
TARGETS_63 = [0, 1, 2, 3, 16, 17, 18, 20, 22, 26, 30, 33, 36, 39, 41,
              43, 44, 45, 49, 52, 53, 54, 55, 57, 59, 60, 61, 62, 63,
              64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77,
              78, 79, 80, 81, 82, 83, 85, 87, 88, 89, 90, 91, 92, 93,
              94, 95, 96, 97, 98, 99]
# Known-reachable Dells run through the identical probe as controls.
POSITIVE_CONTROLS = [8, 12, 51, 28]


def routed_dells(intent):
    out = set()
    if intent is None:
        return out
    if intent.dell is not None:
        out.add(int(intent.dell))
    mandel = intent.mandel or ""
    for m in re.finditer(r"(\d{1,2})\[", mandel):
        out.add(int(m.group(1)))
    return out


def static_scan(dell, name):
    hits = []
    for rel in ("form/mandell/translate.py", "form/mandell/phrases.py"):
        src = open(os.path.join(REPO, rel)).read()
        if re.search(r"(?<!\d)%d\[" % dell, src):
            hits.append(rel + ":seed-token")
        if re.search(r"\b%s\b" % re.escape(name), src, re.I):
            hits.append(rel + ":name-word")
    return hits


def manor_verbs(dell):
    info = get_dell(dell)
    words = re.findall(r"[A-Za-z]+", info["manor"].lower())
    stop = {"a", "the", "on", "of", "to", "per", "not", "no", "or",
            "and", "over", "into", "in", "by", "with", "until"}
    return [w for w in words if w not in stop]


def probe_dell(dell):
    info = get_dell(dell)
    name = info["name"]
    n = name.lower()
    phrases = []
    for v in manor_verbs(dell) + [n]:
        phrases += [f"{v} testitem", f"{v} the testitem",
                    f"please {v} testitem", v]
    phrases += [f"{n} the testitem", f"use {n}", f"use {n} on testitem",
                f"do {n}", f"{n} on testitem", f"{n}s testitem",
                f"{n}ing testitem"]
    seen, uniq = set(), []
    for p in phrases:
        if p not in seen:
            seen.add(p)
            uniq.append(p)
    hit = None
    misroutes = {}
    errors = {}
    for phrase in uniq:
        try:
            intent = translate(phrase)
        except Exception as exc:
            errors[phrase] = str(exc)
            continue
        got = routed_dells(intent)
        if dell in got and hit is None:
            hit = phrase
        for g in got:
            if g != dell:
                misroutes[phrase] = g
    return {
        "dell": dell, "name": name, "manor": info["manor"],
        "static_hits": static_scan(dell, name),
        "phrases_tried": len(uniq),
        "deep_hit": hit,
        "misroutes": misroutes, "errors": errors,
        "verdict": "ROUTE_FOUND_DEEP" if hit else "STILL_NO_ROUTE",
    }


def main():
    rows = [probe_dell(d) for d in TARGETS_63]
    found = [r["dell"] for r in rows if r["verdict"] == "ROUTE_FOUND_DEEP"]
    controls = [probe_dell(d) for d in POSITIVE_CONTROLS]
    out = {"targets": len(TARGETS_63), "route_found_deep": found,
           "still_no_route": [r["dell"] for r in rows
                              if r["verdict"] == "STILL_NO_ROUTE"],
           "rows": rows,
           "positive_controls": controls}
    with open(os.path.join(HERE, "b2_deep_probe.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(f"targets {len(TARGETS_63)}; route_found_deep {found}")
    print("still_no_route:", out["still_no_route"])
    print("controls:", [(c["dell"], c["deep_hit"]) for c in controls])
    print("total phrases (targets):", sum(r["phrases_tried"] for r in rows))
    print("total errors (targets):",
          sum(len(r["errors"]) for r in rows))


if __name__ == "__main__":
    main()
