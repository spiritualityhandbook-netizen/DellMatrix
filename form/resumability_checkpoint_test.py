"""SM-08 suite — durable resumability checkpoints.

Register row #92 (SM-08): make the workflow resumable — last-good
checkpoint + completed-circuit records. The practice exists today
only as convention: the completion envelope (AGENTS.md section 4)
kept in a state file that grew past readable size (the 2026-11-20
01:43 CST cycle failure) and an append-only envelope that once grew
to ~50 KB and stalled a continuation worker (AGENTS.md section 4
lesson). Convention is not a mechanism: there is no writer/reader
pair, no integrity check, and no recovery test. This suite is the
recovery test, written first.

Contract under test (Part 0 plan, director-reports/PART_0_PLAN_2026-11-20.md):
module ``form/resume_checkpoint.py`` provides

    write_checkpoint(path, state)  -> path
    read_checkpoint(path)          -> state dict
    verify_checkpoint(state)       -> list of problem strings ([] = sound)

with these laws:
  * the state carries every completion-envelope field (AGENTS.md
    section 4) — a missing field is named by verify_checkpoint;
  * write is atomic (temp file + replace): a torn or truncated
    checkpoint is NEVER silently trusted — reading it either raises
    or yields a state verify_checkpoint rejects;
  * the state carries a checksum over its canonical form — any
    post-write tampering is detected;
  * COMPLETED_PHASES is append-only across writes: a later
    checkpoint that drops a completed phase is refused at write;
  * unknown extra fields round-trip untouched (forward compatibility);
  * a checkpoint written by one process is readable by another
    (the recovery reader is a different OS process than the writer);
  * multiwriter contract (Director 7056433688, 2026-11-20): the
    append-only law holds across concurrent writers — a write may
    be loudly refused (and retried by its caller) but a phase from
    a write that reported success is NEVER silently lost.

Written failing-first at plan stage (0/9 while the module was
absent); the module landed at code stage and the suite now judges
it. All writes go to a private temp directory — no form/state
contact.
"""
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(("PASS " if cond else "FAIL ") + name +
          ((": " + detail) if (detail and not cond) else ""), flush=True)


try:
    from form import resume_checkpoint as RC
except Exception:
    RC = None

ENVELOPE_FIELDS = [
    "DIRECTIVE_ID", "PARENT_GOAL", "BASE", "BRANCH", "HEAD",
    "WORKTREE", "FILES_CHANGED", "COMPLETED_PHASES", "CURRENT_PHASE",
    "TESTS_RUN", "TESTS_REMAINING", "UNCOMMITTED_WORK", "BLOCKERS",
    "FALLBACK_PATHS", "NEXT_EXECUTABLE_ACTION",
]


def full_state():
    s = {f: "x" for f in ENVELOPE_FIELDS}
    s["HEAD"] = "a" * 40
    s["BASE"] = "b" * 40
    s["FILES_CHANGED"] = ["form/open.py"]
    s["COMPLETED_PHASES"] = ["PLAN"]
    s["TESTS_RUN"] = ["gate_reconciliation 0/24 (failing-first)"]
    s["TESTS_REMAINING"] = ["campaign x3"]
    s["UNCOMMITTED_WORK"] = ""
    s["BLOCKERS"] = []
    s["FALLBACK_PATHS"] = ["resume from HEAD"]
    return s


def main():
    check("module_present", RC is not None,
          "form/resume_checkpoint.py does not exist " "(SM-08 module missing)")
    if RC is None:
        for name in ("round_trip", "cross_process_read",
                     "torn_checkpoint_refused",
                     "tampered_checkpoint_detected",
                     "missing_field_named", "completed_phases_append_only",
                     "extra_fields_round_trip", "no_temp_residue"):
            check(name, False, "module absent")
        n = sum(1 for _, okk in RESULTS if okk)
        print(f"RESUMABILITY_CHECKPOINT: {n}/{len(RESULTS)}",
              flush=True)
        return 0 if n == len(RESULTS) else 1

    tmp = tempfile.mkdtemp(prefix="sm08_")
    path = os.path.join(tmp, "checkpoint.json")
    state = full_state()

    try:
        RC.write_checkpoint(path, state)
        back = RC.read_checkpoint(path)
        check("round_trip", back == state,
              "written state must read back identical")
    except Exception as exc:
        check("round_trip", False, "write/read raised: %r" % (exc,))
        back = None

    try:
        code = ("import json,sys;"
                "d=json.load(open(sys.argv[1]));"
                "print(d['HEAD'])")
        out = subprocess.run(
            [sys.executable, "-c", code, path],
            capture_output=True, text=True, timeout=60)
        check("cross_process_read",
              out.returncode == 0
              and out.stdout.strip() == state["HEAD"],
              "a separate OS process must read the checkpoint")
    except Exception as exc:
        check("cross_process_read", False, "reader raised: %r" % (exc,))

    try:
        raw = open(path, "rb").read()
        torn = os.path.join(tmp, "torn.json")
        with open(torn, "wb") as fh:
            fh.write(raw[: len(raw) // 2])
        try:
            got = RC.read_checkpoint(torn)
            refused = RC.verify_checkpoint(got) != []
        except Exception:
            refused = True
        check("torn_checkpoint_refused", refused,
              "a truncated checkpoint is never silently trusted")
    except Exception as exc:
        check("torn_checkpoint_refused", False, "probe raised: %r"
              % (exc,))

    try:
        raw = open(path, "r", encoding="utf-8").read()
        tamp = os.path.join(tmp, "tampered.json")
        with open(tamp, "w", encoding="utf-8") as fh:
            fh.write(raw.replace(state["HEAD"], "f" * 40, 1))
        try:
            got = RC.read_checkpoint(tamp)
            detected = RC.verify_checkpoint(got) != []
        except Exception:
            detected = True
        check("tampered_checkpoint_detected", detected,
              "post-write tampering must break the checksum")
    except Exception as exc:
        check("tampered_checkpoint_detected", False,
              "probe raised: %r" % (exc,))

    try:
        broken = full_state()
        del broken["HEAD"]
        problems = RC.verify_checkpoint(broken)
        check("missing_field_named",
              any("HEAD" in p for p in problems),
              "verify must name the missing envelope field")
    except Exception as exc:
        check("missing_field_named", False, "verify raised: %r"
              % (exc,))

    try:
        v2 = full_state()
        v2["COMPLETED_PHASES"] = ["PLAN", "CODE"]
        RC.write_checkpoint(path, v2)
        v3 = full_state()
        v3["COMPLETED_PHASES"] = ["CODE"]
        try:
            RC.write_checkpoint(path, v3)
            refused = False
        except Exception:
            refused = True
        check("completed_phases_append_only", refused,
              "a later checkpoint may not drop a completed phase")
    except Exception as exc:
        check("completed_phases_append_only", False,
              "probe raised: %r" % (exc,))

    try:
        extra = full_state()
        extra["FUTURE_FIELD"] = {"nested": [1, 2, 3]}
        p2 = os.path.join(tmp, "extra.json")
        RC.write_checkpoint(p2, extra)
        check("extra_fields_round_trip",
              RC.read_checkpoint(p2) == extra,
              "unknown fields round-trip untouched")
    except Exception as exc:
        check("extra_fields_round_trip", False, "probe raised: %r"
              % (exc,))


    # --- two-writer adversarial probe (Director 7056433688) --------
    try:
        wdir = os.path.join(tmp, "writers")
        os.makedirs(wdir, exist_ok=True)
        wpath = os.path.join(wdir, "shared.json")
        base = full_state()
        RC.write_checkpoint(wpath, base)
        writer_src = os.path.join(wdir, "writer.py")
        with open(writer_src, "w", encoding="utf-8") as fh:
            fh.write(
                "import os, sys\n"
                "sys.path.insert(0, sys.argv[3])\n"
                "from form import resume_checkpoint as RC\n"
                "path, tag, log = sys.argv[1], sys.argv[2], sys.argv[4]\n"
                "ok = []\n"
                "for i in range(20):\n"
                "    st = RC.read_checkpoint(path)\n"
                "    st['COMPLETED_PHASES'] = list("
                "st['COMPLETED_PHASES']) + ['%s-%d' % (tag, i)]\n"
                "    try:\n"
                "        RC.write_checkpoint(path, st)\n"
                "        ok.append('%s-%d' % (tag, i))\n"
                "    except Exception:\n"
                "        pass\n"
                "for attempt in range(100):\n"
                "    st = RC.read_checkpoint(path)\n"
                "    if tag + '-FINAL' in st['COMPLETED_PHASES']:\n"
                "        break\n"
                "    st['COMPLETED_PHASES'] = list("
                "st['COMPLETED_PHASES']) + [tag + '-FINAL']\n"
                "    try:\n"
                "        RC.write_checkpoint(path, st)\n"
                "        ok.append(tag + '-FINAL')\n"
                "        break\n"
                "    except Exception:\n"
                "        continue\n"
                "with open(log, 'w', encoding='utf-8') as fh:\n"
                "    fh.write('\\n'.join(ok))\n")
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        procs = []
        logs = {}
        for tag in ("WA", "WB"):
            log = os.path.join(wdir, tag + ".log")
            logs[tag] = log
            procs.append(subprocess.Popen(
                [sys.executable, writer_src, wpath, tag, root, log]))
        for proc in procs:
            proc.wait(timeout=120)
        final = RC.read_checkpoint(wpath)
        succeeded = set()
        for log in logs.values():
            with open(log, encoding="utf-8") as fh:
                succeeded.update(
                    line.strip() for line in fh if line.strip())
        lost = sorted(ph for ph in succeeded
                      if ph not in final["COMPLETED_PHASES"])
        check("two_writer_no_silent_loss",
              not lost and "WA-FINAL" in final["COMPLETED_PHASES"]
              and "WB-FINAL" in final["COMPLETED_PHASES"],
              "phases from successful writes silently lost: %s; "
              "final phases: %s" % (lost, final["COMPLETED_PHASES"]))
    except Exception as exc:
        check("two_writer_no_silent_loss", False,
              "probe raised: %r" % (exc,))

    residue = [f for f in os.listdir(tmp)
               if f.endswith((".tmp", ".part", "~"))]
    check("no_temp_residue", residue == [],
          "atomic write leaves no temp residue: %s" % (residue,))

    n = sum(1 for _, okk in RESULTS if okk)
    print(f"RESUMABILITY_CHECKPOINT: {n}/{len(RESULTS)}", flush=True)
    return 0 if n == len(RESULTS) else 1


def smoke():
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
