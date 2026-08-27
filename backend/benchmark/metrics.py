from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class BenchmarkMetrics:
    query: str
    policy: str
    dynamic_tokens: int
    static_tokens: int
    dynamic_latency_ms: float
    static_latency_ms: float
    agents_spawned_dynamic: int
    agents_spawned_static: int = 5
    token_savings_pct: float = 0.0
    latency_savings_pct: float = 0.0
    agent_reduction_pct: float = 0.0

    def __post_init__(self):
        if self.static_tokens > 0:
            self.token_savings_pct = round(
                (1 - self.dynamic_tokens / self.static_tokens) * 100, 2
            )
        if self.static_latency_ms > 0:
            self.latency_savings_pct = round(
                (1 - self.dynamic_latency_ms / self.static_latency_ms) * 100, 2
            )
        self.agent_reduction_pct = round(
            (1 - self.agents_spawned_dynamic / self.agents_spawned_static) * 100, 2
        )

    def to_dict(self) -> Dict:
        return asdict(self)


def aggregate_metrics(results: List[BenchmarkMetrics]) -> Dict:
    """Compute mean metrics over multiple benchmark runs."""
    if not results:
        return {}

    def mean(key):
        vals = [getattr(r, key) for r in results]
        return round(sum(vals) / len(vals), 2)

    return {
        "runs": len(results),
        "avg_dynamic_tokens": mean("dynamic_tokens"),
        "avg_static_tokens": mean("static_tokens"),
        "avg_token_savings_pct": mean("token_savings_pct"),
        "avg_dynamic_latency_ms": mean("dynamic_latency_ms"),
        "avg_static_latency_ms": mean("static_latency_ms"),
        "avg_latency_savings_pct": mean("latency_savings_pct"),
        "avg_agent_reduction_pct": mean("agent_reduction_pct"),
    }
