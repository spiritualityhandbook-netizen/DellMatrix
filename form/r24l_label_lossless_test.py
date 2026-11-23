"""R24-L — create-door label losslessness (Director 7098988693).

Defect (Lane C package 7098540189, reproduced at main 88659c49):
`form/idea_create.py` sliced the authored label at 80 chars
(`label[:80]` in parse_create_line, reached via needs.parse_and_place),
so a 122-char authored label persisted as exactly 80 in the saved
state file and the create receipt printed the cut label as if
authored — no refusal, no disclosure.

Contract (no silent truncation, mirroring the canonical label law):
the system's documented label budget is 200 chars — Nursery Q-S2.1
(MAX_LABEL_CHARS = 200, NurseryLabelError BEFORE mutation) and the
inference dock's identical bound, both of which repudiated the
historical label[:80] silent cut as destroying admitted content.
So at the public create door:
  - labels up to 200 chars persist byte-exact and the receipt prints
    the authored label whole;
  - a label over 200 chars is refused with a typed, visible refusal
    BEFORE any mutation — nothing is placed, nothing persists.

Every case drives the PUBLIC door (piped `python3 -m form.repl`),
then reads the persisted state file bytes (plane.units labels).
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = []


def rec(name, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" | {detail}" if detail and not ok else ""))
    RESULTS.append((name, bool(ok)))


def _label(prefix, n):
    return prefix + "x" * (n - len(prefix))


def _session(owner, lines, load=False):
    argv = [sys.executable, "-B", "-m", "form.repl", "--owner", owner]
    if load:
        argv.append("--load")
    p = subprocess.run(argv, input="\n".join(lines) + "\n",
                       capture_output=True, text=True, cwd=str(ROOT),
                       timeout=280)
    return p.stdout + p.stderr


def _persisted_labels(owner):
    f = ROOT / "form" / "state" / f"program_{owner}.json"
    if not f.exists():
        return []
    d = json.loads(f.read_text())
    units = ((d.get("plane") or {}).get("units") or {})
    return [str(u.get("label") or "") for u in units.values()]


def _create_case(owner, label, *, quoted=False, strong=False):
    shown = f"'{label}'" if quoted else label
    line = f"create an idea called {shown}"
    if strong:
        line += " detail: a detailed purpose for this idea goals: first goal; second goal"
    out = _session(owner, [line, "save"])
    return out


def _state_text(owner):
    f = ROOT / "form" / "state" / f"program_{owner}.json"
    return f.read_text() if f.exists() else ""


def _counters(p):
    from form.dell_matrix import needs as _needs
    try:
        props = p.list_proposals()
    except Exception:
        props = []
    try:
        undo = len(_needs._stack(p))
    except Exception:
        undo = -1
    return {
        "units": len(p.cube.session.plane.units),
        "proposals": len(props),
        "outcome_ledger": len(getattr(p, "outcome_ledger", []) or []),
        "duo_ledger": len(getattr(getattr(p, "duo", None), "ledger", []) or []),
        "history": len(getattr(p, "history", []) or []),
        "undo": undo,
    }


def _e12_cases():
    """E-1/E-2 refusal-truth cases (Director 7100595543).

    The R24-L refusal itself is honest at needs.parse_and_place, but
    two callers dressed it as success: the live_visual create arm
    wrapped ANY result as {"ok": True, ..., "end": "create_strong"}
    (so HTTP /cmd answered 200 and the envelope embedded the full
    refused label), and both REPL observer sites persisted a
    "Created idea: ..." outcome message for a refused create.
    These cases pin the caller behavior, not the refusal itself.
    """
    import urllib.error
    import urllib.request

    from form.open import open_program
    from form.dell_matrix.needs import parse_and_place, format_create_end
    from form.dell_matrix import live_visual
    from form.dell_matrix.live_visual import _run_command

    lab201 = _label("CaseOverBudget", 201)
    line201 = f"create an idea called {lab201} detail: x goals: y"
    lab150 = _label("CaseControlE12", 150)
    line150 = f"create an idea called {lab150} detail: x goals: y"

    p = open_program("R24LE12P")
    base = _counters(p)

    # parse_and_place: typed refusal, zero mutation.
    res = parse_and_place(p, line201)
    rec("E12 parse_and_place 201: typed refusal (ok False, label_over_budget)",
        res.get("ok") is False and res.get("error") == "label_over_budget")
    rec("E12 parse_and_place 201: zero mutation (units/proposals/outcomes/history/undo)",
        _counters(p) == base, f"base={base} after={_counters(p)}")

    # Program.create_strong: same refusal through the passthrough.
    res_b = p.create_strong(line201)
    rec("E12 create_strong 201: typed refusal (ok False, label_over_budget)",
        res_b.get("ok") is False and res_b.get("error") == "label_over_budget")
    rec("E12 create_strong 201: zero mutation",
        _counters(p) == base)

    # live _run_command envelope: refusal must stay a refusal.
    env = _run_command(p, line201)
    rec("E12 live envelope 201: outer ok False + typed error + no create_strong end",
        env.get("ok") is False and env.get("error") == "label_over_budget"
        and env.get("end") != "create_strong",
        f"ok={env.get('ok')} error={env.get('error')} end={env.get('end')}")
    rec("E12 live envelope 201: human-readable refusal preserved in msg",
        "Create refused" in (env.get("msg") or "") and "200" in (env.get("msg") or ""))
    # Echo scope: the refusal-specific payload is the arm's own result
    # (ok/error/msg/create/end). The generic "command" echo and the
    # "state" UI payload are attached to EVERY _run_command result by
    # the shared finalizer (Lane E classified the raw-command history
    # as common input logging, not refusal carriage); the E-1 echo
    # being removed is the one inside the refusal result itself.
    def _refusal_payload(e):
        return json.dumps({k: e.get(k) for k in ("ok", "error", "msg", "create", "end")})

    blob = _refusal_payload(env)
    rec("E12 live envelope 201: no full over-budget label echo in the refusal payload",
        lab201 not in blob and "label" not in (env.get("create") or {})
        and "report" not in (env.get("create") or {}),
        f"refusal payload embeds the refused label (len={len(blob)})")
    rec("E12 live envelope 201: zero mutation", _counters(p) == base)

    # Echo bound: a 5000-char label must not inflate the refusal payload.
    lab_big = "Z" * 5000
    env_big = _run_command(p, f"create an idea called {lab_big}")
    blob_big = _refusal_payload(env_big)
    rec("E12 live envelope 5000-char label: echo bounded (no label, payload < 1200 chars)",
        lab_big not in blob_big and len(blob_big) < 1200,
        f"refusal payload len={len(blob_big)}")
    rec("E12 live envelope 5000-char label: zero mutation", _counters(p) == base)

    # Success control through the same wrapper: behavior preserved.
    env_ok = _run_command(p, line150)
    res_ok = parse_and_place(open_program("R24LE12Q"), line150)
    rec("E12 live envelope success: ok True, end create_strong, msg == format_create_end(res)",
        env_ok.get("ok") is True and env_ok.get("end") == "create_strong"
        and env_ok.get("msg") == format_create_end(res_ok),
        f"ok={env_ok.get('ok')} end={env_ok.get('end')}")
    rec("E12 live envelope success: the control create placed exactly one unit",
        _counters(p)["units"] == base["units"] + 1)

    # HTTP /cmd: status follows the real ok.
    port = 18900 + (process_pid() % 60)
    info = live_visual.start_live(p, port=port, background=True)
    rec("E12 HTTP: live server started for /cmd probes", bool(info.get("ok")), str(info)[:120])
    if info.get("ok"):
        try:
            actual = live_visual._LIVE_SERVER.server_address[1]

            def _post(cmd):
                req = urllib.request.Request(
                    f"http://127.0.0.1:{actual}/cmd",
                    data=json.dumps({"cmd": cmd}).encode(),
                    headers={"Content-Type": "application/json"}, method="POST")
                try:
                    with urllib.request.urlopen(req, timeout=30) as r:
                        return r.status, json.loads(r.read().decode())
                except urllib.error.HTTPError as e:
                    return e.code, json.loads(e.read().decode())

            status, body = _post(line201)
            rec("E12 HTTP /cmd 201: non-2xx status, body ok False + typed error, no label echo in create payload",
                status >= 300 and body.get("ok") is False
                and body.get("error") == "label_over_budget"
                and lab201 not in json.dumps(body.get("create") or {}),
                f"status={status} ok={body.get('ok')} error={body.get('error')}")
            status2, body2 = _post(line150)
            rec("E12 HTTP /cmd success: 200, body ok True",
                status2 == 200 and body2.get("ok") is True,
                f"status={status2} ok={body2.get('ok')}")
        finally:
            try:
                live_visual._LIVE_SERVER.shutdown()
                live_visual._LIVE_SERVER.server_close()
            except Exception:
                pass

    # REPL door A (raw-line create arm): no fake Created observer message.
    out_a = _create_case("R24LE12A", lab201)
    text_a = _state_text("R24LE12A")
    rec("E12 REPL door A 201: refusal printed at the door",
        "refus" in out_a.lower())
    rec("E12 REPL door A 201: NO fake 'Created idea' observer message persisted",
        f"Created idea: {lab201[:60]}" not in text_a,
        "persisted outcome message claims a creation for a refused label")
    rec("E12 REPL door A 201: honest failed outcome persisted (label_over_budget)",
        "label_over_budget" in text_a)

    # REPL door B (intent-routed place arm): same observer contract.
    out_b = _session("R24LE12B",
                     [f"please create an idea called {lab201} detail: x goals: y", "save"])
    text_b = _state_text("R24LE12B")
    rec("E12 REPL door B 201: refusal printed at the door",
        "refus" in out_b.lower())
    rec("E12 REPL door B 201: NO fake 'Created idea' observer message persisted",
        f"Created idea: {lab201[:60]}" not in text_b,
        "persisted outcome message claims a creation for a refused label")
    rec("E12 REPL door B 201: honest failed outcome persisted (label_over_budget)",
        "label_over_budget" in text_b)

    # Success control: a lawful create still records its normal message.
    lab_ok = "KeeperControlE12"
    _create_case("R24LE12C", lab_ok)
    text_c = _state_text("R24LE12C")
    rec("E12 REPL success: normal 'Created idea' observer message still persisted",
        f"Created idea: {lab_ok} id=" in text_c)


def process_pid():
    import os
    return os.getpid()


def smoke() -> bool:
    RESULTS.clear()

    # Control: exactly 80 chars — whole at main already.
    lab80 = _label("CaseEighty", 80)
    out = _create_case("R24L80", lab80)
    rec("80-char label: receipt prints the authored label whole",
        f'Created idea: "{lab80}"' in out)
    rec("80-char label: persisted byte-exact",
        lab80 in _persisted_labels("R24L80"))

    # 81 chars — one past the old silent cut.
    lab81 = _label("CaseEightyOne", 81)
    out = _create_case("R24L81", lab81)
    rec("81-char label: receipt prints the authored label whole",
        f'Created idea: "{lab81}"' in out,
        "receipt cut or missing")
    rec("81-char label: persisted byte-exact",
        lab81 in _persisted_labels("R24L81"),
        f"persisted={[len(x) for x in _persisted_labels('R24L81')]}")

    # 122 chars unquoted — the Lane C case.
    lab122 = _label("BoundaryLong", 122)
    out = _create_case("R24L122", lab122)
    rec("122-char label: receipt prints the authored label whole",
        f'Created idea: "{lab122}"' in out)
    rec("122-char label: persisted byte-exact",
        lab122 in _persisted_labels("R24L122"),
        f"persisted={[len(x) for x in _persisted_labels('R24L122')]}")
    # Cold reload: a fresh process loading the saved state shows it whole.
    out2 = _session("R24L122", ["proposals browse"], load=True)
    rec("122-char label: whole after cold reload",
        lab122 in out2, "reloaded surface shows the cut label only")

    # 122 chars quoted — wrapper quotes stripped, content whole.
    out = _create_case("R24L122Q", lab122, quoted=True)
    rec("122-char quoted label: receipt prints the authored label whole",
        f'Created idea: "{lab122}"' in out)
    rec("122-char quoted label: persisted byte-exact",
        lab122 in _persisted_labels("R24L122Q"))

    # 122 chars, strong form (detail:/goals: present).
    out = _create_case("R24L122S", lab122, strong=True)
    rec("122-char strong-form label: persisted byte-exact",
        lab122 in _persisted_labels("R24L122S"),
        f"persisted={[len(x) for x in _persisted_labels('R24L122S')]}")

    # 200 chars — the canonical budget boundary: preserved whole.
    lab200 = _label("CaseBudgetEdge", 200)
    out = _create_case("R24L200", lab200)
    rec("200-char label (canonical budget): receipt whole",
        f'Created idea: "{lab200}"' in out)
    rec("200-char label (canonical budget): persisted byte-exact",
        lab200 in _persisted_labels("R24L200"),
        f"persisted={[len(x) for x in _persisted_labels('R24L200')]}")

    # 201 chars — over budget: typed visible refusal BEFORE mutation.
    lab201 = _label("CaseOverBudget", 201)
    out = _create_case("R24L201", lab201)
    low = out.lower()
    rec("201-char label: no creation is claimed",
        f'Created idea: "{lab201}"' not in out
        and f'Created idea: "{lab201[:80]}"' not in out,
        "a Created receipt was printed for an over-budget label")
    rec("201-char label: refusal is visible and names the 200 bound",
        "refus" in low and "200" in out,
        "no refusal text naming the bound in the door output")
    persisted = _persisted_labels("R24L201")
    rec("201-char label: nothing persisted (no whole, no cut copy)",
        lab201 not in persisted and lab201[:80] not in persisted,
        f"persisted={[len(x) for x in persisted]}")

    # Cold reload at the acceptance boundaries (80/81/200): a fresh
    # process loading the saved state shows each label whole.
    for owner, lab, tag in (("R24L80", lab80, "80"), ("R24L81", lab81, "81"),
                            ("R24L200", lab200, "200")):
        out_r = _session(owner, ["proposals browse"], load=True)
        rec(f"{tag}-char label: whole after cold reload (fresh process)",
            lab in out_r, "reloaded surface shows the cut label only")

    # E-1/E-2: the refusal must stay a refusal through every caller.
    _e12_cases()

    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"R24L LABEL LOSSLESS: {passed}/{len(RESULTS)} PASS")
    return all(ok for _, ok in RESULTS)


if __name__ == "__main__":
    raise SystemExit(0 if smoke() else 1)
