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
    51: ("Deep contract proven (D1 circuit 9, "
         "d1_dell51_select_test; scope semantics corrected "
         "by reconciliation R1, d1_recon1_scope_test): the "
         "universe is SCOPE-BOUND — the whole plane under "
         "scope 'plane', or the named group's membership "
         "(plane-intersected, plane order) under a group "
         "scope; a predicate filters by case-insensitive "
         "substring OR underscore-prefix (a spaced predicate "
         "matches the underscored id by prefix) and can "
         "narrow within the scope but never widen past it. "
         "Select REPLACES the selection, never appends; a "
         "no-match predicate is a successful empty selection "
         "(matched=False, count=0). Its one failure mode is "
         "a dangling scope (scope_unknown refusal, "
         "fail-closed). English select routes and executes "
         "(not blocked); the selection persists."),
    53: (
        "RECONCILIATION R1 NOTE (d1_recon1_scope_test): "
        "Scope establishes the selection boundary Dell 51 "
        "honors. Supported names are explicit: 'plane' (the "
        "default; a bare Scope restores it) or an existing "
        "Dell 82 group name. An unknown name refuses with "
        "scope_unknown:{name} and leaves the scope "
        "unchanged — a scope never silently widens to the "
        "whole plane. Ungrouping the active scope group "
        "leaves the scope dangling and Select refuses "
        "until it is reset. Scope and groups are core_ii "
        "durable state (save/load preserves the contract)."),
    54: ("Deep contract proven (D1 circuit 10, "
         "d1_dell54_query_test): READ-ONLY search of the "
         "current selection — the universe is st.selected "
         "only, never the plane (an idea placed after the "
         "Select is invisible); the selection is "
         "byte-identical after any query (contrast Dell 58, "
         "which rewrites it); matched is a Boolean (bool of "
         "the hits — standardized by reconciliation R2; the "
         "IDs live in value, the quantity in count); confidence "
         "is exactly 1.0 with hits, 0.0 without; Query never "
         "fails (empty selection and no-match are valid "
         "empty results); there is NO English surface — "
         "'query garden' becomes the Dell 9 question intent "
         "and is refused, 'find garden' goes to Dell 56; "
         "the seed line and typed invocation are the only "
         "paths."),
    56: ("Deep contract proven (D1 circuit 11, "
         "d1_dell56_get_test): a THREE-STATE read — ok "
         "(matched=True), empty (stored \"\" — matched=False, "
         "error=\"empty\"), missing (matched=False, "
         "error=\"missing\") — and the atom returns ok=True "
         "in ALL three states; the miss lives in the result "
         "cell, not the atom (contrast Dell 86, whose missing "
         "key fails the atom); bare Get falls back to the "
         "LAST INSERTED store key (\"\" on an empty store); "
         "values return by identity; Get never mutates the "
         "store; English get/find DO reach 56 with the "
         "operand preserved (R5: 'get A' reads 'A' — the "
         "circuit-3 ARGUMENT_LOSS residual that lowercased "
         "the operand on this read path is repaired end to "
         "end and the limitation record reads RESOLVED)."),
    57: ("Deep contract proven (D1 circuit 12, "
         "d1_dell57_compare_test): typed comparison over "
         "resolved operands (literals, store keys, count, "
         "selected, last_result); a lab without an operator "
         "head is rewritten to eq: of its first two tokens "
         "(further tokens dropped); type_mismatch is the "
         "ONE hard failure (the atom fails) while a missing "
         "operand is soft (atom ok, cell error='missing'); "
         "the cell carries a mode (number/string/boolean/"
         "missing/type_mismatch); a bare Compare is vacuous "
         "truth (empty == empty); Compare is the query "
         "cluster's composition reader — count reads Dell "
         "51's selection and last_result reads any previous "
         "Dell's cell, both proven live; no English surface "
         "('compare...' becomes the Dell 9 question intent)."),
    8: (
        "D1 circuit 15 DEEP NOTE: Create mints plane units "
        "through the leaf executor's place_idea with the "
        "canonical slug (lowercase, non-alnum runs to '_', "
        "40-char cap, fallback 'idea') and collision DEDUP "
        "(_1, _2, ...) — an existing unit is never "
        "overwritten; label is the name with '_' -> ' ', "
        "words is the name as passed. Typed law: name "
        "required, label/name conflicts fail with "
        "ARGUMENT_CONFLICT. SKIN (R4 corrected contract): "
        "validate() checks enum membership (skin is the "
        "registry's only enum role) against the canonical "
        "Skin enum — which has NO UNKNOWN member — and the "
        "executor wires the resolved skin into place_idea, "
        "so a typed skin lands on the unit; a non-member "
        "value refuses with INVALID_VALUE before any "
        "mutation, never a silent CUBE substitution; the "
        "untyped label path still defaults to Skin.CUBE. "
        "Creation is in-memory until Dell 10 saves; "
        "Program.load restores. In the REPL, English 'create "
        "a garden' takes the strong-idea door: the whole "
        "phrase becomes the name (id create_a_garden) with "
        "a strength report; the typed-chain Mandell line "
        "printed beside it is an echo, not the execution."),
    67: (
        "D1 circuit 14 DEEP NOTE: Any answers whether AT "
        "LEAST ONE selected id matches the shared predicate "
        "engine; value = matched = the hit, count = "
        "selection size, source 'any'. On an empty selection "
        "Any is False for every predicate; a bare predicate "
        "on a non-empty selection is True, so bare Any reads "
        "as 'is the selection non-empty'. Read-only. Dell 69 "
        "is its exact De Morgan dual (proven in the 67/69 "
        "suites). No English surface; typed form agrees."),
    68: (
        "D1 circuit 14 DEEP NOTE: All answers whether EVERY "
        "selected id matches the shared predicate engine; "
        "value = matched = the hit, count = selection size, "
        "source 'all'. On an empty selection All is True "
        "for every predicate — VACUOUS truth, the classical "
        "dual of Dell 67's empty-False; a bare predicate is "
        "True on any selection. Read-only. No English "
        "surface; typed form agrees."),
    69: (
        "D1 circuit 14 DEEP NOTE: None answers whether NO "
        "selected id matches the shared predicate engine; "
        "value = matched = the hit, count = selection size, "
        "source 'none'. None is the exact DE MORGAN dual of "
        "Dell 67: None(lab) == not Any(lab) on every state "
        "(proven across four predicates); on an empty "
        "selection None is True, and a bare predicate makes "
        "None True exactly when the selection is empty. "
        "Read-only. No English surface; typed form agrees."),
    58: ("Deep contract proven (D1 circuit 13, "
         "d1_dell58_match_test): DESTRUCTIVE narrowing of "
         "the selection by pattern (the dual of Dell 54's "
         "read-only search); chained Matches intersect; "
         "empty pattern is the identity; Match never fails; "
         "matched is a Boolean (as 54; R2 standardization); "
         "the pattern test is the SHARED predicate engine "
         "(unified by reconciliation R3): the spaced pattern "
         "'garden gate' matches [garden_gate] under Match "
         "exactly as under Select — same text, one engine, "
         "same answer; no English "
         "surface; the narrowed selection persists."),
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
