# EVIDENCE — DAF-09 investigations (timeout tree / identity / pidfd)

Scope: the DAF-09 evidence family — timeout-tree suite
development, identity hardening, pidfd hardening, the ESRCH-at
-open repair, the instrumented cross-environment investigation
(Course 1), and the Q2 post-check (NBD-4). Packets for each
sub-investigation are included verbatim.
Tested revisions: per packet (anchors named inside each).
Commands: python3 -m form.daf09_timeout_tree_test (suite);
daf09instr_driver.py (instrumented runs; pre-injects an
instrumented regress module via sys.modules, suite bytes
untouched); regress legs per the esrch_/pidfd_ log prefixes.
Environment limits: Linux VM, /proc + pidfd available;
saturation runs used 6 CPU hogs on 4 CPUs. The Director's
environment is NOT this VM: the cross-environment discrepancy
(session-escape) remains UNRESOLVED and this bundle does not
claim otherwise — it makes the local record fully inspectable.
Gaps: some early regress-chain logs were lost to VM
replacements during the original circuits and re-run in full;
the logs present here are the surviving complete runs the
packets cite.

## Files (SHA-256, bytes)

| File | SHA-256 | Bytes |
|------|---------|-------|
| DAF09_ADDENDUM_PACKET.md | 42e8bbbed41a7b6928eb30205ea4d264f3320672b55f91d37a3a3ee2274d84b5 | 6759 |
| DAF09_ESRCH_PACKET.md | f2550e2835dd966498a1b5341f53e2c177f578baf9fa0b06fb13528c43cdcb87 | 4196 |
| DAF09_IDENTITY_PACKET.md | abb39057f17d2b3a4be66fc89288bc3ca5f1d5cd4624bb053600de3ec582a6e4 | 6649 |
| DAF09_INSTRUMENTED_INVESTIGATION_PACKET.md | feae8ba4ff17ad60fab918fa820e6e5ad8ef0a466e50ad141aa588b8c5246139 | 8266 |
| DAF09_PIDFD_HARDENING_PACKET.md | 71a5fe6acfc9a3555490f2899c470d04ada5025bceb2dae42556d467a7a0f17e | 9165 |
| DAF09_POSTCHECK_PACKET.md | a016ae0e2a9fa5983f4625cb8ad2077bea208cb01f554556acad2a2524e7117c | 4417 |
| DAF09_TIMEOUT_TREE_PACKET.md | fc85d6e899bd2c14641183a93560efc2db4c9ef3e3f039401688f285b6800c51 | 5003 |
| daf09_mapping_reverify_2026-11-01.md | c2304be6c7955eb7838def042a7ad60c9c1f3883cb199ff2bdfc47d689bb3c8f | 18270 |
| daf09_pidfd_hardening_ground.md | a47dae7e122266b8e6bbac1e6be2f6e37f00771b0f5d686e90dc86bc6e956fe1 | 3882 |
| daf09_pidfd_probe.py | 325aa410905a1dcb64fd3dbe601607cdbdce064c2e2e1a3b4109cdacf428a11b | 2230 |
| daf09esrch_ground.md | da07895cda7ebe4acc82592920009b36f1e91d2d18072a2bff85e61905cf4807 | 4408 |
| daf09esrch_probe.py | bb5344320a7ff07ce1751a15136905fceb58fb355cfc17a16eeab4609227ca9a | 1336 |
| daf09id_probe_barepid.py | a801bb1f652c1a29a4f02694627f2cf279e2184e650d8651f57c359d791fb583 | 1207 |
| daf09instr_driver.py | cb25f8f57a3a1a24da787aed92056fb2185ff7899564013e3602a5ab7e319b32 | 14332 |
| daf09post_ground.md | 2b4ddcb7b64a02c7a2bc5139b995bc3291196ff4212f137a56f91290cb58e2b2 | 3481 |
| esrch_freshclone_regress.log | d7d1c351af64f2d4590c2365f94d947882a88850d2e0e732e9227dcf184e8a47 | 17417 |
| esrch_regress_leg1.log | d7d1c351af64f2d4590c2365f94d947882a88850d2e0e732e9227dcf184e8a47 | 17417 |
| esrch_regress_leg2.log | d7d1c351af64f2d4590c2365f94d947882a88850d2e0e732e9227dcf184e8a47 | 17417 |
| esrch_regress_leg3.log | d7d1c351af64f2d4590c2365f94d947882a88850d2e0e732e9227dcf184e8a47 | 17417 |
| instr_baseline_uninstrumented.log | 4ae87123a4493f4d51aa0b8033bc0f8acc85e925acd7ded04383a48a01c6cc60 | 26 |
| instr_run1_idle.jsonl | ddca18893594d369ad10158c88a8ed623542a839230a730da5099ce09bec0be0 | 32145 |
| instr_run1_idle.stdout.log | 4ae87123a4493f4d51aa0b8033bc0f8acc85e925acd7ded04383a48a01c6cc60 | 26 |
| instr_run2_idle.jsonl | 368c7f70d0ac3f3707bcc865dfc10498776a9ea6ed38436e30b296e624a19551 | 32565 |
| instr_run2_idle.stdout.log | 4ae87123a4493f4d51aa0b8033bc0f8acc85e925acd7ded04383a48a01c6cc60 | 26 |
| instr_run3_idle.jsonl | b25c8f95de015559867df80688342c50218611190d79ba5ccdb67d79155521dd | 32988 |
| instr_run3_idle.stdout.log | 4ae87123a4493f4d51aa0b8033bc0f8acc85e925acd7ded04383a48a01c6cc60 | 26 |
| instr_run4_saturated.jsonl | 30fb0679a91dbf1c6370ce2267c8e6f0739bd11449905285e2c33d4446f13d0b | 33670 |
| instr_run4_saturated.stdout.log | 2a280c64d896f1555cd737f77b05ecf7f2bdc064156846f9986cd7ce2532c154 | 113 |
| instr_run5_idle_v2.jsonl | 535de1c3d63d61654587525a054bd7fba008254cf12286067e6c943ed2ecb435 | 35453 |
| instr_run5_idle_v2.stdout.log | 4ae87123a4493f4d51aa0b8033bc0f8acc85e925acd7ded04383a48a01c6cc60 | 26 |
| instr_run6_saturated_v2.jsonl | 7eae5818f12600266c4f8fff6c6b84046b80dc4e9dd3202814f9602207d4ea40 | 35390 |
| instr_run6_saturated_v2.stdout.log | 4ae87123a4493f4d51aa0b8033bc0f8acc85e925acd7ded04383a48a01c6cc60 | 26 |
| instr_run7_saturated_v2.jsonl | 6e18aa8eeaf9a7f62c5985537b0b9f6a43d8d2f4eb73de54b0ce302ee89b8b2f | 36320 |
| instr_run7_saturated_v2.stdout.log | deb2b5e044bb5e3cdf0b8c32f4779286c37a24435834e67917667bae4a40a03d | 110 |
| pidfd_freshclone_regress.log | 58a7e95c74fe0824456c4d92926320a937cb8d76750e805a7d3341f5e118fde4 | 16706 |
| pidfd_reg1_fwd.log | 58a7e95c74fe0824456c4d92926320a937cb8d76750e805a7d3341f5e118fde4 | 16706 |
| pidfd_reg2_twice.log | d43f4a963528a3627b050f6c82d8d0b0ea197b6fa6528013aa84980b6ab3ef0f | 33398 |
| pidfd_reg3_rev.log | 0f9aeedb0c3200bd81463713ae87875441c315b92544092055e6ce0258ae4b3d | 16706 |
| post_baseline_uninstrumented.log | 744b65eb56923071261c2d487511327202bb065569d5f39e7e1489ca2274bc83 | 26 |
| post_post1_idle.jsonl | bd97773a4e069e5b77474fb4cdd51b67a20fb4da9be72b031731593cb2cc3716 | 45304 |
| post_post1_idle.stdout.log | 744b65eb56923071261c2d487511327202bb065569d5f39e7e1489ca2274bc83 | 26 |
| post_post2_saturated.jsonl | a79c6fe1e34aee5185b894b0b6408a9a1844cb2b1b03e7817f2cb5328833780c | 45801 |
| post_post2_saturated.stdout.log | 744b65eb56923071261c2d487511327202bb065569d5f39e7e1489ca2274bc83 | 26 |
| post_post3_saturated.jsonl | 525b9d608080dd0278de7703e2c1b11672d36be726920aa9749fad5ac2b32e87 | 46524 |
| post_post3_saturated.stdout.log | 744b65eb56923071261c2d487511327202bb065569d5f39e7e1489ca2274bc83 | 26 |
| post_post4_saturated.jsonl | 96d38bd012feeff4d42765e3c6508dcdf64af5e688f128b29740ad57755e7c06 | 47245 |
| post_post4_saturated.stdout.log | 744b65eb56923071261c2d487511327202bb065569d5f39e7e1489ca2274bc83 | 26 |

Digests computed at publication time from the
files as copied from the originating workspaces;
the originating circuits' packets (included) are
the claim documents for these artifacts.
