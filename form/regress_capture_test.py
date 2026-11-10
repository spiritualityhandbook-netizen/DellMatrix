"""Privacy + behavior checks for the regress.py failure capture.

DD-31 Q-DD31-D1 hardening (Director ruling 2026-11-10 01:40 CST):
emitted diagnostics must carry only safe assertion identifiers and
sanitized bounded metadata - never raw child stdout/stderr, never
state filenames - with a documented retention lifecycle and no
path escape via entry naming or the capture-dir environment value.
These checks are failing-first against the unhardened capture.
"""
import contextlib
import io
import os
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from form import regress  # noqa: E402

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(("PASS " if cond else "FAIL ") + name +
          ((": " + detail) if (detail and not cond) else ""), flush=True)


CANARIES = ["canary-secret-7f3a9b", "canary-tail-55x", "canary-stderr-99z",
            "AKIA7F3A9B2C4D6E8F01", "DrPrivateNotes"]

FAKEFAIL = '''
import sys
def smoke():
    print("PASS other_check: ok")
    print("FAIL privacy_probe_check: leaked canary-secret-7f3a9b here")
    print("note: token is canary-tail-55x")
    print("error near canary-stderr-99z", file=sys.stderr)
    print("FAKEFAIL: 1/2")
    return False
'''

GREENMOD = '''
def smoke():
    print("GREENMOD: 1/1")
    return True
'''

NESTEDMOD = '''
import os, sys
sys.path.insert(0, os.environ["CAPTEST_PARENT"])
from form.regress import run_entry
def smoke():
    ok, why = run_entry("fakefail:smoke", os.environ["CAPTEST_CWD"], "inner")
    print("NESTEDMOD: 1/1")
    return True
'''


def _run(entry, cwd, label):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ok, why = regress.run_entry(entry, cwd, label)
    return ok, why, buf.getvalue()


def main():
    tmp = tempfile.mkdtemp(prefix="captest_")
    work = os.path.join(tmp, "work")
    state = os.path.join(work, "form", "state")
    os.makedirs(state)
    for mod, src in (("fakefail", FAKEFAIL), ("greenmod", GREENMOD),
                     ("nestedmod", NESTEDMOD)):
        with open(os.path.join(work, mod + ".py"), "w") as fh:
            fh.write(src)
    with open(os.path.join(state, "current_DrPrivateNotes.json"), "w") as fh:
        fh.write('{"canary": "canary-secret-7f3a9b"}')
    with open(os.path.join(state, "plain.json"), "w") as fh:
        fh.write("{}")
    capdir = os.path.join(tmp, "caps")
    os.environ["REGRESS_FAILURE_DIR"] = capdir
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # 1. Failing entry: identifiers + metadata only, no canary anywhere.
    ok, why, out = _run("fakefail:smoke", work, "pass1")
    check("verdict_false_on_failure", not ok)
    check("assertion_id_emitted", "privacy_probe_check" in out)
    for c in CANARIES:
        check(f"canary_absent_stdout[{c[:12]}]", c not in out)
    files = sorted(os.listdir(capdir)) if os.path.isdir(capdir) else []
    check("capture_file_written", len(files) == 1, f"files={files}")
    if files:
        body = open(os.path.join(capdir, files[0])).read()
        check("assertion_id_in_file", "privacy_probe_check" in body)
        for c in CANARIES:
            check(f"canary_absent_file[{c[:12]}]", c not in body)
        check("state_count_metadata", "files=2" in body)
        check("no_raw_fail_detail", "leaked" not in body)

    # 1b. The STOCK summary path (Director finding, 2026-11-10
    # wake review): the returned why string is printed verbatim
    # by run_pass on the RED line — it must never carry the raw
    # stderr tail. Canary-free, metadata intact.
    check("why_canary_free",
          all(c not in why for c in CANARIES), f"why={why}")
    check("why_metadata_kept",
          "rc=" in why and "last=1/2" in why
          and "NOT_RETURNED_TRUE" in why, f"why={why}")
    _before = set(os.listdir(capdir))
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        regress.run_pass(["fakefail:smoke"], ["fakefail:smoke"],
                         work, "pass1b")
    check("runpass_line_canary_free",
          all(c not in buf.getvalue() for c in CANARIES),
          buf.getvalue()[-200:])
    for _f in set(os.listdir(capdir)) - _before:
        os.unlink(os.path.join(capdir, _f))

    # 2. Green entry: silence.
    ok2, _, out2 = _run("greenmod:smoke", work, "pass1")
    check("verdict_true_on_green", ok2)
    check("green_silence", "REGRESS-CAPTURE" not in out2)
    check("green_no_new_file", len(os.listdir(capdir)) == 1)

    # 3. Nested: inner failure captured, outer verdict stays green.
    os.environ["CAPTEST_PARENT"] = root
    os.environ["CAPTEST_CWD"] = work
    ok3, _, _ = _run("nestedmod:smoke", work, "pass1")
    check("nested_outer_green", ok3)
    check("nested_inner_captured", len(os.listdir(capdir)) == 2)

    # 4. Entry naming cannot traverse out of the capture dir.
    regress._emit_capture("../evil_entry", "pass", "rc=1 last=0/0",
                          "FAIL x_y: canary-secret-7f3a9b", "", work)
    names = os.listdir(capdir)
    check("traversal_contained",
          all("/" not in n and not n.startswith(".") for n in names)
          and not os.path.exists(os.path.join(tmp, "evil_entry.log"))
          and len(names) == 3, f"names={names}")

    # 5. Capture dir outside the allowed roots is refused (stdout only).
    esc = "/etc/captest_escape_dir"
    os.environ["REGRESS_FAILURE_DIR"] = esc
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        regress._emit_capture("fakefail:smoke", "pass9", "rc=1", "", "", work)
    check("escape_dir_refused", not os.path.exists(esc)
          and "refused" in buf.getvalue())
    os.environ["REGRESS_FAILURE_DIR"] = capdir

    # 6. Retention lifecycle: directory is pruned to the newest 50.
    for i in range(55):
        p = os.path.join(capdir, f"dummy_{i:02d}.log")
        with open(p, "w") as fh:
            fh.write("old")
        old = time.time() - (1000 - i)
        os.utime(p, (old, old))
    regress._emit_capture("fakefail:smoke", "pass7", "rc=1", "", "", work)
    remaining = os.listdir(capdir)
    check("retention_prunes_to_50", len(remaining) <= 50,
          f"remaining={len(remaining)}")

    n = sum(1 for _, okk in RESULTS if okk)
    print(f"REGRESS_CAPTURE: {n}/{len(RESULTS)}", flush=True)
    return 0 if n == len(RESULTS) else 1


def smoke():
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
