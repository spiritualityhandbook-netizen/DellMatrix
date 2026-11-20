#!/usr/bin/env python3
"""C12 Bridge — failing-first (Part I, MWL #164-#166, GP-E17).

Contracts (Unified Edition §14.3 C12 cards):
- #164 C12.Ledger (DD-34): the Bridge ledger — the ledger of all
  bridges: reports dock/Exchange facts without taking over their
  state.
- #165 C12.ExchangeDoor: local Exchange export/import door —
  preview binds to payload; imports stay PENDING at the human gate.
- #166 C12.RoomBridge: preview/transfer between rooms, only after
  C3 room semantics (#134) are settled; never a silent move.

STATUS: FAILING-FIRST. The control (a plain Exchange import
roundtrip) passes today — the Exchange engine exists (and its
recovery transaction is the Q1 C-B prep subject, separately gated).
The C12 DOOR and LEDGER surfaces fail as absent. NO product code
is changed by this file. Row #166's build is sequenced after #134
inside Part I (named in-Part dependency).
"""
from __future__ import annotations

import glob
import os
import shutil
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from form.open import open_program

OWNER = "C12BRIDGE1112"


def _cleanup(owner):
    state = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state")
    for f in glob.glob(os.path.join(state, f"*{owner}*")):
        try:
            if os.path.isdir(f):
                shutil.rmtree(f)
            else:
                os.remove(f)
        except FileNotFoundError:
            pass
        except OSError as e:
            raise RuntimeError(f"cleanup failed for {f}: {e}")


def smoke() -> bool:
    print("=== C12 BRIDGE (FAILING-FIRST) ===")
    fails = []

    def check(name, cond, detail=""):
        print(f"[{'PASS' if cond else 'FAIL'}] {name}"
              + (f" :: {detail}" if detail else ""))
        if not cond:
            fails.append(name)

    _cleanup(OWNER)
    p = open_program(OWNER)

    # CONTROL — the Exchange engine imports a well-formed packet
    # and the proposal lands PENDING (human gate intact).
    from form.dell_matrix import exchange
    packet = {
        "version": 1,
        "seed": {"label": "c12-door-label", "chain": "chain-c12",
                 "keep": "C12-KEEP"},
        "manifest": {"author_origin": "c12:origin",
                     "created": "2026-11-20T00:00:00Z",
                     "registry": "core1:00-50,core2:51-99",
                     "requirements": ["req-c12"]},
        "receipts": [
            {"origin": "c12:org", "guess": "g0", "test_method": "m",
             "result": "r", "mirror": "mi", "outcome": "o"}],
    }
    try:
        res = exchange.import_packet(p, packet)
        imp_ok = isinstance(res, dict) and res.get("ok") is True
        detail = f"import result ok={res.get('ok') if isinstance(res, dict) else res!r}"
    except Exception as e:
        imp_ok = False
        detail = f"import raised {type(e).__name__}: {e}"
    check("CONTROL exchange.import_packet lands a packet ok=True",
          imp_ok, detail)

    # #165a — an EXPORT door: a local export producing a packet
    # from live state (the door's other half).
    export_surface = [n for n in dir(exchange)
                      if n.lower().startswith(("export", "preview"))]
    check("#165 Exchange export/preview door exists",
          bool(export_surface),
          f"exchange export/preview symbols={export_surface or 'none'} "
          f"(import exists; no export door, no preview)")

    # #165b — preview binds to payload: a preview receipt whose
    # identity (hash) is computed from the exact payload bytes, so
    # what was previewed is what imports. No preview surface today
    # (see #165a); this check pins the binding half of the contract.
    check("#165 preview binds to payload (preview identity == "
          "payload identity)", bool(export_surface) and False,
          "no preview surface to bind (see #165 export check)")

    # #164 — the Bridge ledger: one ledger reporting bridge facts
    # (dock + Exchange) without owning their state.
    ledger_mod = None
    for modname in ("form.dell_matrix.bridge_ledger",
                    "form.dell_matrix.bridge"):
        try:
            ledger_mod = __import__(modname, fromlist=["x"])
        except ImportError:
            pass
    ledger_surface = [n for n in dir(exchange) if "ledger" in n.lower()]
    check("#164 Bridge ledger surface exists",
          ledger_mod is not None or bool(ledger_surface),
          f"bridge ledger module={'present' if ledger_mod else 'ABSENT'}; "
          f"exchange ledger symbols={ledger_surface or 'none'}")

    # #166 — room-to-room bridge: preview/transfer between rooms.
    rb_surface = [n for n in dir(p)
                  if "room" in n.lower() and ("bridge" in n.lower()
                                              or "transfer" in n.lower())]
    check("#166 room-to-room bridge surface exists",
          bool(rb_surface),
          f"Program room-bridge symbols={rb_surface or 'none'} "
          f"(also sequenced after #134 room semantics)")

    total = 5
    print(f"C12 BRIDGE LEDGER: {total - len(fails)}/{total} checks passed"
          + (f"; FAILING: {fails}" if fails else ""))
    _cleanup(OWNER)
    return not fails


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
