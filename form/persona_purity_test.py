#!/usr/bin/env python3
"""Q-OD.2 hygiene circuit — persona status readers must be
observationally pure, and every persona_lens writer must keep
PersonaMatrix.active in sync at write time.

Authorization: Director 6924026251 (2026-11-16) — Q-OD.2 bounded
FIX-FIRST hygiene circuit: (1) synchronize the live_visual.py
`bimo pilot` writer, (2) make both persona status readers
observationally pure; failing-first tests, caller audit, suites,
regression, exact-head CI. Keeper independently checks.

Defect (verified in main bef63b8a, grounding qod2_ground.md):
- Program.persona_matrix_status() and persona_matrix_ascii()
  ASSIGN `self.persona_matrix.active = self.persona_lens` on read
  (form/open.py) — a write-on-read that personas_status() and
  Program.status() inherit transitively. Instruments that route
  through status() silently perturb the measured system
  (sentinel-pinned by c7profile_test t3 / c7schema_test t7, which
  must route AROUND status() today).
- The live_visual `bimo pilot` handler is the sole writer that
  sets persona_lens WITHOUT syncing persona_matrix.active; its
  display path only looked correct because the impure reader
  lazily synced on the next read. Purifying the readers without
  syncing this writer would leave the Studio matrix display
  stale — the two halves of this circuit are one repair.

Contract pinned here:
- t1/t2/t3: status / ascii / personas_status / Program.status()
  leave persona_matrix.active byte-identical (sentinel survives).
- t4: the live_visual `bimo pilot` command syncs BOTH
  persona_lens and persona_matrix.active to the pilot.
- t5: control — set_persona_lens keeps its existing sync
  (the repair must not break the writers that were correct).
- t6: set_persona_lens with an UNRECOGNIZED persona clears
  persona_matrix.active — the writer syncs in every branch
  (Codex finding on PR #462: the fallback branch previously
  left the previous persona highlighted indefinitely once the
  readers stopped lazily syncing on read).
"""
from __future__ import annotations

import glob
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from form.open import open_program

STATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state")
SENTINEL = "SENTINEL_UNTOUCHED"


def _cleanup(owner):
    import shutil
    for f in glob.glob(os.path.join(STATE_DIR, f"*{owner}*")):
        try:
            if os.path.isdir(f):
                shutil.rmtree(f)
            else:
                os.remove(f)
        except FileNotFoundError:
            pass
        except OSError as e:
            raise RuntimeError(f"cleanup failed for {f}: {e}")


def _program(owner):
    _cleanup(owner)
    return open_program(owner)


def smoke() -> bool:
    print("=== Q-OD.2 PERSONA PURITY ===")
    r = []

    def rec(name, ok, detail=""):
        print(f"[{'PASS' if ok else 'FAIL'}] {name}"
              + (f" | {detail}" if detail and not ok else ""))
        r.append(bool(ok))

    # -- t1: persona_matrix_status() is a pure read.
    p = _program("QOD2PurityT1")
    p.persona_lens = "manny"
    p.persona_matrix.active = SENTINEL
    p.persona_matrix_status()
    rec("t1_status_pure", p.persona_matrix.active == SENTINEL,
        f"active={p.persona_matrix.active!r} lens={p.persona_lens!r}")
    _cleanup("QOD2PurityT1")

    # -- t2: persona_matrix_ascii() is a pure read.
    p = _program("QOD2PurityT2")
    p.persona_lens = "manny"
    p.persona_matrix.active = SENTINEL
    p.persona_matrix_ascii()
    rec("t2_ascii_pure", p.persona_matrix.active == SENTINEL,
        f"active={p.persona_matrix.active!r} lens={p.persona_lens!r}")
    _cleanup("QOD2PurityT2")

    # -- t3: transitive readers (personas_status, Program.status)
    #       are pure too.
    p = _program("QOD2PurityT3")
    p.persona_lens = "manny"
    p.persona_matrix.active = SENTINEL
    p.personas_status()
    mid = p.persona_matrix.active
    p.status()
    rec("t3_transitive_pure",
        mid == SENTINEL and p.persona_matrix.active == SENTINEL,
        f"after personas_status={mid!r} after status={p.persona_matrix.active!r}")
    _cleanup("QOD2PurityT3")

    # -- t4: live_visual `bimo pilot` writer syncs lens + active.
    #       Calls the UX handler directly: the full _run_command
    #       path builds a state payload that routes through
    #       persona_matrix_status(), whose write-on-read masks
    #       this writer's missing sync (the de-facto lazy sync
    #       named in the grounding). The handler branch itself
    #       is the writer under test.
    from form.dell_matrix import live_visual as _lv
    p = _program("QOD2PurityT4")
    p.persona_lens = None
    p.persona_matrix.active = None
    out = _lv._handle_ux_command(p, "bimo pilot manny",
                                 "bimo pilot manny") or {}
    pilot = (out.get("result") or {}).get("pilot")
    rec("t4_bimo_pilot_writer_syncs",
        bool(out.get("ok")) and p.persona_lens == pilot
        and p.persona_matrix.active == pilot and pilot is not None,
        f"ok={out.get('ok')} pilot={pilot!r} lens={p.persona_lens!r} "
        f"active={p.persona_matrix.active!r}")
    _cleanup("QOD2PurityT4")

    # -- t5: control — set_persona_lens sync is intact.
    p = _program("QOD2PurityT5")
    p.set_persona_lens("manny")
    sync_ok = p.persona_matrix.active == p.persona_lens and p.persona_lens
    p.set_persona_lens("clear")
    clear_ok = p.persona_lens is None and p.persona_matrix.active is None
    rec("t5_set_persona_lens_sync_intact", bool(sync_ok and clear_ok),
        f"lens={p.persona_lens!r} active={p.persona_matrix.active!r}")
    _cleanup("QOD2PurityT5")

    # -- t6: the setter's unrecognized-persona branch syncs too:
    #       valid persona, then an unknown name — the matrix must
    #       not keep highlighting the previous persona.
    p = _program("QOD2PurityT6")
    p.set_persona_lens("manny")
    p.set_persona_lens("unknown-persona")
    status_active = p.personas_status().get("active")
    rec("t6_setter_fallback_branch_syncs",
        p.persona_matrix.active is None and status_active is None,
        f"lens={p.persona_lens!r} active={p.persona_matrix.active!r} "
        f"status_active={status_active!r}")
    _cleanup("QOD2PurityT6")

    ok = all(r) and len(r) == 6
    print(f"PERSONA PURITY: {'GREEN' if ok else 'RED'} ({sum(r)}/6)")
    return ok


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
