import errno, os, signal, subprocess, sys
sys.path.insert(0, os.getcwd())
import form.regress as R

fails = []

def case(name, cond, detail=""):
    print(("[PASS] " if cond else "[FAIL] ") + name
          + (" -- " + detail if detail else ""))
    if not cond:
        fails.append(name)

def boom(err):
    def _raise(fd, sig):
        raise OSError(err, os.strerror(err))
    return _raise

victim = subprocess.Popen([sys.executable, "-c",
                           "import time; time.sleep(60)"])
try:
    ident = (victim.pid, R._proc_starttime(victim.pid))
    case("sanity: witnessed identity captured", ident[1] is not None,
         "pid=%s starttime=%s" % ident)
    real_send = R._pidfd_send_signal
    for name, err, want in (("EPERM", errno.EPERM, "unavailable"),
                            ("ENOSYS", errno.ENOSYS, "unavailable"),
                            ("ESRCH", errno.ESRCH, "refused")):
        R._pidfd_send_signal = boom(err)
        try:
            outcome = R._signal_identity(ident[0], ident[1],
                                         signal.SIGKILL)
        finally:
            R._pidfd_send_signal = real_send
        case("send-%s classes %s" % (name, want), outcome == want,
             "outcome=%r" % (outcome,))
        case("send-%s: live victim not signalled" % name,
             victim.poll() is None)
finally:
    if victim.poll() is None:
        victim.terminate()
    victim.wait(timeout=10)

print("=== probe_dirf16_send_boundary: %d/7 ===" % (7 - len(fails)))
sys.exit(1 if fails else 0)
