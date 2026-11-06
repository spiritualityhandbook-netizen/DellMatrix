#!/usr/bin/env python3
"""72-16 probe: is flow_executor an independent execution authority,
or a subordinate composition layer over the canonical chain/executor?

Method: identical program text through BOTH paths, each on its own
per-owner isolated Program (supported per-owner state isolation;
never the operator's real owner). Plus one cross-process REPL run
proving which semantics the public path actually delivers (P10 fence).

Paths:
  CHAIN = form.mandell.executor.execute_seed  (front door -> chain_exec)
  FLOW  = form.mandell.flow_executor.parse_program + execute_program
          (per node -> semantic_router.route_intent -> execute_seed)

Usage: python3 q16_probe.py <run-tag>   (owners are suffixed per run)
Exit 0 iff every check passes. Printed lines are the evidence.
"""
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "r1"
    from form.open import Program
    from form.mandell.executor import execute_seed
    from form.mandell.flow_executor import parse_program, execute_program

    def via_chain(suffix, text):
        p = Program(owner=f"Q16{suffix}{tag}")
        return execute_seed(p, text)

    def via_flow(suffix, text):
        p = Program(owner=f"Q16{suffix}{tag}")
        return execute_program(p, parse_program(text))

    def flow_parse_error(text):
        try:
            parse_program(text)
            return None
        except ValueError as e:
            return str(e)

    # ---------- A. Convergence controls (shared domain) ----------
    # A1: plain FlowTo program of two succeeding atoms.
    t = "34[Stamp] :: created > 40[TokenCount]"
    o = via_chain("A1C", t)
    check("A1.chain_ok", o.get("ok") is True
          and [r.get("ok") for r in o.get("atom_results") or []] == [True, True],
          f"atoms={[(r.get('dell'), r.get('ok')) for r in o.get('atom_results') or []]}")
    r = via_flow("A1F", t)
    check("A1.flow_ok", r.ok and [s.ok for s in r.steps] == [True, True],
          f"steps={[(s.dell, s.ok) for s in r.steps]}")

    # A2: FlowThru blocking after a failing atom converges.
    t = "28[Rollback] >> 40[TokenCount]"
    o = via_chain("A2C", t)
    ar = o.get("atom_results") or []
    check("A2.chain_block", len(ar) == 2 and ar[0].get("ok") is False
          and ar[1].get("skipped") is True and ar[1].get("ok") is False,
          f"atoms={[(x.get('dell'), x.get('ok'), x.get('skipped')) for x in ar]}")
    r = via_flow("A2F", t)
    check("A2.flow_block", len(r.steps) == 2 and r.steps[0].ok is False
          and r.steps[1].skipped is True and r.steps[1].ok is False,
          f"steps={[(s.dell, s.ok, s.skipped) for s in r.steps]}")

    # A3: label->args for 'cycle' (one of flow's three hardcoded actions).
    r = via_flow("A3F", "06[Cycle] :: 3 > 40[TokenCount]")
    check("A3.flow_cycle_args", r.steps and r.steps[0].arguments.get("count") == 3,
          f"args={r.steps[0].arguments if r.steps else None}")

    # ---------- B. Divergences (composition semantics) ----------
    # B1: FlowOver (>>>) — chain executes with an honest skip; flow refuses.
    err = flow_parse_error("40[TokenCount] >>> 12[Test]")
    check("B1.flow_refuses_flowover", err is not None and "REQUIRES_RUNTIME_SUPPORT" in err,
          f"err={err!r}")
    o = via_chain("B1C", "40[TokenCount] >>> 12[Test]")
    ar = o.get("atom_results") or []
    check("B1.chain_executes_flowover", len(ar) == 2 and ar[0].get("ok") is True
          and ar[1].get("skipped") is True,
          f"atoms={[(x.get('dell'), x.get('ok'), x.get('skipped')) for x in ar]}")

    # B2: FlowBy (:) — chain runs both atoms; flow refuses.
    err = flow_parse_error("40[TokenCount] : 12[Test]")
    check("B2.flow_refuses_flowby", err is not None and "DESCRIPTIVE_ONLY" in err,
          f"err={err!r}")
    o = via_chain("B2C", "40[TokenCount] : 12[Test]")
    ar = o.get("atom_results") or []
    check("B2.chain_executes_flowby", [x.get("ok") for x in ar] == [True, True],
          f"atoms={[(x.get('dell'), x.get('ok')) for x in ar]}")

    # B3: typed args — chain refuses PER ATOM (UNSUPPORTED_ARGS, Director
    # Core I gate) and the chain CONTINUES; flow refuses the WHOLE program
    # at tokenize time (zero execution, generic error).
    o = via_chain("B3C", '34[Stamp](mark="hello") > 40[TokenCount]')
    ar = o.get("atom_results") or []
    check("B3.chain_per_atom_refusal", len(ar) == 2
          and ar[0].get("ok") is False and "UNSUPPORTED_ARGS" in (ar[0].get("error") or "")
          and ar[1].get("ok") is True,
          f"atoms={[(x.get('dell'), x.get('ok'), (x.get('error') or '')[:22]) for x in ar]}")
    err = flow_parse_error('34[Stamp](mark="hello") > 40[TokenCount]')
    check("B3.flow_whole_program_refusal", err is not None and "expected flow" in err,
          f"err={err!r}")

    # B4: label payload for 'grow' — flow silently rewrites :: 3 to :: 1
    # (_args_from_label has no grow case -> Intent args {} -> cycles=1);
    # chain executes the seed as written.
    r = via_flow("B4F", "13[Loop] :: 3 > 40[TokenCount]")
    flow_msgs = [m for s in r.steps for m in s.messages]
    check("B4.flow_rewrites_grow_label", any("13[Loop] :: 1" in m for m in flow_msgs),
          f"flow seed line={[m for m in flow_msgs if 'Loop' in m][:2]}")
    o = via_chain("B4C", "13[Loop] :: 3 > 40[TokenCount]")
    chain_msgs = list(o.get("messages") or [])
    check("B4.chain_keeps_grow_label", any("13[Loop] :: 3" in m for m in chain_msgs),
          f"chain seed line={[m for m in chain_msgs if 'Loop' in m][:2]}")

    # ---------- C. Static authority census ----------
    root = pathlib.Path(__file__).resolve().parents[3]
    fe = (root / "form/mandell/flow_executor.py").read_text()
    ce = (root / "form/mandell/chain_exec.py").read_text()
    check("C1.flow_delegates_to_router", "route_intent" in fe
          and "executor_leaf" not in fe and "execute_core_ii" not in fe,
          "flow_executor routes every node via route_intent; no direct leaf/Core II calls")
    check("C2.chain_owns_atom_dispatch", "execute_core_ii" in ce and "_leaf=True" in ce,
          "chain_exec dispatches Core II directly and Core I via execute_seed(_leaf=True)")

    # ---------- D. Public-path fence (cross-process REPL) ----------
    owner = f"Q16REPL{tag}"
    cp = subprocess.run(
        [sys.executable, "-m", "form.repl", "--owner", owner],
        input="13[Loop] :: 3 > 40[TokenCount]\n",
        capture_output=True, text=True, timeout=120,
        cwd=str(pathlib.Path(__file__).resolve().parents[3]))
    out = cp.stdout + cp.stderr
    check("D1.repl_uses_chain_semantics", "13[Loop] :: 3" in out and "13[Loop] :: 1" not in out,
          "REPL delivers the seed as written (P10 pre-claim -> chain_exec), "
          "not flow_executor's rewrite")

    failed = [n for n, ok in RESULTS if not ok]
    print(f"\n{len(RESULTS) - len(failed)}/{len(RESULTS)} checks passed"
          + (f"; FAILED: {failed}" if failed else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
