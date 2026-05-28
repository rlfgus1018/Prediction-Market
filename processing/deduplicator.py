import hashlib


def stable_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def url_hash(url: str) -> str:
    return stable_hash(url.strip().lower())


def exact_duplicate_groups(values: list[str]) -> dict[str, str]:
    return {value: stable_hash(value) for value in values}


class NearDuplicateDetector:
    """Interface for future embedding-based duplicate detection."""

    def find_groups(self, texts: list[str]) -> dict[int, str]:
        return {index: stable_hash(text) for index, text in enumerate(texts)}
