import html
import re

TAG_RE = re.compile(r"<[^>]+>")
SPACE_RE = re.compile(r"\s+")


def strip_html(text: str | None) -> str:
    if not text:
        return ""
    return html.unescape(TAG_RE.sub(" ", text))


def normalize_title(title: str) -> str:
    text = strip_html(title).lower()
    text = SPACE_RE.sub(" ", text).strip()
    return text
