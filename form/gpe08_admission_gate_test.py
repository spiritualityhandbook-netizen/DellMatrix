#!/usr/bin/env python3
"""GP-E08 Scope A — admission-refusal gate at the public boundary
(Part II, anchor row #24). Director bounded build authorization
7079028132 on Revision 1 (7078859127) with corrections 7078835811.

THE GATE (the only product change this suite certifies): inside
form/repl.py `_dispatch_public_line`, AFTER every existing
prefix/meta door (ORGANIZE, SEE, ROS, learn, why, lifecycle,
Greek) and BEFORE the P10 seed stage / DCC-IV flow / DCC-V
composite / English tail, a whole-line seed CLAIM that the
canonical grammar rejects is refused by the admission layer with
a typed, user-visible non-execution receipt and zero mutation.
No changes to admission.py / translate.py / parse_seed(); no
second executor; no altered prior-door authority.

WHOLE-LINE CLAIM DISCRIMINATOR (Director fix 2, 7079028132): the
Revision-1 regex-remove predicate is REJECTED as an enforcement
boundary. The discriminator derives from the established seed
grammar itself: it consumes the line left-to-right using seed.py's
OWN token definitions (atom incl. malformed unclosed forms, typed
argument lists incl. malformed role-shaped attempts, the FLOW_OPS
operators, and the AF-2 segment-label rule via seed's own
_scan_label_end). If every character is consumed by grammar
material, the line is a claim and parse_seed/admit decide it. ANY
unconsumed residue makes the line content-bearing English: the
gate does not refuse it, does not call admit() on it, and today's
path runs byte-for-byte. Boundary case, stated plainly: a
parenthesized group after an atom that is NOT role-shaped
(e.g. `12[Harmonic] (see notes)`) is content residue, not an args
attempt — the grammar's args have a defined role="value" shape.

CLASSIFIER FAILURE (Director fix 1): for a CANDIDATE, any
exception from admit() fails CLOSED (typed classifier_failure
receipt, no execution, no mutation). For a NONcandidate, admit()
is never invoked at all (T8b negative spy).

FLOW-DOOR PRECEDENCE (Director CORRECTION REQUIRED 7079919649,
on Uni classification 7079801602): the gate's claim class is
SEED claims. A line carrying the correspondence flow operator
`>>>` is a FLOW claim: when parse_seed declines it (e.g. an
unknown head Dell), the adopted G31-CONTRACT-01 D-6 contract
gives the refusal to the DCC-IV flow door ("Flow refused ...
REQUIRES_RUNTIME_SUPPORT"), not to this gate. The built gate
claimed such lines whole-line (their every character IS seed
grammar material, `>>>` included) and answered with the
admission surface, silently replacing the older contract's
observable refusal — g31_contract_test went 19/20. The
reconciliation narrows the GATE, not the discriminator and not
the G31 expectation: the gate does not claim a line containing
`>>>`; both refusal paths keep their typed surfaces, proven by
the T19/T20 pair (same unknown Dell, with and without the flow
operator) and the T21 known-Dell FlowOver control.

TWO REVISION-1 PREMISES FALSIFIED BY THE CANONICAL CODE ITSELF
(probe-verified at head a2221e4c before this build; filed as
unresolved-design cases for a separate Director ruling — the gate
does NOT act on either, because acting would require changing a
canonical parser/door, outside 7079028132):
  UD-1 (was T11): `12[Harmonik]` PARSES — the manifest resolver
  resolves the term against Dell 12 (rendered 12[Test]) and
  parse_seed returns ok. `47[Embed] > 12[Harmonik]` is ADMITTED
  by admit() and executes today. T11 is therefore a
  grammar-fidelity control: the gate must NOT refuse it.
  UD-2 (was T9/T10 "idea created"): today `create an idea called
  12[Harmonic]` (quoted or not) never reaches the English door —
  the pre-existing looks_like_seed branch claims any line with a
  closed atom fragment and answers "Seed error", recording an
  outcome, creating nothing. That branch is a prior door whose
  authority Scope A does not alter. T9/T10 therefore assert the
  gate's actual contract: no gate refusal, admit() not invoked,
  and today's path preserved exactly (legacy seed-branch receipt,
  outcome recorded by that branch, no idea created BY THE GATE's
  action or inaction).

Realism labels: T1 drives the literal program entry point
(`python3 -m form.repl`, piped stdin) = REAL_USER_PATH limited to
the piped REPL, not interactive human interaction. All other
checks drive _dispatch_public_line directly = INTEGRATION /
high-fidelity dispatch (precedent: iri_i, gpe08 route suites).

Isolation: every check uses its own uniquely-named Program owner
with state files cleaned before use (canonical state dir, exact
owner scope); state is fingerprinted before/after, never assumed
empty.
"""

from __future__ import annotations

import contextlib
import glob
import io
import os
import shutil
import subprocess
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state")

CHECKS = []


def check(name, cond, detail=""):
    CHECKS.append((name, bool(cond)))
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")


def _cleanup(owner):
    for f in glob.glob(os.path.join(STATE_DIR, f"*{owner}*")):
        try:
            if os.path.isdir(f):
                shutil.rmtree(f)
            else:
                os.remove(f)
        except FileNotFoundError:
            pass


def _fresh(owner):
    _cleanup(owner)
    from form.open import Program
    return Program(owner=owner)


def _snap(p):
    return (len(getattr(p, "ideas", None) or []),
            len(getattr(p, "history", None) or []),
            len(getattr(p, "outcome_records", None) or {}),
            getattr(p, "outcome_seq", None))


def _drive(p, line):
    """One line through the canonical public boundary, stdout
    captured (print and _say both land there)."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        p = _dispatch(p, line)
    return p, buf.getvalue()


def _dispatch(p, line):
    from form.repl import _dispatch_public_line
    return _dispatch_public_line(p, line, str(uuid.uuid4()))


GATE_REFUSAL = "Seed admission refused"
NOT_EXECUTED = "This line was not executed."


class _AdmitSpy:
    """Negative spy: records calls; optionally raises."""

    def __init__(self, raise_exc=None):
        self.calls = []
        self.raise_exc = raise_exc

    def __call__(self, text):
        self.calls.append(text)
        if self.raise_exc is not None:
            raise self.raise_exc
        raise AssertionError("spy called without a stubbed verdict")


@contextlib.contextmanager
def _patched_admit(spy):
    import form.mandell.admission as adm_mod
    orig = adm_mod.admit
    adm_mod.admit = spy
    try:
        yield spy
    finally:
        adm_mod.admit = orig


# ---------------------------------------------------------------- T1
def t1_piped_repl():
    # Output is the real-user-path evidence: at the unmodified
    # head the same session prints the English fall-through
    # signature "SEMANTIC: save[Keep]" (probe-verified); the gate
    # replaces it with the typed refusal. (A fresh Program(owner)
    # does not hydrate persisted outcome state on construction —
    # verified at this head — so no load-based assertion is made.)
    owner = "GPE08GateT1"
    _cleanup(owner)
    # No trailing "save" line: the save command itself translates
    # to Dell 10[Keep] and would print the same SEMANTIC signature
    # legitimately. EOF ends the piped session.
    lines = ["10[Keep"]
    proc = subprocess.run(
        [sys.executable, "-m", "form.repl", "--owner", owner],
        input="\n".join(lines) + "\n", capture_output=True, text=True,
        cwd=ROOT, timeout=300)
    out = proc.stdout + proc.stderr
    check("T1_real_user_path_piped_repl_refusal",
          GATE_REFUSAL in out and NOT_EXECUTED in out
          and "SEMANTIC: save[Keep]" not in out,
          f"refusal={GATE_REFUSAL in out} "
          f"fallthrough={'SEMANTIC: save[Keep]' in out}")
    _cleanup(owner)


# ---------------------------------------------------------------- T2
def t2_dispatch_refusal():
    p = _fresh("GPE08GateT2")
    before = _snap(p)
    p, out = _drive(p, "10[Keep")
    check("T2_dispatch_whole_line_claim_refused_no_mutation",
          GATE_REFUSAL in out and "seed_parse_refusal" in out
          and NOT_EXECUTED in out and _snap(p) == before,
          f"state {before} -> {_snap(p)}")


# ---------------------------------------------------------------- T3
def t3_valid_seed_controls():
    p = _fresh("GPE08GateT3")
    before = _snap(p)
    p, out1 = _drive(p, "10[Keep]")
    mid = _snap(p)
    p, out2 = _drive(p, "10[Keep] > 27[Checkpoint]")
    check("T3_valid_single_and_chain_execute",
          GATE_REFUSAL not in out1 and GATE_REFUSAL not in out2
          and mid[1] > before[1] and _snap(p)[1] > mid[1]
          and "Chain atoms=2" in out2,
          f"history {before[1]} -> {mid[1]} -> {_snap(p)[1]}")


# ---------------------------------------------------------------- T4
def t4_plain_english_control():
    p = _fresh("GPE08GateT4")
    before = _snap(p)
    p, out = _drive(p, "create an idea called Gate Plain")
    check("T4_plain_english_unchanged",
          GATE_REFUSAL not in out and _snap(p)[1] > before[1],
          f"history {before[1]} -> {_snap(p)[1]}")


# ---------------------------------------------------------------- T5
def t5_see_door_precedence():
    p = _fresh("GPE08GateT5")
    before = _snap(p)
    p, out = _drive(p, "proposals search 12[Harmonic]")
    check("T5_see_door_claims_bracketed_content",
          "proposals search" in out and GATE_REFUSAL not in out
          and _snap(p) == before,
          f"state {before} -> {_snap(p)}")


# ---------------------------------------------------------------- T6
def t6_latinmandell_control():
    p = _fresh("GPE08GateT6")
    before = _snap(p)
    p, out1 = _drive(p, "la serva")
    mid = _snap(p)
    p, out2 = _drive(p, "la zzzqqq")
    check("T6_latinmandell_mapped_and_unmapped_unchanged",
          GATE_REFUSAL not in out1 and GATE_REFUSAL not in out2
          and mid[1] > before[1]
          and "no LA map" in out2 and _snap(p) == mid,
          f"history {before[1]} -> {mid[1]} -> {_snap(p)[1]}")


# ---------------------------------------------------------------- T7
def t7_reissue_refusal():
    from form import repl as repl_mod
    p = _fresh("GPE08GateT7")
    # A real executed line records a real outcome...
    p, _ = _drive(p, "10[Keep]")
    recs = [r for r in (p.outcome_records or {}).values()
            if isinstance(r, dict)]
    assert recs, "no outcome recorded for staging"
    seq = recs[-1].get("outcome_seq")
    # ...whose recorded source is rewritten to the historical
    # pre-gate shape: a whole-line malformed seed claim that the
    # old route executed as English (the T1 fall-through).
    for r in (p.outcome_records or {}).values():
        if isinstance(r, dict) and r.get("outcome_seq") == seq:
            r["input"] = "10[Keep"
    before = _snap(p)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        p, pending = repl_mod._handle_reissue(p, f"reissue {seq}", None)
        staged = pending
        p, pending = repl_mod._handle_reissue(p, "reissue confirm",
                                               pending)
    out = buf.getvalue()
    check("T7_reissue_of_historical_claim_refused_at_same_boundary",
          staged == "10[Keep" and GATE_REFUSAL in out
          and NOT_EXECUTED in out and _snap(p) == before,
          f"staged={staged!r} state {before} -> {_snap(p)}")


# ------------------------------------------------------- T8a / T8b
def t8a_candidate_classifier_failure_fails_closed():
    p = _fresh("GPE08GateT8a")
    before = _snap(p)
    spy = _AdmitSpy(raise_exc=RuntimeError("classifier boom"))
    with _patched_admit(spy):
        p, out = _drive(p, "10[Keep")
    check("T8a_candidate_admit_exception_fails_closed",
          spy.calls and GATE_REFUSAL in out
          and "classifier_failure" in out and NOT_EXECUTED in out
          and _snap(p) == before,
          f"calls={len(spy.calls)} state {before} -> {_snap(p)}")


def t8b_noncandidate_spy():
    p = _fresh("GPE08GateT8b")
    before = _snap(p)
    spy = _AdmitSpy()  # raises AssertionError if ever called
    with _patched_admit(spy):
        p, out = _drive(p, "create an idea called Gate Spy")
    check("T8b_spy_no_classifier_call_on_noncandidate",
          spy.calls == [] and GATE_REFUSAL not in out
          and _snap(p)[1] > before[1],
          f"calls={spy.calls} history {before[1]} -> {_snap(p)[1]}")


# ---------------------------------------------------------------- T9
def t9_quoted_content_control():
    p = _fresh("GPE08GateT9")
    before = _snap(p)
    spy = _AdmitSpy()
    with _patched_admit(spy):
        p, out = _drive(p, "create an idea called '12[Harmonic]'")
    after = _snap(p)
    # UD-2: the legacy looks_like_seed branch answers this line
    # today ("Seed error", outcome recorded, no idea). The gate
    # must add NOTHING: no gate refusal, no admit() call, and the
    # legacy branch's own footprint preserved exactly.
    check("T9_quoted_embedded_content_gate_silent_path_preserved",
          spy.calls == [] and GATE_REFUSAL not in out
          and "Seed error" in out
          and after[0] == before[0] and after[2] == before[2] + 1,
          f"state {before} -> {after}")


# --------------------------------------------------------------- T10
def t10_unquoted_content_control():
    p = _fresh("GPE08GateT10")
    before = _snap(p)
    spy = _AdmitSpy()
    with _patched_admit(spy):
        p, out = _drive(p, "create an idea called 12[Harmonic]")
    after = _snap(p)
    check("T10_unquoted_embedded_content_gate_silent_path_preserved",
          spy.calls == [] and GATE_REFUSAL not in out
          and "Seed error" in out
          and after[0] == before[0] and after[2] == before[2] + 1,
          f"state {before} -> {after}")


# --------------------------------------------------------------- T11
def t11_grammar_fidelity_control():
    # UD-1: parse_seed ACCEPTS this line (resolver resolves the
    # term); the gate must not invent a refusal the canonical
    # grammar does not make. Executes via P10 exactly as today.
    p = _fresh("GPE08GateT11")
    before = _snap(p)
    p, out = _drive(p, "47[Embed] > 12[Harmonik]")
    check("T11_grammar_fidelity_resolver_accepted_line_not_refused",
          GATE_REFUSAL not in out and "Chain atoms=2" in out
          and _snap(p)[1] > before[1],
          f"history {before[1]} -> {_snap(p)[1]}")


# --------------------------------------------------------------- T12
def t12_malformed_typed_arg():
    p = _fresh("GPE08GateT12")
    before = _snap(p)
    p, out = _drive(p, "12[Harmonic](count=3)")
    check("T12_malformed_whole_line_seed_with_typed_arg_refused",
          GATE_REFUSAL in out and "seed_parse_refusal" in out
          and NOT_EXECUTED in out and _snap(p) == before,
          f"state {before} -> {_snap(p)}")


# --------------------------------------------------------------- T13
def t13_malformed_multiatom_with_label():
    p = _fresh("GPE08GateT13")
    before = _snap(p)
    p, out = _drive(p, "08[Create] > 12[Harmonic] :: my plan :: second")
    check("T13_malformed_multiatom_terminal_label_refused",
          GATE_REFUSAL in out and "seed_parse_refusal" in out
          and NOT_EXECUTED in out and _snap(p) == before,
          f"state {before} -> {_snap(p)}")


# --------------------------------------------------------------- T14
def t14_english_embedding_bracketed_literal():
    p = _fresh("GPE08GateT14")
    before = _snap(p)
    spy = _AdmitSpy()
    with _patched_admit(spy):
        p, out1 = _drive(p, "my favorite atom is 12[Harmonic] today")
        mid = _snap(p)
        p, out2 = _drive(p, "12[Harmonic] (see notes)")
    check("T14_english_with_bracketed_literal_content_not_refused",
          spy.calls == [] and GATE_REFUSAL not in out1
          and GATE_REFUSAL not in out2
          and mid[2] == before[2] + 1,
          f"calls={spy.calls} outcomes {before[2]} -> {mid[2]}")


# --------------------------------------------------------------- T15
def t15_valid_args_and_labeled_chain_p10():
    p = _fresh("GPE08GateT15")
    before = _snap(p)
    p, out1 = _drive(p, '08[Create](name="Gate Wish")')
    mid = _snap(p)
    p, out2 = _drive(
        p, '03[Logic] > 55[Set](key="tempo", value="120") :: session')
    check("T15_valid_arg_seed_and_labeled_chain_execute",
          GATE_REFUSAL not in out1 and GATE_REFUSAL not in out2
          and "Gate Wish" in out1 and mid[1] > before[1]
          and "Chain atoms=2 label=session" in out2
          and _snap(p)[1] > mid[1],
          f"history {before[1]} -> {mid[1]} -> {_snap(p)[1]}")


# --------------------------------------------------------------- T16
def t16_classifier_raise_on_candidate_no_effect():
    p = _fresh("GPE08GateT16")
    before = _snap(p)
    spy = _AdmitSpy(raise_exc=ValueError("classifier exploded"))
    with _patched_admit(spy):
        p, out = _drive(p, '47[Embed](role="memoir"')
    after = _snap(p)
    check("T16_classifier_raise_on_candidate_zero_effects",
          spy.calls and GATE_REFUSAL in out
          and "classifier_failure" in out
          and after == before,
          f"state {before} -> {after}")


# --------------------------------------------------------------- T17
def t17_prefix_doors_never_reach_gate():
    p = _fresh("GPE08GateT17")
    before = _snap(p)
    spy = _AdmitSpy()
    with _patched_admit(spy):
        p, out1 = _drive(p, "proposals search 12[Harmonic]")
        p, out2 = _drive(p, "proposals organize 1 topic:12[Harmonic]")
    check("T17_see_and_organize_doors_precede_gate",
          spy.calls == [] and "proposals search" in out1
          and "proposals organize" in out2
          and GATE_REFUSAL not in out1 and GATE_REFUSAL not in out2
          and _snap(p) == before,
          f"calls={spy.calls} state {before} -> {_snap(p)}")


# --------------------------------------------- foreign-owner control
def t18_no_foreign_owner_mutation():
    pa = _fresh("GPE08GateT18A")
    pb = _fresh("GPE08GateT18B")
    before_b = _snap(pb)
    pa, _ = _drive(pa, "10[Keep")                    # refused on A
    pa, _ = _drive(pa, "create an idea called A Own")  # executes on A
    check("T18_no_foreign_owner_mutation",
          _snap(pb) == before_b,
          f"foreign state {before_b} -> {_snap(pb)}")


# --------------------------------------- T19/T20/T21 precedence
def t19_flow_shaped_claim_belongs_to_flow_door():
    # The classification case: same unknown Dell as T20, but the
    # line carries the correspondence flow operator, so the
    # DCC-IV door's D-6 refusal surface governs. The gate must
    # not claim the line at all (admit() never invoked).
    p = _fresh("GPE08GateT19")
    before = _snap(p)
    spy = _AdmitSpy()
    with _patched_admit(spy):
        p, out = _drive(p, "150[Future] >>> 70[Count]")
    check("T19_flow_claim_unknown_dell_flow_door_refusal_surface",
          spy.calls == [] and "Flow refused" in out
          and "REQUIRES_RUNTIME_SUPPORT" in out
          and GATE_REFUSAL not in out and _snap(p) == before,
          f"calls={spy.calls} state {before} -> {_snap(p)}")


def t20_plain_seed_claim_still_admission_refused():
    # The other half of the pair: a plain whole-line seed claim
    # with the same unknown Dell keeps the gate's typed admission
    # refusal — the precedence narrowing must not reopen the
    # fall-through Scope A was built to close.
    p = _fresh("GPE08GateT20")
    before = _snap(p)
    p, out = _drive(p, "150[Future]")
    check("T20_plain_claim_unknown_dell_admission_refusal_preserved",
          GATE_REFUSAL in out and "seed_parse_refusal" in out
          and NOT_EXECUTED in out and "Flow refused" not in out
          and _snap(p) == before,
          f"state {before} -> {_snap(p)}")


def t21_known_dell_flow_line_flows_normally():
    # Control (g31 T-1's line): a FlowOver chain over known Dells
    # is a valid canonical seed — it executes under the chain
    # profile exactly as before, refused by neither door.
    p = _fresh("GPE08GateT21")
    before = _snap(p)
    p, out = _drive(p, "51[Select] >>> 70[Count] >> 61[Join]")
    check("T21_known_dell_flowover_chain_executes_canonical",
          GATE_REFUSAL not in out and "Flow refused" not in out
          and "skipped by FlowOver" in out
          and _snap(p)[1] > before[1],
          f"history {before[1]} -> {_snap(p)[1]}")


def run_all():
    t1_piped_repl()
    t2_dispatch_refusal()
    t3_valid_seed_controls()
    t4_plain_english_control()
    t5_see_door_precedence()
    t6_latinmandell_control()
    t7_reissue_refusal()
    t8a_candidate_classifier_failure_fails_closed()
    t8b_noncandidate_spy()
    t9_quoted_content_control()
    t10_unquoted_content_control()
    t11_grammar_fidelity_control()
    t12_malformed_typed_arg()
    t13_malformed_multiatom_with_label()
    t14_english_embedding_bracketed_literal()
    t15_valid_args_and_labeled_chain_p10()
    t16_classifier_raise_on_candidate_no_effect()
    t17_prefix_doors_never_reach_gate()
    t18_no_foreign_owner_mutation()
    t19_flow_shaped_claim_belongs_to_flow_door()
    t20_plain_seed_claim_still_admission_refused()
    t21_known_dell_flow_line_flows_normally()
    passed = sum(1 for _, ok in CHECKS if ok)
    print(f"GP-E08 admission gate: {passed}/{len(CHECKS)} checks passed")
    if passed != len(CHECKS):
        raise AssertionError(
            "GP-E08 admission gate: failed: "
            + ", ".join(n for n, ok in CHECKS if not ok))


def smoke() -> bool:
    try:
        run_all()
        return True
    except Exception as e:
        print(f"GP-E08 ADMISSION GATE SMOKE FAILED: {e}")
        return False


if __name__ == "__main__":
    run_all()
