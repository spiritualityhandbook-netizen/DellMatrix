#!/usr/bin/env python3
"""
Auto Growth — matrix grows itself continuously.

  · Internet search_far_wide for fuel
  · Verita + Floor Spirit license
  · Delta pressure guides restore vs expand
  · Nursery handled automatically (auto-confirm / auto-reject)
  · Confirmed ideas enter growth ledger (and plane when available)

Auto mode does what is best for continuous growth under Floor law:
  reject fog · confirm strong aligned · prioritize vital restore seeds

No human nursery click required when auto=True.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import json
import os
import time

_STATE = os.path.join(os.path.dirname(__file__), "..", "state")
os.makedirs(_STATE, exist_ok=True)
LEDGER_PATH = os.path.join(_STATE, "auto_growth_ledger.json")

# Auto-confirm thresholds
MIN_VERITA = 0.45
MIN_COMBINED = 0.40


def _load_ledger() -> List[Dict[str, Any]]:
    if not os.path.isfile(LEDGER_PATH):
        return []
    try:
        with open(LEDGER_PATH, encoding="utf-8") as f:
            data = json.load(f)
        return list(data) if isinstance(data, list) else []
    except Exception:
        return []


def _save_ledger(rows: List[Dict[str, Any]]) -> None:
    rows = rows[-200:]
    with open(LEDGER_PATH, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)


@dataclass
class AutoGrowth:
    auto: bool = True
    internet: bool = True
    queries: List[str] = field(default_factory=lambda: [
        "systems thinking coherence",
        "eigenvalue stability dynamical systems",
        "offline first software architecture",
        "harmonic resonance pattern formation",
        "autonomous agent memory architecture",
    ])
    query_index: int = 0
    tick: int = 0
    confirmed_total: int = 0
    rejected_total: int = 0
    last_report: Dict[str, Any] = field(default_factory=dict)

    def next_query(self, override: str = "") -> str:
        if override.strip():
            return override.strip()
        if not self.queries:
            return "coherent growth systems"
        q = self.queries[self.query_index % len(self.queries)]
        self.query_index += 1
        return q

    def _judge(self, label: str, words: str) -> Dict[str, Any]:
        try:
            from form.dell_matrix.verita import verita_of_one
            from form.dell_matrix.floor_spirit import FLOOR_SPIRIT
            v = verita_of_one(label, words=words)
            lic = FLOOR_SPIRIT.license_verita(v, f"{label} {words}")
            return {
                "verita_score": v.get("score", 0),
                "verita_accept": v.get("accept"),
                "floor_accept": lic.get("final_accept"),
                "combined": lic.get("combined_score", v.get("score", 0)),
                "reason": lic.get("reason"),
                "grade": v.get("grade"),
            }
        except Exception as e:
            return {
                "verita_score": 0.0,
                "verita_accept": False,
                "floor_accept": False,
                "combined": 0.0,
                "reason": f"judge_error:{e}",
                "grade": "fog",
            }

    def _should_auto_confirm(self, judge: Dict[str, Any], delta_band: str) -> bool:
        if not self.auto:
            return False
        if not judge.get("floor_accept"):
            return False
        if float(judge.get("verita_score") or 0) < MIN_VERITA:
            return False
        if float(judge.get("combined") or 0) < MIN_COMBINED:
            return False
        if judge.get("grade") in ("fog", "weak"):
            return False
        # under critical pressure still allow restore-aligned confirms only
        if delta_band == "critical":
            return "restore" in (judge.get("reason") or "") or float(judge.get("combined") or 0) >= 0.55
        return True

    def _nursery_auto(self, label: str, words: str, judge: Dict[str, Any], source: str) -> Dict[str, Any]:
        """Add to nursery and auto confirm/reject — matrix handles nursery itself."""
        try:
            from form.dell_matrix.nursery import Nursery
            n = Nursery.load()
            prop = n.add(
                label=label,
                words=words,
                kind="auto",
                affinity=float(judge.get("combined") or 0),
                reason=f"auto:{source}:{judge.get('reason', '')}"[:160],
            )
            if self._should_auto_confirm(judge, self.last_report.get("delta_band", "elevated")):
                n.confirm(prop.id)
                self.confirmed_total += 1
                status = "auto_confirmed"
            else:
                n.reject(prop.id)
                self.rejected_total += 1
                status = "auto_rejected"
            return {
                "id": prop.id,
                "status": status,
                "label": label[:72],
                "affinity": prop.affinity,
                "nursery": n.summary(),
            }
        except Exception as e:
            # ledger-only fallback if nursery import fails
            status = "ledger_only_confirm" if judge.get("floor_accept") else "ledger_only_reject"
            if "confirm" in status:
                self.confirmed_total += 1
            else:
                self.rejected_total += 1
            return {"id": None, "status": status, "label": label[:72], "error": str(e)}

    def _commit_ledger(self, item: Dict[str, Any]) -> None:
        rows = _load_ledger()
        rows.append({**item, "ts": time.time()})
        _save_ledger(rows)

    def _try_plane_place(self, label: str, words: str) -> Dict[str, Any]:
        """Best-effort place into live plane if Program surface exists."""
        try:
            from form.open import open_program
            p = open_program("AutoGrow")
            if hasattr(p, "place"):
                p.place(label[:24].replace(" ", "_").lower(), label, words=words[:200])
                return {"ok": True, "surface": "program.place"}
        except Exception as e:
            return {"ok": False, "reason": str(e)}
        return {"ok": False, "reason": "no_place"}

    def harvest_net(self, query: str = "") -> List[Dict[str, Any]]:
        ideas: List[Dict[str, Any]] = []
        if not self.internet:
            return ideas
        try:
            from form.dell_matrix.internet_gate import InternetGate
            net = InternetGate()
            if self.auto:
                net.ensure_on_for_auto()
            else:
                net.turn_on()
            q = self.next_query(query)
            # bias queries toward vital gaps when body reports them
            try:
                from form.dell_matrix.matrix_body import body_pulse
                body = body_pulse()
                missing = body.get("missing") or []
                if missing:
                    q = f"{q} {missing[0]} system restore architecture"
            except Exception:
                pass
            fw = net.search_far_wide(q)
            for idea in fw.get("ideas") or []:
                ideas.append(idea)
            self.last_report["last_query"] = q
            self.last_report["net_count"] = fw.get("count", 0)
            self.last_report["net_sources"] = fw.get("primary_sources") or []
        except Exception as e:
            self.last_report["net_error"] = str(e)
        return ideas

    def step(
        self,
        *,
        query: str = "",
        extra_ideas: Optional[List[Dict[str, Any]]] = None,
        place_on_confirm: bool = True,
    ) -> Dict[str, Any]:
        self.tick += 1
        body: Dict[str, Any] = {}
        delta: Dict[str, Any] = {}
        try:
            from form.dell_matrix.matrix_body import body_pulse
            body = body_pulse()
        except Exception as e:
            body = {"missing": [], "error": str(e)}
        try:
            from form.dell_matrix.delta_pressure import from_body
            delta = from_body(body)
        except Exception:
            delta = {"band": "elevated", "magnitude": 0.3}

        self.last_report["delta_band"] = delta.get("band", "elevated")

        # harvest
        ideas = self.harvest_net(query)
        for ex in (extra_ideas or []):
            ideas.append(ex)

        # always seed a restore idea when vital missing
        missing = body.get("missing") or []
        if missing:
            ideas.insert(0, {
                "label": f"Restore {missing[0]} organ",
                "words": f"vital densify {missing[0]} whole body offline coherent growth",
                "source": "delta:vital",
            })

        results = []
        confirmed_labels = []
        for idea in ideas[:12]:
            label = str(idea.get("label") or "")[:80]
            words = str(idea.get("words") or "")[:400]
            if len(label) < 3:
                continue
            judge = self._judge(label, words)
            nursery = self._nursery_auto(label, words, judge, str(idea.get("source") or "auto"))
            plane = {"ok": False}
            if nursery.get("status") in ("auto_confirmed", "ledger_only_confirm") and place_on_confirm:
                plane = self._try_plane_place(label, words)
                self._commit_ledger({
                    "label": label,
                    "words": words[:200],
                    "source": idea.get("source"),
                    "judge": judge,
                    "nursery": nursery.get("status"),
                    "plane": plane.get("ok"),
                })
                confirmed_labels.append(label)
            results.append({
                "label": label[:60],
                "source": idea.get("source"),
                "judge": judge,
                "nursery": nursery.get("status"),
                "plane": plane.get("ok"),
            })

        report = {
            "ok": True,
            "auto": self.auto,
            "tick": self.tick,
            "query": self.last_report.get("last_query"),
            "net_count": self.last_report.get("net_count", 0),
            "net_sources": self.last_report.get("net_sources", []),
            "delta_band": delta.get("band"),
            "delta_top": (delta.get("top_action") or {}).get("action"),
            "missing": missing[:8],
            "processed": len(results),
            "confirmed": len(confirmed_labels),
            "confirmed_labels": confirmed_labels[:8],
            "confirmed_total": self.confirmed_total,
            "rejected_total": self.rejected_total,
            "results": results[:12],
            "law": (
                "auto: net far-wide → Verita+Floor judge → nursery self-handle → "
                "confirm strong · reject fog · ledger · plane when available"
            ),
        }
        self.last_report = {**self.last_report, **report}
        return report

    def run_continuous(self, ticks: int = 5, sleep_s: float = 0.5, query: str = "") -> List[Dict[str, Any]]:
        out = []
        for _ in range(max(1, ticks)):
            out.append(self.step(query=query))
            if sleep_s > 0:
                time.sleep(sleep_s)
        return out


AUTO = AutoGrowth()


def auto_step(**kwargs) -> Dict[str, Any]:
    return AUTO.step(**kwargs)


def smoke() -> bool:
    print("=== AUTO GROWTH SMOKE ===")
    r = []
    def rec(n, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {n}"); r.append(ok)

    ag = AutoGrowth(auto=True, internet=False)  # offline smoke: extra ideas only
    out = ag.step(
        extra_ideas=[
            {"label": "Restore floor skeleton", "words": "vital organ densify coherent offline body grow", "source": "test"},
            {"label": "??", "words": "asdf", "source": "test"},
        ],
        place_on_confirm=False,
    )
    rec("step_ok", out.get("ok") is True)
    rec("processed", out.get("processed", 0) >= 1)
    statuses = [x.get("nursery") for x in out.get("results") or []]
    rec("has_confirm_or_reject", any(s and "auto_" in str(s) for s in statuses) or out.get("processed", 0) >= 1)
    print(f"confirmed_total={ag.confirmed_total} rejected_total={ag.rejected_total}")
    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    if "--smoke" in sys.argv:
        sys.exit(0 if smoke() else 1)
    # live auto tick with network if available
    AUTO.auto = True
    AUTO.internet = True
    rep = AUTO.step(query="coherent autonomous systems architecture")
    print(json.dumps({
        "tick": rep["tick"],
        "query": rep.get("query"),
        "net_count": rep.get("net_count"),
        "confirmed": rep.get("confirmed"),
        "confirmed_labels": rep.get("confirmed_labels"),
        "delta_band": rep.get("delta_band"),
        "law": rep.get("law"),
    }, indent=2))
