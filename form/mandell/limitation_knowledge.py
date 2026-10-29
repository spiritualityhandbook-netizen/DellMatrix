# Mandell Limitation Knowledge Base (MPC-003 V2)
# Machine-readable verified limitations with evidence tracking.
# AUTONOMY = NO. This is knowledge, not autonomous modification authority.
#
# P12 re-verification (2026-10-27, against c6fd2fb): FLOW_PARTIAL_
# IMPLEMENTATION is RESOLVED (P10, PR #118). CONDITIONAL_SEMANTIC_LOSS
# and LEGACY_ONLY_SIGNATURE were re-probed and keep their statuses
# with refreshed evidence.
#
# D1 re-verification (2026-10-28, against eb3389c): ARGUMENT_LOSS
# and ENGLISH_UNREACHABLE_OPERATION now have a canonical probe —
# form/mandell/d1_stale_probes_test.py reproduces both
# measurements at exact current source and pins them; their
# last_verified_against names the probe base. If translate.py
# changes, the probe fails loudly: that failure is the
# re-verification trigger. Guarded by p12_closure_test.

LIMITATIONS = [
    {
        "id": "ARGUMENT_LOSS",
        "capability": "English translation",
        "limitation": "Multi-word arguments may lose case; translation lowercases",
        "evidence": "D1 probe (d1_stale_probes_test) at eb3389c: copy A → source='a'; copy My Field Notes → 'my field notes'; find-idea/trace labels lowercased; place path id/label lowercased. Loss is site-specific: the nurture path (add idea Test) preserves case.",
        "cause": "translate() captures arguments from raw_lower at the losing sites instead of the raw text",
        "affected_path": "form/mandell/translate.py",
        "severity": "MEDIUM",
        "workaround": "Use lowercase keys or direct Mandell",
        "status": "KNOWN",
        "last_verified_against": "eb3389c122f301006b10fa770173ea08c2066d7d",
        "mitigation": "None yet at the losing sites; the nurture path already captures case-preserved",
        "resolution": "Preserve case in argument extraction",
    },
    {
        "id": "ENGLISH_UNREACHABLE_OPERATION",
        "capability": "English → Dell",
        "limitation": "Many Dells lack English patterns",
        "evidence": "D1 probe (d1_stale_probes_test) at eb3389c: static Intent scan of translate() names 29 Dells; 71 of 100 have no Intent path in translate(); dynamic sample (84/86/87/35/9/37) routes as statically read. A separate action tier (save/checkpoint/grow/ledger) returns dell=None for the intent router — operational closure is a distinct dimension from named-Dell reachability.",
        "cause": "Patterns added incrementally, not systematically",
        "affected_path": "form/mandell/translate.py",
        "severity": "MEDIUM",
        "workaround": "Use direct Mandell syntax",
        "status": "IN_PROGRESS",
        "last_verified_against": "eb3389c122f301006b10fa770173ea08c2066d7d",
        "mitigation": "29 Dells reachable by name via translate() (probe-measured at eb3389c; supersedes the earlier '14' figure, which counted typed signatures — a different evidence dimension)",
        "resolution": "Systematic English coverage",
    },
    {
        "id": "CONDITIONAL_SEMANTIC_LOSS",
        "capability": "Safe translation",
        "limitation": "Conditionals on destructive ops → UNKNOWN (safe)",
        "evidence": "'delete X if empty' → UNKNOWN (was: unconditional delete); re-probed P12 2026-10-27: 'delete the plan if empty' → action=unknown, no Dell routed",
        "cause": "No conditional execution semantics in Mandell",
        "affected_path": "form/mandell/translate.py:SEMANTIC_LOSS_GUARD",
        "severity": "HIGH",
        "workaround": "None; UNKNOWN is correct until conditionals exist",
        "status": "MITIGATED",
        "last_verified_against": "c6fd2fb2d2195b4c44149ff883a5c492c8be0847",
        "mitigation": "Guard blocks destructive+conditional",
        "resolution": "Implement conditional execution via Branch (60)",
    },
    {
        "id": "LEGACY_ONLY_SIGNATURE",
        "capability": "Typed operations",
        "limitation": "43 Dells lack typed signatures",
        "evidence": "14 Dells have typed signatures (P12 probe 2026-10-27: get_signature over Dells 00-99 returns 14; count unchanged from the 14 recorded earlier)",
        "cause": "Signatures added incrementally via Ω-055/MPC-002/MPC-003",
        "affected_path": "form/mandell/signatures.py",
        "severity": "MEDIUM",
        "workaround": "Use legacy lab syntax",
        "status": "IN_PROGRESS",
        "last_verified_against": "c6fd2fb2d2195b4c44149ff883a5c492c8be0847",
        "mitigation": "Retrieval + query families typed",
        "resolution": "Continue systematic typing",
    },
    {
        "id": "FLOW_PARTIAL_IMPLEMENTATION",
        "capability": "Flow composition",
        "limitation": "Only 3/9 Flow operators operationally implemented",
        "evidence": "RESOLVED by master-plan P10 (PR #118): all nine operators execute with the canonical chain_exec semantics at the public REPL path; p10_flow_grammar_test 12/12 proves parse set == contract set == publicly executable set",
        "cause": "Flow contract defined aspirationally; the REPL's DCC-IV branch shadowed raw seed lines with a two-operator executor",
        "affected_path": "form/mandell/control_runtime.py:FLOW_CONTRACT",
        "severity": "MEDIUM",
        "workaround": "Use > for sequencing, :/:: for args",
        "status": "RESOLVED",
        "last_verified_against": "c6fd2fb2d2195b4c44149ff883a5c492c8be0847",
        "mitigation": "Document which flows work",
        "resolution": "Implement or remove unimplemented flows — implemented (P10)",
    },
]
