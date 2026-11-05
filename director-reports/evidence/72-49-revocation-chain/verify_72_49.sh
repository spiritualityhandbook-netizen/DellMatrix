#!/usr/bin/env bash
# 72-49 (SM-32) — INDEPENDENT VERIFICATION SCRIPT
#
# Supplied under the Director's 72-49 evidence-supplement review
# (2026-11-05 05:44 CST, Gmail id 1a1ab863d1959421): "Supply one
# independently runnable, frozen exact-head verification
# command/script with prerequisites and explicit checkout of
# df88f72 and ed4ac00; verify sha256sum -c MANIFEST.sha256,
# targeted 60/60, and genuine child-process denial. Preserve
# the original/reconstructed mutant distinction."
#
# This script is the ONE command:
#     bash verify_72_49.sh
# It clones the repository FRESH from GitHub into a temp dir,
# and checks, in order:
#   1. MANIFEST.sha256 integrity of this evidence bundle, in a
#      checkout of the PR #297 branch head that carries it.
#   2. Targeted suite at the EXECUTED code head df88f72:
#      expects exit 0 and the line "SM32: 60/60 GREEN". The
#      suite's restart phase presents session-A artifacts to a
#      GENUINE CHILD OS PROCESS (subprocess) whose fresh policy
#      must deny every one — that is the child-process denial
#      check; the suite fails (nonzero exit) if any is allowed.
#   3. The bundled probe (mr49_probe.py, preserved in the
#      manifest) run against the df88f72 checkout: expects
#      exit 0 (66/66 expectations, cross-process leg included).
#   4. Targeted suite at the MERGED head ed4ac00: same
#      expectations as step 2.
#   5. Byte identity of form/dell_matrix/acceptance_policy.py
#      across base 0c062a1, code head df88f72 and merged head
#      ed4ac00 (SHA-256 of the git blobs must all be equal).
#
# PREREQUISITES: bash, git, python3 (>=3.10), sha256sum, and
# network access to github.com. No repository state is used:
# the clone is fresh and the script never writes outside its
# temp dir. Runtime is dominated by two suite runs (each
# well under a minute on the reference machine).
#
# MUTANT DISTINCTION (preserved, not re-executed here): the
# kill logs mutant_m{1,2,3}.log are the ORIGINALS from the
# Cycle 15 session; mutant_m{1,2,3}_recon.log are LABELED
# RECONSTRUCTIONS re-executed in Cycle 19 from the diffs in
# mutant_m{1,2,3}.diff. This script does not apply mutants;
# it verifies the unmutated contract.
#
# Exit code: 0 only if every step passes; a FAIL line names
# the step that failed.

set -u
REPO_URL="https://github.com/spiritualityhandbook-netizen/DellMatrix"
CODE_HEAD="df88f72ce5711bb7e64f9a506e33c8a0eaf4470f"
REPORT_HEAD="423ab500ece6fcb6292f6fb979587e998c1f91d6"
MERGED_HEAD="ed4ac00fba08b81a7194dfd9d76618d07c74ec21"
BASE_HEAD="0c062a152807392cbfc987eb3c998e99b5662069"
SUPPLEMENT_BRANCH="uni/72-49-evidence-supplement"
FAILED=0

step() { echo; echo "=== $1 ==="; }
fail() { echo "FAIL: $1"; FAILED=1; }

for tool in git python3 sha256sum; do
  command -v "$tool" >/dev/null 2>&1 || { echo "FAIL: prerequisite missing: $tool"; exit 1; }
done

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
echo "verify_72_49: fresh clone into $WORK/repo"

git clone --quiet "$REPO_URL" "$WORK/repo" || { echo "FAIL: clone"; exit 1; }
cd "$WORK/repo" || exit 1
git fetch --quiet origin "$SUPPLEMENT_BRANCH" || { echo "FAIL: fetch supplement branch"; exit 1; }

step "1. MANIFEST.sha256 integrity (PR #297 supplement head)"
git checkout --quiet FETCH_HEAD || fail "checkout supplement head"
SUPP_HEAD="$(git rev-parse HEAD)"
echo "supplement head: $SUPP_HEAD"
(cd director-reports/evidence/72-49-revocation-chain && sha256sum -c MANIFEST.sha256) \
  || fail "MANIFEST.sha256 verification"
cp director-reports/evidence/72-49-revocation-chain/mr49_probe.py "$WORK/mr49_probe.py" \
  || fail "probe copy from bundle"

step "2. Targeted suite at executed code head $CODE_HEAD"
git checkout --quiet "$CODE_HEAD" || fail "checkout code head"
OUT="$(python3 -m form.sm32_revocation_chain_test 2>&1)"; RC=$?
echo "$OUT" | tail -3
[ "$RC" -eq 0 ] || fail "suite exit code at code head (rc=$RC)"
echo "$OUT" | grep -q "SM32: 60/60 GREEN" || fail "suite did not report 60/60 at code head"

step "3. Bundled probe against the code head (cross-process denial)"
# Working tree is still at CODE_HEAD from step 2; the probe copy
# was taken from the verified bundle in step 1. The probe inserts
# the current directory into sys.path, so it runs from the repo
# root of the df88f72 checkout; its "present" leg is a genuine
# child OS process.
(cd "$WORK/repo" && python3 "$WORK/mr49_probe.py" > "$WORK/probe_out.txt" 2>&1); RC=$?
tail -3 "$WORK/probe_out.txt"
[ "$RC" -eq 0 ] || fail "probe exit code (rc=$RC)"
grep -q "FAIL" "$WORK/probe_out.txt" && fail "probe reported a FAIL line"

step "4. Targeted suite at merged head $MERGED_HEAD"
git checkout --quiet "$MERGED_HEAD" || fail "checkout merged head"
OUT="$(python3 -m form.sm32_revocation_chain_test 2>&1)"; RC=$?
echo "$OUT" | tail -3
[ "$RC" -eq 0 ] || fail "suite exit code at merged head (rc=$RC)"
echo "$OUT" | grep -q "SM32: 60/60 GREEN" || fail "suite did not report 60/60 at merged head"

step "5. acceptance_policy.py byte identity (base / code / merged)"
H_BASE="$(git show "$BASE_HEAD:form/dell_matrix/acceptance_policy.py" | sha256sum | cut -d' ' -f1)"
H_CODE="$(git show "$CODE_HEAD:form/dell_matrix/acceptance_policy.py" | sha256sum | cut -d' ' -f1)"
H_MERGED="$(git show "$MERGED_HEAD:form/dell_matrix/acceptance_policy.py" | sha256sum | cut -d' ' -f1)"
echo "base   $BASE_HEAD  $H_BASE"
echo "code   $CODE_HEAD  $H_CODE"
echo "merged $MERGED_HEAD  $H_MERGED"
[ "$H_BASE" = "$H_CODE" ] && [ "$H_CODE" = "$H_MERGED" ] || fail "acceptance_policy.py differs across heads"

echo
if [ "$FAILED" -eq 0 ]; then
  echo "VERIFY_72_49: ALL STEPS PASS (manifest OK; suite 60/60 at df88f72 and ed4ac00; probe exit 0; policy byte-identical)"
  exit 0
else
  echo "VERIFY_72_49: FAILED (see FAIL lines above)"
  exit 1
fi
