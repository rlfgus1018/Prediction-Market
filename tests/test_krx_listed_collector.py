from collectors.krx_listed import _extract_items, _to_listed_stock_item


def test_extract_items_handles_single_item_dict() -> None:
    payload = {
        "response": {
            "body": {
                "items": {
                    "item": {
                        "basDt": "20260102",
                        "srtnCd": "005930",
                        "isinCd": "KR7005930003",
                        "mrktCtg": "KOSPI",
                        "itmsNm": "Samsung Electronics",
                    }
                }
            }
        }
    }

    rows = _extract_items(payload)

    assert len(rows) == 1
    assert rows[0]["srtnCd"] == "005930"


def test_to_listed_stock_item_maps_public_data_fields() -> None:
    item = _to_listed_stock_item(
        {
            "basDt": "20260102",
            "srtnCd": "005930",
            "isinCd": "KR7005930003",
            "mrktCtg": "KOSPI",
            "itmsNm": "Samsung Electronics",
            "crno": "1301110006246",
            "corpNm": "Samsung Electronics Co., Ltd.",
        },
        collected_at=None,
    )

    assert item.base_date == "20260102"
    assert item.short_code == "005930"
    assert item.item_name == "Samsung Electronics"
