# EVIDENCE — independent certification runner, Uni-side fresh-clone run

Scope: the certification runner itself (director-reports/certification_runner.py,
SHA-256 dc988ad38123d75a47a9352ae3c8b6b5af6df83edb351cfec3c594e68a6afcf1)
executed once, exactly as the Director would: a fresh clone of the public
repository at main 081dd35855f964b27bc90e7b6beb5661b7c73c0f, the runner file
overlaid byte-identical (digest verified before the run), one command:

    python3 director-reports/certification_runner.py --out <run dir>

Result: runner exit 0; 12/12 items exit 0 (8 suites + 4 boundary probes).
Suite counts in the raw outputs: DIR-F12 20/20, DIR-F13 17/17, DIR-F14 25/25,
DIR-F15 24/24, DIR-F16 31/31, Step 10 34/34, Step 11 31/31, T2 26/26.
Probes: T2 omitted-node 4/4, DIR-F16 send-boundary 7/7, DIR-F15 2/2,
DIR-F13 8/8. The run's own MANIFEST.sha256 was verified with sha256sum -c:
30/30 files OK.

Environment limits (stated, not hidden): this is a UNI-SIDE SIMULATION of
the Director's path, executed on Uni's machine (Python 3.12.3, Linux) — it
is NOT independent execution and certifies nothing. The fresh clone's HEAD
was 081dd35 (the runner reaches main only with its own merge), so the
runner file was overlaid; its digest in run/environment.txt matches the
committed runner exactly, so the instrument that ran is the instrument
submitted. Certification happens when the Director runs the same command
in his own environment.

## Files (SHA-256, byte size)

- `run/MANIFEST.sha256` — 3196 bytes — `3115d58a741b8e2bad5c0e7308c4f2f9be2a23864dc9de6c9054653b5e0492ec`
- `run/environment.txt` — 712 bytes — `8113fc5028ff42281d8250a688660b62328093354ca1d40bd351afd7aed50233`
- `run/probe_sources/probe_dirf13_malformed_count.py` — 1984 bytes — `f1605705effb1c86a9fe032c8ca4e83ac2cc620e8030f5d526ab0a07f47d1d2b`
- `run/probe_sources/probe_dirf15_absent_vs_none.py` — 2255 bytes — `e4b60235d46c4a7102087ef4c1f0660e0e5e5dc923603ea7143abf1c64a0feb4`
- `run/probe_sources/probe_dirf16_send_boundary.py` — 1538 bytes — `57314b2db6419658aa29ed3d9103d07a172398aea70e3430c88bcaf02367da83`
- `run/probe_sources/probe_t2_omitted_node.py` — 1869 bytes — `56d861fef4919436212fd15f21c0305ce87fcbd5f5fdf11ccfa9ab4d2207c056`
- `run/probes/probe_dirf13_malformed_count.stderr.txt` — 0 bytes — `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `run/probes/probe_dirf13_malformed_count.stdout.txt` — 459 bytes — `a0b80808f7de4d221c77f8ce2fd598b64e7984a051f3482bdea26870cb26b5a9`
- `run/probes/probe_dirf15_absent_vs_none.stderr.txt` — 0 bytes — `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `run/probes/probe_dirf15_absent_vs_none.stdout.txt` — 394 bytes — `787f3fc83230eb8c2c006e853651bea7b991f4c6dbe2df4e3332e5ee923840c9`
- `run/probes/probe_dirf16_send_boundary.stderr.txt` — 0 bytes — `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `run/probes/probe_dirf16_send_boundary.stdout.txt` — 432 bytes — `4459618d54a74820436d63b527878e8fc9defc6277a1382f3671eaf214093772`
- `run/probes/probe_t2_omitted_node.stderr.txt` — 0 bytes — `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `run/probes/probe_t2_omitted_node.stdout.txt` — 405 bytes — `310ea69045ce695fee1ff04a178249ba8fe4fecb57673c8fbaed5e38b4c6fe8e`
- `run/suites/suite_dirf12.stderr.txt` — 0 bytes — `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `run/suites/suite_dirf12.stdout.txt` — 1140 bytes — `91d2336c40db3aa175b587943fd5f7aafe9888d409190f55ed5a09145c3905e4`
- `run/suites/suite_dirf13.stderr.txt` — 0 bytes — `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `run/suites/suite_dirf13.stdout.txt` — 25 bytes — `7ccfea120da9186c1f68f0bc084ef2218692172bb94fa88b7d93d869959adc5d`
- `run/suites/suite_dirf14.stderr.txt` — 0 bytes — `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `run/suites/suite_dirf14.stdout.txt` — 29 bytes — `07d21457fd9f5495161fc2404d1e29e1dc45ae221240ca3518955a25a3c94de7`
- `run/suites/suite_dirf15.stderr.txt` — 0 bytes — `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `run/suites/suite_dirf15.stdout.txt` — 18 bytes — `289f93bed72e5afeec619a769b1b6e08da31f5deb5070ba82ee6066d379e81bb`
- `run/suites/suite_dirf16.stderr.txt` — 0 bytes — `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `run/suites/suite_dirf16.stdout.txt` — 26 bytes — `feedc6683620321fcf14a01048f6c7b3365e1bdc7a615e5d3758fd2f1fb72071`
- `run/suites/suite_step10.stderr.txt` — 0 bytes — `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `run/suites/suite_step10.stdout.txt` — 26 bytes — `ded72197936163d128e64725bf4b492cb050aeb715bdf0fb9371d5ef875e38d3`
- `run/suites/suite_step11.stderr.txt` — 0 bytes — `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `run/suites/suite_step11.stdout.txt` — 31 bytes — `1acd28db9ff6488293d9ef0b3e3de3b119bbb5937e24f5d3e8ff59f50e1989cd`
- `run/suites/suite_t2.stderr.txt` — 0 bytes — `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `run/suites/suite_t2.stdout.txt` — 1623 bytes — `08f45eaa87ed07478ec012184644a2ddba2e0fe4e4498fa975d5db4a2854db8f`
- `run/summary.txt` — 1412 bytes — `c1f8bcc03f915a5a7156f5859ee1cb7ce4376bce0f84e51788d5654efd9dd0da`
