from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session

from collectors.base import RawNewsItem
from database.models import NewsRaw
from processing.deduplicator import url_hash


@dataclass(frozen=True)
class UpsertStats:
    requested: int
    skipped: int
    affected: int


class NewsRawRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def upsert_many(self, items: list[RawNewsItem]) -> UpsertStats:
        rows, skipped = self._rows_from_items(items)
        if not rows:
            return UpsertStats(requested=len(items), skipped=skipped, affected=0)

        bind = getattr(self.db, "bind", None)
        insert_fn = sqlite_insert if bind and bind.dialect.name == "sqlite" else pg_insert
        statement = insert_fn(NewsRaw).values(rows)
        update_columns = {
            "source": statement.excluded.source,
            "publisher": statement.excluded.publisher,
            "title": statement.excluded.title,
            "summary": statement.excluded.summary,
            "url_hash": statement.excluded.url_hash,
            "published_at": statement.excluded.published_at,
            "collected_at": statement.excluded.collected_at,
            "raw_payload": statement.excluded.raw_payload,
        }
        statement = statement.on_conflict_do_update(
            index_elements=[NewsRaw.url],
            set_=update_columns,
        )

        result = self.db.execute(statement)
        self.db.commit()
        affected = result.rowcount if result.rowcount is not None else len(rows)
        return UpsertStats(requested=len(items), skipped=skipped, affected=affected)

    def _rows_from_items(self, items: list[RawNewsItem]) -> tuple[list[dict[str, Any]], int]:
        rows_by_url: dict[str, dict[str, Any]] = {}
        skipped = 0
        for item in items:
            if not item.url:
                skipped += 1
                continue
            collected_at = item.collected_at or datetime.now(UTC)
            rows_by_url[item.url] = {
                "source": item.source,
                "publisher": item.publisher,
                "title": item.title,
                "summary": item.summary,
                "url": item.url,
                "url_hash": url_hash(item.url),
                "published_at": item.published_at,
                "collected_at": collected_at,
                "raw_payload": item.raw_payload or {},
            }
        return list(rows_by_url.values()), skipped
