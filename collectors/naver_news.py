from datetime import UTC, datetime
from email.utils import parsedate_to_datetime

import httpx

from app.config import get_settings
from collectors.base import NewsCollector, RawNewsItem


class NaverNewsCollector(NewsCollector):
    """Thin Naver News Search API client.

    Real persistence is intentionally separate so collection can be tested with mocked HTTP.
    """

    endpoint = "https://openapi.naver.com/v1/search/news.json"

    def __init__(self, client: httpx.Client | None = None) -> None:
        settings = get_settings()
        self.client_id = settings.naver_client_id
        self.client_secret = settings.naver_client_secret
        self.client = client or httpx.Client(timeout=10)

    def collect(self, keywords: list[str]) -> list[RawNewsItem]:
        if not self.client_id or not self.client_secret:
            raise RuntimeError("NAVER_CLIENT_ID and NAVER_CLIENT_SECRET are required.")

        collected_at = datetime.now(UTC)
        headers = {
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret,
        }
        items: list[RawNewsItem] = []
        for keyword in keywords:
            response = self.client.get(
                self.endpoint,
                headers=headers,
                params={"query": keyword, "display": 100, "sort": "date"},
            )
            response.raise_for_status()
            for row in response.json().get("items", []):
                published_at = _parse_pub_date(row.get("pubDate"))
                items.append(
                    RawNewsItem(
                        source="naver_news",
                        publisher=None,
                        title=row.get("title", ""),
                        summary=row.get("description"),
                        url=row.get("originallink") or row.get("link"),
                        published_at=published_at,
                        collected_at=collected_at,
                        raw_payload={**row, "keyword": keyword},
                    )
                )
        return items


def _parse_pub_date(value: str | None) -> datetime | None:
    if not value:
        return None
    parsed = parsedate_to_datetime(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)
