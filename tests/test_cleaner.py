from processing.cleaner import normalize_title, strip_html


def test_strip_html_unescapes_text() -> None:
    assert strip_html("<b>코스피</b>&nbsp;상승") == " 코스피 \xa0상승"


def test_normalize_title() -> None:
    assert normalize_title("<b>코스피</b>   상승") == "코스피 상승"
