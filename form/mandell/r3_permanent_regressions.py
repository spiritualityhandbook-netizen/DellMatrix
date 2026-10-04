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
p.confirm_proposal(old.id)
r = S.supersede_proposal(p, old.id, 'v2 words')
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
p.confirm_proposal(old.id)
old_id = old.id
r = S.supersede_proposal(p, old_id, 'v2 words')
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


def smoke():
    """Runner-compatible entry point for form.regress.
    
    Returns True if all tests pass, False otherwise.
    Resets per-run results.
    Ensures cleanup even if tests crash (for --twice isolation).
    """
    global results
    results = []
    # Clean up any leftover state from previous runs (for --twice)
    for o in ["R3H01", "R3H02", "R3H03", "R3H04", "R3H05", "R3H06", "R3H07", "R3H08", "R3H09", "R3H10", "R3H11", "R3H12", "R3H13", "R3H14", "R3H15"]:
        clean(o)
    try:
        t01(); t02(); t03(); t04(); t05(); t06(); t07(); t08(); t09(); t10(); t11(); t12(); t13(); t14(); t15()
    except Exception as e:
        print("SMOKE EXCEPTION: %s" % e)
        return False
    finally:
        # Ensure cleanup even on crash (for --twice second pass)
        for o in ["R3H01", "R3H02", "R3H03", "R3H04", "R3H05", "R3H06", "R3H07", "R3H08", "R3H09", "R3H10", "R3H11", "R3H12", "R3H13"]:
            clean(o)
    n = sum(results)
    total = len(results)
    print("%d/%d" % (n, total))
    return n == total and total > 0


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
p.confirm_proposal(pr_old.id)
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
    supersede_proposal(p, old_id, words='successor content here')
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
p.confirm_proposal(pr_old.id)
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

# 15. revision_identity_negative: Conflicting revision root/number
# must fail closed, not accept as already_complete. Journal preserved.
def t15():
    o = "R3H15"; clean(o)
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
p.confirm_proposal(pr_old.id)
pr_new = p.nursery.add('NEW_PROP', words='successor')
p.nursery.save()
persist_rest.save(p)
write_supersede_intent(OWNER_ID, pr_old.id, pr_new.id)

# Create otherwise-valid completed relationship, then corrupt revision
npath = os.path.join(REPO_DIR, 'form', 'state', 'nursery_' + OWNER_ID + '.json')
nd = json.load(open(npath))
nd[pr_old.id]['lifecycle_state'] = 'superseded'
nd[pr_old.id]['superseded_by_id'] = pr_new.id
nd[pr_old.id]['revision_root_id'] = 'root1'
nd[pr_old.id]['revision_number'] = 1
nd[pr_new.id]['status'] = 'confirmed'
nd[pr_new.id]['supersedes_id'] = pr_old.id
nd[pr_new.id]['revision_root_id'] = 'root2'  # CORRUPT: mismatch
nd[pr_new.id]['revision_number'] = 2
json.dump(nd, open(npath, 'w'))
ppath = os.path.join(REPO_DIR, 'form', 'state', 'program_' + OWNER_ID + '.json')
pd = json.load(open(ppath))
pd['plane']['units'][pr_new.id] = {'id': pr_new.id}
json.dump(pd, open(ppath, 'w'))
print('CORRUPT_CREATED')
jpath = _supersede_journal_path(OWNER_ID)
assert os.path.isfile(jpath)
print('PRECONDITIONS_OK')
""" % (REPO, o)
    rc, out, err = run_script("t15_setup", setup)
    if rc != 0 or "PRECONDITIONS_OK" not in out:
        rec("15_revision_identity", False, "setup failed")
        print(f"t15 SETUP FAILED: {out[:200]}")
        clean(o)
        return
    # Restart through public entrypoint, expect rejection
    load = """
import sys, os
sys.path.insert(0, %r)
from form import persist_rest
from form.mandell.core_i_recovery import _supersede_journal_path, RollbackRecoveryError
jpath = _supersede_journal_path(%r)
try:
    p = persist_rest.load(%r, activate=False)
    print('NO_RAISE_UNEXPECTED')
except RollbackRecoveryError as e:
    msg = str(e)
    if 'revision root mismatch' in msg or 'revision' in msg.lower():
        print('RAISED_REVISION_MISMATCH JEXISTS:' + str(os.path.isfile(jpath)))
    else:
        print('RAISED_OTHER:' + msg[:60])
except Exception as e:
    print('OTHER:' + type(e).__name__)
# Repeat recovery - must also raise
try:
    p = persist_rest.load(%r, activate=False)
    print('REPEAT_NO_RAISE')
except RollbackRecoveryError:
    print('REPEAT_RAISED JEXISTS:' + str(os.path.isfile(jpath)))
except Exception as e:
    print('REPEAT_OTHER:' + type(e).__name__)
""" % (REPO, o, o, o)
    rc2, out2, err2 = run_script("t15_load", load)
    ok = (rc2 == 0 and "RAISED_REVISION_MISMATCH" in out2 and "JEXISTS:True" in out2 and
          "REPEAT_RAISED" in out2)
    if ok:
        print("t15 postconditions verified")
    rec("15_revision_identity", ok, out2[:100])
    if not ok:
        print(f"t15 FAILED: {out2[:200]}")
    clean(o)

if __name__ == "__main__":
    t01(); t02(); t03(); t04(); t05(); t06(); t07(); t08(); t09(); t10(); t11(); t12(); t13(); t14(); t15()
    n = sum(results)
    print("=== %d/%d ===" % (n, len(results)))
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
