#!/usr/bin/env python3
"""D1-UNSUPPORTED-ARG-GATE — fail-closed gate for typed args on
untyped Core II Dells (Director MODE C repair, ruling on
PR #252, 2026-11-03).

Defect (investigation PR #252, Q1, PUBLIC_ENTRY_PATH 10/10):
chain_exec._run_atom inspected typed args only under
has_signature(n); the 33 unregistered Core II Dells executed
on the legacy payload with the args never read — silent
success under a default (82[Group] files under 'group'),
label silently wins, or a misleading handler failure
(78[Cause] 'malformed_relation' on the empty label).

Repair (this circuit): in the same TOAM block, the missing
else — atom.args nonempty + Dell 51-99 + no signature ->
refuse BEFORE execute_core_ii with error
'UNSUPPORTED_ARGS: <sorted role names>'. Diagnostics name
role NAMES only; raw argument values are never echoed by the
refusal (Director amendment). Control heads 60, 62-66
(Q-D2 Option A): a refused head short-circuits its frame in
_run_control — body occurrences receipt honest skips, frame
status 'fail', zero iterations. Dell 61[Join]: a gate-refused
Join names its refusal at frame/chain level instead of
collapsing to generic 'join_fail', and never overwrites an
earlier refusal (first root cause law).

Zero-mutation snapshot = business state (store, groups,
selected, scope, defs, aliases, compositions, causes,
last_result, plane units, control_steps). Frame bookkeeping
(last_frame / frames) is the refusal's own receipt trail and
is asserted separately, never folded into the snapshot
(SWAT pre-mortem #2). The seed-echo header lines
(Mandell:/English:) and result['seed'] are the caller's own
input text, present in every chain result; the canary checks
assert the refusal's OWN diagnostics (error, receipts,
appended messages) carry no raw value (pre-mortem #3).

Labels: seed execution PUBLIC_ENTRY_PATH (execute_seed on a
real Program); the REPL section is a literal subprocess
session (REAL_USER_PATH). Setup places units directly.
"""
from __future__ import annotations

import glob
import json
import os
import shutil
import subprocess
import sys

RESULTS = []

STATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "state")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Census pin (PR #252 Appendix B). The sweep ITERATES the set
# derived live from the registry + signature source and
# asserts it equals this pin — a future registration fails
# the count loud instead of silently shrinking coverage.
EXPECTED_UNTYPED_33 = [59, 60, 61, 62, 63, 64, 65, 66, 70, 71,
                       72, 73, 74, 75, 76, 77, 78, 79, 80, 81,
                       82, 83, 89, 90, 91, 92, 93, 94, 95, 96,
                       97, 98, 99]
EXPECTED_TYPED_17 = [8, 51, 52, 53, 54, 55, 56, 57, 58, 67,
                     68, 69, 84, 85, 86, 87, 88]

CANARY = "CANARYZZ_9f3e_UNIQ"


def _rec(name, cond, detail=""):
    RESULTS.append((name, bool(cond), str(detail)))


def _cleanup(owner):
    # Loud cleanup (standing law): exact owner scope only.
    for f in glob.glob(os.path.join(STATE_DIR, f"*{owner}*")):
        try:
            if os.path.isdir(f):
                shutil.rmtree(f)
            else:
                os.remove(f)
        except OSError as exc:
            raise RuntimeError(f"cleanup failed for {f}: {exc}")


def _fresh(owner):
    _cleanup(owner)
    from form.open import Program
    p = Program(owner)
    units = set(p.cube.session.plane.units)
    assert units == {"welcome"}, \
        f"owner {owner} unexpected start state: {sorted(units)}"
    return p


def _st(p):
    from form.mandell.core_ii_exec import attach
    return attach(p)


def _snap(p):
    s = _st(p)
    return {
        "store": dict(s.store or {}),
        "groups": {k: list(v) for k, v in (s.groups or {}).items()},
        "selected": list(s.selected or []),
        "scope": s.scope,
        "defs": dict(s.defs or {}),
        "aliases": dict(s.aliases or {}),
        "compositions": dict(s.compositions or {}),
        "causes": [tuple(x) for x in (getattr(s, "causes", None) or [])],
        "last_result": dict(s.last_result or {}),
        "units": sorted(p.cube.session.plane.units),
        "control_steps": s.control_steps,
    }


def _setup(p):
    p.place("garden_gate", "Garden Gate")
    p.place("garden_fern", "Garden Fern")
    p.place("river_stone", "River Stone")
    from form.mandell.executor import execute_seed
    execute_seed(p, "51[Select]")


def _receipts(r):
    return r.get("atom_results") or []


def _by_dell(r, n):
    return [a for a in _receipts(r) if a.get("dell") == n]


def _errs(r):
    return " | ".join(str(a.get("error", "")) for a in _receipts(r))


def _registry_scope():
    from form.mandell.registry import DELLS
    from form.mandell.signatures import get_signature, has_signature
    core_ii = sorted(n for n in DELLS if 51 <= n <= 99)
    derived_untyped = [n for n in core_ii if not has_signature(n)]
    _rec("gate scope derived from registry+signatures is "
         "exactly the 33 untyped Core II Dells",
         derived_untyped == EXPECTED_UNTYPED_33,
         f"derived={derived_untyped}")
    typed = sorted(n for n in range(100) if get_signature(n))
    _rec("typed-signature count stays 17 (no new registrations)",
         typed == EXPECTED_TYPED_17, f"typed={typed}")


def _sweep_untyped():
    from form.mandell.executor import execute_seed
    from form.mandell.registry import get_dell
    from form.mandell.signatures import has_signature
    owner = "GateSweep"
    p = _fresh(owner)
    _setup(p)
    bad = []
    for n in range(51, 100):
        if has_signature(n):
            continue
        name = str((get_dell(n) or {}).get("name", n))
        before = _snap(p)
        r = execute_seed(p, f'{n:02d}[{name}](zzrole="zzvalue")')
        after = _snap(p)
        ars = _by_dell(r, n)
        ok = (not r.get("ok")
              and r.get("error") == "UNSUPPORTED_ARGS: zzrole"
              and len(ars) == 1
              and ars[0].get("ok") is False
              and ars[0].get("skipped") is False
              and ars[0].get("error") == "UNSUPPORTED_ARGS: zzrole"
              and ars[0].get("reason") == "UNSUPPORTED_ARGS: zzrole"
              and after == before)
        if not ok:
            bad.append((n, r.get("ok"), r.get("error"), ars,
                        after == before))
    _rec("all 33 untyped Core II Dells refuse typed args with "
         "UNSUPPORTED_ARGS + exact receipt + zero mutation",
         not bad, f"bad={bad[:3]}")
    _cleanup(owner)


def _family_witnesses():
    from form.mandell.executor import execute_seed
    owner = "GateFam"
    p = _fresh(owner)
    s = _st(p)
    _setup(p)

    before = _snap(p)
    r = execute_seed(p, '82[Group](name="greens")')
    _rec("82[Group] typed name refused; NO group created "
         "(neither 'greens' nor the default 'group')",
         not r.get("ok")
         and r.get("error") == "UNSUPPORTED_ARGS: name"
         and "greens" not in (s.groups or {})
         and "group" not in (s.groups or {})
         and _snap(p) == before,
         f"ok={r.get('ok')} err={r.get('error')} "
         f"groups={sorted((s.groups or {}).keys())}")
    _rec("82[Group] single-atom receipt is exact",
         _receipts(r) == [{"dell": 82, "ok": False,
                           "error": "UNSUPPORTED_ARGS: name",
                           "skipped": False,
                           "reason": "UNSUPPORTED_ARGS: name"}],
         f"ars={_receipts(r)}")

    r = execute_seed(p, '82[Group](bogus="x")')
    _rec("82[Group] bogus role refuses UNSUPPORTED_ARGS "
         "(not UNKNOWN_ROLE — no signature exists)",
         not r.get("ok") and r.get("error") == "UNSUPPORTED_ARGS: bogus",
         f"err={r.get('error')}")

    r = execute_seed(p, '82[Group](zrole="1", arole="2")')
    _rec("refusal names roles SORTED deterministically",
         r.get("error") == "UNSUPPORTED_ARGS: arole, zrole",
         f"err={r.get('error')}")

    r = execute_seed(p, '82[Group](name="greens") :: blues')
    _rec("typed+label on untyped Dell refuses (the label no "
         "longer silently wins); no group created",
         not r.get("ok")
         and r.get("error") == "UNSUPPORTED_ARGS: name"
         and "blues" not in (s.groups or {})
         and "greens" not in (s.groups or {}),
         f"ok={r.get('ok')} err={r.get('error')}")

    before = _snap(p)
    r = execute_seed(p, '97[Define](name="tempo", meaning="120")')
    _rec("97[Define] typed args refused, sorted roles, no "
         "default 'def' definition lands",
         not r.get("ok")
         and r.get("error") == "UNSUPPORTED_ARGS: meaning, name"
         and _snap(p) == before,
         f"ok={r.get('ok')} err={r.get('error')} defs={s.defs}")

    r = execute_seed(p, '78[Cause](cause="rain", effect="flood")')
    _rec("78[Cause] typed args refused as UNSUPPORTED_ARGS — "
         "the misleading 'malformed_relation' never surfaces",
         not r.get("ok")
         and r.get("error") == "UNSUPPORTED_ARGS: cause, effect"
         and "malformed_relation" not in _errs(r)
         and list(getattr(s, "causes", []) or []) == [],
         f"ok={r.get('ok')} err={r.get('error')}")
    _cleanup(owner)


def _chains():
    from form.mandell.executor import execute_seed
    owner = "GateChain"
    p = _fresh(owner)
    s = _st(p)
    _setup(p)

    r = execute_seed(p, '82[Group](name="x") > 55[Set] :: k=v')
    ars = _receipts(r)
    _rec("FlowTo: refused atom fails honestly and the chain "
         "continues (Set still executes)",
         not r.get("ok") and len(ars) == 2
         and ars[0].get("error") == "UNSUPPORTED_ARGS: name"
         and ars[1].get("ok") is True
         and (s.store or {}).get("k") == "v",
         f"ok={r.get('ok')} ars={ars} store={s.store}")

    r = execute_seed(p, '82[Group](name="x") >> 55[Set] :: k2=v2')
    ars = _receipts(r)
    _rec("FlowThru: downstream of a gate refusal is "
         "flow-blocked with its established skip receipt",
         not r.get("ok") and len(ars) == 2
         and ars[1].get("skipped") is True
         and ars[1].get("error") == "flow_thru_block"
         and "k2" not in (s.store or {}),
         f"ok={r.get('ok')} ars={ars} store={s.store}")
    _cleanup(owner)


def _registered_regression():
    from form.mandell.executor import execute_seed
    owner = "GateReg"
    p = _fresh(owner)
    s = _st(p)
    _setup(p)
    garden = ["garden_gate", "garden_fern"]

    r = execute_seed(p, '52[Filter](predicate="garden")')
    _rec("registered 52[Filter] typed behavior unchanged "
         "(narrows by predicate)",
         r.get("ok") and list(s.selected) == garden,
         f"ok={r.get('ok')} selected={s.selected}")
    execute_seed(p, "51[Select]")
    r = execute_seed(p, '52[Filter](bogus="x")')
    _rec("registered 52 bogus role still UNKNOWN_ROLE "
         "(gate does not leak into regime 1)",
         not r.get("ok") and "UNKNOWN_ROLE" in str(r.get("error", ""))
         and "UNSUPPORTED_ARGS" not in str(r.get("error", "")),
         f"err={r.get('error')}")
    r = execute_seed(p, '55[Set](key="k", value="v")')
    _rec("registered 55[Set] valid typed call unchanged",
         r.get("ok") and (s.store or {}).get("k") == "v",
         f"ok={r.get('ok')} store={s.store}")
    r = execute_seed(p, '55[Set](bogus="x")')
    _rec("registered precedence preserved: MISSING_REQUIRED "
         "surfaces before UNKNOWN_ROLE",
         not r.get("ok")
         and str(r.get("error", "")).startswith("MISSING_REQUIRED"),
         f"err={r.get('error')}")
    r = execute_seed(p, '55[Set](key="k2", value="v2") :: other=v')
    _rec("registered typed+legacy conflict still "
         "ARGUMENT_CONFLICT before mutation",
         not r.get("ok") and "ARGUMENT_CONFLICT" in str(r.get("error", ""))
         and "k2" not in (s.store or {}),
         f"err={r.get('error')} store={s.store}")
    execute_seed(p, '82[Group] :: greens')
    execute_seed(p, "51[Select]")
    r = execute_seed(p, '53[Scope](name="greens")')
    _rec("registered 53[Scope] typed behavior unchanged",
         r.get("ok") and s.scope == "greens",
         f"ok={r.get('ok')} scope={s.scope}")
    _cleanup(owner)


def _legacy_corpus():
    from form.mandell.executor import execute_seed
    owner = "GateLeg"
    p = _fresh(owner)
    s = _st(p)
    _setup(p)

    r = execute_seed(p, '82[Group] :: predicate="garden"')
    _rec("legacy: arg-shaped text after :: is a LABEL "
         "(args=={} — gate inert); group takes the literal name",
         r.get("ok") and 'predicate="garden"' in (s.groups or {})
         and "UNSUPPORTED_ARGS" not in _errs(r),
         f"ok={r.get('ok')} groups={sorted((s.groups or {}).keys())}")
    r = execute_seed(p, "82[Group] :: playlist (draft) mix")
    _rec("legacy: label with parentheses is label data",
         r.get("ok") and "playlist (draft) mix" in (s.groups or {})
         and "UNSUPPORTED_ARGS" not in _errs(r),
         f"ok={r.get('ok')} groups={sorted((s.groups or {}).keys())}")
    r = execute_seed(p, "78[Cause] :: rain>flood")
    _rec("legacy: relation label grammar a>b unchanged",
         r.get("ok")
         and [tuple(x) for x in (getattr(s, "causes", None) or [])]
         == [("rain", "flood")],
         f"ok={r.get('ok')} causes={getattr(s, 'causes', None)}")
    r = execute_seed(p, "97[Define] :: tempo=120")
    _rec("legacy: definition label grammar name=meaning "
         "unchanged",
         r.get("ok") and (s.defs or {}).get("tempo") == "120",
         f"ok={r.get('ok')} defs={s.defs}")
    r = execute_seed(p, "55[Set] :: note=a=b")
    _rec("legacy: k=v payload with '=' inside the value "
         "unchanged",
         r.get("ok") and (s.store or {}).get("note") == "a=b",
         f"ok={r.get('ok')} store={s.store}")
    r = execute_seed(p, "51[Select] > 82[Group] :: greens > 54[Query]")
    _rec("legacy: segment label mid-chain unchanged",
         r.get("ok") and "greens" in (s.groups or {})
         and all(a.get("ok") for a in _receipts(r)),
         f"ok={r.get('ok')} ars={_receipts(r)}")
    r = execute_seed(p, "60[Branch] :: true > 55[Set] :: a=1 > "
                        "59[Route] > 55[Set] :: b=2 > 61[Join]")
    _rec("legacy: control frame with condition label + Else "
         "arm unchanged (taken arm only)",
         r.get("ok") and (s.store or {}).get("a") == "1"
         and "b" not in (s.store or {})
         and "UNSUPPORTED_ARGS" not in _errs(r),
         f"ok={r.get('ok')} store={s.store} ars={_receipts(r)}")
    _cleanup(owner)


def _skips_preserved():
    from form.mandell.executor import execute_seed
    owner = "GateSkip"
    p = _fresh(owner)
    s = _st(p)
    _setup(p)

    r = execute_seed(p, '51[Select] > 151[Harmonic](bogus="x") '
                        '> 55[Set] :: k=v')
    ars = _by_dell(r, 151)
    _rec("reserved 151[Harmonic] with args keeps its "
         "Decision-1 skip receipt — args never inspected, "
         "no UNSUPPORTED_ARGS",
         len(ars) == 1 and ars[0].get("ok") is False
         and ars[0].get("skipped") is True
         and ars[0].get("error") == "reserved/not-active"
         and "UNSUPPORTED_ARGS" not in _errs(r)
         and (s.store or {}).get("k") == "v",
         f"ars={_receipts(r)}")
    r = execute_seed(p, '53[Scope] :: nope >> 55[Set](key="k9", value="v9")')
    ars = _by_dell(r, 55)
    _rec("FlowThru-blocked REGISTERED Dell: args unvalidated, "
         "established flow_thru_block skip, store untouched",
         len(ars) == 1 and ars[0].get("skipped") is True
         and ars[0].get("error") == "flow_thru_block"
         and "k9" not in (s.store or {}),
         f"ars={_receipts(r)} store={s.store}")
    _cleanup(owner)


def _heads():
    from form.mandell.executor import execute_seed
    cases = [
        (60, '60[Branch](zzrole="zzvalue") :: true > 55[Set] :: k=v > 61[Join]'),
        (62, '62[Parallel](zzrole="zzvalue") > 55[Set] :: k=v > 61[Join]'),
        (63, '63[Sequence](zzrole="zzvalue") > 55[Set] :: k=v > 61[Join]'),
        (64, '64[Until](zzrole="zzvalue") :: false > 55[Set] :: k=v > 61[Join]'),
        (65, '65[While](zzrole="zzvalue") :: true > 55[Set] :: k=v > 61[Join]'),
        (66, '51[Select] > 66[ForEach](zzrole="zzvalue") > 55[Set] :: k=v > 61[Join]'),
    ]
    for n, seed in cases:
        owner = f"GateHead{n}"
        p = _fresh(owner)
        s = _st(p)
        _setup(p)
        before = _snap(p)
        r = execute_seed(p, seed)
        head = _by_dell(r, n)
        body = _by_dell(r, 55)
        frame = dict(s.last_frame or {})
        _rec(f"head {n}: refused head -> body never executes "
             f"(skip receipt, zero iterations, failed frame, "
             f"zero business mutation)",
             not r.get("ok")
             and str(r.get("error", "")).startswith("UNSUPPORTED_ARGS")
             and len(head) == 1 and head[0].get("ok") is False
             and head[0].get("skipped") is False
             and str(head[0].get("error", "")).startswith("UNSUPPORTED_ARGS")
             and len(body) == 1 and body[0].get("skipped") is True
             and "control head refused" in str(body[0].get("reason", ""))
             and "k" not in (s.store or {})
             and frame.get("status") == "fail"
             and str(frame.get("error", "")).startswith("UNSUPPORTED_ARGS")
             and frame.get("iterations") == 0
             and _snap(p) == before,
             f"ok={r.get('ok')} err={r.get('error')} head={head} "
             f"body={body} frame={frame.get('status')}/"
             f"{frame.get('error')}/{frame.get('iterations')}")
        _cleanup(owner)

    # Branch with an Else arm: every body occurrence receipts.
    owner = "GateHeadElse"
    p = _fresh(owner)
    s = _st(p)
    _setup(p)
    r = execute_seed(p, '60[Branch](zzrole="zzvalue") :: true '
                        '> 55[Set] :: a=1 > 59[Route] '
                        '> 55[Set] :: b=2 > 61[Join]')
    skipped_dells = [a.get("dell") for a in _receipts(r)
                     if a.get("skipped")]
    _rec("head 60 with Else: taken arm, Else marker and "
         "untaken arm ALL receipt head-refusal skips; "
         "nothing executes",
         not r.get("ok") and skipped_dells == [55, 59, 55]
         and (s.store or {}) == {}
         and all("control head refused" in str(a.get("reason", ""))
                 for a in _receipts(r) if a.get("skipped")),
         f"skipped={skipped_dells} store={s.store} "
         f"ars={_receipts(r)}")
    _cleanup(owner)

    # Nested: refused outer head; inner frame occurrences all
    # skip; the chain continues after the outer Join.
    owner = "GateHeadNest"
    p = _fresh(owner)
    s = _st(p)
    _setup(p)
    r = execute_seed(p, '63[Sequence](zzrole="zzvalue") '
                        '> 60[Branch] :: true > 55[Set] :: k=v '
                        '> 61[Join] > 61[Join] > 55[Set] :: after=1')
    body = [a for a in _receipts(r) if a.get("skipped")]
    _rec("nested: refused outer Sequence — inner Branch, its "
         "body and the inner Join all skip; trailing atom "
         "after the outer Join still executes",
         not r.get("ok")
         and str(r.get("error", "")).startswith("UNSUPPORTED_ARGS")
         and [a.get("dell") for a in body] == [60, 55, 61]
         and "k" not in (s.store or {})
         and (s.store or {}).get("after") == "1",
         f"ok={r.get('ok')} err={r.get('error')} body={body} "
         f"store={s.store}")
    _cleanup(owner)

    # Blocked head: flow decides before _run_atom — the
    # head's args are never inspected.
    owner = "GateHeadBlock"
    p = _fresh(owner)
    s = _st(p)
    _setup(p)
    r = execute_seed(p, '55[Set](bogus="x") >> 60[Branch](zzrole="zzvalue") '
                        ':: true >> 55[Set] :: k=v >> 61[Join]')
    _rec("FlowThru-blocked head: flow_thru_block skip, NO "
         "UNSUPPORTED_ARGS anywhere (args uninspected)",
         not r.get("ok") and "UNSUPPORTED_ARGS" not in _errs(r)
         and all(a.get("skipped") for a in _receipts(r)[1:])
         and (s.store or {}) == {},
         f"ars={_receipts(r)}")
    _cleanup(owner)


def _join():
    from form.mandell.executor import execute_seed

    # J1: clean frame, Join itself carries unsupported args.
    owner = "GateJoin1"
    p = _fresh(owner)
    s = _st(p)
    _setup(p)
    r = execute_seed(p, '63[Sequence] > 55[Set] :: k=v '
                        '> 61[Join](zzrole="zzvalue")')
    jr = _by_dell(r, 61)
    frame = dict(s.last_frame or {})
    _rec("J1: Join with unsupported args on a clean frame — "
         "body ran, Join refused, closure NOT faked, chain "
         "and frame errors name the refusal (not join_fail)",
         (s.store or {}).get("k") == "v"
         and len(jr) == 1 and jr[0].get("ok") is False
         and jr[0].get("error") == "UNSUPPORTED_ARGS: zzrole"
         and not r.get("ok")
         and r.get("error") == "UNSUPPORTED_ARGS: zzrole"
         and frame.get("status") == "fail"
         and frame.get("error") == "UNSUPPORTED_ARGS: zzrole",
         f"jr={jr} err={r.get('error')} frame={frame}")
    _cleanup(owner)

    # J2: frame already contains a refusal; Join also carries
    # unsupported args — the FIRST refusal stays the chain
    # error; both receipts carry their own refusal.
    owner = "GateJoin2"
    p = _fresh(owner)
    s = _st(p)
    _setup(p)
    r = execute_seed(p, '63[Sequence] > 82[Group](name="greens") '
                        '> 61[Join](zzrole="zzvalue")')
    body = _by_dell(r, 82)
    jr = _by_dell(r, 61)
    frame = dict(s.last_frame or {})
    _rec("J2: body refusal + Join refusal — original (body) "
         "refusal preserved as the chain error; Join receipt "
         "carries its own UNSUPPORTED_ARGS; no group created",
         len(body) == 1
         and body[0].get("error") == "UNSUPPORTED_ARGS: name"
         and len(jr) == 1 and jr[0].get("ok") is False
         and jr[0].get("error") == "UNSUPPORTED_ARGS: zzrole"
         and r.get("error") == "UNSUPPORTED_ARGS: name"
         and frame.get("status") == "fail"
         and "greens" not in (s.groups or {})
         and "group" not in (s.groups or {}),
         f"body={body} jr={jr} err={r.get('error')} frame={frame}")
    _cleanup(owner)

    # J3 (preserved base behavior, probe-pinned): body refusal
    # under registered law + CLEAN Join — chain error stays
    # the body's; the Join receipt honestly reports join_fail
    # on the failed frame; nothing is rewritten by the gate.
    owner = "GateJoin3"
    p = _fresh(owner)
    s = _st(p)
    _setup(p)
    r = execute_seed(p, '63[Sequence] > 55[Set](bogus="x") > 61[Join]')
    jr = _by_dell(r, 61)
    frame = dict(s.last_frame or {})
    _rec("J3: pre-existing refusal + clean Join — preserved "
         "semantics (chain error = body refusal, Join receipt "
         "join_fail, frame fail)",
         not r.get("ok") and r.get("error") == "MISSING_REQUIRED: key"
         and len(jr) == 1 and jr[0].get("ok") is False
         and jr[0].get("error") == "join_fail"
         and frame.get("status") == "fail"
         and frame.get("error") == "join_fail",
         f"jr={jr} err={r.get('error')} frame={frame}")
    _cleanup(owner)


def _diagnostics_blob(r):
    """Every diagnostic surface the REFUSAL generates: the
    top-level error, all atom receipts, and all appended
    messages EXCEPT the universal seed-echo header lines
    (the caller's own input text — pre-mortem #3)."""
    msgs = [str(m) for m in (r.get("messages") or [])
            if not str(m).startswith(("Mandell:", "English:"))]
    return json.dumps({"error": r.get("error"),
                       "atom_results": _receipts(r),
                       "messages": msgs}, default=str)


def _canary():
    from form.mandell.executor import execute_seed
    owner = "GateCan"
    p = _fresh(owner)
    s = _st(p)
    _setup(p)

    r = execute_seed(p, f'82[Group](name="{CANARY}")')
    blob = _diagnostics_blob(r)
    gate_lines = [str(m) for m in (r.get("messages") or [])
                  if "no registered typed signature" in str(m)]
    _rec("canary: refusal diagnostics name the role and "
         "NEVER the raw value (plain atom)",
         r.get("error") == "UNSUPPORTED_ARGS: name"
         and CANARY not in blob
         and len(gate_lines) == 1 and CANARY not in gate_lines[0]
         and "name" in gate_lines[0],
         f"err={r.get('error')} blob_has_canary={CANARY in blob} "
         f"gate_lines={gate_lines}")
    _rec("canary scoping is explicit: the result's seed echo "
         "is the caller's own input text (universal header)",
         CANARY in str(r.get("seed", "")),
         f"seed={r.get('seed')}")

    r = execute_seed(p, f'63[Sequence](note="{CANARY}") '
                        '> 55[Set] :: k=v > 61[Join]')
    blob = _diagnostics_blob(r)
    _rec("canary: head refusal + skipped-body receipts leak "
         "no raw value either",
         str(r.get("error", "")).startswith("UNSUPPORTED_ARGS")
         and CANARY not in blob
         and (s.store or {}) == {},
         f"err={r.get('error')} blob_has_canary={CANARY in blob}")
    _cleanup(owner)


def _repl():
    owner = "GateRepl"
    _cleanup(owner)
    before = set(os.listdir(STATE_DIR))
    lines = ('82[Group](name="greens")\n'
             '53[Scope] :: greens\n'
             '82[Group] :: greens\n'
             '53[Scope] :: greens\n')
    proc = subprocess.run(
        [sys.executable, "-m", "form.repl", "--owner", owner],
        input=lines, capture_output=True, text=True,
        cwd=ROOT, timeout=120)
    out = proc.stdout + proc.stderr
    _rec("REPL (real user path): typed Group refuses in the "
         "user's own interface (the REPL surfaces the refusal "
         "message — roles named, value never echoed); the "
         "group is never created (Scope then refuses "
         "'greens'); the legacy path works end-to-end",
         "has no registered typed signature" in out
         and "typed arguments refused before execution" in out
         and "(roles: name)" in out
         and "Group group" not in out
         and "unknown scope 'greens'" in out
         and "Group greens" in out
         and "Scope -> greens" in out,
         f"rc={proc.returncode} out_tail={out[-400:]}")
    # Snapshot-diff cleanup of exactly what this session made.
    for name in sorted(set(os.listdir(STATE_DIR)) - before):
        if owner in name:
            path = os.path.join(STATE_DIR, name)
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
    _cleanup(owner)


def main() -> bool:
    _registry_scope()
    _sweep_untyped()
    _family_witnesses()
    _chains()
    _registered_regression()
    _legacy_corpus()
    _skips_preserved()
    _heads()
    _join()
    _canary()
    _repl()
    total = len(RESULTS)
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    for name, ok, detail in RESULTS:
        if not ok:
            print(f"FAIL {name} :: {detail}")
    print(f"D1_UNSUPPORTED_ARG_GATE: {passed}/{total}")
    return passed == total


def smoke() -> bool:
    return main()


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
