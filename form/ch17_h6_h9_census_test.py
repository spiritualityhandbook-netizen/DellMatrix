#!/usr/bin/env python3
"""CH-17 H6 / H9 CENSUS — Part I (PART_I_PLAN_2026-11-20 §5.2;
CH17_EVIDENCE_SWEEP_2026-11-20 open debt H6 + H9).

H6 — per-module writer census + provenance-of-derived-reading
probes for the spatial/geometry modules:

* form/dell_matrix/sacred_geometry.py is PURE: its module-level
  import set is {__future__, dataclasses, typing, math}, it
  calls no I/O, and its derived readings (flower centers,
  Rule 90, fractal shells, sierpinski points, voynich ring) are
  deterministic — same inputs, same outputs, in-process AND in
  a fresh interpreter (CROSS_PROCESS probe). Two function-level
  lazy imports exist and are NAMED, not hidden: geometry_status
  imports form.mandell.bounded_orbit (a status aggregator, not
  a geometry function) and the module's __main__ guard imports
  sys. Its
  production readers are pinned: verita.py, perception.py,
  graph_view.py and form/open.py. Any new production importer
  turns this suite RED until the census is re-pinned — that is
  the tripwire working.
* form/dell_matrix/spatial_audio.py's production-caller set is
  pinned at exactly ONE caller: form/dell_matrix/sonification.py
  (PR #518, Sound S0 — the first genuine production caller,
  landed after the original zero-caller pin; census re-pinned
  under Director ruling 7197123837 on PR #508, 2026-11-26).
  Any further caller turns this suite RED until the census is
  re-earned, not silently inherited.
* form/dell_matrix/spatial_authority.py mutators (place / tick /
  settle) are called through exactly ONE production file —
  form/open.py, the Program doors. Two NAMED non-door writers
  mutate spatial.placements directly, and this census names
  them instead of hiding them:
    - form/dell_matrix/confirm_lineage.py — the confirm
      COMPENSATION path (rolls a placement back when a confirm
      transaction aborts);
    - form/mandell/supersession.py — the supersession cleanup
      (removes a superseded idea's placement).
  explain() is verified read-only by AST (no self.* assignment,
  no placements mutation inside it). Placement itself is a
  deterministic derived reading: two identically built programs
  place the same idea at the same coordinates with the same
  explanation.

H9 — surface write census for gui/server.py: every surface
mutation names its Program door. The POST route set is pinned
{/api/parse, /api/execute, /api/owner} and exactly ONE of them
mutates Program state: /api/execute, through the executor's
execute_seed under the server-local _LOCK (a threading.RLock
that serializes the SERVER only — it is not, and never claims
to be, the owner-state lock; the owner lock is censused by the
lock-order suite). /api/parse never touches a Program;
/api/owner moves only the server-local active-owner pointer.
GET routes are pinned {/api/dells, /api/state, /api/growth}
plus static files, and no GET branch calls execute_seed.

Classification (pinned, explicit): production = every .py under
form/ except *_test.py / *_tests.py / *_test_spec.py /
*_child.py / *_proof.py / *_circuit.py / *_regressions.py and
regress.py (the harness), PLUS gui/server.py (the served
surface). State isolation: dedicated owners, owner-scoped
cleanup that fails loudly.
"""

from __future__ import annotations

import ast
import json
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}"
          + (f" | {detail}" if detail and not cond else ""))


def _cleanup(owner):
    from form.persist import _STATE_DIR, _safe_owner
    safe = _safe_owner(owner)
    files = [os.path.join(_STATE_DIR, f"program_{safe}.json"),
             os.path.join(_STATE_DIR, f"graph_{safe}.json"),
             os.path.join(_STATE_DIR, f"graph_{safe}.journal.json"),
             os.path.join(_STATE_DIR, ".locks", f"{safe}.lock")]
    ideas_dir = os.path.join(_STATE_DIR, f"ideas_{safe}")
    for f in files:
        if os.path.isfile(f):
            os.remove(f)
    if os.path.isdir(ideas_dir):
        shutil.rmtree(ideas_dir)
    if os.path.isdir(_STATE_DIR):
        for name in os.listdir(_STATE_DIR):
            if name.startswith(f"program_{safe}_cp_"):
                os.remove(os.path.join(_STATE_DIR, name))
    leftovers = [f for f in files if os.path.isfile(f)]
    if leftovers or os.path.isdir(ideas_dir):
        raise RuntimeError(f"ch17 census cleanup incomplete: {leftovers}")


# ---------------------------------------------------------------
# census scope
# ---------------------------------------------------------------

_SKIP_SUFFIXES = ("_test.py", "_tests.py", "_test_spec.py", "_child.py",
                  "_proof.py", "_circuit.py", "_regressions.py")
_SKIP_NAMES = {"regress.py"}
_SKIP_DIRS = {"state", "__pycache__"}


def _production_files():
    out = []
    base = os.path.join(ROOT, "form")
    for d, dirs, files in os.walk(base):
        dirs[:] = [x for x in dirs if x not in _SKIP_DIRS]
        for f in sorted(files):
            if (f.endswith(".py") and f not in _SKIP_NAMES
                    and not f.endswith(_SKIP_SUFFIXES)):
                out.append(os.path.join(d, f))
    out.append(os.path.join(ROOT, "gui", "server.py"))
    return sorted(out)


def _rel(path):
    return os.path.relpath(path, ROOT).replace(os.sep, "/")


def _texts():
    out = {}
    for path in _production_files():
        with open(path, encoding="utf-8") as fh:
            out[_rel(path)] = fh.read()
    return out


def _importers(texts, module):
    """Files whose import machinery names `module`."""
    pat = re.compile(
        r"(?:from\s+[\w.]*" + module + r"\s+import"
        r"|import\s+[\w.]*" + module + r"\b"
        r"|from\s+[\w.]+\s+import\s+[^\n]*\b" + module + r"\b)")
    return {rel for rel, text in texts.items()
            if pat.search(text)}


# ---------------------------------------------------------------
# H6
# ---------------------------------------------------------------

def _h6_geometry(texts):
    tree = ast.parse(texts["form/dell_matrix/sacred_geometry.py"])
    top_imports = set()
    lazy_imports = set()  # (module, enclosing function)
    bad_calls = []

    def _visit(node, func):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            func = node.name
        elif isinstance(node, ast.If) and isinstance(
                node.test, ast.Compare) \
                and isinstance(node.test.left, ast.Name) \
                and node.test.left.id == "__name__":
            func = "<__main__ guard>"
        if isinstance(node, ast.Import):
            for a in node.names:
                if func is None:
                    top_imports.add(a.name.split(".")[0])
                else:
                    lazy_imports.add((a.name, func))
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                if func is None:
                    top_imports.add(node.module.split(".")[0])
                else:
                    lazy_imports.add((node.module, func))
        elif isinstance(node, ast.Call):
            fn = node.func
            name = fn.id if isinstance(fn, ast.Name) else None
            if name in ("open", "eval", "exec", "compile",
                        "__import__", "input"):
                bad_calls.append(name)
        for child in ast.iter_child_nodes(node):
            _visit(child, func)

    _visit(tree, None)
    check("h6_sacred_geometry_import_set_is_pure",
          top_imports <= {"__future__", "dataclasses", "typing",
                          "math"},
          f"module-level imports={sorted(top_imports)}")
    check("h6_sacred_geometry_lazy_imports_named_and_pinned",
          lazy_imports == {("form.mandell.bounded_orbit",
                            "geometry_status"),
                           ("sys", "<__main__ guard>")},
          f"lazy imports={sorted(lazy_imports)}")
    check("h6_sacred_geometry_makes_no_io_calls",
          bad_calls == [], f"bad calls: {bad_calls}")
    readers = _importers(texts, "sacred_geometry") - {
        "form/dell_matrix/sacred_geometry.py"}
    check("h6_sacred_geometry_reader_census_pinned",
          readers == {"form/dell_matrix/verita.py",
                      "form/dell_matrix/perception.py",
                      "form/dell_matrix/graph_view.py",
                      "form/open.py"},
          f"readers={sorted(readers)}")
    writers = [rel for rel, text in texts.items()
               if re.search(r"sacred_geometry\.\w+\s*=", text)]
    check("h6_no_production_file_writes_into_sacred_geometry",
          writers == [], f"writers={writers}")


def _geometry_probe():
    from form.dell_matrix import sacred_geometry as sg
    return {
        "flower": sg.flower_centers(3, 1.5),
        "seed": sg.seed_of_life(),
        "rule90": sg.rule90(width=15, steps=6),
        "shells": sg.fractal_shells(4, 1.0),
        "sierp": sg.sierpinski_points(3),
        "ring": sg.voynich_ring_for_unit({"id": "probe",
                                          "label": "Probe"}),
    }


def _h6_geometry_determinism():
    a = _geometry_probe()
    b = _geometry_probe()
    check("h6_geometry_deterministic_in_process", a == b,
          "two identical probe runs differ")
    child = subprocess.run(
        [sys.executable, "-c",
         "import sys, json; sys.path.insert(0, " + repr(ROOT) + ");"
         "from form.ch17_h6_h9_census_test import _geometry_probe;"
         "print(json.dumps(_geometry_probe(), sort_keys=True))"],
        capture_output=True, text=True, timeout=120)
    try:
        theirs = json.loads(child.stdout.strip().splitlines()[-1])
        ours = json.loads(json.dumps(a, sort_keys=True))
        same = theirs == ours
    except Exception as exc:  # noqa: BLE001
        same, theirs = False, f"{exc}: {child.stderr[-300:]}"
    check("h6_geometry_deterministic_cross_process", same,
          f"child rc={child.returncode} theirs={theirs}")


def _is_spatial_ref(node):
    """<x>.spatial or a bare `spatial` alias (spatial = program.spatial)."""
    return (isinstance(node, ast.Attribute) and node.attr == "spatial") \
        or (isinstance(node, ast.Name) and node.id == "spatial")


def _h6_spatial(texts):
    mentions = {rel for rel, text in texts.items()
                if "spatial_audio" in text}
    # Production-caller set re-pinned to {sonification.py}
    # (Director 7197123837): #518 landed the first genuine
    # caller after the original zero-caller pin. Fail-closed
    # both ways: any further caller, or the pinned caller
    # disappearing, turns this check RED.
    check("h6_spatial_audio_production_caller_set_pinned",
          mentions - {"form/dell_matrix/spatial_audio.py"}
          == {"form/dell_matrix/sonification.py"}
          and _importers(texts, "spatial_audio")
          == {"form/dell_matrix/sonification.py"},
          f"mentions={sorted(mentions)}")
    method_writers, direct = set(), set()
    for rel, text in texts.items():
        if rel == "form/dell_matrix/spatial_authority.py":
            continue  # the authority's own internals are the subject
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) \
                    and isinstance(node.func, ast.Attribute):
                fn = node.func
                if fn.attr in ("place", "tick", "settle") \
                        and _is_spatial_ref(fn.value):
                    method_writers.add(rel)
                if fn.attr in ("pop", "clear", "update",
                               "setdefault") \
                        and isinstance(fn.value, ast.Attribute) \
                        and fn.value.attr == "placements" \
                        and _is_spatial_ref(fn.value.value):
                    direct.add(rel)
            if isinstance(node, ast.Assign):
                for tgt in node.targets:
                    if isinstance(tgt, ast.Subscript) \
                            and isinstance(tgt.value, ast.Attribute) \
                            and tgt.value.attr == "placements" \
                            and _is_spatial_ref(tgt.value.value):
                        direct.add(rel)
    check("h6_spatial_mutators_called_only_through_program_doors",
          method_writers == {"form/open.py"},
          f"method writers={sorted(method_writers)}")
    check("h6_spatial_direct_placements_writers_named",
          direct == {"form/dell_matrix/confirm_lineage.py",
                     "form/mandell/supersession.py"},
          f"direct writers={sorted(direct)}")
    # explain() read-only, by AST: no self.* assignment, no
    # mutation call on self.placements inside its body.
    tree = ast.parse(texts["form/dell_matrix/spatial_authority.py"])
    explain_fn = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, ast.FunctionDef) \
                        and item.name == "explain":
                    explain_fn = item
    violations = []
    if explain_fn is not None:
        for node in ast.walk(explain_fn):
            if isinstance(node, (ast.Assign, ast.AugAssign,
                                 ast.AnnAssign)):
                for tgt in (node.targets if isinstance(
                        node, ast.Assign) else [node.target]):
                    if isinstance(tgt, ast.Attribute) \
                            and isinstance(tgt.value, ast.Name) \
                            and tgt.value.id == "self":
                        violations.append(f"self.{tgt.attr} =")
            if isinstance(node, ast.Call) \
                    and isinstance(node.func, ast.Attribute) \
                    and node.func.attr in ("pop", "clear", "update",
                                           "setdefault", "append",
                                           "extend"):
                violations.append(f".{node.func.attr}() call")
    check("h6_spatial_explain_is_read_only",
          explain_fn is not None and violations == [],
          f"violations={violations}")


def _h6_placement_determinism():
    from form.open import open_program
    owners = ["Ch17H6A", "Ch17H6B"]
    for o in owners:
        _cleanup(o)
    try:
        snaps = []
        for o in owners:
            p = open_program(o)
            p.place("h6probe", "H6Probe", words="one")
            placements = {k: (v.get("x"), v.get("y"), v.get("cause"))
                          for k, v in p.spatial.placements.items()}
            snaps.append((placements,
                          p.spatial_explain("h6probe")))
        check("h6_spatial_placement_is_a_deterministic_derived_reading",
              snaps[0] == snaps[1] and "h6probe" in snaps[0][0],
              f"A={snaps[0]} B={snaps[1]}")
    finally:
        for o in owners:
            _cleanup(o)


# ---------------------------------------------------------------
# H9
# ---------------------------------------------------------------

def _segment(text, start_marker, end_marker=None):
    i = text.index(start_marker)
    if end_marker is None:
        return text[i:]
    return text[i:text.index(end_marker, i)]


def _branches(segment):
    """Split a handler body into {route: branch_text} by its
    `if path == "..."` guards, in source order."""
    parts = re.split(r'(?=if path == )', segment)
    out = {}
    for part in parts:
        m = re.match(r'if path == "([^"]+)"', part)
        if m:
            out[m.group(1)] = part
    return out


def _h9_server(texts):
    srv = texts["gui/server.py"]
    post = _segment(srv, "def do_POST")
    get = _segment(srv, "def do_GET", "def do_POST")
    post_routes = _branches(post)
    get_routes = _branches(get)
    check("h9_post_route_census_pinned",
          set(post_routes) == {"/api/parse", "/api/execute",
                               "/api/owner"},
          f"POST routes={sorted(post_routes)}")
    check("h9_get_route_census_pinned",
          set(get_routes) == {"/api/dells", "/api/state",
                              "/api/growth"},
          f"GET routes={sorted(get_routes)}")
    exe = post_routes.get("/api/execute", "")
    parse = post_routes.get("/api/parse", "")
    owner = post_routes.get("/api/owner", "")
    check("h9_execute_is_the_one_program_mutation_door",
          "execute_seed(" in exe and "_LOCK" in exe,
          "execute branch lacks execute_seed under the server lock")
    check("h9_parse_never_touches_a_program",
          "execute_seed" not in parse and "_get_program" not in parse
          and "_parse_payload" in parse,
          f"parse branch: {parse[:200]}")
    check("h9_owner_moves_only_the_server_local_pointer",
          "_ACTIVE_OWNER" in owner and "execute_seed" not in owner
          and "confirm" not in owner and ".save(" not in owner,
          f"owner branch: {owner[:200]}")
    check("h9_no_get_branch_executes",
          "execute_seed" not in get, "a GET branch calls execute_seed")
    imports = set()
    for m in re.finditer(r"from\s+(form[\w.]*)\s+import\s+([^\n#]+)",
                         srv):
        for sym in m.group(2).split(","):
            sym = sym.strip().strip("()")
            if sym:
                imports.add(sym)
    check("h9_server_form_imports_pinned",
          imports == {"filter_nodes_for_room", "CORE_II",
                      "execute_seed", "DELLS", "parse_seed",
                      "open_program"},
          f"imports={sorted(imports)}")
    check("h9_server_lock_is_server_local_not_the_owner_lock",
          "_LOCK = threading.RLock()" in srv
          and "owner_state_lock" not in srv,
          "server lock identity changed")


def run_all():
    texts = _texts()
    _h6_geometry(texts)
    _h6_geometry_determinism()
    _h6_spatial(texts)
    _h6_placement_determinism()
    _h9_server(texts)
    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"CH17 H6/H9 CENSUS: {passed}/{len(RESULTS)} GREEN")
    return passed == len(RESULTS)


def smoke() -> bool:
    return run_all()


if __name__ == "__main__":
    raise SystemExit(0 if smoke() else 1)
