#!/usr/bin/env python3
"""D1 proof cards — a survey of every Dell in the registry.

One card per registry entry (the Director's D1 denominator:
100 entries), each card carrying only MEASURED dimensions:

- identity: number, name, manor, namespace (from the
  registry itself);
- typed signature: present (with roles, output and failures
  from signatures.get_signature) or absent — signature
  presence is its own dimension, never merged with the
  others;
- English reachability: whether translate() names this Dell
  in any Intent it can return (the circuit-1 static scan) —
  English-pattern presence, again its own dimension;
- bare invocation: the OBSERVED outcome of executing the
  Dell's bare seed (NN[Name], no operands) through the
  canonical public executor on an empty field — executed, or
  failed with the executor's own reason. This is
  operational evidence for the bare case only; a failure
  here usually names the missing operand or precondition,
  which is precisely what the card records.

Cards are regenerated from live probes; the committed
DELL_PROOF_CARDS.md is the renderer's output, and the D1
suite fails if the document drifts from a fresh survey.
"""
from __future__ import annotations

import ast
import glob
import os
import shutil
from typing import Any, Dict, List

from .registry import DELLS, get_dell
from .signatures import get_signature


# Deep-contract notes from D1 deepening circuits: one entry per
# Dell whose full contract (arguments, outputs, failures, state,
# persistence, English path) has been derived and proven beyond
# this survey. Keyed by Dell number; text is evidence, kept short.
DEEP_NOTES: Dict[int, str] = {
    84: ("Deep contract proven (D1 circuit 4, "
         "d1_dell84_copy_test): store[copy_<src>] = deepcopy of "
         "the source; the destination is derived, never a caller "
         "argument; a missing source copies the name string "
         "itself; fallback order lab -> selected[0] -> \"object\"; "
         "publishes last_result; copies persist across save/load; "
         "English \"copy A\" routes its typed source through the "
         "generalized route (router arg-loss defect found and "
         "fixed in the same circuit)."),
    85: ("Deep contract proven (D1 circuit 5, "
         "d1_dell85_move_test): store[dest] = store.pop(src) — "
         "the same object relocates (identity, not a copy); lab "
         "is src>dest, partition on the first \">\"; an existing "
         "destination is overwritten; dest == src is a named "
         "no-op success (\"Move same identity\", fresh matched "
         "result cell); failures malformed_move / move_missing "
         "publish failure cells; NOT in the English blocked set "
         "(86/87/88 are) — the English route executes \"move A "
         "to B\" with its operands and the moved state persists; "
         "at the REPL surface, however, the word \"move\" is "
         "captured by avatar navigation, so the REPL user path "
         "for 85 is the Mandell seed line."),
    86: ("Deep contract proven (D1 circuit 6, "
         "d1_dell86_delete_test): key = the whole lab; store "
         "wins over groups for a shared name (two deletes peel "
         "store, then group); NO_AUTHORITATIVE_RESULT — even a "
         "successful delete publishes an explicit non-matched "
         "result cell, distinct from the failure cell that "
         "carries delete_missing:{key} (empty key: "
         "delete_missing:empty — signature failures text synced "
         "to this truth in the same circuit); English delete is "
         "blocked_with_reason (operand-confirmation policy) at "
         "the route and at the REPL, and negated English never "
         "becomes a delete intent; deletions persist."),
    87: ("Deep contract proven (D1 circuit 7, "
         "d1_dell87_replace_test): identity rename old>new; an "
         "occupied destination REFUSES (replace_occupied:{new}, "
         "zero mutation — the MPC-012 §0 / MPC-011 J-decision in "
         "the executor's comment; the deliberate contrast with "
         "Dell 85 Move, which overwrites); replace_missing:{old} "
         "for an absent source (bare form: replace_missing:); "
         "empty new and new == old are no-op successes; "
         "signature failures text + derived_from range synced "
         "to the code in the same circuit (the refusal was "
         "missing from the signature); English replace is "
         "blocked_with_reason; renames persist."),
    88: ("Deep contract proven (D1 circuit 8, "
         "d1_dell88_patch_test): UPDATE-ONLY targeted write — "
         "an absent key fails patch_miss:{key} and is never "
         "created (the contrast with Dell 55 Set, which "
         "creates); first '=' splits, the value keeps further "
         "'=' characters and is stored RAW (key stripped, "
         "value not); an empty value is legal ('' stored, key "
         "survives); patching replaces the value's type "
         "wholesale (a list cell becomes the raw string); "
         "signature derived_from synced to the real arm "
         "(208-227) and its output now states the update-only "
         "law; English patch is blocked_with_reason; patches "
         "persist. This closes the store-mutation cluster "
         "84-88."),
}


def english_named_dells() -> set:
    """Dells translate() can name in an Intent (static scan of
    Intent returns — the circuit-1 measurement)."""
    path = os.path.join(os.path.dirname(__file__), "translate.py")
    tree = ast.parse(open(path, encoding="utf-8").read())
    dells = set()
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call)
                and getattr(node.func, "id", "") == "Intent"
                and len(node.args) >= 2
                and isinstance(node.args[1], ast.Constant)
                and isinstance(node.args[1].value, int)):
            dells.add(node.args[1].value)
    return dells


def _cleanup(owner: str, state_dir: str) -> None:
    for pat in (f"program_{owner}.json", f"nursery_{owner}.json",
                f"checkpoint_{owner}_*", f"confirm_{owner}.journal.json",
                f"checkpoint_{owner}.journal.json", f"gen_{owner}_*",
                f"current_{owner}.json"):
        for f in glob.glob(os.path.join(state_dir, pat)):
            try:
                os.remove(f)
            except FileNotFoundError:
                pass
            except OSError:
                raise
    for d in glob.glob(os.path.join(state_dir, f"ideas_{owner}*")):
        if os.path.isdir(d):
            shutil.rmtree(d)


def build_card(n: int, owner: str, state_dir: str,
               named: set) -> Dict[str, Any]:
    """Probe one Dell. The caller owns cleanup of `owner`."""
    from form.open import Program
    from .executor import execute_seed

    entry = get_dell(n)  # registry view: adds dell + namespace
    sig = get_signature(n)
    card: Dict[str, Any] = {
        "dell": n,
        "name": entry["name"],
        "manor": entry["manor"],
        "namespace": entry["namespace"],
        "typed_signature": None,
        "english_named": n in named,
        "bare": {"outcome": "error", "error": "not probed"},
        "deep_note": DEEP_NOTES.get(n, ""),
    }
    if sig is not None:
        card["typed_signature"] = {
            "roles": [
                {"name": r.name, "type": r.type,
                 "required": bool(r.required)}
                for r in (sig.roles or [])
            ],
            "output": sig.output,
            "failures": sig.failures,
            "derived_from": sig.derived_from,
        }
    p = Program(owner)
    r = execute_seed(p, f"{n:02d}[{entry['name']}]")
    if r.get("ok"):
        card["bare"] = {"outcome": "executed", "error": ""}
    else:
        ars = r.get("atom_results") or []
        reason = ""
        if ars:
            reason = str(ars[0].get("reason")
                         or ars[0].get("error") or "")
        card["bare"] = {
            "outcome": "failed",
            "error": reason or str(r.get("error") or ""),
        }
    return card


def build_all_cards(owner_prefix: str = "D1Card",
                    state_dir: str = None) -> List[Dict[str, Any]]:
    if state_dir is None:
        state_dir = os.path.join(os.path.dirname(__file__), "..",
                                 "state")
    named = english_named_dells()
    cards = []
    for n in sorted(DELLS):
        owner = f"{owner_prefix}{n}"
        _cleanup(owner, state_dir)
        try:
            cards.append(build_card(n, owner, state_dir, named))
        finally:
            _cleanup(owner, state_dir)
    return cards


def render_cards_md(cards: List[Dict[str, Any]]) -> str:
    executed = [c for c in cards if c["bare"]["outcome"] == "executed"]
    failed = [c for c in cards if c["bare"]["outcome"] != "executed"]
    typed = [c for c in cards if c["typed_signature"] is not None]
    named = [c for c in cards if c["english_named"]]
    lines = [
        "# Dell Proof Cards (D1 survey)",
        "",
        "Generated by form/mandell/dell_cards.py from live probes; "
        "the D1 suite fails if this document drifts from a fresh "
        "survey. Dimensions are kept separate by design: a typed "
        "signature is not English reachability, and neither is a "
        "bare-invocation outcome.",
        "",
        f"- Registry entries: {len(cards)}",
        f"- Typed signatures: {len(typed)}",
        f"- Named by translate() English patterns: {len(named)}",
        f"- Bare invocation executed (empty field): {len(executed)}",
        f"- Bare invocation failed with a named reason: {len(failed)}",
        "",
        "| Dell | Name | Typed | English-named | Bare outcome |",
        "|------|------|-------|---------------|--------------|",
    ]
    for c in cards:
        bare = ("executed" if c["bare"]["outcome"] == "executed"
                else f"failed: {c['bare']['error']}")
        lines.append(
            f"| {c['dell']:02d} | {c['name']} | "
            f"{'yes' if c['typed_signature'] else 'no'} | "
            f"{'yes' if c['english_named'] else 'no'} | {bare} |")
    lines += ["", "## Typed signatures (roles / output / failures)", ""]
    for c in typed:
        sig = c["typed_signature"]
        roles = ", ".join(
            f"{r['name']}:{r['type']}"
            f"{' (required)' if r['required'] else ''}"
            for r in sig["roles"]) or "none"
        lines += [
            f"### {c['dell']:02d}[{c['name']}] — {c['manor']}",
            f"- roles: {roles}",
            f"- output: {sig['output']}",
            f"- failures: {sig['failures']}",
            f"- derived_from: {sig['derived_from']}",
            "",
        ]
    noted = [c for c in cards if c.get("deep_note")]
    if noted:
        lines += ["## Deep-contract notes (D1 deepening circuits)", ""]
        for c in noted:
            lines += [f"### {c['dell']:02d}[{c['name']}]",
                      f"- {c['deep_note']}", ""]
    return "\n".join(lines) + "\n"
