#!/usr/bin/env python3
"""
Deterministic terminal visual flows for Mandell seeds (high-S slice).

From Visual Control Language forms:
  - OpBox styles (standard / drop / side / up)
  - Flow links
  - Deterministic color from syntax hash (no random)
  - Optional short fractal (Rule 90) + recursive branch

NOT included (low-S):
  - Infinite 4800 random combinatorial loop
  - React/CDN host UI
  - Claim of 5000 unique hardware frames as core requirement

Offline-safe. Optional show path — not required for acceptance.
"""

from __future__ import annotations

from typing import List, Optional
import sys
import time


class C:
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    WHITE = "\033[97m"
    GREY = "\033[90m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


def color_for(syntax: str) -> str:
    """Deterministic palette from syntax bytes — no random."""
    val = sum(ord(c) for c in (syntax or ""))
    pal = [C.CYAN, C.MAGENTA, C.GREEN, C.YELLOW, C.WHITE, C.BLUE]
    return pal[val % len(pal)]


def _p(text: str, delay: float = 0.02) -> None:
    sys.stdout.write(text + "\n")
    sys.stdout.flush()
    if delay > 0:
        time.sleep(delay)


def opbox_standard(code: str, name: str, payload: str, color: Optional[str] = None) -> None:
    color = color or color_for(code + name)
    _p(color + "  ╔══════════════════════════════════════════════════════╗" + C.RESET, 0.01)
    _p(color + f"  ║  {C.BOLD}[{code}]{C.RESET}{color} {name[:44].ljust(44)}║" + C.RESET, 0.01)
    _p(color + "  ╟──────────────────────────────────────────────────────╢" + C.RESET, 0.01)
    _p(color + f"  ║  {C.GREY}PAYLOAD:{C.RESET} {C.WHITE}{payload[:42].ljust(42)}{color}║" + C.RESET, 0.01)
    _p(color + "  ╚══════════════════════════════════════════════════════╝" + C.RESET, 0.01)


def opbox_drop(code: str, name: str, payload: str) -> None:
    color = C.MAGENTA
    _p(color + "  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓" + C.RESET, 0.01)
    _p(color + f"  ┃  {C.BOLD}[{code}]{C.RESET}{color} {name[:44].ljust(44)}┃" + C.RESET, 0.01)
    _p(color + "  ┗━━━━━━━━━━━━━━━━━━┓          ┏━━━━━━━━━━━━━━━━━━━━━━┛" + C.RESET, 0.01)
    for line in (
        f"                     ┃  {C.YELLOW}▼    ▼    ▼{color}  ┃",
        f"                     ┃  {C.YELLOW}┊    ┊    ┊{color}  ┃",
        f"                     ▼  {C.YELLOW}·    ·    ·{C.RESET}  ▼",
    ):
        _p(line, 0.05)


def opbox_side(code: str, name: str, payload: str) -> None:
    color = C.GREEN
    _p(color + "  ┌────────────────────────────────────────┐" + C.RESET, 0.01)
    _p(color + f"  │  {C.BOLD}[{code}]{C.RESET}{color} {name[:28].ljust(28)}│" + C.RESET, 0.01)
    _p(color + f"  │ {C.GREY}EXFIL:{C.RESET}  ├════>>> {C.YELLOW}{payload[:20]}{C.RESET}", 0.06)
    _p(color + "  └────────────────────────────────────────┘" + C.RESET, 0.01)


def opbox_up(code: str, name: str, payload: str) -> None:
    color = C.RED
    for line in (
        f"                      {C.RED}⟰    ⟰    ⟰{C.RESET}",
        f"                      {C.RED}·    ·    ·{C.RESET}",
    ):
        _p(line, 0.05)
    _p(color + "  ╔══════════════════╩════════╩══════════════════╗" + C.RESET, 0.01)
    _p(color + f"  ║  {C.BOLD}[{code}]{C.RESET}{color} {name[:40].ljust(40)}║" + C.RESET, 0.01)
    _p(color + f"  ║  {C.GREY}RECOVERY:{C.RESET} {C.WHITE}{payload[:38].ljust(38)}{color}║" + C.RESET, 0.01)
    _p(color + "  ╚══════════════════════════════════════════════╝" + C.RESET, 0.01)


def flow_link(kind: str = "down") -> None:
    if kind == "down":
        _p(C.CYAN + "                         ║" + C.RESET, 0.02)
        _p(C.CYAN + "                         ▼" + C.RESET, 0.02)
    elif kind == "cross":
        _p(C.MAGENTA + "                   ⇖ ⇖  ╬  ⇗ ⇗" + C.RESET, 0.04)
        _p(C.MAGENTA + "                   ⇙ ⇙  ╬  ⇘ ⇘" + C.RESET, 0.04)
        _p(C.CYAN + "                         ▼" + C.RESET, 0.02)


def fractal_rule90(syntax: str = "00[Re-birth]", levels: int = 12) -> None:
    """Deterministic Sierpinski-style lattice (Rule 90)."""
    color = color_for(syntax)
    _p(C.GREY + f">>> FRACTAL {C.WHITE}{syntax}{C.GREY} (Rule 90)" + C.RESET, 0.02)
    width = 47
    state = [0] * width
    state[width // 2] = 1
    for _ in range(levels):
        line = "  "
        for v in state:
            line += f"{color}⟁{C.RESET}" if v else f"{C.GREY}·{C.RESET}"
        _p(line, 0.04)
        nxt = [0] * width
        for i in range(1, width - 1):
            nxt[i] = state[i - 1] ^ state[i + 1]
        state = nxt


def show_seed_pipeline(seed: str = "08[Create] > 15[Map] :: idea") -> None:
    """One finite deterministic show — not an infinite combo loop."""
    _p(C.CYAN + C.BOLD + " ░▒▓█ MANDEL TERMINAL FLOW (deterministic) █▓▒░ " + C.RESET, 0.03)
    opbox_standard("00", "NOVA / edge", "not Floor", C.CYAN)
    flow_link("down")
    opbox_standard("08", "CREATE", seed[:40], C.GREEN)
    flow_link("cross")
    opbox_drop("04", "CHANGE", "transform")
    opbox_up("33", "RESUME / catch", "grid-snap")
    flow_link("down")
    opbox_standard("09", "SHOW", "pipeline complete", C.BLUE)
    _p(C.GREY + "  (optional visual · not required for acceptance)" + C.RESET, 0.01)


def smoke() -> bool:
    print("=== VISUAL TERMINAL SMOKE ===")
    # no infinite loops; just ensure functions callable
    try:
        c = color_for("08[Create]")
        assert c.startswith("\033")
        print("[PASS] deterministic color")
        print("[PASS] module load")
        return True
    except Exception as e:
        print("[FAIL]", e)
        return False


if __name__ == "__main__":
    import sys
    if "--show" in sys.argv:
        show_seed_pipeline()
        fractal_rule90()
        sys.exit(0)
    sys.exit(0 if smoke() else 1)
