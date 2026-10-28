# Mandell Limitation Knowledge Base (MPC-003 V2)
# Machine-readable verified limitations with evidence tracking.
# AUTONOMY = NO. This is knowledge, not autonomous modification authority.
#
# P12 re-verification (2026-10-27, against c6fd2fb): FLOW_PARTIAL_
# IMPLEMENTATION is RESOLVED (P10, PR #118). CONDITIONAL_SEMANTIC_LOSS
# and LEGACY_ONLY_SIGNATURE were re-probed and keep their statuses
# with refreshed evidence. ARGUMENT_LOSS and ENGLISH_UNREACHABLE_
# OPERATION were NOT re-verified — no canonical probe reproduces
# their original measurements — so their last_verified_against
# deliberately stays at the old SHA; treat those two claims as
# stale until a probe exists. Guarded by p12_closure_test.

LIMITATIONS = [
    {
        "id": "ARGUMENT_LOSS",
        "capability": "English translation",
        "limitation": "Multi-word arguments may lose case; translation lowercases",
        "evidence": "copy A → source='a' (store has 'A')",
        "cause": "translate() uses raw_lower for matching",
        "affected_path": "form/mandell/translate.py",
        "severity": "MEDIUM",
        "workaround": "Use lowercase keys or direct Mandell",
        "status": "KNOWN",
        "last_verified_against": "b4b7af1904415b0765434aaef2c134181a7e8c9f",
        "mitigation": "None yet",
        "resolution": "Preserve case in argument extraction",
    },
    {
        "id": "ENGLISH_UNREACHABLE_OPERATION",
        "capability": "English → Dell",
        "limitation": "Many Dells lack English patterns",
        "evidence": "Calculated at runtime via translate() coverage",
        "cause": "Patterns added incrementally, not systematically",
        "affected_path": "form/mandell/translate.py",
        "severity": "MEDIUM",
        "workaround": "Use direct Mandell syntax",
        "status": "IN_PROGRESS",
        "last_verified_against": "b4b7af1904415b0765434aaef2c134181a7e8c9f",
        "mitigation": "14 Dells now reachable via English",
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
