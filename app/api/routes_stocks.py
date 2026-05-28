from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from collectors.ingest_stocks import collect_krx_listed_stocks_to_db
from database.repositories.listed_stocks import ListedStockRepository
from database.session import get_db

router = APIRouter()


class KrxListedStockCollectRequest(BaseModel):
    base_date: str | None = Field(default=None, description="YYYYMMDD")
    item_name: str | None = None
    short_code: str | None = None
    rows: int = 1000
    page: int = 1


@router.post("/collect/krx-listed")
def collect_krx_listed_stocks(
    payload: KrxListedStockCollectRequest,
    db: Session = Depends(get_db),
) -> dict[str, int]:
    stats = collect_krx_listed_stocks_to_db(
        db,
        base_date=payload.base_date,
        item_name=payload.item_name,
        short_code=payload.short_code,
        rows=payload.rows,
        page=payload.page,
    )
    return {
        "requested": stats.requested,
        "skipped": stats.skipped,
        "affected": stats.affected,
    }


@router.get("/listed/latest")
def latest_listed_stocks(db: Session = Depends(get_db)) -> dict[str, Any]:
    rows = ListedStockRepository(db).latest()
    return {
        "items": [
            {
                "base_date": row.base_date,
                "short_code": row.short_code,
                "isin_code": row.isin_code,
                "market_category": row.market_category,
                "item_name": row.item_name,
                "corp_registration_number": row.corp_registration_number,
                "corp_name": row.corp_name,
            }
            for row in rows
        ]
    }
