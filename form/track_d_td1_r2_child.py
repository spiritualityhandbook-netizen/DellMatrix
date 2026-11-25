"""TD-1-R2 child runner — one genuine OS process in the race.

Spawned by form/track_d_td1_r2_test.py via
`python3 -m form.track_d_td1_r2_child ...`. Modes:

  bind: load the owner's program (stamped), signal readiness,
        wait for the barrier file, then bind one unit and record
        the outcome as JSON.
  hold: acquire the owner-state lock, signal readiness, then
        sleep — the parent either lets it exit or SIGKILLs it to
        prove kernel lock recovery.

Coordination is by files with bounded polls; no fixed sleeps are
used as synchronization on the parent side.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time


def _wait_for(path: str, timeout: float = 30.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if os.path.isfile(path):
            return True
        time.sleep(0.01)
    return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["bind", "hold"], required=True)
    ap.add_argument("--owner", required=True)
    ap.add_argument("--unit", default="")
    ap.add_argument("--subject", default="Racer")
    ap.add_argument("--ready", required=True)
    ap.add_argument("--barrier", default="")
    ap.add_argument("--result", default="")
    ap.add_argument("--sleep", type=float, default=30.0)
    args = ap.parse_args()

    if args.mode == "hold":
        from form.owner_state_lock import owner_state_lock
        with owner_state_lock(args.owner):
            with open(args.ready, "w") as f:
                f.write("held")
            time.sleep(args.sleep)
        return 0

    from form import persist_rest
    from form.mandell import unit_binding
    prog = persist_rest.load(args.owner, activate=False)
    with open(args.ready, "w") as f:
        f.write("ready")
    if args.barrier and not _wait_for(args.barrier):
        outcome = {"outcome": "barrier_timeout"}
    else:
        try:
            receipt = prog.bind_unit_to_idea(args.unit,
                                             subject=args.subject)
            outcome = {"outcome": receipt["status"],
                       "idea_id": receipt["idea_id"]}
        except unit_binding.BindingRefused as e:
            outcome = {"outcome": "refused", "kind": e.kind}
        except unit_binding.BindingFailed as e:
            outcome = {"outcome": "failed",
                       "orphan": e.orphan_idea_id}
    if args.result:
        with open(args.result, "w") as f:
            json.dump(outcome, f)
    return 0


if __name__ == "__main__":
    sys.exit(main())
