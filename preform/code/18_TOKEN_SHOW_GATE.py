#!/usr/bin/env python3
"""
18_TOKEN_SHOW_GATE.py
Code Phase 4 · Cell 4.3
Status: TRUE
Offline · Zero dependencies · Stdlib only

Applies TokenBudget to Show (09) and seed-strip paths.
- charge on set_seed_strip / show
- over-limit → reject (strict) or trim (soft)
- never raises; returns ok + reason
"""

from __future__ import annotations
from typing import Any, Dict, Optional, Tuple
from dataclasses import dataclass, field

@dataclass
class TokenBudget:
    limit: int = 4096
    used: int = 0
    reserved: int = 64  # reserve for system chrome

    def estimate(self, text: str) -> int:
        if not text:
            return 0
        return max(1, len(text) // 4)

    def remaining(self) -> int:
        return max(0, self.limit - self.used - self.reserved)

    def can_afford(self, text: str) -> bool:
        return self.estimate(text) <= self.remaining()

    def charge(self, text: str) -> bool:
        cost = self.estimate(text)
        if cost > self.remaining():
            return False
        self.used += cost
        return True

    def reset(self) -> None:
        self.used = 0

    def status(self) -> Dict[str, int]:
        return {
            "limit": self.limit,
            "used": self.used,
            "reserved": self.reserved,
            "remaining": self.remaining(),
        }


@dataclass
class ShowGate:
    """
    Gate for seed-strip + Show paths.
    mode:
      strict — reject if cannot afford
      soft   — trim text to remaining budget then charge
    """
    budget: TokenBudget = field(default_factory=TokenBudget)
    mode: str = "strict"  # strict | soft
    seed_strip: str = ""
    last_show: str = ""
    rejects: int = 0
    trims: int = 0

    def _trim_to_budget(self, text: str) -> str:
        rem = self.budget.remaining()
        if rem <= 0:
            return ""
        # estimate chars from remaining tokens
        max_chars = rem * 4
        if len(text) <= max_chars:
            return text
        return text[: max(0, max_chars - 1)] + "…"

    def set_seed_strip(self, text: str) -> Tuple[bool, str]:
        """
        Attempt to set read-only seed strip under budget.
        Returns (ok, message).
        """
        text = text or ""
        if self.budget.can_afford(text):
            self.budget.charge(text)
            self.seed_strip = text
            return True, "seed_strip set"

        if self.mode == "soft":
            trimmed = self._trim_to_budget(text)
            if trimmed and self.budget.charge(trimmed):
                self.seed_strip = trimmed
                self.trims += 1
                return True, "seed_strip trimmed to budget"
            self.rejects += 1
            return False, "seed_strip rejected (no budget)"

        self.rejects += 1
        return False, "seed_strip rejected (strict over limit)"

    def show(self, text: str) -> Tuple[bool, str]:
        """
        Show path (Dell 09). Charges budget for display payload.
        Returns (ok, payload_or_reason).
        """
        text = text or ""
        if self.budget.can_afford(text):
            self.budget.charge(text)
            self.last_show = text
            return True, text

        if self.mode == "soft":
            trimmed = self._trim_to_budget(text)
            if trimmed and self.budget.charge(trimmed):
                self.last_show = trimmed
                self.trims += 1
                return True, trimmed
            self.rejects += 1
            return False, ""

        self.rejects += 1
        return False, ""

    def status(self) -> Dict[str, Any]:
        return {
            "budget": self.budget.status(),
            "mode": self.mode,
            "seed_strip_len": len(self.seed_strip),
            "last_show_len": len(self.last_show),
            "rejects": self.rejects,
            "trims": self.trims,
        }


def smoke_show_gate() -> bool:
    print("=== TOKEN SHOW GATE SMOKE ===")
    results = []

    def record(name: str, passed: bool, detail: str = "") -> None:
        print(f"[{len(results)+1}] {name}: {'PASS' if passed else 'FAIL'}" + (f" | {detail}" if detail else ""))
        results.append(passed)

    def run(name, fn):
        try:
            ok, detail = fn()
            record(name, bool(ok), detail)
        except Exception as e:
            record(name, False, f"EXCEPTION {type(e).__name__}: {e}")

    gate = ShowGate(budget=TokenBudget(limit=100, reserved=10), mode="strict")

    def case_afford_seed():
        ok, msg = gate.set_seed_strip("08[Create] >> 14[Bind]")
        return ok, msg

    def case_show_ok():
        ok, payload = gate.show("(◕‿◕)")
        return ok and payload == "(◕‿◕)", f"payload={payload!r}"

    def case_strict_reject():
        # fill budget
        big = "x" * 400
        ok, msg = gate.set_seed_strip(big)
        return (not ok), f"msg={msg} rejects={gate.rejects}"

    def case_soft_trim():
        soft = ShowGate(budget=TokenBudget(limit=50, reserved=5), mode="soft")
        ok, msg = soft.set_seed_strip("A" * 500)
        return ok and len(soft.seed_strip) < 500 and soft.trims >= 1, f"len={len(soft.seed_strip)} trims={soft.trims}"

    def case_empty_ok():
        g = ShowGate(budget=TokenBudget(limit=20, reserved=0), mode="strict")
        ok, _ = g.show("")
        return ok, "empty show allowed"

    def case_status():
        st = gate.status()
        return "budget" in st and "rejects" in st, str(st.get("budget"))

    for name, fn in [
        ("seed_strip afford", case_afford_seed),
        ("show ok", case_show_ok),
        ("strict reject oversize", case_strict_reject),
        ("soft trim oversize", case_soft_trim),
        ("empty show", case_empty_ok),
        ("status shape", case_status),
    ]:
        run(name, fn)

    passed = sum(1 for p in results if p)
    print(f"=== RESULT: {passed}/{len(results)} PASS ===")
    return passed == len(results)


if __name__ == "__main__":
    import sys
    ok = smoke_show_gate()
    sys.exit(0 if ok else 1)
