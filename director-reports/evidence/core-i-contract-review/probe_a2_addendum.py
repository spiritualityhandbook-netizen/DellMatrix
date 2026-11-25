"""Probe A2 — addendum resolving probe A's open items.

1. Dell 27: the census DIFFERS was a random generation id inside a
   message string. Re-run with generation-id text normalization.
2. Dell 27: search the owner's persisted files after a typed run —
   where (if anywhere) do the arg name/value land?
3. Dell 44: label-driven capability witness (last_core_i).
4. Dell 21: positive path (two sources in one label), bare vs typed.
"""
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.expanduser("~/workspace/nbd-omega-corei"))
os.chdir(os.path.expanduser("~/workspace/nbd-omega-corei"))

from probe_lib import STATE_DIR, cleanup, witness  # noqa: E402

from form.open import Program  # noqa: E402
from form.mandell.executor import execute_seed  # noqa: E402

OWNER = "CoreIRev"
GEN_RE = re.compile(r"generation \S+")
HEX_RE = re.compile(r"\bg[0-9a-f]{16,}\b")


def fresh():
    cleanup(OWNER)
    return Program(owner=OWNER)


def deep_norm(w):
    ok, err, state, msgs = w
    msgs = GEN_RE.sub("generation <GEN>", msgs)
    msgs = HEX_RE.sub("<GEN>", msgs)
    return (ok, err, state, msgs)


def main():
    print("== A2.1: Dell 27 differential, gen-id normalized ==")
    p = fresh()
    wb = deep_norm(witness(execute_seed(p, "27[Checkpoint]"), p))
    p = fresh()
    wt = deep_norm(witness(
        execute_seed(p, '27[Checkpoint](bogus="zzprobe")'), p))
    print(f"  bare==typed(bogus): {wb == wt}")
    p = fresh()
    ws = deep_norm(witness(
        execute_seed(p, '27[Checkpoint](stamp="typedstamp")'), p))
    print(f"  bare==typed(stamp): {wb == ws}")

    print("== A2.2: persisted-file search after typed 27 run ==")
    p = fresh()
    execute_seed(p, '27[Checkpoint](stamp="typedstamp")')
    hits = {}
    for f in sorted(glob.glob(os.path.join(STATE_DIR, f"*{OWNER}*"))):
        if os.path.isfile(f):
            try:
                text = open(f, encoding="utf-8", errors="replace").read()
            except Exception:  # noqa: BLE001
                continue
            for needle in ("typedstamp", "zzprobe", "bogus", "stamp"):
                if needle in text:
                    hits.setdefault(os.path.basename(f), []).append(needle)
    print(f"  files with needles: {json.dumps(hits, indent=1)}")
    cleanup(OWNER)

    print("== A2.3: Dell 44 label-driven capability ==")
    p = fresh()
    r = execute_seed(p, '44[Bridge](bogus="x") :: labelcap')
    print(f"  ok={r.get('ok')} last_core_i="
          f"{json.dumps(getattr(p, 'last_core_i', None), default=str)}")

    print("== A2.4: Dell 21 positive path (two sources) ==")
    setup = ['08[Create] :: alpha_one', '08[Create] :: beta_two']
    p = fresh()
    for s in setup:
        execute_seed(p, s)
    wb = witness(execute_seed(p, "21[Merge] :: alpha_one beta_two"), p)
    p = fresh()
    for s in setup:
        execute_seed(p, s)
    wt = witness(execute_seed(
        p, '21[Merge](bogus="x") :: alpha_one beta_two'), p)
    print(f"  bare ok={wb[0]} typed ok={wt[0]} equal={wb == wt}")
    print(f"  bare units={json.loads(wb[2]).get('units')}")
    cleanup(OWNER)
    print("PROBE A2 DONE")


if __name__ == "__main__":
    main()
