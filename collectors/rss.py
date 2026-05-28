from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
import xml.etree.ElementTree as ET

import httpx

from collectors.base import NewsCollector, RawNewsItem

DEFAULT_RSS_FEEDS = {
    "hankyung_finance": "https://www.hankyung.com/feed/finance",
    "hankyung_economy": "https://www.hankyung.com/feed/economy",
    "mk_stock": "https://www.mk.co.kr/rss/50200011/",
}


class RssCollector(NewsCollector):
    def __init__(
        self,
        feed_urls: dict[str, str] | None = None,
        client: httpx.Client | None = None,
    ) -> None:
        self.feed_urls = feed_urls or DEFAULT_RSS_FEEDS
        self.client = client or httpx.Client(timeout=15, follow_redirects=True)

    def collect(self, keywords: list[str]) -> list[RawNewsItem]:
        normalized_keywords = [keyword.lower() for keyword in keywords if keyword.strip()]
        collected_at = datetime.now(UTC)
        items: list[RawNewsItem] = []
        for source, url in self.feed_urls.items():
            response = self.client.get(
                url,
                headers={"User-Agent": "korea-news-market-predictor/0.1"},
            )
            response.raise_for_status()
            items.extend(
                _parse_rss_items(
                    source=source,
                    xml_text=response.text,
                    collected_at=collected_at,
                    keywords=normalized_keywords,
                )
            )
        return items


def _parse_rss_items(
    source: str,
    xml_text: str,
    collected_at: datetime,
    keywords: list[str],
) -> list[RawNewsItem]:
    root = ET.fromstring(xml_text)
    items: list[RawNewsItem] = []
    for item in root.findall(".//item"):
        title = _text(item, "title")
        summary = _text(item, "description")
        url = _text(item, "link")
        text_for_filter = f"{title} {summary}".lower()
        if keywords and not any(keyword in text_for_filter for keyword in keywords):
            continue
        if not title or not url:
            continue
        items.append(
            RawNewsItem(
                source=source,
                publisher=_publisher(source),
                title=title,
                summary=summary,
                url=url,
                published_at=_parse_date(_text(item, "pubDate")),
                collected_at=collected_at,
                raw_payload={
                    "source": source,
                    "title": title,
                    "description": summary,
                    "link": url,
                    "pubDate": _text(item, "pubDate"),
                },
            )
        )
    return items


def _text(item: ET.Element, tag: str) -> str:
    found = item.find(tag)
    return (found.text or "").strip() if found is not None else ""


def _parse_date(value: str) -> datetime | None:
    if not value:
        return None
    parsed = parsedate_to_datetime(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _publisher(source: str) -> str:
    if source.startswith("hankyung"):
        return "한국경제"
    if source.startswith("mk"):
        return "매일경제"
    return source
