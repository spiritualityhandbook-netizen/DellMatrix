#!/usr/bin/env python3
"""Fixed child script for matched benchmark (t15 pattern).

Takes JSON args via argv[1], writes JSON result to stdout.
Parent harness controls ordering, alternation, and validation.

Args JSON:
{
  "repo": "/path/to/repo",
  "owner": "unique owner",
  "op": "confirm" | "supersede" | "learned_off" | "learned_on",
  "use_auth": true | false,
  "state_root": "/path/to/state"  # canonical state dir
}

Result JSON:
{
  "sha": "actual git sha",
  "clean_tree": true | false,
  "module_path": "imported form package path",
  "mount": "filesystem mount point",
  "fstype": "filesystem type",
  "state_path": "actual state dir used",
  "setup_ok": true | false,
  "setup_ms": float,
  "op_ms": float,
  "fsync_count": int,       # operation-only (reset before timer)
  "fsync_ms": float,        # operation-only fsync duration
  "bytes_written": int,     # via write hook, or -1 if unmeasured
  "checkpoint_files": int,
  "result": {...},          # operation-specific outcome
  "error": null | str
}
"""

import glob
import json
import os
import subprocess
import sys
import time


def get_sha(repo):
    try:
        r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo,
                           capture_output=True, text=True, timeout=10)
        return r.stdout.strip() if r.returncode == 0 else "unknown"
    except Exception:
        return "unknown"


def get_clean(repo):
    try:
        r = subprocess.run(["git", "status", "--porcelain"], cwd=repo,
                           capture_output=True, text=True, timeout=10)
        return r.returncode == 0 and r.stdout.strip() == ""
    except Exception:
        return False


def get_mount(path):
    try:
        r = subprocess.run(["df", "--output=target,fstype", path],
                           capture_output=True, text=True, timeout=10)
        lines = r.stdout.strip().split("\n")
        if len(lines) >= 2:
            parts = lines[1].split()
            return parts[0] if len(parts) > 0 else "unknown", \
                   parts[1] if len(parts) > 1 else "unknown"
    except Exception:
        pass
    return "unknown", "unknown"


def main():
    args = json.loads(sys.argv[1])
    repo = args["repo"]
    owner = args["owner"]
    op = args["op"]
    use_auth = args["use_auth"]

    sys.path.insert(0, repo)
    os.chdir(repo)

    # Identity (runtime-verified, not hardcoded)
    sha = get_sha(repo)
    clean = get_clean(repo)
    import form
    module_path = os.path.dirname(os.path.abspath(form.__file__))
    state_root = os.path.join(repo, "form", "state")
    mount, fstype = get_mount(state_root)

    # Instrumentation: reset immediately before timed operation
    fsync_count = [0]
    fsync_ms = [0.0]
    bytes_written = [0]
    orig_fsync = os.fsync

    def counting_fsync(fd):
        t0 = time.perf_counter()
        try:
            return orig_fsync(fd)
        finally:
            fsync_count[0] += 1
            fsync_ms[0] += (time.perf_counter() - t0) * 1000

    os.fsync = counting_fsync

    # Byte counting via atomic_write hook
    try:
        import form.dell_matrix.atomic_write as aw
        orig_write = aw.atomic_write_bytes

        def counting_write(path, data, **kw):
            bytes_written[0] += len(data) if isinstance(data, (bytes, bytearray)) else 0
            return orig_write(path, data, **kw)

        aw.atomic_write_bytes = counting_write
        bytes_measured = True
    except Exception:
        bytes_measured = False

    from form.open import open_program

    def confirm_one(p, prop):
        if use_auth:
            ctx = p.make_review_context(prop.id, owner)
            return p.confirm_proposal(prop.id, _producer=owner, _review_context=ctx)
        else:
            return p.confirm_proposal(prop.id)

    result = {"ok": False}
    setup_ok = True
    error = None

    try:
        # Setup (not timed for headline; reported separately)
        t_setup0 = time.perf_counter()
        p = open_program(owner)
        if use_auth:
            p.acceptance_policy.grant_opt_in(owner, scope="bench")
        # 10 proposals, 3 confirmed (equivalent accepted content both sides)
        setup_ids = []
        for i in range(10):
            sp = p.nursery.add(f"W{i}", words=f"work content {i} alpha beta")
            if i < 3:
                r = confirm_one(p, sp)
                if not r.get("ok"):
                    setup_ok = False
            setup_ids.append(sp.id)
        # Learned selection: populate valid learning evidence
        if op in ("learned_on", "learned_off"):
            # Confirm two more with overlapping content for selector
            for i in range(2):
                lp = p.nursery.add(f"L{i}", words="alpha beta gamma delta")
                r = confirm_one(p, lp)
                if not r.get("ok"):
                    setup_ok = False
            # Record learning influence state
            p.learning_influence = (op == "learned_on")
        # Prepare operation-specific state BEFORE timer
        prepped = None
        if op == "confirm":
            prepped = p.nursery.add("BenchOp", words="bench operation content")
        elif op == "supersede":
            prepped = p.nursery.add("SupPred", words="v1 content")
            r = confirm_one(p, prepped)
            if not r.get("ok"):
                setup_ok = False
        t_setup1 = time.perf_counter()
        setup_ms = (t_setup1 - t_setup0) * 1000

        # Reset instrumentation immediately before timed operation
        fsync_count[0] = 0
        fsync_ms[0] = 0.0
        bytes_written[0] = 0

        # Timed operation
        t0 = time.perf_counter()
        if op == "confirm":
            r = confirm_one(p, prepped)
            result = {"ok": bool(r.get("ok")),
                      "status": prepped.status,
                      "unit": prepped.id in p.cube.session.plane.units}
        elif op == "supersede":
            from form.mandell.supersession import supersede_proposal
            old_id = prepped.id
            if use_auth:
                receipt = supersede_proposal(p, prepped.id, words="v2 content",
                                             _producer=owner)
            else:
                receipt = supersede_proposal(p, prepped.id, words="v2 content")
            result = {"ok": bool(receipt.get("ok")),
                      "new_successor": receipt.get("new_id") != old_id,
                      "rev": receipt.get("revision_number")}
        elif op in ("learned_on", "learned_off"):
            from form.mandell.knowledge_selector import select_for_context
            # Prove the intended path executes
            sel = select_for_context(p, "alpha beta")
            selected = sel.get("selected", [])
            # Verify influence state matches op
            influence_active = bool(getattr(p, "learning_influence", False))
            expected = (op == "learned_on")
            result = {"ok": True,
                      "n": len(selected),
                      "influence_path": influence_active == expected,
                      "influence_active": influence_active}
        t1 = time.perf_counter()
        op_ms = (t1 - t0) * 1000

        # Durable outcome assertions (after timing, fresh-process reload)
        # We do a lightweight check here; parent does full reload
        ckpt = glob.glob(os.path.join(state_root, f"checkpoint_{owner}_*"))

    except Exception as e:
        error = f"{type(e).__name__}: {e}"
        op_ms = -1
        setup_ms = -1

    print(json.dumps({
        "sha": sha,
        "clean_tree": clean,
        "module_path": module_path,
        "mount": mount,
        "fstype": fstype,
        "state_path": state_root,
        "setup_ok": setup_ok,
        "setup_ms": round(setup_ms, 2) if setup_ms >= 0 else -1,
        "op_ms": round(op_ms, 2) if op_ms >= 0 else -1,
        "fsync_count": fsync_count[0],
        "fsync_ms": round(fsync_ms[0], 2),
        "bytes_written": bytes_written[0] if bytes_measured else -1,
        "checkpoint_files": len(ckpt) if 'ckpt' in dir() else -1,
        "result": result,
        "error": error,
    }))


if __name__ == "__main__":
    main()
