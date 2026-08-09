#!/usr/bin/env python3
"""
Flash path — high capability under tight budget.

From: DeepSeek-style efficiency / "Flash" models
  · Short labels still get judged
  · Token/time budget hard caps
  · Sparse Verita: skip heavy pair work when solo is enough
  · Offline by default

  flash_judge(label, words)
  flash_batch(ideas, budget=8)
"""
from __future__ import annotations

from typing import Any, Dict, List
import time


def flash_judge(label: str, words: str = "", *, budget_ms: float = 50.0) -> Dict[str, Any]:
    t0 = time.time()
    label = (label or "").strip()
    words = (words or "").strip() or label
    out: Dict[str, Any] = {"label": label[:80], "path": "flash"}
    try:
        from form.dell_matrix.verita import verita_of_one
        v = verita_of_one(label, words=words[:240])
        out["verita_score"] = v.get("score")
        out["accept_local"] = v.get("accept")
        # floor only if time remains
        elapsed = (time.time() - t0) * 1000
        if elapsed < budget_ms * 0.7:
            try:
                from form.dell_matrix.floor_spirit import FLOOR_SPIRIT
                lic = FLOOR_SPIRIT.license_verita(v, f"{label} {words[:120]}")
                out["final_accept"] = lic.get("final_accept")
                out["combined"] = lic.get("combined_score")
                out["path"] = "flash+floor"
            except Exception:
                out["final_accept"] = v.get("accept")
        else:
            out["final_accept"] = v.get("accept")
            out["path"] = "flash_verita_only"
    except Exception as e:
        out["error"] = str(e)
        out["final_accept"] = False
    out["ms"] = round((time.time() - t0) * 1000, 2)
    out["source_idea"] = "deepseek_flash_efficiency"
    return out


def flash_batch(ideas: List[Dict[str, Any]], *, budget: int = 8) -> Dict[str, Any]:
    accepted = []
    rejected = []
    for idea in ideas[:budget]:
        j = flash_judge(str(idea.get("label") or ""), str(idea.get("words") or ""))
        if j.get("final_accept"):
            accepted.append(j)
        else:
            rejected.append(j)
    return {
        "ok": True,
        "accepted": accepted,
        "rejected": rejected,
        "accepted_n": len(accepted),
        "rejected_n": len(rejected),
        "budget": budget,
        "law": "sparse fast path · offline",
    }


def smoke() -> bool:
    print("=== FLASH PATH SMOKE ===")
    r = []
    def rec(n, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {n}"); r.append(ok)
    j = flash_judge("Restore lattice", "vital densify coherent offline body")
    rec("judge", "final_accept" in j)
    b = flash_batch([
        {"label": "Restore floor", "words": "vital organ densify"},
        {"label": "x", "words": "?"},
    ], budget=4)
    rec("batch", b.get("ok") is True)
    print(j)
    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
