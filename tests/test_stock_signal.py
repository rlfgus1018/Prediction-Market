from models.stock_signal import _keywords_for_stock


def test_keywords_for_stock_deduplicates_values() -> None:
    keywords = _keywords_for_stock(None, "삼성전자")

    assert keywords == ["삼성전자"]
