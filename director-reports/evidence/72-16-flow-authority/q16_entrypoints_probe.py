#!/usr/bin/env python3
"""72-16 supplement probe (Director Mode A requirement, 2026-11-05):
public-entry routing proof + operand-preservation regression.

For every supported entry point, run the operand-bearing program and
show which executor semantics actually executed it and whether the
operand survived:

  E1  REPL, Mandell seed line (cross-process)      -> chain path
  E2  REPL, English composition (cross-process)    -> composer -> flow path
  E3  Studio /api/execute (cross-process server)   -> execute_seed front door
  E4  Programmatic front door execute_seed         -> chain path
  E5  flow_executor direct API (internal layer)    -> THE DOCUMENTED
      EXCEPTION: the :: 3 operand is rewritten to :: 1 here. This is
      the OPEN semantic-authority divergence pinned by q16_probe B4.
      E5 asserts the exception exists exactly as classified; a future
      authorized repair must flip E5 deliberately, not silently.

Operand program: 13[Loop] :: 3 > 40[TokenCount]  (Loop label = cycles)
English operand: "cycle 3 times and then measure" -> 06[Cycle] :: 3

Usage: python3 q16_entrypoints_probe.py <run-tag>
Exit 0 iff every check passes; exit 2 on setup failure (never a pass).
"""
import json
import pathlib
import re
import subprocess
import sys
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "r1"

    # ---------- E1: REPL seed line (cross-process) ----------
    cp = subprocess.run(
        [sys.executable, "-m", "form.repl", "--owner", f"Q16E1{tag}"],
        input="13[Loop] :: 3 > 40[TokenCount]\n",
        capture_output=True, text=True, timeout=120, cwd=str(ROOT))
    out = cp.stdout + cp.stderr
    check("E1.repl_seed_operand_preserved",
          "13[Loop] :: 3" in out and "13[Loop] :: 1" not in out,
          "REPL seed path executes the operand as written (chain semantics)")

    # ---------- E2: REPL English composition (cross-process) ----------
    cp = subprocess.run(
        [sys.executable, "-m", "form.repl", "--owner", f"Q16E2{tag}"],
        input="cycle 3 times and then measure\n",
        capture_output=True, text=True, timeout=120, cwd=str(ROOT))
    out = cp.stdout + cp.stderr
    check("E2.repl_english_routes_via_composer",
          "INPUT:" in out and "06[Cycle] :: 3" in out,
          "English entry compiles to the Mandell program and executes it "
          "(composer -> flow path, composite receipt shown)")
    check("E2.repl_english_operand_preserved",
          "count=3" in out or "Cycle x3" in out,
          "the count operand 3 reaches execution at the English entry")

    # ---------- E3: Studio /api/execute (cross-process server) ----------
    port = 8973
    srv = None
    try:
        srv = subprocess.Popen(
            [sys.executable, "gui/server.py", "--port", str(port),
             "--owner", f"Q16E3{tag}"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
            cwd=str(ROOT))
        deadline = time.time() + 30
        up = False
        while time.time() < deadline:
            try:
                urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=2)
                up = True
                break
            except Exception:
                if srv.poll() is not None:
                    break
                time.sleep(0.5)
        if not up:
            print("SETUP_FAILED E3: studio server did not come up")
            return 2
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=5) as resp:
            html = resp.read().decode()
        m = re.search(r'name="studio-token"\s+content="([^"]+)"', html)
        if not m:
            print("SETUP_FAILED E3: studio-token meta not found")
            return 2
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/api/execute",
            data=json.dumps({"seed": "13[Loop] :: 3 > 40[TokenCount]",
                             "owner": f"Q16E3{tag}"}).encode(),
            headers={"Content-Type": "application/json",
                     "X-Studio-Token": m.group(1)}, method="POST")
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
        msgs = (data.get("result") or {}).get("messages") or []
        joined = "\n".join(str(x) for x in msgs)
        check("E3.studio_operand_preserved",
              "13[Loop] :: 3" in joined and "13[Loop] :: 1" not in joined,
              "Studio executes via execute_seed; operand as written")
    finally:
        if srv is not None:
            srv.terminate()
            try:
                srv.wait(timeout=10)
            except Exception:
                srv.kill()

    # ---------- E4: programmatic front door ----------
    from form.open import Program
    from form.mandell.executor import execute_seed
    p = Program(owner=f"Q16E4{tag}")
    o = execute_seed(p, "13[Loop] :: 3 > 40[TokenCount]")
    msgs = list(o.get("messages") or [])
    check("E4.front_door_operand_preserved",
          any("13[Loop] :: 3" in m for m in msgs),
          "execute_seed (chain path) executes the operand as written")

    # ---------- E5: flow API — the documented exception ----------
    from form.mandell.flow_executor import parse_program, execute_program
    p = Program(owner=f"Q16E5{tag}")
    rec = execute_program(p, parse_program("13[Loop] :: 3 > 40[TokenCount]"))
    msgs = [m for s in rec.steps for m in s.messages]
    check("E5.flow_api_exception_as_classified",
          any("13[Loop] :: 1" in m for m in msgs),
          "OPEN divergence: direct flow-API execution rewrites :: 3 -> :: 1 "
          "(pinned; a future authorized repair flips this check deliberately)")

    failed = [n for n, ok in RESULTS if not ok]
    print(f"\n{len(RESULTS) - len(failed)}/{len(RESULTS)} checks passed"
          + (f"; FAILED: {failed}" if failed else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
