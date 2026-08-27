from typing import Dict, List


# Keywords for each feature dimension
URGENCY_KEYWORDS = [
    "real-time", "realtime", "immediately", "now", "current",
    "latest", "live", "today", "urgent", "right now", "instant"
]

COMPLEXITY_HIGH_KEYWORDS = [
    "comprehensive", "detailed", "in-depth", "full analysis", "compare",
    "multiple", "vs", "versus", "portfolio", "sector", "macro", "deep dive",
    "all aspects", "complete", "report", "research"
]

COMPLEXITY_MED_KEYWORDS = [
    "analyze", "analysis", "performance", "trend", "outlook",
    "forecast", "review", "assess", "evaluate", "examine"
]


class FeatureExtractor:
    """
    Computes the PSE feature vector F(Q) = (N, U, C, R) for a query.

    N — Novelty:    How different is this query from session history?
    U — Urgency:    Does the query require real-time/immediate data?
    C — Complexity: How many agents are likely needed? (1–5)
    R — Recurrence: How often does this query pattern appear in session?
    """

    def __init__(self):
        self._history: List[str] = []

    def compute(self, query: str) -> Dict[str, float]:
        """Returns F(Q) = {N, U, C, R}"""
        return {
            "N": round(self._novelty(query), 3),
            "U": round(self._urgency(query), 3),
            "C": float(self._complexity(query)),
            "R": round(self._recurrence(query), 3),
        }

    def add_to_history(self, query: str):
        self._history.append(query.lower())
        if len(self._history) > 50:  # rolling window of 50
            self._history = self._history[-50:]

    def reset_session(self):
        self._history.clear()

    # ── Private helpers ──────────────────────────────────────

    def _jaccard(self, a: str, b: str) -> float:
        """Simple token-level Jaccard similarity."""
        set_a = set(a.lower().split())
        set_b = set(b.lower().split())
        if not set_a and not set_b:
            return 0.0
        return len(set_a & set_b) / len(set_a | set_b)

    def _novelty(self, query: str) -> float:
        """N = 1 − max_similarity(query, history). Novel → N close to 1."""
        if not self._history:
            return 1.0
        sims = [self._jaccard(query, h) for h in self._history[-10:]]
        return 1.0 - max(sims)

    def _urgency(self, query: str) -> float:
        """U = function of urgency keywords present. Default 0.3 (low)."""
        q = query.lower()
        hits = sum(1 for kw in URGENCY_KEYWORDS if kw in q)
        if hits == 0:
            return 0.3
        return min(0.95, 0.3 + hits * 0.2)

    def _complexity(self, query: str) -> int:
        """C ∈ {1,2,3,4,5} — predicted agent cardinality."""
        q = query.lower()
        score = 1
        if any(kw in q for kw in COMPLEXITY_HIGH_KEYWORDS):
            score += 2
        if any(kw in q for kw in COMPLEXITY_MED_KEYWORDS):
            score += 1
        word_count = len(query.split())
        if word_count > 25:
            score += 1
        # Count entity-like tokens (capitalized words suggest company/ticker)
        caps = sum(1 for w in query.split() if len(w) > 1 and w[0].isupper())
        if caps >= 3:
            score += 1
        return min(5, max(1, score))

    def _recurrence(self, query: str) -> float:
        """R = fraction of history that is semantically similar to query."""
        if len(self._history) < 3:
            return 0.0
        count = sum(
            1 for h in self._history
            if self._jaccard(query, h) > 0.5
        )
        return min(1.0, count / len(self._history))


# Module-level singleton (shared across request lifecycle in FastAPI)
feature_extractor = FeatureExtractor()
