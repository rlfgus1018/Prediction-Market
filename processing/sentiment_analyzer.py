from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class SentimentResult:
    label: str
    score: float
    probabilities: dict[str, float]


class SentimentAnalyzer(Protocol):
    def analyze(self, text: str) -> SentimentResult:
        ...

    def analyze_batch(self, texts: list[str]) -> list[SentimentResult]:
        ...


class KeywordSentimentAnalyzer:
    """Small deterministic baseline for tests and local development."""

    positive_words = {"상승", "호조", "개선", "강세", "증가", "흑자"}
    negative_words = {"하락", "부진", "악화", "약세", "감소", "적자"}

    def analyze(self, text: str) -> SentimentResult:
        positive = sum(word in text for word in self.positive_words)
        negative = sum(word in text for word in self.negative_words)
        score = float(positive - negative)
        label = "neutral"
        if score > 0:
            label = "positive"
        elif score < 0:
            label = "negative"
        return SentimentResult(label=label, score=score, probabilities={label: 1.0})

    def analyze_batch(self, texts: list[str]) -> list[SentimentResult]:
        return [self.analyze(text) for text in texts]
