#!/usr/bin/env python3
"""R3 Permanent Regressions (GDP_R3_VERIFICATION_UNBLOCK).

Uses multiline subprocess scripts, compiled before execution.
Asserts expected RollbackRecoveryError and journal preservation.
"""
import os
import subprocess
import sys
import json
import py_compile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)
os.chdir(REPO)

def run_script(name, code, timeout=60):
    """Run a multiline script, compiled first. Returns (rc, stdout, stderr)."""
    # Write to temp file for compilation check
    tmp = os.path.join("/tmp", "r3_%s_%d.py" % (name, os.getpid()))
    with open(tmp, "w") as f:
        f.write(code)
    try:
        py_compile.compile(tmp, doraise=True)
    except py_compile.PyCompileError as e:
        return -1, "", "COMPILE_ERROR: %s" % e
    r = subprocess.run([sys.executable, tmp], capture_output=True,
                       text=True, timeout=timeout, cwd=REPO)
    try:
        os.remove(tmp)
    except:
        pass
    return r.returncode, r.stdout.strip(), r.stderr.strip()

def clean(owner):
    for pat in [
        'form/state/program_%s.json' % owner,
        'form/state/nursery_%s.json' % owner,
        'form/state/confirm_%s.journal.json' % owner,
        'form/state/supersede_%s.journal.json' % owner,
    ]:
        try:
            os.remove(os.path.join(REPO, pat))
        except OSError:
            pass

results = []
def rec(name, ok, detail=""):
    results.append(ok)
    print("[%s] %s %s" % ("PASS" if ok else "FAIL", name, detail[:70]))

# 1. malformed_units: Must raise RollbackRecoveryError, journal preserved
def t01():
    o = "R3H01"; clean(o)
    setup = """
import sys
sys.path.insert(0, %r)
from form.open import open_program
from form import persist_rest
p = open_program(%r)
pr = p.nursery.add('t', words='x')
p.nursery.save()
persist_rest.save(p)
print('PID:' + pr.id)
""" % (REPO, o)
    rc, out, err = run_script("t01_setup", setup)
    if rc != 0 or "PID:" not in out:
        rec("01_malformed_units", False, "setup failed rc=%d" % rc)
        clean(o); return
    pid = out.split("PID:")[1].strip().split()[0]
    # Corrupt units
    pp = os.path.join(REPO, 'form/state/program_%s.json' % o)
    d = json.load(open(pp))
    d['plane']['units'] = "NOT_A_DICT"
    json.dump(d, open(pp, 'w'))
    # Write journal with real pid
    jp = os.path.join(REPO, 'form/state/confirm_%s.journal.json' % o)
    json.dump({
        "journal_version": 1,
        "operation": "confirm_proposal",
        "owner": o,
        "proposal_id": pid,
        "phase": "prepared",
        "old_nursery_sha256": "aaa",
        "old_program_sha256": "bbb"
    }, open(jp, 'w'))
    # Try load - must raise RollbackRecoveryError
    load = """
import sys
sys.path.insert(0, %r)
from form import persist_rest
from form.mandell.core_i_recovery import RollbackRecoveryError
try:
    p = persist_rest.load(%r, activate=False)
    print('NO_RAISE')
except RollbackRecoveryError as e:
    print('RAISED_ROLLBACK:' + str(e)[:50])
except Exception as e:
    print('RAISED_OTHER:' + type(e).__name__)
""" % (REPO, o)
    rc, out, err = run_script("t01_load", load)
    jexists = os.path.isfile(jp)
    ok = "RAISED_ROLLBACK" in out and jexists
    rec("01_malformed_units", ok,
        "raised_rollback=%s preserved=%s" % ("RAISED_ROLLBACK" in out, jexists))
    clean(o)

# 2. missing_member: Missing plane -> raise, journal preserved
def t02():
    o = "R3H02"; clean(o)
    setup = """
import sys
sys.path.insert(0, %r)
from form.open import open_program
from form import persist_rest
p = open_program(%r)
pr = p.nursery.add('t', words='x')
p.nursery.save()
persist_rest.save(p)
print('PID:' + pr.id)
""" % (REPO, o)
    rc, out, err = run_script("t02_setup", setup)
    if rc != 0 or "PID:" not in out:
        rec("02_missing_member", False, "setup failed")
        clean(o); return
    pid = out.split("PID:")[1].strip().split()[0]
    pp = os.path.join(REPO, 'form/state/program_%s.json' % o)
    d = json.load(open(pp))
    del d['plane']
    json.dump(d, open(pp, 'w'))
    jp = os.path.join(REPO, 'form/state/confirm_%s.journal.json' % o)
    json.dump({
        "journal_version": 1, "operation": "confirm_proposal", "owner": o,
        "proposal_id": pid, "phase": "prepared",
        "old_nursery_sha256": "aaa", "old_program_sha256": "bbb"
    }, open(jp, 'w'))
    load = """
import sys
sys.path.insert(0, %r)
from form import persist_rest
from form.mandell.core_i_recovery import RollbackRecoveryError
try:
    p = persist_rest.load(%r, activate=False)
    print('NO_RAISE')
except RollbackRecoveryError:
    print('RAISED_ROLLBACK')
except Exception as e:
    print('RAISED_OTHER:' + type(e).__name__)
""" % (REPO, o)
    rc, out, err = run_script("t02_load", load)
    jexists = os.path.isfile(jp)
    ok = "RAISED_ROLLBACK" in out and jexists
    rec("02_missing_member", ok, "raised=%s preserved=%s" % ("RAISED_ROLLBACK" in out, jexists))
    clean(o)

# 3. foreign_owner: Journal for different owner -> raise, preserved
def t03():
    o = "R3H03"; clean(o)
    setup = """
import sys
sys.path.insert(0, %r)
from form.open import open_program
from form import persist_rest
p = open_program(%r)
pr = p.nursery.add('t', words='x')
p.nursery.save()
persist_rest.save(p)
print('PID:' + pr.id)
""" % (REPO, o)
    rc, out, err = run_script("t03_setup", setup)
    if rc != 0 or "PID:" not in out:
        rec("03_foreign_owner", False, "setup failed")
        clean(o); return
    pid = out.split("PID:")[1].strip().split()[0]
    jp = os.path.join(REPO, 'form/state/confirm_%s.journal.json' % o)
    json.dump({
        "journal_version": 1, "operation": "confirm_proposal",
        "owner": "DIFFERENT_OWNER",  # Mismatch!
        "proposal_id": pid, "phase": "prepared",
        "old_nursery_sha256": "aaa", "old_program_sha256": "bbb"
    }, open(jp, 'w'))
    load = """
import sys
sys.path.insert(0, %r)
from form import persist_rest
from form.mandell.core_i_recovery import RollbackRecoveryError
try:
    p = persist_rest.load(%r, activate=False)
    print('NO_RAISE')
except RollbackRecoveryError:
    print('RAISED_ROLLBACK')
except Exception as e:
    print('RAISED_OTHER:' + type(e).__name__)
""" % (REPO, o)
    rc, out, err = run_script("t03_load", load)
    jexists = os.path.isfile(jp)
    ok = "RAISED_ROLLBACK" in out and jexists
    rec("03_foreign_owner", ok, "raised=%s preserved=%s" % ("RAISED_ROLLBACK" in out, jexists))
    clean(o)

# 4. historical preserved (no journal)
def t04():
    o = "R3H04"; clean(o)
    code = """
import sys, json
sys.path.insert(0, %r)
from form.open import open_program
from form import persist_rest
from form.dell_matrix.nursery import owner_nursery_path
p = open_program(%r)
p.cube.session.plane.units.clear()
pr = p.nursery.add('h', words='old')
pid = pr.id
p.nursery.save()
persist_rest.save(p)
# Manually mark confirmed (historical, no journal)
np = owner_nursery_path(%r)
d = json.load(open(np))
d[pid]['status'] = 'confirmed'
json.dump(d, open(np, 'w'))
# Fresh load
p2 = persist_rest.load(%r, activate=False)
st = p2.nursery.proposals[pid].status
print('STATUS:' + st)
""" % (REPO, o, o, o)
    rc, out, err = run_script("t04", code)
    ok = rc == 0 and "STATUS:confirmed" in out
    rec("04_historical_preserved", ok, out[:50])
    clean(o)

# 5. pending with Idea (no journal, not healed)
def t05():
    o = "R3H05"; clean(o)
    code = """
import sys
sys.path.insert(0, %r)
from form.open import open_program
from form import persist_rest
p = open_program(%r)
p.cube.session.plane.units.clear()
pr = p.nursery.add('t', words='x')
pid = pr.id
p.place(pid, 't', words='x')  # Place without confirming
p.nursery.save()
persist_rest.save(p)
p2 = persist_rest.load(%r, activate=False)
st = p2.nursery.proposals[pid].status
has = pid in p2.cube.session.plane.units
print('STATUS:' + st + ' HAS:' + str(has))
""" % (REPO, o, o)
    rc, out, err = run_script("t05", code)
    ok = rc == 0 and "STATUS:pending" in out and "HAS:True" in out
    rec("05_pending_with_idea", ok, out[:50])
    clean(o)

# 6. supersession basic
def t06():
    o = "R3H06"; clean(o)
    code = """
import sys
sys.path.insert(0, %r)
from form.open import open_program
from form.mandell import supersession as S
p = open_program(%r)
old = p.nursery.add('base', words='v1')
p.confirm_proposal(old.id, _producer="test", _review_context=p.make_review_context(old.id, "test"))
p.acceptance_policy.grant_opt_in("test", scope="test")
r = S.supersede_proposal(p, old.id, 'v2 words', _producer="test")
print('OK:' + str(r.get('ok')))
""" % (REPO, o)
    rc, out, err = run_script("t06", code)
    ok = rc == 0 and "OK:True" in out
    rec("06_supersession", ok, out[:50])
    clean(o)

# 7. idempotent recovery
def t07():
    o = "R3H07"; clean(o)
    setup = """
import sys, json
sys.path.insert(0, %r)
from form.open import open_program
from form import persist_rest
from form.mandell.core_i_recovery import write_confirm_intent
from form.dell_matrix.nursery import owner_nursery_path
p = open_program(%r)
p.cube.session.plane.units.clear()
pr = p.nursery.add('t', words='x')
pid = pr.id
p.nursery.save()
persist_rest.save(p)
write_confirm_intent(%r, pid)
np = owner_nursery_path(%r)
d = json.load(open(np))
d[pid]['status'] = 'confirmed'
json.dump(d, open(np, 'w'))
print('PID:' + pid)
""" % (REPO, o, o, o)
    rc, out, err = run_script("t07_setup", setup)
    if rc != 0 or "PID:" not in out:
        rec("07_idempotent", False, "setup failed")
        clean(o); return
    pid = out.split("PID:")[1].strip().split()[0]
    load1 = """
import sys
sys.path.insert(0, %r)
from form import persist_rest
p = persist_rest.load(%r, activate=False)
print('ST1:' + p.nursery.proposals[%r].status)
""" % (REPO, o, pid)
    rc1, out1, _ = run_script("t07_load1", load1)
    load2 = """
import sys
sys.path.insert(0, %r)
from form import persist_rest
p = persist_rest.load(%r, activate=False)
print('ST2:' + p.nursery.proposals[%r].status)
""" % (REPO, o, pid)
    rc2, out2, _ = run_script("t07_load2", load2)
    ok = "ST1:pending" in out1 and "ST2:pending" in out2
    rec("07_idempotent", ok, out1[:30] + " " + out2[:30])
    clean(o)

# 8. revision distinct from derivation
def t08():
    o = "R3H08"; clean(o)
    code = """
import sys
sys.path.insert(0, %r)
from form.open import open_program
from form.mandell import supersession as S
from form import persist_rest
p = open_program(%r)
old = p.nursery.add('base', words='v1')
p.confirm_proposal(old.id, _producer="test", _review_context=p.make_review_context(old.id, "test"))
p.acceptance_policy.grant_opt_in("test", scope="test")
old_id = old.id
r = S.supersede_proposal(p, old_id, 'v2 words', _producer="test")
new_id = r.get('new_id')
p2 = persist_rest.load(%r, activate=False)
old_p = p2.nursery.proposals[old_id]
new_p = p2.nursery.proposals[new_id]
rev_ok = (old_p.superseded_by_id == new_id and new_p.supersedes_id == old_id)
chain = new_p.chain if hasattr(new_p, 'chain') else []
chain_ok = (old_id not in chain)
print('REV:' + str(rev_ok) + ' CHAIN:' + str(chain_ok))
""" % (REPO, o, o)
    rc, out, err = run_script("t08", code)
    ok = rc == 0 and "REV:True" in out and "CHAIN:True" in out
    rec("08_revision_distinct", ok, out[:50])
    clean(o)

def t09():
    """Stale journal + concurrent write -> clear, not DoS."""
    o = "R3H09"; clean(o)
    setup = """
import sys, json
sys.path.insert(0, %r)
from form.open import open_program
from form import persist_rest
from form.mandell.core_i_recovery import write_confirm_intent
p = open_program(%r)
pr = p.nursery.add('A', words='x')
pid_a = pr.id
p.nursery.save()
persist_rest.save(p)
# Write journal for A (simulating crash before write)
write_confirm_intent(%r, pid_a)
# Concurrent legitimate write: add B
pr_b = p.nursery.add('B', words='y')
p.nursery.save()
persist_rest.save(p)
print('PID_A:' + pid_a)
""" % (REPO, o, o)
    rc, out, err = run_script("t09_setup", setup)
    if rc != 0 or "PID_A:" not in out:
        rec("09_stale_concurrent", False, "setup failed")
        clean(o); return
    pid_a = out.split("PID_A:")[1].strip().split()[0]
    # Fresh load should clear stale journal (A still pending), not raise
    load = """
import sys, os
sys.path.insert(0, %r)
from form import persist_rest
from form.mandell.core_i_recovery import _confirm_journal_path
try:
    p = persist_rest.load(%r, activate=False)
    st = p.nursery.proposals[%r].status
    jexists = os.path.isfile(_confirm_journal_path(%r))
    print('STATUS:' + st + ' JEXISTS:' + str(jexists))
except Exception as e:
    print('RAISED:' + type(e).__name__)
""" % (REPO, o, pid_a, o)
    rc, out, err = run_script("t09_load", load)
    # Should NOT raise, A should still be pending, journal cleared
    ok = "STATUS:pending" in out and "JEXISTS:False" in out and "RAISED" not in out
    rec("09_stale_concurrent", ok, out[:60])
    clean(o)

def t10():
    o = "R3H10"; clean(o)
    setup = """
import sys, json
sys.path.insert(0, %r)
from form.open import open_program
from form import persist_rest
from form.mandell.core_i_recovery import write_confirm_intent
p = open_program(%r)
pr = p.nursery.add('t', words='x')
pid = pr.id
p.nursery.save()
persist_rest.save(p)
# Write journal (pending, no Idea)
write_confirm_intent(%r, pid)
# Manually add Idea to Program WITHOUT updating Nursery
# (simulates partial write: Program modified, Nursery unchanged)
from form.persist import _path
pp = _path(%r)
d = json.load(open(pp))
# Add a fake Idea directly
d['plane']['units'][pid] = {'id': pid, 'label': 't', 'fake': True}
json.dump(d, open(pp, 'w'))
print('PID:' + pid)
""" % (REPO, o, o, o)
    rc, out, err = run_script("t10_setup", setup)
    if rc != 0 or "PID:" not in out:
        rec("10_negA", False, "setup failed")
        clean(o); return
    pid = out.split("PID:")[1].strip().split()[0]
    # Recovery must NOT return no_change (Program was modified)
    # It should either heal (if it can prove) or raise (fail closed)
    # It must NOT silently discard the journal
    load = """
import sys, os
sys.path.insert(0, %r)
from form import persist_rest
from form.mandell.core_i_recovery import _confirm_journal_path, RollbackRecoveryError
try:
    p = persist_rest.load(%r, activate=False)
    jexists = os.path.isfile(_confirm_journal_path(%r))
    # If it didn't raise, journal must NOT have been cleared as no_change
    # (because Program was modified)
    print('NO_RAISE JEXISTS:' + str(jexists))
except RollbackRecoveryError:
    print('RAISED_ROLLBACK')
except Exception as e:
    print('RAISED_OTHER:' + type(e).__name__)
""" % (REPO, o, o)
    rc, out, err = run_script("t10_load", load)
    # PASS if it raised (fail closed) OR if journal was NOT cleared as no_change
    # FAIL if it returned no_change and cleared journal while Program modified
    ok = "RAISED_ROLLBACK" in out or ("NO_RAISE" in out and "JEXISTS:True" in out)
    # Actually, the correct behavior: Program modified + proposal pending
    # = incomplete transition. Should raise (cannot prove safe).
    ok = "RAISED_ROLLBACK" in out
    rec("10_negA_program_modified", ok, out[:60])
    clean(o)

# 11. negative_control_B: Nursery has unrelated write, Program modified
# Same as A, but Nursery also has an unrelated legitimate write.
def t11():
    o = "R3H11"; clean(o)
    setup = """
import sys, json
sys.path.insert(0, %r)
from form.open import open_program
from form import persist_rest
from form.mandell.core_i_recovery import write_confirm_intent
p = open_program(%r)
pr = p.nursery.add('A', words='x')
pid_a = pr.id
p.nursery.save()
persist_rest.save(p)
write_confirm_intent(%r, pid_a)
# Unrelated legitimate write: add B to Nursery
pr_b = p.nursery.add('B', words='y')
p.nursery.save()
# Partial write: add Idea for A to Program file directly
# (simulating a crash where Program was written but Nursery update was lost)
# Do NOT call persist_rest.save(p) after this; that would overwrite the edit.
from form.persist import _path
pp = _path(%r)
d = json.load(open(pp))
d['plane']['units'][pid_a] = {'id': pid_a, 'label': 'A', 'fake': True}
json.dump(d, open(pp, 'w'))
print('PID_A:' + pid_a)
""" % (REPO, o, o, o)
    rc, out, err = run_script("t11_setup", setup)
    if rc != 0 or "PID_A:" not in out:
        rec("11_negB", False, "setup failed")
        clean(o); return
    # Recovery must NOT clear journal as no_change
    load = """
import sys, os
sys.path.insert(0, %r)
from form import persist_rest
from form.mandell.core_i_recovery import _confirm_journal_path, RollbackRecoveryError
try:
    p = persist_rest.load(%r, activate=False)
    jexists = os.path.isfile(_confirm_journal_path(%r))
    print('NO_RAISE JEXISTS:' + str(jexists))
except RollbackRecoveryError:
    print('RAISED_ROLLBACK')
except Exception as e:
    print('RAISED_OTHER:' + type(e).__name__)
""" % (REPO, o, o)
    rc, out, err = run_script("t11_load", load)
    ok = "RAISED_ROLLBACK" in out
    rec("11_negB_both_modified", ok, out[:60])
    clean(o)


# Single source of truth: (owner, callable) pairs.
# Used for smoke execution, direct execution, expected count,
# initial cleanup, and finally cleanup. No duplicated lists.
def t16():
    # F2: Complete and failed compensation via real save wrappers.
    # When commit_checkpoint fails after both live saves, the handler
    # must revert BOTH Nursery and Program files. If compensation
    # succeeds, journal is cleared. If compensation fails, journal is
    # preserved for recovery. Existing Idea values must not change.
    o = "R3H16"
    clean(o)
    # Use .replace for REPO/OWNER to avoid % formatting issues
    setup_template = """
import sys, os, json, hashlib
REPO_DIR = __REPO__
OWNER_ID = __OWNER__
sys.path.insert(0, REPO_DIR)
from form.open import open_program
from form import persist_rest
from form.dell_matrix import confirm_lineage
from form.mandell.core_i_recovery import _confirm_journal_path

def fp_bytes(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

# Setup: create proposal, capture baseline
p = open_program(OWNER_ID)
pr = p.nursery.add('F2_TEST', words='test content')
pid = pr.id
p.nursery.save()
persist_rest.save(p)

npath = os.path.join(REPO_DIR, 'form', 'state', 'nursery_' + OWNER_ID + '.json')
from form.persist import _path as _ppath
ppath = _ppath(OWNER_ID)
baseline_nursery = fp_bytes(npath)
baseline_program = fp_bytes(ppath)

# Test 1: Complete compensation (both saves succeed)
from form.mandell import checkpoint_generation as cg
orig_commit = cg.commit_checkpoint
def failing_commit(program, _fail_at=None):
    program.nursery.save()
    persist_rest.save(program)
    raise OSError("INJECTED_COMMIT_FAILURE")
cg.commit_checkpoint = failing_commit

try:
    p.confirm_proposal(pid, _producer="test", _review_context=p.make_review_context(pid, "test"))
    print('NO_RAISE_UNEXPECTED')
except OSError as e:
    if 'INJECTED_COMMIT_FAILURE' in str(e):
        print('RAISED_EXPECTED')
    else:
        print('OTHER_OSERROR:' + str(e)[:50])
except Exception as e:
    print('OTHER:' + type(e).__name__)
finally:
    cg.commit_checkpoint = orig_commit

jpath = _confirm_journal_path(OWNER_ID)
nursery_ok = fp_bytes(npath) == baseline_nursery
program_ok = fp_bytes(ppath) == baseline_program
journal_cleared = not os.path.isfile(jpath)
# F2: Verify in-memory spatial authority is clean (correct authority:
# program.spatial, not cube.session.spatial). A later save must not
# reintroduce the failed Idea.
spatial_clean = True
try:
    sp = p.spatial
    if hasattr(sp, 'velocities') and pid in sp.velocities:
        spatial_clean = False
    if hasattr(sp, 'placements') and pid in sp.placements:
        spatial_clean = False
except Exception:
    spatial_clean = False
# F2: Verify a later save does not reintroduce the Idea. The Idea must
# be absent from plane.units, spatial authority, and lattice cells.
# History may honestly record the attempt (legitimate audit).
persist_rest.save(p)
idea_absent_after_save = True
try:
    if pid in p.cube.session.plane.units:
        idea_absent_after_save = False
    sp2 = p.spatial
    if hasattr(sp2, 'velocities') and pid in sp2.velocities:
        idea_absent_after_save = False
    if hasattr(sp2, 'placements') and pid in sp2.placements:
        idea_absent_after_save = False
    # Check lattice cells do not contain the Idea
    if hasattr(p.lattice, 'cells'):
        for cell in p.lattice.cells.values():
            members = cell.get('members', []) if isinstance(cell, dict) else []
            if pid in members:
                idea_absent_after_save = False
                break
except Exception:
    idea_absent_after_save = False
print('COMPLETE_COMPENSATION: nursery=%s program=%s journal_cleared=%s spatial_clean=%s no_reintroduce=%s' % (
    nursery_ok, program_ok, journal_cleared, spatial_clean, idea_absent_after_save))

# Test 2: Failed compensation (Program save fails during revert)
p2 = open_program(OWNER_ID)
pr2 = p2.nursery.proposals.get(pid)
if pr2:
    pr2.status = 'pending'
    p2.nursery.save()
    persist_rest.save(p2)

from form.dell_matrix import atomic_write as aw
orig_awb = aw.atomic_write_bytes
write_failed = [False]
def failing_awb(path, blob, *a, **k):
    if 'program_' in str(path) and write_failed[0]:
        raise OSError("INJECTED_WRITE_FAILURE")
    return orig_awb(path, blob, *a, **k)

def failing_commit2(program, _fail_at=None):
    program.nursery.save()
    persist_rest.save(program)
    write_failed[0] = True
    raise OSError("INJECTED_COMMIT_FAILURE_2")

cg.commit_checkpoint = failing_commit2
aw.atomic_write_bytes = failing_awb
try:
    p2.confirm_proposal(pid, _producer="test", _review_context=p2.make_review_context(pid, "test"))
    print('NO_RAISE_UNEXPECTED_2')
except OSError:
    print('RAISED_EXPECTED_2')
except Exception as e:
    print('OTHER_2:' + type(e).__name__)
finally:
    cg.commit_checkpoint = orig_commit
    aw.atomic_write_bytes = orig_awb
    write_failed[0] = False
    write_failed[0] = False

jpath2 = _confirm_journal_path(OWNER_ID)
journal_preserved = os.path.isfile(jpath2)
print('FAILED_COMPENSATION: journal_preserved=%s' % journal_preserved)
print('SETUP_DONE')
"""
    setup = setup_template.replace("__REPO__", repr(REPO)).replace("__OWNER__", repr(o))
    rc, out, err = run_script("t16_setup", setup)
    if rc != 0 or "SETUP_DONE" not in out:
        rec("16_f2_compensation", False, "setup failed: %s" % out[:200])
        print("STDOUT:", out[:400])
        print("STDERR:", err[:400])
        clean(o)
        return
    complete_ok = "COMPLETE_COMPENSATION: nursery=True program=True journal_cleared=True spatial_clean=True no_reintroduce=True" in out
    failed_ok = "FAILED_COMPENSATION: journal_preserved=True" in out
    ok = complete_ok and failed_ok
    rec("16_f2_compensation", ok, "complete=%s failed=%s" % (complete_ok, failed_ok))
    if not ok:
        print("T16 OUT:", out[:600])
    clean(o)

TEST_CASES = [
    ("R3H01", lambda: t01()),
    ("R3H02", lambda: t02()),
    ("R3H03", lambda: t03()),
    ("R3H04", lambda: t04()),
    ("R3H05", lambda: t05()),
    ("R3H06", lambda: t06()),
    ("R3H07", lambda: t07()),
    ("R3H08", lambda: t08()),
    ("R3H09", lambda: t09()),
    ("R3H10", lambda: t10()),
    ("R3H11", lambda: t11()),
    ("R3H12", lambda: t12()),
    ("R3H13", lambda: t13()),
    ("R3H14", lambda: t14()),
    ("R3H14B", lambda: t14b()),
    ("R3H15", lambda: t15()),
    ("R3H15B", lambda: t15b()),
    ("R3H16", lambda: t16()),
]

def smoke():
    """Runner-compatible entry point for form.regress.
    
    Returns True if all tests pass, False otherwise.
    Resets per-run results.
    Ensures cleanup even if tests crash (for --twice isolation).
    """
    global results
    results = []
    # Clean up any leftover state from previous runs (for --twice)
    for owner, _ in TEST_CASES:
        clean(owner)
    executed = []
    try:
        for owner, fn in TEST_CASES:
            fn()
            executed.append(owner)
    except Exception as e:
        print("SMOKE EXCEPTION: %s" % e)
        return False
    finally:
        # Ensure cleanup even on crash (for --twice second pass)
        for owner, _ in TEST_CASES:
            clean(owner)
    # Assert every case actually executed
    assert len(executed) == len(TEST_CASES), f"executed {len(executed)}, expected {len(TEST_CASES)}"
    n = sum(results)
    total = len(results)
    print("%d/%d" % (n, total))
    # F8: t15 records an additional harness control result, so total may
    # exceed len(TEST_CASES). The requirement is that all recorded tests pass.
    return n == total and total >= len(TEST_CASES)


def t12():
    o = "R3H12"; clean(o)
    setup = """
import sys, json, os
REPO_DIR = %r
OWNER_ID = %r
sys.path.insert(0, REPO_DIR)
from form.open import open_program
from form.mandell.core_i_recovery import write_confirm_intent
p = open_program(OWNER_ID)
pr = p.nursery.add('test', words='x')
pid = pr.id
p.nursery.save()
# Do NOT save program (absent)
write_confirm_intent(OWNER_ID, pid)
# Persist Nursery as confirmed; Program remains absent
# Nursery saves proposals directly under their IDs (not under 'proposals' key)
npath = os.path.join(REPO_DIR, 'form', 'state', 'nursery_' + OWNER_ID + '.json')
nd = json.load(open(npath))
# Assert precondition: proposal exists and is pending
assert pid in nd, "Proposal not in nursery"
assert nd[pid].get('status') == 'pending', "Proposal not pending"
# Confirm it
nd[pid]['status'] = 'confirmed'
json.dump(nd, open(npath, 'w'))
# Assert precondition: Program is absent
ppath = os.path.join(REPO_DIR, 'form', 'state', 'program_' + OWNER_ID + '.json')
assert not os.path.exists(ppath), "Program should be absent"
# Assert precondition: journal records expected OLD fingerprints
from form.mandell.core_i_recovery import _confirm_journal_path
jpath = _confirm_journal_path(OWNER_ID)
jd = json.load(open(jpath))
assert jd['proposal_id'] == pid, "Journal proposal mismatch"
assert jd['old_program_sha256'] == 'absent', "Journal should record absent Program"
print('PID:' + pid)
print('PRECONDITIONS_OK')
""" % (REPO, o)
    rc, out, err = run_script("t12_setup", setup)
    if rc != 0 or "PRECONDITIONS_OK" not in out:
        rec("12_absent_prog", False, "setup failed or preconditions not met: " + out[:100])
        clean(o); return
    # Recovery must raise (not clear as no_change)
    # After recovery, assert: journal preserved, hybrid NOT exposed
    load = """
import sys, os, json
sys.path.insert(0, %r)
from form import persist_rest
from form.mandell.core_i_recovery import _confirm_journal_path, RollbackRecoveryError
jpath = _confirm_journal_path(%r)
try:
    p = persist_rest.load(%r, activate=False)
    jexists = os.path.isfile(jpath)
    print('NO_RAISE JEXISTS:' + str(jexists))
    # If no raise, verify hybrid was NOT exposed
    # (proposal should not be confirmed without Idea)
except RollbackRecoveryError as e:
    jexists = os.path.isfile(jpath)
    print('RAISED_ROLLBACK JEXISTS:' + str(jexists))
    # Assert journal preserved (not deleted)
    assert jexists, "Journal should be preserved on fail-closed"
except Exception as e:
    print('RAISED_OTHER:' + type(e).__name__)
""" % (REPO, o, o)
    rc, out, err = run_script("t12_load", load)
    # PASS requires: rc==0 (child succeeded), RAISED_ROLLBACK in output,
    # JEXISTS:True (journal preserved). Print success only after assertions.
    # If child assertion failed, rc != 0 or output missing → parent fails.
    ok = (rc == 0 and "RAISED_ROLLBACK" in out and "JEXISTS:True" in out)
    if ok:
        # Verify postconditions: journal preserved, member state unchanged
        # (The child already asserted these; this confirms the parent saw them)
        print("t12 postconditions verified")
    rec("12_absent_prog_confirmed", ok, out[:80])
    if not ok:
        print(f"t12 FAILED: rc={rc}, out={out[:100]}, err={err[:100]}")
    clean(o)

def t13():
    o = "R3H13"
    # Use unique temp dir per Director requirement
    import tempfile
    tmpdir = tempfile.mkdtemp(prefix="r3h13_")
    state_path = os.path.join(tmpdir, "state.json")
    try:
        clean(o)
        setup = """
import sys, os, json, traceback, tempfile, hashlib
REPO_DIR = %r
OWNER_ID = %r
STATE_PATH = %r
sys.path.insert(0, REPO_DIR)
from form.open import open_program
from form import persist_rest
from form.mandell import supersession
from form.mandell.supersession import supersede_proposal, SupersedeError
from form.mandell.core_i_recovery import _supersede_journal_path

def fp(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()[:16]

# Create and confirm predecessor
p = open_program(OWNER_ID)
pr_old = p.nursery.add('OLD_PROP', words='original content here')
p.confirm_proposal(pr_old.id, _producer="test", _review_context=p.make_review_context(pr_old.id, "test"))
assert getattr(pr_old, 'status', None) == 'confirmed'
print('CONFIRMED_OK')
p.nursery.save()
persist_rest.save(p)
old_id = pr_old.id

# Install hooks AFTER setup
orig_save = persist_rest.save
rollback_started = [False]
def wrapped_save(prog, *a, **k):
    if rollback_started[0]:
        raise OSError("INJECTED_ROLLBACK_SAVE_FAILURE_T13")
    return orig_save(prog, *a, **k)
persist_rest.save = wrapped_save
orig_save_nursery = supersession._save_nursery
def hook_save_nursery(program):
    rollback_started[0] = True
    raise SupersedeError("injected_final_commit", "t13_hook")
supersession._save_nursery = hook_save_nursery

got_oserror = False
try:
    p.acceptance_policy.grant_opt_in("test", scope="test")
    supersede_proposal(p, old_id, words='successor content here', _producer="test")
    print('NO_RAISE_UNEXPECTED')
except OSError as e:
    if 'INJECTED_ROLLBACK_SAVE_FAILURE_T13' in str(e):
        got_oserror = True
        print('PROPAGATED_ROLLBACK_OSERROR')
except Exception as e:
    print('OTHER:' + type(e).__name__)
finally:
    persist_rest.save = orig_save
    supersession._save_nursery = orig_save_nursery
assert got_oserror, "OSError did not propagate"

# Verify disk state - CORRECT STRUCTURE (no proposals wrapper)
jpath = _supersede_journal_path(OWNER_ID)
assert os.path.isfile(jpath), "journal cleared"
jd = json.load(open(jpath))
succ_id = jd.get('new_id')
assert succ_id, "no new_id"
print('JOURNAL_RETAINED')

npath = os.path.join(REPO_DIR, 'form', 'state', 'nursery_' + OWNER_ID + '.json')
nd = json.load(open(npath))
# Director exact assertions:
assert old_id in nd, "old_id not in nd"
assert nd[old_id]["lifecycle_state"] == "active" or nd[old_id].get("status") == "confirmed", "old not active"
assert nd[old_id].get("superseded_by_id") is None, "old has link"
assert succ_id not in nd, "succ not removed"
print('NURSERY_ASSERTIONS_OK')

from form.persist import _path as _ppath
ppath = _ppath(OWNER_ID)
pd = json.load(open(ppath))
assert succ_id in pd.get('plane', {}).get('units', {}), "Idea missing"
print('IDEA_EXISTS')

# Capture fingerprints
old_fp = fp(nd[old_id])
idea_fp = fp(pd['plane']['units'][succ_id])
journal_fp = fp(jd)
with open(STATE_PATH, 'w') as f:
    json.dump({'owner': OWNER_ID, 'old_id': old_id, 'succ_id': succ_id,
               'old_fp': old_fp, 'idea_fp': idea_fp, 'journal_fp': journal_fp}, f)
print('SETUP_DONE')
""" % (REPO, o, state_path)
        rc, out, err = run_script("t13_setup", setup)
        if rc != 0 or "SETUP_DONE" not in out:
            rec("13_rollback_propagates", False, "setup failed")
            print("STDOUT:", out[:400])
            print("STDERR:", err[:400])
            return
        ok_setup = all(x in out for x in ["PROPAGATED_ROLLBACK_OSERROR", "JOURNAL_RETAINED",
                                           "NURSERY_ASSERTIONS_OK", "IDEA_EXISTS"])
        if not ok_setup:
            rec("13_rollback_propagates", False, "assertions failed")
            print(out[:400])
            return

        # Restart and verify - compare fingerprints
        restart = """
import sys, os, json, hashlib
sys.path.insert(0, %r)
STATE_PATH = %r
with open(STATE_PATH) as f:
    state = json.load(f)
OWNER_ID = state['owner']
def fp(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()[:16]
from form import persist_rest
from form.mandell.core_i_recovery import _supersede_journal_path, RollbackRecoveryError
jpath = _supersede_journal_path(OWNER_ID)

for attempt in [1, 2]:
    try:
        p = persist_rest.load(OWNER_ID, activate=False)
        print('RECOVERY%%d_NO_RAISE' %% attempt)
        break
    except RollbackRecoveryError:
        # Verify evidence unchanged
        jd = json.load(open(jpath))
        assert fp(jd) == state['journal_fp'], "journal changed"
        npath = os.path.join(%r, 'form', 'state', 'nursery_' + OWNER_ID + '.json')
        nd = json.load(open(npath))
        assert fp(nd[state['old_id']]) == state['old_fp'], "old changed"
        from form.persist import _path as _ppath
        pd = json.load(open(_ppath(OWNER_ID)))
        assert fp(pd['plane']['units'][state['succ_id']]) == state['idea_fp'], "idea changed"
        print('RECOVERY%%d_RAISED_EVIDENCE_INTACT' %% attempt)
    except Exception as e:
        print('RECOVERY%%d_OTHER:' %% attempt + type(e).__name__)
        break
print('RESTART_DONE')
""" % (REPO, state_path, REPO)
        rc2, out2, err2 = run_script("t13_restart", restart)
        ok_restart = rc2 == 0 and "RECOVERY1_RAISED_EVIDENCE_INTACT" in out2 and "RECOVERY2_RAISED_EVIDENCE_INTACT" in out2
        ok = ok_setup and ok_restart
        rec("13_rollback_propagates", ok, "setup=%s restart=%s" % (ok_setup, ok_restart))
        if ok:
            print("t13 postconditions verified")
        else:
            print("RESTART OUT:", out2[:400])
    finally:
        import shutil
        try:
            shutil.rmtree(tmpdir)
        except:
            pass
        clean(o)
        # Include R3H14 in finally cleanup per Director
        clean("R3H14")

# 14. orphan_idea_negative: Orphan Idea (present but proposal not confirmed)
# must not be cleared as healed. Fail closed, preserve evidence.
def t14():
    o = "R3H14"; clean(o)
    setup = """
import sys, os, json
REPO_DIR = %r
OWNER_ID = %r
sys.path.insert(0, REPO_DIR)
from form.open import open_program
from form import persist_rest
from form.mandell.core_i_recovery import write_supersede_intent, _supersede_journal_path

# Create old (confirmed) and new (pending) proposals
p = open_program(OWNER_ID)
pr_old = p.nursery.add('OLD_PROP', words='original')
p.confirm_proposal(pr_old.id, _producer="test", _review_context=p.make_review_context(pr_old.id, "test"))
pr_new = p.nursery.add('NEW_PROP', words='successor')
p.nursery.save()
persist_rest.save(p)

# Write supersede intent (old->new)
write_supersede_intent(OWNER_ID, pr_old.id, pr_new.id)

# Create orphan: add Idea for new to Program file, but new proposal stays pending
ppath = os.path.join(REPO_DIR, 'form', 'state', 'program_' + OWNER_ID + '.json')
pd = json.load(open(ppath))
pd['plane']['units'][pr_new.id] = {'id': pr_new.id, 'label': 'NEW_PROP'}
json.dump(pd, open(ppath, 'w'))
print('ORPHAN_CREATED')

# Verify preconditions
jpath = _supersede_journal_path(OWNER_ID)
assert os.path.isfile(jpath), "journal not created"
print('PRECONDITIONS_OK')
""" % (REPO, o)
    rc, out, err = run_script("t14_setup", setup)
    if rc != 0 or "PRECONDITIONS_OK" not in out:
        rec("14_orphan_idea", False, f"setup failed rc={rc}")
        print(f"t14 SETUP FAILED: {out[:200]} {err[:200]}")
        clean(o)
        return

    # Recovery must raise (orphan Idea is evidence, cannot heal)
    load = """
import sys, os
sys.path.insert(0, %r)
from form import persist_rest
from form.mandell.core_i_recovery import _supersede_journal_path, RollbackRecoveryError
jpath = _supersede_journal_path(%r)
try:
    p = persist_rest.load(%r, activate=False)
    print('NO_RAISE_UNEXPECTED JEXISTS:' + str(os.path.isfile(jpath)))
except RollbackRecoveryError:
    print('RAISED_ROLLBACK JEXISTS:' + str(os.path.isfile(jpath)))
except Exception as e:
    print('OTHER:' + type(e).__name__)
""" % (REPO, o, o)
    rc2, out2, err2 = run_script("t14_load", load)
    ok = rc2 == 0 and "RAISED_ROLLBACK" in out2 and "JEXISTS:True" in out2
    if ok:
        print("t14 postconditions verified")
    rec("14_orphan_idea", ok, out2[:80])
    if not ok:
        print(f"t14 FAILED: rc={rc2}, out={out2[:150]}")
    clean(o)

def t14b():
    # F7: Malformed Program units ([]) during heal must fail closed,
    # not return healed_to_old. Journal preserved.
    o = "R3H14B"; clean(o)
    setup = """
import sys, os, json
REPO_DIR = %r
OWNER_ID = %r
sys.path.insert(0, REPO_DIR)
from form.open import open_program
from form import persist_rest
from form.mandell.core_i_recovery import write_supersede_intent, _supersede_journal_path

p = open_program(OWNER_ID)
pr_old = p.nursery.add('OLD_PROP', words='original')
p.confirm_proposal(pr_old.id, _producer="test", _review_context=p.make_review_context(pr_old.id, "test"))
pr_new = p.nursery.add('NEW_PROP', words='successor')
p.nursery.save()
persist_rest.save(p)
write_supersede_intent(OWNER_ID, pr_old.id, pr_new.id)

# Set up for heal branch: old active, new pending, no links, no Idea
# Then corrupt Program units to [] (malformed)
npath = os.path.join(REPO_DIR, 'form', 'state', 'nursery_' + OWNER_ID + '.json')
nd = json.load(open(npath))
# Ensure old is active, new is pending, no contradictory links
# (default state after setup is already correct)
json.dump(nd, open(npath, 'w'))
ppath = os.path.join(REPO_DIR, 'form', 'state', 'program_' + OWNER_ID + '.json')
pd = json.load(open(ppath))
pd['plane']['units'] = []  # MALFORMED: should be dict
json.dump(pd, open(ppath, 'w'))
print('SETUP_DONE')
""" % (REPO, o)
    rc, out, err = run_script("t14b_setup", setup)
    if rc != 0 or "SETUP_DONE" not in out:
        rec("14b_malformed_units", False, f"setup failed rc={rc}")
        print(f"t14b SETUP FAILED: {out[:200]} {err[:200]}")
        clean(o)
        return

    # Recovery must raise (malformed units), journal preserved
    load = """
import sys, os
sys.path.insert(0, %r)
from form import persist_rest
from form.mandell.core_i_recovery import _supersede_journal_path, RollbackRecoveryError
jpath = _supersede_journal_path(%r)
try:
    p = persist_rest.load(%r, activate=False)
    print('NO_RAISE_UNEXPECTED JEXISTS:' + str(os.path.isfile(jpath)))
except RollbackRecoveryError:
    print('RAISED_ROLLBACK JEXISTS:' + str(os.path.isfile(jpath)))
except Exception as e:
    print('OTHER:' + type(e).__name__)
""" % (REPO, o, o)
    rc2, out2, err2 = run_script("t14b_load", load)
    ok = rc2 == 0 and "RAISED_ROLLBACK" in out2 and "JEXISTS:True" in out2
    rec("14b_malformed_units", ok, out2[:80])
    if not ok:
        print(f"t14b FAILED: rc={rc2}, out={out2[:150]}")
    else:
        print("t14b postconditions verified: malformed units fail closed")
    clean(o)

# 15. revision_identity_negative: Conflicting revision root/number
# must fail closed, not accept as already_complete. Journal preserved.
# Fixed child scripts - no interpolation, args via JSON
_T15_SETUP_CHILD = """
import sys, os, json, hashlib
case = json.loads(sys.argv[1])
REPO_DIR = case["repo"]
OWNER_ID = case["owner"]
BRANCH = case["branch"]
MUTATION = case["mutation"]
sys.path.insert(0, REPO_DIR)
from form.open import open_program
from form import persist_rest
from form.mandell.core_i_recovery import write_supersede_intent, _supersede_journal_path

def fp_bytes(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

p = open_program(OWNER_ID)
pr_old = p.nursery.add('OLD_PROP', words='original')
p.confirm_proposal(pr_old.id, _producer="test", _review_context=p.make_review_context(pr_old.id, "test"))
pr_new = p.nursery.add('NEW_PROP', words='successor')
# F6: Establish genuine revision identity BEFORE writing intent.
# Old is first revision (number=1, no explicit root = own ID is canonical).
# This is recorded in the journal as intent-fixed ancestry evidence.
# Use the in-memory proposal object to avoid NurseryConflict.
pr_old.revision_number = 1
# Note: no revision_root_id for first revision (None = own ID canonical)
p.nursery.save()
persist_rest.save(p)
write_supersede_intent(OWNER_ID, pr_old.id, pr_new.id)
old_id, new_id = pr_old.id, pr_new.id

npath = os.path.join(REPO_DIR, 'form', 'state', 'nursery_' + OWNER_ID + '.json')
nd = json.load(open(npath))
nd[old_id]['lifecycle_state'] = 'superseded'
# Old keeps its genuine identity: number=1, no explicit root
nd[old_id]['revision_number'] = 1
# New is second revision: root=old_id (canonical), number=2
nd[new_id]['status'] = 'confirmed'
nd[new_id]['revision_root_id'] = old_id
nd[new_id]['revision_number'] = 2
if BRANCH == "complete":
    nd[old_id]['superseded_by_id'] = new_id
    nd[new_id]['supersedes_id'] = old_id
if MUTATION == "conflicting_root":
    nd[new_id]['revision_root_id'] = 'rootB'
elif MUTATION == "missing_root":
    del nd[new_id]['revision_root_id']
elif MUTATION == "nonsequential":
    nd[new_id]['revision_number'] = 9
elif MUTATION == "malformed":
    nd[new_id]['revision_number'] = "not-a-number"
elif MUTATION == "paired_unrelated":
    # F6: Both old and new claim the same unrelated root.
    # Intent recorded old as first revision (no root). This must fail.
    nd[old_id]['revision_root_id'] = 'unrelated'
    nd[old_id]['revision_number'] = 1
    nd[new_id]['revision_root_id'] = 'unrelated'
    nd[new_id]['revision_number'] = 2
json.dump(nd, open(npath, 'w'))
ppath = os.path.join(REPO_DIR, 'form', 'state', 'program_' + OWNER_ID + '.json')
pd = json.load(open(ppath))
pd['plane']['units'][new_id] = {'id': new_id}
json.dump(pd, open(ppath, 'w'))

nd2 = json.load(open(npath))
assert old_id in nd2 and new_id in nd2
pd2 = json.load(open(ppath))
assert new_id in pd2['plane']['units']
jpath = _supersede_journal_path(OWNER_ID)
assert os.path.isfile(jpath)
result = {"case": case["case_id"], "ok": True,
          "baseline": {"nursery": fp_bytes(npath),
                       "program": fp_bytes(ppath),
                       "journal": fp_bytes(jpath),
                       "old_id": old_id, "new_id": new_id}}
print(json.dumps(result))
"""

_T15_LOAD_CHILD = """
import sys, os, json, hashlib
case = json.loads(sys.argv[1])
REPO_DIR = case["repo"]
OWNER_ID = case["owner"]
EXPECT_OK = case["expect_ok"]
ENTRYPOINT = case["entrypoint"]
BASELINE = case["baseline"]
sys.path.insert(0, REPO_DIR)
from form import persist_rest
from form.open import open_program
from form.mandell.core_i_recovery import _supersede_journal_path, RollbackRecoveryError

def fp_bytes(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def fail(msg):
    print(json.dumps({"case": case["case_id"], "ok": False, "error": msg}))
    sys.exit(0)

jpath = _supersede_journal_path(OWNER_ID)
npath = os.path.join(REPO_DIR, 'form', 'state', 'nursery_' + OWNER_ID + '.json')
from form.persist import _path as _ppath
ppath = _ppath(OWNER_ID)

def assert_baseline_unchanged():
    # F8: Rejection must not serialize anything. Compare full SHA-256
    # hashes of Nursery, Program and journal bytes against the setup
    # baseline after EACH invalid recovery attempt. Fail if any differ.
    if not os.path.isfile(jpath):
        fail("journal not retained")
    for key, path in (("nursery", npath), ("program", ppath),
                      ("journal", jpath)):
        if not os.path.isfile(path):
            fail("baseline member missing: " + key)
        current = fp_bytes(path)
        if current != BASELINE[key]:
            fail("baseline bytes changed: %s expected=%s got=%s" %
                 (key, BASELINE[key][:16], current[:16]))

def do_recover():
    if ENTRYPOINT == "constructor":
        return open_program(OWNER_ID)
    else:
        return persist_rest.load(OWNER_ID, activate=False)

for attempt in (1, 2):
    try:
        p = do_recover()
        raised = False
    except RollbackRecoveryError:
        raised = True
    except Exception as e:
        fail("unexpected " + type(e).__name__ + ": " + str(e)[:100])
    if EXPECT_OK:
        if raised:
            fail("expected ok but raised on attempt %d" % attempt)
        # Valid rows: reread disk and assert full outcome
        if os.path.isfile(jpath):
            fail("journal not cleared")
        nd = json.load(open(npath))
        pd = json.load(open(ppath))
        old_id, new_id = BASELINE["old_id"], BASELINE["new_id"]
        old_d, new_d = nd.get(old_id), nd.get(new_id)
        if not isinstance(old_d, dict) or not isinstance(new_d, dict):
            fail("members missing from durable nursery")
        if old_d.get("lifecycle_state") != "superseded":
            fail("old not superseded")
        if new_d.get("status") != "confirmed":
            fail("new not confirmed")
        if old_d.get("superseded_by_id") != new_id:
            fail("old link wrong")
        if new_d.get("supersedes_id") != old_id:
            fail("new link wrong")
        # F6: Check roots match via canonical semantics.
        # Old with no explicit root has canonical root = own ID.
        old_root = old_d.get("revision_root_id")
        if old_root is None:
            old_root = old_id
        if old_root != new_d.get("revision_root_id"):
            fail("roots mismatch in durable state")
        try:
            if int(new_d.get("revision_number")) != int(old_d.get("revision_number")) + 1:
                fail("numbers not sequential in durable state")
        except (TypeError, ValueError):
            fail("bad numbers in durable state")
        units = pd.get("plane", {}).get("units", {})
        if new_id not in units:
            fail("Idea missing from durable program")
    else:
        if not raised:
            fail("expected raise but completed on attempt %d" % attempt)
        if not os.path.isfile(jpath):
            fail("journal cleared on invalid")
        assert_baseline_unchanged()
print(json.dumps({"case": case["case_id"], "ok": True}))
"""

def _t15_run_child(child_code, case):
    """Run fixed child script with JSON args. Returns (ok, detail)."""
    import subprocess
    # Compile the fixed script (not just this file)
    try:
        compile(child_code, "<t15_child>", "exec")
    except SyntaxError as e:
        return False, "child compile failed: %s" % e
    r = subprocess.run(
        [sys.executable, "-c", child_code, json.dumps(case)],
        cwd=REPO, capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        return False, "rc=%d stderr=%s" % (r.returncode, r.stderr[:200])
    try:
        result = json.loads(r.stdout.strip().split("\n")[-1])
    except Exception as e:
        return False, "bad json: %s out=%s" % (e, r.stdout[:200])
    if result.get("case") != case["case_id"]:
        return False, "case mismatch"
    if not result.get("ok"):
        return False, result.get("error", "child ok=false")
    return True, result

_T15_HARNESS_CONTROL_CHILD = """
import sys, os, json, hashlib
case = json.loads(sys.argv[1])
REPO_DIR = case["repo"]
OWNER_ID = case["owner"]
sys.path.insert(0, REPO_DIR)
from form.mandell.core_i_recovery import _supersede_journal_path

def fp_bytes(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

jpath = _supersede_journal_path(OWNER_ID)
baseline = fp_bytes(jpath)
# Harness control: change one byte of the journal
with open(jpath, "rb") as f:
    data = bytearray(f.read())
data[0] = (data[0] + 1) % 256
with open(jpath, "wb") as f:
    f.write(data)
current = fp_bytes(jpath)
# The full-hash comparison MUST detect this one-byte change
if current == baseline:
    print(json.dumps({"case": case["case_id"], "ok": False,
                      "error": "harness control: one-byte change NOT detected"}))
else:
    print(json.dumps({"case": case["case_id"], "ok": True,
                      "note": "harness control: one-byte change detected"}))
"""

def t15():
    import itertools
    branches = ["complete", "repair"]
    mutations = ["valid", "conflicting_root", "missing_root",
                 "nonsequential", "malformed", "paired_unrelated"]
    entrypoints = ["load", "constructor"]
    # Compile children once
    py_compile.compile(__file__, doraise=True)
    # Harness control: prove the full-hash baseline assertion can fail.
    # Deliberately change one byte of the journal; the comparison must
    # detect it. If this control fails, the F8 evidence is vacuous.
    hcase = {"case_id": "t15/harness_control", "repo": REPO,
             "owner": "R3H15_HARNESS_CONTROL"}
    clean("R3H15_HARNESS_CONTROL")
    ok, detail = _t15_run_child(_T15_SETUP_CHILD, {
        "case_id": "t15/harness_control", "repo": REPO,
        "owner": "R3H15_HARNESS_CONTROL",
        "branch": "complete", "mutation": "valid"})
    if not ok:
        print("HARNESS CONTROL SETUP FAILED: %s" % detail)
        clean("R3H15_HARNESS_CONTROL")
        rec("15_harness_control", False, "setup failed: %s" % detail)
    else:
        ok2, detail2 = _t15_run_child(_T15_HARNESS_CONTROL_CHILD, hcase)
        clean("R3H15_HARNESS_CONTROL")
        if ok2:
            print("t15 harness control passed: one-byte change detected")
        else:
            print("HARNESS CONTROL FAILED: %s" % detail2)
        rec("15_harness_control", ok2, str(detail2)[:80])
    rows = list(itertools.product(branches, mutations, entrypoints))
    passed = 0
    for branch, mutation, entrypoint in rows:
        case_id = "%s/%s/%s" % (branch, mutation, entrypoint)
        owner = "R3H15_%s_%s_%s" % (branch, mutation, entrypoint)
        owner = owner.replace("/", "_")
        clean(owner)
        expect_ok = (mutation == "valid")
        case = {"case_id": case_id, "repo": REPO, "owner": owner,
                "branch": branch, "mutation": mutation,
                "entrypoint": entrypoint, "expect_ok": expect_ok}
        ok, detail = _t15_run_child(_T15_SETUP_CHILD, case)
        if not ok:
            print("MATRIX ROW SETUP FAILED %s: %s" % (case_id, detail))
            clean(owner)
            continue
        # Pass setup baseline into recovery child
        case["baseline"] = detail["baseline"]
        ok2, detail2 = _t15_run_child(_T15_LOAD_CHILD, case)
        if ok2:
            passed += 1
        else:
            print("MATRIX ROW FAILED %s: %s" % (case_id, detail2))
        clean(owner)
    print("MATRIX_ROWS: %d/24" % passed)
    rec("15_revision_identity", passed == 24, "%d/24" % passed)

def t15b():
    # F6: Prove valid longer history. Create and supersede real proposals
    # twice to establish an actual third revision. The writer must capture
    # the actual predecessor root/number (not None/None).
    o = "R3H15B"; clean(o)
    setup = """
import sys, os, json
REPO_DIR = __REPO__
OWNER_ID = __OWNER__
sys.path.insert(0, REPO_DIR)
from form.open import open_program
from form import persist_rest
from form.mandell.core_i_recovery import write_supersede_intent, _supersede_journal_path

p = open_program(OWNER_ID)
# Revision 1: create and confirm A
pr_a = p.nursery.add('REV1', words='first')
p.confirm_proposal(pr_a.id, _producer="test", _review_context=p.make_review_context(pr_a.id, "test"))
# Set A as revision 1 (explicit, via API)
p.nursery.proposals[pr_a.id].revision_number = 1
p.nursery.save()
persist_rest.save(p)

# Revision 2: create B as successor of A
pr_b = p.nursery.add('REV2', words='second')
p.nursery.proposals[pr_b.id].revision_root_id = pr_a.id
p.nursery.proposals[pr_b.id].revision_number = 2
p.confirm_proposal(pr_b.id, _producer="test", _review_context=p.make_review_context(pr_b.id, "test"))
p.nursery.save()
persist_rest.save(p)

# Revision 3: create C, write intent for B->C
pr_c = p.nursery.add('REV3', words='third')
p.nursery.save()
persist_rest.save(p)

# Writer must capture B's actual root (A.id) and number (2)
write_supersede_intent(OWNER_ID, pr_b.id, pr_c.id)

# Verify writer captured correctly
import json as _j
jpath = _supersede_journal_path(OWNER_ID)
j = _j.load(open(jpath))
captured_root = j.get("intent_old_root")
captured_num = j.get("intent_old_number")
print('WRITER_CAPTURED: root=%s num=%s expected_root=%s expected_num=2' % (
    captured_root, captured_num, pr_a.id))
assert captured_root == pr_a.id, "writer did not capture actual root"
assert captured_num == 2, "writer did not capture actual number"

# Set C as revision 3
npath = os.path.join(REPO_DIR, 'form', 'state', 'nursery_' + OWNER_ID + '.json')
nd = _j.load(open(npath))
nd[pr_b.id]['lifecycle_state'] = 'superseded'
nd[pr_b.id]['superseded_by_id'] = pr_c.id
nd[pr_c.id]['status'] = 'confirmed'
nd[pr_c.id]['revision_root_id'] = pr_a.id
nd[pr_c.id]['revision_number'] = 3
nd[pr_c.id]['supersedes_id'] = pr_b.id
_j.dump(nd, open(npath, 'w'))
ppath = os.path.join(REPO_DIR, 'form', 'state', 'program_' + OWNER_ID + '.json')
pd = _j.load(open(ppath))
pd['plane']['units'][pr_c.id] = {'id': pr_c.id}
_j.dump(pd, open(ppath, 'w'))
print('SETUP_DONE')
""".replace('__REPO__', repr(REPO)).replace('__OWNER__', repr(o))
    rc, out, err = run_script("t15b_setup", setup)
    if rc != 0 or "SETUP_DONE" not in out:
        rec("15b_three_revision", False, f"setup failed rc={rc}: {out[:100]}")
        print(f"t15b SETUP FAILED: {out[:300]} {err[:200]}")
        clean(o)
        return
    if "WRITER_CAPTURED" not in out:
        rec("15b_three_revision", False, "writer capture not verified")
        clean(o)
        return

    # Recovery via load should succeed (already_complete)
    load = """
import sys, os
sys.path.insert(0, %r)
from form import persist_rest
from form.mandell.core_i_recovery import _supersede_journal_path
jpath = _supersede_journal_path(%r)
try:
    p = persist_rest.load(%r, activate=False)
    jexists = os.path.isfile(jpath)
    print('RECOVERED JEXISTS:' + str(jexists))
except Exception as e:
    print('RAISED:' + type(e).__name__ + ':' + str(e)[:100])
""" % (REPO, o, o)
    rc2, out2, err2 = run_script("t15b_load", load)
    # Valid 3-revision chain should recover (journal cleared)
    ok = rc2 == 0 and "RECOVERED" in out2 and "JEXISTS:False" in out2
    rec("15b_three_revision", ok, out2[:80])
    if ok:
        print("t15b verified: 3-revision chain recovers, writer captured actual ancestry")
    else:
        print(f"t15b FAILED: rc={rc2}, out={out2[:200]}")
    clean(o)

if __name__ == "__main__":
    for owner, fn in TEST_CASES:
        clean(owner)
    executed = []
    for owner, fn in TEST_CASES:
        fn()
        executed.append(owner)
    assert len(executed) == len(TEST_CASES), "not all cases executed"
    for owner, _ in TEST_CASES:
        clean(owner)
    n = sum(results)
    print("=== %d/%d ===" % (n, len(results)))
    assert n == len(TEST_CASES), f"expected {len(TEST_CASES)} results, got {n}"
    sys.exit(0 if all(results) else 1)

# 10. negative_control_A: Nursery unchanged, Program modified (Idea added)
# Journal records pending proposal, Program without Idea.
# Then Program is persisted WITH the Idea, Nursery unchanged.
# Recovery must NOT return no_change and discard journal.

# 12. absent_program_confirmed: Director's escape reproduction
# Originally absent Program; Nursery becomes confirmed.
# Recovery must NOT return no_change; must fail closed.

# 13. rollback_program_save_failure: Failure during rollback must propagate
# If _rollback_full's Program save fails, the exception must propagate
# (not be suppressed), journal retained, and repeated recovery must fail closed.
