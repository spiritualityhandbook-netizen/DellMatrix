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
    for o in ["R3H01", "R3H02", "R3H03", "R3H04", "R3H05", "R3H06", "R3H07", "R3H08", "R3H09", "R3H10", "R3H11"]:
        clean(o)
    try:
        t01(); t02(); t03(); t04(); t05(); t06(); t07(); t08(); t09(); t10(); t11()
    except Exception as e:
        print("SMOKE EXCEPTION: %s" % e)
        return False
    finally:
        # Ensure cleanup even on crash (for --twice second pass)
        for o in ["R3H01", "R3H02", "R3H03", "R3H04", "R3H05", "R3H06", "R3H07", "R3H08", "R3H09", "R3H10", "R3H11"]:
            clean(o)
    n = sum(results)
    total = len(results)
    print("%d/%d" % (n, total))
    return n == total and total > 0


if __name__ == "__main__":
    t01(); t02(); t03(); t04(); t05(); t06(); t07(); t08(); t09(); t10(); t11()
    n = sum(results)
    print("=== %d/%d ===" % (n, len(results)))
    sys.exit(0 if all(results) else 1)

# 10. negative_control_A: Nursery unchanged, Program modified (Idea added)
# Journal records pending proposal, Program without Idea.
# Then Program is persisted WITH the Idea, Nursery unchanged.
# Recovery must NOT return no_change and discard journal.
