#!/usr/bin/env python3
"""Proposal B LIVE acceptance at candidate head 081add9 (dock_clone).
Real Gemini via the vault connector; key never enters this process.
Wiring replicates dock()'s production seam exactly as the 2026-11-08
live demo did. Checks: synthesize lands PENDING; last_response_view
session-only present; raw response absent from durable state files;
forced provider failure surfaces sanitized bounded cause."""
import glob, json, sys, uuid
sys.path.insert(0, ".")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.gemini/bin")
import gemini_generate
from form.open import Program
from form.dell_matrix import inference_dock as idock
from form.dell_matrix.agent_coordinator import new_coordinator
from form import persist_rest

OWNER = "DOCKB" + uuid.uuid4().hex[:6].upper()
print("OWNER", OWNER)

class VaultGeminiProvider:
    def __init__(self, model="gemini-3-flash-preview"):
        self.model = model; self.calls = 0; self.last_raw = None; self.last_error = None
    def generate(self, prompt, *, timeout_s, max_chars):
        self.calls += 1
        out = gemini_generate.generate(prompt, self.model)
        if not out.get("ok"):
            self.last_error = out.get("error", "unknown")
            raise ConnectionError(f"gemini transport: {self.last_error}")
        self.last_raw = out.get("text", "")
        return self.last_raw

def seed_unit(p, label, detail, goals):
    pr = p.nursery.add(label, words=label, detail=detail, goals=goals)
    ctx = p.make_review_context(pr.id, reviewer="human:ace")
    r = p.confirm_proposal(pr.id, _producer="acceptance-b", _review_context=ctx)
    assert r.get("ok"), r

def unit_id(p, label):
    for uid, u in p.cube.session.plane.units.items():
        if u.label == label:
            return uid
    raise AssertionError(label)

def wire(p, prov, subject):
    session = idock.DockedSession(p, subject, OWNER, "gemini", prov, prov.model, 30, 8000, 8000, task="propose")
    matrix = getattr(p, "matrix", None)
    if matrix is not None:
        from form.dell_matrix.snap import SnapCandidate
        snap_name = "dock:{}:{}".format(idock._origin_segment(subject, 40), session.session_id[:8])
        result = matrix.snap(SnapCandidate(name=snap_name, kind="other",
            payload={"subject": subject, "provider": "gemini", "task": "propose"}))
        assert result.ok, result.reason
        object.__setattr__(session, "_snap_name", snap_name)
        session._evidence["snap_name"] = snap_name
        session._persist_state()
    coord = new_coordinator(p)
    coord.register_agent(subject)
    object.__setattr__(session, "_coordinator", coord)
    return session

p = Program(owner=OWNER)
seed_unit(p, "Solar Roof", "A roof that harvests sunlight to power the house.", ["energy", "shelter"])
seed_unit(p, "Night Garden", "A garden that blooms after dark for quiet evenings.", ["calm", "nature"])
persist_rest.save(p, OWNER)
roof, garden = unit_id(p, "Solar Roof"), unit_id(p, "Night Garden")
prov = VaultGeminiProvider()
sess = wire(p, prov, "host:acceptance-b")
res = sess.synthesize([roof, garden])
print("SYNTH", json.dumps(res)[:300])
pend = p.nursery.pending()
print("PENDING_COUNT", len(pend))
for pr in pend:
    print("PENDING", pr.label, "| origin:", pr.origin)
view = sess.last_response_view()
print("VIEW_PRESENT", view is not None)
if isinstance(view, dict):
    print("VIEW_KEYS", sorted(view.keys()))
    print("VIEW_TRUNCATED", view.get("truncated"), "VIEW_LEN", len(str(view.get("text", ""))))
raw = prov.last_raw or ""
print("RAW_WAS_FENCED", raw.strip().startswith("```"))
leak = False
for f in glob.glob("form/state/*"):
    try:
        data = open(f, errors="ignore").read()
    except OSError:
        continue
    if OWNER.lower() in f and raw and len(raw) > 40 and raw[:120] in data:
        leak = True; print("LEAK_IN", f)
print("DURABLE_RAW_LEAK", leak)
prov2 = VaultGeminiProvider(model="gemini-does-not-exist-zzz")
sess2 = wire(p, prov2, "host:acceptance-b-fail")
try:
    r2 = sess2.synthesize([roof, garden])
    print("FAIL_CALL", json.dumps(r2)[:400])
except Exception as e:
    print("FAIL_RAISED", type(e).__name__, str(e)[:400])
print("ACCEPTANCE_B_DONE")
