#!/usr/bin/env python3
"""R5-D caller classification analysis (UNI-EXECUTED, script-assisted).

For every note_seed/note/note_unknown_encounter call site in non-test
form/ code: find the enclosing function, then list state-mutating
statements in that function BEFORE and AFTER the call, plus control
context (loop/try/conditional). Mutation = Assign/AugAssign/AnnAssign
to an attribute/subscript, or a call to a known mutating method.
Output: JSONL + summary counts. Classification rules are applied by
the analyst from this evidence (see R5D_CLASSIFICATION artifact).
"""
import ast, json, pathlib, sys

ROOT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else
                    "/home/hatch/workspace/goals/dellmatrix-capability-circuits/hidden_files/r5d_clone/form")
MUT_METHODS = {"append", "extend", "insert", "pop", "remove", "clear",
               "update", "add", "discard", "place", "set", "step",
               "turn_on", "turn_off", "evolve", "snap", "box", "push",
               "record", "register", "define", "create", "delete",
               "move", "copy", "replace", "patch", "grow", "learn",
               "save", "write", "commit", "apply", "execute"}


def target_desc(t):
    try:
        return ast.unparse(t)[:60]
    except Exception:
        return type(t).__name__


def analyze_file(path):
    src = path.read_text(errors="replace")
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return []
    out = []
    parents = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parents[child] = node

    def enclosing_fn(node):
        cur = node
        while cur in parents:
            cur = parents[cur]
            if isinstance(cur, (ast.FunctionDef, ast.AsyncFunctionDef)):
                return cur
        return None

    def contexts(node):
        ctx = []
        cur = node
        while cur in parents:
            cur = parents[cur]
            if isinstance(cur, ast.For):
                ctx.append("loop")
            elif isinstance(cur, ast.While):
                ctx.append("loop")
            elif isinstance(cur, ast.Try):
                ctx.append("try")
            elif isinstance(cur, ast.If):
                ctx.append("cond")
            elif isinstance(cur, (ast.FunctionDef, ast.AsyncFunctionDef)):
                break
        return ctx

    def mutations(fn, upto_line=None, from_line=None):
        muts = []
        for node in ast.walk(fn):
            if isinstance(node, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
                tgts = node.targets if isinstance(node, ast.Assign) else [node.target]
                for t in tgts:
                    if isinstance(t, (ast.Attribute, ast.Subscript)):
                        ln = node.lineno
                        if upto_line and ln >= upto_line:
                            continue
                        if from_line and ln <= from_line:
                            continue
                        muts.append((ln, "assign:" + target_desc(t)))
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr in MUT_METHODS:
                    ln = node.lineno
                    if upto_line and ln >= upto_line:
                        continue
                    if from_line and ln <= from_line:
                        continue
                    muts.append((ln, "call:" + target_desc(node.func)[:60]))
        return sorted(set(muts))

    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                and node.func.attr in ("note_seed", "note", "note_unknown_encounter"):
            fn = enclosing_fn(node)
            fname = fn.name if fn else "<module>"
            before = mutations(fn, upto_line=node.lineno) if fn else []
            after = mutations(fn, from_line=node.lineno) if fn else []
            out.append({
                "file": str(path.relative_to(ROOT.parent)),
                "line": node.lineno,
                "door": node.func.attr,
                "function": fname,
                "ctx": contexts(node),
                "mut_before": before,
                "mut_after": after,
                "n_before": len(before),
                "n_after": len(after),
            })
    return out


def main():
    rows = []
    for f in sorted(ROOT.rglob("*.py")):
        if "_test.py" in f.name or "_tests.py" in f.name:
            continue
        rows.extend(analyze_file(f))
    rows.sort(key=lambda r: (r["file"], r["line"]))
    outp = pathlib.Path(sys.argv[2])
    outp.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    print(f"sites={len(rows)}")
    clean = [r for r in rows if r["n_before"] == 0]
    print(f"no-mutation-before (class-a candidates): {len(clean)}")
    print(f"mutation-before: {len(rows) - len(clean)}")
    inloop = [r for r in rows if "loop" in r["ctx"]]
    print(f"inside loop: {len(inloop)}")


if __name__ == "__main__":
    main()
