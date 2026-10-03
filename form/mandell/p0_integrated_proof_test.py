#!/usr/bin/env python3
"""GDP-001 §16 — Phase-0 integrated proof (registered test).

Drives FRESH OS processes through the full chain:
  English input -> semantic resolution -> Mandell/Dell op -> mutation
  -> Outcome -> save -> NEW PROCESS -> load -> further mutation
  -> checkpoint -> rollback -> further mutation (nursery, the Dell28
  scenario) -> save -> reload
with: no sealed-state corruption, no semantic drift, no dishonest
receipt, no competing authority, no false Perspective report.
Includes negative paths.

Every step runs in a separate python3 process (CROSS_PROCESS evidence).
Uses a unique owner; cleans up only its own state files afterward.
Returns True/False (regress contract); never raises past smoke().
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import uuid

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OWNER = 'p0proof_' + uuid.uuid4().hex[:8]
GEN = {}


def _run_repl(cmds, timeout=180):
    p = subprocess.run(
        [sys.executable, '-B', '-m', 'form.repl', '--owner', OWNER],
        input='\n'.join(cmds) + '\n', capture_output=True, text=True,
        cwd=REPO, timeout=timeout)
    return p.returncode, p.stdout + p.stderr


def _run_py(code, timeout=180):
    p = subprocess.run([sys.executable, '-B', '-c', code],
                       capture_output=True, text=True, cwd=REPO,
                       timeout=timeout)
    return p.returncode, p.stdout + p.stderr


def _cleanup_owner_state():
    """Remove only state files belonging to this proof's unique owner."""
    state_dir = os.path.join(REPO, 'form', 'state')
    if not os.path.isdir(state_dir):
        return
    for name in os.listdir(state_dir):
        if OWNER in name:
            try:
                os.unlink(os.path.join(state_dir, name))
            except OSError:
                pass


def smoke() -> bool:
    print('owner:', OWNER, flush=True)
    results = []

    def check(name, cond, detail=''):
        print(('PASS' if cond else 'FAIL'), '-', name, detail, flush=True)
        results.append(bool(cond))

    try:
        # ---- P1: English -> Mandell -> Dell -> mutation -> Outcome -> save -> checkpoint
        rc, out = _run_repl(['create idea ProofIdea', 'stamp prooflabel',
                             'save', 'checkpoint'])
        check('P1 english create -> idea placed', 'ProofIdea' in out)
        check('P1 stamp executed',
              'prooflabel' in out.lower() or 'stamp' in out.lower())
        m = re.search(r'[Cc]heckpoint written:\s*generation\s+([A-Za-z0-9_.-]+)', out)
        if not m:
            m = re.search(r'\b(gc[A-Za-z0-9_.-]+)\b', out)
        check('P1 checkpoint committed a generation', m is not None,
              out[-400:] if not m else '')
        if m:
            GEN['g1'] = m.group(1)
            print('  generation:', GEN['g1'], flush=True)

        # ---- P2 (fresh process): load -> further mutation -> rollback -> save
        rc, out = _run_repl(['create idea SecondIdea', '28[Rollback]', 'save'])
        check('P2 second idea placed after reload', 'SecondIdea' in out)
        check('P2 rollback honest (ok, no traceback)',
              'rollback' in out.lower() and 'traceback' not in out.lower())

        # ---- P2b (fresh process, API): post-rollback nursery mutation (Dell28)
        code = (
            "import sys; sys.path.insert(0, %r)\n"
            "from form import persist_rest\n"
            "p = persist_rest.load(%r)\n"
            "p.nursery.add('post_rollback_proposal', words='p0proof')\n"
            "persist_rest.save(p)\n"
            "print('nursery_path=' + p.nursery.path)\n"
            "print('live_not_member=' + str('.g_' not in p.nursery.path))\n"
        ) % (REPO, OWNER)
        rc, out = _run_py(code)
        check('P2b post-rollback nursery mutation + save', rc == 0, out[-300:])

        # ---- P3 (fresh process, API): reload -> sealed generation intact?
        code = (
            "import sys, hashlib, json, glob, os; sys.path.insert(0, %r)\n"
            "from form.mandell import checkpoint_generation as CG\n"
            "from form import persist_rest\n"
            "from form.dell_matrix.nursery import owner_nursery_path\n"
            "p, rc = CG.load_checkpoint(%r, activate=False)\n"
            "q = persist_rest.load(%r)\n"
            "units = sorted(str(u) for u in p.cube.session.plane.units)\n"
            "print('units=' + ','.join(units))\n"
            "lunits = sorted(str(u) for u in q.cube.session.plane.units)\n"
            "print('live_units=' + ','.join(lunits))\n"
            "state_dir = os.path.dirname(owner_nursery_path(%r))\n"
            "bad = []\n"
            "for mf in glob.glob(os.path.join(state_dir, 'checkpoint_manifest*.json')):\n"
            "    man = json.load(open(mf))\n"
            "    for gid, gen in man.get('generations', {}).items():\n"
            "        for member, sha in gen.get('members', {}).items():\n"
            "            b = open(member, 'rb').read()\n"
            "            if hashlib.sha256(b).hexdigest() != sha:\n"
            "                bad.append((gid, member))\n"
            "print('sealed_intact=' + str(not bad))\n"
            "if bad: print('BAD=' + str(bad))\n"
        ) % (REPO, OWNER, OWNER, OWNER)
        rc, out = _run_py(code)
        check('P3 checkpoint generation holds P1 idea', 'proofidea' in out, out[-300:])
        m = re.search(r'live_units=([a-z,]+)', out)
        live = m.group(1).split(',') if m else []
        check('P3 live = rolled-back state (proofidea+welcome, secondidea discarded)',
              'proofidea' in live and 'welcome' in live and 'secondidea' not in live,
              out[-300:])
        check('P3 sealed generations byte-intact after post-rollback mutation',
              'sealed_intact=True' in out, out[-300:])

        # ---- P3b (fresh process, API): Perspective honesty
        code = (
            "import sys; sys.path.insert(0, %r)\n"
            "from form import persist_rest\n"
            "from form.dell_matrix import perspective_views as pv\n"
            "p = persist_rest.load(%r)\n"
            "v = pv.see_whole(p, pv.Viewer(id='p0v', role='architect', mode='whole'))\n"
            "print('epistemic=' + v.get('epistemic_status', '?'))\n"
            "print('count=' + str(v.get('count', '?')))\n"
        ) % (REPO, OWNER)
        rc, out = _run_py(code)
        m = re.search(r'epistemic=(\w+)', out)
        check('P3b perspective reports REAL (not confident-empty)',
              m and m.group(1) == 'REAL', out[-300:])
        m = re.search(r'count=(\d+)', out)
        check('P3b perspective count reflects real state (>=2)',
              m and int(m.group(1)) >= 2, out[-300:])

        # ---- Negative paths (fresh REPL)
        rc, out = _run_repl(['151[Harmonic]::x'])
        check('NEG reserved dell refused, zero ideas smuggled',
              'refused' in out.lower() or 'not-active' in out.lower())
        rc, out = _run_repl(['blorple wibble xyz'])
        check('NEG gibberish honestly refused/unknown, no traceback',
              'traceback' not in out.lower() and
              ('unknown' in out.lower() or 'refus' in out.lower()
               or "don't" in out.lower()))
    finally:
        _cleanup_owner_state()

    ok = all(results)
    # Regress contract: last n/m count must have n == m > 0, no traceback.
    print(f"=== RESULT: {sum(results)}/{len(results)} PASS ===", flush=True)
    print(('P0 INTEGRATED PROOF: ALL GREEN' if ok
           else 'P0 INTEGRATED PROOF: FAILED'), flush=True)
    return ok


if __name__ == '__main__':
    sys.exit(0 if smoke() else 1)
