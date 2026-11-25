# EVIDENCE — DIR-F15: Diff absent-vs-None comparator

Scope: repair circuit DIR-F15. Tested revision: candidate
981d524, merged 8eb76e5 (tree equality verified). Commands:
suite + regress legs x3 + fresh-clone regress (logs included).
Full narrative: DIRF15_PACKET.md (included). Environment:
local Linux VM, Python 3.12. Gaps: none known for the listed
artifacts.

## Files (SHA-256, bytes)

| File | SHA-256 | Bytes |
|------|---------|-------|
| DIRF15_PACKET.md | 001fad5531e4a9b22662372f558301243ab60ab40af25755ab04584466967a4a | 7589 |
| failing_first.log | 94548dbcd9e77ed9e683fb4159e811b1183135b54cdfc7c086d63c766ae9e835 | 818 |
| freshclone_regress.log | fe954cdcba959ca85b91bd097e2008bfefbb1599d8837d957594931d6721e5cd | 17259 |
| mutant.log | 94548dbcd9e77ed9e683fb4159e811b1183135b54cdfc7c086d63c766ae9e835 | 818 |
| reg_leg1_fwd.log | fe954cdcba959ca85b91bd097e2008bfefbb1599d8837d957594931d6721e5cd | 17259 |
| reg_leg2_twice.log | 56d7c2ceffa6847e965116b0356342c21ec5e2f7586c3ef782bc772cc28e700d | 34504 |
| reg_leg3_rev.log | d154062b8eb834898183c98f5bacd51afed9924cd6b3bcb49c480595e6680c21 | 17259 |
| suite_fixed.log | 289f93bed72e5afeec619a769b1b6e08da31f5deb5070ba82ee6066d379e81bb | 18 |

Digests computed at publication time from the
files as copied from the originating workspaces;
the originating circuits' packets (included) are
the claim documents for these artifacts.
