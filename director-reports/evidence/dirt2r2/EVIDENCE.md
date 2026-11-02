# EVIDENCE — DIR-T2-R2: plant-to-node identity in the growth lens

Scope: Director finding DIR-T2-R2 (DIR-2026-11-02-CONSOLIDATED-R1,
execution order #1) — an unplanted node supplied alone to the
growth lens inherited another plant's stage through their shared
80-char truncated key. Fix under C-Q3 (exact identity retained)
and C-Q4 (agreeing stages never prove identity).

Tested revision: fix commit ab0a897d6c3ce2637fc9089ddecbabb02d8c9f14
(branch uni/dirt2r2, base 067ca1e), merged by PR #225 as
c3cc550c3eee0033db7818266c3d4f39171b276c. The merged tree's form/
content is identical to the candidate's; the only tree delta is
PR #224's Director-response archive file.

Commands: probe = `python3 dirt2r2_probe.py` run from a repo root
(cwd = repo root); suite = `python3 -m
form.mandell.view_rooms_growth_test`; regression = `python3 -m
form.regress` (leg 2 `--twice`, leg 3 `--order rev`), sequential,
never concurrent; fresh clone = clean `git clone` at the merge
commit, probe + full regression.

Environment limits: local Linux VM, Python 3.12. The probe and
lens checks are INTEGRATION-level (direct calls into GrowthForce
and the lens); the suite additionally covers the public
Program.view_status path (production checks). Exact-head CI
(GitHub Actions: Python package run 41486068793, Form smoke run
41486068804) completed SUCCESS on ab0a897.

Gaps: none known for the listed artifacts. The partial-mutant
output is retained alongside the full defect-restoring mutant so
the contribution of the idea_full read alone is separable.

## Files (SHA-256, bytes)

| File | SHA-256 | Bytes |
|------|---------|-------|
| dirt2r2_probe.py | f05755cc57c4743a7e9be28f19314513fb77ec522c12e031725e3b6b4ae58639 | 2998 |
| probe_prefix_output.txt | cba1174abd21cd8c545541b9ae10cff267c7f2cfa29b062255ebc6755b4fa7b3 | 499 |
| probe_postfix_output.txt | 9725d62f4edb15764ab82c572415909ed80d66d19f634ade49b12a37c736f942 | 497 |
| suite_postfix_output.txt | 08f45eaa87ed07478ec012184644a2ddba2e0fe4e4498fa975d5db4a2854db8f | 1623 |
| mutant_output.txt | 44984a62b52dc808db6c3a4db5c1d2aca74601b3b4b612e45c67408cbcce11a0 | 2496 |
| mutant_partial_output.txt | 3b239f357368eccf56e09a2fa03e2547051be22faa78bca4e6d7d114164dcb42 | 2372 |
| regress_leg1.txt | 88e078ff80ce465663efbeb4bf8672f81a2dd875a8fb4ccb17d51e3632898e38 | 17496 |
| regress_leg2.txt | c89eb951de262428929e256b656eaa93eae6b4e34e47562218b7bd9d65b27c94 | 34978 |
| regress_leg3.txt | 122f9bd3ddac209ffb3590515d68d0e045612794b0c5ff28087c14c4daa81f8a | 17496 |
| regress_chain.txt | 86410dbbe24bd6768cf69500e9396d6cc94aa67e51d44e37db5dfcb10fa7a6f4 | 47 |
| freshclone_output.txt | 5a7c0cb5609a768f318aa39bb1901220bb6a63595b1ccc258ab2005c073302ce | 18021 |

Reading guide: probe_prefix_output.txt is the failing-first run
at base 067ca1e (0/5, exit 1 — B received A's stage 'branch' as
growth_force). mutant_output.txt is the full defect restoration
(pre-fix 067ca1e lens branch verbatim): probe 1/5, suite 17/26,
failures exactly the 9 R2 attribution checks.
mutant_partial_output.txt restores only the prefix-only keying
of full-identity records (lens ignores idea_full): probe 3/5,
suite 20/26. regress legs are 221/221 GREEN each with zero FAIL
lines; freshclone_output.txt is probe 5/5 + regress 221/221
GREEN at the merge commit.
