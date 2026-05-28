from datetime import UTC, datetime

from collectors.base import RawNewsItem
from database.repositories.news_raw import NewsRawRepository


class FakeResult:
    rowcount = 1


class FakeSession:
    def __init__(self) -> None:
        self.executed = None
        self.committed = False

    def execute(self, statement):
        self.executed = statement
        return FakeResult()

    def commit(self) -> None:
        self.committed = True


def test_rows_from_items_skips_empty_url_and_hashes_url() -> None:
    repo = NewsRawRepository(FakeSession())
    rows, skipped = repo._rows_from_items(
        [
            RawNewsItem(source="naver_news", title="A", url="https://example.com/a"),
            RawNewsItem(source="naver_news", title="B", url=""),
        ]
    )

    assert skipped == 1
    assert len(rows) == 1
    assert rows[0]["url_hash"]
    assert rows[0]["raw_payload"] == {}


def test_upsert_many_executes_and_commits() -> None:
    session = FakeSession()
    repo = NewsRawRepository(session)
    stats = repo.upsert_many(
        [
            RawNewsItem(
                source="naver_news",
                title="코스피 상승",
                url="https://example.com/a",
                collected_at=datetime(2026, 5, 26, tzinfo=UTC),
                raw_payload={"keyword": "코스피"},
            )
        ]
    )

    assert stats.requested == 1
    assert stats.skipped == 0
    assert stats.affected == 1
    assert session.executed is not None
    assert session.committed is True
