from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

import httpx

from app.config import get_settings


@dataclass(frozen=True)
class ListedStockItem:
    base_date: str
    short_code: str
    item_name: str
    isin_code: str | None = None
    market_category: str | None = None
    corp_registration_number: str | None = None
    corp_name: str | None = None
    collected_at: datetime | None = None
    raw_payload: dict[str, Any] | None = None


class KrxListedStockCollector:
    endpoint = "https://apis.data.go.kr/1160100/service/GetKrxListedInfoService/getItemInfo"

    def __init__(self, client: httpx.Client | None = None, service_key: str | None = None) -> None:
        settings = get_settings()
        self.service_key = service_key or settings.public_data_service_key
        self.client = client or httpx.Client(timeout=20, follow_redirects=True)

    def collect(
        self,
        base_date: str | None = None,
        item_name: str | None = None,
        short_code: str | None = None,
        rows: int = 1000,
        page: int = 1,
    ) -> list[ListedStockItem]:
        if not self.service_key:
            raise RuntimeError("PUBLIC_DATA_SERVICE_KEY is required.")

        params = {
            "serviceKey": self.service_key,
            "resultType": "json",
            "numOfRows": rows,
            "pageNo": page,
        }
        if base_date:
            params["basDt"] = base_date
        if item_name:
            params["likeItmsNm"] = item_name
        if short_code:
            params["likeSrtnCd"] = short_code

        response = self.client.get(self.endpoint, params=params)
        response.raise_for_status()
        payload = response.json()
        rows_payload = _extract_items(payload)
        collected_at = datetime.now(UTC)
        return [_to_listed_stock_item(row, collected_at) for row in rows_payload]


def _extract_items(payload: dict[str, Any]) -> list[dict[str, Any]]:
    body = payload.get("response", {}).get("body", {})
    items = body.get("items", {})
    rows = items.get("item", []) if isinstance(items, dict) else []
    if isinstance(rows, dict):
        return [rows]
    return rows if isinstance(rows, list) else []


def _to_listed_stock_item(row: dict[str, Any], collected_at: datetime) -> ListedStockItem:
    return ListedStockItem(
        base_date=str(row.get("basDt", "")),
        short_code=str(row.get("srtnCd", "")),
        isin_code=row.get("isinCd"),
        market_category=row.get("mrktCtg"),
        item_name=str(row.get("itmsNm", "")),
        corp_registration_number=row.get("crno"),
        corp_name=row.get("corpNm"),
        collected_at=collected_at,
        raw_payload=row,
    )
