from sqlalchemy.orm import Session

from collectors.krx_listed import KrxListedStockCollector
from database.repositories.listed_stocks import ListedStockRepository, ListedStockUpsertStats


def collect_krx_listed_stocks_to_db(
    db: Session,
    base_date: str | None = None,
    item_name: str | None = None,
    short_code: str | None = None,
    rows: int = 1000,
    page: int = 1,
    collector: KrxListedStockCollector | None = None,
) -> ListedStockUpsertStats:
    stock_collector = collector or KrxListedStockCollector()
    items = stock_collector.collect(
        base_date=base_date,
        item_name=item_name,
        short_code=short_code,
        rows=rows,
        page=page,
    )
    return ListedStockRepository(db).upsert_many(items)
