# EVIDENCE — DIR-F14: Catch consumed-error split

Scope: repair circuit DIR-F14. Tested revision: candidate
acddd37, merged 19388d2 (tree equality verified). Commands:
suite + regress legs x3 + fresh-clone regress (logs included).
Full narrative: DIRF14_PACKET.md (included). Environment:
local Linux VM, Python 3.12. Gaps: leg-3 required re-runs
after NO RESULT attempts (recorded in the packet); included
logs are the completed runs.

## Files (SHA-256, bytes)

| File | SHA-256 | Bytes |
|------|---------|-------|
| DIRF14_PACKET.md | 77a6ee34371a75439a17ec2b570d5370a99c0e4e77f47cc882e88e8ab79a4532 | 6131 |
| failing_first.log | 17783d686f24daf6fe5964853324ef35afba5fc38ece4a9ff6ad14439b232241 | 4838 |
| freshclone_regress.log | 0d37f7c7720aba77d4bcb1b699103c5731b9319a6c1d27c7f40c33a4d0de3b24 | 17259 |
| mutant_m1.log | 61eeee18e8244e8d2af3bdf2fd560c29d1778e96e93c8d91678d5f9d4fb24f9d | 2851 |
| mutant_m2.log | 60c7a7bd290490b15ca8eac8f3ab57ed215312620cbf0f345faaa9c74bca59de | 4212 |
| reg2_leg1.log | 0d37f7c7720aba77d4bcb1b699103c5731b9319a6c1d27c7f40c33a4d0de3b24 | 17259 |
| reg2_leg2.log | 1c9b2e90d8078ae273180be617e6f214066236de3bc39fcf23592ffedcc169b7 | 34504 |
| reg2_leg3.log | 96436b4be9fb1291785aa7d728c61514e32be98f9a9c19097c7df8ead39b96d7 | 14360 |
| reg2_leg3_cycle.log | 611e6821257bcf7cd754c5586ea4256f9fb1a1d889241140452aadcfcf8c0a1f | 2362 |
| reg2_leg3_rerun.log | 76a0007b82c628ccd294d1edc909c7f1027b89aecad302a014727612c3587f8c | 17259 |
| reg_leg1.log | f6c0bfed09598b0bd94dfcb21841e750b7ce435dc4b5adf2c4a0ece7945b711c | 17326 |
| suite_fixed.log | 07d21457fd9f5495161fc2404d1e29e1dc45ae221240ca3518955a25a3c94de7 | 29 |

Digests computed at publication time from the
files as copied from the originating workspaces;
the originating circuits' packets (included) are
the claim documents for these artifacts.
