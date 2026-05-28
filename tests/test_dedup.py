from processing.deduplicator import stable_hash, url_hash


def test_stable_hash_is_deterministic() -> None:
    assert stable_hash("abc") == stable_hash("abc")


def test_url_hash_normalizes_case_and_space() -> None:
    assert url_hash(" HTTPS://EXAMPLE.COM/a ") == url_hash("https://example.com/a")
