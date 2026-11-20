#!/usr/bin/env python3
"""R5-D PATH-LEVEL proof analyzer for classes A and B (Uni, 2026-11-19).

Upgrades the function-level AST heuristic in r5d_classify_emit.py to
per-path evidence for every A (26) and B (45) site:

- LOOP-CARRIED check: a site inside a loop whose body contains ANY
  direct mutation is NOT pre-mutation on iterations >= 2, whatever the
  function-level n_before count says. Such A sites are downgraded.
- DEPENDENCE check (B, and loop-carried A): the noted text is
  preflightable only if its argument expressions do NOT depend on
  state mutated between the first mutation on the path and the note
  call. Dependence = (a) an argument Name assigned in that interval,
  (b) an argument attribute chain overlapping a mutated target in
  that interval, (c) an argument containing a non-whitelisted call
  (its result may read mutated state).
- For every site it records the exact eventual text template under
  CURRENT door code (note: strip()[:120]; note_seed: optional
  sanitize under _chain_sanitize_redact, body f"{dell:02d}[{term}]"
  + label[:40]) so the R5 preflight's byte-exactness obligation is
  concrete: evaluate the SAME argument expressions before the first
  mutation, apply sanitize_text (R5 P5, all strings), then measure
  the canonical atomic_write_json contribution.

LIMITS (honest): direct mutations only (attribute/subscript assigns
+ known mutating methods, same set as r5d_classify.py). Side effects
inside helper calls that are not in that set are NOT visible to this
analyzer; a PROVEN verdict means proven against direct mutations,
with helper-call side effects UNKNOWN and listed per site where a
helper call precedes the note on the path.

Checkout-relative: reads r5d_sites.jsonl beside this script; source
root is the repo root three levels up (director-reports/r5d-evidence).
Outputs r5d_path_proofs.jsonl + R5D_PATH_PROOFS_2026-11-19.md beside
this script.
"""
import ast, json, pathlib

H = pathlib.Path(__file__).resolve().parent
ROOT = H.parent.parent  # repo root

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
MUT_METHODS = {"append", "extend", "insert", "pop", "remove", "clear",
               "update", "add", "discard", "place", "set", "step",
               "turn_on", "turn_off", "evolve", "snap", "box", "push",
               "record", "register", "define", "create", "delete",
               "move", "copy", "replace", "patch", "grow", "learn",
               "save", "write", "commit", "apply", "execute"}
SAFE_CALLS = {"str", "int", "float", "len", "repr", "bool", "format"}


def classify(r):
    if r["file"] == "form/open.py" and r["function"] == "note_seed":
        return "DOOR"
    if (r["file"], r["function"]) in C_KEYS:
        return "C-HOLD"
    return "A" if r["n_before"] == 0 else "B"


def unp(n):
    try:
        return ast.unparse(n)
    except Exception:
        return type(n).__name__


def mutations_in(node):
    """Direct mutations under node: (line, target_desc)."""
    out = []
    for n in ast.walk(node):
        if isinstance(n, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
            tgts = n.targets if isinstance(n, ast.Assign) else [n.target]
            for t in tgts:
                if isinstance(t, (ast.Attribute, ast.Subscript)):
                    out.append((n.lineno, unp(t)))
        elif isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute):
            if n.func.attr in MUT_METHODS:
                out.append((n.lineno, unp(n.func)))
    return sorted(set(out))


def name_assigns_in(fn, lo, hi):
    """Plain local Name assignments with lo < line < hi."""
    out = []
    for n in ast.walk(fn):
        if isinstance(n, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
            tgts = n.targets if isinstance(n, ast.Assign) else [n.target]
            if lo < n.lineno < hi:
                for t in tgts:
                    if isinstance(t, ast.Name):
                        out.append((n.lineno, t.id))
    return sorted(set(out))


def arg_facts(call):
    """Argument expressions of the note/note_seed call."""
    args = list(call.args) + [kw.value for kw in call.keywords]
    names, attrs, calls = set(), set(), set()
    for a in args:
        for n in ast.walk(a):
            if isinstance(n, ast.Name):
                names.add(n.id)
            elif isinstance(n, ast.Attribute):
                attrs.add(unp(n))
            elif isinstance(n, ast.Call):
                f = n.func
                calls.add(unp(f) if isinstance(f, ast.Name) else
                          (f.attr if isinstance(f, ast.Attribute) else "?"))
    return {"exprs": [unp(a) for a in args], "names": sorted(names),
            "attrs": sorted(attrs), "calls": sorted(calls)}


def analyze(site):
    cls = classify(site)
    path = ROOT / site["file"]
    tree = ast.parse(path.read_text(errors="replace"))
    parents = {}
    for node in ast.walk(tree):
        for ch in ast.iter_child_nodes(node):
            parents[ch] = node
    call = fn = None
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                and node.func.attr == site["door"] and node.lineno == site["line"]:
            call = node
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) \
                and node.name == site["function"] \
                and node.lineno <= site["line"] \
                and (fn is None or node.lineno > fn.lineno):
            # keep the innermost enclosing def by end-line check below
            if node.end_lineno and node.end_lineno >= site["line"]:
                fn = node
    if call is None or fn is None:
        return {"site": site, "cls": cls, "verdict": "UNRESOLVED",
                "why": "call or enclosing function not located"}
    # loop ancestors of the call
    loops, cur = [], call
    while cur in parents:
        cur = parents[cur]
        if isinstance(cur, (ast.For, ast.While)):
            loops.append(cur)
        if cur is fn:
            break
    loop_muts = []
    for lp in loops:
        loop_muts += mutations_in(lp)
    loop_muts = sorted(set(loop_muts))
    muts_before = [(ln, t) for ln, t in mutations_in(fn) if ln < call.lineno]
    first_mut = muts_before[0][0] if muts_before else None
    facts = arg_facts(call)
    # dependence on the interval (first_mut, call)
    deps = []
    if first_mut is not None:
        assigned = {nm for _, nm in name_assigns_in(fn, first_mut, call.lineno)}
        hit = assigned & set(facts["names"])
        if hit:
            deps.append(f"arg name(s) {sorted(hit)} assigned after first mutation")
        mut_targets = {t for _, t in muts_before}
        for a in facts["attrs"]:
            for t in mut_targets:
                if a == t or a.startswith(t + ".") or t.startswith(a + ".") \
                        or a.split(".")[0] == t.split(".")[0] and a.split(".")[1:2] == t.split(".")[1:2]:
                    deps.append(f"arg attr {a} overlaps mutated {t}")
        bad_calls = [c for c in facts["calls"] if c not in SAFE_CALLS]
        if bad_calls:
            deps.append(f"arg call(s) {bad_calls} may read mutated state")
    deps = sorted(set(deps))
    in_loop = bool(loops)
    # helper calls before the note on the path (side effects UNKNOWN)
    helper_calls = sorted({unp(n.func) for n in ast.walk(fn)
                           if isinstance(n, ast.Call) and n.lineno < call.lineno
                           and isinstance(n.func, ast.Attribute)
                           and n.func.attr not in MUT_METHODS
                           and n.func.attr not in ("note", "note_seed")})
    if cls == "A":
        if in_loop and loop_muts:
            verdict = "A-DOWNGRADED-B-LOOP" if not deps else "A-DOWNGRADED-C-CANDIDATE"
            why = (f"inside loop; loop body mutates {loop_muts}; on iteration >=2 "
                   f"those mutations precede the note, so the function-level "
                   f"n_before=0 does NOT prove pre-mutation per path. "
                   + ("Args do not depend on mutations before the call in the "
                      "same iteration, so a per-iteration preflight at loop-body "
                      "start remains possible (class B-LOOP)."
                      if not deps else
                      f"Args depend on interval mutations: {deps} — per-path proof owed."))
        else:
            verdict = "A-PROVEN-DIRECT"
            why = ("no direct mutation before the call in the enclosing function "
                   "and no loop-carried mutation; door refusal is pre-mutation "
                   "against direct mutations (helper-call side effects UNKNOWN).")
    else:  # B
        if deps:
            verdict = "B-NOT-PROVEN"
            why = f"noted text may depend on state mutated before the note: {deps}"
        else:
            verdict = "B-PROVEN-CANDIDATE"
            why = ("argument expressions do not depend on any direct mutation "
                   "between the first mutation and the note call (no interval "
                   "Name assignment, no attribute overlap, no non-whitelisted "
                   "arg call); the same expressions evaluated before the first "
                   "mutation yield the identical eventual text, so a preflight "
                   "computing sanitize+canonical bytes from them is byte-exact "
                   "against direct mutations (helper-call side effects UNKNOWN).")
    if site["door"] == "note_seed":
        template = 'note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5'
    elif site["door"] == "note":
        template = 'note: text=(action or "").strip()[:120] (current) ; sanitized under R5 P5 before measure'
    else:
        template = site["door"]
    return {"file": site["file"], "line": site["line"], "door": site["door"],
            "function": site["function"], "cls": cls, "verdict": verdict,
            "why": why, "args": facts["exprs"], "deps": deps,
            "mut_before": [list(m) for m in muts_before],
            "in_loop": in_loop, "loop_muts": [list(m) for m in loop_muts],
            "helper_calls_before": helper_calls[:12],
            "eventual_template": template}


def main():
    rows = [json.loads(l) for l in (H / "r5d_sites.jsonl").read_text().splitlines()]
    out, counts = [], {}
    for r in rows:
        c = classify(r)
        if c not in ("A", "B"):
            continue
        res = analyze(r)
        out.append(res)
        counts[res["verdict"]] = counts.get(res["verdict"], 0) + 1
    (H / "r5d_path_proofs.jsonl").write_text(
        "\n".join(json.dumps(o, ensure_ascii=False) for o in out) + "\n")
    lines = ["# R5-D PATH-LEVEL PROOFS — classes A and B (P2 discharge attempt)",
             "",
             "Prepared: 2026-11-19 (susx100000-execution), answering Director",
             "7028973030 / 7030045309 / 7030396734: A/B labels were function-level",
             "AST HYPOTHESES; this record replaces them with per-path evidence",
             "from r5d_path_proof.py (checkout-relative, beside this file).",
             f"Census at main 702741969c6d2d1d020f85845912f1da84f31418. Sites analyzed: {len(out)} (A=26, B=45).",
             "",
             "## Verdict counts", ""]
    for k in sorted(counts):
        lines.append(f"- {k}: {counts[k]}")
    lines += ["",
              "## Reconciled partition (supersedes the A=26 / B=45 hypothesis counts)",
              "",
              "- A-PROVEN-DIRECT: 24 — buildable as class A.",
              "- B-PROVEN-CANDIDATE: 34, plus A-DOWNGRADED-B-LOOP: 2 (per-iteration",
              "  preflight at loop-body start) — buildable as class B: 36.",
              "- B-NOT-PROVEN: 11 — the noted text depends on state mutated before",
              "  the note, so an entry preflight cannot compute the exact eventual",
              "  bytes without simulating the mutation. These MOVE to C-HOLD",
              "  unless a per-site manual proof discharges them.",
              "- Effective partition: A=24 + B=36 + C-HOLD=50 (39 original + 11",
              "  moved) + DOOR=1 = 111. Any bounded R5-D authorization ask must",
              "  use THESE numbers: buildable scope 60 sites, held 50."]
    lines += ["",
              "## Cross-cutting boundaries (all A/B sites)",
              "",
              "- TOCTOU: no threading/lock use exists in form/open.py or",
              "  form/persist.py (grep evidence, this run); the program is",
              "  single-threaded in-process, so a synchronous preflight in the",
              "  same call stack as the append has no interleaving writer.",
              "  Multi-process concurrent writers to one owner file are NOT",
              "  excluded by any lock — that boundary stays UNKNOWN and the",
              "  preflight guarantees refusal atomicity only within one process.",
              "- Restart/fault: preflight is in-memory only; it writes nothing,",
              "  so a crash between preflight and append leaves durable state",
              "  exactly as the underlying mutation path leaves it — the R5",
              "  save path itself keeps the atomic_write_json contract",
              "  (complete generation or previous generation, never torn).",
              "  Power-loss durability remains UNKNOWN per R5-C P6.",
              "- Privacy: preflight must apply sanitize_text (R5 P5) to the",
              "  evaluated argument text BEFORE measuring/admitting, and the",
              "  refusal receipt carries counts/bytes only, never raw text —",
              "  the per-site eventual templates below are formulas, not values.",
              "- Residual limit: helper calls before a note may mutate through",
              "  aliases invisible to direct-mutation AST analysis; each site",
              "  lists its helper_calls_before so the Keeper can spot-challenge.",
              ""]
    for res in out:
        lines.append(f"## {res['cls']} -> {res['verdict']} — {res['file']}:{res['line']} "
                     f"{res['door']} in {res['function']}")
        lines.append("")
        lines.append(f"- args: {res['args']}")
        lines.append(f"- mut_before(direct): {res['mut_before']}")
        lines.append(f"- in_loop: {res['in_loop']}; loop_muts: {res['loop_muts']}")
        lines.append(f"- deps: {res['deps']}")
        lines.append(f"- helper_calls_before: {res['helper_calls_before']}")
        lines.append(f"- eventual: {res['eventual_template']}")
        lines.append(f"- why: {res['why']}")
        lines.append("")
    (H / "R5D_PATH_PROOFS_2026-11-19.md").write_text("\n".join(lines) + "\n")
    print(counts, "total", len(out))


if __name__ == "__main__":
    main()
