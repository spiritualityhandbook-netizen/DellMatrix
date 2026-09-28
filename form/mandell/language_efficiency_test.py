#!/usr/bin/env python3
"""ManifestSet / Chain / Chainlink / FlowSet tests. Offline."""
from __future__ import annotations

from .seed import (
    BULLET,
    CHAIN_DVS,
    CHAINLINK_DVS,
    compression_report,
    define_cell,
    expand_cell,
    parse_seed,
)


def smoke() -> bool:
    print("=== LANGUAGE EFFICIENCY ===")
    r = []

    def rec(name, ok, detail=""):
        print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" | {detail}" if detail and not ok else ""))
        r.append(bool(ok))

    rec("dvs_chain_grammar", CHAIN_DVS["decision"] == "GRAMMAR_OPERATOR" and CHAIN_DVS["number"] is None)
    rec("dvs_chainlink_grammar", CHAINLINK_DVS["decision"] == "GRAMMAR_OPERATOR" and CHAINLINK_DVS["number"] is None)

    s = parse_seed("08[Create]")
    rec("single_manifest_unchanged", s.ok and [a.dell for a in s.atoms] == [8] and s.atoms[0].term == "Create")

    s = parse_seed(f"08[Create{BULLET}Map{BULLET}Keep]")
    rec("manifest_set_multiple", s.ok and [a.term for a in s.atoms] == ["Create", "Map", "Keep"])
    rec("chain_same_dell", s.ok and [a.dell for a in s.atoms] == [8, 8, 8])
    rec("chain_order", s.ok and [a.term for a in s.atoms] == ["Create", "Map", "Keep"])
    rec("chain_origin", s.ok and all(a.origin == "chain" for a in s.atoms))

    rec("bullet_not_comma", not parse_seed("08[Create,Map]").ok)
    rec("bullet_not_underscore_as_set", parse_seed("08[Create_Map]").ok and parse_seed("08[Create_Map]").atoms[0].term == "Create_Map")

    s = parse_seed(f"08[Create{BULLET}Map] > 12[Test{BULLET}Keep]")
    rec("chainlink_pair", s.ok and [a.dell for a in s.atoms] == [8, 12, 8, 12])
    rec("chainlink_terms", s.ok and [a.term for a in s.atoms] == ["Create", "Test", "Map", "Keep"])
    rec("chainlink_origin", s.ok and all(a.origin == "chainlink" for a in s.atoms))

    bad = parse_seed(f"08[Create{BULLET}Map] > 12[Test{BULLET}Keep{BULLET}Loop]")
    rec("cardinality_mismatch", (not bad.ok) and "cardinality" in bad.error)

    rec("empty_member", not parse_seed(f"08[Create{BULLET}{BULLET}Map]").ok)
    rec("empty_brackets", not parse_seed("08[]").ok)
    rec("aggregate_nested", not parse_seed("08[Create[Map]]").ok)
    rec("invalid_unicode_mid", not parse_seed("08[Create\u00b7Map]").ok)

    rec("1digit", parse_seed("5[Tone]").ok and parse_seed("5[Tone]").atoms[0].dell == 5)
    rec("2digit", parse_seed("08[Create]").ok)
    rec("3digit", parse_seed("151[Harmonic]").ok and parse_seed("151[Harmonic]").atoms[0].dell == 151)
    rec("unknown_200", not parse_seed("200[Nope]").ok)

    rec("flow_gt", parse_seed("08[Create] > 12[Test]").ok and parse_seed("08[Create] > 12[Test]").flows == [">"])
    rec("flow_gtgt", parse_seed("08[Create] >> 12[Test]").ok and parse_seed("08[Create] >> 12[Test]").flows == [">>"])
    rec("flow_gtgtgt", parse_seed("08[Create] >>> 12[Test]").ok and parse_seed("08[Create] >>> 12[Test]").flows == [">>>"])
    rec("flow_colon", parse_seed("08[Create] : 12[Test]").ok and parse_seed("08[Create] : 12[Test]").flows == [":"])
    rec("flow_colon_gt", parse_seed("08[Create] :> 12[Test]").ok and parse_seed("08[Create] :> 12[Test]").flows == [":>"])
    rec("flow_lt_colon", parse_seed("08[Create] <: 12[Test]").ok and parse_seed("08[Create] <: 12[Test]").flows == ["<:"])
    rec("flow_diamond", parse_seed("08[Create] <:> 12[Test]").ok and parse_seed("08[Create] <:> 12[Test]").flows == ["<:>"])
    rec("flow_delta", parse_seed("08[Create] <<[Delta] 12[Test]").ok and parse_seed("08[Create] <<[Delta] 12[Test]").flows == ["<<[Delta]"])

    rec("longest_match_triple", parse_seed("08[Create] >>> 12[Test]").flows == [">>>"])
    rec("legacy_label", parse_seed("08[Create] > 15[Map] :: name").ok and parse_seed("08[Create] > 15[Map] :: name").label == "name")
    rec("legacy_core_ii", parse_seed("51[Select] > 52[Filter] > 66[ForEach] :: nursery").ok)

    verbose = "08[Create] > 08[Map] > 08[Keep]"
    compressed = f"08[Create{BULLET}Map{BULLET}Keep]"
    rep = compression_report(verbose, compressed)
    rec("roundtrip_equiv", rep["equivalent"] is True)
    rec("positive_compression", rep["positive"] is True and rep["compression_percent"] > 0, str(rep))

    cell = define_cell("Complete", "35[Discover] > 18[Mirror] > 12[Test]")
    rec("mandellacell_define", cell.ok)
    rec("mandellacell_expand", [a.dell for a in expand_cell("Complete").atoms] == [35, 18, 12])

    print(f"=== {sum(r)}/{len(r)} ===")
    print(f"compression={rep['compression_percent']}% {rep['verbose_chars']}->{rep['compressed_chars']}")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
