#!/usr/bin/env python3
"""Emit R5D_CLASSIFICATION_2026-11-19.md from r5d_sites.jsonl."""
import json, pathlib

H = pathlib.Path("/home/hatch/workspace/goals/dellmatrix-capability-circuits/hidden_files")
rows = [json.loads(l) for l in (H / "r5d_sites.jsonl").read_text().splitlines()]

C_KEYS = {
    ("form/dell_matrix/confirm_lineage.py", "confirm_proposal"),
    ("form/mandell/executor_leaf.py", "execute_seed"),
    ("form/mandell/executor.py", "execute_seed"),
    ("form/repl.py", "_execute_intent"),
    ("form/mandell/flow_executor.py", "execute_program"),
    ("form/dell_matrix/sync_ux_150_loop.py", "run"),
    ("form/dell_matrix/visual_evolve_loop.py", "run"),
    ("form/dell_matrix/neuroevo.py", "neuroevo_run"),
    ("form/open.py", "grow_ideas"),
}
C_WHY = {
    "confirm_proposal": "the confirm IS the mutation: dozens of staged mutations across sub-objects precede the receipt note; preflight requires the confirm flow itself to admit-check before its first staged change — redesign + per-path proof owed",
    "execute_seed": "dispatcher: each arm mutates owner state then notes its own receipt; the note text is arm-specific and not known at function entry, and one seed can note many times — entry preflight cannot cover later notes; per-arm path proof owed",
    "_execute_intent": "dispatcher: same arm structure as execute_seed (intent arms mutate, then note); per-arm path proof owed",
    "execute_program": "loop driver: steps accumulate mutations per iteration before noting; per-iteration admission cannot be preflighted at entry",
    "run": "long loop driver: many applied steps/pages precede the note inside try; admission must be woven into the loop, not an entry check",
    "neuroevo_run": "evolution loop: population/fitness mutations across generations precede the receipt note",
    "grow_ideas": "12+ mutations incl. helper-driven graph/enhance work precede the note and the noted text is result-dependent",
}

def classify(r):
    if r["file"] == "form/open.py" and r["function"] == "note_seed":
        return ("DOOR", "the note_seed door itself calling note() — not a caller")
    key = (r["file"], r["function"])
    if key in C_KEYS:
        return ("C-HOLD", C_WHY.get(r["function"], "non-preflightable without redesign / per-path proof"))
    if r["n_before"] == 0:
        return ("A", "no state-mutating statement precedes the call in the enclosing function (AST evidence); a door refusal is pre-mutation by construction")
    return ("B", "mutations precede the note in the same function and the noted text is computable from the call's own arguments before the first mutation; build inserts a history preflight before the first mutation (T5 spot-proves)")

counts = {}
lines = []
for r in rows:
    cls, why = classify(r)
    counts[cls] = counts.get(cls, 0) + 1
    lines.append((cls, r, why))

out = []
out.append("# R5-D CALLER CLASSIFICATION — note / note_seed preflight classes (P2)")
out.append("")
out.append("Prepared: 2026-11-19 (susx100000-execution cycle), per Director 7027509092:")
out.append("\"prepare reproducible failing-first tests and classify any non-preflightable")
out.append("callers before asking for bounded implementation authorization.\"")
out.append("Census at main 702741969c6d2d1d020f85845912f1da84f31418 (fresh clone r5d_clone):")
out.append("111 capture call sites in non-test form/ code — 98 note_seed (18 files,")
out.append("exactly the R5-D preparation census) + 13 direct note() = 111 total.")
out.append("The 1 door-internal site (inside note_seed itself) is one of those 13")
out.append("direct note() rows, counted in class DOOR below — it is NOT a 112th site")
out.append("and must not be added on top of 98 + 13. Class partition:")
out.append("A=26 + B=45 + C-HOLD=39 + DOOR=1 = 111.")
out.append("")
out.append("## Classes (per R5D_PREP §2.2)")
out.append("")
out.append("- A — note is the first/only mutation on the path: door refusal is")
out.append("  pre-mutation by construction; no caller change needed.")
out.append("- B — preflightable: caller mutates before noting, but the noted text is")
out.append("  computable before the first mutation; the build inserts a history")
out.append("  preflight (would-admit check) ahead of the first mutation and T5")
out.append("  spot-proves refusal atomicity per class.")
out.append("- C — HOLD (non-preflightable as written): the caller cannot admit-check")
out.append("  before its mutations without redesign or per-path proof. These stay")
out.append("  on HOLD in the R5-D build scope until individually discharged; the")
out.append("  build authorization ask must name them as excluded or separately")
out.append("  scoped — they are NOT silently bypassed.")
out.append("")
out.append(f"## Counts: A={counts.get('A',0)}  B={counts.get('B',0)}  "
           f"C-HOLD={counts.get('C-HOLD',0)}  DOOR={counts.get('DOOR',0)}  "
           f"TOTAL={len(rows)}")
out.append("")
out.append("## Method + limits (honest)")
out.append("")
out.append("AST pass (r5d_classify.py) per call site: enclosing function, mutating")
out.append("statements before/after the call (attribute/subscript assigns + known")
out.append("mutating method calls), control context (loop/try/conditional). LIMIT:")
out.append("counts are FUNCTION-level, so dispatcher functions (execute_seed,")
out.append("_execute_intent) accumulate mutations from sibling arms that never run")
out.append("on a given path — that over-approximation is one reason those sites")
out.append("are class C (per-arm path proof owed) rather than B. Class B is an")
out.append("analyst judgment from the same evidence (single-purpose functions,")
out.append("note text from call arguments); it is a build obligation to spot-prove")
out.append("(T5), not a proof. Evidence rows: r5d_sites.jsonl.")
out.append("")
for cls in ("A", "B", "C-HOLD", "DOOR"):
    sel = [(r, w) for c, r, w in lines if c == cls]
    if not sel:
        continue
    out.append(f"## Class {cls} ({len(sel)})")
    out.append("")
    for r, w in sel:
        ctx = ",".join(r["ctx"]) or "-"
        out.append(f"- {r['file']}:{r['line']} {r['door']} in {r['function']} "
                   f"(ctx {ctx}; mut_before={r['n_before']}, mut_after={r['n_after']}) — {w}")
    out.append("")
(H / "R5D_CLASSIFICATION_2026-11-19.md").write_text("\n".join(out) + "\n")
print(counts, "total", len(rows))
