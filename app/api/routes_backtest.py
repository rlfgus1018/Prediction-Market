from fastapi import APIRouter

router = APIRouter()


@router.get("/summary")
def backtest_summary() -> dict[str, object]:
    return {
        "metrics": {},
        "message": "Backtest metrics will be populated after model experiments.",
    }
