#!/usr/bin/env python3
"""00-99 unified runtime integration. Separate from unit contract suites."""
from __future__ import annotations

from form.open import open_program
from form.mandell.executor import execute_seed
from form.mandell.registry import DELLS
from form.mandell.seed import parse_seed
from form.persist import serialize, save, load
from form.mandell.query_ops import QUERY_DELLS
from form.mandell.spectrum_ops import SPECTRUM_DELLS


def smoke() -> bool:
    print("=== UNIFIED 00-99 ===")
    r = []

    def rec(name, ok, detail=""):
        print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" | {detail}" if detail and not ok else ""))
        r.append(bool(ok))

    rec("exactly_100_addresses", list(range(100)) == sorted(DELLS) and len(DELLS) == 100)
    rec("no_number_collision", len(DELLS) == len(set(DELLS)))

    missing_ii = [n for n in range(51, 100) if n not in QUERY_DELLS and n not in SPECTRUM_DELLS and n not in set(range(60, 67)) and n != 53]
    rec("no_unreachable_registered_core_ii", missing_ii == [])
    rec("no_executable_unregistered_00_99", 151 not in DELLS and all(0 <= n <= 99 for n in DELLS))

    p = open_program("A")
    execute_seed(p, "08[Create] :: alpha_unit")
    out = execute_seed(p, "51[Select] > 52[alpha_unit] > 70[Count] > 10[Keep]")
    a91 = execute_seed(p, "91[Assert] :: gte:count 1")
    rec("cross_core_a", out.get("ok") is True and "alpha_unit" in p.core_ii.selected and a91.get("ok") is True and p.core_ii.last_assert == "PASS")

    p = open_program("B")
    execute_seed(p, "27[Checkpoint]")
    execute_seed(p, "55[Set] :: k=1")
    execute_seed(p, "88[Patch] :: k=2")
    execute_seed(p, "89[Diff]")
    diff_changed = list(p.core_ii.last_diff.get("changed") or [])
    execute_seed(p, "96[Revert]")
    rec("cross_core_b", diff_changed == ["k"] and p.core_ii.store.get("k") == "1")

    p = open_program("C")
    execute_seed(p, "11[Architect]")
    execute_seed(p, "39[Schema]")
    execute_seed(p, "97[Define] :: Wave=80>90")
    execute_seed(p, "98[Alias] :: W=Wave")
    out = execute_seed(p, "99[Compose] :: W")
    execute_seed(p, "12[Test]")
    rec("cross_core_c", p.core_ii.aliases.get("W") == "Wave" and out.get("ok") is not False and any(t.startswith("80") for t in p.core_ii.traces))

    p = open_program("D")
    execute_seed(p, "35[Discover]")
    execute_seed(p, "51[Select]")
    execute_seed(p, "54[Query] :: welcome")
    execute_seed(p, "57[Compare] :: gte:count 1")
    execute_seed(p, "73[Threshold] :: gte:count 1")
    out = execute_seed(p, "60[last_result] > 09[Show]")
    rec("cross_core_d", p.core_ii.branch.get("taken") is True and 60 in (out.get("chain_ran") or []) and 9 in (out.get("chain_ran") or []))

    p = open_program("E")
    execute_seed(p, "08[Create] :: merged")
    execute_seed(p, "21[Merge]")
    execute_seed(p, "51[Select]")
    execute_seed(p, "82[Group] :: g")
    execute_seed(p, "81[Reference] :: merged")
    execute_seed(p, "84[Copy] :: merged")
    execute_seed(p, "90[Trace]")
    rec("cross_core_e", "g" in p.core_ii.groups and p.core_ii.refs.get("merged") == "merged" and "copy_merged" in p.core_ii.store)

    p = open_program("Feed")
    execute_seed(p, "08[Create] :: feed_unit")
    execute_seed(p, "51[Select] :: feed_unit")
    rec("core_i_output_feeds_core_ii", "feed_unit" in p.core_ii.selected)
    rec("flow_preserves_order_across_50_51", parse_seed("50[Manifest] > 51[Select]").ok and [a.dell for a in parse_seed("50[Manifest] > 51[Select]").atoms] == [50, 51])

    p = open_program("Err")
    out = execute_seed(p, "08[Create] >> 86[Delete] >> 09[Show]")
    rec("error_propagates_across_boundary", out.get("ok") is False and "delete_missing" in (out.get("error") or "") and 9 not in (out.get("chain_ran") or []))

    p = open_program("Ov")
    execute_seed(p, "55[Set] :: a=1")
    execute_seed(p, "18[Mirror]")
    mirror_msgs = " ".join(execute_seed(p, "18[Mirror]").get("messages") or [])
    execute_seed(p, "57[Compare] :: eq:a 1")
    cmp_mode = (p.core_ii.last_result or {}).get("mode")
    execute_seed(p, "88[Patch] :: a=2")
    execute_seed(p, "89[Diff]")
    rec("boundary_18_57_89_distinct", p.core_ii.last_diff.get("changed") == ["a"] and cmp_mode == "number" and "last_result" not in mirror_msgs)

    p = open_program("Tst")
    t12 = execute_seed(p, "12[Test]")
    execute_seed(p, "91[Assert] :: true")
    rec("boundary_12_91_distinct", p.core_ii.last_assert == "PASS" and any("Mandell:" in m for m in (t12.get("messages") or [])))

    p = open_program("Cmt")
    execute_seed(p, "20[Alpha]")
    execute_seed(p, "50[Manifest]")
    execute_seed(p, "55[Set] :: k=1")
    execute_seed(p, "93[Try]")
    execute_seed(p, "88[Patch] :: k=2")
    execute_seed(p, "95[Commit]")
    rec("boundary_20_50_95_distinct", p.core_ii.tx and p.core_ii.tx[-1]["status"] == "committed" and p.core_ii.store.get("k") == "2")

    p = open_program("Rb")
    execute_seed(p, "55[Set] :: k=1")
    execute_seed(p, "93[Try]")
    execute_seed(p, "88[Patch] :: k=2")
    execute_seed(p, "96[Revert]")
    execute_seed(p, "28[Rollback]")
    rec("boundary_28_96_distinct", p.core_ii.store.get("k") == "1" and p.core_ii.tx[-1]["status"] == "reverted")

    p = open_program("DefB")
    execute_seed(p, "11[Architect]")
    execute_seed(p, "39[Schema]")
    execute_seed(p, "97[Define] :: Q=80")
    rec("boundary_11_39_97_distinct", p.core_ii.defs.get("Q") == "80")

    p = open_program("Mac")
    execute_seed(p, "48[Macro]")
    rec("boundary_48_98_99_alias_missing_not_macro", execute_seed(p, "98[Alias] :: Z=Q").get("error") == "alias_missing")

    p = open_program("Sc")
    execute_seed(p, "36[Inject]")
    execute_seed(p, "53[Scope] :: frame")
    rec("boundary_36_53_distinct", p.core_ii.scope == "frame")

    p = open_program("Mv")
    execute_seed(p, "19[Drive]")
    execute_seed(p, "55[Set] :: src=1")
    execute_seed(p, "85[Move] :: src>dst")
    rec("boundary_19_85_distinct", "src" not in p.core_ii.store and p.core_ii.store.get("dst") == "1")

    p = open_program("Cnt")
    execute_seed(p, "40[TokenCount]")
    execute_seed(p, "51[Select]")
    execute_seed(p, "70[Count]")
    rec("boundary_40_70_distinct", (p.core_ii.last_result or {}).get("source") == "count")

    rec("parser_ignores_core_boundary", parse_seed("50[Manifest] > 51[Select] > 52[Filter]").ok)
    rec("flow_around_49_50_51_52", [a.dell for a in parse_seed("49[Profile] > 50[Manifest] > 51[Select] > 52[Filter]").atoms] == [49, 50, 51, 52])
    s = parse_seed("08[Create•Keep]")
    rec("manifestset_core_i_only", s.ok and [a.dell for a in s.atoms] == [8, 8] and [a.term for a in s.atoms] == ["Create", "Keep"])
    s = parse_seed("51[Select•Filter]")
    rec("manifestset_core_ii_only", s.ok and [a.dell for a in s.atoms] == [51, 51] and [a.term for a in s.atoms] == ["Select", "Filter"])
    s = parse_seed("08[Create] > 51[Select]")
    rec("manifestset_cross_core_chain", s.ok and [a.dell for a in s.atoms] == [8, 51])
    s = parse_seed("08[Create•Map] > 51[Select•Filter]")
    rec("chainlink_cross_core", s.ok and 8 in {a.dell for a in s.atoms} and 51 in {a.dell for a in s.atoms})
    s = parse_seed("08[Select]")
    rec("unknown_word_does_not_change_number", s.ok and s.atoms[0].dell == 8)

    p = open_program("Pers")
    execute_seed(p, "08[Create] :: persist_unit")
    execute_seed(p, "55[Set] :: k=7")
    execute_seed(p, "82[Group] :: g")
    execute_seed(p, "70[Count]")
    path = "/tmp/dm/unified_rt.json"
    save(p, path)
    q = load("Pers", path)
    rec("cross_core_save_load", "persist_unit" in list(q.cube.session.plane.units) and q.core_ii.store.get("k") == "7" and "g" in q.core_ii.groups)
    rec("transient_not_loaded", "last_result" not in (serialize(q).get("core_ii") or {}))
    rec("load_reestablishes_runtime", execute_seed(q, "56[Get] :: k").get("ok") is not False and (q.core_ii.last_result or {}).get("value") == "7")
    save(q, path)
    q2 = load("Pers", path)
    rec("save_load_save_stable", q2.core_ii.store.get("k") == "7")

    p = open_program("F1")
    out = execute_seed(p, "99[Compose] :: Bad=not_a_dell >> 08[Create]")
    rec("core_ii_failure_blocks_later_core_i", out.get("ok") is False and 8 not in (out.get("chain_ran") or []))
    p = open_program("F2")
    execute_seed(p, "08[Create] :: z")
    out = execute_seed(p, "86[Delete] :: missing >> 09[Show]")
    rec("core_ii_failure_after_core_i_traceable", "delete_missing" in (out.get("error") or "") and 9 not in (out.get("chain_ran") or []))
    p = open_program("F3")
    execute_seed(p, "55[Set] :: k=1")
    execute_seed(p, "93[Try]")
    execute_seed(p, "88[Patch] :: k=bad")
    execute_seed(p, "91[false]")
    execute_seed(p, "96[Revert]")
    rec("tx_governs_cross_core_compatible_store", p.core_ii.store.get("k") == "1")
    p = open_program("F4")
    out = execute_seed(p, "99[Compose] :: Mix=08>not_a_dell")
    rec("compose_mixed_failure_no_exception", out.get("error") == "malformed_composition" and out.get("ok") is False)
    p = open_program("F5")
    out = execute_seed(p, "60[true] > 08[Create] > 61[Join]")
    rec("nested_control_cross_core", out.get("ok") is not False and 8 in (out.get("chain_ran") or [8]))

    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
