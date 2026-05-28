class EventClassifier:
    labels = [
        "interest_rate",
        "fx",
        "semiconductor",
        "exports",
        "policy",
        "geopolitics",
        "earnings",
        "market_flow",
        "other",
    ]

    def classify(self, text: str) -> str:
        """Classify market-relevant event type. Replace with ML/LLM classifier later."""
        return "other"
