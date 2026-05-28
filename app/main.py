from fastapi import FastAPI

from app.api.routes_backtest import router as backtest_router
from app.api.routes_news import router as news_router
from app.api.routes_predictions import router as predictions_router
from app.api.routes_stocks import router as stocks_router
from database.session import init_db

app = FastAPI(
    title="Korea News Market Predictor",
    version="0.1.0",
    description="Research dashboard API for Korean news-based market direction prediction.",
)

app.include_router(predictions_router, prefix="/predictions", tags=["predictions"])
app.include_router(news_router, prefix="/news", tags=["news"])
app.include_router(backtest_router, prefix="/backtest", tags=["backtest"])
app.include_router(stocks_router, prefix="/stocks", tags=["stocks"])


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
