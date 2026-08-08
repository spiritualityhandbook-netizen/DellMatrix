#!/usr/bin/env python3
"""
InternetGate — opt-in network for the matrix.

DEFAULT: OFF (Origin offline law).
User must explicitly allow:  internet on

When ON:
  · fetch_url / search_public for Code Evolution research notes
  · still never auto-writes live plane without Nursery/confirm
  · Floor stays locked

Law: offline acceptance does not require this gate.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from urllib.parse import quote_plus
import json
import time
import re


@dataclass
class InternetGate:
    on: bool = False
    allowed_hosts: List[str] = field(default_factory=lambda: [
        "en.wikipedia.org",
        "api.wikimedia.org",
        "www.wikidata.org",
        "httpbin.org",
        "example.com",
    ])
    last_fetch: Dict[str, Any] = field(default_factory=dict)
    fetch_log: List[Dict[str, Any]] = field(default_factory=list)
    timeout_s: float = 12.0
    max_bytes: int = 200_000

    def turn_on(self) -> Dict[str, Any]:
        self.on = True
        return {"ok": True, "on": True, "msg": "Internet ON · opt-in · Floor still locked · use: net fetch <url> | ce research"}

    def turn_off(self) -> Dict[str, Any]:
        self.on = False
        return {"ok": True, "on": False, "msg": "Internet OFF · matrix offline again"}

    def status(self) -> Dict[str, Any]:
        return {
            "on": self.on,
            "hosts": list(self.allowed_hosts),
            "log_len": len(self.fetch_log),
            "last": dict(self.last_fetch) if self.last_fetch else {},
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "on": self.on,
            "allowed_hosts": list(self.allowed_hosts)[:32],
            "log_len": len(self.fetch_log),
        }

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "InternetGate":
        g = cls()
        if not data:
            return g
        g.on = bool(data.get("on"))
        hosts = data.get("allowed_hosts")
        if isinstance(hosts, list) and hosts:
            g.allowed_hosts = [str(h) for h in hosts[:32]]
        return g

    def _host_ok(self, url: str) -> bool:
        m = re.match(r"^https?://([^/]+)", url.strip(), re.I)
        if not m:
            return False
        host = m.group(1).lower().split(":")[0]
        if host in self.allowed_hosts:
            return True
        # allow subdomains of allowed
        for h in self.allowed_hosts:
            if host.endswith("." + h) or host == h:
                return True
        return False

    def allow_host(self, host: str) -> str:
        h = (host or "").strip().lower().split("/")[0].split(":")[0]
        if h and h not in self.allowed_hosts:
            self.allowed_hosts.append(h)
        return h

    def fetch_url(self, url: str, *, as_text: bool = True) -> Dict[str, Any]:
        if not self.on:
            return {
                "ok": False,
                "error": "Internet gate OFF · type: internet on",
                "on": False,
            }
        url = (url or "").strip()
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
        if not self._host_ok(url):
            return {
                "ok": False,
                "error": f"host not allowed · internet allow <host> first · allowed={self.allowed_hosts[:6]}",
                "url": url,
            }
        try:
            req = Request(url, headers={"User-Agent": "DellMatrix/CodeEvolution (opt-in research; Floor locked)"})
            with urlopen(req, timeout=self.timeout_s) as resp:
                raw = resp.read(self.max_bytes)
                ctype = resp.headers.get("Content-Type", "")
                code = getattr(resp, "status", 200)
            text = raw.decode("utf-8", errors="replace") if as_text else ""
            # strip tags lightly for research notes
            plain = re.sub(r"<script[\s\S]*?</script>", " ", text, flags=re.I)
            plain = re.sub(r"<style[\s\S]*?</style>", " ", plain, flags=re.I)
            plain = re.sub(r"<[^>]+>", " ", plain)
            plain = re.sub(r"\s+", " ", plain).strip()
            entry = {
                "ok": True,
                "url": url,
                "status": code,
                "content_type": ctype,
                "bytes": len(raw),
                "preview": plain[:800],
                "ts": time.time(),
            }
            self.last_fetch = entry
            self.fetch_log.append({"url": url, "ok": True, "bytes": len(raw), "ts": entry["ts"]})
            while len(self.fetch_log) > 24:
                self.fetch_log.pop(0)
            return entry
        except (URLError, HTTPError, TimeoutError, OSError) as e:
            entry = {"ok": False, "url": url, "error": str(e), "ts": time.time()}
            self.last_fetch = entry
            self.fetch_log.append({"url": url, "ok": False, "error": str(e), "ts": entry["ts"]})
            return entry

    def research_topic(self, topic: str) -> Dict[str, Any]:
        """
        Public Wikipedia REST summary — educational only.
        PROJECTED_NOT_FACT for any claim beyond the summary text.
        """
        if not self.on:
            return {"ok": False, "error": "Internet gate OFF · internet on"}
        topic = (topic or "ternary logic").strip() or "ternary logic"
        # Wikipedia API
        title = quote_plus(topic.replace(" ", "_"))
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
        self.allow_host("en.wikipedia.org")
        r = self.fetch_url(url)
        if not r.get("ok"):
            return r
        # parse JSON if possible
        try:
            # re-fetch as we need full json - preview was stripped
            req = Request(url, headers={"User-Agent": "DellMatrix/CodeEvolution"})
            with urlopen(req, timeout=self.timeout_s) as resp:
                data = json.loads(resp.read(self.max_bytes).decode("utf-8", errors="replace"))
            extract = data.get("extract") or data.get("description") or ""
            return {
                "ok": True,
                "topic": topic,
                "title": data.get("title") or topic,
                "extract": extract[:1200],
                "url": data.get("content_urls", {}).get("desktop", {}).get("page") or url,
                "source": "wikipedia_summary",
                "honesty": "PROJECTED_NOT_FACT beyond cited public summary · educational only",
            }
        except Exception as e:
            return {
                "ok": True,
                "topic": topic,
                "extract": r.get("preview") or "",
                "url": url,
                "source": "raw_preview",
                "note": str(e),
                "honesty": "PROJECTED_NOT_FACT",
            }


def smoke() -> bool:
    print("=== INTERNET GATE SMOKE ===")
    g = InternetGate()
    r = []
    def rec(n, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {n}")
        r.append(bool(ok))
    rec("default off", g.on is False)
    blocked = g.fetch_url("https://example.com/")
    rec("blocked when off", blocked.get("ok") is False)
    g.turn_on()
    rec("on", g.on is True)
    # example.com is allowed
    got = g.fetch_url("https://example.com/")
    rec("fetch example", got.get("ok") is True or "error" in got)  # network may fail in sandbox
    g.turn_off()
    rec("off again", g.on is False)
    d = InternetGate.from_dict(g.to_dict())
    rec("roundtrip", d.on is False)
    print(f"=== {sum(r)}/{len(r)} ===")
    # don't require live network for smoke pass
    return r[0] and r[1] and r[2] and r[4] and r[5]


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
