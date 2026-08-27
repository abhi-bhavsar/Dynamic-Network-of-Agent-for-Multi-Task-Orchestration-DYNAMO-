from pydantic import BaseModel, Field
from typing import List


AVAILABLE_AGENTS = [
    "deploy_market",       # Market Data Agent — prices, volumes, technicals
    "deploy_sentiment",    # Sentiment Agent   — news, social, NLP
    "deploy_fundamental",  # Fundamental Agent — earnings, ratios, filings
    "deploy_risk",         # Risk Agent        — volatility, exposure, hedging
    "deploy_macro",        # Macro Agent       — GDP, inflation, interest rates
]


class SpawnManifest(BaseModel):
    """
    The deterministic output of the Orchestrator node.
    Instructor forces the LLM to return a validated instance of this model.
    This manifest is the single routing instruction for the Agent Execution node.
    """

    agents: List[str] = Field(
        description=f"Ordered list of agents to spawn. Choose from: {AVAILABLE_AGENTS}"
    )
    policy: str = Field(
        description="Selected spawning policy: on_demand | pool_based | predictive | hierarchical | composite"
    )
    complexity: int = Field(
        ge=1, le=5,
        description="Query complexity score from 1 (trivial) to 5 (full multi-domain research)"
    )
    reasoning: str = Field(
        description="One sentence explaining why these specific agents were selected"
    )
    memory_keys: List[str] = Field(
        default_factory=list,
        description="Global context keys relevant to this query (e.g. 'ticker', 'sector')"
    )
