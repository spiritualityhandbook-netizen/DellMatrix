#!/usr/bin/env python3
"""Director order step 3 — security circuits DAF-02/B5, DAF-03, DAF-10.

DAF-02/B5: Sanitize disclosed its input via generic echoes, returned
seed/English, the outcome ledger, and the persisted program JSON.
Contract: for any seed containing Dell 41, NO surface (result dict,
messages, outcome record, history, saved JSON, chain last_flow)
contains the secret-shaped marker; sanitized audit facts survive
(dell, ok, redacted text); clean text and non-Sanitize seeds are
byte-unchanged.

DAF-03: InternetGate validated userinfo instead of the host and
followed redirects without per-hop authorization. Contract:
canonical parsing, userinfo rejected, every redirect hop authorized
before connecting, a blocked hop makes ZERO requests to the blocked
destination (server hit counter is the witness), same-host and
allowed-host redirects still work, _json_get uses the same gate.

DAF-10: failed fetches bypassed the fetch-log cap (45 retained vs
40). Contract: one shared append-and-trim — success and failure
alike — and log URLs carry no userinfo/query.

Synthetic canary only, presence booleans only; loopback only;
isolated synthetic program owner with loud cleanup.
"""
import glob
import json
import os
import shutil
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

RESULTS = []
MARKER = "SYNTHETIC_STEP3_CANARY_719"
OWNER = "step3secZZ"


def _rec(name, cond, detail=""):
    RESULTS.append((name, bool(cond), str(detail)[:220]))


def _cleanup(owner):
    state = os.path.join(_ROOT, "form", "state")
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


def _check_sanitize():
    from form.open import Program
    from form.mandell.execution_observer import observe_seed_execution
    from form.mandell.executor import execute_seed

    _cleanup(OWNER)
    p = Program(owner=OWNER)
    r = observe_seed_execution(
        p, f"41[Sanitize] :: password={MARKER} normal words")
    _rec("DAF-02: Sanitize execution ok", r.get("ok") is True, r.get("error"))
    _rec("DAF-02: marker absent from result dict",
         MARKER not in json.dumps(r, default=str))
    _rec("DAF-02: marker absent from messages",
         all(MARKER not in m for m in r.get("messages", [])),
         str(r.get("messages"))[:120])
    _rec("DAF-02: marker absent from outcome records",
         MARKER not in json.dumps(p.outcome_records, default=str))
    _rec("DAF-02: marker absent from history",
         MARKER not in json.dumps(list(p.history), default=str))
    recs = [v for v in p.outcome_records.values() if isinstance(v, dict)]
    rec = recs[-1] if recs else {}
    _rec("DAF-02: sanitized audit facts preserved (dell 41, "
         "redacted input, ordinary words kept)",
         rec.get("dell") == 41 and "[REDACTED]" in str(rec.get("input", ""))
         and "normal words" in str(rec.get("input", "")),
         str(rec.get("input"))[:120])
    _rec("DAF-02: Sanitize lines show sanitized text only",
         any(m == f"Sanitize out: password=[REDACTED] normal words"
             for m in r.get("messages", [])),
         str(r.get("messages"))[:160])
    path = p.save()
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        saved = fh.read()
    _rec("DAF-02: marker absent from SAVED program JSON",
         MARKER not in saved)

    r2 = observe_seed_execution(
        p, f"41[Sanitize] :: password={MARKER} > 70[Count]")
    blob = (json.dumps(r2, default=str)
            + json.dumps(p.outcome_records, default=str)
            + json.dumps(getattr(p, "last_flow", {}), default=str))
    _rec("DAF-02: marker absent from CHAIN result/outcome/last_flow",
         MARKER not in blob and r2.get("ok") is True)

    r3 = execute_seed(p, "41[Sanitize] :: hello world")
    lines = [m for m in r3.get("messages", []) if m.startswith("Sanitize")]
    _rec("DAF-02: clean text passes through unchanged",
         lines == ["Sanitize in:  hello world",
                   "Sanitize out: hello world"], str(lines))
    r4 = execute_seed(p, "70[Count]")
    _rec("DAF-02: non-Sanitize seed echo unchanged",
         r4.get("seed") == "70[Count]"
         and (r4.get("messages") or [""])[0] == "Mandell: 70[Count]",
         str(r4.get("seed")))
    _cleanup(OWNER)


class _Handler(BaseHTTPRequestHandler):
    hits = {"blocked": 0, "ok": 0, "json": 0, "missing": 0}

    def log_message(self, *a):
        pass

    def do_GET(self):
        port = self.server.server_port
        if self.path == "/redir-blocked":
            self.send_response(302)
            self.send_header("Location", f"http://localhost:{port}/hit-blocked")
            self.end_headers()
        elif self.path == "/hit-blocked":
            type(self).hits["blocked"] += 1
            self.send_response(200); self.end_headers()
            self.wfile.write(b"blocked-host-content")
        elif self.path == "/redir-allowed":
            self.send_response(302)
            self.send_header("Location", f"http://localhost:{port}/ok")
            self.end_headers()
        elif self.path == "/redir-ok":
            self.send_response(302)
            self.send_header("Location", "/ok")
            self.end_headers()
        elif self.path == "/ok":
            type(self).hits["ok"] += 1
            self.send_response(200); self.end_headers()
            self.wfile.write(b"hello ok")
        elif self.path == "/data.json":
            type(self).hits["json"] += 1
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"a": 1}')
        else:
            type(self).hits["missing"] += 1
            self.send_response(404); self.end_headers()
            self.wfile.write(b"nope")


def _check_gate():
    from form.dell_matrix.internet_gate import InternetGate

    srv = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    port = srv.server_port
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        g = InternetGate()
        g.allowed_hosts = ["127.0.0.1"]
        g.turn_on()
        r = g.fetch_url(f"http://127.0.0.1:{port}/redir-blocked")
        _rec("DAF-03: redirect to blocked host refused",
             r.get("ok") is False, str(r)[:140])
        _rec("DAF-03: blocked destination received ZERO requests",
             _Handler.hits["blocked"] == 0, str(_Handler.hits))
        r = g.fetch_url(f"http://127.0.0.1:{port}/redir-ok")
        _rec("DAF-03: same-host redirect positive control",
             r.get("ok") is True and "hello ok" in str(r.get("preview", "")),
             str(r)[:140])

        g2 = InternetGate()
        g2.allowed_hosts = ["127.0.0.1", "localhost"]
        g2.turn_on()
        r = g2.fetch_url(f"http://127.0.0.1:{port}/redir-allowed")
        _rec("DAF-03: allowed-host redirect positive control",
             r.get("ok") is True, str(r)[:140])

        gd = InternetGate()
        _rec("DAF-03: userinfo URL fails host validation "
             "(parsed host is the unallowed one)",
             gd._host_ok("https://example.com:pass@not-allowed.invalid/test")
             is False)
        _rec("DAF-03: plain allowed host + subdomain still pass; "
             "non-http(s) scheme refused",
             gd._host_ok("https://example.com/x") is True
             and gd._host_ok("https://en.wikipedia.org/x") is True
             and gd._host_ok("ftp://example.com/x") is False)
        before = _Handler.hits["ok"]
        r = g.fetch_url(f"http://user:pass@127.0.0.1:{port}/ok")
        _rec("DAF-03: userinfo to an allowed host still refused, "
             "no request made",
             r.get("ok") is False and _Handler.hits["ok"] == before,
             str(r)[:140])

        r = g._json_get(f"http://localhost:{port}/data.json")
        _rec("DAF-03: _json_get blocked host refused (same gate)",
             r.get("ok") is False and _Handler.hits["json"] == 0,
             str(r)[:140])
        r = g._json_get(f"http://127.0.0.1:{port}/data.json")
        _rec("DAF-03: _json_get allowed host works",
             r.get("ok") is True and (r.get("data") or {}).get("a") == 1,
             str(r)[:140])

        g3 = InternetGate()
        g3.allowed_hosts = ["127.0.0.1"]
        g3.turn_on()
        for i in range(45):
            g3.fetch_url(f"http://127.0.0.1:{port}/missing-{i}?token=abc123")
        _rec("DAF-10: 45 failures leave exactly the 40-entry cap",
             len(g3.fetch_log) == 40, f"len={len(g3.fetch_log)}")
        _rec("DAF-10: log URLs carry no query/userinfo secrets",
             all("token" not in str(e.get("url", ""))
                 and "@" not in str(e.get("url", ""))
                 for e in g3.fetch_log),
             str(g3.fetch_log[:1])[:140])
        for i in range(5):
            g3.fetch_url(f"http://127.0.0.1:{port}/ok")
        _rec("DAF-10: success path shares the same bound",
             len(g3.fetch_log) == 40
             and g3.fetch_log[-1].get("ok") is True,
             f"len={len(g3.fetch_log)}")
    finally:
        srv.shutdown()


def main():
    _check_sanitize()
    _check_gate()
    passed = sum(1 for _, ok_, _ in RESULTS if ok_)
    for name, ok_, detail in RESULTS:
        if not ok_:
            print(f"FAIL {name}: {detail}")
    print(f"STEP3_SECURITY: {passed}/{len(RESULTS)}")
    return passed == len(RESULTS) and len(RESULTS) > 0


def smoke():
    return main()


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
