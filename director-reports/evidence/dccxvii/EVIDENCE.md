# EVIDENCE MANIFEST — DCC-XVII sigkill flake investigation

Scope: dcc_xvii_test U.sigkill_mid_write nondeterministic failure
(main CI run 41493670559, 80/81, reverse-order leg) — investigation,
mechanism, repair (PR #229, merged 2d92c98), and the same-day
correction of two retracted evidence claims.
Tested revision: fix candidate d3dc6da; merge 2d92c98.
Environment limits: local runs are Uni-side executions; the CI event
is GitHub Actions. Retracted claims are LABELED in DCCXVII_PACKET.md
(leading CORRECTION section) and correction_evidence_note.md; the
original contaminated run log (plain_run_030.log) is preserved
unmodified as evidence of the correction itself.

| file | bytes | sha256 |
|------|-------|--------|
| DCCXVII_PACKET.md | 8545 | 96aa47878621d1a8390bc05cdb09371778b321e538273e9c9c1f7b1b0a4cfaf0 |
| ci_run_log_failed.txt | 131457 | 12a794d4093c653da20da7aefdf3a83a390a8e493654c975138ed1d3eccecba6 |
| correction_evidence_note.md | 2906 | 6f12e065f1502cc8abd3a88224fcc87f6b1bef5687a7cb15d74f349c66f52d8f |
| freshclone_regress.log | 17496 | 88e078ff80ce465663efbeb4bf8672f81a2dd875a8fb4ccb17d51e3632898e38 |
| mutant_a_revert.log | 8057 | eb3a3a23be1c22a0310426e22a1a64017bf340f6617f5956690e756647eb706e |
| mutant_b.log | 436 | 3041478286566f770555448e681f8adb625e9f0093f0c5e67dd03273fbe3496f |
| mutant_b2.log | 757 | e961ad5560a61b03da1b61fbbaf633ee6ec89c4518ad7c2cbe8ef070e38407c1 |
| plain_run_030.log | 3735 | 8bf3f7ca001add990bb14b057a20958470625077c0906d76c095d72a8a6e6213 |
| regress_chain.log | 228 | 4dd2aea99ac454956763738eb7c7394cec2718c0d6377ac936674b0a708a674d |
| regress_leg1_fwd.log | 17496 | 88e078ff80ce465663efbeb4bf8672f81a2dd875a8fb4ccb17d51e3632898e38 |
| regress_leg2_twice.log | 34978 | c89eb951de262428929e256b656eaa93eae6b4e34e47562218b7bd9d65b27c94 |
| regress_leg3_rev.log | 17496 | 122f9bd3ddac209ffb3590515d68d0e045612794b0c5ff28087c14c4daa81f8a |
| sigkill_timing.log | 4326 | d9dd1b9b18d400dd3d481d7456538a2a85fe62a24b7bd91eeb9f47631be7333c |
| sigkill_timing_probe.py | 2936 | 6813822a6288a33b432164fa3493be7f21f10270398f90a98ff090a76b4d00a9 |
| u_probe.py | 920 | 57fbef7979960e258c9b9c7a9d17f22f78705230d664545e3c16d63fd1f59491 |
| u_probe_census.log | 19327 | a60fe716b4c49ccb001c0400bc9b68ae5bff9e24ef516bf335abc6b2e4748744 |
| u_probe_fixed.log | 19327 | a60fe716b4c49ccb001c0400bc9b68ae5bff9e24ef516bf335abc6b2e4748744 |
| u_probe_plain.log | 757 | 034641493086aec7c2bda75f2e69c56e9b3987a3dbbc7aaa5d6834075dcb28f7 |

A manifest claim is not a substitute for verifying file bytes
(C-Q2 standing condition) — the digests above are the verification
instrument.
