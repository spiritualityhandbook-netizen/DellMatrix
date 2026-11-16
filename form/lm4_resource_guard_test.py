#!/usr/bin/env python3
"""A4 PRE-DECOMPOSITION RESOURCE GUARD -- contracts for the
bounded chunked LM-4 decomposition in InferenceDock.propose()
(Director fix-first circuit; grounding
hidden_files/a4_resource_guard_ground_2026-11-14_1643.md;
chunking-equivalence record
hidden_files/a4_chunking_equivalence_2026-11-14_1743.md).

The defect (Gate-2 class): propose() checked the raw prompt
against the caller's bound, then decomposed the FULL prompt
(~9.1x expansion for ordinary text) and only afterwards applied
the assembled-length screen -- a 214,200-char prompt paid ~2.2M
chars of decomposition before being refused.

The repair: _lm4_text_block_bounded composes the token stream in
512-token chunks, pools the records, recomputes the sentence
aggregates ONCE through compose_sentence's own aggregate code,
and renders ONCE. While pooling, the pooled tokens' gloss +
diagnostic line lengths accumulate as a running LOWER bound on
the assembled length; the moment the bound is PROVEN exceeded,
composition aborts and propose() returns the same
prompt_too_large refusal the final screen returns.

Pins proven here:
(a) oversized input refused BEFORE the full decomposition cost
    is paid -- measured by a compose-work counter (tokens
    composed), never by wall-clock timing;
(b) valid content at/near the bound admitted, and the outbound
    decomposition block BYTE-IDENTICAL to the legacy whole-text
    path (_lm4_text_block);
(c) provider calls == 0 on every refusal;
(d) the final assembled-length screen still sees the exact
    outbound text: a bound falling inside the summary/spine gap
    (where the early abort cannot fire) is refused by the FINAL
    screen after a FULL decomposition.

Evidence labels: A = INTEGRATION (module path, direct bounded /
legacy comparison); C = INTEGRATION (scripted FakeProvider
through the public dock() / propose() path).
"""

from __future__ import annotations

import contextlib
import glob
import os
import shutil
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_HERE))

from form.dell_matrix import inference_dock as idock  # noqa: E402
from form.mandell import morpheme  # noqa: E402
from form.open import Program  # noqa: E402

_HEADER = idock._LM4_DECOMP_HEADER
_FINAL_DETAIL = ("Prompt with its LM-4 decomposition exceeds "
                 "the caller's bound; refused rather than sent "
                 "undecomposed.")
_SENTENCE = ("the harbor lantern guides the wooden boats across "
             "the quiet water while the keeper watches the tide")


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


def _repeat_to(sentence, target_chars):
    reps = target_chars // (len(sentence) + 1) + 1
    return " ".join([sentence] * reps)


class _ComposeWork:
    """Counts decomposition work: tokens composed through
    morpheme.compose_sentence while patched in. The A4 guard's
    earliness is asserted on this counter, never on timing."""

    def __init__(self, real):
        self.real = real
        self.tokens = 0
        self.calls = 0

    def __call__(self, text):
        out = self.real(text)
        self.calls += 1
        self.tokens += len(out["tokens"])
        return out


@contextlib.contextmanager
def _counted_compose():
    real = morpheme.compose_sentence
    work = _ComposeWork(real)
    morpheme.compose_sentence = work
    try:
        yield work
    finally:
        morpheme.compose_sentence = real


def _dock(owner, bound=None):
    p = Program(owner=owner)
    kw = {}
    if bound is not None:
        kw["max_prompt_chars"] = bound
    sess = idock.dock(p, "agent-a", provider="fake",
                      fake_mode="valid", **kw)
    return p, sess


def smoke() -> bool:
    print("=== A4 RESOURCE GUARD SMOKE ===")
    r = []

    def rec(n, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {n}")
        r.append(bool(ok))

    # ---------- A. byte-identity battery (pin b, module path) --
    classes = {
        "ordinary": _SENTENCE,
        "caps": ("TRANSFORM THE ANCIENT HARBOR SIGNAL BEFORE THE "
                 "WINTER STORM ARRIVES OVER THE NORTHERN CLIFFS"),
        "unicode": ("le café über naïve façade — señor "
                    "πανελλαδικός тест 日本語 テスト über alles"),
        "punct": ("wait... what?! (really) — yes; no: maybe, "
                  "perhaps; end. begin! stop? go..."),
        "numbers": ("count 123456 by 7890 in 2026 with 3.14159 "
                    "and 0.001 and 1000000 steps of 42"),
        "whitespace": "a  b\t\tc\n\nd   e     f  g",
        "short": "a an the of to in on at by for with from as is are was",
        "empty": "",
        "one": "lantern",
        "chunk-600": " ".join(
            f"word{i % 37} lantern{i % 11} harbor" for i in range(200)),
        "chunk-1500": " ".join(
            f"word{i % 37} lantern{i % 11} harbor" for i in range(500)),
    }
    # chunk-600 / chunk-1500 carry 600 / 1500 tokens: the pooled
    # path crosses the 512-token chunk boundary (and the second
    # boundary at 1024) and must still render byte-identically.
    ident = all(
        idock._lm4_text_block_bounded(t, 10 ** 9)
        == idock._lm4_text_block(t)
        for t in classes.values())
    rec("A1 bounded == legacy whole-text block, byte-identical "
        "across 11 classes incl. chunk crossings (600/1500 tokens)",
        ident)

    # ---------- G1. Gate-2 class at the default bound (a, c) ---
    owner = "A4GuardG1"
    try:
        prompt = _repeat_to(_SENTENCE, 214_200)
        total_tokens = len(prompt.split())
        _p, sess = _dock(owner)  # default bound 1,000,000
        with _counted_compose() as work:
            r1 = sess.propose(prompt)
        rec("G1 Gate-2 class (raw 214,200, default bound): "
            "refused prompt_too_large with the final screen's "
            "detail, provider calls == 0, and the abort fired "
            "early (tokens composed < 60% of the token stream, "
            "at least one full chunk composed)",
            r1.get("ok") is False
            and r1.get("reason") == "prompt_too_large"
            and r1.get("detail") == _FINAL_DETAIL
            and sess._provider.calls == 0
            and idock._LM4_CHUNK_TOKENS <= work.tokens
            < 0.6 * total_tokens)
    finally:
        _cleanup(owner)

    # ---------- G2. mid-size oversized, custom bound (a, c) ----
    owner = "A4GuardG2"
    try:
        prompt = _repeat_to(_SENTENCE, 20_000)
        total_tokens = len(prompt.split())
        legacy_assembled = (len(prompt) + len(_HEADER)
                            + len(idock._lm4_text_block(prompt)))
        _p, sess = _dock(owner, bound=100_000)
        with _counted_compose() as work:
            r2 = sess.propose(prompt)
        rec("G2 raw 20,000 vs caller bound 100,000 (legacy "
            "assembled ~202K): early-abort refusal, 0 provider "
            "calls, tokens composed < total -- and the legacy "
            "assembled length proves the final screen would "
            "refuse the same input",
            legacy_assembled > 100_000
            and r2.get("ok") is False
            and r2.get("reason") == "prompt_too_large"
            and r2.get("detail") == _FINAL_DETAIL
            and sess._provider.calls == 0
            and work.tokens < total_tokens)
    finally:
        _cleanup(owner)

    # ---------- G3. near-bound valid admitted (b, d) ----------
    owner = "A4GuardG3"
    try:
        prompt = _repeat_to(_SENTENCE, 6_000)
        legacy_block = idock._lm4_text_block(prompt)
        assembled = len(prompt) + len(_HEADER) + len(legacy_block)
        _p, sess = _dock(owner, bound=assembled)
        r3 = sess.propose(prompt)
        out = sess._provider.last_prompt or ""
        idx = out.find(_HEADER)
        segment = (out[idx + len(_HEADER):
                       idx + len(_HEADER) + len(legacy_block)]
                   if idx >= 0 else "")
        rec("G3 valid content at exactly the bound (assembled "
            "== bound): admitted, 1 provider call, and the "
            "outbound decomposition segment is byte-identical "
            "to the legacy whole-text block",
            r3.get("ok") is True
            and sess._provider.calls == 1
            and out.startswith(prompt)
            and segment == legacy_block
            and idock._lm4_text_block_bounded(prompt, assembled)
            == legacy_block)
    finally:
        _cleanup(owner)

    # ---------- G4. the final screen still decides (d, c) ------
    owner = "A4GuardG4"
    try:
        prompt = _repeat_to(_SENTENCE, 6_000)
        legacy_block = idock._lm4_text_block(prompt)
        assembled = len(prompt) + len(_HEADER) + len(legacy_block)
        total_tokens = len(prompt.split())
        _p, sess = _dock(owner, bound=assembled - 1)
        with _counted_compose() as work:
            r4 = sess.propose(prompt)
        rec("G4 bound inside the summary/spine gap (assembled "
            "- 1): the early abort cannot fire, the FULL token "
            "stream is composed, and the FINAL assembled screen "
            "refuses -- prompt_too_large, 0 provider calls",
            r4.get("ok") is False
            and r4.get("reason") == "prompt_too_large"
            and r4.get("detail") == _FINAL_DETAIL
            and sess._provider.calls == 0
            and work.tokens == total_tokens)
    finally:
        _cleanup(owner)

    # ---------- G5. refusal-shape identity ---------------------
    rec("G5 early-abort and final-screen refusals are the same "
        "dict shape (ok/reason/detail identical)",
        r1 == r4 == r2)

    # ---------- G6. smaller caller bound is sovereign ----------
    owner = "A4GuardG6"
    try:
        # Short-word text: ~685 tokens in ~3,000 chars, so the
        # stream spans two chunks while the raw length stays
        # under the caller's bound.
        prompt = _repeat_to(
            "a an the of to in on at by for with from as is are was",
            3_000)
        total_tokens = len(prompt.split())
        legacy_assembled = (len(prompt) + len(_HEADER)
                            + len(idock._lm4_text_block(prompt)))
        _p, sess = _dock(owner, bound=10_000)
        with _counted_compose() as work:
            r6 = sess.propose(prompt)
        rec("G6 explicit smaller caller bound 10,000 (raw ~3,000 "
            "short-word chars, legacy assembled > bound): "
            "refused early against the CALLER's bound after the "
            "first chunk, 0 provider calls",
            legacy_assembled > 10_000
            and total_tokens > idock._LM4_CHUNK_TOKENS
            and r6.get("ok") is False
            and r6.get("reason") == "prompt_too_large"
            and sess._provider.calls == 0
            and work.tokens == idock._LM4_CHUNK_TOKENS)
    finally:
        _cleanup(owner)

    # ---------- G7. tollbooth baseline behavior ----------------
    owner = "A4GuardG7"
    try:
        _p, sess = _dock(owner)
        r7 = sess.propose("transform the harbor lantern idea")
        out = sess._provider.last_prompt or ""
        rec("G7 tollbooth baseline: an ordinary docked propose "
            "is admitted and the outbound prompt carries the "
            "[decomposition] block with gloss lines and the "
            "honesty summary line",
            r7.get("ok") is True
            and sess._provider.calls == 1
            and "[decomposition]" in out
            and "LM: " in out
            and "LM: semantic_accounted=" in out)
    finally:
        _cleanup(owner)

    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
