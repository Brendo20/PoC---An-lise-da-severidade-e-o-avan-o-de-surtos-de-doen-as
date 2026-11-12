"""Busca limitada de notícias recentes via feeds públicos fixos; sem URLs do modelo."""
from __future__ import annotations

import hashlib
import html
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import urlsplit

FEEDS = (
    ("Ministério da Saúde", "https://www.gov.br/saude/pt-br/search_rss?SearchableText=SRAG&sort_on=Date&sort_order=reverse"),
    ("Agência Fiocruz", "https://agencia.fiocruz.br/rss.xml"),
    ("Google News RSS", "https://news.google.com/rss/search?q=SRAG+when%3A30d&hl=pt-BR&gl=BR&ceid=BR%3Apt-419"),
)
HOSTS = {"www.gov.br", "agencia.fiocruz.br", "news.google.com"}
TOPIC = re.compile(r"\bsrag\b|s[ií]ndromes? respirat[oó]rias? agudas? graves?|infogripe", re.I)


def safe_url(url: str) -> bool:
    try:
        parsed = urlsplit(url)
        return parsed.scheme == "https" and bool(parsed.hostname) and not parsed.username and not parsed.password and parsed.port in (None, 443)
    except ValueError:
        return False


class FeedRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not safe_url(newurl) or urlsplit(newurl).hostname not in HOSTS:
            raise ValueError("feed_redirect_not_allowed")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def clean(text: str, limit: int) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]*>", " ", text))).strip()[:limit]


def parse_feed(raw: bytes, source: str, now: datetime) -> list[dict]:
    if len(raw) > 1500000 or re.search(br"<!\s*(DOCTYPE|ENTITY)", raw, re.I):
        raise ValueError("unsafe_or_oversized_feed")
    root = ET.fromstring(raw)
    items = [node for node in root.iter() if node.tag.rsplit("}", 1)[-1] in ("item", "entry")]
    result = []
    for item in items[:150]:
        values = {}
        for child in item:
            key = child.tag.rsplit("}", 1)[-1]
            value = "".join(child.itertext()).strip()
            if key == "link" and child.attrib.get("href"):
                value = child.attrib["href"]
            values.setdefault(key, value)
        title = clean(values.get("title", ""), 240)
        excerpt = clean(values.get("description", values.get("summary", "")), 160)
        link = values.get("link", "").strip()
        stamp = values.get("pubDate") or values.get("published") or values.get("date") or values.get("updated")
        try:
            try:
                published = parsedate_to_datetime(stamp)
            except (TypeError, ValueError):
                published = datetime.fromisoformat((stamp or "").replace("Z", "+00:00"))
            if published.tzinfo is None:
                published = published.replace(tzinfo=timezone.utc)
        except (TypeError, ValueError):
            continue
        if not safe_url(link) or not TOPIC.search(title + " " + excerpt):
            continue
        if not now - timedelta(days=30) <= published <= now + timedelta(minutes=5):
            continue
        result.append({"id": "news-" + hashlib.sha256(link.encode()).hexdigest()[:12],
                       "title": title, "excerpt": excerpt, "url": link,
                       "source": clean(values.get("source", source), 96),
                       "discovery": source, "published_at": published.astimezone(timezone.utc).isoformat()})
    return result


class NewsSearch:
    def __init__(self, opener=None, clock=None):
        self.opener = opener or urllib.request.build_opener(FeedRedirect()).open
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def search(self) -> dict:
        now = self.clock()
        articles, errors, seen = [], [], set()
        for source, url in FEEDS:
            if len(articles) >= 5:
                break
            try:
                request = urllib.request.Request(url, headers={"User-Agent": "indicium-srag-poc/0.1",
                    "Accept": "application/rss+xml, application/atom+xml, application/xml"})
                with self.opener(request, timeout=6) as response:
                    items = parse_feed(response.read(1500001), source, now)
                for item in sorted(items, key=lambda item: item["published_at"], reverse=True):
                    if item["url"] not in seen and len(articles) < 5:
                        seen.add(item["url"]); articles.append(item)
            except Exception as error:
                errors.append({"source": source, "error_type": type(error).__name__})
        return {"status": "available" if articles else "unavailable" if errors else "no_recent_matches",
                "retrieved_at": now.isoformat(), "window_days": 30,
                "scope": "Brasil; não representa cobertura específica de cada UF selecionada",
                "method": "títulos e resumos de feeds; sem leitura integral das matérias",
                "articles": articles, "errors": errors}
