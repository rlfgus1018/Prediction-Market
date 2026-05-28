from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session

from collectors.krx_listed import ListedStockItem
from database.models import ListedStock


@dataclass(frozen=True)
class ListedStockUpsertStats:
    requested: int
    skipped: int
    affected: int


class ListedStockRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def upsert_many(self, items: list[ListedStockItem]) -> ListedStockUpsertStats:
        rows, skipped = self._rows_from_items(items)
        if not rows:
            return ListedStockUpsertStats(requested=len(items), skipped=skipped, affected=0)

        bind = getattr(self.db, "bind", None)
        insert_fn = sqlite_insert if bind and bind.dialect.name == "sqlite" else pg_insert
        statement = insert_fn(ListedStock).values(rows)
        statement = statement.on_conflict_do_update(
            index_elements=[ListedStock.base_date, ListedStock.short_code],
            set_={
                "isin_code": statement.excluded.isin_code,
                "market_category": statement.excluded.market_category,
                "item_name": statement.excluded.item_name,
                "corp_registration_number": statement.excluded.corp_registration_number,
                "corp_name": statement.excluded.corp_name,
                "raw_payload": statement.excluded.raw_payload,
                "collected_at": statement.excluded.collected_at,
            },
        )
        result = self.db.execute(statement)
        self.db.commit()
        return ListedStockUpsertStats(
            requested=len(items),
            skipped=skipped,
            affected=result.rowcount or len(rows),
        )

    def latest(self, limit: int = 100) -> list[ListedStock]:
        statement = (
            select(ListedStock)
            .order_by(ListedStock.base_date.desc(), ListedStock.short_code)
            .limit(limit)
        )
        return list(self.db.scalars(statement).all())

    def _rows_from_items(self, items: list[ListedStockItem]) -> tuple[list[dict[str, Any]], int]:
        rows_by_key: dict[tuple[str, str], dict[str, Any]] = {}
        skipped = 0
        for item in items:
            if not item.base_date or not item.short_code or not item.item_name:
                skipped += 1
                continue
            rows_by_key[(item.base_date, item.short_code)] = {
                "base_date": item.base_date,
                "short_code": item.short_code,
                "isin_code": item.isin_code,
                "market_category": item.market_category,
                "item_name": item.item_name,
                "corp_registration_number": item.corp_registration_number,
                "corp_name": item.corp_name,
                "raw_payload": item.raw_payload or {},
                "collected_at": item.collected_at,
            }
        return list(rows_by_key.values()), skipped
