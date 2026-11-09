#!/usr/bin/env python3
"""DD-31 — Sanitize copula leak (Ace-authorized fix-first, 2026-11-09).

Verified live at base (REPL owner TOUR41A): Dell 41 Sanitize's
redaction authority (form/mandell/redaction.py) matched
``keyword [: =]? <next token>``. In the natural-English copula
form "my password is swordfish99" it redacted the word "is"
and left the ACTUAL secret standing in Sanitize's own cleaned
output: "my password=[REDACTED] swordfish99".

Contract proven here:
- Copula forms redact the VALUE: "password is X",
  "secret is X", "token is X", "api_key is X",
  "bearer is X", "password is: X".
- Pre-existing forms keep working byte-for-byte:
  "password=X", "password: X", bare "password X".
- 12+ digit redaction is unchanged.
- Ordinary text (including "is" with no keyword) is untouched.
- The Dell 41 leaf surfaces (messages / result) show no canary
  for the copula case, and the "Sanitize out:" line carries
  [REDACTED].

Synthetic canary only, presence booleans only in records;
isolated synthetic program owners with loud cleanup.
"""
import glob
import json
import os
import shutil
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

RESULTS = []
CANARY = "SYNTHETIC_DD31_CANARY_5151"


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


def main():
    from form.mandell.redaction import sanitize_text

    # ---------- copula forms: the VALUE must be redacted ----------
    for kw in ("password", "secret", "token", "api_key", "bearer"):
        out = sanitize_text(f"my {kw} is {CANARY} today")
        _rec(f"copula '{kw} is X' redacts the value",
             CANARY not in out and "[REDACTED]" in out, out)
    out = sanitize_text(f"the password is: {CANARY}")
    _rec("copula 'password is: X' redacts the value",
         CANARY not in out and "[REDACTED]" in out, out)
    out = sanitize_text(f"Password Is {CANARY}")
    _rec("copula is case-insensitive ('Password Is X')",
         CANARY not in out and "[REDACTED]" in out, out)

    # ---------- pre-existing forms unchanged ----------
    for label, text in (
        ("password=X", f"password={CANARY}"),
        ("password: X", f"password: {CANARY}"),
        ("password X (bare)", f"password {CANARY}"),
        ("token=X", f"token={CANARY}"),
    ):
        out = sanitize_text(text)
        _rec(f"existing form '{label}' still redacts",
             CANARY not in out and "[REDACTED]" in out, out)

    # ---------- numbers unchanged ----------
    out = sanitize_text("card 1234567890123456 end")
    _rec("16-digit run still becomes [REDACTED_NUM]",
         "1234567890123456" not in out and "[REDACTED_NUM]" in out, out)
    out = sanitize_text("call me at 5551234567")
    _rec("10-digit number untouched (12+ contract)",
         out == "call me at 5551234567", out)

    # ---------- ordinary text untouched ----------
    plain = "a perfectly ordinary sentence about gardening"
    _rec("ordinary text byte-identical", sanitize_text(plain) == plain,
         sanitize_text(plain))
    plain2 = "the sky is blue and the grass is green"
    _rec("'is' without a keyword is untouched",
         sanitize_text(plain2) == plain2, sanitize_text(plain2))

    # ---------- Dell 41 leaf surfaces: no canary anywhere ----------
    from form.open import Program
    from form.mandell.execution_observer import observe_seed_execution

    owner = "dd31mainZZ"
    _cleanup(owner)
    p = Program(owner=owner)
    r = observe_seed_execution(p, f"41[Sanitize] :: my password is {CANARY}")
    _rec("copula seed executes ok", r.get("ok") is True, str(r.get("error")))
    blobs = {
        "result": json.dumps(r, default=str),
        "messages": "\n".join(str(m) for m in r.get("messages", [])),
        "history": json.dumps(list(p.history), default=str),
    }
    for name, blob in blobs.items():
        _rec(f"canary absent from leaf {name}", CANARY not in blob)
    _rec("Sanitize out line present and redacted",
         any(m.startswith("Sanitize out:") and "[REDACTED]" in m
             for m in r.get("messages", [])), str(r.get("messages", [])))
    _cleanup(owner)

    leftovers = []
    base = os.path.join(_ROOT, "form", "state")
    if os.path.isdir(base):
        leftovers = [f for f in os.listdir(base) if "dd31" in f.lower()]
    _rec("cleanup leaves no residue", leftovers == [], str(leftovers))

    passed = sum(1 for _, ok_, _ in RESULTS if ok_)
    for name, ok_, detail in RESULTS:
        if not ok_:
            print(f"FAIL {name}: {detail}")
    print(f"DD31_SANITIZE_COPULA: {passed}/{len(RESULTS)}")
    return passed == len(RESULTS) and len(RESULTS) > 0


def smoke():
    return main()


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
