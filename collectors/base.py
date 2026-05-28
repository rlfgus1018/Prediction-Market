from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class RawNewsItem:
    source: str
    title: str
    url: str
    publisher: str | None = None
    summary: str | None = None
    published_at: datetime | None = None
    collected_at: datetime | None = None
    raw_payload: dict[str, Any] | None = None


class NewsCollector(ABC):
    @abstractmethod
    def collect(self, keywords: list[str]) -> list[RawNewsItem]:
        """Collect raw news items for the provided keywords."""
