"""Post-plan PP1 / D6 — stopwords out of pair comparisons.

Ace's rule (2026-10-27): words may FIND candidate pairs, but
connector words ("and", "if", "the") and other function words
that hold no meaning beyond connecting content words must not
count IN the comparisons. Before PP1 there was no stopword
handling anywhere: "and"/"the" were ordinary tokens in growth
affinity and knowledge-selection scoring (the IdeaLab40 field
test watched growth pair ideas over shared function words).

The exclusion lives in ONE authority (text_metrics.STOPWORDS +
content_tokens) and is applied ONLY at pair-comparison sites:
ringed_growth affinity (unit tokens + goal boost) and
knowledge_selector scoring. Raw tokenization is unchanged —
signal consumers (negation/conflict, phrase/order) never see
the filter; negation and contrast words are never stopwords.
"""
from __future__ import annotations

import glob
import os
import shutil
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from form.open import Program  # noqa: E402
from form.dell_matrix import text_metrics as tm  # noqa: E402
from form.dell_matrix import ringed_growth as rg  # noqa: E402
from form.mandell import knowledge_selector as ks  # noqa: E402

RESULTS = []


def _rec(name, cond, detail=""):
    RESULTS.append((name, bool(cond), str(detail)[:200]))


def _cleanup(owner):
    base = os.path.join(os.path.dirname(__file__), "..", "state")
    for pat in (f"program_{owner}.json", f"nursery_{owner}.json",
                f"checkpoint_{owner}_*", f"confirm_{owner}.journal.json",
                f"checkpoint_{owner}.journal.json",
                f"gen_{owner}_*", f"current_{owner}.json"):
        for f in glob.glob(os.path.join(base, pat)):
            try:
                os.remove(f)
            except FileNotFoundError:
                pass
    for d in glob.glob(os.path.join(base, f"ideas_{owner}*")):
        if os.path.isdir(d):
            shutil.rmtree(d)


def _place(p, label, words):
    pr = p.nursery.add(label, words=words, detail=words)
    ctx = p.make_review_context(pr.id, reviewer="human:ace")
    r = p.confirm_proposal(pr.id, _producer="pp1test",
                           _review_context=ctx)
    assert r.get("ok"), r
    return pr.id


def smoke() -> bool:
    # ── the authority itself ──────────────────────────────────
    _rec("connectors_are_stopwords",
         {"and", "the", "with", "from", "that", "this"} <= tm.STOPWORDS)
    _rec("negations_never_stopwords",
         not ({"no", "not", "nor", "never", "but", "yet"}
              & tm.STOPWORDS))
    _rec("stopwords_are_real_tokens",
         all(len(w) >= 3 and tm.TOKEN_RE.fullmatch(w)
             for w in tm.STOPWORDS))
    _rec("content_tokens_filter",
         tm.content_tokens("the heart and the stone")
         == {"heart", "stone"},
         str(tm.content_tokens("the heart and the stone")))
    _rec("raw_tokens_unchanged",
         {"the", "and", "heart"} <= tm.tokens("the heart and soul"))
    _rec("stopword_only_text_has_no_content",
         tm.content_tokens("and the with from") == set())

    owner = "PP1Stop"
    _cleanup(owner)
    try:
        p = Program(owner=owner)
        # Two ideas sharing ONLY function words (plus their own
        # unrelated content): pre-fix their raw token sets
        # overlapped on the/and/with; affinity must now see no
        # content overlap at all.
        a = _place(p, "Alpha", "the lantern and the compass with it")
        b = _place(p, "Beta", "the garden and the harbor with it")
        plane = p.cube.session.plane
        aff = rg._affinity(plane, a, b)
        _rec("function_word_pair_has_zero_jaccard",
             aff["jaccard"] == 0.0, f"aff={ {k: round(v, 4) for k, v in aff.items()} }")
        raw = tm.jaccard(tm.tokens("Alpha the lantern and the compass with it"),
                         tm.tokens("Beta the garden and the harbor with it"))
        _rec("raw_overlap_was_real", raw > 0.0, f"raw={raw:.3f}")

        # A pair sharing real content still scores: filtering
        # must not starve genuine matches.
        c = _place(p, "Lantern Keeper",
                   "the lantern guides the harbor watch")
        aff2 = rg._affinity(plane, a, c)
        _rec("content_pair_still_scores", aff2["jaccard"] > 0.0,
             f"jaccard={aff2['jaccard']:.3f}")

        # Selection scoring: a stopword-only overlap must not
        # select; a content overlap must.
        sel_noise = ks.select_for_context(p, "the and with from")
        _rec("selector_stopword_context_selects_nothing",
             sel_noise.get("selected") == []
             and sel_noise.get("reason") == "no context tokens",
             str(sel_noise.get("reason")))
        sel = ks.select_for_context(p, "lantern harbor")
        ids = [row["id"] for row in sel.get("selected") or []]
        _rec("selector_content_context_selects", len(ids) >= 1,
             f"ids={ids}")
        if ids:
            row = (sel.get("selected") or [{}])[0]
            _rec("selector_shared_shows_content_only",
                 row.get("shared")
                 and not (set(row["shared"]) & tm.STOPWORDS),
                 f"shared={row.get('shared')}")
    finally:
        _cleanup(owner)
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    for name, ok, detail in RESULTS:
        print(f"{'PASS' if ok else 'FAIL'} {name} {detail}")
    print(f"pp1_stopwords_test {passed}/{len(RESULTS)}")
    return passed == len(RESULTS)


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
