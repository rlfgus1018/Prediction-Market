from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from collectors.ingest_news import collect_naver_news_to_db, collect_rss_news_to_db
from database.session import get_db

router = APIRouter()


class NaverCollectRequest(BaseModel):
    keywords: list[str]


@router.get("/latest")
def latest_news() -> dict[str, object]:
    return {
        "items": [],
        "message": "News ingestion endpoints will read from news_raw/news_features.",
    }


@router.post("/collect/naver")
def collect_naver_news(payload: NaverCollectRequest, db: Session = Depends(get_db)) -> dict[str, int]:
    stats = collect_naver_news_to_db(payload.keywords, db)
    return {
        "requested": stats.requested,
        "skipped": stats.skipped,
        "affected": stats.affected,
    }


@router.post("/collect/rss")
def collect_rss_news(payload: NaverCollectRequest, db: Session = Depends(get_db)) -> dict[str, int]:
    stats = collect_rss_news_to_db(payload.keywords, db)
    return {
        "requested": stats.requested,
        "skipped": stats.skipped,
        "affected": stats.affected,
    }
