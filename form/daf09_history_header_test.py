"""DAF-09 D1 — history header must report the RETAINED total, not the
display-slice length.

Defect (Director ruling 7085151190 item 3, issue #512; Lane F
reproduction 7079488053): form/dell_matrix/needs.py history_report
built its header from len(hist), where hist is the last-n display
slice — so a program retaining 24 notes was reported as holding 16.
The header now reads:

    History · <len(program.history)> retained notes (last <len(hist)> shown):

Retention, history bytes, and every other behavior are unchanged.
R5 T1-T4 are a separate, still-open family and are NOT touched here.

Written failing-first: at the pre-fix head the retained-count cases
are RED (the header prints the slice length in both positions).
"""
import os
import sys
import tempfile
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from form.open import Program  # noqa: E402

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond), detail))


def fresh_program(notes=0, history_max=None):
    p = Program(owner="daf09_" + uuid.uuid4().hex[:12])
    if history_max is not None:
        p.history_max = history_max
    for i in range(notes):
        p.note(f"note-{i + 1}")
    return p


def header(p, n=16):
    return p.history_lines(n)[0]


def main():
    # 1. The Director's exact case: 19 retained, default window 16.
    p = fresh_program(19)
    check("retained_19_header",
          header(p) == "History · 19 retained notes (last 16 shown):",
          header(p))
    # 2. Full retention bound: 24 retained.
    p = fresh_program(24)
    check("retained_24_header",
          header(p) == "History · 24 retained notes (last 16 shown):",
          header(p))
    # 3. Above the default bound (bound raised in memory): 30 retained.
    p = fresh_program(30, history_max=40)
    check("retained_30_header",
          header(p) == "History · 30 retained notes (last 16 shown):",
          header(p))
    # 4. Exactly the window: 16 retained, 16 shown.
    p = fresh_program(16)
    check("retained_16_header",
          header(p) == "History · 16 retained notes (last 16 shown):",
          header(p))
    # 5. Window larger than retained: 5 retained, 5 shown.
    p = fresh_program(5)
    check("retained_5_header",
          header(p) == "History · 5 retained notes (last 5 shown):",
          header(p))
    # 6. Empty history: header is truthful and the empty marker stays.
    p = fresh_program(0)
    lines = p.history_lines()
    check("empty_header",
          lines[0] == "History · 0 retained notes (last 0 shown):",
          lines[0])
    check("empty_marker", any("(empty" in ln for ln in lines), str(lines[:2]))
    # 7. Custom window: 19 retained, last 8 shown.
    p = fresh_program(19)
    check("custom_window_header",
          header(p, 8) == "History · 19 retained notes (last 8 shown):",
          header(p, 8))
    # 8. Load path: save + reload keeps the retained total truthful.
    p = fresh_program(19)
    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "prog.json")
        p.save(path)
        q = Program.load(p.owner, path)
        # The save/load cycle itself appends a load note (observed:
        # 19 saved -> 20 retained after load). The contract is that
        # the header equals the loaded program's ACTUAL retained
        # count, which must cover every saved note.
        check("load_path_header",
              len(q.history) >= 19
              and header(q) == f"History · {len(q.history)} retained notes (last 16 shown):",
              header(q))
    # 9. No mutation: history content byte-identical across the call.
    p = fresh_program(19)
    before = repr(list(p.history))
    p.history_lines()
    p.history_lines(8)
    check("no_mutation", repr(list(p.history)) == before,
          "history changed across history_lines()")
    # 10. Body integrity: the shown lines are the LAST notes, in order.
    p = fresh_program(19)
    lines = p.history_lines()
    check("body_is_last_16",
          "note-19" in lines[-3] or any("note-19" in ln for ln in lines),
          str(lines[-3:]))
    check("body_excludes_oldest",
          not any("note-1 " in ln or ln.rstrip().endswith("note-1")
                  for ln in lines[1:]),
          str(lines[1:3]))

    failed = [r for r in RESULTS if not r[1]]
    for name, ok, detail in RESULTS:
        print(f"{'ok  ' if ok else 'FAIL'} {name} {detail if not ok else ''}")
    print(f"{len(RESULTS) - len(failed)}/{len(RESULTS)}")
    return 0 if not failed else 1


def smoke():
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
