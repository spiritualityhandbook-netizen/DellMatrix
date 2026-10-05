"""WO-5.2/5.3 lifecycle coherence proof (Director 2026-10-05 whole-circuit).

Proves, against genuine revision chains:
- fade/unfade preserves identity, content, acceptance, revision links
- unfade/pin cannot reactivate superseded truth
- ordinary consumers exclude historical (superseded) records
- deliberate historical growth remains functional
- malformed records stay excluded in every context (faded presence
  must not rescue malformed revision data)
- save/restart preserves these results

Evidence class: INTEGRATION (real Program, real TPP-I presence, real
supersession; isolated owner).
"""

import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(REPO))

from form.open import open_program
from form.dell_matrix import canonical_lifecycle as cl
from form.lifecycle import set_presence, get_presence
from form.mandell import supersession as S
from form.mandell.supersession import inspect_revision

OWNER = "WO52_COH"
CHECKS = []


def check(name, cond, detail=""):
    CHECKS.append(bool(cond))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}" + (f" | {detail}" if detail and not cond else ""))


def clean():
    for pat in [f'form/state/nursery_{OWNER}.json', f'form/state/program_{OWNER}.json']:
        p = os.path.join(REPO, pat)
        if os.path.isfile(p):
            os.remove(p)


def _confirm(p, pr, producer="test"):
    ctx = p.make_review_context(pr.id, producer)
    r = p.confirm_proposal(pr.id, _producer=producer, _review_context=ctx)
    assert r.get("ok"), r
    return pr.id


def test_fade_unfade_preserves():
    """Fade/unfade preserves identity, content, acceptance, revision links."""
    clean()
    p = open_program(OWNER)
    pr = p.nursery.add("FadeMe", words="original content here")
    pid = _confirm(p, pr)
    before = inspect_revision(p, pid)
    # Fade via TPP-I presence
    set_presence(p, pid, presence="faded")
    p.save()
    check("fade_excludes_ordinary", not cl.is_active(p, pid))
    check("fade_is_faded", cl.is_faded(p, pid))
    check("fade_historical_still", cl.is_participating(p, pid, "historical"))
    # Identity/content/acceptance/revision preserved
    after = inspect_revision(p, pid)
    check("fade_preserves_revision", after["lifecycle_state"] == before["lifecycle_state"])
    check("fade_preserves_links",
          after["supersedes_id"] == before["supersedes_id"]
          and after["revision_root_id"] == before["revision_root_id"])
    prop = p.nursery.proposals[pid]
    check("fade_preserves_content", prop.words == "original content here")
    check("fade_preserves_acceptance", prop.status == "confirmed")
    # Unfade
    set_presence(p, pid, presence="active")
    check("unfade_restores", cl.is_active(p, pid))
    check("unfade_not_faded", not cl.is_faded(p, pid))


def test_unfade_cannot_reactivate_superseded():
    """Unfade/pin on a superseded unit cannot make it ordinarily active."""
    clean()
    p = open_program(OWNER)
    pr = p.nursery.add("SupBase", words="v1")
    pid = _confirm(p, pr)
    p.acceptance_policy.grant_opt_in("test", scope="test")
    r = S.supersede_proposal(p, pid, "v2 words", _producer="test")
    assert r.get("ok"), r
    # Try to "reactivate" via unfade + pin
    set_presence(p, pid, presence="active", pinned=True)
    check("superseded_stays_excluded",
          not cl.is_active(p, pid) and not cl.is_participating(p, pid, "ordinary"),
          cl.participation_reason(p, pid))
    check("superseded_historical_ok", cl.is_participating(p, pid, "historical"))
    # Revision truth intact
    rev = inspect_revision(p, pid)
    check("superseded_revision_intact", rev["lifecycle_state"] == "superseded")


def test_malformed_excluded_everywhere():
    """Faded presence on malformed revision: excluded in ALL contexts."""
    clean()
    p = open_program(OWNER)
    pr = p.nursery.add("BadRec", words="w")
    pid = _confirm(p, pr)
    # Corrupt the revision: claim a successor that doesn't exist
    pr.superseded_by_id = "ghost_successor_zzz"
    p.nursery.save()
    rev = inspect_revision(p, pid)
    check("malformed_detected", rev["lifecycle_state"] == "malformed", rev.get("malformed_reason"))
    # Now add faded presence — must NOT rescue it
    set_presence(p, pid, presence="faded")
    check("malformed_excluded_ordinary", not cl.is_participating(p, pid, "ordinary"))
    check("malformed_excluded_historical", not cl.is_participating(p, pid, "historical"),
          "faded presence must not make malformed eligible for historical use")
    check("malformed_not_faded", not cl.is_faded(p, pid),
          "is_faded requires valid revision")
    check("malformed_not_active", not cl.is_active(p, pid))


def test_ordinary_excludes_historical_growth_works():
    """Ordinary growth excludes superseded; explicit historical use works."""
    clean()
    p = open_program(OWNER)
    a = p.nursery.add("HistA", words="alpha beta gamma")
    aid = _confirm(p, a)
    p.acceptance_policy.grant_opt_in("test", scope="test")
    r = S.supersede_proposal(p, aid, "alpha beta gamma revised", _producer="test")
    assert r.get("ok"), r
    # Ordinary participation excludes the superseded revision
    check("ordinary_excludes_superseded", not cl.is_participating(p, aid, "ordinary"))
    # Explicit historical growth path still functional
    out = p.grow_ideas(1, include_superseded=True)
    check("historical_growth_runs", out is not None)


def test_restart_preserves():
    """Save/restart preserves lifecycle coherence results."""
    clean()
    from form import persist_rest
    p = open_program(OWNER)
    pr = p.nursery.add("PersistMe", words="w")
    pid = _confirm(p, pr)
    set_presence(p, pid, presence="faded")
    p.nursery.save()
    persist_rest.save(p)
    p2 = persist_rest.load(OWNER, activate=False)
    check("restart_faded_excluded", not cl.is_active(p2, pid))
    check("restart_faded_flag", cl.is_faded(p2, pid))
    check("restart_historical", cl.is_participating(p2, pid, "historical"))
    check("restart_revision", inspect_revision(p2, pid)["lifecycle_state"] == "active")




def test_valid_legacy_participates():
    """Genuinely absent legacy data: no proposal, no presence -> participates."""
    clean()
    p = open_program(OWNER)
    # A unit ID with no proposal record and no presence entry.
    # resolve_lifecycle treats as legacy active; acceptance absent_legacy.
    check("legacy_participates_ordinary",
          cl.is_participating(p, "legacy_ghost_001", "ordinary"))
    check("legacy_not_malformed",
          "malformed" not in cl.participation_reason(p, "legacy_ghost_001"))


def test_malformed_status_excluded():
    """Proposal with status=None or garbage: excluded everywhere with reason."""
    clean()
    p = open_program(OWNER)
    pr = p.nursery.add("BadStatus", words="w")
    pid = _confirm(p, pr)
    # Corrupt to None
    pr.status = None
    p.nursery.save()
    check("none_status_excluded_ordinary",
          not cl.is_participating(p, pid, "ordinary"))
    check("none_status_excluded_historical",
          not cl.is_participating(p, pid, "historical"))
    check("none_status_reason",
          "malformed" in cl.participation_reason(p, pid),
          cl.participation_reason(p, pid))
    # Corrupt to garbage
    pr.status = "bogus_state"
    check("garbage_status_excluded",
          not cl.is_participating(p, pid, "ordinary")
          and not cl.is_participating(p, pid, "historical"))


def test_malformed_presence_excluded():
    """Garbage presence value: excluded everywhere with explicit reason."""
    clean()
    p = open_program(OWNER)
    pr = p.nursery.add("BadPresence", words="w")
    pid = _confirm(p, pr)
    set_presence(p, pid, presence="vaporized")
    check("bad_presence_excluded_ordinary",
          not cl.is_participating(p, pid, "ordinary"))
    check("bad_presence_excluded_historical",
          not cl.is_participating(p, pid, "historical"))
    check("bad_presence_reason",
          "malformed" in cl.participation_reason(p, pid),
          cl.participation_reason(p, pid))
    check("bad_presence_not_faded", not cl.is_faded(p, pid))


def test_malformed_restart():
    """Malformed status/presence survive restart as excluded."""
    clean()
    from form import persist_rest
    p = open_program(OWNER)
    pr = p.nursery.add("BadRestart", words="w")
    pid = _confirm(p, pr)
    pr.status = None
    set_presence(p, pid, presence="vaporized")
    p.nursery.save()
    persist_rest.save(p)
    p2 = persist_rest.load(OWNER, activate=False)
    check("restart_malformed_excluded",
          not cl.is_participating(p2, pid, "ordinary")
          and not cl.is_participating(p2, pid, "historical"))


def smoke():
    print("=== WO-5.2/5.3 LIFECYCLE COHERENCE ===")
    for fn in [test_fade_unfade_preserves,
               test_unfade_cannot_reactivate_superseded,
               test_malformed_excluded_everywhere,
               test_ordinary_excludes_historical_growth_works,
               test_restart_preserves,
               test_valid_legacy_participates,
               test_malformed_status_excluded,
               test_malformed_presence_excluded,
               test_malformed_restart]:
        try:
            fn()
        except Exception as e:
            import traceback
            check(fn.__name__, False, f"EXC {type(e).__name__}: {e}")
    n = sum(CHECKS)
    print(f"=== {n}/{len(CHECKS)} ===")
    return n == len(CHECKS)


if __name__ == "__main__":
    ok = smoke()
    sys.exit(0 if ok else 1)
