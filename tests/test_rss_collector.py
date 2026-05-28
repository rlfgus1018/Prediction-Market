from datetime import UTC, datetime

from collectors.rss import _parse_rss_items


RSS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <item>
      <title>KOSPI rises on semiconductor strength</title>
      <description>Chip exporters led the market.</description>
      <link>https://example.com/a</link>
      <pubDate>Tue, 26 May 2026 01:00:00 +0900</pubDate>
    </item>
    <item>
      <title>Sports update</title>
      <description>Not market related.</description>
      <link>https://example.com/b</link>
    </item>
  </channel>
</rss>
"""


def test_parse_rss_items_filters_keywords() -> None:
    items = _parse_rss_items(
        source="test",
        xml_text=RSS_XML,
        collected_at=datetime(2026, 5, 26, tzinfo=UTC),
        keywords=["kospi"],
    )

    assert len(items) == 1
    assert items[0].url == "https://example.com/a"
    assert items[0].published_at is not None
