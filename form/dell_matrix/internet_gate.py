#!/usr/bin/env python3
"""
InternetGate — network search far and wide for matrix growth.

DEFAULT OFF for pure offline runs.
Auto-growth may enable when auto_allowed=True (default).

  fetch_url / research_topic / search_public / search_far_wide

Floor stays locked. Hosts expand via allow_host.
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

DEFAULT_HOSTS = [
    "en.wikipedia.org", "api.wikimedia.org", "www.wikidata.org",
    "api.duckduckgo.com", "duckduckgo.com",
    "en.wiktionary.org", "arxiv.org", "export.arxiv.org",
    "eutils.ncbi.nlm.nih.gov", "api.semanticscholar.org",
    "api.stackexchange.com", "stackoverflow.com",
    "api.github.com", "github.com", "raw.githubusercontent.com",
    "httpbin.org", "example.com",
]


@dataclass
class InternetGate:
    on: bool = False
    auto_allowed: bool = True
    allowed_hosts: List[str] = field(default_factory=lambda: list(DEFAULT_HOSTS))
    last_fetch: Dict[str, Any] = field(default_factory=dict)
    last_search: Dict[str, Any] = field(default_factory=dict)
    fetch_log: List[Dict[str, Any]] = field(default_factory=list)
    timeout_s: float = 14.0
    max_bytes: int = 250_000

    def turn_on(self) -> Dict[str, Any]:
        self.on = True
        return {"ok": True, "on": True, "msg": "Internet ON · search_far_wide ready · Floor locked"}

    def turn_off(self) -> Dict[str, Any]:
        self.on = False
        return {"ok": True, "on": False, "msg": "Internet OFF"}

    def ensure_on_for_auto(self) -> bool:
        if self.on:
            return True
        if self.auto_allowed:
            self.on = True
            return True
        return False

    def status(self) -> Dict[str, Any]:
        return {
            "on": self.on,
            "auto_allowed": self.auto_allowed,
            "hosts": list(self.allowed_hosts)[:24],
            "host_count": len(self.allowed_hosts),
            "log_len": len(self.fetch_log),
            "last_search_q": (self.last_search or {}).get("query"),
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "on": self.on,
            "auto_allowed": self.auto_allowed,
            "allowed_hosts": list(self.allowed_hosts)[:48],
            "log_len": len(self.fetch_log),
        }

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "InternetGate":
        g = cls()
        if not data:
            return g
        g.on = bool(data.get("on"))
        g.auto_allowed = bool(data.get("auto_allowed", True))
        hosts = data.get("allowed_hosts")
        if isinstance(hosts, list) and hosts:
            g.allowed_hosts = [str(h) for h in hosts[:48]]
        return g

    def _host_ok(self, url: str) -> bool:
        m = re.match(r"^https?://([^/]+)", url.strip(), re.I)
        if not m:
            return False
        host = m.group(1).lower().split(":")[0]
        if host in self.allowed_hosts:
            return True
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
            return {"ok": False, "error": "Internet gate OFF · internet on", "on": False}
        url = (url or "").strip()
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
        if not self._host_ok(url):
            return {
                "ok": False,
                "error": f"host not allowed · allow_host first · sample={self.allowed_hosts[:4]}",
                "url": url,
            }
        try:
            req = Request(
                url,
                headers={
                    "User-Agent": "DellMatrix/AutoGrowth (research; Floor locked)",
                    "Accept": "text/html,application/json,text/plain,*/*",
                },
            )
            with urlopen(req, timeout=self.timeout_s) as resp:
                raw = resp.read(self.max_bytes)
                ctype = resp.headers.get("Content-Type", "")
                code = getattr(resp, "status", 200)
            text = raw.decode("utf-8", errors="replace") if as_text else ""
            plain = re.sub(r"<script[\s\S]*?</script>", " ", text, flags=re.I)
            plain = re.sub(r"<style[\s\S]*?</style>", " ", plain, flags=re.I)
            plain = re.sub(r"<[^>]+>", " ", plain)
            plain = re.sub(r"\s+", " ", plain).strip()
            entry = {
                "ok": True, "url": url, "status": code, "content_type": ctype,
                "bytes": len(raw), "preview": plain[:1200], "ts": time.time(),
            }
            self.last_fetch = entry
            self.fetch_log.append({"url": url, "ok": True, "bytes": len(raw), "ts": entry["ts"]})
            while len(self.fetch_log) > 40:
                self.fetch_log.pop(0)
            return entry
        except (URLError, HTTPError, TimeoutError, OSError) as e:
            entry = {"ok": False, "url": url, "error": f"{type(e).__name__}: {e}", "ts": time.time()}
            self.last_fetch = entry
            self.fetch_log.append({"url": url, "ok": False, "error": str(e), "ts": entry["ts"]})
            return entry

    def _json_get(self, url: str) -> Dict[str, Any]:
        if not self.on:
            return {"ok": False, "error": "OFF"}
        try:
            req = Request(url, headers={"User-Agent": "DellMatrix/AutoGrowth", "Accept": "application/json"})
            with urlopen(req, timeout=self.timeout_s) as resp:
                raw = resp.read(self.max_bytes)
            data = json.loads(raw.decode("utf-8", errors="replace"))
            return {"ok": True, "url": url, "data": data}
        except Exception as e:
            return {"ok": False, "url": url, "error": f"{type(e).__name__}: {e}"}

    def research_topic(self, topic: str) -> Dict[str, Any]:
        if not self.on:
            return {"ok": False, "error": "Internet gate OFF"}
        topic = (topic or "intelligence").strip() or "intelligence"
        title = quote_plus(topic.replace(" ", "_"))
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
        self.allow_host("en.wikipedia.org")
        j = self._json_get(url)
        if j.get("ok") and isinstance(j.get("data"), dict):
            data = j["data"]
            extract = data.get("extract") or data.get("description") or ""
            return {
                "ok": bool(extract),
                "topic": topic,
                "title": data.get("title") or topic,
                "extract": str(extract)[:1200],
                "url": data.get("content_urls", {}).get("desktop", {}).get("page") or url,
                "source": "wikipedia_summary",
            }
        r = self.fetch_url(url)
        return {
            "ok": bool(r.get("preview")),
            "topic": topic,
            "title": topic,
            "extract": (r.get("preview") or "")[:900],
            "url": url,
            "source": "wikipedia_raw",
        }

    # alias used by awake / auto
    def research(self, topic: str) -> Dict[str, Any]:
        return self.research_topic(topic)

    def search_public(self, query: str) -> Dict[str, Any]:
        if not self.on:
            return {"ok": False, "error": "Internet OFF", "hits": []}
        query = (query or "").strip()
        if len(query) < 2:
            return {"ok": False, "error": "empty query", "hits": []}

        hits: List[Dict[str, Any]] = []

        self.allow_host("api.duckduckgo.com")
        ddg_url = f"https://api.duckduckgo.com/?q={quote_plus(query)}&format=json&no_html=1&skip_disambig=1"
        ddg = self._json_get(ddg_url)
        if ddg.get("ok") and isinstance(ddg.get("data"), dict):
            data = ddg["data"]
            abstract = (data.get("AbstractText") or "").strip()
            if abstract:
                hits.append({
                    "title": data.get("Heading") or query,
                    "text": abstract[:900],
                    "url": data.get("AbstractURL") or ddg_url,
                    "source": "duckduckgo_abstract",
                })
            for topic in (data.get("RelatedTopics") or [])[:8]:
                if isinstance(topic, dict) and topic.get("Text"):
                    hits.append({
                        "title": (topic.get("Text") or "")[:80],
                        "text": (topic.get("Text") or "")[:500],
                        "url": topic.get("FirstURL") or "",
                        "source": "duckduckgo_related",
                    })
                elif isinstance(topic, dict):
                    for t2 in (topic.get("Topics") or [])[:3]:
                        if isinstance(t2, dict) and t2.get("Text"):
                            hits.append({
                                "title": (t2.get("Text") or "")[:80],
                                "text": (t2.get("Text") or "")[:500],
                                "url": t2.get("FirstURL") or "",
                                "source": "duckduckgo_related",
                            })

        wiki = self.research_topic(query)
        if wiki.get("extract"):
            hits.append({
                "title": wiki.get("title") or query,
                "text": wiki.get("extract") or "",
                "url": wiki.get("url") or "",
                "source": "wikipedia",
            })

        self.allow_host("www.wikidata.org")
        wd_url = (
            "https://www.wikidata.org/w/api.php?action=wbsearchentities&search="
            + quote_plus(query) + "&language=en&format=json&limit=6"
        )
        wd = self._json_get(wd_url)
        if wd.get("ok") and isinstance(wd.get("data"), dict):
            for ent in (wd["data"].get("search") or [])[:6]:
                hits.append({
                    "title": ent.get("label") or query,
                    "text": f"{ent.get('label', '')}: {ent.get('description', '')}",
                    "url": ent.get("concepturi") or "",
                    "source": "wikidata",
                })

        self.last_search = {
            "query": query,
            "hit_count": len(hits),
            "ts": time.time(),
            "sources": sorted({h["source"] for h in hits}),
        }
        return {
            "ok": len(hits) > 0,
            "query": query,
            "hits": hits[:20],
            "sources": self.last_search["sources"],
            "count": len(hits),
        }

    def search_far_wide(self, query: str, *, extra_topics: Optional[List[str]] = None) -> Dict[str, Any]:
        if not self.on and not self.ensure_on_for_auto():
            return {"ok": False, "error": "Internet OFF and auto not allowed", "ideas": []}

        primary = self.search_public(query)
        ideas: List[Dict[str, Any]] = []
        for h in primary.get("hits") or []:
            ideas.append({
                "label": (h.get("title") or query)[:72],
                "words": (h.get("text") or "")[:400],
                "source": f"net:{h.get('source')}",
                "url": h.get("url") or "",
            })

        topics = list(extra_topics or [])
        toks = [t for t in re.findall(r"[A-Za-z]{4,}", query)
                if t.lower() not in {"that", "with", "from", "this", "what", "when"}]
        for t in toks[:4]:
            if t.lower() not in {x.lower() for x in topics}:
                topics.append(t)
        for t in topics[:5]:
            r = self.research_topic(t)
            if r.get("extract"):
                ideas.append({
                    "label": (r.get("title") or t)[:72],
                    "words": (r.get("extract") or "")[:400],
                    "source": "net:wikipedia_expand",
                    "url": r.get("url") or "",
                })

        seen = set()
        unique = []
        for idea in ideas:
            key = (idea.get("label") or "")[:40].lower()
            if not key or key in seen:
                continue
            seen.add(key)
            unique.append(idea)

        return {
            "ok": len(unique) > 0,
            "query": query,
            "ideas": unique[:24],
            "count": len(unique),
            "primary_sources": primary.get("sources") or [],
            "internet_on": self.on,
        }


NET = InternetGate()


def smoke() -> bool:
    print("=== INTERNET GATE SMOKE ===")
    r = []
    def rec(n, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {n}"); r.append(bool(ok))
    g = InternetGate()
    rec("default_off", g.on is False)
    rec("blocked", g.fetch_url("https://example.com/").get("ok") is False)
    g.turn_on()
    rec("on", g.on is True)
    rec("fetch_shape", isinstance(g.fetch_url("https://example.com/"), dict))
    fw = g.search_far_wide("eigenvalue")
    rec("far_wide_shape", "ideas" in fw)
    g.turn_off()
    rec("off", g.on is False)
    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
