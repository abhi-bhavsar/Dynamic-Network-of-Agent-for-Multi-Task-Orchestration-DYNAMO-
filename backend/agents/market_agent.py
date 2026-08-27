from typing import Dict, Any
from .base_agent import BaseAgent, AgentOutput


class MarketDataAgent(BaseAgent):
    name = "deploy_market"
    description = (
        "You specialize in market data analysis: stock prices, trading volumes, "
        "price momentum, moving averages, 52-week highs/lows, market cap, and "
        "technical indicators. Analyze market conditions from the provided context."
    )
    domain_keywords = ["price", "stock", "ticker", "volume", "market", "trading", "technical"]

    async def execute(self, task: str, memory_slice: Dict[str, Any]) -> AgentOutput:
        findings, tokens = await self._call_llm(task, memory_slice)
        return AgentOutput(
            agent_name=self.name,
            findings=findings,
            confidence=self._parse_confidence(findings),
            tokens_used=tokens,
        )
