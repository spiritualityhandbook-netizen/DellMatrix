#!/usr/bin/env bash
# 72-28 (SM-35) — INDEPENDENT VERIFICATION SCRIPT
#
# Supplied under the Director's 72-28 exact-head review
# (2026-11-05 09:32 CST, Gmail id 1a1ac56ce97780e7):
# INSUFFICIENT_EVIDENCE for independent ALL_AI_CONFIRMATION_PASS.
# Demands discharged here: retrievable original raw logs/commands/
# exit codes and mutant diffs at exact SHAs (this bundle); a
# pinned reproducible runner at the final PR SHA covering H1-A/B
# and CP0-CP4 with pre/post hashes and a fresh-process view (the
# suite itself performs the fresh-process file-hash views); an
# independently executed receipt (the verify-72-28 GitHub Actions
# workflow runs this script at the exact pushed head).
#
#     bash verify_72_28.sh <SUPPLEMENT_SHA>
#
# <SUPPLEMENT_SHA> is the full immutable head of the supplement
# branch carrying this bundle. Step 1 checks out exactly that
# SHA in a FRESH clone and ASSERTS HEAD equality BEFORE any
# manifest verification. A script cannot contain its own commit
# SHA, so the pin is an argument, enforced by assertion.
#
# Checks, in order:
#   1. MANIFEST.sha256 integrity of this bundle at the pinned
#      supplement checkout.
#   2. Suite form/sm35_pair_atomic_test.py at the EXECUTED code
#      head b893931: exit 0, "SM35: 45/45 GREEN".
#   3. Suite at the final PR head 2fefcdc: same expectations.
#      (Suite blob is byte-identical at both heads — step 5.)
#   4. Bundled original probe mr28_probe.py (extracted verbatim
#      from commit 132f39b, where it was briefly committed) run
#      against the 2fefcdc checkout: exit 0.
#   5. Byte identity (SHA-256 of git blobs) of
#      form/sm35_pair_atomic_test.py AND the product files under
#      test (form/persist_rest.py,
#      form/mandell/checkpoint_generation.py) across b893931,
#      2fefcdc and merge a585a6d — the b893931<->2fefcdc
#      reconciliation: code under test never changed.
#   6. Mutant re-executions at 2fefcdc (LABELED supplement
#      executions, NOT the originals; original kill logs are
#      mutant_m{1,2,3}.log in this bundle; diffs applied here
#      are the *_recon.diff reconstructions):
#      M1 drop persist_rest.load's recover_checkpoint_intent call
#         -> suite MUST fail with the CP3 signature.
#      M2 skip the seal's program save (persist_save)
#         -> suite MUST fail with the CP4 signature.
#      M3 ordinary save also saves the nursery
#         -> suite MUST fail with the H1-B signature.
#      Each mutant is reverted (git checkout) before the next.
#
# PREREQUISITES: bash, git, python3 (>=3.10), sha256sum,
# network access to github.com. The clone is fresh; the script
# writes only inside its temp dir. PR #298 is MERGED
# (MERGED_VERIFIED_BY_UNI); a PASS here is independent execution
# evidence for the Director, not a certification.
#
# Exit code: 0 only if every step passes.

set -u
REPO_URL="https://github.com/spiritualityhandbook-netizen/DellMatrix"
CODE_SHA="b8939310b3fb0dc9049cb98a33cd1e28d0d26ebb"
FINAL_SHA="2fefcdceea1c28251c53ca90028772ebb5713a1e"
MERGE_SHA="a585a6ddba9fb2128a3cc927bd4bf826c1a83fb8"
PROBE_SHA="132f39b9a7a2ed66512413a630283df602395315"
SUPPLEMENT_SHA="${1:-}"
if [ -z "$SUPPLEMENT_SHA" ]; then echo "FAIL: usage: bash verify_72_28.sh <SUPPLEMENT_SHA>"; exit 1; fi
fail() { echo "FAIL: $1"; exit 1; }
WORK="$(mktemp -d)"
echo "== verify_72_28: env: host=$(hostname) python=$(python3 --version 2>&1) date=$(date -u +%FT%TZ)"
echo "== pins: code=$CODE_SHA final=$FINAL_SHA merge=$MERGE_SHA supplement=$SUPPLEMENT_SHA"
git clone -q "$REPO_URL" "$WORK/repo" || fail "clone"
cd "$WORK/repo" || fail "cd"

echo "== step 1: pinned supplement checkout + HEAD equality + manifest"
git checkout -q "$SUPPLEMENT_SHA" || fail "checkout supplement"
[ "$(git rev-parse HEAD)" = "$SUPPLEMENT_SHA" ] || fail "HEAD != SUPPLEMENT_SHA"
BUNDLE="director-reports/evidence/72-28-pair-atomic"
(cd "$BUNDLE" && sha256sum -c MANIFEST.sha256) || fail "manifest"
echo "PASS step 1"

run_suite() {  # $1 = sha, $2 = label
  git checkout -q "$1" || fail "checkout $2"
  [ "$(git rev-parse HEAD)" = "$1" ] || fail "HEAD != $2"
  python3 -m form.sm35_pair_atomic_test > "$WORK/suite_$2.log" 2>&1
  rc=$?
  tail -2 "$WORK/suite_$2.log"
  [ $rc -eq 0 ] || fail "suite at $2 exit $rc"
  grep -q "45/45" "$WORK/suite_$2.log" || fail "suite at $2 missing 45/45"
  echo "PASS suite at $2 ($1)"
}
echo "== step 2: suite at executed code head"
run_suite "$CODE_SHA" code
echo "== step 3: suite at final PR head"
run_suite "$FINAL_SHA" final

echo "== step 4: original probe at final head"
git show "$PROBE_SHA:mr28_probe.py" > "$WORK/mr28_probe.py" || fail "extract probe"
python3 "$WORK/mr28_probe.py" > "$WORK/probe.log" 2>&1
rc=$?
tail -2 "$WORK/probe.log"
[ $rc -eq 0 ] || fail "probe exit $rc"
echo "PASS step 4"

echo "== step 5: byte identity across heads"
for f in form/sm35_pair_atomic_test.py form/persist_rest.py form/mandell/checkpoint_generation.py; do
  h1=$(git show "$CODE_SHA:$f" | sha256sum | cut -d' ' -f1)
  h2=$(git show "$FINAL_SHA:$f" | sha256sum | cut -d' ' -f1)
  h3=$(git show "$MERGE_SHA:$f" | sha256sum | cut -d' ' -f1)
  echo "  $f code=$h1 final=$h2 merge=$h3"
  [ "$h1" = "$h2" ] && [ "$h2" = "$h3" ] || fail "byte identity $f"
done
echo "PASS step 5"

echo "== step 6: mutant re-executions at final head (supplement executions)"
git checkout -q "$FINAL_SHA" || fail "checkout final for mutants"
mutant() {  # $1 = id, $2 = signature
  python3 -m form.sm35_pair_atomic_test > "$WORK/mutant_$1.log" 2>&1
  rc=$?
  git checkout -- form/persist_rest.py form/mandell/checkpoint_generation.py
  [ $rc -ne 0 ] || fail "mutant $1 NOT killed (suite green)"
  grep -q "$2" "$WORK/mutant_$1.log" || fail "mutant $1 killed at wrong signature (wanted: $2)"
  echo "PASS mutant $1 killed at signature: $2"
}
python3 - <<'PYEOF' || fail "apply M1"
import pathlib
p = pathlib.Path('form/persist_rest.py')
lines = p.read_text().split('\n')
assert lines.count('    recover_checkpoint_intent(owner)') == 1
p.write_text('\n'.join(l for l in lines if l != '    recover_checkpoint_intent(owner)'))
PYEOF
mutant M1 "CP3: checkpoint verdict is OLD_ONLY"
python3 - <<'PYEOF' || fail "apply M2"
import pathlib
p = pathlib.Path('form/mandell/checkpoint_generation.py')
t = p.read_text(); assert t.count('        persist_save(program)') == 1
p.write_text(t.replace('        persist_save(program)', '        pass  # MUTANT M2'))
PYEOF
mutant M2 "CP4: checkpoint verdict is NEW_PAIR"
python3 - <<'PYEOF' || fail "apply M3"
import pathlib
p = pathlib.Path('form/persist_rest.py')
t = p.read_text(); anchor = '    check_save_allowed(program, "persist_rest.save")'
assert t.count(anchor) == 1
p.write_text(t.replace(anchor, anchor + '\n    program.nursery.save()  # MUTANT M3'))
PYEOF
mutant M3 "H1-B: ordinary program-first crash exposes HYBRID pair"
echo "PASS step 6"
echo "ALL STEPS PASS"
exit 0
