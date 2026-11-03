#!/usr/bin/env python3
"""Q6 — The legacy-compatibility surface: which currently-VALID
calls carry parenthesized / arg-shaped text that a fail-closed
gate could misclassify?

Method: parse_seed classification of the dangerous shapes
(derived from the seed.py grammar), plus execution twins where
behavior matters. A gate keyed on atom.args (the parsed dict)
can only ever see shapes where args != {} — every shape below
with args == {} is unreachable by such a gate BY CONSTRUCTION.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_lib import cleanup, fresh, snap, state_listing, verdict

from form.mandell.executor import execute_seed
from form.mandell.seed import parse_seed

results = []


def parse_case(tag, text, expect_ok, expect_args=None, expect_label=None):
    s = parse_seed(text)
    ok = (s.ok == expect_ok)
    detail = f"ok={s.ok} error={s.error!r}"
    if s.ok and expect_args is not None:
        got = s.atoms[0].args if s.atoms else None
        ok = ok and got == expect_args
        detail += f" args={got}"
    if s.ok and expect_label is not None:
        ok = ok and s.label == expect_label
        detail += f" label={s.label!r}"
    print(f"parse {text!r} -> {detail}")
    results.append(verdict(tag, ok, detail))


# Labels carrying parentheses / '=' / quotes are LABEL DATA.
parse_case("Q6-label-parens", "55[Set] :: playlist (draft) mix",
           True, expect_args={}, expect_label="playlist (draft) mix")
parse_case("Q6-label-equals", "55[Set] :: note=a=b",
           True, expect_args={}, expect_label="note=a=b")
parse_case("Q6-label-quotes", '55[Set] :: say "hi" = loud',
           True, expect_args={}, expect_label='say "hi" = loud')
# Arg-SHAPED text after :: is a label, never args.
parse_case("Q6-argshaped-label", '52[Filter] :: predicate="garden"',
           True, expect_args={}, expect_label='predicate="garden"')
# Bare parenthesized text after an atom is ALREADY a parse refusal.
parse_case("Q6-bare-parens-space", "08[Create] (garden)", False)
parse_case("Q6-bare-parens-bare", "08[Create](garden)", False)
parse_case("Q6-spaced-args", '55[Set] (key="a")', False)
# Unquoted values never parse as args.
parse_case("Q6-unquoted", "55[Set](key=5)", False)
# Values may contain '=', ',', parens, and be empty — all inside
# the quoted grammar.
parse_case("Q6-value-equals", '55[Set](key="a", value="x=y")',
           True, expect_args={"key": "a", "value": "x=y"})
parse_case("Q6-value-comma", '55[Set](key="a", value="with, comma")',
           True, expect_args={"key": "a", "value": "with, comma"})
parse_case("Q6-value-parens", '55[Set](key="a", value="f(x)")',
           True, expect_args={"key": "a", "value": "f(x)"})
parse_case("Q6-value-empty", '55[Set](key="a", value="")',
           True, expect_args={"key": "a", "value": ""})
# ManifestSet: ONE args dict is attached to EVERY member atom.
s = parse_seed('82[Group•Collect](name="g")')
print(f"manifest 82[Group•Collect](name=g) -> atoms="
      f"{[(a.dell, a.term, a.args) for a in s.atoms]}")
results.append(verdict("Q6-manifest-args-shared",
                       s.ok and len(s.atoms) == 2
                       and all(a.args == {"name": "g"} for a in s.atoms),
                       "a ManifestSet's typed args ride on every member "
                       "atom — a per-atom gate sees them per member"))


def run(tag, fn):
    before = state_listing()
    owner = "ArgHonQ6" + tag
    try:
        fn(owner)
    finally:
        removed = cleanup(owner, before)
        print(f"  (cleanup {owner}: {len(removed)} entries removed)")


def twin(owner):
    p = fresh(owner)
    execute_seed(p, "55[Set] :: a=x=y")
    legacy_store = dict(snap(p)["store"])
    p2 = fresh(owner + "B")
    execute_seed(p2, '55[Set](key="a", value="x=y")')
    typed_store = dict(snap(p2)["store"])
    print(f"twin '=' in value: legacy={legacy_store} typed={typed_store}")
    results.append(verdict("Q6-twin-equals-value",
                           legacy_store == typed_store == {"a": "x=y"},
                           "typed lowering of a value containing '=' is "
                           "lossless vs the legacy label form"))


def trailing(owner):
    p = fresh(owner)
    from probe_lib import setup_plane
    setup_plane(p)
    execute_seed(p, "51[Select]")
    r = execute_seed(p, '51[Select] >> 82[Group](name="g") :: shared')
    s = snap(p)
    print(f"trailing label: ok={r.get('ok')} groups={list(s['groups'])}")
    results.append(verdict("Q6-trailing-label-wins",
                           r.get("ok") and "shared" in s["groups"]
                           and "g" not in s["groups"],
                           "an untyped atom with BOTH typed args and a "
                           "trailing label executes on the LABEL today — "
                           "the gate proposal must classify this shape "
                           "explicitly (it is a typed call, not a legacy "
                           "call: args != {})"))


run("T1", twin)
run("T2", trailing)

print(f"\nQ6 SUMMARY: {sum(results)}/{len(results)} expectations confirmed")
sys.exit(0 if all(results) else 1)
