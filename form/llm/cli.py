#!/usr/bin/env python3
"""
LLM bridge CLI for sister terminal.

  python -m form.llm.cli --detect
  python -m form.llm.cli --provider grok "summarize my matrix"
  python -m form.llm.cli --all "enhance trading plan"
  python -m form.llm.cli --matrix --owner Sister --provider claude
"""

from __future__ import annotations

import json
import sys

from form.llm.bridge import LLMBridge, enhance_matrix


def main() -> None:
    args = sys.argv[1:]
    if not args or "--detect" in args:
        print(json.dumps(LLMBridge().detect(), indent=2))
        return

    owner = "Sister"
    provider = None
    use_all = "--all" in args
    use_matrix = "--matrix" in args
    for i, a in enumerate(args):
        if a == "--owner" and i + 1 < len(args):
            owner = args[i + 1]
        if a == "--provider" and i + 1 < len(args):
            provider = args[i + 1]

    prompt_parts = [a for a in args if not a.startswith("--") and a not in (owner, provider or "")]
    # strip flags values already parsed
    cleaned = []
    skip = False
    for a in args:
        if skip:
            skip = False
            continue
        if a in ("--owner", "--provider"):
            skip = True
            continue
        if a.startswith("--"):
            continue
        cleaned.append(a)
    prompt = " ".join(cleaned) or "Give a short practical enhancement for this trading matrix."

    if use_matrix:
        try:
            from form.trading.session import TradingSession

            st = TradingSession(owner=owner).status()
            prompt = (
                f"Owner={owner}\nTrading status JSON:\n{json.dumps(st)[:4000]}\n\nUser ask: {prompt}"
            )
        except Exception as e:
            prompt = f"(matrix load error: {e})\n{prompt}"

    bridge = LLMBridge()
    if use_all:
        print(json.dumps(enhance_matrix(bridge, prompt), indent=2))
    elif provider:
        print(json.dumps(bridge.call(provider, prompt).to_dict(), indent=2))
    else:
        # first available
        det = bridge.detect()
        for p in ("grok", "claude", "gemini", "aistudio", "copilot"):
            if det.get(p):
                print(json.dumps(bridge.call(p, prompt).to_dict(), indent=2))
                return
        print(json.dumps({"ok": False, "error": "no providers configured", "detect": det}, indent=2))


if __name__ == "__main__":
    main()
