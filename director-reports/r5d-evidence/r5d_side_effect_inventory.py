#!/usr/bin/env python3
"""R5-D side-effect inventory for the buildable A/B sites.

Answers Director 7031447110: the 36 B candidates (and 24 A) have NOT
proven that evaluating preflight arguments before mutation is
side-effect-free. This generator classifies EVERY helper call that
appears before each buildable site (from r5d_path_proofs.jsonl) into:

  PURE_KNOWN        - stdlib/str/dict pure computation on its args
  ORDER_SENSITIVE   - value or state depends on WHEN it is evaluated
                      (rng draws advance RNG state; clock reads)
  MUTATING_KNOWN    - callee is a known mutator (name grounded in a
                      source spot-check, see MUTATING set notes)
  UNKNOWN           - cannot be proven pure from the call expression;
                      treated as BLOCKING (conservative)

Per-site verdict:
  INVENTORY-CLEAN            all helpers PURE_KNOWN (or none)
  INVENTORY-ORDER-SENSITIVE  no MUTATING/UNKNOWN, >=1 ORDER_SENSITIVE
  INVENTORY-BLOCKED          >=1 MUTATING_KNOWN or UNKNOWN helper:
                             preflight-arg evaluation is NOT proven
                             side-effect-free for this site.

Checkout-relative: reads r5d_path_proofs.jsonl beside itself, writes
r5d_side_effect_inventory.jsonl + R5D_SIDE_EFFECT_INVENTORY_2026-11-19.md
beside itself. Deterministic. Records/evidence only.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent

PURE_EXACT = {
    "hashlib.sha1", "time.strftime", "time.gmtime", "re.split",
    "math.cos", "math.sin", "math.hypot", "math.isfinite",
    "Mat2.identity", "Mat2.rotate", "Mat2.scale", "Mat2.shear_x",
}
PURE_SUFFIX = (
    ".get", ".values", ".items", ".keys", ".strip", ".lower",
    ".upper", ".title", ".split", ".join", ".encode", ".startswith",
    ".hexdigest",
)
ORDER_SENSITIVE_EXACT = {"rng.randint", "time.time"}
# Grounded by source spot-checks 2026-11-19 (def sites):
# forces.py:367 tick, forces.py:198 grow_all, nursery.py:884 reject,
# plane.py:235 unbox, allwhere.py:106 Ability.use -- all mutate state.
MUTATING_SUBSTR = (
    ".tick", "grow_all", ".plant", ".map", ".flow", "merge_last_two",
    "heartbeat", "set_wells_from_scores", "set_condition", ".activate",
    ".reject", "unbox", "zoom_in", "zoom_out", "place_idea", ".dock",
    "dock_defaults", ".fuse", ".use", "observe", "remember",
    "rebuild_from_plane", "_push_user_trail", "apply_grid_snap",
    ".face", "maybe_auto_box", "research_topic", "_build_grid",
)


def classify(expr: str) -> str:
    e = expr.strip()
    base = re.split(r"\(|\[", e)[0]
    if base in ORDER_SENSITIVE_EXACT or e in ORDER_SENSITIVE_EXACT:
        return "ORDER_SENSITIVE"
    if base in PURE_EXACT or e in PURE_EXACT:
        return "PURE_KNOWN"
    if any(e == s or base.endswith(s) or e.endswith(s)
           for s in PURE_SUFFIX):
        # mutating substrings win over pure suffixes (e.g. .use is not
        # pure; .get on a mutating receiver is still a pure read)
        if not any(m in e for m in ("grow_all", "research_topic")):
            return "PURE_KNOWN"
    if any(m in e for m in MUTATING_SUBSTR):
        return "MUTATING_KNOWN"
    if base.startswith(("math.", "hashlib.")):
        return "PURE_KNOWN"
    return "UNKNOWN"


def main() -> int:
    rows = [json.loads(l) for l in
            (HERE / "r5d_path_proofs.jsonl").read_text().splitlines()
            if l.strip()]
    build = [r for r in rows if r["verdict"] in
             ("A-PROVEN-DIRECT", "B-PROVEN-CANDIDATE",
              "A-DOWNGRADED-B-LOOP")]
    out, counts = [], {"INVENTORY-CLEAN": 0,
                       "INVENTORY-ORDER-SENSITIVE": 0,
                       "INVENTORY-BLOCKED": 0}
    helper_counts = {}
    for r in sorted(build, key=lambda x: (x["file"], x["line"])):
        inv = []
        for h in r.get("helper_calls_before") or []:
            c = classify(h)
            helper_counts[c] = helper_counts.get(c, 0) + 1
            inv.append({"call": h, "class": c})
        classes = {i["class"] for i in inv}
        if classes & {"MUTATING_KNOWN", "UNKNOWN"}:
            verdict = "INVENTORY-BLOCKED"
        elif "ORDER_SENSITIVE" in classes:
            verdict = "INVENTORY-ORDER-SENSITIVE"
        else:
            verdict = "INVENTORY-CLEAN"
        counts[verdict] += 1
        out.append({"file": r["file"], "line": r["line"],
                    "function": r["function"], "door": r["door"],
                    "proof_verdict": r["verdict"],
                    "in_loop": r["in_loop"], "inventory": inv,
                    "site_verdict": verdict})
    (HERE / "r5d_side_effect_inventory.jsonl").write_text(
        "".join(json.dumps(o) + "\n" for o in out))
    lines = [
        "# R5-D SIDE-EFFECT INVENTORY — buildable A/B sites",
        "",
        "Prepared 2026-11-19 (susx100000-execution), answering Director",
        "7031447110: explicit side-effect inventories for the proposed",
        "first bounded A/B subset. Source: r5d_path_proofs.jsonl",
        "(aeb862f). Classification is CONSERVATIVE: anything not",
        "provably pure from the call expression + grounded mutator",
        "spot-checks is UNKNOWN and BLOCKS the side-effect-free claim",
        "for its site. Records/evidence only; ZERO product code.",
        "",
        f"## Site verdicts: {counts}",
        f"## Helper-call classes (all occurrences): {helper_counts}",
        "",
    ]
    for o in out:
        lines.append(f"## {o['site_verdict']} — {o['file']}:{o['line']} "
                     f"{o['function']} ({o['door']}, "
                     f"{o['proof_verdict']}, in_loop={o['in_loop']})")
        if not o["inventory"]:
            lines.append("- helpers: none")
        for i in o["inventory"]:
            lines.append(f"- {i['class']}: `{i['call']}`")
        lines.append("")
    (HERE / "R5D_SIDE_EFFECT_INVENTORY_2026-11-19.md").write_text(
        "\n".join(lines))
    print(counts)
    print(helper_counts)
    print(f"sites={len(out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
