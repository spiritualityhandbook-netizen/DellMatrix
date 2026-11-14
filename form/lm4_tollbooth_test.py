#!/usr/bin/env python3
"""LM-4 THE TOLL BOOTH -- contracts for the wired LatinMandell pass
(LatinMandell plan SS15, circuit LM-4; grounding
hidden_files/lm4_ground/GROUNDING.md; Ace build-all order
2026-11-13 11:02 CST).

Contracts proven here:

- ONE TRANSLATOR, EXTENDED: form/mandell/translate.py translate()
  computes the LatinMandell decomposition ONCE at entry (after the
  empty guard) and attaches it to EVERY returned Intent through a
  single-exit wrapper (the pre-LM-4 body is _translate_body(); its
  segmentation recursion calls the BODY, so segments never mint
  their own receipts). No second translator, no parallel path.
  T3 is the anti-silent-reopen pin: any future early return added
  outside the wrapper fails it.
- compose_sentence (form/mandell/morpheme.py, beside compose_word)
  aggregates per-token compose receipts + census classes + the
  FUNCTION spine. The spine is DIAGNOSTIC ONLY (grounding conflict
  C2): routing/Dell selection is PROVABLY unchanged (T15 pins the
  pre-LM-4 baseline recorded at base d9d4926c). The Q-LM3.5
  diagnostic rides the receipt (structural_role / structural_dell
  vs governing_dell + dell_agree); disagreements print, never
  re-route. Curated definitions govern; the composed stack is
  printed beside (Ace's shadow doctrine).
- Q-LM3.6 NAMING at the combined boundary: semantic_accounted
  (sentence) / word_char_accounted (word, relabeled at aggregation
  ONLY) / sentence_morpheme_resolved (sentence roll-up). The
  LM-2/LM-3 word-level `accounted` / `morpheme_resolved` fields
  are untouched (T5).
- OPERAND HONESTY: a token captured as user data by translate's
  arms (label/id/key/source/... argument VALUES; the echo fields
  `raw`/`query` excluded) is marked OPERAND on the receipt --
  traced, but excluded from the spine and from Dell agreement.
- PRESENTATION (Ace routing, 2026-11-13): gloss-style
  decomposition lines (deeper information); the executed chain
  and the labeled spine reading in Mandell (directive); the
  existing English echoes remain the explanation layer.
- THE WIRED PATH = the public REPL path + the translator funnel
  (grounding bypass census B1-B12). B1/B2/B3/B4/B6 close by
  construction; B5 (Mandell seeds) and B8 (raw-line intercepts)
  stay open BY DESIGN and the suite pins the discrimination:
  no trace where no English was read (T19), no trace for an
  execution LatinMandell did not precede (T20).
- DOCKED PATH: DockedSession._verb attaches an "lm" decomposition
  block to each [targets] entry (computed from the SNAPSHOT text)
  and propose() appends a [decomposition] block to the prompt --
  in both cases BEFORE the prompt bound check and the protected
  screen, so decomposition can never become a screen bypass
  (T23) and the input arrives already broken. (Base fact the
  grounding's T23 sketch missed: the field SNAPSHOT already
  redacts handle-format values to "[REDACTED]" before _verb sees
  them, so the verbatim screen pin lives on propose(), whose
  caller text IS screened assembled -- r62 D1's proven surface.)
- FAIL-CLOSED (T26): a PairInconsistentError from the LM table
  loader propagates out of translate() -- never a silent
  execute-without-receipt. (The propagate-vs-honest-unknown
  choice is Q-LM4.4, pending the Director; this build propagates,
  matching the LM-2/LM-3 loader contract.)

Checks access the LM-4 surface through getattr guards so the
suite runs to completion against the UNMODIFIED base (the
failing-first RED log: feature checks FAIL, control checks
T15/T19/T20/T23/T25 PASS -- the behavior LM-4 must not move).

Evidence labels: A = INTEGRATION (module path); B = HIGH-FIDELITY
DISPATCH (_dispatch_public_line, the IRI-I harness pattern) plus
one REAL_USER_PATH subprocess battery (T18); C = INTEGRATION
(scripted FakeProvider, the dock_wall harness pattern);
D = non-regression pins.
"""

from __future__ import annotations

import contextlib
import glob
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import uuid

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from form.mandell import latinmandell, lm_table, morpheme  # noqa: E402
from form.mandell.translate import translate  # noqa: E402
from form.open import Program, open_program  # noqa: E402
from form import repl as repl_mod  # noqa: E402


# ------------------------------------------------------------------
# helpers

def _cleanup(owner):
    """Canonical state-path cleanup; a cleanup failure FAILS the
    suite (never except-pass)."""
    state = os.path.join(_HERE, "state")
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
    ideas_dir = os.path.join(state, f"ideas_{owner}")
    try:
        shutil.rmtree(ideas_dir)
    except FileNotFoundError:
        pass
    except OSError as e:
        raise RuntimeError(f"cleanup failed for {ideas_dir}: {e}")


def _dispatch(p, line):
    """One public REPL turn (IRI-I harness): _say capture + stdout
    capture, through _dispatch_public_line itself."""
    buf = io.StringIO()
    old = repl_mod._say
    repl_mod._say = lambda s: buf.write(str(s) + "\n")
    try:
        sink = io.StringIO()
        with contextlib.redirect_stdout(sink):
            p2 = repl_mod._dispatch_public_line(p, line, str(uuid.uuid4()))
        printed = sink.getvalue()
    finally:
        repl_mod._say = old
    return p2, buf.getvalue() + printed


def _lm_lines(out):
    return [ln for ln in out.splitlines() if ln.startswith("LM:")]


def _sent(intent):
    """The Intent's sentence receipt, or {} when LM-4 is absent."""
    lm = getattr(intent, "lm", None)
    if not isinstance(lm, dict):
        return {}
    s = lm.get("sentence")
    return s if isinstance(s, dict) else {}


def _pres(intent):
    lm = getattr(intent, "lm", None)
    if not isinstance(lm, dict):
        return {}
    pr = lm.get("presentation")
    return pr if isinstance(pr, dict) else {}


def _tokens(sentence):
    return {t["token"]: t for t in sentence.get("tokens") or []}


# T15 baseline: (action, dell, mandel) recorded from the UNMODIFIED
# base (d9d4926c) before the LM-4 build -- translation behavior is
# evidence, not a casualty.
_T15_BASELINE = {
    "status": ("status", None, "35[Discover]"),
    "grow": ("grow", None, "13[Loop] > 04[Transform] :: grow"),
    "create an idea called biology": (
        "place", None, '08[Create](name="biology") > 15[Map] :: biology'),
    "walk forward": ("walk", None, "19[Drive] :: walk"),
    "turn left": ("turn", None, "04[Transform] :: turn_left"),
    "dell 74": ("weight", 74, "74[Weight]"),
    "flibberty nonsense words": ("unknown", 9, "09[Show] :: unknown"),
    "stamp victory": ("stamp", 34, "34[Stamp] :: victory"),
    "measure": ("measure", None, "40[TokenCount]"),
    "save": ("save", None, "10[Keep]"),
}


def smoke() -> bool:
    print("=== LM-4 TOLL BOOTH SMOKE ===")
    r = []

    def rec(name, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {name}")
        r.append(bool(ok))

    # compose_sentence via getattr: absent at the pre-LM-4 base.
    compose_sentence = getattr(
        morpheme, "compose_sentence",
        lambda _text: {"tokens": [], "spine": [], "dell": None})

    # ================= A. decomposition exists and is honest =====
    # T1: receipt exists; sentence text is the input verbatim.
    i1 = translate("status")
    lm1 = getattr(i1, "lm", None)
    rec("T1 translate('status') carries an lm receipt, text verbatim",
        isinstance(lm1, dict)
        and _sent(i1).get("text") == "status")

    # T2: every token exactly once, census + UNRESOLVED included.
    s2 = _sent(translate("transform the zqxjk idea"))
    rec("T2 all 4 tokens present exactly once (incl. census + "
        "UNRESOLVED)",
        [t["token"] for t in s2.get("tokens") or []]
        == ["transform", "the", "zqxjk", "idea"])

    # T3: structural closure across translate's branches.
    battery3 = {
        "loss-guard": "if the idea is stale delete it",
        "sequence": "status then measure",
        "phrase": "show me",
        "operational": "list outcomes",
        "create": "create an idea called biology",
        "core2": "dell 74",
        "save-fallback": "save",
        "stamp-arm": "stamp victory",
        "get-arm": "get the brass key",
        "grow-arm": "grow",
        "turn-arm": "turn left",
        "unknown": "flibberty nonsense words",
    }
    ok3 = True
    for _branch, line in battery3.items():
        if _sent(translate(line)).get("text") != line:
            ok3 = False
    rec("T3 every branch's Intent carries a receipt (12 inputs)",
        ok3)

    # T4: empty input mints NO receipt.
    i4 = translate("")
    rec("T4 empty input: nothing_to_translate, no receipt minted",
        i4.action == "nothing_to_translate"
        and getattr(i4, "lm", None) is None)

    # T5: Q-LM3.6 naming at the combined boundary.
    s5 = _sent(translate("transform the incredible idea"))
    w5 = morpheme.compose_word("incredible")
    rec("T5 semantic_accounted + per-word word_char_accounted; no "
        "bare sentence 'accounted'; word fields untouched",
        "semantic_accounted" in s5
        and "accounted" not in s5
        and all("word_char_accounted" in t
                for t in s5.get("tokens") or [])
        and _tokens(s5).get("incredible", {}).get(
            "word_char_accounted") == 0.2
        and w5["accounted"] == 0.2
        and w5["morpheme_resolved"] == 0.5)

    # T6: the two names measure two things (numeric proof).
    sa6 = s5.get("semantic_accounted")
    smr6 = s5.get("sentence_morpheme_resolved")
    rec("T6 semantic_accounted=1.0 while the PARTIAL word's char "
        "accounting is 0.2 and sentence_morpheme_resolved=5/6",
        sa6 == 1.0 and smr6 is not None
        and abs(smr6 - (2.5 / 3.0)) < 1e-9
        and smr6 < sa6)

    # T7: sentence_morpheme_resolved rolls up CONTENT tokens only.
    rec("T7 sentence_morpheme_resolved excludes census tokens from "
        "its denominator",
        smr6 is not None and abs(smr6 - (2.5 / 3.0)) < 1e-9
        and (_tokens(s5).get("transform", {}).get("compose") or {}
             ).get("morpheme_resolved") == 1.0)

    # T8: Q-LM3.5 diagnostic -- one side absent is STATED (None).
    t8 = _tokens(compose_sentence("transform the idea")).get(
        "transform", {})
    rec("T8 'transform': structural_role prefix+root, governing 4, "
        "structural None, agree None",
        t8.get("structural_role") == "prefix+root"
        and t8.get("governing_dell") == 4
        and t8.get("structural_dell") is None
        and t8.get("dell_agree") is None)

    # T9: Q-LM3.5 disagreement via the real customize authority.
    try:
        latinmandell.customize("idea", dell=9,
                               sense="LM-4 test custom binding")
        t9 = _tokens(compose_sentence("the idea")).get("idea", {})
        pres9 = _pres(translate("the idea")).get("gloss") or []
        ok9 = (t9.get("governing_dell") == 9
               and t9.get("structural_dell") == 8
               and t9.get("dell_agree") is False
               and any("structural Dell 08" in g for g in pres9))
    finally:
        latinmandell.clear_customs()
    rec("T9 custom-governed 9 vs structural candidate 8: agree "
        "False, both values on the receipt + diagnostic printed",
        ok9)

    # T10: the spine -- FUNCTION tokens only, census excluded; a
    # two-Dell spine fabricates NO sentence Dell.
    s10 = compose_sentence("transform the idea")
    rec("T10 spine == [transform->04 curated, idea->08 curated]; "
        "'the' excluded; sentence dell None",
        s10.get("spine") == [
            {"token": "transform", "dell": 4, "via": "curated"},
            {"token": "idea", "dell": 8, "via": "curated"}]
        and s10.get("dell") is None)

    # T11: operand honesty (biology is DATA, not directive).
    i11 = translate("create an idea called biology")
    s11 = _sent(i11)
    t11 = _tokens(s11).get("biology", {})
    rec("T11 'biology' is OPERAND: traced, out of the spine; the "
        "place routing is exactly the baseline",
        t11.get("class") == "OPERAND" and t11.get("role") == "operand"
        and "biology" not in [e["token"] for e in s11.get("spine") or []]
        and i11.action == "place"
        and i11.mandel
        == '08[Create](name="biology") > 15[Map] :: biology')

    # T12: UNRESOLVED flows through -- never dropped, never faked.
    s12 = _sent(translate("transform the zqxjk idea"))
    t12 = _tokens(s12).get("zqxjk", {})
    rec("T12 nonsense token UNRESOLVED in tokens, out of spine, "
        "semantic_accounted 3/4",
        t12.get("class") == "UNRESOLVED"
        and t12.get("role") == "unresolved"
        and (t12.get("compose") or {}).get("gloss_state")
        == "UNRESOLVED"
        and "zqxjk" not in [e["token"] for e in s12.get("spine") or []]
        and s12.get("semantic_accounted") == 0.75)

    # ================= B. the wired path end-to-end ===============
    # T13: dispatch trace (direct arm) + route receipt (routed arm).
    owner = "LM4TollT13"
    _cleanup(owner)
    try:
        p = Program(owner=owner)
        p, out_status = _dispatch(p, "status")
        p, out_grow = _dispatch(p, "grow")
        ok13 = ("LM:" in out_status
                and "semantic_accounted" in out_status
                and "ideas=" in out_status
                and "LM:" in out_grow
                and "ROUTE:" in out_grow
                and "RESULT: ok=True" in out_grow)
    finally:
        _cleanup(owner)
    rec("T13 dispatched English shows the gloss trace; the routed "
        "arm's route receipt carries it too", ok13)

    # T14: determinism of the trace.
    owners = ["LM4TollT14A", "LM4TollT14B"]
    traces = []
    try:
        for ow in owners:
            _cleanup(ow)
            pp = Program(owner=ow)
            pp, oo = _dispatch(pp, "status")
            traces.append(_lm_lines(oo))
        ok14 = bool(traces[0]) and traces[0] == traces[1]
    finally:
        for ow in owners:
            _cleanup(ow)
    rec("T14 identical fresh state: byte-identical gloss blocks",
        ok14)

    # T15: routed action/dell/mandel UNCHANGED vs the base baseline.
    ok15 = True
    for line, (a, d, m) in _T15_BASELINE.items():
        ii = translate(line)
        if (ii.action, ii.dell, ii.mandel) != (a, d, m):
            ok15 = False
    rec("T15 routing unchanged on the 10-line baseline battery "
        "(spine is diagnostic only)", ok15)

    # T16: sequence path -- per-clause decompositions ride the
    # composite receipt; the same chain executes.
    owner = "LM4TollT16"
    _cleanup(owner)
    try:
        p = Program(owner=owner)
        p, out16 = _dispatch(p, "status and then measure")
        ok16 = ("clause 1" in out16 and "clause 2" in out16
                and "LM:" in out16 and "completed=2" in out16)
    finally:
        _cleanup(owner)
    rec("T16 composite receipt carries per-clause decompositions; "
        "chain executes as today", ok16)

    # T17: the loss guard still refuses; the trace shows the
    # decomposition WITH the refusal; nothing executes.
    owner = "LM4TollT17"
    _cleanup(owner)
    try:
        p = Program(owner=owner)
        units0 = len(p.cube.session.plane.units)
        p, out17 = _dispatch(p, "if the idea is stale delete it")
        ok17 = ("Not understood" in out17 and "LM:" in out17
                and len(p.cube.session.plane.units) == units0
                and len(p.nursery.proposals) == 0)
    finally:
        _cleanup(owner)
    rec("T17 loss-guard refusal intact, traced, zero execution",
        ok17)

    # T18: REAL_USER_PATH subprocess battery.
    owner = "LM4TollT18"
    _cleanup(owner)
    try:
        env = {**os.environ, "PYTHONPATH": _ROOT}
        r1 = subprocess.run(
            [sys.executable, "-m", "form.repl", "--owner", owner],
            cwd=_ROOT, env=env,
            input="create an idea called biology\nstatus\nsave\nquit\n",
            capture_output=True, text=True, timeout=180)
        r2 = subprocess.run(
            [sys.executable, "-m", "form.repl", "--owner", owner,
             "--load"],
            cwd=_ROOT, env=env, input="status\nquit\n",
            capture_output=True, text=True, timeout=180)
        ok18 = (r1.returncode == 0 and "LM:" in r1.stdout
                and "OPERAND" in r1.stdout
                and r2.returncode == 0 and "ideas=2" in r2.stdout)
    finally:
        _cleanup(owner)
    rec("T18 subprocess REPL: gloss trace with biology as OPERAND; "
        "second --load process verifies persistence", ok18)

    # T19: B5 discrimination -- a Mandell seed gets NO trace.
    owner = "LM4TollT19"
    _cleanup(owner)
    try:
        p = Program(owner=owner)
        p, out19 = _dispatch(p, "08[Create] :: x")
        ok19 = "LM:" not in out19 and "Created idea" in out19
    finally:
        _cleanup(owner)
    rec("T19 seed line: NO LM trace (Mandell is not English), "
        "executes exactly as today", ok19)

    # T20: B8 intercept honesty -- 'evolve' never consumes the
    # Intent, so no trace may print for it.
    owner = "LM4TollT20"
    _cleanup(owner)
    try:
        p = Program(owner=owner)
        p, out20 = _dispatch(p, "evolve")
        ok20 = "LM:" not in out20 and "Evolved" in out20
    finally:
        _cleanup(owner)
    rec("T20 program-evolve intercept: NO LM trace (the Intent "
        "never executes)", ok20)

    # ================= C. the docked seam =========================
    from form.dell_matrix import inference_dock as idock

    class MaximalJudge(idock.FakeProvider):
        """The dock_wall harness judge: parents = the targets it
        was shown (maximal compliant acceptance)."""

        def generate(self, prompt, *, timeout_s, max_chars):
            self.calls += 1
            self.last_prompt = prompt
            targets = []
            marker = "[targets]\n"
            if marker in prompt:
                raw = prompt.split(marker, 1)[1]
                end = raw.find("\n\n[")
                if end != -1:
                    raw = raw[:end]
                try:
                    entries = json.loads(raw)
                    targets = [e.get("uid") or e.get("pid")
                               for e in entries
                               if isinstance(e, dict)]
                except Exception:
                    targets = []
            return json.dumps({
                "label": "Docked Cross",
                "words": "docked judge synthesis words",
                "detail": "authored from all shown targets",
                "goals": ["probe goal"],
                "reason": "scripted judge accepts all shown targets",
                "parents": targets,
            })

    def _field(owner, bad_words=None):
        _cleanup(owner)
        p = open_program(owner)
        p.place("u_a", "harbor lantern",
                words="harbor lantern craft timber", x=0.0, y=0.0)
        p.place("u_b", "glacier tundra",
                words=bad_words or "glacier tundra obsidian wolf",
                x=1.0, y=0.0)
        sess = idock.dock(p, "agent-a", provider="fake",
                          fake_mode="valid")
        sess._provider = MaximalJudge("valid")
        return p, sess

    def _prompt_entries(sess):
        prompt = sess._provider.last_prompt or ""
        raw = prompt.split("[targets]\n", 1)[1]
        end = raw.find("\n\n[")
        if end != -1:
            raw = raw[:end]
        return json.loads(raw), prompt

    # T21: _verb prompt decomposition from the snapshot text.
    owner = "LM4TollT21"
    try:
        p, sess = _field(owner)
        r21 = sess.relate("u_a", "u_b")
        entries21, prompt21 = _prompt_entries(sess)
        ok21 = (r21.get("ok") is True
                and all("lm" in e for e in entries21)
                and all("label" in e["lm"] and "words" in e["lm"]
                        for e in entries21)
                and "forced first step" in prompt21)
    finally:
        _cleanup(owner)
    rec("T21 relate prompt: every [targets] entry carries an 'lm' "
        "block for label/words; instruction names it", ok21)

    # T22: propose() decomposition block; UNRESOLVED named in it.
    owner = "LM4TollT22"
    _cleanup(owner)
    try:
        p = open_program(owner)
        sess = idock.dock(p, "agent-a", provider="fake",
                          fake_mode="valid")
        r22 = sess.propose("transform the zqxjk idea")
        lp22 = sess._provider.last_prompt or ""
        ok22 = (r22.get("ok") is True
                and "[decomposition]" in lp22
                and "zqxjk" in lp22 and "UNRESOLVED" in lp22)
    finally:
        _cleanup(owner)
    rec("T22 propose prompt carries [decomposition]; UNRESOLVED "
        "pieces named in it", ok22)

    # T23: screen order preserved -- decomposition is never a
    # screen bypass. Two halves, both base-verified: (a) the
    # snapshot already redacts a handle-format value in a target's
    # words to "[REDACTED]", so _verb decomposes the REDACTED
    # snapshot text and the value reaches neither the prompt nor
    # the decomposition; (b) on propose(), whose caller text is
    # screened assembled (r62 D1), the [decomposition] block is
    # appended BEFORE that screen and the refusal still fires
    # with zero provider calls.
    owner = "LM4TollT23"
    try:
        handle = "grant_" + "ab" * 16
        p, sess = _field(owner, bad_words=f"glacier {handle} wolf")
        r23a = sess.relate("u_a", "u_b")
        entries23, prompt23 = _prompt_entries(sess)
        lm23 = json.dumps([e.get("lm") for e in entries23],
                          sort_keys=True)
        ok23a = (r23a.get("ok") is True
                 and all("lm" in e for e in entries23)
                 and handle not in prompt23
                 and handle not in lm23)
        sess23 = idock.dock(p, "agent-a", provider="fake",
                            fake_mode="valid")
        r23b = sess23.propose("transform the idea about " + handle)
        ok23b = (r23b.get("ok") is False
                 and r23b.get("reason") == "protected_input"
                 and sess23._provider.calls == 0)
        ok23 = ok23a and ok23b
    finally:
        _cleanup(owner)
    rec("T23 decomposition never becomes a screen bypass: "
        "snapshot redaction holds through _verb; propose's "
        "assembled screen still refuses protected_input, 0 calls",
        ok23)

    # T24: fake-provider determinism of the decomposition blocks.
    blocks = []
    for ow in ("LM4TollT24A", "LM4TollT24B"):
        try:
            p, sess = _field(ow)
            sess.relate("u_a", "u_b")
            entries24, _pr = _prompt_entries(sess)
            blocks.append(json.dumps(
                [e.get("lm") for e in entries24], sort_keys=True))
        finally:
            _cleanup(ow)
    rec("T24 identical field state: byte-identical 'lm' blocks "
        "across two relate calls",
        len(blocks) == 2 and blocks[0] == blocks[1]
        and blocks[0] != "[null, null]")

    # ================= D. non-regression guards ===================
    # T25: explain surfaces byte-identical to the LM-3 baseline
    # (literals pinned by lm3_composer_test T12 at the LM-3 head).
    rec("T25 format_explain + explain_morphemes byte-identical to "
        "the pre-LM-4 baseline",
        latinmandell.format_explain("transform the idea")
        == "LatinMandell · transform the idea\n"
           "  transform\n"
           "    la: transformare\n"
           "    sense: change form across a boundary  dell=04\n"
           "  idea\n"
           "    la: idea / forma\n"
           "    sense: form held in mind · pattern  dell=08\n"
           "  seeds: 04[Transform] · 08[Create]"
        and morpheme.explain_morphemes("Com-man-dell")["parts"] == [
            {"morpheme": "Com",
             "sense": "together · synthesis · unified",
             "known": True, "kind": "prefix"},
            {"morpheme": "man",
             "sense": "control · hand · execution",
             "known": True, "kind": "prefix"},
            {"morpheme": "dell",
             "sense": "nested unit · operator cell · protected pocket",
             "known": True, "kind": "root"}])

    # T26: fail-closed pair behavior (Q-LM4.4 pinned as PROPAGATE).
    # (a) the wrapper never swallows a decomposition failure;
    import form.mandell.translate as translate_mod
    orig_cs = getattr(translate_mod, "compose_sentence", None)
    ok26a = False
    if orig_cs is not None:
        def _boom(_text):
            raise lm_table.PairInconsistentError("LM-4 T26 seam pin")

        translate_mod.compose_sentence = _boom
        try:
            try:
                translate("status")
                ok26a = False
            except lm_table.PairInconsistentError:
                ok26a = True
        finally:
            translate_mod.compose_sentence = orig_cs
    # (b) the REAL pair, corrupted in a scratch tree: translate()
    # itself raises out of the subprocess -- no Intent, no
    # execute-without-receipt.
    scratch = tempfile.mkdtemp(prefix="lm4_pair_")
    try:
        md_dir = os.path.join(scratch, "form", "mandell")
        shutil.copytree(os.path.join(_HERE, "mandell"), md_dir,
                        ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copy(os.path.join(_HERE, "__init__.py"),
                    os.path.join(scratch, "form", "__init__.py"))
        cpath = os.path.join(md_dir, "lm_table_v2.collisions.json")
        with open(cpath, encoding="utf-8") as f:
            ctext = f.read()
        i = ctext.find("dell")
        with open(cpath, "w", encoding="utf-8") as f:
            f.write(ctext[:i] + "z" + ctext[i + 1:])
        driver = os.path.join(scratch, "driver.py")
        with open(driver, "w", encoding="utf-8") as f:
            f.write(
                "import json\n"
                "try:\n"
                "    from form.mandell.translate import translate\n"
                "    translate('status')\n"
                "    print(json.dumps({'error': None}))\n"
                "except Exception as e:\n"
                "    print(json.dumps({'error': type(e).__name__}))\n")
        proc = subprocess.run(
            [sys.executable, driver], capture_output=True, text=True,
            cwd=scratch,
            env={**os.environ, "PYTHONPATH": scratch})
        out26 = (json.loads(proc.stdout.strip().splitlines()[-1])
                 if proc.returncode == 0 and proc.stdout.strip()
                 else {"driver_error": proc.stderr[-400:]})
        ok26b = out26.get("error") == "PairInconsistentError"
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    rec("T26 broken table pair: translate() propagates "
        "PairInconsistentError (never executes without a receipt)",
        ok26a and ok26b)

    print(f"=== LM-4 TOLLBOOTH: {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
